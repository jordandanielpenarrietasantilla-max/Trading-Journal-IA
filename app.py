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
import re

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
# 2. CONFIGURACIÓN DE SERVICIOS
# ============================================================

LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"

BINANCE_PAY_ID = "JORDAN_SANTI9"

LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"

# ------------------------------------------------------------
# PAGO CON TARJETA
# ------------------------------------------------------------
# IMPORTANTE:
# Sustituye este enlace por tu checkout real de Stripe,
# Mercado Pago, PayPal, etc.
#
# No inventamos una integración de tarjeta sin tus credenciales.
# El botón funcionará cuando coloques aquí tu checkout.
# ------------------------------------------------------------

LINK_PAGO_TARJETA_MENSUAL = ""
LINK_PAGO_TARJETA_ANUAL = ""


SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    "https://lyzvcbjpoydeckxtbcq.supabase.co"
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    "sb_publishable_HIo0YXn-kJUr7HuNZFNfjQ_JBncowE0"
)

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)


# ============================================================
# 3. CLIENTE SUPABASE
# ============================================================

@st.cache_resource
def get_supabase_client() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ============================================================
# 4. LISTA DE ACTIVOS
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
# 5. ESTADO DE SESIÓN
# ============================================================

DEFAULT_REGLAS = (
    "• Acepta la pérdida antes de entrar.\n"
    "• Corta pérdidas rápido.\n"
    "• Deja correr los ganadores.\n"
    "• Máximo 2 operaciones perdedoras por día."
)


def inicializar_estado():

    valores = {
        "authenticated": False,
        "user": None,
        "chat_history": [],
        "nombre_trader": "Trader Pro",
        "capital_actual": 10000.0,
        "capital_meta": 15000.0,
        "reglas_disciplina": DEFAULT_REGLAS,
        "auto_entry": 0.0,
        "auto_sl": 0.0,
        "auto_tp": 0.0,
        "reflexion_semanal": ""
    }

    for key, value in valores.items():
        if key not in st.session_state:
            st.session_state[key] = value


inicializar_estado()


