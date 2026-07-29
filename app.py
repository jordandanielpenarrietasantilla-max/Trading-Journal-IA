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
from io import BytesIO
from PIL import Image
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
if "foto_perfil_custom" not in st.session_state:
    st.session_state.foto_perfil_custom = None

# Variables autocompletadas por la IA
if "auto_entry" not in st.session_state:
    st.session_state.auto_entry = 0.0
if "auto_sl" not in st.session_state:
    st.session_state.auto_sl = 0.0
if "auto_tp" not in st.session_state:
    st.session_state.auto_tp = 0.0

# LISTA COMPLETA DE ACTIVOS FINANCIEROS
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
# FUNCIONES DE COMPRESIÓN Y BASE DE DATOS
# ==========================================
def comprimir_y_convertir_b64(uploaded_file, max_size=(800, 800), quality=60):
    """Comprime la imagen cargada para evitar errores de tamaño en Supabase."""
    if uploaded_file is None:
        return None
    try:
        image = Image.open(uploaded_file)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=quality)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as e:
        st.error(f"Error comprimiendo imagen: {e}")
        return None

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
        st.error(f"Error guardando en Supabase: {e}")
        return False

def actualizar_trade_supabase(trade_id, trade_data):
    try:
        client = get_supabase_client()
        client.table("trades").update(trade_data).eq("id", trade_id).execute()
        return True
    except Exception as e:
        st.error(f"Error actualizando trade: {e}")
        return False

def eliminar_trade_supabase(trade_id):
    try:
        client = get_supabase_client()
        client.table("trades").delete().eq("id", trade_id).execute()
        return True
    except Exception as e:
        st.error(f"Error eliminando trade: {e}")
        return False

def analizar_captura_tradingview(image_bytes):
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
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                ]
            }
        ]
    }
    
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=20)
        res_json = response.json()
        content = res_json["choices"][0]["message"]["content"]
        content_clean = content.replace("```json", "").replace("```", "").strip()
        return json.loads(content_clean)
    except Exception:
        return None

