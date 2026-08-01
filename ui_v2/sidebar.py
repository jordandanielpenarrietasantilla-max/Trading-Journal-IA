from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui_v2.theme import apply_v2_theme


# =========================================================
# AXION PRIME V2
# SIDEBAR PREMIUM
# =========================================================


SIDEBAR_CSS = """
<style>

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 50% -8%,
            rgba(25, 228, 255, 0.12),
            transparent 31%
        ),
        linear-gradient(
            180deg,
            rgba(3, 8, 20, 0.995),
            rgba(2, 5, 14, 0.995)
        ) !important;

    border-right:
        1px solid
        rgba(67, 103, 171, 0.28);
}


[data-testid="stSidebarContent"] {
    padding:
        1rem
        0.85rem
        1.5rem;
}


.v2-side-brand {
    display: flex;
    align-items: center;

    gap: 12px;

    padding:
        7px
        5px
        18px;

    margin-bottom: 14px;

    border-bottom:
        1px solid
        rgba(76, 103, 166, 0.17);
}


.v2-side-logo {
    width: 46px;
    height: 46px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    color: white;

    font-size: 18px;
    font-weight: 950;

    background:
        linear-gradient(
            145deg,
            var(--v2-cyan),
            var(--v2-blue),
            var(--v2-purple)
        );

    border:
        1px solid
        rgba(255, 255, 255, 0.12);

    border-radius: 14px;

    box-shadow:
        0 0 25px
        rgba(25, 228, 255, 0.28);
}


.v2-side-brand-copy {
    min-width: 0;
}


.v2-side-brand-copy strong {
    display: block;

    color:
        var(--v2-white);

    font-size: 13px;
    font-weight: 950;
}


.v2-side-brand-copy span {
    display: block;

    margin-top: 4px;

    color:
        var(--v2-dim);

    font-size: 6px;
    font-weight: 900;

    letter-spacing: 1.5px;
}


.v2-side-online {
    width: 7px;
    height: 7px;

    margin-left: auto;

    border-radius: 50%;

    background:
        var(--v2-green);

    box-shadow:
        0 0 12px
        var(--v2-green);
}


.v2-side-profile {
    padding:
        15px;

    margin-bottom: 10px;

    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(139, 77, 255, 0.13),
            transparent 34%
        ),
        linear-gradient(
            145deg,
            rgba(8, 18, 40, 0.98),
            rgba(4, 10, 25, 0.98)
        );

    border:
        1px solid
        rgba(25, 228, 255, 0.29);

    border-radius: 18px;

    box-shadow:
        0 18px 45px
        rgba(0, 0, 0, 0.28);
}


.v2-side-profile-top {
    display: flex;
    align-items: center;

    gap: 11px;
}


.v2-side-avatar {
    width: 56px;
    height: 56px;

    display: grid;
    place-items: center;

    flex-shrink: 0;
    overflow: hidden;

    color: white;

    font-size: 16px;
    font-weight: 950;

    background:
        linear-gradient(
            145deg,
            var(--v2-cyan),
            var(--v2-blue),
            var(--v2-purple)
        );

    border:
        2px solid
        rgba(255, 255, 255, 0.13);

    border-radius: 50%;

    box-shadow:
        0 0 22px
        rgba(25, 228, 255, 0.30);
}


.v2-side-avatar img {
    width: 100%;
    height: 100%;

    display: block;

    object-fit: cover;
    object-position: center;

    border-radius: 50%;
}


.v2-side-identity {
    min-width: 0;
    flex: 1;
}


.v2-side-name {
    color:
        var(--v2-white);

    font-size: 12px;
    font-weight: 950;
}


.v2-side-role {
    display: inline-flex;

    margin-top: 5px;

    padding:
        3px
        7px;

    color: white;

    font-size: 6px;
    font-weight: 950;

    background:
        linear-gradient(
            90deg,
            var(--v2-purple),
            #ae43ff
        );

    border-radius: 999px;
}


.v2-side-email {
    overflow: hidden;

    margin-top: 5px;

    color:
        #64708d;

    font-size: 7px;

    white-space: nowrap;
    text-overflow: ellipsis;
}


.v2-side-capital {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;

    gap: 8px;

    margin-top: 15px;
}


.v2-side-capital strong {
    color:
        var(--v2-white);

    font-size: 19px;
    font-weight: 950;
}


.v2-side-capital span {
    color:
        #6d7895;

    font-size: 6px;
}


.v2-side-capital-label {
    margin-top: 4px;

    color:
        var(--v2-cyan);

    font-size: 6px;
    font-weight: 950;

    letter-spacing: 1.35px;
}


.v2-side-progress {
    height: 4px;

    overflow: hidden;

    margin-top: 10px;

    background:
        #15203a;

    border-radius: 999px;
}


.v2-side-progress > div {
    height: 100%;

    background:
        linear-gradient(
            90deg,
            var(--v2-cyan),
            var(--v2-blue),
            var(--v2-purple)
        );

    border-radius: 999px;
}


.v2-side-progress-labels {
    display: flex;
    justify-content: space-between;

    margin-top: 6px;

    color:
        #61708f;

    font-size: 6px;
}


.v2-side-section {
    margin:
        21px
        4px
        9px;

    color:
        #5e6c89;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 2px;
}


.v2-side-system {
    padding:
        13px;

    margin-top: 12px;

    background:
        rgba(6, 11, 27, 0.90);

    border:
        1px solid
        rgba(72, 97, 157, 0.24);

    border-radius: 14px;
}


.v2-side-system-row {
    display: flex;
    justify-content: space-between;

    gap: 10px;

    margin-bottom: 10px;

    color:
        #dbe4f8;

    font-size: 8px;
}


.v2-side-system-row:last-child {
    margin-bottom: 0;
}


.v2-side-system-row strong {
    color:
        var(--v2-green);

    font-size: 7px;
}


[data-testid="stSidebar"] .stButton > button {
    min-height: 42px;

    justify-content: flex-start;

    padding-left: 14px !important;

    color:
        #e7edfb !important;

    background:
        linear-gradient(
            145deg,
            rgba(9, 18, 39, 0.98),
            rgba(5, 10, 25, 0.98)
        ) !important;

    border:
        1px solid
        rgba(72, 101, 166, 0.33) !important;

    border-radius:
        11px !important;

    box-shadow:
        none !important;
}


[data-testid="stSidebar"] .stButton > button:hover {
    transform:
        translateX(3px);

    border-color:
        rgba(25, 228, 255, 0.48) !important;

    background:
        linear-gradient(
            95deg,
            rgba(25, 228, 255, 0.15),
            rgba(60, 125, 255, 0.18),
            rgba(139, 77, 255, 0.18)
        ) !important;
}


[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    color:
        white !important;

    background:
        linear-gradient(
            95deg,
            var(--v2-cyan),
            var(--v2-blue),
            var(--v2-purple)
        ) !important;

    border-color:
        rgba(102, 220, 255, 0.40) !important;

    box-shadow:
        0 10px 26px
        rgba(60, 125, 255, 0.18) !important;
}

</style>
"""


