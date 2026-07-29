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

# ==========================================
# 1. CONFIGURACIÓN Y ENLACES REALES DE BINANCE PAY
# ==========================================
st.set_page_config(
    page_title="AI Trading Journal & Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

LINK_BINANCE_INSCRIPCION = "https://s.binance.com/8vSxLZRA"
LINK_BINANCE_ANUAL = "https://s.binance.com/NvHWGF9P"
LINK_BINANCE_RECURRENTE = "https://s.binance.com/U7v5zFVr"

BINANCE_PAY_ID = "JORDAN_SANTI9"
LINK_TELEGRAM_SOPORTE = "https://t.me/tu_usuario_telegram"

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://lyzvcbjpoydeckxtbcq.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_HIo0YXn-kJUr7HuNZFNfjQ_JBncowE0")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

def get_supabase_client() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Función para optimizar y convertir imágenes a Base64 sin saturar la base de datos
def procesar_imagen_b64(uploaded_file, max_size=(800, 600)):
    if uploaded_file is None:
        return ""
    try:
        image = Image.open(uploaded_file)
        image.thumbnail(max_size)  # Redimensionar manteniendo proporción
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=75) # Compresión óptima
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        st.error(f"Error al procesar la imagen: {e}")
        return ""

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

if "auto_entry" not in st.session_state:
    st.session_state.auto_entry = 0.0
if "auto_sl" not in st.session_state:
    st.session_state.auto_sl = 0.0
if "auto_tp" not in st.session_state:
    st.session_state.auto_tp = 0.0

# LISTA DE ACTIVOS
LISTA_ACTIVOS = [
    "🥇 XAU/USD (Oro)", "🥈 XAG/USD (Plata)", "🛢️ USOIL (Petróleo WTI)", "🛢️ UKOIL (Petróleo Brent)",
    "🌾 NGAS (Gas Natural)", "🪙 BTC/USD (Bitcoin)", "🪙 ETH/USD (Ethereum)", "🪙 SOL/USD (Solana)",
    "🪙 XRP/USD (Ripple)", "🪙 BNB/USD (Binance Coin)", "📊 US100 (Nasdaq 100)", "📊 US30 (Dow Jones)",
    "📊 US500 (S&P 500)", "📊 GER40 (Dax Alemán)", "💱 EUR/USD", "💱 GBP/USD", "💱 USD/JPY", "💱 AUD/USD",
    "📈 NVDA (Nvidia)", "📈 TSLA (Tesla)", "📈 AAPL (Apple)", "📈 AMZN (Amazon)"
]

def cargar_trades_usuario(user_id):
    try:
        client = get_supabase_client()
        res = client.table("trades").select("*").eq("user_id", user_id).order("fecha", desc=True).execute()
        return res.data if res.data else []
    except Exception as e:
        st.error(f"Error consultando base de datos: {e}")
        return []

def guardar_trade_supabase(user_id, trade_data):
    try:
        client = get_supabase_client()
        trade_data["user_id"] = user_id
        client.table("trades").insert(trade_data).execute()
        return True
    except Exception as e:
        st.error(f"Error al guardar en Supabase: {e}")
        return False

def eliminar_trade_supabase(trade_id):
    try:
        client = get_supabase_client()
        client.table("trades").delete().eq("id", trade_id).execute()
        return True
    except Exception as e:
        st.error(f"Error al eliminar: {e}")
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
        return json.loads(content_clean)
    except Exception:
        return None

