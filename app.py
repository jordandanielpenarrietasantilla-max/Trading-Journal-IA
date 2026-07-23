import base64
import json
import os
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image
from supabase import create_client, Client

st.set_page_config(page_title="Diario de Trading IA", page_icon="📈", layout="wide")


# Función para aplicar fondo estilizado con imagen local (fondo.jpg)
def aplicar_fondo_local(ruta_imagen):
    bg_style = ""
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        bg_style = f'background-image: linear-gradient(rgba(11, 14, 20, 0.55), rgba(11, 14, 20, 0.65)), url("data:image/jpeg;base64,{encoded_string}") !important;'

    css_fondo = f"""
    <style>
    /* Fondo Principal */
    .stApp {{
        {bg_style}
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* Tipografía y Colores */
    .stApp, p, label, h1, h2, h3, h4, span, div {{
        color: #f0f3fa !important;
        font-family: 'Trebuchet MS', sans-serif !important;
    }}
    
    /* Título con Degradado Neón */
    h1 {{
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }}
    
    /* Paneles con efecto Glassmorphism */
    div[data-testid="stColumn"] {{
        background: rgba(15, 20, 30, 0.78) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(0, 210, 255, 0.25) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5) !important;
    }}
    
    /* Cajas de entrada */
    .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stTextArea textarea {{
        background-color: rgba(10, 14, 23, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(0, 210, 255, 0.35) !important;
        border-radius: 6px !important;
    }}
    
    /* Botones principales */
    .stButton>button {{
        background: linear-gradient(135deg, #2962ff 0%, #00d2ff 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
        height: 48px;
        box-shadow: 0px 4px 15px rgba(0, 210, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 20px rgba(0, 210, 255, 0.6) !important;
    }}
    </style>
    """
    st.markdown(css_fondo, unsafe_allow_html=True)


aplicar_fondo_local("fondo.jpg")

# --- CONEXIÓN A SECRETS ---
openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")
supabase_url = st.secrets.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
supabase_key = st.secrets.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

# Inicializar cliente de Supabase
supabase: Client = None
if supabase_url and supabase_key:
    try:
        supabase = create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")

# Cargar Trades desde Supabase al Iniciar la App
if "trades" not in st.session_state:
    st.session_state.trades = []
    if supabase:
        try:
            res = supabase.table("trades").select("*").order("id", desc=False).execute()
            st.session_state.trades = res.data
        except Exception as e:
            st.warning(f"No se pudieron cargar los trades desde la nube: {e}")

st.title("📈 Journaling & AI Trading Audit")
st.write("Sube tu captura de TradingView para auto-detectar precios, auditar trades y comparar tu análisis con IA.")

tabs = st.tabs(["➕ Registrar Trade", "🆚 Análisis vs IA", "📖 Diario & Auditoría IA", "📊 Dashboard & Analytics"])

