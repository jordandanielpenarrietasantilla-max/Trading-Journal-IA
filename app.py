import streamlit as st
import datetime
import requests
import json
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import calendar
import io

from PIL import Image
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
# 2. CONFIGURACIÓN / SECRETS
# ============================================================

SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    "https://lyzvcbjpoydeckxtbcq.supabase.co"
)

SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)

# Pagos Crypto
LINK_BINANCE_INSCRIPCION = st.secrets.get(
    "LINK_BINANCE_INSCRIPCION",
    "https://s.binance.com/8vSxLZRA"
)

LINK_BINANCE_ANUAL = st.secrets.get(
    "LINK_BINANCE_ANUAL",
    "https://s.binance.com/NvHWGF9P"
)

LINK_BINANCE_RECURRENTE = st.secrets.get(
    "LINK_BINANCE_RECURRENTE",
    "https://s.binance.com/U7v5zFVr"
)

BINANCE_PAY_ID = st.secrets.get(
    "BINANCE_PAY_ID",
    "JORDAN_SANTI9"
)

LINK_TELEGRAM_SOPORTE = st.secrets.get(
    "LINK_TELEGRAM_SOPORTE",
    "https://t.me/tu_usuario_telegram"
)

# Pagos tarjeta
# Coloca aquí tus enlaces de Stripe Checkout cuando los tengas.
STRIPE_MENSUAL_LINK = st.secrets.get(
    "STRIPE_MENSUAL_LINK",
    ""
)

STRIPE_ANUAL_LINK = st.secrets.get(
    "STRIPE_ANUAL_LINK",
    ""
)


# ============================================================
# 3. SUPABASE
# ============================================================

