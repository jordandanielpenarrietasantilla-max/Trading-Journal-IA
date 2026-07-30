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
from zoneinfo import ZoneInfo


# =========================================================
# 1. CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="AI Trading Journal & Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. SECRETOS
# ==========================================

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
    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# =========================================================
# 5. ESTADO INICIAL
# =========================================================

DEFAULT_RULES = """• Acepta la pérdida antes de entrar.
• Corta pérdidas rápido.
• Deja correr los ganadores.
• Máximo 2 operaciones perdedoras por día."""

defaults = {
    "authenticated": False,
    "user": None,
    "chat_history": [],
    "nombre_trader": "Trader Pro",
    "capital_actual": 10000.0,
    "capital_meta": 15000.0,
    "reglas_disciplina": DEFAULT_RULES,

    # Datos detectados por IA
    "auto_entry": 0.0,
    "auto_sl": 0.0,
    "auto_tp": 0.0,
    "auto_asset": "",
    "auto_direction": "LONG 🟢",
    "auto_timeframe": "",

    # Resultado del último escaneo
    "scan_result": None,
    "scan_message": ""
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 6. ACTIVOS
# =========================================================

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


# =========================================================
# 7. MAPA DE ACTIVOS
# =========================================================

ASSET_ALIASES = {
    "XAUUSD": "🥇 XAU/USD (Oro)",
    "XAU/USD": "🥇 XAU/USD (Oro)",
    "GOLD": "🥇 XAU/USD (Oro)",
    "ORO": "🥇 XAU/USD (Oro)",

    "XAGUSD": "🥈 XAG/USD (Plata)",
    "XAG/USD": "🥈 XAG/USD (Plata)",
    "SILVER": "🥈 XAG/USD (Plata)",

    "USOIL": "🛢️ USOIL (Petróleo WTI)",
    "WTI": "🛢️ USOIL (Petróleo WTI)",

    "UKOIL": "🛢️ UKOIL (Petróleo Brent)",
    "BRENT": "🛢️ UKOIL (Petróleo Brent)",

    "NGAS": "🌾 NGAS (Gas Natural)",

    "BTCUSD": "🪙 BTC/USD (Bitcoin)",
    "BTC/USD": "🪙 BTC/USD (Bitcoin)",

    "ETHUSD": "🪙 ETH/USD (Ethereum)",
    "ETH/USD": "🪙 ETH/USD (Ethereum)",

    "SOLUSD": "🪙 SOL/USD (Solana)",
    "XRPUSD": "🪙 XRP/USD (Ripple)",
    "BNBUSD": "🪙 BNB/USD (Binance Coin)",
    "ADAUSD": "🪙 ADA/USD (Cardano)",
    "DOGEUSD": "🪙 DOGE/USD (Dogecoin)",

    "US100": "📊 US100 (Nasdaq 100)",
    "NASDAQ": "📊 US100 (Nasdaq 100)",
    "NAS100": "📊 US100 (Nasdaq 100)",

    "US30": "📊 US30 (Dow Jones)",
    "DOW": "📊 US30 (Dow Jones)",

    "US500": "📊 US500 (S&P 500)",
    "SP500": "📊 US500 (S&P 500)",

    "GER40": "📊 GER40 (Dax Alemán)",
    "DAX": "📊 GER40 (Dax Alemán)",

    "UK100": "📊 UK100 (FTSE 100)",
    "JP225": "📊 JP225 (Nikkei 225)",

    "EURUSD": "💱 EUR/USD",
    "GBPUSD": "💱 GBP/USD",
    "USDJPY": "💱 USD/JPY",
    "AUDUSD": "💱 AUD/USD",
    "USDCAD": "💱 USD/CAD",
    "USDCHF": "💱 USD/CHF",
    "NZDUSD": "💱 NZD/USD",
    "EURGBP": "💱 EUR/GBP",
    "EURJPY": "💱 EUR/JPY",
    "GBPJPY": "💱 GBP/JPY",
    "AUDJPY": "💱 AUD/JPY",

    "NVDA": "📈 NVDA (Nvidia)",
    "TSLA": "📈 TSLA (Tesla)",
    "AAPL": "📈 AAPL (Apple)",
    "AMZN": "📈 AMZN (Amazon)",
    "MSFT": "📈 MSFT (Microsoft)",
    "GOOGL": "📈 GOOGL (Google)",
    "META": "📈 META (Meta / Facebook)",
    "AMD": "📈 AMD (Advanced Micro Devices)",
    "NFLX": "📈 NFLX (Netflix)",
    "COIN": "📈 COIN (Coinbase)"
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


def normalizar_timeframe(valor):
    if not valor:
        return ""

    texto = str(valor).upper().strip()
    equivalencias = {
        "1MIN": "M1", "1M": "M1", "5MIN": "M5", "5M": "M5",
        "15MIN": "M15", "15M": "M15", "30MIN": "M30", "30M": "M30",
        "1H": "H1", "60M": "H1", "4H": "H4", "240M": "H4",
        "1D": "D1", "1DAY": "D1", "1W": "W1", "1WEEK": "W1"
    }

    if texto in equivalencias:
        return equivalencias[texto]
    if texto in ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]:
        return texto

    return ""


# =========================================================
# 8. IMÁGENES
# =========================================================

def procesar_imagen_b64(uploaded_file, max_size=(1200, 900)):
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
        image.save(buffer, format="JPEG", quality=78, optimize=True)
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
        return None
    return None


# =========================================================
# 9. SUPABASE - TRADES
# =========================================================

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
        st.error(f"❌ Error cargando operaciones: {e}")
        return []


def guardar_trade_supabase(user_id, trade_data):
    try:
        client = get_supabase_client()
        data = dict(trade_data)
        data["user_id"] = user_id
        client.table("trades").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"❌ Error guardando operación: {e}")
        return False


