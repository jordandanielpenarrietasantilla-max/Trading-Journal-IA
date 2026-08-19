from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import urllib.parse
import urllib.request


BINANCE_DATA_BASE = "https://data-api.binance.vision"


class OrderBookError(RuntimeError):
    pass


@dataclass(frozen=True)
class OrderBookLevel:
    price: float
    quantity: float


@dataclass(frozen=True)
class OrderBookSnapshot:
    symbol: str
    last_update_id: int
    bids: tuple[OrderBookLevel, ...]
    asks: tuple[OrderBookLevel, ...]

    @property
    def best_bid(self) -> float | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> float | None:
        return self.asks[0].price if self.asks else None

    @property
    def mid_price(self) -> float | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2.0


def _levels(raw: Any) -> tuple[OrderBookLevel, ...]:
    result: list[OrderBookLevel] = []
    if not isinstance(raw, list):
        return tuple()

    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        try:
            price = float(item[0])
            quantity = float(item[1])
        except (TypeError, ValueError):
            continue
        if price <= 0 or quantity < 0:
            continue
        result.append(OrderBookLevel(price=price, quantity=quantity))
    return tuple(result)


def fetch_binance_spot_depth(
    symbol: str = "BTCUSDT",
    *,
    limit: int = 500,
    timeout: float = 8.0,
) -> OrderBookSnapshot:
    """
    Public Binance Spot order-book snapshot.
    No API key is required.

    This returns real exchange depth at request time. It does not fabricate
    missing levels and does not turn top-of-book data into synthetic depth.
    """
    clean = "".join(ch for ch in str(symbol).upper() if ch.isalnum())
    if not clean:
        raise OrderBookError("Símbolo inválido.")

    allowed_limits = (5, 10, 20, 50, 100, 500, 1000, 5000)
    if limit not in allowed_limits:
        raise OrderBookError(
            f"Limit inválido. Usa uno de: {', '.join(map(str, allowed_limits))}."
        )

    query = urllib.parse.urlencode({"symbol": clean, "limit": limit})
    url = f"{BINANCE_DATA_BASE}/api/v3/depth?{query}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "AXION-PRIME/1.0",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise OrderBookError(f"No se pudo obtener profundidad de Binance: {exc}") from exc

    if not isinstance(payload, dict):
        raise OrderBookError("Respuesta inesperada de Binance.")

    if "code" in payload and "msg" in payload:
        raise OrderBookError(f"Binance: {payload.get('msg')}")

    try:
        last_update_id = int(payload["lastUpdateId"])
    except Exception as exc:
        raise OrderBookError("Binance no devolvió lastUpdateId.") from exc

    bids = _levels(payload.get("bids"))
    asks = _levels(payload.get("asks"))

    return OrderBookSnapshot(
        symbol=clean,
        last_update_id=last_update_id,
        bids=bids,
        asks=asks,
    )


def snapshot_to_payload(snapshot: OrderBookSnapshot, *, max_levels: int = 250) -> dict[str, Any]:
    """
    JSON-safe payload for frontend/bootstrap/fallback use.
    """
    bids = snapshot.bids[:max_levels]
    asks = snapshot.asks[:max_levels]
    return {
        "symbol": snapshot.symbol,
        "last_update_id": snapshot.last_update_id,
        "best_bid": snapshot.best_bid,
        "best_ask": snapshot.best_ask,
        "mid_price": snapshot.mid_price,
        "bids": [[level.price, level.quantity] for level in bids],
        "asks": [[level.price, level.quantity] for level in asks],
    }
