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
# 2. CONFIGURACIÓN GENERAL
# ============================================================

# Binance
LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"

BINANCE_PAY_ID = "JORDAN_SANTI9"

# Telegram
LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"

# Stripe
# IMPORTANTE:
# Reemplaza estos enlaces cuando tengas creados tus Payment Links de Stripe.
LINK_STRIPE_MENSUAL = ""
LINK_STRIPE_ANUAL = ""

# Supabase
SUPABASE_URL = st.secrets.get(
    "SUPABASE_URL",
    "https://lyzvcbjpoydeckxtbcq.supabase.co"
)

SUPABASE_KEY = st.secrets.get(
    "SUPABASE_KEY",
    ""
)

# OpenRouter
OPENROUTER_API_KEY = st.secrets.get(
    "OPENROUTER_API_KEY",
    ""
)

# Email administrador
ADMIN_EMAIL = st.secrets.get(
    "ADMIN_EMAIL",
    "jordandanielpenarrietasantilla@gmail.com"
)


# ============================================================
# 3. CLIENTE SUPABASE
# ============================================================

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise Exception(
            "Faltan SUPABASE_URL o SUPABASE_KEY en los Secrets de Streamlit."
        )

    return create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ============================================================
# 4. ESTADO DE SESIÓN
# ============================================================

defaults = {
    "authenticated": False,
    "user": None,
    "chat_history": [],
    "nombre_trader": "Trader Pro",
    "capital_actual": 10000.0,
    "capital_meta": 15000.0,
    "reglas_disciplina": (
        "• Acepta la pérdida antes de entrar.\n"
        "• Corta pérdidas rápido.\n"
        "• Deja correr los ganadores.\n"
        "• Máximo 2 operaciones perdedoras por día."
    ),
    "auto_entry": 0.0,
    "auto_sl": 0.0,
    "auto_tp": 0.0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


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
# 6. PROCESAR IMÁGENES
# ============================================================

def procesar_imagen_b64(uploaded_file, max_size=(1200, 900)):
    if uploaded_file is None:
        return ""

    try:
        image = Image.open(uploaded_file)

        if image.mode != "RGB":
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

        return f"data:image/jpeg;base64,{encoded}"

    except Exception as e:
        st.error(f"Error procesando imagen: {e}")
        return ""


# ============================================================
# 7. BASE DE DATOS - CARGAR TRADES
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

        return response.data if response.data else []

    except Exception as e:

        st.error(
            "❌ Error cargando operaciones desde Supabase."
        )

        st.code(
            str(e),
            language="text"
        )

        return []


# ============================================================
# 8. GUARDAR TRADE
# ============================================================

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

        return True

    except Exception as e:

        st.error(
            "❌ Error guardando operación."
        )

        st.code(
            str(e),
            language="text"
        )

        return False


# ============================================================
# 9. ELIMINAR TRADE
# ============================================================

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
            "❌ Error eliminando operación."
        )

        st.code(
            str(e),
            language="text"
        )

        return False


# ============================================================
# 10. IA - ANALIZAR CAPTURA
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

Busca específicamente la herramienta de posición
Risk/Reward o los niveles de Entry, Stop Loss y Take Profit.

Devuelve ÚNICAMENTE JSON válido con esta estructura:

{
    "entry": 0.0,
    "sl": 0.0,
    "tp": 0.0
}

