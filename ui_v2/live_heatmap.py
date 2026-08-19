from __future__ import annotations

import streamlit as st

from components.axion_heatmap import render_axion_live_heatmap


def _init_live_state() -> None:
    defaults = {
        "live_symbol": "XAUUSD",
        "live_timeframe": "15m",
        "live_heatmap_note": (
            "Terminal AXION LIVE activa · La profundidad real se habilitará al conectar Market Depth."
        ),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _handle_result(result) -> None:
    if result is None:
        return

    symbol = getattr(result, "symbol", None)
    if symbol and symbol != st.session_state.live_symbol:
        st.session_state.live_symbol = symbol
        st.rerun()

    timeframe = getattr(result, "timeframe", None)
    if timeframe and timeframe != st.session_state.live_timeframe:
        st.session_state.live_timeframe = timeframe
        st.rerun()

    navigate = getattr(result, "navigate", None)
    if navigate:
        # Solo registramos la intención por ahora.
        # El routing final se conecta desde ui_v2/dashboard.py.
        st.session_state.live_requested_navigation = navigate


def render_live_heatmap() -> None:
    _init_live_state()

    result = render_axion_live_heatmap(
        symbol=st.session_state.live_symbol,
        timeframe=st.session_state.live_timeframe,
        key="axion_live_heatmap_workspace",
        height=860,
    )
    _handle_result(result)
