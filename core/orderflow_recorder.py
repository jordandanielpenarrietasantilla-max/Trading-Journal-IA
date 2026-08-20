from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import aiohttp
import websockets
from supabase import Client, create_client


# =============================================================================
# AXION PRIME — ORDER FLOW RECORDER
# BTC/USDT Binance Spot
#
# Responsibilities:
#   - Build a correct local Binance Spot order book from REST snapshot + diff
#     depth stream.
#   - Capture one REAL liquidity matrix column every second.
#   - Aggregate REAL aggTrade events into 1-second OHLC / buy / sell volume bars.
#   - Persist both streams to Supabase.
#   - Keep only a rolling retention window (default 24 hours).
#
# This process is designed to run 24/7 as a background worker.
# =============================================================================


BINANCE_REST = "https://data-api.binance.vision"
BINANCE_WS = "wss://stream.binance.com:9443/stream"

SYMBOL = os.getenv("AXION_OF_SYMBOL", "BTCUSDT").upper()
DEPTH_STREAM = f"{SYMBOL.lower()}@depth@100ms"
TRADE_STREAM = f"{SYMBOL.lower()}@aggTrade"

CAPTURE_INTERVAL_SECONDS = float(os.getenv("AXION_OF_CAPTURE_SECONDS", "1"))
RETENTION_HOURS = int(os.getenv("AXION_OF_RETENTION_HOURS", "24"))
BOOK_LEVELS_PER_SIDE = int(os.getenv("AXION_OF_BOOK_LEVELS", "700"))
VISIBLE_RANGE_PCT = float(os.getenv("AXION_OF_RANGE_PCT", "0.010"))
BATCH_SIZE = int(os.getenv("AXION_OF_BATCH_SIZE", "15"))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("axion-orderflow")


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def bucket_step(price: float) -> float:
    """
    Practical aggregation for BTC/USDT.

    Keep this deterministic because historical columns must use the same
    bucketing rule as the renderer.
    """
    if price >= 100_000:
        return 10.0
    if price >= 50_000:
        return 5.0
    if price >= 20_000:
        return 2.0
    if price >= 5_000:
        return 1.0
    if price >= 1_000:
        return 0.5
    return 0.1


def bucket_price(price: float, step: float) -> float:
    return round(price / step) * step


@dataclass
class TradeSecond:
    second_ts_ms: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
    buy_volume: float = 0.0
    sell_volume: float = 0.0
    trade_count: int = 0
    notional: float = 0.0

    def ingest(self, *, price: float, qty: float, aggressive_buy: bool) -> None:
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.volume += qty
        self.trade_count += 1
        self.notional += price * qty

        if aggressive_buy:
            self.buy_volume += qty
        else:
            self.sell_volume += qty

    def to_row(self, symbol: str) -> dict[str, Any]:
        vwap = self.notional / self.volume if self.volume > 0 else self.close
        return {
            "symbol": symbol,
            "ts": datetime.fromtimestamp(
                self.second_ts_ms / 1000,
                tz=timezone.utc,
            ).isoformat(),
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "buy_volume": self.buy_volume,
            "sell_volume": self.sell_volume,
            "delta": self.buy_volume - self.sell_volume,
            "trade_count": self.trade_count,
            "vwap": vwap,
        }


