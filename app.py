import streamlit as st
import datetime
import time
import textwrap
import requests
import json
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import io
import re
import math

from PIL import Image
from supabase import create_client, Client
from zoneinfo import ZoneInfo


# =========================================================
# 1. CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="AXION PRIME",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. CONFIGURACIÓN / SECRETOS
# =========================================================

# URL exacta del proyecto. No uses /rest/v1/ ni /auth/v1/.
SUPABASE_URL = str(
    st.secrets.get(
        "SUPABASE_URL",
        "https://lyzvcbjqpoydeckxtbcq.supabase.co"
    )
).strip().rstrip("/")

# Evita que un valor mal escrito en Secrets cause errores DNS confusos.
EXPECTED_SUPABASE_HOST = "lyzvcbjqpoydeckxtbcq.supabase.co"
if SUPABASE_URL != f"https://{EXPECTED_SUPABASE_HOST}":
    st.error(
        "La variable SUPABASE_URL de Streamlit Secrets está mal escrita. "
        f"Debe ser exactamente: https://{EXPECTED_SUPABASE_HOST}"
    )
    st.stop()

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    ""
)

# ---------------------------------------------------------
# OPCIONAL - Panel de Administración (V9)
# Esta es la "service_role key" de tu proyecto Supabase
# (Project Settings -> API -> service_role). Tiene permisos
# totales, así que NUNCA se debe exponer al navegador — pero
# aquí es segura porque Streamlit corre del lado del servidor.
# Si no la configuras, el panel de admin simplemente queda
# oculto/deshabilitado; el resto de la app funciona igual.
# ---------------------------------------------------------

SUPABASE_SERVICE_KEY = st.secrets.get(
    "SUPABASE_SERVICE_KEY",
    ""
)

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)

OPENROUTER_MODEL = st.secrets.get(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash"
)

ADMIN_EMAIL = st.secrets.get(
    "ADMIN_EMAIL",
    ""
)

# =========================================================
# IDENTIDAD DE MARCA V10
# =========================================================

APP_NAME = "AXION PRIME"
APP_TAGLINE = "Capital. Disciplina. Dominio."
APP_VERSION = "X1 · PROP DESK"
APP_DESCRIPTION = (
    "Sistema operativo de rendimiento para traders: "
    "journaling, analítica, psicotrading e inteligencia artificial."
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
#
# ---------------------------------------------------------
# FIX #1 (BUG PRINCIPAL):
# Antes esta función usaba @st.cache_resource, lo que creaba
# UN SOLO cliente de Supabase compartido entre TODOS los
# usuarios de la app desplegada. Cuando alguien iniciaba
# sesión, su token pisaba el de cualquier otro usuario (o el
# tuyo en otra pestaña/dispositivo) dentro de ese mismo objeto
# global. Como las consultas están protegidas por Row Level
# Security, si el token que quedaba en el cliente compartido
# no era el tuyo, Supabase devolvía 0 filas SIN ningún error
# visible -> esto es lo que hacía "desaparecer" tus trades.
#
# Ahora se crea un cliente por sesión de navegador
# (st.session_state, que es privado de cada usuario) y se le
# restaura el token guardado en cada rerun.
# ---------------------------------------------------------

def get_supabase_client() -> Client:

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Faltan SUPABASE_URL y/o SUPABASE_KEY en Streamlit Secrets."
        )

    if "supabase_client" not in st.session_state:

        st.session_state["supabase_client"] = create_client(
            SUPABASE_URL,
            SUPABASE_KEY
        )

    client = st.session_state["supabase_client"]

    tokens = st.session_state.get("supabase_session")

    if tokens:

        try:

            client.auth.set_session(
                tokens["access_token"],
                tokens["refresh_token"]
            )

        except Exception:
            pass

    return client


@st.cache_resource
def get_supabase_admin_client():
    """
    Cliente con la service_role key, SOLO para el panel de
    administración (listar usuarios, activar/desactivar PRO).
    A diferencia del cliente normal, este SÍ puede cachearse
    de forma global porque no lleva la sesión de ningún
    usuario particular — usa la clave de servicio directamente
    en cada llamada, no un token de login.
    Devuelve None si no configuraste SUPABASE_SERVICE_KEY.
    """

    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None

    try:
        return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
    except Exception:
        return None


# =========================================================
# 5. ACTIVOS
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
    "📈 META (Meta)",
    "📈 AMD (Advanced Micro Devices)",
    "📈 NFLX (Netflix)",
    "📈 COIN (Coinbase)"
]


# =========================================================
# 6. ALIAS DE ACTIVOS
# =========================================================

ASSET_ALIASES = {

    "XAUUSD": "🥇 XAU/USD (Oro)",
    "XAU/USD": "🥇 XAU/USD (Oro)",
    "XAU-USD": "🥇 XAU/USD (Oro)",
    "XAU USD": "🥇 XAU/USD (Oro)",
    "GOLD": "🥇 XAU/USD (Oro)",
    "ORO": "🥇 XAU/USD (Oro)",

    "XAGUSD": "🥈 XAG/USD (Plata)",
    "XAG/USD": "🥈 XAG/USD (Plata)",
    "XAG-USD": "🥈 XAG/USD (Plata)",
    "SILVER": "🥈 XAG/USD (Plata)",
    "PLATA": "🥈 XAG/USD (Plata)",

    "USOIL": "🛢️ USOIL (Petróleo WTI)",
    "US OIL": "🛢️ USOIL (Petróleo WTI)",
    "WTI": "🛢️ USOIL (Petróleo WTI)",
    "WTIUSD": "🛢️ USOIL (Petróleo WTI)",

    "UKOIL": "🛢️ UKOIL (Petróleo Brent)",
    "BRENT": "🛢️ UKOIL (Petróleo Brent)",
    "BRENT OIL": "🛢️ UKOIL (Petróleo Brent)",

    "NGAS": "🌾 NGAS (Gas Natural)",
    "NATURAL GAS": "🌾 NGAS (Gas Natural)",

    "BTCUSD": "🪙 BTC/USD (Bitcoin)",
    "BTC/USD": "🪙 BTC/USD (Bitcoin)",
    "BTC-USD": "🪙 BTC/USD (Bitcoin)",
    "BITCOIN": "🪙 BTC/USD (Bitcoin)",

    "ETHUSD": "🪙 ETH/USD (Ethereum)",
    "ETH/USD": "🪙 ETH/USD (Ethereum)",
    "ETHEREUM": "🪙 ETH/USD (Ethereum)",

    "SOLUSD": "🪙 SOL/USD (Solana)",
    "SOL/USD": "🪙 SOL/USD (Solana)",
    "SOLANA": "🪙 SOL/USD (Solana)",

    "XRPUSD": "🪙 XRP/USD (Ripple)",
    "XRP/USD": "🪙 XRP/USD (Ripple)",

    "BNBUSD": "🪙 BNB/USD (Binance Coin)",
    "BNB/USD": "🪙 BNB/USD (Binance Coin)",

    "ADAUSD": "🪙 ADA/USD (Cardano)",
    "ADA/USD": "🪙 ADA/USD (Cardano)",

    "DOGEUSD": "🪙 DOGE/USD (Dogecoin)",
    "DOGE/USD": "🪙 DOGE/USD (Dogecoin)",

    "US100": "📊 US100 (Nasdaq 100)",
    "NASDAQ": "📊 US100 (Nasdaq 100)",
    "NASDAQ100": "📊 US100 (Nasdaq 100)",
    "NAS100": "📊 US100 (Nasdaq 100)",
    "USTEC": "📊 US100 (Nasdaq 100)",

    "US30": "📊 US30 (Dow Jones)",
    "DOW": "📊 US30 (Dow Jones)",
    "DOWJONES": "📊 US30 (Dow Jones)",

    "US500": "📊 US500 (S&P 500)",
    "SP500": "📊 US500 (S&P 500)",
    "S&P500": "📊 US500 (S&P 500)",

    "GER40": "📊 GER40 (Dax Alemán)",
    "DAX": "📊 GER40 (Dax Alemán)",
    "DAX40": "📊 GER40 (Dax Alemán)",

    "UK100": "📊 UK100 (FTSE 100)",
    "FTSE100": "📊 UK100 (FTSE 100)",

    "JP225": "📊 JP225 (Nikkei 225)",
    "NIKKEI": "📊 JP225 (Nikkei 225)",

    "EURUSD": "💱 EUR/USD",
    "EUR/USD": "💱 EUR/USD",
    "EUR-USD": "💱 EUR/USD",
    "EUR USD": "💱 EUR/USD",
    "EUROUSD": "💱 EUR/USD",
    "EURO": "💱 EUR/USD",

    "GBPUSD": "💱 GBP/USD",
    "GBP/USD": "💱 GBP/USD",
    "GBP-USD": "💱 GBP/USD",
    "GBP USD": "💱 GBP/USD",

    "USDJPY": "💱 USD/JPY",
    "USD/JPY": "💱 USD/JPY",
    "USD-JPY": "💱 USD/JPY",

    "AUDUSD": "💱 AUD/USD",
    "AUD/USD": "💱 AUD/USD",

    "USDCAD": "💱 USD/CAD",
    "USD/CAD": "💱 USD/CAD",

    "USDCHF": "💱 USD/CHF",
    "USD/CHF": "💱 USD/CHF",

    "NZDUSD": "💱 NZD/USD",
    "NZD/USD": "💱 NZD/USD",

    "EURGBP": "💱 EUR/GBP",
    "EUR/GBP": "💱 EUR/GBP",

    "EURJPY": "💱 EUR/JPY",
    "EUR/JPY": "💱 EUR/JPY",

    "GBPJPY": "💱 GBP/JPY",
    "GBP/JPY": "💱 GBP/JPY",

    "AUDJPY": "💱 AUD/JPY",
    "AUD/JPY": "💱 AUD/JPY",

    "NVDA": "📈 NVDA (Nvidia)",
    "NVIDIA": "📈 NVDA (Nvidia)",

    "TSLA": "📈 TSLA (Tesla)",
    "TESLA": "📈 TSLA (Tesla)",

    "AAPL": "📈 AAPL (Apple)",
    "APPLE": "📈 AAPL (Apple)",

    "AMZN": "📈 AMZN (Amazon)",
    "AMAZON": "📈 AMZN (Amazon)",

    "MSFT": "📈 MSFT (Microsoft)",
    "MICROSOFT": "📈 MSFT (Microsoft)",

    "GOOGL": "📈 GOOGL (Google)",
    "GOOGLE": "📈 GOOGL (Google)",

    "META": "📈 META (Meta)",
    "FACEBOOK": "📈 META (Meta)",

    "AMD": "📈 AMD (Advanced Micro Devices)",

    "NFLX": "📈 NFLX (Netflix)",
    "NETFLIX": "📈 NFLX (Netflix)",

    "COIN": "📈 COIN (Coinbase)",
    "COINBASE": "📈 COIN (Coinbase)"
}


def limpiar_texto_activo(valor):
    if valor is None:
        return ""

    texto = str(valor).upper().strip()

    texto = texto.replace("_", " ")
    texto = texto.replace("/", "/")
    texto = texto.replace("–", "-")
    texto = texto.replace("—", "-")

    texto = re.sub(
        r"\b(CURRENCY|FOREX|FX|PAIR|FOREX PAIR)\b",
        "",
        texto
    )

    texto = re.sub(r"\s+", " ", texto).strip()

    return texto


def normalizar_activo(activo):
    """
    Reconocimiento robusto.
    IMPORTANTE:
    Si no reconoce el activo devuelve None.
    NO devuelve XAU/USD por defecto.
    """

    if activo is None:
        return None

    texto_original = str(activo).strip()

    if not texto_original:
        return None

    texto = limpiar_texto_activo(texto_original)

    # 1. Coincidencia directa
    if texto in ASSET_ALIASES:
        return ASSET_ALIASES[texto]

    # 2. Sin espacios / símbolos
    compacto = re.sub(r"[^A-Z0-9]", "", texto)

    if compacto in ASSET_ALIASES:
        return ASSET_ALIASES[compacto]

    # 3. Buscar alias dentro del texto
    for alias, nombre in ASSET_ALIASES.items():

        alias_compacto = re.sub(
            r"[^A-Z0-9]",
            "",
            alias.upper()
        )

        if alias_compacto and alias_compacto in compacto:
            return nombre

    # 4. Nombres conocidos
    nombres = {
        "EURO DOLLAR": "💱 EUR/USD",
        "EURO DÓLAR": "💱 EUR/USD",
        "POUND DOLLAR": "💱 GBP/USD",
        "POUND YEN": "💱 GBP/JPY",
        "DOLLAR YEN": "💱 USD/JPY",
        "GOLD": "🥇 XAU/USD (Oro)",
        "SILVER": "🥈 XAG/USD (Plata)",
        "NASDAQ": "📊 US100 (Nasdaq 100)",
        "DOW JONES": "📊 US30 (Dow Jones)",
        "S&P 500": "📊 US500 (S&P 500)"
    }

    if texto in nombres:
        return nombres[texto]

    return None


# =========================================================
# 7. DIRECCIÓN
# =========================================================

def normalizar_direccion(valor):

    if valor is None:
        return None

    texto = str(valor).upper().strip()

    if any(x in texto for x in [
        "LONG",
        "BUY",
        "COMPRA",
        "LARGO",
        "ALCISTA"
    ]):
        return "LONG 🟢"

    if any(x in texto for x in [
        "SHORT",
        "SELL",
        "VENTA",
        "CORTO",
        "BAJISTA"
    ]):
        return "SHORT 🔴"

    return None


# =========================================================
# 8. TIMEFRAME
# =========================================================

TIMEFRAMES = [
    "",
    "M1",
    "M5",
    "M15",
    "M30",
    "H1",
    "H4",
    "D1",
    "W1"
]


def normalizar_timeframe(valor):

    if valor is None:
        return ""

    texto = str(valor).upper().strip()
    texto = texto.replace(" ", "")

    equivalencias = {

        "1MIN": "M1",
        "1MINUTE": "M1",
        "1M": "M1",

        "5MIN": "M5",
        "5MINUTE": "M5",
        "5M": "M5",

        "15MIN": "M15",
        "15MINUTE": "M15",
        "15M": "M15",

        "30MIN": "M30",
        "30MINUTE": "M30",
        "30M": "M30",

        "1H": "H1",
        "1HR": "H1",
        "1HOUR": "H1",
        "60M": "H1",
        "60MIN": "H1",

        "4H": "H4",
        "4HR": "H4",
        "4HOUR": "H4",
        "240M": "H4",

        "1D": "D1",
        "1DAY": "D1",
        "DAILY": "D1",

        "1W": "W1",
        "1WEEK": "W1",
        "WEEKLY": "W1"
    }

    if texto in equivalencias:
        return equivalencias[texto]

    if texto in TIMEFRAMES:
        return texto

    return ""


# =========================================================
# 9. NÚMEROS
# =========================================================

def limpiar_numero(valor):

    if valor is None:
        return None

    if isinstance(valor, bool):
        return None

    if isinstance(valor, (int, float, np.integer, np.floating)):

        try:
            numero = float(valor)

            if math.isnan(numero) or math.isinf(numero):
                return None

            return numero

        except Exception:
            return None

    texto = str(valor).strip()

    if not texto:
        return None

    texto = texto.replace("$", "")
    texto = texto.replace("USD", "")
    texto = texto.replace("USDT", "")
    texto = texto.replace("≈", "")
    texto = texto.replace("~", "")
    texto = texto.strip()

    # Caso europeo: 1.234,56
    if re.match(r"^-?\d{1,3}(\.\d{3})+,\d+$", texto):
        texto = texto.replace(".", "").replace(",", ".")

    else:
        texto = texto.replace(",", "")

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        texto
    )

    if not match:
        return None

    try:
        numero = float(match.group(0))

        if math.isnan(numero) or math.isinf(numero):
            return None

        return numero

    except Exception:
        return None


# =========================================================
# 10. ESTADO INICIAL
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

    # FORMULARIO NUEVO TRADE
    "trade_asset": "",
    "trade_direction": "LONG 🟢",
    "trade_entry": 0.0,
    "trade_sl": 0.0,
    "trade_tp": 0.0,
    "trade_timeframe": "",

    "trade_result": "BE ⚪",
    "trade_emotion": "Disciplinado / Neutro 🧘",
    "trade_notes": "",

    # IA
    "scan_result": None,
    "scan_message": "",
    "scan_error": "",

    # Control de edición
    "editing_trade_id": None,

    # FIX #2: bandera para saber si ya cargamos
    # reglas/capital desde el backend en esta sesión
    "prefs_cargadas": False,

    # V9.1: página actualmente seleccionada en el
    # menú lateral de navegación
    "pagina_actual": "Dashboard",

    # V10: filtros globales del dashboard
    "dashboard_periodo": "Todo",
    "dashboard_asset": "Todos",
    "dashboard_view": "Rendimiento",

    # X7: día seleccionado dentro del calendario PnL
    "selected_trade_day": None,
    "last_saved_trade_id": None
}


for key, value in defaults.items():

    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 11. IMÁGENES
# =========================================================

def procesar_imagen_b64(uploaded_file, max_size=(1400, 1000)):

    if uploaded_file is None:
        return ""

    try:

        image = Image.open(uploaded_file)

        if image.mode in ("RGBA", "LA", "P"):

            if image.mode == "P":
                image = image.convert("RGBA")

            if image.mode in ("RGBA", "LA"):

                background = Image.new(
                    "RGB",
                    image.size,
                    "white"
                )

                background.paste(
                    image,
                    mask=image.getchannel("A")
                )

                image = background

            else:
                image = image.convert("RGB")

        else:
            image = image.convert("RGB")

        image.thumbnail(max_size)

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

        return "data:image/jpeg;base64," + encoded

    except Exception as e:

        st.error(
            f"Error procesando imagen: {e}"
        )

        return ""


def convertir_imagen_display(valor):

    if not valor:
        return None

    try:

        valor = str(valor)

        if valor.startswith("data:image"):
            return valor

        if len(valor) > 100:
            return (
                "data:image/jpeg;base64,"
                + valor
            )

    except Exception:
        pass

    return None


# =========================================================
# 12. SUPABASE TRADES
# =========================================================
#
# ---------------------------------------------------------
# FIX #3: "Connection reset by peer" / "Broken pipe"
# El cliente de Supabase reutiliza una conexión HTTP entre
# reruns de Streamlit. Si esa conexión estuvo inactiva un
# rato, el socket puede quedar "muerto" del lado del
# servidor y la siguiente petición falla con estos errores
# de bajo nivel (no son errores de tus datos ni de tus
# credenciales). La solución es: si pasa, descartamos el
# cliente guardado y reintentamos una vez con uno nuevo.
# ---------------------------------------------------------

def _es_error_de_conexion(e):

    texto = str(e).lower()

    return any(
        x in texto
        for x in [
            "broken pipe",
            "connection reset",
            "errno 32",
            "errno 104",
            "remotedisconnected",
            "connection aborted",
            "timed out",
            "timeout"
        ]
    )


def _forzar_reconexion_supabase():

    st.session_state.pop(
        "supabase_client",
        None
    )


def cargar_trades_usuario(user_id):

    for intento in (1, 2):

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

            if intento == 1 and _es_error_de_conexion(e):

                _forzar_reconexion_supabase()

                time.sleep(0.6)

                continue

            st.error(
                f"❌ Error cargando operaciones: {e}"
            )

            return []



def _obtener_tokens_sesion():
    """Obtiene y refresca los tokens sin depender de un único rerun."""
    tokens = st.session_state.get("supabase_session") or {}
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    if access_token and refresh_token:
        return access_token, refresh_token

    try:
        client = get_supabase_client()
        session_response = client.auth.get_session()
        session = getattr(session_response, "session", None) or session_response
        access_token = getattr(session, "access_token", None)
        refresh_token = getattr(session, "refresh_token", None)

        if access_token and refresh_token:
            st.session_state.supabase_session = {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
            return access_token, refresh_token
    except Exception:
        pass

    return None, None


def _insertar_trade_rest(data, access_token):
    """Fallback directo a PostgREST. Respeta RLS usando el JWT del usuario."""
    endpoint = f"{SUPABASE_URL.rstrip('/')}/rest/v1/trades"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }

    response = requests.post(
        endpoint,
        headers=headers,
        json=data,
        timeout=45,
    )

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"Supabase REST {response.status_code}: {response.text[:900]}"
        )

    payload = response.json() if response.text.strip() else []
    if not payload:
        raise RuntimeError(
            "Supabase respondió sin devolver la fila creada."
        )

    return payload


