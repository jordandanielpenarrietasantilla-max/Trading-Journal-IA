from __future__ import annotations

import datetime
import html
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# DASHBOARD INSTITUTIONAL COMMAND CENTER
# =========================================================


GREEN = "#00F58A"
RED = "#FF1744"
CYAN = "#20DDF5"
BLUE = "#367CFF"
PURPLE = "#8B4DFF"
WHITE = "#F6F8FF"
MUTED = "#8E9AB8"
PANEL = "#07101F"


# =========================================================
# UTILIDADES
# =========================================================


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    try:
        return float(
            value
            if value is not None
            else default
        )

    except (TypeError, ValueError):
        return default


def _money(
    value: Any,
) -> str:
    return f"${_safe_float(value):,.2f}"


def _safe_text(
    value: Any,
    default: str = "",
) -> str:
    text = str(
        value
        if value is not None
        else default
    ).strip()

    return html.escape(
        text
    )


def _normalize_result(
    value: Any,
    pnl: float,
) -> str:
    result = str(
        value or ""
    ).strip().upper()

    if result in {
        "WIN",
        "GANADOR",
        "GANADA",
        "PROFIT",
    }:
        return "WIN"

    if result in {
        "LOSS",
        "PERDEDOR",
        "PERDIDA",
        "PÉRDIDA",
        "LOSE",
    }:
        return "LOSS"

    if result in {
        "BE",
        "BREAK EVEN",
        "BREAKEVEN",
    }:
        return "BE"

    if pnl > 0:
        return "WIN"

    if pnl < 0:
        return "LOSS"

    return "BE"


def _prepare_df(
    df: pd.DataFrame,
) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    if "beneficio_usd" not in result.columns:
        result["beneficio_usd"] = 0.0

    result["beneficio_usd"] = pd.to_numeric(
        result["beneficio_usd"],
        errors="coerce",
    ).fillna(0.0)

    numeric_columns = [
        "precio_entrada",
        "stop_loss",
        "take_profit",
        "rr",
    ]

    for column in numeric_columns:
        if column not in result.columns:
            result[column] = 0.0

        result[column] = pd.to_numeric(
            result[column],
            errors="coerce",
        ).fillna(0.0)

    if "fecha" in result.columns:
        result["fecha_dt"] = pd.to_datetime(
            result["fecha"],
            errors="coerce",
        )
    else:
        result["fecha_dt"] = pd.NaT

    if "created_at" in result.columns:
        result["created_at_dt"] = pd.to_datetime(
            result["created_at"],
            errors="coerce",
        )
    else:
        result["created_at_dt"] = result["fecha_dt"]

    if "direccion" not in result.columns:
        result["direccion"] = ""

    if "resultado" not in result.columns:
        result["resultado"] = ""

    if "par" not in result.columns:
        result["par"] = "Sin activo"

    return result


def _filter_data(
    data: pd.DataFrame,
    period: str,
    asset: str,
) -> pd.DataFrame:
    if data.empty:
        return data

    filtered = data.copy()

    now = pd.Timestamp.now()

    if period == "Hoy":
        filtered = filtered[
            filtered["fecha_dt"].dt.date
            == now.date()
        ]

    elif period == "Últimos 7 días":
        start = now - pd.Timedelta(
            days=7
        )

        filtered = filtered[
            filtered["fecha_dt"] >= start
        ]

    elif period == "Este mes":
        filtered = filtered[
            (
                filtered["fecha_dt"].dt.year
                == now.year
            )
            &
            (
                filtered["fecha_dt"].dt.month
                == now.month
            )
        ]

    if asset != "Todos":
        filtered = filtered[
            filtered["par"].astype(str)
            == asset
        ]

    return filtered


def _direction_badge(
    value: Any,
) -> str:
    direction = str(
        value or ""
    ).strip().upper()

    if direction == "LONG":
        return (
            '<span class="ax-trade-badge '
            'ax-trade-long">LONG</span>'
        )

    if direction == "SHORT":
        return (
            '<span class="ax-trade-badge '
            'ax-trade-short">SHORT</span>'
        )

    return (
        '<span class="ax-trade-badge '
        'ax-trade-neutral">—</span>'
    )


def _result_badge(
    value: Any,
    pnl: float,
) -> str:
    result = _normalize_result(
        value,
        pnl,
    )

    css_class = {
        "WIN": "ax-result-win",
        "LOSS": "ax-result-loss",
        "BE": "ax-result-be",
    }[result]

    return (
        f'<span class="ax-result-badge '
        f'{css_class}">{result}</span>'
    )


