from __future__ import annotations

from typing import Any

import streamlit as st

from core.api import reset_password, sign_in, sign_up
from core.config import APP_URL
from ui_v2.theme import apply_v2_theme


LOGIN_CSS = """
<style>
[data-testid="stSidebar"] { display:none !important; }

.block-container {
    max-width: 1480px;
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
}

.v2-login-hero {
    min-height: 720px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
    padding:42px;
    overflow:hidden;
    position:relative;
    background:
        radial-gradient(circle at 85% 15%, rgba(25,228,255,.12), transparent 30%),
        radial-gradient(circle at 20% 90%, rgba(139,77,255,.16), transparent 34%),
        linear-gradient(145deg, rgba(5,13,31,.98), rgba(7,5,27,.98));
    border:1px solid rgba(68,107,181,.34);
    border-radius:26px;
    box-shadow:0 30px 90px rgba(0,0,0,.42);
}

.v2-login-hero:after {
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    background-image:
        linear-gradient(rgba(78,108,174,.045) 1px, transparent 1px),
        linear-gradient(90deg, rgba(78,108,174,.045) 1px, transparent 1px);
    background-size:52px 52px;
    mask-image:linear-gradient(to bottom, black, transparent 92%);
}

.v2-login-brand,
.v2-login-copy,
.v2-login-stats { position:relative; z-index:2; }

.v2-login-brand {
    display:flex;
    align-items:center;
    gap:13px;
}

.v2-login-logo {
    width:48px;
    height:48px;
    display:grid;
    place-items:center;
    color:white;
    font-size:18px;
    font-weight:950;
    background:linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);
    border-radius:14px;
    box-shadow:0 0 26px rgba(25,228,255,.28);
}

.v2-login-brand strong {
    display:block;
    color:#f7f9ff;
    font-size:18px;
    font-weight:950;
}

.v2-login-brand small {
    display:block;
    margin-top:4px;
    color:#64718d;
    font-size:7px;
    letter-spacing:1.8px;
    font-weight:900;
}

.v2-login-copy h1 {
    margin:17px 0 0;
    color:#f7f9ff;
    font-size:clamp(50px,5vw,76px);
    line-height:.96;
    letter-spacing:-3.7px;
    font-weight:950;
}

.v2-login-copy h1 span {
    display:block;
    color:transparent;
    background:linear-gradient(90deg,#19e4ff,#69a3ff,#8b4dff);
    background-clip:text;
    -webkit-background-clip:text;
}

.v2-login-copy p {
    max-width:650px;
    margin-top:22px;
    color:#9aa7c4;
    font-size:15px;
    line-height:1.7;
}

.v2-login-features {
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:11px;
    margin-top:28px;
}

.v2-login-feature {
    padding:14px;
    color:#e6ecfb;
    font-size:11px;
    font-weight:800;
    background:rgba(4,10,25,.72);
    border:1px solid rgba(77,104,169,.25);
    border-radius:13px;
}

.v2-login-feature b { color:#19e4ff; margin-right:8px; }

.v2-login-stats {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:10px;
}

.v2-login-stat {
    padding:13px;
    background:rgba(4,10,25,.72);
    border:1px solid rgba(72,101,165,.24);
    border-radius:12px;
}

.v2-login-stat small {
    display:block;
    color:#64718d;
    font-size:7px;
    font-weight:900;
    letter-spacing:1.2px;
}

.v2-login-stat strong {
    display:block;
    margin-top:7px;
    color:#f7f9ff;
    font-size:17px;
}

.v2-form-card {
    padding:34px 32px 30px;
    margin-top:12px;
    background:
        radial-gradient(circle at 100% 0%, rgba(139,77,255,.16), transparent 30%),
        linear-gradient(145deg, rgba(8,16,35,.98), rgba(6,8,25,.98));
    border:1px solid rgba(74,104,171,.34);
    border-radius:24px;
    box-shadow:0 30px 90px rgba(0,0,0,.38);
}

.v2-form-logo {
    width:44px;
    height:44px;
    display:grid;
    place-items:center;
    color:white;
    font-size:18px;
    background:linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);
    border-radius:13px;
    box-shadow:0 0 24px rgba(25,228,255,.24);
}

.v2-form-card h2 {
    margin:22px 0 7px;
    color:#f7f9ff;
    font-size:38px;
    line-height:1.04;
    letter-spacing:-1.8px;
    font-weight:950;
}

.v2-form-card p {
    color:#91a0bf;
    font-size:11px;
    margin-bottom:18px;
}

[data-baseweb="tab-list"] {
    gap:18px;
    border-bottom:1px solid rgba(84,107,166,.23);
}

[data-baseweb="tab"] {
    min-height:42px;
    padding-left:0 !important;
    padding-right:0 !important;
    background:transparent !important;
    color:#8390ad !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    color:#19e4ff !important;
    font-weight:900;
}

@media (max-width: 980px) {
    .v2-login-hero { min-height:auto; }
    .v2-login-features,.v2-login-stats { grid-template-columns:1fr; }
}
</style>
"""


def _payload_value(payload: Any, key: str, default: Any = None) -> Any:
    if payload is None:
        return default
    if isinstance(payload, dict):
        return payload.get(key, default)
    return getattr(payload, key, default)