Reglas:
- entry debe ser el precio de entrada.
- sl debe ser el Stop Loss.
- tp debe ser el Take Profit.
- Si un dato no aparece claramente utiliza 0.0.
- No agregues explicaciones.
- No agregues markdown.
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
                            "url": (
                                "data:image/png;base64,"
                                + b64_img
                            )
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

        if response.status_code != 200:
            return None

        result = response.json()

        content = (
            result["choices"][0]["message"]["content"]
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
# 11. SUSCRIPCIÓN
# ============================================================

def evaluar_suscripcion(user):

    if not user:
        return False, "Sin sesión", 0

    user_email = (
        getattr(user, "email", "") or ""
    ).lower()

    # ADMIN
    if user_email == ADMIN_EMAIL.lower():

        return (
            True,
            "Creador / Admin 👑",
            99999
        )

    metadata = (
        getattr(user, "user_metadata", None)
        or {}
    )

    # VIP
    if metadata.get("es_vip", False):

        return (
            True,
            "Acceso PRO 💎",
            999
        )

    # SUSCRIPCIÓN MANUAL
    subscription_active = metadata.get(
        "subscription_active",
        False
    )

    if subscription_active:

        subscription_until = metadata.get(
            "subscription_until"
        )

        if subscription_until:

            try:

                expiration = (
                    datetime.date.fromisoformat(
                        subscription_until
                    )
                )

                days_remaining = (
                    expiration -
                    datetime.date.today()
                ).days

                if days_remaining >= 0:

                    return (
                        True,
                        "Acceso PRO 💎",
                        days_remaining
                    )

            except Exception:
                pass

    # PRUEBA
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
# 12. CSS
# ============================================================

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

        -webkit-text-fill-color:
        #00f2fe !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[role="listbox"] {

        background-color: #121721 !important;

        border: 1px solid
        #00f2fe !important;

        border-radius: 8px !important;
    }

    div[role="option"],
    li[role="option"] {

        background-color: #121721 !important;

        color: white !important;

        padding: 10px 14px !important;
    }

    div[role="option"]:hover,
    li[role="option"]:hover {

        background-color: #00f2fe !important;

        color: black !important;
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

    .stButton > button {

        background:
        linear-gradient(
            135deg,
            #00d2ff 0%,
            #2962ff 100%
        ) !important;

        color: white !important;

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

        border-right:
        1px solid
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

    .paywall-card {

        background-color: #161b22;

        border: 1px solid #f0b90b;

        border-radius: 12px;

        padding: 24px;

        text-align: center;

        box-shadow:
        0px 0px 20px
        rgba(240, 185, 11, 0.2);
    }

    </style>

    """

    st.markdown(
        css,
        unsafe_allow_html=True
    )


aplicar_estilos()


# ============================================================
# 13. PAYWALL
# ============================================================

def render_paywall():

    st.markdown(
        "## 🔒 Tu período de prueba de 3 días ha expirado"
    )

    st.markdown(
        """
        Continúa utilizando el **AI Trading Journal**
        para registrar tus operaciones, revisar tu Track Record
        y trabajar tu disciplina.
        """
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    # ========================================================
    # BINANCE
    # ========================================================

    with col1:

        st.markdown(
            """
            <div class="paywall-card">

            <h3>🟡 Binance Pay</h3>

            <h2>$5 USD</h2>

            <p>
            Suscripción mensual
            </p>

            <hr>

            <p>
            ✔️ Track Record<br>
            ✔️ Diario de trading<br>
            ✔️ Auditoría IA<br>
            ✔️ Psicotrading<br>
            ✔️ Calculadora de lotaje
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.link_button(
            "🟡 Pagar $5 USD con Binance Pay",
            LINK_BINANCE_INSCRIPCION,
            use_container_width=True
        )

    # ========================================================
    # TARJETA
    # ========================================================

    with col2:

        st.markdown(
            """
            <div class="paywall-card">

            <h3>💳 Tarjeta</h3>

            <h2>$5 USD</h2>

            <p>
            Débito o crédito
            </p>

            <hr>

            <p>
            ✔️ Visa<br>
            ✔️ Mastercard<br>
            ✔️ Métodos disponibles en Stripe<br>
            ✔️ Pago seguro
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        if LINK_STRIPE_MENSUAL:

            st.link_button(
                "💳 Pagar con Débito / Crédito",
                LINK_STRIPE_MENSUAL,
                use_container_width=True
            )

        else:

            st.warning(
                "Configura primero tu enlace de Stripe mensual."
            )

    st.markdown("---")

    # ========================================================
    # ANUAL
    # ========================================================

    st.markdown(
        "## 🚀 Plan Anual"
    )

    col3, col4 = st.columns(2)

    with col3:

        st.markdown(
            """
            <div class="paywall-card">

            <h3>💎 Binance — Anual</h3>

            <h2>$20 USD / año</h2>

            <p>
            Pago único
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.link_button(
            "💎 Pagar $20 con Binance Pay",
            LINK_BINANCE_ANUAL,
            use_container_width=True
        )

    with col4:

        st.markdown(
            """
            <div class="paywall-card">

            <h3>💳 Tarjeta — Anual</h3>

            <h2>$20 USD / año</h2>

            <p>
            Débito o crédito
            </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        if LINK_STRIPE_ANUAL:

            st.link_button(
                "💳 Pagar $20 con Tarjeta",
                LINK_STRIPE_ANUAL,
                use_container_width=True
            )

        else:

            st.warning(
                "Configura primero tu enlace de Stripe anual."
            )

    st.markdown("---")

    st.markdown(
        "### 📲 Activación después del pago"
    )

    st.code(
        f"Binance Pay ID: {BINANCE_PAY_ID}",
        language="text"
    )

    st.markdown(
        """
        Después de realizar el pago, envía el comprobante
        para activar tu cuenta.
        """
    )

    st.link_button(
        "💬 Enviar comprobante / Contactar soporte",
        LINK_TELEGRAM_SOPORTE,
        use_container_width=True
    )


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
            Audita tu operativa con Inteligencia Artificial,
            registra tus emociones y lleva tu disciplina
            al siguiente nivel.
            """
        )

        st.markdown(
            """
            ### Incluye

            🧠 Auditoría IA  
            📊 Track Record  
            📅 Calendario PnL  
            🧮 Calculadora de lotaje  
            📓 Psicotrading  
            📈 Proyecciones  
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

        # ====================================================
        # LOGIN
        # ====================================================

        with tab_login:

            st.markdown(
                "### Ingresa a tu Cuenta"
            )

            login_email = st.text_input(
                "Correo Electrónico",
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
                        "Completa correo y contraseña."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        response = (
                            client
                            .auth
                            .sign_in_with_password(
                                {
                                    "email": login_email,
                                    "password": login_pass
                                }
                            )
                        )

                        st.session_state.authenticated = True
                        st.session_state.user = response.user

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "❌ No se pudo iniciar sesión."
                        )

                        st.code(
                            str(e),
                            language="text"
                        )

        # ====================================================
        # REGISTRO
        # ====================================================

        with tab_register:

            st.markdown(
                "### Crea tu Cuenta"
            )

            reg_email = st.text_input(
                "Correo Electrónico",
                key="reg_email"
            )

            reg_pass = st.text_input(
                "Crea tu Contraseña",
                type="password",
                key="reg_pass"
            )

            if st.button(
                "Crear Cuenta y Probar",
                key="btn_reg"
            ):

                if not reg_email or not reg_pass:

                    st.warning(
                        "Completa todos los campos."
                    )

                elif len(reg_pass) < 6:

                    st.warning(
                        "La contraseña debe tener al menos 6 caracteres."
                    )

                else:

                    try:

                        client = get_supabase_client()

                        response = (
                            client
                            .auth
                            .sign_up(
                                {
                                    "email": reg_email,
                                    "password": reg_pass
                                }
                            )
                        )

                        st.success(
                            """
                            ✅ Registro exitoso.

                            Si Supabase solicita confirmación,
                            revisa tu correo electrónico.
                            """
                        )

                    except Exception as e:

                        st.error(
                            "❌ Error registrando usuario."
                        )

                        st.code(
                            str(e),
                            language="text"
                        )

        # ====================================================
        # RECUPERAR CONTRASEÑA
        # ====================================================

        with tab_reset:

            st.markdown(
                "### 🔐 Recupera tu Contraseña"
            )

            reset_email = st.text_input(
                "Correo Electrónico Registrado",
                key="reset_email"
            )

            if st.button(
                "Enviar Enlace de Recuperación",
                key="btn_reset"
            ):

                if not reset_email:

                    st.warning(
                        "Ingresa tu correo."
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
                            reset_email,
                            {
                                "redirectTo": app_url
                            }
                        )

                        st.success(
                            "📩 Revisa tu correo electrónico."
                        )

                    except Exception as e:

                        st.error(
                            "❌ Error enviando recuperación."
                        )

                        st.code(
                            str(e),
                            language="text"
                        )


# ============================================================
# 15. SIDEBAR
# ============================================================

def render_sidebar(estado_sub):

    with st.sidebar:

        st.markdown(
            "### 👤 Perfil Trader"
        )

        user = st.session_state.user

        user_email = (
            getattr(user, "email", None)
            or "trader@ejemplo.com"
        )

        metadata = (
            getattr(
                user,
                "user_metadata",
                None
            )
            or {}
        )

        nombre_actual = metadata.get(
            "username",
            "Trader Pro"
        )

        foto_b64 = metadata.get(
            "avatar_b64"
        )

        col_img, col_txt = st.columns(
            [1, 2]
        )

        with col_img:

            if foto_b64:

                st.markdown(
                    f"""
                    <img
                    src="data:image/png;base64,{foto_b64}"
                    style="
                    width:65px;
                    height:65px;
                    border-radius:50%;
                    object-fit:cover;
                    border:2px solid #00f2fe;
                    "
                    >
                    """,
                    unsafe_allow_html=True
                )

            else:

                st.markdown(
                    "👤",
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

        # ====================================================
        # PERFIL
        # ====================================================

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
                ]
            )

            if st.button(
                "Guardar Cambios"
            ):

                nueva_foto = foto_b64

                if foto_subida:

                    nueva_foto = base64.b64encode(
                        foto_subida.getvalue()
                    ).decode("utf-8")

                try:

                    client = get_supabase_client()

                    response = (
                        client
                        .auth
                        .update_user(
                            {
                                "data": {
                                    "username": input_nombre,
                                    "avatar_b64": nueva_foto
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
                        "Error actualizando perfil."
                    )

                    st.code(
                        str(e),
                        language="text"
                    )

        st.markdown("---")

        # ====================================================
        # META
        # ====================================================

        st.markdown(
            "### 🎯 Meta de Cuenta"
        )

        cap_act = st.session_state.capital_actual
        cap_met = st.session_state.capital_meta

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
            f"""
            **Capital:** ${cap_act:,.0f}

            **Meta:** ${cap_met:,.0f}
            """
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
                    step=500.0
                )
            )

            st.session_state.capital_meta = (
                st.number_input(
                    "Meta ($)",
                    value=float(cap_met),
                    step=1000.0
                )
            )

        st.markdown("---")

        # ====================================================
        # REGLAS
        # ====================================================

        st.markdown(
            "### 🎯 Mis Reglas"
        )

        with st.expander(
            "✏️ Editar Reglas"
        ):

            reglas = st.text_area(
                "Reglas",
                value=st.session_state.reglas_disciplina,
                height=150
            )

            if st.button(
                "Guardar Reglas"
            ):

                st.session_state.reglas_disciplina = reglas

                st.success(
                    "Reglas actualizadas."
                )

                st.rerun()

        st.markdown(
            st.session_state.reglas_disciplina
        )

        st.markdown("---")

        # ====================================================
        # LOGOUT
        # ====================================================

        if st.button(
            "🚪 Cerrar Sesión"
        ):

            try:

                client = get_supabase_client()
                client.auth.sign_out()

            except Exception:
                pass

            st.session_state.authenticated = False
            st.session_state.user = None

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

    user_id = st.session_state.user.id

    trades_db = cargar_trades_usuario(
        user_id
    )

    df_trades = pd.DataFrame(
        trades_db
    )

    if df_trades.empty:

        df_trades = pd.DataFrame(
            columns=[
                "id",
                "fecha",
                "par",
                "resultado",
                "emocion",
                "beneficio_usd",
                "trades_cant",
                "img_before",
                "img_after",
                "direccion",
                "precio_entrada",
                "stop_loss",
                "take_profit",
                "rr",
                "timeframe",
                "notas_emocionales"
            ]
        )

    st.markdown(
        "## ⚡ Journaling & AI Trading Audit"
    )

    tabs = st.tabs(
        [
            "➕ Registrar Trade",
            "📅 Track Record PnL",
            "💬 Chat IA",
            "🧮 Lotaje",
            "🤖 Auditoría IA",
            "📈 Proyecciones",
            "📓 Psicotrading",
            "📊 Dashboard"
        ]
    )

    # ========================================================
    # TAB 1
    # ========================================================

    with tabs[0]:

        st.info(
            """
            💡 Sube una captura de TradingView.
            La IA puede intentar detectar Entry,
            Stop Loss y Take Profit.
            """
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
                    "jpeg"
                ],
                key="upload_before"
            )

            upload_after = st.file_uploader(
                "2️⃣ Screenshot DESPUÉS",
                type=[
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="upload_after"
            )

            img_before_b64 = ""

            img_after_b64 = ""

            if upload_before:

                bytes_b = (
                    upload_before.getvalue()
                )

                img_before_b64 = (
                    procesar_imagen_b64(
                        upload_before
                    )
                )

                st.image(
                    upload_before,
                    caption="SETUP — ANTES",
                    use_container_width=True
                )

                if st.button(
                    "🧠 Escanear SETUP con IA"
                ):

                    with st.spinner(
                        "Analizando gráfico..."
                    ):

                        extracted = (
                            analizar_captura_tradingview(
                                bytes_b
                            )
                        )

                    if extracted:

                        st.session_state.auto_entry = (
                            float(
                                extracted.get(
                                    "entry",
                                    0
                                )
                            )
                        )

                        st.session_state.auto_sl = (
                            float(
                                extracted.get(
                                    "sl",
                                    0
                                )
                            )
                        )

                        st.session_state.auto_tp = (
                            float(
                                extracted.get(
                                    "tp",
                                    0
                                )
                            )
                        )

                        st.success(
                            "Valores detectados."
                        )

                        st.rerun()

                    else:

                        st.warning(
                            "La IA no pudo detectar los valores."
                        )

            if upload_after:

                img_after_b64 = (
                    procesar_imagen_b64(
                        upload_after
                    )
                )

                st.image(
                    upload_after,
                    caption="RESULTADO — DESPUÉS",
                    use_container_width=True
                )

            monto_pnl = st.number_input(
                "Ganancia / Pérdida ($)",
                value=0.0,
                step=10.0
            )

        with col1:

            fecha_op = st.date_input(
                "Fecha",
                datetime.date.today()
            )

            par = st.selectbox(
                "Activo / Par",
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
                    "FOMO 🚀",
                    "Venganza / Frustrado 🛑",
                    "Eufórico / Sobre-confiado 😎"
                ]
            )

            notas_emocionales = st.text_area(
                "Notas emocionales",
                placeholder=(
                    "¿Respetaste tu plan?"
                )
            )

            if st.button(
                "💾 Guardar Trade",
                key="save_trade"
            ):

                nuevo_trade = {

                    "fecha": str(
                        fecha_op
                    ),

                    "par": par,

                    "resultado": resultado,

                    "emocion": emocion,

                    "beneficio_usd": float(
                        monto_pnl
                    ),

                    "trades_cant": 1,

                    "img_before": (
                        img_before_b64
                    ),

                    "img_after": (
                        img_after_b64
                    ),

                    "direccion": direccion,

                    "precio_entrada": float(
                        precio_entrada
                    ),

                    "stop_loss": float(
                        stop_loss
                    ),

                    "take_profit": float(
                        take_profit
                    ),

                    "rr": float(rr),

                    "timeframe": timeframe,

                    "notas_emocionales": (
                        notas_emocionales
                    )
                }

                if guardar_trade_supabase(
                    user_id,
                    nuevo_trade
                ):

                    st.session_state.auto_entry = 0
                    st.session_state.auto_sl = 0
                    st.session_state.auto_tp = 0

                    st.success(
                        "✅ Trade guardado."
                    )

                    st.rerun()

    # ========================================================
    # TAB 2
    # ========================================================

    with tabs[1]:

        st.markdown(
            "### 📅 Track Record & PnL"
        )

        if not df_trades.empty:

            df_trades["beneficio_usd"] = pd.to_numeric(
                df_trades["beneficio_usd"],
                errors="coerce"
            ).fillna(0)

            total_pnl = (
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

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "PnL",
                f"${total_pnl:,.2f}"
            )

            c2.metric(
                "Wins",
                wins
            )

            c3.metric(
                "Losses",
                losses
            )

            c4.metric(
                "Trades",
                len(df_trades)
            )

            st.markdown("---")

            st.markdown(
                "### 📋 Historial"
            )

            for _, row in df_trades.iterrows():

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
                            "#### Detalles"
                        )

                        st.write(
                            f"**Dirección:** "
                            f"{row.get('direccion', '-')}"
                        )

                        st.write(
                            f"**Entry:** "
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
                            f"1:{row.get('rr', 0)}"
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
                            f"${pnl:,.2f}"
                        )

                        notas = row.get(
                            "notas_emocionales"
                        )

                        if notas:

                            st.write(
                                f"**Notas:** {notas}"
                            )

                        if st.button(
                            "🗑️ Eliminar",
                            key=f"delete_{trade_id}"
                        ):

                            if eliminar_trade_supabase(
                                trade_id
                            ):

                                st.success(
                                    "Trade eliminado."
                                )

                                st.rerun()

                    with c2:

                        st.markdown(
                            "**1️⃣ ANTES**"
                        )

                        img = row.get(
                            "img_before"
                        )

                        if img:

                            st.image(
                                img,
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "Sin captura."
                            )

                    with c3:

                        st.markdown(
                            "**2️⃣ DESPUÉS**"
                        )

                        img = row.get(
                            "img_after"
                        )

                        if img:

                            st.image(
                                img,
                                use_container_width=True
                            )

                        else:

                            st.caption(
                                "Sin captura."
                            )

            st.markdown("---")

            df_chart = (
                df_trades
                .groupby("fecha")
                .agg(
                    {
                        "beneficio_usd": "sum"
                    }
                )
                .reset_index()
            )

            fig = px.bar(
                df_chart,
                x="fecha",
                y="beneficio_usd",
                title="PnL Diario",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "Todavía no tienes operaciones."
            )

    # ========================================================
    # TAB 3
    # ========================================================

    with tabs[2]:

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
            "Pregúntame sobre tu trading..."
        )

        if prompt:

            st.session_state.chat_history.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )

            with st.chat_message(
                "user"
            ):

                st.markdown(
                    prompt
                )

            if df_trades.empty:

                respuesta = (
                    "Todavía no tienes suficientes "
                    "operaciones registradas."
                )

            else:

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

                total = len(
                    df_trades
                )

                win_rate = (
                    wins / total * 100
                )

                respuesta = f"""
### 🧠 Auditoría rápida

Has registrado **{total} operaciones**.

**PnL acumulado:** ${pnl:,.2f}

**Win Rate:** {win_rate:.1f}%

Mi recomendación principal es que no evalúes
solamente el porcentaje de aciertos.

También debemos analizar:

- Riesgo por operación.
- RR promedio.
- FOMO.
- Venganza.
- Operaciones fuera de horario.
- Cumplimiento de tus reglas.
"""

            with st.chat_message(
                "assistant"
            ):

                st.markdown(
                    respuesta
                )

            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": respuesta
                }
            )

    # ========================================================
    # TAB 4
    # ========================================================

    with tabs[3]:

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
            "Riesgo (%)",
            value=1.0,
            step=0.25
        )

        stop = st.number_input(
            "Stop Loss en puntos/pips",
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
            / (stop * 10)
            if stop > 0
            else 0
        )

        st.metric(
            "Riesgo máximo",
            f"${riesgo_usd:,.2f}"
        )

        st.metric(
            "Lotaje estimado",
            f"{lotaje:.2f}"
        )

        st.warning(
            """
            ⚠️ Esta equivalencia es una estimación
            para Forex estándar. En XAU/USD, índices,
            criptomonedas y acciones debes utilizar
            la especificación real del contrato de tu broker.
            """
        )

    # ========================================================
    # TAB 5
    # ========================================================

    with tabs[4]:

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
            key="visual_audit"
        )

        if chart:

            st.image(
                chart,
                use_container_width=True
            )

            if st.button(
                "🔍 Auditar con IA"
            ):

                with st.spinner(
                    "Analizando estructura..."
                ):

                    result = analizar_captura_tradingview(
                        chart.getvalue()
                    )

                if result:

                    st.success(
                        "Lectura de niveles completada."
                    )

                    st.json(
                        result
                    )

                else:

                    st.warning(
                        "No se pudo analizar la imagen."
                    )

    # ========================================================
    # TAB 6
    # ========================================================

    with tabs[5]:

        st.markdown(
            "### 📈 Proyección de Capital"
        )

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

        avg_win = st.number_input(
            "Ganancia promedio WIN ($)",
            value=200.0,
            step=25.0
        )

        avg_loss = st.number_input(
            "Pérdida promedio LOSS ($)",
            value=100.0,
            step=25.0
        )

        capital = (
            st.session_state.capital_actual
        )

        rows = []

        for month in range(1, 13):

            winners = (
                trades_mes
                * win_rate
                / 100
            )

            losers = (
                trades_mes
                - winners
            )

            pnl = (
                winners * avg_win
                - losers * avg_loss
            )

            capital += pnl

            rows.append(
                {
                    "Mes": f"Mes {month}",
                    "Capital": capital
                }
            )

        df_projection = pd.DataFrame(
            rows
        )

        st.metric(
            "Capital proyectado",
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

    # ========================================================
    # TAB 7
    # ========================================================

    with tabs[6]:

        st.markdown(
            "### 📓 Diario de Psicotrading"
        )

        st.text_area(
            "Reflexión",
            height=200,
            placeholder=(
                "¿Qué hiciste bien? "
                "¿Dónde fallaste? "
                "¿Sentiste FOMO? "
                "¿Respetaste el SL?"
            )
        )

        if st.button(
            "💾 Guardar Reflexión"
        ):

            st.success(
                "Reflexión guardada durante esta sesión."
            )

    # ========================================================
    # TAB 8
    # ========================================================

    with tabs[7]:

        st.markdown(
            "### 📊 Dashboard"
        )

        total = len(
            df_trades
        )

        if total > 0:

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

            win_rate = (
                wins / total * 100
            )

        else:

            pnl = 0
            wins = 0
            losses = 0
            win_rate = 0

        c1, c2, c3, c4 = st.columns(4)

        c1.metric(
            "PnL Total",
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
            "Wins",
            wins
        )

        if not df_trades.empty:

            st.markdown(
                "### 📊 Rendimiento por activo"
            )

            df_asset = (
                df_trades
                .groupby("par")
                .agg(
                    {
                        "beneficio_usd": "sum"
                    }
                )
                .reset_index()
            )

            fig = px.bar(
                df_asset,
                x="par",
                y="beneficio_usd",
                template="plotly_dark",
                title="PnL por Activo"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.dataframe(
                df_trades[
                    [
                        "fecha",
                        "par",
                        "direccion",
                        "resultado",
                        "beneficio_usd",
                        "emocion",
                        "timeframe"
                    ]
                ],
                use_container_width=True,
                hide_index=True
            )


# ============================================================
# 17. INICIO DE APP
# ============================================================

if not st.session_state.authenticated:

    render_auth()

else:

    render_dashboard()
