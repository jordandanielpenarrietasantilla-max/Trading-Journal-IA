import os
import base64
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from google import genai

st.set_page_config(page_title="📈 Diario de Trading IA", page_icon="📈", layout="wide")

# Estilos en modo oscuro estilo TradingView
st.markdown("""
    <style>
    .stApp { background-color: #0b0e14 !important; color: #d1d4dc !important; }
    h1, h2, h3, h4, label, span { color: #e0e3eb !important; font-family: 'Trebuchet MS', sans-serif; }
    .stButton>button { background-color: #2962ff !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: bold !important; width: 100%; height: 45px; }
    .stButton>button:hover { background-color: #1e4bd8 !important; }
    </style>
""", unsafe_allow_html=True)

if "trades" not in st.session_state:
    st.session_state.trades = []

# Inicializar cliente de Google Gemini
gemini_key = st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key) if gemini_key else None

st.title("📈 Journaling & AI Trading Audit")
st.write("Sube tu captura de TradingView para auto-detectar precios, posición y ratio R:R con IA.")

tabs = st.tabs(["➕ Registrar Trade", "📖 Diario & Auditoría IA", "📊 Dashboard & Analytics"])

# ----------------- PESTAÑA 1: NUEVO TRADE -----------------
with tabs[0]:
    col_left, col_right = st.columns([1, 1])

    with col_right:
        st.subheader("🖼️ Captura del Gráfico (TradingView)")
        uploaded_image = st.file_uploader("Sube el Screenshot", type=["jpg", "jpeg", "png"])
        
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, caption="Gráfico Cargado", use_container_width=True)

            if not client:
                st.error("⚠️ No se detectó la GEMINI_API_KEY. Revisa los Secrets en Streamlit.")
            else:
                if st.button("🪄 Escanear Gráfico con IA"):
                    with st.spinner("Analizando gráfico con Gemini Vision... 👁️✨"):
                        try:
                            prompt_vision = """
                            Analiza minuciosamente esta captura de TradingView. 
                            Lee la herramienta de posición (Posición Larga / Corta) o los números en la escala de precios y responde ÚNICAMENTE en formato JSON estricto con esta estructura exacta:
                            {
                              "par": "XAU/USD", 
                              "direccion": "LONG" o "SHORT",
                              "precio_entrada": 4050.13,
                              "stop_loss": 4045.16,
                              "take_profit": 4112.65,
                              "ratio_rr": 2.5
                            }
                            Instrucciones:
                            - "par": Identifica el activo (ej: XAU/USD, EUR/USD, BTC/USDT).
                            - "direccion": Si la zona de ganancia está arriba es LONG, si está abajo es SHORT.
                            - "precio_entrada", "stop_loss", "take_profit": Extrae los valores numéricos exactos de las líneas/etiquetas de la escala de precios.
                            - "ratio_rr": Extrae el R:R indicado en la caja o calcula (take_profit - entrada)/(entrada - stop_loss).
                            
                            Responde SOLO el código JSON, sin markdown ni texto extra.
                            """
                            response = client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[image, prompt_vision]
                            )
                            
                            # Limpiar JSON de la respuesta
                            res_text = response.text.strip().replace("```json", "").replace("