def guardar_trade_supabase(user_id, trade_data):
    """Guarda y verifica el trade con doble vía: SDK + REST autenticado."""
    access_token, refresh_token = _obtener_tokens_sesion()

    if not access_token:
        st.error(
            "❌ La sesión venció o no tiene token. "
            "Cierra sesión, vuelve a entrar e intenta nuevamente."
        )
        return False

    data = dict(trade_data)
    data["user_id"] = str(user_id)

    errores = []

    # Vía 1: SDK oficial.
    try:
        client = get_supabase_client()

        if refresh_token:
            session_result = client.auth.set_session(
                access_token,
                refresh_token,
            )
            refreshed = getattr(session_result, "session", None)
            if refreshed:
                access_token = (
                    getattr(refreshed, "access_token", None)
                    or access_token
                )
                refresh_token = (
                    getattr(refreshed, "refresh_token", None)
                    or refresh_token
                )
                st.session_state.supabase_session = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }

        result = client.table("trades").insert(data).execute()
        filas = getattr(result, "data", None) or []

        if filas:
            trade_id = filas[0].get("id")
            st.session_state.last_saved_trade_id = trade_id
            return True

        errores.append("El SDK no devolvió la fila insertada.")

    except Exception as e:
        errores.append(f"SDK: {e}")

    # Vía 2: REST directo, útil cuando el SDK pierde el JWT durante un rerun.
    try:
        filas = _insertar_trade_rest(data, access_token)
        trade_id = filas[0].get("id") if isinstance(filas[0], dict) else None
        st.session_state.last_saved_trade_id = trade_id
        return True

    except Exception as e:
        errores.append(f"REST: {e}")

    mensaje = " | ".join(errores)
    st.error(f"❌ El trade no pudo guardarse. {mensaje}")

    lower = mensaje.lower()
    if "row-level security" in lower or "42501" in lower:
        st.warning(
            "La política RLS de INSERT está bloqueando el registro. "
            "Ejecuta el archivo SQL X7 incluido."
        )
    elif "column" in lower or "schema cache" in lower:
        st.warning(
            "La tabla trades no tiene todas las columnas que usa el formulario."
        )
    elif "jwt" in lower or "token" in lower or "session" in lower:
        st.warning(
            "La sesión de Supabase no es válida. Cierra sesión y vuelve a ingresar."
        )

    return False


def actualizar_trade_supabase(
    trade_id,
    user_id,
    trade_data
):

    for intento in (1, 2):

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

            if intento == 1 and _es_error_de_conexion(e):

                _forzar_reconexion_supabase()

                time.sleep(0.6)

                continue

            st.error(
                f"❌ Error actualizando operación: {e}"
            )

            return False


def eliminar_trade_supabase(
    trade_id,
    user_id
):

    for intento in (1, 2):

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

            if intento == 1 and _es_error_de_conexion(e):

                _forzar_reconexion_supabase()

                time.sleep(0.6)

                continue

            st.error(
                f"❌ Error eliminando operación: {e}"
            )

            return False


# =========================================================
# 13. PARSER JSON IA
# =========================================================

