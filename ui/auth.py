from __future__ import annotations

from textwrap import dedent
from typing import Any

import streamlit as st

from core.api import (
    reset_password,
    sign_in,
    sign_up,
)
from core.config import APP_URL


# =========================================================
# AXION PRIME X10 PRO
# AUTENTICACIÓN
# =========================================================


def _get_payload_value(
    payload: Any,
    key: str,
    default: Any = None,
) -> Any:
    """
    Lee valores de una respuesta recibida como diccionario
    u objeto.
    """

    if payload is None:
        return default

    if isinstance(payload, dict):
        return payload.get(key, default)

    return getattr(payload, key, default)


def save_session(
    payload: dict[str, Any],
) -> None:
    """
    Guarda la sesión devuelta por Supabase.
    """

    if not isinstance(payload, dict):
        raise RuntimeError(
            "Supabase devolvió una sesión con formato inválido."
        )

    access_token = str(
        _get_payload_value(
            payload,
            "access_token",
            "",
        )
        or ""
    ).strip()

    refresh_token = str(
        _get_payload_value(
            payload,
            "refresh_token",
            "",
        )
        or ""
    ).strip()

    user = _get_payload_value(
        payload,
        "user",
        {},
    )

    if not access_token:
        raise RuntimeError(
            "Supabase no devolvió el token de acceso. "
            "Verifica que el correo esté confirmado."
        )

    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.user = user
    st.session_state.authenticated = True
    st.session_state.page = "Dashboard"


# =========================================================
# PRESENTACIÓN DEL LOGIN
# =========================================================


def render_login_presentation() -> None:
    """
    Renderiza el panel visual izquierdo.
    """

    html = dedent(
        """
        <div
            class="ax-hero"
            style="
                min-height:610px;
                display:flex;
                flex-direction:column;
                justify-content:center;
                padding:45px;
            "
        >
            <div
                style="
                    display:flex;
                    align-items:center;
                    gap:14px;
                    margin-bottom:32px;
                "
            >
                <div class="ax-logo">
                    A
                </div>

                <div>
                    <div
                        style="
                            color:#f5f7ff;
                            font-size:18px;
                            font-weight:950;
                        "
                    >
                        AXION PRIME
                    </div>

                    <div
                        style="
                            color:#687594;
                            font-size:8px;
                            letter-spacing:2px;
                            margin-top:4px;
                        "
                    >
                        PERFORMANCE COMMAND OS · X10
                    </div>
                </div>
            </div>

            <div
                style="
                    color:#25e5ff;
                    font-size:11px;
                    letter-spacing:2.2px;
                    font-weight:900;
                "
            >
                TU VENTAJA EMPIEZA CON TUS DATOS
            </div>

            <div
                style="
                    color:#f5f7ff;
                    font-size:58px;
                    line-height:1.04;
                    font-weight:950;
                    letter-spacing:-2.5px;
                    margin-top:24px;
                "
            >
                Opera con más<br>

                <span
                    style="
                        background:linear-gradient(
                            90deg,
                            #25e5ff,
                            #768cff,
                            #a146ff
                        );
                        -webkit-background-clip:text;
                        background-clip:text;
                        -webkit-text-fill-color:transparent;
                        color:transparent;
                    "
                >
                    claridad.
                </span>
            </div>

            <div
                style="
                    color:#9aa7c8;
                    font-size:16px;
                    line-height:1.75;
                    max-width:590px;
                    margin-top:25px;
                "
            >
                Convierte cada operación en inteligencia accionable.
                Analiza tu rendimiento, disciplina, gestión de riesgo
                y emociones desde un solo sistema operativo para traders.
            </div>

            <div
                style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:12px;
                    margin-top:32px;
                "
            >
                <div class="ax-card">
                    📊 Track Record inteligente
                </div>

                <div class="ax-card">
                    🧠 Auditoría visual con IA
                </div>

                <div class="ax-card">
                    💭 Psicotrading medible
                </div>

                <div class="ax-card">
                    📈 Métricas profesionales
                </div>
            </div>

            <div
                style="
                    margin-top:38px;
                    padding:16px;
                    border-left:3px solid #25e5ff;
                    border-radius:5px;
                    background:rgba(10,15,38,.72);
                    color:#8fa0c6;
                    font-size:12px;
                "
            >
                “La consistencia no se adivina.
                Se diseña, se mide y se mejora.”
            </div>
        </div>
        """
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# =========================================================
# ENCABEZADO DEL FORMULARIO
# =========================================================


def _render_form_header() -> None:
    html = dedent(
        """
        <div
            style="
                display:flex;
                align-items:center;
                gap:12px;
                margin-bottom:26px;
            "
        >
            <div class="ax-logo">
                ⚡
            </div>

            <div>
                <div
                    style="
                        color:#f5f7ff;
                        font-size:16px;
                        font-weight:950;
                    "
                >
                    AXION PRIME
                </div>

                <div
                    style="
                        color:#687594;
                        font-size:8px;
                        letter-spacing:1.8px;
                        margin-top:3px;
                    "
                >
                    INTELIGENCIA · DISCIPLINA · VENTAJA
                </div>
            </div>
        </div>

        <div
            style="
                color:#25e5ff;
                font-size:38px;
                line-height:1.1;
                font-weight:950;
                letter-spacing:-1.5px;
                margin-bottom:10px;
            "
        >
            Bienvenido de vuelta 👋
        </div>

        <div
            style="
                color:#8d99ba;
                font-size:13px;
                margin-bottom:24px;
            "
        >
            Accede a tu centro de inteligencia de trading.
        </div>
        """
    )

    st.markdown(
        html,
        unsafe_allow_html=True,
    )


# =========================================================
# INICIAR SESIÓN
# =========================================================


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

    st.markdown("---")

    st.caption(
        "🔐 Acceso seguro mediante Supabase Auth"
    )


# =========================================================
# CREAR CUENTA
# =========================================================


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
                "Creando tu cuenta..."
            ):
                payload = sign_up(
                    clean_email,
                    password,
                )

            access_token = str(
                payload.get(
                    "access_token",
                    "",
                )
                or ""
            ).strip()

            if access_token:
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


# =========================================================
# RECUPERAR CONTRASEÑA
# =========================================================


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
                "Enlace enviado. Revisa también "
                "la carpeta de correo no deseado."
            )

        except Exception as exc:
            st.error(
                f"No se pudo enviar el enlace: {exc}"
            )


# =========================================================
# FORMULARIO COMPLETO
# =========================================================


def render_login_form() -> None:
    """
    Renderiza login, registro y recuperación.
    """

    _render_form_header()

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


# =========================================================
# PANTALLA COMPLETA
# =========================================================


def render_auth() -> None:
    """
    Renderiza la pantalla completa de autenticación.

    No abre etiquetas HTML en una llamada para cerrarlas
    en otra, evitando paneles vacíos o HTML visible.
    """

    st.markdown(
        "<div style='height:8px;'></div>",
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [
            1.28,
            1,
        ],
        gap="large",
    )

    with left:
        render_login_presentation()

    with right:
        render_login_form()
