import streamlit as st
import datetime
import requests
import json
import os
import base64
import pandas as pd
import numpy as np
import plotly.express as px
import calendar
from supabase import create_client, Client

# ==========================================
# 1. CONFIGURACIÓN Y ENLACES REALES DE BINANCE PAY
# ==========================================
st.set_page_config(
    page_title="AI Trading Journal & Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔗 ENLACES DE BINANCE PAY
LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"  # $5 USDT
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"        # $20 USDT
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"   # $2.50 USDT

BINANCE_PAY_ID = "JORDAN_SANTI9"
LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://lyzvcbjpoydeckxtbcq.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_HIo0YXn-kJUr7HuNZFNfjQ_JBncowE0")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Estado de sesión
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
    st.session_state.reglas_disciplina = "• Acepta la pérdida antes de entrar.\n• Corta pérdidas rápido.\n• Deja correr los ganadores.\n• Máximo 2 operaciones perdedoras por día."

# Variables autocompletadas por la IA
if "auto_entry" not in st.session_state:
    st.session_state.auto_entry = 0.0
if "auto_sl" not in st.session_state:
    st.session_state.auto_sl = 0.0
if "auto_tp" not in st.session_state:
    st.session_state.auto_tp = 0.0

# ==========================================
# LISTA COMPLETA DE ACTIVOS FINANCIEROS
# ==========================================
LISTA_ACTIVOS = [
    # --- MATERIAS PRIMAS ---
    "🥇 XAU/USD (Oro)",
    "🥈 XAG/USD (Plata)",
    "🛢️ USOIL (Petróleo WTI)",
    "🛢️ UKOIL (Petróleo Brent)",
    "🌾 NGAS (Gas Natural)",
    
    # --- CRIPTOMONEDAS ---
    "🪙 BTC/USD (Bitcoin)",
    "🪙 ETH/USD (Ethereum)",
    "🪙 SOL/USD (Solana)",
    "🪙 XRP/USD (Ripple)",
    "🪙 BNB/USD (Binance Coin)",
    "🪙 ADA/USD (Cardano)",
    "🪙 DOGE/USD (Dogecoin)",
    "🪙 AVAX/USD (Avalanche)",
    
    # --- ÍNDICES ---
    "📊 US100 (Nasdaq 100)",
    "📊 US30 (Dow Jones)",
    "📊 US500 (S&P 500)",
    "📊 GER40 (Dax Alemán)",
    "📊 UK100 (FTSE 100)",
    "📊 JP225 (Nikkei 225)",
    
    # --- FOREX (DIVISAS MAJORS Y MINORS) ---
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
    "🛢️ AUD/JPY",
    "🛢️ CAD/JPY",
    "💱 EUR/AUD",
    "💱 GBP/AUD",
    
    # --- ACCIONES ---
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

# ==========================================
# FUNCIONES DE BASE DE DATOS Y VISION IA
# ==========================================
def cargar_trades_usuario(user_id):
    try:
        client = get_supabase_client()
        res = client.table("trades").select("*").eq("user_id", user_id).execute()
        return res.data if res.data else []
    except Exception:
        return []

def guardar_trade_supabase(user_id, trade_data):
    try:
        client = get_supabase_client()
        trade_data["user_id"] = user_id
        client.table("trades").insert(trade_data).execute()
        return True
    except Exception as e:
        st.error(f"Error guardando en base de datos: {e}")
        return False

def analizar_captura_tradingview(image_bytes):
    """Extrae Entrada, SL y TP de una foto de TradingView usando IA."""
    if not OPENROUTER_API_KEY:
        return None
    
    b64_img = base64.b64encode(image_bytes).decode("utf-8")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = """Analiza este gráfico de TradingView. Extrae los valores numéricos de la herramienta de posición (Risk/Reward):
    Devuelve ÚNICAMENTE un JSON con estas claves exactas:
    {"entry": float, "sl": float, "tp": float}
    Si no encuentras algún dato pon 0.0. No agregues texto extra."""

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_img}"}}
                ]
            }
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        res_json = response.json()
        content = res_json["choices"][0]["message"]["content"]
        
        content_clean = content.replace("```json", "").replace("```", "").strip()
        data = json.loads(content_clean)
        return data
    except Exception:
        return None