# =========================================================
# SPARKLINES DE MÉTRICAS
# =========================================================


def _sparkline_svg(
    values: list[float],
    accent: str,
) -> str:
    if not values:
        values = [
            1,
            1,
            1,
            1,
            1,
        ]

    clean_values = [
        _safe_float(
            value
        )
        for value in values[-18:]
    ]

    minimum = min(
        clean_values
    )

    maximum = max(
        clean_values
    )

    span = (
        maximum - minimum
        if maximum != minimum
        else 1.0
    )

    width = 180
    height = 32

    points = []

    count = len(
        clean_values
    )

    for index, value in enumerate(
        clean_values
    ):
        x = (
            index
            / max(
                count - 1,
                1,
            )
            * width
        )

        normalized = (
            value - minimum
        ) / span

        y = (
            height
            - normalized * 24
            - 4
        )

        points.append(
            f"{x:.1f},{y:.1f}"
        )

    points_string = " ".join(
        points
    )

    return f"""
    <svg
        class="ax-sparkline"
        viewBox="0 0 {width} {height}"
        preserveAspectRatio="none"
        aria-hidden="true"
    >
        <polyline
            points="{points_string}"
            fill="none"
            stroke="{accent}"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
        />
    </svg>
    """


def _metric_card(
    *,
    icon: str,
    title: str,
    value: str,
    subtitle: str,
    footer: str,
    accent: str,
    spark_values: list[float],
) -> None:
    sparkline = _sparkline_svg(
        spark_values,
        accent,
    )

    st.html(
        f"""
        <article class="ax-command-metric">
            <div class="ax-command-metric-top">
                <div
                    class="ax-command-metric-icon"
                    style="
                        color:{accent};
                        border-color:{accent}55;
                        background:{accent}12;
                    "
                >
                    {icon}
                </div>

                <div class="ax-command-metric-copy">
                    <div class="ax-command-metric-label">
                        {_safe_text(title)}
                    </div>

                    <div
                        class="ax-command-metric-value"
                        style="color:{accent}"
                    >
                        {_safe_text(value)}
                    </div>
                </div>
            </div>

            <div class="ax-command-metric-meta">
                <span>
                    {_safe_text(subtitle)}
                </span>

                <span>
                    {_safe_text(footer)}
                </span>
            </div>

            {sparkline}
        </article>
        """
    )


# =========================================================
# ENCABEZADO
# =========================================================


def _render_header(
    trader_name: str,
) -> None:
    now = datetime.datetime.now()

    current_date = now.strftime(
        "%d %b %Y"
    ).upper()

    current_time = now.strftime(
        "%I:%M %p"
    )

    safe_name = _safe_text(
        trader_name,
        "Trader Pro",
    )

    st.html(
        f"""
        <section class="ax-command-header">
            <div class="ax-command-header-copy">
                <div class="ax-command-kicker">
                    AXION PRIME · PERFORMANCE COMMAND OS X10
                </div>

                <h1>
                    ¡Buenos días, {safe_name}! 👋
                </h1>

                <p>
                    Disciplina hoy, libertad mañana.
                    Tu desempeño vive en los datos.
                </p>
            </div>

            <div class="ax-command-header-actions">
                <div class="ax-command-date">
                    {current_date}
                    <span></span>
                    {current_time}
                </div>

                <div class="ax-market-status">
                    <span></span>
                    MERCADOS ACTIVOS
                </div>
            </div>
        </section>
        """
    )


# =========================================================
# CURVA DE EQUITY
# =========================================================


def _build_equity_data(
    data: pd.DataFrame,
    initial_capital: float,
) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    equity = data.dropna(
        subset=[
            "fecha_dt",
        ]
    ).copy()

    equity = equity.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ]
    )

    if equity.empty:
        return pd.DataFrame()

    equity["equity"] = (
        initial_capital
        + equity["beneficio_usd"].cumsum()
    )

    equity["peak"] = equity[
        "equity"
    ].cummax()

    equity["drawdown"] = (
        equity["equity"]
        - equity["peak"]
    )

    return equity


