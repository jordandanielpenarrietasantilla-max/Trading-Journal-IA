from __future__ import annotations

import html
from typing import Any

import streamlit as st

from core.config import ADMIN_EMAIL
from core.profile import (
    get_avatar_url,
    get_profile_capital,
    get_profile_name,
    get_profile_target,
)
from core.state import clear_auth


# =========================================================
# AXION PRIME X10 PRO
# SIDEBAR COMPLETO
# =========================================================


MAIN_NAVIGATION = [
    ("📊", "Dashboard"),
    ("➕", "Registrar Trade"),
    ("📕", "Track Record"),
    ("🤖", "Chat IA"),
]

ADVANCED_NAVIGATION = [
    ("🧠", "Psicotrading"),
    ("🔍", "Análisis IA"),
    ("📈", "Proyecciones"),
    ("🧮", "Lotaje"),
]

SETTINGS_NAVIGATION = [
    ("⚙️", "Modificar perfil"),
]


# =========================================================
# UTILIDADES DEL USUARIO
# =========================================================


def _user_value(
    user: Any,
    key: str,
    default: Any = "",
) -> Any:
    """
    Lee valores tanto de diccionarios como de objetos.
    """

    if user is None:
        return default

    if isinstance(user, dict):
        return user.get(
            key,
            default,
        )

    return getattr(
        user,
        key,
        default,
    )


def _current_user() -> Any:
    """
    Devuelve el usuario autenticado.
    """

    return st.session_state.get(
        "user",
        {},
    )


def _email() -> str:
    """
    Devuelve el correo del usuario autenticado.
    """

    user = _current_user()

    value = _user_value(
        user,
        "email",
        "",
    )

    return str(
        value or ""
    ).strip()


def _trader_name() -> str:
    """
    Devuelve el nombre actual del trader.
    """

    try:
        profile_name = get_profile_name()

        if profile_name:
            return str(
                profile_name
            ).strip()

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

    return "Trader Pro"


