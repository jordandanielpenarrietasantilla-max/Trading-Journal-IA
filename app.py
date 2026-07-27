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

# 🔗 TUS ENLACES REALES
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
# 2. ESTILOS CSS PERSONALIZADOS
# ==========================================
def aplicar_estilos():
    css = """
    <style>
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

    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0, 210, 255, 0.2) !important;
    }

    div[data-testid="stExpander"] {
        background: rgba(15, 20, 30, 0.9) !important;
        border: 1px solid rgba(0, 210, 255, 0.3) !important;
        border-radius: 10px !important;
        margin-bottom: 12px !important;
    }

    div[data-testid="stFileUploader"] {
        background-color: #141a24 !important;
        border: 1px dashed #00f2fe !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #141a24 !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
        border-radius: 8px !important;
    }

    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background-color: #141a24 !important;
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
        transition: all 0.3s ease !important;
    }

    .paywall-card {
        background-color: #141a24;
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
# 3. VERIFICACIÓN DE DÍAS DE PRUEBA / PRO
# ==========================================
def evaluar_suscripcion(user):
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
# 5. AUTENTICACIÓN
# ==========================================
def render_auth():
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")

    with col2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

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

# ==========================================
# 6. SIDEBAR
# ==========================================
def render_sidebar(estado_sub):
    with st.sidebar:
        st.markdown("### 👤 Perfil Trader")
        
        user = st.session_state.user
        user_email = user.email if user else "trader@ejemplo.com"
        metadata = user.user_metadata if (user and hasattr(user, 'user_metadata') and user.user_metadata) else {}
        nombre_actual = metadata.get("username", st.session_state.get("nombre_trader", "Trader Pro"))

        st.markdown(f"**{nombre_actual}**")
        st.caption(f"`{user_email}`")

        if "PRO" in estado_sub:
            st.success(f"💎 {estado_sub}")
        else:
            st.warning(f"⏳ {estado_sub}")

        st.markdown("---")

        if st.button("🚪 Cerrar Sesión"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()

# ==========================================
# 7. DASHBOARD PRINCIPAL
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
    # TAB 1: REGISTRAR TRADE
    # --------------------------------------
    with tab1:
        st.info("💡 **Tip con IA:** Al subir una captura de TradingView con la herramienta de Posición (Larga/Corta), la IA escaneará la imagen y **autocompletará los precios de Entrada, Stop Loss y Take Profit** por ti.")
        
        col_left, col_right = st.columns([1, 1])

        with col_right:
            st.markdown("### 🖼️ Capturas del Gráfico (Antes & Después)")
            before_img = st.file_uploader("1️⃣ Screenshot ANTES (Escaneo Automático con IA)", type=["png", "jpg", "jpeg"], key="upload_before")
            after_img = st.file_uploader("2️⃣ Screenshot DESPUÉS", type=["png", "jpg", "jpeg"])

            if before_img:
                st.image(before_img, caption="Setup Antes de Ejecutar", use_container_width=True)
                
                # Botón para activar el escáner IA
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

            monto_pnl = st.number_input("Ganancia / Pérdida en $USD de este trade:", value=0.0, step=10.0)

        with col_left:
            st.markdown("### 📝 Parámetros & Fecha")
            fecha_op = st.date_input("Fecha de la Operación", datetime.date.today())
            
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                par = st.selectbox("Seleccionar Activo / Par", ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD", "US100 (Nasdaq)"])
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
                nuevo_trade = {
                    "fecha": str(fecha_op), 
                    "hora": datetime.datetime.now().strftime("%H:%M"), 
                    "par": par, 
                    "resultado": resultado, 
                    "emocion": emocion, 
                    "beneficio_usd": float(monto_pnl), 
                    "trades_cant": 1
                }
                if guardar_trade_supabase(user_id, nuevo_trade):
                    # Resetear autocompletado
                    st.session_state.auto_entry = 0.0
                    st.session_state.auto_sl = 0.0
                    st.session_state.auto_tp = 0.0
                    st.success("¡Trade guardado exitosamente!")
                    st.rerun()

    # --------------------------------------
    # TAB 2: TRACK RECORD CALENDARIO
    # --------------------------------------
    with tab2:
        st.info("💡 **¿Para qué sirve?** Vista mensual estilo Prop Firm. Las ganancias/pérdidas y la cantidad exacta de trades se agrupan por día.")
        
        df_calendar = pd.DataFrame(trades_db)
        total_mes = df_calendar['beneficio_usd'].sum() if not df_calendar.empty else 0.0
        
        if not df_calendar.empty:
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
        if not df_calendar.empty:
            for _, r in df_calendar.iterrows():
                f_str = r['fecha']
                pnl_map[f_str] = pnl_map.get(f_str, 0.0) + r['beneficio_usd']
                # Contar exactamente 1 trade por cada registro real
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

    # --------------------------------------
    # TAB 3 A TAB 8 (RESTO DE HERRAMIENTAS)
    # --------------------------------------
    with tab3:
        st.markdown("### 💬 Chat de Auditoría de Trading con IA")
        st.caption("Escribe tus dudas sobre tu operativa.")
    with tab4:
        st.markdown("### 🧮 Calculadora de Tamaño de Posición")
    with tab5:
        st.markdown("### 🤖 Auditoría Visual con Inteligencia Artificial")
    with tab6:
        st.markdown("### 📈 Proyección de Crecimiento Interés Compuesto")
    with tab7:
        st.markdown("### 📓 Bitácora Psicológica")
    with tab8:
        st.markdown("### 📊 Métricas Operativas & Horas de Oro")

# ==========================================
# 8. FLUJO PRINCIPAL
# ==========================================
if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
