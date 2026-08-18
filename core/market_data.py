from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
import re

import pandas as pd
import requests
import streamlit as st


BINANCE_MARKET_BASE = "https://data-api.binance.vision"
MASSIVE_API_BASE = "https://api.massive.com"
REQUEST_TIMEOUT = 20

INTERVALS = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
}

# Massive uses multiplier + timespan for Forex/Metals aggregates.
MASSIVE_INTERVALS = {
    "1m": (1, "minute"),
    "5m": (5, "minute"),
    "15m": (15, "minute"),
    "30m": (30, "minute"),
    "1H": (1, "hour"),
    "4H": (4, "hour"),
    "1D": (1, "day"),
}

POPULAR_SYMBOLS = {
    "XAUUSD": "Gold Spot / U.S. Dollar",
    "EURUSD": "Euro / U.S. Dollar",
    "GBPUSD": "British Pound / U.S. Dollar",
    "USDJPY": "U.S. Dollar / Japanese Yen",
    "BTCUSDT": "Bitcoin / Tether",
    "ETHUSDT": "Ethereum / Tether",
    "SOLUSDT": "Solana / Tether",
}

# Static catalog for the Forex/Metals markets we want to expose in AXION.
FOREX_MARKETS = {
    "XAUUSD": ("XAU", "USD", "Gold Spot / U.S. Dollar"),
    "XAGUSD": ("XAG", "USD", "Silver Spot / U.S. Dollar"),
    "EURUSD": ("EUR", "USD", "Euro / U.S. Dollar"),
    "GBPUSD": ("GBP", "USD", "British Pound / U.S. Dollar"),
    "USDJPY": ("USD", "JPY", "U.S. Dollar / Japanese Yen"),
    "AUDUSD": ("AUD", "USD", "Australian Dollar / U.S. Dollar"),
    "USDCAD": ("USD", "CAD", "U.S. Dollar / Canadian Dollar"),
    "USDCHF": ("USD", "CHF", "U.S. Dollar / Swiss Franc"),
    "NZDUSD": ("NZD", "USD", "New Zealand Dollar / U.S. Dollar"),
    "EURJPY": ("EUR", "JPY", "Euro / Japanese Yen"),
    "EURGBP": ("EUR", "GBP", "Euro / British Pound"),
    "GBPJPY": ("GBP", "JPY", "British Pound / Japanese Yen"),
}

ALIASES = {
    # Crypto
    "BTC/USD": "BTCUSDT",
    "BTCUSD": "BTCUSDT",
    "BTC/USDT": "BTCUSDT",
    "ETH/USD": "ETHUSDT",
    "ETHUSD": "ETHUSDT",
    "ETH/USDT": "ETHUSDT",
    "SOL/USD": "SOLUSDT",
    "SOLUSD": "SOLUSDT",
    "SOL/USDT": "SOLUSDT",

    # Gold / Silver
    "GOLD": "XAUUSD",
    "ORO": "XAUUSD",
    "XAU/USD": "XAUUSD",
    "XAUUSD": "XAUUSD",
    "SILVER": "XAGUSD",
    "PLATA": "XAGUSD",
    "XAG/USD": "XAGUSD",
    "XAGUSD": "XAGUSD",

    # Forex
    "EUR/USD": "EURUSD",
    "GBP/USD": "GBPUSD",
    "USD/JPY": "USDJPY",
    "AUD/USD": "AUDUSD",
    "USD/CAD": "USDCAD",
    "USD/CHF": "USDCHF",
    "NZD/USD": "NZDUSD",
    "EUR/JPY": "EURJPY",
    "EUR/GBP": "EURGBP",
    "GBP/JPY": "GBPJPY",
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
    provider_symbol: str | None = None
    market_name: str | None = None


def normalize_symbol(value: str) -> str:
    raw = str(value or "").strip().upper()
    if raw in ALIASES:
        return ALIASES[raw]

    cleaned = re.sub(r"[^A-Z0-9]", "", raw)
    if cleaned in ALIASES:
        return ALIASES[cleaned]
    return cleaned


def _massive_api_key() -> str:
    try:
        key = str(st.secrets.get("MASSIVE_API_KEY", "")).strip()
    except Exception:
        key = ""

    if not key:
        raise MarketDataError(
            "Falta MASSIVE_API_KEY en Streamlit Secrets. "
            "Agrégala para habilitar XAU/USD y Forex."
        )
    return key


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
            provider="Binance Spot",
            provider_symbol=symbol,
            market_name=f"{base} / {quote}",
        )
    return result