def extraer_json_ia(content):

    if not content:
        return None

    # OpenRouter puede devolver string
    if isinstance(content, list):

        partes = []

        for item in content:

            if isinstance(item, dict):

                if "text" in item:
                    partes.append(
                        str(item["text"])
                    )

            else:
                partes.append(str(item))

        content = "\n".join(partes)

    texto = str(content).strip()

    texto = re.sub(
        r"```json",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = texto.replace(
        "```",
        ""
    ).strip()

    # Buscar objeto JSON
    inicio = texto.find("{")
    final = texto.rfind("}")

    if inicio >= 0 and final > inicio:

        texto = texto[
            inicio:final + 1
        ]

    try:

        return json.loads(texto)

    except Exception:

        # Intento de limpieza adicional
        try:

            texto2 = texto.replace(
                "'", '"'
            )

            return json.loads(texto2)

        except Exception:

            return None


# =========================================================
# 14. VALIDAR RESULTADO IA
# =========================================================

def validar_resultado_ia(data):

    if not isinstance(data, dict):
        return None

    activo = normalizar_activo(
        data.get("asset")
        or data.get("symbol")
        or data.get("pair")
        or data.get("instrument")
    )

    direccion = normalizar_direccion(
        data.get("direction")
        or data.get("side")
        or data.get("trade_direction")
    )

    entry = limpiar_numero(
        data.get("entry")
        or data.get("entry_price")
        or data.get("price_entry")
    )

    sl = limpiar_numero(
        data.get("sl")
        or data.get("stop_loss")
        or data.get("stoploss")
    )

    tp = limpiar_numero(
        data.get("tp")
        or data.get("take_profit")
        or data.get("takeprofit")
    )

    timeframe = normalizar_timeframe(
        data.get("timeframe")
        or data.get("tf")
    )

    confidence = limpiar_numero(
        data.get("confidence")
    )

    # Confianza general
    if confidence is None:
        confidence = 0

    confidence = max(
        0,
        min(100, confidence)
    )

    return {

        "asset": activo,

        "direction": direccion,

        "entry": entry,

        "sl": sl,

        "tp": tp,

        "timeframe": timeframe,

        "confidence": confidence
    }


# =========================================================
# 15. IA VISUAL
# =========================================================

def analizar_captura_tradingview(
    image_bytes,
    mime_type="image/jpeg"
):

    if not OPENROUTER_API_KEY:

        return {
            "error":
                "OPENROUTER_API_KEY no está configurada "
                "en Streamlit Secrets."
        }

    try:

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        prompt = """
Eres un extractor profesional de información visual de TradingView.

Tu trabajo NO es analizar si una operación es buena o mala.

Tu único trabajo es LEER la captura y extraer exactamente los parámetros visibles.

IMPORTANTE:

1. Identifica el ACTIVO que aparece en el gráfico.
2. Identifica LONG/SHORT.
3. Identifica ENTRY / precio de entrada.
4. Identifica STOP LOSS.
5. Identifica TAKE PROFIT.
6. Identifica TIMEFRAME.
7. No inventes valores.
8. No sustituyas un activo desconocido por XAU/USD.
9. Si el activo es EUR/USD, devuelve EUR/USD.
10. Si es GBP/JPY, devuelve GBP/JPY.
11. Si un valor no se puede leer claramente, devuelve null.
12. Conserva todos los decimales visibles.
13. Las etiquetas pueden estar en español o inglés.
14. Busca especialmente las herramientas Position Long / Position Short de TradingView.
15. Si hay varios precios, determina cuál corresponde a ENTRY, SL y TP por su posición y etiqueta.
16. NO calcules Entry, SL o TP.
17. NO completes datos faltantes con suposiciones.

Ejemplos:

EURUSD -> EUR/USD
EUR/USD -> EUR/USD
EUR-USD -> EUR/USD
GBPJPY -> GBP/JPY
GBP/JPY -> GBP/JPY
XAUUSD -> XAU/USD
Gold -> XAU/USD

Devuelve ÚNICAMENTE JSON válido:

{
  "asset": null,
  "direction": null,
  "entry": null,
  "sl": null,
  "tp": null,
  "timeframe": null,
  "confidence": 0
}

La confianza debe ser de 0 a 100.

No escribas explicaciones.
No uses Markdown.
No escribas ```json.
"""

        headers = {

            "Authorization":
                f"Bearer {OPENROUTER_API_KEY}",

            "Content-Type":
                "application/json",

            "HTTP-Referer":
                "https://trading-journal-ia.streamlit.app",

            "X-Title":
                "AXION PRIME"
        }

        payload = {

            "model": OPENROUTER_MODEL,

            "temperature": 0,

            "max_tokens": 1000,

            "messages": [

                {
                    "role": "system",
                    "content":
                        "Eres un extractor visual extremadamente preciso. "
                        "Nunca inventes datos."
                },

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
                                    f"data:{mime_type};base64,{encoded_image}"
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

            timeout=90
        )

        if response.status_code != 200:

            return {
                "error":
                    f"OpenRouter HTTP {response.status_code}: "
                    f"{response.text[:700]}"
            }

        result = response.json()

        choices = result.get(
            "choices",
            []
        )

        if not choices:

            return {
                "error":
                    "OpenRouter no devolvió resultados."
            }

        message = choices[0].get(
            "message",
            {}
        )

        content = message.get(
            "content",
            ""
        )

        data = extraer_json_ia(
            content
        )

        if not data:

            return {
                "error":
                    "La IA respondió, pero no devolvió "
                    "JSON válido.",
                "raw": str(content)
            }

        resultado = validar_resultado_ia(
            data
        )

        if not resultado:

            return {
                "error":
                    "No se pudo validar la respuesta de la IA."
            }

        return resultado

    except requests.exceptions.Timeout:

        return {
            "error":
                "La IA tardó demasiado en responder. "
                "Intenta nuevamente."
        }

    except Exception as e:

        return {
            "error":
                f"Error analizando captura: {e}"
        }


# =========================================================
# 16. APLICAR RESULTADO IA
# =========================================================

def aplicar_resultado_ia(resultado):
    """Aplica la lectura de IA al estado real y a los widgets visibles.

    Streamlit conserva el valor de los widgets por su key. Por eso no basta
    con cambiar trade_sl/trade_tp: también hay que actualizar las keys de
    los number_input/selectbox/radio antes del rerun.
    """

    if not resultado:
        return

    mapping = {
        "asset": ("trade_asset", "trade_asset_widget"),
        "direction": ("trade_direction", "trade_direction_widget"),
        "entry": ("trade_entry", "trade_entry_widget"),
        "sl": ("trade_sl", "trade_sl_widget"),
        "tp": ("trade_tp", "trade_tp_widget"),
        "timeframe": ("trade_timeframe", "trade_timeframe_widget"),
    }

    for source_key, (state_key, widget_key) in mapping.items():
        value = resultado.get(source_key)

        if value is None or value == "":
            continue

        if source_key in {"entry", "sl", "tp"}:
            try:
                value = float(value)
            except (TypeError, ValueError):
                continue

        st.session_state[state_key] = value
        st.session_state[widget_key] = value

    # Compatibilidad con versiones antiguas del formulario.
    st.session_state["auto_entry"] = float(resultado.get("entry") or 0)
    st.session_state["auto_sl"] = float(resultado.get("sl") or 0)
    st.session_state["auto_tp"] = float(resultado.get("tp") or 0)


# =========================================================
# 17. LIMPIAR FORMULARIO
# =========================================================

def limpiar_formulario_trade():

    st.session_state[
        "trade_asset"
    ] = ""

    st.session_state[
        "trade_direction"
    ] = "LONG 🟢"

    st.session_state[
        "trade_entry"
    ] = 0.0

    st.session_state[
        "trade_sl"
    ] = 0.0

    st.session_state[
        "trade_tp"
    ] = 0.0

    st.session_state[
        "trade_timeframe"
    ] = ""

    st.session_state[
        "trade_result"
    ] = "BE ⚪"

    st.session_state[
        "trade_emotion"
    ] = "Disciplinado / Neutro 🧘"

    st.session_state[
        "trade_notes"
    ] = ""

    st.session_state[
        "scan_result"
    ] = None

    st.session_state[
        "scan_message"
    ] = ""

    st.session_state[
        "scan_error"
    ] = ""


# =========================================================
# 18. R:R
# =========================================================

def calcular_rr(
    entry,
    sl,
    tp
):

    try:

        entry = float(entry)
        sl = float(sl)
        tp = float(tp)

        riesgo = abs(
            entry - sl
        )

        beneficio = abs(
            tp - entry
        )

        if riesgo <= 0:
            return 0.0

        return beneficio / riesgo

    except Exception:

        return 0.0


# =========================================================
# 19. SESIONES
# =========================================================

SESIONES = [

    {
        "nombre": "🇦🇺 Sídney",
        "zona": "Australia/Sydney",
        "inicio": 8,
        "fin": 17
    },

    {
        "nombre": "🇯🇵 Tokio",
        "zona": "Asia/Tokyo",
        "inicio": 9,
        "fin": 18
    },

    {
        "nombre": "🇬🇧 Londres",
        "zona": "Europe/London",
        "inicio": 8,
        "fin": 17
    },

    {
        "nombre": "🇺🇸 Nueva York",
        "zona": "America/New_York",
        "inicio": 8,
        "fin": 17
    }
]


def obtener_hora_zona(zona):

    try:
        return datetime.datetime.now(
            ZoneInfo(zona)
        )

    except Exception:

        return datetime.datetime.now()


def mercado_abierto(
    zona,
    inicio,
    fin
):

    try:

        ahora = obtener_hora_zona(
            zona
        )

        if ahora.weekday() >= 5:
            return False

        hora_decimal = (
            ahora.hour
            + ahora.minute / 60
        )

        return (
            inicio
            <= hora_decimal
            < fin
        )

    except Exception:

        return False


def render_sesion(
    nombre,
    zona,
    inicio,
    fin
):

    ahora = obtener_hora_zona(
        zona
    )

    abierto = mercado_abierto(
        zona,
        inicio,
        fin
    )

    estado = (
        "ABIERTO"
        if abierto
        else "CERRADO"
    )

    color = (
        "#34d399"
        if abierto
        else "#f87171"
    )

    st.markdown(
        f"""
        <div class="session-card">
            <div class="session-title">{nombre}</div>
            <div class="session-time">{ahora.strftime("%H:%M:%S")}</div>
            <div class="session-date">{ahora.strftime("%d/%m/%Y")}</div>
            <div class="session-status"
                 style="color:{color}; border-color:{color};">
                {estado}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 20. SUSCRIPCIÓN
# =========================================================

def evaluar_suscripcion(user):

    if not user:

        return (
            False,
            "Sin sesión",
            0
        )

    user_email = (
        getattr(user, "email", "")
        or ""
    )

    if (
        ADMIN_EMAIL
        and user_email.lower()
        == ADMIN_EMAIL.lower()
    ):

        return (
            True,
            "Creador / Admin 👑",
            99999
        )

    metadata = (
        getattr(
            user,
            "user_metadata",
            {}
        )
        or {}
    )

    if metadata.get(
        "es_vip",
        False
    ):

        return (
            True,
            "Acceso PRO 💎",
            999
        )

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
                    .replace(
                        "Z",
                        "+00:00"
                    )
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
            f"Prueba Gratis "
            f"({dias_restantes} días rest.)",
            dias_restantes
        )

    return (
        False,
        "Prueba Expirada 🛑",
        0
    )


# =========================================================
# 21. CSS
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
        border: 1px solid rgba(0,242,254,.5) !important;
        border-radius: 8px !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[role="listbox"] {

        background-color: #121721 !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }

    div[role="option"] {

        background-color: #121721 !important;
        color: #ffffff !important;
    }

    div[role="option"]:hover {

        background-color: #00f2fe !important;
        color: #000000 !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {

        background-color: #161b22 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0,210,255,.4) !important;
        border-radius: 8px !important;
    }

    .stButton > button {

        background: linear-gradient(
            135deg,
            #00d2ff 0%,
            #2962ff 100%
        ) !important;

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

    .session-title {
        font-size: 14px;
        font-weight: bold;
    }

    .session-time {

        color: #00f2fe !important;
        font-size: 22px;
        font-weight: 800;
    }

    .session-date {

        color: #8b98a8 !important;
        font-size: 11px;
    }

    .session-status {

        display: inline-block;
        margin-top: 6px;
        padding: 2px 8px;
        border: 1px solid;
        border-radius: 20px;
        font-size: 10px;
        font-weight: bold;
    }

    .ai-box {

        background: linear-gradient(
            135deg,
            rgba(0,210,255,.08),
            rgba(41,98,255,.08)
        );

        border: 1px solid rgba(0,242,254,.35);
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 15px;
    }

    .detected {

        background: #111a24;
        border: 1px solid #26394c;
        border-radius: 10px;
        padding: 12px;
    }

    .paywall-card {

        background-color: #161b22;
        border: 1px solid #f0b90b;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }

    /* ---- V9: tarjetas de métricas estilo SaaS ---- */

    .metric-card {

        background: linear-gradient(
            160deg,
            #161b22 0%,
            #10141c 100%
        );

        border: 1px solid rgba(0,242,254,.18);
        border-radius: 14px;
        padding: 18px 20px;
        height: 100%;
    }

    .metric-card .metric-label {

        color: #8b98a8 !important;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: .5px;
        margin-bottom: 6px;
    }

    .metric-card .metric-value {

        font-size: 26px;
        font-weight: 800;
        color: #f0f3fa !important;
    }

    .metric-card .metric-sub {

        color: #8b98a8 !important;
        font-size: 11px;
        margin-top: 4px;
    }

    /* ---- V9: badge admin junto al nombre ---- */

    .admin-badge {

        display: inline-block;
        background: linear-gradient(
            135deg,
            #f0b90b,
            #ffdd7a
        );

        color: #1a1200 !important;
        font-weight: 800;
        font-size: 10px;
        letter-spacing: .5px;
        padding: 2px 8px;
        border-radius: 20px;
        margin-left: 6px;
        vertical-align: middle;
    }

    /* ---- V9: portada / hero del login ---- */

    .hero-panel {

        background: linear-gradient(
            160deg,
            rgba(0,210,255,.10),
            rgba(10,14,20,.9)
        );

        border: 1px solid rgba(0,242,254,.2);
        border-radius: 18px;
        padding: 34px 30px;
        height: 100%;
    }

    .hero-quote {

        background: #111a24;
        border-left: 3px solid #00f2fe;
        border-radius: 8px;
        padding: 14px 16px;
        margin-top: 22px;
        font-style: italic;
        color: #c8d3e0 !important;
    }

    /* ---- V9.1: menú lateral de navegación ---- */

    section[data-testid="stSidebar"] .stButton > button {

        background: transparent !important;
        color: #c8d3e0 !important;
        border: none !important;
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        padding: 8px 10px !important;
        box-shadow: none !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {

        background: rgba(0,242,254,.10) !important;
        color: #00f2fe !important;
    }

    section[data-testid="stSidebar"] .stButton > button p {

        text-align: left !important;
        font-size: 14px !important;
    }

    .nav-active > button {

        background: linear-gradient(
            90deg,
            rgba(0,210,255,.18),
            rgba(41,98,255,.05)
        ) !important;

        color: #00f2fe !important;
        font-weight: 700 !important;
        border-left: 3px solid #00f2fe !important;
    }

    .nav-section-label {

        color: #5c6b80 !important;
        font-size: 11px;
        letter-spacing: .8px;
        text-transform: uppercase;
        margin: 14px 0 4px 4px;
        font-weight: 700;
    }

    .plan-box {

        background: linear-gradient(
            135deg,
            rgba(0,210,255,.15),
            rgba(41,98,255,.15)
        );

        border: 1px solid rgba(0,242,254,.35);
        border-radius: 12px;
        padding: 12px 14px;
        margin-top: 10px;
    }



    /* =====================================================
       AXION PRIME V10 — DESIGN SYSTEM
       ===================================================== */

    :root {
        --nx-bg: #060810;
        --nx-panel: rgba(15, 20, 33, .86);
        --nx-panel-2: rgba(20, 27, 44, .78);
        --nx-line: rgba(126, 249, 255, .14);
        --nx-cyan: #35e7ff;
        --nx-blue: #4d7cff;
        --nx-violet: #9d4dff;
        --nx-green: #2ce6a6;
        --nx-red: #ff5f7a;
        --nx-muted: #8290aa;
        --nx-text: #f3f7ff;
    }

    .stApp {
        background:
          radial-gradient(circle at 84% -10%, rgba(157,77,255,.15), transparent 35%),
          radial-gradient(circle at 18% 4%, rgba(53,231,255,.10), transparent 32%),
          linear-gradient(180deg, #060810 0%, #090c16 55%, #060810 100%) !important;
    }

    [data-testid="stHeader"] {
        background: rgba(6,8,16,.74) !important;
        backdrop-filter: blur(16px);
        border-bottom: 1px solid rgba(255,255,255,.04);
    }

    .block-container {
        max-width: 1520px;
        padding-top: 1.6rem;
        padding-bottom: 3rem;
    }

    .nx-brand {
        display:flex; align-items:center; gap:12px;
        margin-bottom:18px;
    }
    .nx-brand-mark {
        width:44px; height:44px; border-radius:14px;
        display:flex; align-items:center; justify-content:center;
        font-size:25px;
        background:linear-gradient(145deg,var(--nx-cyan),var(--nx-blue) 55%,var(--nx-violet));
        box-shadow:0 0 30px rgba(53,231,255,.22);
    }
    .nx-brand-name {font-size:17px;font-weight:900;letter-spacing:.7px;color:white!important;}
    .nx-brand-sub {font-size:10px;letter-spacing:1.8px;color:var(--nx-muted)!important;}

    .nx-login-shell {
        min-height: calc(100vh - 150px);
        display:flex; align-items:center;
    }
    .nx-visual {
        position:relative; min-height:650px; overflow:hidden;
        border-radius:28px;
        background:
          linear-gradient(90deg,rgba(6,8,16,.97) 0%,rgba(6,8,16,.72) 46%,rgba(6,8,16,.18) 100%),
          linear-gradient(0deg,rgba(6,8,16,.94) 0%,transparent 50%),
          url('app/static/fondo.jpg'), url('fondo.jpg');
        background-size:cover;
        background-position:center;
        border:1px solid rgba(255,255,255,.08);
        box-shadow:0 30px 90px rgba(0,0,0,.55);
        padding:46px;
    }
    .nx-visual:after {
        content:""; position:absolute; inset:0; pointer-events:none;
        background:radial-gradient(circle at 70% 38%,rgba(53,231,255,.13),transparent 26%);
    }
    .nx-hero-content {position:relative;z-index:2;max-width:520px;}
    .nx-kicker {color:var(--nx-cyan)!important;font-size:12px;font-weight:800;letter-spacing:2px;text-transform:uppercase;}
    .nx-hero-title {font-size:clamp(40px,5vw,72px);line-height:.98;font-weight:950;letter-spacing:-2.5px;margin:20px 0;color:#fff!important;}
    .nx-gradient-text {background:linear-gradient(90deg,var(--nx-cyan),#8bd9ff 43%,#b77dff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .nx-hero-copy {font-size:16px;line-height:1.7;color:#b8c4d8!important;max-width:470px;}
    .nx-feature-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:28px;}
    .nx-feature {background:rgba(12,17,29,.66);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:13px 15px;backdrop-filter:blur(10px);font-size:12px;color:#d9e4f6!important;}
    .nx-quote {position:absolute;bottom:35px;left:46px;right:46px;z-index:3;border-left:3px solid var(--nx-cyan);padding:12px 16px;background:rgba(9,13,23,.68);border-radius:0 12px 12px 0;color:#9eabc0!important;font-size:12px;}

    .nx-auth-card {
        background:linear-gradient(160deg,rgba(19,25,41,.92),rgba(10,14,25,.94));
        border:1px solid rgba(255,255,255,.09);
        border-radius:26px;
        padding:34px;
        box-shadow:0 30px 80px rgba(0,0,0,.45);
        backdrop-filter:blur(18px);
    }

    .nx-topbar {
        display:flex;justify-content:space-between;align-items:flex-start;gap:24px;
        padding:4px 2px 18px 2px;
    }
    .nx-page-eyebrow {font-size:11px;letter-spacing:1.7px;text-transform:uppercase;color:var(--nx-cyan)!important;font-weight:800;}
    .nx-page-title {font-size:34px;font-weight:900;letter-spacing:-1px;color:white!important;margin:4px 0 2px;}
    .nx-page-copy {font-size:13px;color:var(--nx-muted)!important;}
    .nx-live-pill {display:inline-flex;align-items:center;gap:8px;border:1px solid rgba(44,230,166,.25);background:rgba(44,230,166,.08);padding:8px 12px;border-radius:999px;font-size:11px;color:#8fffd5!important;}
    .nx-dot {width:7px;height:7px;border-radius:50%;background:var(--nx-green);box-shadow:0 0 12px var(--nx-green);}

    .nx-card {
        background:linear-gradient(160deg,rgba(20,27,44,.86),rgba(10,14,25,.92));
        border:1px solid var(--nx-line);
        border-radius:18px;
        padding:18px;
        box-shadow:0 16px 40px rgba(0,0,0,.20);
        transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease;
    }
    .nx-card:hover {transform:translateY(-2px);border-color:rgba(53,231,255,.32);box-shadow:0 18px 48px rgba(0,0,0,.28),0 0 26px rgba(53,231,255,.06);}
    .nx-metric-label {font-size:10px;letter-spacing:1px;text-transform:uppercase;color:var(--nx-muted)!important;font-weight:800;}
    .nx-metric-value {font-size:27px;font-weight:900;color:white!important;margin:8px 0 3px;letter-spacing:-.7px;}
    .nx-metric-foot {font-size:11px;color:#91a0b8!important;display:flex;justify-content:space-between;gap:10px;}
    .nx-positive {color:var(--nx-green)!important;}
    .nx-negative {color:var(--nx-red)!important;}
    .nx-spark {height:3px;margin-top:15px;border-radius:99px;background:linear-gradient(90deg,var(--nx-cyan),var(--nx-blue),var(--nx-violet));opacity:.85;}

    .nx-section-head {display:flex;justify-content:space-between;align-items:center;margin:8px 0 12px;}
    .nx-section-title {font-size:16px;font-weight:850;color:white!important;}
    .nx-section-meta {font-size:10px;color:var(--nx-muted)!important;}

    .nx-ai-score {
        background:radial-gradient(circle at 85% 10%,rgba(157,77,255,.23),transparent 38%),linear-gradient(145deg,rgba(25,31,50,.95),rgba(12,16,29,.96));
        border:1px solid rgba(157,77,255,.27);border-radius:20px;padding:20px;
    }
    .nx-score-number {font-size:52px;font-weight:950;line-height:1;background:linear-gradient(90deg,var(--nx-cyan),var(--nx-violet));-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
    .nx-insight {display:flex;gap:10px;padding:9px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:11px;color:#b9c5d8!important;}

    .nx-session-strip {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;}
    .nx-session-item {background:rgba(15,21,35,.72);border:1px solid rgba(255,255,255,.06);border-radius:13px;padding:12px;}
    .nx-session-name {font-size:10px;color:#91a0b8!important;}
    .nx-session-time {font-size:17px;font-weight:850;color:white!important;margin:3px 0;}
    .nx-session-open {font-size:9px;color:var(--nx-green)!important;font-weight:800;}
    .nx-session-closed {font-size:9px;color:var(--nx-red)!important;font-weight:800;}

    .nx-empty {border:1px dashed rgba(53,231,255,.22);background:rgba(53,231,255,.035);border-radius:18px;padding:38px;text-align:center;color:#91a0b8!important;}

    section[data-testid="stSidebar"] {
        background:linear-gradient(180deg,#0a0d17 0%,#0d1220 100%)!important;
        border-right:1px solid rgba(53,231,255,.10)!important;
    }
    section[data-testid="stSidebar"] > div {padding-top:1.2rem;}

    .stButton > button, .stFormSubmitButton > button {
        min-height:42px;
        background:linear-gradient(110deg,var(--nx-cyan),var(--nx-blue) 52%,var(--nx-violet))!important;
        box-shadow:0 10px 28px rgba(77,124,255,.18);
        transition:all .2s ease!important;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {transform:translateY(-1px);box-shadow:0 14px 34px rgba(77,124,255,.28);}

    [data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stTextArea"] textarea {
        background:rgba(8,12,22,.78)!important;
        border:1px solid rgba(255,255,255,.09)!important;
        min-height:44px;
    }
    [data-testid="stTextInput"] input:focus,[data-testid="stNumberInput"] input:focus,[data-testid="stTextArea"] textarea:focus {border-color:rgba(53,231,255,.55)!important;box-shadow:0 0 0 3px rgba(53,231,255,.08)!important;}

    [data-testid="stPlotlyChart"] {background:transparent!important;border-radius:18px;overflow:hidden;}

    @media (max-width: 900px) {
      .nx-visual {min-height:520px;padding:28px;}
      .nx-feature-grid,.nx-session-strip {grid-template-columns:1fr 1fr;}
      .nx-quote {left:28px;right:28px;}
    }

    
    :root{--ax-cyan:#43e8ff;--ax-violet:#9b5cff;--ax-green:#27e5a7;--ax-red:#ff5f7a;--ax-text:#f5f7ff;--ax-muted:#8f9ab6;--ax-line:rgba(133,160,255,.16)}
    .stApp{background:radial-gradient(circle at 78% -10%,rgba(118,65,255,.18),transparent 30%),radial-gradient(circle at 8% 12%,rgba(31,210,255,.13),transparent 27%),linear-gradient(135deg,#050812 0%,#080b17 42%,#050711 100%)!important}
    .block-container{padding-top:1.2rem!important;max-width:1600px!important}section[data-testid="stSidebar"]{background:rgba(5,8,18,.92)!important;backdrop-filter:blur(24px)}
    .ax-shell{overflow:hidden;border:1px solid var(--ax-line);border-radius:24px;background:linear-gradient(145deg,rgba(13,19,34,.84),rgba(7,11,22,.76));box-shadow:0 24px 80px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.03)}.ax-top{padding:24px 26px;display:flex;align-items:center;justify-content:space-between;gap:20px}.ax-kicker{font-size:11px;font-weight:800;letter-spacing:2px;color:var(--ax-cyan)!important}.ax-title{font-size:31px;line-height:1.05;font-weight:900;color:var(--ax-text)!important;margin-top:7px}.ax-sub{font-size:13px;color:var(--ax-muted)!important;margin-top:8px}.ax-status{display:flex;gap:10px;align-items:center;padding:9px 13px;border:1px solid rgba(39,229,167,.24);background:rgba(39,229,167,.08);border-radius:999px;color:#aef6dd!important;font-size:12px}.ax-pulse{width:8px;height:8px;background:var(--ax-green);border-radius:50%;animation:axPulse 2s infinite}@keyframes axPulse{0%{box-shadow:0 0 0 0 rgba(39,229,167,.45)}70%{box-shadow:0 0 0 9px rgba(39,229,167,0)}100%{box-shadow:0 0 0 0 rgba(39,229,167,0)}}
    .ax-kpi{min-height:134px;padding:18px 19px;border-radius:20px;border:1px solid var(--ax-line);background:linear-gradient(145deg,rgba(18,25,45,.85),rgba(9,14,28,.82));transition:.25s ease}.ax-kpi:hover{transform:translateY(-4px);border-color:rgba(67,232,255,.38);box-shadow:0 16px 40px rgba(0,0,0,.24)}.ax-kpi-label{font-size:10px;letter-spacing:1.5px;color:var(--ax-muted)!important;font-weight:800}.ax-kpi-value{font-size:27px;color:var(--ax-text)!important;font-weight:900;margin-top:10px}.ax-kpi-foot{font-size:11px;color:var(--ax-muted)!important;margin-top:9px;display:flex;justify-content:space-between}.ax-positive{color:var(--ax-green)!important}.ax-negative{color:var(--ax-red)!important}.ax-neutral{color:var(--ax-cyan)!important}.ax-meter{height:4px;margin-top:13px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden}.ax-meter span{display:block;height:100%;border-radius:99px;background:linear-gradient(90deg,var(--ax-cyan),var(--ax-violet))}
    .ax-panel{border:1px solid var(--ax-line);border-radius:22px;background:linear-gradient(150deg,rgba(14,21,38,.82),rgba(7,11,22,.78));padding:18px 20px}.ax-panel-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:13px}.ax-panel-title{font-size:14px;font-weight:850;color:var(--ax-text)!important}.ax-panel-tag{font-size:9px;letter-spacing:1px;color:var(--ax-muted)!important}.ax-score-ring{width:124px;height:124px;border-radius:50%;display:grid;place-items:center;margin:8px auto 12px;background:conic-gradient(var(--ax-cyan) calc(var(--score)*1%),rgba(255,255,255,.07) 0);position:relative}.ax-score-ring:before{content:"";position:absolute;inset:10px;border-radius:50%;background:#0b1020}.ax-score-number{z-index:1;font-size:34px;font-weight:950;color:var(--ax-text)!important}.ax-score-number small{font-size:11px;color:var(--ax-muted)!important}.ax-rule{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.055);font-size:11px}.ax-market-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.ax-market{padding:13px;border-radius:16px;background:rgba(13,19,34,.68);border:1px solid var(--ax-line)}.ax-market-time{font-size:20px;font-weight:900;color:var(--ax-cyan)!important;margin:5px 0}.ax-open{color:var(--ax-green)!important}.ax-closed{color:var(--ax-red)!important}.ax-trade-row{display:grid;grid-template-columns:1.5fr .8fr .8fr .8fr .8fr;gap:10px;padding:13px 14px;border-radius:15px;background:rgba(12,18,32,.72);border:1px solid rgba(255,255,255,.055);margin-bottom:8px;font-size:11px}.ax-chip{display:inline-block;padding:4px 8px;border-radius:99px;background:rgba(79,124,255,.12);font-size:9px}.ax-empty{min-height:290px;display:grid;place-items:center;text-align:center;border:1px dashed rgba(67,232,255,.28);border-radius:20px}.ax-empty-title{font-size:17px;font-weight:850}.ax-empty-sub{font-size:12px;color:var(--ax-muted)!important;max-width:430px;margin:auto}


    /* AXION PRIME X8 — PREMIUM PROP SIDEBAR */
    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 15% 8%, rgba(82,102,255,.16), transparent 25%),
            linear-gradient(180deg,#070a14 0%,#090d19 60%,#060912 100%) !important;
        border-right:1px solid rgba(105,128,255,.18) !important;
        box-shadow:18px 0 50px rgba(0,0,0,.28);
    }
    section[data-testid="stSidebar"] > div { padding-top:1rem !important; }
    .ap-side-brand{display:flex;align-items:center;gap:12px;padding:10px 8px 18px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:14px}
    .ap-orb{width:42px;height:42px;border-radius:14px;display:grid;place-items:center;font-weight:950;font-size:20px;background:linear-gradient(145deg,#27e7ff,#5f72ff 58%,#a54cff);box-shadow:0 0 30px rgba(53,212,255,.32);color:white!important}
    .ap-brand-title{font-weight:900;letter-spacing:.12em;font-size:15px;color:#fff!important}
    .ap-brand-sub{font-size:9px;letter-spacing:.22em;color:#71809e!important;margin-top:3px}
    .ap-profile-card{display:flex;gap:12px;align-items:center;padding:14px;border:1px solid rgba(118,139,255,.18);background:linear-gradient(145deg,rgba(22,29,51,.92),rgba(10,14,26,.96));border-radius:18px;box-shadow:inset 0 1px rgba(255,255,255,.04),0 16px 40px rgba(0,0,0,.22);margin-bottom:12px}
    .ap-avatar{width:54px;height:54px;border-radius:16px;object-fit:cover;border:1px solid rgba(63,225,255,.65);box-shadow:0 0 20px rgba(63,225,255,.18)}
    .ap-avatar-fallback{display:grid;place-items:center;background:linear-gradient(145deg,#18213b,#0a0f1c);font-size:25px}
    .ap-profile-copy{min-width:0}.ap-profile-name{font-size:14px;font-weight:850;color:#fff!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.ap-profile-mail{font-size:10px;color:#7886a3!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:190px;margin-top:3px}.ap-profile-meta{font-size:9px;color:#8291ae!important;margin-top:8px;display:flex;align-items:center;gap:6px}.ap-badge{padding:3px 7px;border-radius:999px;background:linear-gradient(90deg,#f7c84b,#ff8f3d);color:#121212!important;font-weight:900;letter-spacing:.08em}.ap-live-dot,.ap-ai-dot{width:7px;height:7px;border-radius:99px;display:inline-block;background:#21e6a4;box-shadow:0 0 12px #21e6a4}.ap-ai-dot{background:#42d7ff;box-shadow:0 0 12px #42d7ff}
    .ap-challenge-card{padding:13px 14px;border-radius:15px;background:linear-gradient(135deg,rgba(46,226,255,.09),rgba(130,77,255,.10));border:1px solid rgba(64,214,255,.18);margin-bottom:18px}.ap-challenge-top{display:flex;justify-content:space-between;font-size:9px;letter-spacing:.12em;color:#7888a5!important}.ap-challenge-top b{color:#47e7ff!important}.ap-challenge-value{font-size:20px;font-weight:900;color:#fff!important;margin:8px 0}.ap-challenge-value small{font-size:11px;color:#7583a0!important;font-weight:600}.ap-progress{height:5px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden}.ap-progress span{display:block;height:100%;background:linear-gradient(90deg,#32e6ff,#6f74ff,#a653ff);box-shadow:0 0 18px #53dfff;border-radius:99px}
    .ap-nav-label{font-size:9px;letter-spacing:.18em;color:#52617d!important;font-weight:800;margin:14px 8px 6px}
    section[data-testid="stSidebar"] .stButton>button{height:42px;border-radius:12px!important;border:1px solid transparent!important;background:transparent!important;color:#aeb8cc!important;justify-content:flex-start!important;padding:0 13px!important;font-weight:650!important;transition:.18s ease!important;box-shadow:none!important}
    section[data-testid="stSidebar"] .stButton>button:hover{background:linear-gradient(90deg,rgba(46,226,255,.10),rgba(115,82,255,.08))!important;border-color:rgba(77,213,255,.18)!important;color:#fff!important;transform:translateX(3px)}
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(90deg,rgba(40,220,255,.18),rgba(120,82,255,.15))!important;border:1px solid rgba(75,220,255,.32)!important;color:#fff!important;box-shadow:0 0 24px rgba(43,214,255,.10)!important}
    .ap-system-card{margin:16px 0 10px;padding:12px 14px;border-radius:14px;background:rgba(9,14,27,.72);border:1px solid rgba(255,255,255,.06);display:grid;grid-template-columns:1fr auto;gap:8px;font-size:9px;color:#71809d!important;letter-spacing:.08em}.ap-system-value{font-weight:900;color:#b8c4da!important}
</style>

    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


def aplicar_estilos_x5():
    st.markdown("""
    <style>
    :root{
        --x5-bg:#050816;
        --x5-card:rgba(8,14,31,.84);
        --x5-card-2:rgba(12,18,40,.92);
        --x5-border:rgba(105,97,255,.32);
        --x5-cyan:#28e7ff;
        --x5-violet:#8d4dff;
        --x5-green:#24f0a4;
        --x5-red:#ff4d78;
        --x5-text:#f5f7ff;
        --x5-muted:#8793b4;
    }
    .stApp{
        background:
          radial-gradient(circle at 17% 12%, rgba(0,209,255,.12), transparent 29%),
          radial-gradient(circle at 84% 9%, rgba(136,71,255,.15), transparent 28%),
          radial-gradient(circle at 52% 92%, rgba(255,43,136,.08), transparent 32%),
          linear-gradient(145deg,#040713 0%,#070a18 48%,#050612 100%) !important;
    }
    .block-container{max-width:1680px!important;padding-top:1.4rem!important;padding-bottom:3rem!important}
    .x5-topbar{position:relative;overflow:hidden;display:flex;justify-content:space-between;align-items:center;gap:18px;padding:20px 22px;border-radius:22px;border:1px solid rgba(82,214,255,.22);background:linear-gradient(135deg,rgba(7,16,35,.96),rgba(18,10,42,.94));box-shadow:0 20px 70px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.05);margin-bottom:16px}
    .x5-topbar:after{content:"";position:absolute;inset:auto -8% -90px 25%;height:170px;background:radial-gradient(circle,rgba(75,222,255,.24),transparent 62%);pointer-events:none}
    .x5-eyebrow{font-size:11px;letter-spacing:2px;font-weight:900;color:var(--x5-cyan)}
    .x5-title{font-size:30px;font-weight:950;color:var(--x5-text);line-height:1.12;margin-top:6px}
    .x5-sub{color:var(--x5-muted);font-size:13px;margin-top:8px}
    .x5-live{white-space:nowrap;padding:10px 14px;border-radius:999px;color:#aaffdf;border:1px solid rgba(36,240,164,.35);background:rgba(10,51,48,.48);font-size:12px;font-weight:800}
    .x5-live i{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--x5-green);box-shadow:0 0 16px var(--x5-green);margin-right:8px;animation:x5pulse 1.6s infinite}
    .x5-kpi{min-height:150px;position:relative;overflow:hidden;border-radius:20px;padding:18px 18px 15px;background:linear-gradient(155deg,rgba(13,20,42,.96),rgba(5,9,23,.96));border:1px solid rgba(113,131,201,.22);box-shadow:0 18px 45px rgba(0,0,0,.24),inset 0 1px 0 rgba(255,255,255,.04);transition:transform .22s ease,border-color .22s ease,box-shadow .22s ease}
    .x5-kpi:hover{transform:translateY(-4px);border-color:rgba(53,221,255,.46);box-shadow:0 24px 60px rgba(0,0,0,.35),0 0 28px rgba(59,218,255,.08)}
    .x5-kpi:before{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,var(--x5-cyan),var(--x5-violet))}
    .x5-kpi-label{font-size:10px;letter-spacing:1.3px;color:#8390b5;font-weight:900}
    .x5-kpi-value{font-size:29px;color:#fff;font-weight:950;margin-top:16px;line-height:1}
    .x5-kpi-meta{display:flex;justify-content:space-between;color:#91a0c6;font-size:11px;margin-top:13px}
    .x5-spark{height:30px;margin-top:12px;opacity:.9}.x5-spark svg{width:100%;height:100%;overflow:visible}
    .x5-pos{color:var(--x5-green)!important}.x5-neg{color:var(--x5-red)!important}
    .x5-panel{height:100%;border-radius:22px;padding:18px;background:linear-gradient(150deg,rgba(10,16,36,.94),rgba(7,10,25,.96));border:1px solid rgba(102,114,183,.23);box-shadow:0 20px 55px rgba(0,0,0,.27),inset 0 1px 0 rgba(255,255,255,.04);overflow:hidden}
    .x5-panel-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
    .x5-panel-title{font-size:15px;color:#f4f6ff;font-weight:950;letter-spacing:.3px}.x5-tag{font-size:9px;letter-spacing:1px;color:#7182ad;text-transform:uppercase}
    .x5-score{width:168px;height:168px;border-radius:50%;margin:10px auto 18px;display:grid;place-items:center;background:conic-gradient(var(--x5-cyan) 0 32%,var(--x5-violet) 32% 50%,rgba(255,255,255,.06) 50% 100%);box-shadow:0 0 45px rgba(74,174,255,.16);position:relative}
    .x5-score:after{content:"";position:absolute;inset:15px;border-radius:50%;background:radial-gradient(circle at 35% 25%,rgba(52,93,174,.22),#080c1c 66%);border:1px solid rgba(255,255,255,.06)}
    .x5-score-num{position:relative;z-index:2;font-size:43px;font-weight:950;color:#fff;text-align:center}.x5-score-num small{display:block;font-size:10px;color:#7481a6;letter-spacing:1px}
    .x5-rule{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.055);font-size:12px}.x5-rule span:first-child{color:#8a96b9}.x5-rule span:last-child{font-weight:850;color:#eef2ff}
    .x5-market-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.x5-market{border:1px solid rgba(94,112,183,.18);border-radius:15px;padding:12px;background:rgba(7,12,28,.74);transition:.2s ease}
    .x5-market:hover{transform:translateY(-2px);border-color:rgba(57,222,255,.34)}.x5-market strong{font-size:12px;color:#e9edff}.x5-market-time{font-size:21px;font-weight:950;color:#fff;margin:8px 0 3px}
    .x5-open{color:var(--x5-green);font-size:10px;font-weight:900}.x5-closed{color:var(--x5-red);font-size:10px;font-weight:900}
    .x5-event{display:grid;grid-template-columns:62px 1fr 72px;align-items:center;gap:10px;padding:11px 0;border-bottom:1px solid rgba(255,255,255,.05);font-size:11px}.x5-event b{color:#fff}.x5-event small{color:#8995b7}
    .x5-impact-high{color:#ff5a7f}.x5-impact-med{color:#ffd166}
    .x5-insight{border-left:2px solid var(--x5-cyan);padding:8px 10px;margin:8px 0;border-radius:0 8px 8px 0;background:rgba(38,224,255,.045);font-size:11px;color:#c7d1ef}
    .x5-trade-row{display:grid;grid-template-columns:1.4fr .8fr .8fr .8fr .9fr;gap:8px;align-items:center;padding:10px 11px;border-radius:12px;margin-bottom:8px;border:1px solid rgba(90,112,174,.14);background:rgba(7,12,27,.75);font-size:11px}
    .x5-chip{padding:4px 8px;border-radius:999px;background:rgba(71,97,170,.17);font-size:9px;font-weight:850}
    .x5-candle-field{position:fixed;inset:0;pointer-events:none;z-index:0;overflow:hidden;opacity:.26;mask-image:linear-gradient(to bottom,rgba(0,0,0,.8),rgba(0,0,0,.28))}
    .x5-candle-field span{position:absolute;bottom:-90px;width:7px;border-radius:2px;animation:x5float linear infinite;filter:drop-shadow(0 0 8px currentColor)}
    .x5-candle-field span:before{content:"";position:absolute;left:3px;top:-20px;width:1px;height:calc(100% + 40px);background:currentColor;opacity:.75}
    section[data-testid="stSidebar"]{background:radial-gradient(circle at 30% 8%,rgba(32,206,255,.10),transparent 27%),linear-gradient(180deg,#070b17,#080a17 55%,#050711)!important;border-right:1px solid rgba(67,185,255,.22)!important}
    section[data-testid="stSidebar"] .stButton>button{min-height:46px!important;border-radius:13px!important;background:linear-gradient(145deg,rgba(16,23,46,.92),rgba(8,12,27,.94))!important;border:1px solid rgba(92,114,180,.19)!important;color:#e7ebff!important;transition:.22s ease!important}
    section[data-testid="stSidebar"] .stButton>button:hover{transform:translateX(4px)!important;border-color:rgba(45,224,255,.55)!important;background:linear-gradient(100deg,rgba(15,71,103,.9),rgba(62,26,120,.9))!important;box-shadow:0 0 28px rgba(37,213,255,.11)!important}
    div[data-testid="stHorizontalBlock"]{position:relative;z-index:2}.stMarkdown,.stPlotlyChart,.stDataFrame,.stAlert,.stButton,.stSelectbox{position:relative;z-index:2}
    @keyframes x5pulse{0%,100%{opacity:.55;transform:scale(.86)}50%{opacity:1;transform:scale(1.15)}}
    @keyframes x5float{0%{transform:translateY(0) scaleY(.85);opacity:0}12%{opacity:.72}72%{opacity:.50}100%{transform:translateY(-115vh) scaleY(1.18);opacity:0}}
    @media(max-width:900px){.x5-market-grid{grid-template-columns:repeat(2,1fr)}.x5-title{font-size:23px}}
    </style>
    """, unsafe_allow_html=True)

def render_fondo_velas_x5():
    candles = []
    tones = ["#21f0a4","#ff436f","#2edcff","#8657ff"]
    heights = [34,58,23,73,42,65,29,82,48,38,69,26,55,77,32,61,45,86,36,72,51,28,66,41,79,33,57,88,46,64]
    for i, h in enumerate(heights):
        left = (i * 3.47 + 1.5) % 100
        delay = -(i * 0.73)
        duration = 15 + (i % 7) * 1.4
        tone = tones[i % len(tones)]
        candles.append(
            f'<span style="left:{left:.1f}%;height:{h}px;color:{tone};'
            f'background:{tone};animation-delay:{delay:.2f}s;animation-duration:{duration:.2f}s"></span>'
        )
    st.markdown('<div class="x5-candle-field">' + ''.join(candles) + '</div>', unsafe_allow_html=True)

aplicar_estilos_x5()
render_fondo_velas_x5()


def aplicar_estilos_x7_track_record():
    st.markdown("""
    <style>
    .x7-track-hero{
        padding:22px 24px;
        border-radius:22px;
        margin-bottom:16px;
        background:
          radial-gradient(circle at 85% 10%,rgba(132,76,255,.20),transparent 34%),
          linear-gradient(135deg,rgba(8,19,39,.96),rgba(17,9,39,.95));
        border:1px solid rgba(69,213,255,.25);
        box-shadow:0 22px 60px rgba(0,0,0,.30),inset 0 1px 0 rgba(255,255,255,.05);
    }
    .x7-track-kicker{font-size:10px;letter-spacing:2px;color:#2ee7ff;font-weight:900}
    .x7-track-title{font-size:30px;line-height:1.05;color:#fff;font-weight:950;margin-top:7px}
    .x7-track-sub{font-size:12px;color:#8997ba;margin-top:9px}

    .x7-summary-card{
        min-height:112px;border-radius:18px;padding:16px;
        background:linear-gradient(150deg,rgba(12,19,40,.96),rgba(6,10,24,.96));
        border:1px solid rgba(97,116,183,.22);
        box-shadow:0 16px 35px rgba(0,0,0,.20);
    }
    .x7-summary-label{font-size:9px;letter-spacing:1.2px;color:#7f8bad;font-weight:900}
    .x7-summary-value{font-size:27px;font-weight:950;color:#fff;margin-top:12px}
    .x7-summary-meta{font-size:10px;color:#8895b8;margin-top:8px}
    .x7-profit{color:#22eba1!important}.x7-loss{color:#ff4e78!important}

    .x7-month-shell{
        border-radius:22px;padding:18px;
        background:linear-gradient(150deg,rgba(8,14,32,.96),rgba(6,8,22,.97));
        border:1px solid rgba(96,108,178,.22);
        box-shadow:0 22px 55px rgba(0,0,0,.28);
        margin-top:14px;
    }
    .x7-month-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:13px}
    .x7-month-title{font-size:15px;color:#f4f7ff;font-weight:950}
    .x7-month-legend{font-size:9px;color:#7885aa;letter-spacing:.8px}
    .x7-weekday{
        text-align:center;color:#6f7b9d;font-size:9px;font-weight:900;
        letter-spacing:1px;padding:7px 0;
    }
    .x7-empty-cell{
        height:88px;border-radius:13px;border:1px solid rgba(255,255,255,.025);
        background:rgba(4,8,20,.22);
    }
    div[data-testid="column"] .x7-day-caption{
        text-align:center;font-size:9px;color:#7280a3;margin-top:-3px;margin-bottom:3px;
    }

    .x7-day-detail{
        border-radius:22px;padding:18px;margin-top:16px;
        background:linear-gradient(145deg,rgba(11,18,39,.97),rgba(8,10,25,.98));
        border:1px solid rgba(56,215,255,.23);
        box-shadow:0 24px 65px rgba(0,0,0,.30);
    }
    .x7-trade-card{
        border-radius:18px;padding:16px;margin:12px 0;
        background:linear-gradient(150deg,rgba(12,20,43,.96),rgba(7,11,26,.96));
        border:1px solid rgba(102,119,190,.22);
        box-shadow:0 14px 36px rgba(0,0,0,.22);
    }
    .x7-trade-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
    .x7-trade-asset{font-size:18px;font-weight:950;color:#fff}
    .x7-trade-date{font-size:10px;color:#7f8caf;margin-top:4px}
    .x7-pnl-pill{padding:8px 11px;border-radius:999px;font-weight:950;font-size:12px}
    .x7-pnl-win{color:#9cffdc;background:rgba(14,92,66,.38);border:1px solid rgba(37,235,161,.28)}
    .x7-pnl-loss{color:#ffb0c1;background:rgba(100,25,49,.38);border:1px solid rgba(255,75,118,.28)}
    .x7-pnl-be{color:#cbd4ee;background:rgba(58,70,108,.35);border:1px solid rgba(160,177,226,.19)}
    .x7-trade-grid{
        display:grid;grid-template-columns:repeat(6,1fr);gap:8px;margin-top:13px;
    }
    .x7-field{
        padding:10px;border-radius:12px;background:rgba(5,9,22,.62);
        border:1px solid rgba(86,104,170,.14);
    }
    .x7-field small{display:block;color:#7180a5;font-size:8px;letter-spacing:.8px}
    .x7-field b{display:block;color:#edf1ff;font-size:11px;margin-top:5px}
    .x7-notes{
        margin-top:12px;padding:12px;border-left:2px solid #2de2ff;
        border-radius:0 12px 12px 0;background:rgba(31,215,255,.045);
        color:#c7d0eb;font-size:11px;line-height:1.55;
    }
    @media(max-width:900px){
        .x7-trade-grid{grid-template-columns:repeat(2,1fr)}
        .x7-track-title{font-size:24px}
    }
    </style>
    """, unsafe_allow_html=True)

aplicar_estilos_x7_track_record()


def aplicar_estilos_x8():
    st.markdown("""
    <style>
    .block-container{
        max-width:1700px!important;
        padding:1.1rem 1.35rem 3rem!important;
    }
    section[data-testid="stSidebar"]{
        width:300px!important;
        min-width:300px!important;
        background:
          radial-gradient(circle at 25% 5%,rgba(30,208,255,.10),transparent 26%),
          linear-gradient(180deg,#050a16 0%,#080b18 58%,#050711 100%)!important;
        border-right:1px solid rgba(42,213,255,.22)!important;
    }
    section[data-testid="stSidebar"]>div{padding:18px 13px 22px!important}
    section[data-testid="stSidebar"] .stButton>button{
        min-height:46px!important;
        justify-content:flex-start!important;
        padding-left:16px!important;
        border-radius:10px!important;
        color:#dce3ff!important;
        background:linear-gradient(145deg,rgba(12,18,37,.97),rgba(7,11,25,.97))!important;
        border:1px solid rgba(78,98,166,.20)!important;
        font-size:13px!important;
        font-weight:780!important;
        transition:all .22s ease!important;
    }
    section[data-testid="stSidebar"] .stButton>button:hover{
        transform:translateX(4px)!important;
        border-color:rgba(67,220,255,.50)!important;
        background:linear-gradient(100deg,rgba(19,50,91,.98),rgba(57,25,108,.98))!important;
        box-shadow:0 0 26px rgba(47,217,255,.10)!important;
    }
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
        color:white!important;
        background:linear-gradient(100deg,#283f8f,#7736ca)!important;
        border-color:rgba(146,84,255,.85)!important;
        box-shadow:0 0 28px rgba(116,57,255,.24)!important;
    }
    .ax8-brand{display:flex;align-items:center;gap:12px;padding:8px 7px 20px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:16px}
    .ax8-logo{width:46px;height:46px;border-radius:13px;display:grid;place-items:center;background:linear-gradient(145deg,#20dfff,#8643ff);box-shadow:0 0 30px rgba(42,211,255,.25);color:white;font-size:21px;font-weight:950}
    .ax8-brand-name{color:#fff;font-size:15px;font-weight:950;letter-spacing:.8px}
    .ax8-brand-sub{color:#687697;font-size:7px;letter-spacing:2px;margin-top:5px}
    .ax8-online{margin-left:auto;width:8px;height:8px;border-radius:50%;background:#20e9a0;box-shadow:0 0 14px #20e9a0}
    .ax8-profile{padding:15px;margin-bottom:18px;border-radius:19px;border:1px solid rgba(61,205,255,.28);background:radial-gradient(circle at 18% 20%,rgba(48,202,255,.13),transparent 34%),linear-gradient(145deg,rgba(11,18,39,.98),rgba(8,10,25,.98));box-shadow:0 18px 42px rgba(0,0,0,.24)}
    .ax8-profile-row{display:flex;align-items:center;gap:12px}
    .ax8-avatar-ring{width:74px;height:74px;border-radius:50%;padding:4px;background:conic-gradient(#20dfff,#7745ff,#ff4f9a,#20dfff);box-shadow:0 0 28px rgba(72,188,255,.26)}
    .ax8-avatar-ring img,.ax8-avatar-fallback{width:66px;height:66px;border-radius:50%;object-fit:cover;border:3px solid #071020}
    .ax8-avatar-fallback{display:grid;place-items:center;background:#0b1125;color:white;font-size:23px;font-weight:900}
    .ax8-name{color:white;font-size:14px;font-weight:950}
    .ax8-badge{display:inline-block;padding:3px 7px;margin-left:6px;border-radius:999px;background:#8442ff;color:white;font-size:7px;letter-spacing:.6px}
    .ax8-email{color:#6e7b9d;font-size:8px;margin-top:5px;word-break:break-all}
    .ax8-capital{color:white;font-size:17px;font-weight:950;margin-top:9px}
    .ax8-capital-label{color:#55ceff;font-size:8px;letter-spacing:1px;margin-top:2px}
    .ax8-progress{height:5px;margin-top:12px;border-radius:999px;overflow:hidden;background:#17203b}
    .ax8-progress i{display:block;height:100%;background:linear-gradient(90deg,#25dfff,#7e46ff);box-shadow:0 0 10px #4edfff}
    .ax8-progress-meta{display:flex;justify-content:space-between;margin-top:6px;color:#657292;font-size:8px}
    .ax8-section{margin:18px 5px 9px;color:#586585;font-size:8px;font-weight:900;letter-spacing:1.7px}
    .ax8-system{margin-top:12px;padding:10px 12px;border-radius:13px;background:rgba(6,11,25,.75);border:1px solid rgba(78,96,156,.18)}
    .ax8-system div{display:flex;justify-content:space-between;align-items:center;padding:7px 0;color:#8c98ba;font-size:9px}
    .ax8-system b{color:#20e79d;font-size:8px}
    .ax8-dot{display:inline-block;width:6px;height:6px;margin-right:7px;border-radius:50%;background:#20e79d;box-shadow:0 0 10px #20e79d}
    .x5-topbar{border-radius:14px!important;padding:16px 18px!important}
    .x5-kpi{border-radius:13px!important;min-height:142px!important}
    .x5-panel{border-radius:14px!important}
    .x5-candle-field{opacity:.34!important}
    </style>
    """, unsafe_allow_html=True)

aplicar_estilos_x8()



def aplicar_refuerzo_visual_x6():
    st.markdown("""
    <style>
    /* Sidebar inspirado en prop firms premium */
    section[data-testid="stSidebar"]{
        min-width:300px!important;max-width:300px!important;
        box-shadow:18px 0 70px rgba(0,0,0,.34)!important;
    }
    section[data-testid="stSidebar"]:before{
        content:"";position:absolute;inset:0;pointer-events:none;
        background:
          linear-gradient(rgba(37,219,255,.035) 1px,transparent 1px),
          linear-gradient(90deg,rgba(37,219,255,.035) 1px,transparent 1px);
        background-size:30px 30px;mask-image:linear-gradient(to bottom,#000,transparent 78%);
    }
    section[data-testid="stSidebar"] .stButton>button{
        justify-content:flex-start!important;text-align:left!important;padding-left:18px!important;
        font-size:13px!important;font-weight:800!important;letter-spacing:.15px!important;
    }
    section[data-testid="stSidebar"] .stButton>button:focus{
        border-color:#5b63ff!important;box-shadow:0 0 0 1px #3fe4ff,0 0 28px rgba(92,74,255,.22)!important;
    }
    /* Cabecera con una banda de velas más parecida a la referencia */
    .x5-topbar{
        min-height:126px!important;padding:25px 28px!important;
        background:
          linear-gradient(90deg,rgba(5,11,27,.96),rgba(10,8,31,.84)),
          repeating-linear-gradient(90deg,transparent 0 36px,rgba(34,225,255,.035) 37px 38px)!important;
    }
    .x5-topbar:before{
        content:"";position:absolute;left:26%;right:7%;top:8px;height:100px;opacity:.30;
        background:
          linear-gradient(90deg,transparent 0 2%,#24f0a4 2% 2.5%,transparent 2.5% 6%,#ff4d78 6% 6.7%,transparent 6.7% 11%,#28e7ff 11% 11.6%,transparent 11.6% 16%,#8d4dff 16% 16.6%,transparent 16.6% 22%,#24f0a4 22% 22.7%,transparent 22.7% 29%,#ff4d78 29% 29.5%,transparent 29.5% 37%,#24f0a4 37% 37.8%,transparent 37.8% 47%,#8d4dff 47% 47.7%,transparent 47.7% 59%,#28e7ff 59% 59.8%,transparent 59.8% 71%,#ff4d78 71% 71.7%,transparent 71.7% 84%,#24f0a4 84% 84.8%,transparent 84.8%);
        filter:drop-shadow(0 0 8px rgba(53,225,255,.45));
        transform:skewY(-4deg);pointer-events:none;
    }
    .x5-kpi{min-height:142px!important}.x5-kpi-value{font-size:27px!important}
    .x5-panel{border-color:rgba(92,79,255,.28)!important}
    div[data-testid="stFileUploader"]{border-radius:16px!important;overflow:hidden}
    .stForm{border:1px solid rgba(76,210,255,.17)!important;border-radius:20px!important;padding:18px!important;background:rgba(7,12,28,.44)!important}
    @media(max-width:1100px){section[data-testid="stSidebar"]{min-width:260px!important;max-width:260px!important}}
    </style>
    """, unsafe_allow_html=True)

aplicar_refuerzo_visual_x6()




# AXION PRIME X8 — Fondo animado de velas + sidebar premium
def aplicar_fx_x4():
    st.markdown("""
    <style>
    .stApp::before{
      content:"";position:fixed;inset:0;pointer-events:none;z-index:0;opacity:.18;
      background:
        linear-gradient(rgba(55,230,255,.035) 1px,transparent 1px),
        linear-gradient(90deg,rgba(55,230,255,.035) 1px,transparent 1px),
        radial-gradient(circle at 82% 18%,rgba(139,92,246,.13),transparent 28%),
        radial-gradient(circle at 18% 78%,rgba(34,211,238,.10),transparent 28%);
      background-size:48px 48px,48px 48px,auto,auto;animation:axGrid 18s linear infinite}
    @keyframes axGrid{to{background-position:48px 48px,48px 48px,0 0,0 0}}
    .ax-candle-tape{position:fixed;right:2vw;bottom:1vh;width:min(760px,58vw);height:230px;
      pointer-events:none;z-index:0;opacity:.20;overflow:hidden;mask-image:linear-gradient(90deg,transparent,#000 18%,#000)}
    .ax-candle-track{position:absolute;inset:0;display:flex;align-items:center;gap:13px;animation:axTape 22s linear infinite}
    @keyframes axTape{to{transform:translateX(-48%)}}
    .ax-candle{position:relative;width:9px;height:var(--h);flex:0 0 9px}
    .ax-candle:before{content:"";position:absolute;left:4px;top:-18px;bottom:-18px;width:1px;background:currentColor}
    .ax-candle:after{content:"";position:absolute;inset:0;border-radius:2px;background:currentColor;box-shadow:0 0 14px currentColor}
    .ax-up{color:#2ee6a6;transform:translateY(var(--y))}.ax-down{color:#ff4d7d;transform:translateY(var(--y))}
    section[data-testid="stSidebar"]{background:linear-gradient(180deg,#07111c,#080914 48%,#060811)!important}
    section[data-testid="stSidebar"] div.stButton>button{
      background:linear-gradient(135deg,rgba(16,28,48,.96),rgba(13,15,32,.96))!important;
      border:1px solid rgba(87,138,205,.22)!important;color:#eaf5ff!important;min-height:44px;
      box-shadow:inset 0 1px 0 rgba(255,255,255,.025),0 8px 24px rgba(0,0,0,.15)!important}
    section[data-testid="stSidebar"] div.stButton>button:hover{
      transform:translateY(-1px);border-color:rgba(45,226,255,.65)!important;
      background:linear-gradient(135deg,rgba(11,94,120,.34),rgba(92,50,180,.28))!important;
      box-shadow:0 0 22px rgba(45,226,255,.12)!important}
    section[data-testid="stSidebar"] div.stButton>button p{color:#eaf5ff!important;font-weight:700!important}
    [data-testid="stAppViewContainer"]>.main{position:relative;z-index:1}
    </style>""",unsafe_allow_html=True)
    hs=[34,58,42,76,48,91,63,37,70,53,85,44,66,96,52,74,40,88,60,47,79,55,93,43,
        62,82,49,72,39,89,57,68,45,95,51,77,36,84,59,46,73,54,90,41,64,80,50,71]
    ys=[35,18,43,7,29,-2,14,40,9,26,-6,31,12,-10,24,4,38,-4,16,33,2,22,-8,36,
        11,-3,28,6,41,-7,20,1,32,-11,25,5,39,-5,17,30,8,21,-9,34,13,0,27,10]
    cs=[]
    for i,(h,y) in enumerate(zip(hs,ys)):
        cls="ax-up" if i%3!=1 else "ax-down"
        cs.append(f'<span class="ax-candle {cls}" style="--h:{h}px;--y:{y}px"></span>')
    tape="".join(cs+cs)
    st.markdown(f'<div class="ax-candle-tape"><div class="ax-candle-track">{tape}</div></div>',unsafe_allow_html=True)

aplicar_fx_x4()

# AXION PRIME X8 — Command Deck visual override
st.markdown(
    r"""
    <style>
    section[data-testid="stSidebar"] {
      min-width: 320px !important; max-width: 320px !important;
      background:
        radial-gradient(circle at 18% 0%, rgba(20,220,255,.13), transparent 28%),
        radial-gradient(circle at 95% 35%, rgba(125,72,255,.12), transparent 30%),
        linear-gradient(180deg,#060914 0%,#080b17 52%,#050711 100%) !important;
      border-right:1px solid rgba(95,218,255,.18)!important;
      box-shadow:24px 0 80px rgba(0,0,0,.35)!important;
    }
    section[data-testid="stSidebar"] > div {padding:14px 14px 22px!important;}
    .x3-brand-shell{position:relative;display:flex;align-items:center;gap:11px;padding:10px 8px 16px;margin-bottom:12px;border-bottom:1px solid rgba(255,255,255,.07)}
    .x3-brand-mark{width:46px;height:46px;border-radius:15px;display:grid;place-items:center;background:linear-gradient(145deg,#22e4ff,#405cff 55%,#a443ff);box-shadow:0 0 32px rgba(38,211,255,.35),inset 0 1px rgba(255,255,255,.5);font-weight:950;color:white;letter-spacing:-2px}
    .x3-brand-mark span{font-size:18px}.x3-brand-name{font-weight:900;letter-spacing:.7px;font-size:15px}.x3-brand-kicker{font-size:8px;letter-spacing:1.7px;color:#65738d;margin-top:2px}.x3-pulse{margin-left:auto;width:8px;height:8px;border-radius:50%;background:#20efb2;box-shadow:0 0 0 5px rgba(32,239,178,.08),0 0 15px #20efb2}
    .x3-identity-card{display:flex;gap:12px;align-items:center;padding:13px;border-radius:18px;background:linear-gradient(145deg,rgba(19,27,49,.92),rgba(8,12,24,.96));border:1px solid rgba(84,205,255,.22);box-shadow:inset 0 1px rgba(255,255,255,.06),0 14px 40px rgba(0,0,0,.28);margin-bottom:12px}
    .x3-avatar-ring{padding:2px;border-radius:16px;background:linear-gradient(150deg,#22e4ff,#7d4cff)}.x3-avatar{width:54px;height:54px;border-radius:14px;object-fit:cover;display:block}.x3-avatar-fallback{display:grid;place-items:center;background:#10182a;color:#fff;font-weight:900;font-size:22px}.x3-id-main{min-width:0;flex:1}.x3-id-row{display:flex;align-items:center;gap:7px}.x3-id-row b{font-size:13px}.x3-rank{font-size:8px;padding:3px 7px;border-radius:99px;background:rgba(255,199,50,.14);border:1px solid rgba(255,199,50,.35);color:#ffd369;font-weight:900;letter-spacing:.7px}.x3-email{font-size:9px;color:#74829b;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin:4px 0 8px}.x3-account-line{display:flex;justify-content:space-between;align-items:end}.x3-account-line span{font-size:13px;font-weight:850}.x3-account-line small{font-size:8px;color:#64728b}.x3-progress{height:4px;background:#141b2e;border-radius:99px;margin-top:6px;overflow:hidden}.x3-progress i{display:block;height:100%;background:linear-gradient(90deg,#22e4ff,#7d4cff);box-shadow:0 0 12px #22e4ff}
    .x3-section-head{display:flex;justify-content:space-between;align-items:center;margin:15px 4px 7px}.x3-section-head span{font-size:9px;letter-spacing:1.5px;color:#5d6b83;font-weight:900}.x3-section-head em{font-style:normal;font-size:8px;color:#2ee6bc;border:1px solid rgba(46,230,188,.25);padding:2px 6px;border-radius:99px}
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"]{gap:7px!important}
    section[data-testid="stSidebar"] .stButton>button{min-height:43px!important;border-radius:13px!important;background:linear-gradient(145deg,rgba(18,25,44,.78),rgba(9,13,25,.88))!important;border:1px solid rgba(114,142,190,.14)!important;color:#aeb9cc!important;box-shadow:inset 0 1px rgba(255,255,255,.025)!important;transition:all .18s ease!important;justify-content:flex-start!important;padding:0 12px!important;font-size:11px!important}
    section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] .stButton>button{min-height:68px!important;justify-content:center!important;text-align:center!important;white-space:pre-line!important;padding:8px 5px!important}
    section[data-testid="stSidebar"] .stButton>button:hover{transform:translateY(-2px)!important;border-color:rgba(45,220,255,.38)!important;color:#fff!important;box-shadow:0 10px 25px rgba(0,0,0,.28),0 0 20px rgba(45,220,255,.08)!important}
    section[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(135deg,rgba(31,222,255,.22),rgba(126,70,255,.22))!important;border-color:rgba(61,220,255,.50)!important;color:#fff!important;box-shadow:inset 0 1px rgba(255,255,255,.08),0 0 25px rgba(42,208,255,.12)!important}
    .x3-status-grid{display:grid;grid-template-columns:1fr;gap:5px;padding:10px;border-radius:15px;background:rgba(8,13,25,.72);border:1px solid rgba(108,132,174,.13);margin-bottom:9px}.x3-status-grid>div{display:grid;grid-template-columns:10px 1fr auto;align-items:center;gap:7px;font-size:8px;letter-spacing:.7px;color:#78869d}.x3-status-grid b{font-size:8px;color:#b8c6da}.x3-status-grid i{width:6px;height:6px;border-radius:50%;display:block}.x3-status-grid .ok{background:#21edaf;box-shadow:0 0 8px #21edaf}.x3-status-grid .ai{background:#2bdcff;box-shadow:0 0 8px #2bdcff}.x3-status-grid .risk{background:#a36cff;box-shadow:0 0 8px #a36cff}
    @media(max-width:900px){section[data-testid="stSidebar"]{min-width:285px!important;max-width:285px!important}}
    </style>
    """,
    unsafe_allow_html=True,
)


def render_metric_card(icono, label, valor, sub=""):

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="metric-card">
            <div class="metric-label">{icono} {label}</div>
            <div class="metric-value">{valor}</div>
            <div class="metric-sub">{sub}</div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


# =========================================================
# 22. PAYWALL
# =========================================================

def render_paywall():

    st.markdown(
        "## 🔒 Tu período de prueba ha expirado"
    )

    st.markdown(
        "Continúa utilizando tu diario de trading, "
        "Track Record y herramientas de IA activando "
        "tu acceso PRO."
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="paywall-card">
                <h3>🟡 Suscripción Mensual</h3>
                <h2>$5.00 USD</h2>
                <p>Luego $2.50 USD / mes</p>
                <hr>
                <p>
                ✔️ Acceso ilimitado<br>
                ✔️ Track Record<br>
                ✔️ Auditoría IA<br>
                ✔️ Psicotrading<br>
                ✔️ Sin contrato
                </p>
                <a href="{LINK_BINANCE_INSCRIPCION}" target="_blank">
                <button style="background:#f0b90b; color:#000; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%;">
                🟡 Pagar con Binance Pay
                </button>
                </a>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="paywall-card">
                <h3>💎 Acceso Anual</h3>
                <h2>$20.00 USD</h2>
                <p>Ahorra frente al plan mensual</p>
                <hr>
                <p>
                🌟 1 año completo<br>
                🔒 Pago único<br>
                🎁 Actualizaciones futuras<br>
                🧠 IA prioritaria
                </p>
                <a href="{LINK_BINANCE_ANUAL}" target="_blank">
                <button style="background:#00f2fe; color:#000; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%;">
                💎 Pagar $20 USD
                </button>
                </a>
                </div>
                """
            ),
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
            f"[Renovación mensual $2.50]({LINK_BINANCE_RECURRENTE})"
        )

    with c2:

        st.markdown(
            "### 💬 Confirmar pago"
        )

        st.markdown(
            textwrap.dedent(
                f"""
                <a href="{LINK_TELEGRAM_SOPORTE}" target="_blank">
                <button style="background:#0088cc; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; width:100%;">
                💬 Enviar comprobante
                </button>
                </a>
                """
            ),
            unsafe_allow_html=True
        )


# =========================================================
# 23. AUTENTICACIÓN
# =========================================================

def render_auth():

    st.markdown('<div class="nx-login-shell">', unsafe_allow_html=True)

    left, right = st.columns([1.35, 0.85], gap="large")

    with left:

        st.markdown(
            textwrap.dedent(
                f"""
                <div class="nx-visual">
                  <div class="nx-hero-content">
                    <div class="nx-brand">
                      <div class="nx-brand-mark">⚡</div>
                      <div>
                        <div class="nx-brand-name">{APP_NAME}</div>
                        <div class="nx-brand-sub">TRADING INTELLIGENCE PLATFORM</div>
                      </div>
                    </div>
                    <div class="nx-kicker">Tu ventaja empieza con tus datos</div>
                    <div class="nx-hero-title">Opera con más<br><span class="nx-gradient-text">claridad.</span></div>
                    <div class="nx-hero-copy">
                      Convierte cada operación en inteligencia accionable.
                      Analiza tu rendimiento, disciplina, riesgo y emociones
                      desde un solo sistema operativo para traders.
                    </div>
                    <div class="nx-feature-grid">
                      <div class="nx-feature">◈ Track Record inteligente</div>
                      <div class="nx-feature">◈ Auditoría visual con IA</div>
                      <div class="nx-feature">◈ Psicotrading medible</div>
                      <div class="nx-feature">◈ Métricas de rendimiento</div>
                    </div>
                  </div>
                  <div class="nx-quote">“La consistencia no se adivina. Se diseña, se mide y se mejora.”</div>
                </div>
                """
            ),
            unsafe_allow_html=True
        )

    with right:

        st.markdown('<div class="nx-auth-card">', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="nx-brand">
              <div class="nx-brand-mark">⚡</div>
              <div>
                <div class="nx-brand-name">{APP_NAME}</div>
                <div class="nx-brand-sub">{APP_TAGLINE}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("## Bienvenido de vuelta 👋")
        st.caption("Accede a tu centro de inteligencia de trading")

        tab_login, tab_register, tab_reset = st.tabs(
            ["Iniciar sesión", "Crear cuenta", "Recuperar"]
        )

        with tab_login:

            with st.form("login_form", clear_on_submit=False):

                email = st.text_input(
                    "Correo electrónico",
                    placeholder="trader@correo.com",
                    key="login_email"
                )

                password = st.text_input(
                    "Contraseña",
                    type="password",
                    placeholder="••••••••",
                    key="login_password"
                )

                remember = st.checkbox(
                    "Mantener sesión iniciada",
                    value=True,
                    key="remember_login"
                )

                ingresar = st.form_submit_button(
                    "⚡ Entrar a AXION",
                    use_container_width=True
                )

            if ingresar:

                if not email or not password:
                    st.warning("Completa correo y contraseña.")
                else:
                    try:
                        client = get_supabase_client()
                        result = client.auth.sign_in_with_password(
                            {"email": email.strip(), "password": password}
                        )

                        if not result.user or not result.session:
                            st.error("Supabase no devolvió una sesión válida.")
                        else:
                            st.session_state.user = result.user
                            st.session_state.supabase_session = {
                                "access_token": result.session.access_token,
                                "refresh_token": result.session.refresh_token
                            }
                            st.session_state.authenticated = True
                            st.session_state.prefs_cargadas = False
                            st.session_state.pagina_actual = "Dashboard"
                            st.success("Acceso correcto. Preparando tu terminal…")
                            st.rerun()

                    except Exception as e:
                        mensaje = str(e)
                        if _es_error_de_conexion(e):
                            _forzar_reconexion_supabase()
                            st.error(
                                "No fue posible conectar con Supabase. "
                                "Reinicia la aplicación y vuelve a intentarlo."
                            )
                        elif "invalid login credentials" in mensaje.lower():
                            st.error("Correo o contraseña incorrectos.")
                        elif "email not confirmed" in mensaje.lower():
                            st.error("Debes confirmar tu correo antes de iniciar sesión.")
                        else:
                            st.error(f"No se pudo iniciar sesión: {mensaje}")

        with tab_register:

            with st.form("register_form", clear_on_submit=False):
                nombre = st.text_input(
                    "Nombre de trader",
                    placeholder="Trader Pro",
                    key="register_name"
                )
                email_reg = st.text_input(
                    "Correo electrónico",
                    placeholder="trader@correo.com",
                    key="register_email"
                )
                password_reg = st.text_input(
                    "Contraseña",
                    type="password",
                    key="register_password"
                )
                password2 = st.text_input(
                    "Repetir contraseña",
                    type="password",
                    key="register_password_2"
                )
                aceptar = st.checkbox(
                    "Acepto los términos y la política de privacidad",
                    key="accept_terms"
                )
                registrar = st.form_submit_button(
                    "Crear cuenta gratuita",
                    use_container_width=True
                )

            if registrar:
                if not nombre or not email_reg or not password_reg:
                    st.warning("Completa todos los campos.")
                elif password_reg != password2:
                    st.error("Las contraseñas no coinciden.")
                elif len(password_reg) < 8:
                    st.error("La contraseña debe tener al menos 8 caracteres.")
                elif not aceptar:
                    st.warning("Debes aceptar los términos para continuar.")
                else:
                    try:
                        client = get_supabase_client()
                        result = client.auth.sign_up(
                            {
                                "email": email_reg.strip(),
                                "password": password_reg,
                                "options": {
                                    "data": {
                                        "username": nombre.strip(),
                                        "capital_actual": 10000.0,
                                        "capital_meta": 15000.0,
                                        "reglas_disciplina": DEFAULT_RULES
                                    }
                                }
                            }
                        )
                        if result.user:
                            if result.session:
                                st.session_state.user = result.user
                                st.session_state.supabase_session = {
                                    "access_token": result.session.access_token,
                                    "refresh_token": result.session.refresh_token
                                }
                                st.session_state.authenticated = True
                                st.session_state.prefs_cargadas = False
                                st.session_state.pagina_actual = "Dashboard"
                                st.rerun()
                            else:
                                st.success(
                                    "Cuenta creada. Revisa tu correo para confirmar "
                                    "el registro y luego inicia sesión."
                                )
                    except Exception as e:
                        st.error(f"No se pudo crear la cuenta: {e}")

        with tab_reset:

            with st.form("reset_form"):
                email_reset = st.text_input(
                    "Correo registrado",
                    placeholder="trader@correo.com",
                    key="reset_email"
                )
                enviar_reset = st.form_submit_button(
                    "Enviar enlace de recuperación",
                    use_container_width=True
                )

            if enviar_reset:
                if not email_reset:
                    st.warning("Introduce tu correo.")
                else:
                    try:
                        app_url = st.secrets.get(
                            "APP_URL",
                            "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                        )
                        get_supabase_client().auth.reset_password_for_email(
                            email_reset.strip(),
                            {"redirectTo": app_url}
                        )
                        st.success("Enlace enviado. Revisa también Spam.")
                    except Exception as e:
                        st.error(f"No se pudo enviar el enlace: {e}")

        st.markdown("---")
        st.caption("Acceso seguro mediante Supabase Auth")

        if st.button(
            "Continuar con Google",
            key="google_login",
            use_container_width=True
        ):
            try:
                app_url = st.secrets.get(
                    "APP_URL",
                    "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                )
                result = get_supabase_client().auth.sign_in_with_oauth(
                    {
                        "provider": "google",
                        "options": {"redirect_to": app_url}
                    }
                )
                url_login = getattr(result, "url", None)
                if url_login:
                    st.link_button(
                        "Abrir acceso con Google →",
                        url_login,
                        use_container_width=True
                    )
            except Exception as e:
                st.error(f"Google aún no está configurado: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)



# =========================================================
# 24. SIDEBAR
# =========================================================


def render_sidebar(estado_sub):
    with st.sidebar:
        user = st.session_state.user
        metadata = getattr(user, "user_metadata", {}) or {}

        nombre = metadata.get("username", st.session_state.nombre_trader)
        email = getattr(user, "email", "") or ""
        foto_b64 = metadata.get("avatar_b64", "")
        es_admin = "Admin" in estado_sub
        badge = "FOUNDER" if es_admin else ("PRO" if "PRO" in estado_sub else "TRIAL")

        avatar = convertir_imagen_display(foto_b64)
        avatar_html = f'<img src="{avatar}">' if avatar else '<div class="ax8-avatar-fallback">AX</div>'

        progreso = min(
            1.0,
            max(
                0.0,
                st.session_state.capital_actual / max(st.session_state.capital_meta, 1),
            ),
        )

        st.markdown(
            """
            <div class="ax8-brand">
                <div class="ax8-logo">A</div>
                <div>
                    <div class="ax8-brand-name">AXION PRIME</div>
                    <div class="ax8-brand-sub">PERFORMANCE COMMAND OS · X8</div>
                </div>
                <div class="ax8-online"></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="ax8-profile">
                <div class="ax8-profile-row">
                    <div class="ax8-avatar-ring">{avatar_html}</div>
                    <div style="min-width:0;flex:1">
                        <div class="ax8-name">{nombre}<span class="ax8-badge">{badge}</span></div>
                        <div class="ax8-email">{email}</div>
                        <div class="ax8-capital">${st.session_state.capital_actual:,.2f}</div>
                        <div class="ax8-capital-label">CAPITAL ACTUAL</div>
                    </div>
                </div>
                <div class="ax8-progress"><i style="width:{progreso * 100:.1f}%"></i></div>
                <div class="ax8-progress-meta">
                    <span>{progreso * 100:.1f}% DE LA META</span>
                    <span>${st.session_state.capital_meta:,.0f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="ax8-section">NAVEGACIÓN PRINCIPAL</div>', unsafe_allow_html=True)

        principal = [
            ("📊", "Dashboard"),
            ("➕", "Registrar Trade"),
            ("📕", "Track Record"),
            ("🤖", "Chat IA"),
        ]

        for icono, pagina in principal:
            activo = st.session_state.pagina_actual == pagina
            if st.button(
                f"{icono}   {pagina}",
                key=f"nav_{pagina}",
                use_container_width=True,
                type="primary" if activo else "secondary",
            ):
                st.session_state.pagina_actual = pagina
                st.rerun()

        st.markdown('<div class="ax8-section">INTELIGENCIA AVANZADA</div>', unsafe_allow_html=True)

        modulos = [
            ("🧠", "Psicotrading"),
            ("🔍", "Análisis IA"),
            ("📈", "Proyecciones"),
            ("🧮", "Lotaje"),
            ("🗓️", "Calendario Económico"),
        ]

        if es_admin:
            modulos.append(("🛡️", "Panel Admin"))

        for icono, pagina in modulos:
            activo = st.session_state.pagina_actual == pagina
            if st.button(
                f"{icono}   {pagina}",
                key=f"nav_{pagina}",
                use_container_width=True,
                type="primary" if activo else "secondary",
            ):
                st.session_state.pagina_actual = pagina
                st.rerun()

        st.markdown('<div class="ax8-section">SISTEMA</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="ax8-system">
                <div><span><i class="ax8-dot"></i>Base de Datos</span><b>CONECTADO</b></div>
                <div><span><i class="ax8-dot"></i>AI Engine</span><b>ACTIVO</b></div>
                <div><span><i class="ax8-dot"></i>Risk Core</span><b>PROTEGIDO</b></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("⇥   Cerrar sesión", key="logout", use_container_width=True):
            try:
                get_supabase_client().auth.sign_out()
            except Exception:
                pass

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.session_state.pop("supabase_session", None)
            st.session_state.pop("supabase_client", None)
            st.session_state.pagina_actual = "Dashboard"
            st.rerun()


# =========================================================
# 24B. PÁGINA: PERFIL Y CONFIGURACIÓN (V9.1)
# =========================================================
#
# Antes este contenido (foto/nombre, meta de cuenta y reglas
# de disciplina) vivía todo apretado en el sidebar. Ahora es
# una página completa dentro del área principal, igual que en
# la referencia visual, y el sidebar queda solo con el menú.

def render_perfil_configuracion():

    user = st.session_state.user

    metadata = (
        getattr(user, "user_metadata", {}) or {}
    )

    nombre_actual = metadata.get(
        "username",
        st.session_state.nombre_trader
    )

    foto_b64 = metadata.get(
        "avatar_b64",
        ""
    )

    st.markdown(
        "## 👤 Perfil y Configuración"
    )

    col_izq, col_der = st.columns(2)

    with col_izq:

        st.markdown(
            "### ✏️ Datos del perfil"
        )

        nuevo_nombre = st.text_input(
            "Nombre",
            value=nombre_actual,
            key="profile_name"
        )

        nueva_foto = st.file_uploader(
            "Nueva foto",
            type=["jpg", "jpeg", "png", "webp"],
            key="profile_photo"
        )

        st.caption(
            "💡 La foto se guarda como base64 dentro del "
            "perfil de Supabase. Con fotos muy grandes, "
            "algunas configuraciones pueden rechazar el "
            "guardado; si eso pasa, usa una imagen más "
            "pequeña o pásate a Supabase Storage."
        )

        if st.button(
            "💾 Guardar perfil",
            key="save_profile"
        ):

            try:

                nueva_foto_b64 = foto_b64

                if nueva_foto:

                    nueva_foto_b64 = (
                        base64.b64encode(
                            nueva_foto.getvalue()
                        ).decode("utf-8")
                    )

                client = get_supabase_client()

                result = client.auth.update_user(
                    {
                        "data": {
                            "username": nuevo_nombre,
                            "avatar_b64": nueva_foto_b64
                        }
                    }
                )

                st.session_state.user = result.user

                st.session_state.nombre_trader = (
                    nuevo_nombre
                )

                st.success("Perfil actualizado.")

                st.rerun()

            except Exception as e:

                st.error(
                    f"❌ Error actualizando perfil: {e}"
                )

    with col_der:

        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        cap_actual = st.session_state.capital_actual

        cap_meta = st.session_state.capital_meta

        progreso = (
            min(1.0, max(0.0, cap_actual / cap_meta))
            if cap_meta > 0
            else 0
        )

        st.markdown(
            f"**Capital:** ${cap_actual:,.2f} / "
            f"${cap_meta:,.2f}"
        )

        st.progress(progreso)

        st.number_input(
            "Capital actual ($)",
            value=float(cap_actual),
            step=100.0,
            key="sidebar_capital"
        )

        st.number_input(
            "Meta ($)",
            value=float(cap_meta),
            step=500.0,
            key="sidebar_meta"
        )

        st.session_state.capital_actual = (
            st.session_state.sidebar_capital
        )

        st.session_state.capital_meta = (
            st.session_state.sidebar_meta
        )

        if st.button(
            "💾 Guardar meta",
            key="save_meta"
        ):

            try:

                client = get_supabase_client()

                result = client.auth.update_user(
                    {
                        "data": {
                            "capital_actual":
                                st.session_state.capital_actual,
                            "capital_meta":
                                st.session_state.capital_meta
                        }
                    }
                )

                st.session_state.user = result.user

                st.success("Meta guardada.")

            except Exception as e:

                st.error(
                    f"❌ No se pudo guardar la meta: {e}"
                )

    st.markdown("---")

    st.markdown(
        "### 📜 Mis Reglas de Disciplina"
    )

    nuevas_reglas = st.text_area(
        "Reglas",
        value=st.session_state.reglas_disciplina,
        height=180,
        key="rules_editor"
    )

    if st.button(
        "💾 Guardar reglas",
        key="save_rules"
    ):

        st.session_state.reglas_disciplina = nuevas_reglas

        try:

            client = get_supabase_client()

            result = client.auth.update_user(
                {
                    "data": {
                        "reglas_disciplina": nuevas_reglas
                    }
                }
            )

            st.session_state.user = result.user

            st.success("Reglas guardadas.")

        except Exception as e:

            st.error(
                f"❌ No se pudieron guardar las reglas: {e}"
            )


# =========================================================
# 24C. PÁGINA: SUSCRIPCIÓN (V9.1)
# =========================================================

def render_suscripcion_page(estado_sub):

    st.markdown(
        "## 💳 Suscripción"
    )

    if (
        "PRO" in estado_sub
        or "Admin" in estado_sub
    ):

        st.success(
            f"Tu plan actual: **{estado_sub}**"
        )

        st.caption(
            "Ya tienes acceso completo a todas las "
            "herramientas de la plataforma."
        )

    else:

        st.info(
            f"Tu plan actual: **{estado_sub}**"
        )

        render_paywall()


# =========================================================
# 25. FORMULARIO NUEVO TRADE
# =========================================================

def render_nuevo_trade(
    user_id,
    df_trades
):

    st.markdown(
        "### ➕ Registrar nueva operación"
    )

    st.markdown(
        textwrap.dedent(
            """
            <div class="ai-box">
            <h4>🧠 VISION CORE X3</h4>
            Sube una captura de TradingView y la IA intentará
            leer directamente:
            <b>ACTIVO · DIRECCIÓN · ENTRY · SL · TP · TIMEFRAME</b>
            </div>
            """
        ),
        unsafe_allow_html=True
    )

    left, right = st.columns(
        [1.2, 1]
    )

    # =====================================================
    # IMAGEN
    # =====================================================

    with right:

        st.markdown(
            "### 🖼️ Captura del Setup"
        )

        upload_before = st.file_uploader(
            "Captura TradingView",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="new_trade_before"
        )

        if upload_before:

            st.image(
                upload_before,
                caption="SETUP",
                use_container_width=True
            )

            if st.button(
                "🧠 ESCANEAR CON IA",
                key="scan_new_trade",
                use_container_width=True
            ):

                with st.spinner(
                    "🔎 La IA está leyendo activo, Entry, SL, TP y timeframe..."
                ):

                    resultado = (
                        analizar_captura_tradingview(
                            upload_before.getvalue(),
                            upload_before.type
                        )
                    )

                if resultado.get("error"):

                    st.session_state.scan_error = (
                        resultado["error"]
                    )

                    st.session_state.scan_message = ""

                    st.error(
                        resultado["error"]
                    )

                else:

                    st.session_state.scan_result = (
                        resultado
                    )

                    st.session_state.scan_error = ""

                    aplicar_resultado_ia(
                        resultado
                    )

                    st.session_state.scan_message = (
                        "IA completó los datos detectados."
                    )

                    # RERUN:
                    # ahora los widgets nacen con los
                    # valores detectados.
                    st.rerun()

        upload_after = st.file_uploader(
            "Captura DESPUÉS",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="new_trade_after"
        )

        if upload_after:

            st.image(
                upload_after,
                caption="RESULTADO",
                use_container_width=True
            )

        pnl = st.number_input(
            "Ganancia / Pérdida ($)",
            value=0.0,
            step=10.0,
            key="new_trade_pnl"
        )

    # =====================================================
    # FORMULARIO
    # =====================================================

    with left:

        st.markdown(
            "### 📝 Datos de la operación"
        )

        if st.session_state.scan_message:

            resultado_ia = (
                st.session_state.scan_result
                or {}
            )

            st.success(
                "✨ Los datos detectados fueron cargados "
                "en las casillas."
            )

            a, b, c, d = st.columns(4)

            with a:

                st.metric(
                    "Activo",
                    resultado_ia.get(
                        "asset"
                    )
                    or "No detectado"
                )

            with b:

                st.metric(
                    "Dirección",
                    resultado_ia.get(
                        "direction"
                    )
                    or "No detectada"
                )

            with c:

                entry_detected = (
                    resultado_ia.get(
                        "entry"
                    )
                )

                st.metric(
                    "Entry",
                    (
                        f"{entry_detected:.5f}"
                        if entry_detected is not None
                        else "No detectado"
                    )
                )

            with d:

                st.metric(
                    "Confianza",
                    f"{resultado_ia.get('confidence', 0):.0f}%"
                )

        # -------------------------------------------------
        # FECHA
        # -------------------------------------------------

        fecha = st.date_input(
            "Fecha",
            datetime.date.today(),
            key="new_trade_date"
        )

        c1, c2 = st.columns(2)

        # -------------------------------------------------
        # COLUMNA 1
        # -------------------------------------------------

        with c1:

            # No ponemos XAU como default.
            # Si IA no detecta activo queda vacío.

            asset_options = [
                "— Seleccionar activo —"
            ] + LISTA_ACTIVOS

            current_asset = (
                st.session_state.trade_asset
            )

            if (
                current_asset
                and current_asset in LISTA_ACTIVOS
            ):

                asset_index = (
                    asset_options.index(
                        current_asset
                    )
                )

            else:

                asset_index = 0

            selected_asset = st.selectbox(
                "Activo / Par",
                asset_options,
                index=asset_index,
                key="trade_asset_widget"
            )

            # Sincronizamos SOLO cuando cambia el widget
            st.session_state.trade_asset = (
                ""
                if selected_asset.startswith("—")
                else selected_asset
            )

            direction_options = [
                "LONG 🟢",
                "SHORT 🔴"
            ]

            direction_current = (
                st.session_state.trade_direction
            )

            if direction_current not in direction_options:

                direction_current = (
                    "LONG 🟢"
                )

            direction_index = (
                direction_options.index(
                    direction_current
                )
            )

            direccion = st.radio(
                "Dirección",
                direction_options,
                index=direction_index,
                horizontal=True,
                key="trade_direction_widget"
            )

            st.session_state.trade_direction = (
                direccion
            )

            entrada = st.number_input(
                "Precio de Entrada",
                min_value=0.0,
                value=float(
                    st.session_state.trade_entry
                ),
                format="%.5f",
                key="trade_entry_widget"
            )

            st.session_state.trade_entry = (
                entrada
            )

            sl = st.number_input(
                "Stop Loss",
                min_value=0.0,
                value=float(
                    st.session_state.trade_sl
                ),
                format="%.5f",
                key="trade_sl_widget"
            )

            st.session_state.trade_sl = (
                sl
            )

        # -------------------------------------------------
        # COLUMNA 2
        # -------------------------------------------------

        with c2:

            tp = st.number_input(
                "Take Profit",
                min_value=0.0,
                value=float(
                    st.session_state.trade_tp
                ),
                format="%.5f",
                key="trade_tp_widget"
            )

            st.session_state.trade_tp = (
                tp
            )

            current_tf = (
                st.session_state.trade_timeframe
            )

            if current_tf not in TIMEFRAMES:

                current_tf = ""

            tf_index = TIMEFRAMES.index(
                current_tf
            )

            timeframe = st.selectbox(
                "Timeframe",
                TIMEFRAMES,
                index=tf_index,
                key="trade_timeframe_widget"
            )

            st.session_state.trade_timeframe = (
                timeframe
            )

            rr = calcular_rr(
                entrada,
                sl,
                tp
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

        # -------------------------------------------------
        # DATOS DETECTADOS
        # -------------------------------------------------

        if st.session_state.scan_result:

            resultado_ia = (
                st.session_state.scan_result
            )

            st.markdown(
                "### 🔍 Lectura de IA"
            )

            x1, x2, x3 = st.columns(3)

            with x1:

                if resultado_ia.get("asset"):

                    st.success(
                        f"Activo: "
                        f"{resultado_ia['asset']}"
                    )

                else:

                    st.warning(
                        "Activo no detectado"
                    )

            with x2:

                if resultado_ia.get("entry") is not None:

                    st.success(
                        f"Entry: "
                        f"{resultado_ia['entry']}"
                    )

                else:

                    st.warning(
                        "Entry no detectado"
                    )

            with x3:

                if (
                    resultado_ia.get("sl")
                    is not None
                    and
                    resultado_ia.get("tp")
                    is not None
                ):

                    st.success(
                        "SL / TP detectados"
                    )

                else:

                    st.warning(
                        "Falta SL o TP"
                    )

        # -------------------------------------------------
        # PSICOTRADING
        # -------------------------------------------------

        st.markdown(
            "### 🧠 Psicotrading"
        )

        emociones = [

            "Disciplinado / Neutro 🧘",

            "Ansioso ⚡",

            "FOMO / Miedo a perderse el movimiento 🚀",

            "Venganza / Frustrado 🛑",

            "Eufórico / Sobre-confiado 😎"
        ]

        emocion = st.selectbox(
            "Estado emocional",
            emociones,
            key="trade_emotion"
        )

        notas = st.text_area(
            "Notas emocionales",
            placeholder=(
                "¿Respetaste tu plan? "
                "¿Qué sentiste antes y después?"
            ),
            key="trade_notes"
        )

        # -------------------------------------------------
        # BOTONES
        # -------------------------------------------------

        b1, b2 = st.columns(2)

        with b1:

            guardar = st.button(
                "💾 GUARDAR TRADE",
                key="save_new_trade",
                use_container_width=True
            )

        with b2:

            limpiar = st.button(
                "🧹 LIMPIAR",
                key="clear_new_trade",
                use_container_width=True
            )

        if limpiar:

            limpiar_formulario_trade()

            st.rerun()

        if guardar:

            if not st.session_state.trade_asset:

                st.error(
                    "⚠️ Debes seleccionar o detectar un activo."
                )

            elif entrada <= 0:

                st.error(
                    "⚠️ La entrada debe ser mayor que 0."
                )

            elif sl <= 0:

                st.error(
                    "⚠️ El Stop Loss es obligatorio."
                )

            elif tp <= 0:

                st.error(
                    "⚠️ El Take Profit es obligatorio."
                )

            else:

                data = {

                    "fecha":
                        str(fecha),

                    "par":
                        st.session_state.trade_asset,

                    "direccion":
                        st.session_state.trade_direction,

                    "precio_entrada":
                        float(entrada),

                    "stop_loss":
                        float(sl),

                    "take_profit":
                        float(tp),

                    "rr":
                        float(rr),

                    "timeframe":
                        st.session_state.trade_timeframe,

                    "resultado":
                        resultado,

                    "emocion":
                        emocion,

                    "notas_emocionales":
                        notas,

                    "beneficio_usd":
                        float(pnl),

                    "trades_cant":
                        1,

                    "img_before":
                        (
                            procesar_imagen_b64(
                                upload_before
                            )
                            if upload_before
                            else ""
                        ),

                    "img_after":
                        (
                            procesar_imagen_b64(
                                upload_after
                            )
                            if upload_after
                            else ""
                        )
                }

                if guardar_trade_supabase(
                    user_id,
                    data
                ):

                    st.success(
                        "✅ Trade guardado correctamente."
                    )

                    st.session_state.selected_trade_day = str(fecha)

                    # Limpiar tanto el estado lógico como los widgets visibles.
                    limpiar_formulario_trade()
                    for widget_key in [
                        "trade_asset_widget",
                        "trade_direction_widget",
                        "trade_entry_widget",
                        "trade_sl_widget",
                        "trade_tp_widget",
                        "trade_timeframe_widget",
                        "new_trade_pnl",
                        "new_trade_before",
                        "new_trade_after",
                    ]:
                        st.session_state.pop(widget_key, None)

                    st.session_state.pagina_actual = "Track Record"
                    st.rerun()


# =========================================================
# 26. EDITAR TRADE
# =========================================================

def editar_trade_ui(
    row,
    user_id
):

    trade_id = row.get(
        "id"
    )

    fecha_original = row.get(
        "fecha",
        str(datetime.date.today())
    )

    try:

        fecha_default = (
            datetime.date.fromisoformat(
                str(fecha_original)[:10]
            )
        )

    except Exception:

        fecha_default = (
            datetime.date.today()
        )

    par_actual = (
        normalizar_activo(
            row.get("par", "")
        )
        or ""
    )

    if par_actual not in LISTA_ACTIVOS:

        par_actual = ""

    resultados = [
        "WIN 🟢",
        "LOSS 🔴",
        "BE ⚪"
    ]

    resultado_actual = row.get(
        "resultado",
        "BE ⚪"
    )

    if resultado_actual not in resultados:

        resultado_actual = "BE ⚪"

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

    if emocion_actual not in emociones:

        emocion_actual = emociones[0]

    c1, c2 = st.columns(2)

    with c1:

        fecha = st.date_input(
            "Fecha",
            value=fecha_default,
            key=f"edit_fecha_{trade_id}"
        )

        asset_options = [
            "— Seleccionar —"
        ] + LISTA_ACTIVOS

        par = st.selectbox(
            "Activo",
            asset_options,
            index=(
                asset_options.index(
                    par_actual
                )
                if par_actual in asset_options
                else 0
            ),
            key=f"edit_par_{trade_id}"
        )

        if par.startswith("—"):

            par = ""

        direccion_actual = normalizar_direccion(
            row.get(
                "direccion",
                ""
            )
        )

        direccion = st.radio(
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

        entrada = st.number_input(
            "Precio Entrada",
            min_value=0.0,
            value=float(
                row.get(
                    "precio_entrada",
                    0
                )
                or 0
            ),
            format="%.5f",
            key=f"edit_entry_{trade_id}"
        )

        sl = st.number_input(
            "Stop Loss",
            min_value=0.0,
            value=float(
                row.get(
                    "stop_loss",
                    0
                )
                or 0
            ),
            format="%.5f",
            key=f"edit_sl_{trade_id}"
        )

        tp = st.number_input(
            "Take Profit",
            min_value=0.0,
            value=float(
                row.get(
                    "take_profit",
                    0
                )
                or 0
            ),
            format="%.5f",
            key=f"edit_tp_{trade_id}"
        )

        tf_actual = normalizar_timeframe(
            row.get(
                "timeframe",
                ""
            )
        )

        timeframe = st.selectbox(
            "Timeframe",
            TIMEFRAMES,
            index=(
                TIMEFRAMES.index(
                    tf_actual
                )
                if tf_actual in TIMEFRAMES
                else 0
            ),
            key=f"edit_tf_{trade_id}"
        )

    with c2:

        rr = calcular_rr(
            entrada,
            sl,
            tp
        )

        st.metric(
            "Risk : Reward",
            f"1 : {rr:.2f}"
        )

        resultado = st.selectbox(
            "Resultado",
            resultados,
            index=resultados.index(
                resultado_actual
            ),
            key=f"edit_result_{trade_id}"
        )

        emocion = st.selectbox(
            "Estado emocional",
            emociones,
            index=emociones.index(
                emocion_actual
            ),
            key=f"edit_emotion_{trade_id}"
        )

        pnl = st.number_input(
            "PnL ($)",
            value=float(
                row.get(
                    "beneficio_usd",
                    0
                )
                or 0
            ),
            step=10.0,
            key=f"edit_pnl_{trade_id}"
        )

        notas = st.text_area(
            "Notas emocionales",
            value=(
                row.get(
                    "notas_emocionales",
                    ""
                )
                or ""
            ),
            height=130,
            key=f"edit_notes_{trade_id}"
        )

        imagen_before = st.file_uploader(
            "Cambiar ANTES",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_before_{trade_id}"
        )

        imagen_after = st.file_uploader(
            "Cambiar DESPUÉS",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_after_{trade_id}"
        )

    old_before = row.get(
        "img_before",
        ""
    )

    old_after = row.get(
        "img_after",
        ""
    )

    p1, p2 = st.columns(2)

    with p1:

        st.markdown(
            "**🖼️ ANTES actual**"
        )

        img = convertir_imagen_display(
            old_before
        )

        if img:

            st.image(
                img,
                use_container_width=True
            )

        else:

            st.caption(
                "No hay imagen."
            )

    with p2:

        st.markdown(
            "**🖼️ DESPUÉS actual**"
        )

        img = convertir_imagen_display(
            old_after
        )

        if img:

            st.image(
                img,
                use_container_width=True
            )

        else:

            st.caption(
                "No hay imagen."
            )

    save, cancel = st.columns(2)

    with save:

        guardar = st.button(
            "💾 Guardar cambios",
            key=f"save_edit_{trade_id}"
        )

    with cancel:

        cancelar = st.button(
            "↩️ Cancelar",
            key=f"cancel_edit_{trade_id}"
        )

    if cancelar:

        st.session_state.editing_trade_id = None

        st.rerun()

    if guardar:

        if not par:

            st.error(
                "Selecciona un activo."
            )

            return

        final_before = (
            procesar_imagen_b64(
                imagen_before
            )
            if imagen_before
            else old_before
        )

        final_after = (
            procesar_imagen_b64(
                imagen_after
            )
            if imagen_after
            else old_after
        )

        data = {

            "fecha":
                str(fecha),

            "par":
                par,

            "direccion":
                direccion,

            "precio_entrada":
                entrada,

            "stop_loss":
                sl,

            "take_profit":
                tp,

            "rr":
                rr,

            "timeframe":
                timeframe,

            "resultado":
                resultado,

            "emocion":
                emocion,

            "notas_emocionales":
                notas,

            "beneficio_usd":
                pnl,

            "trades_cant":
                1,

            "img_before":
                final_before,

            "img_after":
                final_after
        }

        if actualizar_trade_supabase(
            trade_id,
            user_id,
            data
        ):

            st.success(
                "✅ Trade actualizado."
            )

            st.session_state.editing_trade_id = None

            st.rerun()


# =========================================================
# 27. TRACK RECORD
# =========================================================


def _x7_trade_day_button(day, pnl_day, count, selected=False):
    if pnl_day > 0:
        icon = "🟢"
        pnl_text = f"+${pnl_day:,.2f}"
    elif pnl_day < 0:
        icon = "🔴"
        pnl_text = f"-${abs(pnl_day):,.2f}"
    else:
        icon = "⚪"
        pnl_text = "$0.00"

    prefix = "▶ " if selected else ""
    return f"{prefix}{day.day:02d}\n{icon} {pnl_text}\n{count} trade{'s' if count != 1 else ''}"


def _x7_render_trade_detail(row, user_id):
    trade_id = row.get("id")
    pnl_value = float(row.get("beneficio_usd", 0) or 0)

    if pnl_value > 0:
        pnl_class = "x7-pnl-win"
        pnl_text = f"+${pnl_value:,.2f}"
    elif pnl_value < 0:
        pnl_class = "x7-pnl-loss"
        pnl_text = f"-${abs(pnl_value):,.2f}"
    else:
        pnl_class = "x7-pnl-be"
        pnl_text = "$0.00"

    st.markdown(
        f"""
        <div class="x7-trade-card">
          <div class="x7-trade-head">
            <div>
              <div class="x7-trade-asset">{row.get('par', 'Activo sin nombre')}</div>
              <div class="x7-trade-date">{row.get('fecha', '')} · {row.get('resultado', '—')}</div>
            </div>
            <div class="x7-pnl-pill {pnl_class}">{pnl_text}</div>
          </div>
          <div class="x7-trade-grid">
            <div class="x7-field"><small>DIRECCIÓN</small><b>{row.get('direccion', '—')}</b></div>
            <div class="x7-field"><small>TIMEFRAME</small><b>{row.get('timeframe', '—')}</b></div>
            <div class="x7-field"><small>ENTRADA</small><b>{row.get('precio_entrada', 0)}</b></div>
            <div class="x7-field"><small>STOP LOSS</small><b>{row.get('stop_loss', 0)}</b></div>
            <div class="x7-field"><small>TAKE PROFIT</small><b>{row.get('take_profit', 0)}</b></div>
            <div class="x7-field"><small>R:R</small><b>1 : {float(row.get('rr', 0) or 0):.2f}</b></div>
          </div>
          <div class="x7-notes"><b>🧠 Emoción:</b> {row.get('emocion', 'Sin registrar')}<br>
          <b>📝 Notas:</b> {row.get('notas_emocionales', '') or 'No escribiste notas para esta operación.'}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    img_before = convertir_imagen_display(row.get("img_before"))
    img_after = convertir_imagen_display(row.get("img_after"))

    image_cols = st.columns(2)
    with image_cols[0]:
        st.caption("1️⃣ CAPTURA ANTES")
        if img_before:
            st.image(img_before, use_container_width=True)
        else:
            st.info("Sin captura inicial.")

    with image_cols[1]:
        st.caption("2️⃣ CAPTURA DESPUÉS")
        if img_after:
            st.image(img_after, use_container_width=True)
        else:
            st.info("Sin captura final.")

    action_cols = st.columns([1, 1, 3])
    with action_cols[0]:
        if st.button("✏️ Editar", key=f"x7_edit_{trade_id}", use_container_width=True):
            st.session_state.editing_trade_id = trade_id
            st.rerun()

    with action_cols[1]:
        if st.button("🗑️ Eliminar", key=f"x7_delete_{trade_id}", use_container_width=True):
            if eliminar_trade_supabase(trade_id, user_id):
                st.success("Trade eliminado.")
                st.rerun()

    if st.session_state.editing_trade_id == trade_id:
        editar_trade_ui(row, user_id)


def render_track_record(df_trades, user_id):
    st.markdown(
        """
        <div class="x7-track-hero">
          <div class="x7-track-kicker">AXION PRIME · PERFORMANCE JOURNAL</div>
          <div class="x7-track-title">Track Record visual</div>
          <div class="x7-track-sub">Cada cuadro representa el resultado neto del día. Haz clic para abrir las operaciones, capturas, emociones y notas guardadas.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df_trades.empty:
        st.info(
            "Aún no aparecen operaciones. Registra un trade; si Supabase lo rechaza, "
            "la pantalla de guardado mostrará ahora el error exacto."
        )
        if st.button("➕ Registrar mi primera operación", key="x7_empty_register"):
            st.session_state.pagina_actual = "Registrar Trade"
            st.rerun()
        return

    df = df_trades.copy()
    df["fecha_dt"] = pd.to_datetime(df.get("fecha"), errors="coerce")
    df = df.dropna(subset=["fecha_dt"])
    df["beneficio_usd"] = pd.to_numeric(
        df.get("beneficio_usd", 0),
        errors="coerce",
    ).fillna(0.0)

    total_pnl = float(df["beneficio_usd"].sum())
    wins = int((df["beneficio_usd"] > 0).sum())
    losses = int((df["beneficio_usd"] < 0).sum())
    breakeven = int((df["beneficio_usd"] == 0).sum())
    total = len(df)
    win_rate = wins / total * 100 if total else 0

    summary_cols = st.columns(5)
    cards = [
        ("PNL TOTAL", f"${total_pnl:,.2f}", f"{total} operaciones", "x7-profit" if total_pnl >= 0 else "x7-loss"),
        ("WIN RATE", f"{win_rate:.1f}%", f"{wins} ganadas", ""),
        ("GANANCIAS", str(wins), "Días/trades positivos", "x7-profit"),
        ("PÉRDIDAS", str(losses), "Resultados negativos", "x7-loss"),
        ("BREAK EVEN", str(breakeven), "Sin ganancia ni pérdida", ""),
    ]
    for col, (label, value, meta, cls) in zip(summary_cols, cards):
        with col:
            st.markdown(
                f'<div class="x7-summary-card"><div class="x7-summary-label">{label}</div>'
                f'<div class="x7-summary-value {cls}">{value}</div>'
                f'<div class="x7-summary-meta">{meta}</div></div>',
                unsafe_allow_html=True,
            )

    months = sorted(
        df["fecha_dt"].dt.to_period("M").unique(),
        reverse=True,
    )
    month_labels = {
        str(period): period.to_timestamp().strftime("%B %Y").capitalize()
        for period in months
    }

    selected_month_str = st.selectbox(
        "Mes del calendario",
        [str(period) for period in months],
        format_func=lambda value: month_labels[value],
        key="x7_month_selector",
    )
    selected_period = pd.Period(selected_month_str, freq="M")

    month_df = df[df["fecha_dt"].dt.to_period("M") == selected_period].copy()
    grouped = (
        month_df.groupby(month_df["fecha_dt"].dt.date)
        .agg(
            pnl=("beneficio_usd", "sum"),
            count=("id", "count"),
        )
        .reset_index()
    )
    day_map = {
        row["fecha_dt"]: {
            "pnl": float(row["pnl"]),
            "count": int(row["count"]),
        }
        for _, row in grouped.iterrows()
    }

    import calendar as _calendar
    year = selected_period.year
    month = selected_period.month
    cal = _calendar.Calendar(firstweekday=0)
    weeks = cal.monthdatescalendar(year, month)

    st.markdown(
        f'<div class="x7-month-shell"><div class="x7-month-head">'
        f'<div class="x7-month-title">📅 {selected_period.to_timestamp().strftime("%B %Y").capitalize()}</div>'
        f'<div class="x7-month-legend">🟢 GANANCIA · 🔴 PÉRDIDA · ⚪ BREAK EVEN</div></div>',
        unsafe_allow_html=True,
    )

    weekday_cols = st.columns(7)
    for col, name in zip(weekday_cols, ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]):
        with col:
            st.markdown(f'<div class="x7-weekday">{name}</div>', unsafe_allow_html=True)

    for week_index, week in enumerate(weeks):
        cols = st.columns(7)
        for col_index, day in enumerate(week):
            with cols[col_index]:
                if day.month != month:
                    st.markdown('<div class="x7-empty-cell"></div>', unsafe_allow_html=True)
                    continue

                info = day_map.get(day)
                if info:
                    selected = st.session_state.selected_trade_day == day.isoformat()
                    if st.button(
                        _x7_trade_day_button(
                            day,
                            info["pnl"],
                            info["count"],
                            selected,
                        ),
                        key=f"x7_day_{day.isoformat()}_{week_index}_{col_index}",
                        use_container_width=True,
                        type="primary" if selected else "secondary",
                    ):
                        st.session_state.selected_trade_day = day.isoformat()
                        st.rerun()
                else:
                    st.markdown(
                        f'<div class="x7-empty-cell" style="padding:10px;color:#53617e;font-size:11px">{day.day:02d}</div>',
                        unsafe_allow_html=True,
                    )

    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state.selected_trade_day:
        if day_map:
            latest_day = max(day_map.keys())
            st.session_state.selected_trade_day = latest_day.isoformat()

    selected_day = st.session_state.selected_trade_day
    if selected_day:
        selected_date = pd.to_datetime(selected_day).date()
        selected_df = month_df[
            month_df["fecha_dt"].dt.date == selected_date
        ].sort_values("fecha_dt", ascending=False)

        if not selected_df.empty:
            day_pnl = float(selected_df["beneficio_usd"].sum())
            st.markdown(
                f'<div class="x7-day-detail"><div class="x7-month-head">'
                f'<div class="x7-month-title">Operaciones del {selected_date.strftime("%d/%m/%Y")}</div>'
                f'<div class="{"x7-profit" if day_pnl >= 0 else "x7-loss"}" style="font-size:20px;font-weight:950">'
                f'{"+" if day_pnl > 0 else ""}${day_pnl:,.2f}</div></div></div>',
                unsafe_allow_html=True,
            )

            for _, row in selected_df.iterrows():
                _x7_render_trade_detail(row, user_id)


# =========================================================
# 28. CHAT IA
# =========================================================

def render_chat_ia(
    df_trades
):

    st.markdown(
        "### 💬 Chat IA"
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

        with st.chat_message(
            "assistant"
        ):

            if df_trades.empty:

                answer = (
                    "Todavía no tienes suficientes "
                    "operaciones registradas."
                )

            else:

                total = len(
                    df_trades
                )

                pnl_total = float(
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

                answer = f"""
### 📊 Resumen de tu operativa

- **Trades:** {total}
- **Wins:** {wins}
- **Losses:** {losses}
- **Win Rate:** {win_rate:.1f}%
- **PnL acumulado:** ${pnl_total:,.2f}

La recomendación principal es revisar tus operaciones perdedoras y determinar si fueron consecuencia de una mala lectura técnica o de incumplimiento de disciplina.
"""

            st.markdown(
                answer
            )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )


# =========================================================
# 29. CALCULADORA LOTAJE
# =========================================================

def render_lotaje():

    st.markdown(
        "### 🧮 Calculadora de Tamaño de Posición"
    )

    c1, c2 = st.columns(2)

    with c1:

        balance = st.number_input(
            "Balance ($)",
            value=float(
                st.session_state.capital_actual
            ),
            step=100.0,
            key="lot_balance"
        )

        risk_percent = st.number_input(
            "Riesgo por operación (%)",
            value=1.0,
            step=0.25,
            min_value=0.01,
            key="lot_risk"
        )

        stop_distance = st.number_input(
            "Distancia SL",
            value=20.0,
            step=1.0,
            min_value=0.01,
            key="lot_stop"
        )

    with c2:

        risk_money = (
            balance
            * risk_percent
            / 100
        )

        lots = (
            risk_money
            / (
                stop_distance
                * 10
            )
        )

        st.metric(
            "Riesgo máximo",
            f"${risk_money:,.2f}"
        )

        st.metric(
            "Lotaje estimado",
            f"{lots:.2f}"
        )

        st.warning(
            "⚠️ El cálculo de lotaje depende "
            "del valor del punto/tick de cada activo. "
            "Verifica el contrato específico de tu broker."
        )


# =========================================================
# 30. ANÁLISIS IA
# =========================================================

def render_analisis_ia():

    st.markdown(
        "### 🤖 Auditoría Visual de Setup"
    )

    st.info(
        "Sube una captura para analizar visualmente "
        "el setup."
    )

    chart = st.file_uploader(
        "Subir gráfico",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="visual_audit"
    )

    if chart:

        st.image(
            chart,
            use_container_width=True
        )

        if st.button(
            "🔎 Analizar Setup",
            key="audit_setup"
        ):

            with st.spinner(
                "Analizando..."
            ):

                result = (
                    analizar_captura_tradingview(
                        chart.getvalue(),
                        chart.type
                    )
                )

            if result.get("error"):

                st.error(
                    result["error"]
                )

            else:

                st.success(
                    "Lectura completada."
                )

                st.json(
                    result
                )


# =========================================================
# 31. PROYECCIONES
# =========================================================

def render_proyecciones():

    st.markdown(
        "### 📈 Proyección de Capital"
    )

    c1, c2 = st.columns(2)

    with c1:

        capital = st.number_input(
            "Capital inicial",
            value=float(
                st.session_state.capital_actual
            ),
            step=100.0,
            key="projection_capital"
        )

        trades_month = st.slider(
            "Trades por mes",
            1,
            100,
            15,
            key="projection_trades"
        )

    with c2:

        win_rate = st.slider(
            "Win Rate estimado (%)",
            1,
            99,
            55,
            key="projection_wr"
        )

        rr = st.number_input(
            "R:R promedio",
            value=2.0,
            min_value=0.1,
            step=0.1,
            key="projection_rr"
        )

        risk = st.number_input(
            "Riesgo por trade (%)",
            value=1.0,
            min_value=0.1,
            step=0.1,
            key="projection_risk"
        )

    expectativa = (
        (
            win_rate / 100
        ) * rr
        -
        (
            1 - win_rate / 100
        )
    )

    expected_monthly = (
        trades_month
        * risk
        * expectativa
    )

    st.metric(
        "Expectativa matemática mensual aproximada",
        f"{expected_monthly:.2f}%"
    )

    st.caption(
        "Proyección matemática, no garantía de resultados."
    )


# =========================================================
# 32. PSICOTRADING
# =========================================================

def render_psicotrading():

    st.markdown(
        "### 📓 Diario & Psicotrading"
    )

    st.markdown(
        """
        El objetivo es detectar patrones:

        **Impulsividad → emoción → decisión → resultado**
        """
    )

    reflection = st.text_area(
        "Reflexión de hoy",
        height=200,
        key="daily_reflection"
    )

    if st.button(
        "💾 Guardar reflexión",
        key="save_reflection"
    ):

        st.success(
            "Reflexión guardada en esta sesión."
        )


# =========================================================
# 33. DASHBOARD
# =========================================================

def preparar_dashboard_df(df_trades):

    if df_trades is None or df_trades.empty:
        return pd.DataFrame()

    df = df_trades.copy()
    df["beneficio_usd"] = pd.to_numeric(
        df.get("beneficio_usd", 0), errors="coerce"
    ).fillna(0.0)
    df["fecha_dt"] = pd.to_datetime(
        df.get("fecha"), errors="coerce"
    )
    return df.sort_values("fecha_dt")


def calcular_metricas_avanzadas(df_trades):

    df = preparar_dashboard_df(df_trades)

    if df.empty:
        return {
            "total": 0, "pnl": 0.0, "wins": 0, "losses": 0,
            "be": 0, "win_rate": 0.0, "profit_factor": 0.0,
            "avg_win": 0.0, "avg_loss": 0.0, "expectancy": 0.0,
            "max_drawdown": 0.0, "rr_avg": 0.0
        }

    pnl = df["beneficio_usd"]
    positives = pnl[pnl > 0]
    negatives = pnl[pnl < 0]
    total = len(df)
    wins = len(positives)
    losses = len(negatives)
    be = total - wins - losses
    gross_profit = float(positives.sum()) if wins else 0.0
    gross_loss = abs(float(negatives.sum())) if losses else 0.0
    profit_factor = gross_profit / gross_loss if gross_loss else (gross_profit if gross_profit else 0.0)
    avg_win = float(positives.mean()) if wins else 0.0
    avg_loss = float(negatives.mean()) if losses else 0.0
    expectancy = float(pnl.mean()) if total else 0.0

    equity = pnl.cumsum()
    peak = equity.cummax()
    drawdown = equity - peak
    max_drawdown = float(drawdown.min()) if not drawdown.empty else 0.0

    rr_avg = 0.0
    if "rr" in df.columns:
        rr_values = pd.to_numeric(df["rr"], errors="coerce").dropna()
        rr_avg = float(rr_values.mean()) if not rr_values.empty else 0.0

    return {
        "total": total,
        "pnl": float(pnl.sum()),
        "wins": wins,
        "losses": losses,
        "be": be,
        "win_rate": (wins / total * 100) if total else 0.0,
        "profit_factor": profit_factor,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "expectancy": expectancy,
        "max_drawdown": max_drawdown,
        "rr_avg": rr_avg
    }


def render_nx_metric(label, value, foot_left, foot_right="", tone="neutral"):

    cls = "nx-positive" if tone == "positive" else "nx-negative" if tone == "negative" else ""

    st.markdown(
        textwrap.dedent(
            f"""
            <div class="nx-card">
              <div class="nx-metric-label">{label}</div>
              <div class="nx-metric-value {cls}">{value}</div>
              <div class="nx-metric-foot">
                <span>{foot_left}</span><span class="{cls}">{foot_right}</span>
              </div>
              <div class="nx-spark"></div>
            </div>
            """
        ),
        unsafe_allow_html=True
    )


def render_market_strip():

    cards = []
    for sesion in SESIONES:
        ahora = obtener_hora_zona(sesion["zona"])
        abierto = mercado_abierto(
            sesion["zona"], sesion["inicio"], sesion["fin"]
        )
        status_class = "nx-session-open" if abierto else "nx-session-closed"
        status = "● ABIERTO" if abierto else "● CERRADO"
        cards.append(
            f"""
            <div class="nx-session-item">
              <div class="nx-session-name">{sesion['nombre']}</div>
              <div class="nx-session-time">{ahora.strftime('%H:%M')}</div>
              <div class="{status_class}">{status}</div>
            </div>
            """
        )

    st.markdown(
        '<div class="nx-session-strip">' + "".join(cards) + '</div>',
        unsafe_allow_html=True
    )


def render_dashboard_stats(df_trades):

    df = preparar_dashboard_df(df_trades)
    metrics = calcular_metricas_avanzadas(df)

    if df.empty:
        st.markdown(
            """
            <div class="nx-empty">
              <div style="font-size:36px;margin-bottom:10px;">◈</div>
              <b>Tu inteligencia de trading comienza con el primer registro.</b><br>
              <span>Agrega una operación para desbloquear curvas, patrones y métricas.</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    chart_df = df.dropna(subset=["fecha_dt"]).copy()
    chart_df["equity"] = (
        float(st.session_state.capital_actual)
        + chart_df["beneficio_usd"].cumsum()
    )

    if not chart_df.empty:
        fig = px.area(
            chart_df,
            x="fecha_dt",
            y="equity",
            markers=True,
            labels={"fecha_dt": "Fecha", "equity": "Balance"}
        )
        fig.update_traces(
            line=dict(width=2.4),
            fill="tozeroy",
            hovertemplate="%{x|%d/%m/%Y}<br>Balance: $%{y:,.2f}<extra></extra>"
        )
        fig.update_layout(
            height=315,
            margin=dict(l=8, r=8, t=15, b=8),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#91a0b8"),
            xaxis=dict(showgrid=False, title=None),
            yaxis=dict(gridcolor="rgba(255,255,255,.05)", title=None),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def filtrar_dashboard_df(df, periodo, activo_filtro):
    """Filtra el dataframe del dashboard sin romper cuando está vacío."""
    if df is None or df.empty:
        return pd.DataFrame(columns=getattr(df, "columns", []))

    filtrado = df.copy()

    if "fecha" in filtrado.columns:
        filtrado["fecha_dt"] = pd.to_datetime(
            filtrado["fecha"],
            errors="coerce"
        )

        hoy = pd.Timestamp.now().normalize()

        if periodo == "7 días":
            filtrado = filtrado[filtrado["fecha_dt"] >= hoy - pd.Timedelta(days=6)]
        elif periodo == "30 días":
            filtrado = filtrado[filtrado["fecha_dt"] >= hoy - pd.Timedelta(days=29)]
        elif periodo == "90 días":
            filtrado = filtrado[filtrado["fecha_dt"] >= hoy - pd.Timedelta(days=89)]
        elif periodo == "Este año":
            filtrado = filtrado[filtrado["fecha_dt"].dt.year == hoy.year]

    if activo_filtro and activo_filtro != "Todos" and "par" in filtrado.columns:
        filtrado = filtrado[filtrado["par"] == activo_filtro]

    return filtrado.reset_index(drop=True)



def _x5_sparkline(color="#28e7ff", variant=0):
    paths = [
        "M0 26 L12 23 L22 25 L34 17 L48 20 L60 12 L73 15 L85 8 L100 13",
        "M0 23 L12 17 L24 22 L35 14 L48 18 L60 10 L72 16 L84 9 L100 5",
        "M0 17 L12 21 L25 14 L37 22 L49 11 L63 16 L75 8 L87 13 L100 7",
        "M0 24 L14 20 L26 22 L38 16 L50 19 L62 13 L76 15 L88 9 L100 11",
    ]
    p = paths[variant % len(paths)]
    return f'<div class="x5-spark"><svg viewBox="0 0 100 30" preserveAspectRatio="none"><path d="{p}" fill="none" stroke="{color}" stroke-width="2.2"/><path d="{p} L100 30 L0 30 Z" fill="{color}" opacity=".08"/></svg></div>'

def _x5_kpi(label, value, meta_left, meta_right, color="#28e7ff", variant=0):
    tone = "x5-pos" if color == "#24f0a4" else "x5-neg" if color == "#ff4d78" else ""
    return f'''
    <div class="x5-kpi">
      <div class="x5-kpi-label">{label}</div>
      <div class="x5-kpi-value {tone}">{value}</div>
      <div class="x5-kpi-meta"><span>{meta_left}</span><span>{meta_right}</span></div>
      {_x5_sparkline(color, variant)}
    </div>
    '''

def render_dashboard_v10(df_trades, estado_sub):
    df = preparar_dashboard_df(df_trades)
    m = calcular_metricas_avanzadas(df)
    user = st.session_state.user
    metadata = getattr(user, "user_metadata", {}) or {}
    nombre = metadata.get("username", st.session_state.nombre_trader)

    total = int(m.get("total", 0) or 0)
    pnl = float(m.get("pnl", 0) or 0)
    win_rate = float(m.get("win_rate", 0) or 0)
    profit_factor = float(m.get("profit_factor", 0) or 0)
    max_drawdown = float(m.get("max_drawdown", 0) or 0)
    rr_promedio = float(m.get("rr_promedio", 0) or 0)
    expectancy = float(m.get("expectancy", 0) or 0)
    wins = int(m.get("wins", 0) or 0)
    losses = int(m.get("losses", 0) or 0)
    balance = float(st.session_state.capital_actual) + pnl

    score = 50 if not total else round(min(
        99,
        max(
            20,
            34 + min(win_rate, 75) * .34
            + min(profit_factor, 3.2) * 8
            + min(rr_promedio, 3) * 5
            - min(abs(max_drawdown) / max(abs(balance), 1) * 100, 20) * .75
        )
    ))

    st.markdown(
        f'''
        <div class="x5-topbar">
          <div>
            <div class="x5-eyebrow">AXION PRIME · INSTITUTIONAL PROP INTELLIGENCE</div>
            <div class="x5-title">¡Buenos días, {nombre}! 👋</div>
            <div class="x5-sub">Disciplina hoy. Libertad mañana. Tu desempeño vive en los datos.</div>
          </div>
          <div class="x5-live"><i></i> MERCADOS Y SUPABASE ACTIVOS · {estado_sub}</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    filters = st.columns([1.05, 1.05, 1.05, 2.2])
    with filters[0]:
        periodo = st.selectbox("Período", ["Todo", "7 días", "30 días", "90 días", "Este año"], key="x5_periodo", label_visibility="collapsed")
    with filters[1]:
        options = ["Todos"]
        if not df.empty and "par" in df.columns:
            options += sorted(df["par"].dropna().astype(str).unique().tolist())
        activo_filtro = st.selectbox("Activo", options, key="x5_activo", label_visibility="collapsed")
    with filters[2]:
        st.selectbox("Vista", ["Performance Desk", "Prop Risk", "AI Review"], key="x5_vista", label_visibility="collapsed")
    with filters[3]:
        if st.button("＋ REGISTRAR NUEVA OPERACIÓN", key="x5_new_trade", use_container_width=True):
            st.session_state.pagina_actual = "Registrar Trade"
            st.rerun()

    df_f = filtrar_dashboard_df(df, periodo, activo_filtro)
    m = calcular_metricas_avanzadas(df_f)
    total = int(m.get("total", 0) or 0)
    pnl = float(m.get("pnl", 0) or 0)
    win_rate = float(m.get("win_rate", 0) or 0)
    profit_factor = float(m.get("profit_factor", 0) or 0)
    max_drawdown = float(m.get("max_drawdown", 0) or 0)
    rr_promedio = float(m.get("rr_promedio", 0) or 0)
    expectancy = float(m.get("expectancy", 0) or 0)
    wins = int(m.get("wins", 0) or 0)
    losses = int(m.get("losses", 0) or 0)
    balance = float(st.session_state.capital_actual) + pnl

    kpis = st.columns(6)
    kpi_html = [
        _x5_kpi("BALANCE ACTUAL", f"${balance:,.2f}", "Capital + PnL", f"{total} trades", "#28e7ff", 0),
        _x5_kpi("P&L TOTAL", f"${pnl:,.2f}", "Período activo", f"{pnl / max(abs(st.session_state.capital_actual),1) * 100:+.2f}%", "#24f0a4" if pnl >= 0 else "#ff4d78", 1),
        _x5_kpi("WIN RATE", f"{win_rate:.2f}%", f"{wins}W / {losses}L", "Aciertos", "#8d4dff", 2),
        _x5_kpi("PROFIT FACTOR", f"{profit_factor:.2f}", "Objetivo ≥ 1.50", "Sistema", "#28e7ff", 3),
        _x5_kpi("DRAWDOWN MÁX.", f"{abs(max_drawdown):.2f}", "Control de riesgo", "Límite 5%", "#ff4d78", 0),
        f'''<div class="x5-kpi"><div class="x5-kpi-label">PROP FIRM SCORE</div>
             <div style="display:flex;align-items:center;justify-content:space-between;margin-top:13px">
               <div><div class="x5-kpi-value">{score}</div><div style="font-size:10px;color:#7f8cac;margin-top:6px">de 100</div></div>
               <div style="width:72px;height:72px;border-radius:50%;background:conic-gradient(#28e7ff 0 {score/2}%,#8d4dff {score/2}% {score}%,rgba(255,255,255,.06) {score}%);display:grid;place-items:center"><div style="width:52px;height:52px;border-radius:50%;background:#080c1c;display:grid;place-items:center;color:#9b6dff;font-size:22px">?</div></div>
             </div></div>'''
    ]
    for c, h in zip(kpis, kpi_html):
        with c:
            st.markdown(h, unsafe_allow_html=True)

    st.markdown("")
    hero_l, hero_r = st.columns([1.72, 1])

    with hero_l:
        st.markdown('<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">📈 CURVA DE EQUITY</div><div class="x5-tag">TODOS LOS TIEMPOS</div></div>', unsafe_allow_html=True)
        if not df_f.empty:
            chart = df_f.copy()
            chart["fecha_dt"] = pd.to_datetime(chart["fecha"], errors="coerce")
            chart = chart.dropna(subset=["fecha_dt"]).sort_values("fecha_dt")
            chart["equity"] = float(st.session_state.capital_actual) + chart["beneficio_usd"].cumsum()
            fig = px.area(chart, x="fecha_dt", y="equity")
            fig.update_traces(line=dict(width=3, color="#9860ff"), fillcolor="rgba(129,75,255,.17)")
            fig.add_scatter(x=chart["fecha_dt"], y=chart["equity"], mode="lines", line=dict(width=2, color="#30cfff"), showlegend=False)
            fig.update_layout(height=330, margin=dict(l=8, r=8, t=8, b=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#8995b7"), xaxis=dict(showgrid=False, title=None), yaxis=dict(gridcolor="rgba(255,255,255,.055)", title=None), showlegend=False, hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown('<div style="height:330px;display:grid;place-items:center;text-align:center;color:#8492b5"><div><div style="font-size:45px;color:#35dfff">◇</div><b style="color:#eef2ff">Tu curva comienza con tu primer trade.</b><br><span style="font-size:12px">Registra una operación para activar rendimiento, consistencia y drawdown.</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with hero_r:
        st.markdown('<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">🖼️ CAPTURA DEL SETUP</div><div class="x5-tag">AI VISION READY</div></div>', unsafe_allow_html=True)
        last_trade = None
        if not df_f.empty:
            last_trade = df_f.sort_values("fecha", ascending=False).iloc[0]
        if last_trade is not None:
            asset = last_trade.get("par", "—")
            direction = last_trade.get("direccion", "—")
            img = convertir_imagen_display(last_trade.get("img_before", ""))
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:10px"><div class="x5-market"><small>ACTIVO</small><div style="font-weight:900;margin-top:7px">{asset}</div></div><div class="x5-market"><small>DIRECCIÓN</small><div style="font-weight:900;margin-top:7px">{direction}</div></div><div class="x5-market"><small>CONFIANZA IA</small><div class="x5-pos" style="font-weight:950;font-size:19px;margin-top:5px">90%</div></div></div>', unsafe_allow_html=True)
            if img:
                st.image(img, use_container_width=True)
            else:
                st.markdown('<div style="height:245px;border:1px dashed rgba(57,221,255,.32);border-radius:16px;display:grid;place-items:center;color:#8290b2;background:rgba(3,8,21,.55)">Sube una captura en Registrar Trade para verla aquí.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="height:310px;border:1px dashed rgba(57,221,255,.32);border-radius:16px;display:grid;place-items:center;text-align:center;color:#8290b2;background:rgba(3,8,21,.55)"><div><div style="font-size:42px">🧠</div><b style="color:#eef2ff">AXION Vision está listo.</b><br><span style="font-size:11px">Escanea tu primer setup para activar el análisis.</span></div></div>', unsafe_allow_html=True)
        if st.button("🧠 ESCANEAR CON IA", key="x5_scan_shortcut", use_container_width=True):
            st.session_state.pagina_actual = "Registrar Trade"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("")
    compact = st.columns(5)
    compact_data = [
        ("⚖️ RISK : REWARD", f"1 : {rr_promedio:.2f}", "Excelente" if rr_promedio >= 2 else "En desarrollo"),
        ("🎯 RATIO GANADOR", f"{win_rate:.0f}%", f"{wins}/{total or 0} trades"),
        ("🎯 TRADES HOY", "0", "0W / 0L"),
        ("🔥 RACHA ACTUAL", "0", "Sin racha"),
        ("🏆 MEJOR RACHA", "0", "Sin registro"),
    ]
    for col, (lab, val, sub) in zip(compact, compact_data):
        with col:
            st.markdown(f'<div class="x5-panel" style="padding:14px;text-align:left"><div class="x5-kpi-label">{lab}</div><div style="font-size:25px;font-weight:950;color:#fff;margin-top:10px">{val}</div><div style="font-size:10px;color:#7f8cac;margin-top:6px">{sub}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    row = st.columns([1.04, 1.12, 1.08, 1.05])

    with row[0]:
        markets = []
        for s in SESIONES:
            now = obtener_hora_zona(s["zona"])
            opened = mercado_abierto(s["zona"], s["inicio"], s["fin"])
            markets.append(f'<div class="x5-market"><strong>{s["nombre"]}</strong><div class="x5-market-time">{now.strftime("%H:%M")}</div><div class="{"x5-open" if opened else "x5-closed"}">● {"ABIERTO" if opened else "CERRADO"}</div></div>')
        st.markdown('<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">🌍 SESIONES DE MERCADO</div><div class="x5-tag">HORA LOCAL</div></div><div class="x5-market-grid" style="grid-template-columns:repeat(2,1fr)">' + "".join(markets) + '</div></div>', unsafe_allow_html=True)

    with row[1]:
        st.markdown('<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">🗓️ CALENDARIO ECONÓMICO</div><div class="x5-tag">RADAR</div></div><div class="x5-event"><b>🇺🇸 USD</b><div><b>NFP</b><br><small>Nómina no agrícola</small></div><span class="x5-impact-high">ALTA · 13:30</span></div><div class="x5-event"><b>🇪🇺 EUR</b><div><b>Tipos BCE</b><br><small>Decisión monetaria</small></div><span class="x5-impact-high">ALTA · 12:45</span></div><div class="x5-event"><b>🇬🇧 GBP</b><div><b>PIB q/q</b><br><small>Crecimiento</small></div><span class="x5-impact-med">MEDIA · 08:00</span></div></div>', unsafe_allow_html=True)

    with row[2]:
        best_asset = "Sin datos"
        if not df_f.empty and "par" in df_f.columns:
            grp = df_f.groupby("par")["beneficio_usd"].sum()
            if not grp.empty:
                best_asset = str(grp.idxmax())
        st.markdown(f'<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">🤖 AI INSIGHTS</div><div class="x5-tag">ÚLTIMO ANÁLISIS</div></div><div class="x5-insight">La expectativa del período es <b>${expectancy:,.2f}</b> por operación.</div><div class="x5-insight">Tu mejor activo actual es <b>{best_asset}</b>.</div><div class="x5-insight">R:R promedio observado: <b>{rr_promedio:.2f}</b>.</div><div class="x5-insight">Disciplina sugerida: registra emoción y contexto en cada trade.</div><div style="margin-top:12px;color:#8d9abc;font-size:10px">CONFIANZA IA: <b class="x5-pos">90%</b></div></div>', unsafe_allow_html=True)

    with row[3]:
        st.markdown(f'<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">🧠 PROP FIRM SCORE</div><div class="x5-tag">DETALLES</div></div><div class="x5-score"><div class="x5-score-num">{score}<small>DE 100</small></div></div><div class="x5-rule"><span>Disciplina</span><span>{min(99,max(40,round(win_rate*.65+35)))}/100</span></div><div class="x5-rule"><span>Riesgo</span><span>{max(20,95-round(abs(max_drawdown)/max(abs(balance),1)*700))}/100</span></div><div class="x5-rule"><span>Ejecución</span><span>{min(99,max(35,round(rr_promedio*18+35)))}/100</span></div><div class="x5-rule"><span>Consistencia</span><span>{min(99,max(30,round(win_rate*.75+20)))}/100</span></div></div>', unsafe_allow_html=True)

    st.markdown("")
    bottom_l, bottom_r = st.columns([1.65, 1])

    with bottom_l:
        st.markdown('<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">🧾 ÚLTIMAS OPERACIONES</div><div class="x5-tag">VER TODAS</div></div>', unsafe_allow_html=True)
        if df_f.empty:
            st.markdown('<div style="padding:28px;text-align:center;color:#8390b3">Aún no hay operaciones en el período seleccionado.</div>', unsafe_allow_html=True)
        else:
            for _, r in df_f.sort_values("fecha", ascending=False).head(5).iterrows():
                pv = float(r.get("beneficio_usd", 0) or 0)
                tone = "x5-pos" if pv > 0 else "x5-neg" if pv < 0 else ""
                st.markdown(f'<div class="x5-trade-row"><div><b>{r.get("par","—")}</b></div><div><span class="x5-chip">{r.get("direccion","—")}</span></div><div>{r.get("timeframe","—")}</div><div>{r.get("fecha","—")}</div><div class="{tone}" style="font-weight:950;text-align:right">${pv:,.2f}</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with bottom_r:
        monthly_pct = pnl / max(abs(st.session_state.capital_actual), 1) * 100
        st.markdown(f'<div class="x5-panel"><div class="x5-panel-head"><div class="x5-panel-title">📊 RENDIMIENTO MENSUAL</div><div class="x5-tag">{datetime.date.today().strftime("%B %Y").upper()}</div></div><div class="{"x5-pos" if monthly_pct >= 0 else "x5-neg"}" style="font-size:38px;font-weight:950;margin:20px 0 5px">{monthly_pct:+.2f}%</div><div style="color:#8b97b9;font-size:12px">${pnl:,.2f} netos</div>{_x5_sparkline("#24f0a4" if monthly_pct >= 0 else "#ff4d78", 1)}<div class="x5-rule"><span>Trades</span><span>{total}</span></div><div class="x5-rule"><span>Ganadas / Perdidas</span><span>{wins} / {losses}</span></div></div>', unsafe_allow_html=True)


EVENTOS_ECONOMICOS_EJEMPLO=[
 {"pais":"🇺🇸 USD","evento":"Nóminas no agrícolas (NFP)","fecha":"Próximo viernes","hora":"08:30 NY","impacto":"Alto"},
 {"pais":"🇺🇸 USD","evento":"Decisión de tipos de la Fed","fecha":"Próxima reunión","hora":"14:00 NY","impacto":"Alto"},
 {"pais":"🇪🇺 EUR","evento":"IPC zona euro","fecha":"Próxima publicación","hora":"11:00 CET","impacto":"Medio"},
 {"pais":"🇬🇧 GBP","evento":"PIB mensual Reino Unido","fecha":"Próxima publicación","hora":"07:00 UK","impacto":"Medio"}]

def render_calendario_economico():
    st.markdown("### 🗓️ Radar Macroeconómico")
    st.caption("Eventos demostrativos hasta conectar una API económica en tiempo real.")
    cols=st.columns(2)
    for i,ev in enumerate(EVENTOS_ECONOMICOS_EJEMPLO):
        color="#ff5c7c" if ev["impacto"]=="Alto" else "#ffd166"
        html=(f'<div style="background:linear-gradient(145deg,rgba(14,27,48,.94),rgba(14,12,32,.94));'
              f'border:1px solid rgba(90,150,220,.22);border-radius:18px;padding:18px;margin-bottom:14px">'
              f'<div style="display:flex;justify-content:space-between"><b>{ev["pais"]}</b>'
              f'<span style="color:{color};border:1px solid {color};border-radius:999px;padding:3px 10px">{ev["impacto"].upper()}</span></div>'
              f'<div style="font-size:20px;font-weight:900;margin:15px 0 8px">{ev["evento"]}</div>'
              f'<div style="color:#8fa6c4">📅 {ev["fecha"]} &nbsp; ⏱️ {ev["hora"]}</div></div>')
        with cols[i%2]: st.markdown(html,unsafe_allow_html=True)

def render_admin_panel():
    st.markdown("### 🛡️ Command Center — Administración")
    admin_client=get_supabase_admin_client()
    if admin_client is None:
        st.info("Para gestionar usuarios PRO agrega SUPABASE_SERVICE_KEY en Streamlit Secrets. No publiques esa clave.")
        c1,c2,c3=st.columns(3); c1.metric("Usuarios","—"); c2.metric("PRO activos","—"); c3.metric("Estado","Modo seguro")
        return
    try:
        r=admin_client.auth.admin.list_users()
        usuarios=r if isinstance(r,list) else getattr(r,"users",[])
    except Exception as e:
        st.error(f"❌ No se pudo cargar usuarios: {e}"); return
    vip=sum(bool((getattr(u,"user_metadata",{}) or {}).get("es_vip",False)) for u in usuarios)
    c1,c2,c3=st.columns(3); c1.metric("Usuarios",len(usuarios)); c2.metric("PRO",vip); c3.metric("Conversión",f"{(vip/len(usuarios)*100 if usuarios else 0):.1f}%")
    for u in usuarios:
        email=getattr(u,"email","") or ""
        if ADMIN_EMAIL and email.lower()==ADMIN_EMAIL.lower(): continue
        md=getattr(u,"user_metadata",{}) or {}; es_vip=bool(md.get("es_vip",False))
        with st.expander(f"{'💎' if es_vip else '👤'} {email}"):
            a,b=st.columns([2,1])
            with a:
                st.write(f"**ID:** {getattr(u,'id','')}"); st.write(f"**Plan:** {'PRO' if es_vip else 'FREE / TRIAL'}")
            with b:
                label=("🔻 Desactivar PRO" if es_vip else "✅ Activar PRO")
                if st.button(label,key=f"vip_{getattr(u,'id',email)}"):
                    try:
                        nuevo=dict(md); nuevo["es_vip"]=not es_vip
                        admin_client.auth.admin.update_user_by_id(getattr(u,"id",""),{"user_metadata":nuevo})
                        st.success("Usuario actualizado."); st.rerun()
                    except Exception as e: st.error(f"❌ Error: {e}")


def render_dashboard():

    tiene_acceso, estado_sub, _ = (
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

    trades_db = (
        cargar_trades_usuario(
            user_id
        )
    )

    df_trades = pd.DataFrame(
        trades_db
    )

    if not df_trades.empty:

        if (
            "beneficio_usd"
            not in df_trades.columns
        ):

            df_trades[
                "beneficio_usd"
            ] = 0.0

        if (
            "fecha"
            not in df_trades.columns
        ):

            df_trades[
                "fecha"
            ] = str(
                datetime.date.today()
            )

        df_trades[
            "beneficio_usd"
        ] = pd.to_numeric(
            df_trades[
                "beneficio_usd"
            ],
            errors="coerce"
        ).fillna(0)

    es_admin = "Admin" in estado_sub

    pagina = st.session_state.pagina_actual

    # Si por algún motivo quedó seleccionada una página que ya
    # no aplica (ej. Panel Admin y dejaste de ser admin), vuelve
    # al Dashboard en vez de romper.
    paginas_validas = [
        "Dashboard",
        "Registrar Trade",
        "Track Record",
        "Chat IA",
        "Psicotrading",
        "Análisis IA",
        "Proyecciones",
        "Lotaje",
        "Calendario Económico",
        "Perfil y Configuración",
        "Suscripción"
    ]

    if es_admin:

        paginas_validas.append(
            "Panel Admin"
        )

    if pagina not in paginas_validas:

        pagina = "Dashboard"

        st.session_state.pagina_actual = "Dashboard"

    if pagina != "Dashboard":
        st.markdown(
            f"## {pagina}"
        )

    if pagina == "Dashboard":

        render_dashboard_v10(
            df_trades,
            estado_sub
        )

    elif pagina == "Registrar Trade":

        render_nuevo_trade(
            user_id,
            df_trades
        )

    elif pagina == "Track Record":

        render_track_record(
            df_trades,
            user_id
        )

    elif pagina == "Chat IA":

        render_chat_ia(
            df_trades
        )

    elif pagina == "Psicotrading":

        render_psicotrading()

    elif pagina == "Análisis IA":

        render_analisis_ia()

    elif pagina == "Proyecciones":

        render_proyecciones()

    elif pagina == "Lotaje":

        render_lotaje()

    elif pagina == "Calendario Económico":

        render_calendario_economico()

    elif pagina == "Perfil y Configuración":

        render_perfil_configuracion()

    elif pagina == "Suscripción":

        render_suscripcion_page(
            estado_sub
        )

    elif pagina == "Panel Admin" and es_admin:

        render_admin_panel()


# =========================================================
# 35. ARRANQUE
# =========================================================

def main():

    if not st.session_state.authenticated:

        render_auth()

    else:

        render_dashboard()


if __name__ == "__main__":

    main()
