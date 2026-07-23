import os
import base64
import pandas as pd
import plotly.express as px
import streamlit as st
from groq import Groq

# Configuración de página con tema Oscuro estilo TradingView
st.set_page_config(page_title="📈 Diario de Trading IA", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0e14 !important;
        color: #d1d4dc !important;
    }
    h1, h2, h3, h4, label, span {
        color: #e0e3eb !important;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
    }
    .stButton>button {
        background-color: #2962ff !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1e4bd8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializar sesión de almacenamiento local de trades
if "trades" not in st.session_state:
    st.session_state.trades = []

api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key else None

st.title("📈 Journaling & AI Trading Audit")
st.write("Registra tus entradas, analiza tu ratio R:R y recibe auditoría técnica por IA de tus gráficos.")

tabs = st.tabs(["➕ Registrar Trade", "📖 Diario & Auditoría IA", "📊 Dashboard & Analytics"])

# ----------------- PESTAÑA 1: NUEVO TRADE -----------------
with tabs[0]:
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📝 Parámetros del Trade")
        
        c1, c2 = st.columns(2)
        with c1:
            par = st.selectbox("Par / Activo", ["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USDT", "NAS100", "US30", "XAU/USD"])
            direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], horizontal=True)
            precio_entrada = st.number_input("Precio Entrada", value=0.0, format="%.5f")
            stop_loss = st.number_input("Stop Loss", value=0.0, format="%.5f")
            
        with c2:
            take_profit = st.number_input("Take Profit", value=0.0, format="%.5f")
            precio_salida = st.number_input("Precio Salida (Ejecutado)", value=0.0, format="%.5f")
            resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BREAKEVEN ⚪"])
            riesgo_usd = st.number_input("Riesgo ($ USD)", value=100.0)

        # Cálculo de R:R
        rr_calculado = 0.0
        if stop_loss != 0 and precio_entrada != 0 and take_profit != 0:
            riesgo = abs(precio_entrada - stop_loss)
            beneficio = abs(take_profit - precio_entrada)
            if riesgo > 0:
                rr_calculado = round(beneficio / riesgo, 2)
        
        st.info(f"**Ratio Riesgo/Beneficio (R:R):** 1 : {rr_calculado}")

        st.subheader("📋 Checklist de Confirmación")
        c_chk1 = st.checkbox("¿Hubo toma de liquidez previa (BSL/SSL)?")
        c_chk2 = st.checkbox("¿Entrada en zona FVG / Order Block?")
        c_chk3 = st.checkbox("¿Estructura alineada en Temporalidad Mayor?")
        c_chk4 = st.checkbox("¿Riesgo respetado según el plan?")

        notas = st.text_area("Notas / Emociones / Razón de entrada")

    with col_right:
        st.subheader("🖼️ Captura de TradingView")
        uploaded_image = st.file_uploader("Sube el Screenshot de la Operación", type=["jpg", "jpeg", "png"])
        
        if uploaded_image:
            st.image(uploaded_image, caption="Gráfico Cargado", use_container_width=True)

        if st.button("🚀 Guardar Trade y Auditar con IA"):
            evaluacion_ia = "Sin auditoría disponible."
            
            # Evaluación con IA Groq (Llama-3.3)
            if client:
                with st.spinner("La IA está auditando tu entrada... 🧠📈"):
                    try:
                        prompt_ia = f"""
                        Eres un Máster Trader de Nivel Institucional y Mentor de Gestión de Riesgo.
                        Audita la siguiente operación:
                        - Par: {par} ({direccion})
                        - Entrada: {precio_entrada} | Stop Loss: {stop_loss} | Take Profit: {take_profit}
                        - R:R Calculado: 1:{rr_calculado}
                        - Resultado: {resultado}
                        - Checklist Cumplido: Liquidez ({c_chk1}), FVG/OB ({c_chk2}), Estructura HTF ({c_chk3}), Plan ({c_chk4})
                        - Notas del Trader: {notas}

                        Por favor proporciona:
                        1. Calificación de la Entrada (1 al 10).
                        2. Crítica de Gestión de Riesgo y R:R.
                        3. 2 Consejos Clave para mejorar esta entrada.
                        Sé directo, profesional y conciso.
                        """
                        response = client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[{"role": "user", "content": prompt_ia}],
                            temperature=0.7,
                            max_tokens=400
                        )
                        evaluacion_ia = response.choices[0].message.content
                    except Exception as e:
                        evaluacion_ia = f"Error al generar auditoría: {e}"

            # Convertir imagen para guardar localmente en sesión
            img_b64 = None
            if uploaded_image:
                img_b64 = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")

            nuevo_trade = {
                "id": len(st.session_state.trades) + 1,
                "par": par,
                "direccion": direccion,
                "rr": rr_calculado,
                "resultado": resultado,
                "riesgo": riesgo_usd,
                "notas": notas,
                "evaluacion_ia": evaluacion_ia,
                "imagen_b64": img_b64
            }
            st.session_state.trades.append(nuevo_trade)
            st.success("¡Trade registrado e auditado con éxito!")

# ----------------- PESTAÑA 2: DIARIO -----------------
with tabs[1]:
    st.subheader("📖 Historial de Trades Registrados")
    if not st.session_state.trades:
        st.write("Aún no has registrado ninguna operación. Ve a 'Registrar Trade' para empezar.")
    else:
        for t in reversed(st.session_state.trades):
            with st.expander(f"Trade #{t['id']} | {t['par']} - {t['direccion']} | {t['resultado']} (R:R 1:{t['rr']})"):
                c_img, c_info = st.columns([1, 1])
                with c_img:
                    if t["imagen_b64"]:
                        st.image(f"data:image/png;base64,{t['imagen_b64']}", use_container_width=True)
                    else:
                        st.info("Sin captura adjunta")
                with c_info:
                    st.markdown(f"**Notas:** {t['notas']}")
                    st.markdown("---")
                    st.markdown("### 🧠 Auditoría de la IA")
                    st.markdown(t["evaluacion_ia"])

# ----------------- PESTAÑA 3: DASHBOARD -----------------
with tabs[2]:
    st.subheader("📊 Métricas y Rendimiento")
    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        
        wins = len(df[df["resultado"].str.contains("WIN")])
        total = len(df)
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Trades", total)
        col_m2.metric("Win Rate", f"{win_rate}%")
        col_m3.metric("R Promedio", f"1:{round(df['rr'].mean(), 2)}")

        fig = px.bar(df, x="par", color="resultado", title="Rendimiento por Activo", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Registra operaciones para ver las estadísticas interactiva aquí.")
