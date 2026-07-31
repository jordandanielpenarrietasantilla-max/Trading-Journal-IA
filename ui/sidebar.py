from __future__ import annotations

from typing import Any

import streamlit as st

from core.config import ADMIN_EMAIL
from core.state import clear_auth


# =========================================================
# AXION PRIME X10 PRO
# PANEL LATERAL
# =========================================================

NAVIGATION_MAIN = [
    ("📊", "Dashboard"),
    ("➕", "Registrar Trade"),
    ("📕", "Track Record"),
    ("🤖", "Chat IA"),
]

NAVIGATION_ADVANCED = [
    ("🧠", "Psicotrading"),
    ("🔍", "Análisis IA"),
    ("📈", "Proyecciones"),
    ("🧮", "Lotaje"),
]


# =========================================================
# DATOS DEL USUARIO
# =========================================================

def _get_user_value(
    user: Any,
    key: str,
    default: Any = "",
) -> Any:
    """
    Permite leer usuarios recibidos como diccionario
    o como objeto de Supabase.
    """

    if user is None:
        return default

    if isinstance(user, dict):
        return user.get(key, default)

    return getattr(
        user,
        key,
        default,
    )


def _get_user_metadata(
    user: Any,
) -> dict:
    """
    Obtiene user_metadata de manera segura.
    """

    metadata = _get_user_value(
        user,
        "user_metadata",
        {},
    )

    if isinstance(metadata, dict):
        return metadata

    return {}


def _get_email() -> str:
    """
    Devuelve el correo del usuario autenticado.
    """

    user = st.session_state.get(
        "user"
    )

    email = _get_user_value(
        user,
        "email",
        "",
    )

    return str(
        email or ""
    ).strip()


def _get_display_name() -> str:
    """
    Devuelve el nombre visible del trader.
    """

    user = st.session_state.get(
        "user"
    )

    metadata = _get_user_metadata(
        user
    )

    possible_names = [
        metadata.get("username"),
        metadata.get("full_name"),
        metadata.get("name"),
        st.session_state.get(
            "nombre_trader"
        ),
    ]

    for value in possible_names:

        if value:
            return str(value)

    return "Trader Pro"


