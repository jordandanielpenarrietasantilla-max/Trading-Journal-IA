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
# 2. CONFIGURACIÓN DE SERVICIOS
# ============================================================

LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"

BINANCE_PAY_ID = "JORDAN_SANTI9"
LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"


# ------------------------------------------------------------
# SUPABASE
# ------------------------------------------------------------

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


@st.cache_resource
def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "Faltan SUPABASE_URL y/o SUPABASE_KEY en Secrets."
        )

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
• Máximo 2 operaciones perdedoras por día.
• Stop Loss obligatorio.
• No operar por venganza.
• No entrar por FOMO."""


def inicializar_estado():

    defaults = {
        "authenticated": False,
        "user": None,
        "chat_history": [],
        "nombre_trader": "Trader Pro",
        "capital_actual": 10000.0,
        "capital_meta": 15000.0,
        "reglas_disciplina": DEFAULT_RULES,
        "auto_entry": 0.0,
        "auto_sl": 0.0,
        "auto_tp": 0.0,
        "perfil_cargado": False
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


inicializar_estado()


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
# 5. FUNCIONES DE IMÁGENES
# ============================================================

def imagen_a_base64(uploaded_file, max_size=(1000, 800)):

    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file).convert("RGB")

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

        st.error(
            f"Error procesando imagen: {e}"
        )

        return ""


# ============================================================
# 6. FUNCIONES SUPABASE - TRADES
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
            f"Error cargando operaciones: {e}"
        )

        return []


def guardar_trade_supabase(user_id, trade_data):

    try:

        client = get_supabase_client()

        payload = dict(trade_data)

        payload["user_id"] = user_id

        response = (
            client
            .table("trades")
            .insert(payload)
            .execute()
        )

        return bool(response.data)

    except Exception as e:

        st.error(
            f"Error guardando operación: {e}"
        )

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

        st.error(
            f"Error eliminando operación: {e}"
        )

        return False


# ============================================================
# 7. PERFIL DEL USUARIO
# ============================================================

def cargar_perfil_usuario():

    user = st.session_state.user

    if not user:
        return

    metadata = getattr(
        user,
        "user_metadata",
        {}
    ) or {}

    st.session_state.nombre_trader = metadata.get(
        "username",
        "Trader Pro"
    )

    st.session_state.capital_actual = float(
        metadata.get(
            "capital_actual",
            10000.0
        )
    )

    st.session_state.capital_meta = float(
        metadata.get(
            "capital_meta",
            15000.0
        )
    )

    st.session_state.reglas_disciplina = metadata.get(
        "reglas_disciplina",
        DEFAULT_RULES
    )

    st.session_state.perfil_cargado = True


def guardar_perfil_usuario(
    nombre,
    capital_actual,
    capital_meta,
    reglas,
    avatar_b64=None
):

    try:

        client = get_supabase_client()

        current_metadata = (
            st.session_state.user.user_metadata
            if st.session_state.user
            else {}
        ) or {}

        metadata = {
            **current_metadata,
            "username": nombre,
            "capital_actual": float(capital_actual),
            "capital_meta": float(capital_meta),
            "reglas_disciplina": reglas
        }

        if avatar_b64 is not None:
            metadata["avatar_b64"] = avatar_b64

        response = client.auth.update_user({
            "data": metadata
        })

        st.session_state.user = response.user

        st.session_state.nombre_trader = nombre
        st.session_state.capital_actual = float(capital_actual)
        st.session_state.capital_meta = float(capital_meta)
        st.session_state.reglas_disciplina = reglas

        return True

    except Exception as e:

        st.error(
            f"Error guardando perfil: {e}"
        )

        return False


# ============================================================
# 8. IA - ANÁLISIS DE TRADINGVIEW
# ============================================================

def analizar_captura_tradingview(image_bytes):

    if not OPENROUTER_API_KEY:
        st.warning(
            "No existe OPENROUTER_API_KEY en los Secrets."
        )
        return None

    try:

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
o cualquier elemento que muestre Entry, Stop Loss
y Take Profit.

Devuelve ÚNICAMENTE JSON válido.

Formato exacto:

{
  "entry": 0.0,
  "sl": 0.0,
  "tp": 0.0
}

Si no puedes encontrar alguno de los valores,
usa 0.0.

No escribas explicaciones.
No uses Markdown.
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
            ],
            "temperature": 0
        }

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=45
        )

        response.raise_for_status()

        data = response.json()

        content = (
            data["choices"][0]["message"]["content"]
            .strip()
        )

        content = (
            content
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        result = json.loads(content)

        return {
            "entry": float(result.get("entry", 0)),
            "sl": float(result.get("sl", 0)),
            "tp": float(result.get("tp", 0))
        }

    except Exception as e:

        st.error(
            f"No se pudo analizar la imagen: {e}"
        )

        return None


# ============================================================
# 9. ESTILOS
# ============================================================

def aplicar_estilos():

    css = """

    <style>

    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
    }

    p, label, h1, h2, h3, h4, span,
    div, .stMarkdown {
        color: #f0f3fa !important;
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

        border: 1px solid
        rgba(0, 242, 254, 0.5) !important;

        border-radius: 8px !important;
    }

    div[data-baseweb="select"] input {

        color: #00f2fe !important;

        -webkit-text-fill-color: #00f2fe !important;
    }

    div[data-baseweb="select"]
    span[data-testid="stMarkdownContainer"] p {

        color: #00f2fe !important;
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

        font-size: 14px !important;

        padding: 10px 14px !important;

        border-bottom:
        1px solid rgba(255,255,255,0.05) !important;
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

        border: 1px solid
        rgba(0, 210, 255, 0.4) !important;

        border-radius: 8px !important;
    }

    div[data-testid="stChatInput"] {

        background-color: #161b22 !important;

        border-radius: 12px !important;

        border: 1px solid
        rgba(0, 210, 255, 0.5) !important;
    }

    div[data-testid="stChatInput"] textarea {

        background-color: #161b22 !important;

        color: #00f2fe !important;

        -webkit-text-fill-color: #00f2fe !important;
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

        box-shadow:
        0px 4px 15px
        rgba(0, 210, 255, 0.3) !important;
    }

    section[data-testid="stSidebar"] {

        background-color: #0f141e !important;

        border-right: 1px solid
        rgba(0, 210, 255, 0.2) !important;
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

    if not user:
        return False, "Sin sesión", 0

    email = (
        getattr(user, "email", "")
        or ""
    ).lower()

    # ADMIN
    if email == "jordandanielpenarrietasantilla@gmail.com":
        return True, "Creador / Admin 👑", 99999

    metadata = (
        getattr(user, "user_metadata", {})
        or {}
    )

    # VIP
    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999

    created_at = getattr(
        user,
        "created_at",
        None
    )

    if created_at:

        try:

            fecha_registro = datetime.datetime.strptime(
                str(created_at)[:10],
                "%Y-%m-%d"
            ).date()

        except Exception:

            fecha_registro = datetime.date.today()

    else:

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
        "## 🔒 Tu período de prueba ha expirado"
    )

    st.markdown(
        """
        Para continuar utilizando el Journal,
        Track Record y herramientas de IA,
        activa tu acceso PRO.
        """
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            <div class="paywall-card">

            <h3>🟡 Suscripción Mensual</h3>

            <h2>$5 USD / mes</h2>

            <p>
            Luego $2.50 USD / mes
            </p>

            <hr>

            <p>✔️ Acceso ilimitado</p>
            <p>✔️ Track Record PnL</p>
            <p>✔️ Auditoría IA</p>
            <p>✔️ Chat IA</p>
            <p>✔️ Sin contratos</p>

            <br>

            <a
            href="{LINK_BINANCE_INSCRIPCION}"
            target="_blank">

            <button style="
            background:#f0b90b;
            color:black;
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

            <h2>$20 USD / año</h2>

            <p>
            Ahorra frente al plan mensual
            </p>

            <hr>

            <p>🌟 Acceso por 1 año</p>
            <p>🔒 Pago único</p>
            <p>🎁 Actualizaciones incluidas</p>
            <p>🧠 IA prioritaria</p>

            <br>

            <a
            href="{LINK_BINANCE_ANUAL}"
            target="_blank">

            <button style="
            background:#00f2fe;
            color:black;
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
            "### 📲 Pago / Renovación"
        )

        st.code(
            f"Binance Pay ID: {BINANCE_PAY_ID}"
        )

        st.markdown(
            f"""
            [Renovación mensual $2.50 USD]
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
            ">

            💬 Enviar comprobante

            </button>

            </a>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# 12. AUTENTICACIÓN
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
            - 📈 Proyecciones
            - 💰 Gestión de riesgo
            - 📸 Análisis de capturas
            """
        )

    with col2:

        tabs = st.tabs([
            "🔑 Iniciar Sesión",
            "📝 Registrarse",
            "🔐 Recuperar Clave"
        ])

        # LOGIN
        with tabs[0]:

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
                        "Completa todos los campos."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        response = (
                            client
                            .auth
                            .sign_in_with_password({
                                "email": email,
                                "password": password
                            })
                        )

                        st.session_state.authenticated = True

                        st.session_state.user = (
                            response.user
                        )

                        cargar_perfil_usuario()

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"No se pudo iniciar sesión: {e}"
                        )

        # REGISTRO
        with tabs[1]:

            st.markdown(
                "### Crear cuenta"
            )

            st.info(
                "Incluye 3 días de prueba."
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
                key="register_password2"
            )

            if st.button(
                "Crear cuenta",
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

                        response = (
                            client
                            .auth
                            .sign_up({
                                "email": email,
                                "password": password,
                                "options": {
                                    "data": {
                                        "username": "Trader Pro",
                                        "capital_actual": 10000,
                                        "capital_meta": 15000,
                                        "reglas_disciplina":
                                            DEFAULT_RULES
                                    }
                                }
                            })
                        )

                        st.success(
                            "Cuenta creada. Revisa tu correo si Supabase solicita confirmación."
                        )

                    except Exception as e:

                        st.error(
                            f"Error registrando cuenta: {e}"
                        )

        # RECUPERACIÓN
        with tabs[2]:

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
                        "Ingresa tu correo."
                    )

                else:

                    try:

                        client = get_supabase_client()

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
                            "📩 Revisa tu correo electrónico."
                        )

                    except Exception as e:

                        st.error(
                            f"Error: {e}"
                        )


