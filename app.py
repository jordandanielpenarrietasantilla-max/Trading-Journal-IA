import streamlit as st
from supabase import create_client, Client

# Configuración de página
st.set_page_config(page_title="AI Trading Journal & Auditor", layout="wide")

# Inicialización segura de Supabase
@st.cache_resource
def init_supabase() -> Client:
    try:
        # Extraer credenciales desde Secrets
        url = st.secrets["SUPABASE_URL"].strip().rstrip("/")
        
        # Si por error quedó el sufijo '/rest/v1', lo remueve
        if url.endswith("/rest/v1"):
            url = url[:-8]
            
        key = st.secrets["SUPABASE_KEY"].strip()
        return create_client(url, key)
    except Exception as e:
        st.error(f"Error al conectar con Supabase: {e}")
        st.stop()

supabase = init_supabase()

# -------------------------------------------------------------
# LÓGICA DE AUTENTICACIÓN (LOGIN Y REGISTRO)
# -------------------------------------------------------------

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.title("⚡ AI Trading Journal & Auditor")
    st.write("Audita tu operativa con Inteligencia Artificial, registra tus emociones y lleva tu disciplina al siguiente nivel.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🚀 ¿Por qué usar este Diario de Trading?")
        st.markdown("""
        * 👁️ **Escaneo Visual con IA:** Sube tus capturas de TradingView y extrae entradas, SL, TP y Ratio Risk/Reward.
        * 🧠 **Psicotrading y Bitácora Emocional:** Detecta patrones emocionales perjudiciales.
        * 🧮 **Calculadora de Lotaje Incorporada:** Ajusta el tamaño de posición exacto.
        * 📊 **Auditoría y Proyecciones:** Compara tu hipótesis técnica contra la IA.
        * 🔒 **Acceso Privado:** Tus datos solo están visibles para ti.
        """)
        
    with col2:
        tab_login, tab_register = st.tabs(["🔑 Iniciar Sesión", "📝 Registrarse"])
        
        # --- TAB REGISTRO ---
        with tab_register:
            st.subheader("Crea tu Cuenta Gratis")
            email_reg = st.text_input("Correo Electrónico", key="reg_email")
            pass_reg = st.text_input("Crea tu Contraseña", type="password", key="reg_pass")
            
            if st.button("🚀 Crear Cuenta", use_container_width=True):
                if email_reg and pass_reg:
                    try:
                        response = supabase.auth.sign_up({"email": email_reg, "password": pass_reg})
                        st.success("¡Cuenta creada exitosamente! Revisa tu correo o inicia sesión.")
                    except Exception as err:
                        st.error(f"Error al registrar: {err}")
                else:
                    st.warning("Por favor completa todos los campos.")
                    
        # --- TAB INICIO DE SESIÓN ---
        with tab_login:
            st.subheader("Ingresa a tu Cuenta")
            email_log = st.text_input("Correo Electrónico", key="log_email")
            pass_log = st.text_input("Contraseña", type="password", key="log_pass")
            
            if st.button("Ingresar", use_container_width=True):
                if email_log and pass_log:
                    try:
                        response = supabase.auth.sign_in_with_password({"email": email_log, "password": pass_log})
                        st.session_state.user = response.user
                        st.rerun()
                    except Exception as err:
                        st.error(f"Error al iniciar sesión: {err}")
                else:
                    st.warning("Por favor ingresa tu correo y contraseña.")

else:
    # -------------------------------------------------------------
    # PANEL PRINCIPAL (USUARIO AUTENTICADO)
    # -------------------------------------------------------------
    st.sidebar.write(f"Bienvenido, **{st.session_state.user.email}**")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.user = None
        st.rerun()
        
    st.title("🎯 Dashboard & Auditoría de Trading")
    st.write("¡Conexión a Supabase establecida correctamente!")
