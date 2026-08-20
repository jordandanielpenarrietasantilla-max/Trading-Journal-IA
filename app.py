from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests
import streamlit as st

from core.api import (
    ensure_access_token,
    list_trades,
)
from core.config import (
    ADMIN_EMAIL,
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
    render_chat,
    render_lotage,
)

from ui_v2.ai_analysis import render_ai_analysis
from ui_v2.backtesting import render_backtesting_lab
from ui_v2.dashboard import render_v2_dashboard
from ui_v2.login import render_v2_auth
from ui_v2.market_tools import (
    render_news,
    render_sessions,
)
from ui_v2.profile import render_v2_profile
from ui_v2.projections import render_v2_projections
from ui_v2.psychotrading import render_psychotrading
from ui_v2.sidebar import render_v2_sidebar
from ui_v2.subscription import render_subscription


# =========================================================
# AXION PRIME X10 PRO
# APP PRINCIPAL
# =========================================================

# 1. OBLIGATORIO: Configuración inicial de la página
st.set_page_config(
    page_title="AXION PRIME X10 PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed", # Colapsado para dar prioridad al nuevo UI
)

REQUEST_TIMEOUT = 30

# =========================================================
# ESTILOS GLOBALES (BOCETO 4 / FULL SCREEN)
# =========================================================

# Obtenemos la página actual antes de aplicar los estilos
current_page = st.session_state.get("page", "Dashboard")

# Ocultamos el header y footer en TODA la app
global_css = """
    <style>
        header { display: none !important; }
        footer { display: none !important; }
    </style>
"""

# Si estamos en el Dashboard (donde va el nuevo mapa de calor), 
# ocultamos ABSOLUTAMENTE TODO el padding y la barra lateral de Streamlit
if current_page == "Dashboard":
    global_css += """
        <style>
            .block-container { padding: 0rem !important; max-width: 100% !important; }
            [data-testid="stSidebar"] { display: none !important; }
        </style>
    """
else:
    # Para las demás páginas, dejamos un poco de padding superior para que no se pegue al borde
    global_css += """
        <style>
            .block-container { padding-top: 2rem !important; }
        </style>
    """

st.markdown(global_css, unsafe_allow_html=True)


# =========================================================
# HELPERS
# =========================================================

def _as_dict(value: Any) -> dict[str, Any]:
    """Convierte de forma segura objetos de usuario o metadata en un diccionario estándar."""
    if isinstance(value, dict):
        return value
    try:
        dumped = value.model_dump()
        if isinstance(dumped, dict):
            return dumped
    except Exception:
        pass
    try:
        converted = dict(value)
        if isinstance(converted, dict):
            return converted
    except Exception:
        pass
    return {}


def _first_value(source: dict[str, Any], keys: tuple[str, ...], default: Any = None) -> Any:
    """Devuelve el primer valor no vacío encontrado."""
    for key in keys:
        value = source.get(key)
        if value not in (None, ""):
            return value
    return default