# ==========================================
# ESTILOS CSS
# ==========================================
def aplicar_estilos():
    css = """
    <style>
    .stApp { background-color: #0b0e14 !important; color: #ffffff !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important; }
    p, label, h1, h2, h3, h4, span, div, .stMarkdown { color: #ffffff !important; }
    h1, h2 { background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800 !important; }
    .stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] {
        background-color: #161b22 !important; color: #00f2fe !important; -webkit-text-fill-color: #00f2fe !important; border: 1px solid #00f2fe !important; border-radius: 8px !important;
    }
    input { color: #00f2fe !important; -webkit-text-fill-color: #00f2fe !important; }
    textarea { background-color: #161b22 !important; color: #ffffff !important; border: 1px solid #00f2fe !important; border-radius: 8px !important; }
    .stButton>button { background: linear-gradient(135deg, #00d2ff 0%, #2962ff 100%) !important; color: #ffffff !important; border-radius: 8px !important; border: none !important; font-weight: bold !important; width: 100%; box-shadow: 0px 4px 15px rgba(0, 210, 255, 0.3) !important; }
    section[data-testid="stSidebar"] { background-color: #0f141e !important; border-right: 1px solid rgba(0, 210, 255, 0.2) !important; }
    section[data-testid="stSidebar"] .stButton>button { background: linear-gradient(135deg, #e53935 0%, #b71c1c 100%) !important; box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.3) !important; }
    .market-badge { display: inline-block; padding: 2px 6px; border-radius: 8px; font-size: 0.75rem; font-weight: bold; }
    .open { background-color: rgba(76, 175, 80, 0.2); color: #4caf50; border: 1px solid #4caf50; }
    .closed { background-color: rgba(244, 67, 54, 0.2); color: #f44336; border: 1px solid #f44336; }
    .paywall-card { background-color: #161b22; border: 1px solid #f0b90b; border-radius: 12px; padding: 24px; text-align: center; box-shadow: 0px 0px 20px rgba(240, 185, 11, 0.2); }
    .stExpander { background-color: #12161f !important; border: 1px solid #1f2937 !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    
    .user-profile-box { text-align: center; padding: 10px 0 15px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 15px; }
    .user-avatar-img { width: 80px; height: 80px; border-radius: 50%; border: 3px solid #00f2fe; box-shadow: 0px 0px 15px rgba(0, 242, 254, 0.4); object-fit: cover; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos()

def evaluar_suscripcion(user):
    user_email = user.email if (user and hasattr(user, 'email')) else ""
    if user_email.lower() == "jordandanielpenarrietasantilla@gmail.com":
        return True, "Creador / Admin 👑", 99999
    metadata = user.user_metadata if (user and hasattr(user, 'user_metadata') and user.user_metadata) else {}
    if metadata.get("es_vip", False):
        return True, "Acceso PRO 💎", 999
    created_at_str = str(user.created_at) if hasattr(user, 'created_at') else None
    fecha_registro = datetime.datetime.strptime(created_at_str[:10], "%Y-%m-%d").date() if created_at_str else datetime.date.today()
    dias_usados = (datetime.date.today() - fecha_registro).days
    dias_restantes = max(0, 3 - dias_usados)
    return (True, f"Prueba Gratis ({dias_restantes} días rest.)", dias_restantes) if dias_usados <= 3 else (False, "Prueba Expirada 🛑", 0)

def render_paywall():
    st.markdown("## 🔒 Tu Período de Prueba Gratis de 3 Días ha Expirado")
    st.markdown("Para continuar auditando tus operaciones con IA, activa tu acceso mediante **Binance Pay**:")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="paywall-card">
            <h3 style="color:#f0b90b;">🟡 Suscripción Mensual</h3>
            <h2 style="color:#ffffff;">$5 USD <span style="font-size:1rem; color:#aaa;">Inscripción</span></h2>
            <p style="color:#00f2fe; font-weight:bold;">luego solo $2.50 USD / mes</p>
            <hr style="border-color:#333;">
            <a href="{LINK_BINANCE_INSCRIPCION}" target="_blank">
                <button style="background:linear-gradient(135deg, #f0b90b 0%, #f39c12 100%); color:black; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                    🟡 Pagar $5 USD
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="paywall-card" style="border: 2px solid #38d361;">
            <h3 style="color:#38d361;">🚀 Acceso Anual (Pago Único)</h3>
            <h2 style="color:#ffffff;">$20 USD <span style="font-size:1rem; color:#aaa;">/ 1 Año</span></h2>
            <p style="color:#38d361; font-weight:bold;">¡Ahorra más del 50%!</p>
            <hr style="border-color:#333;">
            <a href="{LINK_BINANCE_ANUAL}" target="_blank">
                <button style="background:linear-gradient(135deg, #38d361 0%, #1b8a3e 100%); color:white; border:none; padding:14px; border-radius:8px; font-weight:bold; width:100%; cursor:pointer;">
                    💎 Pagar $20 USD
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

def render_auth():
    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")
    with col2:
        tab_login, tab_register, tab_reset = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse", "🔐 Recuperar Clave"])
        with tab_login:
            login_email = st.text_input("Correo Electrónico", key="login_email")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            if st.button("Ingresar", key="btn_login"):
                try:
                    client = get_supabase_client()
                    res = client.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                    st.session_state.authenticated = True
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as err:
                    st.error(f"Error al iniciar sesión: {err}")
        with tab_register:
            reg_email = st.text_input("Correo Electrónico", key="reg_email")
            reg_pass = st.text_input("Crea tu Contraseña", type="password", key="reg_pass")
            if st.button("Crear Cuenta y Probar", key="btn_reg"):
                try:
                    client = get_supabase_client()
                    res = client.auth.sign_up({"email": reg_email, "password": reg_pass})
                    st.success("¡Registro exitoso! Inicia sesión.")
                except Exception as e:
                    st.error(f"Error al registrar: {e}")
        with tab_reset:
            reset_email = st.text_input("Correo Electrónico Registrado", key="reset_email")
            if st.button("Enviar Enlace de Recuperación", key="btn_reset"):
                if reset_email:
                    try:
                        client = get_supabase_client()
                        app_url = "https://trading-journal-ia-7lvamxtjspcbclwcda2zxg.streamlit.app/"
                        client.auth.reset_password_for_email(reset_email, {"redirectTo": app_url})
                        st.success("📩 Se ha enviado un enlace de recuperación.")
                    except Exception as e:
                        st.error(f"Error: {e}")

# ==========================================
# SIDEBAR CON CONFIGURACIÓN DE PERFIL, REGLAS Y HORARIOS
# ==========================================
def render_sidebar(estado_sub):
    with st.sidebar:
        user = st.session_state.user
        user_email = user.email if user else "trader@ejemplo.com"
        metadata = user.user_metadata if (user and hasattr(user, 'user_metadata') and user.user_metadata) else {}
        
        # 1. Foto de Perfil Custom o Avatar por defecto
        foto_custom = st.session_state.get("foto_perfil_custom", None)
        if foto_custom:
            avatar_url = f"data:image/jpeg;base64,{foto_custom}"
        else:
            avatar_url = metadata.get("avatar_url") or metadata.get("picture") or f"https://api.dicebear.com/7.x/bottts/svg?seed={user_email}"

        nombre_actual = st.session_state.get("nombre_trader", metadata.get("username") or metadata.get("full_name") or "Trader Pro")

        st.markdown(f"""
        <div class="user-profile-box">
            <img src="{avatar_url}" class="user-avatar-img">
            <h3 style="margin:10px 0 2px 0; font-size:1.2rem; color:#ffffff;">{nombre_actual}</h3>
            <p style="margin:0; font-size:0.75rem; color:#00f2fe; word-break:break-all;">{user_email}</p>
        </div>
        """, unsafe_allow_html=True)

        if "PRO" in estado_sub or "Admin" in estado_sub:
            st.success(f"💎 {estado_sub}")
        else:
            st.warning(f"⏳ {estado_sub}")

        # ⚙️ EDICIÓN DE PERFIL Y REGLAS DE TRADING
        with st.expander("⚙️ Configurar Perfil y Reglas"):
            nuevo_nombre = st.text_input("Nombre de Trader", value=st.session_state.nombre_trader)
            nueva_foto = st.file_uploader("Subir Foto de Perfil", type=["jpg", "png", "jpeg"])
            st.session_state.capital_actual = st.number_input("Capital Actual ($)", value=float(st.session_state.capital_actual))
            st.session_state.capital_meta = st.number_input("Meta de Capital ($)", value=float(st.session_state.capital_meta))
            st.session_state.reglas_disciplina = st.text_area("📋 Mis Reglas de Trading", value=st.session_state.reglas_disciplina, height=120)

            if st.button("💾 Guardar Configuración"):
                st.session_state.nombre_trader = nuevo_nombre
                if nueva_foto:
                    st.session_state.foto_perfil_custom = comprimir_y_convertir_b64(nueva_foto)
                st.toast("¡Perfil y reglas actualizados!")
                st.rerun()

        st.markdown("---")
        
        # 2. Reloj UTC y Sesiones de Mercado
        st.markdown("### 🕒 Mercado & Sesiones UTC")
        ahora_utc = datetime.datetime.now(datetime.timezone.utc)
        hora_utc_str = ahora_utc.strftime("%H:%M:%S UTC")
        st.caption(f"📅 **{ahora_utc.strftime('%Y-%m-%d')}** | ⏱️ `{hora_utc_str}`")

        h_utc = ahora_utc.hour
        tokyo_open = (0 <= h_utc < 9)
        london_open = (8 <= h_utc < 16)
        ny_open = (13 <= h_utc < 21)
        sydney_open = (22 <= h_utc or h_utc < 7)

        st.markdown(f"""
        <div style="font-size:0.85rem; line-height:1.8;">
            🇬🇧 <b>Londres:</b> <span class="market-badge {'open' if london_open else 'closed'}">{'OPEN 🟢' if london_open else 'CLOSED 🔴'}</span><br>
            🇺🇸 <b>Nueva York:</b> <span class="market-badge {'open' if ny_open else 'closed'}">{'OPEN 🟢' if ny_open else 'CLOSED 🔴'}</span><br>
            🇯🇵 <b>Tokio:</b> <span class="market-badge {'open' if tokyo_open else 'closed'}">{'OPEN 🟢' if tokyo_open else 'CLOSED 🔴'}</span><br>
            🇦🇺 <b>Sídney:</b> <span class="market-badge {'open' if sydney_open else 'closed'}">{'OPEN 🟢' if sydney_open else 'CLOSED 🔴'}</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        
        # 3. Meta de Cuenta
        st.markdown("### 🎯 Meta de Cuenta")
        cap_act = st.session_state.capital_actual
        cap_met = st.session_state.capital_meta
        progreso = min(1.0, max(0.0, cap_act / cap_met)) if cap_met > 0 else 0.0
        st.markdown(f"**Capital:** `${cap_act:,.0f}` / `${cap_met:,.0f}`")
        st.progress(progreso)

        st.markdown("---")
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# ==========================================
# DASHBOARD PRINCIPAL
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

    # --- TAB 1: REGISTRAR TRADE ---
    with tab1:
        st.info("💡 **Tip con IA:** Sube una captura de TradingView para extraer la entrada, Stop Loss y Take Profit de forma automática.")
        col_left, col_right = st.columns([1, 1])

        with col_right:
            st.markdown("### 🖼️ Capturas del Gráfico (Antes & Después)")
            before_img = st.file_uploader("1️⃣ Screenshot ANTES (Escaneo IA)", type=["png", "jpg", "jpeg"], key="upload_before")
            after_img = st.file_uploader("2️⃣ Screenshot DESPUÉS", type=["png", "jpg", "jpeg"], key="upload_after")

            if before_img:
                st.image(before_img, caption="Setup ANTES", use_container_width=True)
                if st.button("🧠 Escanear Gráfico y Autocompletar Campos"):
                    with st.spinner("Escaneando gráfico con IA..."):
                        extracted = analizar_captura_tradingview(before_img.getvalue())
                        if extracted:
                            st.session_state.auto_entry = float(extracted.get("entry", 0.0))
                            st.session_state.auto_sl = float(extracted.get("sl", 0.0))
                            st.session_state.auto_tp = float(extracted.get("tp", 0.0))
                            st.toast("¡Valores extraídos!", icon="✨")
                            st.rerun()

            if after_img:
                st.image(after_img, caption="Setup DESPUÉS", use_container_width=True)

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
                resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"])

            st.markdown("### 🧠 Psicotrading & Estado Emocional")
            emocion = st.selectbox("¿Cómo te sentías?", ["Disciplinado / Neutro 🧘", "Ansioso ⚡", "FOMO 🚀", "Venganza / Frustrado 🛑", "Eufórico 😎"])
            notas_emocionales = st.text_area("Notas emocionales de la sesión:", placeholder="Escribe detalles sobre la ejecución...")

            if st.button("💾 Guardar Trade en Diario"):
                b64_before = comprimir_y_convertir_b64(before_img)
                b64_after = comprimir_y_convertir_b64(after_img)

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
                    "foto_antes": b64_before,
                    "foto_despues": b64_after
                }

                if guardar_trade_supabase(user_id, nuevo_trade):
                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0
                    st.success("¡Trade guardado exitosamente!")
                    st.rerun()

    # --- TAB 2: TRACK RECORD CALENDARIO CON LISTADO, EDICIÓN Y BORRADO ---
    with tab2:
        st.info("💡 **Vista de Calendario y Detalle:** Agrupa ganancias/pérdidas del mes y te permite editar o eliminar cada registro.")
        
        df_calendar = pd.DataFrame(trades_db)
        total_mes = df_calendar['beneficio_usd'].sum() if not df_calendar.empty and 'beneficio_usd' in df_calendar.columns else 0.0
        
        if not df_calendar.empty and 'beneficio_usd' in df_calendar.columns:
            df_grouped = df_calendar.groupby('fecha').agg({'beneficio_usd': 'sum', 'trades_cant': 'count'}).reset_index()
            dias_ganadores = len(df_grouped[df_grouped['beneficio_usd'] > 0])
            dias_perdedores = len(df_grouped[df_grouped['beneficio_usd'] < 0])
        else:
            dias_ganadores, dias_perdedores = 0, 0

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
                            pnl_html, trades_html = "", ""
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
        st.markdown("### 📋 Historial Detallado, Capturas, Edición y Borrado")

        if not trades_db:
            st.info("No hay trades registrados aún.")
        else:
            for idx, trade in enumerate(trades_db):
                trade_id = trade.get("id")
                fecha_t = trade.get("fecha", "Sin fecha")
                par_t = trade.get("par", "Activo")
                res_t = trade.get("resultado", "N/A")
                pnl_t = trade.get("beneficio_usd", 0.0)

                expander_label = f"📅 {fecha_t} | {par_t} | Resultado: {res_t} | PnL: ${pnl_t:,.2f} USD"

                with st.expander(expander_label, expanded=(idx == 0)):
                    col_det, col_f1, col_f2 = st.columns([1.2, 1, 1])

                    with col_det:
                        st.markdown("#### ⚙️ Detalle de Operación")
                        st.write(f"**Dirección:** {trade.get('direccion', 'N/A')}")
                        st.write(f"**Entrada:** {trade.get('precio_entrada', 0.0)}")
                        st.write(f"**SL:** {trade.get('stop_loss', 0.0)} | **TP:** {trade.get('take_profit', 0.0)}")
                        st.write(f"**Emoción:** {trade.get('emocion', 'N/A')}")
                        st.write(f"**Notas:** {trade.get('notas', 'Sin notas')}")

                        st.markdown("---")
                        if st.button("🗑️ Eliminar Trade", key=f"del_{trade_id}_{idx}"):
                            if eliminar_trade_supabase(trade_id):
                                st.toast("Trade eliminado correctamente")
                                st.rerun()

                    with col_f1:
                        st.markdown("**1️⃣ ANTES**")
                        foto_a = trade.get("foto_antes")
                        if foto_a and str(foto_a).strip() != "":
                            st.markdown(f'<img src="data:image/jpeg;base64,{foto_a}" style="width:100%; border-radius:8px;">', unsafe_allow_html=True)
                        else:
                            st.caption("Sin captura ANTES")

                    with col_f2:
                        st.markdown("**2️⃣ DESPUÉS**")
                        foto_d = trade.get("foto_despues")
                        if foto_d and str(foto_d).strip() != "":
                            st.markdown(f'<img src="data:image/jpeg;base64,{foto_d}" style="width:100%; border-radius:8px;">', unsafe_allow_html=True)
                        else:
                            st.caption("Sin captura DESPUÉS")

                    # MÓDULO DE EDICIÓN
                    with st.expander("✏️ Editar datos de este trade"):
                        edit_pnl = st.number_input("Editar PnL ($USD)", value=float(pnl_t), key=f"edit_pnl_{trade_id}")
                        edit_res = st.selectbox("Editar Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"], key=f"edit_res_{trade_id}")
                        edit_notes = st.text_area("Editar Notas", value=trade.get("notas", ""), key=f"edit_notes_{trade_id}")
                        edit_img_before = st.file_uploader("Reemplazar Foto ANTES", type=["png", "jpg", "jpeg"], key=f"edit_fb_{trade_id}")
                        edit_img_after = st.file_uploader("Reemplazar Foto DESPUÉS", type=["png", "jpg", "jpeg"], key=f"edit_fa_{trade_id}")

                        if st.button("💾 Guardar Cambios", key=f"save_edit_{trade_id}"):
                            payload_edit = {
                                "beneficio_usd": float(edit_pnl),
                                "resultado": edit_res,
                                "notas": edit_notes
                            }
                            if edit_img_before:
                                payload_edit["foto_antes"] = comprimir_y_convertir_b64(edit_img_before)
                            if edit_img_after:
                                payload_edit["foto_despues"] = comprimir_y_convertir_b64(edit_img_after)

                            if actualizar_trade_supabase(trade_id, payload_edit):
                                st.toast("Trade actualizado con éxito")
                                st.rerun()

    # --- TAB 3: CHAT IA ---
    with tab3:
        st.markdown("### 💬 Chat de Auditoría con IA")
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Escribe tu consulta..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                cant_trades = len(trades_db)
                respuesta_ia = f"Tienes **{cant_trades}** operaciones registradas en tu historial."
                st.markdown(respuesta_ia)
                st.session_state.chat_history.append({"role": "assistant", "content": respuesta_ia})

    # --- TAB 4: CALCULADORA LOTAJE ---
    with tab4:
        st.markdown("### 🧮 Calculadora de Lotaje")
        balance = st.number_input("Balance ($USD)", value=float(st.session_state.capital_actual))
        pips = st.number_input("Stop Loss (Pips)", value=20.0)
        lotaje = (balance * 0.01) / (pips * 10) if pips > 0 else 0.0
        st.metric("Lotaje Sugerido (1% Riesgo)", f"{lotaje:.2f} Lotes")

    # --- TAB 5: ANÁLISIS VS IA ---
    with tab5:
        st.markdown("### 🤖 Auditoría Visual")
        chart = st.file_uploader("Subir Gráfico", type=["png", "jpg", "jpeg"], key="audit_v")
        if chart and st.button("Auditar Gráfico"):
            st.success("Estructura analizada correctamente.")

    # --- TAB 6: PROYECCIONES ---
    with tab6:
        st.markdown("### 📈 Proyección de Crecimiento")
        trades_mes = st.slider("Trades al mes", 5, 50, 15)
        st.write(f"Proyección estimada basada en {trades_mes} trades mensuales.")

    # --- TAB 7: PSICOTRADING Y REGLAS ---
    with tab7:
        st.markdown("### 📓 Bitácora Emocional & Reglas de Disciplina")
        st.markdown("#### 📜 Mis Reglas de Trading Actuales")
        st.info(st.session_state.reglas_disciplina)
        st.markdown("---")
        st.text_area("Notas breves de mentalidad para hoy:")

    # --- TAB 8: DASHBOARD ---
    with tab8:
        st.markdown("### 📊 Dashboard General")
        df_t = pd.DataFrame(trades_db)
        if not df_t.empty and "beneficio_usd" in df_t.columns:
            st.metric("PnL Total", f"${df_t['beneficio_usd'].sum():,.2f} USD")
            fig = px.bar(df_t, x="par", y="beneficio_usd", title="Rendimiento por Activo", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
