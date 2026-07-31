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
from ui.trades import render_register, render_track_record
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
# AUTENTICACIÓN
# =========================================================

if not st.session_state.authenticated:

    render_auth()

    st.stop()


# =========================================================
# MENÚ LATERAL
# =========================================================

render_sidebar()


# =========================================================
# CARGAR TRADES DEL USUARIO
# =========================================================

try:

    trades = list_trades()

except Exception as exc:

    trades = []

    st.error(
        f"No se pudieron cargar los trades: {exc}"
    )


# Convertir los datos recibidos de Supabase
# en un DataFrame preparado para las métricas.

df = prepare_df(trades)


# =========================================================
# NAVEGACIÓN
# =========================================================

page = st.session_state.page


if page == "Dashboard":

    render_dashboard(df)


elif page == "Registrar Trade":

    render_register()


elif page == "Track Record":

    render_track_record(df)


elif page == "Chat IA":

    render_chat(df)


elif page == "Psicotrading":

    render_psychology(df)


elif page == "Análisis IA":

    render_analysis()


elif page == "Proyecciones":

    render_projections()


elif page == "Lotaje":

    render_lotage()


else:

    st.session_state.page = "Dashboard"

    st.rerun()
