from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui_v2.theme import apply_v2_theme


SIDEBAR_CSS = """
<style>
[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 50% -8%, rgba(25,228,255,.10), transparent 30%),
        linear-gradient(180deg,#030814 0%,#02050d 100%) !important;
    border-right:1px solid rgba(67,103,171,.28);
}
[data-testid="stSidebarContent"] {
    padding: .8rem .75rem 1.2rem;
}
.ax-side-brand {
    display:flex; align-items:center; gap:11px;
    padding:6px 4px 14px; margin-bottom:12px;
    border-bottom:1px solid rgba(76,103,166,.17);
}
.ax-side-logo {
    width:42px; height:42px; display:grid; place-items:center;
    color:white; font-size:17px; font-weight:950;
    background:linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);
    border-radius:13px; box-shadow:0 0 24px rgba(25,228,255,.26);
}
.ax-side-brand strong { display:block; color:#f7f9ff; font-size:12px; }
.ax-side-brand small { display:block; margin-top:3px; color:#64718d; font-size:6px; letter-spacing:1.5px; }
.ax-side-online {
    width:7px; height:7px; margin-left:auto; border-radius:50%;
    background:#00f58a; box-shadow:0 0 11px #00f58a;
}
.ax-side-profile {
    padding:13px; margin-bottom:9px;
    background:linear-gradient(145deg,rgba(8,18,40,.98),rgba(4,10,25,.98));
    border:1px solid rgba(25,228,255,.27);
    border-radius:16px;
}
.ax-side-profile-top { display:flex; align-items:center; gap:10px; }
.ax-side-avatar {
    width:49px; height:49px; display:grid; place-items:center;
    overflow:hidden; flex-shrink:0; color:white; font-weight:950;
    background:linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);
    border:2px solid rgba(255,255,255,.13); border-radius:50%;
}
.ax-side-avatar img { width:100%; height:100%; object-fit:cover; }
.ax-side-name { color:#f7f9ff; font-size:11px; font-weight:950; }
.ax-side-role {
    display:inline-flex; margin-top:4px; padding:3px 6px;
    color:white; font-size:6px; font-weight:950;
    background:linear-gradient(90deg,#8b4dff,#ae43ff); border-radius:999px;
}
.ax-side-email { margin-top:4px; color:#64708d; font-size:6px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }
.ax-side-capital { display:flex; justify-content:space-between; align-items:end; gap:7px; margin-top:12px; }
.ax-side-capital strong { color:#f7f9ff; font-size:17px; }
.ax-side-capital span { color:#6d7895; font-size:6px; }
.ax-side-label { margin-top:3px; color:#19e4ff; font-size:6px; font-weight:950; letter-spacing:1.2px; }
.ax-side-progress { height:4px; margin-top:8px; background:#15203a; border-radius:999px; overflow:hidden; }
.ax-side-progress div { height:100%; background:linear-gradient(90deg,#19e4ff,#3c7dff,#8b4dff); }
.ax-side-section { margin:16px 4px 7px; color:#5e6c89; font-size:6px; font-weight:950; letter-spacing:1.8px; }
.ax-side-system {
    padding:10px; margin-top:10px; background:rgba(6,11,27,.90);
    border:1px solid rgba(72,97,157,.24); border-radius:12px;
}
.ax-side-system-row { display:flex; justify-content:space-between; gap:8px; margin-bottom:7px; color:#dbe4f8; font-size:7px; }
.ax-side-system-row:last-child { margin-bottom:0; }
.ax-side-system-row strong { color:#00f58a; font-size:6px; }
[data-testid="stSidebar"] .stButton > button {
    min-height:36px !important;
    justify-content:flex-start;
    padding:0 11px !important;
    font-size:11px !important;
    color:#e7edfb !important;
    background:linear-gradient(145deg,rgba(9,18,39,.98),rgba(5,10,25,.98)) !important;
    border:1px solid rgba(72,101,166,.33) !important;
    border-radius:10px !important;
    box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    transform:translateX(2px);
    border-color:rgba(25,228,255,.48) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background:linear-gradient(95deg,#19e4ff,#3c7dff,#8b4dff) !important;
    border-color:rgba(102,220,255,.40) !important;
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
    parts = [p for p in name.split() if p]
    if not parts:
        return "TP"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


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
    avatar = str(metadata.get("avatar_url") or metadata.get("photo_url") or "").strip()
    return str(name), email, avatar


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

    avatar_html = (
        f'<div class="ax-side-avatar"><img src="{_safe(avatar)}" alt="Avatar"></div>'
        if avatar
        else f'<div class="ax-side-avatar">{_initials(name)}</div>'
    )

    active = str(st.session_state.get("page", "Dashboard"))

    with st.sidebar:
        st.html(
            """
            <div class="ax-side-brand">
                <div class="ax-side-logo">A</div>
                <div><strong>AXION PRIME</strong><small>PERFORMANCE COMMAND OS · X10</small></div>
                <div class="ax-side-online"></div>
            </div>
            """
        )

        st.html(
            f"""
            <section class="ax-side-profile">
                <div class="ax-side-profile-top">
                    {avatar_html}
                    <div style="min-width:0">
                        <div class="ax-side-name">{_safe(name)}</div>
                        <div class="ax-side-role">FOUNDER</div>
                        <div class="ax-side-email">{_safe(email)}</div>
                    </div>
                </div>
                <div class="ax-side-capital">
                    <div>
                        <strong>{_money(capital)}</strong>
                        <div class="ax-side-label">CAPITAL ACTUAL</div>
                    </div>
                    <span>META {_money(target)}</span>
                </div>
                <div class="ax-side-progress"><div style="width:{progress:.1f}%"></div></div>
            </section>
            """
        )

        if st.button("⚙️ Modificar perfil", use_container_width=True, key="ax_profile"):
            _go("Modificar perfil")

        st.html('<div class="ax-side-section">NAVEGACIÓN PRINCIPAL</div>')
        _nav("📊 Dashboard", "Dashboard", "ax_nav_dashboard", active)
        _nav("➕ Registrar Trade", "Registrar Trade", "ax_nav_trade", active)
        _nav("📕 Track Record", "Track Record", "ax_nav_track", active)
        _nav("🤖 Chat IA", "Chat IA", "ax_nav_chat", active)

        st.html('<div class="ax-side-section">INTELIGENCIA Y RIESGO</div>')
        _nav("🧠 Psicotrading", "Psicotrading", "ax_nav_psy", active)
        _nav("🔍 Análisis IA", "Análisis IA", "ax_nav_analysis", active)
        _nav("📈 Proyecciones", "Proyecciones", "ax_nav_proj", active)
        _nav("🧮 Calculadora de lotaje", "Lotaje", "ax_nav_lot", active)

        st.html('<div class="ax-side-section">MERCADO</div>')
        _nav("🕒 Sesiones de trading", "Sesiones", "ax_nav_sessions", active)
        _nav("📰 Noticias de impacto", "Noticias", "ax_nav_news", active)

        st.html(
            """
            <div class="ax-side-system">
                <div class="ax-side-system-row"><span>🟢 Base de datos</span><strong>CONECTADO</strong></div>
                <div class="ax-side-system-row"><span>🤖 AI Engine</span><strong>ACTIVO</strong></div>
                <div class="ax-side-system-row"><span>⚡ Risk Core</span><strong>PROTEGIDO</strong></div>
            </div>
            """
        )

        st.write("")

        if st.button("🚪 Cerrar sesión", use_container_width=True, key="ax_logout"):
            for key in ("authenticated", "access_token", "refresh_token", "user"):
                st.session_state.pop(key, None)
            st.session_state.authenticated = False
            st.session_state.page = "Dashboard"
            st.rerun()
