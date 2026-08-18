from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import streamlit as st

from components.axion_chart import render_axion_chart
from core.backtest_engine import TradePlan, evaluate_trade
from core.market_data import MarketDataError, get_backtest_dataset, resolve_symbol
from ui_v2.theme import apply_v2_theme


TIMEFRAMES = ["1m", "5m", "15m", "30m", "1H", "4H", "1D"]


def _init_state() -> None:
    defaults = {
        "bt_symbol": "BTCUSDT",
        "bt_interval": "1H",
        "bt_date": date.today() - timedelta(days=30),
        "bt_market": None,
        "bt_dataset": None,
        "bt_cursor": 80,
        "bt_trade": None,
        "bt_trade_result": None,
        "bt_error": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _load_dataset(symbol: str, interval: str, start_day: date) -> None:
    market, frame = get_backtest_dataset(symbol, interval, start_day, limit=1000)

    if frame is None or frame.empty:
        raise MarketDataError("La fuente no devolvió datos para esa selección.")

    st.session_state.bt_market = market
    st.session_state.bt_dataset = frame
    st.session_state.bt_symbol = market.symbol
    st.session_state.bt_interval = interval
    st.session_state.bt_date = start_day

    # Contexto inicial suficiente sin revelar toda la sesión visualmente.
    st.session_state.bt_cursor = min(
        max(80, int(len(frame) * 0.20)),
        max(0, len(frame) - 1),
    )
    st.session_state.bt_trade = None
    st.session_state.bt_trade_result = None
    st.session_state.bt_error = None


def _candles(frame: pd.DataFrame) -> list[dict]:
    rows = []
    for _, row in frame.iterrows():
        rows.append(
            {
                "time": int(pd.Timestamp(row["open_time"]).timestamp()),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            }
        )
    return rows


def _volumes(frame: pd.DataFrame) -> list[dict]:
    rows = []
    for _, row in frame.iterrows():
        up = float(row["close"]) >= float(row["open"])
        rows.append(
            {
                "time": int(pd.Timestamp(row["open_time"]).timestamp()),
                "value": float(row["volume"]),
                "color": "rgba(20,217,154,.28)" if up else "rgba(255,73,105,.25)",
            }
        )
    return rows


def _handle_component_events(result) -> None:
    # Timeframe lives inside the chart.
    if getattr(result, "timeframe", None):
        new_tf = str(result.timeframe)
        if new_tf in TIMEFRAMES and new_tf != st.session_state.bt_interval:
            try:
                _load_dataset(
                    st.session_state.bt_symbol,
                    new_tf,
                    st.session_state.bt_date,
                )
                st.rerun()
            except MarketDataError as exc:
                st.session_state.bt_error = str(exc)
                st.rerun()

    # Symbol search lives inside the chart.
    if getattr(result, "symbol", None):
        symbol = str(result.symbol).strip().upper()
        if symbol and symbol != st.session_state.bt_symbol:
            try:
                _load_dataset(
                    symbol,
                    st.session_state.bt_interval,
                    st.session_state.bt_date,
                )
                st.rerun()
            except MarketDataError as exc:
                st.session_state.bt_error = str(exc)
                st.rerun()

    # Historical date lives inside the replay dock.
    if getattr(result, "date", None):
        try:
            new_date = date.fromisoformat(str(result.date))
            if new_date != st.session_state.bt_date:
                _load_dataset(
                    st.session_state.bt_symbol,
                    st.session_state.bt_interval,
                    new_date,
                )
                st.rerun()
        except (ValueError, MarketDataError) as exc:
            st.session_state.bt_error = str(exc)
            st.rerun()

    # Visual position -> Python backtest engine.
    event = getattr(result, "position_execute", None)
    if isinstance(event, dict):
        try:
            direction = str(event["direction"]).upper()
            entry = float(event["entry"])
            stop = float(event["stop"])
            target = float(event["target"])
            cursor = int(event.get("cursor", st.session_state.bt_cursor))

            plan = TradePlan(
                direction=direction,
                entry=entry,
                stop=stop,
                target=target,
                risk_amount=100.0,
            )
            valid, message = plan.validate()
            if not valid:
                raise ValueError(message)

            st.session_state.bt_cursor = max(
                0,
                min(cursor, len(st.session_state.bt_dataset) - 1),
            )
            st.session_state.bt_trade = {
                "direction": direction,
                "entry": entry,
                "stop": stop,
                "target": target,
                "risk_amount": 100.0,
                "created_index": st.session_state.bt_cursor,
            }
            st.session_state.bt_trade_result = None
            st.toast("Posición enviada al motor de backtesting.", icon="✅")
        except Exception as exc:
            st.session_state.bt_error = f"No pudimos ejecutar la posición: {exc}"


def _render_trade_status() -> None:
    trade = st.session_state.bt_trade
    frame = st.session_state.bt_dataset
    if not trade or frame is None or frame.empty:
        return

    plan = TradePlan(
        direction=trade["direction"],
        entry=float(trade["entry"]),
        stop=float(trade["stop"]),
        target=float(trade["target"]),
        risk_amount=float(trade["risk_amount"]),
    )

    start_index = int(trade["created_index"])
    candles = frame.iloc[start_index:].copy()
    result = evaluate_trade(plan, candles)
    st.session_state.bt_trade_result = result

    with st.expander("⚡ Operación enviada al motor AXION", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Dirección", trade["direction"])
        c2.metric("Entry", f"{trade['entry']:,.4f}")
        c3.metric("R:R", f"1 : {plan.rr:.2f}")
        c4.metric("Estado", result["status"])

        st.caption(
            f"MFE {result['mfe_r']:.2f}R · "
            f"MAE -{result['mae_r']:.2f}R · "
            f"P&L ${result['pnl']:+,.2f}"
        )


def render_backtesting_lab() -> None:
    apply_v2_theme()
    _init_state()

    # First verified load.
    if st.session_state.bt_dataset is None:
        try:
            with st.spinner("Cargando AXION REPLAY…"):
                _load_dataset(
                    st.session_state.bt_symbol,
                    st.session_state.bt_interval,
                    st.session_state.bt_date,
                )
        except MarketDataError as exc:
            st.error(str(exc))
            return

    if st.session_state.bt_error:
        st.error(st.session_state.bt_error)
        st.session_state.bt_error = None

    frame = st.session_state.bt_dataset
    market = st.session_state.bt_market

    if frame is None or market is None or frame.empty:
        st.error("No hay datos históricos disponibles.")
        return

    data = {
        "symbol": market.symbol,
        "symbol_label": market.display_symbol,
        "interval": st.session_state.bt_interval,
        "source": market.provider,
        "start_date": st.session_state.bt_date.isoformat(),
        "candles": _candles(frame),
        "volumes": _volumes(frame),
        "cursor": min(st.session_state.bt_cursor, len(frame) - 1),
        "context_cursor": min(80, len(frame) - 1),
        "workspace": {
            "name": "Workspace Trader",
            "fib_template": "AXION PRIME",
            "risk_template": "1.0%",
        },
    }

    result = render_axion_chart(
        data=data,
        key="axion_replay_terminal",
        height=860,
    )

    _handle_component_events(result)
    _render_trade_status()

    st.caption(
        "AXION Chart Component V2 · datos históricos verificados · "
        "replay, drawings y fullscreen viven dentro del terminal."
    )
