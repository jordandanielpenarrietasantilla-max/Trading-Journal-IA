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
from zoneinfo import ZoneInfo
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
# 2. ENLACES Y CONFIGURACIÓN
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
# 4. ESTADO DE SESIÓN
# ============================================================

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
    st.session_state.reglas_disciplina = (
        "• Acepta la pérdida antes de entrar.\n"
        "• Corta pérdidas rápido.\n"
        "• Deja correr los ganadores.\n"
        "• Máximo 2 operaciones perdedoras por día."
    )

if "auto_entry" not in st.session_state:
    st.session_state.auto_entry = 0.0

if "auto_sl" not in st.session_state:
    st.session_state.auto_sl = 0.0

if "auto_tp" not in st.session_state:
    st.session_state.auto_tp = 0.0


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
# 6. UTILIDADES DE IMÁGENES
# ============================================================

def procesar_imagen_b64(uploaded_file, max_size=(1000, 800)):
    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file)

        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        image.thumbnail(max_size)

        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=80,
            optimize=True
        )

        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return f"data:image/jpeg;base64,{encoded}"

    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return ""


def mostrar_imagen_segura(img_data, caption=""):
    """
    Muestra imágenes Base64 sin imprimir el código.
    """

    if not img_data:
        st.caption("📷 Sin imagen")
        return

    if isinstance(img_data, str) and img_data.startswith("data:image"):
        try:
            header, encoded = img_data.split(",", 1)

            image_bytes = base64.b64decode(encoded)

            st.image(
                image_bytes,
                caption=caption,
                use_container_width=True
            )

        except Exception:
            st.caption("⚠️ Imagen no disponible")
    else:
        st.caption("📷 Sin imagen")


# ============================================================
# 7. SUPABASE — TRADES
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
            f"❌ Error cargando operaciones desde Supabase: {e}"
        )

        return []


