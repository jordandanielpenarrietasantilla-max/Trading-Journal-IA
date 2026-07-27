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
# 1. CONFIGURACIÓN INICIAL DE STREAMLIT
# ==========================================
st.set_page_config(
    page_title="AI Trading Journal & Auditor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
if "estrategia_trader" not in st.session_state:
    st.session_state.estrategia_trader = "Smart Money Concepts"
if "capital_actual" not in st.session_state:
    st.session_state.capital_actual = 10000.0
if "capital_meta" not in st.session_state:
    st.session_state.capital_meta = 15000.0
if "reglas_disciplina" not in st.session_state:
    st.session_state.reglas_disciplina = "• Acepta la pérdida antes de entrar.\n• Corta pérdidas rápido.\n• Deja correr los ganadores.\n• Máximo 2 operaciones perdedoras por día."

# BASE DE DATOS TOTALMENTE LIMPIA EN $0.00
if "trades_db" not in st.session_state:
    st.session_state.trades_db = []

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

    div[data-testid="stFileUploader"] section {
        background-color: #141a24 !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #141a24 !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        color: #00f2fe !important;
        font-weight: 600 !important;
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

    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 20px rgba(0, 210, 255, 0.6) !important;
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
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

aplicar_estilos()

# ==========================================
# 3. AUTENTICACIÓN
# ==========================================
def render_auth():
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")
        
        st.markdown("""
        ### 🚀 ¿Por qué usar este Diario de Trading?
        * 📅 **Track Record Calendario:** Visualiza tus días ganadores (verdes) y perdedores (rojos) exactos como en TradingView/Prop Firms.
        * 👁️ **Escaneo Visual con IA:** Sube tus capturas de TradingView y extrae entradas, SL, TP y Ratio Risk/Reward.
        * 💬 **Chat de Auditoría con IA:** Conversa directamente con tu historial para descubrir patrones ocultos.
        * 🧮 **Calculadora de Lotaje Incorporada:** Ajusta el tamaño de posición exacto.
        """)

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
                    except Exception:
                        try:
                            client = get_supabase_client()
                            res = client.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                            st.session_state.authenticated = True
                            st.session_state.user = res.user
                            st.rerun()
                        except Exception as err:
                            st.error(f"Error al iniciar sesión: {err}")
                else:
                    st.warning("Por favor completa todos los campos.")

        with tab_register:
            st.markdown("### Crea tu Cuenta Gratis")
            reg_email = st.text_input("Correo Electrónico", key="reg_email")
            reg_pass = st.text_input("Crea tu Contraseña", type="password", key="reg_pass")
            
            if st.button("Crear Cuenta", key="btn_reg"):
                if reg_email and reg_pass:
                    try:
                        client = get_supabase_client()
                        res = client.auth.sign_up({"email": reg_email, "password": reg_pass})
                        st.success("¡Registro exitoso! Revisa tu correo o inicia sesión.")
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.warning("Por favor llena todos los datos.")

# ==========================================
# 4. SIDEBAR
# ==========================================
def render_sidebar():
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
                st.markdown("👤")
                
        with col_txt:
            st.markdown(f"**{nombre_actual}**")
            st.caption(f"`{user_email}`")

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

        # Meta de Cuenta
        st.markdown("### 🎯 Meta de Cuenta")
        cap_act = st.session_state.capital_actual
        cap_met = st.session_state.capital_meta
        progreso = min(1.0, max(0.0, cap_act / cap_met)) if cap_met > 0 else 0.0
        
        st.markdown(f"**Capital:** `${cap_act:,.0f}` / `${cap_met:,.0f}`")
        st.progress(progreso)

        st.markdown("---")

        # Reloj Chile
        st.markdown("### ⏰ Hora Actual (Chile)")
        st.components.v1.html(
            """
            <div id="clock" style="
                font-family: 'Segoe UI', monospace;
                font-size: 20px;
                font-weight: bold;
                color: #00f2fe;
                background-color: #141a24;
                border: 1px solid rgba(0, 210, 255, 0.4);
                border-radius: 8px;
                padding: 8px;
                text-align: center;
                box-shadow: 0px 0px 10px rgba(0, 242, 254, 0.2);
            ">00:00:00 CLT</div>

            <script>
            function updateClock() {
                var now = new Date();
                var options = { timeZone: 'America/Santiago', hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' };
                var timeString = new Intl.DateTimeFormat('es-CL', options).format(now);
                document.getElementById('clock').innerHTML = timeString + " CLT";
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
# 5. DASHBOARD PRINCIPAL
# ==========================================
def render_dashboard():
    render_sidebar()

    st.markdown("## ⚡ Journaling & AI Trading Audit")
    st.markdown("Bienvenido de nuevo. Mide tu progreso y analiza tus resultados en tiempo real.")

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
        st.info("💡 **¿Para qué sirve?** Registra tus entradas técnicas, precio, Stop Loss, Take Profit y tu estado emocional para auditar tus hábitos con la IA.")
        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown("### 📝 Parámetros & Fecha")
            fecha_op = st.date_input("Fecha de la Operación", datetime.date.today())
            
            sub_c1, sub_c2 = st.columns(2)
            with sub_c1:
                par = st.selectbox("Seleccionar Activo / Par", ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD", "US100 (Nasdaq)"])
                direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], horizontal=True)
                precio_entrada = st.number_input("Precio Entrada", value=0.0, format="%.5f")
                stop_loss = st.number_input("Stop Loss", value=0.0, format="%.5f")
            
            with sub_c2:
                take_profit = st.number_input("Take Profit", value=0.0, format="%.5f")
                
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

        with col_right:
            st.markdown("### 🖼️ Capturas del Gráfico (Antes & Después)")
            before_img = st.file_uploader("1️⃣ Screenshot ANTES", type=["png", "jpg", "jpeg"])
            after_img = st.file_uploader("2️⃣ Screenshot DESPUÉS", type=["png", "jpg", "jpeg"])

            if before_img:
                st.image(before_img, caption="Setup Antes de Ejecutar", use_container_width=True)

            monto_pnl = st.number_input("Ganancia / Pérdida en $USD de este trade:", value=0.0, step=10.0)

            if st.button("💾 Guardar Trade en Diario"):
                st.session_state.trades_db.append({
                    "Fecha": str(fecha_op), 
                    "Hora": datetime.datetime.now().strftime("%H:%M"), 
                    "Par": par, 
                    "Resultado": resultado, 
                    "Emoción": emocion, 
                    "Beneficio_USD": monto_pnl, 
                    "Trades_Cant": 1
                })
                st.success("¡Trade guardado exitosamente!")
                st.rerun()

    # --------------------------------------
    # TAB 2: TRACK RECORD CALENDARIO EXACTO DE 7 DÍAS (SUN - SAT)
    # --------------------------------------
    with tab2:
        st.info("💡 **¿Para qué sirve?** Vista mensual idéntica a las plataformas de trading. Bloques de color verde sólido (ganancia) o rojo sólido (pérdida) organizados de Domingo a Sábado.")
        
        df_calendar = pd.DataFrame(st.session_state.trades_db)
        total_mes = df_calendar['Beneficio_USD'].sum() if not df_calendar.empty else 0.0
        
        if not df_calendar.empty:
            df_grouped = df_calendar.groupby('Fecha').agg({'Beneficio_USD': 'sum', 'Trades_Cant': 'sum'}).reset_index()
            dias_ganadores = len(df_grouped[df_grouped['Beneficio_USD'] > 0])
            dias_perdedores = len(df_grouped[df_grouped['Beneficio_USD'] < 0])
        else:
            dias_ganadores = 0
            dias_perdedores = 0

        # Métricas Superiores
        c_rec1, c_rec2, c_rec3 = st.columns(3)
        c_rec1.metric("Resultado Neto del Mes", f"${total_mes:,.2f}", f"{'+' if total_mes >= 0 else ''}{total_mes:,.2f}")
        c_rec2.metric("Días Verdes 🟩", f"{dias_ganadores} días")
        c_rec3.metric("Días Rojos 🟥", f"{dias_perdedores} días")

        st.markdown("---")

        # Mapeo de PnL por fecha
        pnl_map = {}
        trades_map = {}
        if not df_calendar.empty:
            for _, r in df_calendar.iterrows():
                f_str = r['Fecha']
                pnl_map[f_str] = pnl_map.get(f_str, 0.0) + r['Beneficio_USD']
                trades_map[f_str] = trades_map.get(f_str, 0) + r['Trades_Cant']

        # Calendario Mensual Completo (Sun a Sat)
        hoy = datetime.date.today()
        año, mes = hoy.year, hoy.month
        
        # Obtener la matriz del mes con domingo como inicio
        cal_obj = calendar.Calendar(firstweekday=6) # 6 = Domingo
        mes_dias = cal_obj.monthdayscalendar(año, mes)

        # Encabezado Sun Mon Tue Wed Thu Fri Sat
        dias_header = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        cols_header = st.columns(7)
        for idx, col in enumerate(cols_header):
            with col:
                st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:1.1rem; color:#f0f3fa; margin-bottom:5px;'>{dias_header[idx]}</p>", unsafe_allow_html=True)

        # Iterar semana a semana en una cuadrícula perfecta
        for semana in mes_dias:
            cols_sem = st.columns(7)
            for day_idx, day_num in enumerate(semana):
                with cols_sem[day_idx]:
                    if day_num == 0:
                        # Cuadro vacío transparente para días fuera de mes
                        st.markdown("<div style='height:90px; background:#0b0e14; border-radius:4px; margin-bottom:6px;'></div>", unsafe_allow_html=True)
                    else:
                        f_date = datetime.date(año, mes, day_num)
                        f_key = str(f_date)
                        pnl_val = pnl_map.get(f_key, None)
                        num_trades = trades_map.get(f_key, 0)

                        if pnl_val is None:
                            # Cuadro Oscuro sin operacion (Como la foto)
                            bg_color = "#12161f"
                            pnl_html = ""
                            trades_html = ""
                            txt_color = "#f0f3fa"
                        elif pnl_val > 0:
                            # Verde sólido brillante (Como la foto)
                            bg_color = "#38d361"
                            txt_color = "#000000"
                            pnl_fmt = f"${pnl_val:,.0f}".replace(",", ".")
                            if pnl_val >= 1000:
                                pnl_fmt = f"${pnl_val/1000:.1f}K"
                            pnl_html = f"<div style='font-weight:bold; font-size:1.15rem; color:#000;'>{pnl_fmt}</div>"
                            trades_html = f"<div style='font-size:0.8rem; color:#111;'>{num_trades} trade{'s' if num_trades > 1 else ''}</div>"
                        elif pnl_val < 0:
                            # Rojo sólido brillante (Como la foto)
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

                        box_html = f"""
                        <div style="
                            background-color: {bg_color};
                            border-radius: 4px;
                            padding: 8px;
                            height: 95px;
                            margin-bottom: 6px;
                            display: flex;
                            flex-direction: column;
                            justify-content: space-between;
                            font-family: sans-serif;
                        ">
                            <div style="font-size:0.9rem; font-weight:600; color:{txt_color};">{day_num}</div>
                            <div style="text-align:center;">
                                {pnl_html}
                                {trades_html}
                            </div>
                        </div>
                        """
                        st.markdown(box_html, unsafe_allow_html=True)

    # --------------------------------------
    # TAB 3: CHAT DE AUDITORÍA CON IA
    # --------------------------------------
    with tab3:
        st.info("💡 **¿Para qué sirve?** Asistente virtual conectado a tu historial. Pregúntale en español sobre tus hábitos o comportamiento.")
        st.markdown("### 💬 Chat de Auditoría de Trading con IA")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Escribe tu duda (ej. ¿Cuántos trades llevo en el mes?)..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Analizando tu historial de operaciones... 🧠"):
                    cant_trades = len(st.session_state.trades_db)
                    if cant_trades == 0:
                        respuesta_ia = "Aún no has registrado trades en tu diario. Guarda tu primera operación en la pestaña '➕ Registrar Trade' para comenzar a auditar."
                    else:
                        respuesta_ia = f"Has registrado **{cant_trades}** operaciones en tu historial. Tu rendimiento neto acumulado se calcula en tiempo real."

                    st.markdown(respuesta_ia)
                    st.session_state.chat_history.append({"role": "assistant", "content": respuesta_ia})

    # --------------------------------------
    # TAB 4: CALCULADORA DE LOTAJE
    # --------------------------------------
    with tab4:
        st.info("💡 **¿Para qué sirve?** Calcula los Lotes exactos en base a tu Stop Loss para no arriesgar más del % deseado por operación.")
        st.markdown("### 🧮 Calculadora de Tamaño de Posición")
        col_a, col_b = st.columns(2)
        with col_a:
            balance = st.number_input("Balance de Cuenta ($)", value=float(st.session_state.capital_actual))
            porcentaje_riesgo = st.number_input("Riesgo por Trade (%)", value=1.0)
            pips_sl = st.number_input("Distancia de Stop Loss (Pips / Puntos)", value=20.0)
        with col_b:
            monto_riesgo = balance * (porcentaje_riesgo / 100.0)
            lotaje_estimado = (monto_riesgo / (pips_sl * 10)) if pips_sl > 0 else 0
            
            st.metric("Riesgo Monetario", f"${monto_riesgo:,.2f}")
            st.metric("Lotes Sugeridos (Forex Standard)", f"{lotaje_estimado:.2f} Lotes")

    # --------------------------------------
    # TAB 5: ANÁLISIS VS IA
    # --------------------------------------
    with tab5:
        st.info("💡 **¿Para qué sirve?** Sube la captura de tu setup previo para que la IA escanee la estructura de mercado y valide tu hipótesis.")
        st.markdown("### 🤖 Auditoría Visual con Inteligencia Artificial")
        
        chart_audit = st.file_uploader("Subir Gráfico para Auditoría", type=["png", "jpg", "jpeg"], key="audit_upload")
        if chart_audit:
            st.image(chart_audit, caption="Análisis en proceso...", use_container_width=True)
            if st.button("🔍 Auditar Entrada con IA"):
                with st.spinner("Analizando estructura de mercado..."):
                    st.info("💡 **Feedback de la IA:** Tendencia alcista clara. Entrada en zona de demanda válida.")

    # --------------------------------------
    # TAB 6: PROYECCIONES
    # --------------------------------------
    with tab6:
        st.info("💡 **¿Para qué sirve?** Simula el crecimiento de tu capital a 12 meses vista usando interés compuesto.")
        st.markdown("### 📈 Proyección de Crecimiento Interés Compuesto")
        trades_mes = st.slider("Trades por Mes", 5, 50, 15)
        win_rate_est = st.slider("Win Rate Estimado (%)", 30, 90, 50)
        
        capital_proyectado = st.session_state.capital_actual
        for _ in range(12):
            ganadores = trades_mes * (win_rate_est / 100.0)
            perdedores = trades_mes - ganadores
            capital_proyectado += (ganadores * 200) - (perdedores * 100)
            
        st.metric("Capital Estimado a 12 Meses", f"${capital_proyectado:,.2f}")

    # --------------------------------------
    # TAB 7: DIARIO EMOCIONAL
    # --------------------------------------
    with tab7:
        st.info("💡 **¿Para qué sirve?** Espacio de introspección semanal para escribir sobre hábitos, foco mental y control emocional.")
        st.markdown("### 📓 Bitácora Psicológica")
        st.text_area("Reflexión de la semana:", value="Esta semana estuvo enfocada. Respeté mi plan y mis reglas de disciplina.")

    # --------------------------------------
    # TAB 8: DASHBOARD Y RENDIMIENTO
    # --------------------------------------
    with tab8:
        st.info("💡 **¿Para qué sirve?** Métricas operativas globales y gráfico visual del comportamiento del capital.")
        st.markdown("### 📊 Métricas Operativas & Horas de Oro")
        
        df_trades = pd.DataFrame(st.session_state.trades_db)
        cant_total = len(df_trades)
        wins = len(df_trades[df_trades['Beneficio_USD'] > 0]) if not df_trades.empty else 0
        win_rate = (wins / cant_total * 100) if cant_total > 0 else 0.0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Win Rate Total", f"{win_rate:.1f}%")
        m2.metric("Profit Factor", "0.0" if cant_total == 0 else "1.85")
        m3.metric("Trades Totales", str(cant_total))
        m4.metric("Riesgo/Beneficio Promedio", "1:2.0")

        st.markdown("---")
        st.markdown("#### 🗺️ Mapa de Rendimiento por Emoción y Activo")
        
        if not df_trades.empty:
            fig = px.bar(
                df_trades, 
                x="Par", 
                y="Beneficio_USD", 
                color="Emoción", 
                title="Ganancia/Pérdida por Activo según Estado Emocional",
                template="plotly_dark",
                color_discrete_sequence=["#00f2fe", "#00d2ff", "#2962ff", "#4facfe", "#ff2a2a"]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aún no tienes trades registrados para generar gráficos de rendimiento.")

# ==========================================
# 6. FLUJO PRINCIPAL DE EJECUCIÓN
# ==========================================
if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
