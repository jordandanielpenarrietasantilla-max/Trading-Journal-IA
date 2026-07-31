from __future__ import annotations

import datetime
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.metrics import (
    build_equity_curve,
    calculate_prop_firm_score,
    calculate_summary,
    pnl_by_asset,
)


# =========================================================
# AXION PRIME X10 PRO
# DASHBOARD PRINCIPAL
# =========================================================


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def _format_money(
    value: Any,
) -> str:
    number = _safe_float(value)
    return f"${number:,.2f}"


def _metric_card(
    label: str,
    value: str,
    subtitle: str,
    accent: str,
    footer_left: str = "",
    footer_right: str = "",
) -> None:
    st.markdown(
        f"""
        <div
            class="ax-card"
            style="
                min-height:155px;
                position:relative;
                overflow:hidden;
                padding:19px;
            "
        >
            <div
                style="
                    color:#7f8bad;
                    font-size:9px;
                    letter-spacing:1.5px;
                    font-weight:900;
                "
            >
                {label}
            </div>

            <div
                style="
                    margin-top:14px;
                    color:{accent};
                    font-size:29px;
                    line-height:1;
                    font-weight:950;
                "
            >
                {value}
            </div>

            <div
                style="
                    margin-top:13px;
                    display:flex;
                    justify-content:space-between;
                    gap:8px;
                    color:#8b98b8;
                    font-size:9px;
                "
            >
                <span>{subtitle}</span>
                <span>{footer_right}</span>
            </div>

            <div
                style="
                    position:absolute;
                    left:18px;
                    right:18px;
                    bottom:14px;
                    height:3px;
                    border-radius:999px;
                    background:
                        linear-gradient(
                            90deg,
                            {accent},
                            #9146ff
                        );
                    box-shadow:
                        0 0 15px {accent};
                    opacity:.9;
                "
            ></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_header(
    trader_name: str,
) -> None:
    current_date = datetime.datetime.now().strftime(
        "%d %b %Y"
    ).upper()

    st.markdown(
        f"""
        <div class="ax-hero">
            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    gap:20px;
                    flex-wrap:wrap;
                "
            >
                <div>
                    <div
                        style="
                            color:#25e5ff;
                            font-size:9px;
                            font-weight:950;
                            letter-spacing:2px;
                        "
                    >
                        AXION PRIME · PERFORMANCE COMMAND OS
                    </div>

                    <div class="ax-title">
                        ¡Buenos días, {trader_name}! 👋
                    </div>

                    <div class="ax-sub">
                        Disciplina hoy, libertad mañana.
                        Tu desempeño vive en los datos.
                    </div>
                </div>

                <div
                    style="
                        display:flex;
                        align-items:center;
                        gap:12px;
                        flex-wrap:wrap;
                    "
                >
                    <div
                        style="
                            color:#dce6ff;
                            font-size:11px;
                            font-weight:900;
                        "
                    >
                        {current_date}
                    </div>

                    <div class="ax-status">
                        ● MERCADOS ACTIVOS
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_equity_chart(
    equity_df: pd.DataFrame,
    initial_capital: float,
) -> None:
    st.markdown(
        """
        <div
            class="ax-card"
            style="
                margin-bottom:10px;
                padding:16px 19px;
            "
        >
            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                "
            >
                <strong>📈 CURVA DE EQUITY</strong>

                <span
                    style="
                        color:#7180a4;
                        font-size:8px;
                        letter-spacing:1.2px;
                    "
                >
                    BALANCE ACUMULADO
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if equity_df.empty:
        st.markdown(
            """
            <div
                class="ax-card"
                style="
                    min-height:355px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    text-align:center;
                "
            >
                <div>
                    <div
                        style="
                            font-size:42px;
                            color:#25e5ff;
                        "
                    >
                        ◇
                    </div>

                    <div
                        style="
                            font-size:17px;
                            font-weight:900;
                            margin-top:12px;
                        "
                    >
                        Tu curva comienza con tu primer trade.
                    </div>

                    <div
                        style="
                            color:#8290b1;
                            font-size:11px;
                            margin-top:8px;
                        "
                    >
                        Registra una operación para activar
                        rendimiento, consistencia y drawdown.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    chart_df = equity_df.copy()

    chart_df["fecha_dt"] = pd.to_datetime(
        chart_df["fecha_dt"],
        errors="coerce",
    )

    chart_df = chart_df.dropna(
        subset=["fecha_dt"]
    )

    if chart_df.empty:
        st.info(
            "No existen fechas válidas para construir la curva."
        )
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df["fecha_dt"],
            y=chart_df["equity"],
            mode="lines",
            line={
                "width": 3,
                "color": "#7c4dff",
            },
            fill="tozeroy",
            fillcolor="rgba(67, 104, 255, 0.16)",
            hovertemplate=(
                "%{x|%d/%m/%Y}<br>"
                "Balance: $%{y:,.2f}<extra></extra>"
            ),
        )
    )

    fig.add_hline(
        y=float(initial_capital),
        line_dash="dot",
        line_color="rgba(37,229,255,.55)",
    )

    fig.update_layout(
        height=355,
        margin={
            "l": 20,
            "r": 20,
            "t": 20,
            "b": 20,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(4,9,24,.80)",
        font={
            "color": "#9ba8c7",
        },
        xaxis={
            "showgrid": False,
            "zeroline": False,
        },
        yaxis={
            "gridcolor": "rgba(126,142,181,.10)",
            "tickprefix": "$",
            "zeroline": False,
        },
        hoverlabel={
            "bgcolor": "#080f22",
            "bordercolor": "#25e5ff",
        },
        showlegend=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )


def _render_setup_panel(
    df: pd.DataFrame,
) -> None:
    st.markdown(
        """
        <div
            class="ax-card"
            style="
                padding:16px 19px;
                margin-bottom:10px;
            "
        >
            <div
                style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                "
            >
                <strong>🖼️ CAPTURA DEL SETUP</strong>

                <span
                    style="
                        color:#7180a4;
                        font-size:8px;
                        letter-spacing:1.2px;
                    "
                >
                    AI VISION READY
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty:
        st.markdown(
            """
            <div
                class="ax-card"
                style="
                    min-height:355px;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    text-align:center;
                "
            >
                <div>
                    <div style="font-size:43px">
                        🧠
                    </div>

                    <div
                        style="
                            margin-top:13px;
                            font-size:16px;
                            font-weight:900;
                        "
                    >
                        AXION Vision está listo.
                    </div>

                    <div
                        style="
                            margin-top:7px;
                            color:#8491b2;
                            font-size:11px;
                        "
                    >
                        Escanea tu primer setup para activar el análisis.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            "🧠 Escanear primer setup",
            use_container_width=True,
            key="dashboard_scan_first",
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

        return

    last_trade = df.sort_values(
        ["fecha_dt", "created_at_dt"],
        ascending=False,
    ).iloc[0]

    image_value = (
        last_trade.get("img_before")
        or last_trade.get("img_after")
        or ""
    )

    par = last_trade.get(
        "par",
        "Sin activo",
    )

    direction = last_trade.get(
        "direccion",
        "-",
    )

    pnl = _safe_float(
        last_trade.get("beneficio_usd")
    )

    confidence = last_trade.get(
        "confidence",
        "-",
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Activo",
        str(par),
    )

    c2.metric(
        "Dirección",
        str(direction),
    )

    c3.metric(
        "PnL",
        _format_money(pnl),
    )

    if image_value:
        st.image(
            image_value,
            use_container_width=True,
        )
    else:
        st.markdown(
            """
            <div
                class="ax-card"
                style="
                    min-height:230px;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                "
            >
                <div
                    style="
                        color:#7f8bad;
                        text-align:center;
                    "
                >
                    📷 El último trade no tiene captura guardada.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if confidence != "-":
        st.caption(
            f"Confianza de lectura IA: {confidence}%"
        )


def _render_secondary_cards(
    summary: dict,
    df: pd.DataFrame,
) -> None:
    cards = st.columns(5)

    average_rr = _safe_float(
        summary.get("average_rr")
    )

    cards[0].metric(
        "Risk : Reward",
        f"1 : {average_rr:.2f}",
    )

    cards[1].metric(
        "Ratio ganador",
        f"{summary.get('win_rate', 0):.1f}%",
    )

    today = datetime.date.today()

    today_trades = 0

    if (
        not df.empty
        and "fecha_dt" in df.columns
    ):
        dates = pd.to_datetime(
            df["fecha_dt"],
            errors="coerce",
        ).dt.date

        today_trades = int(
            (dates == today).sum()
        )

    cards[2].metric(
        "Trades hoy",
        today_trades,
    )

    cards[3].metric(
        "Mejor trade",
        _format_money(
            summary.get("best_trade")
        ),
    )

    cards[4].metric(
        "Peor trade",
        _format_money(
            summary.get("worst_trade")
        ),
    )


def _render_asset_performance(
    df: pd.DataFrame,
) -> None:
    st.markdown(
        "### 🥇 Rendimiento por activo"
    )

    asset_df = pnl_by_asset(
        df
    )

    if asset_df.empty:
        st.info(
            "Aún no hay rendimiento por activo."
        )
        return

    asset_df = asset_df.head(
        6
    )

    for _, row in asset_df.iterrows():
        value = _safe_float(
            row.get("beneficio_usd")
        )

        value_color = (
            "#00ff88"
            if value >= 0
            else "#ff1744"
        )

        st.markdown(
            f"""
            <div
                class="ax-card"
                style="
                    padding:13px 15px;
                    margin-bottom:9px;
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                "
            >
                <strong>
                    {row.get("par", "Sin activo")}
                </strong>

                <span
                    style="
                        color:{value_color};
                        font-weight:950;
                    "
                >
                    {_format_money(value)}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_recent_trades(
    df: pd.DataFrame,
) -> None:
    st.markdown(
        "### 🧾 Últimas operaciones"
    )

    if df.empty:
        st.info(
            "Aún no existen operaciones."
        )
        return

    recent = df.sort_values(
        ["fecha_dt", "created_at_dt"],
        ascending=False,
    ).head(5)

    columns = [
        column
        for column in [
            "fecha",
            "par",
            "direccion",
            "precio_entrada",
            "stop_loss",
            "take_profit",
            "rr",
            "resultado",
            "beneficio_usd",
        ]
        if column in recent.columns
    ]

    st.dataframe(
        recent[columns],
        use_container_width=True,
        hide_index=True,
    )


def render_dashboard(
    df: pd.DataFrame,
    trader_name: str = "Trader Pro",
    initial_capital: float | None = None,
) -> None:
    """
    Renderiza el dashboard principal.

    El parámetro df debe ser el DataFrame preparado
    mediante core.metrics.prepare_df().
    """

    if initial_capital is None:
        initial_capital = float(
            st.session_state.get(
                "capital_actual",
                10000.0,
            )
        )

    _render_header(
        trader_name
    )

    filters = st.columns(
        [1, 1, 1, 2]
    )

    with filters[0]:
        st.selectbox(
            "Período",
            [
                "Todo",
                "Hoy",
                "Últimos 7 días",
                "Este mes",
            ],
            label_visibility="collapsed",
            key="dashboard_period",
        )

    with filters[1]:
        st.selectbox(
            "Activo",
            ["Todos"],
            label_visibility="collapsed",
            key="dashboard_asset",
        )

    with filters[2]:
        st.selectbox(
            "Vista",
            [
                "Performance Desk",
                "Risk Desk",
                "Psychology Desk",
            ],
            label_visibility="collapsed",
            key="dashboard_view",
        )

    with filters[3]:
        if st.button(
            "＋ REGISTRAR NUEVA OPERACIÓN",
            use_container_width=True,
            key="dashboard_new_trade",
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

    summary = calculate_summary(
        df,
        initial_capital,
    )

    score = calculate_prop_firm_score(
        summary
    )

    metric_columns = st.columns(
        6
    )

    with metric_columns[0]:
        _metric_card(
            "BALANCE ACTUAL",
            _format_money(
                summary["balance"]
            ),
            "Capital + PnL",
            "#ffffff",
            footer_right=f"{summary['total']} trades",
        )

    with metric_columns[1]:
        pnl_color = (
            "#00ff88"
            if summary["pnl"] >= 0
            else "#ff1744"
        )

        _metric_card(
            "P&L TOTAL",
            _format_money(
                summary["pnl"]
            ),
            "Período activo",
            pnl_color,
            footer_right=(
                f"{summary['pnl'] / initial_capital * 100:+.2f}%"
                if initial_capital > 0
                else "0.00%"
            ),
        )

    with metric_columns[2]:
        _metric_card(
            "WIN RATE",
            f"{summary['win_rate']:.2f}%",
            f"{summary['wins']}W / {summary['losses']}L",
            "#ffffff",
            footer_right="Aciertos",
        )

    with metric_columns[3]:
        _metric_card(
            "PROFIT FACTOR",
            f"{summary['profit_factor']:.2f}",
            "Objetivo ≥ 1.50",
            "#ffffff",
            footer_right="Sistema",
        )

    with metric_columns[4]:
        _metric_card(
            "DRAWDOWN MÁX.",
            f"{summary['drawdown_percent']:.2f}%",
            "Control de riesgo",
            "#ff1744",
            footer_right="Límite 5%",
        )

    with metric_columns[5]:
        _metric_card(
            "PROP FIRM SCORE",
            str(score),
            "de 100",
            "#25e5ff",
            footer_right="AXION",
        )

    chart_left, chart_right = st.columns(
        [1.65, 1]
    )

    with chart_left:
        equity_df = build_equity_curve(
            df,
            initial_capital,
        )

        _render_equity_chart(
            equity_df,
            initial_capital,
        )

    with chart_right:
        _render_setup_panel(
            df
        )

    _render_secondary_cards(
        summary,
        df,
    )

    lower_left, lower_right = st.columns(
        [1.45, 1]
    )

    with lower_left:
        _render_recent_trades(
            df
        )

    with lower_right:
        _render_asset_performance(
            df
        )
        # =========================================================
# PANTALLA COMPLETA DE AUTENTICACIÓN
# =========================================================

def render_auth() -> None:
    """
    Renderiza la pantalla completa de acceso,
    registro y recuperación de contraseña.
    """

    st.markdown(
        """
        <div style="height:10px;"></div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns(
        [1.28, 1],
        gap="large",
    )

    with left:
        render_login_presentation()

    with right:
        st.markdown(
            """
            <div
                class="ax-card"
                style="
                    padding:34px;
                    min-height:610px;
                "
            >
            """,
            unsafe_allow_html=True,
        )

        render_login_form()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )
# =========================================================
# PRESENTACIÓN DEL LOGIN
# =========================================================

def render_login_presentation() -> None:
    st.markdown(
        """
        <div class="ax-hero" style="
            min-height:610px;
            display:flex;
            flex-direction:column;
            justify-content:center;
            padding:45px;
        ">
            <div style="
                color:#25e5ff;
                font-size:11px;
                letter-spacing:2px;
                font-weight:900;
            ">
                AXION PRIME · TRADING INTELLIGENCE
            </div>

            <div style="
                font-size:58px;
                line-height:1.05;
                font-weight:950;
                margin-top:25px;
            ">
                Opera con más
                <br>
                <span style="
                    background:linear-gradient(
                        90deg,
                        #25e5ff,
                        #768cff,
                        #a146ff
                    );
                    -webkit-background-clip:text;
                    -webkit-text-fill-color:transparent;
                ">
                    claridad.
                </span>
            </div>

            <div style="
                color:#9aa7c8;
                font-size:16px;
                line-height:1.7;
                margin-top:25px;
            ">
                Convierte cada operación en inteligencia accionable.
                Analiza tu disciplina, riesgo, rendimiento y emociones
                desde un solo centro operativo.
            </div>

            <div style="
                display:grid;
                grid-template-columns:1fr 1fr;
                gap:12px;
                margin-top:32px;
            ">
                <div class="ax-card">📊 Track Record inteligente</div>
                <div class="ax-card">🧠 Auditoría visual con IA</div>
                <div class="ax-card">💭 Psicotrading medible</div>
                <div class="ax-card">📈 Métricas profesionales</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FORMULARIO DEL LOGIN
# =========================================================

def render_login_form() -> None:
    st.markdown(
        """
        <div style="
            font-size:38px;
            font-weight:950;
            color:#25e5ff;
            margin-bottom:8px;
        ">
            Bienvenido de vuelta 👋
        </div>

        <div style="
            color:#8d99ba;
            font-size:13px;
            margin-bottom:22px;
        ">
            Accede a tu centro de inteligencia de trading.
        </div>
        """,
        unsafe_allow_html=True,
    )

    login_tab, register_tab, reset_tab = st.tabs(
        [
            "Iniciar sesión",
            "Crear cuenta",
            "Recuperar",
        ]
    )

    with login_tab:
        email = st.text_input(
            "Correo electrónico",
            placeholder="trader@correo.com",
            key="login_email",
        )

        password = st.text_input(
            "Contraseña",
            type="password",
            key="login_password",
        )

        if st.button(
            "⚡ Entrar a AXION",
            use_container_width=True,
            key="login_button",
        ):
            if not email or not password:
                st.warning(
                    "Completa el correo y la contraseña."
                )
            else:
                try:
                    with st.spinner(
                        "Conectando con AXION..."
                    ):
                        payload = sign_in(
                            email,
                            password,
                        )

                    save_session(payload)
                    st.success(
                        "Sesión iniciada correctamente."
                    )
                    st.rerun()

                except Exception as exc:
                    st.error(
                        f"No se pudo iniciar sesión: {exc}"
                    )

    with register_tab:
        email = st.text_input(
            "Correo para crear la cuenta",
            key="register_email",
        )

        password = st.text_input(
            "Nueva contraseña",
            type="password",
            key="register_password",
        )

        if st.button(
            "Crear cuenta",
            use_container_width=True,
            key="register_button",
        ):
            if not email or len(password) < 6:
                st.warning(
                    "Introduce un correo y una contraseña "
                    "de al menos 6 caracteres."
                )
            else:
                try:
                    payload = sign_up(
                        email,
                        password,
                    )

                    if payload.get("access_token"):
                        save_session(payload)
                        st.rerun()
                    else:
                        st.success(
                            "Cuenta creada. Revisa tu correo "
                            "para confirmar el registro."
                        )

                except Exception as exc:
                    st.error(
                        f"No se pudo crear la cuenta: {exc}"
                    )

    with reset_tab:
        email = st.text_input(
            "Correo registrado",
            key="reset_email",
        )

        if st.button(
            "Enviar recuperación",
            use_container_width=True,
            key="reset_button",
        ):
            if not email:
                st.warning(
                    "Introduce tu correo."
                )
            else:
                try:
                    reset_password(
                        email,
                        APP_URL,
                    )

                    st.success(
                        "Enlace enviado. Revisa tu correo."
                    )

                except Exception as exc:
                    st.error(
                        f"No se pudo enviar el enlace: {exc}"
                    )
