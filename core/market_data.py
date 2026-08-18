from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from typing import Any
import re

import pandas as pd
import requests
import streamlit as st


BINANCE_MARKET_BASE = "https://data-api.binance.vision"
REQUEST_TIMEOUT = 15

INTERVALS = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
}

POPULAR_SYMBOLS = {
    "BTCUSDT": "Bitcoin / Tether",
    "ETHUSDT": "Ethereum / Tether",
    "SOLUSDT": "Solana / Tether",
    "XRPUSDT": "XRP / Tether",
    "BNBUSDT": "BNB / Tether",
    "ADAUSDT": "Cardano / Tether",
    "DOGEUSDT": "Dogecoin / Tether",
}

ALIASES = {
    "BTC/USD": "BTCUSDT",
    "BTCUSD": "BTCUSDT",
    "BTC/USDT": "BTCUSDT",
    "ETH/USD": "ETHUSDT",
    "ETHUSD": "ETHUSDT",
    "ETH/USDT": "ETHUSDT",
    "SOL/USD": "SOLUSDT",
    "SOLUSD": "SOLUSDT",
    "SOL/USDT": "SOLUSDT",
}


class MarketDataError(RuntimeError):
    pass


@dataclass(frozen=True)
class MarketSymbol:
    symbol: str
    display_symbol: str
    base_asset: str
    quote_asset: str
    status: str
    provider: str = "Binance Spot"


def normalize_symbol(value: str) -> str:
    raw = str(value or "").strip().upper()
    if raw in ALIASES:
        return ALIASES[raw]
    return re.sub(r"[^A-Z0-9]", "", raw)


@st.cache_data(ttl=3600, show_spinner=False)
def get_binance_symbols() -> dict[str, MarketSymbol]:
    url = f"{BINANCE_MARKET_BASE}/api/v3/exchangeInfo"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketDataError(
            "No pudimos consultar el catálogo de mercados de Binance en este momento."
        ) from exc

    result: dict[str, MarketSymbol] = {}
    for item in payload.get("symbols", []):
        if not isinstance(item, dict):
            continue
        symbol = str(item.get("symbol") or "").upper()
        base = str(item.get("baseAsset") or "").upper()
        quote = str(item.get("quoteAsset") or "").upper()
        status = str(item.get("status") or "")
        if not symbol or not base or not quote:
            continue
        result[symbol] = MarketSymbol(
            symbol=symbol,
            display_symbol=f"{base}/{quote}",
            base_asset=base,
            quote_asset=quote,
            status=status,
        )
    return result


def resolve_symbol(value: str) -> MarketSymbol:
    symbol = normalize_symbol(value)
    if not symbol:
        raise MarketDataError("Escribe un activo para buscarlo.")

    catalog = get_binance_symbols()
    item = catalog.get(symbol)
    if item and item.status == "TRADING":
        return item

    # UX: si el usuario escribe BTC o ETH, intentar la cotización USDT.
    if symbol and not symbol.endswith(("USDT", "USDC", "FDUSD", "BTC", "ETH", "BNB")):
        candidate = f"{symbol}USDT"
        item = catalog.get(candidate)
        if item and item.status == "TRADING":
            return item

    raise MarketDataError(
        f"{value!s} no está disponible en la fuente gratuita verificada actual (Binance Spot). "
        "AXION PRIME no generará datos sustitutos."
    )