def _capital_actual() -> float:
    """
    Devuelve el capital actual del perfil.
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


def _capital_meta() -> float:
    """
    Devuelve la meta de capital.
    """

    try:
        return float(
            get_profile_target()
        )

    except Exception:
        try:
            return float(
                st.session_state.get(
                    "capital_meta",
                    15000.0,
                )
                or 15000.0
            )

        except (TypeError, ValueError):
            return 15000.0


def _avatar_url() -> str:
    """
    Devuelve únicamente una URL válida y pequeña.

    Nunca muestra imágenes Base64 dentro del token.
    """

    try:
        avatar = str(
            get_avatar_url()
            or ""
        ).strip()

    except Exception:
        avatar = str(
            st.session_state.get(
                "avatar_url",
                "",
            )
            or ""
        ).strip()

    if not avatar:
        return ""

    if avatar.startswith(
        "data:"
    ):
        return ""

    if len(avatar) > 3000:
        return ""

    return avatar


def _initials(
    name: str,
) -> str:
    """
    Genera iniciales cuando el perfil no tiene fotografía.
    """

    words = [
        word
        for word in str(name).split()
        if word
    ]

    if not words:
        return "AX"

    if len(words) == 1:
        return words[0][:2].upper()

    return (
        words[0][0]
        + words[-1][0]
    ).upper()


def _is_admin() -> bool:
    """
    Verifica si el usuario coincide con ADMIN_EMAIL.
    """

    current_email = _email().lower()

    admin_email = str(
        ADMIN_EMAIL or ""
    ).strip().lower()

    return bool(
        current_email
        and admin_email
        and current_email == admin_email
    )


def _navigate(
    page_name: str,
) -> None:
    """
    Cambia la página seleccionada.
    """

    st.session_state.page = page_name
    st.rerun()


# =========================================================
# LOGOTIPO
# =========================================================


def _render_brand() -> None:
    """
    Muestra la identidad principal de AXION.
    """

    st.html(
        """
        <div class="ax-brand">

            <div class="ax-logo">
                A
            </div>

            <div>
                <b>
                    AXION PRIME
                </b>

                <small>
                    PERFORMANCE COMMAND OS · X10
                </small>
            </div>

            <div class="ax-brand-online"></div>

        </div>
        """
    )


# =========================================================
# AVATAR
# =========================================================


def _avatar_html(
    trader_name: str,
) -> str:
    """
    Construye la foto del perfil o las iniciales.
    """

    avatar_url = _avatar_url()

    if avatar_url:
        safe_avatar_url = html.escape(
            avatar_url,
            quote=True,
        )

        return f"""
        <div class="ax-profile-avatar ax-profile-photo">
            <img
                src="{safe_avatar_url}"
                alt="Foto del perfil"
                loading="lazy"
            >
        </div>
        """

    initials = html.escape(
        _initials(
            trader_name
        )
    )

    return f"""
    <div class="ax-profile-avatar">
        {initials}
    </div>
    """


# =========================================================
# TARJETA DEL PERFIL
# =========================================================


def _render_profile() -> None:
    """
    Muestra el perfil, capital y fotografía.
    """

    trader_name = _trader_name()
    email = _email()

    safe_name = html.escape(
        trader_name
    )

    safe_email = html.escape(
        email
    )

    capital_actual = _capital_actual()
    capital_meta = _capital_meta()

    if capital_meta > 0:
        progress = (
            capital_actual
            / capital_meta
            * 100
        )
    else:
        progress = 0.0

    progress = min(
        100.0,
        max(
            0.0,
            progress,
        ),
    )

    role = (
        "FOUNDER"
        if _is_admin()
        else "TRADER"
    )

    avatar = _avatar_html(
        trader_name
    )

    st.html(
        f"""
        <div class="ax-profile">

            <div class="ax-profile-top">

                {avatar}

                <div class="ax-profile-identity">

                    <div class="ax-profile-name-row">

                        <strong>
                            {safe_name}
                        </strong>

                        <span class="ax-profile-role">
                            {role}
                        </span>

                    </div>

                    <div class="ax-profile-email">
                        {safe_email}
                    </div>

                </div>

            </div>

            <div class="ax-profile-capital-row">

                <div>

                    <div class="ax-profile-capital">
                        ${capital_actual:,.2f}
                    </div>

                    <div class="ax-profile-capital-label">
                        CAPITAL ACTUAL
                    </div>

                </div>

                <div class="ax-profile-target">
                    META ${capital_meta:,.0f}
                </div>

            </div>

            <div class="ax-progress-track">

                <div
                    class="ax-progress-value"
                    style="width:{progress:.1f}%"
                ></div>

            </div>

            <div class="ax-progress-labels">

                <span>
                    {progress:.1f}% DE LA META
                </span>

                <span>
                    ${capital_meta:,.0f}
                </span>

            </div>

        </div>
        """
    )

    if st.button(
        "⚙️ Modificar perfil",
        key="sidebar_edit_profile_top",
        use_container_width=True,
        type="secondary",
    ):
        _navigate(
            "Modificar perfil"
        )


# =========================================================
# NAVEGACIÓN
# =========================================================


def _navigation_button(
    icon: str,
    page_name: str,
) -> None:
    """
    Muestra un botón de navegación.
    """

    current_page = st.session_state.get(
        "page",
        "Dashboard",
    )

    is_active = (
        current_page
        == page_name
    )

    clicked = st.button(
        f"{icon}  {page_name}",
        key=f"sidebar_nav_{page_name}",
        use_container_width=True,
        type=(
            "primary"
            if is_active
            else "secondary"
        ),
    )

    if clicked:
        _navigate(
            page_name
        )


def _render_navigation_section(
    title: str,
    items: list[tuple[str, str]],
) -> None:
    """
    Muestra una sección completa del menú.
    """

    safe_title = html.escape(
        title
    )

    st.html(
        f"""
        <div class="ax-section-title">
            {safe_title}
        </div>
        """
    )

    for icon, page_name in items:
        _navigation_button(
            icon,
            page_name,
        )


# =========================================================
# ESTADO DEL SISTEMA
# =========================================================


def _render_system_status() -> None:
    """
    Muestra el estado visual del sistema.
    """

    st.html(
        """
        <div class="ax-section-title">
            SISTEMA
        </div>

        <div class="ax-system-card">

            <div class="ax-system-row">
                <span>
                    🟢 Base de datos
                </span>

                <b>
                    CONECTADO
                </b>
            </div>

            <div class="ax-system-row">
                <span>
                    🤖 AI Engine
                </span>

                <b>
                    ACTIVO
                </b>
            </div>

            <div class="ax-system-row">
                <span>
                    ⚡ Risk Core
                </span>

                <b>
                    PROTEGIDO
                </b>
            </div>

        </div>
        """
    )


# =========================================================
# CERRAR SESIÓN
# =========================================================


def _logout() -> None:
    """
    Limpia la autenticación local.
    """

    try:
        clear_auth()

    except Exception:
        keys_to_delete = [
            "access_token",
            "refresh_token",
            "user",
            "authenticated",
            "page",
            "avatar_url",
        ]

        for key in keys_to_delete:
            st.session_state.pop(
                key,
                None,
            )

    st.rerun()


# =========================================================
# SIDEBAR PRINCIPAL
# =========================================================


def render_sidebar() -> None:
    """
    Renderiza toda la barra lateral.
    """

    with st.sidebar:

        _render_brand()

        _render_profile()

        _render_navigation_section(
            "NAVEGACIÓN PRINCIPAL",
            MAIN_NAVIGATION,
        )

        _render_navigation_section(
            "INTELIGENCIA AVANZADA",
            ADVANCED_NAVIGATION,
        )

        _render_navigation_section(
            "CONFIGURACIÓN",
            SETTINGS_NAVIGATION,
        )

        _render_system_status()

        st.html(
            "<div style='height:14px'></div>"
        )

        if st.button(
            "🚪 Cerrar sesión",
            key="sidebar_logout",
            use_container_width=True,
            type="secondary",
        ):
            _logout()