@dataclass
class OrderFlowRecorder:
    supabase: Client
    symbol: str = SYMBOL

    bids: dict[float, float] = field(default_factory=dict)
    asks: dict[float, float] = field(default_factory=dict)

    last_update_id: int = 0
    snapshot_ready: bool = False
    depth_buffer: list[dict[str, Any]] = field(default_factory=list)

    trade_second: TradeSecond | None = None

    depth_batch: list[dict[str, Any]] = field(default_factory=list)
    trade_batch: list[dict[str, Any]] = field(default_factory=list)

    stop_event: asyncio.Event = field(default_factory=asyncio.Event)
    last_cleanup_monotonic: float = field(default_factory=time.monotonic)

    # -------------------------------------------------------------------------
    # Order book
    # -------------------------------------------------------------------------

    @staticmethod
    def _parse_levels(raw: Any) -> list[tuple[float, float]]:
        out: list[tuple[float, float]] = []
        if not isinstance(raw, list):
            return out

        for item in raw:
            try:
                price = float(item[0])
                qty = float(item[1])
            except (TypeError, ValueError, IndexError):
                continue

            if price > 0 and qty >= 0:
                out.append((price, qty))

        return out

    @staticmethod
    def _apply_side(
        book: dict[float, float],
        levels: list[tuple[float, float]],
    ) -> None:
        for price, qty in levels:
            if qty == 0:
                book.pop(price, None)
            else:
                book[price] = qty

    def apply_depth_event(self, evt: dict[str, Any]) -> None:
        self._apply_side(self.bids, self._parse_levels(evt.get("b")))
        self._apply_side(self.asks, self._parse_levels(evt.get("a")))
        self.last_update_id = int(evt.get("u", self.last_update_id))

    def best_bid_ask(self) -> tuple[float | None, float | None]:
        if not self.bids or not self.asks:
            return None, None

        return max(self.bids), min(self.asks)

    def mid_price(self) -> float | None:
        best_bid, best_ask = self.best_bid_ask()
        if best_bid is None or best_ask is None:
            return None
        return (best_bid + best_ask) / 2.0

    async def fetch_snapshot(self, session: aiohttp.ClientSession) -> None:
        url = f"{BINANCE_REST}/api/v3/depth"
        params = {
            "symbol": self.symbol,
            "limit": 1000,
        }

        async with session.get(url, params=params, timeout=10) as resp:
            resp.raise_for_status()
            payload = await resp.json()

        bids = {
            p: q
            for p, q in self._parse_levels(payload.get("bids"))
            if q > 0
        }
        asks = {
            p: q
            for p, q in self._parse_levels(payload.get("asks"))
            if q > 0
        }

        snapshot_id = int(payload["lastUpdateId"])

        self.bids = bids
        self.asks = asks
        self.last_update_id = snapshot_id

        # Binance local order-book sync:
        # discard events fully older than snapshot, then locate the first event
        # whose range bridges snapshot_id + 1.
        buffered = [
            evt
            for evt in self.depth_buffer
            if int(evt.get("u", 0)) > snapshot_id
        ]

        start_index: int | None = None

        for i, evt in enumerate(buffered):
            U = int(evt.get("U", 0))
            u = int(evt.get("u", 0))
            expected = snapshot_id + 1

            if U <= expected <= u:
                start_index = i
                break

        if start_index is not None:
            for evt in buffered[start_index:]:
                if int(evt.get("u", 0)) > self.last_update_id:
                    self.apply_depth_event(evt)

        self.depth_buffer.clear()
        self.snapshot_ready = True

        log.info(
            "Snapshot ready | id=%s | bids=%s | asks=%s",
            self.last_update_id,
            len(self.bids),
            len(self.asks),
        )

    async def handle_depth(
        self,
        evt: dict[str, Any],
        session: aiohttp.ClientSession,
    ) -> None:
        if not self.snapshot_ready:
            self.depth_buffer.append(evt)

            if len(self.depth_buffer) > 6000:
                self.depth_buffer = self.depth_buffer[-6000:]
            return

        expected = self.last_update_id + 1
        U = int(evt.get("U", 0))
        u = int(evt.get("u", 0))

        if u < expected:
            return

        if U > expected:
            log.warning(
                "Depth sequence gap | expected=%s U=%s u=%s | resyncing",
                expected,
                U,
                u,
            )
            self.snapshot_ready = False
            self.depth_buffer = [evt]
            await self.fetch_snapshot(session)
            return

        self.apply_depth_event(evt)

    # -------------------------------------------------------------------------
    # Liquidity matrix
    # -------------------------------------------------------------------------

    def build_depth_column(self) -> dict[str, Any] | None:
        mid = self.mid_price()
        best_bid, best_ask = self.best_bid_ask()

        if mid is None or best_bid is None or best_ask is None:
            return None

        step = bucket_step(mid)
        low = mid * (1.0 - VISIBLE_RANGE_PCT)
        high = mid * (1.0 + VISIBLE_RANGE_PCT)

        buckets: dict[float, dict[str, float]] = {}

        bid_levels = sorted(
            self.bids.items(),
            key=lambda x: x[0],
            reverse=True,
        )[:BOOK_LEVELS_PER_SIDE]

        ask_levels = sorted(
            self.asks.items(),
            key=lambda x: x[0],
        )[:BOOK_LEVELS_PER_SIDE]

        def add(side: str, levels: list[tuple[float, float]]) -> None:
            for price, qty in levels:
                if price < low or price > high or qty <= 0:
                    continue

                p = bucket_price(price, step)
                row = buckets.setdefault(
                    p,
                    {"price": p, "bid": 0.0, "ask": 0.0},
                )
                row[side] += qty

        add("bid", bid_levels)
        add("ask", ask_levels)

        compact_buckets: list[dict[str, float]] = []

        for row in sorted(buckets.values(), key=lambda x: x["price"]):
            total = row["bid"] + row["ask"]
            if total <= 0:
                continue

            compact_buckets.append(
                {
                    "p": row["price"],
                    "b": round(row["bid"], 8),
                    "a": round(row["ask"], 8),
                    "q": round(total, 8),
                }
            )

        return {
            "symbol": self.symbol,
            "ts": utc_now_iso(),
            "mid": mid,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "spread": best_ask - best_bid,
            "bucket_step": step,
            "range_pct": VISIBLE_RANGE_PCT,
            "buckets": compact_buckets,
        }

    # -------------------------------------------------------------------------
    # Trades
    # -------------------------------------------------------------------------

    def handle_trade(self, evt: dict[str, Any]) -> None:
        try:
            price = float(evt["p"])
            qty = float(evt["q"])
            ts_ms = int(evt.get("T", int(time.time() * 1000)))
        except (KeyError, TypeError, ValueError):
            return

        if price <= 0 or qty <= 0:
            return

        # Binance aggTrade:
        # m=True means buyer was maker -> aggressive seller.
        aggressive_buy = not bool(evt.get("m"))

        second_ts_ms = (ts_ms // 1000) * 1000

        if (
            self.trade_second is None
            or self.trade_second.second_ts_ms != second_ts_ms
        ):
            if self.trade_second is not None:
                self.trade_batch.append(
                    self.trade_second.to_row(self.symbol)
                )

            self.trade_second = TradeSecond(
                second_ts_ms=second_ts_ms,
                open=price,
                high=price,
                low=price,
                close=price,
            )

        self.trade_second.ingest(
            price=price,
            qty=qty,
            aggressive_buy=aggressive_buy,
        )

    # -------------------------------------------------------------------------
    # Supabase
    # -------------------------------------------------------------------------

    async def flush_batches(self, force: bool = False) -> None:
        if self.trade_second is not None and force:
            self.trade_batch.append(
                self.trade_second.to_row(self.symbol)
            )
            self.trade_second = None

        should_flush_depth = (
            len(self.depth_batch) >= BATCH_SIZE
            or (force and self.depth_batch)
        )
        should_flush_trades = (
            len(self.trade_batch) >= BATCH_SIZE
            or (force and self.trade_batch)
        )

        if should_flush_depth:
            rows = self.depth_batch[:]
            self.depth_batch.clear()

            try:
                await asyncio.to_thread(
                    lambda: self.supabase
                    .table("orderflow_depth")
                    .upsert(
                        rows,
                        on_conflict="symbol,ts",
                    )
                    .execute()
                )
                log.info("Stored depth rows=%s", len(rows))
            except Exception:
                log.exception("Depth insert failed")
                self.depth_batch = rows + self.depth_batch

        if should_flush_trades:
            rows = self.trade_batch[:]
            self.trade_batch.clear()

            try:
                await asyncio.to_thread(
                    lambda: self.supabase
                    .table("orderflow_trade_seconds")
                    .upsert(
                        rows,
                        on_conflict="symbol,ts",
                    )
                    .execute()
                )
                log.info("Stored trade rows=%s", len(rows))
            except Exception:
                log.exception("Trade insert failed")
                self.trade_batch = rows + self.trade_batch

    async def cleanup_old_rows(self) -> None:
        cutoff_epoch = time.time() - RETENTION_HOURS * 3600
        cutoff_iso = datetime.fromtimestamp(
            cutoff_epoch,
            tz=timezone.utc,
        ).isoformat()

        log.info("Retention cleanup | older than %s", cutoff_iso)

        try:
            await asyncio.to_thread(
                lambda: self.supabase
                .table("orderflow_depth")
                .delete()
                .eq("symbol", self.symbol)
                .lt("ts", cutoff_iso)
                .execute()
            )

            await asyncio.to_thread(
                lambda: self.supabase
                .table("orderflow_trade_seconds")
                .delete()
                .eq("symbol", self.symbol)
                .lt("ts", cutoff_iso)
                .execute()
            )
        except Exception:
            log.exception("Retention cleanup failed")

    # -------------------------------------------------------------------------
    # Runtime loops
    # -------------------------------------------------------------------------

    async def capture_loop(self) -> None:
        while not self.stop_event.is_set():
            started = time.monotonic()

            if self.snapshot_ready:
                row = self.build_depth_column()

                if row is not None:
                    self.depth_batch.append(row)

            await self.flush_batches()

            if time.monotonic() - self.last_cleanup_monotonic >= 15 * 60:
                self.last_cleanup_monotonic = time.monotonic()
                await self.cleanup_old_rows()

            elapsed = time.monotonic() - started
            await asyncio.sleep(
                max(0.05, CAPTURE_INTERVAL_SECONDS - elapsed)
            )

    async def websocket_loop(self) -> None:
        streams = f"{DEPTH_STREAM}/{TRADE_STREAM}"
        url = f"{BINANCE_WS}?streams={streams}"

        timeout = aiohttp.ClientTimeout(total=15)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            while not self.stop_event.is_set():
                self.snapshot_ready = False
                self.depth_buffer.clear()

                try:
                    log.info("Connecting Binance | %s", url)

                    async with websockets.connect(
                        url,
                        ping_interval=20,
                        ping_timeout=20,
                        close_timeout=5,
                        max_queue=10000,
                    ) as ws:
                        # Begin buffering depth before fetching snapshot.
                        snapshot_task = asyncio.create_task(
                            self.fetch_snapshot(session)
                        )

                        async for raw in ws:
                            if self.stop_event.is_set():
                                break

                            packet = json.loads(raw)
                            evt = packet.get("data", packet)

                            event_type = evt.get("e")

                            if event_type == "depthUpdate":
                                if not snapshot_task.done():
                                    self.depth_buffer.append(evt)

                                    if len(self.depth_buffer) > 6000:
                                        self.depth_buffer = self.depth_buffer[-6000:]
                                else:
                                    if snapshot_task.exception():
                                        raise snapshot_task.exception()

                                    await self.handle_depth(evt, session)

                            elif event_type == "aggTrade":
                                self.handle_trade(evt)

                        if not snapshot_task.done():
                            await snapshot_task

                except asyncio.CancelledError:
                    raise
                except Exception:
                    log.exception("Binance websocket loop failed")

                    if not self.stop_event.is_set():
                        await asyncio.sleep(2.0)

    async def run(self) -> None:
        log.info(
            "AXION recorder starting | symbol=%s | capture=%ss | retention=%sh",
            self.symbol,
            CAPTURE_INTERVAL_SECONDS,
            RETENTION_HOURS,
        )

        capture_task = asyncio.create_task(self.capture_loop())
        ws_task = asyncio.create_task(self.websocket_loop())

        await self.stop_event.wait()

        log.info("Stopping AXION recorder…")

        for task in (capture_task, ws_task):
            task.cancel()

        await asyncio.gather(
            capture_task,
            ws_task,
            return_exceptions=True,
        )

        await self.flush_batches(force=True)

        log.info("AXION recorder stopped cleanly")


async def main() -> None:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_SERVICE_ROLE_KEY,
    )

    recorder = OrderFlowRecorder(supabase=supabase)

    loop = asyncio.get_running_loop()

    def request_stop() -> None:
        recorder.stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, request_stop)
        except NotImplementedError:
            pass

    await recorder.run()


if __name__ == "__main__":
    asyncio.run(main())
