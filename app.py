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
import math

from PIL import Image
from supabase import create_client, Client
from zoneinfo import ZoneInfo
import streamlit as st

# =========================================================
# 1. CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="AI Trading Journal & Auditor V8",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. CONFIGURACIÓN / SECRETOS
# =========================================================

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://lyzvcbjpoydeckxtbcq.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL", "google/gemini-2.5-flash")
ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL", "")

# =========================================================
# 3. PAGOS
# =========================================================

LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"

BINANCE_PAY_ID = "JORDAN_SANTI9"
LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"

# =========================================================
# 4. SUPABASE
# =========================================================

@st.cache_resource
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Faltan SUPABASE_URL y/o SUPABASE_KEY en Streamlit Secrets.")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================================================
# 5. ACTIVOS
# =========================================================

LISTA_ACTIVOS = [
    "🥇 XAU/USD (Oro)", "🥈 XAG/USD (Plata)", "🛢️ USOIL (Petróleo WTI)", "🛢️ UKOIL (Petróleo Brent)",
    "🌾 NGAS (Gas Natural)", "🪙 BTC/USD (Bitcoin)", "🪙 ETH/USD (Ethereum)", "🪙 SOL/USD (Solana)",
    "🪙 XRP/USD (Ripple)", "🪙 BNB/USD (Binance Coin)", "🪙 ADA/USD (Cardano)", "🪙 DOGE/USD (Dogecoin)",
    "📊 US100 (Nasdaq 100)", "📊 US30 (Dow Jones)", "📊 US500 (S&P 500)", "📊 GER40 (Dax Alemán)",
    "📊 UK100 (FTSE 100)", "📊 JP225 (Nikkei 225)", "💱 EUR/USD", "💱 GBP/USD", "💱 USD/JPY",
    "💱 AUD/USD", "💱 USD/CAD", "💱 USD/CHF", "💱 NZD/USD", "💱 EUR/GBP", "💱 EUR/JPY",
    "💱 GBP/JPY", "💱 AUD/JPY", "📈 NVDA (Nvidia)", "📈 TSLA (Tesla)", "📈 AAPL (Apple)",
    "📈 AMZN (Amazon)", "📈 MSFT (Microsoft)", "📈 GOOGL (Google)", "📈 META (Meta)",
    "📈 AMD (Advanced Micro Devices)", "📈 NFLX (Netflix)", "📈 COIN (Coinbase)"
]

ASSET_ALIASES = {
    "XAUUSD": "🥇 XAU/USD (Oro)", "XAU/USD": "🥇 XAU/USD (Oro)", "GOLD": "🥇 XAU/USD (Oro)", "ORO": "🥇 XAU/USD (Oro)",
    "XAGUSD": "🥈 XAG/USD (Plata)", "XAG/USD": "🥈 XAG/USD (Plata)", "SILVER": "🥈 XAG/USD (Plata)",
    "USOIL": "🛢️ USOIL (Petróleo WTI)", "WTI": "🛢️ USOIL (Petróleo WTI)",
    "UKOIL": "🛢️ UKOIL (Petróleo Brent)", "BRENT": "🛢️ UKOIL (Petróleo Brent)",
    "NGAS": "🌾 NGAS (Gas Natural)", "BTCUSD": "🪙 BTC/USD (Bitcoin)", "BTC/USD": "🪙 BTC/USD (Bitcoin)",
    "ETHUSD": "🪙 ETH/USD (Ethereum)", "ETH/USD": "🪙 ETH/USD (Ethereum)",
    "US100": "📊 US100 (Nasdaq 100)", "NASDAQ": "📊 US100 (Nasdaq 100)", "NAS100": "📊 US100 (Nasdaq 100)",
    "US30": "📊 US30 (Dow Jones)", "DOW": "📊 US30 (Dow Jones)", "DOWJONES": "📊 US30 (Dow Jones)",
    "US500": "📊 US500 (S&P 500)", "SP500": "📊 US500 (S&P 500)",
    "EURUSD": "💱 EUR/USD", "GBPUSD": "💱 GBP/USD", "USDJPY": "💱 USD/JPY", "AUDUSD": "💱 AUD/USD",
    "NVDA": "📈 NVDA (Nvidia)", "TSLA": "📈 TSLA (Tesla)", "AAPL": "📈 AAPL (Apple)", "AMZN": "📈 AMZN (Amazon)"
}