# ============================================================
# 6. CSS
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
        color: #f0f3fa;
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
        border-right: 1px solid rgba(0, 210, 255, 0.2) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #121721 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.5) !important;
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
        border: 1px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
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
            0px 4px 15px
            rgba(0, 210, 255, 0.3) !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(
            135deg,
            #00d2ff 0%,
            #2962ff 100%
        ) !important;
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
            0px 0px 20px
            rgba(240,185,11,0.2);
    }

    .payment-card {
        background-color: #121721;
        border: 1px solid rgba(0,242,254,0.25);
        border-radius: 12px;
        padding: 20px;
        min-height: 220px;
    }

    .profile-box {
        background-color: #121721;
        border: 1px solid rgba(0,242,254,0.25);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
    }

    .trade-card {
        background-color: #121721;
        border: 1px solid rgba(0,242,254,0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }

    </style>
    """

    st.markdown(css, unsafe_allow_html=True)


aplicar_estilos()


# ============================================================
# 7. FUNCIONES DE IMÁGENES
# ============================================================

def limpiar_base64(valor):

    if not valor:
        return None

    if not isinstance(valor, str):
        return None

    valor = valor.strip()

    if not valor:
        return None

    # Elimina posibles prefijos repetidos
    valor = re.sub(
        r"^data:image/[^;]+;base64,",
        "",
        valor,
        flags=re.IGNORECASE
    )

    # Si accidentalmente se guardó otro prefijo
    if "base64," in valor[:100]:
        valor = valor.split("base64,", 1)[1]

    return valor


def base64_a_bytes(valor):

    limpio = limpiar_base64(valor)

    if not limpio:
        return None

    try:
        return base64.b64decode(
            limpio,
            validate=False
        )
    except Exception:
        return None


def bytes_a_base64_datauri(
    image_bytes,
    mime_type="image/jpeg"
):

    if not image_bytes:
        return ""

    try:

        encoded = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        return f"data:{mime_type};base64,{encoded}"

    except Exception:
        return ""


def procesar_imagen_b64(
    uploaded_file,
    max_size=(800, 600)
):

    if uploaded_file is None:
        return ""

    try:

        image = Image.open(
            uploaded_file
        ).convert("RGB")

        image.thumbnail(max_size)

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=75,
            optimize=True
        )

        return bytes_a_base64_datauri(
            buffer.getvalue(),
            "image/jpeg"
        )

    except Exception as e:

        st.error(
            f"Error al procesar imagen: {e}"
        )

        return ""


def mostrar_avatar(foto_b64):

    if not foto_b64:
        st.markdown(
            """
            <div style="
                width:70px;
                height:70px;
                border-radius:50%;
                background:#161b22;
                border:2px solid #00f2fe;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:32px;
            ">
            👤
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    image_bytes = base64_a_bytes(
        foto_b64
    )

    if image_bytes:

        try:

            image = Image.open(
                io.BytesIO(image_bytes)
            )

            st.image(
                image,
                width=70
            )

            return

        except Exception:
            pass

    st.markdown(
        """
        <div style="
            width:70px;
            height:70px;
            border-radius:50%;
            background:#161b22;
            border:2px solid #ff5252;
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


# ============================================================
# 8. BASE DE DATOS
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
            f"Error cargando operaciones: {e}"
        )

        return []


def guardar_trade_supabase(
    user_id,
    trade_data
):

    try:

        client = get_supabase_client()

        data = dict(trade_data)

        data["user_id"] = user_id

        client.table(
            "trades"
        ).insert(data).execute()

        return True

    except Exception as e:

        st.error(
            f"Error guardando operación: {e}"
        )

        return False


def eliminar_trade_supabase(
    trade_id
):

    try:

        client = get_supabase_client()

        client.table(
            "trades"
        ).delete().eq(
            "id",
            trade_id
        ).execute()

        return True

    except Exception as e:

        st.error(
            f"Error eliminando operación: {e}"
        )

        return False


# ============================================================
# 9. IA — VISIÓN
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

Busca la herramienta de posición
Risk/Reward y extrae:

- Entry
- Stop Loss
- Take Profit

Devuelve ÚNICAMENTE JSON válido:

{
  "entry": 0.0,
  "sl": 0.0,
  "tp": 0.0
}

Si no encuentras algún valor,
usa 0.0.

No agregues explicación.
"""

    payload = {

        "model":
            "openai/gpt-4o-mini",

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

                            "url":
                                "data:image/png;base64,"
                                + b64_img
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

        data = response.json()

        content = (
            data["choices"][0]
            ["message"]["content"]
        )

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(content)

    except Exception as e:

        st.error(
            f"Error de IA: {e}"
        )

        return None


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

    if (
        user_email.lower()
        == "jordandanielpenarrietasantilla@gmail.com"
    ):

        return True, "Creador / Admin 👑", 99999

    metadata = getattr(
        user,
        "user_metadata",
        {}
    ) or {}

    if metadata.get(
        "es_vip",
        False
    ):

        return True, "Acceso PRO 💎", 999

    # Permite activar manualmente PRO
    # desde metadata
    if metadata.get(
        "subscription_active",
        False
    ):

        return True, "Acceso PRO 💎", 999

    created_at = getattr(
        user,
        "created_at",
        None
    )

    try:

        if created_at:

            fecha_registro = (
                datetime.datetime
                .fromisoformat(
                    str(created_at)
                    .replace("Z", "+00:00")
                )
                .date()
            )

        else:

            fecha_registro = (
                datetime.date.today()
            )

    except Exception:

        fecha_registro = (
            datetime.date.today()
        )

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
# 11. PAYWALL
# ============================================================

def render_paywall():

    st.markdown(
        "## 🔒 Tu período de prueba ha expirado"
    )

    st.markdown(
        """
        Activa tu acceso para continuar
        utilizando el diario de trading,
        Track Record y herramientas de IA.
        """
    )

    st.markdown("### 💳 Elige tu método de pago")

    c1, c2, c3 = st.columns(3)

    # --------------------------------------------------------
    # BINANCE
    # --------------------------------------------------------

    with c1:

        st.markdown(
            f"""
            <div class="payment-card">

            <h3>🟡 Binance Pay</h3>

            <h2>$5 USD</h2>

            <p>
            Suscripción mensual
            </p>

            <p>
            Después $2.50 USD/mes
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.link_button(
            "🟡 Pagar con Binance Pay",
            LINK_BINANCE_INSCRIPCION,
            use_container_width=True
        )

    # --------------------------------------------------------
    # TARJETA
    # --------------------------------------------------------

    with c2:

        st.markdown(
            """
            <div class="payment-card">

            <h3>💳 Tarjeta</h3>

            <h2>$5 USD</h2>

            <p>
            Visa / Mastercard /
            Débito / Crédito
            </p>

            <p>
            Pago seguro mediante
            checkout externo.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        if LINK_PAGO_TARJETA_MENSUAL:

            st.link_button(
                "💳 Pagar con Tarjeta",
                LINK_PAGO_TARJETA_MENSUAL,
                use_container_width=True
            )

        else:

            st.warning(
                "Checkout de tarjeta pendiente de configurar."
            )

    # --------------------------------------------------------
    # ANUAL
    # --------------------------------------------------------

    with c3:

        st.markdown(
            """
            <div class="payment-card">

            <h3>💎 Plan Anual</h3>

            <h2>$20 USD</h2>

            <p>
            Acceso durante 1 año.
            </p>

            <p>
            Pago único.
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.link_button(
            "💎 Pagar Plan Anual",
            LINK_BINANCE_ANUAL,
            use_container_width=True
        )

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "### 📲 Pago directo / renovación"
        )

        st.code(
            f"Binance Pay ID: {BINANCE_PAY_ID}",
            language="text"
        )

        st.link_button(
            "🔄 Renovación mensual $2.50 USDT",
            LINK_BINANCE_RECURRENTE,
            use_container_width=True
        )

    with c2:

        st.markdown(
            "### ✈️ Confirmar pago"
        )

        st.link_button(
            "💬 Enviar comprobante / soporte",
            LINK_TELEGRAM_SOPORTE,
            use_container_width=True
        )


# ============================================================
# 12. AUTENTICACIÓN
# ============================================================

def render_auth():

    c1, c2 = st.columns(
        [1.2, 1]
    )

    with c1:

        st.markdown(
            "# ⚡ AI Trading Journal & Auditor"
        )

        st.markdown(
            """
            Tu centro de control para:

            - 📊 Track Record
            - 🧠 Psicotrading
            - 🤖 Auditoría IA
            - 📈 Proyecciones
            - 🎯 Disciplina
            """
        )

        st.info(
            "Regístrate y disfruta de 3 días de prueba."
        )

    with c2:

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

        # ----------------------------------------------------
        # LOGIN
        # ----------------------------------------------------

        with tab_login:

            st.markdown(
                "### Ingresa a tu cuenta"
            )

            email = st.text_input(
                "Correo electrónico",
                key="login_email"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                key="login_password"
            )

            if st.button(
                "Ingresar",
                key="login_button"
            ):

                if not email or not password:

                    st.warning(
                        "Completa ambos campos."
                    )

                else:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        result = (
                            client.auth
                            .sign_in_with_password(
                                {
                                    "email": email,
                                    "password": password
                                }
                            )
                        )

                        st.session_state.user = (
                            result.user
                        )

                        st.session_state.authenticated = True

                        st.success(
                            "Inicio de sesión correcto."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Error al iniciar sesión: {e}"
                        )

        # ----------------------------------------------------
        # REGISTER
        # ----------------------------------------------------

        with tab_register:

            st.markdown(
                "### Crear cuenta"
            )

            email = st.text_input(
                "Correo electrónico",
                key="register_email"
            )

            password = st.text_input(
                "Crea tu contraseña",
                type="password",
                key="register_password"
            )

            if st.button(
                "Crear Cuenta y Probar",
                key="register_button"
            ):

                if not email or not password:

                    st.warning(
                        "Completa ambos campos."
                    )

                elif len(password) < 6:

                    st.warning(
                        "La contraseña debe tener al menos 6 caracteres."
                    )

                else:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        client.auth.sign_up(
                            {
                                "email": email,
                                "password": password
                            }
                        )

                        st.success(
                            """
                            ¡Cuenta creada!

                            Si Supabase tiene activada
                            la confirmación por correo,
                            revisa tu email antes de iniciar sesión.
                            """
                        )

                    except Exception as e:

                        st.error(
                            f"Error al registrar: {e}"
                        )

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

        with tab_reset:

            st.markdown(
                "### Recuperar contraseña"
            )

            email = st.text_input(
                "Correo registrado",
                key="reset_email"
            )

            if st.button(
                "Enviar enlace",
                key="reset_button"
            ):

                if not email:

                    st.warning(
                        "Ingresa tu correo."
                    )

                else:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        app_url = (
                            "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                        )

                        client.auth.reset_password_for_email(
                            email,
                            {
                                "redirectTo": app_url
                            }
                        )

                        st.success(
                            "Revisa tu correo electrónico."
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


# ============================================================
# 13. SIDEBAR
# ============================================================

def render_sidebar(
    estado_sub
):

    with st.sidebar:

        # ----------------------------------------------------
        # PERFIL
        # ----------------------------------------------------

        st.markdown(
            "### 👤 Perfil Trader"
        )

        user = (
            st.session_state.user
        )

        user_email = (
            getattr(
                user,
                "email",
                None
            )
            if user
            else "trader@ejemplo.com"
        )

        metadata = (
            getattr(
                user,
                "user_metadata",
                {}
            )
            or {}
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
            None
        )

        # ----------------------------------------------------
        # AQUÍ ESTÁ LA CORRECCIÓN PRINCIPAL
        #
        # NO usamos:
        #
        # st.markdown("<img src='...base64...'>")
        #
        # porque eso provocaba que apareciera el Base64.
        #
        # Usamos st.image() mediante mostrar_avatar().
        # ----------------------------------------------------

        c_img, c_info = st.columns(
            [1, 2]
        )

        with c_img:

            mostrar_avatar(
                foto_b64
            )

        with c_info:

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
                f"⏳ {estado_sub}"
            )

        else:

            st.warning(
                f"🛑 {estado_sub}"
            )

        # ----------------------------------------------------
        # EDITAR PERFIL
        # ----------------------------------------------------

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

            if foto_subida:

                st.image(
                    foto_subida,
                    width=120
                )

            if st.button(
                "💾 Guardar Cambios",
                key="save_profile"
            ):

                try:

                    nueva_foto = foto_b64

                    if foto_subida:

                        nueva_foto = (
                            procesar_imagen_b64(
                                foto_subida,
                                max_size=(500, 500)
                            )
                        )

                    client = (
                        get_supabase_client()
                    )

                    response = (
                        client.auth
                        .update_user(
                            {
                                "data": {
                                    "username":
                                        input_nombre,

                                    "avatar_b64":
                                        nueva_foto
                                }
                            }
                        )
                    )

                    st.session_state.user = (
                        response.user
                    )

                    st.session_state.nombre_trader = (
                        input_nombre
                    )

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error guardando perfil: {e}"
                    )

        st.markdown("---")

        # ----------------------------------------------------
        # META
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        cap_actual = float(
            st.session_state.capital_actual
        )

        cap_meta = float(
            st.session_state.capital_meta
        )

        progreso = (
            min(
                1.0,
                max(
                    0.0,
                    cap_actual / cap_meta
                )
            )
            if cap_meta > 0
            else 0
        )

        st.markdown(
            f"""
            **Capital:** ${cap_actual:,.2f}
            /
            ${cap_meta:,.2f}
            """
        )

        st.progress(
            progreso
        )

        with st.expander(
            "🔧 Configuración Meta"
        ):

            st.session_state.capital_actual = (
                st.number_input(
                    "Capital Actual ($)",
                    value=cap_actual,
                    step=100.0
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta ($)",
                    value=cap_meta,
                    step=500.0
                )
            )

        st.markdown("---")

        # ----------------------------------------------------
        # HORA / SESIONES
        # ----------------------------------------------------

        st.markdown(
            "### ⏰ Hora Local & Sesiones"
        )

        st.components.v1.html(
            """
            <div id="clock"
            style="
                font-family:monospace;
                font-size:18px;
                font-weight:bold;
                color:#00f2fe;
                background:#161b22;
                border:1px solid rgba(0,210,255,.4);
                border-radius:8px;
                padding:7px;
                text-align:center;
            ">
            00:00:00
            </div>

            <script>

            function updateClock() {

                const now = new Date();

                document.getElementById(
                    "clock"
                ).innerHTML =
                    now.toLocaleTimeString();

            }

            updateClock();

            setInterval(
                updateClock,
                1000
            );

            </script>
            """,
            height=55
        )

        utc_hour = (
            datetime.datetime.utcnow().hour
        )

        london_open = (
            7 <= utc_hour <= 15
        )

        ny_open = (
            12 <= utc_hour <= 20
        )

        london = (
            "🟢 ABIERTO"
            if london_open
            else "🔴 CERRADO"
        )

        new_york = (
            "🟢 ABIERTO"
            if ny_open
            else "🔴 CERRADO"
        )

        st.markdown(
            f"**🇬🇧 Londres:** {london}"
        )

        st.markdown(
            f"**🇺🇸 Nueva York:** {new_york}"
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

            reglas = st.text_area(
                "Reglas personalizadas",
                value=st.session_state.reglas_disciplina,
                height=150,
                key="rules_editor"
            )

            if st.button(
                "Guardar Reglas",
                key="save_rules"
            ):

                st.session_state.reglas_disciplina = (
                    reglas
                )

                st.success(
                    "Reglas actualizadas."
                )

                st.rerun()

        st.markdown(
            st.session_state.reglas_disciplina
        )

        st.markdown("---")

        # ----------------------------------------------------
        # LOGOUT
        # ----------------------------------------------------

        if st.button(
            "🚪 Cerrar Sesión",
            key="logout"
        ):

            try:

                client = (
                    get_supabase_client()
                )

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

    user = st.session_state.user

    tiene_acceso, estado_sub, dias_restantes = (
        evaluar_suscripcion(user)
    )

    render_sidebar(
        estado_sub
    )

    if not tiene_acceso:

        render_paywall()

        return

    user_id = user.id

    trades_db = (
        cargar_trades_usuario(
            user_id
        )
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
    # TAB 1
    # ========================================================

    with tab1:

        st.info(
            """
            💡 Sube una captura de TradingView
            con la herramienta Risk/Reward
            para intentar completar automáticamente
            Entry, Stop Loss y Take Profit.
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
                    "jpeg"
                ],
                key="upload_before"
            )

            upload_after = st.file_uploader(
                "2️⃣ Screenshot DESPUÉS",
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

                bytes_before = (
                    upload_before.getvalue()
                )

                img_before_b64 = (
                    bytes_a_base64_datauri(
                        bytes_before,
                        "image/png"
                    )
                )

                st.image(
                    upload_before,
                    caption="Trade SETUP — Antes",
                    use_container_width=True
                )

                if st.button(
                    "🧠 Escanear SETUP con IA",
                    key="scan_setup"
                ):

                    with st.spinner(
                        "Analizando gráfico..."
                    ):

                        extracted = (
                            analizar_captura_tradingview(
                                bytes_before
                            )
                        )

                        if extracted:

                            st.session_state.auto_entry = float(
                                extracted.get(
                                    "entry",
                                    0
                                ) or 0
                            )

                            st.session_state.auto_sl = float(
                                extracted.get(
                                    "sl",
                                    0
                                ) or 0
                            )

                            st.session_state.auto_tp = float(
                                extracted.get(
                                    "tp",
                                    0
                                ) or 0
                            )

                            st.success(
                                "Valores encontrados."
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "No se pudieron extraer los valores."
                            )

            if upload_after:

                bytes_after = (
                    upload_after.getvalue()
                )

                img_after_b64 = (
                    bytes_a_base64_datauri(
                        bytes_after,
                        "image/png"
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
                key="trade_pnl"
            )

        with col1:

            st.markdown(
                "### 📝 Parámetros"
            )

            fecha_op = st.date_input(
                "Fecha",
                datetime.date.today(),
                key="trade_date"
            )

            a, b = st.columns(2)

            with a:

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

            with b:

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
                    "¿Qué sentiste antes y después?"
                ),
                key="trade_notes"
            )

            if st.button(
                "💾 Guardar Trade",
                key="save_trade"
            ):

                nuevo_trade = {

                    "fecha":
                        str(fecha_op),

                    "par":
                        par,

                    "resultado":
                        resultado,

                    "emocion":
                        emocion,

                    "beneficio_usd":
                        float(monto_pnl),

                    "trades_cant":
                        1,

                    "img_before":
                        img_before_b64,

                    "img_after":
                        img_after_b64,

                    "direccion":
                        direccion,

                    "precio_entrada":
                        float(precio_entrada),

                    "stop_loss":
                        float(stop_loss),

                    "take_profit":
                        float(take_profit),

                    "rr":
                        float(rr),

                    "timeframe":
                        timeframe,

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
                        "¡Trade guardado correctamente!"
                    )

                    st.rerun()


    # ========================================================
    # TAB 2
    # ========================================================

    with tab2:

        st.markdown(
            "### 📅 Track Record & Calendario PnL"
        )

        if not df_trades.empty:

            df_trades["beneficio_usd"] = pd.to_numeric(
                df_trades["beneficio_usd"],
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

        dias_ganadores = (
            len(
                df_grouped[
                    df_grouped["beneficio_usd"] > 0
                ]
            )
            if not df_grouped.empty
            else 0
        )

        dias_perdedores = (
            len(
                df_grouped[
                    df_grouped["beneficio_usd"] < 0
                ]
            )
            if not df_grouped.empty
            else 0
        )

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Resultado Neto",
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

        semanas = (
            calendar
            .Calendar(
                firstweekday=6
            )
            .monthdayscalendar(
                hoy.year,
                hoy.month
            )
        )

        headers = [
            "Dom",
            "Lun",
            "Mar",
            "Mié",
            "Jue",
            "Vie",
            "Sáb"
        ]

        cols = st.columns(7)

        for i, col in enumerate(cols):

            with col:

                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        font-weight:bold;
                    ">
                    {headers[i]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        for semana in semanas:

            cols = st.columns(7)

            for idx, day in enumerate(semana):

                with cols[idx]:

                    if day == 0:

                        st.write("")

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

                    trades_count = trades_map.get(
                        key,
                        0
                    )

                    if pnl is None:

                        bg = "#161b22"
                        fg = "#ffffff"
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

                    borde = (
                        "2px solid #00f2fe"
                        if fecha == hoy
                        else "1px solid #252b35"
                    )

                    st.markdown(
                        f"""
                        <div style="
                            background:{bg};
                            color:{fg};
                            border:{borde};
                            border-radius:7px;
                            padding:7px;
                            min-height:80px;
                        ">

                        <b>{day}</b>

                        <div style="
                            text-align:center;
                            margin-top:15px;
                            font-size:16px;
                            font-weight:bold;
                        ">
                        {texto}
                        </div>

                        <div style="
                            text-align:center;
                            font-size:11px;
                        ">
                        {trades_count} trade
                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # ----------------------------------------------------
        # HISTORIAL
        # ----------------------------------------------------

        st.markdown(
            "### 📋 Historial Detallado"
        )

        if df_trades.empty:

            st.info(
                "Aún no tienes trades registrados."
            )

        else:

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
                    f"📅 {row.get('fecha')} | "
                    f"📊 {row.get('par')} | "
                    f"{row.get('resultado')} | "
                    f"${pnl:,.2f}"
                )

                with st.expander(
                    titulo
                ):

                    a, b, c = st.columns(
                        [1.3, 2, 2]
                    )

                    with a:

                        st.markdown(
                            "#### ⚙️ Operación"
                        )

                        st.write(
                            f"**Dirección:** "
                            f"{row.get('direccion', 'N/A')}"
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
                            f"**RR:** "
                            f"1 : {row.get('rr', 0)}"
                        )

                        st.write(
                            f"**Timeframe:** "
                            f"{row.get('timeframe', 'N/A')}"
                        )

                        st.write(
                            f"**Emoción:** "
                            f"{row.get('emocion', 'N/A')}"
                        )

                        st.write(
                            f"**PnL:** "
                            f"${pnl:,.2f}"
                        )

                        notas = row.get(
                            "notas_emocionales",
                            ""
                        )

                        if notas:

                            st.write(
                                f"**Notas:** {notas}"
                            )

                        if st.button(
                            "🗑️ Eliminar Trade",
                            key=f"delete_{trade_id}"
                        ):

                            if eliminar_trade_supabase(
                                trade_id
                            ):

                                st.success(
                                    "Trade eliminado."
                                )

                                st.rerun()

                    with b:

                        st.markdown(
                            "**1️⃣ ANTES**"
                        )

                        img_before = row.get(
                            "img_before"
                        )

                        if img_before:

                            image_bytes = (
                                base64_a_bytes(
                                    img_before
                                )
                            )

                            if image_bytes:

                                st.image(
                                    image_bytes,
                                    use_container_width=True
                                )

                            else:

                                st.caption(
                                    "Captura no disponible."
                                )

                        else:

                            st.caption(
                                "Sin captura."
                            )

                    with c:

                        st.markdown(
                            "**2️⃣ DESPUÉS**"
                        )

                        img_after = row.get(
                            "img_after"
                        )

                        if img_after:

                            image_bytes = (
                                base64_a_bytes(
                                    img_after
                                )
                            )

                            if image_bytes:

                                st.image(
                                    image_bytes,
                                    use_container_width=True
                                )

                            else:

                                st.caption(
                                    "Captura no disponible."
                                )

                        else:

                            st.caption(
                                "Sin captura."
                            )

        # ----------------------------------------------------
        # GRÁFICO
        # ----------------------------------------------------

        if not df_grouped.empty:

            chart_df = (
                df_grouped.copy()
            )

            chart_df["tipo"] = np.where(
                chart_df["beneficio_usd"] >= 0,
                "GANANCIA",
                "PÉRDIDA"
            )

            fig = px.bar(
                chart_df,
                x="fecha",
                y="beneficio_usd",
                color="tipo",
                title="PnL Diario",
                template="plotly_dark"
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
    # TAB 3 — CHAT IA
    # ========================================================

    with tab3:

        st.markdown(
            "### 💬 Chat de Auditoría con IA"
        )

        st.caption(
            "Consulta tus estadísticas y disciplina."
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
            "Escribe tu pregunta..."
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

            with st.chat_message("user"):

                st.markdown(
                    prompt
                )

            with st.chat_message(
                "assistant"
            ):

                if df_trades.empty:

                    respuesta = (
                        "Todavía no tienes "
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

                    winrate = (
                        wins / total * 100
                        if total
                        else 0
                    )

                    respuesta = f"""
### 🧠 Auditoría rápida

Has registrado **{total} trades**.

- 🟢 Ganadores: **{wins}**
- 🔴 Perdedores: **{losses}**
- 📊 Win Rate: **{winrate:.1f}%**
- 💰 PnL acumulado: **${pnl:,.2f}**

Tu siguiente objetivo debería ser identificar
si las pérdidas están relacionadas con
FOMO, venganza, sobreoperación o incumplimiento
de tus reglas.
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
    # TAB 4 — LOTES
    # ========================================================

    with tab4:

        st.markdown(
            "### 🧮 Calculadora de Tamaño de Posición"
        )

        a, b = st.columns(2)

        with a:

            balance = st.number_input(
                "Balance ($)",
                value=float(
                    st.session_state.capital_actual
                ),
                step=500.0,
                key="lot_balance"
            )

            riesgo_pct = st.number_input(
                "Riesgo por Trade (%)",
                value=1.0,
                step=0.25,
                key="lot_risk"
            )

            distancia_sl = st.number_input(
                "Distancia SL",
                value=20.0,
                step=1.0,
                key="lot_sl"
            )

        with b:

            riesgo_usd = (
                balance
                * riesgo_pct
                / 100
            )

            lotaje = (
                riesgo_usd
                / (distancia_sl * 10)
                if distancia_sl > 0
                else 0
            )

            st.metric(
                "Riesgo máximo",
                f"${riesgo_usd:,.2f}"
            )

            st.metric(
                "Lotes estimados",
                f"{lotaje:.2f}"
            )

            st.info(
                "La equivalencia exacta cambia "
                "según instrumento y broker."
            )


    # ========================================================
    # TAB 5 — ANÁLISIS IA
    # ========================================================

    with tab5:

        st.markdown(
            "### 🤖 Auditoría Visual"
        )

        st.caption(
            "Sube tu gráfico para una segunda opinión."
        )

        chart = st.file_uploader(
            "Gráfico",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="visual_audit"
        )

        if chart:

            st.image(
                chart,
                use_container_width=True
            )

            if st.button(
                "🔍 Auditar Entrada",
                key="audit_button"
            ):

                if not OPENROUTER_API_KEY:

                    st.warning(
                        "Configura OPENROUTER_API_KEY "
                        "en Secrets."
                    )

                else:

                    with st.spinner(
                        "Analizando gráfico..."
                    ):

                        result = (
                            analizar_captura_tradingview(
                                chart.getvalue()
                            )
                        )

                        if result:

                            st.success(
                                "Análisis visual completado."
                            )

                            st.json(
                                result
                            )

                        else:

                            st.warning(
                                "No se pudo analizar la imagen."
                            )


    # ========================================================
    # TAB 6 — PROYECCIÓN
    # ========================================================

    with tab6:

        st.markdown(
            "### 📈 Proyección de Capital"
        )

        a, b = st.columns(2)

        with a:

            trades_mes = st.slider(
                "Trades por mes",
                5,
                50,
                15
            )

            win_rate = st.slider(
                "Win Rate estimado (%)",
                30,
                90,
                55
            )

        with b:

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
                * win_rate
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
                    "Mes":
                        f"Mes {mes}",

                    "Capital":
                        capital
                }
            )

        df_proy = pd.DataFrame(
            datos
        )

        st.metric(
            "Capital estimado a 12 meses",
            f"${capital:,.2f}"
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


    # ========================================================
    # TAB 7 — PSICOTRADING
    # ========================================================

    with tab7:

        st.markdown(
            "### 📓 Diario & Psicotrading"
        )

        reflexion = st.text_area(
            "Reflexión semanal",
            value=st.session_state.reflexion_semanal,
            height=220,
            placeholder=(
                "¿Qué hiciste bien?\n"
                "¿Qué incumpliste?\n"
                "¿Tuviste FOMO?\n"
                "¿Respetaste tus SL?\n"
                "¿Operaste por venganza?"
            )
        )

        if st.button(
            "💾 Guardar Reflexión",
            key="save_reflection"
        ):

            st.session_state.reflexion_semanal = (
                reflexion
            )

            st.success(
                "Reflexión guardada en esta sesión."
            )


    # ========================================================
    # TAB 8 — DASHBOARD
    # ========================================================

    with tab8:

        st.markdown(
            "### 📊 Dashboard Operativo"
        )

        total_trades = len(
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
                wins
                / total_trades
                * 100
                if total_trades
                else 0
            )

            dias_operados = (
                df_trades["fecha"]
                .nunique()
            )

        else:

            wins = 0
            losses = 0
            pnl = 0
            win_rate = 0
            dias_operados = 0

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "PnL Acumulado",
            f"${pnl:,.2f}"
        )

        m2.metric(
            "Win Rate",
            f"{win_rate:.1f}%"
        )

        m3.metric(
            "Trades",
            total_trades
        )

        m4.metric(
            "Días Operados",
            dias_operados
        )

        st.markdown("---")

        if not df_trades.empty:

            st.markdown(
                "#### 📊 PnL por Activo"
            )

            fig = px.bar(
                df_trades,
                x="par",
                y="beneficio_usd",
                color="resultado",
                template="plotly_dark",
                title="Resultado por Activo"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.markdown(
                "#### 🧠 Resultado por Emoción"
            )

            emotion_df = (
                df_trades
                .groupby("emocion")
                ["beneficio_usd"]
                .sum()
                .reset_index()
            )

            fig2 = px.bar(
                emotion_df,
                x="emocion",
                y="beneficio_usd",
                template="plotly_dark",
                title="PnL según Estado Emocional"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            st.markdown(
                "#### 📋 Trades"
            )

            columnas = [
                "fecha",
                "par",
                "direccion",
                "timeframe",
                "resultado",
                "beneficio_usd",
                "emocion",
                "rr"
            ]

            columnas_existentes = [
                col
                for col in columnas
                if col in df_trades.columns
            ]

            st.dataframe(
                df_trades[
                    columnas_existentes
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Registra tu primer trade "
                "para desbloquear las métricas."
            )


# ============================================================
# 15. FLUJO PRINCIPAL
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
