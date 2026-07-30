import streamlit as st
import datetime
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
    page_title="AI Trading Journal & Auditor V8",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# 2. CONFIGURACIÓN / SECRETOS
# =========================================================

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

OPENROUTER_MODEL = st.secrets.get(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash"
)

ADMIN_EMAIL = st.secrets.get(
    "ADMIN_EMAIL",
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

    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Faltan SUPABASE_URL y/o SUPABASE_KEY en Streamlit Secrets."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


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
    "editing_trade_id": None
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
            f"❌ Error cargando operaciones: {e}"
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
                "AI Trading Journal V8"
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

    if not resultado:
        return

    # IMPORTANTE:
    # Estos valores se escriben ANTES de construir
    # los widgets del formulario en el siguiente rerun.

    if resultado.get("asset"):

        st.session_state[
            "trade_asset"
        ] = resultado["asset"]

    if resultado.get("direction"):

        st.session_state[
            "trade_direction"
        ] = resultado["direction"]

    if resultado.get("entry") is not None:

        st.session_state[
            "trade_entry"
        ] = float(
            resultado["entry"]
        )

    if resultado.get("sl") is not None:

        st.session_state[
            "trade_sl"
        ] = float(
            resultado["sl"]
        )

    if resultado.get("tp") is not None:

        st.session_state[
            "trade_tp"
        ] = float(
            resultado["tp"]
        )

    if resultado.get("timeframe"):

        st.session_state[
            "trade_timeframe"
        ] = resultado["timeframe"]


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

    </style>

    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


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
            f"""
            <div class="paywall-card">

                <h3>🟡 Suscripción Mensual</h3>

                <h2>$5.00 USD</h2>

                <p>
                    Luego $2.50 USD / mes
                </p>

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
                        width:100%;
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

                <h2>$20.00 USD</h2>

                <p>
                    Ahorra frente al plan mensual
                </p>

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
            f"[Renovación mensual $2.50]({LINK_BINANCE_RECURRENTE})"
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
                    width:100%;
                ">

                    💬 Enviar comprobante

                </button>

            </a>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 23. AUTENTICACIÓN
# =========================================================

def render_auth():

    left, right = st.columns(
        [1.3, 1]
    )

    with left:

        st.markdown(
            "# ⚡ AI Trading Journal V8"
        )

        st.markdown(
            """
            ### Tu operativa. Tus datos. Tu disciplina.

            Registra tus operaciones, analiza tus emociones,
            controla tu Track Record y utiliza IA para auditar
            visualmente tus setups.

            ### 🧠 IA Visual V8

            La IA puede detectar:

            - Activo
            - LONG / SHORT
            - Entry
            - Stop Loss
            - Take Profit
            - Timeframe
            - Confianza de lectura
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

                        client = (
                            get_supabase_client()
                        )

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
                        "La contraseña debe tener "
                        "al menos 6 caracteres."
                    )

                else:

                    try:

                        client = (
                            get_supabase_client()
                        )

                        result = (
                            client
                            .auth
                            .sign_up(
                                {
                                    "email": email,
                                    "password": password
                                }
                            )
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
                            "📩 Revisa tu correo y Spam."
                        )

                    except Exception as e:

                        st.error(
                            f"❌ Error: {e}"
                        )


# =========================================================
# 24. SIDEBAR
# =========================================================

