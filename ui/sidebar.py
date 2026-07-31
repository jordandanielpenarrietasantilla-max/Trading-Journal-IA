from __future__ import annotations

from typing import Any

import streamlit as st

from core.config import ADMIN_EMAIL
from core.state import clear_auth


# =========================================================
# AXION PRIME X10
# SIDEBAR PROFESIONAL
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


def _user_value(
    user: Any,
    key: str,
    default: Any = "",
) -> Any:
    if user is None:
        return default

    if isinstance(user, dict):
        return user.get(key, default)

    return getattr(user, key, default)


def _user_metadata() -> dict[str, Any]:
    user = st.session_state.get("user")

    metadata = _user_value(
        user,
        "user_metadata",
        {},
    )

    return metadata if isinstance(metadata, dict) else {}


def _email() -> str:
    user = st.session_state.get("user")

    return str(
        _user_value(
            user,
            "email",
            "",
        )
        or ""
    ).strip()


def _trader_name() -> str:
    metadata = _user_metadata()

    possible_names = [
        metadata.get("username"),
        metadata.get("full_name"),
        metadata.get("name"),
        st.session_state.get("nombre_trader"),
    ]

    for value in possible_names:
        if value:
            return str(value)

    return "Trader Pro"


def _initials(
    name: str,
) -> str:
    words = [
        word
        for word in name.split()
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
    email = _email().lower()

    return bool(
        ADMIN_EMAIL
        and email
        and email == ADMIN_EMAIL.lower()
    )


def _navigate(
    page_name: str,
) -> None:
    st.session_state.page = page_name
    st.rerun()


def _render_brand() -> None:
    st.html(
        """
        <div class="ax-brand">
            <div class="ax-logo">A</div>

            <div>
                <b>AXION PRIME</b>
                <small>PERFORMANCE COMMAND OS · X10</small>
            </div>

            <div class="ax-brand-online"></div>
        </div>
        """
    )


def _render_profile() -> None:
    name = _trader_name()
    email = _email()
    initials = _initials(name)

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

    role = "FOUNDER" if _is_admin() else "TRADER"

    st.html(
        f"""
        <div class="ax-profile">
            <div class="ax-profile-top">
                <div class="ax-profile-avatar">
                    {initials}
                </div>

                <div class="ax-profile-identity">
                    <div class="ax-profile-name-row">
                        <strong>{name}</strong>
                        <span class="ax-profile-role">{role}</span>
                    </div>

                    <div class="ax-profile-email">
                        {email}
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
                <span>{progress:.1f}% DE LA META</span>
                <span>${target:,.0f}</span>
            </div>
        </div>
        """
    )


def _navigation_button(
    icon: str,
    page_name: str,
) -> None:
    current_page = st.session_state.get(
        "page",
        "Dashboard",
    )

    active = current_page == page_name

    if st.button(
        f"{icon}  {page_name}",
        key=f"sidebar_nav_{page_name}",
        use_container_width=True,
        type="primary" if active else "secondary",
    ):
        _navigate(page_name)


def _render_system_status() -> None:
    st.html(
        """
        <div class="ax-section-title">
            SISTEMA
        </div>

        <div class="ax-system-card">
            <div class="ax-system-row">
                <span>🟢 Base de datos</span>
                <b>CONECTADO</b>
            </div>

            <div class="ax-system-row">
                <span>🤖 AI Engine</span>
                <b>ACTIVO</b>
            </div>

            <div class="ax-system-row">
                <span>⚡ Risk Core</span>
                <b>PROTEGIDO</b>
            </div>
        </div>
        """
    )


def render_sidebar() -> None:
    with st.sidebar:
        _render_brand()
        _render_profile()

        st.html(
            """
            <div class="ax-section-title">
                NAVEGACIÓN PRINCIPAL
            </div>
            """
        )

        for icon, page_name in MAIN_NAVIGATION:
            _navigation_button(
                icon,
                page_name,
            )

        st.html(
            """
            <div class="ax-section-title">
                INTELIGENCIA AVANZADA
            </div>
            """
        )

        for icon, page_name in ADVANCED_NAVIGATION:
            _navigation_button(
                icon,
                page_name,
            )

        _render_system_status()

        st.html(
            "<div style='height:12px'></div>"
        )

        if st.button(
            "🚪 Cerrar sesión",
            key="sidebar_logout",
            use_container_width=True,
            type="secondary",
        ):
            clear_auth()
            st.rerun()
