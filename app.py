````python
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
# 2. CONFIGURACIÓN SUPABASE / OPENROUTER
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
    "sb_publishable_HIo0YXn-kJUr7HuNZFNfjQ_JBncowE0"
)

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)


def get_supabase_client() -> Client:
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ============================================================
# 3. ESTADO DE SESIÓN
# ============================================================

DEFAULT_RULES = """• Acepta la pérdida antes de entrar.
• Corta pérdidas rápido.
• Deja correr los ganadores.
• Máximo 2 operaciones perdedoras por día."""

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "user" not in st.session_state:
    st.session_state.user = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "nombre_trader" not in st.session_state:
    st.session_state.nombre_trader = "Trader Pro"

if "capital_actual" not in st.session_state:
    st.session_state.capital_actual = 10000.0

if "capital_meta" not in st.session_state:
    st.session_state.capital_meta = 15000.0

if "reglas_disciplina" not in st.session_state:
    st.session_state.reglas_disciplina = DEFAULT_RULES

if "auto_entry" not in st.session_state:
    st.session_state.auto_entry = 0.0

if "auto_sl" not in st.session_state:
    st.session_state.auto_sl = 0.0

if "auto_tp" not in st.session_state:
    st.session_state.auto_tp = 0.0


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
# 5. UTILIDADES
# ============================================================

def safe_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def procesar_imagen_b64(uploaded_file, max_size=(1000, 800)):
    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

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


# ============================================================
# 6. BASE DE DATOS
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
            "❌ Error cargando operaciones desde Supabase."
        )

        with st.expander("🔎 Ver detalle técnico del error"):
            st.code(str(e))

        return []