def render_sidebar(estado_sub):

    with st.sidebar:

        user = st.session_state.user

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
                    """
                    <div style="
                        font-size:45px;
                        text-align:center;
                    ">
                        👤
                    </div>
                    """,
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

                        nueva_foto_b64 = (
                            base64.b64encode(
                                nueva_foto.getvalue()
                            ).decode("utf-8")
                        )

                    client = (
                        get_supabase_client()
                    )

                    result = (
                        client
                        .auth
                        .update_user(
                            {
                                "data": {
                                    "username":
                                        nuevo_nombre,
                                    "avatar_b64":
                                        nueva_foto_b64
                                }
                            }
                        )
                    )

                    st.session_state.user = (
                        result.user
                    )

                    st.session_state.nombre_trader = (
                        nuevo_nombre
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"❌ Error actualizando perfil: {e}"
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

        st.markdown("---")

        st.markdown(
            "### 🎯 Mis Reglas"
        )

        with st.expander(
            "✏️ Editar reglas"
        ):

            nuevas_reglas = st.text_area(
                "Reglas",
                value=st.session_state.reglas_disciplina,
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

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []

            st.rerun()


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
        """
        <div class="ai-box">

        <h4>🧠 AI Vision V8</h4>

        Sube una captura de TradingView y la IA intentará
        leer directamente:

        <b>ACTIVO · DIRECCIÓN · ENTRY · SL · TP · TIMEFRAME</b>

        </div>
        """,
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

                    limpiar_formulario_trade()

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

def render_track_record(
    df_trades,
    user_id
):

    st.markdown(
        "### 📅 Track Record & Calendario PnL"
    )

    if df_trades.empty:

        st.info(
            "Aún no tienes operaciones registradas."
        )

        return

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
        "PnL Total",
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

    # -----------------------------------------------------
    # CURVA DE CAPITAL
    # -----------------------------------------------------

    chart_df = df_trades.copy()

    chart_df["fecha"] = pd.to_datetime(
        chart_df["fecha"],
        errors="coerce"
    )

    chart_df = chart_df.sort_values(
        "fecha"
    )

    chart_df["PnL acumulado"] = (
        chart_df[
            "beneficio_usd"
        ].cumsum()
    )

    if not chart_df.empty:

        fig = px.line(
            chart_df,
            x="fecha",
            y="PnL acumulado",
            markers=True,
            title="📈 Curva de PnL"
        )

        fig.update_layout(
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -----------------------------------------------------
    # HISTORIAL
    # -----------------------------------------------------

    st.markdown(
        "### 📋 Historial Detallado"
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
            or 0
        )

        titulo = (
            f"📅 {row.get('fecha', '')} | "
            f"{row.get('par', '')} | "
            f"{row.get('resultado', '')} | "
            f"PnL: ${pnl_value:,.2f}"
        )

        with st.expander(
            titulo
        ):

            if (
                st.session_state.editing_trade_id
                == trade_id
            ):

                editar_trade_ui(
                    row,
                    user_id
                )

                continue

            c1, c2, c3 = st.columns(
                [1.2, 2, 2]
            )

            with c1:

                st.markdown(
                    "#### ⚙️ Operación"
                )

                st.write(
                    f"**Activo:** "
                    f"{row.get('par', '-')}"
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

                if st.button(
                    "✏️ Editar",
                    key=f"edit_{trade_id}"
                ):

                    st.session_state.editing_trade_id = (
                        trade_id
                    )

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

                img = convertir_imagen_display(
                    row.get(
                        "img_before"
                    )
                )

                if img:

                    st.image(
                        img,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "📷 Sin captura"
                    )

            with c3:

                st.markdown(
                    "**2️⃣ DESPUÉS**"
                )

                img = convertir_imagen_display(
                    row.get(
                        "img_after"
                    )
                )

                if img:

                    st.image(
                        img,
                        use_container_width=True
                    )

                else:

                    st.info(
                        "📷 Sin captura"
                    )


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

def render_dashboard_stats(
    df_trades
):

    st.markdown(
        "### 📊 Dashboard Operativo"
    )

    if df_trades.empty:

        st.info(
            "Registra operaciones para comenzar "
            "a construir tu dashboard."
        )

        return

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

    total = len(
        df_trades
    )

    win_rate = (
        wins / total * 100
        if total
        else 0
    )

    avg_win = (
        df_trades[
            df_trades[
                "beneficio_usd"
            ] > 0
        ][
            "beneficio_usd"
        ].mean()
        if wins
        else 0
    )

    avg_loss = (
        df_trades[
            df_trades[
                "beneficio_usd"
            ] < 0
        ][
            "beneficio_usd"
        ].mean()
        if losses
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "PnL",
        f"${pnl:,.2f}"
    )

    c2.metric(
        "Win Rate",
        f"{win_rate:.1f}%"
    )

    c3.metric(
        "Ganancia promedio",
        f"${avg_win:,.2f}"
    )

    c4.metric(
        "Pérdida promedio",
        f"${avg_loss:,.2f}"
    )

    st.markdown("---")

    # PNL POR ACTIVO

    if "par" in df_trades.columns:

        asset_pnl = (
            df_trades
            .groupby("par")[
                "beneficio_usd"
            ]
            .sum()
            .reset_index()
        )

        if not asset_pnl.empty:

            fig = px.bar(
                asset_pnl,
                x="par",
                y="beneficio_usd",
                title="PnL por activo"
            )

            fig.update_layout(
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    st.dataframe(
        df_trades,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# 34. DASHBOARD PRINCIPAL
# =========================================================

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

    st.markdown(
        "## ⚡ AI Trading Journal & Auditor V8"
    )

    st.caption(
        "Sistema de journaling + IA visual + disciplina + Track Record"
    )

    tabs = st.tabs(
        [
            "➕ Registrar Trade",
            "📅 Track Record",
            "💬 Chat IA",
            "🧮 Lotaje",
            "🤖 Análisis IA",
            "📈 Proyecciones",
            "📓 Psicotrading",
            "📊 Dashboard"
        ]
    )

    # TAB 1

    with tabs[0]:

        render_nuevo_trade(
            user_id,
            df_trades
        )

    # TAB 2

    with tabs[1]:

        render_track_record(
            df_trades,
            user_id
        )

    # TAB 3

    with tabs[2]:

        render_chat_ia(
            df_trades
        )

    # TAB 4

    with tabs[3]:

        render_lotaje()

    # TAB 5

    with tabs[4]:

        render_analisis_ia()

    # TAB 6

    with tabs[5]:

        render_proyecciones()

    # TAB 7

    with tabs[6]:

        render_psicotrading()

    # TAB 8

    with tabs[7]:

        render_dashboard_stats(
            df_trades
        )


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