def _safe_float(value: Any, default: float) -> float:
    """Convierte un valor a float sin romper la aplicación."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _supabase_base_url() -> str:
    """Devuelve la URL de Supabase sin barra final."""
    return str(SUPABASE_URL or "").strip().rstrip("/")


def _supabase_api_key() -> str:
    """Devuelve la clave pública configurada."""
    return str(SUPABASE_KEY or "").strip()


# =========================================================
# REFRESCAR USUARIO DESDE SUPABASE
# =========================================================

def _refresh_authenticated_user() -> bool:
    """
    Consulta el usuario actual directamente en Supabase Auth.
    """
    if not st.session_state.get("authenticated", False):
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
                "Authorization": f"Bearer {access_token}",
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

    if not isinstance(payload, dict):
        return False

    user_payload = payload.get("user")
    user = user_payload if isinstance(user_payload, dict) else payload

    if not isinstance(user, dict) or not user.get("id"):
        return False

    st.session_state.user = user
    metadata = _as_dict(user.get("user_metadata", {}))
    st.session_state.user_metadata = metadata

    return True


# =========================================================
# SINCRONIZACIÓN DE PERFIL
# =========================================================

def _sync_profile_state() -> tuple[str, float, float]:
    """
    Sincroniza nombre, capital, meta y fotografía del perfil
    con st.session_state.
    """
    raw_user = st.session_state.get("user", {})
    user = _as_dict(raw_user)

    raw_metadata = (
        user.get("user_metadata")
        or user.get("raw_user_meta_data")
        or st.session_state.get("user_metadata")
        or {}
    )
    metadata = _as_dict(raw_metadata)
    st.session_state.user_metadata = metadata

    trader_name = _first_value(
        metadata,
        ("username", "full_name", "name", "display_name", "nombre_trader"),
        st.session_state.get("nombre_trader", "Trader Pro"),
    )

    capital_actual = _safe_float(
        _first_value(
            metadata,
            ("capital_actual", "current_capital"),
            st.session_state.get("capital_actual", 10000.0),
        ),
        10000.0,
    )

    capital_meta = _safe_float(
        _first_value(
            metadata,
            ("capital_meta", "target_capital"),
            st.session_state.get("capital_meta", 15000.0),
        ),
        15000.0,
    )

    avatar_value = _first_value(
        metadata,
        ("avatar_url", "profile_image", "profile_photo", "photo_url", "picture", "foto_perfil", "user_avatar", "user_photo"),
        None,
    )

    if avatar_value in (None, ""):
        avatar_value = _first_value(
            user,
            ("avatar_url", "profile_image", "profile_photo", "photo_url", "picture"),
            st.session_state.get("profile_image"),
        )

    st.session_state.nombre_trader = str(trader_name)
    st.session_state.capital_actual = capital_actual
    st.session_state.capital_meta = capital_meta

    if avatar_value not in (None, ""):
        st.session_state.profile_image = avatar_value
        st.session_state.profile_photo = avatar_value
        st.session_state.avatar_url = avatar_value
        st.session_state.user_avatar = avatar_value
        st.session_state.user_photo = avatar_value

    return (str(trader_name), capital_actual, capital_meta)


# =========================================================
# DATOS DEL JOURNAL
# =========================================================

def _load_trades() -> list[dict[str, Any]]:
    """Carga los trades desde Supabase."""
    try:
        trades = list_trades()
        return trades if isinstance(trades, list) else []
    except Exception as exc:
        message = str(exc or "").lower()
        if "jwt expired" in message or "sesión expiró" in message or "session expired" in message:
            st.session_state.flash_error = "Tu sesión expiró. Inicia sesión nuevamente para continuar."
            st.session_state.authenticated = False
            st.session_state.access_token = ""
            st.rerun()

        st.error("No pudimos cargar tus operaciones en este momento. Inténtalo nuevamente.")
        return []


# =========================================================
# ACCESO Y NAVEGACIÓN
# =========================================================

def _redirect_expired_membership() -> None:
    """Valida la membresía PRO."""
    membership = get_membership_info()
    allowed_pages = {"Dashboard", "Modificar perfil", "AXION PRIME PRO"}
    current_page = str(st.session_state.get("page", "Dashboard"))

    if membership.is_expired and current_page not in allowed_pages:
        st.session_state.page = "AXION PRIME PRO"
        st.warning("Tu plan PRO venció. Renueva tu membresía para continuar utilizando las funciones premium.")
        st.rerun()


# =========================================================
# PÁGINAS LEGALES PÚBLICAS
# =========================================================

LEGAL_PAGE_CSS = """...""" # Mantenemos tu variable intacta (la omito aquí por brevedad, pero déjala igual en tu código real)

def _public_path() -> str:
    try:
        current_url = str(st.context.url or "").strip()
        path = urlparse(current_url).path
    except Exception:
        path = ""
    return str(path or "/").strip().lower().rstrip("/") or "/"

def _legal_contact_email() -> str:
    return str(ADMIN_EMAIL or "").strip() or "soporte@axionprime.app"

def _legal_document(path: str) -> tuple[str, str] | None:
    # Mantenemos tus strings privacy_body, terms_body, refund_body iguales.
    # ...
    pass 

def _render_public_legal_page(title: str, body: str) -> None:
    # Tu código HTML de página legal igual
    pass

def _handle_public_page() -> None:
    document = _legal_document(_public_path())
    if document is None:
        return
    title, body = document
    _render_public_legal_page(title, body)
    st.stop()


# =========================================================
# INICIALIZACIÓN Y AUTENTICACIÓN
# =========================================================

_handle_public_page()
validate_config()
init_state()

if not st.session_state.get("authenticated", False):
    render_v2_auth()
    st.stop()

_refresh_authenticated_user()

if not st.session_state.get("authenticated", False):
    st.session_state.flash_error = "Tu sesión expiró. Inicia sesión nuevamente para continuar."
    st.rerun()


# =========================================================
# PERFIL, MEMBRESÍA Y DATOS
# =========================================================

trader_name, capital_actual, capital_meta = _sync_profile_state()
_redirect_expired_membership()

# Renderizamos la sidebar nativa SI NO estamos en el Dashboard
if current_page != "Dashboard":
    render_v2_sidebar()

trades = _load_trades()
df = prepare_df(trades)


# =========================================================
# RUTEO DE PÁGINAS
# =========================================================

if current_page == "Dashboard":
    render_v2_dashboard(df, trader_name=trader_name, initial_capital=capital_actual)

elif current_page == "Modificar perfil":
    render_v2_profile()

elif current_page == "Registrar Trade":
    render_register_trade()

elif current_page == "Track Record":
    render_track_record(df)

elif current_page == "Chat IA":
    render_chat(df)

elif current_page == "Backtesting Lab":
    render_backtesting_lab()

elif current_page == "Psicotrading":
    render_psychotrading(df)

elif current_page == "Análisis IA":
    render_ai_analysis(df)

elif current_page == "Proyecciones":
    render_v2_projections()

elif current_page == "Lotaje":
    render_lotage()

elif current_page == "Sesiones":
    render_sessions()

elif current_page == "Noticias":
    render_news()

elif current_page == "AXION PRIME PRO":
    render_subscription()

else:
    st.session_state.page = "Dashboard"
    st.rerun()
