import os
import base64
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from google import genai
from google.genai import types

st.set_page_config(page_title="📈 Diario de Trading IA", page_icon="📈", layout="wide")

# Estilos en modo oscuro
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; color: #d1d4dc !important; }
    h1, h2, h3, h4, label, span { color: #e0e3eb !important; font-family: 'Trebuchet MS', sans-serif; }
    .stButton>button { background-color: #2962ff !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: bold !important; width: 100%; }
    .stButton>button:hover { background-color: #1e4bd8 !important; }
    </style>
""", unsafe_allow_html=True)

if "trades" not in st.session_state:
    st.session_state.trades = []

# Inicializar cliente de Google Gemini
gemini_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key) if gemini_key else None

st.title("📈 Journaling & AI Trading Audit (Visión Automática)")
st.write("Sube tu captura de TradingView para auto-detectar precios, posición y ratio R:R con IA.")

tabs = st.tabs(["➕ Registrar Trade", "📖 Diario & Auditoría IA", "📊 Dashboard & Analytics"])

# ----------------- PESTAÑA 1: NUEVO TRADE -----------------
with tabs[0]:
    col_left, col_right = st.columns([1, 1])

    with col_right:
        st.subheader("🖼️ Captura del Gráfico (TradingView)")
        uploaded_image = st.file_uploader("Sube el Screenshot", type=["jpg", "jpeg", "png"])
        
        # Variables por defecto
        auto_par = "EUR/USD"
        auto_direccion = "LONG 🟢"
        auto_entry = 0.0
        auto_sl = 0.0
        auto_tp = 0.0
        auto_rr = 0.0

        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Gráfico Cargado", use_container_width=True)

            if client and st.button("🪄 Escanear Gráfico con IA (Gemini)"):
                with st.spinner("Leyendo precios, tipo de posición y R:R del gráfico... 👁️✨"):
                    try:
                        prompt_vision = """
                        Analiza minuciosamente esta captura de TradingView. 
                        Lee la herramienta de posición (Posición Larga / Corta) o los números en pantalla y responde ÚNICAMENTE en formato JSON estricto con esta estructura:
                        {
                          "par": "Nombre del par o activo visible, ej: EURUSD, BTCUSDT, NAS100",
                          "direccion": "LONG" o "SHORT",
                          "precio_entrada": número flotante,
                          "stop_loss": número flotante,
                          "take_profit": número flotante,
                          "ratio_rr": número flotante (el R:R indicado en la caja o calculado)
                        }
                        Si algún número no es visible, pon 0.0. No agregues texto explicativo, solo el JSON.
                        """
                        response = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[image, prompt_vision]
                        )
                        
                        # Limpiar JSON de la respuesta
                        res_text = response.text.strip().replace("```json", "").replace("```", "")
                        data = json.loads(res_text)

                        st.session_state["auto_data"] = data
                        st.success("¡Datos extraídos automáticamente!")
                    except Exception as e:
                        st.error(f"Error al escanear: {e}")

    # Si hay datos detectados, los cargamos en el formulario
    auto_data = st.session_state.get("auto_data", {})

    with col_left:
        st.subheader("📝 Parámetros (Auto-completados por IA)")
        
        pares_lista = ["EUR/USD", "GBP/USD", "USD/JPY", "BTC/USDT", "NAS100", "US30", "XAU/USD"]
        par_detectado = auto_data.get("par", "EUR/USD")
        idx_par = pares_lista.index(par_detectado) if par_detectado in pares_lista else 0

        c1, c2 = st.columns(2)
        with c1:
            par = st.selectbox("Par / Activo", pares_lista, index=idx_par)
            dir_index = 0 if auto_data.get("direccion") == "LONG" else 1
            direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], index=dir_index, horizontal=True)
            precio_entrada = st.number_input("Precio Entrada", value=float(auto_data.get("precio_entrada", 0.0)), format="%.5f")
            stop_loss = st.number_input("Stop Loss", value=float(auto_data.get("stop_loss", 0.0)), format="%.5f")
            
        with c2:
            take_profit = st.number_input("Take Profit", value=float(auto_data.get("take_profit", 0.0)), format="%.5f")
            rr_detectado = float(auto_data.get("ratio_rr", 0.0))
            
            # Recalcular R:R si no viene en la imagen
            if rr_detectado == 0.0 and stop_loss != 0 and precio_entrada != 0 and take_profit != 0:
                riesgo = abs(precio_entrada - stop_loss)
                beneficio = abs(take_profit - precio_entrada)
                if riesgo > 0:
                    rr_detectado = round(beneficio / riesgo, 2)

            st.info(f"**Ratio Risk:Reward (R:R):** 1 : {rr_detectado}")
            resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BREAKEVEN ⚪"])
            riesgo_usd = st.number_input("Riesgo ($ USD)", value=100.0)

        st.subheader("📋 Confirmaciones y Notas")
        c_chk1 = st.checkbox("¿Toma de liquidez previa?")
        c_chk2 = st.checkbox("¿Entrada en FVG / Order Block?")
        c_chk3 = st.checkbox("¿Alineado con estructura HTF?")

        notas = st.text_area("Notas sobre la operación")

        if st.button("🚀 Guardar Trade y Generar Auditoría"):
            evaluacion_ia = "Evaluación no disponible."
            
            if client:
                with st.spinner("Auditando tu estrategia... 🧠"):
                    try:
                        prompt_audit = f"""
                        Eres un Máster Trader Institucional. Audita este trade:
                        - Activo: {par} ({direccion}) | Entrada: {precio_entrada} | SL: {stop_loss} | TP: {take_profit}
                        - R:R: 1:{rr_detectado} | Resultado: {resultado}
                        - Notas: {notas}
                        Da un puntaje del 1 al 10, evalúa el R:R y da 2 consejos clave. Conciso y directo.
                        """
                        res_audit = client.models.generate_content(
                            model='gemini-2.5-flash',
                            contents=[prompt_audit]
                        )
                        evaluacion_ia = res_audit.text
                    except Exception as e:
                        evaluacion_ia = f"Error auditando: {e}"

            img_b64 = None
            if uploaded_image:
                uploaded_image.seek(0)
                img_b64 = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")

            nuevo_trade = {
                "id": len(st.session_state.trades) + 1,
                "par": par,
                "direccion": direccion,
                "rr": rr_detectado,
                "resultado": resultado,
                "notas": notas,
                "evaluacion_ia": evaluacion_ia,
                "imagen_b64": img_b64
            }
            st.session_state.trades.append(nuevo_trade)
            st.session_state["auto_data"] = {}
            st.success("¡Trade guardado exitosamente!")

# ----------------- PESTAÑA 2: DIARIO -----------------
with tabs[1]:
    st.subheader("📖 Historial de Trades")
    if not st.session_state.trades:
        st.write("No hay entradas aún.")
    else:
        for t in reversed(st.session_state.trades):
            with st.expander(f"Trade #{t['id']} | {t['par']} - {t['direccion']} | {t['resultado']} (R:R 1:{t['rr']})"):
                c_img, c_info = st.columns([1, 1])
                with c_img:
                    if t["imagen_b64"]:
                        st.image(f"data:image/png;base64,{t['imagen_b64']}", use_container_width=True)
                with c_info:
                    st.markdown(f"**Notas:** {t['notas']}")
                    st.markdown("---")
                    st.markdown("### 🧠 Auditoría de IA")
                    st.markdown(t["evaluacion_ia"])

# ----------------- PESTAÑA 3: DASHBOARD -----------------
with tabs[2]:
    st.subheader("📊 Analytics")
    if st.session_state.trades:
        df = pd.DataFrame(st.session_state.trades)
        wins = len(df[df["resultado"].str.contains("WIN")])
        total = len(df)
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Total Trades", total)
        c_m2.metric("Win Rate", f"{win_rate}%")
        c_m3.metric("R Promedio", f"1:{round(df['rr'].mean(), 2)}")

        fig = px.bar(df, x="par", color="resultado", title="Rendimiento por Activo", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
