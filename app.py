import streamlit as st
import datetime
import pandas as pd
import numpy as np

# 1. Configuración de la página
st.set_page_config(
    page_title="Journaling & AI Trading Audit",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Personalizado: Alto Contraste, Textos Nítidos y Botón Neón
st.markdown("""
<style>
    /* Fondo General Dark Mode */
    .stApp {
        background-color: #0b0e14 !important;
        color: #ffffff !important;
    }
    
    /* TODAS LAS ETIQUETAS Y TEXTOS EN BLANCO LUMINOSO */
    label, p, span, div, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* SUBTÍTULOS EN CIAN NEÓN */
    h2, h3 {
        color: #00f2fe !important;
        font-weight: 700 !important;
    }

    /* CAMPOS DE ENTRADA Y DESPLEGABLES (Alto Contraste) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }

    /* CAJAS DE TEXTO GRANDE (Notas) */
    textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }
    
    /* BOTÓN PARA ABRIR/CERRAR MENÚ (Sidebar) RESPLANDECIENTE NEÓN */
    button[data-testid="stSidebarCollapseButton"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"],
    header button {
        background: #00f2fe !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        box-shadow: 0px 0px 15px rgba(0, 242, 254, 1) !important;
        font-size: 16px !important;
    }

    /* PESTAÑAS (TABS) CLARAS Y VISIBLES */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22 !important;
        border-radius: 10px;
        padding: 6px;
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #c9d1d9 !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        border-radius: 6px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #00f2fe !important;
        border-bottom: 3px solid #00f2fe !important;
    }

    /* TARJETAS DE MÉTRICAS */
    .metric-card {
        background-color: #131b2e;
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value-green {
        font-size: 28px;
        font-weight: bold;
        color: #10b981 !important;
    }
    .metric-value-cyan {
        font-size: 28px;
        font-weight: bold;
        color: #00f2fe !important;
    }

    /* INSIGNIAS DINÁMICAS (VIP, PRUEBA, EXPIRADO) */
    .vip-badge {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        color: #000000 !important;
        font-weight: bold;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin-top: 8px;
    }
    .trial-badge {
        background: linear-gradient(90deg, #10b981, #34d399);
        color: #000000 !important;
        font-weight: bold;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin-top: 8px;
    }
    .expired-badge {
        background: #ef4444;
        color: #ffffff !important;
        font-weight: bold;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin-top: 8px;
    }

    /* CAJA DE CONSEJO CON IA */
    .info-box {
        background-color: #0d233a;
        border-left: 4px solid #00f2fe;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 20px;
    }

    /* BOTÓN PRINCIPAL DE GUARDAR */
    .stButton > button {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 12px rgba(0, 242, 254, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. MANTENIMIENTO DE ESTADO & USUARIO DINÁMICO DE SUPABASE
if "trades_db" not in st.session_state:
    st.session_state["trades_db"] = [
        {"fecha": "2026-07-27", "par": "XAU/USD", "tipo": "LONG", "pnl": 2500.00, "resultado": "WIN", "estado": "Disciplinado / Neutro"},
        {"fecha": "2026-07-25", "par": "EUR/USD", "tipo": "SHORT", "pnl": -300.00, "resultado": "LOSS", "estado": "Ansioso / FOMO"},
        {"fecha": "2026-07-20", "par": "BTC/USD", "tipo": "LONG", "pnl": 300.00, "resultado": "WIN", "estado": "Confiado"}
    ]

# Obtener usuario logueado en Supabase (si existe en la sesión)
user = st.session_state.get("user", None)

if user and hasattr(user, "email"):
    user_email = user.email
    # Cálculo dinámico de días desde el registro
    try:
        created_at = datetime.datetime.strptime(user.created_at[:10], "%Y-%m-%d")
        dias_registro = (datetime.datetime.now() - created_at).days
    except Exception:
        dias_registro = 0
        
    # Lógica de suscripción: 3 días de prueba o VIP si pagó
    is_vip_db = st.session_state.get("is_vip_paid", False)
    
    if is_vip_db:
        estado_plan = "⚡ VIP / PLAN PRO ACTIVO"
        badge_class = "vip-badge"
    elif dias_registro <= 3:
        dias_restantes = max(0, 3 - dias_registro)
        estado_plan = f"🎁 PRUEBA GRATUITA ({dias_restantes} DÍAS RESTANTES)"
        badge_class = "trial-badge"
    else:
        estado_plan = "🔴 PRUEBA EXPIRADA ($5/mes)"
        badge_class = "expired-badge"
else:
    # Fallback temporal si la sesión se reinicia o está en modo local
    user_email = st.session_state.get("user_email", "usuario@trading.com")
    estado_plan = "🎁 PRUEBA GRATUITA (3 DÍAS)"
    badge_class = "trial-badge"

# ------------------- SIDEBAR / PERFIL REAL Y SESIONES -------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=80)
    st.markdown("### 👤 Perfil de Usuario")
    
    # Muestra el correo dinámico del usuario real
    st.write(f"**Email:** `{user_email}`")
    
    # Muestra el estado del plan real (Prueba, VIP o Expirado)
    st.markdown(f'<span class="{badge_class}">{estado_plan}</span>', unsafe_allow_html=True)

    st.markdown("---")
    
    # Horario de Sesiones de Mercado
    st.markdown("#### 🕒 Sesiones de Mercado (UTC)")
    st.caption("🟢 **Londres:** Abierto (08:00 - 16:00)")
    st.caption("🟢 **Nueva York:** Abierto (13:00 - 21:00)")
    st.caption("🔴 **Tokio:** Cerrado (00:00 - 09:00)")
    st.caption("🔴 **Sídney:** Cerrado (22:00 - 07:00)")

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ------------------- ENCABEZADO PRINCIPAL -------------------
st.title("⚡ Journaling & AI Trading Audit")

# ------------------- PESTAÑAS PRINCIPALES -------------------
tabs = st.tabs([
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
with tabs[0]:
    st.markdown('<div class="info-box">💡 <b>Tip con IA:</b> Al subir una captura de TradingView con la herramienta de Posición (Larga/Corta), la IA escaneará la imagen y autocompletará los precios de Entrada, Stop Loss y Take Profit por ti.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 Parámetros & Fecha")
        fecha = st.date_input("Fecha de la Operación", datetime.date.today())
        activo = st.selectbox("Seleccionar Activo / Par", ["XAU/USD (Oro)", "EUR/USD", "GBP/USD", "BTC/USD", "US100 (Nasdaq)"])
        direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], horizontal=True)
        
        c_e, c_sl, c_tp = st.columns(3)
        with c_e:
            precio_entrada = st.number_input("Precio Entrada", value=0.0, format="%.5f")
        with c_sl:
            stop_loss = st.number_input("Stop Loss", value=0.0, format="%.5f")
        with c_tp:
            take_profit = st.number_input("Take Profit", value=0.0, format="%.5f")
            
        resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BE ⚪"])
        
        st.subheader("🧠 Psicotrading & Estado Emocional")
        estado_emocional = st.selectbox("¿Cómo te sentías?", ["Disciplinado / Neutro 🧘", "Ansioso / FOMO 😰", "Venganza / Rabia 😡", "Confiado 😎"])
        notas = st.text_area("Notas emocionales de la sesión", placeholder="Escribe aquí si respetaste tu plan...")

    with col2:
        st.subheader("🖼️ Capturas del Gráfico (Antes & Después)")
        st.file_uploader("1️⃣ Screenshot ANTES (Escaneo Automático con IA)", type=["png", "jpg", "jpeg"])
        st.file_uploader("2️⃣ Screenshot DESPUÉS", type=["png", "jpg", "jpeg"])
        pnl_trade = st.number_input("Ganancia / Pérdida en $USD de este trade:", value=0.0)

        if st.button("💾 Guardar Trade en Diario", type="primary", use_container_width=True):
            nuevo_trade = {
                "fecha": str(fecha),
                "par": activo,
                "tipo": "LONG" if "LONG" in direccion else "SHORT",
                "pnl": pnl_trade,
                "resultado": "WIN" if "WIN" in resultado else ("LOSS" if "LOSS" in resultado else "BE"),
                "estado": estado_emocional
            }
            st.session_state["trades_db"].append(nuevo_trade)
            st.success("¡Trade guardado exitosamente!")

# --- TAB 2: TRACK RECORD PNL ---
with tabs[1]:
    st.markdown('<div class="info-box">💡 <b>¿Para qué sirve?</b> Vista mensual estilo Prop Firm. Las ganancias/pérdidas y la cantidad exacta de trades se agrupan por día.</div>', unsafe_allow_html=True)
    
    col_m1, col_m2, col_m3 = st.columns(3)
    pnl_total = sum(t["pnl"] for t in st.session_state["trades_db"])
    dias_verdes = len([t for t in st.session_state["trades_db"] if t["pnl"] > 0])
    dias_rojos = len([t for t in st.session_state["trades_db"] if t["pnl"] < 0])
    
    with col_m1:
        st.markdown(f'<div class="metric-card"><div>Neto del Mes</div><div class="metric-value-green">${pnl_total:,.2f} USD</div></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><div>Días Verdes</div><div class="metric-value-cyan">{dias_verdes} días</div></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><div>Días Rojos</div><div style="color: #ef4444;" class="metric-value-cyan">{dias_rojos} días</div></div>', unsafe_allow_html=True)
        
    st.markdown("### 📅 Calendario de Rendimiento (Julio 2026)")
    st.info("🟢 **27 Julio:** +$2,500.00 USD (1 Trade) | 🟢 **20 Julio:** +$300.00 USD (1 Trade) | 🔴 **25 Julio:** -$300.00 USD (1 Trade)")

# --- TAB 3: CHAT IA & AUDITORÍA ---
with tabs[2]:
    st.subheader("💬 Chat de Auditoría de Trading con IA")
    st.caption("Consulta a tu asistente sobre tus hábitos, estadísticas o reglas operativas.")
    
    chat_container = st.container()
    with chat_container:
        st.chat_message("assistant").write(f"Has registrado {len(st.session_state['trades_db'])} operaciones con un resultado neto acumulado de **${pnl_total:,.2f} USD**. Tu tasa de acierto actual es del **66.6%**. ¿En qué área te gustaría enfocar tu auditoría de hoy?")
    
    user_query = st.chat_input("Escribe tu duda (ej. ¿Cómo puedo mejorar mi Win Rate este mes?)...")
    if user_query:
        st.chat_message("user").write(user_query)
        st.chat_message("assistant").write("Analizando tus datos... Basado en tu historial, tus mejores resultados ocurren en el par XAU/USD cuando mantienes un estado emocional Disciplinado. Te sugiero reducir la operativa cuando sientas FOMO.")

# --- TAB 4: CALCULADORA DE LOTAJE ---
with tabs[3]:
    st.subheader("🧮 Calculadora de Tamaño de Posición")
    st.caption("Calcula el lotaje ideal para no sobrepasar el riesgo permitido por operación.")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        balance = st.number_input("Balance de Cuenta ($USD)", value=10000.0, step=500.0)
        riesgo_pct = st.slider("Riesgo por Trade (%)", 0.1, 5.0, 1.0, 0.1)
        pips_sl = st.number_input("Pips / Puntos de Stop Loss", value=20.0, step=1.0)
    
    with col_c2:
        riesgo_usd = balance * (riesgo_pct / 100.0)
        lotaje_sugerido = riesgo_usd / (pips_sl * 10) if pips_sl > 0 else 0.0
        
        st.markdown(f'<div class="metric-card"><div>Riesgo Moneda Máximo</div><div class="metric-value-green">${riesgo_usd:,.2f} USD</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="metric-card"><div>Lotes Sugeridos (Lote Estándar)</div><div class="metric-value-cyan">{lotaje_sugerido:.2f} Lotes</div></div>', unsafe_allow_html=True)

# --- TAB 5: ANÁLISIS VS IA ---
with tabs[4]:
    st.subheader("🧠 Auditoría Visual de Estructura de Mercado")
    st.file_uploader("Sube una captura de tu setup previo a la entrada para recibir una segunda opinión basada en IA.", type=["png", "jpg"])

# --- TAB 6: PROYECCIONES ---
with tabs[5]:
    st.subheader("📈 Proyección de Crecimiento por Interés Compuesto")
    meses = st.slider("Plazo en Meses", 1, 12, 12)
    retorno_mensual = st.slider("Rendimiento Mensual Estimado (%)", 1.0, 30.0, 8.0)
    
    capital_inicial = 500.0
    proyeccion = [capital_inicial * ((1 + (retorno_mensual / 100)) ** m) for m in range(meses + 1)]
    
    df_proy = pd.DataFrame({"Mes": list(range(meses + 1)), "Capital USD": proyeccion})
    st.line_chart(df_proy.set_index("Mes"))
    st.success(f"Capital estimado a {meses} meses: **${proyeccion[-1]:,.2f} USD**")

# --- TAB 7: DIARIO & PSICOTRADING ---
with tabs[6]:
    st.subheader("📓 Bitácora de Psicotrading & Reflexión Mental")
    st.text_area("Registro semanal de mentalidad:", placeholder="Escribe aquí cómo te sentiste esta semana, si respetaste tus reglas de Stop Loss, etc.")

# --- TAB 8: DASHBOARD & PROGRESO ---
with tabs[7]:
    st.subheader("📊 Dashboard Operativo & Rendimiento Global")
    c_d1, c_d2, c_d3, c_d4 = st.columns(4)
    with c_d1:
        st.metric("P&L Acumulado", f"${pnl_total:,.2f} USD")
    with c_d2:
        st.metric("Win Rate Total", "66.6%")
    with c_d3:
        st.metric("Trades Totales", len(st.session_state["trades_db"]))
    with c_d4:
        st.metric("Días Operados", "3")
