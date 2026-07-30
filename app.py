import streamlit as st
import datetime
import requests
import json
import base64
import pandas as pd
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
# =========================================================

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
# 5. ESTADO
# =========================================================

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


# =========================================================
# ESTADO DEL ESCÁNER IA
# =========================================================

if "auto_asset" not in st.session_state:
    st.session_state.auto_asset = "🥇 XAU/USD (Oro)"

if "auto_direction" not in st.session_state:
    st.session_state.auto_direction = "LONG 🟢"

if "auto_entry" not in st.session_state:
    st.session_state.auto_entry = 0.0

if "auto_sl" not in st.session_state:
    st.session_state.auto_sl = 0.0

if "auto_tp" not in st.session_state:
    st.session_state.auto_tp = 0.0

if "auto_timeframe" not in st.session_state:
    st.session_state.auto_timeframe = ""

if "scan_message" not in st.session_state:
    st.session_state.scan_message = ""


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


DIRECCIONES = [
    "LONG 🟢",
    "SHORT 🔴"
]


RESULTADOS = [
    "WIN 🟢",
    "LOSS 🔴",
    "BE ⚪"
]


EMOCIONES = [
    "Disciplinado / Neutro 🧘",
    "Ansioso ⚡",
    "FOMO / Miedo a perderse el movimiento 🚀",
    "Venganza / Frustrado 🛑",
    "Eufórico / Sobre-confiado 😎"
]


# =========================================================
# 7. MAPEO INTELIGENTE DE ACTIVOS
# =========================================================

ASSET_ALIASES = {

    "🥇 XAU/USD (Oro)": [
        "xauusd",
        "xau/usd",
        "xau-usd",
        "xau usd",
        "gold",
        "oro",
        "gold/usd",
        "goldusd"
    ],

    "🥈 XAG/USD (Plata)": [
        "xagusd",
        "xag/usd",
        "xag-usd",
        "silver",
        "plata"
    ],

    "🛢️ USOIL (Petróleo WTI)": [
        "usoil",
        "us oil",
        "wti",
        "crude oil",
        "oil",
        "petróleo wti",
        "petróleo"
    ],

    "🛢️ UKOIL (Petróleo Brent)": [
        "ukoil",
        "uk oil",
        "brent",
        "brent oil"
    ],

    "🌾 NGAS (Gas Natural)": [
        "ngas",
        "natural gas",
        "natgas",
        "gas natural"
    ],

    "🪙 BTC/USD (Bitcoin)": [
        "btcusd",
        "btc/usd",
        "btc-usd",
        "bitcoin",
        "btc"
    ],

    "🪙 ETH/USD (Ethereum)": [
        "ethusd",
        "eth/usd",
        "eth-usd",
        "ethereum",
        "eth"
    ],

    "🪙 SOL/USD (Solana)": [
        "solusd",
        "sol/usd",
        "sol-usd",
        "solana",
        "sol"
    ],

    "🪙 XRP/USD (Ripple)": [
        "xrpusd",
        "xrp/usd",
        "xrp-usd",
        "ripple",
        "xrp"
    ],

    "🪙 BNB/USD (Binance Coin)": [
        "bnbusd",
        "bnb/usd",
        "bnb-usd",
        "binance coin",
        "bnb"
    ],

    "🪙 ADA/USD (Cardano)": [
        "adausd",
        "ada/usd",
        "ada-usd",
        "cardano",
        "ada"
    ],

    "🪙 DOGE/USD (Dogecoin)": [
        "dogeusd",
        "doge/usd",
        "doge-usd",
        "dogecoin",
        "doge"
    ],

    "📊 US100 (Nasdaq 100)": [
        "us100",
        "nas100",
        "nasdaq",
        "nasdaq100",
        "nasdaq 100",
        "ndx"
    ],

    "📊 US30 (Dow Jones)": [
        "us30",
        "dj30",
        "dow",
        "dow jones",
        "dow30"
    ],

    "📊 US500 (S&P 500)": [
        "us500",
        "sp500",
        "s&p500",
        "s&p 500",
        "spx",
        "s and p 500"
    ],

    "📊 GER40 (Dax Alemán)": [
        "ger40",
        "dax",
        "dax40",
        "germany40"
    ],

    "📊 UK100 (FTSE 100)": [
        "uk100",
        "ftse",
        "ftse100"
    ],

    "📊 JP225 (Nikkei 225)": [
        "jp225",
        "nikkei",
        "nikkei225"
    ],

    "💱 EUR/USD": [
        "eurusd",
        "eur/usd",
        "eur-usd",
        "euro dollar"
    ],

    "💱 GBP/USD": [
        "gbpusd",
        "gbp/usd",
        "gbp-usd",
        "pound dollar"
    ],

    "💱 USD/JPY": [
        "usdjpy",
        "usd/jpy",
        "usd-jpy"
    ],

    "💱 AUD/USD": [
        "audusd",
        "aud/usd",
        "aud-usd"
    ],

    "💱 USD/CAD": [
        "usdcad",
        "usd/cad",
        "usd-cad"
    ],

    "💱 USD/CHF": [
        "usdchf",
        "usd/chf",
        "usd-chf"
    ],

    "💱 NZD/USD": [
        "nzdusd",
        "nzd/usd",
        "nzd-usd"
    ],

    "💱 EUR/GBP": [
        "eurgbp",
        "eur/gbp",
        "eur-gbp"
    ],

    "💱 EUR/JPY": [
        "eurjpy",
        "eur/jpy",
        "eur-jpy"
    ],

    "💱 GBP/JPY": [
        "gbpjpy",
        "gbp/jpy",
        "gbp-jpy"
    ],

    "💱 AUD/JPY": [
        "audjpy",
        "aud/jpy",
        "aud-jpy"
    ],

    "📈 NVDA (Nvidia)": [
        "nvda",
        "nvidia"
    ],

    "📈 TSLA (Tesla)": [
        "tsla",
        "tesla"
    ],

    "📈 AAPL (Apple)": [
        "aapl",
        "apple"
    ],

    "📈 AMZN (Amazon)": [
        "amzn",
        "amazon"
    ],

    "📈 MSFT (Microsoft)": [
        "msft",
        "microsoft"
    ],

    "📈 GOOGL (Google)": [
        "googl",
        "google",
        "alphabet"
    ],

    "📈 META (Meta / Facebook)": [
        "meta",
        "facebook"
    ],

    "📈 AMD (Advanced Micro Devices)": [
        "amd",
        "advanced micro devices"
    ],

    "📈 NFLX (Netflix)": [
        "nflx",
        "netflix"
    ],

    "📈 COIN (Coinbase)": [
        "coin",
        "coinbase"
    ]
}


