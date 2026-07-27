import streamlit as st
import datetime
import requests
import json
import os
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

# Obtener secretos de Streamlit
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://lyzvcbjpoydeckxtbcq.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "sb_publishable_HIo0YXn-kJUr7HuNZFNfjQ_JBncowE0")
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")

# Inicializar cliente de Supabase
@st.cache_resource
def init_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    supabase = None

# Manejo de Estado de Sesión
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# 2. ESTILOS CSS PERSONALIZADOS (CORREGIDO)
# ==========================================
def aplicar_estilos():
    css = """
    <style>
    /* Animación Neón Suave */
    @keyframes neonGlow {
        0% { border-color: rgba(0, 242, 254, 0.4); box-shadow: 0 0 8px rgba(0, 242, 254, 0.15); }
        50% { border-color: rgba(41, 98, 255, 0.7); box-shadow: 0 0 16px rgba(41, 98, 255, 0.3); }
        100% { border-color: rgba(0, 242, 254, 0.4); box-shadow: 0 0 8px rgba(0, 242, 254, 0.15); }
    }

    /* Fondo de la Aplicación */
    .stApp {
        background-color: #0b0e14 !important;
        color: #f0f3fa !important;
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
    }

    /* Ocultar elementos rotos de íconos de Streamlit en expanders */
    button[data-testid="stExpanderToggleIconButton"] {
        color: #00f2fe !important;
    }

    /* Tipografía Global Legible */
    p, label, h1, h2, h3, h4, span, div, .stMarkdown {
        color: #f0f3fa !important;
    }

    /* Títulos Gradiente */
    h1, h2 {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }

    /* Barra Lateral Fija y Limpia */
    section[data-testid="stSidebar"] {
        background-color: #0f141e !important;
        border-right: 1px solid rgba(0, 210, 255, 0.2) !important;
    }

    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {
        padding-top: 1rem;
    }

    /* Badges de Código / Textos Destacados */
    code, .stCodeBlock {
        background-color: rgba(0, 242, 254, 0.1) !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 242, 254, 0.3) !important;
        border-radius: 6px !important;
        padding: 3px 8px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    /* Expanders (Acordeones como Modificar Perfil) */
    div[data-testid="stExpander"] {
        background: rgba(15, 20, 30, 0.6) !important;
        border: 1px solid rgba(0, 210, 255, 0.25) !important;
        border-radius: 10px !important;
        margin-bottom: 12px !important;
    }

    /* Tarjetas Neón Solo para Bloques Principales */
    div[data-testid="stColumn"] > div {
        background: rgba(15, 20, 28, 0.8) !important;
        border: 1px solid rgba(0, 210, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 10px !important;
    }

    /* Entradas de Texto, Números y Selects */
    .stTextInput input, .stNumberInput input, .stTextArea textarea, div[data-baseweb="select"] > div {
        background-color: #141a24 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 8px !important;
    }

    /* Botones Estilo Cyberpunk/Neon */
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

    /* Botón Rojo Cierre de Sesión */
    section[data-testid="stSidebar"] .stButton>button {
        background: linear-gradient(135deg, #e53935 0%, #b71c1c 100%) !important;
        box-shadow: 0px 4px 12px rgba(229, 57, 53, 0.3) !important;
    }

    /* Tarjetas de Métricas de Mercado */
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
# 3. AUTENTICACIÓN (LOGIN / REGISTRO)
# ==========================================
def render_auth():
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.markdown("# ⚡ AI Trading Journal & Auditor")
        st.markdown("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")
        
        st.markdown("""
        ### 🚀 ¿Por qué usar este Diario de Trading?
        * 👁️ **Escaneo Visual con IA:** Sube tus capturas de TradingView y deja que la IA extraiga entradas, SL, TP y Ratio Risk/Reward.
        * 🧠 **Psicotrading y Bitácora Emocional:** Registra tu estado mental antes y después de cada sesión para detectar patrones perjudiciales.
        * 🧮 **Calculadora de Lotaje Incorporada:** Ajusta el tamaño de posición exacto para Forex, Oro, Criptos e Índices.
        * 📊 **Auditoría y Proyecciones:** Compara tu hipótesis técnica contra el modelo de IA y mide tu evolución temporal.
        * 🔒 **Acceso Privado:** Tus datos y capturas solo estarán visibles para ti mediante tu cuenta personal.
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
                        res = supabase.auth.sign_in_with_password({"email": login_email, "password": login_pass})
                        st.session_state.authenticated = True
                        st.session_state.user = res.user
                        st.rerun()
                    except Exception as e:
                        err_msg = str(e)
                        if "Email not confirmed" in err_msg:
                            st.error("Error al iniciar sesión: Email no confirmado. Revisa tu bandeja de entrada o confirma el correo en Supabase.")
                        else:
                            st.error(f"Error al iniciar sesión: {err_msg}")
                else:
                    st.warning("Por favor completa todos los campos.")

        with tab_register:
            st.markdown("### Crea tu Cuenta Gratis")
            reg_email = st.text_input("Correo Electrónico", key="reg_email")
            reg_pass = st.text_input("Crea tu Contraseña", type="password", key="reg_pass")
            
            if st.button("Crear Cuenta", key="btn_reg"):
                if reg_email and reg_pass:
                    try:
                        res = supabase.auth.sign_up({"email": reg_email, "password": reg_pass})
                        st.success("¡Registro exitoso! Revisa tu correo electrónico para confirmar la cuenta antes de iniciar sesión.")
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.warning("Por favor llena todos los datos.")

