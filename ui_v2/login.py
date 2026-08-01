from __future__ import annotations

from typing import Any

import streamlit as st

from core.api import reset_password, sign_in, sign_up
from core.config import APP_URL
from ui_v2.theme import apply_v2_theme


# =========================================================
# AXION PRIME V2
# LOGIN CINEMATOGRÁFICO
# =========================================================


LOGIN_CSS = """
<style>

.v2-auth-shell {
    position: relative;

    min-height: calc(100vh - 95px);

    display: grid;
    grid-template-columns:
        minmax(0, 1.35fr)
        minmax(390px, 0.8fr);

    gap: 18px;

    overflow: hidden;
}


.v2-auth-hero {
    position: relative;

    min-height: 720px;

    display: flex;
    flex-direction: column;
    justify-content: space-between;

    overflow: hidden;

    padding:
        clamp(30px, 4vw, 58px);

    background:
        radial-gradient(
            circle at 78% 20%,
            rgba(25, 228, 255, 0.13),
            transparent 28%
        ),
        radial-gradient(
            circle at 22% 88%,
            rgba(139, 77, 255, 0.18),
            transparent 34%
        ),
        linear-gradient(
            145deg,
            rgba(4, 12, 29, 0.98),
            rgba(8, 5, 28, 0.98)
        );

    border:
        1px solid
        rgba(67, 113, 190, 0.34);

    border-radius: 26px;

    box-shadow:
        0 32px 100px
        rgba(0, 0, 0, 0.46);
}


.v2-auth-hero::before {
    content: "";

    position: absolute;
    inset: 0;

    pointer-events: none;

    background:
        linear-gradient(
            110deg,
            transparent 22%,
            rgba(25, 228, 255, 0.045) 50%,
            transparent 78%
        );

    transform:
        translateX(-120%);

    animation:
        v2-auth-scan
        9s
        ease-in-out
        infinite;
}


.v2-auth-hero::after {
    content: "";

    position: absolute;
    inset: 0;

    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(81, 113, 178, 0.045) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(81, 113, 178, 0.045) 1px,
            transparent 1px
        );

    background-size:
        52px 52px;

    mask-image:
        linear-gradient(
            to bottom,
            black,
            transparent 86%
        );
}


@keyframes v2-auth-scan {
    0%,
    55% {
        transform:
            translateX(-120%);
    }

    90%,
    100% {
        transform:
            translateX(120%);
    }
}


.v2-auth-brand,
.v2-auth-mini-brand {
    position: relative;
    z-index: 2;

    display: flex;
    align-items: center;

    gap: 13px;
}


.v2-auth-logo,
.v2-auth-mini-logo {
    width: 48px;
    height: 48px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    color:
        white;

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
        rgba(255, 255, 255, 0.13);

    border-radius: 14px;

    box-shadow:
        0 0 28px
        rgba(25, 228, 255, 0.28);
}


.v2-auth-brand-title,
.v2-auth-mini-title {
    color:
        var(--v2-white);

    font-size: 17px;
    font-weight: 950;
}


.v2-auth-brand-subtitle,
.v2-auth-mini-subtitle {
    margin-top: 4px;

    color:
        var(--v2-dim);

    font-size: 7px;
    font-weight: 850;

    letter-spacing: 1.9px;
}


.v2-auth-copy {
    position: relative;
    z-index: 2;

    max-width: 760px;

    margin:
        auto 0;
}


.v2-auth-copy h1 {
    margin:
        20px
        0
        0;

    color:
        var(--v2-white);

    font-size:
        clamp(48px, 5vw, 76px);

    line-height: 0.96;

    font-weight: 950;

    letter-spacing: -3.8px;
}


.v2-auth-copy h1 span {
    display: block;

    color:
        transparent;

    background:
        linear-gradient(
            90deg,
            var(--v2-cyan),
            #76a1ff,
            var(--v2-purple)
        );

    background-clip:
        text;

    -webkit-background-clip:
        text;
}


.v2-auth-copy p {
    max-width: 660px;

    margin-top: 23px;

    color:
        #9aa7c4;

    font-size: 15px;
    line-height: 1.75;
}


.v2-auth-feature-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 11px;

    margin-top: 29px;
}


.v2-auth-feature {
    display: flex;
    align-items: center;

    gap: 10px;

    padding:
        14px;

    color:
        #e1e8f9;

    font-size: 11px;
    font-weight: 780;

    background:
        rgba(5, 12, 29, 0.70);

    border:
        1px solid
        rgba(75, 105, 170, 0.25);

    border-radius: 13px;

    backdrop-filter:
        blur(12px);

    transition:
        transform 0.18s ease,
        border-color 0.18s ease;
}


.v2-auth-feature:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(25, 228, 255, 0.45);
}


.v2-auth-feature span {
    color:
        var(--v2-cyan);

    font-size: 16px;
}


.v2-auth-market {
    position: relative;
    z-index: 2;

    display: grid;

    grid-template-columns:
        repeat(3, minmax(0, 1fr));

    gap: 10px;
}


.v2-auth-market-card {
    padding:
        12px;

    background:
        rgba(4, 10, 25, 0.72);

    border:
        1px solid
        rgba(72, 101, 165, 0.23);

    border-radius: 12px;
}


.v2-auth-market-card small {
    display: block;

    color:
        var(--v2-dim);

    font-size: 7px;
    font-weight: 900;

    letter-spacing: 1.2px;
}


.v2-auth-market-card strong {
    display: block;

    margin-top: 7px;

    color:
        var(--v2-white);

    font-size: 16px;
}


.v2-auth-market-card span {
    display: block;

    margin-top: 4px;

    font-size: 8px;
    font-weight: 850;
}


.v2-auth-form-shell {
    min-height: 720px;

    display: flex;
    align-items: center;

    padding:
        clamp(24px, 3vw, 42px);

    background:
        radial-gradient(
            circle at 100% 0,
            rgba(139, 77, 255, 0.16),
            transparent 31%
        ),
        linear-gradient(
            145deg,
            rgba(8, 14, 31, 0.98),
            rgba(8, 5, 27, 0.98)
        );

    border:
        1px solid
        rgba(78, 104, 166, 0.29);

    border-radius: 26px;

    box-shadow:
        0 32px 100px
        rgba(0, 0, 0, 0.43);
}


.v2-auth-form-inner {
    width: 100%;
    max-width: 580px;

    margin:
        auto;
}


.v2-auth-form-header h2 {
    margin:
        25px
        0
        8px;

    color:
        var(--v2-white);

    font-size:
        clamp(30px, 3vw, 43px);

    line-height: 1.04;

    font-weight: 950;

    letter-spacing: -1.8px;
}


.v2-auth-form-header p {
    color:
        var(--v2-muted);

    font-size: 12px;
}


.v2-auth-secure {
    display: flex;
    align-items: center;

    gap: 8px;

    margin-top: 18px;

    padding:
        10px
        12px;

    color:
        #8ea0c0;

    font-size: 9px;

    background:
        rgba(4, 10, 25, 0.66);

    border:
        1px solid
        rgba(73, 100, 163, 0.22);

    border-radius: 11px;
}


.v2-auth-secure span {
    color:
        var(--v2-green);
}


[data-baseweb="tab-list"] {
    gap: 18px;

    border-bottom:
        1px solid
        rgba(84, 107, 166, 0.23);
}


[data-baseweb="tab"] {
    min-height: 42px;

    padding-left:
        0 !important;

    padding-right:
        0 !important;

    color:
        #8390ad !important;

    background:
        transparent !important;
}


[aria-selected="true"][data-baseweb="tab"] {
    color:
        var(--v2-cyan) !important;

    font-weight:
        900;
}


@media (max-width: 1050px) {

    .v2-auth-shell {
        grid-template-columns:
            1fr;
    }

    .v2-auth-hero,
    .v2-auth-form-shell {
        min-height:
            auto;
    }
}


@media (max-width: 680px) {

    .v2-auth-feature-grid,
    .v2-auth-market {
        grid-template-columns:
            1fr;
    }

    .v2-auth-copy h1 {
        font-size:
            43px;

        letter-spacing:
            -2.5px;
    }

    .v2-auth-hero,
    .v2-auth-form-shell {
        padding:
            24px;
    }
}

</style>
"""