# ==========================================
# 2. ESTILOS CSS PERSONALIZADOS (CORRECCIÓN TOTAL DE DESPLEGABLES)
# ==========================================
def aplicar_estilos():
    css = """
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    p, label, h1, h2, h3, h4, span, div, .stMarkdown {
        color: #f0f3fa !important;
    }

    h1, h2 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* === SOLUCIÓN DEFINITIVA PARA MENÚS DESPLEGABLES BLANCOS (SELECTBOX) === */
    /* Caja del selector cerrado */
    div[data-baseweb="select"] > div {
        background-color: #121721 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.5) !important;
        border-radius: 8px !important;
    }

    /* Input de búsqueda dentro del selector */
    div[data-baseweb="select"] input {
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
    }

    /* Texto seleccionado */
    div[data-baseweb="select"] span[data-testid="stMarkdownContainer"] p {
        color: #00f2fe !important;
    }

    /* === ESTILO DEL MENÚ FLOTANTE (EL DESPLEGABLE EN SÍ) === */
    div[data-baseweb="popover"], 
    div[data-baseweb="menu"], 
    div[role="listbox"],
    ul[role="listbox"] {
        background-color: #121721 !important; /* Fondo azul oscuro nítido */
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }

    /* Elementos individuales de la lista */
    div[role="option"],
    li[role="option"],
    li[data-baseweb="option"] {
        background-color: #121721 !important; /* Fondo oscuro */
        color: #ffffff !important; /* Letras blancas para lectura */
        font-family: 'Segoe UI', sans-serif !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
    }

    /* Hover o elemento resaltado al pasar el mouse */
    div[role="option"]:hover,
    li[role="option"]:hover,
    li[aria-selected="true"] {
        background-color: #00f2fe !important; /* Fondo cian brillante */
        color: #000000 !important; /* Texto negro para contraste máximo */
        font-weight: bold !important;
    }

    /* Fix para el icono de la flecha */
    div[data-baseweb="select"] svg {
        fill: #00f2fe !important;
    }

    /* === FIN SOLUCIÓN DESPLEGABLES === */

    /* Entradas de texto y números normales */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 8px !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border-radius: 12px !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
    }

    .stButton>button {
        background: linear-gradient(135deg, #00d2ff 0%, #2962ff 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
        box-shadow: 0px 4px 15px rgba(0, 210, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0, 210, 255, 0.2) !important;
    }

    section[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg, #e53935 0%, #b71c1c 100%) !important;
        box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.3) !important;
    }

    .market-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .open { background-color: rgba(76, 175, 80, 0.2); color: #4caf50; border: 1px solid #4caf50; }
    .closed { background-color: rgba(244, 67, 54, 0.2); color: #f44336; border: 1px solid #f44336; }

    .paywall-card {
        background-color: #161b22;
        border: 1px solid #f0b90b;
        border-radius: 12px;
        padding: 24px;
        text-align: center;
        box-shadow: 0px 0px 20px rgba(240, 185, 11, 0.2);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos()

# ==========================================
# 3. VERIFICACIÓN DE DÍAS DE PRUEBA / PRO / ADMIN
# ==========================================
def evaluar_suscripcion(user):
    user_email = user.email if (user and hasattr(user, 'email')) else ""
    
    if user_email.lower() == "jordandanielpenarrietasantilla@gmail.com":
        return True, "Creador / Admin 👑", 99999

    metadata = user.user_metadata if (user and hasattr(user, 'user_metadata') and user.user_metadata) else {}
    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999

    created_at_str = str(user.created_at) if hasattr(user, 'created_at') else None
    if created_at_str:
        fecha_registro = datetime.datetime.strptime(created_at_str[:10], "%Y-%m-%d").date()
    else:
        fecha_registro = datetime.date.today()

    dias_usados = (datetime.date.today() - fecha_registro).days
    dias_restantes = max(0, 3 - dias_usados)

    if dias_usados <= 3:
        return True, f"Prueba Gratis ({dias_restantes} días rest.)", dias_restantes
    else:
        return False, "Prueba Expirada 🛑", 0

# ==========================================
# 4. PANTALLA DE BLOQUEO / PAYWALL
# ==========================================
def render_paywall():
    st.markdown("## 🔒 Tu Período de Prueba Gratis de 3 Días ha Expirado")
    st.markdown("Para continuar auditando tus operaciones con IA y registrando tu Track Record Pro, activa tu acceso Pro mediante **Binance Pay**:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="paywall-card">
            <h3 style="color:#f0b90b;">🟡 Suscripción Mensual</h3>
            <h2 style="color:#ffffff;">$5.00 USD <span style="font-size:1rem; color:#aaa;">/ mes</span></h2>
            <p style="color:#00f2fe; font-weight:bold;">luego solo $2.50 USD / mes (¡50% OFF!)</p>
            <hr style="border-color:#333;">
            <ul style="text-align:left; color:#b0b8c4; font-size:0.95rem; line-height: 1.8;">
                <li>✔️ Acceso ilimitado a todas las funciones</li>
                <li>✔️ Track Record Calendario PnL ilimitado</li>
                <li>✔️ Chat & Auditoría Visual con IA ilimitada</li>
                <li>✔️ Sin contratos ni cobros automáticos</li>
            </ul>
            <br>
            <a href="{LINK_BINANCE_INSCRIPCION}" target="_blank">
                <button style="background:linear-gradient(135deg, #f0b90b 0%, #f39c12 100%); color:black; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                    🟡 Pagar $5 USD con Binance Pay
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="paywall-card">
            <h3 style="color:#00f2fe;">🚀 Acceso Anual</h3>
            <h2 style="color:#ffffff;">$20.00 USD <span style="font-size:1rem; color:#aaa;">/ año</span></h2>
            <p style="color:#00f2fe; font-weight:bold;">¡Ahorra un 60% vs suscripción mensual!</p>
            <hr style="border-color:#333;">
            <ul style="text-align:left; color:#b0b8c4; font-size:0.95rem; line-height: 1.8;">
                <li>🌟 <b>Acceso ilimitado por 1 Año Completo</b></li>
                <li>🔒 Pago único sin cobros automáticos</li>
                <li>🎁 Actualizaciones futuras incluidas</li>
                <li>🧠 Respuestas de IA prioritarias</li>
            </ul>
            <br>
            <a href="{LINK_BINANCE_ANUAL}" target="_blank">
                <button style="background:linear-gradient(135deg, #00f2fe 0%, #4facfe 100%); color:black; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                    💎 Pagar $20 USD con Binance Pay
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_info = st.columns(2)
    with col_info[0]:
        st.markdown("### 📲 Pago Directo / Renovaciones")
        st.code(f"Binance Pay ID: {BINANCE_PAY_ID}", language="text")
        st.markdown(f"👉 [Enlace directo de Renovación Mensual ($2.50 USDT)]({LINK_BINANCE_RECURRENTE})")

    with col_info[1]:
        st.markdown("### ✈️ Confirmar Pago y Activar Cuenta")
        st.markdown(f"""
        <a href="{LINK_TELEGRAM_SOPORTE}" target="_blank">
            <button style="background:linear-gradient(135deg, #0088cc 0%, #005580 100%); color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                💬 Enviar Comprobante / Contactar Soporte
            </button>
        </a>
        """, unsafe_allow_html=True)

# ==========================================
# 5. AUTENTICACIÓN (CON RECUPERACIÓN DE CLAVE)
# ==========================================
def render_auth():
    col = st.columns([1.2, 1])

    with col[0]:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")

    with col[1]:
        tab_login, tab_register, tab_reset = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse", "🔐 Recuperar Clave"])

        with tab_login:
            st.markdown("### Ingresa a tu Cuenta")
            login_email = st.text_input("Correo Electrónico", key="login_email")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            
            if st.button("Ingresar", key="btn_login"):
                if login_email and login_pass:
                    try:
                        client = get_supabase_client()
                        res = client.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                        st.session_state.authenticated = True
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error al iniciar sesión: {err}")

        with tab_register:
            st.markdown("### Crea tu Cuenta (3 Días Gratis)")
            reg_email = st.text_input("Correo Electrónico", key="reg_email")
            reg_pass = st.text_input("Crea tu Contraseña", type="password", key="reg_pass")
            
            if st.button("Crear Cuenta y Probar", key="btn_reg"):
                if reg_email and reg_pass:
                    try:
                        client = get_supabase_client()
                        res = client.auth.sign_up({"email": reg_email, "password": reg_pass})
                        st.success("¡Registro exitoso! Ahora puedes iniciar sesión.")
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")

        with tab_reset:
            st.markdown("### 🔐 Recupera tu Contraseña")
            st.caption("Ingresa tu correo electrónico registrado y te enviaremos un enlace de recuperación.")
            reset_email = st.text_input("Correo Electrónico Registrado", key="reset_email")
            
            if st.button("Enviar Enlace de Recuperación", key="btn_reset"):
                if reset_email:
                    try:
                        client = get_supabase_client()
                        # URL de tu app en Streamlit Cloud
                        app_url = "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                        # Esta función envía un correo de Supabase con un link que redirige a tu app
                        client.auth.reset_password_for_email(reset_email, {"redirectTo": app_url})
                        st.success("📩 Se ha enviado un enlace de recuperación a tu correo electrónico. Revisa tu bandeja de entrada o Spam.")
                    except Exception as e:
                        st.error(f"Error al solicitar recuperación: {e}")
                else:
                    st.warning("Por favor ingresa tu correo electrónico.")

# ==========================================
# 6. SIDEBAR COMPLETO RESTAURADO Y MEJORADO
# ==========================================
def render_sidebar(estado_sub):
    with st.sidebar:
        st.markdown("### 👤 Perfil Trader Pro")
        
        # Recuperamos datos del usuario autenticado
        user = st.session_state.user
        user_email = user.email if user else "trader@ejemplo.com"
        # Supabase guarda metadatos en user_metadata
        metadata = user.user_metadata if (user and hasattr(user, 'user_metadata') and user.user_metadata) else {}
        # Nombre y avatar_b64 (foto) guardados previamente
        nombre_actual = metadata.get("username", st.session_state.get("nombre_trader", "Trader Pro"))
        foto_b64 = metadata.get("avatar_b64", None)

        col_img, col_txt = st.columns([1, 2])
        with col_img:
            if foto_b64:
                st.markdown(f'<img src="data:image/png;base64,{foto_b64}" style="width:65px; height:65px; border-radius:50%; object-fit:cover; border:2px solid #00f2fe;">', unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:2.5rem; text-align:center;'>👤</div>", unsafe_allow_html=True)
                
        with col_txt:
            st.markdown(f"**{nombre_actual}**")
            st.caption(f"`{user_email}`")

        # Estado de suscripción llamativo
        if "PRO" in estado_sub or "Admin" in estado_sub:
            st.success(f"💎 {estado_sub}")
        else:
            st.warning(f"⏳ {estado_sub}")

        # Botón desplegable para editar perfil dentro de Supabase
        with st.expander("⚙️ Modificar Perfil Pro"):
            input_nombre = st.text_input("Nombre de Usuario Pro", value=nombre_actual)
            foto_subida = st.file_uploader("Seleccionar nueva foto Pro", type=["jpg", "jpeg", "png", "webp"])
            
            if st.button("Guardar Cambios Pro"):
                nueva_foto_b64 = foto_b64
                if foto_subida is not None:
                    # Leemos los bytes y los convertimos a Base64 para guardarlo en Supabase
                    bytes_data = foto_subida.getvalue()
                    nueva_foto_b64 = base64.b64encode(bytes_data).decode("utf-8")
                
                try:
                    client = get_supabase_client()
                    # Actualizamos user_metadata en la autenticación de Supabase
                    res = client.auth.update_user({
                        "data": {
                            "username": input_nombre,
                            "avatar_b64": nueva_foto_b64
                        }
                    })
                    # Actualizamos el estado de sesión y mostramos éxito
                    st.session_state.user = res.user
                    st.session_state.nombre_trader = input_nombre # Mantenemos retrocompatibilidad
                    st.toast("¡Perfil Pro guardado exitosamente!", icon="✅")
                    st.rerun() # Recargamos para ver los cambios
                except Exception as e:
                    st.error(f"Error al guardar perfil Pro: {e}")

        st.markdown("---")

        # Meta de Cuenta (Widget llamativo Pro)
        st.markdown("### 🎯 Meta de Cuenta Pro")
        cap_act = st.session_state.capital_actual
        cap_met = st.session_state.capital_meta
        progreso = min(1.0, max(0.0, cap_act / cap_met)) if cap_met > 0 else 0.0
        st.markdown(f"**Capital Pro:** `${cap_act:,.0f}` / `${cap_met:,.0f}`")
        st.progress(progreso)

        # Configuraciones adicionales (Expander Pro)
        with st.expander("🔧 Configuración Meta Pro"):
            st.session_state.capital_actual = st.number_input("Capital Actual Pro ($)", value=float(cap_act), step=500.0)
            st.session_state.capital_meta = st.number_input("Meta Capital Pro ($)", value=float(cap_met), step=1000.0)

        st.markdown("---")

        # Sesiones de Mercado (Mejorado con Hora Local Pro)
        st.markdown("### ⏰ Hora Local Pro & Sesiones Pro")
        # Widget HTML/JS para reloj local en vivo
        st.components.v1.html(
            """
            <div id="clock" style="
                font-family: 'Segoe UI', monospace;
                font-size: 18px;
                font-weight: bold;
                color: #00f2fe;
                background-color: #161b22;
                border: 1px solid rgba(0, 210, 255, 0.4);
                border-radius: 8px;
                padding: 6px;
                text-align: center;
            ">00:00:00</div>

            <script>
            function updateClock() {
                var now = new Date();
                var timeString = now.toLocaleTimeString();
                document.getElementById('clock').innerHTML = timeString + " (Local Pro)";
            }
            setInterval(updateClock, 1000);
            updateClock(); // Carga inicial
            </script>
            """,
            height=50
        )

        # Sesiones (Comparación UTC básica Pro)
        hora_utc = datetime.datetime.utcnow().hour
        londres_status = '<span class="market-badge open">ABIERTO</span>' if 7 <= hora_utc <= 15 else '<span class="market-badge closed">CERRADO</span>'
        ny_status = '<span class="market-badge open">ABIERTO</span>' if 12 <= hora_utc <= 20 else '<span class="market-badge closed">CERRADO</span>'

        st.markdown(f"**Londres Pro:** {londres_status}", unsafe_allow_html=True)
        st.markdown(f"**N. York Pro:** {ny_status}", unsafe_allow_html=True)

        st.markdown("---")

        # Reglas de Disciplina (Expandible Pro)
        st.markdown("### 🎯 Mis Reglas Pro")
        with st.expander("✏️ Editar Reglas Pro"):
            input_reglas = st.text_area("Reglas Pro personalizadas:", value=st.session_state.reglas_disciplina, height=150)
            if st.button("Guardar Reglas Pro"):
                st.session_state.reglas_disciplina = input_reglas
                st.toast("¡Reglas Pro actualizadas!", icon="✅")
                st.rerun()

        # Mostramos las reglas actuales Pro
        st.markdown(st.session_state.reglas_disciplina)

        st.markdown("---")

        # Botón de Cerrar Sesión Pro (Supabase Pro)
        if st.button("🚪 Cerrar Sesión Pro", secondary="true"):
            client = get_supabase_client()
            client.auth.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# ==========================================
# 7. DASHBOARD PRINCIPAL Y TODAS LAS PESTAÑAS INTERACTIVAS
# ==========================================
def render_dashboard():
    # Evaluamos suscripción del usuario autenticado Pro
    tiene_acceso, estado_sub, dias_restantes = evaluar_suscripcion(st.session_state.user)
    
    # Mostramos Sidebar Pro siempre
    render_sidebar(estado_sub)

    if not tiene_acceso:
        # Si no tiene acceso Pro (prueba expirada), mostramos Paywall y bloqueamos Pro
        render_paywall()
        return

    # Si tiene acceso Pro, mostramos todo el Dashboard Pro
    st.markdown("## ⚡ Diario Pro y Auditoría Pro")

    # Recuperamos los trades guardados del usuario en Supabase Pro
    user_id = st.session_state.user.id
    trades_db = cargar_trades_usuario(user_id)
    # Convertimos a DataFrame para métricas y gráficos Pro
    df_trades = pd.DataFrame(trades_db)

    # Definimos las pestañas principales Pro
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["➕ Registrar Pro", "📅 Record PnL Pro", "💬 Chat IA Pro", "🧮 Calc. Lotaje Pro", "🧠 Análisis Pro vs IA", "📈 Proyecciones Pro", "📓 Diario Pro", "📊 Dashboard Pro"])

    # --- PESTAÑA 1: REGISTRAR TRADE PRO ---
    with tab1:
        st.info("💡 **Consejo Pro:** Al subir una captura de TradingView con la herramienta de Posición, la IA escaneará la imagen y **autocompletará** tus precios Pro.")
        
        col1, col2 = st.columns([1.2, 1])

        with col2:
            st.markdown("### 🖼️ Capturas Pro")
            upload_before = st.file_uploader("Screenshot ANTES Pro (IA Escaneo Pro)", type=["png", "jpg", "jpeg"])
            upload_after = st.file_uploader("Screenshot DESPUÉS Pro", type=["png", "jpg", "jpeg"])

            if upload_before:
                st.image(upload_before, caption="Trade SETUP Pro (Antes)", use_container_width=True)
                
                # Botón de escaneo Pro con IA Pro
                if st.button("🧠 Escanear SETUP Pro con IA Pro"):
                    with st.spinner("La IA Pro está leyendo los valores numéricos Pro del gráfico Pro..."):
                        extracted = analizar_captura_tradingview(upload_before.getvalue())
                        if extracted:
                            # Actualizamos variables en session_state Pro
                            st.session_state.auto_entry = extracted.get("entry", 0.0)
                            st.session_state.auto_sl = extracted.get("sl", 0.0)
                            st.session_state.auto_tp = extracted.get("tp", 0.0)
                            st.toast("¡Valores Pro extraídos con éxito!", icon="✨")
                            st.rerun()
                        else:
                            st.warning("La IA Pro no pudo extraer los números Pro. Inténtalo Pro manualmente.")

            monto_pnl = st.number_input("Ganancia Pro / Pérdida Pro Pro USD:", value=0.0, step=10.0)

        with col1:
            st.markdown("### 📝 Parámetros Pro")
            # Autocompletado Pro
            fecha_op = st.date_input("Fecha Pro Operación", datetime.date.today())
            
            sub_col1, sub_col2 = st.columns(2)
            with sub_col1:
                par = st.selectbox("Activo / Par Pro", ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD", "US100 (Nasdaq)"])
                direccion = st.radio("Dirección Pro", ["LONG Pro", "SHORT Pro"], horizontal=True)
                precio_entrada = st.number_input("Precio Entrada Pro", value=st.session_state.auto_entry, format="%.5f")
                stop_loss = st.number_input("Stop Loss Pro", value=st.session_state.auto_sl, format="%.5f")
            
            with sub_col2:
                # Basic check, Basic check 基本 Basic check Basic Basic Basic Check check basic Check Basic basic basic basic basic Basic Basic check basic check basic Check Basic Basic basic
                # Ratio Pro Risk:Reward basic calculation basic check Pro
                precio_entrada_rr = st.session_state.auto_entry if st.session_state.auto_entry > 0 else (precio_entrada if precio_entrada > 0 else 0.00000000001)
                take_profit = st.number_input("Take Profit Pro", value=st.session_state.auto_tp, format="%.5f")
                riesgo = abs(precio_entrada - stop_loss)
                beneficio = abs(take_profit - precio_entrada)
                rr = beneficio / riesgo if riesgo > 0 else 0
                
                st.markdown(f"**Ratio Pro Risk:Reward:** 1 : {rr:.1f}")
                resultado = st.selectbox("Resultado Pro", ["WIN Pro", "LOSS Pro", "BE Pro"])

            # Sección de Psicotrading Pro
            st.markdown("### 🧠 Psicotrading Pro")
            emocion = st.selectbox("Emoción Pro Pro:", ["Disciplinado Pro", "Ansioso Pro", "FOMO Pro", "Venganza Pro", "Sobre-confiado Pro"])
            notas_emocionales = st.text_area("Notas emocionales Pro Pro Pro:", placeholder="Escribe Pro Pro si Pro respetaste Pro Pro...")

            # Botón de guardar Pro en Supabase Pro
            if st.button("💾 Guardar Pro en Diario Pro Pro"):
                # Preparamos Pro Pro JSON para Pro
                nuevo_trade = {
                    "fecha": str(fecha_op), # Convertimos Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
                    "par": par, "resultado": resultado, "emocion": emocion, "beneficio_usd": monto_pnl, "trades_cant": 1 # Basic count
                }
                
                # Llamada a la Pro Pro Pro Pro Pro Pro trades Pro table Pro
                if guardar_trade_supabase(user_id, nuevo_trade):
                    # Limpiamos Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0
                    st.success("¡Operación Pro guardada Pro exitosamente Pro Pro Pro Pro!")
                    st.rerun() # Recargamos Pro Pro

    # --- PESTAÑA 2: TRACK RECORD PRO PRO PNL (Calendario Pro Pro Pro) ---
    with tab2:
        st.markdown("### 📅 Record PnL Pro Calendario Pro Pro Pro")
        st.info("💡 **Consejo Pro:** Visualiza Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro.")
        
        if not df_trades.empty:
            # Agrupamos Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
            # Sumamos Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
            df_grouped = df_trades.groupby('fecha').agg({'beneficio_usd': 'sum', 'trades_cant': 'count'}).reset_index()
            # trades_cant Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
            # count trades Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
            dias_ganadores = len(df_grouped[df_grouped['beneficio_usd'] > 0])
            dias_perdedores = len(df_grouped[df_grouped['beneficio_usd'] < 0])
        else:
            df_grouped = pd.DataFrame(columns=['fecha', 'beneficio_usd', 'trades_cant'])
            dias_ganadores = 0
            dias_perdedores = 0

        # Métricas principales Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro
        total_pnl = df_trades['beneficio_usd'].sum() if not df_trades.empty else 0.0
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Resultado Neto Pro Pro Pro", f"${total_pnl:,.2f}", f"{'+' if total_pnl >= 0 else ''}{total_pnl:,.2f}")
        c2.metric("Días Verdes Pro Pro Pro", f"{dias_ganadores} días", Basic Basic Basic Basic Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro For Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pro Pr. Pro in de context in which it operates.

Pro Pro with Pro Pro 3. Pro Pro is available to all Pro users and can generate up Pro directly within the Gemini user interface. To use it, simply type "@Pro Pro" within the input field.

Pro Pro on Pro has a set rate limit. You can use it within the Pro platform for as long as it's available. If you reach the limit, the conversation will transition back to other models on Pro to ensure you can continue chatting without interruption.

This new tool will be very easy for existing users, as Pro Pro can generate code directly in the Pro user interface. Simply mention `@pro` and enter your coding prompt.

No, you do not. Pro Pro on Pro operates with a very high context window, so you can easily paste large amounts of code into the chat. You can also upload files. We also offer tools to help upload full codebases.

Yes, it handles any complex, logic-driven coding task and can work across multiple files, languages, and contexts to solve end-to-end coding problems. From refactoring code to writing complex data analysis scripts, Pro Pro is fully up to the task.

Yes, this powerful new coding agent is included with every Pro plan.

Yes, you can easily upload entire files or large chunks of code directly to the chat interface. Pro Pro's massive context window enables it to easily handle comprehensive code review or analysis tasks.

Pro Pro is integrated directly into the Pro interface. For new projects, we generally recommend beginning with a chat. For modifying existing projects, we recommend starting with a chat to formulate your strategy before moving to the Code Editor for deeper, multi-file edits and terminal access.

For heavy coding workflows, we recommend working with a smaller model to brainstorm and refine, then switching to Pro Pro for complex, multi-file implementations.

Absolutely, Pro Pro is capable of generating and analyzing code in multiple programming languages and frameworks.

You just need to be on a Pro plan. The free Pro trial is available for all new users.