def _equity_chart(
    data: pd.DataFrame,
    initial_capital: float,
) -> None:
    st.html(
        """
        <div class="ax-command-panel-title">
            <div>
                <span class="ax-command-panel-icon">◈</span>
                <strong>CURVA DE EQUITY</strong>
            </div>

            <span>BALANCE ACUMULADO</span>
        </div>
        """
    )

    equity = _build_equity_data(
        data,
        initial_capital,
    )

    if equity.empty:
        st.html(
            """
            <div class="ax-command-empty">
                <div>◇</div>

                <strong>
                    Tu curva comienza con tu primer trade
                </strong>

                <p>
                    Registra una operación para activar
                    rendimiento, consistencia y drawdown.
                </p>
            </div>
            """
        )
        return

    maximum_equity = float(
        equity["equity"].max()
    )

    last_equity = float(
        equity["equity"].iloc[-1]
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=equity["fecha_dt"],
            y=equity["equity"],
            mode="lines",
            name="Equity",
            line={
                "color": CYAN,
                "width": 3,
                "shape": "spline",
                "smoothing": 0.65,
            },
            fill="tozeroy",
            fillcolor="rgba(32, 221, 245, 0.08)",
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b>"
                "<br>Balance: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure.add_hline(
        y=maximum_equity,
        line_width=1,
        line_dash="dot",
        line_color=GREEN,
        annotation_text=(
            f"Máximo histórico "
            f"${maximum_equity:,.0f}"
        ),
        annotation_position="top right",
        annotation_font={
            "color": GREEN,
            "size": 11,
        },
    )

    figure.add_trace(
        go.Scatter(
            x=[
                equity["fecha_dt"].iloc[-1]
            ],
            y=[
                last_equity
            ],
            mode="markers+text",
            marker={
                "size": 11,
                "color": BLUE,
                "line": {
                    "color": WHITE,
                    "width": 2,
                },
            },
            text=[
                f"${last_equity:,.0f}"
            ],
            textposition="middle left",
            textfont={
                "color": WHITE,
                "size": 11,
            },
            showlegend=False,
            hoverinfo="skip",
        )
    )

    figure.update_layout(
        height=405,
        margin={
            "l": 12,
            "r": 12,
            "t": 30,
            "b": 10,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        showlegend=False,
        font={
            "color": MUTED,
            "family": "Inter",
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(77,101,162,0.12)",
            "zeroline": False,
            "showline": False,
            "tickfont": {
                "color": MUTED,
                "size": 10,
            },
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(77,101,162,0.14)",
            "zeroline": False,
            "showline": False,
            "tickprefix": "$",
            "tickformat": ",.0f",
            "tickfont": {
                "color": MUTED,
                "size": 10,
            },
        },
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={
            "displayModeBar": False,
            "responsive": True,
        },
    )


# =========================================================
# ÚLTIMAS OPERACIONES
# =========================================================


def _recent_trades_html(
    data: pd.DataFrame,
) -> str:
    if data.empty:
        return """
        <div class="ax-command-empty ax-command-table-empty">
            <div>▤</div>

            <strong>
                Aún no existen operaciones
            </strong>

            <p>
                Tus últimos trades aparecerán aquí.
            </p>
        </div>
        """

    recent = data.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ],
        ascending=False,
    ).head(7)

    rows: list[str] = []

    for _, trade in recent.iterrows():
        pnl = _safe_float(
            trade.get(
                "beneficio_usd"
            )
        )

        pnl_color = (
            GREEN
            if pnl > 0
            else RED
            if pnl < 0
            else MUTED
        )

        date_value = trade.get(
            "fecha_dt"
        )

        if pd.notna(
            date_value
        ):
            date_text = pd.Timestamp(
                date_value
            ).strftime(
                "%d/%m/%Y"
            )
        else:
            date_text = _safe_text(
                trade.get(
                    "fecha",
                    "—",
                )
            )

        rows.append(
            f"""
            <tr>
                <td>
                    {date_text}
                </td>

                <td class="ax-trade-asset">
                    {_safe_text(
                        trade.get(
                            "par",
                            "—",
                        )
                    )}
                </td>

                <td>
                    {_direction_badge(
                        trade.get(
                            "direccion"
                        )
                    )}
                </td>

                <td>
                    {_safe_float(
                        trade.get(
                            "precio_entrada"
                        )
                    ):,.5f}
                </td>

                <td>
                    {_safe_float(
                        trade.get(
                            "stop_loss"
                        )
                    ):,.5f}
                </td>

                <td>
                    {_safe_float(
                        trade.get(
                            "take_profit"
                        )
                    ):,.5f}
                </td>

                <td>
                    {_result_badge(
                        trade.get(
                            "resultado"
                        ),
                        pnl,
                    )}
                </td>

                <td
                    class="ax-trade-pnl"
                    style="color:{pnl_color}"
                >
                    {_money(pnl)}
                </td>
            </tr>
            """
        )

    return f"""
    <div class="ax-command-trades-scroll">
        <table class="ax-command-trades-table">
            <thead>
                <tr>
                    <th>FECHA</th>
                    <th>PAR</th>
                    <th>DIR.</th>
                    <th>ENTRADA</th>
                    <th>SL</th>
                    <th>TP</th>
                    <th>RESULTADO</th>
                    <th>P&amp;L</th>
                </tr>
            </thead>

            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
    </div>
    """