# =========================================================
# SESIÓN
# =========================================================


def _payload_value(
    payload: Any,
    key: str,
    default: Any = None,
) -> Any:
    if payload is None:
        return default

    if isinstance(
        payload,
        dict,
    ):
        return payload.get(
            key,
            default,
        )

    return getattr(
        payload,
        key,
        default,
    )


def save_v2_session(
    payload: dict[str, Any],
) -> None:
    """
    Guarda la sesión devuelta por Supabase.
    """

    access_token = str(
        _payload_value(
            payload,
            "access_token",
            "",
        )
        or ""
    ).strip()

    refresh_token = str(
        _payload_value(
            payload,
            "refresh_token",
            "",
        )
        or ""
    ).strip()

    user = _payload_value(
        payload,
        "user",
        {},
    )

    if not access_token:
        raise RuntimeError(
            "Supabase no devolvió un token de acceso."
        )

    st.session_state.access_token = (
        access_token
    )

    st.session_state.refresh_token = (
        refresh_token
    )

    st.session_state.user = user

    st.session_state.authenticated = True

    st.session_state.page = "Dashboard"


# =========================================================
# BLOQUES VISUALES
# =========================================================


def _hero_html() -> str:
    return """
    <section class="v2-auth-hero">

        <div class="v2-auth-brand">

            <div class="v2-auth-logo">
                A
            </div>

            <div>
                <div class="v2-auth-brand-title">
                    AXION PRIME
                </div>

                <div class="v2-auth-brand-subtitle">
                    PERFORMANCE COMMAND OS · X10
                </div>
            </div>

        </div>

        <div class="v2-auth-copy">

            <div class="v2-eyebrow">
                TU VENTAJA EMPIEZA CON TUS DATOS
            </div>

            <h1>
                Opera con más
                <span>
                    claridad.
                </span>
            </h1>

            <p>
                Registra, analiza y perfecciona cada operación
                desde un solo centro de inteligencia. Convierte
                disciplina, riesgo y psicología en una ventaja
                medible.
            </p>

            <div class="v2-auth-feature-grid">

                <div class="v2-auth-feature">
                    <span>▣</span>
                    Track Record inteligente
                </div>

                <div class="v2-auth-feature">
                    <span>◉</span>
                    Auditoría visual con IA
                </div>

                <div class="v2-auth-feature">
                    <span>☁</span>
                    Psicotrading medible
                </div>

                <div class="v2-auth-feature">
                    <span>⌁</span>
                    Riesgo profesional
                </div>

            </div>

        </div>

        <div class="v2-auth-market">

            <div class="v2-auth-market-card">
                <small>AXION SCORE</small>
                <strong>94/100</strong>
                <span style="color:#00F58A">
                    SISTEMA ACTIVO
                </span>
            </div>

            <div class="v2-auth-market-card">
                <small>AI ENGINE</small>
                <strong>24/7</strong>
                <span style="color:#19E4FF">
                    ONLINE
                </span>
            </div>

            <div class="v2-auth-market-card">
                <small>PRIVACIDAD</small>
                <strong>100%</strong>
                <span style="color:#8B4DFF">
                    PROTEGIDA
                </span>
            </div>

        </div>

    </section>
    """