# ----------------- PESTAÑA 1: NUEVO TRADE -----------------
with tabs[0]:
    col_left, col_right = st.columns([1, 1])

    with col_right:
        st.subheader("🖼️ Captura del Gráfico (TradingView)")
        uploaded_image = st.file_uploader("Sube el Screenshot", type=["jpg", "jpeg", "png"], key="upload_trade")

        if uploaded_image:
            st.image(uploaded_image, caption="Gráfico Cargado", use_container_width=True)

            if not openrouter_key:
                st.error("⚠️ No se detectó OPENROUTER_API_KEY en los Secrets de Streamlit.")
            else:
                if st.button("🪄 Escanear Gráfico con IA"):
                    with st.spinner("Escaneando gráfico con IA... 👁️✨"):
                        try:
                            uploaded_image.seek(0)
                            img_bytes = uploaded_image.read()
                            base64_image = base64.b64encode(img_bytes).decode("utf-8")
                            mime_type = uploaded_image.type

                            prompt_vision = (
                                "Analiza esta captura de TradingView. "
                                "Lee la herramienta de posición y responde ÚNICAMENTE un JSON estricto con esta estructura: "
                                '{"par": "XAU/USD", "direccion": "SHORT", "precio_entrada": 4050.13, "stop_loss": 4045.16, "take_profit": 4112.65, "ratio_rr": 2.5}. '
                                "Si la ganancia está abajo es SHORT, si está arriba es LONG. No agregues texto extra."
                            )

                            headers = {
                                "Authorization": f"Bearer {openrouter_key}",
                                "Content-Type": "application/json",
                            }

                            payload = {
                                "model": "google/gemini-2.5-flash",
                                "max_tokens": 300,
                                "messages": [
                                    {
                                        "role": "user",
                                        "content": [
                                            {"type": "text", "text": prompt_vision},
                                            {
                                                "type": "image_url",
                                                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                                            },
                                        ],
                                    }
                                ],
                            }

                            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                            res_json = response.json()

                            if "choices" in res_json:
                                raw_text = res_json["choices"][0]["message"]["content"]
                                start_idx = raw_text.find("{")
                                end_idx = raw_text.rfind("}") + 1

                                if start_idx != -1 and end_idx != 0:
                                    json_str = raw_text[start_idx:end_idx]
                                    data = json.loads(json_str)

                                    st.session_state["val_par"] = data.get("par", "XAU/USD")
                                    st.session_state["val_dir"] = "LONG 🟢" if data.get("direccion") == "LONG" else "SHORT 🔴"
                                    st.session_state["val_entry"] = float(data.get("precio_entrada", 0.0))
                                    st.session_state["val_sl"] = float(data.get("stop_loss", 0.0))
                                    st.session_state["val_tp"] = float(data.get("take_profit", 0.0))
                                    st.session_state["val_rr"] = float(data.get("ratio_rr", 0.0))

                                    st.success("¡Lectura completada!")
                                    st.rerun()
                                else:
                                    st.error("No se encontró JSON en la respuesta.")
                            else:
                                st.error(f"Error de API: {res_json}")

                        except Exception as e:
                            st.error(f"Error procesando la imagen: {e}")

    val_par = st.session_state.get("val_par", "XAU/USD")
    val_dir = st.session_state.get("val_dir", "SHORT 🔴")
    val_entry = st.session_state.get("val_entry", 0.0)
    val_sl = st.session_state.get("val_sl", 0.0)
    val_tp = st.session_state.get("val_tp", 0.0)
    val_rr = st.session_state.get("val_rr", 0.0)

    with col_left:
        st.subheader("📝 Parámetros (Auto-completados por IA)")

        pares_lista = ["XAU/USD", "EUR/USD", "GBP/USD", "USD/JPY", "BTC/USDT", "NAS100", "US30"]
        idx_par = pares_lista.index(val_par) if val_par in pares_lista else 0

        c1, c2 = st.columns(2)
        with c1:
            par = st.selectbox("Par / Activo", pares_lista, index=idx_par)
            dir_index = 0 if "LONG" in val_dir else 1
            direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], index=dir_index, horizontal=True)
            precio_entrada = st.number_input("Precio Entrada", value=val_entry, format="%.2f")
            stop_loss = st.number_input("Stop Loss", value=val_sl, format="%.2f")

        with c2:
            take_profit = st.number_input("Take Profit", value=val_tp, format="%.2f")

            rr_final = val_rr
            if rr_final == 0.0 and stop_loss != 0 and precio_entrada != 0 and take_profit != 0:
                riesgo = abs(precio_entrada - stop_loss)
                beneficio = abs(take_profit - precio_entrada)
                if riesgo > 0:
                    rr_final = round(beneficio / riesgo, 2)

            st.info(f"**Ratio Risk:Reward (R:R):** 1 : {rr_final}")
            resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BREAKEVEN ⚪"])
            riesgo_usd = st.number_input("Riesgo ($ USD)", value=100.0)

        st.subheader("📋 Confirmaciones y Notas")
        c_chk1 = st.checkbox("¿Toma de liquidez previa?")
        c_chk2 = st.checkbox("¿Entrada en FVG / Order Block?")
        c_chk3 = st.checkbox("¿Alineado con estructura HTF?")

        notas = st.text_area("Notas sobre la operación")

        if st.button("🚀 Guardar Trade y Generar Auditoría"):
            evaluacion_ia = "Evaluación no disponible."

            if openrouter_key:
                with st.spinner("Auditando tu estrategia con IA... 🧠"):
                    try:
                        prompt_audit = f"Audita este trade de trading: Activo {par} ({direccion}), Entrada {precio_entrada}, SL {stop_loss}, TP {take_profit}, R:R 1:{rr_final}, Resultado {resultado}. Notas: {notas}. Da una nota del 1 al 10 y 2 consejos breves."
                        headers = {
                            "Authorization": f"Bearer {openrouter_key}",
                            "Content-Type": "application/json",
                        }
                        payload = {
                            "model": "google/gemini-2.5-flash",
                            "max_tokens": 300,
                            "messages": [{"role": "user", "content": prompt_audit}],
                        }
                        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                        evaluacion_ia = res.json()["choices"][0]["message"]["content"]
                    except Exception as e:
                        evaluacion_ia = f"Error auditando: {e}"

            img_b64 = None
            if uploaded_image:
                uploaded_image.seek(0)
                img_b64 = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")

            nuevo_trade = {
                "par": par,
                "direccion": direccion,
                "precio_entrada": precio_entrada,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "rr": rr_final,
                "resultado": resultado,
                "notas": notas,
                "evaluacion_ia": evaluacion_ia,
                "imagen_b64": img_b64,
            }

            # Guardar en Supabase permanente
            if supabase:
                try:
                    res = supabase.table("trades").insert(nuevo_trade).execute()
                    st.session_state.trades.append(res.data[0])
                    st.success("¡Trade guardado de forma permanente en la nube! ☁️")
                except Exception as e:
                    st.error(f"Error guardando en Supabase: {e}")
                    st.session_state.trades.append(nuevo_trade)
            else:
                st.session_state.trades.append(nuevo_trade)
                st.success("Trade guardado localmente (configura Supabase para guardar en la nube).")

            for k in ["val_entry", "val_sl", "val_tp", "val_rr"]:
                if k in st.session_state:
                    del st.session_state[k]

            st.rerun()

