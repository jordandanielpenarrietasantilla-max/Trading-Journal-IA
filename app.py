from __future__ import annotations

import streamlit as st

from core.config import validate_config
from core.state import init_state
from core.styles import apply_styles
from core.api import list_trades
from core.metrics import prepare_df

from ui.auth import render_auth
from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard
from ui.trades import render_register_trade
from ui.track_record import render_track_record
from ui.tools import (
    render_chat,
    render_psychology,
    render_analysis,
    render_projections,
    render_lotage,
)


# =========================================================
# AXION PRIME X10 PRO
# ARCHIVO PRINCIPAL
# =========================================================

st.set_page_config(
    page_title="AXION PRIME X10 PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CONFIGURACIÓN INICIAL
# =========================================================

validate_config()
init_state()
apply_styles()


# =========================================================
# LOGIN
# =========================================================

if not st.session_state.authenticated:
    render_auth()
    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

render_sidebar()


# =========================================================
# CARGAR TRADES
# =========================================================

try:
    trades = list_trades()

except Exception as exc:
    trades = []

    st.error(
        "No se pudieron cargar los trades desde Supabase."
    )

    st.code(
        str(exc)
    )


df = prepare_df(
    trades
)


# =========================================================
# DATOS DEL USUARIO
# =========================================================

user = st.session_state.get(
    "user"
)

trader_name = "Trader Pro"

if isinstance(
    user,
    dict,
):
    metadata = (
        user.get(
            "user_metadata",
            {}
        )
        or {}
    )

    trader_name = (
        metadata.get(
            "username"
        )
        or metadata.get(
            "full_name"
        )
        or metadata.get(
            "name"
        )
        or "Trader Pro"
    )


# =========================================================
# NAVEGACIÓN
# =========================================================

page = st.session_state.get(
    "page",
    "Dashboard",
)


if page == "Dashboard":

    render_dashboard(
        df,
        trader_name=trader_name,
        initial_capital=float(
            st.session_state.get(
                "capital_actual",
                10000.0,
            )
        ),
    )


elif page == "Registrar Trade":

    render_register_trade()


elif page == "Track Record":

    render_track_record(
        df
    )


elif page == "Chat IA":

    render_chat(
        df
    )


elif page == "Psicotrading":

    render_psychology(
        df
    )


elif page == "Análisis IA":

    render_analysis()


elif page == "Proyecciones":

    render_projections()


elif page == "Lotaje":

    render_lotage()


else:

    st.session_state.page = (
        "Dashboard"
    )

    st.rerun()
