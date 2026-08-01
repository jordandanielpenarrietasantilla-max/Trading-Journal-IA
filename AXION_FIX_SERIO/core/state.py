from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# ESTADO GENERAL DE LA APLICACIÓN
# =========================================================

DEFAULTS = {

    # AUTENTICACIÓN
    "authenticated": False,
    "user": None,
    "access_token": "",
    "refresh_token": "",

    # NAVEGACIÓN
    "page": "Dashboard",

    # CUENTA
    "capital_actual": 10000.0,
    "capital_meta": 15000.0,

    # TRACK RECORD
    "selected_day": None,

    # IA
    "scan_data": None,

    # MENSAJES
    "flash_success": "",
    "flash_error": "",

    # FORMULARIO DE TRADE
    "entry": 0.0,
    "sl": 0.0,
    "tp": 0.0,
}


# =========================================================
# INICIALIZAR ESTADO
# =========================================================

def init_state() -> None:
    """
    Crea las variables de session_state
    si todavía no existen.
    """

    for key, value in DEFAULTS.items():

        if key not in st.session_state:

            st.session_state[key] = value


# =========================================================
# LIMPIAR SESIÓN
# =========================================================

def clear_auth() -> None:
    """
    Elimina los datos de autenticación
    cuando el usuario cierra sesión.
    """

    st.session_state.authenticated = False

    st.session_state.user = None

    st.session_state.access_token = ""

    st.session_state.refresh_token = ""

    st.session_state.page = "Dashboard"

    st.session_state.scan_data = None

    st.session_state.flash_success = ""

    st.session_state.flash_error = ""


# =========================================================
# LIMPIAR FORMULARIO
# =========================================================

def clear_trade_form() -> None:
    """
    Reinicia Entry, Stop Loss y Take Profit.
    """

    st.session_state.entry = 0.0

    st.session_state.sl = 0.0

    st.session_state.tp = 0.0

    st.session_state.scan_data = None