def get_supabase_client() -> Client:
    if not SUPABASE_KEY:
        raise RuntimeError(
            "Falta SUPABASE_KEY en los Secrets de Streamlit."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ============================================================
# 4. ESTADO DE SESIÓN
# ============================================================

defaults = {
    "authenticated": False,
    "user": None,
    "chat_history": [],
    "nombre_trader": "Trader Pro",
    "capital_actual": 10000.0,
    "capital_meta": 15000.0,
    "reglas_disciplina": (
        "• Acepta la pérdida antes de entrar.\n"
        "• Corta pérdidas rápido.\n"
        "• Deja correr los ganadores.\n"
        "• Máximo 2 operaciones perdedoras por día."
    ),
    "auto_entry": 0.0,
    "auto_sl": 0.0,
    "auto_tp": 0.0,
    "editing_trade_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
# 6. UTILIDADES DE IMAGEN
# ============================================================

def image_file_to_data_url(uploaded_file):
    """
    Convierte una imagen subida a Data URL.
    """
    if uploaded_file is None:
        return ""

    try:
        raw = uploaded_file.getvalue()

        image = Image.open(io.BytesIO(raw)).convert("RGB")

        image.thumbnail((1200, 900))

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=82,
            optimize=True
        )

        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return f"data:image/jpeg;base64,{encoded}"

    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return ""


def data_url_to_bytes(data_url):
    """
    Convierte una Data URL almacenada en Supabase
    nuevamente a bytes para st.image().
    """

    if not data_url:
        return None

    try:
        if "," not in str(data_url):
            return None

        encoded = str(data_url).split(",", 1)[1]

        return base64.b64decode(encoded)

    except Exception:
        return None


def mostrar_imagen_guardada(data_url, caption=""):
    """
    Muestra correctamente una imagen guardada en Base64.
    Nunca imprime el Base64 en pantalla.
    """

    image_bytes = data_url_to_bytes(data_url)

    if image_bytes:
        st.image(
            image_bytes,
            caption=caption,
            use_container_width=True
        )

    else:
        st.caption("📷 Sin captura")


# ============================================================
# 7. CSS
# ============================================================

def aplicar_estilos():

    css = """
    <style>

    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
    }

    p, label, h1, h2, h3, h4, span, div, .stMarkdown {
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

    div[data-baseweb="select"] span {
        color: #00f2fe !important;
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
        font-size: 14px !important;
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
        border: 1px solid rgba(0,210,255,0.4) !important;
        border-radius: 8px !important;
    }

    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #77808c !important;
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
        width: 100%;
        box-shadow:
            0px 4px 15px rgba(0,210,255,0.3) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow:
            0px 6px 20px rgba(0,210,255,0.45) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0,210,255,0.2) !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(
            135deg,
            #e53935 0%,
            #b71c1c 100%
        ) !important;

        box-shadow:
            0px 4px 12px rgba(229,57,53,0.3) !important;
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
        color: #4caf50;
        border: 1px solid #4caf50;
    }

    .closed {
        background-color: rgba(244,67,54,0.2);
        color: #f44336;
        border: 1px solid #f44336;
    }

    .paywall-card {
        background-color: #161b22;
        border: 1px solid #f0b90b;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow:
            0px 0px 20px rgba(240,185,11,0.2);
    }

    .trade-card {
        background-color: #121721;
        border: 1px solid rgba(0,242,254,0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }

    .edit-card {
        background-color: #111822;
        border: 1px solid rgba(0,242,254,0.4);
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0 20px 0;
    }

    </style>
    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


# ============================================================
# 8. BASE DE DATOS — CARGAR TRADES
# ============================================================

def cargar_trades_usuario(user_id):

    try:

        client = get_supabase_client()

        res = (
            client
            .table("trades")
            .select("*")
            .eq("user_id", user_id)
            .order("fecha", desc=True)
            .execute()
        )

        return res.data if res.data else []

    except Exception as e:

        st.error(
            f"❌ Error cargando operaciones: {e}"
        )

        return []


# ============================================================
# 9. GUARDAR TRADE
# ============================================================

def guardar_trade_supabase(
    user_id,
    trade_data
):

    try:

        client = get_supabase_client()

        data = dict(trade_data)

        data["user_id"] = user_id

        client \
            .table("trades") \
            .insert(data) \
            .execute()

        return True

    except Exception as e:

        st.error(
            f"❌ Error guardando operación: {e}"
        )

        return False


# ============================================================
# 10. ACTUALIZAR TRADE EXISTENTE
# ============================================================

def actualizar_trade_supabase(
    trade_id,
    user_id,
    trade_data
):

    try:

        client = get_supabase_client()

        data = dict(trade_data)

        # Seguridad adicional:
        # solo modifica el trade perteneciente
        # al usuario actual.

        response = (
            client
            .table("trades")
            .update(data)
            .eq("id", trade_id)
            .eq("user_id", user_id)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        st.error(
            f"❌ Error actualizando operación: {e}"
        )

        return False


# ============================================================
# 11. ELIMINAR TRADE
# ============================================================

def eliminar_trade_supabase(
    trade_id,
    user_id
):

    try:

        client = get_supabase_client()

        (
            client
            .table("trades")
            .delete()
            .eq("id", trade_id)
            .eq("user_id", user_id)
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"❌ Error eliminando operación: {e}"
        )

        return False


# ============================================================
# 12. IA — ANÁLISIS DE TRADINGVIEW
# ============================================================

def analizar_captura_tradingview(
    image_bytes
):

    if not OPENROUTER_API_KEY:

        return None

    b64_img = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    headers = {
        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json"
    }

    prompt = """
Analiza este gráfico de TradingView.

Busca específicamente la herramienta de posición
Risk/Reward o los niveles numéricos de:

Entry
Stop Loss
Take Profit

Devuelve ÚNICAMENTE JSON válido.

Formato exacto:

{
    "entry": 0.0,
    "sl": 0.0,
    "tp": 0.0
}

Si un valor no aparece claramente utiliza 0.0.

No escribas explicaciones.
No escribas markdown.
No agregues texto adicional.
"""

    payload = {

        "model":
            "openai/gpt-4o-mini",

        "messages": [

            {
                "role": "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            prompt
                    },

                    {
                        "type":
                            "image_url",

                        "image_url": {

                            "url":
                                f"data:image/png;base64,{b64_img}"
                        }
                    }
                ]
            }
        ]
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()

        result = response.json()

        content = (
            result["choices"][0]
            ["message"]["content"]
        )

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(content)

    except Exception:

        return None


# ============================================================
# 13. SUSCRIPCIÓN
# ============================================================

def evaluar_suscripcion(user):

    user_email = (
        user.email
        if user and hasattr(user, "email")
        else ""
    )

    # ADMIN

    if (
        user_email.lower()
        == "jordandanielpenarrietasantilla@gmail.com"
    ):

        return (
            True,
            "Creador / Admin 👑",
            99999
        )

    metadata = (
        user.user_metadata
        if (
            user
            and hasattr(user, "user_metadata")
            and user.user_metadata
        )
        else {}
    )

    if metadata.get("es_vip", False):

        return (
            True,
            "Acceso PRO 💎",
            999
        )

    created_at_str = (
        str(user.created_at)
        if hasattr(user, "created_at")
        else None
    )

    try:

        if created_at_str:

            fecha_registro = (
                datetime.datetime
                .strptime(
                    created_at_str[:10],
                    "%Y-%m-%d"
                )
                .date()
            )

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
# 14. PAYWALL
# ============================================================

def render_paywall():

    st.markdown(
        "## 🔒 Tu Período de Prueba Gratis de 3 Días ha Expirado"
    )

    st.markdown(
        """
Para continuar utilizando el Journal, Track Record
y herramientas de auditoría, activa tu acceso.
"""
    )

    tab_crypto, tab_card = st.tabs(
        [
            "🪙 Binance Pay",
            "💳 Débito / Crédito"
        ]
    )


    # --------------------------------------------------------
    # BINANCE
    # --------------------------------------------------------

    with tab_crypto:

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                f"""
                <div class="paywall-card">

                <h3>🟡 Suscripción Mensual</h3>

                <h2>$5 USD / mes</h2>

                <p>
                Luego $2.50 USD / mes
                </p>

                <hr>

                <p>✔️ Acceso ilimitado</p>
                <p>✔️ Track Record</p>
                <p>✔️ Auditoría IA</p>
                <p>✔️ Sin contrato</p>

                <br>

                <a href="{LINK_BINANCE_INSCRIPCION}"
                   target="_blank">

                <button style="
                    background:#f0b90b;
                    color:#000;
                    border:none;
                    padding:14px;
                    border-radius:8px;
                    font-weight:bold;
                    width:100%;
                ">

                🟡 Pagar $5 con Binance Pay

                </button>

                </a>

                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            st.markdown(
                f"""
                <div class="paywall-card">

                <h3>🚀 Acceso Anual</h3>

                <h2>$20 USD / año</h2>

                <p>
                Ahorra frente al mensual
                </p>

                <hr>

                <p>🌟 Acceso por 1 año</p>
                <p>🔒 Pago único</p>
                <p>🎁 Actualizaciones incluidas</p>
                <p>🧠 IA incluida</p>

                <br>

                <a href="{LINK_BINANCE_ANUAL}"
                   target="_blank">

                <button style="
                    background:#00f2fe;
                    color:#000;
                    border:none;
                    padding:14px;
                    border-radius:8px;
                    font-weight:bold;
                    width:100%;
                ">

                💎 Pagar $20 con Binance Pay

                </button>

                </a>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("---")

        st.markdown(
            "### 📲 Pago directo / Renovación"
        )

        st.code(
            f"Binance Pay ID: {BINANCE_PAY_ID}"
        )

        st.markdown(
            f"""
            [👉 Renovación mensual $2.50 USDT]
            ({LINK_BINANCE_RECURRENTE})
            """
        )


    # --------------------------------------------------------
    # TARJETAS
    # --------------------------------------------------------

    with tab_card:

        st.markdown(
            "### 💳 Paga con tarjeta de débito o crédito"
        )

        st.info(
            """
            Los pagos con tarjeta funcionan mediante
            un enlace seguro de checkout.
            """
        )

        col1, col2 = st.columns(2)

        with col1:

            st.markdown(
                """
                <div class="paywall-card">

                <h3>💳 Mensual</h3>

                <h2>$5 USD / mes</h2>

                <p>
                Acceso completo al Journal.
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

            if STRIPE_MENSUAL_LINK:

                st.link_button(
                    "💳 Pagar $5 con tarjeta",
                    STRIPE_MENSUAL_LINK,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Configura STRIPE_MENSUAL_LINK en Secrets."
                )


        with col2:

            st.markdown(
                """
                <div class="paywall-card">

                <h3>💎 Anual</h3>

                <h2>$20 USD / año</h2>

                <p>
                Acceso completo durante 12 meses.
                </p>

                </div>
                """,
                unsafe_allow_html=True
            )

            if STRIPE_ANUAL_LINK:

                st.link_button(
                    "💳 Pagar $20 con tarjeta",
                    STRIPE_ANUAL_LINK,
                    use_container_width=True
                )

            else:

                st.warning(
                    "Configura STRIPE_ANUAL_LINK en Secrets."
                )


    st.markdown("---")

    st.markdown(
        "### ✈️ Después del pago"
    )

    st.markdown(
        f"""
        Envía tu comprobante para activar la cuenta.

        [💬 Contactar soporte]({LINK_TELEGRAM_SOPORTE})
        """
    )


# ============================================================
# 15. AUTENTICACIÓN
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
            Audita tu operativa con Inteligencia Artificial,
            registra tus emociones y lleva tu disciplina
            al siguiente nivel.
            """
        )

        st.markdown(
            """
            ### 🧠 Tu centro de control de trading

            - 📊 Track Record
            - 📅 Calendario PnL
            - 📸 Antes / Después
            - 🤖 IA
            - 🧠 Psicotrading
            - 🧮 Gestión de riesgo
            """
        )


    with col2:

        (
            tab_login,
            tab_register,
            tab_reset
        ) = st.tabs(
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

                if login_email and login_pass:

                    try:

                        client = get_supabase_client()

                        res = (
                            client.auth
                            .sign_in_with_password(
                                {
                                    "email":
                                        login_email,

                                    "password":
                                        login_pass
                                }
                            )
                        )

                        st.session_state.authenticated = True
                        st.session_state.user = res.user

                        st.rerun()

                    except Exception as err:

                        st.error(
                            f"Error al iniciar sesión: {err}"
                        )


        # REGISTRO

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

                if reg_email and reg_pass:

                    try:

                        client = get_supabase_client()

                        client.auth.sign_up(
                            {
                                "email":
                                    reg_email,

                                "password":
                                    reg_pass
                            }
                        )

                        st.success(
                            """
                            ¡Registro exitoso!
                            Revisa tu correo si Supabase
                            solicita confirmación y luego
                            inicia sesión.
                            """
                        )

                    except Exception as e:

                        st.error(
                            f"Error al registrar: {e}"
                        )


        # RESET

        with tab_reset:

            st.markdown(
                "### 🔐 Recupera tu Contraseña"
            )

            reset_email = st.text_input(
                "Correo Electrónico Registrado",
                key="reset_email"
            )

            if st.button(
                "Enviar Enlace de Recuperación",
                key="btn_reset"
            ):

                if reset_email:

                    try:

                        client = get_supabase_client()

                        app_url = (
                            "https://trading-journal-ia-"
                            "7lvamxtjspcbclwcda2zxg"
                            ".streamlit.app/"
                        )

                        client.auth.reset_password_for_email(
                            reset_email,
                            {
                                "redirectTo":
                                    app_url
                            }
                        )

                        st.success(
                            """
                            📩 Se ha enviado el enlace
                            de recuperación.
                            """
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


# ============================================================
# 16. SIDEBAR
# ============================================================

def render_sidebar(estado_sub):

    with st.sidebar:

        st.markdown(
            "### 👤 Perfil Trader"
        )

        user = st.session_state.user

        user_email = (
            user.email
            if user
            else "trader@ejemplo.com"
        )

        metadata = (
            user.user_metadata
            if (
                user
                and hasattr(user, "user_metadata")
                and user.user_metadata
            )
            else {}
        )

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


        # ----------------------------------------------------
        # PERFIL
        # ----------------------------------------------------

        col_img, col_txt = st.columns(
            [1, 2]
        )

        with col_img:

            if foto_b64:

                foto_bytes = data_url_to_bytes(
                    foto_b64
                )

                # Soporta tanto Data URL como Base64
                # puro de versiones anteriores.

                if foto_bytes is None:

                    try:

                        foto_bytes = base64.b64decode(
                            foto_b64
                        )

                    except Exception:

                        foto_bytes = None

                if foto_bytes:

                    st.image(
                        foto_bytes,
                        width=65
                    )

                else:

                    st.markdown(
                        "👤"
                    )

            else:

                st.markdown(
                    "<div style='font-size:2.5rem;text-align:center;'>👤</div>",
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

        else:

            st.warning(
                f"⏳ {estado_sub}"
            )


        # ----------------------------------------------------
        # EDITAR PERFIL
        # ----------------------------------------------------

        with st.expander(
            "⚙️ Modificar Perfil"
        ):

            input_nombre = st.text_input(
                "Nombre de Usuario",
                value=nombre_actual
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
                "Guardar Cambios",
                key="save_profile"
            ):

                nueva_foto = foto_b64

                if foto_subida:

                    nueva_foto = (
                        image_file_to_data_url(
                            foto_subida
                        )
                    )

                try:

                    client = get_supabase_client()

                    res = client.auth.update_user(
                        {
                            "data": {
                                "username":
                                    input_nombre,

                                "avatar_b64":
                                    nueva_foto
                            }
                        }
                    )

                    st.session_state.user = res.user

                    st.session_state.nombre_trader = (
                        input_nombre
                    )

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )


        st.markdown("---")


        # ----------------------------------------------------
        # META
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        cap_act = (
            st.session_state.capital_actual
        )

        cap_met = (
            st.session_state.capital_meta
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
            else 0
        )

        st.markdown(
            f"""
            **Capital:** `${cap_act:,.0f}`
            /
            `${cap_met:,.0f}`
            """
        )

        st.progress(progreso)

        with st.expander(
            "🔧 Configuración Meta"
        ):

            st.session_state.capital_actual = (
                st.number_input(
                    "Capital Actual ($)",
                    value=float(cap_act),
                    step=500.0
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta de Capital ($)",
                    value=float(cap_met),
                    step=1000.0
                )
            )


        st.markdown("---")


        # ----------------------------------------------------
        # SESIONES
        # ----------------------------------------------------

        st.markdown(
            "### ⏰ Hora Local & Sesiones"
        )

        st.components.v1.html(
            """
            <div id="clock" style="
                font-family:monospace;
                font-size:18px;
                font-weight:bold;
                color:#00f2fe;
                background:#161b22;
                border:1px solid rgba(0,210,255,0.4);
                border-radius:8px;
                padding:6px;
                text-align:center;
            ">
            00:00:00
            </div>

            <script>

            function updateClock() {

                var now = new Date();

                var timeString =
                    now.toLocaleTimeString();

                document.getElementById(
                    "clock"
                ).innerHTML =
                    timeString + " (Local)";
            }

            setInterval(
                updateClock,
                1000
            );

            updateClock();

            </script>
            """,
            height=50
        )


        hora_utc = (
            datetime.datetime.utcnow().hour
        )

        londres_status = (
            '<span class="market-badge open">'
            'ABIERTO'
            '</span>'
            if 7 <= hora_utc <= 15
            else
            '<span class="market-badge closed">'
            'CERRADO'
            '</span>'
        )

        ny_status = (
            '<span class="market-badge open">'
            'ABIERTO'
            '</span>'
            if 12 <= hora_utc <= 20
            else
            '<span class="market-badge closed">'
            'CERRADO'
            '</span>'
        )

        st.markdown(
            f"**Londres:** {londres_status}",
            unsafe_allow_html=True
        )

        st.markdown(
            f"**N. York:** {ny_status}",
            unsafe_allow_html=True
        )


        st.markdown("---")


        # ----------------------------------------------------
        # REGLAS
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Mis Reglas"
        )

        with st.expander(
            "✏️ Editar Reglas"
        ):

            input_reglas = st.text_area(
                "Reglas personalizadas:",
                value=(
                    st.session_state
                    .reglas_disciplina
                ),
                height=150
            )

            if st.button(
                "Guardar Reglas",
                key="save_rules"
            ):

                st.session_state.reglas_disciplina = (
                    input_reglas
                )

                st.success(
                    "Reglas actualizadas."
                )

                st.rerun()

        st.markdown(
            st.session_state.reglas_disciplina
        )


        st.markdown("---")


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

            st.rerun()


# ============================================================
# 17. FORMULARIO DE EDICIÓN
# ============================================================

def render_editor_trade(
    row,
    user_id
):

    trade_id = row.get("id")

    st.markdown(
        """
        <div class="edit-card">
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### ✏️ Editar operación"
    )

    st.info(
        """
        Puedes completar ahora las capturas que
        faltaban y modificar cualquier dato del trade.
        """
    )


    # --------------------------------------------------------
    # FECHA
    # --------------------------------------------------------

    fecha_original = row.get(
        "fecha",
        str(datetime.date.today())
    )

    try:

        fecha_default = (
            datetime.datetime
            .strptime(
                str(fecha_original)[:10],
                "%Y-%m-%d"
            )
            .date()
        )

    except Exception:

        fecha_default = datetime.date.today()


    fecha = st.date_input(
        "Fecha",
        value=fecha_default,
        key=f"edit_date_{trade_id}"
    )


    # --------------------------------------------------------
    # DATOS PRINCIPALES
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        par_actual = row.get(
            "par",
            LISTA_ACTIVOS[0]
        )

        if par_actual not in LISTA_ACTIVOS:

            opciones_par = (
                [par_actual]
                + LISTA_ACTIVOS
            )

        else:

            opciones_par = LISTA_ACTIVOS

        par = st.selectbox(
            "Activo / Par",
            opciones_par,
            index=opciones_par.index(
                par_actual
            ),
            key=f"edit_par_{trade_id}"
        )


        direccion_actual = row.get(
            "direccion",
            "LONG 🟢"
        )

        direccion = st.radio(
            "Dirección",
            [
                "LONG 🟢",
                "SHORT 🔴"
            ],
            index=(
                1
                if str(
                    direccion_actual
                ).startswith("SHORT")
                else 0
            ),
            horizontal=True,
            key=f"edit_direction_{trade_id}"
        )


        precio_entrada = st.number_input(
            "Precio Entrada",
            value=float(
                row.get(
                    "precio_entrada",
                    0
                ) or 0
            ),
            format="%.5f",
            key=f"edit_entry_{trade_id}"
        )


        stop_loss = st.number_input(
            "Stop Loss",
            value=float(
                row.get(
                    "stop_loss",
                    0
                ) or 0
            ),
            format="%.5f",
            key=f"edit_sl_{trade_id}"
        )


    with col2:

        take_profit = st.number_input(
            "Take Profit",
            value=float(
                row.get(
                    "take_profit",
                    0
                ) or 0
            ),
            format="%.5f",
            key=f"edit_tp_{trade_id}"
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


        resultado_actual = row.get(
            "resultado",
            "BE ⚪"
        )

        resultados = [
            "WIN 🟢",
            "LOSS 🔴",
            "BE ⚪"
        ]

        resultado = st.selectbox(
            "Resultado",
            resultados,
            index=(
                resultados.index(
                    resultado_actual
                )
                if resultado_actual in resultados
                else 0
            ),
            key=f"edit_result_{trade_id}"
        )


        monto_pnl = st.number_input(
            "PnL USD",
            value=float(
                row.get(
                    "beneficio_usd",
                    0
                ) or 0
            ),
            step=10.0,
            key=f"edit_pnl_{trade_id}"
        )


    # --------------------------------------------------------
    # PSICOLOGÍA
    # --------------------------------------------------------

    emociones = [
        "Disciplinado / Neutro 🧘",
        "Ansioso ⚡",
        "FOMO / Miedo a perderse el movimiento 🚀",
        "Venganza / Frustrado 🛑",
        "Eufórico / Sobre-confiado 😎"
    ]

    emocion_actual = row.get(
        "emocion",
        emociones[0]
    )

    emocion = st.selectbox(
        "Estado emocional",
        emociones,
        index=(
            emociones.index(
                emocion_actual
            )
            if emocion_actual in emociones
            else 0
        ),
        key=f"edit_emotion_{trade_id}"
    )


    timeframe = st.text_input(
        "Timeframe",
        value=str(
            row.get(
                "timeframe",
                ""
            ) or ""
        ),
        placeholder="Ej: D1 / H4 / H1",
        key=f"edit_tf_{trade_id}"
    )


    notas = st.text_area(
        "Notas emocionales",
        value=str(
            row.get(
                "notas_emocionales",
                ""
            ) or ""
        ),
        height=120,
        key=f"edit_notes_{trade_id}"
    )


    # --------------------------------------------------------
    # IMÁGENES EXISTENTES
    # --------------------------------------------------------

    st.markdown(
        "### 📸 Capturas"
    )

    img_before_existing = row.get(
        "img_before",
        ""
    )

    img_after_existing = row.get(
        "img_after",
        ""
    )

    img1, img2 = st.columns(2)

    with img1:

        st.markdown(
            "**1️⃣ ANTES**"
        )

        if img_before_existing:

            mostrar_imagen_guardada(
                img_before_existing,
                "Captura actual"
            )

        else:

            st.info(
                "Todavía no hay captura ANTES."
            )

        upload_before_edit = st.file_uploader(
            "Subir / reemplazar ANTES",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_before_{trade_id}"
        )


    with img2:

        st.markdown(
            "**2️⃣ DESPUÉS**"
        )

        if img_after_existing:

            mostrar_imagen_guardada(
                img_after_existing,
                "Captura actual"
            )

        else:

            st.info(
                "Todavía no hay captura DESPUÉS."
            )

        upload_after_edit = st.file_uploader(
            "Subir / reemplazar DESPUÉS",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_after_{trade_id}"
        )


    # --------------------------------------------------------
    # BOTONES
    # --------------------------------------------------------

    b1, b2 = st.columns(2)

    with b1:

        guardar = st.button(
            "💾 Guardar cambios",
            key=f"save_edit_{trade_id}",
            use_container_width=True
        )

    with b2:

        cancelar = st.button(
            "❌ Cancelar edición",
            key=f"cancel_edit_{trade_id}",
            use_container_width=True
        )


    if cancelar:

        st.session_state.editing_trade_id = None

        st.rerun()


    if guardar:

        img_before_final = img_before_existing
        img_after_final = img_after_existing

        if upload_before_edit:

            nueva = image_file_to_data_url(
                upload_before_edit
            )

            if nueva:

                img_before_final = nueva


        if upload_after_edit:

            nueva = image_file_to_data_url(
                upload_after_edit
            )

            if nueva:

                img_after_final = nueva


        updated_data = {

            "fecha":
                str(fecha),

            "par":
                par,

            "direccion":
                direccion,

            "precio_entrada":
                precio_entrada,

            "stop_loss":
                stop_loss,

            "take_profit":
                take_profit,

            "rr":
                rr,

            "timeframe":
                timeframe,

            "resultado":
                resultado,

            "emocion":
                emocion,

            "beneficio_usd":
                monto_pnl,

            "notas_emocionales":
                notas,

            "img_before":
                img_before_final,

            "img_after":
                img_after_final
        }


        if actualizar_trade_supabase(
            trade_id,
            user_id,
            updated_data
        ):

            st.success(
                "✅ Trade actualizado correctamente."
            )

            st.session_state.editing_trade_id = None

            st.rerun()


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# ============================================================
# 18. DASHBOARD
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


    user_id = (
        st.session_state.user.id
    )

    trades_db = cargar_trades_usuario(
        user_id
    )

    df_trades = pd.DataFrame(
        trades_db
    )


    st.markdown(
        "## ⚡ Journaling & AI Trading Audit"
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
    ) = st.tabs(
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


    # ========================================================
    # TAB 1 — REGISTRAR
    # ========================================================

    with tab1:

        st.info(
            """
            💡 Sube una captura de TradingView con
            Risk/Reward y la IA intentará completar
            Entry, SL y TP automáticamente.
            """
        )

        col1, col2 = st.columns(
            [1.2, 1]
        )


        with col2:

            st.markdown(
                "### 🖼️ Capturas"
            )

            upload_before = st.file_uploader(
                "1️⃣ Screenshot ANTES",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                ],
                key="new_before"
            )

            upload_after = st.file_uploader(
                "2️⃣ Screenshot DESPUÉS",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                ],
                key="new_after"
            )


            img_before_b64 = ""

            img_after_b64 = ""


            if upload_before:

                img_before_b64 = (
                    image_file_to_data_url(
                        upload_before
                    )
                )

                st.image(
                    upload_before,
                    caption="Trade SETUP — Antes",
                    use_container_width=True
                )


                if st.button(
                    "🧠 Escanear SETUP con IA",
                    key="scan_new"
                ):

                    with st.spinner(
                        "Analizando gráfico..."
                    ):

                        extracted = (
                            analizar_captura_tradingview(
                                upload_before.getvalue()
                            )
                        )

                        if extracted:

                            st.session_state.auto_entry = (
                                float(
                                    extracted.get(
                                        "entry",
                                        0
                                    )
                                    or 0
                                )
                            )

                            st.session_state.auto_sl = (
                                float(
                                    extracted.get(
                                        "sl",
                                        0
                                    )
                                    or 0
                                )
                            )

                            st.session_state.auto_tp = (
                                float(
                                    extracted.get(
                                        "tp",
                                        0
                                    )
                                    or 0
                                )
                            )

                            st.success(
                                "✨ Valores detectados."
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "No se pudieron detectar los valores."
                            )


            if upload_after:

                img_after_b64 = (
                    image_file_to_data_url(
                        upload_after
                    )
                )

                st.image(
                    upload_after,
                    caption="Resultado — Después",
                    use_container_width=True
                )


            monto_pnl = st.number_input(
                "Ganancia / Pérdida USD",
                value=0.0,
                step=10.0,
                key="new_pnl"
            )


        with col1:

            st.markdown(
                "### 📝 Parámetros"
            )

            fecha_op = st.date_input(
                "Fecha",
                datetime.date.today(),
                key="new_date"
            )


            sub1, sub2 = st.columns(2)


            with sub1:

                par = st.selectbox(
                    "Activo / Par",
                    LISTA_ACTIVOS,
                    key="new_par"
                )

                direccion = st.radio(
                    "Dirección",
                    [
                        "LONG 🟢",
                        "SHORT 🔴"
                    ],
                    horizontal=True,
                    key="new_direction"
                )

                precio_entrada = st.number_input(
                    "Precio Entrada",
                    value=float(
                        st.session_state.auto_entry
                    ),
                    format="%.5f",
                    key="new_entry"
                )

                stop_loss = st.number_input(
                    "Stop Loss",
                    value=float(
                        st.session_state.auto_sl
                    ),
                    format="%.5f",
                    key="new_sl"
                )


            with sub2:

                take_profit = st.number_input(
                    "Take Profit",
                    value=float(
                        st.session_state.auto_tp
                    ),
                    format="%.5f",
                    key="new_tp"
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
                    key="new_result"
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
                key="new_emotion"
            )


            timeframe = st.text_input(
                "Timeframe",
                placeholder="Ej: D1 / H4 / H1",
                key="new_timeframe"
            )


            notas_emocionales = st.text_area(
                "Notas emocionales",
                placeholder=(
                    "¿Respetaste tu plan? "
                    "¿Sentiste FOMO? "
                    "¿Qué aprendiste?"
                ),
                key="new_notes"
            )


            if st.button(
                "💾 Guardar Trade",
                key="save_new_trade"
            ):

                nuevo_trade = {

                    "fecha":
                        str(fecha_op),

                    "par":
                        par,

                    "direccion":
                        direccion,

                    "precio_entrada":
                        precio_entrada,

                    "stop_loss":
                        stop_loss,

                    "take_profit":
                        take_profit,

                    "rr":
                        rr,

                    "timeframe":
                        timeframe,

                    "resultado":
                        resultado,

                    "emocion":
                        emocion,

                    "beneficio_usd":
                        monto_pnl,

                    "trades_cant":
                        1,

                    "notas_emocionales":
                        notas_emocionales,

                    "img_before":
                        img_before_b64,

                    "img_after":
                        img_after_b64
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
    # TAB 2 — TRACK RECORD
    # ========================================================

    with tab2:

        st.markdown(
            "### 📅 Track Record & Calendario PnL"
        )


        if not df_trades.empty:

            # Compatibilidad con registros antiguos

            for col in [
                "beneficio_usd",
                "trades_cant"
            ]:

                if col not in df_trades.columns:

                    df_trades[col] = 0


            df_trades[
                "beneficio_usd"
            ] = pd.to_numeric(
                df_trades[
                    "beneficio_usd"
                ],
                errors="coerce"
            ).fillna(0)


            df_grouped = (
                df_trades
                .groupby("fecha")
                .agg(
                    {
                        "beneficio_usd":
                            "sum",

                        "trades_cant":
                            "count"
                    }
                )
                .reset_index()
            )


            dias_ganadores = len(
                df_grouped[
                    df_grouped[
                        "beneficio_usd"
                    ] > 0
                ]
            )

            dias_perdedores = len(
                df_grouped[
                    df_grouped[
                        "beneficio_usd"
                    ] < 0
                ]
            )

        else:

            df_grouped = pd.DataFrame(
                columns=[
                    "fecha",
                    "beneficio_usd",
                    "trades_cant"
                ]
            )

            dias_ganadores = 0
            dias_perdedores = 0


        total_pnl = (
            df_trades[
                "beneficio_usd"
            ].sum()
            if not df_trades.empty
            else 0
        )


        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Resultado Neto",
            f"${total_pnl:,.2f}"
        )

        c2.metric(
            "Días Verdes 🟩",
            f"{dias_ganadores}"
        )

        c3.metric(
            "Días Rojos 🟥",
            f"{dias_perdedores}"
        )


        st.markdown("---")


        # ----------------------------------------------------
        # CALENDARIO
        # ----------------------------------------------------

        pnl_map = (
            df_grouped
            .set_index("fecha")
            ["beneficio_usd"]
            .to_dict()
            if not df_grouped.empty
            else {}
        )


        trades_map = (
            df_grouped
            .set_index("fecha")
            ["trades_cant"]
            .to_dict()
            if not df_grouped.empty
            else {}
        )


        hoy = datetime.date.today()

        mes_dias = (
            calendar
            .Calendar(firstweekday=6)
            .monthdayscalendar(
                hoy.year,
                hoy.month
            )
        )


        dias_header = [
            "Dom",
            "Lun",
            "Mar",
            "Mié",
            "Jue",
            "Vie",
            "Sáb"
        ]


        cols_header = st.columns(7)

        for i, col in enumerate(
            cols_header
        ):

            with col:

                st.markdown(
                    f"""
                    <div style="
                    text-align:center;
                    font-weight:bold;">
                    {dias_header[i]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


        for semana in mes_dias:

            cols = st.columns(7)

            for day_idx, day_num in enumerate(
                semana
            ):

                with cols[day_idx]:

                    if day_num == 0:

                        st.markdown(
                            "<div style='height:80px;'></div>",
                            unsafe_allow_html=True
                        )

                        continue


                    f_date = datetime.date(
                        hoy.year,
                        hoy.month,
                        day_num
                    )

                    f_key = str(f_date)

                    pnl_val = pnl_map.get(
                        f_key,
                        None
                    )

                    num_trades = trades_map.get(
                        f_key,
                        0
                    )


                    if pnl_val is None:

                        bg = "#161b22"
                        txt = "#ffffff"
                        pnl_html = ""

                    elif pnl_val > 0:

                        bg = "#34d399"
                        txt = "#000000"

                        pnl_html = (
                            f"<b>+${pnl_val:,.0f}</b>"
                        )

                    else:

                        bg = "#f87171"
                        txt = "#000000"

                        pnl_html = (
                            f"<b>-${abs(pnl_val):,.0f}</b>"
                        )


                    border = (
                        "2px solid #00f2fe"
                        if f_date == hoy
                        else
                        "1px solid #222"
                    )


                    box = f"""
                    <div style="
                    background:{bg};
                    color:{txt};
                    border:{border};
                    border-radius:6px;
                    padding:6px;
                    height:80px;
                    display:flex;
                    flex-direction:column;
                    justify-content:space-between;
                    ">

                    <div>
                    {day_num}
                    </div>

                    <div style="
                    text-align:center;">
                    {pnl_html}

                    <div style="
                    font-size:11px;">
                    {num_trades} trade
                    </div>

                    </div>

                    </div>
                    """

                    st.markdown(
                        box,
                        unsafe_allow_html=True
                    )


        st.markdown("---")


        # ====================================================
        # HISTORIAL
        # ====================================================

        st.markdown(
            "### 📋 Historial de Operaciones"
        )


        if not df_trades.empty:

            for _, row in df_trades.iterrows():

                trade_id = row.get(
                    "id"
                )

                pnl = float(
                    row.get(
                        "beneficio_usd",
                        0
                    )
                    or 0
                )


                titulo = (
                    f"📅 {row.get('fecha', '')} "
                    f"| 📊 {row.get('par', '')} "
                    f"| {row.get('resultado', '')} "
                    f"| PnL: ${pnl:,.2f}"
                )


                with st.expander(
                    titulo
                ):

                    # ----------------------------------------
                    # EDITOR
                    # ----------------------------------------

                    if (
                        st.session_state
                        .editing_trade_id
                        == trade_id
                    ):

                        render_editor_trade(
                            row,
                            user_id
                        )

                        continue


                    # ----------------------------------------
                    # VISTA NORMAL
                    # ----------------------------------------

                    c_det, c_before, c_after = (
                        st.columns(
                            [1.3, 2, 2]
                        )
                    )


                    with c_det:

                        st.markdown(
                            "#### ⚙️ Detalle"
                        )

                        st.markdown(
                            f"**Activo:** "
                            f"{row.get('par', 'N/A')}"
                        )

                        st.markdown(
                            f"**Dirección:** "
                            f"{row.get('direccion', 'N/A')}"
                        )

                        st.markdown(
                            f"**Entrada:** "
                            f"{row.get('precio_entrada', 0)}"
                        )

                        st.markdown(
                            f"**SL:** "
                            f"{row.get('stop_loss', 0)}"
                        )

                        st.markdown(
                            f"**TP:** "
                            f"{row.get('take_profit', 0)}"
                        )

                        st.markdown(
                            f"**R:R:** "
                            f"1 : {float(row.get('rr', 0) or 0):.2f}"
                        )

                        st.markdown(
                            f"**Emoción:** "
                            f"{row.get('emocion', 'N/A')}"
                        )

                        st.markdown(
                            f"**PnL:** "
                            f"${pnl:,.2f} USD"
                        )


                        st.markdown("---")


                        if st.button(
                            "✏️ Editar Trade",
                            key=f"edit_{trade_id}"
                        ):

                            st.session_state.editing_trade_id = (
                                trade_id
                            )

                            st.rerun()


                        if st.button(
                            "🗑️ Eliminar Trade",
                            key=f"delete_{trade_id}"
                        ):

                            if eliminar_trade_supabase(
                                trade_id,
                                user_id
                            ):

                                st.success(
                                    "Trade eliminado."
                                )

                                st.rerun()


                    with c_before:

                        st.markdown(
                            "**1️⃣ ANTES**"
                        )

                        mostrar_imagen_guardada(
                            row.get(
                                "img_before",
                                ""
                            ),
                            "Setup antes de entrar"
                        )


                    with c_after:

                        st.markdown(
                            "**2️⃣ DESPUÉS**"
                        )

                        mostrar_imagen_guardada(
                            row.get(
                                "img_after",
                                ""
                            ),
                            "Resultado después"
                        )


        else:

            st.info(
                """
                Aún no tienes trades registrados.
                Ve a **➕ Registrar Trade**.
                """
            )


        # ----------------------------------------------------
        # GRÁFICO
        # ----------------------------------------------------

        if not df_grouped.empty:

            df_grouped[
                "color_pnl"
            ] = np.where(
                df_grouped[
                    "beneficio_usd"
                ] >= 0,
                "GANANCIA",
                "PÉRDIDA"
            )


            fig_pnl = px.bar(
                df_grouped,
                x="fecha",
                y="beneficio_usd",
                color="color_pnl",
                title="PnL Diario",
                template="plotly_dark",
                color_discrete_map={
                    "GANANCIA":
                        "#00f2fe",

                    "PÉRDIDA":
                        "#f44336"
                }
            )


            fig_pnl.update_layout(
                plot_bgcolor="#0b0e14",
                paper_bgcolor="#0b0e14",
                xaxis_title="Fecha",
                yaxis_title="PnL USD"
            )


            st.plotly_chart(
                fig_pnl,
                use_container_width=True
            )


    # ========================================================
    # TAB 3 — CHAT IA
    # ========================================================

    with tab3:

        st.markdown(
            "### 💬 Chat de Auditoría de Trading con IA"
        )

        st.caption(
            "Consulta tus estadísticas y hábitos."
        )


        for message in (
            st.session_state.chat_history
        ):

            with st.chat_message(
                message["role"]
            ):

                st.markdown(
                    message["content"]
                )


        prompt = st.chat_input(
            "Escribe tu duda..."
        )


        if prompt:

            st.session_state.chat_history.append(
                {
                    "role":
                        "user",

                    "content":
                        prompt
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

                with st.spinner(
                    "Analizando..."
                ):

                    cant = len(
                        trades_db
                    )


                    if cant == 0:

                        respuesta = (
                            "Aún no tienes trades registrados."
                        )

                    else:

                        pnl = (
                            df_trades[
                                "beneficio_usd"
                            ].sum()
                        )

                        wins = len(
                            df_trades[
                                df_trades[
                                    "beneficio_usd"
                                ] > 0
                            ]
                        )

                        winrate = (
                            wins / cant * 100
                        )


                        respuesta = f"""
                        Has registrado **{cant} operaciones**.

                        Resultado acumulado:
                        **${pnl:,.2f} USD**

                        Win Rate:
                        **{winrate:.1f}%**

                        Sigue evaluando no solo el resultado,
                        sino también tu disciplina emocional.
                        """


                    st.markdown(
                        respuesta
                    )


                    st.session_state.chat_history.append(
                        {
                            "role":
                                "assistant",

                            "content":
                                respuesta
                        }
                    )


    # ========================================================
    # TAB 4 — LOTAJE
    # ========================================================

    with tab4:

        st.markdown(
            "### 🧮 Calculadora de Tamaño de Posición"
        )

        balance = st.number_input(
            "Balance USD",
            value=float(
                st.session_state.capital_actual
            ),
            step=500.0
        )

        porcentaje_riesgo = st.number_input(
            "Riesgo por Trade (%)",
            value=1.0,
            step=0.25
        )

        pips_sl = st.number_input(
            "Stop Loss (Pips / Puntos)",
            value=20.0,
            step=1.0
        )


        monto_riesgo = (
            balance
            * porcentaje_riesgo
            / 100
        )


        lotaje = (
            monto_riesgo
            / (pips_sl * 10)
            if pips_sl > 0
            else 0
        )


        c1, c2 = st.columns(2)

        c1.metric(
            "Riesgo Máximo",
            f"${monto_riesgo:,.2f}"
        )

        c2.metric(
            "Lotes Estimados",
            f"{lotaje:.2f}"
        )


        st.info(
            """
            ⚠️ La equivalencia de lotes cambia
            según instrumento y broker.
            """
        )


    # ========================================================
    # TAB 5 — ANÁLISIS IA
    # ========================================================

    with tab5:

        st.markdown(
            "### 🤖 Auditoría Visual"
        )

        chart_audit = st.file_uploader(
            "Subir gráfico",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="audit_visual"
        )


        if chart_audit:

            st.image(
                chart_audit,
                use_container_width=True
            )


            if st.button(
                "🔍 Auditar Entrada con IA"
            ):

                with st.spinner(
                    "Analizando..."
                ):

                    extracted = (
                        analizar_captura_tradingview(
                            chart_audit.getvalue()
                        )
                    )


                    if extracted:

                        st.success(
                            "Análisis visual realizado."
                        )

                        st.json(
                            extracted
                        )

                    else:

                        st.warning(
                            "No se pudo analizar."
                        )


    # ========================================================
    # TAB 6 — PROYECCIONES
    # ========================================================

    with tab6:

        st.markdown(
            "### 📈 Proyección de Capital"
        )


        trades_mes = st.slider(
            "Trades por Mes",
            5,
            50,
            15
        )

        win_rate_est = st.slider(
            "Win Rate Estimado (%)",
            30,
            90,
            55
        )

        ganancia_prom = st.number_input(
            "Ganancia Promedio WIN ($)",
            value=200.0,
            step=25.0
        )

        perdida_prom = st.number_input(
            "Pérdida Promedio LOSS ($)",
            value=100.0,
            step=25.0
        )


        capital = (
            st.session_state.capital_actual
        )

        proyeccion = []


        for m in range(1, 13):

            ganadores = (
                trades_mes
                * win_rate_est
                / 100
            )

            perdedores = (
                trades_mes
                - ganadores
            )

            pnl_mes = (
                ganadores
                * ganancia_prom
                -
                perdedores
                * perdida_prom
            )

            capital += pnl_mes

            proyeccion.append(
                {
                    "Mes":
                        f"Mes {m}",

                    "Capital":
                        capital
                }
            )


        df_proy = pd.DataFrame(
            proyeccion
        )


        st.metric(
            "Capital a 12 Meses",
            f"${capital:,.2f}"
        )


        fig = px.line(
            df_proy,
            x="Mes",
            y="Capital",
            markers=True,
            title="Proyección 12 Meses",
            template="plotly_dark"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # ========================================================
    # TAB 7 — PSICOTRADING
    # ========================================================

    with tab7:

        st.markdown(
            "### 📓 Bitácora de Psicotrading"
        )

        st.caption(
            """
            Registra tus pensamientos,
            impulsos y disciplina.
            """
        )


        reflexion = st.text_area(
            "Reflexión",
            height=180,
            placeholder=(
                "¿Cómo fue tu semana?"
            )
        )


        if st.button(
            "💾 Guardar Reflexión"
        ):

            st.success(
                "🧠 Reflexión guardada en esta sesión."
            )


    # ========================================================
    # TAB 8 — DASHBOARD
    # ========================================================

    with tab8:

        st.markdown(
            "### 📊 Dashboard Operativo"
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

            winrate = (
                wins / total * 100
                if total
                else 0
            )

            dias = len(
                df_trades[
                    "fecha"
                ].unique()
            )

        else:

            wins = 0
            losses = 0
            pnl = 0
            winrate = 0
            dias = 0


        m1, m2, m3, m4 = st.columns(4)


        m1.metric(
            "PnL Acumulado",
            f"${pnl:,.2f}"
        )

        m2.metric(
            "Win Rate",
            f"{winrate:.1f}%"
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
                color="emocion",
                title="PnL por Activo y Emoción",
                template="plotly_dark"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


            columnas_mostrar = [
                "fecha",
                "par",
                "resultado",
                "beneficio_usd",
                "emocion"
            ]


            columnas_disponibles = [
                c
                for c in columnas_mostrar
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
                "Registra tu primer trade."
            )


# ============================================================
# 19. FLUJO PRINCIPAL
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
