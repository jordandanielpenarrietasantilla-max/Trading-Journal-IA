import os
import base64
import json
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

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

openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

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
            st.image(uploaded_image, caption="Gráfico Cargado", use_container_width=True)

            if not openrouter_key:
                st.error("⚠️ No se detectó OPENROUTER_API_KEY en los Secrets de Streamlit.")
            else:
                if st.button("🪄 Escanear Gráfico con IA"):
                    with st.spinner("Escaneando gráfico con OpenRouter Vision... 👁️✨"):
                        try:
                            # Convertir la imagen cargada a base64
                            uploaded_image.seek(0)
                            img_bytes = uploaded_image.read()
                            base64_image = base64.b64encode(img_bytes).decode('utf-8')
                            mime_type = uploaded_image.type

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

                            headers = {
                                "Authorization": f"Bearer {openrouter_key}",
                                "Content-Type": "application/json"
                            }

                            payload = {
                                "model": "google/gemini-2.5-flash",
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": prompt_vision},
                                            {
                                                "type": "image_url",
                                                "image_url": {
                                                    "url": f"data:{mime_type};base64,{base64_image}"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }

                            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                            res_json = response.json()

                            if "choices" in res_json:
                                raw_text = res_json["choices"][0]["message"]["content"]
                                
                                # Limpieza segura de JSON
                                clean_text = raw_text.strip()
                                if clean_text.startswith("```"):
                                    clean_text = clean_text.split("\n", 1)[-1]
                                if clean_text.endswith("```"):
                                    clean_text = clean_text.rsplit("```", 1)[0]
                                clean_text = clean_text.strip()

                                data = json.loads(clean_text)

                                st.session_state["val_par"] = data.get("par", "XAU/USD")
                                st.session_state["val_dir"] = "LONG 🟢" if data.get("direccion") == "LONG" else "SHORT 🔴"
                                st.session_state["val_entry"] = float(data.get("precio_entrada", 0.0))
                                st.session_state["val_sl"] = float(data.get("stop_loss", 0.0))
                                st.session_state["val_tp"] = float(data.get("take_profit", 0.0))
                                st.session_state["val_rr"] = float(data.get("ratio_rr", 0.0))

                                st.success("¡Lectura completada!")
                                st.rerun()
                            else:
                                st