def _save_session(payload: dict[str, Any]) -> None:
    access_token = str(_payload_value(payload, "access_token", "") or "").strip()
    refresh_token = str(_payload_value(payload, "refresh_token", "") or "").strip()
    user = _payload_value(payload, "user", {})

    if not access_token:
        raise RuntimeError("Supabase no devolvió un token de acceso.")

    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.user = user
    st.session_state.authenticated = True
    st.session_state.page = "Dashboard"


def _hero() -> None:
    st.html(
        """
        <section class="v2-login-hero">
            <div class="v2-login-brand">
                <div class="v2-login-logo">A</div>
                <div>
                    <strong>AXION PRIME</strong>
                    <small>PERFORMANCE COMMAND OS · X10</small>
                </div>
            </div>

            <div class="v2-login-copy">
                <div class="v2-eyebrow">TU VENTAJA EMPIEZA CON TUS DATOS</div>
                <h1>Opera con más <span>claridad.</span></h1>
                <p>
                    Registra, analiza y perfecciona cada operación desde un solo
                    centro de inteligencia. Convierte disciplina, riesgo y
                    psicología en una ventaja medible.
                </p>

                <div class="v2-login-features">
                    <div class="v2-login-feature"><b>▣</b>Track Record inteligente</div>
                    <div class="v2-login-feature"><b>◉</b>Auditoría visual con IA</div>
                    <div class="v2-login-feature"><b>☁</b>Psicotrading medible</div>
                    <div class="v2-login-feature"><b>⌁</b>Riesgo profesional</div>
                </div>
            </div>

            <div class="v2-login-stats">
                <div class="v2-login-stat"><small>AXION SCORE</small><strong>94/100</strong></div>
                <div class="v2-login-stat"><small>AI ENGINE</small><strong>24/7</strong></div>
                <div class="v2-login-stat"><small>PRIVACIDAD</small><strong>100%</strong></div>
            </div>
        </section>
        """
    )


def _login_tab() -> None:
    email = st.text_input(
        "Correo electrónico",
        placeholder="trader@correo.com",
        key="v2_login_email",
    )
    password = st.text_input(
        "Contraseña",
        type="password",
        placeholder="••••••••",
        key="v2_login_password",
    )
    remember = st.checkbox(
        "Mantener sesión iniciada",
        value=True,
        key="v2_login_remember",
    )

    if st.button(
        "⚡ Entrar a AXION",
        use_container_width=True,
        key="v2_login_button",
    ):
        clean_email = email.strip().lower()
        if not clean_email or not password:
            st.warning("Introduce correo y contraseña.")
            return

        try:
            with st.spinner("Conectando con AXION..."):
                payload = sign_in(clean_email, password)

            _save_session(payload)

            if not remember:
                st.session_state.refresh_token = ""

            st.rerun()
        except Exception as exc:
            st.error(f"No se pudo iniciar sesión: {exc}")


def _register_tab() -> None:
    email = st.text_input(
        "Correo electrónico",
        placeholder="nuevo@correo.com",
        key="v2_register_email",
    )
    password = st.text_input(
        "Contraseña",
        type="password",
        placeholder="Mínimo 6 caracteres",
        key="v2_register_password",
    )
    password_repeat = st.text_input(
        "Repetir contraseña",
        type="password",
        key="v2_register_password_repeat",
    )

    if st.button(
        "Crear cuenta AXION",
        use_container_width=True,
        key="v2_register_button",
    ):
        clean_email = email.strip().lower()

        if len(password) < 6:
            st.warning("La contraseña debe tener al menos 6 caracteres.")
            return
        if password != password_repeat:
            st.error("Las contraseñas no coinciden.")
            return

        try:
            with st.spinner("Creando cuenta..."):
                payload = sign_up(clean_email, password)

            if payload.get("access_token"):
                _save_session(payload)
                st.rerun()
            else:
                st.success("Cuenta creada. Revisa tu correo para confirmarla.")
        except Exception as exc:
            st.error(f"No se pudo crear la cuenta: {exc}")


def _reset_tab() -> None:
    email = st.text_input(
        "Correo registrado",
        placeholder="trader@correo.com",
        key="v2_reset_email",
    )

    if st.button(
        "Enviar enlace de recuperación",
        use_container_width=True,
        key="v2_reset_button",
    ):
        clean_email = email.strip().lower()
        if not clean_email:
            st.warning("Introduce tu correo electrónico.")
            return

        try:
            with st.spinner("Enviando enlace..."):
                reset_password(clean_email, APP_URL or "")
            st.success("Enlace enviado. Revisa también Spam.")
        except Exception as exc:
            st.error(f"No se pudo enviar el enlace: {exc}")


def _form() -> None:
    st.html(
        """
        <section class="v2-form-card">
            <div class="v2-form-logo">⚡</div>
            <h2>Bienvenido de vuelta 👋</h2>
            <p>Accede a tu centro de inteligencia operativa.</p>
        </section>
        """
    )

    login_tab, register_tab, reset_tab = st.tabs(
        ["Iniciar sesión", "Crear cuenta", "Recuperar"]
    )

    with login_tab:
        _login_tab()
    with register_tab:
        _register_tab()
    with reset_tab:
        _reset_tab()


def render_v2_auth() -> None:
    apply_v2_theme()
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    left, right = st.columns([1.22, 0.78], gap="large")

    with left:
        _hero()

    with right:
        _form()
