import base64
import json
import os
from datetime import datetime, time
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from supabase import create_client, Client

# ---------------------------------------------------------------------
# 1. CONFIGURACIÓN INICIAL Y ESTILOS AVANZADOS (CSS NEÓN + SIDEBAR)
# ---------------------------------------------------------------------
st.set_page_config(page_title="AI Trading Journal & Auditor", page_icon="📈", layout="wide")

def aplicar_fondo_local(ruta_imagen):
    bg_style = ""
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        bg_style = f'background-image: linear-gradient(rgba(11, 14, 20, 0.85), rgba(11, 14, 20, 0.9)), url("data:image/jpeg;base64,{encoded_string}") !important;'

    css = f"""
    <style>
    @keyframes neonGlow {{
        0% {{ border-color: rgba(0, 242, 254, 0.4); box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); }}
        50% {{ border-color: rgba(41, 98, 255, 0.8); box-shadow: 0 0 20px rgba(41, 98, 255, 0.5); }}
        100% {{ border-color: rgba(0, 242, 254, 0.4); box-shadow: 0 0 10px rgba(0, 242, 254, 0.2); }}
    }}

    /* Fondo Global de la Aplicación */
    .stApp {{
        {bg_style}
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* Tipografía Global */
    .stApp, p, label, h1, h2, h3, h4, span, div, .stMarkdown, .stTabs {{
        color: #f0f3fa !important;
        font-family: 'Trebuchet MS', sans-serif !important;
    }}
    
    h1 {{
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800 !important;
    }}
    
    /* ELIMINAR EL FONDO BLANCO DE LA BARRA LATERAL (SIDEBAR) */
    section[data-testid="stSidebar"] {{
        background-color: rgba(11, 14, 20, 0.92) !important;
        border-right: 1px solid rgba(0, 210, 255, 0.3) !important;
        backdrop-filter: blur(15px) !important;
    }}

    section[data-testid="stSidebar"] div[data-testid="stSidebarUserContent"] {{
        padding-top: 1.5rem;
    }}

    /* Botón especial para Cerrar Sesión en el Sidebar */
    section[data-testid="stSidebar"] .stButton>button {{
        background: linear-gradient(135deg, #ff2a2a 0%, #990000 100%) !important;
        color: #ffffff !important;
        box-shadow: 0px 4px 15px rgba(255, 42, 42, 0.4) !important;
        border: none !important;
    }}
    
    section[data-testid="stSidebar"] .stButton>button:hover {{
        box-shadow: 0px 6px 25px rgba(255, 42, 42, 0.8) !important;
        transform: translateY(-2px) !important;
    }}
    
    /* Contenedores con Estilo Glassmorphism Neón */
    div[data-testid="stColumn"], div[data-testid="stExpander"], div[data-testid="stMetricBlock"] {{
        background: rgba(15, 20, 30, 0.85) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(0, 210, 255, 0.4) !important;
        border-radius: 14px !important;
        padding: 20px !important;
        animation: neonGlow 4s infinite ease-in-out !important;
    }}
    
    /* Inputs y Selects */
    .stNumberInput input, .stTextArea textarea, .stTextInput input {{
        background-color: #0b0e14 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
        border-radius: 8px !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #0b0e14 !important;
        color: #00f2fe !important;
        border: 1px solid rgba(0, 210, 255, 0.5) !important;
        border-radius: 8px !important;
    }}
    
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {{
        background-color: #0d121d !important;
        border: 1px solid #00f2fe !important;
    }}

    li[role="option"], div[role="option"] {{
        background-color: #0d121d !important;
        color: #ffffff !important;
    }}

    /* Botones Principales */
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
    st.markdown(css, unsafe_allow_html=True)

aplicar_fondo_local("fondo.jpg")

# ---------------------------------------------------------------------
# 2. CONEXIÓN SEGURA A SUPABASE & OPENROUTER
# ---------------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    try:
        raw_url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
        if raw_url.endswith("/rest/v1"):
            raw_url = raw_url[:-8]
        key = st.secrets["SUPABASE_KEY"].strip()
        return create_client(raw_url, key)
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        st.stop()

supabase = init_supabase()
openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_API_KEY")

if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None

# ---------------------------------------------------------------------
# 3. LANDING PAGE & AUTENTICACIÓN (LOGIN / REGISTRO)
# ---------------------------------------------------------------------
if st.session_state.usuario_logueado is None:
    st.title("⚡ AI Trading Journal & Auditor")
    st.write("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")

    col_land1, col_land2 = st.columns([1.2, 1])

    with col_land1:
        st.subheader("🚀 ¿Por qué usar este Diario de Trading?")
        st.markdown("""
        * **👁️ Escaneo Visual con IA:** Sube tus capturas de TradingView y deja que la IA extraiga entradas, SL, TP y Ratio Risk/Reward en segundos.
        * **🧠 Psicotrading y Bitácora Emocional:** Registra tu estado mental antes y después de cada sesión para detectar patrones emocionales perjudiciales.
        * **🧮 Calculadora de Lotaje Incorporada:** Ajusta el tamaño de posición exacto para Forex, Oro, Criptos e Índices sin salir de la plataforma.
        * **📁 Auditoría y Proyecciones:** Compara tu hipótesis técnica contra el modelo de IA y mide tu evolución temporal con métricas avanzadas.
        """)
        st.info("💡 **Acceso Privado:** Tus datos y capturas solo estarán visibles para ti mediante tu cuenta personal.")

    with col_land2:
        tab_login, tab_registro = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])

        with tab_login:
            st.subheader("Ingresa a tu Cuenta")
            email_in = st.text_input("Correo Electrónico", key="login_email")
            pass_in = st.text_input("Contraseña", type="password", key="login_pass")

            if st.button("🚀 Entrar al Diario"):
                if email_in and pass_in:
                    try:
                        res = supabase.auth.sign_in_with_password({"email": email_in, "password": pass_in})
                        st.session_state.usuario_logueado = res.user
                        st.success("¡Inicio de sesión exitoso!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error de acceso: {e}")
                else:
                    st.warning("Completa todos los campos.")

        with tab_registro:
            st.subheader("Crea tu Cuenta Gratis")
            email_reg = st.text_input("Correo Electrónico", key="reg_email")
            pass_reg = st.text_input("Crea tu Contraseña", type="password", key="reg_pass")

            if st.button("✨ Crear Cuenta"):
                if email_reg and pass_reg:
                    try:
                        res = supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                        st.success("¡Cuenta creada exitosamente! Inicia sesión.")
                    except Exception as e:
                        st.error(f"Error al registrar: {e}")
                else:
                    st.warning("Completa todos los campos.")

# ---------------------------------------------------------------------
# 4. PANEL PRIVADO COMPLETO (USUARIO AUTENTICADO)
# ---------------------------------------------------------------------
else:
    user_id = st.session_state.usuario_logueado.id
    user_email = st.session_state.usuario_logueado.email

    if "trades" not in st.session_state or st.session_state.get("last_user") != user_id:
        st.session_state.trades = []
        st.session_state.last_user = user_id
        try:
            res = supabase.table("trades").select("*").eq("user_id", user_id).order("id", desc=False).execute()
            st.session_state.trades = res.data
        except Exception as e:
            st.warning(f"No se pudieron cargar tus datos: {e}")

    # =================================================================
    # BARRA LATERAL (SIDEBAR): CENTRO DE CONTROL DE TRADER
    # =================================================================
    with st.sidebar:
        st.markdown("## 👤 Perfil Trader")

        # Foto de Perfil + Datos del Usuario
        col_av, col_dt = st.columns([1, 2])
        with col_av:
            if "foto_b64" in st.session_state and st.session_state["foto_b64"]:
                st.image(f"data:image/png;base64,{st.session_state['foto_b64']}", use_container_width=True)
            else:
                st.markdown("👤")
                
        with col_dt:
            alias_display = st.session_state.get("alias_user", "Trader Pro")
            st.markdown(f"**{alias_display}**")
            st.caption(f"`{user_email}`")

        # Editar Perfil (Modal/Expander)
        with st.expander("⚙️ Modificar Perfil", expanded=False):
            nuevo_alias = st.text_input("Nombre / Alias:", value=st.session_state.get("alias_user", "Trader Pro"))
            cap_actual_input = st.number_input("Capital Actual ($USD):", value=st.session_state.get("cap_actual", 10000.0), step=500.0)
            cap_meta_input = st.number_input("Meta de Capital ($USD):", value=st.session_state.get("cap_meta", 15000.0), step=1000.0)
            uploaded_avatar = st.file_uploader("Foto de Perfil", type=["jpg", "png"], key="upload_avatar")

            if st.button("💾 Guardar Cambios"):
                st.session_state["alias_user"] = nuevo_alias
                st.session_state["cap_actual"] = cap_actual_input
                st.session_state["cap_meta"] = cap_meta_input
                if uploaded_avatar:
                    st.session_state["foto_b64"] = base64.b64encode(uploaded_avatar.read()).decode("utf-8")
                st.success("¡Perfil actualizado!")
                st.rerun()

        st.markdown("---")

        # Progreso de Capital y Meta
        c_act = st.session_state.get("cap_actual", 10000.0)
        c_met = st.session_state.get("cap_meta", 15000.0)
        progreso_val = min(1.0, max(0.0, c_act / c_met)) if c_met > 0 else 0.0

        st.markdown(f"🎯 **Meta de Cuenta:** `${c_act:,.0f}` / `${c_met:,.0f}`")
        st.progress(progreso_val)

        st.markdown("---")

        # Reloj de Mercado
        st.markdown("### 🌐 Sesiones de Mercado")
        hora_utc = datetime.utcnow().time()
        
        # Estados simples de sesión (UTC)
        londres = "🟢 ABIERTO" if time(7,0) <= hora_utc <= time(16,0) else "🔴 CERRADO"
        ny = "🟢 ABIERTO" if time(12,0) <= hora_utc <= time(21,0) else "🔴 CERRADO"
        tokio = "🟢 ABIERTO" if time(0,0) <= hora_utc <= time(9,0) else "🔴 CERRADO"

        st.caption(f"🇬🇧 **Londres:** {londres}")
        st.caption(f"🇺🇸 **Nueva York:** {ny}")
        st.caption(f"🇯🇵 **Tokio / Asia:** {tokio}")

        st.markdown("---")

        # Reglas de Oro
        st.markdown("### 🎯 Reglas de Disciplina")
        st.markdown("""
        * 🛑 Acepta la pérdida antes de entrar.
        * ✂️ Corta pérdidas rápido.
        * 🧘 Evita la venganza (FOMO).
        """)

        st.markdown("---")

        # Botón de Cerrar Sesión
        if st.button("🚪 Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state.usuario_logueado = None
            st.session_state.trades = []
            st.rerun()

    # =================================================================
    # ÁREA PRINCIPAL Y HERRAMIENTAS
    # =================================================================
    st.title("📈 Journaling & AI Trading Audit")
    st.write("Mide tu progreso, audita con IA y gestiona tu psicología operativa.")

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
                            base64_image = base64.b64encode(uploaded_image_before.read()).decode("utf-8")
                            mime_type = uploaded_image_before.type

                            prompt_vision = (
                                "Analiza esta captura de TradingView. "
                                "Lee la herramienta de posición y responde ÚNICAMENTE un JSON estricto: "
                                '{"par": "XAU/USD (Oro)", "direccion": "SHORT", "precio_entrada": 4050.13, "stop_loss": 4045.16, "take_profit": 4112.65, "ratio_rr": 2.5}. '
                                "Si la ganancia está abajo es SHORT, si está arriba es LONG."
                            )

                            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
                            payload = {
                                "model": "google/gemini-2.5-flash",
                                "max_tokens": 300,
                                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt_vision}, {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}]}]
                            }

                            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload).json()
                            raw_text = res["choices"][0]["message"]["content"]
                            data = json.loads(raw_text[raw_text.find("{"):raw_text.rfind("}") + 1])

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
                par = st.text_input("✍️ Escribe el Activo:", placeholder="Ej. NVDA...") if par_seleccionado == "Otro (Escribir manualmente)" else par_seleccionado
                direccion = st.radio("Dirección", ["LONG 🟢", "SHORT 🔴"], index=0 if "LONG" in val_dir else 1, horizontal=True)
                precio_entrada = st.number_input("Precio Entrada", value=val_entry, format="%.2f")
                stop_loss = st.number_input("Stop Loss", value=val_sl, format="%.2f")

            with c2:
                take_profit = st.number_input("Take Profit", value=val_tp, format="%.2f")
                rr_final = val_rr
                if rr_final == 0.0 and stop_loss != 0 and precio_entrada != 0 and take_profit != 0:
                    rr_final = round(abs(take_profit - precio_entrada) / abs(precio_entrada - stop_loss), 2)

                st.info(f"**Ratio Risk:Reward:** 1 : {rr_final}")
                resultado = st.selectbox("Resultado", ["WIN 🟢", "LOSS 🔴", "BREAKEVEN ⚪"])

            st.subheader("🧠 Psicotrading & Estado Emocional")
            emocion = st.selectbox("¿Cómo te sentías?", ["🎯 Disciplinado / Neutro", "⚡ Enfocado / Confiado", "😰 Ansioso / Con Miedo", "🚀 Euforico / Sobreconfiado", "😡 Venganza (FOMO)", "😴 Cansado / Distraído"])
            notas_emocionales = st.text_area("Notas emocionales de la sesión:")
            notas = st.text_area("Notas técnicas sobre la operación:")

            if st.button("🚀 Guardar Trade Ejecutado"):
                evaluacion_ia = "Evaluación no disponible."
                if openrouter_key:
                    with st.spinner("Auditando con IA... 🧠"):
                        try:
                            prompt_audit = f"Audita este trade: Activo {par} ({direccion}), Entrada {precio_entrada}, SL {stop_loss}, TP {take_profit}, R:R 1:{rr_final}, Resultado {resultado}. Emoción: {emocion}. Notas: {notas}. Da una nota del 1 al 10 y un consejo."
                            headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
                            payload = {"model": "google/gemini-2.5-flash", "max_tokens": 300, "messages": [{"role": "user", "content": prompt_audit}]}
                            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload).json()
                            evaluacion_ia = res["choices"][0]["message"]["content"]
                        except Exception as e:
                            evaluacion_ia = f"Error auditando: {e}"

                img_b64_before = base64.b64encode(uploaded_image_before.getvalue()).decode("utf-8") if uploaded_image_before else None
                img_b64_after = base64.b64encode(uploaded_image_after.getvalue()).decode("utf-8") if uploaded_image_after else None

                nuevo_trade = {
                    "user_id": user_id, "par": par if par else "S/D", "direccion": direccion,
                    "precio_entrada": precio_entrada, "stop_loss": stop_loss, "take_profit": take_profit,
                    "rr": rr_final, "resultado": resultado, "notas": notas, "evaluacion_ia": evaluacion_ia,
                    "imagen_b64": img_b64_before, "imagen_despues_b64": img_b64_after,
                    "es_analisis_previo": False, "fecha": str(fecha_trade), "emocion": emocion, "notas_emocionales": notas_emocionales
                }

                try:
                    res = supabase.table("trades").insert(nuevo_trade).execute()
                    st.session_state.trades.append(res.data[0])
                    st.success("¡Trade guardado exitosamente!")
                except Exception as e:
                    st.error(f"Error guardando: {e}")

                for k in ["val_entry", "val_sl", "val_tp", "val_rr"]:
                    st.session_state.pop(k, None)
                st.rerun()

    # ----------------- PESTAÑA 2: CALCULADORA DE LOTAJE -----------------
    with tabs[1]:
        st.subheader("🧮 Calculadora de Lotaje & Gestión de Riesgo")
        col_calc1, col_calc2 = st.columns([1, 1])

        with col_calc1:
            balance_cuenta = st.number_input("💰 Capital ($ USD)", value=st.session_state.get("cap_actual", 10000.0), step=500.0)
            porcentaje_riesgo = st.number_input("⚠️ Riesgo deseado (%)", value=1.0, step=0.25)
            distancia_sl_pips = st.number_input("📏 Stop Loss (Pips / Puntos)", value=20.0, step=1.0)
            tipo_instrumento = st.selectbox("📈 Tipo de Activo", ["Forex (Pares de Divisas)", "Oro / XAUUSD", "Índices (NAS100/US30)", "Criptos"])

        with col_calc2:
            monto_riesgo_usd = (balance_cuenta * porcentaje_riesgo) / 100.0
            st.markdown(f"### 💵 Dinero en Riesgo: **${monto_riesgo_usd:.2f} USD**")

            if distancia_sl_pips > 0:
                lotes = monto_riesgo_usd / (distancia_sl_pips * 10) if "Forex" in tipo_instrumento or "Oro" in tipo_instrumento else monto_riesgo_usd / distancia_sl_pips
                st.success(f"### 📊 Lote Recomendado: **{lotes:.2f} Lotes**")

    # ----------------- PESTAÑA 3: ANÁLISIS VS IA -----------------
    with tabs[2]:
        st.subheader("🆚 Comparar tu Análisis Técnico con la IA")
        col_a1, col_a2 = st.columns([1, 1])

        with col_a1:
            img_analisis = st.file_uploader("Sube el Gráfico de tu Análisis", type=["jpg", "jpeg", "png"], key="upload_analysis")
            hipotesis_usuario = st.text_area("✍️ Tu Hipótesis:", placeholder="Ej. Veo un barrido de liquidez en M15...", height=120)
            btn_comparar = st.button("🔎 Comparar con IA")

        with col_a2:
            if img_analisis:
                st.image(img_analisis, caption="🖼️ Gráfico de Análisis", use_container_width=True)

            if img_analisis and btn_comparar and openrouter_key:
                with st.spinner("Analizando con la IA... 🧠⚡"):
                    try:
                        base64_img = base64.b64encode(img_analisis.read()).decode("utf-8")
                        prompt_compare = f"El usuario propone: '{hipotesis_usuario}'. Examina la imagen. Indica: 1) ¿Coincide el gráfico? 2) Riesgos no considerados. 3) Veredicto."
                        headers = {"Authorization": f"Bearer {openrouter_key}", "Content-Type": "application/json"}
                        payload = {"model": "google/gemini-2.5-flash", "max_tokens": 300, "messages": [{"role": "user", "content": [{"type": "text", "text": prompt_compare}, {"type": "image_url", "image_url": {"url": f"data:{img_analisis.type};base64,{base64_img}"}}]}]}
                        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload).json()
                        st.session_state["ultimo_veredicto_ia"] = res["choices"][0]["message"]["content"]
                    except Exception as e:
                        st.error(f"Error: {e}")

            if "ultimo_veredicto_ia" in st.session_state:
                st.info(st.session_state["ultimo_veredicto_ia"])

    # ----------------- PESTAÑA 4: PROYECCIONES -----------------
    with tabs[3]:
        st.subheader("📁 Registro de Proyecciones No Ejecutadas")
        with st.expander("➕ Guardar Nueva Proyección", expanded=False):
            c_p1, c_p2 = st.columns([1, 1])
            with c_p1:
                par_proy_sel = st.selectbox("Seleccionar Activo", LISTA_ACTIVOS, key="par_proy_sel")
                par_proy = st.text_input("✍️ Escribe el Activo:", key="par_proy_manual") if par_proy_sel == "Otro (Escribir manualmente)" else par_proy_sel
                notas_proy = st.text_area("Descripción / Hipótesis", key="notas_proy")
            with c_p2:
                img_proy = st.file_uploader("Captura de Proyección", type=["jpg", "jpeg", "png"], key="upload_proy_manual")

            if st.button("💾 Guardar Proyección"):
                img_proy_b64 = base64.b64encode(img_proy.read()).decode("utf-8") if img_proy else None
                nueva_proy = {
                    "user_id": user_id, "par": par_proy if par_proy else "S/D", "direccion": "NO EJECUTADO",
                    "rr": 0.0, "resultado": "PROYECCIÓN 📁", "notas": notas_proy, "evaluacion_ia": "Guardado manualmente.",
                    "imagen_b64": img_proy_b64, "es_analisis_previo": True, "fecha": str(datetime.now().date())
                }
                res = supabase.table("trades").insert(nueva_proy).execute()
                st.session_state.trades.append(res.data[0])
                st.success("¡Proyección guardada!")
                st.rerun()

        st.markdown("---")
        analisis_filtrados = [t for t in st.session_state.trades if t.get("es_analisis_previo") == True or t.get("resultado") == "PROYECCIÓN 📁"]
        for a in reversed(analisis_filtrados):
            with st.expander(f"Proyección [{a.get('fecha', 'N/A')}] | {a.get('par', 'Activo')}"):
                if a.get("imagen_b64"):
                    st.image(f"data:image/png;base64,{a['imagen_b64']}", use_container_width=True)
                st.write(a.get('notas', ''))

    # ----------------- PESTAÑA 5: DIARIO Y PSICOTRADING -----------------
    with tabs[4]:
        st.subheader("📖 Diario de Trading & Psicotrading")
        with st.expander("✍️ Escribir Bitácora Diaria", expanded=True):
            col_ps1, col_ps2 = st.columns([1, 1])
            with col_ps1:
                fecha_psico = st.date_input("Fecha", datetime.now(), key="fecha_psico")
                estado_emocional_dia = st.selectbox("Estado Emocional", ["🎯 Disciplinado / Neutro", "⚡ Enfocado / Confiado", "😰 Ansioso / Con Miedo", "🚀 Euforico / Sobreconfiado", "😡 Venganza (FOMO)", "😴 Cansado / Distraído"], key="estado_emocional_dia")
            with col_ps2:
                cumplio_plan = st.radio("¿Respetaste tu Plan?", ["Sí 🟢", "Parcialmente 🟡", "No 🔴"], horizontal=True, key="cumplio_plan")

            bitacora_texto = st.text_area("🧠 Reflexiones y Hábitos:", height=120, key="input_bitacora_texto")

            if st.button("💾 Guardar Reflexión"):
                if bitacora_texto.strip():
                    nueva_bitacora = {
                        "user_id": user_id, "par": "BITÁCORA DIARIA", "direccion": "PSICOTRADING",
                        "rr": 0.0, "resultado": cumplio_plan, "notas": f"Reflexión: {bitacora_texto}",
                        "evaluacion_ia": "Bitácora guardada.", "es_analisis_previo": True,
                        "fecha": str(fecha_psico), "emocion": estado_emocional_dia, "notas_emocionales": bitacora_texto
                    }
                    res = supabase.table("trades").insert(nueva_bitacora).execute()
                    st.session_state.trades.append(res.data[0])
                    st.success("¡Reflexión guardada!")
                    st.rerun()

        st.markdown("---")
        trades_ejecutados = [t for t in st.session_state.trades if not t.get("es_analisis_previo") or t.get("par") == "BITÁCORA DIARIA"]
        for t in reversed(trades_ejecutados):
            if t.get("par") == "BITÁCORA DIARIA":
                with st.expander(f"🧠 BITÁCORA [{t.get('fecha')}] | Plan: {t.get('resultado')}"):
                    st.info(t.get("notas_emocionales") or t.get("notas", ""))
            else:
                with st.expander(f"📅 {t.get('fecha')} | Trade #{t.get('id')} | {t['par']} ({t['direccion']}) | {t['resultado']}"):
                    c_b, c_a, c_i = st.columns([1, 1, 1])
                    with c_b:
                        if t.get("imagen_b64"): st.image(f"data:image/png;base64,{t['imagen_b64']}", use_container_width=True)
                    with c_a:
                        if t.get("imagen_despues_b64"): st.image(f"data:image/png;base64,{t['imagen_despues_b64']}", use_container_width=True)
                    with c_i:
                        st.write(f"**Emoción:** {t.get('emocion')}")
                        st.write(f"**Notas:** {t.get('notas')}")
                        st.info(t.get("evaluacion_ia"))

    # ----------------- PESTAÑA 6: DASHBOARD -----------------
    with tabs[5]:
        st.subheader("📊 Analytics & Evolución")
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
                fig_tiempo = px.histogram(df, x="fecha", color="resultado", title="Trades por Fecha", template="plotly_dark")
                st.plotly_chart(fig_tiempo, use_container_width=True)

            fig_activos = px.bar(df, x="par", color="resultado", title="Rendimiento por Activo", template="plotly_dark")
            st.plotly_chart(fig_activos, use_container_width=True)
