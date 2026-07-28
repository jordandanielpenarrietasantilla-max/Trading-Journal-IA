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

# 2. CSS Personalizado con Resaltado Neón para el Menú Lateral
st.markdown("""
<style>
    /* Estilo de Fondo y Tema General Dark Mode */
    .stApp {
        background-color: #0b0e14;
        color: #e0e6ed;
    }
    
    /* --- BOTÓN DE COLAPSAR/ABRIR SIDEBAR BRRILLANTE NEÓN --- */
    button[data-testid="stSidebarCollapseButton"],
    button[data-testid="stBaseButton-headerNoPadding"],
    button[aria-label="Close sidebar"],
    button[aria-label="Open sidebar"] {
        background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 8px !important;
        box-shadow: 0px 0px 12px rgba(0, 242, 254, 0.9) !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    button[data-testid="stSidebarCollapseButton"]:hover,
    button[aria-label="Open sidebar"]:hover {
        transform: scale(1.15) !important;
        box-shadow: 0px 0px 18px rgba(0, 242, 254, 1) !important;
    }

    /* Pestañas Personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #121824;
        padding: 8px 12px;
        border-radius: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 6px;
        color: #8a99ad;
        font-weight: 600;
        font-size: 14px;
        padding: 0px 16px;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #00f2fe !important;
        border-bottom: 3px solid #00f2fe !important;
    }

    /* Tarjetas de Métricas */
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
        color: #10b981;
    }
    .metric-value-cyan {
        font-size: 28px;
        font-weight: bold;
        color: #00f2fe;
    }
    
    /* Insignia VIP */
    .vip-badge {
        background: linear-gradient(90deg, #f59e0b, #fbbf24);
        color: #000;
        font-weight: bold;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        display: inline-block;
        margin-top: 5px;
    }

    /* Cajas de Info */
    .info-box {
        background-color: #0d233a;
        border-left: 4px solid #00f2fe;
        padding: 12px 16px;
        border-radius: 4px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Inicializar Estados de Sesión (Simulación / Supabase Metadata)
if "user_email" not in st.session_state:
    st.session_state["user_email"] = "rey.david_daniel@hotmail.com"
if "is_vip" not in st.session_state:
    st.session_state["is_vip"] = True
if "trades_db" not in st.session_state:
    st.session_state["trades_db"] = [
        {"fecha": "2026-07-27", "par": "XAU/USD", "tipo": "LONG", "pnl": 2500.00, "resultado": "WIN", "estado": "Disciplinado / Neutro"},
        {"fecha": "2026-07-25", "par": "EUR/USD", "tipo": "SHORT", "pnl": -300.00, "resultado": "LOSS", "estado": "Ansioso / FOMO"},
        {"fecha": "2026-07-20", "par": "BTC/USD", "tipo": "LONG", "pnl": 300.00, "resultado": "WIN", "estado": "Confiado"}
    ]

# ------------------- SIDEBAR / PERFIL DE USUARIO -------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=70)
    st.markdown(f"### 👤 Perfil de Usuario")
    st.write(f"**Email:** `{st.session_state['user_email']}`")
    
    if st.session_state["is_vip"]:
        st.markdown('<span class="vip-badge">⚡ VIP / PLAN PRO ACTIVO</span>', unsafe_allow_html=True)
    else:
        st.markdown('🔴 **Plan Gratuito**')

    st.markdown("---")
    st.markdown("#### 🕒 Horario de Mercados")
    st.caption("🌐 **Londres:** Abierto")
    st.caption("🗽 **Nueva York:** Abierto")
    st.caption("🗾 **Tokio:** Cerrado")

    st.markdown("---")
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.success("Sesión cerrada correctamente")

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
    # Muestra visual simplificada del calendario Prop Firm
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
        st.chat_message("assistant").write(" Analizando tus datos... Basado en tu historial, tus mejores resultados ocurren en el par XAU/USD cuando mantienes un estado emocional Disciplinado. Te sugiero reducir la operativa cuando sientas FOMO.")

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
        # Fórmula simplificada de lotaje estándar en Forex
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
