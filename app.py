import os
import base64
import json
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Diario de Trading IA", page_icon="📈", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #0b0e14 !important; color: #d1d4dc !important; }
    h1, h2, h3, h4, label, span { color: #e0e3eb !important; font-family: 'Trebuchet MS', sans-serif; }
    .stButton>button { background-color: #2962ff !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: bold !important; width: 100%; height: 45px; }
    .stButton>button:hover { background-color: #1e4bd8 !important; }
    </style>
""",
    unsafe_allow_html=True,
)

if "trades" not in st.session_state:
    st.session_state.trades = []

openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.environ.get(
    "OPENROUTER_API_KEY"
)

st.title("📈 Journaling & AI Trading Audit")
st.write(
    "Sube tu captura de TradingView para auto-detectar precios, posición y ratio R:R con IA."
)

tabs = st.tabs(
    ["➕ Registrar Trade", "📖 Diario & Auditoría IA", "📊 Dashboard & Analytics"]
)

with tabs[0]:
    col_left, col_right = st.columns([1, 1])

    with col_right:
        st.subheader("🖼️ Captura del Gráfico (TradingView)")
        uploaded_image = st.file_uploader(
            "Sube el Screenshot", type=["jpg", "jpeg", "png"]
        )

        if uploaded_image:
            st.image(
                uploaded_image, caption="Gráfico Cargado", use_container_width=True
            )

            if not openrouter_key:
                st.error(
                    "⚠️ No se detectó OPENROUTER_API_KEY en los Secrets de Streamlit."
                )
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
                                                "image_url": {
                                                    "url": f"data:{mime_type};base64,{base64_image}"
                                                },
                                            },
                                        ],
                                    }
                                ],
                            }

                            response = requests.post(
                                "https://openrouter.ai/api/v1/chat/completions",
                                headers=headers,
                                json=payload,
                            )
                            res_json = response.json()

                            if "choices" in res_json:
                                raw_text = res_json["choices"][0]["message"]["content"]
                                start_idx = raw_text.find("{")
                                end_idx = raw_text.rfind("}") + 1

                                if start_idx != -1 and end_idx != 0:
                                    json_str = raw_text[start_idx:end_idx]
                                    data = json.loads(json_str)

                                    st.session_state["val_par"] = data.get(
                                        "par", "XAU/USD"
                                    )
                                    st.session_state["val_dir"] = (
                                        "LONG 🟢"
                                        if data.get("direccion") == "LONG"
                                        else "SHORT 🔴"
                                    )
                                    st.session_state["val_entry"] = float(
                                        data.get("precio_entrada", 0.0)
                                    )
                                    st.session_state["val_sl"] = float(
                                        data.get("stop_loss", 0.0)
                                    )
                                    st.session_state["val_tp"] = float(
                                        data.get("take_profit", 0.0)
                                    )
                                    st.session_state["val_rr"] = float(
                                        data.get("ratio_rr", 0.0)
                                    )

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

        pares_lista = [
            "XAU/USD",
            "EUR/USD",
            "GBP/USD",
            "USD/JPY",
            "BTC/USDT",
            "NAS100",
            "US30",
        ]
        idx_par = pares_lista.index(val_par) if val_par in pares_lista else 0

        c1, c2 = st.columns(2)
        with c1:
            par = st.selectbox("Par / Activo", pares_lista, index=idx_par)
            dir_index = 0 if "LONG" in val_dir else 1
            direccion = st.radio(
                "Dirección", ["LONG 🟢", "SHORT 🔴"], index=dir_index, horizontal=True
            )
            precio_entrada = st.number_input(
                "Precio Entrada", value=val_entry, format="%.2f"
            )
            stop_loss = st.number_input("Stop Loss", value=val_sl, format="%.2f")

        with c2:
            take_profit = st.number_input("Take Profit", value=val_tp, format="%.2f")

            rr_final = val_rr
            if (
                rr_final == 0.0
                and stop_loss != 0
                and precio_entrada != 0
                and take_profit != 0
            ):
                riesgo = abs(precio_entrada - stop_loss)
                beneficio = abs(take_profit - precio_entrada)
                if riesgo > 0:
                    rr_final = round(beneficio / riesgo, 2)

            st.info(f"**Ratio Risk:Reward (R:R):** 1 : {rr_final}")
            resultado = st.selectbox(
                "Resultado", ["WIN 🟢", "LOSS 🔴", "BREAKEVEN ⚪"]
            )
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
                        res = requests.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers=headers,
                            json=payload,
                        )
                        evaluacion_ia = res.json()["choices"][0]["message"]["content"]
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
                "rr": rr_final,
                "resultado": resultado,
                "notas": notas,
                "evaluacion_ia": evaluacion_ia,
                "imagen_b64": img_b64,
            }
            st.session_state.trades.append(nuevo_trade)

            for k in ["val_entry", "val_sl", "val_tp", "val_rr"]:
                if k in st.session_state:
                    del st.session_state[k]

            st.success("¡Trade guardado exitosamente!")

with tabs[1]:
    st.subheader("📖 Historial de Trades")
    if not st.session_state.trades:
        st.write("No hay entradas aún.")
    else:
        for t in reversed(st.session_state.trades):
            with st.expander(
                f"Trade #{t['id']} | {t['par']} - {t['direccion']} | {t['resultado']} (R:R 1:{t['rr']})"
            ):
                c_img, c_info = st.columns([1, 1])
                with c_img:
                    if t["imagen_b64"]:
                        st.image(
                            f"data:image/png;base64,{t['imagen_b64']}",
                            use_container_width=True,
                        )
                with c_info:
                    st.markdown(f"**Notas:** {t['notas']}")
                    st.markdown("---")
                    st.markdown("### 🧠 Auditoría de IA")
                    st.markdown(t["evaluacion_ia"])

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

        fig = px.bar(
            df,
            x="par",
            color="resultado",
            title="Rendimiento por Activo",
            template="plotly_dark",
        )
        st.plotly_chart(fig, use_container_width=True)
