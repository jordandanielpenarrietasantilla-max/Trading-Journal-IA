from __future__ import annotations

import streamlit as st

from core.api import list_trades
from core.config import validate_config
from core.metrics import prepare_df
from core.state import init_state

from ui.track_record import render_track_record
from ui.trades import render_register_trade
from ui.tools import (
    render_analysis,
    render_chat,
    render_lotage,
    render_projections,
    render_psychology,
)

from ui_v2.dashboard import render_v2_dashboard
from ui_v2.login import render_v2_auth
from ui_v2.profile import render_v2_profile
from ui_v2.sidebar import render_v2_sidebar


# =========================================================
# AXION PRIME X10 PRO
# ARCHIVO PRINCIPAL CON INTERFAZ V2
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


# =========================================================
# AUTENTICACIÓN V2
# =========================================================


if not st.session_state.get(
    "authenticated",
    False,
):
    render_v2_auth()
    st.stop()


# =========================================================
# SIDEBAR V2
# =========================================================


render_v2_sidebar()


# =========================================================
# CARGAR OPERACIONES
# =========================================================


try:
    trades = list_trades()

except Exception as exc:
    trades = []

    st.error(
        "No se pudieron cargar los trades desde Supabase."
    )

    with st.expander(
        "Ver detalle técnico",
        expanded=False,
    ):
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
    "user",
    {},
)

metadata = {}

if isinstance(
    user,
    dict,
):
    metadata = (
        user.get(
            "user_metadata",
            {},
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
    or st.session_state.get(
        "nombre_trader",
        "Trader Pro",
    )
)


capital_actual = float(
    metadata.get(
        "capital_actual",
        st.session_state.get(
            "capital_actual",
            10000.0,
        ),
    )
    or 10000.0
)


capital_meta = float(
    metadata.get(
        "capital_meta",
        st.session_state.get(
            "capital_meta",
            15000.0,
        ),
    )
    or 15000.0
)


st.session_state.nombre_trader = (
    trader_name
)

st.session_state.capital_actual = (
    capital_actual
)

st.session_state.capital_meta = (
    capital_meta
)


# =========================================================
# NAVEGACIÓN
# =========================================================


page = st.session_state.get(
    "page",
    "Dashboard",
)


if page == "Dashboard":
    render_v2_dashboard(
        df,
        trader_name=trader_name,
        initial_capital=capital_actual,
    )


elif page == "Modificar perfil":
    render_v2_profile()


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