def _forex_market(symbol: str) -> MarketSymbol | None:
    info = FOREX_MARKETS.get(symbol)
    if not info:
        return None

    base, quote, name = info
    return MarketSymbol(
        symbol=symbol,
        display_symbol=f"{base}/{quote}",
        base_asset=base,
        quote_asset=quote,
        status="ACTIVE",
        provider="Massive Forex",
        provider_symbol=f"C:{symbol}",
        market_name=name,
    )


def resolve_symbol(value: str) -> MarketSymbol:
    symbol = normalize_symbol(value)
    if not symbol:
        raise MarketDataError("Escribe un activo para buscarlo.")

    # Forex/metals are resolved locally; Massive validates the actual dataset on fetch.
    fx = _forex_market(symbol)
    if fx:
        return fx

    # Crypto remains on Binance.
    catalog = get_binance_symbols()
    item = catalog.get(symbol)
    if item and item.status == "TRADING":
        return item

    # UX: BTC, ETH, SOL, etc. -> USDT when Binance has the pair.
    if symbol and not symbol.endswith(("USDT", "USDC", "FDUSD", "BTC", "ETH", "BNB")):
        candidate = f"{symbol}USDT"
        item = catalog.get(candidate)
        if item and item.status == "TRADING":
            return item

    raise MarketDataError(
        f"{value!s} no está disponible en las fuentes verificadas actuales "
        "(Binance Spot para crypto / Massive para Forex y metales). "
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
            "No pudimos descargar las velas históricas reales desde Binance."
        ) from exc

    if not isinstance(payload, list) or not payload:
        raise MarketDataError(
            "Binance no devolvió velas para ese activo, fecha y timeframe."
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
        raise MarketDataError("No se pudieron interpretar las velas recibidas de Binance.")

    return frame.sort_values("open_time").reset_index(drop=True)


def _massive_range_end(start_day: date, interval: str) -> date:
    """
    Request enough calendar time to obtain ~1000 useful bars without asking
    for the entire two-year history on each query.
    """
    days_by_interval = {
        "1m": 10,
        "5m": 30,
        "15m": 60,
        "30m": 90,
        "1H": 120,
        "4H": 365,
        "1D": 730,
    }
    days = days_by_interval.get(interval, 120)

    # Basic plan offers up to two years of history. Never request future data.
    today = datetime.now(timezone.utc).date()
    two_year_limit = start_day + timedelta(days=730)
    desired = start_day + timedelta(days=days)
    return min(today, two_year_limit, desired)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_massive_aggregates(
    symbol: str,
    interval: str,
    start_day_iso: str,
    limit: int = 1000,
) -> pd.DataFrame:
    if interval not in MASSIVE_INTERVALS:
        raise MarketDataError(f"Timeframe no soportado para Forex/Metales: {interval}")

    api_key = _massive_api_key()
    symbol = normalize_symbol(symbol)

    if symbol not in FOREX_MARKETS:
        raise MarketDataError(f"{symbol} no está habilitado como mercado Forex/Metal.")

    start_day = date.fromisoformat(start_day_iso)
    end_day = _massive_range_end(start_day, interval)

    if end_day < start_day:
        raise MarketDataError("La fecha seleccionada está en el futuro.")

    multiplier, timespan = MASSIVE_INTERVALS[interval]
    provider_symbol = f"C:{symbol}"

    url = (
        f"{MASSIVE_API_BASE}/v2/aggs/ticker/{provider_symbol}"
        f"/range/{multiplier}/{timespan}/{start_day.isoformat()}/{end_day.isoformat()}"
    )

    params = {
        "adjusted": "true",
        "sort": "asc",
        # Massive documents this as the number of base aggregates used.
        # Keep it high enough for intraday bars, then trim locally.
        "limit": 50000,
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code in (401, 403):
            raise MarketDataError(
                "Massive rechazó la consulta. Revisa MASSIVE_API_KEY y confirma "
                "que tu cuenta tenga acceso a Currencies/Forex."
            )

        response.raise_for_status()
        payload: Any = response.json()

    except MarketDataError:
        raise
    except requests.RequestException as exc:
        raise MarketDataError(
            "No pudimos descargar el histórico de Forex/Metales desde Massive."
        ) from exc
    except ValueError as exc:
        raise MarketDataError("Massive devolvió una respuesta que AXION no pudo interpretar.") from exc

    if not isinstance(payload, dict):
        raise MarketDataError("Massive devolvió una respuesta inesperada.")

    if str(payload.get("status", "")).upper() not in ("OK", "DELAYED"):
        message = payload.get("error") or payload.get("message") or payload.get("status")
        raise MarketDataError(f"Massive no pudo entregar los datos: {message}")

    results = payload.get("results") or []
    if not isinstance(results, list) or not results:
        raise MarketDataError(
            "Massive no devolvió velas para ese activo, fecha y timeframe. "
            "Recuerda que el plan gratuito trabaja con histórico/EOD, no con mercado live."
        )

    rows: list[dict[str, Any]] = []
    for item in results:
        if not isinstance(item, dict):
            continue
        try:
            open_time = pd.to_datetime(int(item["t"]), unit="ms", utc=True)
            rows.append(
                {
                    "open_time": open_time,
                    "open": float(item["o"]),
                    "high": float(item["h"]),
                    "low": float(item["l"]),
                    "close": float(item["c"]),
                    # Forex aggregates are quote-derived. Preserve provider volume
                    # if supplied; otherwise use zero rather than fabricate it.
                    "volume": float(item.get("v") or 0.0),
                    "close_time": open_time,
                    "quote_volume": 0.0,
                    "trades": int(item.get("n") or 0),
                    "taker_buy_base": 0.0,
                    "taker_buy_quote": 0.0,
                }
            )
        except (KeyError, TypeError, ValueError):
            continue

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise MarketDataError("No se pudieron interpretar las velas recibidas de Massive.")

    frame = (
        frame.sort_values("open_time")
        .drop_duplicates(subset=["open_time"], keep="last")
        .reset_index(drop=True)
    )

    requested = max(100, min(int(limit), 5000))
    return frame.iloc[:requested].reset_index(drop=True)



@st.cache_data(ttl=5, show_spinner=False)
def fetch_recent_klines(symbol: str, interval: str = "1m", limit: int = 300) -> pd.DataFrame:
    """
    Compatibilidad con el Market Stream existente de AXION.
    Descarga las velas más recientes verificadas de Binance Spot.
    """
    if interval not in INTERVALS:
        raise MarketDataError(f"Timeframe no soportado: {interval}")

    params = {
        "symbol": normalize_symbol(symbol),
        "interval": INTERVALS[interval],
        "limit": max(50, min(int(limit), 1000)),
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
            "No pudimos descargar las velas actuales del mercado."
        ) from exc

    if not isinstance(payload, list) or not payload:
        raise MarketDataError("La fuente no devolvió velas actuales.")

    rows = []
    for item in payload:
        if not isinstance(item, list) or len(item) < 11:
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
        raise MarketDataError("No se pudieron interpretar las velas actuales.")

    return frame.sort_values("open_time").reset_index(drop=True)

def get_backtest_dataset(
    user_symbol: str,
    interval: str,
    start_day: date,
    limit: int = 1000,
) -> tuple[MarketSymbol, pd.DataFrame]:
    market = resolve_symbol(user_symbol)

    if market.provider == "Massive Forex":
        frame = fetch_massive_aggregates(
            symbol=market.symbol,
            interval=interval,
            start_day_iso=start_day.isoformat(),
            limit=limit,
        )
    else:
        frame = fetch_binance_klines(
            symbol=market.symbol,
            interval=interval,
            start_day_iso=start_day.isoformat(),
            limit=limit,
        )

    return market, frame


def search_markets(query: str, limit: int = 12) -> list[MarketSymbol]:
    cleaned = normalize_symbol(query)
    matches: list[MarketSymbol] = []

    # Forex / metals first so XAUUSD appears immediately.
    fx_items = [_forex_market(symbol) for symbol in FOREX_MARKETS]
    fx_items = [item for item in fx_items if item is not None]

    if not cleaned:
        priority = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY"]
        for symbol in priority:
            item = _forex_market(symbol)
            if item:
                matches.append(item)

        try:
            catalog = get_binance_symbols()
            for symbol in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
                item = catalog.get(symbol)
                if item:
                    matches.append(item)
        except MarketDataError:
            pass

        return matches[:limit]

    for item in fx_items:
        haystack = (
            f"{item.symbol} {item.base_asset} {item.quote_asset} "
            f"{item.display_symbol} {item.market_name or ''}"
        )
        normalized_haystack = re.sub(r"[^A-Z0-9]", "", haystack.upper())
        if cleaned in normalized_haystack:
            matches.append(item)
            if len(matches) >= limit:
                return matches[:limit]

    try:
        catalog = get_binance_symbols()
        for item in catalog.values():
            haystack = f"{item.symbol} {item.base_asset} {item.quote_asset} {item.display_symbol}"
            if cleaned in re.sub(r"[^A-Z0-9]", "", haystack.upper()):
                if item.status == "TRADING":
                    matches.append(item)
            if len(matches) >= limit:
                break
    except MarketDataError:
        # Forex/Metals search can continue to work even if Binance is unavailable.
        pass

    return matches[:limit]
