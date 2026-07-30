# ==========================================
# RELOJES Y SESIONES DE TRADING
# ==========================================

st.markdown("### 🌍 Sesiones de Trading")

def obtener_hora_zona(zona):
    ahora = datetime.datetime.now(ZoneInfo(zona))
    return ahora

def sesion_abierta(zona, hora_inicio, hora_fin):
    ahora = obtener_hora_zona(zona)
    hora_actual = ahora.hour + ahora.minute / 60

    if hora_inicio <= hora_fin:
        return hora_inicio <= hora_actual < hora_fin
    else:
        return hora_actual >= hora_inicio or hora_actual < hora_fin


# Hora local del usuario/navegador
st.components.v1.html(
    """
    <div style="
        font-family:'Segoe UI', monospace;
        font-size:18px;
        font-weight:bold;
        color:#00f2fe;
        background:#161b22;
        border:1px solid rgba(0,210,255,0.4);
        border-radius:8px;
        padding:8px;
        text-align:center;
    ">
        🕐 HORA LOCAL
        <div id="local-clock" style="font-size:22px;margin-top:3px;">
            00:00:00
        </div>
    </div>

    <script>
    function actualizarHora() {
        const ahora = new Date();

        document.getElementById("local-clock").innerHTML =
            ahora.toLocaleTimeString([], {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit"
            });
    }

    actualizarHora();
    setInterval(actualizarHora, 1000);
    </script>
    """,
    height=85
)

st.markdown("#### 📊 Mercados Globales")

# ------------------------------------------
# SÍDNEY
# ------------------------------------------

sydney = obtener_hora_zona("Australia/Sydney")
sydney_abierta = sesion_abierta(
    "Australia/Sydney",
    7,
    16
)

# ------------------------------------------
# TOKIO
# ------------------------------------------

tokyo = obtener_hora_zona("Asia/Tokyo")
tokyo_abierta = sesion_abierta(
    "Asia/Tokyo",
    9,
    18
)

# ------------------------------------------
# LONDRES
# ------------------------------------------

london = obtener_hora_zona("Europe/London")
london_abierta = sesion_abierta(
    "Europe/London",
    8,
    17
)

# ------------------------------------------
# NUEVA YORK
# ------------------------------------------

new_york = obtener_hora_zona("America/New_York")
new_york_abierta = sesion_abierta(
    "America/New_York",
    8,
    17
)


def mostrar_sesion(nombre, bandera, ciudad, ahora, abierta):
    if abierta:
        estado = "🟢 ABIERTA"
        estado_color = "#34d399"
    else:
        estado = "🔴 CERRADA"
        estado_color = "#f87171"

    st.markdown(
        f"""
        <div style="
            background:#121721;
            border:1px solid rgba(0,242,254,0.18);
            border-radius:10px;
            padding:10px;
            margin-bottom:8px;
        ">

            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
            ">

                <div>
                    <div style="
                        color:#f0f3fa;
                        font-weight:700;
                        font-size:15px;
                    ">
                        {bandera} {nombre}
                    </div>

                    <div style="
                        color:#8b95a7;
                        font-size:12px;
                        margin-top:2px;
                    ">
                        {ciudad}
                    </div>
                </div>

                <div style="text-align:right;">

                    <div style="
                        color:#00f2fe;
                        font-family:monospace;
                        font-size:17px;
                        font-weight:bold;
                    ">
                        {ahora.strftime("%H:%M:%S")}
                    </div>

                    <div style="
                        color:{estado_color};
                        font-size:11px;
                        font-weight:bold;
                        margin-top:2px;
                    ">
                        {estado}
                    </div>

                </div>

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


mostrar_sesion(
    "Sídney",
    "🇦🇺",
    "Australia",
    sydney,
    sydney_abierta
)

mostrar_sesion(
    "Tokio",
    "🇯🇵",
    "Japón",
    tokyo,
    tokyo_abierta
)

mostrar_sesion(
    "Londres",
    "🇬🇧",
    "Reino Unido",
    london,
    london_abierta
)

mostrar_sesion(
    "Nueva York",
    "🇺🇸",
    "Estados Unidos",
    new_york,
    new_york_abierta
)

st.markdown("---")

# ------------------------------------------
# RESUMEN DE SESIONES
# ------------------------------------------

sesiones_abiertas = sum([
    sydney_abierta,
    tokyo_abierta,
    london_abierta,
    new_york_abierta
])

if sesiones_abiertas == 0:
    st.info("🌙 Actualmente no hay una sesión principal abierta.")

elif sesiones_abiertas == 1:
    st.success("📈 Hay 1 sesión principal abierta.")

else:
    st.success(
        f"🔥 Hay {sesiones_abiertas} sesiones abiertas simultáneamente."
    )
