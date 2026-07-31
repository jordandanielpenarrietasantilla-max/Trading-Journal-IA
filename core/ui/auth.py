from __future__ import annotations

import streamlit as st

from core.api import (
    reset_password,
    sign_in,
    sign_up,
)

from core.config import APP_URL


# =========================================================
# AXION PRIME X10 PRO
# LOGIN / REGISTRO / RECUPERACIÓN
# =========================================================


def save_session(
    payload: dict,
) -> None:
    """
    Guarda los tokens y el usuario en session_state.
    """

    access_token = payload.get(
        "access_token",
        "",
    )

    refresh_token = payload.get(
        "refresh_token",
        "",
    )

    user = payload.get(
        "user",
    )


    if not access_token:

        raise RuntimeError(
            "Supabase no devolvió access_token."
        )


    st.session_state.access_token = (
        access_token
    )

    st.session_state.refresh_token = (
        refresh_token
    )

    st.session_state.user = (
        user
    )

    st.session_state.authenticated = (
        True
    )

    st.session_state.page = (
        "Dashboard"
    )


# =========================================================
# PANEL IZQUIERDO DEL LOGIN
# =========================================================

def render_login_presentation() -> None:

    st.markdown(
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
                    margin-bottom:34px;
                "
            >

                <div class="ax-logo">
                    A
                </div>

                <div>

                    <div
                        style="
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
                    letter-spacing:2.4px;
                    font-weight:900;
                "
            >
                TU VENTAJA EMPIEZA CON TUS DATOS
            </div>


            <div
                style="
                    font-size:62px;
                    line-height:1.02;
                    font-weight:950;
                    margin-top:25px;
                    letter-spacing:-3px;
                "
            >
                Opera con más
                <br>

                <span
                    style="
                        background:
                            linear-gradient(
                                90deg,
                                #25e5ff,
                                #7d8cff,
                                #a146ff
                            );

                        -webkit-background-clip:text;
                        -webkit-text-fill-color:transparent;
                    "
                >
                    claridad.
                </span>
            </div>


            <div
                style="
                    color:#9aa7c8;
                    font-size:16px;
                    line-height:1.8;
                    max-width:590px;
                    margin-top:26px;
                "
            >
                Convierte cada operación en inteligencia accionable.
                Analiza rendimiento, disciplina, riesgo y emociones
                desde un solo sistema operativo para traders.
            </div>


            <div
                style="
                    display:grid;
                    grid-template-columns:1fr 1fr;
                    gap:12px;
                    margin-top:34px;
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
                    📈 Métricas de rendimiento
                </div>

            </div>


            <div
                style="
                    margin-top:42px;
                    padding:17px;
                    border-left:3px solid #25e5ff;
                    border-radius:5px;
                    background:
                        rgba(
                            10,
                            15,
                            38,
                            0.72
                        );
                    color:#8fa0c6;
                    font-size:12px;
                "
            >
                “La consistencia no se adivina.
                Se diseña, se mide y se mejora.”
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FORMULARIO LOGIN
# =========================================================

def render_login_form() -> None:

    st.markdown(
        """
        <div
            style="
                display:flex;
                align-items:center;
                gap:12px;
                margin-bottom:28px;
            "
        >

            <div class="ax-logo">
                ⚡
            </div>

            <div>

                <div
                    style="
                        font-weight:950;
                        font-size:16px;
                    "
                >
                    AXION PRIME
                </div>

                <div
                    style="
                        color:#687594;
                        font-size:8px;
                        letter-spacing:1.8px;
                    "
                >
                    INTELIGENCIA · DISCIPLINA · VENTAJA
                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div
            style="
                font-size:40px;
                line-height:1.1;
                font-weight:950;
                color:#25e5ff;
                margin-bottom:10px;
            "
        >
            Bienvenido de vuelta 👋
        </div>

        <div
            style="
                color:#8d99ba;
                font-size:13px;
                margin-bottom:25px;
            "
        >
            Accede a tu centro de inteligencia de trading.
        </div>
        """,
        unsafe_allow_html=True,
    )


    login_tab, register_tab, reset_tab = st.tabs(
        [
            "Iniciar sesión",
            "Crear cuenta",
            "Recuperar",
        ]
    )


    # =====================================================
    # LOGIN
    # =====================================================

    with login_tab:

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

            if not email or not password:

                st.warning(
                    "Completa el correo y la contraseña."
                )

            else:

                try:

                    with st.spinner(
                        "Conectando con AXION..."
                    ):

                        payload = sign_in(
                            email,
                            password,
                        )


                    save_session(
                        payload
                    )


                    if not remember:

                        st.session_state.refresh_token = (
                            ""
                        )


                    st.success(
                        "Sesión iniciada correctamente."
                    )


                    st.rerun()


                except Exception as exc:

                    st.error(
                        "No se pudo iniciar sesión: "
                        f"{exc}"
                    )


        st.markdown("---")


        st.caption(
            "Acceso seguro mediante Supabase Auth"
        )


    # =====================================================
    # CREAR CUENTA
    # =====================================================

    with register_tab:

        email = st.text_input(
            "Correo electrónico",
            placeholder="nuevo@correo.com",
            key="register_email",
        )


        password = st.text_input(
            "Contraseña",
            type="password",
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

            if not email or not password:

                st.warning(
                    "Completa todos los campos."
                )


            elif password != password_repeat:

                st.error(
                    "Las contraseñas no coinciden."
                )


            elif len(password) < 6:

                st.error(
                    "La contraseña debe tener "
                    "al menos 6 caracteres."
                )


            elif not accept_terms:

                st.warning(
                    "Debes aceptar las condiciones."
                )


            else:

                try:

                    with st.spinner(
                        "Creando cuenta..."
                    ):

                        payload = sign_up(
                            email,
                            password,
                        )


                    if payload.get(
                        "access_token"
                    ):

                        save_session(
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
                        "No se pudo crear la cuenta: "
                        f"{exc}"
                    )


    # =====================================================
    # RECUPERAR CONTRASEÑA
    # =====================================================

    with reset_tab:

        email = st.text_input(
            "Correo registrado",
            placeholder="trader@correo.com",
            key="reset_email",
        )


        st.info(
            "Recibirás un enlace para cambiar "
            "tu contraseña."
        )


        if st.button(
            "Enviar enlace de recuperación",
            use_container_width=True,
            key="reset_button",
        ):

            if not email:

                st.warning(
                    "Introduce tu correo."
                )


            else:

                try:

                    redirect_url = (
                        APP_URL
                        if APP_URL
                        else ""
                    )


                    with st.spinner(
                        "Enviando enlace..."
                    ):

                        reset_password(
                            email,
                            redirect_url,
                        )


                    st.success(
                        "Enlace enviado. Revisa también Spam."
                    )


                except Exception as exc:

                    st.error(
                        "No se pudo enviar el enlace: "
                        f"{exc}"
                    )


# =========================================================
# PANTALLA COMPLETA
# =========================================================

def render_auth() -> None:

    st.markdown(
        """
        <div
            style="
                height:10px;
            "
        ></div>
        """,
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

        st.markdown(
            """
            <div
                class="ax-card"
                style="
                    padding:34px;
                    min-height:610px;
                "
            >
            """,
            unsafe_allow_html=True,
        )


        render_login_form()


        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )
