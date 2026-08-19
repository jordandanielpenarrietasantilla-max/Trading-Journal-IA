from __future__ import annotations

import streamlit as st

from components.axion_heatmap import render_axion_live_heatmap


def _init_live_state() -> None:
    defaults = {
        "live_symbol": "XAUUSD",
        "live_timeframe": "15m",
        "live_heatmap_note": (
            "La interfaz está lista. La profundidad real del mercado todavía no está conectada."
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

    st.markdown(
        """
        <style>
          .axion-live-intro{
            margin:0 0 12px 0;
            padding:14px 16px;
            border:1px solid rgba(69,108,167,.22);
            border-radius:12px;
            background:linear-gradient(135deg,rgba(4,13,27,.96),rgba(8,11,22,.96));
          }
          .axion-live-intro strong{color:#eef6ff}
          .axion-live-intro span{color:#64d8ea}
          .axion-live-intro p{
            margin:5px 0 0 0;color:#7f91ac;font-size:12px
          }
        </style>
        <div class="axion-live-intro">
          <strong>AXION LIVE · <span>HEATMAP ORDER FLOW</span></strong>
          <p>
            Módulo preparado para datos de profundidad reales.
            AXION no mostrará liquidez sintética ni inventada.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result = render_axion_live_heatmap(
        symbol=st.session_state.live_symbol,
        timeframe=st.session_state.live_timeframe,
        key="axion_live_heatmap_workspace",
        height=920,
    )
    _handle_result(result)

    st.caption(
        "Fase 1 · Interfaz del Heatmap. "
        "Siguiente paso: conectar una fuente real de order book / market depth."
    )