def normalizar_activo(activo):
    if not activo:
        return None
    texto = str(activo).upper().strip()
    texto = re.sub(r"[^\w/&.-]", "", texto)
    if texto in ASSET_ALIASES:
        return ASSET_ALIASES[texto]
    for alias, nombre in ASSET_ALIASES.items():
        if alias in texto:
            return nombre
    for nombre in LISTA_ACTIVOS:
        if texto in nombre.upper():
            return nombre
    return None

def normalizar_direccion(valor):
    if not valor:
        return "LONG 🟢"
    texto = str(valor).upper().strip()
    if any(x in texto for x in ["LONG", "BUY", "COMPRA", "LARGO"]):
        return "LONG 🟢"
    if any(x in texto for x in ["SHORT", "SELL", "VENTA", "CORTO"]):
        return "SHORT 🔴"
    return "LONG 🟢"

TIMEFRAMES = ["", "M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]

def normalizar_timeframe(valor):
    if not valor:
        return ""
    texto = str(valor).upper().strip().replace(" ", "")
    equivalencias = {"1MIN": "M1", "1M": "M1", "5MIN": "M5", "5M": "M5", "15MIN": "M15", "15M": "M15", "30MIN": "M30", "30M": "M30", "1H": "H1", "60M": "H1", "4H": "H4", "240M": "H4", "1D": "D1", "1DAY": "D1", "1W": "W1"}
    return equivalencias.get(texto, texto if texto in TIMEFRAMES else "")

def limpiar_numero(valor):
    if valor is None or isinstance(valor, bool):
        return None
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor) if not (math.isnan(valor) or math.isinf(valor)) else None
    texto = str(valor).strip().replace("$", "").replace("USD", "").replace("USDT", "").replace("≈", "").replace("~", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", texto)
    if not match:
        return None
    try:
        return float(match.group(0))
    except Exception:
        return None

# =========================================================
# ESTADO INICIAL
# =========================================================

DEFAULT_RULES = """• Acepta la pérdida antes de entrar.
• Corta pérdidas rápido.
• Deja correr los ganadores.
• Stop Loss obligatorio.
• No operar por impulso.
• Máximo 2 operaciones perdedoras por día.
• Después de una pérdida fuerte, detenerse."""

defaults = {
    "authenticated": False,
    "user": None,
    "chat_history": [],
    "nombre_trader": "Trader Pro",
    "capital_actual": 10000.0,
    "capital_meta": 15000.0,
    "reglas_disciplina": DEFAULT_RULES,
    "trade_asset": "",
    "trade_direction": "LONG 🟢",
    "trade_entry": 0.0,
    "trade_sl": 0.0,
    "trade_tp": 0.0,
    "trade_timeframe": "",
    "trade_result": "BE ⚪",
    "trade_emotion": "Disciplinado / Neutro 🧘",
    "trade_notes": "",
    "scan_result": None,
    "scan_message": "",
    "scan_error": "",
    "editing_trade_id": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# IMÁGENES (COMPRESIÓN OPTIMIZADA PARA EVITAR BROKEN PIPE)
# =========================================================

def procesar_imagen_b64(uploaded_file, max_size=(600, 450)):
    if uploaded_file is None:
        return ""
    try:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "LA", "P"):
            if image.mode == "P":
                image = image.convert("RGBA")
            background = Image.new("RGB", image.size, "white")
            if image.mode in ("RGBA", "LA"):
                background.paste(image, mask=image.getchannel("A"))
                image = background
            else:
                image = image.convert("RGB")
        else:
            image = image.convert("RGB")

        image.thumbnail(max_size)
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=55, optimize=True)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return "data:image/jpeg;base64," + encoded
    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return ""

def convertir_imagen_display(valor):
    if not valor:
        return None
    try:
        valor = str(valor)
        if valor.startswith("data:image"):
            return valor
        if len(valor) > 100:
            return "data:image/jpeg;base64," + valor
    except Exception:
        pass
    return None

# =========================================================
# SUPABASE TRADES
# =========================================================

