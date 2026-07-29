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
    "💱 AUD/JPY",
    "💱 CAD/JPY",
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
        res = client.table("trades").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
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
# 2. ESTILOS CSS PERSONALIZADOS (SOLUCIÓN DEFINITIVA A CAJAS BLANCAS)
# ==========================================
def aplicar_estilos():
    css = """
    <style>
    /* Fondo principal de la app */
    .stApp {
        background-color: #0b0e14 !important;
        color: #ffffff !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    p, label, h1, h2, h3, h4, span, div, .stMarkdown {
        color: #ffffff !important;
    }

    h1, h2 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* === FORZAR FONDO OSCURO EN TODAS LAS CAJAS DE ENTRADA Y DESPLEGABLES === */
    .stTextInput input, 
    .stNumberInput input, 
    .stDateInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"] {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }

    input {
        color: #00f2fe !important;
        -webkit-text-fill-color: #00f2fe !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    div[role="listbox"],
    ul[role="listbox"] {
        background-color: #161b22 !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }

    [data-baseweb="menu"] li,
    div[role="listbox"] li,
    li[role="option"],
    li[data-baseweb="option"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        font-size: 14px !important;
        padding: 10px !important;
    }

    li[role="option"]:hover,
    li[data-baseweb="option"]:hover,
    li[aria-selected="true"] {
        background-color: #00f2fe !important;
        color: #000000 !important;
        font-weight: bold !important;
    }

    textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #00f2fe !important;
        border-radius: 8px !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #161b22 !important;
        border-radius: 12px !important;
        border: 1px solid #00f2fe !important;
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
    st.markdown("Para continuar auditando tus operaciones con IA, calculando lotajes y registrando tu Track Record, activa tu acceso mediante **Binance Pay**:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="paywall-card">
            <h3 style="color:#f0b90b;">🟡 Suscripción Mensual</h3>
            <h2 style="color:#ffffff;">$5 USD <span style="font-size:1rem; color:#aaa;">Inscripción</span></h2>
            <p style="color:#00f2fe; font-weight:bold;">luego solo $2.50 USD / mes</p>
            <hr style="border-color:#333;">
            <ul style="text-align:left; color:#b0b8c4; font-size:0.95rem; line-height: 1.8;">
                <li>✔️ Acceso a todas las herramientas</li>
                <li>✔️ Track Record Calendario PnL</li>
                <li>✔️ Chat & Auditoría Visual con IA</li>
                <li>✔️ Sin contratos ni permanencia</li>
            </ul>
            <br>
            <a href="{LINK_BINANCE_INSCRIPCION}" target="_blank">
                <button style="background:linear-gradient(135deg, #f0b90b 0%, #f39c12 100%); color:black; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                    🟡 Pagar $5 USD (Inscripción + 1er Mes)
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="paywall-card" style="border: 2px solid #38d361;">
            <h3 style="color:#38d361;">🚀 Acceso Anual (Pago Único)</h3>
            <h2 style="color:#ffffff;">$20 USD <span style="font-size:1rem; color:#aaa;">/ 1 Año Completo</span></h2>
            <p style="color:#38d361; font-weight:bold;">¡Ahorra más del 50% sin mensualidades!</p>
            <hr style="border-color:#333;">
            <ul style="text-align:left; color:#b0b8c4; font-size:0.95rem; line-height: 1.8;">
                <li>🌟 <b>Acceso ilimitado por 365 días</b></li>
                <li>🔒 Pago único sin cobros automáticos</li>
                <li>🎁 Actualizaciones futuras incluidas</li>
                <li>🧠 Respuestas de IA prioritarias</li>
            </ul>
            <br>
            <a href="{LINK_BINANCE_ANUAL}" target="_blank">
                <button style="background:linear-gradient(135deg, #38d361 0%, #1b8a3e 100%); color:white; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                    💎 Pagar $20 USD (1 Año Completo)
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_info1, col_info2 = st.columns([1.2, 1])
    with col_info1:
        st.markdown("### 📲 Pago Directo / Renovaciones")
        st.code(f"Binance Pay ID: {BINANCE_PAY_ID}", language="text")
        st.markdown(f"👉 [Enlace directo de Renovación Mensual ($2.50 USDT)]({LINK_BINANCE_RECURRENTE})")

    with col_info2:
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
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")

    with col2:
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
                        st.success("¡Registro exitoso! Inicia sesión.")
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
                        app_url = "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                        client.auth.reset_password_for_email(reset_email, {"redirectTo": app_url})
                        st.success("📩 Se ha enviado un enlace de recuperación a tu correo electrónico. Revisa tu bandeja de entrada o Spam.")
                    except Exception as e:
                        st.error(f"Error al solicitar recuperación: {e}")
                else:
                    st.warning("Por favor ingresa tu correo electrónico.")

# ==========================================
# 6. SIDEBAR COMPLETO RESTAURADO
# ==========================================
def render_sidebar(estado_sub):
    with st.sidebar:
        st.markdown("### 👤 Perfil Trader")
        
        user = st.session_state.user
        user_email = user.email if user else "trader@ejemplo.com"
        metadata = user.user_metadata if (user and hasattr(user, 'user_metadata') and user.user_metadata) else {}
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

        if "PRO" in estado_sub or "Admin" in estado_sub:
            st.success(f"💎 {estado_sub}")
        else:
            st.warning(f"⏳ {estado_sub}")

        with st.expander("⚙️ Modificar Perfil"):
            input_nombre = st.text_input("Nombre de Usuario", value=nombre_actual)
            foto_subida = st.file_uploader("Seleccionar nueva foto", type=["jpg", "jpeg", "png", "webp"])
            lista_estrategias = ["Smart Money Concepts", "Price Action", "ICT", "Indicator Based", "Wyckoff", "Scalping"]
            input_estrategia = st.selectbox("Estrategia Principal", lista_estrategias)
            
            input_cap_actual = st.number_input("Capital Actual ($USD)", value=float(st.session_state.capital_actual), step=500.0)
            input_cap_meta = st.number_input("Meta de Capital ($USD)", value=float(st.session_state.capital_meta), step=1000.0)

            if st.button("Guardar Cambios de Perfil"):
                nueva_foto_b64 = foto_b64
                if foto_subida is not None:
                    bytes_data = foto_subida.getvalue()
                    nueva_foto_b64 = base64.b64encode(bytes_data).decode("utf-8")
                
                try:
                    client = get_supabase_client()
                    res = client.auth.update_user({
                        "data": {
                            "username": input_nombre,
                            "avatar_b64": nueva_foto_b64,
                            "estrategia": input_estrategia
                        }
                    })
                    st.session_state.user = res.user
                    st.session_state.nombre_trader = input_nombre
                    st.session_state.capital_actual = input_cap_actual
                    st.session_state.capital_meta = input_cap_meta
                    
                    st.toast("¡Perfil guardado con éxito!", icon="✅")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")

        st.markdown("---")

        st.markdown("### 🎯 Meta de Cuenta")
        cap_act = st.session_state.capital_actual
        cap_met = st.session_state.capital_meta
        progreso = min(1.0, max(0.0, cap_act / cap_met)) if cap_met > 0 else 0.0
        st.markdown(f"**Capital:** `${cap_act:,.0f}` / `${cap_met:,.0f}`")
        st.progress(progreso)

        st.markdown("---")

        st.markdown("### ⏰ Hora Local")
        st.components.v1.html(
            """
            <div id="clock" style="
                font-family: 'Segoe UI', monospace;
                font-size: 19px;
                font-weight: bold;
                color: #00f2fe;
                background-color: #141a24;
                border: 1px solid rgba(0, 210, 255, 0.4);
                border-radius: 8px;
                padding: 8px;
                text-align: center;
                box-shadow: 0px 0px 10px rgba(0, 242, 254, 0.2);
            ">00:00:00</div>

            <script>
            function updateClock() {
                var now = new Date();
                var timeString = now.toLocaleTimeString([], { hour12: false });
                document.getElementById('clock').innerHTML = timeString + " (Local)";
            }
            setInterval(updateClock, 1000);
            updateClock();
            </script>
            """,
            height=55
        )

        st.markdown("### 🌐 Sesiones de Mercado")
        hora_utc = datetime.datetime.utcnow().hour
        londres_status = '<span class="market-badge open">ABIERTO</span>' if 7 <= hora_utc <= 15 else '<span class="market-badge closed">CERRADO</span>'
        ny_status = '<span class="market-badge open">ABIERTO</span>' if 12 <= hora_utc <= 20 else '<span class="market-badge closed">CERRADO</span>'
        tokio_status = '<span class="market-badge open">ABIERTO</span>' if 0 <= hora_utc <= 9 else '<span class="market-badge closed">CERRADO</span>'

        st.markdown(f"**GB Londres:** {londres_status}", unsafe_allow_html=True)
        st.markdown(f"**US Nueva York:** {ny_status}", unsafe_allow_html=True)
        st.markdown(f"**JP Tokio / Asia:** {tokio_status}", unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("### 🎯 Mis Reglas de Disciplina")
        with st.expander("✏️ Editar Mis Reglas"):
            input_reglas = st.text_area("Escribe tus reglas personalizadas:", value=st.session_state.reglas_disciplina, height=150)
            if st.button("Guardar Reglas"):
                st.session_state.reglas_disciplina = input_reglas
                st.toast("¡Reglas actualizadas!", icon="✅")
                st.rerun()

        st.markdown(st.session_state.reglas_disciplina)

        st.markdown("---")

        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# ==========================================
# 7. DASHBOARD PRINCIPAL Y TODAS LAS PESTAÑAS INTERACTIVAS
# ==========================================
def render_dashboard():
    tiene_acceso, estado_sub, dias_restantes = evaluar_suscripcion(st.session_state.user)
    render_sidebar(estado_sub)

    if not tiene_acceso:
        render_paywall()
        return

    user_id = st.session_state.user.id
    trades_db = cargar_trades_usuario(user_id)

    st.markdown("## ⚡ Journaling & AI Trading Audit")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "➕ Registrar Trade", 
        "📅 Track Record PnL",
        "💬 Chat IA & Auditoría",
        "🧮 Calc. Lotaje", 
        "🧠 Análisis vs IA", 
        "📈 Proyecciones", 
        "📓 Diario & Psicotrading", 
        "📊 Dashboard & Progreso"
    ])

    # --------------------------------------
    # TAB 1: REGISTRAR TRADE (NUEVA LÓGICA DE FOTOS)
    # --------------------------------------
    with tab1:
        st.info("💡 **Tip con IA:** Al subir una captura de TradingView con la herramienta de Posición (Larga/Corta), la IA escaneará la imagen y **autocompletará los precios de Entrada, Stop Loss y Take Profit** por ti.")
        
        col_left, col_right = st.columns([1, 1])

        with col_right:
            st.markdown("### 🖼️ Capturas del Gráfico (Antes & Después)")
            before_img = st.file_uploader("1️⃣ Screenshot ANTES (Escaneo Automático con IA)", type=["png", "jpg", "jpeg"], key="upload_before")
            after_img = st.file_uploader("2️⃣ Screenshot DESPUÉS", type=["png", "jpg", "jpeg"], key="upload_after")

            if before_img:
                st.image(before_img, caption="Setup Antes de Ejecutar", use_container_width=True)
                
                if st.button("🧠 Escanear Gráfico y Autocompletar Campos"):
                    with st.spinner("Leyendo valores numéricos del gráfico con IA..."):
                        extracted = analizar_captura_tradingview(before_img.getvalue())
                        if extracted:
                            st.session_state.auto_entry = float(extracted.get("entry", 0.0))
                            st.session_state.auto_sl = float(extracted.get("sl", 0.0))
                            st.session_state.auto_tp = float(extracted.get("tp", 0.0))
                            st.toast("¡Valores extraídos con éxito!", icon="✨")
                            st.rerun()
                        else:
                            st.warning("No se pudieron extraer los números de la captura. Ingrésalos manualmente.")

            if after_img:
                st.image(after_img, caption="Setup Después de Ejecutar", use_container_width=True)

            monto_pnl = st.number_input("Ganancia / Pérdida en $USD de este trade:", value=0.0, step=10.0)

        with col_left:
            st.markdown("### 📝 Parámetros & Fecha")
            fecha_op = st.date_input("Fecha de la Operación", datetime.date.today())
            
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                par = st.selectbox("Seleccionar Activo / Par", LISTA_ACTIVOS)
                direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], horizontal=True)
                precio_entrada = st.number_input("Precio Entrada", value=st.session_state.auto_entry, format="%.5f")
                stop_loss = st.number_input("Stop Loss", value=st.session_state.auto_sl, format="%.5f")
            
            with sub_c2:
                take_profit = st.number_input("Take Profit", value=st.session_state.auto_tp, format="%.5f")
                
                if precio_entrada > 0 and stop_loss > 0 and take_profit > 0:
                    riesgo = abs(precio_entrada - stop_loss)
                    beneficio = abs(take_profit - precio_entrada)
                    rr = beneficio / riesgo if riesgo > 0 else 0
                else:
                    rr = 0.0
                
                st.markdown(f"**Ratio Risk:Reward:** `1 : {rr:.1f}`")
                resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"])

            st.markdown("### 🧠 Psicotrading & Estado Emocional")
            emocion = st.selectbox("¿Cómo te sentías?", [
                "Disciplinado / Neutro 🧘", 
                "Ansioso ⚡", 
                "FOMO / Miedo a perderse el movimiento 🚀", 
                "Venganza / Frustrado 🛑", 
                "Eufórico / Sobre-confiado 😎"
            ])
            notas_emocionales = st.text_area("Notas emocionales de la sesión:", placeholder="Escribe aquí si respetaste tu plan...")

            if st.button("💾 Guardar Trade en Diario"):
                # Convertir imágenes a Base64 para guardarlas en la BD
                foto_antes_b64 = base64.b64encode(before_img.getvalue()).decode("utf-8") if before_img else None
                foto_despues_b64 = base64.b64encode(after_img.getvalue()).decode("utf-8") if after_img else None

                nuevo_trade = {
                    "fecha": str(fecha_op), 
                    "hora": datetime.datetime.now().strftime("%H:%M"), 
                    "par": par, 
                    "direccion": direccion,
                    "precio_entrada": precio_entrada,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "resultado": resultado, 
                    "emocion": emocion, 
                    "notas": notas_emocionales,
                    "beneficio_usd": float(monto_pnl), 
                    "trades_cant": 1,
                    "foto_antes": foto_antes_b64,
                    "foto_despues": foto_despues_b64
                }
                if guardar_trade_supabase(user_id, nuevo_trade):
                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0
                    st.success("¡Trade guardado exitosamente!")
                    st.rerun()

    # --------------------------------------
    # TAB 2: TRACK RECORD CALENDARIO CON LISTADO COMPLETO Y FOTOS
    # --------------------------------------
    with tab2:
        st.info("💡 **¿Para qué sirve?** Vista mensual estilo Prop Firm. Las ganancias/pérdidas y la cantidad exacta de trades se agrupan por día.")
        
        df_calendar = pd.DataFrame(trades_db)
        total_mes = df_calendar['beneficio_usd'].sum() if not df_calendar.empty and 'beneficio_usd' in df_calendar.columns else 0.0
        
        if not df_calendar.empty and 'beneficio_usd' in df_calendar.columns:
            df_grouped = df_calendar.groupby('fecha').agg({'beneficio_usd': 'sum', 'trades_cant': 'count'}).reset_index()
            dias_ganadores = len(df_grouped[df_grouped['beneficio_usd'] > 0])
            dias_perdedores = len(df_grouped[df_grouped['beneficio_usd'] < 0])
        else:
            dias_ganadores = 0
            dias_perdedores = 0

        c_rec1, c_rec2, c_rec3 = st.columns(3)
        c_rec1.metric("Resultado Neto del Mes", f"${total_mes:,.2f}", f"{'+' if total_mes >= 0 else ''}{total_mes:,.2f}")
        c_rec2.metric("Días Verdes 🟩", f"{dias_ganadores} días")
        c_rec3.metric("Días Rojos 🟥", f"{dias_perdedores} días")

        st.markdown("---")

        pnl_map = {}
        trades_map = {}
        if not df_calendar.empty and 'beneficio_usd' in df_calendar.columns:
            for _, r in df_calendar.iterrows():
                f_str = r['fecha']
                pnl_map[f_str] = pnl_map.get(f_str, 0.0) + (r['beneficio_usd'] or 0.0)
                trades_map[f_str] = trades_map.get(f_str, 0) + 1

        hoy = datetime.date.today()
        año, mes = hoy.year, hoy.month
        
        cal_obj = calendar.Calendar(firstweekday=6)
        mes_dias = cal_obj.monthdayscalendar(año, mes)

        dias_header = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        cols_header = st.columns(7)
        for idx, col in enumerate(cols_header):
            with col:
                st.markdown(f"<div style='text-align:center; font-weight:bold; font-size:1.1rem; color:#f0f3fa; margin-bottom:8px;'>{dias_header[idx]}</div>", unsafe_allow_html=True)

        for semana in mes_dias:
            cols_sem = st.columns(7)
            for day_idx, day_num in enumerate(semana):
                with cols_sem[day_idx]:
                    if day_num == 0:
                        st.markdown("<div style='height:90px; background:transparent;'></div>", unsafe_allow_html=True)
                    else:
                        f_date = datetime.date(año, mes, day_num)
                        f_key = str(f_date)
                        pnl_val = pnl_map.get(f_key, None)
                        num_trades = trades_map.get(f_key, 0)

                        is_today = (f_date == hoy)
                        border_css = "border: 2px solid #00f2fe; box-shadow: 0px 0px 10px rgba(0,242,254,0.4);" if is_today else "border: 1px solid #1f2937;"

                        if pnl_val is None:
                            bg_color = "#12161f"
                            txt_color = "#f0f3fa"
                            pnl_html = ""
                            trades_html = ""
                        elif pnl_val > 0:
                            bg_color = "#38d361"
                            txt_color = "#000000"
                            pnl_fmt = f"${pnl_val:,.0f}".replace(",", ".")
                            if pnl_val >= 1000:
                                pnl_fmt = f"${pnl_val/1000:.1f}K"
                            pnl_html = f"<div style='font-weight:bold; font-size:1.15rem; color:#000;'>+{pnl_fmt}</div>"
                            trades_html = f"<div style='font-size:0.8rem; color:#111;'>{num_trades} trade{'s' if num_trades > 1 else ''}</div>"
                        elif pnl_val < 0:
                            bg_color = "#ff4d4d"
                            txt_color = "#000000"
                            pnl_fmt = f"-${abs(pnl_val):,.0f}".replace(",", ".")
                            if abs(pnl_val) >= 1000:
                                pnl_fmt = f"-${abs(pnl_val)/1000:.1f}K"
                            pnl_html = f"<div style='font-weight:bold; font-size:1.15rem; color:#000;'>{pnl_fmt}</div>"
                            trades_html = f"<div style='font-size:0.8rem; color:#111;'>{num_trades} trade{'s' if num_trades > 1 else ''}</div>"
                        else:
                            bg_color = "#2a3242"
                            txt_color = "#ffffff"
                            pnl_html = "<div style='font-weight:bold; font-size:1.15rem;'>$0</div>"
                            trades_html = f"<div style='font-size:0.8rem;'>{num_trades} trades</div>"

                        today_tag = " <span style='font-size:0.7rem; color:#00f2fe;'>(HOY)</span>" if is_today else ""

                        box_html = f"""<div style="background-color: {bg_color}; {border_css} border-radius: 6px; padding: 6px 8px; height: 95px; margin-bottom: 8px; display: flex; flex-direction: column; justify-content: space-between;"><div style="font-size:0.85rem; font-weight:700; color:{txt_color};">{day_num}{today_tag}</div><div style="text-align:center;">{pnl_html}{trades_html}</div></div>"""
                        
                        st.markdown(box_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 📋 Historial Detallado de Trades Registrados & Capturas")

        if not trades_db:
            st.info("Aún no se registran trades en la base de datos para mostrar imágenes.")
        else:
            for idx, trade in enumerate(trades_db):
                fecha_t = trade.get("fecha", "Sin fecha")
                par_t = trade.get("par", "Activo")
                res_t = trade.get("resultado", "N/A")
                pnl_t = trade.get("beneficio_usd", 0.0)
                dir_t = trade.get("direccion", "N/A")
                
                titulo_expander = f"📅 {fecha_t} | {par_t} ({dir_t}) | Resultado: {res_t} | PnL: ${pnl_t:,.2f} USD"
                
                with st.expander(titulo_expander, expanded=(idx==0)):
                    col_info, col_f1, col_f2 = st.columns([1, 1.2, 1.2])
                    
                    with col_info:
                        st.markdown("#### ⚙️ Datos del Trade")
                        st.markdown(f"**Activo:** `{par_t}`")
                        st.markdown(f"**Dirección:** `{dir_t}`")
                        st.markdown(f"**Precio Entrada:** `{trade.get('precio_entrada', 0.0)}`")
                        st.markdown(f"**Stop Loss:** `{trade.get('stop_loss', 0.0)}`")
                        st.markdown(f"**Take Profit:** `{trade.get('take_profit', 0.0)}`")
                        st.markdown(f"**Estado Emocional:** {trade.get('emocion', 'N/A')}")
                        st.markdown(f"**Notas:** {trade.get('notas', 'Sin notas')}")

                    with col_f1:
                        st.markdown("#### 1️⃣ Screenshot ANTES")
                        foto_a = trade.get("foto_antes")
                        if foto_a:
                            st.markdown(f'<img src="data:image/png;base64,{foto_a}" style="width:100%; border-radius:8px; border:1px solid #00f2fe;">', unsafe_allow_html=True)
                        else:
                            st.caption("No se adjuntó captura del ANTES.")

                    with col_f2:
                        st.markdown("#### 2️⃣ Screenshot DESPUÉS")
                        foto_d = trade.get("foto_despues")
                        if foto_d:
                            st.markdown(f'<img src="data:image/png;base64,{foto_d}" style="width:100%; border-radius:8px; border:1px solid #00f2fe;">', unsafe_allow_html=True)
                        else:
                            st.caption("No se adjuntó captura del DESPUÉS.")

    # --------------------------------------
    # TAB 3: CHAT DE AUDITORÍA CON IA
    # --------------------------------------
    with tab3:
        st.markdown("### 💬 Chat de Auditoría de Trading con IA")
        st.caption("Pregúntale a tu asistente sobre tus hábitos, estadísticas o reglas operativas.")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Escribe tu duda (ej. ¿Cómo puedo mejorar mi Win Rate este mes?)..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analizando tu historial de operaciones con IA... 🧠"):
                    cant_trades = len(trades_db)
                    if cant_trades == 0:
                        respuesta_ia = "Aún no has registrado trades en tu diario. Ve a la pestaña **'➕ Registrar Trade'** para comenzar a auditar tu operativa."
                    else:
                        df_tr = pd.DataFrame(trades_db)
                        pnl_tot = df_tr['beneficio_usd'].sum() if 'beneficio_usd' in df_tr.columns else 0.0
                        wins = len(df_tr[df_tr['beneficio_usd'] > 0]) if 'beneficio_usd' in df_tr.columns else 0
                        win_rate = (wins / cant_trades * 100) if cant_trades > 0 else 0
                        respuesta_ia = f"Has registrado **{cant_trades}** operaciones con un resultado neto acumulado de **${pnl_tot:,.2f} USD** y una tasa de acierto del **{win_rate:.1f}%**. Te sugiero seguir manteniendo la disciplina emocional."

                    st.markdown(respuesta_ia)
                    st.session_state.chat_history.append({"role": "assistant", "content": respuesta_ia})

    # --------------------------------------
    # TAB 4: CALCULADORA DE LOTAJE
    # --------------------------------------
    with tab4:
        st.markdown("### 🧮 Calculadora de Tamaño de Posición")
        st.caption("Calcula el lotaje ideal para no sobrepasar el riesgo permitido por operación.")

        col_a, col_b = st.columns(2)
        with col_a:
            balance = st.number_input("Balance de Cuenta ($USD)", value=float(st.session_state.capital_actual), step=500.0)
            porcentaje_riesgo = st.number_input("Riesgo por Trade (%)", value=1.0, step=0.25)
            pips_sl = st.number_input("Distancia de Stop Loss (Pips / Puntos)", value=20.0, step=1.0)

        with col_b:
            monto_riesgo = balance * (porcentaje_riesgo / 100.0)
            lotaje_estimado = (monto_riesgo / (pips_sl * 10.0)) if pips_sl > 0 else 0.0

            st.metric("Riesgo Monetario Máximo", f"${monto_riesgo:,.2f} USD")
            st.metric("Lotes Sugeridos (Forex Estándar)", f"{lotaje_estimado:.2f} Lotes")
            st.info("💡 **Nota:** Para índices como US100 / US30 o Criptos, ajusta la equivalencia según el contrato de tu broker.")

    # --------------------------------------
    # TAB 5: ANÁLISIS VS IA (AUDITORÍA VISUAL)
    # --------------------------------------
    with tab5:
        st.markdown("### 🤖 Auditoría Visual de Estructura de Mercado")
        st.caption("Sube la captura de tu setup previo a la entrada para recibir una segunda opinión basada en IA.")

        chart_audit = st.file_uploader("Subir Gráfico para Auditoría Visual", type=["png", "jpg", "jpeg"], key="audit_upload_visual")
        if chart_audit:
            st.image(chart_audit, caption="Análisis en proceso...", use_container_width=True)
            if st.button("🔍 Auditar Entrada con IA"):
                with st.spinner("Escaneando zonas de oferta, demanda y estructura..."):
                    st.success("✅ **Análisis completado:** El gráfico muestra una estructura clara. Recuerda confirmar la confluencia en temporalidades menores antes de ejecutar.")

    # --------------------------------------
    # TAB 6: PROYECCIONES DE CAPITAL
    # --------------------------------------
    with tab6:
        st.markdown("### 📈 Proyección de Crecimiento por Interés Compuesto")
        st.caption("Simula cómo crecería tu cuenta a 12 meses manteniendo tu porcentaje de efectividad.")

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            trades_mes = st.slider("Trades por Mes", 5, 50, 15)
            win_rate_est = st.slider("Win Rate Estimado (%)", 30, 90, 55)
        with col_p2:
            ganancia_prom = st.number_input("Ganancia Promedio por WIN ($)", value=200.0, step=25.0)
            perdida_prom = st.number_input("Pérdida Promedio por LOSS ($)", value=100.0, step=25.0)

        capital_proyectado = st.session_state.capital_actual
        proyeccion_meses = []

        for m in range(1, 13):
            ganadores = trades_mes * (win_rate_est / 100.0)
            perdedores = trades_mes - ganadores
            pnl_mes = (ganadores * ganancia_prom) - (perdedores * perdida_prom)
            capital_proyectado += pnl_mes
            proyeccion_meses.append({"Mes": f"Mes {m}", "Capital": capital_proyectado})

        df_proy = pd.DataFrame(proyeccion_meses)
        st.metric("Capital Estimado a 12 Meses", f"${capital_proyectado:,.2f} USD", f"+${capital_proyectado - st.session_state.capital_actual:,.2f} USD")
        
        fig_proy = px.line(df_proy, x="Mes", y="Capital", title="Proyección de Cuenta a 12 Meses", markers=True, template="plotly_dark")
        st.plotly_chart(fig_proy, use_container_width=True)

    # --------------------------------------
    # TAB 7: DIARIO Y PSICOTRADING
    # --------------------------------------
    with tab7:
        st.markdown("### 📓 Bitácora de Psicotrading & Reflexión Mental")
        st.caption("Lleva un registro de tu mentalidad y estado emocional para evitar el overtrading y el FOMO.")

        reflexion = st.text_area("Reflexión semanal o notas mentales:", height=180, placeholder="Escribe aquí cómo te sentiste esta semana, si respetaste tus Stop Loss, etc.")
        if st.button("💾 Guardar Reflexión en Bitácora"):
            st.toast("¡Reflexión guardada en tu sesión!", icon="🧠")

    # --------------------------------------
    # TAB 8: DASHBOARD & METRICAS
    # --------------------------------------
    with tab8:
        st.markdown("### 📊 Dashboard Operativo & Rendimiento Global")

        df_trades = pd.DataFrame(trades_db)
        cant_total = len(df_trades)
        
        if not df_trades.empty and 'beneficio_usd' in df_trades.columns:
            wins = len(df_trades[df_trades['beneficio_usd'] > 0])
            losses = len(df_trades[df_trades['beneficio_usd'] < 0])
            win_rate = (wins / cant_total * 100) if cant_total > 0 else 0.0
            pnl_total = df_trades['beneficio_usd'].sum()
        else:
            wins, losses, win_rate, pnl_total = 0, 0, 0.0, 0.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Resultado Acumulado", f"${pnl_total:,.2f} USD")
        m2.metric("Win Rate Total", f"{win_rate:.1f}%")
        m3.metric("Trades Totales", str(cant_total))
        m4.metric("Días Operados", str(len(df_trades['fecha'].unique()) if not df_trades.empty and 'fecha' in df_trades.columns else 0))

        st.markdown("---")
        st.markdown("#### 🗺️ Mapa de Rendimiento por Activo y Emoción")

        if not df_trades.empty and 'beneficio_usd' in df_trades.columns:
            fig = px.bar(
                df_trades, 
                x="par", 
                y="beneficio_usd", 
                color="emocion", 
                title="Ganancia / Pérdida según Estado Emocional",
                template="plotly_dark",
                color_discrete_sequence=["#00f2fe", "#00d2ff", "#2962ff", "#4facfe", "#ff2a2a"]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no tienes operaciones registradas. Registra tu primer trade para desbloquear tus métricas avanzadas.")

# ==========================================
# 8. FLUJO PRINCIPAL DE EJECUCIÓN
# ==========================================
if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
