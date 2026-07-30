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
    page_title="AI Trading Journal & Auditor V8",
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
    "📈 META (Meta / Facebook)",
    "📈 AMD (Advanced Micro Devices)",
    "📈 NFLX (Netflix)",
    "📈 COIN (Coinbase)"
]


# =========================================================
# 6. ALIASES DE ACTIVOS
# =========================================================

ASSET_ALIASES = {
    "XAUUSD": "🥇 XAU/USD (Oro)",
    "XAU/USD": "🥇 XAU/USD (Oro)",
    "XAU-USD": "🥇 XAU/USD (Oro)",
    "GOLD": "🥇 XAU/USD (Oro)",
    "ORO": "🥇 XAU/USD (Oro)",

    "XAGUSD": "🥈 XAG/USD (Plata)",
    "XAG/USD": "🥈 XAG/USD (Plata)",
    "XAG-USD": "🥈 XAG/USD (Plata)",
    "SILVER": "🥈 XAG/USD (Plata)",
    "PLATA": "🥈 XAG/USD (Plata)",

    "USOIL": "🛢️ USOIL (Petróleo WTI)",
    "USOILUSD": "🛢️ USOIL (Petróleo WTI)",
    "WTI": "🛢️ USOIL (Petróleo WTI)",
    "OIL": "🛢️ USOIL (Petróleo WTI)",

    "UKOIL": "🛢️ UKOIL (Petróleo Brent)",
    "BRENT": "🛢️ UKOIL (Petróleo Brent)",

    "NGAS": "🌾 NGAS (Gas Natural)",
    "NATGAS": "🌾 NGAS (Gas Natural)",

    "BTCUSD": "🪙 BTC/USD (Bitcoin)",
    "BTC/USD": "🪙 BTC/USD (Bitcoin)",
    "BTC-USD": "🪙 BTC/USD (Bitcoin)",
    "BITCOIN": "🪙 BTC/USD (Bitcoin)",

    "ETHUSD": "🪙 ETH/USD (Ethereum)",
    "ETH/USD": "🪙 ETH/USD (Ethereum)",
    "ETH-USD": "🪙 ETH/USD (Ethereum)",
    "ETHEREUM": "🪙 ETH/USD (Ethereum)",

    "SOLUSD": "🪙 SOL/USD (Solana)",
    "SOL/USD": "🪙 SOL/USD (Solana)",

    "XRPUSD": "🪙 XRP/USD (Ripple)",
    "XRP/USD": "🪙 XRP/USD (Ripple)",

    "BNBUSD": "🪙 BNB/USD (Binance Coin)",
    "BNB/USD": "🪙 BNB/USD (Binance Coin)",

    "ADAUSD": "🪙 ADA/USD (Cardano)",
    "ADA/USD": "🪙 ADA/USD (Cardano)",

    "DOGEUSD": "🪙 DOGE/USD (Dogecoin)",
    "DOGE/USD": "🪙 DOGE/USD (Dogecoin)",

    "US100": "📊 US100 (Nasdaq 100)",
    "NAS100": "📊 US100 (Nasdaq 100)",
    "NASDAQ": "📊 US100 (Nasdaq 100)",
    "NASDAQ100": "📊 US100 (Nasdaq 100)",

    "US30": "📊 US30 (Dow Jones)",
    "DJ30": "📊 US30 (Dow Jones)",
    "DOW": "📊 US30 (Dow Jones)",
    "DOWJONES": "📊 US30 (Dow Jones)",

    "US500": "📊 US500 (S&P 500)",
    "SP500": "📊 US500 (S&P 500)",
    "SPX": "📊 US500 (S&P 500)",

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

    "GBPUSD": "💱 GBP/USD",
    "GBP/USD": "💱 GBP/USD",
    "GBP-USD": "💱 GBP/USD",

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

    "META": "📈 META (Meta / Facebook)",
    "FACEBOOK": "📈 META (Meta / Facebook)",

    "AMD": "📈 AMD (Advanced Micro Devices)",
    "NFLX": "📈 NFLX (Netflix)",
    "NETFLIX": "📈 NFLX (Netflix)",

    "COIN": "📈 COIN (Coinbase)",
    "COINBASE": "📈 COIN (Coinbase)"
}


# =========================================================
# 7. NORMALIZADORES
# =========================================================

def limpiar_texto_activo(valor):
    if valor is None:
        return ""

    texto = str(valor).upper().strip()

    reemplazos = {
        " ": "",
        "_": "",
        "-": "",
        ":": "",
        "(": "",
        ")": "",
        ".": "",
        ",": ""
    }

    for viejo, nuevo in reemplazos.items():
        texto = texto.replace(viejo, nuevo)

    return texto


def normalizar_activo(activo):
    if not activo:
        return None

    original = str(activo).strip()
    limpio = limpiar_texto_activo(original)

    # 1. Coincidencia exacta
    for alias, nombre in ASSET_ALIASES.items():
        if limpiar_texto_activo(alias) == limpio:
            return nombre

    # 2. Buscar ticker dentro del texto
    for alias, nombre in ASSET_ALIASES.items():
        alias_limpio = limpiar_texto_activo(alias)

        if len(alias_limpio) >= 4 and alias_limpio in limpio:
            return nombre

    # 3. Buscar por nombre visible
    original_upper = original.upper()

    for nombre in LISTA_ACTIVOS:
        if nombre.upper() in original_upper:
            return nombre

    return None


def normalizar_direccion(valor):
    if not valor:
        return ""

    texto = str(valor).upper().strip()

    if any(x in texto for x in [
        "LONG",
        "BUY",
        "COMPRA",
        "LARGO",
        "CALL"
    ]):
        return "LONG 🟢"

    if any(x in texto for x in [
        "SHORT",
        "SELL",
        "VENTA",
        "CORTO",
        "PUT"
    ]):
        return "SHORT 🔴"

    return ""