def _get_initials(
    name: str,
) -> str:
    """
    Crea iniciales para el avatar.
    """

    words = [
        word
        for word in name.strip().split()
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
    Comprueba si el usuario es el administrador.
    """

    email = _get_email().lower()

    return bool(
        ADMIN_EMAIL
        and email
        and email == ADMIN_EMAIL.lower()
    )


# =========================================================
# CAMBIAR PÁGINA
# =========================================================

def _navigate(
    page_name: str,
) -> None:
    """
    Cambia la página activa.
    """

    st.session_state.page = (
        page_name
    )

    st.rerun()


def _render_navigation_button(
    icon: str,
    page_name: str,
) -> None:
    """
    Renderiza cada botón de navegación.
    """

    current_page = st.session_state.get(
        "page",
        "Dashboard",
    )

    is_active = (
        current_page == page_name
    )

    label = (
        f"{icon}  {page_name}"
    )

    button_type = (
        "primary"
        if is_active
        else "secondary"
    )

    if st.button(
        label,
        key=f"nav_{page_name}",
        use_container_width=True,
        type=button_type,
    ):

        _navigate(
            page_name
        )


# =========================================================
# MARCA AXION
# =========================================================

def _render_brand() -> None:

    st.markdown(
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

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PERFIL
# =========================================================

def _render_profile() -> None:

    name = _get_display_name()

    email = _get_email()

    initials = _get_initials(
        name
    )

    capital = float(
        st.session_state.get(
            "capital_actual",
            10000.0,
        )
    )

    target = float(
        st.session_state.get(
            "capital_meta",
            15000.0,
        )
    )

    progress = (
        min(
            100.0,
            max(
                0.0,
                capital / target * 100,
            ),
        )
        if target > 0
        else 0.0
    )

    role = (
        "FOUNDER"
        if _is_admin()
        else "TRADER"
    )

    role_color = (
        "#ffd740"
        if _is_admin()
        else "#25e5ff"
    )

    st.markdown(
        f"""
        <div class="ax-profile">

            <div
                style="
                    display:flex;
                    align-items:center;
                    gap:13px;
                "
            >

                <div
                    style="
                        width:60px;
                        height:60px;
                        min-width:60px;
                        border-radius:50%;
                        display:grid;
                        place-items:center;
                        font-size:18px;
                        font-weight:950;
                        color:white;

                        background:
                            linear-gradient(
                                145deg,
                                #25e5ff,
                                #218cff,
                                #a146ff
                            );

                        border:
                            3px solid
                            rgba(
                                255,
                                255,
                                255,
                                0.15
                            );

                        box-shadow:
                            0 0 25px
                            rgba(
                                37,
                                229,
                                255,
                                0.35
                            ),
                            0 0 38px
                            rgba(
                                161,
                                70,
                                255,
                                0.25
                            );
                    "
                >
                    {initials}
                </div>

                <div
                    style="
                        min-width:0;
                        flex:1;
                    "
                >

                    <div
                        style="
                            display:flex;
                            align-items:center;
                            gap:8px;
                            flex-wrap:wrap;
                        "
                    >

                        <strong
                            style="
                                color:white;
                                font-size:14px;
                            "
                        >
                            {name}
                        </strong>

                        <span
                            style="
                                padding:3px 7px;
                                border-radius:999px;
                                font-size:7px;
                                font-weight:950;
                                color:#050713;
                                background:{role_color};
                                letter-spacing:.7px;
                            "
                        >
                            {role}
                        </span>

                    </div>

                    <div
                        style="
                            color:#687594;
                            font-size:8px;
                            margin-top:5px;
                            overflow:hidden;
                            text-overflow:ellipsis;
                            white-space:nowrap;
                        "
                    >
                        {email}
                    </div>

                </div>

            </div>

            <div
                style="
                    margin-top:16px;
                    display:flex;
                    justify-content:space-between;
                    align-items:flex-end;
                "
            >

                <div>

                    <div
                        style="
                            color:white;
                            font-size:20px;
                            font-weight:950;
                        "
                    >
                        ${capital:,.2f}
                    </div>

                    <div
                        style="
                            color:#25e5ff;
                            font-size:7px;
                            letter-spacing:1.4px;
                            font-weight:900;
                            margin-top:4px;
                        "
                    >
                        CAPITAL ACTUAL
                    </div>

                </div>

                <div
                    style="
                        color:#7c89aa;
                        font-size:8px;
                    "
                >
                    Meta ${target:,.0f}
                </div>

            </div>

            <div
                style="
                    margin-top:11px;
                    height:5px;
                    overflow:hidden;
                    border-radius:999px;
                    background:#18213d;
                "
            >

                <div
                    style="
                        width:{progress:.1f}%;
                        height:100%;
                        border-radius:999px;

                        background:
                            linear-gradient(
                                90deg,
                                #25e5ff,
                                #218cff,
                                #a146ff
                            );

                        box-shadow:
                            0 0 12px
                            rgba(
                                37,
                                229,
                                255,
                                .5
                            );
                    "
                >
                </div>

            </div>

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    color:#6f7d9e;
                    font-size:7px;
                    margin-top:6px;
                "
            >

                <span>
                    {progress:.1f}% DE LA META
                </span>

                <span>
                    ${target:,.0f}
                </span>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# ESTADO DEL SISTEMA
# =========================================================

def _render_system_status() -> None:

    st.markdown(
        '<div class="ax-section">SYSTEM</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div
            class="ax-card"
            style="
                padding:14px;
                font-size:10px;
            "
        >

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    margin-bottom:12px;
                "
            >

                <span>
                    🟢 Base de Datos
                </span>

                <span
                    style="
                        color:#00ff88;
                        font-weight:900;
                    "
                >
                    CONECTADO
                </span>

            </div>

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    margin-bottom:12px;
                "
            >

                <span>
                    🤖 AI Engine
                </span>

                <span
                    style="
                        color:#00ff88;
                        font-weight:900;
                    "
                >
                    ACTIVO
                </span>

            </div>

            <div
                style="
                    display:flex;
                    justify-content:space-between;
                "
            >

                <span>
                    ⚡ Risk Core
                </span>

                <span
                    style="
                        color:#00ff88;
                        font-weight:900;
                    "
                >
                    PROTEGIDO
                </span>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CERRAR SESIÓN
# =========================================================

def _render_logout() -> None:

    st.markdown(
        "<div style='height:12px'></div>",
        unsafe_allow_html=True,
    )

    if st.button(
        "🚪  Cerrar sesión",
        key="sidebar_logout",
        use_container_width=True,
    ):

        clear_auth()

        st.rerun()


# =========================================================
# SIDEBAR COMPLETO
# =========================================================

def render_sidebar() -> None:
    """
    Renderiza el panel lateral completo.
    """

    with st.sidebar:

        _render_brand()

        _render_profile()

        st.markdown(
            '<div class="ax-section">'
            'NAVEGACIÓN PRINCIPAL'
            '</div>',
            unsafe_allow_html=True,
        )

        for icon, page_name in NAVIGATION_MAIN:

            _render_navigation_button(
                icon,
                page_name,
            )

        st.markdown(
            '<div class="ax-section">'
            'INTELIGENCIA AVANZADA'
            '</div>',
            unsafe_allow_html=True,
        )

        for icon, page_name in NAVIGATION_ADVANCED:

            _render_navigation_button(
                icon,
                page_name,
            )

        _render_system_status()

        _render_logout()
