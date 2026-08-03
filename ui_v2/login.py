from __future__ import annotations

from typing import Any

import streamlit as st

from core.api import reset_password, sign_in, sign_up
from core.config import APP_URL
from ui_v2.theme import apply_v2_theme


LOGIN_CSS = """
<style>
[data-testid="stSidebar"]{display:none!important}
html,body,[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 15% 15%,rgba(25,228,255,.07),transparent 22%),radial-gradient(circle at 82% 18%,rgba(139,77,255,.08),transparent 26%),linear-gradient(180deg,#020713 0%,#040313 56%,#020711 100%)!important}
.block-container{max-width:1580px;padding-top:1rem;padding-bottom:1.2rem}
.v2-login-hero{min-height:1060px;display:flex;flex-direction:column;justify-content:space-between;padding:42px;overflow:hidden;position:relative;background:radial-gradient(circle at 18% 8%,rgba(25,228,255,.12),transparent 24%),radial-gradient(circle at 12% 78%,rgba(62,125,255,.13),transparent 28%),radial-gradient(circle at 38% 88%,rgba(139,77,255,.18),transparent 31%),linear-gradient(145deg,rgba(5,13,31,.99),rgba(7,5,27,.99));border:1px solid rgba(68,107,181,.38);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.46)}
.v2-login-hero:before{content:"";position:absolute;inset:0;background:linear-gradient(rgba(78,108,174,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(78,108,174,.035) 1px,transparent 1px);background-size:48px 48px}
.v2-login-hero:after{content:"";position:absolute;left:-12%;right:-12%;bottom:-12%;height:42%;border-radius:50% 50% 0 0;background:radial-gradient(ellipse at center,rgba(25,228,255,.18),transparent 60%),linear-gradient(rgba(25,228,255,.10) 1px,transparent 1px),linear-gradient(90deg,rgba(139,77,255,.10) 1px,transparent 1px);background-size:auto,34px 34px,34px 34px;transform:perspective(500px) rotateX(63deg);transform-origin:center bottom;opacity:.78}
.v2-login-brand,.v2-login-copy,.v2-login-stats,.v2-login-security{position:relative;z-index:2}
.v2-login-brand{display:flex;align-items:center;gap:13px}.v2-login-logo{width:54px;height:54px;display:grid;place-items:center;color:#fff;font-size:20px;font-weight:950;background:linear-gradient(145deg,#19e4ff,#3c7dff 55%,#8b4dff);border-radius:16px;box-shadow:0 0 30px rgba(25,228,255,.30)}
.v2-login-brand strong{display:block;color:#f7f9ff;font-size:22px;font-weight:950}.v2-login-brand small{display:block;margin-top:4px;color:#64718d;font-size:7px;letter-spacing:1.8px;font-weight:900}
.v2-login-copy h1{margin:20px 0 0;color:#f7f9ff;font-size:clamp(48px,4.7vw,76px);line-height:.96;letter-spacing:-3.7px;font-weight:950;text-transform:uppercase}
.v2-login-copy h1 span{display:block;color:transparent;background:linear-gradient(90deg,#19e4ff,#69a3ff,#8b4dff,#ff4bc8);background-clip:text;-webkit-background-clip:text}
.v2-login-copy p{max-width:650px;margin-top:22px;color:#9aa7c4;font-size:15px;line-height:1.7}
.v2-login-features{display:grid;grid-template-columns:1fr;gap:10px;margin-top:28px}.v2-login-feature{display:grid;grid-template-columns:52px 1fr;gap:13px;align-items:center;padding:14px;color:#e6ecfb;background:radial-gradient(circle at 0 50%,rgba(var(--feature-rgb),.11),transparent 24%),rgba(4,10,25,.76);border:1px solid rgba(var(--feature-rgb),.24);border-radius:14px}
.v2-feature-icon{width:46px;height:46px;display:grid;place-items:center;color:rgb(var(--feature-rgb));font-size:22px;border-radius:50%;background:rgba(var(--feature-rgb),.10);border:1px solid rgba(var(--feature-rgb),.30)}
.v2-login-feature strong{display:block;color:#f4f7ff;font-size:11px;font-weight:950}.v2-login-feature span{display:block;margin-top:3px;color:#8392b0;font-size:8px;line-height:1.45}
.v2-login-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:18px}.v2-login-stat{padding:14px;text-align:center;background:rgba(4,10,25,.78);border:1px solid rgba(72,101,165,.24);border-radius:13px}
.v2-login-stat small{display:block;color:#64718d;font-size:7px;font-weight:900;letter-spacing:1.2px}.v2-login-stat strong{display:block;margin-top:7px;color:#f7f9ff;font-size:19px}
.v2-login-security{width:min(320px,100%);padding:15px;margin-bottom:20px;background:radial-gradient(circle at 0 0,rgba(139,77,255,.14),transparent 38%),rgba(4,10,25,.86);border:1px solid rgba(139,77,255,.30);border-radius:14px}
.v2-login-security strong{display:block;color:#f5f7ff;font-size:10px}.v2-login-security span{display:block;margin-top:5px;color:#8f9db9;font-size:8px;line-height:1.45}
.v2-auth-panel{min-height:1060px;padding:24px;background:radial-gradient(circle at 100% 0%,rgba(139,77,255,.14),transparent 24%),linear-gradient(145deg,rgba(5,12,29,.99),rgba(5,7,22,.99));border:1px solid rgba(69,108,190,.40);border-radius:26px;box-shadow:0 30px 90px rgba(0,0,0,.44)}
.v2-form-card{padding:28px 28px 24px;background:radial-gradient(circle at 100% 0%,rgba(139,77,255,.16),transparent 30%),linear-gradient(145deg,rgba(8,16,35,.98),rgba(6,8,25,.98));border:1px solid rgba(74,104,171,.34);border-radius:21px}
.v2-form-logo{width:48px;height:48px;display:grid;place-items:center;margin:auto;color:#fff;font-size:19px;background:linear-gradient(145deg,#19e4ff,#3c7dff,#8b4dff);border-radius:14px}.v2-form-card h2{margin:20px 0 7px;color:#f7f9ff;font-size:35px;line-height:1.04;letter-spacing:-1.8px;font-weight:950;text-align:center}.v2-form-card p{color:#91a0bf;font-size:11px;margin-bottom:18px;text-align:center}
[data-baseweb="tab-list"]{gap:18px;border-bottom:1px solid rgba(84,107,166,.23)}[data-baseweb="tab"]{min-height:42px;padding-left:0!important;padding-right:0!important;background:transparent!important;color:#8390ad!important}[aria-selected="true"][data-baseweb="tab"]{color:#19e4ff!important;font-weight:900}
.v2-payment-panel{margin-top:16px;padding:18px;background:radial-gradient(circle at 100% 0%,rgba(25,228,255,.08),transparent 30%),linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));border:1px solid rgba(67,116,205,.38);border-radius:18px}
.v2-payment-title{display:flex;align-items:center;gap:10px;margin-bottom:14px;color:#2bdcff;font-size:12px;font-weight:950}.v2-payment-title:before,.v2-payment-title:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,transparent,#2bdcff,#8b4dff,transparent)}
.v2-payment-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.v2-payment-card{min-width:0;min-height:86px;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:12px;text-align:center;background:radial-gradient(circle at 100% 0%,rgba(var(--pay-rgb),.13),transparent 35%),rgba(5,11,28,.92);border:1px solid rgba(var(--pay-rgb),.34);border-radius:13px}
.v2-payment-card.wide{grid-column:span 2}.v2-payment-logo{color:rgb(var(--pay-rgb));font-size:22px;font-weight:950}.v2-payment-card strong{margin-top:5px;color:#f5f7ff;font-size:10px}.v2-payment-card span{margin-top:3px;color:#8291ad;font-size:7px}
.v2-crypto-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px;margin-top:10px}.v2-trial-panel{margin-top:14px;padding:15px;text-align:center;border:1px solid rgba(139,77,255,.30);border-radius:14px;background:radial-gradient(circle at 50% 0%,rgba(139,77,255,.13),transparent 45%),rgba(5,11,28,.90)}
.v2-trial-panel strong{display:block;color:#c7ff57;font-size:18px;font-weight:950}.v2-trial-panel span{display:block;margin-top:5px;color:#9aa7c1;font-size:8px}
.v2-price-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:12px}.v2-price-card{padding:14px;text-align:center;background:rgba(5,11,28,.92);border:1px solid rgba(25,228,255,.27);border-radius:13px}.v2-price-card.annual{border-color:rgba(214,72,255,.45)}
.v2-price-card small{color:#2bdcff;font-size:8px;font-weight:950}.v2-price-card strong{display:block;margin-top:7px;color:#f5f7ff;font-size:25px}.v2-price-card span{color:#7f8fac;font-size:7px}.v2-trust-row{display:flex;justify-content:center;gap:13px;flex-wrap:wrap;margin-top:13px;color:#8b99b4;font-size:7px}.v2-login-footer{margin-top:12px;padding:11px 14px;color:#7d8ca8;font-size:8px;text-align:center;border:1px solid rgba(72,101,165,.18);border-radius:12px;background:rgba(4,10,25,.70)}
@media(max-width:980px){.v2-login-hero,.v2-auth-panel{min-height:auto}.v2-login-features,.v2-login-stats,.v2-payment-grid,.v2-crypto-grid,.v2-price-grid{grid-template-columns:1fr}.v2-payment-card.wide{grid-column:span 1}}
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
            <div>
                <div class="v2-login-brand">
                    <div class="v2-login-logo">A</div>
                    <div>
                        <strong>AXION PRIME</strong>
                        <small>PERFORMANCE COMMAND OS · X10</small>
                    </div>
                </div>

                <div class="v2-login-copy">
                    <h1>Opera con más claridad.<span>Decide con ventaja.</span></h1>
                    <p>
                        La plataforma todo en uno que combina IA, psicotrading,
                        track record y auditoría avanzada para llevar tu rendimiento
                        al siguiente nivel.
                    </p>

                    <div class="v2-login-features">
                        <div class="v2-login-feature" style="--feature-rgb:39,216,255">
                            <div class="v2-feature-icon">🧠</div>
                            <div><strong>IA PARA TRADING</strong><span>Análisis inteligente de tu operativa y patrones reales.</span></div>
                        </div>
                        <div class="v2-login-feature" style="--feature-rgb:139,77,255">
                            <div class="v2-feature-icon">◉</div>
                            <div><strong>PSICOTRADING</strong><span>Control emocional y mentalidad para traders consistentes.</span></div>
                        </div>
                        <div class="v2-login-feature" style="--feature-rgb:39,216,255">
                            <div class="v2-feature-icon">↗</div>
                            <div><strong>TRACK RECORD</strong><span>Registra, analiza y mejora cada una de tus operaciones.</span></div>
                        </div>
                        <div class="v2-login-feature" style="--feature-rgb:180,76,255">
                            <div class="v2-feature-icon">◇</div>
                            <div><strong>AUDITORÍA IA</strong><span>Revisión automática de tus trades con feedback personalizado.</span></div>
                        </div>
                    </div>
                </div>

                <div class="v2-login-stats">
                    <div class="v2-login-stat"><small>AI ENGINE</small><strong>24/7</strong></div>
                    <div class="v2-login-stat"><small>DATOS</small><strong>100%</strong></div>
                    <div class="v2-login-stat"><small>PRIVACIDAD</small><strong>PRO</strong></div>
                </div>
            </div>

            <div class="v2-login-security">
                <strong>🔒 Pago y acceso protegidos</strong>
                <span>Tus credenciales y pagos serán procesados mediante proveedores externos seguros.</span>
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


def _payment_showcase() -> None:
    st.html(
        """
        <section class="v2-payment-panel">
            <div class="v2-payment-title">MÉTODOS DE PAGO DISPONIBLES</div>

            <div class="v2-payment-grid">
                <div class="v2-payment-card" style="--pay-rgb:39,216,255">
                    <div class="v2-payment-logo">VISA</div><strong>DÉBITO / CRÉDITO</strong><span>Tarjetas compatibles</span>
                </div>
                <div class="v2-payment-card" style="--pay-rgb:255,142,48">
                    <div class="v2-payment-logo">●●</div><strong>MASTERCARD</strong><span>Débito / Crédito</span>
                </div>
                <div class="v2-payment-card wide" style="--pay-rgb:63,188,255">
                    <div class="v2-payment-logo">MERCADO PAGO</div><strong>PAGO SEGURO</strong><span>Tarjeta y medios compatibles</span>
                </div>
                <div class="v2-payment-card wide" style="--pay-rgb:255,196,0">
                    <div class="v2-payment-logo">BINANCE PAY</div><strong>PAGO CON CRIPTOMONEDAS</strong><span>Integración comercial próxima</span>
                </div>
            </div>

            <div class="v2-crypto-grid">
                <div class="v2-payment-card" style="--pay-rgb:247,147,26">
                    <div class="v2-payment-logo">₿</div><strong>BITCOIN</strong><span>BEP20 · BNB Smart Chain</span>
                </div>
                <div class="v2-payment-card" style="--pay-rgb:98,126,234">
                    <div class="v2-payment-logo">◆</div><strong>ETHEREUM</strong><span>BEP20 · BNB Smart Chain</span>
                </div>
                <div class="v2-payment-card" style="--pay-rgb:38,161,123">
                    <div class="v2-payment-logo">₮</div><strong>USDT</strong><span>TRC20 · TRON</span>
                </div>
            </div>

            <div class="v2-trial-panel">
                <strong>🎁 7 DÍAS GRATIS</strong>
                <span>Disfruta todas las funciones PRO sin compromiso.</span>
            </div>

            <div class="v2-price-grid">
                <div class="v2-price-card"><small>PRO MENSUAL</small><strong>US$3</strong><span>por mes</span></div>
                <div class="v2-price-card annual"><small>PRO ANUAL</small><strong>US$20</strong><span>por año · ahorra US$16</span></div>
            </div>

            <div class="v2-trust-row">
                <span>✓ Sin cargos ocultos</span><span>✓ Cancela cuando quieras</span><span>✓ Soporte futuro</span>
            </div>
        </section>

        <div class="v2-login-footer">
            Aceptamos pagos internacionales mediante tarjeta, Mercado Pago,
            Binance Pay y criptomonedas.
        </div>
        """
    )

def render_v2_auth() -> None:
    apply_v2_theme()
    st.markdown(LOGIN_CSS, unsafe_allow_html=True)

    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        _hero()

    with right:
        st.html('<section class="v2-auth-panel">')
        _form()
        _payment_showcase()
        st.html('</section>')