def guardar_trade_supabase(user_id, trade_data):

    try:

        client = get_supabase_client()

        trade_data["user_id"] = user_id

        response = (
            client
            .table("trades")
            .insert(trade_data)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        st.error(
            f"❌ Error guardando operación: {e}"
        )

        return False


def actualizar_trade_supabase(trade_id, trade_data):

    try:

        client = get_supabase_client()

        (
            client
            .table("trades")
            .update(trade_data)
            .eq("id", trade_id)
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"❌ Error actualizando operación: {e}"
        )

        return False


def eliminar_trade_supabase(trade_id):

    try:

        client = get_supabase_client()

        (
            client
            .table("trades")
            .delete()
            .eq("id", trade_id)
            .execute()
        )

        return True

    except Exception as e:

        st.error(
            f"❌ Error eliminando operación: {e}"
        )

        return False


# ============================================================
# 8. IA — VISIÓN
# ============================================================

def analizar_captura_tradingview(image_bytes):

    if not OPENROUTER_API_KEY:
        return None

    b64_img = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = """
Analiza este gráfico de TradingView.

Busca la herramienta de posición/risk reward.

Extrae:

- Entry
- Stop Loss
- Take Profit

Devuelve ÚNICAMENTE JSON válido:

{
  "entry": 0.0,
  "sl": 0.0,
  "tp": 0.0
}

Si no encuentras algún valor utiliza 0.0.
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

        response.raise_for_status()

        data = response.json()

        content = (
            data["choices"][0]["message"]["content"]
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
# 9. CSS
# ============================================================

def aplicar_estilos():

    css = """

    <style>

    .stApp {
        background-color:#0b0e14 !important;
        color:#f0f3fa !important;
        font-family:'Segoe UI',Roboto,sans-serif !important;
    }

    p,label,h1,h2,h3,h4,span,div,
    .stMarkdown {
        color:#f0f3fa !important;
    }

    h1,h2 {
        background:
        linear-gradient(
            90deg,
            #00f2fe 0%,
            #4facfe 100%
        );

        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;

        font-weight:800 !important;
    }

    div[data-baseweb="select"] > div {

        background-color:#121721 !important;

        color:#00f2fe !important;

        border:
        1px solid rgba(0,242,254,0.5) !important;

        border-radius:8px !important;
    }

    div[data-baseweb="select"] input {

        color:#00f2fe !important;

        -webkit-text-fill-color:#00f2fe !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {

        background-color:#121721 !important;

        border:1px solid #00f2fe !important;

        border-radius:8px !important;
    }

    div[role="option"],
    li[role="option"],
    li[data-baseweb="option"] {

        background-color:#121721 !important;

        color:#ffffff !important;

        padding:10px 14px !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"] {

        background-color:#00f2fe !important;

        color:#000000 !important;

        font-weight:bold !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {

        background-color:#161b22 !important;

        color:#00f2fe !important;

        border:
        1px solid rgba(0,210,255,0.4) !important;

        border-radius:8px !important;
    }

    div[data-testid="stChatInput"] {

        background-color:#161b22 !important;

        border-radius:12px !important;

        border:
        1px solid rgba(0,210,255,0.5) !important;
    }

    div[data-testid="stChatInput"] textarea {

        background-color:#161b22 !important;

        color:#00f2fe !important;

        -webkit-text-fill-color:#00f2fe !important;
    }

    .stButton > button {

        background:
        linear-gradient(
            135deg,
            #00d2ff 0%,
            #2962ff 100%
        ) !important;

        color:white !important;

        border:none !important;

        border-radius:8px !important;

        font-weight:bold !important;

        width:100%;

        box-shadow:
        0 4px 15px
        rgba(0,210,255,0.3) !important;
    }

    section[data-testid="stSidebar"] {

        background-color:#0f141e !important;

        border-right:
        1px solid
        rgba(0,210,255,0.2) !important;
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

    .trade-card {

        background-color:#121721;

        border:
        1px solid
        rgba(0,242,254,0.2);

        border-radius:10px;

        padding:15px;

        margin-bottom:20px;
    }

    .session-card {

        background:#121721;

        border:
        1px solid
        rgba(0,242,254,0.18);

        border-radius:10px;

        padding:10px;

        margin-bottom:8px;
    }

    .paywall-card {

        background-color:#161b22;

        border:1px solid #f0b90b;

        border-radius:12px;

        padding:24px;

        text-align:center;

        box-shadow:
        0 0 20px
        rgba(240,185,11,0.2);
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

    user_email = (
        user.email
        if user and hasattr(user, "email")
        else ""
    )

    if (
        user_email.lower()
        == "jordandanielpenarrietasantilla@gmail.com"
    ):

        return True, "Creador / Admin 👑", 99999

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

        return True, "Acceso PRO 💎", 999

    created_at_str = (
        str(user.created_at)
        if hasattr(user, "created_at")
        else None
    )

    try:

        if created_at_str:

            fecha_registro = datetime.datetime.strptime(
                created_at_str[:10],
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
# 11. PAYWALL
# ============================================================

def render_paywall():

    st.markdown(
        "## 🔒 Tu período de prueba gratis ha expirado"
    )

    st.markdown(
        "Activa tu acceso para continuar utilizando "
        "el Journal, Track Record y herramientas de IA."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="paywall-card">

            <h3>🟡 Suscripción Mensual</h3>

            <h2>$5.00 USD / mes</h2>

            <p>
            Luego $2.50 USD / mes
            </p>

            <hr>

            <p>✔️ Journal ilimitado</p>
            <p>✔️ Track Record</p>
            <p>✔️ Auditoría IA</p>
            <p>✔️ Psicotrading</p>

            <br>

            <a
            href="{LINK_BINANCE_INSCRIPCION}"
            target="_blank">

            <button style="
            background:#f0b90b;
            color:#000;
            border:none;
            padding:14px;
            border-radius:8px;
            font-weight:bold;
            width:100%;
            cursor:pointer;
            ">

            🟡 Pagar con Binance Pay

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

            <h3>💎 Acceso Anual</h3>

            <h2>$20.00 USD / año</h2>

            <p>
            Ahorra frente al plan mensual
            </p>

            <hr>

            <p>🌟 1 año completo</p>
            <p>🔒 Pago único</p>
            <p>🎁 Actualizaciones futuras</p>
            <p>🧠 IA incluida</p>

            <br>

            <a
            href="{LINK_BINANCE_ANUAL}"
            target="_blank">

            <button style="
            background:#00f2fe;
            color:#000;
            border:none;
            padding:14px;
            border-radius:8px;
            font-weight:bold;
            width:100%;
            cursor:pointer;
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

    with c2:

        st.markdown(
            "### ✈️ Confirmar pago"
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
            font-weight:bold;
            width:100%;
            cursor:pointer;
            ">

            💬 Enviar comprobante

            </button>

            </a>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 12. SESIONES DE TRADING
# ============================================================

SESIONES = [

    {
        "nombre": "Sídney",
        "bandera": "🇦🇺",
        "zona": "Australia/Sydney",
        "inicio": 7,
        "fin": 16
    },

    {
        "nombre": "Tokio",
        "bandera": "🇯🇵",
        "zona": "Asia/Tokyo",
        "inicio": 9,
        "fin": 18
    },

    {
        "nombre": "Londres",
        "bandera": "🇬🇧",
        "zona": "Europe/London",
        "inicio": 8,
        "fin": 17
    },

    {
        "nombre": "Nueva York",
        "bandera": "🇺🇸",
        "zona": "America/New_York",
        "inicio": 8,
        "fin": 17
    }

]


def obtener_hora_zona(zona):

    return datetime.datetime.now(
        ZoneInfo(zona)
    )


def sesion_abierta(zona, inicio, fin):

    ahora = obtener_hora_zona(zona)

    hora_decimal = (
        ahora.hour
        + ahora.minute / 60
    )

    return (
        inicio
        <= hora_decimal
        < fin
    )


def render_sesiones():

    st.markdown(
        "### 🌍 Sesiones de Trading"
    )

    st.markdown(
        "#### 🕐 Hora local"
    )

    st.components.v1.html(
        """
        <div style="
        font-family:monospace;
        font-size:22px;
        font-weight:bold;
        color:#00f2fe;
        background:#161b22;
        border:1px solid rgba(0,210,255,.4);
        border-radius:8px;
        padding:8px;
        text-align:center;
        ">

        <span id="clock">
        00:00:00
        </span>

        </div>

        <script>

        function updateClock(){

            const now = new Date();

            document.getElementById(
                "clock"
            ).innerHTML =
            now.toLocaleTimeString(
                [],
                {
                    hour:"2-digit",
                    minute:"2-digit",
                    second:"2-digit"
                }
            );

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

    st.markdown(
        "#### 📊 Mercados globales"
    )

    abiertas = []

    for sesion in SESIONES:

        ahora = obtener_hora_zona(
            sesion["zona"]
        )

        abierta = sesion_abierta(
            sesion["zona"],
            sesion["inicio"],
            sesion["fin"]
        )

        if abierta:
            abiertas.append(
                sesion["nombre"]
            )

        estado = (
            "🟢 ABIERTA"
            if abierta
            else "🔴 CERRADA"
        )

        estado_color = (
            "#34d399"
            if abierta
            else "#f87171"
        )

        st.markdown(
            f"""
            <div class="session-card">

            <div style="
            display:flex;
            justify-content:space-between;
            align-items:center;
            ">

            <div>

            <div style="
            font-weight:bold;
            font-size:15px;
            ">

            {sesion["bandera"]}
            {sesion["nombre"]}

            </div>

            <div style="
            color:#8b95a7;
            font-size:11px;
            ">

            {ahora.strftime("%d/%m/%Y")}

            </div>

            </div>

            <div style="
            text-align:right;
            ">

            <div style="
            color:#00f2fe;
            font-family:monospace;
            font-size:17px;
            font-weight:bold;
            ">

            {ahora.strftime("%H:%M:%S")}

            </div>

            <div style="
            color:{estado_color};
            font-size:11px;
            font-weight:bold;
            ">

            {estado}

            </div>

            </div>

            </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")

    if len(abiertas) == 0:

        st.info(
            "🌙 No hay sesiones principales abiertas."
        )

    else:

        st.success(
            "🔥 Sesiones abiertas: "
            + ", ".join(abiertas)
        )

    if (
        "Londres" in abiertas
        and "Nueva York" in abiertas
    ):

        st.warning(
            "⚡ SOLAPAMIENTO LONDRES + NUEVA YORK: "
            "zona de alta actividad del mercado."
        )


# ============================================================
# 13. SIDEBAR
# ============================================================

def render_sidebar(estado_sub):

    with st.sidebar:

        st.markdown(
            "## 👤 Perfil Trader"
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
            st.session_state.nombre_trader
        )

        foto_b64 = metadata.get(
            "avatar_b64",
            ""
        )

        # ----------------------------------------------------
        # PERFIL — IMPORTANTE:
        # NUNCA MOSTRAR EL BASE64 COMO TEXTO
        # ----------------------------------------------------

        col_img, col_txt = st.columns(
            [1, 2]
        )

        with col_img:

            if foto_b64:

                try:

                    if foto_b64.startswith(
                        "data:image"
                    ):

                        header, encoded = (
                            foto_b64.split(",", 1)
                        )

                        image_bytes = base64.b64decode(
                            encoded
                        )

                    else:

                        image_bytes = base64.b64decode(
                            foto_b64
                        )

                    st.image(
                        image_bytes,
                        width=65
                    )

                except Exception:

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

            if foto_subida:

                st.image(
                    foto_subida,
                    width=100
                )

            if st.button(
                "💾 Guardar Perfil"
            ):

                try:

                    nueva_foto = foto_b64

                    if foto_subida:

                        nueva_foto = procesar_imagen_b64(
                            foto_subida,
                            max_size=(400, 400)
                        )

                    client = (
                        get_supabase_client()
                    )

                    response = (
                        client.auth.update_user(
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
                        f"Error: {e}"
                    )

        st.markdown("---")

        # ----------------------------------------------------
        # META DE CAPITAL
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
            f"**Capital:** "
            f"${cap_act:,.2f} / "
            f"${cap_met:,.2f}"
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
                    value=float(cap_act),
                    step=100.0
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta de Capital ($)",
                    value=float(cap_met),
                    step=500.0
                )
            )

        st.markdown("---")

        # ----------------------------------------------------
        # SESIONES
        # ----------------------------------------------------

        render_sesiones()

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
                "Reglas:",
                value=st.session_state.reglas_disciplina,
                height=150
            )

            if st.button(
                "💾 Guardar Reglas"
            ):

                st.session_state.reglas_disciplina = (
                    input_reglas
                )

                st.rerun()

        st.markdown(
            st.session_state.reglas_disciplina
        )

        st.markdown("---")

        if st.button(
            "🚪 Cerrar Sesión"
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

            st.rerun()


# ============================================================
# 14. AUTENTICACIÓN
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

            - 📊 Track Record
            - 🧠 Psicotrading
            - 🤖 Auditoría IA
            - 📈 Estadísticas
            - 📝 Diario de operaciones
            """
        )

    with col2:

        tab_login, tab_register, tab_reset = st.tabs(
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
                "### Ingresa a tu Cuenta"
            )

            login_email = st.text_input(
                "Correo",
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
                        "Completa todos los campos."
                    )

                else:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        res = (
                            client.auth.sign_in_with_password(
                                {
                                    "email":
                                        login_email,
                                    "password":
                                        login_pass
                                }
                            )
                        )

                        st.session_state.authenticated = True

                        st.session_state.user = (
                            res.user
                        )

                        st.rerun()

                    except Exception as err:

                        st.error(
                            f"Error al iniciar sesión: {err}"
                        )

        # ----------------------------------------------------
        # REGISTRO
        # ----------------------------------------------------

        with tab_register:

            st.markdown(
                "### Crear Cuenta"
            )

            reg_email = st.text_input(
                "Correo",
                key="reg_email"
            )

            reg_pass = st.text_input(
                "Contraseña",
                type="password",
                key="reg_pass"
            )

            if st.button(
                "Crear Cuenta y Probar",
                key="btn_reg"
            ):

                if reg_email and reg_pass:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        client.auth.sign_up(
                            {
                                "email":
                                    reg_email,
                                "password":
                                    reg_pass
                            }
                        )

                        st.success(
                            "✅ Cuenta creada. "
                            "Ahora puedes iniciar sesión."
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )

        # ----------------------------------------------------
        # RESET
        # ----------------------------------------------------

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

                if reset_email:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        app_url = (
                            "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                        )

                        client.auth.reset_password_for_email(
                            reset_email,
                            {
                                "redirectTo":
                                    app_url
                            }
                        )

                        st.success(
                            "📩 Revisa tu correo."
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


# ============================================================
# 15. EDITOR DE TRADES
# ============================================================

def render_editor_trade(row):

    trade_id = row.get("id")

    st.markdown(
        "### ✏️ Editar Operación"
    )

    c1, c2 = st.columns(2)

    with c1:

        fecha_actual = row.get(
            "fecha",
            str(datetime.date.today())
        )

        try:

            fecha_default = (
                datetime.datetime.strptime(
                    str(fecha_actual),
                    "%Y-%m-%d"
                ).date()
            )

        except Exception:

            fecha_default = (
                datetime.date.today()
            )

        nueva_fecha = st.date_input(
            "Fecha",
            value=fecha_default,
            key=f"edit_fecha_{trade_id}"
        )

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

        nuevo_par = st.selectbox(
            "Activo",
            opciones_par,
            index=0,
            key=f"edit_par_{trade_id}"
        )

        direccion_actual = row.get(
            "direccion",
            "LONG 🟢"
        )

        nueva_direccion = st.radio(
            "Dirección",
            [
                "LONG 🟢",
                "SHORT 🔴"
            ],
            index=(
                0
                if direccion_actual
                != "SHORT 🔴"
                else 1
            ),
            horizontal=True,
            key=f"edit_dir_{trade_id}"
        )

        nueva_entrada = st.number_input(
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

        nuevo_sl = st.number_input(
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

        nuevo_tp = st.number_input(
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

    with c2:

        riesgo_dist = abs(
            nueva_entrada
            - nuevo_sl
        )

        beneficio_dist = abs(
            nuevo_tp
            - nueva_entrada
        )

        nuevo_rr = (
            beneficio_dist / riesgo_dist
            if riesgo_dist > 0
            else 0
        )

        st.metric(
            "Risk : Reward",
            f"1 : {nuevo_rr:.2f}"
        )

        nuevo_timeframe = st.selectbox(
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
            index=(
                [
                    "M1",
                    "M5",
                    "M15",
                    "M30",
                    "H1",
                    "H4",
                    "D1",
                    "W1"
                ].index(
                    row.get(
                        "timeframe",
                        "H1"
                    )
                )
                if row.get(
                    "timeframe",
                    "H1"
                ) in [
                    "M1",
                    "M5",
                    "M15",
                    "M30",
                    "H1",
                    "H4",
                    "D1",
                    "W1"
                ]
                else 4
            ),
            key=f"edit_tf_{trade_id}"
        )

        resultado_actual = row.get(
            "resultado",
            "BE ⚪"
        )

        nuevo_resultado = st.selectbox(
            "Resultado",
            [
                "WIN 🟢",
                "LOSS 🔴",
                "BE ⚪"
            ],
            index=(
                [
                    "WIN 🟢",
                    "LOSS 🔴",
                    "BE ⚪"
                ].index(
                    resultado_actual
                )
                if resultado_actual in [
                    "WIN 🟢",
                    "LOSS 🔴",
                    "BE ⚪"
                ]
                else 0
            ),
            key=f"edit_resultado_{trade_id}"
        )

        emocion_actual = row.get(
            "emocion",
            "Disciplinado / Neutro 🧘"
        )

        emociones = [
            "Disciplinado / Neutro 🧘",
            "Ansioso ⚡",
            "FOMO / Miedo a perderse el movimiento 🚀",
            "Venganza / Frustrado 🛑",
            "Eufórico / Sobre-confiado 😎"
        ]

        nueva_emocion = st.selectbox(
            "Estado emocional",
            emociones,
            index=(
                emociones.index(
                    emocion_actual
                )
                if emocion_actual in emociones
                else 0
            ),
            key=f"edit_emocion_{trade_id}"
        )

        nuevo_pnl = st.number_input(
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

        nuevas_notas = st.text_area(
            "Notas emocionales",
            value=row.get(
                "notas_emocionales",
                ""
            ) or "",
            height=120,
            key=f"edit_notas_{trade_id}"
        )

    st.markdown(
        "### 🖼️ Capturas"
    )

    img1, img2 = st.columns(2)

    with img1:

        st.markdown(
            "#### 1️⃣ Antes"
        )

        mostrar_imagen_segura(
            row.get("img_before"),
            "Captura actual"
        )

        nueva_img_before = st.file_uploader(
            "Reemplazar / agregar Antes",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_img_before_{trade_id}"
        )

    with img2:

        st.markdown(
            "#### 2️⃣ Después"
        )

        mostrar_imagen_segura(
            row.get("img_after"),
            "Captura actual"
        )

        nueva_img_after = st.file_uploader(
            "Reemplazar / agregar Después",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_img_after_{trade_id}"
        )

    if st.button(
        "💾 GUARDAR CAMBIOS",
        key=f"save_edit_{trade_id}"
    ):

        img_before = row.get(
            "img_before",
            ""
        )

        img_after = row.get(
            "img_after",
            ""
        )

        if nueva_img_before:

            img_before = procesar_imagen_b64(
                nueva_img_before
            )

        if nueva_img_after:

            img_after = procesar_imagen_b64(
                nueva_img_after
            )

        datos_actualizados = {

            "fecha":
                str(nueva_fecha),

            "par":
                nuevo_par,

            "direccion":
                nueva_direccion,

            "precio_entrada":
                nueva_entrada,

            "stop_loss":
                nuevo_sl,

            "take_profit":
                nuevo_tp,

            "rr":
                nuevo_rr,

            "timeframe":
                nuevo_timeframe,

            "resultado":
                nuevo_resultado,

            "emocion":
                nueva_emocion,

            "beneficio_usd":
                nuevo_pnl,

            "notas_emocionales":
                nuevas_notas,

            "img_before":
                img_before,

            "img_after":
                img_after

        }

        if actualizar_trade_supabase(
            trade_id,
            datos_actualizados
        ):

            st.success(
                "✅ Operación actualizada."
            )

            st.rerun()


# ============================================================
# 16. DASHBOARD
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

    tabs = st.tabs(
        [
            "➕ Registrar Trade",
            "📅 Track Record PnL",
            "💬 Chat IA & Auditoría",
            "🧮 Calc. Lotaje",
            "🧠 Análisis vs IA",
            "📈 Proyecciones",
            "📓 Diario & Psicotrading",
            "📊 Dashboard"
        ]
    )

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = tabs


    # ========================================================
    # TAB 1
    # ========================================================

    with tab1:

        st.markdown(
            "### ➕ Registrar Nueva Operación"
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
                    procesar_imagen_b64(
                        upload_before
                    )
                )

                st.image(
                    upload_before,
                    caption="ANTES",
                    use_container_width=True
                )

                if st.button(
                    "🧠 Escanear Setup con IA"
                ):

                    extracted = (
                        analizar_captura_tradingview(
                            upload_before.getvalue()
                        )
                    )

                    if extracted:

                        st.session_state.auto_entry = (
                            extracted.get(
                                "entry",
                                0
                            )
                        )

                        st.session_state.auto_sl = (
                            extracted.get(
                                "sl",
                                0
                            )
                        )

                        st.session_state.auto_tp = (
                            extracted.get(
                                "tp",
                                0
                            )
                        )

                        st.success(
                            "✨ Valores detectados."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "No fue posible detectar los valores."
                        )

            if upload_after:

                img_after_b64 = (
                    procesar_imagen_b64(
                        upload_after
                    )
                )

                st.image(
                    upload_after,
                    caption="DESPUÉS",
                    use_container_width=True
                )

            monto_pnl = st.number_input(
                "Ganancia / Pérdida USD",
                value=0.0,
                step=10.0
            )

        with col1:

            fecha_op = st.date_input(
                "Fecha",
                datetime.date.today()
            )

            par = st.selectbox(
                "Activo",
                LISTA_ACTIVOS
            )

            direccion = st.radio(
                "Dirección",
                [
                    "LONG 🟢",
                    "SHORT 🔴"
                ],
                horizontal=True
            )

            precio_entrada = st.number_input(
                "Precio Entrada",
                value=float(
                    st.session_state.auto_entry
                ),
                format="%.5f"
            )

            stop_loss = st.number_input(
                "Stop Loss",
                value=float(
                    st.session_state.auto_sl
                ),
                format="%.5f"
            )

            take_profit = st.number_input(
                "Take Profit",
                value=float(
                    st.session_state.auto_tp
                ),
                format="%.5f"
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
                ]
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
                ]
            )

            emocion = st.selectbox(
                "Estado emocional",
                [
                    "Disciplinado / Neutro 🧘",
                    "Ansioso ⚡",
                    "FOMO / Miedo a perderse el movimiento 🚀",
                    "Venganza / Frustrado 🛑",
                    "Eufórico / Sobre-confiado 😎"
                ]
            )

            notas = st.text_area(
                "Notas emocionales"
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
                        notas,

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
                        "✅ Trade guardado."
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
            "Días Verdes",
            dias_ganadores
        )

        c3.metric(
            "Días Rojos",
            dias_perdedores
        )

        st.markdown("---")

        st.markdown(
            "### 📋 Historial de Operaciones"
        )

        if df_trades.empty:

            st.info(
                "Todavía no tienes trades."
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
                    ) or 0
                )

                titulo = (
                    f"📅 {row.get('fecha')} | "
                    f"{row.get('par')} | "
                    f"{row.get('resultado')} | "
                    f"${pnl:,.2f}"
                )

                with st.expander(
                    titulo
                ):

                    d1, d2, d3 = st.columns(
                        [1.2, 2, 2]
                    )

                    with d1:

                        st.markdown(
                            "#### 📊 Datos"
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
                            f"1:{float(row.get('rr', 0) or 0):.2f}"
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

                    with d2:

                        st.markdown(
                            "#### 1️⃣ ANTES"
                        )

                        mostrar_imagen_segura(
                            row.get(
                                "img_before"
                            )
                        )

                    with d3:

                        st.markdown(
                            "#### 2️⃣ DESPUÉS"
                        )

                        mostrar_imagen_segura(
                            row.get(
                                "img_after"
                            )
                        )

                    st.markdown("---")

                    # ------------------------------------------------
                    # EDITAR
                    # ------------------------------------------------

                    render_editor_trade(
                        row
                    )

                    st.markdown("---")

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

        st.markdown("---")

        # ----------------------------------------------------
        # CALENDARIO
        # ----------------------------------------------------

        st.markdown(
            "### 🗓️ Calendario PnL"
        )

        pnl_map = (
            df_grouped
            .set_index("fecha")[
                "beneficio_usd"
            ]
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

        encabezados = [
            "Dom",
            "Lun",
            "Mar",
            "Mié",
            "Jue",
            "Vie",
            "Sáb"
        ]

        cols = st.columns(7)

        for i, nombre in enumerate(
            encabezados
        ):

            cols[i].markdown(
                f"**{nombre}**"
            )

        for semana in semanas:

            cols = st.columns(7)

            for i, dia in enumerate(
                semana
            ):

                with cols[i]:

                    if dia == 0:

                        st.markdown(
                            "<div style='height:80px'></div>",
                            unsafe_allow_html=True
                        )

                        continue

                    fecha = datetime.date(
                        hoy.year,
                        hoy.month,
                        dia
                    )

                    valor = pnl_map.get(
                        str(fecha),
                        None
                    )

                    if valor is None:

                        bg = "#161b22"

                    elif valor > 0:

                        bg = "#34d399"

                    elif valor < 0:

                        bg = "#f87171"

                    else:

                        bg = "#161b22"

                    texto = (
                        ""
                        if valor is None
                        else f"${valor:,.0f}"
                    )

                    st.markdown(
                        f"""
                        <div style="
                        background:{bg};
                        border-radius:7px;
                        padding:7px;
                        height:80px;
                        text-align:center;
                        ">

                        <b>{dia}</b>

                        <div style="
                        margin-top:15px;
                        font-weight:bold;
                        color:#000;
                        ">

                        {texto}

                        </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        if not df_grouped.empty:

            fig = px.bar(
                df_grouped,
                x="fecha",
                y="beneficio_usd",
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
    # TAB 3 — CHAT
    # ========================================================

    with tab3:

        st.markdown(
            "### 💬 Chat de Auditoría IA"
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
            "Pregunta sobre tu operativa..."
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

                if df_trades.empty:

                    respuesta = (
                        "Todavía no tienes "
                        "operaciones registradas."
                    )

                else:

                    total = len(
                        df_trades
                    )

                    pnl = df_trades[
                        "beneficio_usd"
                    ].sum()

                    wins = len(
                        df_trades[
                            df_trades[
                                "beneficio_usd"
                            ] > 0
                        ]
                    )

                    win_rate = (
                        wins / total * 100
                    )

                    respuesta = (
                        f"Has registrado "
                        f"**{total} trades**. "
                        f"Tu PnL acumulado es "
                        f"**${pnl:,.2f}** y tu "
                        f"Win Rate es "
                        f"**{win_rate:.1f}%**."
                    )

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
            "### 🧮 Calculadora de Lotaje"
        )

        balance = st.number_input(
            "Balance ($)",
            value=float(
                st.session_state.capital_actual
            )
        )

        riesgo_pct = st.number_input(
            "Riesgo por operación (%)",
            value=1.0,
            step=0.25
        )

        stop_pips = st.number_input(
            "Stop Loss (pips/puntos)",
            value=20.0,
            step=1.0
        )

        riesgo_usd = (
            balance
            * riesgo_pct
            / 100
        )

        lotaje = (
            riesgo_usd
            / (stop_pips * 10)
            if stop_pips > 0
            else 0
        )

        c1, c2 = st.columns(2)

        c1.metric(
            "Riesgo máximo",
            f"${riesgo_usd:,.2f}"
        )

        c2.metric(
            "Lotaje estimado",
            f"{lotaje:.2f}"
        )

        st.warning(
            "⚠️ La equivalencia del lote cambia "
            "según el instrumento y broker."
        )


    # ========================================================
    # TAB 5 — AUDITORÍA VISUAL
    # ========================================================

    with tab5:

        st.markdown(
            "### 🤖 Auditoría Visual"
        )

        chart = st.file_uploader(
            "Subir gráfico",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="audit_visual"
        )

        if chart:

            st.image(
                chart,
                use_container_width=True
            )

            if st.button(
                "🔍 Auditar Entrada"
            ):

                st.info(
                    "La auditoría visual está "
                    "preparada para conectarse "
                    "con el modelo IA."
                )


    # ========================================================
    # TAB 6 — PROYECCIONES
    # ========================================================

    with tab6:

        st.markdown(
            "### 📈 Proyección de Capital"
        )

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

            pnl = (
                wins * ganancia_prom
                - losses * perdida_prom
            )

            capital += pnl

            datos.append(
                {
                    "Mes":
                        mes,
                    "Capital":
                        capital
                }
            )

        df_proy = pd.DataFrame(
            datos
        )

        st.metric(
            "Capital proyectado",
            f"${capital:,.2f}"
        )

        fig = px.line(
            df_proy,
            x="Mes",
            y="Capital",
            markers=True,
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
            "### 📓 Diario de Psicotrading"
        )

        st.caption(
            "Registra tu estado mental y "
            "disciplina."
        )

        reflexion = st.text_area(
            "Reflexión",
            height=200,
            placeholder=(
                "¿Respetaste tus reglas? "
                "¿Tuviste FOMO? "
                "¿Moviste el SL?"
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

        total_trades = len(
            df_trades
        )

        if not df_trades.empty:

            pnl_total = (
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
                wins
                / total_trades
                * 100
            )

            dias = (
                df_trades[
                    "fecha"
                ].nunique()
            )

        else:

            pnl_total = 0
            wins = 0
            losses = 0
            win_rate = 0
            dias = 0

        m1, m2, m3, m4 = st.columns(4)

        m1.metric(
            "PnL Total",
            f"${pnl_total:,.2f}"
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
            "Días operados",
            dias
        )

        st.markdown("---")

        if not df_trades.empty:

            fig = px.bar(
                df_trades,
                x="par",
                y="beneficio_usd",
                color="resultado",
                title="Rendimiento por Activo",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            columnas = [
                "fecha",
                "par",
                "direccion",
                "resultado",
                "beneficio_usd",
                "emocion",
                "timeframe"
            ]

            columnas_existentes = [
                c
                for c in columnas
                if c in df_trades.columns
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
                "para comenzar."
            )


# ============================================================
# 17. FLUJO PRINCIPAL
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
