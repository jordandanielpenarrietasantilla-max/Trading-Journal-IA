import streamlit as st
import datetime
import requests
import json
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import calendar
from PIL import Image
import io
from supabase import create_client, Client


# ============================================================
# 1. CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="AI Trading Journal & Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# 2. CONFIGURACIÓN / SECRETOS
# ============================================================

LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"

BINANCE_PAY_ID = "JORDAN_SANTI9"

LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"

SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    "https://lyzvcbjpoydeckxtbcq.supabase.co"
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    ""
)

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)

# Puedes colocar aquí un Payment Link de Stripe.
# Ejemplo en secrets.toml:
#
# STRIPE_MONTHLY_URL = "https://buy.stripe.com/..."
# STRIPE_ANNUAL_URL = "https://buy.stripe.com/..."
#
STRIPE_MONTHLY_URL = st.secrets.get("STRIPE_MONTHLY_URL", "")
STRIPE_ANNUAL_URL = st.secrets.get("STRIPE_ANNUAL_URL", "")


# ============================================================
# 3. SUPABASE
# ============================================================

@st.cache_resource
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Faltan SUPABASE_URL y/o SUPABASE_KEY en Streamlit Secrets."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ============================================================
# 4. ESTADO DE SESIÓN
# ============================================================

DEFAULT_RULES = (
    "• Acepta la pérdida antes de entrar.\n"
    "• Corta pérdidas rápido.\n"
    "• Deja correr los ganadores.\n"
    "• Máximo 2 operaciones perdedoras por día."
)


def inicializar_estado():

    defaults = {
        "authenticated": False,
        "user": None,
        "chat_history": [],
        "nombre_trader": "Trader Pro",
        "capital_actual": 10000.0,
        "capital_meta": 15000.0,
        "reglas_disciplina": DEFAULT_RULES,
        "auto_entry": 0.0,
        "auto_sl": 0.0,
        "auto_tp": 0.0,
        "auto_rr": 0.0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


inicializar_estado()


# ============================================================
# 5. ACTIVOS
# ============================================================

LISTA_ACTIVOS = [
    "🥇 XAU/USD (Oro)",
    "🥈 XAG/USD (Plata)",
    "🛢️ USOIL (Petróleo WTI)",
    "🛢️ UKOIL (Petróleo Brent)",
    "🌾 NGAS (Gas Natural)",
    "🪙 BTC/USD (Bitcoin)",
    "🪙 ETH/USD (Ethereum)",
    "🪙 SOL/USD (Solana)",
    "🪙 XRP/USD (Ripple)",
    "🪙 BNB/USD (Binance Coin)",
    "🪙 ADA/USD (Cardano)",
    "🪙 DOGE/USD (Dogecoin)",
    "📊 US100 (Nasdaq 100)",
    "📊 US30 (Dow Jones)",
    "📊 US500 (S&P 500)",
    "📊 GER40 (Dax Alemán)",
    "📊 UK100 (FTSE 100)",
    "📊 JP225 (Nikkei 225)",
    "💱 EUR/USD",
    "💱 GBP/USD",
    "💱 USD/JPY",
    "💱 AUD/USD",
    "💱 USD/CAD",
    "💱 USD/CHF",
    "💱 NZD/USD",
    "💱 EUR/GBP",
    "💱 EUR/JPY",
    "💱 GBP/JPY",
    "💱 AUD/JPY",
    "📈 NVDA (Nvidia)",
    "📈 TSLA (Tesla)",
    "📈 AAPL (Apple)",
    "📈 AMZN (Amazon)",
    "📈 MSFT (Microsoft)",
    "📈 GOOGL (Google)",
    "📈 META (Meta / Facebook)",
    "📈 AMD (Advanced Micro Devices)",
    "📈 NFLX (Netflix)",
    "📈 COIN (Coinbase)"
]


# ============================================================
# 6. UTILIDADES
# ============================================================

def procesar_imagen_b64(uploaded_file, max_size=(1000, 800)):

    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file).convert("RGB")
        image.thumbnail(max_size)

        buffer = io.BytesIO()
        image.save(
            buffer,
            format="JPEG",
            quality=78,
            optimize=True
        )

        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return f"data:image/jpeg;base64,{encoded}"

    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return ""


def safe_float(value, default=0.0):

    try:
        if value is None:
            return default

        if isinstance(value, str):
            value = value.replace(",", ".")

        return float(value)

    except Exception:
        return default


# ============================================================
# 7. BASE DE DATOS - TRADES
# ============================================================