def normalizar_texto(texto):
    if texto is None:
        return ""

    texto = str(texto).lower().strip()

    reemplazos = {
        "/": "",
        "-": "",
        "_": "",
        " ": "",
        ".": "",
        ",": ""
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    return texto


def detectar_activo_local(nombre_detectado):
    """
    Convierte lo que devuelva la IA a uno de los activos
    EXACTOS de LISTA_ACTIVOS.
    """

    if not nombre_detectado:
        return None

    original = str(nombre_detectado).lower().strip()

    normalizado = normalizar_texto(original)

    # 1. Coincidencia exacta por alias
    for activo, aliases in ASSET_ALIASES.items():

        for alias in aliases:

            alias_norm = normalizar_texto(alias)

            if normalizado == alias_norm:
                return activo

    # 2. Coincidencia contenida
    for activo, aliases in ASSET_ALIASES.items():

        for alias in aliases:

            alias_norm = normalizar_texto(alias)

            if len(alias_norm) >= 3 and alias_norm in normalizado:
                return activo

            if len(normalizado) >= 3 and normalizado in alias_norm:
                return activo

    # 3. Buscar ticker directamente en el texto
    for activo, aliases in ASSET_ALIASES.items():

        for alias in aliases:

            if alias.lower() in original:
                return activo

    return None


def normalizar_direccion(valor):

    if not valor:
        return None

    texto = str(valor).lower().strip()

    if any(
        palabra in texto
        for palabra in [
            "long",
            "buy",
            "compra",
            "alcista",
            "comprar"
        ]
    ):
        return "LONG 🟢"

    if any(
        palabra in texto
        for palabra in [
            "short",
            "sell",
            "venta",
            "bajista",
            "vender"
        ]
    ):
        return "SHORT 🔴"

    return None


def normalizar_timeframe(valor):

    if not valor:
        return ""

    texto = str(valor).upper().strip()

    equivalencias = {
        "1M": "M1",
        "5M": "M5",
        "15M": "M15",
        "30M": "M30",
        "1H": "H1",
        "4H": "H4",
        "1D": "D1",
        "1W": "W1",
        "WEEKLY": "W1",
        "DAILY": "D1",
        "4 HOURS": "H4",
        "1 HOUR": "H1"
    }

    if texto in equivalencias:
        return equivalencias[texto]

    if texto in TIMEFRAMES:
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

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

            if image.mode == "P":
                image = image.convert("RGBA")

            if image.mode in ("RGBA", "LA"):

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
            quality=78,
            optimize=True
        )

        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

        return (
            "data:image/jpeg;base64,"
            + encoded
        )

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
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:

        st.error(
            "❌ Error cargando operaciones:\n\n"
            f"{e}"
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
        ).insert(
            data
        ).execute()

        return True

    except Exception as e:

        st.error(
            f"❌ Error guardando operación: {e}"
        )

        return False


def actualizar_trade_supabase(
    trade_id,
    user_id,
    trade_data
):

    try:

        client = get_supabase_client()

        data = dict(trade_data)

        data.pop(
            "user_id",
            None
        )

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


# =========================================================
# 10. IA - ESCÁNER COMPLETO
# =========================================================

def analizar_captura_tradingview(
    image_bytes
):

    if not OPENROUTER_API_KEY:

        st.error(
            "OPENROUTER_API_KEY no está configurada."
        )

        return None

    try:

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
ERES UN SISTEMA DE EXTRACCIÓN DE DATOS DE TRADING.

Analiza cuidadosamente la captura de pantalla.

Tu trabajo NO es dar una recomendación.
Tu trabajo es IDENTIFICAR los datos que aparecen
VISUALMENTE en la captura.

DEBES buscar:

1. ACTIVO / SÍMBOLO
2. DIRECCIÓN: LONG o SHORT
3. PRECIO DE ENTRADA
4. STOP LOSS
5. TAKE PROFIT
6. TIMEFRAME

La captura puede ser de TradingView.

El activo puede aparecer como:

XAUUSD
XAU/USD
GOLD
Oro
BTCUSD
ETHUSD
EURUSD
GBPJPY
US100
NAS100
US30
US500
etc.

La dirección puede aparecer como:

LONG
SHORT
BUY
SELL
COMPRA
VENTA

MUY IMPORTANTE:

- NO asumas que el activo es XAU/USD.
- NO pongas XAU/USD por defecto.
- Si la captura muestra otro activo, debes devolver ese activo.
- Si no puedes identificar el activo, devuelve "".
- No inventes datos.
- Si un dato no aparece claramente, devuelve null.
- Si aparece un símbolo en la esquina superior izquierda de TradingView, úsalo.
- Si existe una herramienta Long Position / Short Position, úsala para determinar dirección.
- Si ves Entry, SL y TP en la herramienta, extrae esos precios.
- Analiza toda la imagen, incluyendo las esquinas y encabezados.

Devuelve ÚNICAMENTE un JSON válido.

Formato EXACTO:

{
    "asset": "",
    "direction": "",
    "entry": null,
    "sl": null,
    "tp": null,
    "timeframe": "",
    "confidence": 0
}

confidence debe ser un número entre 0 y 100.

No escribas explicaciones.
No uses Markdown.
No pongas ```json.
"""

        payload = {

            "model":
                "openai/gpt-4o-mini",

            "messages": [

                {
                    "role":
                        "user",

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
                                    "data:image/jpeg;base64,"
                                    + b64_img
                            }
                        }
                    ]
                }
            ],

            "temperature": 0,

            "max_tokens": 500
        }

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers=headers,

            json=payload,

            timeout=60
        )

        if response.status_code != 200:

            st.error(
                f"OpenRouter respondió "
                f"{response.status_code}: "
                f"{response.text[:500]}"
            )

            return None

        result = response.json()

        content = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        if isinstance(content, list):

            partes = []

            for item in content:

                if isinstance(item, dict):

                    if item.get("type") == "text":

                        partes.append(
                            item.get("text", "")
                        )

            content = "".join(partes)

        content = str(content).strip()

        # -----------------------------------------------
        # LIMPIAR MARKDOWN
        # -----------------------------------------------

        content = re.sub(
            r"```json",
            "",
            content,
            flags=re.IGNORECASE
        )

        content = content.replace(
            "```",
            ""
        ).strip()

        # -----------------------------------------------
        # EXTRAER JSON SI EL MODELO AGREGÓ TEXTO
        # -----------------------------------------------

        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL
        )

        if match:

            content = match.group(0)

        data = json.loads(content)

        return data

    except json.JSONDecodeError:

        st.error(
            "La IA respondió algo que no era JSON válido."
        )

        return None

    except requests.exceptions.Timeout:

        st.error(
            "La IA tardó demasiado en responder."
        )

        return None

    except Exception as e:

        st.error(
            f"Error leyendo captura con IA: {e}"
        )

        return None


# =========================================================
# 11. APLICAR RESULTADO DEL ESCÁNER
# =========================================================

