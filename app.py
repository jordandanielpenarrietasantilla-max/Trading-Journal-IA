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

defaults = {
    "authenticated": False,
    "user": None,
    "chat_history": [],
    "nombre_trader": "Trader Pro",
    "capital_actual": 10000.0,
    "capital_meta": 15000.0,
    "reglas_disciplina": DEFAULT_RULES,

    # IA
    "auto_asset": "",
    "auto_direction": "",
    "auto_entry": 0.0,
    "auto_sl": 0.0,
    "auto_tp": 0.0,
    "scan_message": "",

    # Control de edición
    "editing_trade": None
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
# 7. NORMALIZACIÓN DE ACTIVOS
# =========================================================

def normalizar_texto(texto):
    if not texto:
        return ""

    texto = str(texto).upper()
    texto = texto.replace(" ", "")
    texto = texto.replace("-", "")
    texto = texto.replace("_", "")
    texto = texto.replace("(", "")
    texto = texto.replace(")", "")
    texto = texto.replace("/", "")

    return texto


MAPA_ACTIVOS = {
    "XAUUSD": "🥇 XAU/USD (Oro)",
    "GOLD": "🥇 XAU/USD (Oro)",
    "ORO": "🥇 XAU/USD (Oro)",

    "XAGUSD": "🥈 XAG/USD (Plata)",
    "SILVER": "🥈 XAG/USD (Plata)",
    "PLATA": "🥈 XAG/USD (Plata)",

    "USOIL": "🛢️ USOIL (Petróleo WTI)",
    "WTI": "🛢️ USOIL (Petróleo WTI)",
    "OIL": "🛢️ USOIL (Petróleo WTI)",

    "UKOIL": "🛢️ UKOIL (Petróleo Brent)",
    "BRENT": "🛢️ UKOIL (Petróleo Brent)",

    "NGAS": "🌾 NGAS (Gas Natural)",
    "NATGAS": "🌾 NGAS (Gas Natural)",

    "BTCUSD": "🪙 BTC/USD (Bitcoin)",
    "BTC": "🪙 BTC/USD (Bitcoin)",

    "ETHUSD": "🪙 ETH/USD (Ethereum)",
    "ETH": "🪙 ETH/USD (Ethereum)",

    "SOLUSD": "🪙 SOL/USD (Solana)",
    "SOL": "🪙 SOL/USD (Solana)",

    "XRPUSD": "🪙 XRP/USD (Ripple)",
    "XRP": "🪙 XRP/USD (Ripple)",

    "BNBUSD": "🪙 BNB/USD (Binance Coin)",
    "BNB": "🪙 BNB/USD (Binance Coin)",

    "ADAUSD": "🪙 ADA/USD (Cardano)",
    "ADA": "🪙 ADA/USD (Cardano)",

    "DOGEUSD": "🪙 DOGE/USD (Dogecoin)",
    "DOGE": "🪙 DOGE/USD (Dogecoin)",

    "US100": "📊 US100 (Nasdaq 100)",
    "NAS100": "📊 US100 (Nasdaq 100)",
    "NASDAQ": "📊 US100 (Nasdaq 100)",

    "US30": "📊 US30 (Dow Jones)",
    "DOW": "📊 US30 (Dow Jones)",

    "US500": "📊 US500 (S&P 500)",
    "SP500": "📊 US500 (S&P 500)",
    "SPX": "📊 US500 (S&P 500)",

    "GER40": "📊 GER40 (Dax Alemán)",
    "DAX": "📊 GER40 (Dax Alemán)",

    "UK100": "📊 UK100 (FTSE 100)",
    "FTSE": "📊 UK100 (FTSE 100)",

    "JP225": "📊 JP225 (Nikkei 225)",
    "NIKKEI": "📊 JP225 (Nikkei 225)",

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


def normalizar_activo_detectado(valor):
    if not valor:
        return ""

    limpio = normalizar_texto(valor)

    if limpio in MAPA_ACTIVOS:
        return MAPA_ACTIVOS[limpio]

    # Buscar coincidencias parciales
    for clave, activo in MAPA_ACTIVOS.items():
        if clave in limpio or limpio in clave:
            return activo

    # Buscar por nombre
    for activo in LISTA_ACTIVOS:
        if normalizar_texto(activo) == limpio:
            return activo

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
            + str(e)
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
            "❌ Error guardando operación: "
            + str(e)
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
            "❌ Error actualizando operación: "
            + str(e)
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
            "❌ Error eliminando operación: "
            + str(e)
        )

        return False


# =========================================================
# 10. IA - ESCÁNER COMPLETO
# =========================================================

def analizar_captura_tradingview(
    image_bytes,
    mime_type="image/png"
):

    if not OPENROUTER_API_KEY:

        return {
            "error": (
                "OPENROUTER_API_KEY "
                "no está configurada."
            )
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

        prompt = """
Eres un analista experto en capturas de TradingView.

Analiza TODA la imagen cuidadosamente.

Tu objetivo es identificar los datos de una operación.

IMPORTANTE:

1. IDENTIFICA EL ACTIVO REAL visible en la captura.
2. IDENTIFICA si la operación es LONG o SHORT.
3. IDENTIFICA el ENTRY.
4. IDENTIFICA el STOP LOSS.
5. IDENTIFICA el TAKE PROFIT.
6. Si existe una herramienta Long Position o Short Position,
   úsala como fuente principal.
7. Busca también el ticker en la parte superior del gráfico.
8. NO asumas XAU/USD.
9. Si el activo es BTCUSD, EURUSD, GBPJPY, US30,
   NAS100, etc., debes devolver ese activo.
10. No confundas el activo con indicadores o símbolos secundarios.
11. Para dirección utiliza exclusivamente LONG o SHORT.
12. Para números devuelve números, sin símbolos de moneda.

ACTIVOS POSIBLES:

XAUUSD
XAGUSD
USOIL
UKOIL
NGAS
BTCUSD
ETHUSD
SOLUSD
XRPUSD
BNBUSD
ADAUSD
DOGEUSD
US100
US30
US500
GER40
UK100
JP225
EURUSD
GBPUSD
USDJPY
AUDUSD
USDCAD
USDCHF
NZDUSD
EURGBP
EURJPY
GBPJPY
AUDJPY
NVDA
TSLA
AAPL
AMZN
MSFT
GOOGL
META
AMD
NFLX
COIN

Devuelve ÚNICAMENTE un JSON válido con esta estructura:

{
    "asset": "XAUUSD",
    "direction": "LONG",
    "entry": 0.0,
    "sl": 0.0,
    "tp": 0.0,
    "confidence": 0
}

REGLAS:

- asset = ticker detectado.
- direction = LONG o SHORT.
- entry = precio de entrada.
- sl = stop loss.
- tp = take profit.
- confidence = número entero de 0 a 100.
- Si un dato realmente no puede determinarse usa 0.
- NO escribas explicaciones.
- NO escribas Markdown.
- NO uses ```json.
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

        if isinstance(content, list):

            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )

        content = str(content).strip()

        # Limpiar Markdown por seguridad
        content = re.sub(
            r"^```json\s*",
            "",
            content,
            flags=re.IGNORECASE
        )

        content = re.sub(
            r"^```\s*",
            "",
            content
        )

        content = re.sub(
            r"\s*```$",
            "",
            content
        )

        # Extraer solamente el objeto JSON
        match = re.search(
            r"\{.*\}",
            content,
            flags=re.DOTALL
        )

        if not match:

            return {
                "error":
                    "La IA no devolvió JSON válido."
            }

        data = json.loads(
            match.group(0)
        )

        asset = normalizar_activo_detectado(
            data.get("asset", "")
        )

        direction = str(
            data.get(
                "direction",
                ""
            )
        ).upper().strip()

        if direction not in [
            "LONG",
            "SHORT"
        ]:

            direction = ""

        try:
            entry = float(
                data.get("entry", 0) or 0
            )
        except Exception:
            entry = 0.0

        try:
            sl = float(
                data.get("sl", 0) or 0
            )
        except Exception:
            sl = 0.0

        try:
            tp = float(
                data.get("tp", 0) or 0
            )
        except Exception:
            tp = 0.0

        try:
            confidence = int(
                data.get(
                    "confidence",
                    0
                ) or 0
            )
        except Exception:
            confidence = 0

        return {
            "asset":
                asset,

            "direction":
                direction,

            "entry":
                entry,

            "sl":
                sl,

            "tp":
                tp,

            "confidence":
                confidence
        }

    except json.JSONDecodeError:

        return {
            "error":
                "La respuesta de IA no pudo "
                "convertirse a JSON."
        }

    except Exception as e:

        return {
            "error":
                "Error analizando imagen: "
                + str(e)
        }


# =========================================================
# 11. SESIONES
# =========================================================

SESIONES = [

    {
        "nombre":
            "🇦🇺 Sídney",

        "zona":
            "Australia/Sydney",

        "inicio":
            8,

        "fin":
            17
    },

    {
        "nombre":
            "🇯🇵 Tokio",

        "zona":
            "Asia/Tokyo",

        "inicio":
            9,

        "fin":
            18
    },

    {
        "nombre":
            "🇬🇧 Londres",

        "zona":
            "Europe/London",

        "inicio":
            8,

        "fin":
            17
    },

    {
        "nombre":
            "🇺🇸 Nueva York",

        "zona":
            "America/New_York",

        "inicio":
            8,

        "fin":
            17
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
# 12. SUSCRIPCIÓN
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
        or ""
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
# 13. CSS
# =========================================================

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
        color:#f0f3fa;
    }

    h1,h2 {
        background:linear-gradient(
            90deg,
            #00f2fe 0%,
            #4facfe 100%
        );

        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
        font-weight:800 !important;
    }

    section[data-testid="stSidebar"] {
        background-color:#0f141e !important;
        border-right:1px solid
            rgba(0,210,255,.2) !important;
    }

    div[data-baseweb="select"] > div {
        background-color:#121721 !important;
        color:#00f2fe !important;
        border:1px solid
            rgba(0,242,254,.5) !important;
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
    }

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea {
        background-color:#161b22 !important;
        color:#00f2fe !important;
        border:1px solid
            rgba(0,210,255,.4) !important;
        border-radius:8px !important;
    }

    .stButton > button {
        background:linear-gradient(
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
        border:1px solid
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
        margin-top:3px;
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

    .paywall-card {
        background-color:#161b22;
        border:1px solid #f0b90b;
        border-radius:12px;
        padding:24px;
        text-align:center;
    }

    </style>
    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


# =========================================================
# 14. PAYWALL
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
            width:100%;">
            💬 Enviar comprobante
            </button>

            </a>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# 15. AUTENTICACIÓN
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

                        st.success(
                            "Inicio de sesión correcto."
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "❌ No se pudo iniciar sesión: "
                            + str(e)
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

                        result = (
                            client
                            .auth
                            .sign_up(
                                {
                                    "email":
                                        email,
                                    "password":
                                        password
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
                            "❌ Error registrando usuario: "
                            + str(e)
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
                            "❌ Error: "
                            + str(e)
                        )


# =========================================================
# 16. SIDEBAR
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
                            ).decode("utf-8")
                        )

                    client = get_supabase_client()

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

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        "❌ Error actualizando perfil: "
                        + str(e)
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
            max(0, progreso)
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
            "Hora local automática de cada mercado."
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

            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []

            st.rerun()


# =========================================================
# 17. EDITAR TRADE
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
            datetime.date.fromisoformat(
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

        par_actual = (
            normalizar_activo_detectado(
                par_actual
            )
            or LISTA_ACTIVOS[0]
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
                )
                or 0
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
                or 0
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

        old_tf = row.get(
            "timeframe",
            ""
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

    st.markdown("---")

    preview1, preview2 = st.columns(2)

    with preview1:

        st.markdown(
            "**🖼️ ANTES actual**"
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
                "No hay imagen guardada."
            )

        if imagen_before:

            st.image(
                imagen_before,
                caption="Nueva imagen ANTES",
                use_container_width=True
            )

    with preview2:

        st.markdown(
            "**🖼️ DESPUÉS actual**"
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
                "No hay imagen guardada."
            )

        if imagen_after:

            st.image(
                imagen_after,
                caption="Nueva imagen DESPUÉS",
                use_container_width=True
            )

    st.markdown("---")

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

        st.session_state.editing_trade = None

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

            st.session_state.editing_trade = None

            st.success(
                "✅ Trade actualizado correctamente."
            )

            st.rerun()


# =========================================================
# 18. DASHBOARD
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
    # TAB 1
    # =====================================================

    with tab1:

        st.markdown(
            "### ➕ Registrar nueva operación"
        )

        st.info(
            "🧠 Sube una captura de TradingView. "
            "La IA intentará identificar automáticamente "
            "ACTIVO, LONG/SHORT, ENTRY, SL y TP."
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
                    "🧠 ESCANEAR TRADE COMPLETO",
                    key="scan_new_trade"
                ):

                    with st.spinner(
                        "IA leyendo activo, dirección, Entry, SL y TP..."
                    ):

                        extension = (
                            upload_before.name
                            .lower()
                        )

                        if extension.endswith(
                            ".jpg"
                        ) or extension.endswith(
                            ".jpeg"
                        ):

                            mime = "image/jpeg"

                        elif extension.endswith(
                            ".webp"
                        ):

                            mime = "image/webp"

                        else:

                            mime = "image/png"

                        extracted = (
                            analizar_captura_tradingview(
                                upload_before.getvalue(),
                                mime
                            )
                        )

                    if extracted and not extracted.get(
                        "error"
                    ):

                        # ---------------------------------
                        # GUARDAR RESULTADOS EN SESSION
                        # ---------------------------------

                        detected_asset = (
                            extracted.get(
                                "asset",
                                ""
                            )
                        )

                        detected_direction = (
                            extracted.get(
                                "direction",
                                ""
                            )
                        )

                        st.session_state.auto_asset = (
                            detected_asset
                        )

                        st.session_state.auto_direction = (
                            detected_direction
                        )

                        st.session_state.auto_entry = (
                            float(
                                extracted.get(
                                    "entry",
                                    0
                                )
                                or 0
                            )
                        )

                        st.session_state.auto_sl = (
                            float(
                                extracted.get(
                                    "sl",
                                    0
                                )
                                or 0
                            )
                        )

                        st.session_state.auto_tp = (
                            float(
                                extracted.get(
                                    "tp",
                                    0
                                )
                                or 0
                            )
                        )

                        confidence = extracted.get(
                            "confidence",
                            0
                        )

                        st.session_state.scan_message = (
                            "ok"
                        )

                        st.success(
                            "✅ Escaneo completado."
                        )

                        st.rerun()

                    else:

                        error = (
                            extracted.get(
                                "error",
                                "No se pudo analizar."
                            )
                            if extracted
                            else
                            "No hubo respuesta de la IA."
                        )

                        st.error(
                            "❌ " + str(error)
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

            if st.session_state.scan_message == "ok":

                detected = []

                if st.session_state.auto_asset:
                    detected.append(
                        f"Activo: **{st.session_state.auto_asset}**"
                    )

                if st.session_state.auto_direction:
                    detected.append(
                        f"Dirección: **{st.session_state.auto_direction}**"
                    )

                if st.session_state.auto_entry:
                    detected.append(
                        f"Entry: **{st.session_state.auto_entry}**"
                    )

                if st.session_state.auto_sl:
                    detected.append(
                        f"SL: **{st.session_state.auto_sl}**"
                    )

                if st.session_state.auto_tp:
                    detected.append(
                        f"TP: **{st.session_state.auto_tp}**"
                    )

                if detected:

                    st.success(
                        "🤖 Datos detectados por IA:\n\n"
                        + " | ".join(detected)
                    )

            fecha = st.date_input(
                "Fecha",
                datetime.date.today(),
                key="new_trade_date"
            )

            c1, c2 = st.columns(2)

            # ---------------------------------------------
            # ACTIVO + DIRECCIÓN
            # ---------------------------------------------

            with c1:

                detected_asset = (
                    st.session_state.auto_asset
                )

                if (
                    detected_asset
                    and detected_asset in LISTA_ACTIVOS
                ):

                    default_asset_index = (
                        LISTA_ACTIVOS.index(
                            detected_asset
                        )
                    )

                else:

                    default_asset_index = 0

                par = st.selectbox(
                    "Activo / Par",
                    LISTA_ACTIVOS,
                    index=default_asset_index,
                    key="new_trade_asset"
                )

                detected_direction = (
                    st.session_state.auto_direction
                )

                if detected_direction == "SHORT":

                    direction_index = 1

                else:

                    direction_index = 0

                direccion = st.radio(
                    "Dirección",
                    [
                        "LONG 🟢",
                        "SHORT 🔴"
                    ],
                    index=direction_index,
                    horizontal=True,
                    key="new_trade_direction"
                )

                entrada = st.number_input(
                    "Precio Entrada",
                    value=float(
                        st.session_state.auto_entry
                    ),
                    format="%.5f",
                    key="new_trade_entry"
                )

                sl = st.number_input(
                    "Stop Loss",
                    value=float(
                        st.session_state.auto_sl
                    ),
                    format="%.5f",
                    key="new_trade_sl"
                )

            # ---------------------------------------------
            # TP / RR
            # ---------------------------------------------

            with c2:

                tp = st.number_input(
                    "Take Profit",
                    value=float(
                        st.session_state.auto_tp
                    ),
                    format="%.5f",
                    key="new_trade_tp"
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

                timeframe = st.selectbox(
                    "Timeframe",
                    timeframes,
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
                    [
                        "WIN 🟢",
                        "LOSS 🔴",
                        "BE ⚪"
                    ],
                    key="new_trade_result"
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

                    st.session_state.auto_asset = ""
                    st.session_state.auto_direction = ""
                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0
                    st.session_state.scan_message = ""

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
                    or 0
                )

                titulo = (
                    f"📅 {row.get('fecha', '')} | "
                    f"{row.get('par', '')} | "
                    f"{row.get('direccion', '')} | "
                    f"{row.get('resultado', '')} | "
                    f"${pnl_value:,.2f}"
                )

                with st.expander(
                    titulo
                ):

                    if (
                        st.session_state.editing_trade
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

                            st.session_state.editing_trade = (
                                trade_id
                            )

                            st.rerun()

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

No evalúes solamente el porcentaje de acierto. Analiza también R:R, drawdown, emoción y contexto.
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
                * risk_percent
                / 100
            )

            lots = (
                risk_money
                / (
                    stop_distance
                    * 10
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
                "⚠️ La equivalencia cambia según "
                "instrumento y broker."
            )


    # =====================================================
    # TAB 5 - ANÁLISIS IA
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

Devuelve una evaluación educativa y clara.
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
                                                        f"data:image/png;base64,{b64}"
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

                                result = (
                                    response.json()
                                )

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
                                "Error de IA: "
                                + str(e)
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
                * win_rate_est
                / 100
            )

            losers = (
                trades_month
                - winners
            )

            pnl_month = (
                winners
                * avg_win
                -
                losers
                * avg_loss
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

            if "emocion" in df_trades.columns:

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
                .sort_values(
                    "fecha"
                )
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
# 19. FLUJO PRINCIPAL
# =========================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
