from __future__ import annotations

import base64
from typing import Any

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

from core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)

from core.metrics import (
    calculate_summary,
    pnl_by_emotion,
)

from core.vision import (
    VisionError,
    scan_trade,
)


# =========================================================
# AXION PRIME X10 PRO
# HERRAMIENTAS SECUNDARIAS
# =========================================================


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Convierte valores a float de forma segura.
    """

    try:
        return float(value or 0)

    except (TypeError, ValueError):
        return default


def _money(
    value: Any,
) -> str:
    """
    Formatea un valor como dinero.
    """

    return f"${_safe_float(value):,.2f}"


def _section_header(
    eyebrow: str,
    title: str,
    description: str,
) -> None:
    """
    Encabezado reutilizable para las herramientas.
    """

    st.markdown(
        f"""
        <div class="ax-hero">

            <div
                style="
                    color:#25e5ff;
                    font-size:9px;
                    font-weight:950;
                    letter-spacing:2px;
                "
            >
                {eyebrow}
            </div>

            <div class="ax-title">
                {title}
            </div>

            <div class="ax-sub">
                {description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# CHAT IA
# =========================================================


def _build_trading_context(
    df: pd.DataFrame,
) -> str:
    """
    Construye un resumen pequeño de las operaciones
    para enviarlo al chat de IA.
    """

    initial_capital = float(
        st.session_state.get(
            "capital_actual",
            10000.0,
        )
    )

    summary = calculate_summary(
        df,
        initial_capital,
    )

    context = f"""
Resumen de la cuenta del trader:

Capital inicial: {initial_capital}
Balance actual: {summary.get("balance", initial_capital)}
PnL acumulado: {summary.get("pnl", 0)}
Total de trades: {summary.get("total", 0)}
Ganadores: {summary.get("wins", 0)}
Perdedores: {summary.get("losses", 0)}
Break even: {summary.get("break_even", 0)}
Win rate: {summary.get("win_rate", 0):.2f}%
Profit factor: {summary.get("profit_factor", 0):.2f}
R:R promedio: {summary.get("average_rr", 0):.2f}
Drawdown máximo: {summary.get("drawdown_percent", 0):.2f}%
Ganancia promedio: {summary.get("average_win", 0):.2f}
Pérdida promedio: {summary.get("average_loss", 0):.2f}
Mejor trade: {summary.get("best_trade", 0):.2f}
Peor trade: {summary.get("worst_trade", 0):.2f}
"""

    if not df.empty:

        recent_columns = [
            column
            for column in [
                "fecha",
                "par",
                "direccion",
                "resultado",
                "beneficio_usd",
                "rr",
                "emocion",
                "notas_emocionales",
            ]
            if column in df.columns
        ]

        recent = (
            df.sort_values(
                [
                    "fecha_dt",
                    "created_at_dt",
                ],
                ascending=False,
            )
            .head(10)
        )

        context += (
            "\nÚltimas operaciones:\n"
            + recent[
                recent_columns
            ].to_string(
                index=False
            )
        )

    return context


def _ask_openrouter(
    prompt: str,
    context: str,
) -> str:
    """
    Envía una pregunta a OpenRouter.
    """

    if not OPENROUTER_API_KEY:

        raise RuntimeError(
            "OPENROUTER_API_KEY no está configurada "
            "en Streamlit Secrets."
        )

    headers = {
        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "https://streamlit.io",

        "X-Title":
            "AXION PRIME X10 PRO",
    }

    system_message = """
Eres AXION Coach, un auditor profesional de trading.

Analiza solamente los datos suministrados por el diario
del usuario.

Debes responder en español, con claridad y sin exagerar.

No prometas rentabilidad.
No inventes datos que no aparezcan en el contexto.
No des señales de compra o venta.
No indiques que una operación futura está garantizada.

Tu misión es ayudar al trader a detectar:

- errores de disciplina;
- patrones emocionales;
- problemas de gestión de riesgo;
- activos con mejor o peor desempeño;
- fortalezas de su sistema;
- acciones concretas para mejorar.

Usa explicaciones sencillas, pero profesionales.
"""

    payload = {
        "model": OPENROUTER_MODEL,
        "temperature": 0.3,
        "max_tokens": 1200,
        "messages": [
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": (
                    context
                    + "\n\nPregunta del trader:\n"
                    + prompt
                ),
            },
        ],
    }

    try:

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90,
        )

    except requests.Timeout as exc:

        raise RuntimeError(
            "La IA tardó demasiado en responder."
        ) from exc

    except requests.ConnectionError as exc:

        raise RuntimeError(
            "No se pudo conectar con OpenRouter."
        ) from exc

    if response.status_code != 200:

        raise RuntimeError(
            f"OpenRouter HTTP {response.status_code}: "
            f"{response.text[:700]}"
        )

    try:

        payload_response = response.json()

    except ValueError as exc:

        raise RuntimeError(
            "OpenRouter devolvió una respuesta inválida."
        ) from exc

    choices = payload_response.get(
        "choices",
        [],
    )

    if not choices:

        raise RuntimeError(
            "OpenRouter no devolvió una respuesta."
        )

    content = (
        choices[0]
        .get("message", {})
        .get("content", "")
    )

    if isinstance(content, list):

        content = "\n".join(
            str(item.get("text", ""))
            if isinstance(item, dict)
            else str(item)
            for item in content
        )

    answer = str(
        content
    ).strip()

    if not answer:

        raise RuntimeError(
            "La IA devolvió una respuesta vacía."
        )

    return answer


