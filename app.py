import streamlit as st
from supabase import create_client, Client

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------
# ESTADO DE SESIÓN
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# FUNCIONES DE AUTH
# -----------------------------
def login(email, password):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.success("Login exitoso")
    except Exception as e:
        st.error(f"Error en login: {e}")

def register(email, password):
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.success("Usuario creado, ahora inicia sesión")
    except Exception as e:
        st.error(f"Error en registro: {e}")

def logout():
    st.session_state.user = None

# -----------------------------
# UI LOGIN / REGISTER
# -----------------------------
if st.session_state.user is None:
    st.title("🔐 Login")

    option = st.radio("Selecciona", ["Login", "Registro"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if option == "Login":
        if st.button("Entrar"):
            login(email, password)

    else:
        if st.button("Crear cuenta"):
            register(email, password)

# -----------------------------
# APP PRINCIPAL
# -----------------------------
else:
    st.title("📊 Trading Journal PRO")

    st.write(f"Bienvenido: {st.session_state.user.email}")

    if st.button("Cerrar sesión"):
        logout()

    st.subheader("Agregar Trade")

    asset = st.text_input("Activo (BTC, EURUSD...)")
    entry = st.number_input("Entrada")
    exit_price = st.number_input("Salida")
    result = st.selectbox("Resultado", ["Win", "Loss"])

    if st.button("Guardar Trade"):
        try:
            data = {
                "user_id": st.session_state.user.id,
                "asset": asset,
                "entry": entry,
                "exit": exit_price,
                "result": result
            }

            supabase.table("trades").insert(data).execute()

            st.success("Trade guardado")
        except Exception as e:
            st.error(f"Error guardando: {e}")

    st.subheader("Tus trades")

    try:
        response = supabase.table("trades") \
            .select("*") \
            .eq("user_id", st.session_state.user.id) \
            .execute()

        for trade in response.data:
            st.write(trade)

    except Exception as e:
        st.error(f"Error cargando datos: {e}")
