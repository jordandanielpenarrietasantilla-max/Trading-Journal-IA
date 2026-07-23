import base64
import os
import streamlit as st

# Función en Python para poner una imagen local como fondo de pantalla
def aplicar_fondo_local(ruta_imagen):
    if os.path.exists(ruta_imagen):
        with open(ruta_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        
        css_fondo = f"""
        <style>
        .stApp {{
            background-image: linear-gradient(rgba(11, 14, 20, 0.85), rgba(11, 14, 20, 0.92)), url("data:image/jpeg;base64,{encoded_string}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            color: #e0e3eb !important;
        }}
        
        /* Efecto Vidrio / Glassmorphism en los paneles */
        div[data-testid="stColumn"] {{
            background: rgba(20, 24, 35, 0.70) !important;
            backdrop-filter: blur(12px) !important;
            -webkit-backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            padding: 20px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
        }}
        </style>
        """
        st.markdown(css_fondo, unsafe_allow_html=True)

# Llama a la función en Python usando el nombre de tu archivo
aplicar_fondo_local("fondo.jpg")