# ============================================================
# 13. SIDEBAR
# ============================================================

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

        nombre = metadata.get(
            "username",
            st.session_state.nombre_trader
        )

        email = (
            getattr(user, "email", "")
            or ""
        )

        avatar = metadata.get(
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

            if avatar:

                st.markdown(
                    f"""
                    <img
                    src="data:image/jpeg;base64,{avatar}"
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
                    "👤",
                    unsafe_allow_html=True
                )

        with c2:

            st.markdown(
                f"**{nombre}**"
            )

            st.caption(
                email
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
        # PERFIL
        # ----------------------------------------------------

        with st.expander(
            "⚙️ Modificar Perfil"
        ):

            nuevo_nombre = st.text_input(
                "Nombre",
                value=nombre
            )

            nueva_foto = st.file_uploader(
                "Nueva foto",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp"
                ]
            )

            if st.button(
                "Guardar Perfil",
                key="save_profile"
            ):

                avatar_nuevo = None

                if nueva_foto:

                    avatar_nuevo = base64.b64encode(
                        nueva_foto.getvalue()
                    ).decode("utf-8")

                ok = guardar_perfil_usuario(
                    nuevo_nombre,
                    st.session_state.capital_actual,
                    st.session_state.capital_meta,
                    st.session_state.reglas_disciplina,
                    avatar_nuevo
                )

                if ok:

                    st.success(
                        "Perfil actualizado."
                    )

                    st.rerun()

        st.markdown("---")

        # ----------------------------------------------------
        # META
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        capital = st.session_state.capital_actual
        meta = st.session_state.capital_meta

        progreso = (
            capital / meta
            if meta > 0
            else 0
        )

        progreso = min(
            1,
            max(0, progreso)
        )

        st.markdown(
            f"""
            **Capital:** ${capital:,.2f}
            /
            ${meta:,.2f}
            """
        )

        st.progress(
            progreso
        )

        with st.expander(
            "🔧 Configurar Meta"
        ):

            nuevo_capital = st.number_input(
                "Capital actual",
                value=float(capital),
                step=100.0
            )

            nueva_meta = st.number_input(
                "Meta",
                value=float(meta),
                step=500.0
            )

            if st.button(
                "Guardar Meta",
                key="save_goal"
            ):

                if guardar_perfil_usuario(
                    nombre,
                    nuevo_capital,
                    nueva_meta,
                    st.session_state.reglas_disciplina,
                    None
                ):

                    st.success(
                        "Meta guardada."
                    )

                    st.rerun()

        st.markdown("---")

        # ----------------------------------------------------
        # REGLAS
        # ----------------------------------------------------

        st.markdown(
            "### 🎯 Mis Reglas"
        )

        with st.expander(
            "✏️ Editar reglas"
        ):

            reglas = st.text_area(
                "Reglas personales",
                value=st.session_state.reglas_disciplina,
                height=180
            )

            if st.button(
                "Guardar Reglas",
                key="save_rules"
            ):

                if guardar_perfil_usuario(
                    nombre,
                    capital,
                    meta,
                    reglas,
                    None
                ):

                    st.toast(
                        "Reglas actualizadas.",
                        icon="✅"
                    )

                    st.rerun()

        st.markdown(
            st.session_state.reglas_disciplina
        )

        st.markdown("---")

        # ----------------------------------------------------
        # SESIONES
        # ----------------------------------------------------

        st.markdown(
            "### ⏰ Sesiones de Mercado"
        )

        ahora = datetime.datetime.now()

        st.markdown(
            f"""
            <div style="
            background:#161b22;
            border:1px solid #00d2ff;
            padding:10px;
            border-radius:8px;
            text-align:center;
            font-size:18px;
            color:#00f2fe;
            ">
            🕐 {ahora.strftime("%H:%M:%S")}
            </div>
            """,
            unsafe_allow_html=True
        )

        utc_hour = datetime.datetime.utcnow().hour

        london_open = (
            7 <= utc_hour <= 15
        )

        ny_open = (
            12 <= utc_hour <= 20
        )

        st.markdown(
            f"""
            **Londres:** 
            <span class="market-badge {'open' if london_open else 'closed'}">
            {'ABIERTO' if london_open else 'CERRADO'}
            </span>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            **Nueva York:** 
            <span class="market-badge {'open' if ny_open else 'closed'}">
            {'ABIERTO' if ny_open else 'CERRADO'}
            </span>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")

        # LOGOUT

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


# ============================================================
# 14. TAB 1 - REGISTRAR TRADE
# ============================================================

def render_tab_registrar(
    user_id,
    trades_db
):

    st.markdown(
        "### ➕ Registrar Nueva Operación"
    )

    st.info(
        """
        💡 Sube una captura de TradingView con
        la herramienta de posición y la IA intentará
        detectar automáticamente Entry, Stop Loss y Take Profit.
        """
    )

    col1, col2 = st.columns(
        [1.15, 1]
    )

    # --------------------------------------------------------
    # IMÁGENES
    # --------------------------------------------------------

    with col2:

        st.markdown(
            "### 🖼️ Antes & Después"
        )

        upload_before = st.file_uploader(
            "1️⃣ Captura ANTES",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="trade_before"
        )

        upload_after = st.file_uploader(
            "2️⃣ Captura DESPUÉS",
            type=[
                "png",
                "jpg",
                "jpeg"
            ],
            key="trade_after"
        )

        img_before_b64 = ""
        img_after_b64 = ""

        if upload_before:

            bytes_before = (
                upload_before.getvalue()
            )

            img_before_b64 = (
                imagen_a_base64(
                    upload_before
                )
            )

            st.image(
                upload_before,
                caption="SETUP ANTES",
                use_container_width=True
            )

            if st.button(
                "🧠 Escanear Setup con IA",
                key="scan_setup"
            ):

                with st.spinner(
                    "La IA está leyendo el gráfico..."
                ):

                    resultado = (
                        analizar_captura_tradingview(
                            bytes_before
                        )
                    )

                if resultado:

                    st.session_state.auto_entry = (
                        resultado["entry"]
                    )

                    st.session_state.auto_sl = (
                        resultado["sl"]
                    )

                    st.session_state.auto_tp = (
                        resultado["tp"]
                    )

                    st.success(
                        "Valores detectados."
                    )

                    st.rerun()

                else:

                    st.warning(
                        "No pude detectar los valores."
                    )

        if upload_after:

            img_after_b64 = (
                imagen_a_base64(
                    upload_after
                )
            )

            st.image(
                upload_after,
                caption="RESULTADO DESPUÉS",
                use_container_width=True
            )

        pnl = st.number_input(
            "Ganancia / Pérdida USD",
            value=0.0,
            step=10.0,
            key="trade_pnl"
        )

    # --------------------------------------------------------
    # DATOS
    # --------------------------------------------------------

    with col1:

        fecha = st.date_input(
            "Fecha",
            datetime.date.today(),
            key="trade_date"
        )

        c1, c2 = st.columns(2)

        with c1:

            par = st.selectbox(
                "Activo / Par",
                LISTA_ACTIVOS,
                key="trade_asset"
            )

            direccion = st.radio(
                "Dirección",
                [
                    "LONG 🟢",
                    "SHORT 🔴"
                ],
                horizontal=True,
                key="trade_direction"
            )

            entry = st.number_input(
                "Precio Entrada",
                value=float(
                    st.session_state.auto_entry
                ),
                format="%.5f",
                key="trade_entry"
            )

            sl = st.number_input(
                "Stop Loss",
                value=float(
                    st.session_state.auto_sl
                ),
                format="%.5f",
                key="trade_sl"
            )

        with c2:

            tp = st.number_input(
                "Take Profit",
                value=float(
                    st.session_state.auto_tp
                ),
                format="%.5f",
                key="trade_tp"
            )

            riesgo = abs(
                entry - sl
            )

            beneficio = abs(
                tp - entry
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
                key="trade_result"
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
            key="trade_emotion"
        )

        notas = st.text_area(
            "Notas de la operación",
            placeholder=(
                "¿Respetaste tu plan? "
                "¿Qué aprendiste?"
            ),
            key="trade_notes"
        )

        if st.button(
            "💾 Guardar Trade",
            key="save_trade",
            type="primary"
        ):

            if entry <= 0:

                st.error(
                    "Introduce un precio de entrada válido."
                )

            elif sl <= 0:

                st.error(
                    "El Stop Loss es obligatorio."
                )

            elif tp <= 0:

                st.error(
                    "Introduce un Take Profit válido."
                )

            else:

                nuevo_trade = {

                    "fecha": str(fecha),

                    "par": par,

                    "direccion": direccion,

                    "entry": float(entry),

                    "stop_loss": float(sl),

                    "take_profit": float(tp),

                    "rr": float(rr),

                    "resultado": resultado,

                    "emocion": emocion,

                    "notas": notas,

                    "beneficio_usd": float(pnl),

                    "trades_cant": 1,

                    "img_before": img_before_b64,

                    "img_after": img_after_b64
                }

                if guardar_trade_supabase(
                    user_id,
                    nuevo_trade
                ):

                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0

                    st.success(
                        "✅ Operación guardada correctamente."
                    )

                    st.rerun()


# ============================================================
# 15. TAB 2 - TRACK RECORD
# ============================================================

def render_tab_track_record(
    user_id,
    df
):

    st.markdown(
        "### 📅 Track Record & Calendario PnL"
    )

    if df.empty:

        st.info(
            "Todavía no tienes operaciones registradas."
        )

        return

    df["beneficio_usd"] = pd.to_numeric(
        df["beneficio_usd"],
        errors="coerce"
    ).fillna(0)

    total_pnl = (
        df["beneficio_usd"].sum()
    )

    wins = len(
        df[df["beneficio_usd"] > 0]
    )

    losses = len(
        df[df["beneficio_usd"] < 0]
    )

    win_rate = (
        wins / len(df) * 100
        if len(df) > 0
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
        len(df)
    )

    c4.metric(
        "Wins / Losses",
        f"{wins} / {losses}"
    )

    st.markdown("---")

    # --------------------------------------------------------
    # CALENDARIO
    # --------------------------------------------------------

    df["fecha"] = pd.to_datetime(
        df["fecha"]
    ).dt.date

    grouped = (
        df.groupby("fecha")
        .agg({
            "beneficio_usd": "sum",
            "trades_cant": "count"
        })
        .reset_index()
    )

    pnl_map = dict(
        zip(
            grouped["fecha"],
            grouped["beneficio_usd"]
        )
    )

    trades_map = dict(
        zip(
            grouped["fecha"],
            grouped["trades_cant"]
        )
    )

    hoy = datetime.date.today()

    semanas = calendar.Calendar(
        firstweekday=6
    ).monthdayscalendar(
        hoy.year,
        hoy.month
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

    for i, name in enumerate(headers):

        with cols[i]:

            st.markdown(
                f"""
                <div style="
                text-align:center;
                font-weight:bold;
                ">
                {name}
                </div>
                """,
                unsafe_allow_html=True
            )

    for semana in semanas:

        cols = st.columns(7)

        for i, day in enumerate(semana):

            with cols[i]:

                if day == 0:

                    st.markdown(
                        "<div style='height:90px'></div>",
                        unsafe_allow_html=True
                    )

                    continue

                fecha = datetime.date(
                    hoy.year,
                    hoy.month,
                    day
                )

                pnl = pnl_map.get(
                    fecha,
                    None
                )

                trades = trades_map.get(
                    fecha,
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
                    if fecha == hoy
                    else "1px solid #30363d"
                )

                st.markdown(
                    f"""
                    <div style="
                    background:{bg};
                    color:{text};
                    border:{border};
                    border-radius:8px;
                    height:85px;
                    padding:7px;
                    margin-bottom:5px;
                    ">

                    <b>{day}</b>

                    <div style="
                    text-align:center;
                    margin-top:10px;
                    font-weight:bold;
                    ">

                    {pnl_text}

                    </div>

                    <div style="
                    text-align:center;
                    font-size:11px;
                    ">

                    {trades} trade(s)

                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # --------------------------------------------------------
    # HISTORIAL
    # --------------------------------------------------------

    st.markdown("---")

    st.markdown(
        "### 📋 Historial Detallado"
    )

    for _, row in df.iterrows():

        trade_id = row.get(
            "id"
        )

        pnl = float(
            row.get(
                "beneficio_usd",
                0
            )
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

            c1, c2, c3 = st.columns(
                [1.3, 2, 2]
            )

            with c1:

                st.markdown(
                    "#### ⚙️ Operación"
                )

                st.write(
                    f"**Dirección:** "
                    f"{row.get('direccion', 'N/A')}"
                )

                st.write(
                    f"**Entrada:** "
                    f"{row.get('entry', 'N/A')}"
                )

                st.write(
                    f"**Stop Loss:** "
                    f"{row.get('stop_loss', 'N/A')}"
                )

                st.write(
                    f"**Take Profit:** "
                    f"{row.get('take_profit', 'N/A')}"
                )

                st.write(
                    f"**RR:** "
                    f"1 : {row.get('rr', 'N/A')}"
                )

                st.write(
                    f"**Emoción:** "
                    f"{row.get('emocion', 'N/A')}"
                )

                st.write(
                    f"**PnL:** "
                    f"${pnl:,.2f}"
                )

                notas = row.get(
                    "notas",
                    ""
                )

                if notas:

                    st.markdown(
                        f"**Notas:** {notas}"
                    )

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
                    "#### 1️⃣ ANTES"
                )

                img = row.get(
                    "img_before"
                )

                if (
                    img
                    and str(img).startswith(
                        "data:image"
                    )
                ):

                    st.image(
                        img,
                        use_container_width=True
                    )

                else:

                    st.caption(
                        "Sin captura"
                    )

            with c3:

                st.markdown(
                    "#### 2️⃣ DESPUÉS"
                )

                img = row.get(
                    "img_after"
                )

                if (
                    img
                    and str(img).startswith(
                        "data:image"
                    )
                ):

                    st.image(
                        img,
                        use_container_width=True
                    )

                else:

                    st.caption(
                        "Sin captura"
                    )

    # --------------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------------

    grouped_chart = grouped.copy()

    grouped_chart["tipo"] = np.where(
        grouped_chart["beneficio_usd"] >= 0,
        "GANANCIA",
        "PÉRDIDA"
    )

    fig = px.bar(
        grouped_chart,
        x="fecha",
        y="beneficio_usd",
        color="tipo",
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


# ============================================================
# 16. TAB 3 - CHAT IA
# ============================================================

def render_tab_chat(df):

    st.markdown(
        "### 💬 Chat IA & Auditoría"
    )

    st.caption(
        "Consulta tus estadísticas y hábitos de trading."
    )

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    prompt = st.chat_input(
        "Pregunta sobre tu trading..."
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

            if df.empty:

                answer = (
                    "Todavía no tienes trades "
                    "registrados."
                )

            else:

                pnl = df[
                    "beneficio_usd"
                ].sum()

                wins = len(
                    df[
                        df["beneficio_usd"] > 0
                    ]
                )

                total = len(df)

                win_rate = (
                    wins / total * 100
                    if total
                    else 0
                )

                losses = len(
                    df[
                        df["beneficio_usd"] < 0
                    ]
                )

                answer = f"""
### 🧠 Auditoría rápida

Has registrado **{total} operaciones**.

**PnL acumulado:** ${pnl:,.2f}

**Win Rate:** {win_rate:.1f}%

**Wins:** {wins}

**Losses:** {losses}

Tu siguiente objetivo debería ser estudiar
qué emociones aparecen con mayor frecuencia
antes de tus pérdidas y no solamente buscar
más operaciones ganadoras.
"""

            st.markdown(answer)

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": answer
                }
            )


# ============================================================
# 17. TAB 4 - CALCULADORA DE LOTAJE
# ============================================================

def render_tab_lotaje():

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

        riesgo_pct = st.number_input(
            "Riesgo por operación (%)",
            value=1.0,
            min_value=0.01,
            max_value=100.0,
            step=0.25
        )

        distancia = st.number_input(
            "Stop Loss (pips/puntos)",
            value=20.0,
            min_value=0.1,
            step=1.0
        )

    with c2:

        riesgo_usd = (
            balance *
            riesgo_pct /
            100
        )

        lotes = (
            riesgo_usd /
            (distancia * 10)
        )

        st.metric(
            "Riesgo máximo",
            f"${riesgo_usd:,.2f}"
        )

        st.metric(
            "Lotaje estimado",
            f"{lotes:.2f}"
        )

        st.warning(
            "⚠️ Esta fórmula es una aproximación "
            "para Forex estándar. Oro, índices, "
            "cripto y CFDs requieren conocer "
            "el valor por punto de tu broker."
        )


# ============================================================
# 18. TAB 5 - AUDITORÍA VISUAL
# ============================================================

def render_tab_auditoria():

    st.markdown(
        "### 🤖 Auditoría Visual de Mercado"
    )

    st.caption(
        "Sube un gráfico para analizar visualmente "
        "tu setup."
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
            "🔍 Auditar Setup",
            key="audit_button"
        ):

            if not OPENROUTER_API_KEY:

                st.warning(
                    "Configura OPENROUTER_API_KEY "
                    "para activar la auditoría IA."
                )

            else:

                with st.spinner(
                    "Analizando gráfico..."
                ):

                    resultado = (
                        analizar_captura_tradingview(
                            chart.getvalue()
                        )
                    )

                if resultado:

                    st.success(
                        "Análisis visual completado."
                    )

                    c1, c2, c3 = st.columns(3)

                    c1.metric(
                        "Entry detectado",
                        resultado["entry"]
                    )

                    c2.metric(
                        "Stop Loss",
                        resultado["sl"]
                    )

                    c3.metric(
                        "Take Profit",
                        resultado["tp"]
                    )


# ============================================================
# 19. TAB 6 - PROYECCIONES
# ============================================================

def render_tab_proyecciones():

    st.markdown(
        "### 📈 Proyección de Capital"
    )

    c1, c2 = st.columns(2)

    with c1:

        trades_mes = st.slider(
            "Trades por mes",
            5,
            50,
            15
        )

        win_rate = st.slider(
            "Win Rate estimado (%)",
            30,
            90,
            55
        )

    with c2:

        win_avg = st.number_input(
            "Ganancia media por WIN",
            value=200.0,
            step=25.0
        )

        loss_avg = st.number_input(
            "Pérdida media por LOSS",
            value=100.0,
            step=25.0
        )

    capital = (
        st.session_state.capital_actual
    )

    datos = []

    for month in range(1, 13):

        winners = (
            trades_mes *
            win_rate /
            100
        )

        losers = (
            trades_mes -
            winners
        )

        pnl = (
            winners * win_avg
            -
            losers * loss_avg
        )

        capital += pnl

        datos.append(
            {
                "Mes": month,
                "Capital": capital
            }
        )

    df_proj = pd.DataFrame(
        datos
    )

    st.metric(
        "Capital proyectado 12 meses",
        f"${capital:,.2f}"
    )

    fig = px.line(
        df_proj,
        x="Mes",
        y="Capital",
        markers=True,
        template="plotly_dark",
        title="Proyección 12 meses"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# 20. TAB 7 - PSICOTRADING
# ============================================================

def render_tab_psicotrading():

    st.markdown(
        "### 📓 Diario de Psicotrading"
    )

    st.caption(
        "Registra tus pensamientos, emociones y aprendizajes."
    )

    fecha = st.date_input(
        "Fecha",
        datetime.date.today(),
        key="journal_date"
    )

    reflexion = st.text_area(
        "Reflexión",
        height=220,
        placeholder="""
¿Cómo estaba mi mente hoy?

¿Respeté mi plan?

¿Entré por FOMO?

¿Moví el Stop Loss?

¿Intenté recuperar una pérdida?

¿Qué haré diferente mañana?
"""
    )

    if st.button(
        "💾 Guardar Reflexión",
        key="save_journal"
    ):

        st.success(
            f"Reflexión del {fecha} guardada en esta sesión."
        )

        st.info(
            "En la siguiente versión podemos "
            "guardar también estas reflexiones "
            "permanentemente en Supabase."
        )


# ============================================================
# 21. TAB 8 - DASHBOARD
# ============================================================

def render_tab_dashboard(df):

    st.markdown(
        "### 📊 Dashboard & Rendimiento"
    )

    if df.empty:

        st.info(
            "Registra tu primer trade para comenzar."
        )

        return

    df["beneficio_usd"] = pd.to_numeric(
        df["beneficio_usd"],
        errors="coerce"
    ).fillna(0)

    total = len(df)

    wins = len(
        df[df["beneficio_usd"] > 0]
    )

    losses = len(
        df[df["beneficio_usd"] < 0]
    )

    pnl = df[
        "beneficio_usd"
    ].sum()

    win_rate = (
        wins / total * 100
        if total
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
        "Trades",
        total
    )

    c4.metric(
        "Días",
        df["fecha"].nunique()
    )

    st.markdown("---")

    # --------------------------------------------------------
    # PNL POR ACTIVO
    # --------------------------------------------------------

    if "par" in df.columns:

        asset_df = (
            df.groupby("par")
            ["beneficio_usd"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            asset_df,
            x="par",
            y="beneficio_usd",
            title="PnL por Activo",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------------
    # EMOCIONES
    # --------------------------------------------------------

    if "emocion" in df.columns:

        emotion_df = (
            df.groupby("emocion")
            ["beneficio_usd"]
            .sum()
            .reset_index()
        )

        fig2 = px.bar(
            emotion_df,
            x="emocion",
            y="beneficio_usd",
            title="PnL según Estado Emocional",
            template="plotly_dark"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    st.markdown(
        "### 📋 Todas las Operaciones"
    )

    columnas = [
        "fecha",
        "par",
        "direccion",
        "resultado",
        "beneficio_usd",
        "emocion"
    ]

    columnas_validas = [
        c for c in columnas
        if c in df.columns
    ]

    st.dataframe(
        df[columnas_validas],
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# 22. DASHBOARD GENERAL
# ============================================================

def render_dashboard():

    if not st.session_state.perfil_cargado:

        cargar_perfil_usuario()

    tiene_acceso, estado_sub, dias = (
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

    user = st.session_state.user

    if not user:

        st.session_state.authenticated = False

        st.rerun()

    user_id = user.id

    trades = cargar_trades_usuario(
        user_id
    )

    df = pd.DataFrame(
        trades
    )

    st.markdown(
        "## ⚡ AI Trading Journal & Auditor"
    )

    st.caption(
        f"Hola, {st.session_state.nombre_trader}. "
        f"Tu centro de control de trading."
    )

    tabs = st.tabs([
        "➕ Registrar Trade",
        "📅 Track Record",
        "💬 Chat IA",
        "🧮 Calculadora",
        "🤖 Auditoría",
        "📈 Proyecciones",
        "📓 Psicotrading",
        "📊 Dashboard"
    ])

    with tabs[0]:

        render_tab_registrar(
            user_id,
            trades
        )

    with tabs[1]:

        render_tab_track_record(
            user_id,
            df
        )

    with tabs[2]:

        render_tab_chat(
            df
        )

    with tabs[3]:

        render_tab_lotaje()

    with tabs[4]:

        render_tab_auditoria()

    with tabs[5]:

        render_tab_proyecciones()

    with tabs[6]:

        render_tab_psicotrading()

    with tabs[7]:

        render_tab_dashboard(
            df
        )


# ============================================================
# 23. ARRANQUE
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