def actualizar_trade_supabase(trade_id, user_id, trade_data):
    try:
        client = get_supabase_client()
        data = dict(trade_data)
        data.pop("user_id", None)
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
        st.error(f"❌ Error actualizando operación: {e}")
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
        st.error(f"❌ Error eliminando operación: {e}")
        return False


# =========================================================
# 10. IA & PARSER
# =========================================================

def extraer_json_ia(content):
    if not content:
        return None
    texto = str(content).strip()
    texto = texto.replace("```json", "").replace("```JSON", "").replace("```", "").strip()
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        texto = match.group(0)
    try:
        return json.loads(texto)
    except Exception:
        try:
            texto2 = texto.replace("'", '"')
            return json.loads(texto2)
        except Exception:
            return None


def limpiar_numero(valor):
    if valor is None:
        return 0.0
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor).strip().replace(",", "").replace("$", "").replace("USD", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", texto)
    if not match:
        return 0.0
    try:
        return float(match.group(0))
    except Exception:
        return 0.0


def analizar_captura_tradingview(image_bytes):
    if not OPENROUTER_API_KEY:
        return {"error": "OPENROUTER_API_KEY no configurada."}

    try:
        b64_img = base64.b64encode(image_bytes).decode("utf-8")
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        prompt = """
        Analiza este gráfico de TradingView. Extrae los datos numéricos de la herramienta de posición (Risk/Reward):
        Devuelve ÚNICAMENTE un JSON con estas claves exactas:
        {"asset": "XAU/USD", "direction": "LONG", "entry": float, "sl": float, "tp": float, "timeframe": "H1", "confidence": 90}
        Si no encuentras algún dato pon null. No agregues texto extra.
        """

        payload = {
            "model": "openai/gpt-4o-mini",
            "temperature": 0,
            "messages": [
                {"role": "system", "content": "Eres un extractor visual preciso de datos de trading."},
                {"role": "user", "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + b64_img}}
                ]}
            ]
        }

        response = requests.post("[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)", headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return {"error": f"OpenRouter HTTP {response.status_code}: {response.text[:500]}"}

        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        data = extraer_json_ia(content)

        if not data:
            return {"error": "La IA respondió, pero no devolvió JSON válido.", "raw": content}

        return {
            "asset": normalizar_activo(data.get("asset")),
            "direction": normalizar_direccion(data.get("direction")),
            "entry": limpiar_numero(data.get("entry")),
            "sl": limpiar_numero(data.get("sl")),
            "tp": limpiar_numero(data.get("tp")),
            "timeframe": normalizar_timeframe(data.get("timeframe")),
            "confidence": limpiar_numero(data.get("confidence"))
        }
    except Exception as e:
        return {"error": f"Error analizando imagen: {e}"}


def aplicar_resultado_ia_a_formulario(resultado):
    if not resultado:
        return
    if resultado.get("asset"):
        st.session_state["auto_asset"] = resultado["asset"]
    if resultado.get("direction"):
        st.session_state["auto_direction"] = resultado["direction"]
    if resultado.get("entry", 0) > 0:
        st.session_state["auto_entry"] = float(resultado["entry"])
    if resultado.get("sl", 0) > 0:
        st.session_state["auto_sl"] = float(resultado["sl"])
    if resultado.get("tp", 0) > 0:
        st.session_state["auto_tp"] = float(resultado["tp"])
    if resultado.get("timeframe"):
        st.session_state["auto_timeframe"] = resultado["timeframe"]


# =========================================================
# 11. SESIONES
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


# =========================================================
# 12. SUSCRIPCIÓN
# =========================================================

def evaluar_suscripcion(user):
    if not user:
        return False, "Sin sesión", 0

    user_email = getattr(user, "email", "") or ""
    if user_email.lower() == "jordandanielpenarrietasantilla@gmail.com":
        return True, "Creador / Admin 👑", 99999

    metadata = getattr(user, "user_metadata", {}) or {}
    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999

    created_at = getattr(user, "created_at", None)
    try:
        if created_at:
            fecha_registro = datetime.datetime.fromisoformat(str(created_at).replace("Z", "+00:00")).date()
        else:
            fecha_registro = datetime.date.today()
    except Exception:
        fecha_registro = datetime.date.today()

    dias_usados = (datetime.date.today() - fecha_registro).days
    dias_restantes = max(0, 3 - dias_usados)

    if dias_usados <= 3:
        return True, f"Prueba Gratis ({dias_restantes} días rest.)", dias_restantes

    return False, "Prueba Expirada 🛑", 0


# =========================================================
# 13. CSS
# =========================================================

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
    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0, 210, 255, 0.2) !important;
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
        border: 1px solid rgba(0, 242, 254, 0.5) !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] input {
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], div[role="listbox"], ul[role="listbox"] {
        background-color: #121721 !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }
    div[role="option"], li[role="option"], li[data-baseweb="option"] {
        background-color: #121721 !important;
        color: #ffffff !important;
    }
    div[role="option"]:hover, li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #00f2fe !important;
        color: #000000 !important;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 8px !important;
    }
    .stButton > button {
        background: linear-gradient(135deg, #00d2ff 0%, #2962ff 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    .session-card {
        background: #161b22;
        border: 1px solid rgba(0, 242, 254, 0.25);
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        text-align: center;
    }
    .session-title { font-size: 14px; font-weight: bold; }
    .session-time { color: #00f2fe !important; font-size: 22px; font-weight: 800; }
    .session-date { color: #8b98a8 !important; font-size: 11px; }
    .session-status { display: inline-block; margin-top: 6px; padding: 2px 8px; border: 1px solid; border-radius: 20px; font-size: 10px; font-weight: bold; }
    .paywall-card {
        background-color: #161b22;
        border: 1px solid #f0b90b;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos()


# =========================================================
# 14. PAYWALL
# =========================================================

def render_paywall():
    st.markdown("## 🔒 Tu período de prueba ha expirado")
    st.markdown("Continúa utilizando tu diario de trading, Track Record y herramientas de IA activando tu acceso PRO.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="paywall-card">
            <h3>🟡 Suscripción Mensual</h3>
            <h2>$5.00 USD</h2>
            <p>Luego $2.50 USD / mes</p>
            <hr>
            <p>✔️ Acceso ilimitado<br>✔️ Track Record<br>✔️ Auditoría IA<br>✔️ Psicotrading<br>✔️ Sin contrato</p>
            <a href="{LINK_BINANCE_INSCRIPCION}" target="_blank">
                <button style="background:#f0b90b; color:#000; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%;">
                    🟡 Pagar con Binance Pay
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="paywall-card">
            <h3>💎 Acceso Anual</h3>
            <h2>$20.00 USD</h2>
            <p>Ahorra frente al plan mensual</p>
            <hr>
            <p>🌟 1 año completo<br>🔒 Pago único<br>🎁 Actualizaciones futuras<br>🧠 IA prioritaria</p>
            <a href="{LINK_BINANCE_ANUAL}" target="_blank">
                <button style="background:#00f2fe; color:#000; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%;">
                    💎 Pagar $20 USD
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📲 Renovación")
        st.code(f"Binance Pay ID: {BINANCE_PAY_ID}")
        st.markdown(f"[Renovación mensual $2.50]({LINK_BINANCE_RECURRENTE})")
    with c2:
        st.markdown("### 💬 Confirmar pago")
        st.markdown(f"""
        <a href="{LINK_TELEGRAM_SOPORTE}" target="_blank">
            <button style="background:#0088cc; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; width:100%;">
                💬 Enviar comprobante
            </button>
        </a>
        """, unsafe_allow_html=True)


# =========================================================
# 15. AUTENTICACIÓN
# =========================================================

def render_auth():
    left, right = st.columns([1.3, 1])

    with left:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("""
        ### Tu operativa. Tus datos. Tu disciplina.
        Registra tus operaciones, analiza tus emociones, controla tu Track Record y utiliza IA para auditar tu proceso de trading.
        """)
        st.markdown("---")
        st.markdown("""
        **Incluye:**
        🧠 Psicotrading | 📊 Track Record | 📅 Calendario PnL  
        🖼️ Antes / Después | 🤖 Auditoría IA | 🌎 Sesiones de mercado
        """)

    with right:
        tab_login, tab_register, tab_reset = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse", "🔐 Recuperar"])

        with tab_login:
            st.markdown("### Ingresa a tu cuenta")
            email = st.text_input("Correo electrónico", key="login_email")
            password = st.text_input("Contraseña", type="password", key="login_password")

            if st.button("Ingresar", key="login_button"):
                if not email or not password:
                    st.warning("Completa correo y contraseña.")
                else:
                    try:
                        client = get_supabase_client()
                        result = client.auth.sign_in_with_password({"email": email, "password": password})
                        st.session_state.user = result.user
                        st.session_state.authenticated = True
                        st.success("Inicio de sesión correcto.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ No se pudo iniciar sesión: {e}")

        with tab_register:
            st.markdown("### Crear cuenta")
            email = st.text_input("Correo electrónico", key="register_email")
            password = st.text_input("Contraseña", type="password", key="register_password")
            password2 = st.text_input("Repetir contraseña", type="password", key="register_password_2")

            if st.button("Crear cuenta y probar", key="register_button"):
                if not email or not password:
                    st.warning("Completa todos los campos.")
                elif password != password2:
                    st.error("Las contraseñas no coinciden.")
                elif len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres.")
                else:
                    try:
                        client = get_supabase_client()
                        result = client.auth.sign_up({"email": email, "password": password})
                        if result.user:
                            st.success("Cuenta creada. Ahora puedes iniciar sesión.")
                    except Exception as e:
                        st.error(f"❌ Error registrando usuario: {e}")

        with tab_reset:
            st.markdown("### Recuperar contraseña")
            email = st.text_input("Correo registrado", key="reset_email")

            if st.button("Enviar enlace", key="reset_button"):
                if not email:
                    st.warning("Introduce tu correo.")
                else:
                    try:
                        client = get_supabase_client()
                        app_url = "[https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/](https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/)"
                        client.auth.reset_password_for_email(email, {"redirectTo": app_url})
                        st.success("📩 Revisa tu correo y Spam.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")


# =========================================================
# 16. SIDEBAR
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

        if "PRO" in estado_sub or "Admin" in estado_sub:
            st.success(f"💎 {estado_sub}")
        else:
            st.info(f"⏳ {estado_sub}")

        with st.expander("⚙️ Modificar Perfil"):
            nuevo_nombre = st.text_input("Nombre", value=nombre_actual, key="profile_name")
            nueva_foto = st.file_uploader("Nueva foto", type=["jpg", "jpeg", "png", "webp"], key="profile_photo")

            if st.button("Guardar perfil", key="save_profile"):
                try:
                    nueva_foto_b64 = foto_b64
                    if nueva_foto:
                        nueva_foto_b64 = base64.b64encode(nueva_foto.getvalue()).decode("utf-8")

                    client = get_supabase_client()
                    result = client.auth.update_user({
                        "data": {
                            "username": nuevo_nombre,
                            "avatar_b64": nueva_foto_b64
                        }
                    })
                    st.session_state.user = result.user
                    st.session_state.nombre_trader = nuevo_nombre
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error actualizando perfil: {e}")

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
            st.session_state.chat_history = []
            st.rerun()


# =========================================================
# 17. EDITAR TRADE
# =========================================================

def editar_trade_ui(row, user_id):
    trade_id = row.get("id")
    fecha_original = row.get("fecha", str(datetime.date.today()))

    try:
        fecha_default = datetime.date.fromisoformat(str(fecha_original)[:10])
    except Exception:
        fecha_default = datetime.date.today()

    par_actual = normalizar_activo(row.get("par", "")) or LISTA_ACTIVOS[0]
    direccion_actual = normalizar_direccion(row.get("direccion", ""))
    resultados = ["WIN 🟢", "LOSS 🔴", "BE ⚪"]
    resultado_actual = row.get("resultado", "BE ⚪")
    if resultado_actual not in resultados:
        resultado_actual = "BE ⚪"

    emociones = [
        "Disciplinado / Neutro 🧘", "Ansioso ⚡", 
        "FOMO / Miedo a perderse el movimiento 🚀", 
        "Venganza / Frustrado 🛑", "Eufórico / Sobre-confiado 😎"
    ]
    emocion_actual = row.get("emocion", emociones[0])
    if emocion_actual not in emociones:
        emocion_actual = emociones[0]

    c1, c2 = st.columns(2)
    with c1:
        fecha = st.date_input("Fecha", value=fecha_default, key=f"edit_fecha_{trade_id}")
        par = st.selectbox("Activo", LISTA_ACTIVOS, index=LISTA_ACTIVOS.index(par_actual), key=f"edit_par_{trade_id}")
        direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], index=(0 if direccion_actual == "LONG 🟢" else 1), horizontal=True, key=f"edit_dir_{trade_id}")
        entrada = st.number_input("Precio de entrada", value=float(row.get("precio_entrada", 0) or 0), format="%.5f", key=f"edit_entry_{trade_id}")
        sl = st.number_input("Stop Loss", value=float(row.get("stop_loss", 0) or 0), format="%.5f", key=f"edit_sl_{trade_id}")
        tp = st.number_input("Take Profit", value=float(row.get("take_profit", 0) or 0), format="%.5f", key=f"edit_tp_{trade_id}")

        timeframes = ["", "M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]
        tf_actual = normalizar_timeframe(row.get("timeframe", ""))
        timeframe = st.selectbox("Timeframe", timeframes, index=(timeframes.index(tf_actual) if tf_actual in timeframes else 0), key=f"edit_tf_{trade_id}")

    with c2:
        riesgo = abs(entrada - sl)
        beneficio = abs(tp - entrada)
        rr = beneficio / riesgo if riesgo > 0 else 0

        st.metric("Risk : Reward", f"1 : {rr:.2f}")
        resultado = st.selectbox("Resultado", resultados, index=resultados.index(resultado_actual), key=f"edit_result_{trade_id}")
        emocion = st.selectbox("Estado emocional", emociones, index=emociones.index(emocion_actual), key=f"edit_emotion_{trade_id}")
        pnl = st.number_input("PnL ($)", value=float(row.get("beneficio_usd", 0) or 0), step=10.0, key=f"edit_pnl_{trade_id}")
        notas = st.text_area("Notas emocionales", value=row.get("notas_emocionales", "") or "", height=130, key=f"edit_notes_{trade_id}")

        imagen_before = st.file_uploader("Cambiar ANTES", type=["png", "jpg", "jpeg", "webp"], key=f"edit_before_{trade_id}")
        imagen_after = st.file_uploader("Cambiar DESPUÉS", type=["png", "jpg", "jpeg", "webp"], key=f"edit_after_{trade_id}")

    old_before = row.get("img_before", "")
    old_after = row.get("img_after", "")

    p1, p2 = st.columns(2)
    with p1:
        st.markdown("**🖼️ ANTES actual**")
        img = convertir_imagen_display(old_before)
        if img:
            st.image(img, use_container_width=True)
        else:
            st.caption("No hay imagen.")

    with p2:
        st.markdown("**🖼️ DESPUÉS actual**")
        img = convertir_imagen_display(old_after)
        if img:
            st.image(img, use_container_width=True)
        else:
            st.caption("No hay imagen.")

    save, cancel = st.columns(2)
    with save:
        guardar = st.button("💾 Guardar cambios", key=f"save_edit_{trade_id}")
    with cancel:
        cancelar = st.button("↩️ Cancelar", key=f"cancel_edit_{trade_id}")

    if cancelar:
        st.rerun()

    if guardar:
        final_before = procesar_imagen_b64(imagen_before) if imagen_before else old_before
        final_after = procesar_imagen_b64(imagen_after) if imagen_after else old_after

        data = {
            "fecha": str(fecha),
            "par": par,
            "direccion": direccion,
            "precio_entrada": entrada,
            "stop_loss": sl,
            "take_profit": tp,
            "rr": rr,
            "timeframe": timeframe,
            "resultado": resultado,
            "emocion": emocion,
            "notas_emocionales": notas,
            "beneficio_usd": pnl,
            "trades_cant": 1,
            "img_before": final_before,
            "img_after": final_after
        }

        if actualizar_trade_supabase(trade_id, user_id, data):
            st.success("✅ Trade actualizado.")
            st.rerun()


# =========================================================
# 18. DASHBOARD
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

    st.markdown("## ⚡ Journaling & AI Trading Audit")

    tabs = st.tabs([
        "➕ Registrar Trade",
        "📅 Track Record PnL",
        "💬 Chat IA",
        "🧮 Lotaje",
        "🧠 Análisis IA",
        "📈 Proyecciones",
        "📓 Psicotrading",
        "📊 Dashboard"
    ])

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = tabs

    # --- TAB 1: REGISTRAR TRADE ---
    with tab1:
        st.markdown("### ➕ Registrar nueva operación")
        st.info("🧠 Sube una captura de TradingView. La IA intentará detectar automáticamente ACTIVO, DIRECCIÓN, ENTRY, SL, TP y TIMEFRAME.")

        left, right = st.columns([1.15, 1])

        with right:
            st.markdown("### 🖼️ Capturas")
            upload_before = st.file_uploader("1️⃣ ANTES de la operación", type=["png", "jpg", "jpeg", "webp"], key="new_trade_before")
            upload_after = st.file_uploader("2️⃣ DESPUÉS de la operación", type=["png", "jpg", "jpeg", "webp"], key="new_trade_after")

            if upload_before:
                st.image(upload_before, caption="SETUP ANTES", use_container_width=True)

                if st.button("🧠 ESCANEAR OPERACIÓN CON IA", key="scan_new_trade"):
                    with st.spinner("Analizando gráfico..."):
                        resultado_ia = analizar_captura_tradingview(upload_before.getvalue())

                    if resultado_ia.get("error"):
                        st.error(resultado_ia["error"])
                    else:
                        st.session_state.scan_result = resultado_ia
                        aplicar_resultado_ia_a_formulario(resultado_ia)
                        st.session_state.scan_message = "IA completó los campos."
                        st.rerun()

            if upload_after:
                st.image(upload_after, caption="RESULTADO DESPUÉS", use_container_width=True)

            pnl = st.number_input("Ganancia / Pérdida ($)", value=0.0, step=10.0, key="new_trade_pnl")

        with left:
            st.markdown("### 📝 Datos de la operación")

            if st.session_state.scan_message:
                resultado = st.session_state.scan_result or {}
                st.success("✨ Datos detectados e ingresados.")
                a, b, c = st.columns(3)
                with a:
                    if resultado.get("asset"):
                        st.metric("Activo", resultado["asset"])
                with b:
                    if resultado.get("direction"):
                        st.metric("Dirección", resultado["direction"])
                with c:
                    st.metric("Confianza IA", f"{resultado.get('confidence', 0):.0f}%")

                if st.button("✖️ Limpiar resultado IA", key="clear_scan"):
                    st.session_state.scan_result = None
                    st.session_state.scan_message = ""
                    st.session_state.auto_asset = ""
                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0
                    st.rerun()

            fecha = st.date_input("Fecha", datetime.date.today(), key="new_trade_date")
            c1, c2 = st.columns(2)

            with c1:
                asset_index = LISTA_ACTIVOS.index(st.session_state.auto_asset) if st.session_state.auto_asset in LISTA_ACTIVOS else 0
                par = st.selectbox("Activo / Par", LISTA_ACTIVOS, index=asset_index, key="select_asset")

                dir_opts = ["LONG 🟢", "SHORT 🔴"]
                dir_index = dir_opts.index(st.session_state.auto_direction) if st.session_state.auto_direction in dir_opts else 0
                direccion = st.radio("Dirección", dir_opts, index=dir_index, horizontal=True, key="select_direction")

                entrada = st.number_input("Precio Entrada", min_value=0.0, value=float(st.session_state.auto_entry), format="%.5f", key="input_entry")
                sl = st.number_input("Stop Loss", min_value=0.0, value=float(st.session_state.auto_sl), format="%.5f", key="input_sl")

            with c2:
                tp = st.number_input("Take Profit", min_value=0.0, value=float(st.session_state.auto_tp), format="%.5f", key="input_tp")

                timeframes = ["", "M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]
                tf_index = timeframes.index(st.session_state.auto_timeframe) if st.session_state.auto_timeframe in timeframes else 0
                timeframe = st.selectbox("Timeframe", timeframes, index=tf_index, key="select_tf")

                riesgo = abs(entrada - sl)
                beneficio = abs(tp - entrada)
                rr = beneficio / riesgo if riesgo > 0 else 0

                st.metric("Risk : Reward", f"1 : {rr:.2f}")
                resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"], key="new_trade_result")

            st.markdown("### 🧠 Psicotrading")
            emocion = st.selectbox("Estado emocional", [
                "Disciplinado / Neutro 🧘", "Ansioso ⚡", 
                "FOMO / Miedo a perderse el movimiento 🚀", 
                "Venganza / Frustrado 🛑", "Eufórico / Sobre-confiado 😎"
            ], key="new_trade_emotion")

            notas = st.text_area("Notas emocionales", placeholder="¿Respetaste tu plan?", key="new_trade_notes")

            if st.button("💾 GUARDAR TRADE", key="save_new_trade"):
                if not par:
                    st.error("Selecciona un activo.")
                elif entrada <= 0:
                    st.error("La entrada debe ser mayor que 0.")
                else:
                    data = {
                        "fecha": str(fecha),
                        "par": par,
                        "direccion": direccion,
                        "precio_entrada": entrada,
                        "stop_loss": sl,
                        "take_profit": tp,
                        "rr": rr,
                        "timeframe": timeframe,
                        "resultado": resultado,
                        "emocion": emocion,
                        "notas_emocionales": notas,
                        "beneficio_usd": pnl,
                        "trades_cant": 1,
                        "img_before": procesar_imagen_b64(upload_before) if upload_before else "",
                        "img_after": procesar_imagen_b64(upload_after) if upload_after else ""
                    }

                    if guardar_trade_supabase(user_id, data):
                        st.session_state.auto_entry = 0.0
                        st.session_state.auto_sl = 0.0
                        st.session_state.auto_tp = 0.0
                        st.session_state.auto_asset = ""
                        st.session_state.auto_direction = "LONG 🟢"
                        st.session_state.auto_timeframe = ""
                        st.session_state.scan_result = None
                        st.session_state.scan_message = ""
                        st.success("✅ Trade guardado correctamente.")
                        st.rerun()

    # --- TAB 2: TRACK RECORD PNL ---
    with tab2:
        st.markdown("### 📅 Track Record & Calendario PnL")

        if df_trades.empty:
            st.info("Aún no tienes operaciones registradas.")
        else:
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
            st.markdown("### 📋 Historial Detallado y Capturas (ANTES / DESPUÉS)")

            for _, row in df_trades.iterrows():
                trade_id = row.get("id")
                pnl_value = float(row.get("beneficio_usd", 0) or 0)
                titulo = f"📅 {row.get('fecha', '')} | {row.get('par', '')} | {row.get('resultado', '')} | PnL: ${pnl_value:,.2f}"

                with st.expander(titulo):
                    editing_key = f"editing_{trade_id}"
                    if editing_key not in st.session_state:
                        st.session_state[editing_key] = False

                    if not st.session_state[editing_key]:
                        c1, c2, c3 = st.columns([1.2, 2, 2])
                        with c1:
                            st.markdown("#### ⚙️ Detalle de Operación")
                            st.write(f"**Activo:** {row.get('par', '-')}")
                            st.write(f"**Dirección:** {row.get('direccion', '-')}")
                            st.write(f"**Entrada:** {row.get('precio_entrada', 0)}")
                            st.write(f"**SL:** {row.get('stop_loss', 0)} | **TP:** {row.get('take_profit', 0)}")
                            st.write(f"**R:R:** 1 : {float(row.get('rr', 0) or 0):.2f}")
                            st.write(f"**Emoción:** {row.get('emocion', '-')}")

                            if st.button("✏️ Editar Trade", key=f"edit_{trade_id}"):
                                st.session_state[editing_key] = True
                                st.rerun()

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
                                st.info("📷 Sin captura ANTES")

                        with c3:
                            st.markdown("**2️⃣ DESPUÉS**")
                            img = convertir_imagen_display(row.get("img_after"))
                            if img:
                                st.image(img, use_container_width=True)
                            else:
                                st.info("📷 Sin captura DESPUÉS")
                    else:
                        editar_trade_ui(row, user_id)

    # --- TAB 3: CHAT IA ---
    with tab3:
        st.markdown("### 💬 Chat IA & Auditoría")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Pregúntame sobre tu operativa...")
        if prompt:
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("assistant"):
                if df_trades.empty:
                    answer = "Todavía no tienes suficientes operaciones registradas."
                else:
                    total = len(df_trades)
                    pnl_tot = df_trades["beneficio_usd"].sum()
                    wins = len(df_trades[df_trades["beneficio_usd"] > 0])
                    wr = (wins / total * 100)
                    answer = f"Has registrado **{total} trades** con un PnL acumulado de **${pnl_tot:,.2f}** y un Win Rate de **{wr:.1f}%**."
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # --- TAB 4: CALCULADORA LOTAJE ---
    with tab4:
        st.markdown("### 🧮 Calculadora de Tamaño de Posición")
        c1, c2 = st.columns(2)
        with c1:
            balance = st.number_input("Balance ($)", value=float(st.session_state.capital_actual), step=100.0)
            risk_percent = st.number_input("Riesgo por operación (%)", value=1.0, step=0.25)
            stop_distance = st.number_input("Distancia SL", value=20.0, step=1.0)
        with c2:
            risk_money = balance * risk_percent / 100
            lots = (risk_money / (stop_distance * 10)) if stop_distance > 0 else 0
            st.metric("Riesgo máximo", f"${risk_money:,.2f}")
            st.metric("Lotaje estimado", f"{lots:.2f}")

    # --- TAB 5: ANÁLISIS IA ---
    with tab5:
        st.markdown("### 🤖 Auditoría Visual de Setup")
        chart = st.file_uploader("Subir gráfico", type=["png", "jpg", "jpeg", "webp"], key="visual_audit")
        if chart:
            st.image(chart, use_container_width=True)

    # --- TAB 6: PROYECCIONES ---
    with tab6:
        st.markdown("### 📈 Proyección de Capital")
        trades_month = st.slider("Trades por mes", 5, 100, 15)
        win_rate_est = st.slider("Win Rate estimado (%)", 1, 99, 55)

    # --- TAB 7: PSICOTRADING ---
    with tab7:
        st.markdown("### 📓 Diario & Psicotrading")
        st.text_area("Reflexión de hoy", height=200, key="daily_reflection")

    # --- TAB 8: DASHBOARD ---
    with tab8:
        st.markdown("### 📊 Dashboard Operativo")
        if not df_trades.empty:
            st.dataframe(df_trades, use_container_width=True, hide_index=True)


# =========================================================
# 19. FLUJO PRINCIPAL
# =========================================================

if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