def render_chat(
    df: pd.DataFrame,
) -> None:
    """
    Chat del trader basado en sus operaciones guardadas.
    """

    _section_header(
        "AXION PRIME · AI COACH",
        "Chat IA",
        (
            "Consulta patrones de rendimiento, disciplina, "
            "riesgo y psicología utilizando los datos "
            "reales de tu journal."
        ),
    )

    if "chat_history" not in st.session_state:

        st.session_state.chat_history = []

    if df.empty:

        st.info(
            "Registra operaciones para que AXION Coach "
            "pueda analizar tu rendimiento."
        )

    for message in st.session_state.chat_history:

        role = message.get(
            "role",
            "assistant",
        )

        content = message.get(
            "content",
            "",
        )

        with st.chat_message(
            role
        ):

            st.markdown(
                content
            )

    prompt = st.chat_input(
        "Pregunta sobre tu operativa..."
    )

    if not prompt:

        return

    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            prompt
        )

    with st.chat_message(
        "assistant"
    ):

        if df.empty:

            answer = (
                "Todavía no hay operaciones suficientes "
                "para realizar una auditoría basada en datos."
            )

            st.markdown(
                answer
            )

        else:

            try:

                context = _build_trading_context(
                    df
                )

                with st.spinner(
                    "AXION Coach está analizando tus datos..."
                ):

                    answer = _ask_openrouter(
                        prompt,
                        context,
                    )

                st.markdown(
                    answer
                )

            except Exception as exc:

                answer = (
                    "No pude completar el análisis: "
                    f"{exc}"
                )

                st.error(
                    answer
                )

    st.session_state.chat_history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )


# =========================================================
# PSICOTRADING
# =========================================================