# ==========================================
# ESTILOS CSS
# ==========================================
def aplicar_estilos():
    css = """
    <style>
    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, sans-serif !important;
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
    div[data-baseweb="select"] > div {
        background-color: #121721 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.5) !important;
        border-radius: 8px !important;
    }
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #161b22 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 8px !important;
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
    .trade-card {
        background-color: #121721;
        border: 1px solid rgba(0, 242, 254, 0.3);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
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
    st.markdown("Activa tu acceso mediante **Binance Pay** para continuar usando el diario:")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"[🟡 Pagar $5 USD Mensual con Binance Pay]({LINK_BINANCE_INSCRIPCION})")
    with col2:
        st.markdown(f"[💎 Pagar $20 USD Anual con Binance Pay]({LINK_BINANCE_ANUAL})")

def render_auth():
    col = st.columns([1.2, 1])
    with col[0]:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
    with col[1]:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
        with tab_login:
            login_email = st.text_input("Correo", key="login_email")
            login_pass = st.text_input("Contraseña", type="password", key="login_pass")
            if st.button("Ingresar"):
                try:
                    client = get_supabase_client()
                    res = client.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                    st.session_state.authenticated = True
                    st.session_state.user = res.user
                    st.rerun()
                except Exception as err:
                    st.error(f"Error: {err}")
        with tab_register:
            reg_email = st.text_input("Correo Nuevo", key="reg_email")
            reg_pass = st.text_input("Contraseña Nueva", type="password", key="reg_pass")
            if st.button("Registrarse"):
                try:
                    client = get_supabase_client()
                    client.auth.sign_up({"email": reg_email, "password": reg_pass})
                    st.success("¡Cuenta creada! Inicia sesión.")
                except Exception as e:
                    st.error(f"Error: {e}")

def render_sidebar(estado_sub):
    with st.sidebar:
        st.markdown("### 👤 Perfil Trader")
        user = st.session_state.user
        st.caption(f"`{user.email if user else ''}`")
        st.info(estado_sub)
        if st.button("🚪 Cerrar Sesión"):
            get_supabase_client().auth.sign_out()
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

def render_dashboard():
    tiene_acceso, estado_sub, _ = evaluar_suscripcion(st.session_state.user)
    render_sidebar(estado_sub)

    if not tiene_acceso:
        render_paywall()
        return

    user_id = st.session_state.user.id
    trades_db = cargar_trades_usuario(user_id)
    df_trades = pd.DataFrame(trades_db)

    st.markdown("## ⚡ Journaling & AI Trading Audit")

    tab1, tab2, tab3 = st.tabs([
        "➕ Registrar Trade", 
        "📅 Track Record & Historial Visual", 
        "📊 Dashboard & Tabla General"
    ])

    # --- TAB 1: REGISTRAR TRADE ---
    with tab1:
        col1, col2 = st.columns([1.2, 1])

        with col2:
            st.markdown("### 🖼️ Capturas del Gráfico")
            upload_before = st.file_uploader("1️⃣ Screenshot ANTES (Setup)", type=["png", "jpg", "jpeg"])
            upload_after = st.file_uploader("2️⃣ Screenshot DESPUÉS (Resultado)", type=["png", "jpg", "jpeg"])

            if upload_before:
                st.image(upload_before, caption="Vista Previa Antes", use_container_width=True)
                if st.button("🧠 Escanear Valores con IA"):
                    with st.spinner("Escaneando gráfico..."):
                        ext = analizar_captura_tradingview(upload_before.getvalue())
                        if ext:
                            st.session_state.auto_entry = ext.get("entry", 0.0)
                            st.session_state.auto_sl = ext.get("sl", 0.0)
                            st.session_state.auto_tp = ext.get("tp", 0.0)
                            st.toast("¡Valores extraídos!", icon="✨")
                            st.rerun()

            if upload_after:
                st.image(upload_after, caption="Vista Previa Después", use_container_width=True)

            monto_pnl = st.number_input("Ganancia / Pérdida ($USD):", value=0.0, step=10.0)

        with col1:
            st.markdown("### 📝 Parámetros del Trade")
            fecha_op = st.date_input("Fecha", datetime.date.today())
            par = st.selectbox("Activo", LISTA_ACTIVOS)
            resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"])
            emocion = st.selectbox("Emoción", ["Disciplinado 🧘", "Ansioso ⚡", "FOMO 🚀", "Venganza 🛑"])

            if st.button("💾 Guardar Trade"):
                with st.spinner("Procesando imágenes y guardando..."):
                    img_b64_before = procesar_imagen_b64(upload_before)
                    img_b64_after = procesar_imagen_b64(upload_after)

                    nuevo_trade = {
                        "fecha": str(fecha_op),
                        "par": par,
                        "resultado": resultado,
                        "emocion": emocion,
                        "beneficio_usd": monto_pnl,
                        "trades_cant": 1,
                        "img_before": img_b64_before,
                        "img_after": img_b64_after
                    }

                    if guardar_trade_supabase(user_id, nuevo_trade):
                        st.success("¡Trade guardado exitosamente con sus imágenes!")
                        st.rerun()

    # --- TAB 2: TRACK RECORD Y GALERÍA ---
    with tab2:
        st.markdown("### 🖼️ Registros con Imagen Antes y Después")
        
        if not df_trades.empty:
            for idx, row in df_trades.iterrows():
                st.markdown('<div class="trade-card">', unsafe_allow_html=True)
                c_info, c_before, c_after = st.columns([2, 3, 3])

                with c_info:
                    st.markdown(f"### {row.get('par', 'N/A')}")
                    st.markdown(f"**Fecha:** `{row.get('fecha', 'N/A')}`")
                    st.markdown(f"**Resultado:** {row.get('resultado', 'N/A')}")
                    pnl = row.get('beneficio_usd', 0.0)
                    color = "#34d399" if pnl >= 0 else "#f87171"
                    st.markdown(f"**PnL:** <h4 style='color:{color}; font-weight:bold; margin:0;'>${pnl:,.2f} USD</h4>", unsafe_allow_html=True)
                    st.markdown(f"**Estado Emocional:** {row.get('emocion', 'N/A')}")

                with c_before:
                    st.markdown("**📸 ANTES DEL TRADE**")
                    img_b = row.get("img_before")
                    if img_b and str(img_b).startswith("data:image"):
                        st.image(img_b, use_container_width=True)
                    else:
                        st.info("Sin imagen del Antes")

                with c_after:
                    st.markdown("**📸 DESPUÉS DEL TRADE**")
                    img_a = row.get("img_after")
                    if img_a and str(img_a).startswith("data:image"):
                        st.image(img_a, use_container_width=True)
                    else:
                        st.info("Sin imagen del Después")

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Aún no tienes operaciones registradas.")

    # --- TAB 3: TABLA DE DATOS CON IMÁGENES ---
    with tab3:
        st.markdown("### 📊 Tabla de Registros Interactiva")
        if not df_trades.empty:
            cols_mostrar = ['fecha', 'par', 'resultado', 'beneficio_usd', 'emocion', 'img_before', 'img_after']
            df_display = df_trades[[c for c in cols_mostrar if c in df_trades.columns]].copy()

            # Renderizado de la tabla con miniatura de imágenes
            st.dataframe(
                df_display,
                column_config={
                    "img_before": st.column_config.ImageColumn("Foto ANTES", help="Vista previa del setup"),
                    "img_after": st.column_config.ImageColumn("Foto DESPUÉS", help="Resultado visual"),
                    "beneficio_usd": st.column_config.NumberColumn("PnL ($)", format="$%.2f")
                },
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")
            with st.expander("🗑️ Eliminar una Operación"):
                if 'id' in df_trades.columns:
                    trade_id = st.selectbox("Selecciona ID a borrar:", df_trades['id'].tolist())
                    if st.button("❌ Eliminar Trade"):
                        if eliminar_trade_supabase(trade_id):
                            st.toast("Operación eliminada", icon="✅")
                            st.rerun()

if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