def cargar_trades_usuario(user_id):

    try:
        client = get_supabase_client()

        response = (
            client
            .table("trades")
            .select("*")
            .eq("user_id", user_id)
            .order("fecha", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        st.error(
            f"⚠️ Error cargando operaciones: {e}"
        )
        return []


def guardar_trade_supabase(user_id, trade_data):

    try:

        client = get_supabase_client()

        data = dict(trade_data)
        data["user_id"] = user_id

        client.table("trades").insert(data).execute()

        return True

    except Exception as e:

        st.error(
            f"❌ Error guardando la operación: {e}"
        )

        return False


def eliminar_trade_supabase(trade_id):

    try:

        client = get_supabase_client()

        client.table("trades").delete().eq(
            "id",
            trade_id
        ).execute()

        return True

    except Exception as e:

        st.error(
            f"❌ Error eliminando la operación: {e}"
        )

        return False


# ============================================================
# 8. IA / VISION
# ============================================================

def analizar_captura_tradingview(image_bytes):

    if not OPENROUTER_API_KEY:
        return None

    try:

        b64_img = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = """
Analiza este gráfico de TradingView.

Busca la herramienta de posición / Risk Reward y extrae:

- precio de entrada
- stop loss
- take profit

Devuelve ÚNICAMENTE JSON válido con estas claves exactas:

{
  "entry": 0.0,
  "sl": 0.0,
  "tp": 0.0
}

Si no puedes identificar un valor, devuelve 0.0.
No escribas ninguna explicación.
"""

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:image/png;base64,"
                                    + b64_img
                                )
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        content = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        content = content.replace(
            "```json",
            ""
        ).replace(
            "```",
            ""
        ).strip()

        data = json.loads(content)

        return {
            "entry": safe_float(data.get("entry")),
            "sl": safe_float(data.get("sl")),
            "tp": safe_float(data.get("tp"))
        }

    except Exception:
        return None


def analizar_grafico_ia(image_bytes, pregunta="Analiza este gráfico"):

    if not OPENROUTER_API_KEY:
        return (
            "La IA no está configurada todavía. "
            "Agrega OPENROUTER_API_KEY en Streamlit Secrets."
        )

    try:

        b64_img = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""
Eres un auditor de trading.

Analiza la captura proporcionada.

Pregunta:
{pregunta}

Evalúa de forma educativa:

1. Estructura de mercado.
2. Tendencia.
3. Zonas relevantes.
4. Posible entrada.
5. Stop Loss.
6. Take Profit.
7. Risk/Reward.
8. Confluencias.
9. Riesgos de la operación.
10. Disciplina y posibles errores psicológicos.

No garantices resultados ni presentes el análisis como una certeza.
"""

        payload = {
            "model": "openai/gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    "data:image/png;base64,"
                                    + b64_img
                                )
                            }
                        }
                    ]
                }
            ]
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )

        response.raise_for_status()

        result = response.json()

        return (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "No se obtuvo respuesta de la IA.")
        )

    except Exception as e:

        return f"Error comunicando con la IA: {e}"


# ============================================================
# 9. CSS
# ============================================================

def aplicar_estilos():

    css = """
    <style>

    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
    }

    p, label, h1, h2, h3, h4, h5, h6, span, div,
    .stMarkdown {
        color: #f0f3fa !important;
    }

    h1, h2 {
        background: linear-gradient(
            90deg,
            #00f2fe 0%,
            #4facfe 100%
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        font-weight: 800 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0,210,255,0.25) !important;
    }

    section[data-testid="stSidebar"] > div {
        background-color: #0f141e !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #121721 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0,242,254,0.5) !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="select"] input {
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {
        background-color: #121721 !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }

    div[role="option"],
    li[role="option"],
    li[data-baseweb="option"] {
        background-color: #121721 !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background-color: #00f2fe !important;
        color: #000000 !important;
        font-weight: bold !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
        border: 1px solid rgba(0,210,255,0.4) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0,210,255,0.5) !important;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
    }

    .stButton > button {
        background: linear-gradient(
            135deg,
            #00d2ff 0%,
            #2962ff 100%
        ) !important;

        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;

        box-shadow:
            0px 4px 15px
            rgba(0,210,255,0.3) !important;
    }

    .market-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    .open {
        background-color: rgba(76,175,80,0.2);
        color: #4caf50 !important;
        border: 1px solid #4caf50;
    }

    .closed {
        background-color: rgba(244,67,54,0.2);
        color: #f44336 !important;
        border: 1px solid #f44336;
    }

    .paywall-card {
        background-color: #161b22;
        border: 1px solid #f0b90b;
        border-radius: 12px;
        padding: 24px;
        text-align: center;

        box-shadow:
            0px 0px 20px
            rgba(240,185,11,0.2);
    }

    .profile-card {
        background-color: #121721;
        border: 1px solid rgba(0,242,254,0.2);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }

    .sidebar-section {
        background-color: #121721;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }

    </style>
    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


# ============================================================
# 10. SUSCRIPCIÓN
# ============================================================

def evaluar_suscripcion(user):

    if not user:
        return False, "Sin sesión", 0

    user_email = getattr(
        user,
        "email",
        ""
    ) or ""

    # ADMIN
    if user_email.lower() == "jordandanielpenarrietasantilla@gmail.com":
        return True, "Creador / Admin 👑", 99999

    metadata = getattr(
        user,
        "user_metadata",
        {}
    ) or {}

    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999

    # Suscripción manual
    if metadata.get("subscription_active", False):
        return True, "Acceso PRO 💎", 999

    created_at_str = getattr(
        user,
        "created_at",
        None
    )

    try:

        if created_at_str:
            fecha_registro = datetime.datetime.strptime(
                str(created_at_str)[:10],
                "%Y-%m-%d"
            ).date()
        else:
            fecha_registro = datetime.date.today()

    except Exception:

        fecha_registro = datetime.date.today()

    dias_usados = (
        datetime.date.today()
        - fecha_registro
    ).days

    dias_restantes = max(
        0,
        3 - dias_usados
    )

    if dias_usados <= 3:
        return (
            True,
            f"Prueba Gratis ({dias_restantes} días rest.)",
            dias_restantes
        )

    return (
        False,
        "Prueba Expirada 🛑",
        0
    )


# ============================================================
# 11. PAGOS
# ============================================================

def render_stripe_button(url, texto):

    if url:

        st.markdown(
            f"""
            <a href="{url}" target="_blank"
            style="text-decoration:none;">
                <div style="
                    background:linear-gradient(
                        135deg,
                        #635bff,
                        #4b45c6
                    );
                    color:white;
                    padding:14px;
                    border-radius:8px;
                    text-align:center;
                    font-weight:bold;
                    margin-top:10px;
                    cursor:pointer;
                ">
                    💳 {texto}
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )

    else:

        st.warning(
            "El pago con tarjeta todavía no está configurado. "
            "Agrega STRIPE_MONTHLY_URL o STRIPE_ANNUAL_URL "
            "en Streamlit Secrets."
        )


def render_paywall():

    st.markdown(
        "## 🔒 Tu período de prueba ha expirado"
    )

    st.markdown(
        """
        Continúa utilizando tu diario de trading,
        Track Record, análisis y herramientas de IA.
        """
    )

    col1, col2 = st.columns(2)

    # ---------------- MONTHLY ----------------

    with col1:

        st.markdown(
            """
            <div class="paywall-card">

            <h3 style="color:#f0b90b;">
            🟡 Suscripción Mensual
            </h3>

            <h2 style="color:#ffffff;">
            $5.00 USD
            </h2>

            <p style="color:#00f2fe;">
            Luego $2.50 USD / mes
            </p>

            <hr>

            <p>✔️ Acceso PRO</p>
            <p>✔️ Track Record ilimitado</p>
            <p>✔️ IA y auditoría</p>
            <p>✔️ Diario psicológico</p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 💳 Tarjeta")

        render_stripe_button(
            STRIPE_MONTHLY_URL,
            "Pagar con Débito / Crédito"
        )

        st.markdown("### 🟡 Binance Pay")

        st.markdown(
            f"""
            <a href="{LINK_BINANCE_INSCRIPCION}"
            target="_blank"
            style="text-decoration:none;">

            <div style="
                background:linear-gradient(
                    135deg,
                    #f0b90b,
                    #f39c12
                );
                color:black;
                padding:14px;
                border-radius:8px;
                text-align:center;
                font-weight:bold;
            ">

            🟡 Pagar $5 USD con Binance Pay

            </div>

            </a>
            """,
            unsafe_allow_html=True
        )

    # ---------------- ANNUAL ----------------

    with col2:

        st.markdown(
            """
            <div class="paywall-card">

            <h3 style="color:#00f2fe;">
            🚀 Acceso Anual
            </h3>

            <h2 style="color:#ffffff;">
            $20.00 USD
            </h2>

            <p style="color:#00f2fe;">
            Ahorra frente al mensual
            </p>

            <hr>

            <p>🌟 1 año completo</p>
            <p>🔒 Pago único</p>
            <p>🎁 Actualizaciones futuras</p>
            <p>🧠 IA y auditoría</p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 💳 Tarjeta")

        render_stripe_button(
            STRIPE_ANNUAL_URL,
            "Pagar con Débito / Crédito"
        )

        st.markdown("### 💎 Binance Pay")

        st.markdown(
            f"""
            <a href="{LINK_BINANCE_ANUAL}"
            target="_blank"
            style="text-decoration:none;">

            <div style="
                background:linear-gradient(
                    135deg,
                    #00f2fe,
                    #4facfe
                );
                color:black;
                padding:14px;
                border-radius:8px;
                text-align:center;
                font-weight:bold;
            ">

            💎 Pagar $20 USD con Binance Pay

            </div>

            </a>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "### 📲 Pago directo / Renovaciones"
        )

        st.code(
            f"Binance Pay ID: {BINANCE_PAY_ID}",
            language="text"
        )

        st.markdown(
            f"""
            <a href="{LINK_BINANCE_RECURRENTE}"
            target="_blank">

            🔄 Renovación mensual $2.50 USDT

            </a>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            "### ✈️ Confirmar pago"
        )

        st.markdown(
            f"""
            <a href="{LINK_TELEGRAM_SOPORTE}"
            target="_blank"
            style="text-decoration:none;">

            <div style="
                background:linear-gradient(
                    135deg,
                    #0088cc,
                    #005580
                );
                color:white;
                padding:12px;
                border-radius:8px;
                text-align:center;
                font-weight:bold;
            ">

            💬 Enviar comprobante / soporte

            </div>

            </a>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 12. AUTENTICACIÓN
# ============================================================

def render_auth():

    col1, col2 = st.columns(
        [1.2, 1]
    )

    with col1:

        st.markdown(
            "# ⚡ AI Trading Journal & Auditor"
        )

        st.markdown(
            """
            Tu centro de control para:

            • Registrar operaciones.
            • Analizar disciplina.
            • Guardar capturas.
            • Auditar setups.
            • Analizar estadísticas.
            • Mejorar tu psicología de trading.
            """
        )

        st.markdown("---")

        st.info(
            "🎁 Crea tu cuenta y disfruta de tu período de prueba."
        )

    with col2:

        tab_login, tab_register, tab_reset = st.tabs(
            [
                "🔑 Iniciar Sesión",
                "📝 Registrarse",
                "🔐 Recuperar Clave"
            ]
        )

        # LOGIN

        with tab_login:

            st.markdown(
                "### Ingresa a tu Cuenta"
            )

            login_email = st.text_input(
                "Correo Electrónico",
                key="login_email"
            )

            login_pass = st.text_input(
                "Contraseña",
                type="password",
                key="login_pass"
            )

            if st.button(
                "Ingresar",
                key="btn_login"
            ):

                if not login_email or not login_pass:

                    st.warning(
                        "Completa correo y contraseña."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        res = (
                            client
                            .auth
                            .sign_in_with_password(
                                {
                                    "email": login_email,
                                    "password": login_pass
                                }
                            )
                        )

                        st.session_state.authenticated = True
                        st.session_state.user = res.user

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Error al iniciar sesión: {e}"
                        )

        # REGISTER

        with tab_register:

            st.markdown(
                "### Crea tu Cuenta"
            )

            reg_email = st.text_input(
                "Correo Electrónico",
                key="reg_email"
            )

            reg_pass = st.text_input(
                "Crea tu Contraseña",
                type="password",
                key="reg_pass"
            )

            if st.button(
                "Crear Cuenta y Probar",
                key="btn_reg"
            ):

                if not reg_email or not reg_pass:

                    st.warning(
                        "Completa todos los campos."
                    )

                elif len(reg_pass) < 6:

                    st.warning(
                        "La contraseña debe tener al menos 6 caracteres."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        client.auth.sign_up(
                            {
                                "email": reg_email,
                                "password": reg_pass
                            }
                        )

                        st.success(
                            "¡Registro exitoso! "
                            "Ahora inicia sesión."
                        )

                    except Exception as e:

                        st.error(
                            f"Error registrando usuario: {e}"
                        )

        # RESET

        with tab_reset:

            st.markdown(
                "### 🔐 Recuperar Contraseña"
            )

            reset_email = st.text_input(
                "Correo registrado",
                key="reset_email"
            )

            if st.button(
                "Enviar Enlace",
                key="btn_reset"
            ):

                if not reset_email:

                    st.warning(
                        "Ingresa tu correo."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        app_url = (
                            "https://trading-journal-ia-"
                            "7lvamxtjspcbclwcda2zxg."
                            "streamlit.app/"
                        )

                        client.auth.reset_password_for_email(
                            reset_email,
                            {
                                "redirectTo": app_url
                            }
                        )

                        st.success(
                            "📩 Revisa tu correo y Spam."
                        )

                    except Exception as e:

                        st.error(
                            f"Error enviando recuperación: {e}"
                        )


# ============================================================
# 13. SIDEBAR COMPLETO
# ============================================================

def render_sidebar(estado_sub):

    with st.sidebar:

        # ====================================================
        # PERFIL
        # ====================================================

        st.markdown(
            "## 👤 Perfil Trader"
        )

        user = st.session_state.user

        user_email = (
            getattr(user, "email", None)
            if user
            else "trader@ejemplo.com"
        )

        metadata = (
            getattr(
                user,
                "user_metadata",
                {}
            )
            if user
            else {}
        ) or {}

        nombre_actual = metadata.get(
            "username",
            st.session_state.get(
                "nombre_trader",
                "Trader Pro"
            )
        )

        foto_b64 = metadata.get(
            "avatar_b64",
            ""
        )

        # FOTO + NOMBRE

        col_img, col_txt = st.columns(
            [1, 1.7]
        )

        with col_img:

            if foto_b64:

                st.markdown(
                    f"""
                    <img
                        src="data:image/png;base64,{foto_b64}"
                        style="
                            width:65px;
                            height:65px;
                            border-radius:50%;
                            object-fit:cover;
                            border:2px solid #00f2fe;
                        "
                    >
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    """
                    <div style="
                        width:65px;
                        height:65px;
                        border-radius:50%;
                        border:2px solid #00f2fe;
                        background:#161b22;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:30px;
                    ">
                    👤
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with col_txt:

            st.markdown(
                f"**{nombre_actual}**"
            )

            st.caption(
                user_email
            )

        if (
            "PRO" in estado_sub
            or "Admin" in estado_sub
        ):

            st.success(
                f"💎 {estado_sub}"
            )

        elif "Prueba" in estado_sub:

            st.info(
                f"🎁 {estado_sub}"
            )

        else:

            st.warning(
                estado_sub
            )

        # ====================================================
        # MODIFICAR PERFIL
        # ====================================================

        with st.expander(
            "⚙️ Modificar Perfil"
        ):

            input_nombre = st.text_input(
                "Nombre de Usuario",
                value=nombre_actual,
                key="profile_name"
            )

            foto_subida = st.file_uploader(
                "Nueva foto",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ],
                key="profile_photo"
            )

            if st.button(
                "💾 Guardar Cambios",
                key="save_profile"
            ):

                nueva_foto_b64 = foto_b64

                if foto_subida:

                    nueva_foto_b64 = base64.b64encode(
                        foto_subida.getvalue()
                    ).decode("utf-8")

                try:

                    client = get_supabase_client()

                    res = client.auth.update_user(
                        {
                            "data": {
                                "username": input_nombre,
                                "avatar_b64": nueva_foto_b64
                            }
                        }
                    )

                    st.session_state.user = res.user
                    st.session_state.nombre_trader = input_nombre

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error actualizando perfil: {e}"
                    )

        st.markdown("---")

        # ====================================================
        # SESIÓN DE OPERATIVA
        # ====================================================

        st.markdown(
            "## 🎯 Sesión de Operativa"
        )

        hora_utc = datetime.datetime.utcnow().hour

        # Londres
        londres_abierto = (
            7 <= hora_utc <= 15
        )

        # Nueva York
        ny_abierto = (
            12 <= hora_utc <= 20
        )

        londres_status = (
            '<span class="market-badge open">ABIERTO</span>'
            if londres_abierto
            else
            '<span class="market-badge closed">CERRADO</span>'
        )

        ny_status = (
            '<span class="market-badge open">ABIERTO</span>'
            if ny_abierto
            else
            '<span class="market-badge closed">CERRADO</span>'
        )

        st.markdown(
            f"**🇬🇧 Londres:** {londres_status}",
            unsafe_allow_html=True
        )

        st.markdown(
            f"**🇺🇸 Nueva York:** {ny_status}",
            unsafe_allow_html=True
        )

        # ====================================================
        # RELOJ
        # ====================================================

        st.components.v1.html(
            """
            <div id="clock" style="
                font-family:monospace;
                font-size:18px;
                font-weight:bold;
                color:#00f2fe;
                background:#161b22;
                border:1px solid rgba(0,210,255,.4);
                border-radius:8px;
                padding:8px;
                text-align:center;
            ">
            00:00:00
            </div>

            <script>

            function updateClock(){

                const now = new Date();

                const timeString =
                    now.toLocaleTimeString();

                document.getElementById(
                    "clock"
                ).innerHTML =
                    timeString + " (Local)";
            }

            updateClock();

            setInterval(
                updateClock,
                1000
            );

            </script>
            """,
            height=50
        )

        st.markdown("---")

        # ====================================================
        # META DE CUENTA
        # ====================================================

        st.markdown(
            "## 💰 Meta de Cuenta"
        )

        cap_act = safe_float(
            st.session_state.capital_actual,
            10000
        )

        cap_met = safe_float(
            st.session_state.capital_meta,
            15000
        )

        progreso = (
            min(
                1.0,
                max(
                    0.0,
                    cap_act / cap_met
                )
            )
            if cap_met > 0
            else 0.0
        )

        st.markdown(
            f"""
            **Capital actual:** ${cap_act:,.2f}

            **Meta:** ${cap_met:,.2f}
            """
        )

        st.progress(
            progreso
        )

        st.caption(
            f"Progreso: {progreso * 100:.1f}%"
        )

        with st.expander(
            "🔧 Configurar Meta"
        ):

            st.session_state.capital_actual = (
                st.number_input(
                    "Capital Actual ($)",
                    value=float(cap_act),
                    step=100.0,
                    key="sidebar_capital_actual"
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta de Capital ($)",
                    value=float(cap_met),
                    step=500.0,
                    key="sidebar_capital_meta"
                )
            )

        st.markdown("---")

        # ====================================================
        # REGLAS
        # ====================================================

        st.markdown(
            "## 📋 Mis Reglas"
        )

        st.markdown(
            st.session_state.reglas_disciplina
        )

        with st.expander(
            "✏️ Editar Reglas"
        ):

            input_reglas = st.text_area(
                "Reglas personalizadas:",
                value=st.session_state.reglas_disciplina,
                height=180,
                key="edit_rules"
            )

            if st.button(
                "💾 Guardar Reglas",
                key="save_rules"
            ):

                st.session_state.reglas_disciplina = (
                    input_reglas
                )

                st.success(
                    "Reglas actualizadas."
                )

                st.rerun()

        st.markdown("---")

        # ====================================================
        # PAGOS
        # ====================================================

        st.markdown(
            "## 💳 Suscripción"
        )

        st.caption(
            "Gestiona tu acceso PRO."
        )

        if STRIPE_MONTHLY_URL:

            st.markdown(
                f"""
                <a href="{STRIPE_MONTHLY_URL}"
                target="_blank"
                style="text-decoration:none;">

                <div style="
                    background:#635bff;
                    padding:10px;
                    border-radius:8px;
                    text-align:center;
                    font-weight:bold;
                ">

                💳 Pagar con Tarjeta

                </div>

                </a>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        # ====================================================
        # CERRAR SESIÓN
        # ====================================================

        if st.button(
            "🚪 Cerrar Sesión",
            key="logout"
        ):

            try:

                client = get_supabase_client()
                client.auth.sign_out()

            except Exception:
                pass

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []

            st.rerun()


# ============================================================
# 14. DASHBOARD
# ============================================================

def render_dashboard():

    tiene_acceso, estado_sub, dias_restantes = (
        evaluar_suscripcion(
            st.session_state.user
        )
    )

    render_sidebar(
        estado_sub
    )

    if not tiene_acceso:

        render_paywall()

        return

    user_id = st.session_state.user.id

    trades_db = cargar_trades_usuario(
        user_id
    )

    df_trades = pd.DataFrame(
        trades_db
    )

    st.markdown(
        "# ⚡ Journaling & AI Trading Audit"
    )

    st.caption(
        f"Estado: {estado_sub}"
    )

    tabs = st.tabs(
        [
            "➕ Registrar Trade",
            "📅 Track Record PnL",
            "💬 Chat IA & Auditoría",
            "🧮 Calc. Lotaje",
            "🧠 Análisis vs IA",
            "📈 Proyecciones",
            "📓 Diario & Psicotrading",
            "📊 Dashboard & Progreso"
        ]
    )

    (
        tab1,
        tab2,
        tab3,
        tab4,
        tab5,
        tab6,
        tab7,
        tab8
    ) = tabs

    # ========================================================
    # TAB 1
    # ========================================================

    with tab1:

        st.markdown(
            "## ➕ Registrar Nueva Operación"
        )

        st.info(
            "💡 Sube una captura de TradingView y la IA "
            "intentará detectar Entrada, SL y TP."
        )

        col1, col2 = st.columns(
            [1.25, 1]
        )

        with col2:

            st.markdown(
                "### 🖼️ Capturas"
            )

            upload_before = st.file_uploader(
                "1️⃣ ANTES — Setup",
                type=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="upload_before"
            )

            upload_after = st.file_uploader(
                "2️⃣ DESPUÉS — Resultado",
                type=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="upload_after"
            )

            img_before_b64 = ""
            img_after_b64 = ""

            if upload_before:

                bytes_b = upload_before.getvalue()

                img_before_b64 = (
                    procesar_imagen_b64(
                        upload_before
                    )
                )

                st.image(
                    bytes_b,
                    caption="SETUP ANTES",
                    use_container_width=True
                )

                if st.button(
                    "🧠 Escanear SETUP con IA",
                    key="scan_setup"
                ):

                    with st.spinner(
                        "Analizando captura..."
                    ):

                        extracted = (
                            analizar_captura_tradingview(
                                bytes_b
                            )
                        )

                    if extracted:

                        st.session_state.auto_entry = (
                            extracted["entry"]
                        )

                        st.session_state.auto_sl = (
                            extracted["sl"]
                        )

                        st.session_state.auto_tp = (
                            extracted["tp"]
                        )

                        st.success(
                            "✨ Entrada, SL y TP detectados."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "No pude detectar los valores. "
                            "Puedes introducirlos manualmente."
                        )

            if upload_after:

                img_after_b64 = (
                    procesar_imagen_b64(
                        upload_after
                    )
                )

                st.image(
                    upload_after,
                    caption="RESULTADO DESPUÉS",
                    use_container_width=True
                )

            monto_pnl = st.number_input(
                "Ganancia / Pérdida ($ USD)",
                value=0.0,
                step=10.0,
                key="trade_pnl"
            )

        with col1:

            st.markdown(
                "### ⚙️ Parámetros"
            )

            fecha_op = st.date_input(
                "Fecha",
                datetime.date.today(),
                key="trade_date"
            )

            par = st.selectbox(
                "Activo / Par",
                LISTA_ACTIVOS,
                key="trade_asset"
            )

            direccion = st.radio(
                "Dirección",
                [
                    "LONG 🟢",
                    "SHORT 🔴"
                ],
                horizontal=True,
                key="trade_direction"
            )

            timeframe = st.selectbox(
                "Timeframe",
                [
                    "M1",
                    "M5",
                    "M15",
                    "M30",
                    "H1",
                    "H4",
                    "D1",
                    "W1"
                ],
                index=5,
                key="trade_timeframe"
            )

            c_a, c_b = st.columns(2)

            with c_a:

                precio_entrada = st.number_input(
                    "Precio Entrada",
                    value=float(
                        st.session_state.auto_entry
                    ),
                    format="%.5f",
                    key="trade_entry"
                )

                stop_loss = st.number_input(
                    "Stop Loss",
                    value=float(
                        st.session_state.auto_sl
                    ),
                    format="%.5f",
                    key="trade_sl"
                )

            with c_b:

                take_profit = st.number_input(
                    "Take Profit",
                    value=float(
                        st.session_state.auto_tp
                    ),
                    format="%.5f",
                    key="trade_tp"
                )

                riesgo = abs(
                    precio_entrada
                    - stop_loss
                )

                beneficio = abs(
                    take_profit
                    - precio_entrada
                )

                rr = (
                    beneficio / riesgo
                    if riesgo > 0
                    else 0
                )

                st.metric(
                    "Risk : Reward",
                    f"1 : {rr:.2f}"
                )

            resultado = st.selectbox(
                "Resultado",
                [
                    "WIN 🟢",
                    "LOSS 🔴",
                    "BE ⚪"
                ],
                key="trade_result"
            )

            st.markdown(
                "### 🧠 Psicotrading"
            )

            emocion = st.selectbox(
                "Estado emocional",
                [
                    "Disciplinado / Neutro 🧘",
                    "Ansioso ⚡",
                    "FOMO / Miedo a perderse el movimiento 🚀",
                    "Venganza / Frustrado 🛑",
                    "Eufórico / Sobre-confiado 😎"
                ],
                key="trade_emotion"
            )

            notas_emocionales = st.text_area(
                "Notas emocionales",
                placeholder=(
                    "¿Respetaste tu plan? "
                    "¿Sentiste FOMO? "
                    "¿Moviste el SL?"
                ),
                key="trade_notes"
            )

            if st.button(
                "💾 Guardar Trade",
                key="save_trade",
                type="primary"
            ):

                nuevo_trade = {

                    "fecha": str(
                        fecha_op
                    ),

                    "par": par,

                    "resultado": resultado,

                    "emocion": emocion,

                    "beneficio_usd": float(
                        monto_pnl
                    ),

                    "trades_cant": 1,

                    "img_before": img_before_b64,

                    "img_after": img_after_b64,

                    # V2
                    "direccion": direccion,

                    "precio_entrada": float(
                        precio_entrada
                    ),

                    "stop_loss": float(
                        stop_loss
                    ),

                    "take_profit": float(
                        take_profit
                    ),

                    "rr": float(
                        rr
                    ),

                    "timeframe": timeframe,

                    "notas_emocionales":
                        notas_emocionales
                }

                if guardar_trade_supabase(
                    user_id,
                    nuevo_trade
                ):

                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0

                    st.success(
                        "✅ Operación guardada."
                    )

                    st.rerun()

    # ========================================================
    # TAB 2
    # ========================================================

    with tab2:

        st.markdown(
            "## 📅 Track Record & Calendario PnL"
        )

        if not df_trades.empty:

            df_trades["beneficio_usd"] = pd.to_numeric(
                df_trades["beneficio_usd"],
                errors="coerce"
            ).fillna(0)

            if "trades_cant" not in df_trades.columns:

                df_trades["trades_cant"] = 1

            df_grouped = (
                df_trades
                .groupby("fecha")
                .agg(
                    {
                        "beneficio_usd": "sum",
                        "trades_cant": "count"
                    }
                )
                .reset_index()
            )

        else:

            df_grouped = pd.DataFrame(
                columns=[
                    "fecha",
                    "beneficio_usd",
                    "trades_cant"
                ]
            )

        total_pnl = (
            df_trades["beneficio_usd"].sum()
            if not df_trades.empty
            else 0
        )

        dias_ganadores = len(
            df_grouped[
                df_grouped["beneficio_usd"] > 0
            ]
        )

        dias_perdedores = len(
            df_grouped[
                df_grouped["beneficio_usd"] < 0
            ]
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "PnL Acumulado",
            f"${total_pnl:,.2f}"
        )

        c2.metric(
            "Días Verdes 🟩",
            dias_ganadores
        )

        c3.metric(
            "Días Rojos 🟥",
            dias_perdedores
        )

        st.markdown("---")

        # CALENDARIO

        st.markdown(
            "### 🗓️ Calendario"
        )

        pnl_map = (
            df_grouped
            .set_index("fecha")["beneficio_usd"]
            .to_dict()
            if not df_grouped.empty
            else {}
        )

        trades_map = (
            df_grouped
            .set_index("fecha")["trades_cant"]
            .to_dict()
            if not df_grouped.empty
            else {}
        )

        hoy = datetime.date.today()

        semanas = calendar.Calendar(
            firstweekday=6
        ).monthdayscalendar(
            hoy.year,
            hoy.month
        )

        headers = [
            "Sun",
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat"
        ]

        cols = st.columns(7)

        for i, name in enumerate(headers):

            with cols[i]:

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-weight:bold;
                        padding:5px;
                    ">
                    {name}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        for semana in semanas:

            cols = st.columns(7)

            for idx, day in enumerate(semana):

                with cols[idx]:

                    if day == 0:

                        st.markdown(
                            "<div style='height:85px'></div>",
                            unsafe_allow_html=True
                        )

                        continue

                    fecha = datetime.date(
                        hoy.year,
                        hoy.month,
                        day
                    )

                    key = str(fecha)

                    pnl = pnl_map.get(
                        key,
                        None
                    )

                    trades = trades_map.get(
                        key,
                        0
                    )

                    if pnl is None:

                        bg = "#161b22"
                        fg = "#f0f3fa"
                        texto = ""

                    elif pnl > 0:

                        bg = "#34d399"
                        fg = "#000000"
                        texto = (
                            f"+${pnl:,.0f}"
                        )

                    elif pnl < 0:

                        bg = "#f87171"
                        fg = "#000000"
                        texto = (
                            f"-${abs(pnl):,.0f}"
                        )

                    else:

                        bg = "#161b22"
                        fg = "#ffffff"
                        texto = "$0"

                    border = (
                        "2px solid #00f2fe"
                        if fecha == hoy
                        else
                        "1px solid #252b36"
                    )

                    st.markdown(
                        f"""
                        <div style="
                            background:{bg};
                            color:{fg};
                            border:{border};
                            border-radius:7px;
                            height:85px;
                            padding:7px;
                            margin-bottom:7px;
                            text-align:center;
                        ">

                        <div style="
                            text-align:left;
                            font-weight:bold;
                        ">
                        {day}
                        </div>

                        <div style="
                            font-size:1.1rem;
                            font-weight:bold;
                            margin-top:8px;
                        ">
                        {texto}
                        </div>

                        <div style="
                            font-size:.7rem;
                        ">
                        {trades if pnl is not None else ""}
                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # HISTORIAL

        st.markdown(
            "### 📋 Historial Detallado"
        )

        if df_trades.empty:

            st.info(
                "Aún no tienes operaciones."
            )

        else:

            for _, row in df_trades.iterrows():

                trade_id = row.get(
                    "id"
                )

                pnl = safe_float(
                    row.get(
                        "beneficio_usd",
                        0
                    )
                )

                titulo = (
                    f"📅 {row.get('fecha')} | "
                    f"📊 {row.get('par')} | "
                    f"{row.get('resultado')} | "
                    f"${pnl:,.2f}"
                )

                with st.expander(
                    titulo
                ):

                    c1, c2, c3 = st.columns(
                        [1.2, 2, 2]
                    )

                    with c1:

                        st.markdown(
                            "### ⚙️ Operación"
                        )

                        st.write(
                            f"**Dirección:** "
                            f"{row.get('direccion', 'N/A')}"
                        )

                        st.write(
                            f"**Timeframe:** "
                            f"{row.get('timeframe', 'N/A')}"
                        )

                        st.write(
                            f"**Entrada:** "
                            f"{row.get('precio_entrada', 0)}"
                        )

                        st.write(
                            f"**SL:** "
                            f"{row.get('stop_loss', 0)}"
                        )

                        st.write(
                            f"**TP:** "
                            f"{row.get('take_profit', 0)}"
                        )

                        st.write(
                            f"**R:R:** "
                            f"1:{row.get('rr', 0)}"
                        )

                        st.write(
                            f"**Emoción:** "
                            f"{row.get('emocion', 'N/A')}"
                        )

                        notas = row.get(
                            "notas_emocionales",
                            ""
                        )

                        if notas:

                            st.markdown(
                                "**Notas:**"
                            )

                            st.write(
                                notas
                            )

                        if st.button(
                            "🗑️ Eliminar",
                            key=f"delete_{trade_id}"
                        ):

                            if eliminar_trade_supabase(
                                trade_id
                            ):

                                st.success(
                                    "Trade eliminado."
                                )

                                st.rerun()

                    with c2:

                        st.markdown(
                            "### 1️⃣ ANTES"
                        )

                        img_b = row.get(
                            "img_before"
                        )

                        if (
                            img_b
                            and str(img_b).startswith(
                                "data:image"
                            )
                        ):

                            st.image(
                                img_b,
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "Sin captura."
                            )

                    with c3:

                        st.markdown(
                            "### 2️⃣ DESPUÉS"
                        )

                        img_a = row.get(
                            "img_after"
                        )

                        if (
                            img_a
                            and str(img_a).startswith(
                                "data:image"
                            )
                        ):

                            st.image(
                                img_a,
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "Sin captura."
                            )

        if not df_grouped.empty:

            st.markdown("---")

            df_chart = df_grouped.copy()

            df_chart["tipo"] = np.where(
                df_chart["beneficio_usd"] >= 0,
                "GANANCIA",
                "PÉRDIDA"
            )

            fig = px.bar(
                df_chart,
                x="fecha",
                y="beneficio_usd",
                color="tipo",
                title="PnL Diario",
                template="plotly_dark",
                color_discrete_map={
                    "GANANCIA": "#00f2fe",
                    "PÉRDIDA": "#f44336"
                }
            )

            fig.update_layout(
                plot_bgcolor="#0b0e14",
                paper_bgcolor="#0b0e14"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # ========================================================
    # TAB 3
    # ========================================================

    with tab3:

        st.markdown(
            "## 💬 Chat IA & Auditoría"
        )

        st.caption(
            "Pregunta sobre tus estadísticas, "
            "hábitos y disciplina."
        )

        for message in st.session_state.chat_history:

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )

        prompt = st.chat_input(
            "Ejemplo: analiza mi disciplina..."
        )

        if prompt:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    prompt
                )

            with st.chat_message(
                "assistant"
            ):

                if df_trades.empty:

                    respuesta = (
                        "Todavía no tienes suficientes "
                        "operaciones registradas."
                    )

                else:

                    total = len(
                        df_trades
                    )

                    wins = len(
                        df_trades[
                            df_trades[
                                "beneficio_usd"
                            ] > 0
                        ]
                    )

                    losses = len(
                        df_trades[
                            df_trades[
                                "beneficio_usd"
                            ] < 0
                        ]
                    )

                    pnl = df_trades[
                        "beneficio_usd"
                    ].sum()

                    win_rate = (
                        wins / total * 100
                    )

                    respuesta = f"""
### 🧠 Auditoría rápida

Has registrado **{total} operaciones**.

- 🟢 Wins: **{wins}**
- 🔴 Losses: **{losses}**
- 📊 Win Rate: **{win_rate:.1f}%**
- 💰 PnL: **${pnl:,.2f} USD**

Tu siguiente objetivo debería ser identificar si tus pérdidas están relacionadas con **FOMO, venganza, exceso de operaciones o incumplimiento de reglas**.
"""

                st.markdown(
                    respuesta
                )

                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": respuesta
                    }
                )

    # ========================================================
    # TAB 4
    # ========================================================

    with tab4:

        st.markdown(
            "## 🧮 Calculadora de Lotaje"
        )

        c1, c2 = st.columns(2)

        with c1:

            balance = st.number_input(
                "Balance ($)",
                value=float(
                    st.session_state.capital_actual
                ),
                step=100.0
            )

            riesgo_pct = st.number_input(
                "Riesgo por operación (%)",
                value=1.0,
                step=0.25
            )

            stop_distance = st.number_input(
                "Distancia SL (pips/puntos)",
                value=20.0,
                step=1.0
            )

            valor_pip_lote = st.number_input(
                "Valor aproximado por pip/punto por lote",
                value=10.0,
                step=1.0
            )

        with c2:

            riesgo_usd = (
                balance
                * riesgo_pct
                / 100
            )

            if (
                stop_distance > 0
                and valor_pip_lote > 0
            ):

                lotaje = (
                    riesgo_usd
                    / (
                        stop_distance
                        * valor_pip_lote
                    )
                )

            else:

                lotaje = 0

            st.metric(
                "Riesgo máximo",
                f"${riesgo_usd:,.2f}"
            )

            st.metric(
                "Lotaje estimado",
                f"{lotaje:.2f}"
            )

            st.warning(
                "⚠️ El cálculo es orientativo. "
                "El valor por punto depende del instrumento "
                "y del contrato de tu broker."
            )

    # ========================================================
    # TAB 5
    # ========================================================

    with tab5:

        st.markdown(
            "## 🧠 Auditoría Visual con IA"
        )

        chart_audit = st.file_uploader(
            "Subir gráfico",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="audit_visual"
        )

        pregunta_ia = st.text_area(
            "¿Qué quieres que audite?",
            value=(
                "Analiza si la estructura del gráfico "
                "tiene buenas confluencias para mi setup."
            )
        )

        if chart_audit:

            st.image(
                chart_audit,
                use_container_width=True
            )

            if st.button(
                "🔍 Auditar con IA",
                key="audit_button"
            ):

                with st.spinner(
                    "La IA está analizando el gráfico..."
                ):

                    resultado_ia = analizar_grafico_ia(
                        chart_audit.getvalue(),
                        pregunta_ia
                    )

                st.markdown(
                    resultado_ia
                )

    # ========================================================
    # TAB 6
    # ========================================================

    with tab6:

        st.markdown(
            "## 📈 Proyección de Capital"
        )

        c1, c2 = st.columns(2)

        with c1:

            trades_mes = st.slider(
                "Trades por mes",
                5,
                50,
                15
            )

            win_rate_est = st.slider(
                "Win Rate estimado (%)",
                30,
                90,
                55
            )

        with c2:

            ganancia_prom = st.number_input(
                "Ganancia promedio WIN ($)",
                value=200.0,
                step=25.0
            )

            perdida_prom = st.number_input(
                "Pérdida promedio LOSS ($)",
                value=100.0,
                step=25.0
            )

        capital = float(
            st.session_state.capital_actual
        )

        datos = []

        for mes in range(1, 13):

            wins = (
                trades_mes
                * win_rate_est
                / 100
            )

            losses = (
                trades_mes
                - wins
            )

            pnl_mes = (
                wins * ganancia_prom
                - losses * perdida_prom
            )

            capital += pnl_mes

            datos.append(
                {
                    "Mes": f"Mes {mes}",
                    "Capital": capital
                }
            )

        st.metric(
            "Capital proyectado 12 meses",
            f"${capital:,.2f}"
        )

        df_proy = pd.DataFrame(
            datos
        )

        fig = px.line(
            df_proy,
            x="Mes",
            y="Capital",
            markers=True,
            template="plotly_dark",
            title="Proyección"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.warning(
            "Esta simulación no garantiza resultados reales."
        )

    # ========================================================
    # TAB 7
    # ========================================================

    with tab7:

        st.markdown(
            "## 📓 Diario & Psicotrading"
        )

        st.caption(
            "Utiliza esta sección para analizar "
            "tu comportamiento y disciplina."
        )

        reflexion = st.text_area(
            "Reflexión",
            height=220,
            placeholder=(
                "¿Qué hiciste bien hoy?\n"
                "¿Qué rompiste?\n"
                "¿Qué emoción dominó tu operativa?\n"
                "¿Qué vas a cambiar mañana?"
            )
        )

        if st.button(
            "💾 Guardar Reflexión"
        ):

            st.success(
                "🧠 Reflexión guardada durante esta sesión."
            )

    # ========================================================
    # TAB 8
    # ========================================================

    with tab8:

        st.markdown(
            "## 📊 Dashboard & Progreso"
        )

        total = len(
            df_trades
        )

        if not df_trades.empty:

            wins = len(
                df_trades[
                    df_trades[
                        "beneficio_usd"
                    ] > 0
                ]
            )

            losses = len(
                df_trades[
                    df_trades[
                        "beneficio_usd"
                    ] < 0
                ]
            )

            pnl = df_trades[
                "beneficio_usd"
            ].sum()

            win_rate = (
                wins / total * 100
                if total
                else 0
            )

            dias = (
                df_trades["fecha"]
                .nunique()
            )

        else:

            wins = 0
            losses = 0
            pnl = 0
            win_rate = 0
            dias = 0

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "PnL",
            f"${pnl:,.2f}"
        )

        m2.metric(
            "Win Rate",
            f"{win_rate:.1f}%"
        )

        m3.metric(
            "Trades",
            total
        )

        m4.metric(
            "Días Operados",
            dias
        )

        st.markdown("---")

        if not df_trades.empty:

            fig = px.bar(
                df_trades,
                x="par",
                y="beneficio_usd",
                color="resultado",
                title="Resultado por Activo",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.markdown(
                "### 📋 Operaciones"
            )

            columnas = [
                "fecha",
                "par",
                "direccion",
                "timeframe",
                "precio_entrada",
                "stop_loss",
                "take_profit",
                "rr",
                "resultado",
                "beneficio_usd",
                "emocion"
            ]

            columnas_disponibles = [
                c
                for c in columnas
                if c in df_trades.columns
            ]

            st.dataframe(
                df_trades[
                    columnas_disponibles
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Registra tu primer trade para "
                "activar las estadísticas."
            )


# ============================================================
# 15. FLUJO PRINCIPAL
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