def _form_header_html() -> str:
    return """
    <section class="v2-auth-form-header">

        <div class="v2-auth-mini-brand">

            <div class="v2-auth-mini-logo">
                ⚡
            </div>

            <div>
                <div class="v2-auth-mini-title">
                    ACCESO SEGURO
                </div>

                <div class="v2-auth-mini-subtitle">
                    INTELIGENCIA · DISCIPLINA · VENTAJA
                </div>
            </div>

        </div>

        <h2>
            Bienvenido de vuelta 👋
        </h2>

        <p>
            Accede a tu centro de inteligencia operativa.
        </p>

    </section>
    """


# =========================================================
# FORMULARIOS
# =========================================================


def _render_login_tab() -> None:
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
        clean_email = (
            email
            .strip()
            .lower()
        )

        if not clean_email:
            st.warning(
                "Introduce tu correo electrónico."
            )
            return

        if not password:
            st.warning(
                "Introduce tu contraseña."
            )
            return

        try:
            with st.spinner(
                "Conectando con AXION..."
            ):
                payload = sign_in(
                    clean_email,
                    password,
                )

            save_v2_session(
                payload
            )

            if not remember:
                st.session_state.refresh_token = ""

            st.success(
                "Sesión iniciada correctamente."
            )

            st.rerun()

        except Exception as exc:
            st.error(
                f"No se pudo iniciar sesión: {exc}"
            )


