from __future__ import annotations

import datetime
import html
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# DASHBOARD FUTURISTIC COMMAND CENTER
# =========================================================


GREEN = "#00F58A"
RED = "#FF1744"
CYAN = "#20DDF5"
BLUE = "#367CFF"
PURPLE = "#8B4DFF"
WHITE = "#F6F8FF"
MUTED = "#8E9AB8"


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
    clean_value = str(
        value
        if value is not None
        else default
    ).strip()

    return html.escape(
        clean_value
    )


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

    for column in (
        "precio_entrada",
        "stop_loss",
        "take_profit",
        "rr",
    ):
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

    if "par" not in result.columns:
        result["par"] = "Sin activo"

    if "direccion" not in result.columns:
        result["direccion"] = ""

    if "resultado" not in result.columns:
        result["resultado"] = ""

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
        filtered = filtered[
            filtered["fecha_dt"]
            >= now - pd.Timedelta(days=7)
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


# =========================================================
# CABECERA
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

    st.html(
        f"""
        <section class="ax-future-header">

            <div class="ax-future-header-copy">

                <div class="ax-future-kicker">
                    AXION PRIME · PERFORMANCE COMMAND OS X10
                </div>

                <h1>
                    ¡Buenos días, {_safe_text(trader_name)}! 👋
                </h1>

                <p>
                    Disciplina hoy, libertad mañana.
                    Tu desempeño vive en los datos.
                </p>

            </div>

            <div class="ax-future-header-status">

                <div class="ax-future-date">
                    {current_date}
                    <span></span>
                    {current_time}
                </div>

                <div class="ax-future-market-status">
                    <i></i>
                    MERCADOS ACTIVOS
                </div>

            </div>

        </section>
        """
    )


# =========================================================
# MINI GRÁFICOS
# =========================================================


def _sparkline_svg(
    values: list[float],
    accent: str,
) -> str:
    clean_values = [
        _safe_float(value)
        for value in values[-20:]
    ]

    if len(clean_values) < 2:
        clean_values = [
            0.0,
            0.0,
            0.0,
            0.0,
        ]

    minimum = min(
        clean_values
    )

    maximum = max(
        clean_values
    )

    difference = (
        maximum - minimum
        if maximum != minimum
        else 1.0
    )

    width = 210
    height = 40

    points: list[str] = []

    for index, value in enumerate(
        clean_values
    ):
        x = (
            index
            / max(
                len(clean_values) - 1,
                1,
            )
            * width
        )

        normalized = (
            value - minimum
        ) / difference

        y = (
            height
            - normalized * 29
            - 5
        )

        points.append(
            f"{x:.1f},{y:.1f}"
        )

    return f"""
    <svg
        class="ax-future-sparkline"
        viewBox="0 0 {width} {height}"
        preserveAspectRatio="none"
    >
        <defs>
            <linearGradient
                id="spark-{accent.replace('#', '')}"
                x1="0"
                y1="0"
                x2="1"
                y2="0"
            >
                <stop
                    offset="0%"
                    stop-color="{accent}"
                    stop-opacity="0.25"
                />

                <stop
                    offset="100%"
                    stop-color="{accent}"
                    stop-opacity="1"
                />
            </linearGradient>
        </defs>

        <polyline
            points="{' '.join(points)}"
            fill="none"
            stroke="url(#spark-{accent.replace('#', '')})"
            stroke-width="2.4"
            stroke-linecap="round"
            stroke-linejoin="round"
        />
    </svg>
    """


def _metric_card(
    *,
    icon: str,
    label: str,
    value: str,
    subtitle: str,
    footer: str,
    accent: str,
    spark_values: list[float],
) -> None:
    st.html(
        f"""
        <article class="ax-future-metric">

            <div class="ax-future-metric-head">

                <div
                    class="ax-future-metric-icon"
                    style="
                        color:{accent};
                        background:{accent}12;
                        border-color:{accent}55;
                        box-shadow:0 0 25px {accent}18;
                    "
                >
                    {icon}
                </div>

                <div>
                    <div class="ax-future-metric-label">
                        {_safe_text(label)}
                    </div>

                    <div
                        class="ax-future-metric-value"
                        style="color:{accent}"
                    >
                        {_safe_text(value)}
                    </div>
                </div>

            </div>

            <div class="ax-future-metric-meta">
                <span>
                    {_safe_text(subtitle)}
                </span>

                <span>
                    {_safe_text(footer)}
                </span>
            </div>

            {_sparkline_svg(
                spark_values,
                accent,
            )}

        </article>
        """
    )


# =========================================================
# EQUITY
# =========================================================


def _build_equity(
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


def _panel_title(
    icon: str,
    title: str,
    subtitle: str,
) -> None:
    st.html(
        f"""
        <div class="ax-future-panel-title">

            <div>
                <span>{icon}</span>
                <strong>
                    {_safe_text(title)}
                </strong>
            </div>

            <small>
                {_safe_text(subtitle)}
            </small>

        </div>
        """
    )


def _equity_chart(
    data: pd.DataFrame,
    initial_capital: float,
) -> None:
    _panel_title(
        "◈",
        "CURVA DE EQUITY",
        "BALANCE ACUMULADO",
    )

    equity = _build_equity(
        data,
        initial_capital,
    )

    if equity.empty:
        st.html(
            """
            <div class="ax-future-empty">
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

    last_equity = float(
        equity["equity"].iloc[-1]
    )

    maximum_equity = float(
        equity["equity"].max()
    )

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=equity["fecha_dt"],
            y=equity["equity"],
            mode="lines",
            line={
                "color": CYAN,
                "width": 3,
                "shape": "spline",
                "smoothing": 0.75,
            },
            fill="tozeroy",
            fillcolor="rgba(32,221,245,0.08)",
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b>"
                "<br>Balance: $%{y:,.2f}"
                "<extra></extra>"
            ),
            showlegend=False,
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
            "size": 10,
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
            mode="markers",
            marker={
                "size": 11,
                "color": BLUE,
                "line": {
                    "color": WHITE,
                    "width": 2,
                },
            },
            hovertemplate=(
                f"Balance actual: "
                f"${last_equity:,.2f}"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    figure.update_layout(
        height=430,
        margin={
            "l": 8,
            "r": 8,
            "t": 26,
            "b": 8,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        font={
            "color": MUTED,
            "family": "Inter",
        },
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(82,111,175,0.11)",
            "zeroline": False,
            "tickfont": {
                "color": MUTED,
                "size": 9,
            },
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(82,111,175,0.13)",
            "zeroline": False,
            "tickprefix": "$",
            "tickformat": ",.0f",
            "tickfont": {
                "color": MUTED,
                "size": 9,
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
# OPERACIONES RECIENTES
# =========================================================


def _direction_badge(
    direction: Any,
) -> str:
    clean_direction = str(
        direction or ""
    ).strip().upper()

    if clean_direction == "LONG":
        return (
            '<span class="ax-future-badge '
            'ax-future-long">LONG</span>'
        )

    if clean_direction == "SHORT":
        return (
            '<span class="ax-future-badge '
            'ax-future-short">SHORT</span>'
        )

    return (
        '<span class="ax-future-badge '
        'ax-future-neutral">—</span>'
    )


def _result_badge(
    result: Any,
    pnl: float,
) -> str:
    normalized = _normalize_result(
        result,
        pnl,
    )

    class_name = {
        "WIN": "ax-future-win",
        "LOSS": "ax-future-loss",
        "BE": "ax-future-be",
    }[normalized]

    return (
        f'<span class="ax-future-result '
        f'{class_name}">{normalized}</span>'
    )


def _recent_trades(
    data: pd.DataFrame,
) -> None:
    _panel_title(
        "▣",
        "ÚLTIMAS OPERACIONES",
        "HISTORIAL RECIENTE",
    )

    if data.empty:
        st.html(
            """
            <div class="ax-future-empty">
                <div>▤</div>

                <strong>
                    Todavía no existen operaciones
                </strong>

                <p>
                    Tus operaciones aparecerán aquí.
                </p>
            </div>
            """
        )
        return

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

        pnl_color = (
            GREEN
            if pnl > 0
            else RED
            if pnl < 0
            else MUTED
        )

        rows.append(
            f"""
            <tr>
                <td>
                    {date_text}
                </td>

                <td>
                    <strong>
                        {_safe_text(
                            trade.get(
                                "par",
                                "—",
                            )
                        )}
                    </strong>
                </td>

                <td>
                    {_direction_badge(
                        trade.get(
                            "direccion"
                        )
                    )}
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
                    class="ax-future-pnl"
                    style="color:{pnl_color}"
                >
                    {_money(pnl)}
                </td>
            </tr>
            """
        )

    st.html(
        f"""
        <div class="ax-future-table-shell">

            <table class="ax-future-table">

                <thead>
                    <tr>
                        <th>FECHA</th>
                        <th>ACTIVO</th>
                        <th>DIRECCIÓN</th>
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
    )


# =========================================================
# SETUP
# =========================================================


def _setup_panel(
    data: pd.DataFrame,
) -> None:
    _panel_title(
        "▧",
        "CAPTURA DEL SETUP",
        "AI VISION READY",
    )

    if data.empty:
        st.html(
            """
            <div class="ax-future-empty ax-future-setup-empty">
                <div>🧠</div>

                <strong>
                    AXION Vision está listo
                </strong>

                <p>
                    Registra un setup para activar
                    el análisis visual.
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
            <div class="ax-future-empty ax-future-setup-empty">
                <div>📷</div>

                <strong>
                    Sin captura disponible
                </strong>

                <p>
                    El último trade no tiene imagen guardada.
                </p>
            </div>
            """
        )


# =========================================================
# RESUMEN RÁPIDO
# =========================================================


def _current_streak(
    values: list[float],
) -> int:
    streak = 0

    for value in reversed(
        values
    ):
        if value > 0:
            streak += 1
        else:
            break

    return streak


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


def _maximum_drawdown(
    data: pd.DataFrame,
    initial_capital: float,
) -> float:
    equity = _build_equity(
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
        _safe_float(
            percentage.min()
        )
    )


def _quick_summary(
    data: pd.DataFrame,
    initial_capital: float,
) -> None:
    _panel_title(
        "⚡",
        "RESUMEN RÁPIDO",
        "PERFORMANCE",
    )

    if data.empty:
        best_day = 0.0
        worst_day = 0.0
        current_streak = 0
        maximum_streak = 0
        drawdown = 0.0

    else:
        valid_dates = data.dropna(
            subset=[
                "fecha_dt",
            ]
        ).copy()

        if valid_dates.empty:
            daily = pd.Series(
                dtype=float
            )
        else:
            daily = (
                valid_dates.groupby(
                    valid_dates[
                        "fecha_dt"
                    ].dt.date
                )["beneficio_usd"]
                .sum()
            )

        best_day = (
            _safe_float(
                daily.max()
            )
            if not daily.empty
            else 0.0
        )

        worst_day = (
            _safe_float(
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

    summary_items = [
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

    rows = "".join(
        f"""
        <div class="ax-future-summary-row">
            <span>
                {label}
            </span>

            <strong style="color:{color}">
                {value}
            </strong>
        </div>
        """
        for label, value, color
        in summary_items
    )

    st.html(
        f"""
        <div class="ax-future-summary">
            {rows}
        </div>
        """
    )


# =========================================================
# BANNER FUTURISTA
# =========================================================


def _intelligence_banner(
    total: int,
    pnl: float,
    win_rate: float,
) -> None:
    pnl_color = (
        GREEN
        if pnl >= 0
        else RED
    )

    st.html(
        f"""
        <section class="ax-future-intelligence">

            <div class="ax-future-intelligence-copy">

                <div class="ax-future-kicker">
                    AXION INTELLIGENCE
                </div>

                <h2>
                    Convierte disciplina
                    <span>en ventaja.</span>
                </h2>

                <p>
                    Registra, analiza y perfecciona
                    cada ejecución desde un solo centro
                    de inteligencia operativa.
                </p>

                <div class="ax-future-feature-grid">

                    <div>
                        <i>▣</i>
                        Track Record inteligente
                    </div>

                    <div>
                        <i>◉</i>
                        Auditoría visual con IA
                    </div>

                    <div>
                        <i>☁</i>
                        Psicotrading medible
                    </div>

                    <div>
                        <i>⌁</i>
                        Riesgo y métricas avanzadas
                    </div>

                </div>

            </div>

            <div class="ax-future-market-visual">

                <div class="ax-future-bull">
                    BULL
                </div>

                <div class="ax-future-center-logo">
                    A
                </div>

                <div class="ax-future-bear">
                    BEAR
                </div>

                <div class="ax-future-market-line"></div>

            </div>

            <div class="ax-future-global-stats">

                <div>
                    <strong>
                        +{total:,}
                    </strong>

                    <span>
                        Trades analizados
                    </span>
                </div>

                <div>
                    <strong style="color:{pnl_color}">
                        {_money(pnl)}
                    </strong>

                    <span>
                        Resultado acumulado
                    </span>
                </div>

                <div>
                    <strong>
                        {win_rate:.1f}%
                    </strong>

                    <span>
                        Precisión
                    </span>
                </div>

                <div>
                    <strong>
                        24/7
                    </strong>

                    <span>
                        IA activa
                    </span>
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
            1.35,
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
        _safe_float(
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
        _safe_float(
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
            _safe_float(
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
        profit_factor = float(
            "inf"
        )

    else:
        profit_factor = 0.0

    finite_profit_factor = (
        min(
            profit_factor,
            3.0,
        )
        if profit_factor != float("inf")
        else 3.0
    )

    score = min(
        100,
        max(
            0,
            round(
                50
                + win_rate * 0.25
                + finite_profit_factor * 8
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
            0.0,
            0.0,
        ]
    )

    balance_spark = [
        initial_capital + value
        for value in cumulative_pnl
    ]

    running_wins = 0
    win_spark: list[float] = []

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
            label="BALANCE ACTUAL",
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
            label="P&L TOTAL",
            value=_money(pnl),
            subtitle="Resultado acumulado",
            footer="Performance",
            accent=pnl_color,
            spark_values=cumulative_pnl,
        )

    with metric_columns[2]:
        _metric_card(
            icon="◎",
            label="WIN RATE",
            value=f"{win_rate:.1f}%",
            subtitle=f"{wins}W / {losses}L",
            footer="Aciertos",
            accent=CYAN,
            spark_values=win_spark,
        )

    with metric_columns[3]:
        profit_factor_text = (
            "∞"
            if profit_factor == float("inf")
            else f"{profit_factor:.2f}"
        )

        _metric_card(
            icon="Σ",
            label="PROFIT FACTOR",
            value=profit_factor_text,
            subtitle="Objetivo > 1.50",
            footer="Sistema",
            accent=PURPLE,
            spark_values=cumulative_pnl,
        )

    with metric_columns[4]:
        _metric_card(
            icon="♢",
            label="PROP FIRM SCORE",
            value=str(score),
            subtitle="de 100",
            footer="AXION",
            accent=GREEN,
            spark_values=[
                50,
                55,
                61,
                67,
                score,
            ],
        )

    main_left, main_center = st.columns(
        [
            1.08,
            1,
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

    right_left, right_right = st.columns(
        [
            1.25,
            0.75,
        ],
        gap="medium",
    )

    with right_left:
        _setup_panel(
            filtered_data
        )

    with right_right:
        _quick_summary(
            filtered_data,
            initial_capital,
        )

    _intelligence_banner(
        total,
        pnl,
        win_rate,
    )