# =========================================================
# UTILIDADES
# =========================================================


def _safe_text(
    value: Any,
    default: str = "",
) -> str:
    clean = str(
        value
        if value is not None
        else default
    ).strip()

    return html.escape(
        clean
    )


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(
            value
            if value is not None
            else default
        )

    except (TypeError, ValueError):
        return default


def _money(
    value: Any,
) -> str:
    return f"${_safe_float(value):,.2f}"


def _initials(
    name: str,
) -> str:
    pieces = [
        part
        for part in name.split()
        if part
    ]

    if not pieces:
        return "TP"

    if len(pieces) == 1:
        return pieces[0][:2].upper()

    return (
        pieces[0][0]
        + pieces[-1][0]
    ).upper()


def _user_data() -> tuple[
    str,
    str,
    str,
]:
    user = st.session_state.get(
        "user",
        {}
    )

    metadata: dict[str, Any] = {}

    email = ""

    if isinstance(
        user,
        dict,
    ):
        metadata = (
            user.get(
                "user_metadata",
                {}
            )
            or {}
        )

        email = str(
            user.get(
                "email",
                ""
            )
            or ""
        )

    name = (
        metadata.get(
            "username"
        )
        or metadata.get(
            "full_name"
        )
        or metadata.get(
            "name"
        )
        or "Trader Pro"
    )

    avatar_url = str(
        metadata.get(
            "avatar_url"
        )
        or metadata.get(
            "photo_url"
        )
        or ""
    ).strip()

    return (
        str(name),
        email,
        avatar_url,
    )


# =========================================================
# BLOQUES VISUALES
# =========================================================


def _render_brand() -> None:
    st.html(
        """
        <div class="v2-side-brand">

            <div class="v2-side-logo">
                A
            </div>

            <div class="v2-side-brand-copy">
                <strong>
                    AXION PRIME
                </strong>

                <span>
                    PERFORMANCE COMMAND OS · X10
                </span>
            </div>

            <div class="v2-side-online"></div>

        </div>
        """
    )