def normalizar_timeframe(valor):
    if not valor:
        return ""

    texto = str(valor).upper().strip().replace(" ", "")

    equivalencias = {
        "1MIN": "M1",
        "1M": "M1",
        "M1": "M1",

        "5MIN": "M5",
        "5M": "M5",
        "M5": "M5",

        "15MIN": "M15",
        "15M": "M15",
        "M15": "M15",

        "30MIN": "M30",
        "30M": "M30",
        "M30": "M30",

        "1H": "H1",
        "1HR": "H1",
        "1HOUR": "H1",
        "60M": "H1",
        "H1": "H1",

        "4H": "H4",
        "4HR": "H4",
        "240M": "H4",
        "H4": "H4",

        "1D": "D1",
        "1DAY": "D1",
        "DAILY": "D1",
        "D1": "D1",

        "1W": "W1",
        "1WEEK": "W1",
        "WEEKLY": "W1",
        "W1": "W1"
    }

    return equivalencias.get(texto, "")


def limpiar_numero(valor):
    if valor is None:
        return None

    if isinstance(valor, bool):
        return None

    if isinstance(valor, (int, float, np.integer, np.floating)):
        if np.isnan(float(valor)):
            return None
        return float(valor)

    texto = str(valor).strip()

    if not texto:
        return None

    texto = texto.replace("$", "")
    texto = texto.replace("USD", "")
    texto = texto.replace("USDT", "")
    texto = texto.strip()

    # Soporte para números tipo 1,234.56
    if re.match(r"^-?\d{1,3}(,\d{3})+(\.\d+)?$", texto):
        texto = texto.replace(",", "")

    # Soporte para decimal con coma
    elif re.match(r"^-?\d+,\d+$", texto):
        texto = texto.replace(",", ".")

    match = re.search(
        r"-?\d+(?:\.\d+)?",
        texto
    )

    if not match:
        return None

    try:
        return float(match.group(0))
    except Exception:
        return None


# =========================================================
# 8. SESSION STATE
# =========================================================

DEFAULT_RULES = """• Acepta la pérdida antes de entrar.
• Corta pérdidas rápido.
• Deja correr los ganadores.
• Máximo 2 operaciones perdedoras por día.
• Stop Loss obligatorio.
• No operar por venganza.
• No operar fuera del plan."""

DEFAULTS = {
    "authenticated": False,
    "user": None,

    "chat_history": [],

    "nombre_trader": "Trader Pro",

    "capital_actual": 10000.0,
    "capital_meta": 15000.0,

    "reglas_disciplina": DEFAULT_RULES,

    # Escaneo
    "pending_scan": None,
    "last_scan": None,
    "scan_message": "",
    "scan_error": "",

    # Formulario
    "new_asset": "",
    "new_direction": "",
    "new_entry": 0.0,
    "new_sl": 0.0,
    "new_tp": 0.0,
    "new_timeframe": "",

    # Historial
    "trades_cache": [],
    "trades_loaded": False,
    "trades_error": ""
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# 9. APLICAR SCAN PENDIENTE
#
# IMPORTANTE:
# Esto ocurre ANTES de crear los widgets.
# Así evitamos el error:
# StreamlitAPIException: st.session_state[...] cannot be modified
# after widget instantiated.
# =========================================================

def aplicar_scan_pendiente():
    pending = st.session_state.get("pending_scan")

    if not pending:
        return

    asset = pending.get("asset")
    direction = pending.get("direction")
    entry = pending.get("entry")
    sl = pending.get("sl")
    tp = pending.get("tp")
    timeframe = pending.get("timeframe")

    if asset:
        st.session_state["new_asset"] = asset

    if direction:
        st.session_state["new_direction"] = direction

    if entry is not None and entry > 0:
        st.session_state["new_entry"] = float(entry)

    if sl is not None and sl > 0:
        st.session_state["new_sl"] = float(sl)

    if tp is not None and tp > 0:
        st.session_state["new_tp"] = float(tp)

    if timeframe:
        st.session_state["new_timeframe"] = timeframe

    st.session_state["last_scan"] = pending
    st.session_state["scan_message"] = "Datos de IA cargados en el formulario."
    st.session_state["pending_scan"] = None


aplicar_scan_pendiente()


# =========================================================
# 10. IMÁGENES
# =========================================================

def procesar_imagen_b64(uploaded_file, max_size=(1400, 1000)):
    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file)

        if image.mode in ("RGBA", "LA", "P"):
            if image.mode == "P":
                image = image.convert("RGBA")

            background = Image.new(
                "RGB",
                image.size,
                "white"
            )

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
            quality=82,
            optimize=True
        )

        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode("utf-8")

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
# 11. SUPABASE - TRADES
# =========================================================

def cargar_trades_usuario(user_id):
    """
    Carga exclusivamente los trades del usuario.
    Devuelve:
        lista de trades
        error
    """

    try:
        client = get_supabase_client()

        response = (
            client
            .table("trades")
            .select("*")
            .eq("user_id", str(user_id))
            .execute()
        )

        data = response.data or []

        # Orden local para no depender de que fecha exista
        if data:
            data = sorted(
                data,
                key=lambda x: str(x.get("fecha", "")),
                reverse=True
            )

        return data, None

    except Exception as e:
        return [], str(e)