def cargar_trades_usuario(user_id):
    try:
        client = get_supabase_client()
        response = client.table("trades").select("*").eq("user_id", user_id).order("fecha", desc=True).execute()
        return response.data or []
    except Exception as e:
        st.error(f"❌ Error cargando operaciones: {e}")
        return []

def guardar_trade_supabase(user_id, trade_data):
    try:
        client = get_supabase_client()
        data = dict(trade_data)
        data["user_id"] = user_id
        client.table("trades").insert(data).execute()
        return True
    except (BrokenPipeError, ConnectionResetError, OSError):
        st.error("🔌 Error de red temporal al enviar la imagen. Haz clic en 'GUARDAR TRADE' de nuevo.")
        return False
    except Exception as e:
        st.error(f"❌ Error guardando operación: {e}")
        return False

def actualizar_trade_supabase(trade_id, user_id, trade_data):
    try:
        client = get_supabase_client()
        data = dict(trade_data)
        data.pop("user_id", None)
        response = client.table("trades").update(data).eq("id", trade_id).eq("user_id", user_id).execute()
        return bool(response.data)
    except Exception as e:
        st.error(f"❌ Error actualizando operación: {e}")
        return False

def eliminar_trade_supabase(trade_id, user_id):
    try:
        client = get_supabase_client()
        client.table("trades").delete().eq("id", trade_id).eq("user_id", user_id).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error eliminando operación: {e}")
        return False

# =========================================================
# PARSER & IA VISUAL
# =========================================================

def extraer_json_ia(content):
    if not content:
        return None
    texto = str(content).strip()
    texto = re.sub(r"```json", "", texto, flags=re.IGNORECASE).replace("```", "").strip()
    inicio = texto.find("{")
    final = texto.rfind("}")
    if inicio >= 0 and final > inicio:
        texto = texto[inicio:final + 1]
    try:
        return json.loads(texto)
    except Exception:
        try:
            return json.loads(texto.replace("'", '"'))
        except Exception:
            return None

def analizar_captura_tradingview(image_bytes, mime_type="image/jpeg"):
    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY no configurada."}

    try:
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = """Analiza este gráfico de TradingView. Extrae:
        {"asset": string, "direction": "LONG"/"SHORT", "entry": float, "sl": float, "tp": float, "timeframe": string, "confidence": float}
        Devuelve ÚNICAMENTE un JSON sin explicaciones."""

        payload = {
            "model": OPENROUTER_MODEL,
            "temperature": 0,
            "messages": [
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64_img}"}}
                ]}
            ]
        }

        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"error": f"OpenRouter HTTP {response.status_code}"}

        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        data = extraer_json_ia(content)

        if not data:
            return {"error": "No se reconoció JSON de la IA."}

        return {
            "asset": normalizar_activo(data.get("asset")),
            "direction": normalizar_direccion(data.get("direction")),
            "entry": limpiar_numero(data.get("entry")),
            "sl": limpiar_numero(data.get("sl")),
            "tp": limpiar_numero(data.get("tp")),
            "timeframe": normalizar_timeframe(data.get("timeframe")),
            "confidence": limpiar_numero(data.get("confidence")) or 80
        }
    except Exception as e:
        return {"error": f"Error leyendo imagen: {e}"}

def aplicar_resultado_ia(resultado):
    if not resultado:
        return
    if resultado.get("asset"):
        st.session_state.trade_asset = resultado["asset"]
    if resultado.get("direction"):
        st.session_state.trade_direction = resultado["direction"]
    if resultado.get("entry") is not None:
        st.session_state.trade_entry = float(resultado["entry"])
    if resultado.get("sl") is not None:
        st.session_state.trade_sl = float(resultado["sl"])
    if resultado.get("tp") is not None:
        st.session_state.trade_tp = float(resultado["tp"])
    if resultado.get("timeframe"):
        st.session_state.trade_timeframe = resultado["timeframe"]

def limpiar_formulario_trade():
    st.session_state.trade_asset = ""
    st.session_state.trade_direction = "LONG 🟢"
    st.session_state.trade_entry = 0.0
    st.session_state.trade_sl = 0.0
    st.session_state.trade_tp = 0.0
    st.session_state.trade_timeframe = ""
    st.session_state.trade_result = "BE ⚪"
    st.session_state.trade_emotion = "Disciplinado / Neutro 🧘"
    st.session_state.trade_notes = ""
    st.session_state.scan_result = None
    st.session_state.scan_message = ""
    st.session_state.scan_error = ""