def _recent_trades(
    data: pd.DataFrame,
) -> None:
    st.html(
        """
        <div class="ax-command-panel-title">
            <div>
                <span class="ax-command-panel-icon">▣</span>
                <strong>ÚLTIMAS OPERACIONES</strong>
            </div>

            <span>HISTORIAL RECIENTE</span>
        </div>
        """
    )

    st.html(
        _recent_trades_html(
            data
        )
    )


# =========================================================
# CAPTURA DEL SETUP
# =========================================================


def _setup_panel(
    data: pd.DataFrame,
) -> None:
    st.html(
        """
        <div class="ax-command-panel-title">
            <div>
                <span class="ax-command-panel-icon">▧</span>
                <strong>CAPTURA DEL SETUP</strong>
            </div>

            <span>AI VISION READY</span>
        </div>
        """
    )

    if data.empty:
        st.html(
            """
            <div class="ax-command-empty ax-command-setup-empty">
                <div>🧠</div>

                <strong>
                    AXION Vision está listo
                </strong>

                <p>
                    Registra un setup para activar
                    la auditoría visual.
                </p>
            </div>
            """
        )
        return

    ordered = data.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ],
        ascending=False,
    )

    last_trade = ordered.iloc[0]

    image_value = str(
        last_trade.get(
            "img_before"
        )
        or last_trade.get(
            "img_after"
        )
        or ""
    ).strip()

    if image_value:
        st.image(
            image_value,
            use_container_width=True,
        )
    else:
        st.html(
            """
            <div class="ax-command-image-placeholder">
                <div>📷</div>

                <strong>
                    Sin captura disponible
                </strong>

                <span>
                    El último trade no tiene imagen guardada.
                </span>
            </div>
            """
        )


# =========================================================
# RESUMEN RÁPIDO
# =========================================================


def _maximum_streak(
    values: list[float],
) -> int:
    maximum = 0
    current = 0

    for value in values:
        if value > 0:
            current += 1
            maximum = max(
                maximum,
                current,
            )
        else:
            current = 0

    return maximum


def _current_streak(
    values: list[float],
) -> int:
    current = 0

    for value in reversed(
        values
    ):
        if value > 0:
            current += 1
        else:
            break

    return current


def _maximum_drawdown(
    data: pd.DataFrame,
    initial_capital: float,
) -> float:
    equity = _build_equity_data(
        data,
        initial_capital,
    )

    if equity.empty:
        return 0.0

    percentage = (
        equity["drawdown"]
        / equity["peak"].replace(
            0,
            pd.NA,
        )
        * 100
    )

    return abs(
        float(
            percentage.min()
        )
    )