def guardar_trade_supabase(user_id, trade_data):
    try:
        client = get_supabase_client()

        data = dict(trade_data)

        data["user_id"] = str(user_id)

        response = (
            client
            .table("trades")
            .insert(data)
            .execute()
        )

        return bool(response.data), None

    except Exception as e:
        return False, str(e)


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
            .eq("user_id", str(user_id))
            .execute()
        )

        return bool(response.data), None

    except Exception as e:
        return False, str(e)


def eliminar_trade_supabase(
    trade_id,
    user_id
):
    try:
        client = get_supabase_client()

        response = (
            client
            .table("trades")
            .delete()
            .eq("id", trade_id)
            .eq("user_id", str(user_id))
            .execute()
        )

        return True, None

    except Exception as e:
        return False, str(e)


# =========================================================
# 12. IA - JSON ROBUSTO
# =========================================================

def extraer_json_ia(content):
    if not content:
        return None

    texto = str(content).strip()

    texto = re.sub(
        r"```json",
        "",
        texto,
        flags=re.IGNORECASE
    )

    texto = texto.replace("```", "").strip()

    # Intento directo
    try:
        return json.loads(texto)
    except Exception:
        pass

    # Buscar primer objeto JSON
    inicio = texto.find("{")
    fin = texto.rfind("}")

    if inicio >= 0 and fin > inicio:
        candidato = texto[inicio:fin + 1]

        try:
            return json.loads(candidato)
        except Exception:
            pass

        try:
            candidato = candidato.replace("'", '"')
            return json.loads(candidato)
        except Exception:
            pass

    return None


def preparar_resultado_ia(data):
    if not isinstance(data, dict):
        return {
            "asset": None,
            "direction": None,
            "entry": None,
            "sl": None,
            "tp": None,
            "timeframe": None,
            "confidence": 0
        }

    asset_raw = (
        data.get("asset")
        or data.get("symbol")
        or data.get("ticker")
        or data.get("instrument")
    )

    direction_raw = (
        data.get("direction")
        or data.get("side")
        or data.get("bias")
    )

    entry_raw = (
        data.get("entry")
        or data.get("entry_price")
        or data.get("entryPrice")
    )

    sl_raw = (
        data.get("sl")
        or data.get("stop_loss")
        or data.get("stopLoss")
    )

    tp_raw = (
        data.get("tp")
        or data.get("take_profit")
        or data.get("takeProfit")
    )

    timeframe_raw = (
        data.get("timeframe")
        or data.get("time_frame")
        or data.get("tf")
    )

    confidence_raw = (
        data.get("confidence")
        or data.get("score")
        or 0
    )

    return {
        "asset": normalizar_activo(asset_raw),
        "asset_raw": str(asset_raw) if asset_raw else "",
        "direction": normalizar_direccion(direction_raw),
        "entry": limpiar_numero(entry_raw),
        "sl": limpiar_numero(sl_raw),
        "tp": limpiar_numero(tp_raw),
        "timeframe": normalizar_timeframe(timeframe_raw),
        "confidence": limpiar_numero(confidence_raw) or 0
    }


# =========================================================
# 13. ANALIZAR CAPTURA
# =========================================================

def analizar_captura_tradingview(image_bytes):
    if not OPENROUTER_API_KEY:
        return {
            "error": "OPENROUTER_API_KEY no configurada."
        }

    try:
        b64_img = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = """
Analiza cuidadosamente esta captura de TradingView.

OBJETIVO:
Extraer exactamente los parámetros de la operación que aparecen
en el gráfico o herramienta de posición.

IMPORTANTE:
NO asumas XAU/USD.
NO uses XAU/USD como valor predeterminado.
El activo debe salir VISUALMENTE del gráfico.

Busca especialmente:

1. Símbolo / activo visible en la parte superior del gráfico.
2. Dirección LONG o SHORT.
3. Entry / precio de entrada.
4. Stop Loss.
5. Take Profit.
6. Timeframe.

La herramienta puede mostrar números con muchos decimales.

Devuelve ÚNICAMENTE JSON válido.

Formato EXACTO:

{
  "asset": null,
  "direction": null,
  "entry": null,
  "sl": null,
  "tp": null,
  "timeframe": null,
  "confidence": 0
}

REGLAS:

- Si el activo visible es EURUSD devuelve "EUR/USD".
- Si es GBPJPY devuelve "GBP/JPY".
- Si es XAUUSD devuelve "XAU/USD".
- Si es US30 devuelve "US30".
- Si es NAS100 devuelve "US100".
- No inventes valores.
- Si Entry no se puede leer, devuelve null.
- Si SL no se puede leer, devuelve null.
- Si TP no se puede leer, devuelve null.
- Si dirección no se puede determinar, devuelve null.
- Si timeframe no se puede determinar, devuelve null.
- confidence debe ser de 0 a 100.

NO escribas explicaciones.
NO uses Markdown.
NO uses bloques de código.
"""

        payload = {
            "model": "openai/gpt-4o-mini",
            "temperature": 0,
            "max_tokens": 500,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un extractor visual de datos de trading. "
                        "Nunca inventes valores. "
                        "Nunca asumas XAU/USD."
                    )
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
                                "url": (
                                    "data:image/jpeg;base64,"
                                    + b64_img
                                )
                            }
                        }
                    ]
                }
            ]
        }

        # URL REAL.
        # NO poner Markdown aquí.
        url = "https://openrouter.ai/api/v1/chat/completions"

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=90
        )

        if response.status_code != 200:
            return {
                "error": (
                    f"OpenRouter HTTP "
                    f"{response.status_code}: "
                    f"{response.text[:1000]}"
                )
            }

        result = response.json()

        choices = result.get("choices", [])

        if not choices:
            return {
                "error": "OpenRouter no devolvió choices."
            }

        message = choices[0].get(
            "message",
            {}
        )

        content = message.get(
            "content",
            ""
        )

        data = extraer_json_ia(content)

        if not data:
            return {
                "error": (
                    "La IA respondió pero no "
                    "devolvió JSON válido."
                ),
                "raw": content
            }

        parsed = preparar_resultado_ia(data)

        # Información de diagnóstico
        parsed["raw_json"] = data

        return parsed

    except Exception as e:
        return {
            "error": f"Error analizando imagen: {e}"
        }