def _to_utc_ms(day: date) -> int:
    dt = datetime.combine(day, time.min, tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_binance_klines(
    symbol: str,
    interval: str,
    start_day_iso: str,
    limit: int = 1000,
) -> pd.DataFrame:
    if interval not in INTERVALS:
        raise MarketDataError(f"Timeframe no soportado: {interval}")

    start_day = date.fromisoformat(start_day_iso)
    params = {
        "symbol": normalize_symbol(symbol),
        "interval": INTERVALS[interval],
        "startTime": _to_utc_ms(start_day),
        "limit": max(100, min(int(limit), 1000)),
    }

    try:
        response = requests.get(
            f"{BINANCE_MARKET_BASE}/api/v3/klines",
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload: Any = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketDataError(
            "No pudimos descargar las velas históricas reales. Intenta nuevamente."
        ) from exc

    if not isinstance(payload, list) or not payload:
        raise MarketDataError(
            "La fuente no devolvió velas para ese activo, fecha y timeframe."
        )

    rows = []
    for item in payload:
        if not isinstance(item, list) or len(item) < 6:
            continue
        rows.append(
            {
                "open_time": pd.to_datetime(item[0], unit="ms", utc=True),
                "open": float(item[1]),
                "high": float(item[2]),
                "low": float(item[3]),
                "close": float(item[4]),
                "volume": float(item[5]),
                "close_time": pd.to_datetime(item[6], unit="ms", utc=True),
                "quote_volume": float(item[7]),
                "trades": int(item[8]),
                "taker_buy_base": float(item[9]),
                "taker_buy_quote": float(item[10]),
            }
        )

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise MarketDataError("No se pudieron interpretar las velas recibidas.")
    return frame.sort_values("open_time").reset_index(drop=True)


def get_backtest_dataset(
    user_symbol: str,
    interval: str,
    start_day: date,
    limit: int = 1000,
) -> tuple[MarketSymbol, pd.DataFrame]:
    market = resolve_symbol(user_symbol)
    frame = fetch_binance_klines(
        symbol=market.symbol,
        interval=interval,
        start_day_iso=start_day.isoformat(),
        limit=limit,
    )
    return market, frame


def search_markets(query: str, limit: int = 12) -> list[MarketSymbol]:
    cleaned = normalize_symbol(query)
    if not cleaned:
        keys = list(POPULAR_SYMBOLS)[:limit]
        catalog = get_binance_symbols()
        return [catalog[k] for k in keys if k in catalog]

    catalog = get_binance_symbols()
    matches: list[MarketSymbol] = []
    for item in catalog.values():
        haystack = f"{item.symbol} {item.base_asset} {item.quote_asset} {item.display_symbol}"
        if cleaned in re.sub(r"[^A-Z0-9]", "", haystack.upper()):
            if item.status == "TRADING":
                matches.append(item)
        if len(matches) >= limit:
            break
    return matches


@st.cache_data(ttl=5, show_spinner=False)
def fetch_recent_klines(symbol: str, interval: str = "1m", limit: int = 300) -> pd.DataFrame:
    """Descarga las velas mas recientes verificadas de Binance Spot."""
    if interval not in INTERVALS:
        raise MarketDataError(f"Timeframe no soportado: {interval}")
    params = {
        "symbol": normalize_symbol(symbol),
        "interval": INTERVALS[interval],
        "limit": max(50, min(int(limit), 1000)),
    }
    try:
        response = requests.get(f"{BINANCE_MARKET_BASE}/api/v3/klines", params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload: Any = response.json()
    except (requests.RequestException, ValueError) as exc:
        raise MarketDataError("No pudimos descargar las velas actuales del mercado.") from exc
    if not isinstance(payload, list) or not payload:
        raise MarketDataError("La fuente no devolvio velas actuales.")
    rows = []
    for item in payload:
        if not isinstance(item, list) or len(item) < 11:
            continue
        rows.append({
            "open_time": pd.to_datetime(item[0], unit="ms", utc=True),
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
            "close_time": pd.to_datetime(item[6], unit="ms", utc=True),
            "quote_volume": float(item[7]),
            "trades": int(item[8]),
            "taker_buy_base": float(item[9]),
            "taker_buy_quote": float(item[10]),
        })
    frame = pd.DataFrame(rows)
    if frame.empty:
        raise MarketDataError("No se pudieron interpretar las velas actuales.")
    return frame.sort_values("open_time").reset_index(drop=True)


@st.cache_data(ttl=3, show_spinner=False)
def fetch_ticker_price(symbol: str) -> float:
    """Obtiene el ultimo precio publicado por Binance Spot."""
    try:
        response = requests.get(
            f"{BINANCE_MARKET_BASE}/api/v3/ticker/price",
            params={"symbol": normalize_symbol(symbol)},
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        return float(payload["price"])
    except (requests.RequestException, ValueError, KeyError, TypeError) as exc:
        raise MarketDataError("No pudimos consultar el precio actual.") from exc