def render_psychology(
    df: pd.DataFrame,
) -> None:
    """
    Panel de psicotrading basado en las emociones
    registradas en las operaciones.
    """

    _section_header(
        "AXION PRIME · BEHAVIOR INTELLIGENCE",
        "Psicotrading",
        (
            "Relaciona emociones, decisiones y resultados "
            "para identificar los comportamientos que "
            "fortalecen o destruyen tu consistencia."
        ),
    )

    reflection = st.text_area(
        "Reflexión de la sesión",
        height=160,
        placeholder=(
            "¿Cómo te sentiste hoy? ¿Seguiste tu plan? "
            "¿Operaste por impulso, miedo o FOMO?"
        ),
        key="psychology_reflection",
    )

    if st.button(
        "💾 Guardar reflexión en esta sesión",
        use_container_width=True,
        key="save_session_reflection",
    ):

        st.session_state.last_reflection = (
            reflection
        )

        st.success(
            "Reflexión guardada durante esta sesión."
        )

    st.markdown("---")

    if df.empty:

        st.info(
            "Registra trades con estados emocionales "
            "para desbloquear este panel."
        )

        return

    emotion_df = pnl_by_emotion(
        df
    )

    if emotion_df.empty:

        st.info(
            "Las operaciones guardadas todavía no incluyen "
            "información emocional."
        )

        return

    total_trades = int(
        emotion_df[
            "trades"
        ].sum()
    )

    best_row = emotion_df.sort_values(
        "pnl_total",
        ascending=False,
    ).iloc[0]

    worst_row = emotion_df.sort_values(
        "pnl_total",
        ascending=True,
    ).iloc[0]

    metrics = st.columns(4)

    metrics[0].metric(
        "Trades analizados",
        total_trades,
    )

    metrics[1].metric(
        "Estados detectados",
        len(emotion_df),
    )

    metrics[2].metric(
        "Mejor estado",
        str(
            best_row.get(
                "emocion",
                "-",
            )
        ),
        _money(
            best_row.get(
                "pnl_total"
            )
        ),
    )

    metrics[3].metric(
        "Estado de mayor pérdida",
        str(
            worst_row.get(
                "emocion",
                "-",
            )
        ),
        _money(
            worst_row.get(
                "pnl_total"
            )
        ),
    )

    fig = px.bar(
        emotion_df,
        x="emocion",
        y="pnl_total",
        hover_data=[
            "trades",
            "pnl_promedio",
        ],
        title="PnL acumulado por estado emocional",
    )

    fig.update_layout(
        template="plotly_dark",
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,10,27,.78)",
        xaxis_title="Estado emocional",
        yaxis_title="PnL",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    st.dataframe(
        emotion_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# ANÁLISIS VISUAL IA
# =========================================================


def render_analysis() -> None:
    """
    Auditor visual independiente para capturas
    de TradingView.
    """

    _section_header(
        "AXION PRIME · VISION ENGINE",
        "Análisis IA",
        (
            "Extrae parámetros visibles de una captura "
            "de TradingView sin guardarla como operación."
        ),
    )

    chart = st.file_uploader(
        "Subir captura del gráfico",
        type=[
            "png",
            "jpg",
            "jpeg",
            "webp",
        ],
        key="analysis_chart",
    )

    if chart is None:

        st.info(
            "Sube una captura para activar el análisis."
        )

        return

    st.image(
        chart,
        caption="Captura seleccionada",
        use_container_width=True,
    )

    if not st.button(
        "🔍 ANALIZAR CAPTURA",
        use_container_width=True,
        key="analysis_scan_button",
    ):

        return

    try:

        with st.spinner(
            "AXION Vision está leyendo el gráfico..."
        ):

            result = scan_trade(
                chart.getvalue(),
                chart.type
                or "image/jpeg",
            )

        st.success(
            "Lectura visual completada."
        )

        metrics = st.columns(4)

        metrics[0].metric(
            "Activo",
            result.get("asset")
            or "No detectado",
        )

        metrics[1].metric(
            "Dirección",
            result.get("direction")
            or "No detectada",
        )

        metrics[2].metric(
            "Entrada",
            result.get("entry")
            if result.get("entry") is not None
            else "No detectada",
        )

        metrics[3].metric(
            "Confianza",
            f"{_safe_float(result.get('confidence')):.0f}%",
        )

        secondary = st.columns(3)

        secondary[0].metric(
            "Stop Loss",
            result.get("sl")
            if result.get("sl") is not None
            else "No detectado",
        )

        secondary[1].metric(
            "Take Profit",
            result.get("tp")
            if result.get("tp") is not None
            else "No detectado",
        )

        secondary[2].metric(
            "Timeframe",
            result.get("timeframe")
            or "No detectado",
        )

        with st.expander(
            "Ver JSON completo"
        ):

            st.json(
                result
            )

    except VisionError as exc:

        st.error(
            f"No se pudo analizar la captura: {exc}"
        )

    except Exception as exc:

        st.error(
            f"Error inesperado: {exc}"
        )


# =========================================================
# PROYECCIONES
# =========================================================


def render_projections() -> None:
    """
    Calculadora de expectativa y proyección de capital.
    """

    _section_header(
        "AXION PRIME · EXPECTANCY LAB",
        "Proyecciones",
        (
            "Simula escenarios matemáticos basados en "
            "win rate, riesgo, frecuencia y ratio R:R."
        ),
    )

    left, right = st.columns(2)

    with left:

        capital = st.number_input(
            "Capital inicial",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    "capital_actual",
                    10000.0,
                )
            ),
            step=100.0,
            key="projection_capital",
        )

        trades_month = st.slider(
            "Operaciones por mes",
            min_value=1,
            max_value=100,
            value=20,
            key="projection_trades_month",
        )

        months = st.slider(
            "Meses de proyección",
            min_value=1,
            max_value=36,
            value=12,
            key="projection_months",
        )

    with right:

        win_rate = st.slider(
            "Win rate estimado (%)",
            min_value=1,
            max_value=99,
            value=55,
            key="projection_win_rate",
        )

        average_rr = st.number_input(
            "R:R promedio",
            min_value=0.1,
            value=2.0,
            step=0.1,
            key="projection_average_rr",
        )

        risk_percent = st.number_input(
            "Riesgo por operación (%)",
            min_value=0.01,
            max_value=20.0,
            value=1.0,
            step=0.1,
            key="projection_risk",
        )

    probability_win = (
        win_rate
        / 100
    )

    probability_loss = (
        1
        - probability_win
    )

    expectancy_r = (
        probability_win
        * average_rr
        -
        probability_loss
    )

    expected_monthly_percent = (
        expectancy_r
        * risk_percent
        * trades_month
    )

    expected_monthly_money = (
        capital
        * expected_monthly_percent
        / 100
    )

    projected_capital = (
        capital
        * (
            1
            + expected_monthly_percent
            / 100
        ) ** months
    )

    metrics = st.columns(4)

    metrics[0].metric(
        "Expectativa por trade",
        f"{expectancy_r:.2f}R",
    )

    metrics[1].metric(
        "Expectativa mensual",
        f"{expected_monthly_percent:.2f}%",
    )

    metrics[2].metric(
        "Resultado mensual estimado",
        _money(
            expected_monthly_money
        ),
    )

    metrics[3].metric(
        f"Capital proyectado ({months} meses)",
        _money(
            projected_capital
        ),
    )

    projection_rows = []

    current_capital = float(
        capital
    )

    for month in range(
        1,
        months + 1,
    ):

        current_capital *= (
            1
            + expected_monthly_percent
            / 100
        )

        projection_rows.append(
            {
                "Mes": month,
                "Capital proyectado":
                    current_capital,
            }
        )

    projection_df = pd.DataFrame(
        projection_rows
    )

    fig = px.line(
        projection_df,
        x="Mes",
        y="Capital proyectado",
        markers=True,
        title="Proyección matemática del capital",
    )

    fig.update_layout(
        template="plotly_dark",
        height=430,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,10,27,.78)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    st.warning(
        "Esta proyección es matemática y no representa "
        "una garantía de resultados futuros."
    )


