from __future__ import annotations

from typing import Any

import streamlit as st

from core.api import reset_password, sign_in, sign_up
from core.config import APP_URL
from ui_v2.theme import apply_v2_theme


LOGIN_CSS = """
<style>
[data-testid="stSidebar"] {
    display: none !important;
}

html,
body,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at 10% 10%, rgba(25,228,255,.08), transparent 22%),
        radial-gradient(circle at 90% 12%, rgba(139,77,255,.09), transparent 24%),
        linear-gradient(180deg,#020713 0%,#030514 55%,#020711 100%) !important;
}

.block-container {
    max-width: 1780px;
    padding-top: .8rem;
    padding-bottom: 1rem;
}

.v2-login-root {
    position: relative;
    isolation: isolate;
}

.v2-login-root::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: -2;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(74,103,171,.032) 1px, transparent 1px),
        linear-gradient(90deg, rgba(74,103,171,.032) 1px, transparent 1px);
    background-size: 46px 46px;
}

.v2-column-card {
    position: relative;
    min-height: 920px;
    overflow: hidden;
    padding: 26px;
    border: 1px solid rgba(73,108,188,.38);
    border-radius: 24px;
    background:
        radial-gradient(circle at 100% 0%, rgba(139,77,255,.13), transparent 28%),
        linear-gradient(145deg, rgba(6,13,31,.99), rgba(5,7,23,.99));
    box-shadow:
        0 28px 82px rgba(0,0,0,.42),
        inset 0 1px 0 rgba(255,255,255,.03);
}

.v2-column-card::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        linear-gradient(rgba(79,108,173,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(79,108,173,.03) 1px, transparent 1px);
    background-size: 42px 42px;
}

.v2-brand,
.v2-hero-copy,
.v2-feature-stack,
.v2-holo,
.v2-hero-stats,
.v2-security-grid,
.v2-payment-panel,
.v2-center-shell {
    position: relative;
    z-index: 2;
}

/* =====================================================
   COLUMNA IZQUIERDA
   ===================================================== */

.v2-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}

.v2-logo {
    width: 48px;
    height: 48px;
    display: grid;
    place-items: center;
    color: white;
    font-size: 18px;
    font-weight: 950;
    background: linear-gradient(145deg,#19e4ff,#3c7dff 55%,#8b4dff);
    border-radius: 14px;
    box-shadow: 0 0 28px rgba(25,228,255,.26);
}

.v2-brand strong {
    display: block;
    color: #f7f9ff;
    font-size: 18px;
    font-weight: 950;
}

.v2-brand small {
    display: block;
    margin-top: 3px;
    color: #66738f;
    font-size: 6px;
    font-weight: 900;
    letter-spacing: 1.5px;
}

.v2-hero-copy {
    margin-top: 25px;
}

.v2-hero-chip {
    display: inline-flex;
    padding: 6px 10px;
    color: #2bdcff;
    font-size: 7px;
    font-weight: 950;
    letter-spacing: .8px;
    border: 1px solid rgba(43,220,255,.32);
    border-radius: 999px;
    background: rgba(43,220,255,.06);
}

.v2-hero-copy h1 {
    margin: 15px 0 0;
    color: #f7f9ff;
    font-size: clamp(42px,4vw,66px);
    line-height: .95;
    letter-spacing: -3px;
    font-weight: 950;
    text-transform: uppercase;
}

.v2-hero-copy h1 span {
    display: block;
    color: transparent;
    background: linear-gradient(90deg,#19e4ff,#69a3ff,#8b4dff,#ff4bc8);
    -webkit-background-clip: text;
    background-clip: text;
}

.v2-hero-copy p {
    margin-top: 17px;
    color: #9aa7c4;
    font-size: 13px;
    line-height: 1.65;
}

.v2-feature-stack {
    display: grid;
    gap: 8px;
    margin-top: 21px;
}

.v2-feature-item {
    display: grid;
    grid-template-columns: 42px 1fr;
    gap: 10px;
    align-items: center;
    padding: 11px;
    border: 1px solid rgba(var(--rgb),.25);
    border-radius: 13px;
    background:
        radial-gradient(circle at 0 50%, rgba(var(--rgb),.12), transparent 24%),
        rgba(4,10,25,.76);
}

.v2-feature-icon {
    width: 38px;
    height: 38px;
    display: grid;
    place-items: center;
    color: rgb(var(--rgb));
    font-size: 19px;
    border-radius: 12px;
    background: rgba(var(--rgb),.10);
    border: 1px solid rgba(var(--rgb),.28);
}

.v2-feature-item strong {
    display: block;
    color: #f4f7ff;
    font-size: 9.5px;
    font-weight: 950;
}

.v2-feature-item span {
    display: block;
    margin-top: 2px;
    color: #8492ae;
    font-size: 6.6px;
    line-height: 1.4;
}

.v2-holo {
    height: 175px;
    margin-top: 18px;
    overflow: hidden;
    border: 1px solid rgba(61,116,225,.28);
    border-radius: 17px;
    background:
        radial-gradient(circle at 50% 66%,rgba(25,228,255,.24),transparent 12%),
        radial-gradient(circle at 50% 50%,rgba(139,77,255,.17),transparent 34%),
        linear-gradient(180deg,rgba(5,14,35,.95),rgba(3,8,20,.98));
}

.v2-holo::before {
    content: "A";
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
    color: transparent;
    font-size: 108px;
    font-weight: 950;
    background: linear-gradient(180deg,#2bdcff,#6c5cff,#e84dff);
    -webkit-background-clip: text;
    background-clip: text;
    filter: drop-shadow(0 0 22px rgba(43,220,255,.38));
}

.v2-holo::after {
    content: "";
    position: absolute;
    left: 14%;
    right: 14%;
    bottom: 15px;
    height: 58px;
    border-radius: 50%;
    border: 2px solid rgba(43,220,255,.42);
    box-shadow:
        0 0 26px rgba(43,220,255,.28),
        inset 0 0 26px rgba(139,77,255,.20);
    transform: perspective(280px) rotateX(72deg);
}

.v2-hero-stats {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 8px;
    margin-top: 12px;
}

.v2-stat {
    padding: 11px;
    text-align: center;
    background: rgba(4,10,25,.78);
    border: 1px solid rgba(72,101,165,.24);
    border-radius: 11px;
}

.v2-stat small {
    display: block;
    color: #687590;
    font-size: 5.7px;
    font-weight: 900;
    letter-spacing: 1px;
}

.v2-stat strong {
    display: block;
    margin-top: 5px;
    color: #2bdcff;
    font-size: 17px;
}

.v2-security-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 8px;
    margin-top: 10px;
}

.v2-security-card {
    padding: 11px;
    border: 1px solid rgba(139,77,255,.28);
    border-radius: 11px;
    background: rgba(4,10,25,.78);
}

.v2-security-card strong {
    display: block;
    color: #f4f7ff;
    font-size: 8.5px;
}

.v2-security-card span {
    display: block;
    margin-top: 3px;
    color: #8997b4;
    font-size: 6.4px;
    line-height: 1.35;
}

/* =====================================================
   COLUMNA CENTRAL
   ===================================================== */

.v2-center-shell {
    display: flex;
    flex-direction: column;
    min-height: 868px;
}

.v2-form-head {
    padding: 24px 22px 18px;
    text-align: center;
    border: 1px solid rgba(72,107,183,.34);
    border-radius: 18px;
    background:
        radial-gradient(circle at 100% 0%,rgba(139,77,255,.14),transparent 28%),
        linear-gradient(145deg,rgba(8,16,35,.98),rgba(6,8,25,.98));
}

.v2-form-logo {
    width: 46px;
    height: 46px;
    display: grid;
    place-items: center;
    margin: auto;
    color: white;
    font-size: 18px;
    background: linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);
    border-radius: 14px;
    box-shadow: 0 0 24px rgba(25,228,255,.24);
}

.v2-form-head h2 {
    margin: 17px 0 5px;
    color: #f7f9ff;
    font-size: 30px;
    line-height: 1.02;
    letter-spacing: -1.4px;
    font-weight: 950;
}

.v2-form-head p {
    color: #91a0bf;
    font-size: 9.5px;
    margin: 0;
}

.v2-form-body {
    margin-top: 14px;
    padding: 0 2px;
}

.v2-center-benefits {
    margin-top: auto;
    display: grid;
    gap: 9px;
}

.v2-center-benefit {
    padding: 11px 12px;
    border: 1px solid rgba(72,101,165,.22);
    border-radius: 11px;
    background: rgba(4,10,25,.74);
}

.v2-center-benefit strong {
    display: block;
    color: #eef4ff;
    font-size: 8px;
}

.v2-center-benefit span {
    display: block;
    margin-top: 3px;
    color: #7f8fac;
    font-size: 6.4px;
    line-height: 1.35;
}

[data-baseweb="tab-list"] {
    gap: 16px;
    border-bottom: 1px solid rgba(84,107,166,.23);
}

[data-baseweb="tab"] {
    min-height: 40px;
    padding-left: 0 !important;
    padding-right: 0 !important;
    background: transparent !important;
    color: #8390ad !important;
}

[aria-selected="true"][data-baseweb="tab"] {
    color: #19e4ff !important;
    font-weight: 900;
}

/* =====================================================
   COLUMNA DERECHA
   ===================================================== */

.v2-payment-panel {
    min-height: 868px;
    display: flex;
    flex-direction: column;
}

.v2-payment-title {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    color: #2bdcff;
    font-size: 10px;
    font-weight: 950;
}

.v2-payment-title::before,
.v2-payment-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg,transparent,#2bdcff,#8b4dff,transparent);
}

.v2-payment-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 8px;
}

.v2-pay-card {
    min-height: 78px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 11px;
    text-align: center;
    border: 1px solid rgba(var(--rgb),.34);
    border-radius: 12px;
    background:
        radial-gradient(circle at 100% 0%,rgba(var(--rgb),.13),transparent 34%),
        rgba(5,11,28,.92);
}

.v2-pay-card.wide {
    grid-column: span 2;
}

.v2-pay-logo {
    color: rgb(var(--rgb));
    font-size: 20px;
    font-weight: 950;
}

.v2-pay-card strong {
    margin-top: 5px;
    color: #f5f7ff;
    font-size: 8.5px;
}

.v2-pay-card span {
    margin-top: 3px;
    color: #8391ad;
    font-size: 5.8px;
}

.v2-crypto-grid {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 8px;
    margin-top: 8px;
}

.v2-trial {
    margin-top: 12px;
    padding: 13px;
    text-align: center;
    border: 1px solid rgba(139,77,255,.32);
    border-radius: 13px;
    background:
        radial-gradient(circle at 50% 0%,rgba(139,77,255,.13),transparent 44%),
        rgba(5,11,28,.92);
}

.v2-trial strong {
    display: block;
    color: #c7ff57;
    font-size: 17px;
    font-weight: 950;
}

.v2-trial span {
    display: block;
    margin-top: 4px;
    color: #9aa7c1;
    font-size: 6.6px;
}

.v2-price-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 8px;
    margin-top: 10px;
}

.v2-price-card {
    padding: 13px;
    text-align: center;
    border: 1px solid rgba(25,228,255,.28);
    border-radius: 12px;
    background: rgba(5,11,28,.92);
}

.v2-price-card.annual {
    border-color: rgba(214,72,255,.46);
}

.v2-price-card small {
    color: #2bdcff;
    font-size: 6.6px;
    font-weight: 950;
}

.v2-price-card strong {
    display: block;
    margin-top: 6px;
    color: #f5f7ff;
    font-size: 23px;
}

.v2-price-card span {
    color: #7f8fac;
    font-size: 5.8px;
}

.v2-payment-trust {
    margin-top: auto;
    display: grid;
    gap: 8px;
}

.v2-trust-card {
    padding: 10px 11px;
    border: 1px solid rgba(72,101,165,.21);
    border-radius: 11px;
    background: rgba(4,10,25,.74);
}

.v2-trust-card strong {
    display: block;
    color: #eef4ff;
    font-size: 7.6px;
}

.v2-trust-card span {
    display: block;
    margin-top: 3px;
    color: #7f8fac;
    font-size: 6.2px;
    line-height: 1.35;
}

.v2-footer-bar {
    margin-top: 9px;
    padding: 10px 12px;
    color: #7e8da8;
    font-size: 6.7px;
    text-align: center;
    border: 1px solid rgba(72,101,165,.18);
    border-radius: 10px;
    background: rgba(4,10,25,.72);
}

@media (max-width: 1200px) {
    .v2-column-card {
        min-height: auto;
    }

    .v2-center-shell,
    .v2-payment-panel {
        min-height: auto;
    }
}

@media (max-width: 900px) {
    .v2-payment-grid,
    .v2-crypto-grid,
    .v2-price-grid,
    .v2-hero-stats,
    .v2-security-grid {
        grid-template-columns: 1fr;
    }

    .v2-pay-card.wide {
        grid-column: span 1;
    }
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
        <section class="v2-column-card">
            <div class="v2-brand">
                <div class="v2-logo">A</div>
                <div>
                    <strong>AXION PRIME</strong>
                    <small>PERFORMANCE COMMAND OS · X10</small>
                </div>
            </div>

            <div class="v2-hero-copy">
                <div class="v2-hero-chip">PLATAFORMA TODO EN UNO</div>
                <h1>Opera con más claridad.<span>Decide con ventaja.</span></h1>
                <p>
                    La plataforma definitiva que combina IA, psicotrading,
                    track record y auditoría avanzada para llevar tu rendimiento
                    al siguiente nivel.
                </p>
            </div>

            <div class="v2-feature-stack">
                <div class="v2-feature-item" style="--rgb:39,216,255">
                    <div class="v2-feature-icon">🧠</div>
                    <div>
                        <strong>IA PARA TRADING</strong>
                        <span>Análisis inteligente de tu operativa y patrones reales.</span>
                    </div>
                </div>

                <div class="v2-feature-item" style="--rgb:139,77,255">
                    <div class="v2-feature-icon">◉</div>
                    <div>
                        <strong>PSICOTRADING</strong>
                        <span>Control emocional y mentalidad para traders consistentes.</span>
                    </div>
                </div>

                <div class="v2-feature-item" style="--rgb:39,216,255">
                    <div class="v2-feature-icon">↗</div>
                    <div>
                        <strong>TRACK RECORD</strong>
                        <span>Registra, analiza y mejora cada operación.</span>
                    </div>
                </div>

                <div class="v2-feature-item" style="--rgb:180,76,255">
                    <div class="v2-feature-icon">◇</div>
                    <div>
                        <strong>AUDITORÍA IA</strong>
                        <span>Revisión automática de tus trades con feedback personalizado.</span>
                    </div>
                </div>
            </div>

            <div class="v2-holo"></div>

            <div class="v2-hero-stats">
                <div class="v2-stat"><small>AI ENGINE</small><strong>24/7</strong></div>
                <div class="v2-stat"><small>DATOS</small><strong>100%</strong></div>
                <div class="v2-stat"><small>PRIVACIDAD</small><strong>PRO</strong></div>
            </div>

            <div class="v2-security-grid">
                <div class="v2-security-card">
                    <strong>🔒 PAGO 100% SEGURO</strong>
                    <span>Protección mediante proveedores externos.</span>
                </div>

                <div class="v2-security-card">
                    <strong>🎧 SOPORTE 24/7</strong>
                    <span>Atención preferencial cuando la necesites.</span>
                </div>
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
        <section class="v2-column-card">
            <div class="v2-center-shell">
                <div class="v2-form-head">
                    <div class="v2-form-logo">⚡</div>
                    <h2>Bienvenido de nuevo</h2>
                    <p>Inicia sesión para continuar.</p>
                </div>

                <div class="v2-form-body"></div>
            </div>
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

    st.html(
        """
        <div class="v2-center-benefits">
            <div class="v2-center-benefit">
                <strong>🛡️ ACCESO PROTEGIDO</strong>
                <span>Autenticación segura mediante Supabase.</span>
            </div>

            <div class="v2-center-benefit">
                <strong>⚡ EXPERIENCIA INMEDIATA</strong>
                <span>Tu journal queda disponible apenas inicias sesión.</span>
            </div>

            <div class="v2-center-benefit">
                <strong>☁️ DATOS EN LA NUBE</strong>
                <span>Operaciones, perfil y métricas sincronizadas.</span>
            </div>
        </div>
        """
    )

def _payment_showcase() -> None:
    st.html(
        """
        <section class="v2-column-card">
            <div class="v2-payment-panel">
                <div class="v2-payment-title">MÉTODOS DE PAGO DISPONIBLES</div>

                <div class="v2-payment-grid">
                    <div class="v2-pay-card" style="--rgb:39,216,255">
                        <div class="v2-pay-logo">VISA</div>
                        <strong>DÉBITO / CRÉDITO</strong>
                        <span>Tarjetas compatibles</span>
                    </div>

                    <div class="v2-pay-card" style="--rgb:255,142,48">
                        <div class="v2-pay-logo">●●</div>
                        <strong>MASTERCARD</strong>
                        <span>Débito / Crédito</span>
                    </div>

                    <div class="v2-pay-card wide" style="--rgb:63,188,255">
                        <div class="v2-pay-logo">MERCADO PAGO</div>
                        <strong>PAGO SEGURO</strong>
                        <span>Tarjeta y medios compatibles</span>
                    </div>

                    <div class="v2-pay-card wide" style="--rgb:255,196,0">
                        <div class="v2-pay-logo">BINANCE PAY</div>
                        <strong>PAGO CON CRIPTOMONEDAS</strong>
                        <span>Integración comercial próxima</span>
                    </div>
                </div>

                <div class="v2-crypto-grid">
                    <div class="v2-pay-card" style="--rgb:247,147,26">
                        <div class="v2-pay-logo">₿</div>
                        <strong>BITCOIN</strong>
                        <span>BEP20 · BNB Smart Chain</span>
                    </div>

                    <div class="v2-pay-card" style="--rgb:98,126,234">
                        <div class="v2-pay-logo">◆</div>
                        <strong>ETHEREUM</strong>
                        <span>BEP20 · BNB Smart Chain</span>
                    </div>

                    <div class="v2-pay-card" style="--rgb:38,161,123">
                        <div class="v2-pay-logo">₮</div>
                        <strong>USDT</strong>
                        <span>TRC20 · TRON</span>
                    </div>
                </div>

                <div class="v2-trial">
                    <strong>🎁 7 DÍAS GRATIS</strong>
                    <span>Disfruta todas las funciones PRO sin compromiso.</span>
                </div>

                <div class="v2-price-grid">
                    <div class="v2-price-card">
                        <small>PRO MENSUAL</small>
                        <strong>US$3</strong>
                        <span>por mes</span>
                    </div>

                    <div class="v2-price-card annual">
                        <small>PRO ANUAL</small>
                        <strong>US$20</strong>
                        <span>por año · ahorra US$16</span>
                    </div>
                </div>

                <div class="v2-payment-trust">
                    <div class="v2-trust-card">
                        <strong>✓ SIN CARGOS OCULTOS</strong>
                        <span>Precios claros y visibles.</span>
                    </div>

                    <div class="v2-trust-card">
                        <strong>✓ CANCELA CUANDO QUIERAS</strong>
                        <span>Control total de tu suscripción.</span>
                    </div>

                    <div class="v2-trust-card">
                        <strong>✓ PAGOS INTERNACIONALES</strong>
                        <span>Tarjeta, Mercado Pago, Binance Pay y cripto.</span>
                    </div>
                </div>

                <div class="v2-footer-bar">
                    AXION PRIME PRO · Seguridad, flexibilidad y acceso global.
                </div>
            </div>
        </section>
        """
    )

def render_v2_auth() -> None:
    apply_v2_theme()
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    st.html('<div class="v2-login-root"></div>')

    left, center, right = st.columns(
        [1.12, 1.00, 1.08],
        gap="medium",
    )

    with left:
        _hero()

    with center:
        _form()

    with right:
        _payment_showcase()
