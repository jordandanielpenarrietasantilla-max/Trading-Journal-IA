from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from core.api import (
    ensure_access_token,
    list_trades,
)
from core.config import (
    SUPABASE_KEY,
    SUPABASE_URL,
    validate_config,
)
from core.membership import get_membership_info
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
from ui_v2.market_tools import (
    render_news,
    render_sessions,
)
from ui_v2.profile import render_v2_profile
from ui_v2.sidebar import render_v2_sidebar
from ui_v2.subscription import render_subscription


# =========================================================
# AXION PRIME X10 PRO
# APP PRINCIPAL
# =========================================================


st.set_page_config(
    page_title="AXION PRIME X10 PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


REQUEST_TIMEOUT = 30


# =========================================================
# HELPERS
# =========================================================


def _as_dict(
    value: Any,
) -> dict[str, Any]:
    """
    Convierte de forma segura objetos de usuario o metadata
    en un diccionario estándar.
    """

    if isinstance(
        value,
        dict,
    ):
        return value

    try:
        dumped = value.model_dump()

        if isinstance(
            dumped,
            dict,
        ):
            return dumped

    except Exception:
        pass

    try:
        converted = dict(
            value
        )

        if isinstance(
            converted,
            dict,
        ):
            return converted

    except Exception:
        pass

    return {}


def _first_value(
    source: dict[str, Any],
    keys: tuple[str, ...],
    default: Any = None,
) -> Any:
    """
    Devuelve el primer valor no vacío encontrado.
    """

    for key in keys:
        value = source.get(
            key
        )

        if value not in (
            None,
            "",
        ):
            return value

    return default


def _safe_float(
    value: Any,
    default: float,
) -> float:
    """
    Convierte un valor a float sin romper la aplicación.
    """

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _supabase_base_url() -> str:
    """
    Devuelve la URL de Supabase sin barra final.
    """

    return str(
        SUPABASE_URL
        or ""
    ).strip().rstrip("/")


def _supabase_api_key() -> str:
    """
    Devuelve la clave pública configurada.
    """

    return str(
        SUPABASE_KEY
        or ""
    ).strip()


# =========================================================
# REFRESCAR USUARIO DESDE SUPABASE
# =========================================================


def _refresh_authenticated_user() -> bool:
    """
    Consulta el usuario actual directamente en Supabase Auth.

    Esto es importante porque los planes PRO se guardan en
    auth.users.raw_user_meta_data. Al volver a iniciar sesión,
    esta función garantiza que Streamlit reciba los metadatos
    más recientes:

        plan
        membership_status
        plan_started_at
        plan_expires_at
        payment_provider

    Devuelve True si logró actualizar la sesión.
    """

    if not st.session_state.get(
        "authenticated",
        False,
    ):
        return False

    base_url = _supabase_base_url()
    api_key = _supabase_api_key()

    if not base_url or not api_key:
        return False

    try:
        access_token = ensure_access_token()

    except Exception:
        return False

    if not access_token:
        return False

    try:
        response = requests.get(
            f"{base_url}/auth/v1/user",
            headers={
                "apikey": api_key,
                "Authorization": (
                    f"Bearer {access_token}"
                ),
                "Accept": "application/json",
            },
            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException:
        return False

    if response.status_code >= 400:
        return False

    try:
        payload = response.json()

    except ValueError:
        return False

    if not isinstance(
        payload,
        dict,
    ):
        return False

    user_payload = payload.get(
        "user"
    )

    if isinstance(
        user_payload,
        dict,
    ):
        user = user_payload

    else:
        user = payload

    if not isinstance(
        user,
        dict,
    ):
        return False

    if not user.get(
        "id"
    ):
        return False

    st.session_state.user = user

    metadata = _as_dict(
        user.get(
            "user_metadata",
            {},
        )
    )

    st.session_state.user_metadata = (
        metadata
    )

    return True


# =========================================================
# SINCRONIZACIÓN DE PERFIL
# =========================================================


def _sync_profile_state() -> tuple[str, float, float]:
    """
    Sincroniza nombre, capital, meta y fotografía del perfil
    con st.session_state.

    También conserva los metadatos PRO ya cargados desde
    Supabase Auth.
    """

    raw_user = st.session_state.get(
        "user",
        {},
    )

    user = _as_dict(
        raw_user
    )

    raw_metadata = (
        user.get(
            "user_metadata"
        )
        or user.get(
            "raw_user_meta_data"
        )
        or st.session_state.get(
            "user_metadata"
        )
        or {}
    )

    metadata = _as_dict(
        raw_metadata
    )

    st.session_state.user_metadata = (
        metadata
    )

    trader_name = _first_value(
        metadata,
        (
            "username",
            "full_name",
            "name",
            "display_name",
            "nombre_trader",
        ),
        st.session_state.get(
            "nombre_trader",
            "Trader Pro",
        ),
    )

    capital_actual = _safe_float(
        _first_value(
            metadata,
            (
                "capital_actual",
                "current_capital",
            ),
            st.session_state.get(
                "capital_actual",
                10000.0,
            ),
        ),
        10000.0,
    )

    capital_meta = _safe_float(
        _first_value(
            metadata,
            (
                "capital_meta",
                "target_capital",
            ),
            st.session_state.get(
                "capital_meta",
                15000.0,
            ),
        ),
        15000.0,
    )

    avatar_value = _first_value(
        metadata,
        (
            "avatar_url",
            "profile_image",
            "profile_photo",
            "photo_url",
            "picture",
            "foto_perfil",
            "user_avatar",
            "user_photo",
        ),
        None,
    )

    if avatar_value in (
        None,
        "",
    ):
        avatar_value = _first_value(
            user,
            (
                "avatar_url",
                "profile_image",
                "profile_photo",
                "photo_url",
                "picture",
            ),
            st.session_state.get(
                "profile_image",
            ),
        )

    st.session_state.nombre_trader = str(
        trader_name
    )

    st.session_state.capital_actual = (
        capital_actual
    )

    st.session_state.capital_meta = (
        capital_meta
    )

    if avatar_value not in (
        None,
        "",
    ):
        st.session_state.profile_image = (
            avatar_value
        )

        st.session_state.profile_photo = (
            avatar_value
        )

        st.session_state.avatar_url = (
            avatar_value
        )

        st.session_state.user_avatar = (
            avatar_value
        )

        st.session_state.user_photo = (
            avatar_value
        )

    return (
        str(
            trader_name
        ),
        capital_actual,
        capital_meta,
    )


# =========================================================
# DATOS DEL JOURNAL
# =========================================================


def _load_trades() -> list[dict[str, Any]]:
    """
    Carga los trades desde Supabase sin detener toda la app
    si ocurre un error.
    """

    try:
        trades = list_trades()

        if isinstance(
            trades,
            list,
        ):
            return trades

        return []

    except Exception as exc:
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

        return []


# =========================================================
# ACCESO Y NAVEGACIÓN
# =========================================================


def _redirect_expired_membership() -> None:
    """
    Si el plan ya venció, permite entrar a la sección de
    membresía, perfil y dashboard, pero evita conservar una
    página PRO seleccionada.

    El bloqueo completo de funciones se conectará después
    usando require_pro_access().
    """

    membership = get_membership_info()

    allowed_pages = {
        "Dashboard",
        "Modificar perfil",
        "AXION PRIME PRO",
    }

    current_page = str(
        st.session_state.get(
            "page",
            "Dashboard",
        )
    )

    if (
        membership.is_expired
        and current_page not in allowed_pages
    ):
        st.session_state.page = (
            "AXION PRIME PRO"
        )

        st.warning(
            "Tu plan PRO venció. Renueva tu membresía "
            "para continuar utilizando las funciones premium."
        )

        st.rerun()


# =========================================================
# INICIALIZACIÓN
# =========================================================


validate_config()
init_state()


# =========================================================
# AUTENTICACIÓN
# =========================================================


if not st.session_state.get(
    "authenticated",
    False,
):
    render_v2_auth()
    st.stop()


# =========================================================
# REFRESCAR DATOS DEL USUARIO
# =========================================================


_refresh_authenticated_user()


# =========================================================
# PERFIL Y MEMBRESÍA
# =========================================================


trader_name, capital_actual, capital_meta = (
    _sync_profile_state()
)

_redirect_expired_membership()

render_v2_sidebar()


# =========================================================
# DATOS DEL JOURNAL
# =========================================================


trades = _load_trades()

df = prepare_df(
    trades
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


elif page == "Sesiones":

    render_sessions()


elif page == "Noticias":

    render_news()


elif page == "AXION PRIME PRO":

    render_subscription()


else:

    st.session_state.page = (
        "Dashboard"
    )

    st.rerun()
