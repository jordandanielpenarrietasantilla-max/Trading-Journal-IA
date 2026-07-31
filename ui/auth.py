from __future__ import annotations

from typing import Any

import streamlit as st

from core.api import reset_password, sign_in, sign_up
from core.config import APP_URL


# =========================================================
# AXION PRIME X10 PRO
# AUTENTICACIÓN COMPLETA
# =========================================================


def _payload_value(
    payload: Any,
    key: str,
    default: Any = None,
) -> Any:
    if payload is None:
        return default

    if isinstance(payload, dict):
        return payload.get(key, default)

    return getattr(payload, key, default)


def save_session(
    payload: dict[str, Any],
) -> None:
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

    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.user = user
    st.session_state.authenticated = True
    st.session_state.page = "Dashboard"


def _hero_html() -> str:
    return """
    <section class="ax-auth-hero">
        <div class="ax-auth-brand">
            <div class="ax-auth-logo">A</div>

            <div>
                <div class="ax-auth-brand-title">
                    AXION PRIME
                </div>

                <div class="ax-auth-brand-subtitle">
                    PERFORMANCE COMMAND OS · X10
                </div>
            </div>
        </div>

        <div class="ax-auth-eyebrow">
            TU VENTAJA EMPIEZA CON TUS DATOS
        </div>

        <h1 class="ax-auth-title">
            Opera con más
            <span>claridad.</span>
        </h1>

        <p class="ax-auth-description">
            Convierte cada operación en inteligencia accionable.
            Analiza tu rendimiento, disciplina, riesgo y emociones
            desde un solo centro operativo para traders.
        </p>

        <div class="ax-auth-feature-grid">
            <div class="ax-auth-feature">
                📊 Track Record inteligente
            </div>

            <div class="ax-auth-feature">
                🧠 Auditoría visual con IA
            </div>

            <div class="ax-auth-feature">
                💭 Psicotrading medible
            </div>

            <div class="ax-auth-feature">
                📈 Métricas profesionales
            </div>
        </div>

        <div class="ax-auth-quote">
            “La consistencia no se adivina.
            Se diseña, se mide y se mejora.”
        </div>
    </section>
    """


def _form_header_html() -> str:
    return """
    <section class="ax-auth-form-header">
        <div class="ax-auth-mini-brand">
            <div class="ax-auth-mini-logo">⚡</div>

            <div>
                <div class="ax-auth-mini-title">
                    AXION PRIME
                </div>

                <div class="ax-auth-mini-subtitle">
                    INTELIGENCIA · DISCIPLINA · VENTAJA
                </div>
            </div>
        </div>

        <h2>Bienvenido de vuelta 👋</h2>

        <p>
            Accede a tu centro de inteligencia de trading.
        </p>
    </section>
    """


def _render_login_tab() -> None:
    email = st.text_input(
        "Correo electrónico",
        placeholder="trader@correo.com",
        key="login_email",
    )

    password = st.text_input(
        "Contraseña",
        type="password",
        placeholder="••••••••",
        key="login_password",
    )

    remember = st.checkbox(
        "Mantener sesión iniciada",
        value=True,
        key="login_remember",
    )

    if st.button(
        "⚡ Entrar a AXION",
        use_container_width=True,
        key="login_button",
    ):
        clean_email = email.strip().lower()

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

            save_session(payload)

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
        key="register_email",
    )

    password = st.text_input(
        "Contraseña",
        type="password",
        placeholder="Mínimo 6 caracteres",
        key="register_password",
    )

    password_repeat = st.text_input(
        "Repetir contraseña",
        type="password",
        key="register_password_repeat",
    )

    accept_terms = st.checkbox(
        "Acepto las condiciones de uso",
        key="register_terms",
    )

    if st.button(
        "Crear cuenta AXION",
        use_container_width=True,
        key="register_button",
    ):
        clean_email = email.strip().lower()

        if not clean_email:
            st.warning(
                "Introduce un correo electrónico."
            )
            return

        if len(password) < 6:
            st.warning(
                "La contraseña debe tener al menos 6 caracteres."
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

            if payload.get("access_token"):
                save_session(payload)
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
        key="reset_email",
    )

    st.info(
        "Recibirás un enlace seguro para cambiar "
        "tu contraseña."
    )

    if st.button(
        "Enviar enlace de recuperación",
        use_container_width=True,
        key="reset_button",
    ):
        clean_email = email.strip().lower()

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


def render_login_form() -> None:
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


def render_auth() -> None:
    st.html(
        "<div class='ax-auth-spacer'></div>"
    )

    left, right = st.columns(
        [1.25, 1],
        gap="large",
    )

    with left:
        st.html(
            _hero_html()
        )

    with right:
        st.html(
            "<div class='ax-auth-form-shell'>"
            "<div class='ax-auth-form-inner'>"
        )

        render_login_form()

        st.html(
            "</div></div>"
        )
