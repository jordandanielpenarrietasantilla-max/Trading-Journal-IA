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
    
)

OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    
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
# 7. FUNCIONES DE IMAGEN
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
            quality=80,
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
            return (
                "data:image/jpeg;base64,"
                + valor
            )

    except Exception:
        pass

    return None


def obtener_mime(uploaded_file):
    if uploaded_file is None:
        return "image/jpeg"

    mime = getattr(
        uploaded_file,
        "type",
        None
    )

    if mime:
        return mime

    nombre = str(
        getattr(
            uploaded_file,
            "name",
            ""
        )
    ).lower()

    if nombre.endswith(".png"):
        return "image/png"

    if nombre.endswith(".webp"):
        return "image/webp"

    return "image/jpeg"


# =========================================================
# 8. BASE DE DATOS
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
            "❌ Error cargando operaciones.\n\n"
            f"{e}"
        )
        return []


def guardar_trade_supabase(user_id, trade_data):

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
# 9. NORMALIZACIÓN DE ACTIVO
# =========================================================

def normalizar_activo(valor):

    if not valor:
        return LISTA_ACTIVOS[0]

    texto = str(valor).upper().strip()

    mapa = {
        "XAUUSD": "🥇 XAU/USD (Oro)",
        "XAU/USD": "🥇 XAU/USD (Oro)",
        "GOLD": "🥇 XAU/USD (Oro)",
        "ORO": "🥇 XAU/USD (Oro)",

        "XAGUSD": "🥈 XAG/USD (Plata)",
        "XAG/USD": "🥈 XAG/USD (Plata)",
        "SILVER": "🥈 XAG/USD (Plata)",
        "PLATA": "🥈 XAG/USD (Plata)",

        "EURUSD": "💱 EUR/USD",
        "EUR/USD": "💱 EUR/USD",

        "GBPUSD": "💱 GBP/USD",
        "GBP/USD": "💱 GBP/USD",

        "USDJPY": "💱 USD/JPY",
        "USD/JPY": "💱 USD/JPY",

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

        "BTCUSD": "🪙 BTC/USD (Bitcoin)",
        "BTC/USD": "🪙 BTC/USD (Bitcoin)",
        "BITCOIN": "🪙 BTC/USD (Bitcoin)",

        "ETHUSD": "🪙 ETH/USD (Ethereum)",
        "ETH/USD": "🪙 ETH/USD (Ethereum)",

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
        "FTSE": "📊 UK100 (FTSE 100)",

        "JP225": "📊 JP225 (Nikkei 225)",
        "NIKKEI": "📊 JP225 (Nikkei 225)",

        "USOIL": "🛢️ USOIL (Petróleo WTI)",
        "WTI": "🛢️ USOIL (Petróleo WTI)",

        "UKOIL": "🛢️ UKOIL (Petróleo Brent)",
        "BRENT": "🛢️ UKOIL (Petróleo Brent)",

        "NGAS": "🌾 NGAS (Gas Natural)",

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

    if texto in mapa:
        return mapa[texto]

    texto_sin_emoji = re.sub(
        r"[^\w/.-]",
        "",
        texto
    )

    for activo in LISTA_ACTIVOS:

        limpio = re.sub(
            r"[^\w/.-]",
            "",
            activo.upper()
        )

        if (
            texto_sin_emoji == limpio
            or texto_sin_emoji in limpio
            or limpio in texto_sin_emoji
        ):
            return activo

    return LISTA_ACTIVOS[0]


# =========================================================
# 10. EXTRACCIÓN ROBUSTA DE JSON
# =========================================================

def limpiar_json_ia(content):

    if not content:
        return None

    texto = str(content).strip()

    texto = texto.replace(
        "```json",
        
    )

    texto = texto.replace(
        "```",
        
    )

    texto = texto.strip()

    inicio = texto.find("{")
    final = texto.rfind("}")

    if inicio == -1 or final == -1:
        return None

    texto_json = texto[
        inicio:final + 1
    ]

    try:
        return json.loads(texto_json)

    except Exception:
        return None


# =========================================================
# 11. IA - LECTURA DE TRADINGVIEW
# =========================================================

def analizar_captura_tradingview(
    image_bytes,
    mime_type="image/jpeg"
):

    if not OPENROUTER_API_KEY:
        return {
            "error":
                "OPENROUTER_API_KEY no configurada."
        }

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

        lista_texto = ", ".join(
            LISTA_ACTIVOS
        )

        prompt = f"""
ERES UN LECTOR DE CAPTURAS DE TRADINGVIEW.

Analiza cuidadosamente la imagen.

Tu trabajo NO es dar una señal.
Tu trabajo es EXTRAER los datos que ya aparecen
visualmente en la captura.

Debes intentar identificar:

1. ACTIVO
2. DIRECCIÓN: LONG o SHORT
3. PRECIO DE ENTRADA
4. STOP LOSS
5. TAKE PROFIT
6. TIMEFRAME

IMPORTANTE:

- Lee el símbolo del gráfico.
- Busca textos como EURUSD, EUR/USD,
  XAUUSD, GOLD, GBPJPY, US30, NASDAQ, etc.
- NO asumas que el activo es XAU/USD.
- Si aparece EUR/USD, devuelve EUR/USD.
- Si aparece GBP/JPY, devuelve GBP/JPY.
- Si aparece BTC/USD, devuelve BTC/USD.
- Si no puedes identificar el activo,
  devuelve "UNKNOWN".
- No inventes valores.

DIRECCIÓN:

Si el gráfico muestra una posición alcista,
BUY, LONG o herramienta de posición larga:
"LONG"

Si muestra una posición bajista,
SELL, SHORT o herramienta de posición corta:
"SHORT"

Si no puedes identificarla:
"UNKNOWN"

PRECIOS:

Busca específicamente:

- Entry
- Stop
- Stop Loss
- SL
- Target
- Take Profit
- TP

También analiza las etiquetas de la herramienta
Long Position / Short Position de TradingView.

IMPORTANTE CON LOS NÚMEROS:

Devuelve los precios EXACTAMENTE como números.
No agregues símbolos.
No agregues comas de miles.

Ejemplo:
"entry": 3345.72

Si no puedes identificar un número:
0.0

TIMEFRAME:

Busca si aparece:
M1, M5, M15, M30, H1, H4, D1 o W1.

ACTIVOS DISPONIBLES EN LA APLICACIÓN:

{lista_texto}

Devuelve ÚNICAMENTE este JSON:

{{
    "asset": "EUR/USD",
    "direction": "LONG",
    "entry": 0.0,
    "sl": 0.0,
    "tp": 0.0,
    "timeframe": "H1",
    "confidence": 0
}}

confidence debe ser un número entre 0 y 100.

NO escribas explicaciones.
NO uses Markdown.
NO pongas ```json.
SOLO JSON.
"""

        payload = {
            "model":
                "openai/gpt-4o-mini",

            "temperature":
                0,

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
                                    f"data:{mime_type};base64,{b64_img}"
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

        if response.status_code != 200:

            return {
                "error":
                    f"OpenRouter HTTP {response.status_code}: "
                    f"{response.text[:500]}"
            }

        result = response.json()

        content = (
            result
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )

        data = limpiar_json_ia(
            content
        )

        if not data:

            return {
                "error":
                    "La IA respondió algo que no "
                    "pude convertir en JSON."
            }

        return data

    except Exception as e:

        return {
            "error":
                f"Error leyendo captura: {e}"
        }


# =========================================================
# 12. APLICAR RESULTADO IA A STREAMLIT
# =========================================================

def aplicar_resultado_ia(resultado):

    if not resultado:
        return

    if resultado.get("error"):
        return

    # ---------------------------------------------
    # ACTIVO
    # ---------------------------------------------

    asset_raw = resultado.get(
        "asset",
        ""
    )

    asset = normalizar_activo(
        asset_raw
    )

    if (
        asset_raw
        and str(asset_raw).upper() != "UNKNOWN"
    ):

        st.session_state[
            "new_trade_asset"
        ] = asset

    # ---------------------------------------------
    # DIRECCIÓN
    # ---------------------------------------------

    direction_raw = str(
        resultado.get(
            "direction",
            ""
        )
    ).upper().strip()

    if direction_raw in [
        "LONG",
        "BUY",
        "LARGO"
    ]:

        st.session_state[
            "new_trade_direction"
        ] = "LONG 🟢"

    elif direction_raw in [
        "SHORT",
        "SELL",
        "CORTO"
    ]:

        st.session_state[
            "new_trade_direction"
        ] = "SHORT 🔴"

    # ---------------------------------------------
    # ENTRY
    # ---------------------------------------------

    try:

        entry = float(
            resultado.get(
                "entry",
                0
            ) or 0
        )

        if entry > 0:

            st.session_state[
                "new_trade_entry"
            ] = entry

    except Exception:
        pass

    # ---------------------------------------------
    # SL
    # ---------------------------------------------

    try:

        sl = float(
            resultado.get(
                "sl",
                0
            ) or 0
        )

        if sl > 0:

            st.session_state[
                "new_trade_sl"
            ] = sl

    except Exception:
        pass

    # ---------------------------------------------
    # TP
    # ---------------------------------------------

    try:

        tp = float(
            resultado.get(
                "tp",
                0
            ) or 0
        )

        if tp > 0:

            st.session_state[
                "new_trade_tp"
            ] = tp

    except Exception:
        pass

    # ---------------------------------------------
    # TIMEFRAME
    # ---------------------------------------------

    timeframe = str(
        resultado.get(
            "timeframe",
            
        )
    ).upper().strip()

    valid_tf = [
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

    if timeframe in valid_tf:

        st.session_state[
            "new_trade_tf"
        ] = timeframe


# =========================================================
# 13. SESIONES
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
# 14. SUSCRIPCIÓN
# =========================================================

def evaluar_suscripcion(user):

    if not user:
        return False, "Sin sesión", 0

    email = (
        getattr(
            user,
            "email",
            
        )
        or ""
    )

    if email.lower() == (
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
# 15. CSS
# =========================================================

def aplicar_estilos():

    css = """
    <style>

    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI',
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
        color: #f0f3fa;
    }

    h1,
    h2 {
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

    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right:
            1px solid
            rgba(0, 210, 255, 0.2) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #121721 !important;
        color: #00f2fe !important;
        border:
            1px solid
            rgba(0, 242, 254, 0.5) !important;
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
    li[role="option"] {
        background-color: #121721 !important;
        color: #ffffff !important;
        padding: 10px 14px !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background-color: #00f2fe !important;
        color: #000000 !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        border:
            1px solid
            rgba(0, 210, 255, 0.4) !important;
        border-radius: 8px !important;
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
        width: 100%;
    }

    .session-card {
        background: #161b22;
        border:
            1px solid
            rgba(0, 242, 254, 0.25);
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
        margin-top: 3px;
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

    .trade-card {
        background-color: #121721;
        border:
            1px solid
            rgba(0, 242, 254, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
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
# 16. PAYWALL
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

            <h3 style="color:#f0b90b;">
            🟡 Suscripción Mensual
            </h3>

            <h2 style="color:#ffffff;">
            $5.00 USD
            </h2>

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

            <h3 style="color:#00f2fe;">
            💎 Acceso Anual
            </h3>

            <h2 style="color:#ffffff;">
            $20.00 USD
            </h2>

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
            width:100%;">
            💎 Pagar $20 USD
            </button>

            </a>

            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 17. AUTENTICACIÓN
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
                                    "email":
                                        email,
                                    "password":
                                        password
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
                        "La contraseña debe tener al menos 6 caracteres."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        result = client.auth.sign_up(
                            {
                                "email":
                                    email,
                                "password":
                                    password
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
                                "redirectTo":
                                    app_url
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
# 18. SIDEBAR
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

                        nueva_foto_b64 = (
                            base64.b64encode(
                                nueva_foto.getvalue()
                            )
                            .decode("utf-8")
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
# 19. EDITAR TRADE
# =========================================================

def editar_trade_ui(
    row,
    user_id
):

    trade_id = row.get("id")

    st.markdown(
        "### ✏️ Editar operación"
    )

    try:

        fecha_default = (
            datetime.date.fromisoformat(
                str(
                    row.get(
                        "fecha",
                        datetime.date.today()
                    )
                )[:10]
            )
        )

    except Exception:

        fecha_default = (
            datetime.date.today()
        )

    par_actual = normalizar_activo(
        row.get(
            "par",
            LISTA_ACTIVOS[0]
        )
    )

    direccion_actual = row.get(
        "direccion",
        "LONG 🟢"
    )

    if direccion_actual not in [
        "LONG 🟢",
        "SHORT 🔴"
    ]:

        direccion_actual = "LONG 🟢"

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
            value=float(
                row.get(
                    "precio_entrada",
                    0
                ) or 0
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
                ) or 0
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
                ) or 0
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

        old_tf = row.get(
            "timeframe",
            
        )

        if old_tf not in timeframes:
            old_tf = ""

        timeframe = st.selectbox(
            "Timeframe",
            timeframes,
            index=timeframes.index(
                old_tf
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
                ) or 0
            ),
            step=10.0,
            key=f"edit_pnl_{trade_id}"
        )

        notas = st.text_area(
            "Notas emocionales",
            value=row.get(
                "notas_emocionales",
                ""
            ) or "",
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
            "**ANTES actual**"
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
            "**DESPUÉS actual**"
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

    csave, ccancel = st.columns(2)

    with csave:

        guardar = st.button(
            "💾 Guardar cambios",
            key=f"save_edit_{trade_id}"
        )

    with ccancel:

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
# 20. DASHBOARD
# =========================================================

def render_dashboard():

    (
        tiene_acceso,
        estado_sub,
        dias_restantes
    ) = evaluar_suscripcion(
        st.session_state.user
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

        if "beneficio_usd" not in df_trades.columns:
            df_trades[
                "beneficio_usd"
            ] = 0.0

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
    # TAB 1
    # =====================================================

    with tab1:

        st.markdown(
            "### ➕ Registrar nueva operación"
        )

        st.info(
            "💡 Sube la captura de TradingView "
            "y utiliza el escáner IA. "
            "La IA intentará detectar activo, "
            "dirección, Entry, SL, TP y timeframe."
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

            if upload_before:

                st.image(
                    upload_before,
                    caption="SETUP ANTES",
                    use_container_width=True
                )

                if st.button(
                    "🧠 ESCANEAR OPERACIÓN CON IA",
                    key="scan_new_trade"
                ):

                    with st.spinner(
                        "🔍 Analizando activo, dirección, "
                        "Entry, SL, TP y timeframe..."
                    ):

                        resultado_ia = (
                            analizar_captura_tradingview(
                                upload_before.getvalue(),
                                obtener_mime(
                                    upload_before
                                )
                            )
                        )

                    if resultado_ia.get(
                        "error"
                    ):

                        st.error(
                            resultado_ia[
                                "error"
                            ]
                        )

                    else:

                        aplicar_resultado_ia(
                            resultado_ia
                        )

                        st.session_state[
                            "last_ai_result"
                        ] = resultado_ia

                        st.success(
                            "✅ IA completó el análisis. "
                            "Los campos fueron actualizados."
                        )

                        st.rerun()

            if upload_after:

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

            fecha = st.date_input(
                "Fecha",
                datetime.date.today(),
                key="new_trade_date"
            )

            # ---------------------------------------------
            # VALORES DETECTADOS
            # ---------------------------------------------

            if (
                "last_ai_result"
                in st.session_state
            ):

                ai = st.session_state[
                    "last_ai_result"
                ]

                confidence = ai.get(
                    "confidence",
                    0
                )

                st.success(
                    f"🤖 Último escaneo IA — "
                    f"confianza aproximada: "
                    f"{confidence}%"
                )

                with st.expander(
                    "🔎 Ver lectura de la IA"
                ):

                    st.json(
                        ai
                    )

            # ---------------------------------------------
            # ACTIVO
            # ---------------------------------------------

            if (
                "new_trade_asset"
                not in st.session_state
            ):

                st.session_state[
                    "new_trade_asset"
                ] = LISTA_ACTIVOS[0]

            par = st.selectbox(
                "Activo / Par",
                LISTA_ACTIVOS,
                key="new_trade_asset"
            )

            # ---------------------------------------------
            # DIRECCIÓN
            # ---------------------------------------------

            if (
                "new_trade_direction"
                not in st.session_state
            ):

                st.session_state[
                    "new_trade_direction"
                ] = "LONG 🟢"

            direccion = st.radio(
                "Dirección",
                [
                    "LONG 🟢",
                    "SHORT 🔴"
                ],
                horizontal=True,
                key="new_trade_direction"
            )

            c1, c2 = st.columns(2)

            with c1:

                # -----------------------------------------
                # ENTRY
                # -----------------------------------------

                if (
                    "new_trade_entry"
                    not in st.session_state
                ):

                    st.session_state[
                        "new_trade_entry"
                    ] = 0.0

                entrada = st.number_input(
                    "Precio Entrada",
                    min_value=0.0,
                    value=float(
                        st.session_state[
                            "new_trade_entry"
                        ]
                    ),
                    format="%.5f",
                    key="new_trade_entry"
                )

                # -----------------------------------------
                # SL
                # -----------------------------------------

                if (
                    "new_trade_sl"
                    not in st.session_state
                ):

                    st.session_state[
                        "new_trade_sl"
                    ] = 0.0

                sl = st.number_input(
                    "Stop Loss",
                    min_value=0.0,
                    value=float(
                        st.session_state[
                            "new_trade_sl"
                        ]
                    ),
                    format="%.5f",
                    key="new_trade_sl"
                )

            with c2:

                # -----------------------------------------
                # TP
                # -----------------------------------------

                if (
                    "new_trade_tp"
                    not in st.session_state
                ):

                    st.session_state[
                        "new_trade_tp"
                    ] = 0.0

                tp = st.number_input(
                    "Take Profit",
                    min_value=0.0,
                    value=float(
                        st.session_state[
                            "new_trade_tp"
                        ]
                    ),
                    format="%.5f",
                    key="new_trade_tp"
                )

                # -----------------------------------------
                # TIMEFRAME
                # -----------------------------------------

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

                if (
                    "new_trade_tf"
                    not in st.session_state
                ):

                    st.session_state[
                        "new_trade_tf"
                    ] = ""

                timeframe = st.selectbox(
                    "Timeframe",
                    timeframes,
                    key="new_trade_tf"
                )

            # ---------------------------------------------
            # RR
            # ---------------------------------------------

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

            # ---------------------------------------------
            # PSICOTRADING
            # ---------------------------------------------

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
                placeholder=(
                    "¿Respetaste tu plan? "
                    "¿Qué sentías antes de entrar?"
                ),
                key="new_trade_notes"
            )

            # ---------------------------------------------
            # GUARDAR
            # ---------------------------------------------

            if st.button(
                "💾 GUARDAR TRADE",
                key="save_new_trade"
            ):

                img_before_b64 = ""

                img_after_b64 = ""

                if upload_before:

                    img_before_b64 = (
                        procesar_imagen_b64(
                            upload_before
                        )
                    )

                if upload_after:

                    img_after_b64 = (
                        procesar_imagen_b64(
                            upload_after
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
                        img_before_b64,

                    "img_after":
                        img_after_b64
                }

                if guardar_trade_supabase(
                    user_id,
                    data
                ):

                    st.success(
                        "✅ Trade guardado correctamente."
                    )

                    # Reset
                    st.session_state[
                        "new_trade_entry"
                    ] = 0.0

                    st.session_state[
                        "new_trade_sl"
                    ] = 0.0

                    st.session_state[
                        "new_trade_tp"
                    ] = 0.0

                    st.session_state[
                        "new_trade_asset"
                    ] = LISTA_ACTIVOS[0]

                    st.session_state[
                        "new_trade_direction"
                    ] = "LONG 🟢"

                    st.session_state[
                        "new_trade_tf"
                    ] = ""

                    st.session_state.pop(
                        "last_ai_result",
                        None
                    )

                    st.rerun()


    # =====================================================
    # TAB 2 TRACK RECORD
    # =====================================================

    with tab2:

        st.markdown(
            "### 📅 Track Record & Calendario PnL"
        )

        if df_trades.empty:

            st.info(
                "Aún no tienes operaciones registradas."
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

            today = (
                datetime.date.today()
            )

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

                        date_value = datetime.date(
                            today.year,
                            today.month,
                            day
                        )

                        key = str(
                            date_value
                        )

                        pnl_day = grouped.get(
                            key
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
                    ) or 0
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
    # TAB 3 CHAT IA
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
                        wins /
                        total *
                        100
                    )

                    answer = f"""
### 🧠 Resumen de tu operativa

Has registrado **{total} trades**.

**PnL acumulado:** ${pnl:,.2f}

**Win Rate:** {wr:.1f}%

**Wins:** {wins}

**Losses:** {losses}

No evalúes únicamente el porcentaje de acierto. Analiza también R:R, drawdown, emoción y contexto.
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
    # TAB 4 LOTAJE
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

            st.warning(
                "⚠️ La equivalencia de lotes cambia "
                "según instrumento y broker."
            )


    # =====================================================
    # TAB 5 ANÁLISIS IA
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
                        "OPENROUTER_API_KEY no está configurada."
                    )

                else:

                    with st.spinner(
                        "Analizando gráfico..."
                    ):

                        try:

                            b64 = base64.b64encode(
                                chart.getvalue()
                            ).decode("utf-8")

                            mime = obtener_mime(
                                chart
                            )

                            headers = {
                                "Authorization":
                                    f"Bearer {OPENROUTER_API_KEY}",
                                "Content-Type":
                                    "application/json"
                            }

                            prompt = """
Analiza este gráfico como auditor de trading.

No des una señal de compra o venta.

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
                                                        f"data:{mime};base64,{b64}"
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
    # TAB 6 PROYECCIONES
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
    # TAB 7 PSICOTRADING
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
    # TAB 8 DASHBOARD
    # =====================================================

    with tab8:

        st.markdown(
            "### 📊 Dashboard Operativo"
        )

        if df_trades.empty:

            st.info(
                "Registra operaciones para desbloquear "
                "tus estadísticas."
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
                wins /
                total *
                100
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
                for c in display_columns
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
# 21. FLUJO PRINCIPAL
# =========================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
