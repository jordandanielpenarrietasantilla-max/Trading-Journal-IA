from __future__ import annotations

import html
from typing import Any

import streamlit as st

from core.membership import get_membership_info
from ui_v2.theme import apply_v2_theme


SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 45% -10%, rgba(25,228,255,.11), transparent 28%),
        linear-gradient(180deg,#020713 0%,#01040b 100%) !important;
    border-right:1px solid rgba(70,108,178,.30);
}

[data-testid="stSidebar"] {
    height: 100vh !important;
    overflow: hidden !important;
}

[data-testid="stSidebarContent"] {
    height: 100vh !important;
    max-height: 100vh !important;
    padding:.55rem .62rem 1.2rem !important;
    overflow-y:auto !important;
    overflow-x:hidden !important;
    overscroll-behavior:contain;
    scrollbar-width:thin;
    scrollbar-color:rgba(25,228,255,.45) rgba(4,10,25,.55);
}

[data-testid="stSidebarContent"]::-webkit-scrollbar {
    width:7px;
}

[data-testid="stSidebarContent"]::-webkit-scrollbar-track {
    background:rgba(4,10,25,.55);
    border-radius:999px;
}

[data-testid="stSidebarContent"]::-webkit-scrollbar-thumb {
    background:linear-gradient(180deg,#19e4ff,#3c7dff,#8b4dff);
    border-radius:999px;
}

[data-testid="stSidebarUserContent"] {
    min-height:max-content !important;
    padding-bottom:1rem !important;
}

.ax-brand {
    display:flex;
    align-items:center;
    gap:10px;
    padding:5px 4px 10px;
    border-bottom:1px solid rgba(76,103,166,.16);
}

.ax-logo {
    width:40px;
    height:40px;
    display:grid;
    place-items:center;
    color:white;
    font-size:17px;
    font-weight:950;
    background:
        linear-gradient(145deg,#19e4ff,#3c7dff 55%,#8b4dff);
    border:1px solid rgba(255,255,255,.10);
    border-radius:13px;
    box-shadow:
        0 0 22px rgba(25,228,255,.25),
        inset 0 1px 0 rgba(255,255,255,.10);
}

.ax-brand strong {
    display:block;
    color:#f7f9ff;
    font-size:12px;
    font-weight:950;
    letter-spacing:.2px;
}

.ax-brand small {
    display:block;
    margin-top:3px;
    color:#5f6d89;
    font-size:5.7px;
    font-weight:900;
    letter-spacing:1.55px;
}

.ax-live {
    width:7px;
    height:7px;
    margin-left:auto;
    border-radius:50%;
    background:#00f58a;
    box-shadow:0 0 12px #00f58a;
}

.ax-profile {
    margin-top:9px;
    padding:11px;
    background:
        radial-gradient(circle at 100% 0%,rgba(139,77,255,.13),transparent 34%),
        linear-gradient(145deg,rgba(8,18,40,.98),rgba(4,10,25,.98));
    border:1px solid rgba(25,228,255,.25);
    border-radius:15px;
}

.ax-profile-top {
    display:flex;
    align-items:center;
    gap:9px;
}

.ax-avatar {
    width:45px;
    height:45px;
    display:grid;
    place-items:center;
    flex-shrink:0;
    overflow:hidden;
    color:white;
    font-size:13px;
    font-weight:950;
    background:linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);
    border:2px solid rgba(255,255,255,.12);
    border-radius:50%;
    box-shadow:0 0 18px rgba(25,228,255,.22);
}

.ax-avatar img {
    width:100%;
    height:100%;
    object-fit:cover;
}

.ax-name {
    color:#f7f9ff;
    font-size:10.5px;
    font-weight:950;
}

.ax-role {
    display:inline-flex;
    margin-top:3px;
    padding:2px 6px;
    color:white;
    font-size:5.5px;
    font-weight:950;
    background:linear-gradient(90deg,#8b4dff,#ae43ff);
    border-radius:999px;
}

.ax-email {
    max-width:105px;
    overflow:hidden;
    margin-top:3px;
    color:#63708b;
    font-size:5.8px;
    white-space:nowrap;
    text-overflow:ellipsis;
}

.ax-capital-row {
    display:flex;
    justify-content:space-between;
    align-items:flex-end;
    gap:7px;
    margin-top:9px;
}

.ax-capital-row strong {
    color:#f7f9ff;
    font-size:15px;
    font-weight:950;
}

.ax-capital-row span {
    color:#697590;
    font-size:5.7px;
}

.ax-capital-label {
    margin-top:2px;
    color:#19e4ff;
    font-size:5.5px;
    font-weight:950;
    letter-spacing:1.15px;
}

.ax-progress {
    height:3px;
    margin-top:7px;
    overflow:hidden;
    background:#142039;
    border-radius:999px;
}

.ax-progress div {
    height:100%;
    background:linear-gradient(90deg,#19e4ff,#3c7dff,#8b4dff);
}

.ax-section {
    margin:12px 4px 5px;
    color:#53617d;
    font-size:5.7px;
    font-weight:950;
    letter-spacing:1.7px;
}

.ax-health {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:5px;
    margin-top:8px;
}

.ax-health-item {
    padding:6px 4px;
    text-align:center;
    color:#73809a;
    font-size:5.3px;
    background:rgba(6,11,27,.88);
    border:1px solid rgba(72,97,157,.20);
    border-radius:8px;
}

.ax-health-item strong {
    display:block;
    margin-top:3px;
    color:#00f58a;
    font-size:5.6px;
}

[data-testid="stSidebar"] .stButton {
    margin-bottom:2px !important;
}

[data-testid="stSidebar"] .stButton > button {
    min-height:31px !important;
    justify-content:flex-start !important;
    padding:0 9px !important;
    color:#e7edfb !important;
    font-size:9.6px !important;
    font-weight:760 !important;
    background:
        linear-gradient(145deg,rgba(8,17,37,.98),rgba(4,9,23,.98)) !important;
    border:1px solid rgba(69,99,162,.29) !important;
    border-radius:9px !important;
    box-shadow:none !important;
    transition:all .16s ease !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
    transform:translateX(2px);
    border-color:rgba(25,228,255,.48) !important;
    background:
        linear-gradient(90deg,rgba(25,228,255,.09),rgba(60,125,255,.12),rgba(139,77,255,.12)) !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    color:white !important;
    background:
        linear-gradient(95deg,rgba(25,228,255,.82),rgba(60,125,255,.86),rgba(139,77,255,.90)) !important;
    border-color:rgba(104,217,255,.42) !important;
    box-shadow:0 8px 20px rgba(60,125,255,.16) !important;
}

.ax-plan-strip {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:8px;
    margin-top:8px;
    padding:8px 9px;
    border-radius:10px;
    background:
        radial-gradient(circle at 100% 0%,rgba(255,209,102,.13),transparent 38%),
        linear-gradient(145deg,rgba(20,15,35,.96),rgba(7,10,25,.96));
    border:1px solid rgba(255,209,102,.28);
}

.ax-plan-strip strong {
    color:#ffd166;
    font-size:6.3px;
    font-weight:950;
    letter-spacing:.8px;
}

.ax-plan-strip span {
    color:#9ca8bf;
    font-size:5.6px;
}

.ax-owner-strip {
    background:
        radial-gradient(circle at 100% 0%,rgba(49,255,156,.13),transparent 38%),
        linear-gradient(145deg,rgba(7,26,25,.96),rgba(7,10,25,.96));
    border-color:rgba(49,255,156,.30);
}

.ax-owner-strip strong {
    color:#31ff9c;
}

</style>
"""


def _safe(value: Any) -> str:
    return html.escape(str(value or "").strip())


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _money(value: Any) -> str:
    return f"${_float(value, 0):,.2f}"


def _initials(name: str) -> str:
    pieces = [part for part in name.split() if part]
    if not pieces:
        return "TP"
    if len(pieces) == 1:
        return pieces[0][:2].upper()
    return (pieces[0][0] + pieces[-1][0]).upper()


def _user_data() -> tuple[str, str, str]:
    user = st.session_state.get("user", {})
    metadata: dict[str, Any] = {}
    email = ""

    if isinstance(user, dict):
        metadata = user.get("user_metadata", {}) or {}
        email = str(user.get("email", "") or "")

    name = (
        metadata.get("username")
        or metadata.get("full_name")
        or metadata.get("name")
        or st.session_state.get("nombre_trader", "Trader Pro")
    )

    avatar = str(
        metadata.get("avatar_url")
        or metadata.get("photo_url")
        or ""
    ).strip()

    return str(name), email, avatar


def _is_owner(email: str) -> bool:
    """
    La única cuenta FOUNDER es la configurada como ADMIN_EMAIL
    en Streamlit Secrets.
    """

    try:
        admin_email = str(
            st.secrets.get("ADMIN_EMAIL", "")
        ).strip().lower()
    except Exception:
        admin_email = ""

    return bool(
        admin_email
        and email.strip().lower() == admin_email
    )


def _go(page: str) -> None:
    st.session_state.page = page
    st.rerun()


def _nav(label: str, page: str, key: str, active: str) -> None:
    if st.button(
        label,
        key=key,
        use_container_width=True,
        type="primary" if active == page else "secondary",
    ):
        _go(page)


def render_v2_sidebar() -> None:
    apply_v2_theme()
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)

    name, email, avatar = _user_data()
    capital = _float(st.session_state.get("capital_actual", 10000), 10000)
    target = _float(st.session_state.get("capital_meta", 15000), 15000)
    progress = max(0.0, min(100.0, capital / target * 100 if target else 0.0))
    active = str(st.session_state.get("page", "Dashboard"))

    membership = get_membership_info()
    is_owner = membership.is_owner

    role_label = (
        "FOUNDER"
        if is_owner
        else (
            "PRO"
            if membership.is_pro
            else "TRADER"
        )
    )

    plan_label = membership.label

    if is_owner:
        plan_detail = "LIFETIME"

    elif membership.is_active:
        if membership.days_remaining is not None:
            plan_detail = (
                f"{membership.days_remaining} DÍAS RESTANTES"
            )
        else:
            plan_detail = "ACCESO ACTIVO"

    elif membership.is_expired:
        plan_detail = "RENOVACIÓN REQUERIDA"

    elif membership.plan == "TRIAL":
        plan_detail = "ACCESO DE PRUEBA"

    else:
        plan_detail = "AXION PRIME PRO"

    plan_class = (
        "ax-plan-strip ax-owner-strip"
        if is_owner
        else "ax-plan-strip"
    )

    avatar_html = (
        f'<div class="ax-avatar"><img src="{_safe(avatar)}" alt="Avatar"></div>'
        if avatar
        else f'<div class="ax-avatar">{_initials(name)}</div>'
    )

    with st.sidebar:
        st.html(
            """
            <div class="ax-brand">
                <div class="ax-logo">A</div>
                <div>
                    <strong>AXION PRIME</strong>
                    <small>PERFORMANCE COMMAND OS · X10</small>
                </div>
                <div class="ax-live"></div>
            </div>
            """
        )

        st.html(
            f"""
            <section class="ax-profile">
                <div class="ax-profile-top">
                    {avatar_html}
                    <div style="min-width:0">
                        <div class="ax-name">{_safe(name)}</div>
                        <div class="ax-role">{_safe(role_label)}</div>
                        <div class="ax-email">{_safe(email)}</div>
                    </div>
                </div>

                <div class="ax-capital-row">
                    <div>
                        <strong>{_money(capital)}</strong>
                        <div class="ax-capital-label">CAPITAL ACTUAL</div>
                    </div>
                    <span>META {_money(target)}</span>
                </div>

                <div class="ax-progress">
                    <div style="width:{progress:.1f}%"></div>
                </div>

                <div class="{plan_class}">
                    <strong>{_safe(plan_label)}</strong>
                    <span>{_safe(plan_detail)}</span>
                </div>
            </section>
            """
        )

        if st.button("⚙️ Modificar perfil", use_container_width=True, key="ax_profile_top"):
            _go("Modificar perfil")

        st.html('<div class="ax-section">PRINCIPAL</div>')
        _nav("📊 Dashboard", "Dashboard", "ax_dash", active)
        _nav("➕ Registrar Trade", "Registrar Trade", "ax_trade", active)
        _nav("📕 Track Record", "Track Record", "ax_track", active)
        _nav("🤖 Chat IA", "Chat IA", "ax_chat", active)

        st.html('<div class="ax-section">ANÁLISIS Y MEJORA</div>')
        _nav("🧠 Psicotrading", "Psicotrading", "ax_psy", active)
        _nav("🔍 Auditoría / Análisis IA", "Análisis IA", "ax_analysis", active)
        _nav("📈 Proyecciones", "Proyecciones", "ax_proj", active)

        st.html('<div class="ax-section">MEMBRESÍA</div>')
        _nav("💎 AXION PRIME PRO", "AXION PRIME PRO", "ax_pro", active)

        st.html('<div class="ax-section">HERRAMIENTAS</div>')
        _nav("🧮 Calculadora de lotaje", "Lotaje", "ax_lot", active)
        _nav("🕒 Sesiones de trading", "Sesiones", "ax_sessions", active)
        _nav("📰 Noticias de impacto", "Noticias", "ax_news", active)

        st.html(
            """
            <div class="ax-health">
                <div class="ax-health-item">DB<strong>ONLINE</strong></div>
                <div class="ax-health-item">IA<strong>ACTIVA</strong></div>
                <div class="ax-health-item">RISK<strong>SAFE</strong></div>
            </div>
            """
        )

        if st.button("🚪 Cerrar sesión", use_container_width=True, key="ax_logout_top"):
            for key in ("authenticated", "access_token", "refresh_token", "user"):
                st.session_state.pop(key, None)

            st.session_state.authenticated = False
            st.session_state.page = "Dashboard"
            st.rerun()