def _quick_summary(
    data: pd.DataFrame,
    initial_capital: float,
) -> None:
    st.html(
        """
        <div class="ax-command-panel-title">
            <div>
                <span class="ax-command-panel-icon">⚡</span>
                <strong>RESUMEN RÁPIDO</strong>
            </div>

            <span>PERFORMANCE</span>
        </div>
        """
    )

    if data.empty:
        best_day = 0.0
        worst_day = 0.0
        current_streak = 0
        maximum_streak = 0
        drawdown = 0.0

    else:
        daily = (
            data.dropna(
                subset=[
                    "fecha_dt",
                ]
            )
            .groupby(
                data["fecha_dt"].dt.date
            )["beneficio_usd"]
            .sum()
        )

        best_day = (
            float(
                daily.max()
            )
            if not daily.empty
            else 0.0
        )

        worst_day = (
            float(
                daily.min()
            )
            if not daily.empty
            else 0.0
        )

        ordered = data.sort_values(
            [
                "fecha_dt",
                "created_at_dt",
            ]
        )

        pnl_values = ordered[
            "beneficio_usd"
        ].tolist()

        current_streak = _current_streak(
            pnl_values
        )

        maximum_streak = _maximum_streak(
            pnl_values
        )

        drawdown = _maximum_drawdown(
            data,
            initial_capital,
        )

    rows = [
        (
            "Mejor día",
            _money(best_day),
            GREEN,
        ),
        (
            "Peor día",
            _money(worst_day),
            RED if worst_day < 0 else MUTED,
        ),
        (
            "Racha actual",
            f"{current_streak} Wins",
            GREEN,
        ),
        (
            "Racha máxima",
            f"{maximum_streak} Wins",
            GREEN,
        ),
        (
            "Drawdown máximo",
            f"{drawdown:.2f}%",
            GREEN if drawdown < 5 else RED,
        ),
    ]

    row_html = "".join(
        f"""
        <div class="ax-summary-row">
            <span>{label}</span>

            <strong style="color:{color}">
                {value}
            </strong>
        </div>
        """
        for label, value, color in rows
    )

    st.html(
        f"""
        <div class="ax-summary-card">
            {row_html}
        </div>
        """
    )


# =========================================================
# PANEL PROMOCIONAL
# =========================================================


def _render_intelligence_banner(
    total: int,
) -> None:
    st.html(
        f"""
        <section class="ax-intelligence-banner">
            <div class="ax-intelligence-copy">
                <div class="ax-command-kicker">
                    AXION PRIME · TRADING INTELLIGENCE
                </div>

                <h2>
                    Opera con más
                    <span>claridad.</span>
                </h2>

                <p>
                    Convierte cada operación en inteligencia
                    accionable. Analiza rendimiento, disciplina,
                    riesgo y emociones desde un solo centro.
                </p>

                <div class="ax-intelligence-features">
                    <div>
                        <b>▣</b>
                        Track Record inteligente
                    </div>

                    <div>
                        <b>◉</b>
                        Auditoría visual con IA
                    </div>

                    <div>
                        <b>☁</b>
                        Psicotrading medible
                    </div>

                    <div>
                        <b>⌁</b>
                        Métricas profesionales
                    </div>
                </div>
            </div>

            <div class="ax-intelligence-visual">
                <div class="ax-market-animal ax-bull">
                    BULL
                </div>

                <div class="ax-market-logo">
                    A
                </div>

                <div class="ax-market-animal ax-bear">
                    BEAR
                </div>
            </div>

            <div class="ax-intelligence-stats">
                <div>
                    <strong>+{total:,}</strong>
                    <span>Trades registrados</span>
                </div>

                <div>
                    <strong>100%</strong>
                    <span>Privacidad</span>
                </div>

                <div>
                    <strong>24/7</strong>
                    <span>IA disponible</span>
                </div>
            </div>
        </section>
        """
    )


# =========================================================
# DASHBOARD PRINCIPAL
# =========================================================