def aplicar_resultado_scan(extracted):

    if not extracted:
        return False

    # -----------------------------------------------------
    # ACTIVO
    # -----------------------------------------------------

    activo_detectado = extracted.get(
        "asset",
        ""
    )

    activo_normalizado = detectar_activo_local(
        activo_detectado
    )

    if activo_normalizado:

        st.session_state.auto_asset = (
            activo_normalizado
        )

        st.session_state.new_trade_asset = (
            activo_normalizado
        )

    # -----------------------------------------------------
    # DIRECCIÓN
    # -----------------------------------------------------

    direccion_detectada = extracted.get(
        "direction",
        ""
    )

    direccion_normalizada = normalizar_direccion(
        direccion_detectada
    )

    if direccion_normalizada:

        st.session_state.auto_direction = (
            direccion_normalizada
        )

        st.session_state.new_trade_direction = (
            direccion_normalizada
        )

    # -----------------------------------------------------
    # ENTRY
    # -----------------------------------------------------

    entry = extracted.get(
        "entry"
    )

    if entry is not None:

        try:

            st.session_state.auto_entry = float(
                entry
            )

            st.session_state.new_trade_entry = float(
                entry
            )

        except Exception:
            pass

    # -----------------------------------------------------
    # SL
    # -----------------------------------------------------

    sl = extracted.get(
        "sl"
    )

    if sl is not None:

        try:

            st.session_state.auto_sl = float(
                sl
            )

            st.session_state.new_trade_sl = float(
                sl
            )

        except Exception:
            pass

    # -----------------------------------------------------
    # TP
    # -----------------------------------------------------

    tp = extracted.get(
        "tp"
    )

    if tp is not None:

        try:

            st.session_state.auto_tp = float(
                tp
            )

            st.session_state.new_trade_tp = float(
                tp
            )

        except Exception:
            pass

    # -----------------------------------------------------
    # TIMEFRAME
    # -----------------------------------------------------

    timeframe = normalizar_timeframe(
        extracted.get(
            "timeframe",
            ""
        )
    )

    if timeframe:

        st.session_state.auto_timeframe = (
            timeframe
        )

        st.session_state.new_trade_tf = (
            timeframe
        )

    return True