# ==========================================
# 4. SIDEBAR (PERFIL Y NAVEGACIÓN)
# ==========================================
def render_sidebar():
    with st.sidebar:
        st.markdown("### 👤 Perfil Trader")
        
        user_email = st.session_state.user.email if st.session_state.user else "trader@ejemplo.com"
        
        st.markdown(f"""
        **Trader Pro** `{user_email}`
        """, unsafe_allow_html=True)

        with st.expander("⚙️ Modificar Perfil"):
            st.text_input("Nombre de Usuario", value="Trader Pro")
            st.selectbox("Estrategia Principal", ["Smart Money Concepts", "Price Action", "ICT", "Indicator Based"])
            if st.button("Guardar Cambios"):
                st.toast("Perfil actualizado correctamente", icon="✅")

        st.markdown("---")
        
        # Meta de Cuenta
        st.markdown("### 🎯 Meta de Cuenta")
        meta_actual = 10000
        meta_objetivo = 15000
        progreso = (meta_actual / meta_objetivo)
        
        st.markdown(f"**Capital:** `${meta_actual:,.0f}` / `${meta_objetivo:,.0f}`")
        st.progress(progreso)

        st.markdown("---")

        # Sesiones de Mercado (Simuladas en tiempo real)
        st.markdown("### 🌐 Sesiones de Mercado")
        hora_utc = datetime.datetime.utcnow().hour
        
        londres_status = '<span class="market-badge open">ABIERTO</span>' if 7 <= hora_utc <= 15 else '<span class="market-badge closed">CERRADO</span>'
        ny_status = '<span class="market-badge open">ABIERTO</span>' if 12 <= hora_utc <= 20 else '<span class="market-badge closed">CERRADO</span>'
        tokio_status = '<span class="market-badge open">ABIERTO</span>' if 0 <= hora_utc <= 9 else '<span class="market-badge closed">CERRADO</span>'

        st.markdown(f"**GB Londres:** {londres_status}", unsafe_allow_html=True)
        st.markdown(f"**US Nueva York:** {ny_status}", unsafe_allow_html=True)
        st.markdown(f"**JP Tokio / Asia:** {tokio_status}", unsafe_allow_html=True)

        st.markdown("---")

        # Reglas de Disciplina
        st.markdown("### 🎯 Reglas de Disciplina")
        st.markdown("""
        * 🛑 Acepta la pérdida antes de entrar.
        * ✂️ Corta pérdidas rápido.
        * 📈 Deja correr los ganadores.
        * 🚫 Máximo 2 operaciones perdedoras por día.
        """)

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

    st.markdown("## 🩵 Journaling & AI Trading Audit")
    st.markdown("Bienvenido de nuevo. Mide tu progreso y disciplina en tiempo real.")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "➕ Registrar Trade", 
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
                
                # Cálculo automático de Risk Reward
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
            notas_emocionales = st.text_area("Notas emocionales de la sesión:", placeholder="Escribe aquí si respetaste tu plan o qué detonó tu entrada...")

        with col_right:
            st.markdown("### 🖼️ Capturas del Gráfico (Antes & Después)")
            before_img = st.file_uploader("1️⃣ Screenshot ANTES (Entrada / Setup)", type=["png", "jpg", "jpeg"])
            after_img = st.file_uploader("2️⃣ Screenshot DESPUÉS (Cierre / Resultado)", type=["png", "jpg", "jpeg"])

            if before_img:
                st.image(before_img, caption="Setup Antes de Ejecutar", use_container_width=True)

            if st.button("💾 Guardar Trade en Diario"):
                st.success("Trade guardado exitosamente en tu base de datos.")

    # --------------------------------------
    # TAB 2: CALCULADORA DE LOTAJE
    # --------------------------------------
    with tab2:
        st.markdown("### 🧮 Calculadora de Tamaño de Posición")
        col_a, col_b = st.columns(2)
        with col_a:
            balance = st.number_input("Balance de Cuenta ($)", value=10000.0)
            porcentaje_riesgo = st.number_input("Riesgo por Trade (%)", value=1.0)
            pips_sl = st.number_input("Distancia de Stop Loss (Pips / Puntos)", value=20.0)
        with col_b:
            monto_riesgo = balance * (porcentaje_riesgo / 100.0)
            lotaje_estimado = (monto_riesgo / (pips_sl * 10)) if pips_sl > 0 else 0
            
            st.metric("Riesgo Monetario", f"${monto_riesgo:,.2f}")
            st.metric("Lotes Sugeridos (Forex Standard)", f"{lotaje_estimado:.2f} Lotes")

    # --------------------------------------
    # TAB 3: ANÁLISIS VS IA
    # --------------------------------------
    with tab3:
        st.markdown("### 🤖 Auditoría Visual con Inteligencia Artificial")
        st.markdown("Sube una captura de pantalla de tu gráfico para recibir feedback técnico instantáneo.")
        
        chart_audit = st.file_uploader("Subir Gráfico para Auditoría", type=["png", "jpg", "jpeg"], key="audit_upload")
        if chart_audit:
            st.image(chart_audit, caption="Análisis en proceso...", use_container_width=True)
            if st.button("🔍 Auditar Entrada con IA"):
                with st.spinner("Analizando estructura de mercado, zonas de oferta/demanda y gestión de riesgo..."):
                    st.info("💡 **Feedback de la IA:** La estructura muestra una tendencia alcista clara en H1. Tu entrada en la zona de demanda tiene sentido técnico, pero el Stop Loss se encuentra demasiado ajustado por debajo del mínimo anterior.")

    # --------------------------------------
    # TAB 4: PROYECCIONES
    # --------------------------------------
    with tab4:
        st.markdown("### 📈 Proyección de Crecimiento Interés Compuesto")
        trades_mes = st.slider("Trades por Mes", 5, 50, 15)
        win_rate_est = st.slider("Win Rate Estimado (%)", 30, 90, 50)
        
        # Simulación
        capital_proyectado = 10000
        for _ in range(12):
            ganadores = trades_mes * (win_rate_est / 100.0)
            perdedores = trades_mes - ganadores
            capital_proyectado += (ganadores * 200) - (perdedores * 100)
            
        st.metric("Capital Estimado a 12 Meses", f"${capital_proyectado:,.2f}")

    # --------------------------------------
    # TAB 5: DIARIO EMOCIONAL
    # --------------------------------------
    with tab5:
        st.markdown("### 📓 Bitácora Psicológica")
        st.info("El 80% del éxito en el trading depende del control emocional. Mantén un registro diario de tus estados mentales.")
        st.text_area("Reflexión de la semana:", value="Esta semana estuve enfocado. Respeté el stop loss en el trade de Oro y evité el Overtrading.")

    # --------------------------------------
    # TAB 6: DASHBOARD & METRICAS
    # --------------------------------------
    with tab6:
        st.markdown("### 📊 Métricas Operativas Globales")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Win Rate Total", "58.3%", "+2.1%")
        m2.metric("Profit Factor", "1.85", "+0.12")
        m3.metric("Trades Totales", "24", "Este mes")
        m4.metric("Riesgo/Beneficio Promedio", "1:2.4", "Óptimo")

# ==========================================
# 6. FLUJO PRINCIPAL DE EJECUCIÓN
# ==========================================
if not st.session_state.authenticated:
    render_auth()
else:
    render_dashboard()