def guardar_trade_supabase(user_id, trade_data):

    try:

        client = get_supabase_client()

        data = dict(trade_data)
        data["user_id"] = user_id

        response = (
            client
            .table("trades")
            .insert(data)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        st.error("❌ No se pudo guardar la operación.")

        with st.expander("🔎 Ver detalle técnico"):
            st.code(str(e))

        return False


def eliminar_trade_supabase(trade_id, user_id):

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

        st.error("❌ Error eliminando la operación.")

        with st.expander("🔎 Detalle técnico"):
            st.code(str(e))

        return False


def actualizar_trade_supabase(
    trade_id,
    user_id,
    trade_data
):

    try:

        client = get_supabase_client()

        (
            client
            .table("trades")
            .update(trade_data)
            .eq("id", trade_id)
            .eq("user_id", user_id)
            .execute()
        )

        return True

    except Exception as e:

        st.error("❌ Error actualizando operación.")

        with st.expander("🔎 Detalle técnico"):
            st.code(str(e))

        return False


# ============================================================
# 7. IA — ANÁLISIS DE TRADINGVIEW
# ============================================================

def analizar_captura_tradingview(image_bytes):

    if not OPENROUTER_API_KEY:
        st.warning(
            "OPENROUTER_API_KEY no está configurada."
        )
        return None

    b64_img = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = """
Analiza esta captura de TradingView.

Busca específicamente la herramienta de posición
(Risk/Reward / Long Position / Short Position).

Extrae únicamente:

- Precio de entrada
- Stop Loss
- Take Profit

Devuelve ÚNICAMENTE JSON válido:

{
  "entry": 0.0,
  "sl": 0.0,
  "tp": 0.0
}

Si un valor no aparece claramente, utiliza 0.0.
No agregues explicaciones.
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

        if response.status_code != 200:
            st.warning(
                f"OpenRouter respondió HTTP {response.status_code}"
            )
            return None

        res_json = response.json()

        content = (
            res_json["choices"][0]
            ["message"]["content"]
        )

        content_clean = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(content_clean)

        return {
            "entry": safe_float(data.get("entry")),
            "sl": safe_float(data.get("sl")),
            "tp": safe_float(data.get("tp"))
        }

    except Exception as e:

        st.warning(
            f"No fue posible analizar la imagen: {e}"
        )

        return None


# ============================================================
# 8. CSS
# ============================================================

def aplicar_estilos():

    css = """

    <style>

    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
    }

    p, label, h1, h2, h3, h4, span, div,
    .stMarkdown {
        color: #f0f3fa !important;
    }

    h1, h2 {
        background:
        linear-gradient(
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
    }

    .stButton > button {
        background:
        linear-gradient(
            135deg,
            #00d2ff 0%,
            #2962ff 100%
        ) !important;

        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow:
        0px 4px 15px
        rgba(0,210,255,0.3) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right:
        1px solid rgba(0,210,255,0.2) !important;
    }

    section[data-testid="stSidebar"]
    .stButton > button {
        background:
        linear-gradient(
            135deg,
            #e53935 0%,
            #b71c1c 100%
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
        background-color:
        rgba(76,175,80,0.2);
        color: #4caf50;
        border: 1px solid #4caf50;
    }

    .closed {
        background-color:
        rgba(244,67,54,0.2);
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

    .trade-card {
        background-color: #121721;
        border:
        1px solid rgba(0,242,254,0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }

    </style>

    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


# ============================================================
# 9. SUSCRIPCIÓN
# ============================================================

def evaluar_suscripcion(user):

    if not user:
        return False, "Sin sesión", 0

    user_email = (
        getattr(user, "email", "") or ""
    ).lower()

    # ADMIN
    if user_email == "jordandanielpenarrietasantilla@gmail.com":
        return True, "Creador / Admin 👑", 99999

    metadata = (
        getattr(user, "user_metadata", None)
        or {}
    )

    # VIP
    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999

    # FECHA
    created_at = getattr(
        user,
        "created_at",
        None
    )

    try:

        if created_at:

            fecha_registro = datetime.datetime.strptime(
                str(created_at)[:10],
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

    DIAS_PRUEBA = 3

    dias_restantes = max(
        0,
        DIAS_PRUEBA - dias_usados
    )

    if dias_usados < DIAS_PRUEBA:

        return (
            True,
            f"Prueba Gratis "
            f"({dias_restantes} días restantes)",
            dias_restantes
        )

    return (
        False,
        "Prueba Expirada 🛑",
        0
    )


# ============================================================
# 10. PAYWALL
# ============================================================

def render_paywall():

    st.markdown(
        "## 🔒 Tu período de prueba gratis ha expirado"
    )

    st.markdown(
        "Continúa utilizando tu Journal, "
        "Track Record y herramientas de auditoría "
        "mediante **Binance Pay**."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="paywall-card">

            <h3>🟡 Suscripción Mensual</h3>

            <h2>$5.00 USD
            <span style="font-size:1rem;">
            / mes
            </span>
            </h2>

            <p>
            Luego $2.50 USD / mes
            </p>

            <hr>

            <p>✔️ Acceso ilimitado</p>
            <p>✔️ Track Record PnL</p>
            <p>✔️ Auditoría IA</p>
            <p>✔️ Sin contratos</p>

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

            🟡 Pagar $5 USD

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

            <h2>$20.00 USD
            <span style="font-size:1rem;">
            / año
            </span>
            </h2>

            <p>
            ¡Ahorra 60%!
            </p>

            <hr>

            <p>🌟 1 año completo</p>
            <p>🔒 Pago único</p>
            <p>🎁 Actualizaciones incluidas</p>
            <p>🧠 IA prioritaria</p>

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

            💎 Pagar $20 USD

            </button>

            </a>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            "### 📲 Renovación"
        )

        st.code(
            f"Binance Pay ID: {BINANCE_PAY_ID}"
        )

        st.markdown(
            f"[👉 Renovación mensual $2.50 USD]"
            f"({LINK_BINANCE_RECURRENTE})"
        )

    with c2:

        st.markdown(
            "### ✈️ Activar cuenta"
        )

        st.markdown(
            f"""
            <a href="{LINK_TELEGRAM_SOPORTE}"
               target="_blank">

            <button style="
            background:#0088cc;
            color:white;
            border:none;
            padding:12px;
            border-radius:8px;
            width:100%;
            font-weight:bold;
            ">

            💬 Enviar comprobante

            </button>

            </a>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 11. AUTENTICACIÓN
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

        st.markdown("---")

        st.markdown(
            "### 🧠 Tu operativa. Tus datos. Tu disciplina."
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
                        "La contraseña debe tener "
                        "al menos 6 caracteres."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        res = (
                            client
                            .auth
                            .sign_up(
                                {
                                    "email": reg_email,
                                    "password": reg_pass
                                }
                            )
                        )

                        st.success(
                            "✅ Registro exitoso. "
                            "Ahora puedes iniciar sesión."
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
                "Correo Electrónico",
                key="reset_email"
            )

            if st.button(
                "Enviar Enlace de Recuperación",
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
                                "redirectTo":
                                app_url
                            }
                        )

                        st.success(
                            "📩 Enlace enviado. "
                            "Revisa tu correo y Spam."
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


# ============================================================
# 12. SIDEBAR
# ============================================================

def render_sidebar(estado_sub):

    with st.sidebar:

        st.markdown(
            "### 👤 Perfil Trader"
        )

        user = st.session_state.user

        user_email = (
            getattr(user, "email", "")
            if user
            else "trader@ejemplo.com"
        )

        metadata = (
            getattr(user, "user_metadata", None)
            or {}
        )

        nombre_actual = metadata.get(
            "username",
            st.session_state.nombre_trader
        )

        foto_b64 = metadata.get(
            "avatar_b64"
        )

        col_img, col_txt = st.columns(
            [1, 2]
        )

        with col_img:

            if foto_b64:

                st.markdown(
                    f"""
                    <img src="data:image/png;base64,
                    {foto_b64}"
                    style="
                    width:65px;
                    height:65px;
                    border-radius:50%;
                    object-fit:cover;
                    border:2px solid #00f2fe;
                    ">
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    "<div style='font-size:2.5rem;"
                    "text-align:center;'>👤</div>",
                    unsafe_allow_html=True
                )

        with col_txt:

            st.markdown(
                f"**{nombre_actual}**"
            )

            st.caption(
                f"`{user_email}`"
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

        # PERFIL
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
                ]
            )

            if st.button(
                "Guardar Cambios",
                key="save_profile"
            ):

                nueva_foto_b64 = foto_b64

                if foto_subida:

                    nueva_foto_b64 = base64.b64encode(
                        foto_subida.getvalue()
                    ).decode("utf-8")

                try:

                    client = get_supabase_client()

                    res = (
                        client
                        .auth
                        .update_user(
                            {
                                "data": {
                                    "username":
                                    input_nombre,
                                    "avatar_b64":
                                    nueva_foto_b64
                                }
                            }
                        )
                    )

                    st.session_state.user = res.user
                    st.session_state.nombre_trader = input_nombre

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )

        st.markdown("---")

        # CAPITAL
        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        cap_act = st.session_state.capital_actual
        cap_met = st.session_state.capital_meta

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
            f"**Capital:** "
            f"${cap_act:,.2f} / "
            f"${cap_met:,.2f}"
        )

        st.progress(progreso)

        with st.expander(
            "🔧 Configuración Meta"
        ):

            st.session_state.capital_actual = (
                st.number_input(
                    "Capital Actual",
                    value=float(cap_act),
                    step=100.0
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta de Capital",
                    value=float(cap_met),
                    step=500.0
                )
            )

        st.markdown("---")

        # REGLAS
        st.markdown(
            "### 🎯 Mis Reglas"
        )

        with st.expander(
            "✏️ Editar Reglas"
        ):

            input_reglas = st.text_area(
                "Reglas personalizadas",
                value=st.session_state.reglas_disciplina,
                height=160
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

        # SESIONES
        st.markdown(
            "### ⏰ Sesiones de Mercado"
        )

        hora_utc = datetime.datetime.utcnow().hour

        londres_status = (
            '<span class="market-badge open">'
            'ABIERTO</span>'
            if 7 <= hora_utc <= 15
            else
            '<span class="market-badge closed">'
            'CERRADO</span>'
        )

        ny_status = (
            '<span class="market-badge open">'
            'ABIERTO</span>'
            if 12 <= hora_utc <= 20
            else
            '<span class="market-badge closed">'
            'CERRADO</span>'
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
# 13. DASHBOARD
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

    # Garantizar columnas para datos antiguos
    columnas_default = {
        "id": None,
        "fecha": "",
        "par": "N/A",
        "direccion": "",
        "precio_entrada": 0.0,
        "stop_loss": 0.0,
        "take_profit": 0.0,
        "rr": 0.0,
        "timeframe": "",
        "resultado": "",
        "emocion": "",
        "notas_emocionales": "",
        "beneficio_usd": 0.0,
        "trades_cant": 1,
        "img_before": "",
        "img_after": ""
    }

    for col, default in columnas_default.items():

        if col not in df_trades.columns:

            df_trades[col] = default

    if not df_trades.empty:

        df_trades["beneficio_usd"] = pd.to_numeric(
            df_trades["beneficio_usd"],
            errors="coerce"
        ).fillna(0)

        df_trades["trades_cant"] = 1

    # ========================================================
    # TÍTULO
    # ========================================================

    st.markdown(
        "## ⚡ Journaling & AI Trading Audit"
    )

    # Botón de recarga
    col_reload, col_status = st.columns(
        [1, 5]
    )

    with col_reload:

        if st.button(
            "🔄 Recargar",
            key="reload_trades"
        ):

            st.rerun()

    with col_status:

        st.caption(
            f"📊 {len(df_trades)} operaciones cargadas "
            f"desde Supabase."
        )

    # ========================================================
    # TABS
    # ========================================================

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

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = tabs

    # ========================================================
    # TAB 1 — REGISTRAR TRADE
    # ========================================================

    with tab1:

        st.info(
            "💡 Sube una captura de TradingView "
            "con la herramienta de posición y la IA "
            "intentará extraer Entrada, SL y TP."
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

                bytes_b = upload_before.getvalue()

                img_before_b64 = (
                    procesar_imagen_b64(
                        upload_before
                    )
                )

                st.image(
                    upload_before,
                    caption="SETUP — Antes",
                    use_container_width=True
                )

                if st.button(
                    "🧠 Escanear SETUP con IA",
                    key="scan_setup"
                ):

                    with st.spinner(
                        "La IA está analizando..."
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
                            "No se pudieron detectar "
                            "los valores automáticamente."
                        )

            if upload_after:

                img_after_b64 = (
                    procesar_imagen_b64(
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
                key="new_fecha"
            )

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
                key="new_timeframe"
            )

            c1, c2 = st.columns(2)

            with c1:

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

            with c2:

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
                key="new_emotion"
            )

            notas_emocionales = st.text_area(
                "Notas emocionales",
                placeholder=(
                    "¿Respetaste tu plan? "
                    "¿Qué pensabas antes de entrar?"
                ),
                key="new_notes"
            )

            if st.button(
                "💾 Guardar Trade",
                key="save_trade",
                type="primary"
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

                    "notas_emocionales":
                    notas_emocionales,

                    "beneficio_usd":
                    monto_pnl,

                    "trades_cant":
                    1,

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
                        "✅ Trade guardado correctamente."
                    )

                    st.rerun()

    # ========================================================
    # TAB 2 — TRACK RECORD
    # ========================================================

    with tab2:

        st.markdown(
            "### 📅 Track Record & Calendario PnL"
        )

        if df_trades.empty:

            st.info(
                "Todavía no tienes operaciones."
            )

        else:

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

            total_pnl = (
                df_trades["beneficio_usd"]
                .sum()
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

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "PnL Acumulado",
                f"${total_pnl:,.2f}"
            )

            c2.metric(
                "Días Verdes",
                dias_ganadores
            )

            c3.metric(
                "Días Rojos",
                dias_perdedores
            )

            c4.metric(
                "Trades",
                len(df_trades)
            )

            st.markdown("---")

            # CALENDARIO
            st.markdown(
                "### 📅 Calendario"
            )

            pnl_map = (
                df_grouped
                .set_index("fecha")
                ["beneficio_usd"]
                .to_dict()
            )

            trades_map = (
                df_grouped
                .set_index("fecha")
                ["trades_cant"]
                .to_dict()
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

            for i, col in enumerate(cols):

                with col:

                    st.markdown(
                        f"<div style='text-align:center;"
                        f"font-weight:bold;'>"
                        f"{headers[i]}"
                        f"</div>",
                        unsafe_allow_html=True
                    )

            for semana in mes_dias:

                cols = st.columns(7)

                for idx, day_num in enumerate(semana):

                    with cols[idx]:

                        if day_num == 0:

                            st.markdown(
                                "<div style='height:90px;'>"
                                "</div>",
                                unsafe_allow_html=True
                            )

                            continue

                        f_date = datetime.date(
                            hoy.year,
                            hoy.month,
                            day_num
                        )

                        key = str(f_date)

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
                            text = "#f0f3fa"
                            pnl_text = ""

                        elif pnl > 0:

                            bg = "#34d399"
                            text = "#000000"
                            pnl_text = (
                                f"+${pnl:,.0f}"
                            )

                        elif pnl < 0:

                            bg = "#f87171"
                            text = "#000000"
                            pnl_text = (
                                f"-${abs(pnl):,.0f}"
                            )

                        else:

                            bg = "#161b22"
                            text = "#ffffff"
                            pnl_text = "$0"

                        border = (
                            "2px solid #00f2fe"
                            if f_date == hoy
                            else
                            "1px solid #242a35"
                        )

                        html = f"""

                        <div style="
                        background:{bg};
                        color:{text};
                        border:{border};
                        border-radius:7px;
                        padding:7px;
                        height:85px;
                        margin-bottom:7px;
                        ">

                        <b>{day_num}</b>

                        <div style="
                        text-align:center;
                        font-size:1.1rem;
                        font-weight:bold;
                        margin-top:10px;
                        ">

                        {pnl_text}

                        </div>

                        <div style="
                        text-align:center;
                        font-size:0.7rem;
                        ">

                        {trades_count} trade(s)

                        </div>

                        </div>

                        """

                        st.markdown(
                            html,
                            unsafe_allow_html=True
                        )

            st.markdown("---")

            # HISTORIAL
            st.markdown(
                "### 📋 Historial Detallado"
            )

            for _, row in df_trades.iterrows():

                trade_id = row.get("id")

                pnl = safe_float(
                    row.get("beneficio_usd")
                )

                titulo = (
                    f"📅 {row.get('fecha')} | "
                    f"📊 {row.get('par')} | "
                    f"{row.get('resultado')} | "
                    f"PnL: ${pnl:,.2f}"
                )

                with st.expander(titulo):

                    c1, c2, c3 = st.columns(
                        [1.5, 2, 2]
                    )

                    with c1:

                        st.markdown(
                            "#### ⚙️ Operación"
                        )

                        st.write(
                            f"**Dirección:** "
                            f"{row.get('direccion') or 'N/A'}"
                        )

                        st.write(
                            f"**Timeframe:** "
                            f"{row.get('timeframe') or 'N/A'}"
                        )

                        st.write(
                            f"**Entrada:** "
                            f"{safe_float(row.get('precio_entrada'))}"
                        )

                        st.write(
                            f"**SL:** "
                            f"{safe_float(row.get('stop_loss'))}"
                        )

                        st.write(
                            f"**TP:** "
                            f"{safe_float(row.get('take_profit'))}"
                        )

                        st.write(
                            f"**RR:** "
                            f"1 : {safe_float(row.get('rr')):.2f}"
                        )

                        st.write(
                            f"**Emoción:** "
                            f"{row.get('emocion') or 'N/A'}"
                        )

                        if row.get(
                            "notas_emocionales"
                        ):

                            st.markdown(
                                "**Notas:**"
                            )

                            st.write(
                                row.get(
                                    "notas_emocionales"
                                )
                            )

                        st.markdown("---")

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

                    with c2:

                        st.markdown(
                            "**1️⃣ ANTES**"
                        )

                        img_b = row.get(
                            "img_before"
                        )

                        if (
                            img_b
                            and str(img_b)
                            .startswith("data:image")
                        ):

                            st.image(
                                img_b,
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "📷 Sin captura"
                            )

                    with c3:

                        st.markdown(
                            "**2️⃣ DESPUÉS**"
                        )

                        img_a = row.get(
                            "img_after"
                        )

                        if (
                            img_a
                            and str(img_a)
                            .startswith("data:image")
                        ):

                            st.image(
                                img_a,
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "📷 Sin captura"
                            )

            # GRÁFICO
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
                    "GANANCIA":
                    "#00f2fe",
                    "PÉRDIDA":
                    "#f44336"
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
    # TAB 3 — CHAT IA
    # ========================================================

    with tab3:

        st.markdown(
            "### 💬 Chat de Auditoría IA"
        )

        st.caption(
            "Analiza tus hábitos, estadísticas y disciplina."
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
            "Pregúntame sobre tu operativa..."
        )

        if prompt:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message("user"):

                st.markdown(prompt)

            with st.chat_message("assistant"):

                if df_trades.empty:

                    respuesta = (
                        "Todavía no tienes "
                        "trades registrados."
                    )

                else:

                    total = len(df_trades)

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

                    losses = len(
                        df_trades[
                            df_trades[
                                "beneficio_usd"
                            ] < 0
                        ]
                    )

                    win_rate = (
                        wins / total * 100
                    )

                    respuesta = f"""
### 🧠 Auditoría rápida

Has registrado **{total} trades**.

**PnL acumulado:** ${pnl:,.2f}

**Win Rate:** {win_rate:.1f}%

**Wins:** {wins}

**Losses:** {losses}

Mi recomendación: no evalúes solamente
el porcentaje de aciertos. También analiza
tu comportamiento emocional, el cumplimiento
del Stop Loss, el R:R y la calidad de tus entradas.
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
    # TAB 4 — LOTAJE
    # ========================================================

    with tab4:

        st.markdown(
            "### 🧮 Calculadora de Tamaño de Posición"
        )

        c1, c2 = st.columns(2)

        with c1:

            balance = st.number_input(
                "Balance USD",
                value=float(
                    st.session_state.capital_actual
                ),
                step=500.0
            )

            porcentaje_riesgo = st.number_input(
                "Riesgo por operación (%)",
                value=1.0,
                step=0.25
            )

            pips_sl = st.number_input(
                "Distancia SL (pips/puntos)",
                value=20.0,
                step=1.0
            )

        with c2:

            riesgo_usd = (
                balance
                * porcentaje_riesgo
                / 100
            )

            lotaje = (
                riesgo_usd
                / (pips_sl * 10)
                if pips_sl > 0
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

            st.warning(
                "⚠️ La equivalencia de pip/punto "
                "depende del instrumento y broker. "
                "Verifica el valor contractual antes "
                "de ejecutar una operación."
            )

    # ========================================================
    # TAB 5 — AUDITORÍA VISUAL
    # ========================================================

    with tab5:

        st.markdown(
            "### 🤖 Auditoría Visual de Mercado"
        )

        st.caption(
            "Sube un gráfico para una segunda opinión."
        )

        chart = st.file_uploader(
            "Subir gráfico",
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

                with st.spinner(
                    "Analizando estructura..."
                ):

                    resultado_ia = (
                        analizar_captura_tradingview(
                            chart.getvalue()
                        )
                    )

                if resultado_ia:

                    st.success(
                        "### 🤖 Lectura detectada"
                    )

                    st.write(
                        f"**Entrada:** "
                        f"{resultado_ia['entry']}"
                    )

                    st.write(
                        f"**SL:** "
                        f"{resultado_ia['sl']}"
                    )

                    st.write(
                        f"**TP:** "
                        f"{resultado_ia['tp']}"
                    )

                else:

                    st.warning(
                        "No pude leer los niveles."
                    )

    # ========================================================
    # TAB 6 — PROYECCIONES
    # ========================================================

    with tab6:

        st.markdown(
            "### 📈 Proyección de Capital"
        )

        c1, c2 = st.columns(2)

        with c1:

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

        with c2:

            ganancia_prom = st.number_input(
                "Ganancia promedio WIN",
                value=200.0,
                step=25.0
            )

            perdida_prom = st.number_input(
                "Pérdida promedio LOSS",
                value=100.0,
                step=25.0
            )

        capital = (
            st.session_state.capital_actual
        )

        datos = []

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

            datos.append(
                {
                    "Mes":
                    f"Mes {m}",
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
            "### 📓 Diario & Psicotrading"
        )

        st.caption(
            "Registra tus reflexiones y patrones mentales."
        )

        reflexion = st.text_area(
            "Reflexión",
            height=200,
            placeholder=(
                "¿Qué hice bien?\n"
                "¿Qué hice mal?\n"
                "¿Respeté mi riesgo?\n"
                "¿Sentí FOMO?\n"
                "¿Entré por venganza?"
            )
        )

        if st.button(
            "💾 Guardar Reflexión",
            key="save_reflection"
        ):

            st.success(
                "🧠 Reflexión guardada "
                "en esta sesión."
            )

            st.caption(
                "En la próxima versión podemos "
                "guardar estas reflexiones también "
                "en Supabase para crear un historial "
                "permanente de psicotrading."
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

        if total_trades > 0:

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

            pnl_total = (
                df_trades[
                    "beneficio_usd"
                ].sum()
            )

            win_rate = (
                wins
                / total_trades
                * 100
            )

            dias = (
                df_trades["fecha"]
                .nunique()
            )

        else:

            wins = 0
            losses = 0
            pnl_total = 0
            win_rate = 0
            dias = 0

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "PnL Total",
            f"${pnl_total:,.2f}"
        )

        c2.metric(
            "Win Rate",
            f"{win_rate:.1f}%"
        )

        c3.metric(
            "Trades",
            total_trades
        )

        c4.metric(
            "Días Operados",
            dias
        )

        st.markdown("---")

        if not df_trades.empty:

            st.markdown(
                "#### 📊 PnL por Activo"
            )

            df_asset = (
                df_trades
                .groupby("par")
                ["beneficio_usd"]
                .sum()
                .reset_index()
            )

            fig_asset = px.bar(
                df_asset,
                x="par",
                y="beneficio_usd",
                title="Rendimiento por Activo",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig_asset,
                use_container_width=True
            )

            st.markdown("---")

            st.markdown(
                "#### 🧠 Resultado por Emoción"
            )

            df_emotion = (
                df_trades
                .groupby("emocion")
                ["beneficio_usd"]
                .sum()
                .reset_index()
            )

            fig_emotion = px.bar(
                df_emotion,
                x="emocion",
                y="beneficio_usd",
                title="PnL según Estado Emocional",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig_emotion,
                use_container_width=True
            )

            st.markdown("---")

            st.markdown(
                "#### 📋 Base de Operaciones"
            )

            columnas_mostrar = [
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

            columnas_validas = [
                c for c in columnas_mostrar
                if c in df_trades.columns
            ]

            st.dataframe(
                df_trades[
                    columnas_validas
                ],
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "Registra tu primer trade "
                "para desbloquear tus métricas."
            )


# ============================================================
# 14. FLUJO PRINCIPAL
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
````