# =========================================================
# CALCULADORA DE LOTAJE
# =========================================================


def render_lotage() -> None:
    """
    Calculadora general de tamaño de posición.
    """

    _section_header(
        "AXION PRIME · RISK CORE",
        "Calculadora de lotaje",
        (
            "Calcula el riesgo monetario y un tamaño "
            "estimado de posición antes de ejecutar."
        ),
    )

    left, right = st.columns(2)

    with left:

        balance = st.number_input(
            "Balance de la cuenta ($)",
            min_value=0.0,
            value=float(
                st.session_state.get(
                    "capital_actual",
                    10000.0,
                )
            ),
            step=100.0,
            key="lotage_balance",
        )

        risk_percent = st.number_input(
            "Riesgo por operación (%)",
            min_value=0.01,
            max_value=100.0,
            value=1.0,
            step=0.1,
            key="lotage_risk_percent",
        )

        stop_distance = st.number_input(
            "Distancia al Stop Loss",
            min_value=0.00001,
            value=20.0,
            step=1.0,
            format="%.5f",
            key="lotage_stop_distance",
        )

    with right:

        value_per_point = st.number_input(
            "Valor por punto de 1 lote ($)",
            min_value=0.00001,
            value=10.0,
            step=1.0,
            format="%.5f",
            key="lotage_value_per_point",
        )

        commission = st.number_input(
            "Comisión estimada ($)",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key="lotage_commission",
        )

    risk_money = (
        balance
        * risk_percent
        / 100
    )

    usable_risk = max(
        0.0,
        risk_money
        - commission,
    )

    denominator = (
        stop_distance
        * value_per_point
    )

    lot_size = (
        usable_risk
        / denominator
        if denominator > 0
        else 0.0
    )

    metrics = st.columns(4)

    metrics[0].metric(
        "Riesgo máximo",
        _money(
            risk_money
        ),
    )

    metrics[1].metric(
        "Riesgo después de comisión",
        _money(
            usable_risk
        ),
    )

    metrics[2].metric(
        "Lotaje estimado",
        f"{lot_size:.3f}",
    )

    metrics[3].metric(
        "Pérdida máxima estimada",
        _money(
            risk_money
        ),
    )

    st.info(
        "El valor del punto cambia según el activo, "
        "broker y tipo de contrato. Verifica siempre "
        "la especificación del instrumento antes de operar."
    )