# =========================================================
# 12. SESIONES
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
            +
            ahora.minute / 60
        )

        return (
            inicio
            <=
            hora_decimal
            <
            fin
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
        else
        "CERRADO"
    )

    color = (
        "#34d399"
        if abierto
        else
        "#f87171"
    )

    st.markdown(
        f"""
        <div class="session-card">

            <div class="session-title">
                {nombre}
            </div>

            <div class="session-time">
                {ahora.strftime("%H:%M:%S")}
            </div>

            <div class="session-date">
                {ahora.strftime("%d/%m/%Y")}
            </div>

            <div class="session-status"
                 style="color:{color};
                        border-color:{color};">
                {estado}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# 13. SUSCRIPCIÓN
# =========================================================

def evaluar_suscripcion(user):

    if not user:

        return (
            False,
            "Sin sesión",
            0
        )

    user_email = (
        getattr(
            user,
            "email",
            ""
        )
        or
        ""
    )

    if user_email.lower() == (
        "jordandanielpenarrietasantilla@gmail.com"
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
        or
        {}
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
                    str(
                        created_at
                    ).replace(
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
        -
        fecha_registro
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


# =========================================================
# 14. CSS
# =========================================================

def aplicar_estilos():

    css = """

    <style>

    .stApp {

        background-color:
            #0b0e14 !important;

        color:
            #f0f3fa !important;

        font-family:
            'Segoe UI',
            Roboto,
            sans-serif !important;
    }

    p,
    label,
    h1,
    h2,
    h3,
    h4,
    span,
    div,
    .stMarkdown {

        color:
            #f0f3fa;
    }

    h1,
    h2 {

        background:
            linear-gradient(
                90deg,
                #00f2fe 0%,
                #4facfe 100%
            );

        -webkit-background-clip:
            text;

        -webkit-text-fill-color:
            transparent;

        font-weight:
            800 !important;
    }

    section[data-testid="stSidebar"] {

        background-color:
            #0f141e !important;

        border-right:
            1px solid
            rgba(0, 210, 255, 0.2)
            !important;
    }

    div[data-baseweb="select"] > div {

        background-color:
            #121721 !important;

        color:
            #00f2fe !important;

        border:
            1px solid
            rgba(0, 242, 254, 0.5)
            !important;

        border-radius:
            8px !important;
    }

    div[data-baseweb="select"] input {

        color:
            #00f2fe !important;

        -webkit-text-fill-color:
            #00f2fe !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {

        background-color:
            #121721 !important;

        border:
            1px solid
            #00f2fe !important;

        border-radius:
            8px !important;
    }

    div[role="option"],
    li[role="option"],
    li[data-baseweb="option"] {

        background-color:
            #121721 !important;

        color:
            #ffffff !important;

        padding:
            10px 14px !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"] {

        background-color:
            #00f2fe !important;

        color:
            #000000 !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {

        background-color:
            #161b22 !important;

        color:
            #00f2fe !important;

        border:
            1px solid
            rgba(0, 210, 255, 0.4)
            !important;

        border-radius:
            8px !important;
    }

    .stButton > button {

        background:
            linear-gradient(
                135deg,
                #00d2ff 0%,
                #2962ff 100%
            ) !important;

        color:
            #ffffff !important;

        border-radius:
            8px !important;

        border:
            none !important;

        font-weight:
            bold !important;

        width:
            100%;
    }

    .session-card {

        background:
            #161b22;

        border:
            1px solid
            rgba(0, 242, 254, 0.25);

        border-radius:
            10px;

        padding:
            10px;

        margin-bottom:
            10px;

        text-align:
            center;
    }

    .session-title {

        font-size:
            14px;

        font-weight:
            bold;
    }

    .session-time {

        color:
            #00f2fe !important;

        font-size:
            22px;

        font-weight:
            800;

        margin-top:
            3px;
    }

    .session-date {

        color:
            #8b98a8 !important;

        font-size:
            11px;
    }

    .session-status {

        display:
            inline-block;

        margin-top:
            6px;

        padding:
            2px 8px;

        border:
            1px solid;

        border-radius:
            20px;

        font-size:
            10px;

        font-weight:
            bold;
    }

    .paywall-card {

        background-color:
            #161b22;

        border:
            1px solid
            #f0b90b;

        border-radius:
            12px;

        padding:
            24px;

        text-align:
            center;
    }

    .scan-result {

        background:
            #121721;

        border:
            1px solid
            rgba(0,242,254,.35);

        border-radius:
            12px;

        padding:
            15px;

        margin:
            10px 0;
    }

    </style>

    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


# =========================================================
# 15. PAYWALL
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

            <a href="{LINK_BINANCE_INSCRIPCION}"
               target="_blank">

            <button style="
            background:#f0b90b;
            color:#000;
            border:none;
            padding:14px;
            border-radius:8px;
            font-weight:bold;
            width:100%;">
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

            <h2>$20.00 USD</h2>

            <p>Ahorra frente al plan mensual</p>

            <hr>

            <p>
            🌟 1 año completo<br>
            🔒 Pago único<br>
            🎁 Actualizaciones futuras<br>
            🧠 IA prioritaria
            </p>

            <a href="{LINK_BINANCE_ANUAL}"
               target="_blank">

            <button style="
            background:#00f2fe;
            color:#000;
            border:none;
            padding:14px;
            border-radius:8px;
            font-weight:bold;
            width:100%;">
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
            f"[Renovación mensual $2.50]"
            f"({LINK_BINANCE_RECURRENTE})"
        )

    with c2:

        st.markdown(
            "### 💬 Confirmar pago"
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
            width:100%;">
            💬 Enviar comprobante
            </button>

            </a>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 16. AUTENTICACIÓN
# =========================================================

def render_auth():

    left, right = st.columns(
        [1.3, 1]
    )

    with left:

        st.markdown(
            "# ⚡ AI Trading Journal & Auditor"
        )

        st.markdown(
            """
            ### Tu operativa. Tus datos. Tu disciplina.

            Registra tus operaciones, analiza tus emociones,
            controla tu Track Record y utiliza IA para auditar
            tu proceso de trading.
            """
        )

        st.markdown("---")

        st.markdown(
            """
            **Incluye:**

            🧠 Psicotrading  
            📊 Track Record  
            📅 Calendario PnL  
            🖼️ Antes / Después  
            🤖 Auditoría IA  
            🌎 Sesiones de mercado  
            🧮 Gestión de riesgo
            """
        )

    with right:

        tab_login, tab_register, tab_reset = st.tabs(
            [
                "🔑 Iniciar Sesión",
                "📝 Registrarse",
                "🔐 Recuperar"
            ]
        )

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
                        "Completa correo y contraseña."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        result = (
                            client
                            .auth
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

                        st.session_state.authenticated = (
                            True
                        )

                        st.success(
                            "Inicio de sesión correcto."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"❌ No se pudo iniciar sesión: {e}"
                        )

        with tab_register:

            st.markdown(
                "### Crear cuenta"
            )

            email = st.text_input(
                "Correo electrónico",
                key="register_email"
            )

            password = st.text_input(
                "Contraseña",
                type="password",
                key="register_password"
            )

            password2 = st.text_input(
                "Repetir contraseña",
                type="password",
                key="register_password_2"
            )

            if st.button(
                "Crear cuenta y probar",
                key="register_button"
            ):

                if not email or not password:

                    st.warning(
                        "Completa todos los campos."
                    )

                elif password != password2:

                    st.error(
                        "Las contraseñas no coinciden."
                    )

                elif len(password) < 6:

                    st.error(
                        "La contraseña debe tener al menos 6 caracteres."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        result = client.auth.sign_up(
                            {
                                "email": email,
                                "password": password
                            }
                        )

                        if result.user:

                            st.success(
                                "Cuenta creada. "
                                "Ahora puedes iniciar sesión."
                            )

                    except Exception as e:

                        st.error(
                            f"❌ Error registrando usuario: {e}"
                        )

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
                        "Introduce tu correo."
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
                            email,
                            {
                                "redirectTo": app_url
                            }
                        )

                        st.success(
                            "📩 Revisa tu correo y Spam."
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Error: {e}"
                        )


# =========================================================
# 17. SIDEBAR
# =========================================================

def render_sidebar(
    estado_sub
):

    with st.sidebar:

        user = st.session_state.user

        metadata = (
            getattr(
                user,
                "user_metadata",
                {}
            )
            or
            {}
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
            "### 👤 Perfil Trader"
        )

        c1, c2 = st.columns(
            [1, 2]
        )

        with c1:

            foto_display = (
                convertir_imagen_display(
                    foto_b64
                )
            )

            if foto_display:

                st.image(
                    foto_display,
                    width=65
                )

            else:

                st.markdown(
                    "<div style='font-size:45px;"
                    "text-align:center;'>👤</div>",
                    unsafe_allow_html=True
                )

        with c2:

            st.markdown(
                f"**{nombre_actual}**"
            )

            st.caption(
                getattr(
                    user,
                    "email",
                    ""
                )
            )

        if (
            "PRO" in estado_sub
            or "Admin" in estado_sub
        ):

            st.success(
                f"💎 {estado_sub}"
            )

        else:

            st.info(
                f"⏳ {estado_sub}"
            )

        with st.expander(
            "⚙️ Modificar Perfil"
        ):

            nuevo_nombre = st.text_input(
                "Nombre",
                value=nombre_actual,
                key="profile_name"
            )

            nueva_foto = st.file_uploader(
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
                "Guardar perfil",
                key="save_profile"
            ):

                try:

                    nueva_foto_b64 = foto_b64

                    if nueva_foto:

                        raw = nueva_foto.getvalue()

                        nueva_foto_b64 = (
                            base64.b64encode(
                                raw
                            ).decode("utf-8")
                        )

                    client = get_supabase_client()

                    result = client.auth.update_user(
                        {
                            "data": {
                                "username":
                                    nuevo_nombre,

                                "avatar_b64":
                                    nueva_foto_b64
                            }
                        }
                    )

                    st.session_state.user = (
                        result.user
                    )

                    st.session_state.nombre_trader = (
                        nuevo_nombre
                    )

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Error: {e}"
                    )

        st.markdown("---")

        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        cap_actual = (
            st.session_state.capital_actual
        )

        cap_meta = (
            st.session_state.capital_meta
        )

        progreso = (
            cap_actual / cap_meta
            if cap_meta > 0
            else 0
        )

        progreso = min(
            1,
            max(
                0,
                progreso
            )
        )

        st.markdown(
            f"**Capital:** "
            f"${cap_actual:,.2f} / "
            f"${cap_meta:,.2f}"
        )

        st.progress(
            progreso
        )

        with st.expander(
            "🔧 Configurar meta"
        ):

            st.session_state.capital_actual = (
                st.number_input(
                    "Capital actual ($)",
                    value=float(
                        cap_actual
                    ),
                    step=100.0,
                    key="sidebar_capital"
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta ($)",
                    value=float(
                        cap_meta
                    ),
                    step=500.0,
                    key="sidebar_meta"
                )
            )

        st.markdown("---")

        st.markdown(
            "### 🌎 Sesiones de Trading"
        )

        for sesion in SESIONES:

            render_sesion(
                sesion["nombre"],
                sesion["zona"],
                sesion["inicio"],
                sesion["fin"]
            )

        st.caption(
            "Hora local de cada mercado."
        )

        st.markdown("---")

        st.markdown(
            "### 🎯 Mis Reglas"
        )

        with st.expander(
            "✏️ Editar reglas"
        ):

            nuevas_reglas = st.text_area(
                "Reglas",
                value=(
                    st.session_state
                    .reglas_disciplina
                ),
                height=150,
                key="rules_editor"
            )

            if st.button(
                "Guardar reglas",
                key="save_rules"
            ):

                st.session_state.reglas_disciplina = (
                    nuevas_reglas
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

                get_supabase_client().auth.sign_out()

            except Exception:
                pass

            st.session_state.authenticated = (
                False
            )

            st.session_state.user = None

            st.session_state.chat_history = []

            st.rerun()


# =========================================================
# 18. EDITAR TRADE
# =========================================================

def editar_trade_ui(
    row,
    user_id
):

    trade_id = row.get(
        "id"
    )

    st.markdown(
        "### ✏️ Editar operación"
    )

    fecha_original = row.get(
        "fecha",
        str(
            datetime.date.today()
        )
    )

    try:

        fecha_default = (
            datetime.date
            .fromisoformat(
                str(
                    fecha_original
                )[:10]
            )
        )

    except Exception:

        fecha_default = (
            datetime.date.today()
        )

    par_actual = row.get(
        "par",
        LISTA_ACTIVOS[0]
    )

    if par_actual not in LISTA_ACTIVOS:

        detected = detectar_activo_local(
            par_actual
        )

        par_actual = (
            detected
            if detected
            else LISTA_ACTIVOS[0]
        )

    direccion_actual = row.get(
        "direccion",
        "LONG 🟢"
    )

    direccion_actual = (
        normalizar_direccion(
            direccion_actual
        )
        or
        "LONG 🟢"
    )

    resultado_actual = row.get(
        "resultado",
        "BE ⚪"
    )

    if resultado_actual not in RESULTADOS:

        resultado_actual = "BE ⚪"

    emocion_actual = row.get(
        "emocion",
        EMOCIONES[0]
    )

    if emocion_actual not in EMOCIONES:

        emocion_actual = EMOCIONES[0]

    c1, c2 = st.columns(2)

    with c1:

        fecha = st.date_input(
            "Fecha",
            value=fecha_default,
            key=f"edit_fecha_{trade_id}"
        )

        par = st.selectbox(
            "Activo",
            LISTA_ACTIVOS,
            index=LISTA_ACTIVOS.index(
                par_actual
            ),
            key=f"edit_par_{trade_id}"
        )

        direccion = st.radio(
            "Dirección",
            DIRECCIONES,
            index=(
                0
                if direccion_actual
                ==
                "LONG 🟢"
                else
                1
            ),
            horizontal=True,
            key=f"edit_dir_{trade_id}"
        )

        entrada = st.number_input(
            "Precio de entrada",
            value=float(
                row.get(
                    "precio_entrada",
                    0
                )
                or
                0
            ),
            format="%.5f",
            key=f"edit_entry_{trade_id}"
        )

        sl = st.number_input(
            "Stop Loss",
            value=float(
                row.get(
                    "stop_loss",
                    0
                )
                or
                0
            ),
            format="%.5f",
            key=f"edit_sl_{trade_id}"
        )

        tp = st.number_input(
            "Take Profit",
            value=float(
                row.get(
                    "take_profit",
                    0
                )
                or
                0
            ),
            format="%.5f",
            key=f"edit_tp_{trade_id}"
        )

        timeframe = st.selectbox(
            "Timeframe",
            TIMEFRAMES,
            index=(
                TIMEFRAMES.index(
                    row.get(
                        "timeframe",
                        ""
                    )
                )
                if row.get(
                    "timeframe",
                    ""
                )
                in TIMEFRAMES
                else
                0
            ),
            key=f"edit_tf_{trade_id}"
        )

    with c2:

        riesgo = abs(
            entrada - sl
        )

        beneficio = abs(
            tp - entrada
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
            RESULTADOS,
            index=RESULTADOS.index(
                resultado_actual
            ),
            key=f"edit_result_{trade_id}"
        )

        emocion = st.selectbox(
            "Estado emocional",
            EMOCIONES,
            index=EMOCIONES.index(
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
                or
                0
            ),
            step=10.0,
            key=f"edit_pnl_{trade_id}"
        )

        notas = st.text_area(
            "Notas emocionales",
            value=row.get(
                "notas_emocionales",
                ""
            )
            or
            "",
            height=130,
            key=f"edit_notes_{trade_id}"
        )

        st.markdown(
            "#### 🖼️ Capturas"
        )

        imagen_before = st.file_uploader(
            "Cambiar / agregar ANTES",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key=f"edit_before_{trade_id}"
        )

        imagen_after = st.file_uploader(
            "Cambiar / agregar DESPUÉS",
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
            "**Imagen ANTES actual**"
        )

        display_before = (
            convertir_imagen_display(
                old_before
            )
        )

        if display_before:

            st.image(
                display_before,
                use_container_width=True
            )

        else:

            st.caption(
                "No hay imagen."
            )

    with p2:

        st.markdown(
            "**Imagen DESPUÉS actual**"
        )

        display_after = (
            convertir_imagen_display(
                old_after
            )
        )

        if display_after:

            st.image(
                display_after,
                use_container_width=True
            )

        else:

            st.caption(
                "No hay imagen."
            )

    save_col, cancel_col = st.columns(2)

    with save_col:

        guardar = st.button(
            "💾 Guardar cambios",
            key=f"save_edit_{trade_id}"
        )

    with cancel_col:

        cancelar = st.button(
            "↩️ Cancelar",
            key=f"cancel_edit_{trade_id}"
        )

    if cancelar:

        st.rerun()

    if guardar:

        final_before = old_before

        final_after = old_after

        if imagen_before:

            final_before = (
                procesar_imagen_b64(
                    imagen_before
                )
            )

        if imagen_after:

            final_after = (
                procesar_imagen_b64(
                    imagen_after
                )
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

            st.rerun()


# =========================================================
# 19. DASHBOARD
# =========================================================

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

    if not df_trades.empty:

        if "beneficio_usd" not in df_trades.columns:

            df_trades[
                "beneficio_usd"
            ] = 0.0

        if "fecha" not in df_trades.columns:

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

    st.markdown(
        "## ⚡ Journaling & AI Trading Audit"
    )

    st.caption(
        f"Estado: **{estado_sub}**"
    )

    tabs = st.tabs(
        [
            "➕ Registrar Trade",
            "📅 Track Record PnL",
            "💬 Chat IA",
            "🧮 Lotaje",
            "🧠 Análisis IA",
            "📈 Proyecciones",
            "📓 Psicotrading",
            "📊 Dashboard"
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


    # =====================================================
    # TAB 1 - REGISTRAR TRADE
    # =====================================================

    with tab1:

        st.markdown(
            "### ➕ Registrar nueva operación"
        )

        st.info(
            "💡 Sube una captura de TradingView. "
            "La IA intentará identificar automáticamente "
            "activo, dirección, Entry, SL, TP y timeframe."
        )

        left, right = st.columns(
            [1.15, 1]
        )

        # -------------------------------------------------
        # CAPTURAS
        # -------------------------------------------------

        with right:

            st.markdown(
                "### 🖼️ Capturas"
            )

            upload_before = st.file_uploader(
                "1️⃣ ANTES de la operación",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                ],
                key="new_trade_before"
            )

            upload_after = st.file_uploader(
                "2️⃣ DESPUÉS de la operación",
                type=[
                    "png",
                    "jpg",
                    "jpeg",
                    "webp"
                ],
                key="new_trade_after"
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
                    caption="SETUP ANTES",
                    use_container_width=True
                )

                if st.button(
                    "🧠 ESCANEAR TRADE COMPLETO CON IA",
                    key="scan_new_trade"
                ):

                    with st.spinner(
                        "Analizando activo, dirección, Entry, SL, TP y timeframe..."
                    ):

                        extracted = (
                            analizar_captura_tradingview(
                                upload_before.getvalue()
                            )
                        )

                    if extracted:

                        aplicar_resultado_scan(
                            extracted
                        )

                        # ---------------------------------
                        # DATOS CRUDOS PARA DEBUG
                        # ---------------------------------

                        activo_raw = extracted.get(
                            "asset",
                            ""
                        )

                        direccion_raw = extracted.get(
                            "direction",
                            ""
                        )

                        activo_ok = detectar_activo_local(
                            activo_raw
                        )

                        direccion_ok = normalizar_direccion(
                            direccion_raw
                        )

                        confidence = extracted.get(
                            "confidence",
                            0
                        )

                        st.session_state.scan_message = (
                            f"IA detectó: "
                            f"{activo_raw or 'Activo no identificado'} "
                            f"| "
                            f"{direccion_raw or 'Dirección no identificada'} "
                            f"| "
                            f"Confianza: {confidence}%"
                        )

                        st.success(
                            st.session_state.scan_message
                        )

                        # Mostrar si algo no fue reconocido
                        if not activo_ok:

                            st.warning(
                                "⚠️ La IA no pudo identificar "
                                "el activo con suficiente certeza. "
                                "Puedes seleccionarlo manualmente."
                            )

                        if not direccion_ok:

                            st.warning(
                                "⚠️ La IA no pudo identificar "
                                "la dirección. "
                                "Puedes seleccionarla manualmente."
                            )

                        st.rerun()

                    else:

                        st.warning(
                            "No se pudieron detectar "
                            "los datos automáticamente."
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

            pnl = st.number_input(
                "Ganancia / Pérdida ($)",
                value=0.0,
                step=10.0,
                key="new_trade_pnl"
            )

        # -------------------------------------------------
        # DATOS
        # -------------------------------------------------

        with left:

            st.markdown(
                "### 📝 Datos de la operación"
            )

            # ---------------------------------------------
            # FECHA
            # ---------------------------------------------

            fecha = st.date_input(
                "Fecha",
                datetime.date.today(),
                key="new_trade_date"
            )

            c1, c2 = st.columns(2)

            with c1:

                # -----------------------------------------
                # ACTIVO
                # -----------------------------------------

                activo_default = (
                    st.session_state.auto_asset
                )

                if activo_default not in LISTA_ACTIVOS:

                    activo_default = (
                        LISTA_ACTIVOS[0]
                    )

                indice_activo = (
                    LISTA_ACTIVOS.index(
                        activo_default
                    )
                )

                par = st.selectbox(
                    "Activo / Par",
                    LISTA_ACTIVOS,
                    index=indice_activo,
                    key="new_trade_asset"
                )

                # -----------------------------------------
                # DIRECCIÓN
                # -----------------------------------------

                direccion_default = (
                    st.session_state.auto_direction
                )

                if direccion_default not in DIRECCIONES:

                    direccion_default = (
                        "LONG 🟢"
                    )

                indice_direccion = (
                    DIRECCIONES.index(
                        direccion_default
                    )
                )

                direccion = st.radio(
                    "Dirección",
                    DIRECCIONES,
                    index=indice_direccion,
                    horizontal=True,
                    key="new_trade_direction"
                )

                # -----------------------------------------
                # ENTRY
                # -----------------------------------------

                entrada = st.number_input(
                    "Precio Entrada",
                    value=float(
                        st.session_state.auto_entry
                    ),
                    format="%.5f",
                    key="new_trade_entry"
                )

                # -----------------------------------------
                # SL
                # -----------------------------------------

                sl = st.number_input(
                    "Stop Loss",
                    value=float(
                        st.session_state.auto_sl
                    ),
                    format="%.5f",
                    key="new_trade_sl"
                )

            with c2:

                # -----------------------------------------
                # TP
                # -----------------------------------------

                tp = st.number_input(
                    "Take Profit",
                    value=float(
                        st.session_state.auto_tp
                    ),
                    format="%.5f",
                    key="new_trade_tp"
                )

                # -----------------------------------------
                # TIMEFRAME
                # -----------------------------------------

                tf_default = (
                    st.session_state.auto_timeframe
                )

                if tf_default not in TIMEFRAMES:

                    tf_default = ""

                timeframe = st.selectbox(
                    "Timeframe",
                    TIMEFRAMES,
                    index=TIMEFRAMES.index(
                        tf_default
                    ),
                    key="new_trade_tf"
                )

                riesgo = abs(
                    entrada - sl
                )

                beneficio = abs(
                    tp - entrada
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
                    RESULTADOS,
                    key="new_trade_result"
                )

            st.markdown(
                "### 🧠 Psicotrading"
            )

            emocion = st.selectbox(
                "Estado emocional",
                EMOCIONES,
                key="new_trade_emotion"
            )

            notas = st.text_area(
                "Notas emocionales",
                placeholder=(
                    "¿Respetaste tu plan? "
                    "¿Qué sentías antes de entrar?"
                ),
                key="new_trade_notes"
            )

            # ---------------------------------------------
            # RESUMEN DEL ESCÁNER
            # ---------------------------------------------

            if st.session_state.scan_message:

                st.markdown(
                    "### 🤖 Resultado del escáner"
                )

                st.markdown(
                    f"""
                    <div class="scan-result">

                    <b>Activo:</b>
                    {par}<br>

                    <b>Dirección:</b>
                    {direccion}<br>

                    <b>Entry:</b>
                    {entrada}<br>

                    <b>Stop Loss:</b>
                    {sl}<br>

                    <b>Take Profit:</b>
                    {tp}<br>

                    <b>Timeframe:</b>
                    {timeframe or "No detectado"}<br>

                    <b>R:R:</b>
                    1 : {rr:.2f}

                    </div>
                    """,
                    unsafe_allow_html=True
                )

            # ---------------------------------------------
            # GUARDAR
            # ---------------------------------------------

            if st.button(
                "💾 GUARDAR TRADE",
                key="save_new_trade"
            ):

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
                        img_before_b64,

                    "img_after":
                        img_after_b64
                }

                if guardar_trade_supabase(
                    user_id,
                    data
                ):

                    # ---------------------------------
                    # LIMPIAR ESCÁNER
                    # ---------------------------------

                    st.session_state.auto_asset = (
                        LISTA_ACTIVOS[0]
                    )

                    st.session_state.auto_direction = (
                        "LONG 🟢"
                    )

                    st.session_state.auto_entry = 0.0

                    st.session_state.auto_sl = 0.0

                    st.session_state.auto_tp = 0.0

                    st.session_state.auto_timeframe = ""

                    st.session_state.scan_message = ""

                    # Limpiar widgets para próximo trade
                    for key in [
                        "new_trade_asset",
                        "new_trade_direction",
                        "new_trade_entry",
                        "new_trade_sl",
                        "new_trade_tp",
                        "new_trade_tf"
                    ]:

                        if key in st.session_state:

                            del st.session_state[key]

                    st.success(
                        "✅ Trade guardado correctamente."
                    )

                    st.rerun()


    # =====================================================
    # TAB 2 - TRACK RECORD
    # =====================================================

    with tab2:

        st.markdown(
            "### 📅 Track Record & Calendario PnL"
        )

        if df_trades.empty:

            st.info(
                "Aún no tienes operaciones."
            )

        else:

            total_pnl = float(
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

            total = len(
                df_trades
            )

            win_rate = (
                wins / total * 100
                if total
                else 0
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "PnL",
                f"${total_pnl:,.2f}"
            )

            c2.metric(
                "Win Rate",
                f"{win_rate:.1f}%"
            )

            c3.metric(
                "Trades",
                total
            )

            c4.metric(
                "Wins / Losses",
                f"{wins} / {losses}"
            )

            st.markdown("---")

            st.markdown(
                "### 🗓️ Calendario"
            )

            grouped = (
                df_trades
                .groupby("fecha")
                ["beneficio_usd"]
                .sum()
                .to_dict()
            )

            today = datetime.date.today()

            weeks = (
                calendar.Calendar(
                    firstweekday=6
                )
                .monthdayscalendar(
                    today.year,
                    today.month
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

            for i, header in enumerate(
                headers
            ):

                with cols[i]:

                    st.markdown(
                        f"<div style='text-align:center;"
                        f"font-weight:bold;'>"
                        f"{header}</div>",
                        unsafe_allow_html=True
                    )

            for week in weeks:

                cols = st.columns(7)

                for i, day in enumerate(
                    week
                ):

                    with cols[i]:

                        if day == 0:

                            st.markdown(
                                "<div style='height:85px;'>"
                                "</div>",
                                unsafe_allow_html=True
                            )

                            continue

                        date_value = (
                            datetime.date(
                                today.year,
                                today.month,
                                day
                            )
                        )

                        key = str(
                            date_value
                        )

                        pnl_day = grouped.get(
                            key,
                            None
                        )

                        if pnl_day is None:

                            bg = "#161b22"
                            color = "#ffffff"
                            content = ""

                        elif pnl_day > 0:

                            bg = "#34d399"
                            color = "#000000"

                            content = (
                                f"<b>+${pnl_day:,.0f}</b>"
                            )

                        else:

                            bg = "#f87171"
                            color = "#000000"

                            content = (
                                f"<b>-${abs(pnl_day):,.0f}</b>"
                            )

                        border = (
                            "2px solid #00f2fe"
                            if date_value == today
                            else
                            "1px solid #252b36"
                        )

                        st.markdown(
                            f"""
                            <div style="
                                background:{bg};
                                color:{color};
                                border:{border};
                                border-radius:8px;
                                height:85px;
                                padding:7px;
                                text-align:center;
                            ">

                            <div style="
                                text-align:left;
                                font-weight:bold;
                            ">
                            {day}
                            </div>

                            <div style="
                                margin-top:15px;
                                font-size:16px;
                            ">
                            {content}
                            </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

            st.markdown("---")

            st.markdown(
                "### 📋 Historial de operaciones"
            )

            for _, row in df_trades.iterrows():

                trade_id = row.get(
                    "id"
                )

                pnl_value = float(
                    row.get(
                        "beneficio_usd",
                        0
                    )
                    or
                    0
                )

                titulo = (
                    f"📅 {row.get('fecha', '')} | "
                    f"{row.get('par', '')} | "
                    f"{row.get('resultado', '')} | "
                    f"${pnl_value:,.2f}"
                )

                with st.expander(
                    titulo
                ):

                    editar_key = (
                        f"editing_{trade_id}"
                    )

                    if editar_key not in st.session_state:

                        st.session_state[
                            editar_key
                        ] = False

                    if not st.session_state[
                        editar_key
                    ]:

                        c1, c2, c3 = st.columns(
                            [1.2, 2, 2]
                        )

                        with c1:

                            st.markdown(
                                "#### ⚙️ Operación"
                            )

                            st.write(
                                f"**Dirección:** "
                                f"{row.get('direccion', '-')}"
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
                                f"1 : "
                                f"{float(row.get('rr', 0) or 0):.2f}"
                            )

                            st.write(
                                f"**Timeframe:** "
                                f"{row.get('timeframe', '-')}"
                            )

                            st.write(
                                f"**Emoción:** "
                                f"{row.get('emocion', '-')}"
                            )

                            st.write(
                                f"**PnL:** "
                                f"${pnl_value:,.2f}"
                            )

                            if row.get(
                                "notas_emocionales"
                            ):

                                st.markdown(
                                    "**Notas:**"
                                )

                                st.caption(
                                    row.get(
                                        "notas_emocionales"
                                    )
                                )

                            if st.button(
                                "✏️ Editar Trade",
                                key=f"edit_{trade_id}"
                            ):

                                st.session_state[
                                    editar_key
                                ] = True

                                st.rerun()

                            if st.button(
                                "🗑️ Eliminar",
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

                            img_before = (
                                convertir_imagen_display(
                                    row.get(
                                        "img_before"
                                    )
                                )
                            )

                            if img_before:

                                st.image(
                                    img_before,
                                    use_container_width=True
                                )

                            else:

                                st.info(
                                    "📷 Sin captura ANTES"
                                )

                        with c3:

                            st.markdown(
                                "**2️⃣ DESPUÉS**"
                            )

                            img_after = (
                                convertir_imagen_display(
                                    row.get(
                                        "img_after"
                                    )
                                )
                            )

                            if img_after:

                                st.image(
                                    img_after,
                                    use_container_width=True
                                )

                            else:

                                st.info(
                                    "📷 Sin captura DESPUÉS"
                                )

                    else:

                        editar_trade_ui(
                            row,
                            user_id
                        )

            st.markdown("---")

            df_chart = (
                df_trades
                .groupby("fecha")
                ["beneficio_usd"]
                .sum()
                .reset_index()
            )

            if not df_chart.empty:

                fig = px.bar(
                    df_chart,
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


    # =====================================================
    # TAB 3 - CHAT IA
    # =====================================================

    with tab3:

        st.markdown(
            "### 💬 Chat IA & Auditoría"
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

                    answer = (
                        "Todavía no tienes suficientes "
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

                    losses = len(
                        df_trades[
                            df_trades[
                                "beneficio_usd"
                            ] < 0
                        ]
                    )

                    wr = (
                        wins / total * 100
                    )

                    answer = f"""
### 🧠 Resumen de tu operativa

Has registrado **{total} trades**.

**PnL acumulado:** ${pnl:,.2f}

**Win Rate:** {wr:.1f}%

**Wins:** {wins}

**Losses:** {losses}

No evalúes únicamente el porcentaje de acierto. También analiza **R:R, drawdown, emoción y contexto de entrada**.
"""

                st.markdown(
                    answer
                )

                st.session_state.chat_history.append(
                    {
                        "role":
                            "assistant",

                        "content":
                            answer
                    }
                )


    # =====================================================
    # TAB 4 - LOTAJE
    # =====================================================

    with tab4:

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
                step=100.0
            )

            risk_percent = st.number_input(
                "Riesgo por operación (%)",
                value=1.0,
                step=0.25
            )

            stop_distance = st.number_input(
                "Distancia SL (pips/puntos)",
                value=20.0,
                step=1.0
            )

        with c2:

            risk_money = (
                balance
                *
                risk_percent
                /
                100
            )

            lots = (
                risk_money
                /
                (
                    stop_distance
                    *
                    10
                )
                if stop_distance > 0
                else
                0
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
                "⚠️ La equivalencia cambia según "
                "instrumento y broker."
            )


    # =====================================================
    # TAB 5 - AUDITORÍA VISUAL
    # =====================================================

    with tab5:

        st.markdown(
            "### 🤖 Auditoría Visual de Setup"
        )

        st.caption(
            "Segunda opinión educativa."
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
                "🔍 Analizar con IA",
                key="analyze_chart"
            ):

                if not OPENROUTER_API_KEY:

                    st.warning(
                        "OPENROUTER_API_KEY no configurada."
                    )

                else:

                    with st.spinner(
                        "Analizando gráfico..."
                    ):

                        try:

                            b64 = base64.b64encode(
                                chart.getvalue()
                            ).decode("utf-8")

                            headers = {
                                "Authorization":
                                    f"Bearer {OPENROUTER_API_KEY}",

                                "Content-Type":
                                    "application/json"
                            }

                            prompt = """
Analiza este gráfico como auditor de trading.

No des una señal automática.

Evalúa:

1. Estructura
2. Tendencia
3. Soportes/resistencias
4. Liquidez
5. Riesgo
6. R:R visible
7. Calidad del setup
8. Posibles errores de disciplina

Devuelve una evaluación clara y educativa.
"""

                            payload = {

                                "model":
                                    "openai/gpt-4o-mini",

                                "messages": [

                                    {
                                        "role":
                                            "user",

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
                                                        "data:image/jpeg;base64,"
                                                        + b64
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
                                timeout=60
                            )

                            if response.status_code == 200:

                                result = response.json()

                                answer = (
                                    result
                                    .get(
                                        "choices",
                                        [{}]
                                    )[0]
                                    .get(
                                        "message",
                                        {}
                                    )
                                    .get(
                                        "content",
                                        ""
                                    )
                                )

                                st.markdown(
                                    answer
                                )

                            else:

                                st.error(
                                    "La IA no respondió correctamente."
                                )

                        except Exception as e:

                            st.error(
                                f"Error de IA: {e}"
                            )


    # =====================================================
    # TAB 6 - PROYECCIONES
    # =====================================================

    with tab6:

        st.markdown(
            "### 📈 Proyección de Capital"
        )

        c1, c2 = st.columns(2)

        with c1:

            trades_month = st.slider(
                "Trades por mes",
                5,
                100,
                15
            )

            win_rate_est = st.slider(
                "Win Rate estimado (%)",
                1,
                99,
                55
            )

        with c2:

            avg_win = st.number_input(
                "Ganancia promedio por WIN ($)",
                value=200.0,
                step=25.0
            )

            avg_loss = st.number_input(
                "Pérdida promedio por LOSS ($)",
                value=100.0,
                step=25.0
            )

        capital = float(
            st.session_state.capital_actual
        )

        projection = []

        for month in range(
            1,
            13
        ):

            winners = (
                trades_month
                *
                win_rate_est
                /
                100
            )

            losers = (
                trades_month
                -
                winners
            )

            pnl_month = (
                winners
                *
                avg_win
                -
                losers
                *
                avg_loss
            )

            capital += pnl_month

            projection.append(
                {
                    "Mes":
                        f"Mes {month}",

                    "Capital":
                        capital
                }
            )

        df_projection = pd.DataFrame(
            projection
        )

        st.metric(
            "Capital proyectado a 12 meses",
            f"${capital:,.2f}"
        )

        fig = px.line(
            df_projection,
            x="Mes",
            y="Capital",
            markers=True,
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # =====================================================
    # TAB 7 - PSICOTRADING
    # =====================================================

    with tab7:

        st.markdown(
            "### 📓 Diario & Psicotrading"
        )

        if not df_trades.empty:

            st.markdown(
                "#### 🧠 Emociones registradas"
            )

            emotion_stats = (
                df_trades
                .groupby("emocion")
                ["beneficio_usd"]
                .agg(
                    [
                        "count",
                        "sum",
                        "mean"
                    ]
                )
                .reset_index()
            )

            emotion_stats.columns = [
                "Emoción",
                "Trades",
                "PnL",
                "Promedio"
            ]

            st.dataframe(
                emotion_stats,
                use_container_width=True,
                hide_index=True
            )

        st.markdown("---")

        reflection = st.text_area(
            "Reflexión de hoy",
            height=200,
            placeholder=(
                "¿Qué hiciste bien?\n"
                "¿Qué hiciste mal?\n"
                "¿Respetaste tus reglas?\n"
                "¿Hubo FOMO?\n"
                "¿Hubo revenge trading?"
            ),
            key="daily_reflection"
        )

        if st.button(
            "🧠 Guardar reflexión",
            key="save_reflection"
        ):

            st.success(
                "Reflexión guardada en esta sesión."
            )


    # =====================================================
    # TAB 8 - DASHBOARD
    # =====================================================

    with tab8:

        st.markdown(
            "### 📊 Dashboard Operativo"
        )

        if df_trades.empty:

            st.info(
                "Registra operaciones para desbloquear estadísticas."
            )

        else:

            total = len(
                df_trades
            )

            pnl = float(
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

            wr = (
                wins / total * 100
            )

            max_win = float(
                df_trades[
                    "beneficio_usd"
                ].max()
            )

            max_loss = float(
                df_trades[
                    "beneficio_usd"
                ].min()
            )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "PnL",
                f"${pnl:,.2f}"
            )

            c2.metric(
                "Win Rate",
                f"{wr:.1f}%"
            )

            c3.metric(
                "Trades",
                total
            )

            c4.metric(
                "Máx. Win / Loss",
                f"${max_win:,.0f} / "
                f"${max_loss:,.0f}"
            )

            st.markdown("---")

            pnl_series = (
                df_trades
                .sort_values("fecha")
                ["beneficio_usd"]
                .cumsum()
            )

            chart_df = pd.DataFrame(
                {
                    "Trade":
                        range(
                            1,
                            len(
                                pnl_series
                            ) + 1
                        ),

                    "PnL Acumulado":
                        pnl_series.values
                }
            )

            fig = px.line(
                chart_df,
                x="Trade",
                y="PnL Acumulado",
                markers=True,
                template="plotly_dark",
                title="Curva de PnL"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.markdown(
                "#### 📋 Operaciones"
            )

            display_columns = [
                "fecha",
                "par",
                "direccion",
                "timeframe",
                "resultado",
                "beneficio_usd",
                "emocion"
            ]

            existing_columns = [
                c
                for c
                in display_columns
                if c in df_trades.columns
            ]

            st.dataframe(
                df_trades[
                    existing_columns
                ],
                use_container_width=True,
                hide_index=True
            )


# =========================================================
# 20. FLUJO PRINCIPAL
# =========================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
````
