from __future__ import annotations

import html
from typing import Any

import streamlit as st

from core.config import ADMIN_EMAIL
from core.state import clear_auth


# =========================================================
# AXION PRIME X10
# SIDEBAR PROFESIONAL COMPLETO
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


# =========================================================
# UTILIDADES DE USUARIO
# =========================================================


def _user_value(
    user: Any,
    key: str,
    default: Any = "",
) -> Any:
    """
    Lee un valor del usuario tanto si viene como diccionario
    como si viene como objeto.
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
    Obtiene el usuario guardado en la sesión.
    """

    return st.session_state.get(
        "user",
        {},
    )


def _user_metadata() -> dict[str, Any]:
    """
    Obtiene los metadatos del usuario desde Supabase Auth.
    """

    user = _current_user()

    metadata = _user_value(
        user,
        "user_metadata",
        {},
    )

    if isinstance(metadata, dict):
        return metadata

    return {}


def _email() -> str:
    """
    Obtiene el correo del usuario autenticado.
    """

    user = _current_user()

    email = _user_value(
        user,
        "email",
        "",
    )

    return str(
        email or ""
    ).strip()


def _trader_name() -> str:
    """
    Obtiene el nombre del trader desde los metadatos
    o desde session_state.
    """

    metadata = _user_metadata()

    possible_names = [
        metadata.get("username"),
        metadata.get("full_name"),
        metadata.get("display_name"),
        metadata.get("name"),
        metadata.get("nombre"),
        metadata.get("nombre_trader"),
        st.session_state.get("nombre_trader"),
    ]

    for value in possible_names:
        clean_value = str(
            value or ""
        ).strip()

        if clean_value:
            return clean_value

    return "Trader Pro"


def _initials(
    name: str,
) -> str:
    """
    Genera iniciales como respaldo cuando no existe foto.
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


def _profile_photo() -> str:
    """
    Recupera la fotografía que fue guardada anteriormente
    desde la pantalla Modificar perfil.

    Revisa varios nombres posibles para ser compatible
    con versiones anteriores de la aplicación.
    """

    metadata = _user_metadata()

    possible_photo_keys = [
        "avatar_url",
        "photo_url",
        "profile_image",
        "profile_photo",
        "profile_picture",
        "picture",
        "foto",
        "foto_url",
        "foto_perfil",
        "imagen_perfil",
        "avatar",
    ]

    for key in possible_photo_keys:
        value = metadata.get(
            key,
            "",
        )

        clean_value = str(
            value or ""
        ).strip()

        if clean_value:
            return clean_value

    session_photo_keys = [
        "avatar_url",
        "photo_url",
        "profile_image",
        "profile_photo",
        "foto_perfil",
        "imagen_perfil",
    ]

    for key in session_photo_keys:
        value = st.session_state.get(
            key,
            "",
        )

        clean_value = str(
            value or ""
        ).strip()

        if clean_value:
            return clean_value

    return ""


def _is_admin() -> bool:
    """
    Verifica si el usuario es administrador.
    """

    current_email = _email().lower()

    configured_admin = str(
        ADMIN_EMAIL or ""
    ).strip().lower()

    return bool(
        current_email
        and configured_admin
        and current_email == configured_admin
    )


def _capital_actual() -> float:
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


def _navigate(
    page_name: str,
) -> None:
    """
    Cambia la página seleccionada.
    """

    st.session_state.page = page_name
    st.rerun()


# =========================================================
# MARCA
# =========================================================


def _render_brand() -> None:
    st.html(
        """
        <div class="ax-brand">
            <div class="ax-logo">
                A
            </div>

            <div>
                <b>AXION PRIME</b>

                <small>
                    PERFORMANCE COMMAND OS · X10
                </small>
            </div>

            <div class="ax-brand-online"></div>
        </div>
        """
    )


# =========================================================
# PERFIL
# =========================================================


def _avatar_html(
    name: str,
) -> str:
    """
    Devuelve el HTML de la foto o las iniciales.
    """

    photo = _profile_photo()

    if photo:
        safe_photo = html.escape(
            photo,
            quote=True,
        )

        return f"""
        <div class="ax-profile-avatar ax-profile-photo">
            <img
                src="{safe_photo}"
                alt="Foto de perfil"
                loading="lazy"
            >
        </div>
        """

    initials = html.escape(
        _initials(name)
    )

    return f"""
    <div class="ax-profile-avatar">
        {initials}
    </div>
    """


def _render_profile() -> None:
    name = _trader_name()
    email = _email()

    safe_name = html.escape(
        name
    )

    safe_email = html.escape(
        email
    )

    capital = _capital_actual()
    target = _capital_meta()

    if target > 0:
        progress = (
            capital
            / target
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
        name
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
                        ${capital:,.2f}
                    </div>

                    <div class="ax-profile-capital-label">
                        CAPITAL ACTUAL
                    </div>

                </div>

                <div class="ax-profile-target">
                    META ${target:,.0f}
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
                    ${target:,.0f}
                </span>

            </div>

        </div>
        """
    )


# =========================================================
# NAVEGACIÓN
# =========================================================


def _navigation_button(
    icon: str,
    page_name: str,
) -> None:
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
    Limpia la sesión y vuelve al login.
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
        ]

        for key in keys_to_delete:
            if key in st.session_state:
                del st.session_state[key]

    st.rerun()


# =========================================================
# SIDEBAR COMPLETO
# =========================================================


def render_sidebar() -> None:
    """
    Renderiza el menú lateral completo.
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