def _render_register_tab() -> None:
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

    accept_terms = st.checkbox(
        "Acepto las condiciones de uso",
        key="v2_register_terms",
    )

    if st.button(
        "Crear cuenta AXION",
        use_container_width=True,
        key="v2_register_button",
    ):
        clean_email = (
            email
            .strip()
            .lower()
        )

        if not clean_email:
            st.warning(
                "Introduce un correo electrónico."
            )
            return

        if len(password) < 6:
            st.warning(
                "La contraseña debe tener al menos "
                "6 caracteres."
            )
            return

        if password != password_repeat:
            st.error(
                "Las contraseñas no coinciden."
            )
            return

        if not accept_terms:
            st.warning(
                "Debes aceptar las condiciones de uso."
            )
            return

        try:
            with st.spinner(
                "Creando cuenta..."
            ):
                payload = sign_up(
                    clean_email,
                    password,
                )

            if payload.get(
                "access_token"
            ):
                save_v2_session(
                    payload
                )

                st.success(
                    "Cuenta creada correctamente."
                )

                st.rerun()

            else:
                st.success(
                    "Cuenta creada. Revisa tu correo "
                    "para confirmar el registro."
                )

        except Exception as exc:
            st.error(
                f"No se pudo crear la cuenta: {exc}"
            )


def _render_reset_tab() -> None:
    email = st.text_input(
        "Correo registrado",
        placeholder="trader@correo.com",
        key="v2_reset_email",
    )

    st.info(
        "Recibirás un enlace seguro para cambiar "
        "tu contraseña."
    )

    if st.button(
        "Enviar enlace de recuperación",
        use_container_width=True,
        key="v2_reset_button",
    ):
        clean_email = (
            email
            .strip()
            .lower()
        )

        if not clean_email:
            st.warning(
                "Introduce tu correo electrónico."
            )
            return

        try:
            with st.spinner(
                "Enviando enlace..."
            ):
                reset_password(
                    clean_email,
                    APP_URL or "",
                )

            st.success(
                "Enlace enviado. Revisa también Spam."
            )

        except Exception as exc:
            st.error(
                f"No se pudo enviar el enlace: {exc}"
            )


def render_v2_login_form() -> None:
    """
    Renderiza las pestañas del formulario.
    """

    st.html(
        _form_header_html()
    )

    login_tab, register_tab, reset_tab = st.tabs(
        [
            "Iniciar sesión",
            "Crear cuenta",
            "Recuperar",
        ]
    )

    with login_tab:
        _render_login_tab()

    with register_tab:
        _render_register_tab()

    with reset_tab:
        _render_reset_tab()

    st.html(
        """
        <div class="v2-auth-secure">
            <span>●</span>
            Conexión cifrada · Sesión protegida · Supabase Auth
        </div>
        """
    )


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================


def render_v2_auth() -> None:
    """
    Renderiza el login completo de AXION PRIME V2.
    """

    apply_v2_theme()

    st.markdown(
        LOGIN_CSS,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [
            1.35,
            0.8,
        ],
        gap="medium",
    )

    with left:
        st.html(
            _hero_html()
        )

    with right:
        st.html(
            """
            <section class="v2-auth-form-shell">
                <div class="v2-auth-form-inner">
            """
        )

        render_v2_login_form()

        st.html(
            """
                </div>
            </section>
            """
        )