def calcular_rr(entry, sl, tp):
    try:
        riesgo = abs(float(entry) - float(sl))
        beneficio = abs(float(tp) - float(entry))
        return beneficio / riesgo if riesgo > 0 else 0.0
    except Exception:
        return 0.0

# =========================================================
# SESIONES Y HORA
# =========================================================

SESIONES = [
    {"nombre": "🇦🇺 Sídney", "zona": "Australia/Sydney", "inicio": 8, "fin": 17},
    {"nombre": "🇯🇵 Tokio", "zona": "Asia/Tokyo", "inicio": 9, "fin": 18},
    {"nombre": "🇬🇧 Londres", "zona": "Europe/London", "inicio": 8, "fin": 17},
    {"nombre": "🇺🇸 Nueva York", "zona": "America/New_York", "inicio": 8, "fin": 17}
]

def obtener_hora_zona(zona):
    try:
        return datetime.datetime.now(ZoneInfo(zona))
    except Exception:
        return datetime.datetime.now()

def mercado_abierto(zona, inicio, fin):
    try:
        ahora = obtener_hora_zona(zona)
        if ahora.weekday() >= 5:
            return False
        hora_decimal = ahora.hour + ahora.minute / 60
        return inicio <= hora_decimal < fin
    except Exception:
        return False

