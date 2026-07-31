from __future__ import annotations

from typing import Any

import streamlit as st

from core.api import list_trades
from core.config import validate_config
from core.metrics import prepare_df
from core.profile import (
    get_profile_capital,
    get_profile_name,
)
from core.state import init_state
from core.styles import apply_styles

from ui.auth import render_auth
from ui.dashboard import render_dashboard
from ui.profile import render_profile
from ui.sidebar import render_sidebar
from ui.track_record import render_track_record
from ui.trades import render_register_trade
from ui.tools import (
    render_analysis,
    render_chat,
    render_lotage,
    render_projections,
    render_psychology,
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


def initialize_application() -> None:
    """
    Valida la configuración, prepara el estado de Streamlit
    y aplica los estilos visuales de AXION PRIME.
    """

    validate_config()
    init_state()
    apply_styles()


# =========================================================
# AUTENTICACIÓN
# =========================================================


def user_is_authenticated() -> bool:
    """
    Comprueba si existe una sesión autenticada.
    """

    return bool(
        st.session_state.get(
            "authenticated",
            False,
        )
    )


def render_login_if_required() -> None:
    """
    Muestra el login cuando no existe una sesión activa.
    """

    if user_is_authenticated():
        return

    render_auth()
    st.stop()


# =========================================================
# DATOS DEL USUARIO
# =========================================================


def get_trader_name() -> str:
    """
    Obtiene el nombre del perfil.

    Usa core.profile para mantener compatibilidad
    con el editor de perfil.
    """

    try:
        trader_name = str(
            get_profile_name()
            or ""
        ).strip()

        if trader_name:
            return trader_name

    except Exception:
        pass

    session_name = str(
        st.session_state.get(
            "nombre_trader",
            "",
        )
        or ""
    ).strip()

    if session_name:
        return session_name

    user = st.session_state.get(
        "user",
        {},
    )

    if isinstance(user, dict):
        metadata = user.get(
            "user_metadata",
            {},
        )

        if isinstance(metadata, dict):
            possible_names = [
                metadata.get("username"),
                metadata.get("full_name"),
                metadata.get("display_name"),
                metadata.get("name"),
                metadata.get("nombre"),
                metadata.get("nombre_trader"),
            ]

            for value in possible_names:
                clean_value = str(
                    value or ""
                ).strip()

                if clean_value:
                    return clean_value

    return "Trader Pro"


def get_initial_capital() -> float:
    """
    Obtiene el capital actual del perfil.
    """

    try:
        return float(
            get_profile_capital()
        )

    except Exception:
        try:
            return float(
                st.session_state.get(
                    "capital_actual",
                    10000.0,
                )
                or 10000.0
            )

        except (TypeError, ValueError):
            return 10000.0


# =========================================================
# DIAGNÓSTICO SEGURO
# =========================================================


def _safe_length(
    value: Any,
) -> int:
    """
    Devuelve únicamente el tamaño de un valor.

    Nunca muestra claves ni tokens.
    """

    if value is None:
        return 0

    try:
        return len(
            str(value)
        )

    except Exception:
        return 0


def render_supabase_diagnostics(
    error: Exception,
) -> None:
    """
    Muestra un diagnóstico seguro cuando falla la carga
    de operaciones.
    """

    error_message = str(
        error or "Error desconocido"
    ).strip()

    if len(error_message) > 1800:
        error_message = (
            error_message[:1800]
            + "\n\n[Mensaje recortado]"
        )

    try:
        supabase_key = st.secrets.get(
            "SUPABASE_KEY",
            "",
        )

    except Exception:
        supabase_key = ""

    access_token = st.session_state.get(
        "access_token",
        "",
    )

    refresh_token = st.session_state.get(
        "refresh_token",
        "",
    )

    user = st.session_state.get(
        "user",
        {},
    )

    st.error(
        "No se pudieron cargar los trades desde Supabase."
    )

    with st.expander(
        "🔧 Ver diagnóstico técnico",
        expanded=True,
    ):
        st.code(
            error_message,
            language="text",
        )

        st.warning(
            "DIAGNÓSTICO SEGURO\n\n"
            f"SUPABASE_KEY: {_safe_length(supabase_key)} caracteres\n\n"
            f"ACCESS_TOKEN: {_safe_length(access_token)} caracteres\n\n"
            f"REFRESH_TOKEN: {_safe_length(refresh_token)} caracteres\n\n"
            f"USER: {_safe_length(user)} caracteres"
        )

        st.caption(
            "Este diagnóstico solamente muestra tamaños. "
            "No expone claves, tokens ni datos sensibles."
        )


# =========================================================
# CARGAR OPERACIONES
# =========================================================


def load_trades() -> list[dict[str, Any]]:
    """
    Carga los trades del usuario desde Supabase.

    Si ocurre un error, devuelve una lista vacía para
    mantener la aplicación disponible.
    """

    try:
        result = list_trades()

        if result is None:
            return []

        if not isinstance(
            result,
            list,
        ):
            raise RuntimeError(
                "list_trades() devolvió un formato inválido. "
                "Se esperaba una lista."
            )

        return [
            trade
            for trade in result
            if isinstance(
                trade,
                dict,
            )
        ]

    except Exception as exc:
        render_supabase_diagnostics(
            exc
        )

        return []


def prepare_trades_dataframe(
    trades: list[dict[str, Any]],
):
    """
    Convierte los trades en un DataFrame preparado.
    """

    try:
        return prepare_df(
            trades
        )

    except Exception as exc:
        st.error(
            "No se pudieron preparar los datos "
            "de las operaciones."
        )

        with st.expander(
            "Ver detalle técnico",
            expanded=False,
        ):
            st.code(
                str(exc),
                language="text",
            )

        return prepare_df(
            []
        )


# =========================================================
# NAVEGACIÓN
# =========================================================


def render_current_page(
    df,
    trader_name: str,
) -> None:
    """
    Renderiza la sección seleccionada en el sidebar.
    """

    page = st.session_state.get(
        "page",
        "Dashboard",
    )

    if page == "Dashboard":
        render_dashboard(
            df,
            trader_name=trader_name,
            initial_capital=get_initial_capital(),
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

    elif page == "Modificar perfil":
        render_profile()

    else:
        st.session_state.page = "Dashboard"
        st.rerun()


# =========================================================
# EJECUCIÓN PRINCIPAL
# =========================================================


def main() -> None:
    """
    Punto de entrada principal de AXION PRIME.
    """

    initialize_application()

    render_login_if_required()

    render_sidebar()

    trades = load_trades()

    df = prepare_trades_dataframe(
        trades
    )

    trader_name = get_trader_name()

    render_current_page(
        df,
        trader_name,
    )


if __name__ == "__main__":
    main()