# ----------------- PESTAÑA 2: ANÁLISIS VS IA -----------------
with tabs[1]:
    st.subheader("🆚 Comparar tu Análisis Técnico con la IA")
    st.write("Sube tu proyección o gráfico de análisis y escribe tu hipótesis para ver qué opina la IA.")

    col_a1, col_a2 = st.columns([1, 1])

    with col_a1:
        img_analisis = st.file_uploader("Sube el Gráfico de tu Análisis", type=["jpg", "jpeg", "png"], key="upload_analysis")
        hipotesis_usuario = st.text_area(
            "✍️ Tu Análisis / Hipótesis:",
            placeholder="Ejemplo: Veo un barrido de liquidez en M15 y espero un retroceso a la zona de FVG para entrar en Long buscando los máximos de la sesión de Asia.",
            height=150
        )
        btn_comparar = st.button("🔎 Comparar mi Análisis con IA")

    with col_a2:
        if img_analisis and btn_comparar:
            if not openrouter_key:
                st.error("⚠️ Falta la clave de OpenRouter en los Secrets.")
            else:
                with st.spinner("Analizando tu hipótesis con la IA... 🧠⚡"):
                    try:
                        img_analisis.seek(0)
                        img_bytes = img_analisis.read()
                        base64_img = base64.b64encode(img_bytes).decode("utf-8")
                        mime_type = img_analisis.type

                        prompt_compare = (
                            f"El usuario propone este análisis técnico/hipótesis de trading: '{hipotesis_usuario}'. "
                            "Examina la imagen adjunta del gráfico. Responde en español de forma profesional, breve e indica: "
                            "1) ¿Coincide el gráfico con la hipótesis del usuario? "
                            "2) Riesgos o detalles no considerados (zonas de liquidez, tendencia, etc.). "
                            "3) Veredicto final / Sugerencia de confirmación."
                        )

                        headers = {
                            "Authorization": f"Bearer {openrouter_key}",
                            "Content-Type": "application/json",
                        }

                        payload = {
                            "model": "google/gemini-2.5-flash",
                            "max_tokens": 300,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt_compare},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:{mime_type};base64,{base64_img}"},
                                        },
                                    ],
                                }
                            ],
                        }

                        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
                        res_json = response.json()

                        if "choices" in res_json:
                            resultado_comparacion = res_json["choices"][0]["message"]["content"]
                            st.markdown("### 🤖 Veredicto de la IA:")
                            st.info(resultado_comparacion)
                        else:
                            st.error(f"Error procesando: {res_json}")
                    except Exception as e:
                        st.error(f"Error durante la comparación: {e}")

        elif img_analisis:
            st.image(img_analisis, caption="Análisis Cargado", use_container_width=True)

# ----------------- PESTAÑA 3: DIARIO -----------------
with tabs[2]:
    st.subheader("📖 Historial de Trades (Guardados en Nube)")
    if not st.session_state.trades:
        st.write("No hay entradas guardadas aún.")
    else:
        for t in reversed(st.session_state.trades):
            with st.expander(f"Trade #{t.get('id', 'N/A')} | {t['par']} - {t['direccion']} | {t['resultado']} (R:R 1:{t['rr']})"):
                c_img, c_info = st.columns([1, 1])
                with c_img:
                    if t.get("imagen_b64"):
                        st.image(f"data:image/png;base64,{t['imagen_b64']}", use_container_width=True)
                with c_info:
                    st.markdown(f"**Notas:** {t.get('notas', '')}")
                    st.markdown("---")
                    st.markdown("### 🧠 Auditoría de IA")
                    st.markdown(t.get("evaluacion_ia", ""))

# ----------------- PESTAÑA 4: DASHBOARD -----------------
with tabs[3]:
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