# =========================================================
# 14. VALIDACIÓN DEL RESULTADO
# =========================================================

def validar_resultado_scan(resultado):
    errores = []

    if not resultado:
        return ["No hubo resultado."]

    if not resultado.get("asset"):
        errores.append(
            "No pude identificar el activo visualmente."
        )

    if not resultado.get("direction"):
        errores.append(
            "No pude identificar LONG/SHORT."
        )

    if not resultado.get("entry"):
        errores.append(
            "No pude leer el precio de entrada."
        )

    if not resultado.get("sl"):
        errores.append(
            "No pude leer el Stop Loss."
        )

    if not resultado.get("tp"):
        errores.append(
            "No pude leer el Take Profit."
        )

    return errores


# =========================================================
# 15. SESIONES
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


def mercado_abierto(zona, inicio, fin):
    try:
        ahora = obtener_hora_zona(zona)

        if ahora.weekday() >= 5:
            return False

        hora_decimal = (
            ahora.hour
            + ahora.minute / 60
        )

        return inicio <= hora_decimal < fin

    except Exception:
        return False


def render_sesion(nombre, zona, inicio, fin):
    ahora = obtener_hora_zona(zona)
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
# 16. SUSCRIPCIÓN
# =========================================================

def evaluar_suscripcion(user):
    if not user:
        return False, "Sin sesión", 0

    user_email = (
        getattr(user, "email", "")
        or ""
    )

    if (
        user_email.lower()
        == "jordandanielpenarrietasantilla@gmail.com"
    ):
        return True, "Creador / Admin 👑", 99999

    metadata = (
        getattr(
            user,
            "user_metadata",
            {}
        )
        or {}
    )

    if metadata.get("es_vip", False):
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


# =========================================================
# 17. CSS
# =========================================================

