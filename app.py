import base64
import json
import os
from datetime import datetime
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image
from supabase import create_client, Client

st.set_page_config(page_title="Diario de Trading IA", page_icon="📈", layout="wide")


# Función para aplicar fondo estilizado con bordes e insumos animados (Neon Glow)
def aplicar_fondo_local(ruta_imagen):
    bg_style = ""
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        bg_style = f'background-image: linear-gradient(rgba(11, 14, 20, 0.55), rgba(11, 14, 20, 0.65)), url("data:image/jpeg;base64,{encoded_string}") !important;'

    css_fondo = f"""
    <style>
    /* Animación de Neón para Bordes y Líneas */
    @keyframes neonGlow {{
        0% {{
            border-color: rgba(0, 242, 254, 0.4);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2), inset 0 0 5px rgba(0, 242, 254, 0.1);
        }}
        50% {{
            border-color: rgba(41, 98, 255, 0.8);
            box-shadow: 0 0 20px rgba(41, 98, 255, 0.5), inset 0 0 10px rgba(41, 98, 255, 0.2);
        }}
        100% {{
            border-color: rgba(0, 242, 254, 0.4);
            box-shadow: 0 0 10px rgba(0, 242, 254, 0.2), inset 0 0 5px rgba(0, 242, 254, 0.1);
        }}
    }}

    /* Fondo Principal */
    .stApp {{
        {bg_style}
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* Tipografía y Colores General */
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
    
    /* Paneles con efecto Glassmorphism y BORDES ANIMADOS */
    div[data-testid="stColumn"] {{
        background: rgba(15, 20, 30, 0.82) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 2px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 14px !important;
        padding: 22px !important;
        animation: neonGlow 4s infinite ease-in-out !important;
    }}
    
    /* Cajas de Entrada con Animación de Enfoque */
    .stNumberInput input, .stTextArea textarea, .stTextInput input {{
        background-color: #0b0e14 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
        border-radius: 8px !important;
        transition: all 0.3s ease-in-out !important;
    }}

    .stNumberInput input:focus, .stTextArea textarea:focus, .stTextInput input:focus {{
        border-color: #00f2fe !important;
        box-shadow: 0 0 12px rgba(0, 242, 254, 0.8) !important;
    }}

    /* --- FIX Y ESTILO ANIMADO PARA SELECTBOX & DESPLEGABLES --- */
    div[data-baseweb="select"] > div {{
        background-color: #0b0e14 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
        border-radius: 8px !important;
    }}
    
    div[data-baseweb="select"] input {{
        color: #ffffff !important;
    }}

    /* Menú emergente de las listas desplegables */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: #0d121d !important;
        border: 1px solid #00f2fe !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.3) !important;
    }}

    li[role="option"], div[role="option"] {{
        background-color: #0d121d !important;
        color: #ffffff !important;
    }}

    li[role="option"]:hover, div[role="option"]:hover, [aria-selected="true"] {{
        background-color: #2962ff !important;
        color: #ffffff !important;
    }}

    /* Botones Neón Estilizados */
    .stButton>button {{
        background: linear-gradient(135deg, #2962ff 0%, #00d2ff 100%) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold !important;
        width: 100%;
        height: 48px;
        box-shadow: 0px 4px 15px rgba(0, 210, 255, 0.4) !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 25px rgba(0, 210, 255, 0.8) !important;
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
st.write("Sube o pega tus capturas, audita tus emociones, calcula lotaje y mide tu progreso con estilo neón.")

# LISTA PREDETERMINADA DE ACTIVOS
LISTA_ACTIVOS = [
    "Otro (Escribir manualmente)", "XAU/USD (Oro)", "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", 
    "USD/CAD", "USD/CHF", "NZD/USD", "GBP/JPY", "EUR/JPY", "EUR/GBP", "BTC/USDT", 
    "ETH/USDT", "SOL/USDT", "NAS100 / US100", "US30 / Dow Jones", "SPX500 / S&P500", 
    "GER30 / DAX40", "USOIL (Petróleo)"
]

tabs = st.tabs([
    "➕ Registrar Trade", 
    "🧮 Calc. Lotaje",
    "🆚 Análisis vs IA", 
    "📁 Proyecciones", 
    "📖 Diario & Psicotrading", 
    "📊 Dashboard & Progreso"
])

# ----------------- PESTAÑA 1: NUEVO TRADE -----------------
with tabs[0]:
    col_left, col_right = st.columns([1, 1])

    with col_right:
        st.subheader("🖼️ Capturas del Gráfico (Antes & Después)")
        
        uploaded_image_before = st.file_uploader("1️⃣ Screenshot ANTES (Entrada / Setup)", type=["jpg", "jpeg", "png"], key="upload_trade_before")
        uploaded_image_after = st.file_uploader("2️⃣ Screenshot DESPUÉS (Cierre / Resultado)", type=["jpg", "jpeg", "png"], key="upload_trade_after")

        if uploaded_image_before:
            c_preview1, c_preview2 = st.columns(2)
            with c_preview1:
                st.image(uploaded_image_before, caption="🟢 ANTES (Entrada)", use_container_width=True)
            with c_preview2:
                if uploaded_image_after:
                    st.image(uploaded_image_after, caption="🔴 DESPUÉS (Resultado)", use_container_width=True)

            if openrouter_key and st.button("🪄 Escanear Gráfico ANTES con IA"):
                with st.spinner("Escaneando gráfico con IA... 👁️✨"):
                    try:
                        uploaded_image_before.seek(0)
                        img_bytes = uploaded_image_before.read()
                        base64_image = base64.b64encode(img_bytes).decode("utf-8")
                        mime_type = uploaded_image_before.type

                        prompt_vision = (
                            "Analiza esta captura de TradingView. "
                            "Lee la herramienta de posición y responde ÚNICAMENTE un JSON estricto con esta estructura: "
                            '{"par": "XAU/USD (Oro)", "direccion": "SHORT", "precio_entrada": 4050.13, "stop_loss": 4045.16, "take_profit": 4112.65, "ratio_rr": 2.5}. '
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

                                st.session_state["val_par"] = data.get("par", "XAU/USD (Oro)")
                                st.session_state["val_dir"] = "LONG 🟢" if data.get("direccion") == "LONG" else "SHORT 🔴"
                                st.session_state["val_entry"] = float(data.get("precio_entrada", 0.0))
                                st.session_state["val_sl"] = float(data.get("stop_loss", 0.0))
                                st.session_state["val_tp"] = float(data.get("take_profit", 0.0))
                                st.session_state["val_rr"] = float(data.get("ratio_rr", 0.0))

                                st.success("¡Lectura completada!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error procesando la imagen: {e}")

    val_par = st.session_state.get("val_par", "XAU/USD (Oro)")
    val_dir = st.session_state.get("val_dir", "SHORT 🔴")
    val_entry = st.session_state.get("val_entry", 0.0)
    val_sl = st.session_state.get("val_sl", 0.0)
    val_tp = st.session_state.get("val_tp", 0.0)
    val_rr = st.session_state.get("val_rr", 0.0)

    with col_left:
        st.subheader("📝 Parámetros & Fecha")

        fecha_trade = st.date_input("Fecha de la Operación", datetime.now())
        
        idx_par = LISTA_ACTIVOS.index(val_par) if val_par in LISTA_ACTIVOS else 1

        c1, c2 = st.columns(2)
        with c1:
            par_seleccionado = st.selectbox("Seleccionar Activo / Par", LISTA_ACTIVOS, index=idx_par)
            
            # Opción para escribir un par personalizado si elige 'Otro' o desea escribirlo
            if par_seleccionado == "Otro (Escribir manualmente)":
                par = st.text_input("✍️ Escribe el nombre del Activo:", placeholder="Ej. NVDA, US2000, DOGEUSD...")
            else:
                par = par_seleccionado

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

            st.info(f"**Ratio Risk:Reward:** 1 : {rr_final}")
            resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BREAKEVEN ⚪"])

        st.subheader("🧠 Psicotrading & Estado Emocional")
        emocion = st.selectbox(
            "¿Cómo te sentías al tomar la entrada?", 
            ["🎯 Disciplinado / Neutro", "⚡ Enfocado / Confiado", "😰 Ansioso / Con Miedo", "🚀 Euforico / Sobreconfiado", "😡 Venganza (FOMO)", "😴 Cansado / Distraído"]
        )
        notas_emocionales = st.text_area("Notas emocionales y del estado mental de la sesión:")

        notas = st.text_area("Notas técnicas sobre la operación:")

        if st.button("🚀 Guardar Trade Ejecutado"):
            evaluacion_ia = "Evaluación no disponible."

            if openrouter_key:
                with st.spinner("Auditando tu estrategia con IA... 🧠"):
                    try:
                        prompt_audit = f"Audita este trade: Activo {par} ({direccion}), Entrada {precio_entrada}, SL {stop_loss}, TP {take_profit}, R:R 1:{rr_final}, Resultado {resultado}. Emoción: {emocion}. Notas: {notas}. Da una nota del 1 al 10 y un consejo sobre la parte emocional y técnica."
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

            img_b64_before = None
            if uploaded_image_before:
                uploaded_image_before.seek(0)
                img_b64_before = base64.b64encode(uploaded_image_before.getvalue()).decode("utf-8")

            img_b64_after = None
            if uploaded_image_after:
                uploaded_image_after.seek(0)
                img_b64_after = base64.b64encode(uploaded_image_after.getvalue()).decode("utf-8")

            nuevo_trade = {
                "par": par if par else "S/D",
                "direccion": direccion,
                "precio_entrada": precio_entrada,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "rr": rr_final,
                "resultado": resultado,
                "notas": notas,
                "evaluacion_ia": evaluacion_ia,
                "imagen_b64": img_b64_before,
                "imagen_despues_b64": img_b64_after,
                "es_analisis_previo": False,
                "fecha": str(fecha_trade),
                "emocion": emocion,
                "notas_emocionales": notas_emocionales
            }

            if supabase:
                try:
                    res = supabase.table("trades").insert(nuevo_trade).execute()
                    st.session_state.trades.append(res.data[0])
                    st.success("¡Trade guardado en la nube de forma permanente! ☁️")
                except Exception as e:
                    st.error(f"Error guardando en Supabase: {e}")
                    st.session_state.trades.append(nuevo_trade)
            else:
                st.session_state.trades.append(nuevo_trade)
                st.success("Trade guardado localmente.")

            for k in ["val_entry", "val_sl", "val_tp", "val_rr"]:
                if k in st.session_state:
                    del st.session_state[k]

            st.rerun()

# ----------------- PESTAÑA 2: CALCULADORA DE LOTAJE -----------------
with tabs[1]:
    st.subheader("🧮 Calculadora de Lotaje & Gestión de Riesgo")
    st.write("Calcula exactamente cuántos lotes abrir según tu capital y distancia de Stop Loss.")

    col_calc1, col_calc2 = st.columns([1, 1])

    with col_calc1:
        balance_cuenta = st.number_input("💰 Capital / Balance de Cuenta ($ USD)", value=10000.0, step=500.0)
        porcentaje_riesgo = st.number_input("⚠️ Riesgo deseado por operación (%)", value=1.0, step=0.25)
        distancia_sl_pips = st.number_input("📏 Distancia de Stop Loss (Pips / Puntos)", value=20.0, step=1.0)
        
        tipo_instrumento = st.selectbox("📈 Tipo de Activo", ["Forex (Pares de Divisas)", "Oro / XAUUSD", "Índices (NAS100/US30)", "Criptos"])

    with col_calc2:
        monto_riesgo_usd = (balance_cuenta * porcentaje_riesgo) / 100.0
        st.markdown(f"### 💵 Dinero en Riesgo: **${monto_riesgo_usd:.2f} USD**")

        if distancia_sl_pips > 0:
            if "Forex" in tipo_instrumento or "Oro" in tipo_instrumento:
                lotes = monto_riesgo_usd / (distancia_sl_pips * 10)
            else:
                lotes = monto_riesgo_usd / distancia_sl_pips

            st.success(f"### 📊 Lote Recomendado: **{lotes:.2f} Lotes**")
            st.info(f"💡 Abre una posición de **{lotes:.2f} lotes** para arriesgar exactamente el **{porcentaje_riesgo}% (${monto_riesgo_usd:.2f} USD)**.")

# ----------------- PESTAÑA 3: ANÁLISIS VS IA -----------------
with tabs[2]:
    st.subheader("🆚 Comparar tu Análisis Técnico con la IA")
    
    col_a1, col_a2 = st.columns([1, 1])

    with col_a1:
        img_analisis = st.file_uploader("Sube o pega el Gráfico de tu Análisis", type=["jpg", "jpeg", "png"], key="upload_analysis")
        hipotesis_usuario = st.text_area(
            "✍️ Tu Análisis / Hipótesis:",
            placeholder="Ejemplo: Veo un barrido de liquidez en M15 y espero un retroceso a la zona de FVG...",
            height=120
        )
        btn_comparar = st.button("🔎 Comparar mi Análisis con IA")

    with col_a2:
        if img_analisis:
            st.image(img_analisis, caption="🖼️ Gráfico de Análisis", use_container_width=True)

        if img_analisis and btn_comparar:
            if openrouter_key:
                with st.spinner("Analizando tu hipótesis con la IA... 🧠⚡"):
                    try:
                        img_analisis.seek(0)
                        img_bytes = img_analisis.read()
                        base64_img = base64.b64encode(img_bytes).decode("utf-8")
                        mime_type = img_analisis.type

                        prompt_compare = (
                            f"El usuario propone esta hipótesis: '{hipotesis_usuario}'. "
                            "Examina la imagen del gráfico. Responde breve e indica: "
                            "1) ¿Coincide el gráfico con la hipótesis? "
                            "2) Riesgos no considerados. "
                            "3) Veredicto / Sugerencia."
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
                            st.session_state["ultimo_veredicto_ia"] = resultado_comparacion
                            st.session_state["ultima_img_analisis_b64"] = base64_img
                            st.session_state["ultima_hipotesis"] = hipotesis_usuario
                    except Exception as e:
                        st.error(f"Error durante la comparación: {e}")

        if "ultimo_veredicto_ia" in st.session_state and st.session_state["ultimo_veredicto_ia"]:
            st.markdown("### 🤖 Veredicto de la IA:")
            st.info(st.session_state["ultimo_veredicto_ia"])

# ----------------- PESTAÑA 4: PROYECCIONES NO EJECUTADAS -----------------
with tabs[3]:
    st.subheader("📁 Registro de Proyecciones No Ejecutadas")
    
    with st.expander("➕ Guardar Nueva Proyección Manualmente", expanded=False):
        c_p1, c_p2 = st.columns([1, 1])
        with c_p1:
            par_proy_sel = st.selectbox("Activo / Par", LISTA_ACTIVOS, key="par_proy_sel")
            par_proy = st.text_input("✍️ Escribe el Activo (Si elegiste 'Otro'):", key="par_proy_manual") if par_proy_sel == "Otro (Escribir manualmente)" else par_proy_sel
            notas_proy = st.text_area("Descripción / Hipótesis", key="notas_proy")
        with c_p2:
            img_proy = st.file_uploader("Captura de la Proyección", type=["jpg", "jpeg", "png"], key="upload_proy_manual")
        
        if st.button("💾 Guardar Proyección"):
            img_proy_b64 = None
            if img_proy:
                img_proy.seek(0)
                img_proy_b64 = base64.b64encode(img_proy.read()).decode("utf-8")

            nueva_proy_manual = {
                "par": par_proy if par_proy else "S/D",
                "direccion": "NO EJECUTADO",
                "rr": 0.0,
                "resultado": "PROYECCIÓN 📁",
                "notas": notas_proy,
                "evaluacion_ia": "Análisis guardado manualmente.",
                "imagen_b64": img_proy_b64,
                "es_analisis_previo": True,
                "fecha": str(datetime.now().date())
            }

            if supabase:
                try:
                    res = supabase.table("trades").insert(nueva_proy_manual).execute()
                    st.session_state.trades.append(res.data[0])
                    st.success("¡Proyección guardada! 📁")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error guardando: {e}")
            else:
                st.session_state.trades.append(nueva_proy_manual)
                st.rerun()

    st.markdown("---")
    analisis_filtrados = [t for t in st.session_state.trades if t.get("es_analisis_previo") == True or t.get("resultado") == "PROYECCIÓN 📁"]

    if not analisis_filtrados:
        st.info("No hay análisis no ejecutados guardados.")
    else:
        for a in reversed(analisis_filtrados):
            with st.expander(f"Proyección [{a.get('fecha', 'Sin fecha')}] | {a.get('par', 'Activo')} - {a.get('notas', 'Sin notas')[:40]}..."):
                c_img_a, c_info_a = st.columns([1, 1])
                with c_img_a:
                    if a.get("imagen_b64"):
                        st.image(f"data:image/png;base64,{a['imagen_b64']}", use_container_width=True)
                with c_info_a:
                    st.markdown(f"**{a.get('notas', '')}**")
                    st.markdown("---")
                    st.markdown("### 🤖 Veredicto")
                    st.markdown(a.get("evaluacion_ia", ""))

# ----------------- PESTAÑA 5: DIARIO Y PSICOTRADING -----------------
with tabs[4]:
    st.subheader("📖 Diario de Trading & Psicotrading")
    trades_ejecutados = [t for t in st.session_state.trades if not t.get("es_analisis_previo")]

    if not trades_ejecutados:
        st.write("No hay entradas ejecutadas guardadas aún.")
    else:
        for t in reversed(trades_ejecutados):
            fecha_str = t.get('fecha', 'Fecha N/A')
            emocion_str = t.get('emocion', 'Sin registro emocional')
            
            with st.expander(f"📅 {fecha_str} | Trade #{t.get('id', 'N/A')} | {t['par']} ({t['direccion']}) | {t['resultado']} | {emocion_str}"):
                c_before, c_after, c_info = st.columns([1, 1, 1])
                
                with c_before:
                    st.markdown("#### 🟢 ANTES (Entrada)")
                    if t.get("imagen_b64"):
                        st.image(f"data:image/png;base64,{t['imagen_b64']}", use_container_width=True)
                    else:
                        st.caption("Sin imagen.")

                with c_after:
                    st.markdown("#### 🔴 DESPUÉS (Resultado)")
                    if t.get("imagen_despues_b64"):
                        st.image(f"data:image/png;base64,{t['imagen_despues_b64']}", use_container_width=True)
                    else:
                        st.caption("Sin imagen.")

                with c_info:
                    st.markdown(f"**🧠 Estado Emocional:** {emocion_str}")
                    if t.get("notas_emocionales"):
                        st.markdown(f"**💭 Bitácora Mental:** {t.get('notas_emocionales')}")
                    st.markdown(f"**📝 Notas Técnicas:** {t.get('notas', '')}")
                    st.markdown("---")
                    st.markdown("### 🤖 Auditoría IA")
                    st.markdown(t.get("evaluacion_ia", ""))

# ----------------- PESTAÑA 6: DASHBOARD & PROGRESO -----------------
with tabs[5]:
    st.subheader("📊 Analytics & Evolución en el Tiempo")
    trades_ejecutados = [t for t in st.session_state.trades if not t.get("es_analisis_previo")]
    
    if trades_ejecutados:
        df = pd.DataFrame(trades_ejecutados)
        wins = len(df[df["resultado"].str.contains("WIN")])
        total = len(df)
        win_rate = round((wins / total) * 100, 1) if total > 0 else 0

        c_m1, c_m2, c_m3 = st.columns(3)
        c_m1.metric("Total Trades", total)
        c_m2.metric("Win Rate", f"{win_rate}%")
        c_m3.metric("R Promedio", f"1:{round(df['rr'].mean(), 2)}")

        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'])
            df = df.sort_values('fecha')
            fig_tiempo = px.histogram(df, x="fecha", color="resultado", title="Evolución de Trades por Fecha", template="plotly_dark")
            st.plotly_chart(fig_tiempo, use_container_width=True)

        fig_activos = px.bar(df, x="par", color="resultado", title="Rendimiento por Activo", template="plotly_dark")
        st.plotly_chart(fig_activos, use_container_width=True)