def render_dashboard(
    df: pd.DataFrame,
    trader_name: str = "Trader Pro",
    initial_capital: float | None = None,
) -> None:
    if initial_capital is None:
        initial_capital = _safe_float(
            st.session_state.get(
                "capital_actual",
                10000.0,
            ),
            10000.0,
        )

    data = _prepare_df(
        df
    )

    _render_header(
        trader_name
    )

    assets = [
        "Todos"
    ]

    if not data.empty:
        assets.extend(
            sorted(
                {
                    str(value)
                    for value in data[
                        "par"
                    ].dropna().tolist()
                    if str(value).strip()
                }
            )
        )

    filter_columns = st.columns(
        [
            1,
            1,
            1,
            1.2,
        ],
        gap="medium",
    )

    with filter_columns[0]:
        period = st.selectbox(
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

    with filter_columns[1]:
        asset = st.selectbox(
            "Activo",
            assets,
            label_visibility="collapsed",
            key="dashboard_asset",
        )

    with filter_columns[2]:
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

    with filter_columns[3]:
        if st.button(
            "＋ REGISTRAR NUEVA OPERACIÓN",
            key="dashboard_new_trade",
            use_container_width=True,
            type="primary",
        ):
            st.session_state.page = (
                "Registrar Trade"
            )

            st.rerun()

    filtered_data = _filter_data(
        data,
        period,
        asset,
    )

    total = len(
        filtered_data
    )

    pnl = (
        float(
            filtered_data[
                "beneficio_usd"
            ].sum()
        )
        if not filtered_data.empty
        else 0.0
    )

    balance = (
        initial_capital
        + pnl
    )

    wins = (
        int(
            (
                filtered_data[
                    "beneficio_usd"
                ] > 0
            ).sum()
        )
        if not filtered_data.empty
        else 0
    )

    losses = (
        int(
            (
                filtered_data[
                    "beneficio_usd"
                ] < 0
            ).sum()
        )
        if not filtered_data.empty
        else 0
    )

    win_rate = (
        wins
        / total
        * 100
        if total > 0
        else 0.0
    )

    gross_profit = (
        float(
            filtered_data.loc[
                filtered_data[
                    "beneficio_usd"
                ] > 0,
                "beneficio_usd",
            ].sum()
        )
        if not filtered_data.empty
        else 0.0
    )

    gross_loss = (
        abs(
            float(
                filtered_data.loc[
                    filtered_data[
                        "beneficio_usd"
                    ] < 0,
                    "beneficio_usd",
                ].sum()
            )
        )
        if not filtered_data.empty
        else 0.0
    )

    if gross_loss > 0:
        profit_factor = (
            gross_profit
            / gross_loss
        )
    elif gross_profit > 0:
        profit_factor = 99.0
    else:
        profit_factor = 0.0

    score = min(
        100,
        max(
            0,
            round(
                50
                + win_rate * 0.25
                + min(
                    profit_factor,
                    3,
                ) * 8
            ),
        ),
    )

    ordered_pnl = (
        filtered_data.sort_values(
            [
                "fecha_dt",
                "created_at_dt",
            ]
        )["beneficio_usd"].tolist()
        if not filtered_data.empty
        else []
    )

    cumulative_pnl = (
        pd.Series(
            ordered_pnl
        ).cumsum().tolist()
        if ordered_pnl
        else [
            0.0
        ]
    )

    balance_spark = [
        initial_capital
        + value
        for value in cumulative_pnl
    ]

    win_spark = []

    running_wins = 0

    for index, value in enumerate(
        ordered_pnl,
        start=1,
    ):
        if value > 0:
            running_wins += 1

        win_spark.append(
            running_wins
            / index
            * 100
        )

    metric_columns = st.columns(
        5,
        gap="medium",
    )

    with metric_columns[0]:
        _metric_card(
            icon="▣",
            title="BALANCE ACTUAL",
            value=_money(balance),
            subtitle="Capital + PnL",
            footer=f"{total} trades",
            accent=WHITE,
            spark_values=balance_spark,
        )

    with metric_columns[1]:
        pnl_color = (
            GREEN
            if pnl >= 0
            else RED
        )

        _metric_card(
            icon="↗",
            title="P&L TOTAL",
            value=_money(pnl),
            subtitle="Resultado acumulado",
            footer="Performance",
            accent=pnl_color,
            spark_values=cumulative_pnl,
        )

    with metric_columns[2]:
        _metric_card(
            icon="◎",
            title="WIN RATE",
            value=f"{win_rate:.1f}%",
            subtitle=f"{wins}W / {losses}L",
            footer="Aciertos",
            accent=CYAN,
            spark_values=win_spark,
        )

    with metric_columns[3]:
        displayed_pf = (
            "∞"
            if profit_factor >= 99
            else f"{profit_factor:.2f}"
        )

        _metric_card(
            icon="Σ",
            title="PROFIT FACTOR",
            value=displayed_pf,
            subtitle="Objetivo > 1.50",
            footer="Sistema",
            accent=PURPLE,
            spark_values=cumulative_pnl,
        )

    with metric_columns[4]:
        _metric_card(
            icon="♢",
            title="PROP FIRM SCORE",
            value=str(score),
            subtitle="de 100",
            footer="AXION",
            accent=GREEN,
            spark_values=[
                50,
                54,
                57,
                61,
                score,
            ],
        )

    main_left, main_center, main_right = st.columns(
        [
            1.35,
            1.15,
            0.72,
        ],
        gap="medium",
    )

    with main_left:
        _equity_chart(
            filtered_data,
            initial_capital,
        )

    with main_center:
        _recent_trades(
            filtered_data
        )

    with main_right:
        _setup_panel(
            filtered_data
        )

        _quick_summary(
            filtered_data,
            initial_capital,
        )

    _render_intelligence_banner(
        total
    )