def aplicar_estilos():
    st.markdown(
        """
        <style>

        .stApp {
            background-color:#0b0e14 !important;
            color:#f0f3fa !important;
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
        div {
            color:#f0f3fa;
        }

        section[data-testid="stSidebar"] {
            background-color:#0f141e !important;
            border-right:
                1px solid
                rgba(0,210,255,.2) !important;
        }

        h1,
        h2 {
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
                1px solid
                rgba(0,242,254,.5) !important;
            border-radius:8px !important;
        }

        div[data-baseweb="popover"],
        div[data-baseweb="menu"],
        div[role="listbox"] {
            background-color:#121721 !important;
            border:1px solid #00f2fe !important;
        }

        div[role="option"] {
            background-color:#121721 !important;
            color:#ffffff !important;
        }

        div[role="option"]:hover {
            background-color:#00f2fe !important;
            color:#000000 !important;
        }

        .stTextInput input,
        .stNumberInput input,
        .stTextArea textarea {
            background-color:#161b22 !important;
            color:#00f2fe !important;
            border:
                1px solid
                rgba(0,210,255,.4) !important;
            border-radius:8px !important;
        }

        .stButton > button {
            background:
                linear-gradient(
                    135deg,
                    #00d2ff 0%,
                    #2962ff 100%
                ) !important;

            color:#ffffff !important;
            border-radius:8px !important;
            border:none !important;
            font-weight:bold !important;
            width:100%;
        }

        .session-card {
            background:#161b22;
            border:
                1px solid
                rgba(0,242,254,.25);
            border-radius:10px;
            padding:10px;
            margin-bottom:10px;
            text-align:center;
        }

        .session-title {
            font-size:14px;
            font-weight:bold;
        }

        .session-time {
            color:#00f2fe !important;
            font-size:22px;
            font-weight:800;
        }

        .session-date {
            color:#8b98a8 !important;
            font-size:11px;
        }

        .session-status {
            display:inline-block;
            margin-top:6px;
            padding:2px 8px;
            border:1px solid;
            border-radius:20px;
            font-size:10px;
            font-weight:bold;
        }

        .scan-box {
            background:#111821;
            border:1px solid #00d2ff;
            border-radius:12px;
            padding:18px;
            margin:10px 0;
        }

        .detected-box {
            background:#101a18;
            border:1px solid #34d399;
            border-radius:12px;
            padding:15px;
        }

        .warning-box {
            background:#211a10;
            border:1px solid #f59e0b;
            border-radius:12px;
            padding:15px;
        }

        .paywall-card {
            background-color:#161b22;
            border:1px solid #f0b90b;
            border-radius:12px;
            padding:24px;
            text-align:center;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


aplicar_estilos()


# =========================================================
# 18. PAYWALL
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
        st.markdown("### 📲 Renovación")
        st.code(
            f"Binance Pay ID: {BINANCE_PAY_ID}"
        )

        st.markdown(
            f"[Renovación mensual $2.50]"
            f"({LINK_BINANCE_RECURRENTE})"
        )

    with c2:
        st.markdown("### 💬 Confirmar pago")

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
# 19. AUTENTICACIÓN
# =========================================================

def render_auth():
    left, right = st.columns(
        [1.3, 1]
    )

    with left:
        st.markdown(
            "# ⚡ AI Trading Journal & Auditor V8"
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

        # LOGIN
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

                        st.session_state.authenticated = True

                        st.success(
                            "Inicio de sesión correcto."
                        )

                        st.rerun()

                    except Exception as e:
                        st.error(
                            f"❌ No se pudo iniciar sesión: {e}"
                        )

        # REGISTER
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
                        client = get_supabase_client()

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

        # RESET
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
# 20. SIDEBAR
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
            foto_display = convertir_imagen_display(
                foto_b64
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
                    text-align:center;">
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

        # PERFIL
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
                            )
                            .decode("utf-8")
                        )

                    client = get_supabase_client()

                    result = (
                        client
                        .auth
                        .update_user(
                            {
                                "data": {
                                    "username": nuevo_nombre,
                                    "avatar_b64": nueva_foto_b64
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

        # META
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
            f"**Capital:** "
            f"${cap_actual:,.2f} / "
            f"${cap_meta:,.2f}"
        )

        st.progress(progreso)

        with st.expander(
            "🔧 Configurar meta"
        ):

            st.number_input(
                "Capital actual ($)",
                min_value=0.0,
                value=float(
                    st.session_state.capital_actual
                ),
                step=100.0,
                key="sidebar_capital"
            )

            st.number_input(
                "Meta ($)",
                min_value=0.0,
                value=float(
                    st.session_state.capital_meta
                ),
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

        # SESIONES
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

        # REGLAS
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
# 21. EDITAR TRADE
# =========================================================

def editar_trade_ui(
    row,
    user_id
):

    trade_id = row.get("id")

    try:
        fecha_default = (
            datetime.date
            .fromisoformat(
                str(
                    row.get(
                        "fecha",
                        datetime.date.today()
                    )
                )[:10]
            )
        )
    except Exception:
        fecha_default = datetime.date.today()

    par_actual = (
        normalizar_activo(
            row.get("par", "")
        )
        or LISTA_ACTIVOS[0]
    )

    direccion_actual = (
        normalizar_direccion(
            row.get("direccion", "")
        )
        or "LONG 🟢"
    )

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
            [
                "LONG 🟢",
                "SHORT 🔴"
            ],
            index=(
                0
                if direccion_actual == "LONG 🟢"
                else 1
            ),
            horizontal=True,
            key=f"edit_dir_{trade_id}"
        )

        entrada = st.number_input(
            "Precio de entrada",
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

        timeframes = [
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

        tf_actual = normalizar_timeframe(
            row.get(
                "timeframe",
                ""
            )
        )

        timeframe = st.selectbox(
            "Timeframe",
            timeframes,
            index=(
                timeframes.index(tf_actual)
                if tf_actual in timeframes
                else 0
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
            value=row.get(
                "notas_emocionales",
                ""
            )
            or "",
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
        st.rerun()

    if guardar:

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

        ok, error = actualizar_trade_supabase(
            trade_id,
            user_id,
            data
        )

        if ok:
            st.success(
                "✅ Trade actualizado."
            )
            st.rerun()

        else:
            st.error(
                f"❌ No se pudo actualizar: {error}"
            )


# =========================================================
# 22. CREAR DATAFRAME
# =========================================================

def construir_dataframe(trades):
    if not trades:
        return pd.DataFrame()

    df = pd.DataFrame(trades)

    if "beneficio_usd" not in df.columns:
        df["beneficio_usd"] = 0.0

    df["beneficio_usd"] = pd.to_numeric(
        df["beneficio_usd"],
        errors="coerce"
    ).fillna(0)

    if "fecha" not in df.columns:
        df["fecha"] = ""

    if "par" in df.columns:
        df["par"] = df["par"].apply(
            lambda x: normalizar_activo(x) or x
        )

    return df


# =========================================================
# 23. TAB REGISTRAR TRADE
# =========================================================

def render_registrar_trade(user_id):

    st.markdown(
        "### ➕ Registrar nueva operación"
    )

    st.info(
        "🧠 Sube una captura de TradingView. "
        "La IA intentará identificar ACTIVO, "
        "DIRECCIÓN, ENTRY, SL, TP y TIMEFRAME."
    )

    # -----------------------------------------------------
    # CAPTURA PARA ESCANEAR
    # -----------------------------------------------------

    st.markdown(
        "### 🧠 Escáner inteligente"
    )

    scan_image = st.file_uploader(
        "Sube la captura del setup",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="scan_image_v8"
    )

    if scan_image:

        st.image(
            scan_image,
            caption="Captura que analizará la IA",
            use_container_width=True
        )

        if st.button(
            "🧠 ESCANEAR OPERACIÓN CON IA",
            key="scan_trade_v8"
        ):

            with st.spinner(
                "Analizando activo, dirección, Entry, SL y TP..."
            ):

                resultado = analizar_captura_tradingview(
                    scan_image.getvalue()
                )

            if resultado.get("error"):

                st.session_state.scan_error = (
                    resultado["error"]
                )

                st.session_state.scan_message = ""

                st.error(
                    resultado["error"]
                )

                if resultado.get("raw"):
                    with st.expander(
                        "🔎 Ver respuesta IA"
                    ):
                        st.code(
                            str(
                                resultado["raw"]
                            )
                        )

            else:

                errores = validar_resultado_scan(
                    resultado
                )

                # Guardamos el resultado como PENDIENTE.
                # NO modificamos widgets todavía.
                st.session_state.pending_scan = (
                    resultado
                )

                st.session_state.scan_error = ""

                if errores:
                    st.session_state.scan_message = (
                        "Escaneo parcial."
                    )
                else:
                    st.session_state.scan_message = (
                        "Escaneo completo."
                    )

                st.rerun()

    # -----------------------------------------------------
    # RESULTADO DEL SCAN
    # -----------------------------------------------------

    last_scan = st.session_state.get(
        "last_scan"
    )

    if last_scan:

        st.markdown(
            """
            <div class="detected-box">
            <b>🤖 DATOS DETECTADOS POR IA</b>
            </div>
            """,
            unsafe_allow_html=True
        )

        sc1, sc2, sc3 = st.columns(3)

        with sc1:
            st.metric(
                "Activo",
                last_scan.get(
                    "asset"
                )
                or "No detectado"
            )

            st.metric(
                "Dirección",
                last_scan.get(
                    "direction"
                )
                or "No detectada"
            )

        with sc2:

            entry_show = last_scan.get(
                "entry"
            )

            sl_show = last_scan.get(
                "sl"
            )

            st.metric(
                "Entry",
                (
                    f"{entry_show:.5f}"
                    if entry_show
                    else "No detectado"
                )
            )

            st.metric(
                "SL",
                (
                    f"{sl_show:.5f}"
                    if sl_show
                    else "No detectado"
                )
            )

        with sc3:

            tp_show = last_scan.get(
                "tp"
            )

            st.metric(
                "TP",
                (
                    f"{tp_show:.5f}"
                    if tp_show
                    else "No detectado"
                )
            )

            st.metric(
                "Timeframe",
                last_scan.get(
                    "timeframe"
                )
                or "No detectado"
            )

        errores = validar_resultado_scan(
            last_scan
        )

        if errores:

            st.warning(
                "⚠️ La IA no pudo leer todo:"
            )

            for error in errores:
                st.write(
                    f"• {error}"
                )

            st.caption(
                "Los campos no detectados quedan "
                "disponibles para introducirlos manualmente."
            )

        else:

            st.success(
                "✅ Todos los parámetros principales fueron detectados."
            )

        if st.button(
            "🧹 Limpiar escaneo",
            key="clear_scan_v8"
        ):

            # Limpiar los valores ANTES de crear
            # nuevamente los widgets.
            st.session_state.new_asset = ""
            st.session_state.new_direction = ""
            st.session_state.new_entry = 0.0
            st.session_state.new_sl = 0.0
            st.session_state.new_tp = 0.0
            st.session_state.new_timeframe = ""

            st.session_state.last_scan = None
            st.session_state.scan_message = ""

            st.rerun()

    st.markdown("---")

    # -----------------------------------------------------
    # FORMULARIO
    # -----------------------------------------------------

    st.markdown(
        "### 📝 Datos de la operación"
    )

    fecha = st.date_input(
        "Fecha",
        datetime.date.today(),
        key="new_trade_date"
    )

    c1, c2 = st.columns(2)

    with c1:

        # IMPORTANTE:
        # Ya no usamos index=0 como fallback de XAU.
        # Si no hay activo, mostramos "Selecciona..."
        opciones_asset = [
            "— Selecciona activo —"
        ] + LISTA_ACTIVOS

        current_asset = (
            st.session_state.get(
                "new_asset",
                ""
            )
        )

        if current_asset in LISTA_ACTIVOS:
            asset_index = (
                opciones_asset.index(
                    current_asset
                )
            )
        else:
            asset_index = 0

        par = st.selectbox(
            "Activo / Par",
            opciones_asset,
            index=asset_index,
            key="new_asset"
        )

        if par == "— Selecciona activo —":
            par = ""

        direction_options = [
            "— Selecciona dirección —",
            "LONG 🟢",
            "SHORT 🔴"
        ]

        current_direction = (
            st.session_state.get(
                "new_direction",
                ""
            )
        )

        if current_direction in direction_options:
            direction_index = (
                direction_options.index(
                    current_direction
                )
            )
        else:
            direction_index = 0

        direccion = st.radio(
            "Dirección",
            direction_options,
            index=direction_index,
            horizontal=True,
            key="new_direction"
        )

        if direccion == "— Selecciona dirección —":
            direccion = ""

        entrada = st.number_input(
            "Precio Entrada",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    "new_entry",
                    0.0
                )
            ),
            format="%.5f",
            key="new_entry"
        )

        sl = st.number_input(
            "Stop Loss",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    "new_sl",
                    0.0
                )
            ),
            format="%.5f",
            key="new_sl"
        )

    with c2:

        tp = st.number_input(
            "Take Profit",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    "new_tp",
                    0.0
                )
            ),
            format="%.5f",
            key="new_tp"
        )

        timeframes = [
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

        current_tf = (
            st.session_state.get(
                "new_timeframe",
                ""
            )
        )

        tf_index = (
            timeframes.index(
                current_tf
            )
            if current_tf in timeframes
            else 0
        )

        timeframe = st.selectbox(
            "Timeframe",
            timeframes,
            index=tf_index,
            key="new_timeframe"
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
            [
                "WIN 🟢",
                "LOSS 🔴",
                "BE ⚪"
            ],
            key="new_trade_result"
        )

    # -----------------------------------------------------
    # PSICOTRADING
    # -----------------------------------------------------

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
        key="new_trade_emotion"
    )

    notas = st.text_area(
        "Notas emocionales",
        placeholder="¿Respetaste tu plan?",
        key="new_trade_notes"
    )

    pnl = st.number_input(
        "Ganancia / Pérdida ($)",
        value=0.0,
        step=10.0,
        key="new_trade_pnl"
    )

    upload_before = st.file_uploader(
        "📸 Captura ANTES",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="new_trade_before"
    )

    upload_after = st.file_uploader(
        "📸 Captura DESPUÉS",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp"
        ],
        key="new_trade_after"
    )

    if st.button(
        "💾 GUARDAR TRADE",
        key="save_new_trade_v8"
    ):

        errores_form = []

        if not par:
            errores_form.append(
                "Selecciona un activo."
            )

        if not direccion:
            errores_form.append(
                "Selecciona LONG o SHORT."
            )

        if entrada <= 0:
            errores_form.append(
                "La entrada debe ser mayor que 0."
            )

        if sl <= 0:
            errores_form.append(
                "El Stop Loss debe ser mayor que 0."
            )

        if tp <= 0:
            errores_form.append(
                "El Take Profit debe ser mayor que 0."
            )

        if errores_form:

            for error in errores_form:
                st.error(
                    f"❌ {error}"
                )

        else:

            data = {
                "fecha": str(fecha),
                "par": par,
                "direccion": direccion,
                "precio_entrada": float(entrada),
                "stop_loss": float(sl),
                "take_profit": float(tp),
                "rr": float(rr),
                "timeframe": timeframe,
                "resultado": resultado,
                "emocion": emocion,
                "notas_emocionales": notas,
                "beneficio_usd": float(pnl),
                "trades_cant": 1,
                "img_before": (
                    procesar_imagen_b64(
                        upload_before
                    )
                    if upload_before
                    else ""
                ),
                "img_after": (
                    procesar_imagen_b64(
                        upload_after
                    )
                    if upload_after
                    else ""
                )
            }

            ok, error = guardar_trade_supabase(
                user_id,
                data
            )

            if ok:

                st.success(
                    "✅ Trade guardado correctamente."
                )

                # Limpiar formulario
                st.session_state.new_asset = ""
                st.session_state.new_direction = ""
                st.session_state.new_entry = 0.0
                st.session_state.new_sl = 0.0
                st.session_state.new_tp = 0.0
                st.session_state.new_timeframe = ""

                st.session_state.last_scan = None
                st.session_state.scan_message = ""

                st.session_state.trades_loaded = False

                st.rerun()

            else:

                st.error(
                    f"❌ Error guardando trade: {error}"
                )


# =========================================================
# 24. TRACK RECORD
# =========================================================

def render_track_record(
    df_trades,
    user_id
):

    st.markdown(
        "### 📅 Track Record & Calendario PnL"
    )

    if df_trades.empty:

        st.warning(
            "⚠️ No hay trades cargados para este usuario."
        )

        st.info(
            "Esto puede significar que no existen "
            "registros en Supabase para este user_id "
            "o que las políticas RLS de la tabla "
            "`trades` están bloqueando la lectura."
        )

        st.code(
            f"user_id actual:\n{user_id}"
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

    total = len(df_trades)

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

    # Gráfico PnL acumulado
    chart_df = df_trades.copy()

    chart_df["beneficio_usd"] = pd.to_numeric(
        chart_df["beneficio_usd"],
        errors="coerce"
    ).fillna(0)

    chart_df = chart_df.iloc[::-1].copy()

    chart_df["PnL acumulado"] = (
        chart_df["beneficio_usd"]
        .cumsum()
    )

    if len(chart_df) > 0:

        fig = px.line(
            chart_df,
            y="PnL acumulado",
            markers=True,
            title="📈 Evolución del PnL"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#0b0e14",
            plot_bgcolor="#0b0e14"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.markdown("---")

    st.markdown(
        "### 📋 Historial Detallado"
    )

    for _, row in df_trades.iterrows():

        trade_id = row.get(
            "id",
            f"row_{_}"
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

        with st.expander(titulo):

            editing_key = (
                f"editing_{trade_id}"
            )

            if editing_key not in st.session_state:
                st.session_state[
                    editing_key
                ] = False

            if not st.session_state[
                editing_key
            ]:

                c1, c2, c3 = st.columns(
                    [1.2, 2, 2]
                )

                with c1:

                    st.markdown(
                        "#### ⚙️ Detalle"
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
                        "✏️ Editar Trade",
                        key=f"edit_{trade_id}"
                    ):

                        st.session_state[
                            editing_key
                        ] = True

                        st.rerun()

                    if st.button(
                        "🗑️ Eliminar Trade",
                        key=f"delete_{trade_id}"
                    ):

                        ok, error = (
                            eliminar_trade_supabase(
                                trade_id,
                                user_id
                            )
                        )

                        if ok:

                            st.success(
                                "Trade eliminado."
                            )

                            st.session_state[
                                "trades_loaded"
                            ] = False

                            st.rerun()

                        else:
                            st.error(
                                f"❌ {error}"
                            )

                with c2:

                    st.markdown(
                        "**1️⃣ ANTES**"
                    )

                    img = (
                        convertir_imagen_display(
                            row.get(
                                "img_before"
                            )
                        )
                    )

                    if img:
                        st.image(
                            img,
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

                    img = (
                        convertir_imagen_display(
                            row.get(
                                "img_after"
                            )
                        )
                    )

                    if img:
                        st.image(
                            img,
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


# =========================================================
# 25. CHAT IA
# =========================================================

def render_chat_ia(df_trades):

    st.markdown(
        "### 💬 Chat IA & Auditoría"
    )

    for message in st.session_state.chat_history:

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
                    "Todavía no tienes "
                    "operaciones registradas."
                )

            else:

                total = len(
                    df_trades
                )

                pnl_tot = float(
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

                wr = (
                    wins / total * 100
                )

                answer = (
                    f"Has registrado "
                    f"**{total} trades** con un "
                    f"PnL acumulado de "
                    f"**${pnl_tot:,.2f}** y un "
                    f"Win Rate de "
                    f"**{wr:.1f}%**."
                )

            st.markdown(answer)

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )


# =========================================================
# 26. CALCULADORA
# =========================================================

def render_calculadora():

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
            key="lot_risk"
        )

        stop_distance = st.number_input(
            "Distancia SL",
            value=20.0,
            step=1.0,
            min_value=0.0,
            key="lot_sl"
        )

    with c2:

        risk_money = (
            balance
            * risk_percent
            / 100
        )

        lots = (
            risk_money
            / (stop_distance * 10)
            if stop_distance > 0
            else 0
        )

        st.metric(
            "Riesgo máximo",
            f"${risk_money:,.2f}"
        )

        st.metric(
            "Lotaje estimado",
            f"{lots:.2f}"
        )


# =========================================================
# 27. PROYECCIONES
# =========================================================

def render_proyecciones():

    st.markdown(
        "### 📈 Proyección de Capital"
    )

    capital = st.number_input(
        "Capital inicial",
        value=float(
            st.session_state.capital_actual
        ),
        key="projection_capital"
    )

    trades_month = st.slider(
        "Trades por mes",
        5,
        100,
        15,
        key="projection_trades"
    )

    win_rate_est = st.slider(
        "Win Rate estimado (%)",
        1,
        99,
        55,
        key="projection_wr"
    )

    avg_win = st.number_input(
        "Ganancia media por WIN ($)",
        value=100.0,
        step=10.0,
        key="projection_win"
    )

    avg_loss = st.number_input(
        "Pérdida media por LOSS ($)",
        value=60.0,
        step=10.0,
        key="projection_loss"
    )

    win_decimal = (
        win_rate_est / 100
    )

    expected_trade = (
        win_decimal * avg_win
        - (1 - win_decimal) * avg_loss
    )

    expected_month = (
        expected_trade
        * trades_month
    )

    st.metric(
        "Valor esperado por trade",
        f"${expected_trade:,.2f}"
    )

    st.metric(
        "Proyección mensual",
        f"${expected_month:,.2f}"
    )

    months = list(
        range(0, 13)
    )

    capitals = [
        capital
        + expected_month * month
        for month in months
    ]

    projection_df = pd.DataFrame(
        {
            "Mes": months,
            "Capital proyectado": capitals
        }
    )

    fig = px.line(
        projection_df,
        x="Mes",
        y="Capital proyectado",
        markers=True,
        title="Proyección 12 meses"
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b0e14",
        plot_bgcolor="#0b0e14"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================================
# 28. DASHBOARD
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

    user_id = str(
        st.session_state.user.id
    )

    # =====================================================
    # CARGA DE TRADES
    # =====================================================

    if not st.session_state.trades_loaded:

        trades_db, trades_error = (
            cargar_trades_usuario(
                user_id
            )
        )

        st.session_state.trades_cache = (
            trades_db
        )

        st.session_state.trades_error = (
            trades_error or ""
        )

        st.session_state.trades_loaded = True

    else:

        trades_db = (
            st.session_state.trades_cache
        )

        trades_error = (
            st.session_state.trades_error
        )

    df_trades = construir_dataframe(
        trades_db
    )

    st.markdown(
        "## ⚡ AI Trading Journal & Auditor V8"
    )

    # Diagnóstico Supabase
    if trades_error:

        st.error(
            "❌ Supabase no pudo cargar "
            "tus operaciones."
        )

        with st.expander(
            "🔎 Ver diagnóstico técnico"
        ):

            st.code(
                trades_error
            )

            st.write(
                "**User ID actual:**"
            )

            st.code(
                user_id
            )

            st.info(
                "Si tienes trades antiguos y aquí "
                "aparece este error, probablemente "
                "hay que revisar RLS de la tabla "
                "`trades` en Supabase."
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
    # TAB 1
    # =====================================================

    with tab1:

        render_registrar_trade(
            user_id
        )

    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        render_track_record(
            df_trades,
            user_id
        )

    # =====================================================
    # TAB 3
    # =====================================================

    with tab3:

        render_chat_ia(
            df_trades
        )

    # =====================================================
    # TAB 4
    # =====================================================

    with tab4:

        render_calculadora()

    # =====================================================
    # TAB 5
    # =====================================================

    with tab5:

        st.markdown(
            "### 🤖 Auditoría Visual de Setup"
        )

        chart = st.file_uploader(
            "Subir gráfico",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp"
            ],
            key="visual_audit_v8"
        )

        if chart:

            st.image(
                chart,
                use_container_width=True
            )

            st.info(
                "Puedes utilizar el mismo escáner "
                "de la pestaña Registrar Trade para "
                "extraer Entry, SL, TP y activo."
            )

    # =====================================================
    # TAB 6
    # =====================================================

    with tab6:

        render_proyecciones()

    # =====================================================
    # TAB 7
    # =====================================================

    with tab7:

        st.markdown(
            "### 📓 Diario & Psicotrading"
        )

        st.text_area(
            "Reflexión de hoy",
            height=200,
            key="daily_reflection_v8"
        )

    # =====================================================
    # TAB 8
    # =====================================================

    with tab8:

        st.markdown(
            "### 📊 Dashboard Operativo"
        )

        if df_trades.empty:

            st.warning(
                "No hay operaciones disponibles."
            )

            if not trades_error:

                st.caption(
                    "La consulta a Supabase respondió "
                    "correctamente, pero no encontró "
                    "registros asociados a este usuario."
                )

        else:

            c1, c2, c3 = st.columns(3)

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

            total = len(
                df_trades
            )

            wr = (
                wins / total * 100
                if total
                else 0
            )

            c1.metric(
                "PnL",
                f"${total_pnl:,.2f}"
            )

            c2.metric(
                "Trades",
                total
            )

            c3.metric(
                "Win Rate",
                f"{wr:.1f}%"
            )

            st.markdown("---")

            st.dataframe(
                df_trades,
                use_container_width=True,
                hide_index=True
            )


# =========================================================
# 29. FLUJO PRINCIPAL
# =========================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