def _render_profile() -> None:
    name, email, avatar_url = (
        _user_data()
    )

    capital = _safe_float(
        st.session_state.get(
            "capital_actual",
            10000.0,
        ),
        10000.0,
    )

    target = _safe_float(
        st.session_state.get(
            "capital_meta",
            15000.0,
        ),
        15000.0,
    )

    progress = (
        capital
        / target
        * 100
        if target > 0
        else 0.0
    )

    progress = max(
        0.0,
        min(
            progress,
            100.0,
        ),
    )

    avatar_html = (
        f"""
        <div class="v2-side-avatar">
            <img
                src="{_safe_text(avatar_url)}"
                alt="Avatar"
            />
        </div>
        """
        if avatar_url
        else f"""
        <div class="v2-side-avatar">
            {_initials(name)}
        </div>
        """
    )

    st.html(
        f"""
        <section class="v2-side-profile">

            <div class="v2-side-profile-top">

                {avatar_html}

                <div class="v2-side-identity">

                    <div class="v2-side-name">
                        {_safe_text(name)}
                    </div>

                    <div class="v2-side-role">
                        FOUNDER
                    </div>

                    <div class="v2-side-email">
                        {_safe_text(email)}
                    </div>

                </div>

            </div>

            <div class="v2-side-capital">

                <div>
                    <strong>
                        {_money(capital)}
                    </strong>

                    <div class="v2-side-capital-label">
                        CAPITAL ACTUAL
                    </div>
                </div>

                <span>
                    META {_money(target)}
                </span>

            </div>

            <div class="v2-side-progress">
                <div style="width:{progress:.1f}%"></div>
            </div>

            <div class="v2-side-progress-labels">
                <span>
                    {progress:.1f}% DE LA META
                </span>

                <span>
                    {_money(target)}
                </span>
            </div>

        </section>
        """
    )


def _go_to(
    page: str,
) -> None:
    st.session_state.page = page
    st.rerun()


def _nav_button(
    *,
    label: str,
    page: str,
    key: str,
    active_page: str,
) -> None:
    if st.button(
        label,
        key=key,
        use_container_width=True,
        type=(
            "primary"
            if active_page == page
            else "secondary"
        ),
    ):
        _go_to(
            page
        )


def _render_system_status() -> None:
    st.html(
        """
        <div class="v2-side-section">
            SISTEMA
        </div>

        <div class="v2-side-system">

            <div class="v2-side-system-row">
                <span>
                    🟢 Base de datos
                </span>

                <strong>
                    CONECTADO
                </strong>
            </div>

            <div class="v2-side-system-row">
                <span>
                    🤖 AI Engine
                </span>

                <strong>
                    ACTIVO
                </strong>
            </div>

            <div class="v2-side-system-row">
                <span>
                    ⚡ Risk Core
                </span>

                <strong>
                    PROTEGIDO
                </strong>
            </div>

        </div>
        """
    )


# =========================================================
# SIDEBAR PRINCIPAL
# =========================================================


def render_v2_sidebar() -> None:
    """
    Renderiza la navegación lateral premium.
    """

    apply_v2_theme()

    st.markdown(
        SIDEBAR_CSS,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        _render_brand()
        _render_profile()

        if st.button(
            "⚙️ Modificar perfil",
            use_container_width=True,
            key="v2_sidebar_profile",
        ):
            st.session_state.page = (
                "Modificar perfil"
            )

            st.rerun()

        active_page = str(
            st.session_state.get(
                "page",
                "Dashboard",
            )
        )

        st.html(
            """
            <div class="v2-side-section">
                NAVEGACIÓN PRINCIPAL
            </div>
            """
        )

        _nav_button(
            label="📊 Dashboard",
            page="Dashboard",
            key="v2_nav_dashboard",
            active_page=active_page,
        )

        _nav_button(
            label="➕ Registrar Trade",
            page="Registrar Trade",
            key="v2_nav_register",
            active_page=active_page,
        )

        _nav_button(
            label="📕 Track Record",
            page="Track Record",
            key="v2_nav_track",
            active_page=active_page,
        )

        _nav_button(
            label="🤖 Chat IA",
            page="Chat IA",
            key="v2_nav_chat",
            active_page=active_page,
        )

        st.html(
            """
            <div class="v2-side-section">
                INTELIGENCIA AVANZADA
            </div>
            """
        )

        _nav_button(
            label="🧠 Psicotrading",
            page="Psicotrading",
            key="v2_nav_psychology",
            active_page=active_page,
        )

        _nav_button(
            label="🔍 Análisis IA",
            page="Análisis IA",
            key="v2_nav_analysis",
            active_page=active_page,
        )

        _nav_button(
            label="📈 Proyecciones",
            page="Proyecciones",
            key="v2_nav_projections",
            active_page=active_page,
        )

        _nav_button(
            label="🧮 Lotaje",
            page="Lotaje",
            key="v2_nav_lotage",
            active_page=active_page,
        )

        _render_system_status()

        st.write("")

        if st.button(
            "🚪 Cerrar sesión",
            use_container_width=True,
            key="v2_sidebar_logout",
        ):
            for key in (
                "authenticated",
                "access_token",
                "refresh_token",
                "user",
            ):
                if key in st.session_state:
                    del st.session_state[key]

            st.session_state.authenticated = False
            st.session_state.page = "Dashboard"

            st.rerun()