def render_sesion(nombre, zona, inicio, fin):
    ahora = obtener_hora_zona(zona)
    abierto = mercado_abierto(zona, inicio, fin)
    estado = "ABIERTO" if abierto else "CERRADO"
    color = "#34d399" if abierto else "#f87171"

    st.markdown(
        f"""
        <div class="session-card">
            <div class="session-title">{nombre}</div>
            <div class="session-time">{ahora.strftime("%H:%M:%S")}</div>
            <div class="session-date">{ahora.strftime("%d/%m/%Y")}</div>
            <div class="session-status" style="color:{color}; border-color:{color};">{estado}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def evaluar_suscripcion(user):
    if not user:
        return False, "Sin sesión", 0
    user_email = getattr(user, "email", "") or ""
    if ADMIN_EMAIL and user_email.lower() == ADMIN_EMAIL.lower():
        return True, "Creador / Admin 👑", 99999
    metadata = getattr(user, "user_metadata", {}) or {}
    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999
    created_at = getattr(user, "created_at", None)
    try:
        fecha_registro = datetime.datetime.fromisoformat(str(created_at).replace("Z", "+00:00")).date() if created_at else datetime.date.today()
    except Exception:
        fecha_registro = datetime.date.today()
    dias_usados = (datetime.date.today() - fecha_registro).days
    dias_restantes = max(0, 3 - dias_usados)
    return (True, f"Prueba Gratis ({dias_restantes} días rest.)", dias_restantes) if dias_usados <= 3 else (False, "Prueba Expirada 🛑", 0)

# =========================================================
# CSS
# =========================================================

def aplicar_estilos():
    css = """
    <style>
    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
    }
    p, label, h1, h2, h3, h4, span, div {
        color: #f0f3fa;
    }
    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0,210,255,.2) !important;
    }
    h1, h2 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #121721 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0,242,254,.5) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"] {
        background-color: #121721 !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }
    div[role="option"] { background-color: #121721 !important; color: #ffffff !important; }
    div[role="option"]:hover { background-color: #00f2fe !important; color: #000000 !important; }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0,210,255,.4) !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d2ff 0%, #2962ff 100%) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
    }
    .session-card {
        background: #161b22;
        border: 1px solid rgba(0,242,254,.25);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
    .session-title { font-size: 14px; font-weight: bold; }
    .session-time { color: #00f2fe !important; font-size: 22px; font-weight: 800; }
    .session-date { color: #8b98a8 !important; font-size: 11px; }
    .session-status { display: inline-block; margin-top: 6px; padding: 2px 8px; border: 1px solid; border-radius: 20px; font-size: 10px; font-weight: bold; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos()

# =========================================================
# PAYWALL Y AUTH
# =========================================================

def render_paywall():
    st.markdown("## 🔒 Tu período de prueba ha expirado")
    st.markdown("Continúa utilizando tu diario de trading activando tu acceso PRO:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[🟡 Pagar con Binance Pay]({LINK_BINANCE_INSCRIPCION})")
    with col2:
        st.markdown(f"[💎 Pagar $20 USD Anual]({LINK_BINANCE_ANUAL})")

def render_auth():
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("# ⚡ AI Trading Journal V8")
        st.markdown("Audita tu operativa con IA, registra tus emociones y lleva tu disciplina al siguiente nivel.")
    with right:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
        with tab_login:
            email = st.text_input("Correo electrónico", key="login_email")
            password = st.text_input("Contraseña", type="password", key="login_password")
            if st.button("Ingresar", key="login_button"):
                try:
                    client = get_supabase_client()
                    result = client.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = result.user
                    st.session_state.authenticated = True
                    st.rerun()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    st.error("🔌 Error temporal de conexión. Intenta de nuevo.")
                except Exception as e:
                    st.error(f"❌ Error al iniciar sesión: {e}")
        with tab_register:
            email = st.text_input("Correo electrónico", key="register_email")
            password = st.text_input("Contraseña", type="password", key="register_password")
            if st.button("Crear cuenta", key="register_button"):
                try:
                    client = get_supabase_client()
                    client.auth.sign_up({"email": email, "password": password})
                    st.success("Cuenta creada. Ya puedes iniciar sesión.")
                except Exception as e:
                    st.error(f"❌ Error: {e}")

# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar(estado_sub):
    with st.sidebar:
        user = st.session_state.user
        metadata = getattr(user, "user_metadata", {}) or {}
        nombre_actual = metadata.get("username", st.session_state.nombre_trader)
        foto_b64 = metadata.get("avatar_b64", "")

        st.markdown("### 👤 Perfil Trader")
        c1, c2 = st.columns([1, 2])
        with c1:
            foto_display = convertir_imagen_display(foto_b64)
            if foto_display:
                st.image(foto_display, width=65)
            else:
                st.markdown("<div style='font-size:45px; text-align:center;'>👤</div>", unsafe_allow_html=True)

        with c2:
            st.markdown(f"**{nombre_actual}**")
            st.caption(getattr(user, "email", ""))

        st.info(estado_sub)

        with st.expander("⚙️ Modificar Perfil"):
            nuevo_nombre = st.text_input("Nombre", value=nombre_actual, key="profile_name")
            nueva_foto = st.file_uploader("Nueva foto", type=["jpg", "jpeg", "png", "webp"], key="profile_photo")
            if st.button("Guardar perfil", key="save_profile"):
                try:
                    nueva_foto_b64 = foto_b64
                    if nueva_foto:
                        nueva_foto_b64 = base64.b64encode(nueva_foto.getvalue()).decode("utf-8")
                    client = get_supabase_client()
                    result = client.auth.update_user({"data": {"username": nuevo_nombre, "avatar_b64": nueva_foto_b64}})
                    st.session_state.user = result.user
                    st.session_state.nombre_trader = nuevo_nombre
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error: {e}")

        st.markdown("---")
        st.markdown("### 🎯 Meta de Cuenta")
        cap_actual = st.session_state.capital_actual
        cap_meta = st.session_state.capital_meta
        progreso = min(1.0, max(0.0, cap_actual / cap_meta)) if cap_meta > 0 else 0
        st.markdown(f"**Capital:** ${cap_actual:,.2f} / ${cap_meta:,.2f}")
        st.progress(progreso)

        with st.expander("🔧 Configurar meta"):
            st.session_state.capital_actual = st.number_input("Capital actual ($)", value=float(cap_actual), step=100.0, key="sidebar_capital")
            st.session_state.capital_meta = st.number_input("Meta ($)", value=float(cap_meta), step=500.0, key="sidebar_meta")

        st.markdown("---")
        st.markdown("### 🌎 Sesiones de Trading")
        for sesion in SESIONES:
            render_sesion(sesion["nombre"], sesion["zona"], sesion["inicio"], sesion["fin"])

        st.markdown("---")
        st.markdown("### 🎯 Mis Reglas")
        with st.expander("✏️ Editar reglas"):
            nuevas_reglas = st.text_area("Reglas", value=st.session_state.reglas_disciplina, height=150, key="rules_editor")
            if st.button("Guardar reglas", key="save_rules"):
                st.session_state.reglas_disciplina = nuevas_reglas
                st.rerun()

        st.markdown(st.session_state.reglas_disciplina)

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", key="logout"):
            try:
                get_supabase_client().auth.sign_out()
            except Exception:
                pass
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# =========================================================
# VISTA REGISTRAR Y TRACK RECORD
# =========================================================

def render_nuevo_trade(user_id):
    st.markdown("### ➕ Registrar nueva operación")

    left, right = st.columns([1.2, 1])
    with right:
        st.markdown("### 🖼️ Captura del Setup")
        upload_before = st.file_uploader("1️⃣ ANTES de la operación", type=["png", "jpg", "jpeg", "webp"], key="new_trade_before")
        upload_after = st.file_uploader("2️⃣ DESPUÉS de la operación", type=["png", "jpg", "jpeg", "webp"], key="new_trade_after")

        if upload_before:
            st.image(upload_before, caption="SETUP ANTES", use_container_width=True)
            if st.button("🧠 ESCANEAR CON IA", key="scan_new_trade", use_container_width=True):
                with st.spinner("Leyendo captura..."):
                    res = analizar_captura_tradingview(upload_before.getvalue(), upload_before.type)
                if res.get("error"):
                    st.error(res["error"])
                else:
                    aplicar_resultado_ia(res)
                    st.toast("Datos detectados por la IA", icon="✨")
                    st.rerun()

        if upload_after:
            st.image(upload_after, caption="RESULTADO DESPUÉS", use_container_width=True)

        pnl = st.number_input("Ganancia / Pérdida ($)", value=0.0, step=10.0, key="new_trade_pnl")

    with left:
        fecha = st.date_input("Fecha", datetime.date.today(), key="new_trade_date")
        c1, c2 = st.columns(2)

        with c1:
            asset_opts = ["— Seleccionar —"] + LISTA_ACTIVOS
            asset_idx = asset_opts.index(st.session_state.trade_asset) if st.session_state.trade_asset in asset_opts else 0
            selected_asset = st.selectbox("Activo / Par", asset_opts, index=asset_idx, key="trade_asset_widget")
            st.session_state.trade_asset = "" if selected_asset.startswith("—") else selected_asset

            dir_opts = ["LONG 🟢", "SHORT 🔴"]
            dir_idx = dir_opts.index(st.session_state.trade_direction) if st.session_state.trade_direction in dir_opts else 0
            st.session_state.trade_direction = st.radio("Dirección", dir_opts, index=dir_idx, horizontal=True, key="trade_direction_widget")

            st.session_state.trade_entry = st.number_input("Precio Entrada", min_value=0.0, value=float(st.session_state.trade_entry), format="%.5f", key="trade_entry_widget")
            st.session_state.trade_sl = st.number_input("Stop Loss", min_value=0.0, value=float(st.session_state.trade_sl), format="%.5f", key="trade_sl_widget")

        with c2:
            st.session_state.trade_tp = st.number_input("Take Profit", min_value=0.0, value=float(st.session_state.trade_tp), format="%.5f", key="trade_tp_widget")
            tf_idx = TIMEFRAMES.index(st.session_state.trade_timeframe) if st.session_state.trade_timeframe in TIMEFRAMES else 0
            st.session_state.trade_timeframe = st.selectbox("Timeframe", TIMEFRAMES, index=tf_idx, key="trade_timeframe_widget")

            rr = calcular_rr(st.session_state.trade_entry, st.session_state.trade_sl, st.session_state.trade_tp)
            st.metric("Risk : Reward", f"1 : {rr:.2f}")
            resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"], key="trade_result")

        emocion = st.selectbox("Estado emocional", ["Disciplinado / Neutro 🧘", "Ansioso ⚡", "FOMO 🚀", "Venganza 🛑"], key="trade_emotion")
        notas = st.text_area("Notas emocionales", key="trade_notes")

        b1, b2 = st.columns(2)
        with b1:
            guardar = st.button("💾 GUARDAR TRADE", key="save_new_trade", use_container_width=True)
        with b2:
            if st.button("🧹 LIMPIAR", key="clear_new_trade", use_container_width=True):
                limpiar_formulario_trade()
                st.rerun()

        if guardar:
            if not st.session_state.trade_asset:
                st.error("Selecciona un activo.")
            elif st.session_state.trade_entry <= 0:
                st.error("La entrada debe ser mayor a 0.")
            else:
                data = {
                    "fecha": str(fecha),
                    "par": st.session_state.trade_asset,
                    "direccion": st.session_state.trade_direction,
                    "precio_entrada": float(st.session_state.trade_entry),
                    "stop_loss": float(st.session_state.trade_sl),
                    "take_profit": float(st.session_state.trade_tp),
                    "rr": float(rr),
                    "timeframe": st.session_state.trade_timeframe,
                    "resultado": resultado,
                    "emocion": emocion,
                    "notas_emocionales": notas,
                    "beneficio_usd": float(pnl),
                    "trades_cant": 1,
                    "img_before": procesar_imagen_b64(upload_before) if upload_before else "",
                    "img_after": procesar_imagen_b64(upload_after) if upload_after else ""
                }

                if guardar_trade_supabase(user_id, data):
                    st.success("✅ Trade guardado correctamente.")
                    limpiar_formulario_trade()
                    st.rerun()

def render_track_record(df_trades, user_id):
    st.markdown("### 📅 Track Record & Calendario PnL")
    if df_trades.empty:
        st.info("Aún no tienes operaciones registradas.")
        return

    total_pnl = float(df_trades["beneficio_usd"].sum())
    wins = len(df_trades[df_trades["beneficio_usd"] > 0])
    losses = len(df_trades[df_trades["beneficio_usd"] < 0])
    total = len(df_trades)
    win_rate = (wins / total * 100) if total else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("PnL Total", f"${total_pnl:,.2f}")
    c2.metric("Win Rate", f"{win_rate:.1f}%")
    c3.metric("Trades", total)
    c4.metric("Wins / Losses", f"{wins} / {losses}")

    st.markdown("---")

    # CALENDARIO MENSUAL
    df_grouped = df_trades.groupby('fecha').agg({'beneficio_usd': 'sum', 'trades_cant': 'count'}).reset_index()
    pnl_map = df_grouped.set_index('fecha')['beneficio_usd'].to_dict() if not df_grouped.empty else {}
    trades_map = df_grouped.set_index('fecha')['trades_cant'].to_dict() if not df_grouped.empty else {}

    hoy = datetime.date.today()
    mes_dias = calendar.Calendar(firstweekday=6).monthdayscalendar(hoy.year, hoy.month)
    
    dias_header = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    cols_header = st.columns(7)
    for idx, col in enumerate(cols_header):
        with col:
            st.markdown(f"<div style='text-align:center; font-weight:bold; color:#f0f3fa;'>{dias_header[idx]}</div>", unsafe_allow_html=True)

    for semana in mes_dias:
        cols_sem = st.columns(7)
        for day_idx, day_num in enumerate(semana):
            with cols_sem[day_idx]:
                if day_num == 0:
                    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
                else:
                    f_date = datetime.date(hoy.year, hoy.month, day_num)
                    f_key = str(f_date)
                    pnl_val = pnl_map.get(f_key, None)
                    num_trades = trades_map.get(f_key, 0)
                    border_css = "border: 2px solid #00f2fe;" if f_date == hoy else "border: 1px solid #161b22;"

                    if pnl_val is None:
                        bg_color, txt_color, pnl_html, trades_html = "#161b22", "#f0f3fa", "", ""
                    elif pnl_val > 0:
                        bg_color, txt_color = "#34d399", "#000000"
                        pnl_fmt = f"${pnl_val:,.0f}" if pnl_val < 1000 else f"${pnl_val/1000:.1f}k"
                        pnl_html = f"<div style='font-weight:bold; font-size:1.1rem; color:{txt_color};'>+{pnl_fmt}</div>"
                        trades_html = f"<div style='font-size:0.8rem; color:{txt_color};'>{num_trades} trade</div>"
                    elif pnl_val < 0:
                        bg_color, txt_color = "#f87171", "#000000"
                        pnl_fmt = f"-${abs(pnl_val):,.0f}" if abs(pnl_val) < 1000 else f"-${abs(pnl_val)/1000:.1f}k"
                        pnl_html = f"<div style='font-weight:bold; font-size:1.1rem; color:{txt_color};'>{pnl_fmt}</div>"
                        trades_html = f"<div style='font-size:0.8rem; color:{txt_color};'>{num_trades} trade</div>"
                    else:
                        bg_color, txt_color, pnl_html, trades_html = "#161b22", "#ffffff", "<div style='font-weight:bold; font-size:1.1rem;'>$0</div>", f"<div style='font-size:0.7rem;'>{num_trades} trades</div>"

                    today_tag = " <span style='font-size:0.6rem; color:#00f2fe;'>(HOY)</span>" if f_date == hoy else ""
                    st.markdown(f"""<div style="background-color: {bg_color}; {border_css} border-radius: 6px; padding: 6px; height: 80px; display: flex; flex-direction: column; justify-content: space-between;"><div style="font-size:0.75rem; font-weight:bold; color:{txt_color};">{day_num}{today_tag}</div><div style="text-align:center;">{pnl_html}{trades_html}</div></div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Historial Detallado y Capturas (ANTES / DESPUÉS)")

    for _, row in df_trades.iterrows():
        trade_id = row.get("id")
        pnl_val = float(row.get("beneficio_usd", 0) or 0)
        titulo = f"📅 {row.get('fecha', '')} | {row.get('par', '')} | {row.get('resultado', '')} | PnL: ${pnl_val:,.2f}"

        with st.expander(titulo):
            c1, c2, c3 = st.columns([1.2, 2, 2])
            with c1:
                st.markdown("#### ⚙️ Detalle")
                st.write(f"**Activo:** {row.get('par', '-')}")
                st.write(f"**Dirección:** {row.get('direccion', '-')}")
                st.write(f"**Entrada:** {row.get('precio_entrada', 0)}")
                st.write(f"**SL:** {row.get('stop_loss', 0)} | **TP:** {row.get('take_profit', 0)}")
                st.write(f"**Emoción:** {row.get('emocion', '-')}")

                if st.button("🗑️ Eliminar Trade", key=f"delete_{trade_id}"):
                    if eliminar_trade_supabase(trade_id, user_id):
                        st.success("Trade eliminado.")
                        st.rerun()

            with c2:
                st.markdown("**1️⃣ ANTES**")
                img = convertir_imagen_display(row.get("img_before"))
                if img:
                    st.image(img, use_container_width=True)
                else:
                    st.info("📷 Sin captura")

            with c3:
                st.markdown("**2️⃣ DESPUÉS**")
                img = convertir_imagen_display(row.get("img_after"))
                if img:
                    st.image(img, use_container_width=True)
                else:
                    st.info("📷 Sin captura")

# =========================================================
# MAIN DASHBOARD
# =========================================================

def render_dashboard():
    tiene_acceso, estado_sub, _ = evaluar_suscripcion(st.session_state.user)
    render_sidebar(estado_sub)

    if not tiene_acceso:
        render_paywall()
        return

    user_id = st.session_state.user.id
    trades_db = cargar_trades_usuario(user_id)
    df_trades = pd.DataFrame(trades_db)

    if not df_trades.empty:
        if "beneficio_usd" not in df_trades.columns:
            df_trades["beneficio_usd"] = 0.0
        if "fecha" not in df_trades.columns:
            df_trades["fecha"] = str(datetime.date.today())
        df_trades["beneficio_usd"] = pd.to_numeric(df_trades["beneficio_usd"], errors="coerce").fillna(0)

    st.markdown("## ⚡ AI Trading Journal & Auditor V8")

    tabs = st.tabs(["➕ Registrar Trade", "📅 Track Record", "💬 Chat IA", "📊 Dashboard"])
    with tabs[0]:
        render_nuevo_trade(user_id)
    with tabs[1]:
        render_track_record(df_trades, user_id)
    with tabs[2]:
        st.markdown("### 💬 Chat IA")
        st.info("Escribe en el chat para analizar tus estadísticas con IA.")
    with tabs[3]:
        st.markdown("### 📊 Dashboard Operativo")
        if not df_trades.empty:
            st.dataframe(df_trades, use_container_width=True, hide_index=True)
        else:
            st.info("Sin registros.")

def main():
    if not st.session_state.authenticated:
        render_auth()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
