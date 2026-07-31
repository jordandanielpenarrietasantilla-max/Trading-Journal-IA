from __future__ import annotations

import datetime
from typing import Any

import pandas as pd
import streamlit as st


# =========================================================
# AXION PRIME X10
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


def _money(
    value: Any,
) -> str:
    return f"${_safe_float(value):,.2f}"


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

    return result


def _metric_card(
    title: str,
    value: str,
    subtitle: str,
    accent: str,
    footer: str = "",
) -> None:
    st.html(
        f"""
        <div class="ax-metric-card">
            <div class="ax-metric-label">
                {title}
            </div>

            <div
                class="ax-metric-value"
                style="color:{accent}"
            >
                {value}
            </div>

            <div class="ax-metric-bottom">
                <span>{subtitle}</span>
                <span>{footer}</span>
            </div>

            <div
                class="ax-metric-line"
                style="
                    background:linear-gradient(
                        90deg,
                        {accent},
                        #9146ff
                    )
                "
            ></div>
        </div>
        """
    )


def _render_header(
    trader_name: str,
) -> None:
    current_date = datetime.datetime.now().strftime(
        "%d %b %Y"
    ).upper()

    st.html(
        f"""
        <section class="ax-dashboard-hero">
            <div>
                <div class="ax-dashboard-eyebrow">
                    AXION PRIME · PERFORMANCE COMMAND OS
                </div>

                <h1>
                    ¡Buenos días, {trader_name}! 👋
                </h1>

                <p>
                    Disciplina hoy, libertad mañana.
                    Tu desempeño vive en los datos.
                </p>
            </div>

            <div class="ax-dashboard-status-area">
                <div class="ax-dashboard-date">
                    {current_date}
                </div>

                <div class="ax-market-status">
                    <span></span>
                    MERCADOS ACTIVOS
                </div>
            </div>
        </section>
        """
    )


def _equity_chart(
    data: pd.DataFrame,
    initial_capital: float,
) -> None:
    st.html(
        """
        <div class="ax-panel-title">
            <strong>📈 CURVA DE EQUITY</strong>
            <span>BALANCE ACUMULADO</span>
        </div>
        """
    )

    if data.empty:
        st.html(
            """
            <div class="ax-empty-panel">
                <div class="ax-empty-icon">◇</div>

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

    chart_data = data.copy()

    chart_data = chart_data.dropna(
        subset=["fecha_dt"]
    )

    chart_data = chart_data.sort_values(
        "fecha_dt"
    )

    if chart_data.empty:
        st.info(
            "No existen fechas válidas para construir la curva."
        )
        return

    chart_data["equity"] = (
        initial_capital
        + chart_data["beneficio_usd"].cumsum()
    )

    chart_data = chart_data.set_index(
        "fecha_dt"
    )

    st.line_chart(
        chart_data["equity"],
        use_container_width=True,
        height=360,
    )


def _setup_panel(
    data: pd.DataFrame,
) -> None:
    st.html(
        """
        <div class="ax-panel-title">
            <strong>🖼️ CAPTURA DEL SETUP</strong>
            <span>AI VISION READY</span>
        </div>
        """
    )

    if data.empty:
        st.html(
            """
            <div class="ax-empty-panel ax-setup-empty">
                <div class="ax-empty-icon">🧠</div>

                <strong>
                    AXION Vision está listo
                </strong>

                <p>
                    Escanea tu primer setup para activar el análisis.
                </p>
            </div>
            """
        )

        if st.button(
            "🧠 ESCANEAR PRIMER SETUP",
            key="dashboard_scan_first",
            use_container_width=True,
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

        return

    ordered = data.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ],
        ascending=False,
    )

    last_trade = ordered.iloc[0]

    image_value = (
        last_trade.get("img_before")
        or last_trade.get("img_after")
        or ""
    )

    info_columns = st.columns(3)

    info_columns[0].metric(
        "Activo",
        str(
            last_trade.get(
                "par",
                "Sin activo",
            )
        ),
    )

    info_columns[1].metric(
        "Dirección",
        str(
            last_trade.get(
                "direccion",
                "-",
            )
        ),
    )

    info_columns[2].metric(
        "PnL",
        _money(
            last_trade.get(
                "beneficio_usd"
            )
        ),
    )

    if image_value:
        st.image(
            image_value,
            use_container_width=True,
        )
    else:
        st.html(
            """
            <div class="ax-image-placeholder">
                📷 El último trade no tiene captura guardada
            </div>
            """
        )


def _recent_trades(
    data: pd.DataFrame,
) -> None:
    st.html(
        """
        <div class="ax-panel-title">
            <strong>🧾 ÚLTIMAS OPERACIONES</strong>
            <span>HISTORIAL RECIENTE</span>
        </div>
        """
    )

    if data.empty:
        st.info(
            "Todavía no existen operaciones."
        )
        return

    recent = data.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ],
        ascending=False,
    ).head(8)

    display_columns = [
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
        recent[display_columns],
        use_container_width=True,
        hide_index=True,
    )


def render_dashboard(
    df: pd.DataFrame,
    trader_name: str = "Trader Pro",
    initial_capital: float | None = None,
) -> None:
    if initial_capital is None:
        initial_capital = float(
            st.session_state.get(
                "capital_actual",
                10000.0,
            )
        )

    data = _prepare_df(df)

    total = len(data)

    pnl = (
        float(data["beneficio_usd"].sum())
        if not data.empty
        else 0.0
    )

    balance = initial_capital + pnl

    wins = (
        int(
            (
                data["beneficio_usd"] > 0
            ).sum()
        )
        if not data.empty
        else 0
    )

    losses = (
        int(
            (
                data["beneficio_usd"] < 0
            ).sum()
        )
        if not data.empty
        else 0
    )

    win_rate = (
        wins / total * 100
        if total > 0
        else 0.0
    )

    gross_profit = (
        float(
            data.loc[
                data["beneficio_usd"] > 0,
                "beneficio_usd",
            ].sum()
        )
        if not data.empty
        else 0.0
    )

    gross_loss = (
        abs(
            float(
                data.loc[
                    data["beneficio_usd"] < 0,
                    "beneficio_usd",
                ].sum()
            )
        )
        if not data.empty
        else 0.0
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0.0
    )

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

    _render_header(trader_name)

    filter_columns = st.columns(
        [
            1,
            1,
            1,
            2,
        ]
    )

    with filter_columns[0]:
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

    with filter_columns[1]:
        st.selectbox(
            "Activo",
            ["Todos"],
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
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

    metric_columns = st.columns(5)

    with metric_columns[0]:
        _metric_card(
            "BALANCE ACTUAL",
            _money(balance),
            "Capital + PnL",
            "#ffffff",
            f"{total} trades",
        )

    with metric_columns[1]:
        pnl_color = (
            "#00ff88"
            if pnl >= 0
            else "#ff1744"
        )

        _metric_card(
            "P&L TOTAL",
            _money(pnl),
            "Resultado acumulado",
            pnl_color,
            "",
        )

    with metric_columns[2]:
        _metric_card(
            "WIN RATE",
            f"{win_rate:.1f}%",
            f"{wins}W / {losses}L",
            "#25e5ff",
            "Aciertos",
        )

    with metric_columns[3]:
        _metric_card(
            "PROFIT FACTOR",
            f"{profit_factor:.2f}",
            "Objetivo ≥ 1.50",
            "#9146ff",
            "Sistema",
        )

    with metric_columns[4]:
        _metric_card(
            "PROP FIRM SCORE",
            str(score),
            "de 100",
            "#00ff88",
            "AXION",
        )

    chart_left, chart_right = st.columns(
        [
            1.65,
            1,
        ],
        gap="large",
    )

    with chart_left:
        _equity_chart(
            data,
            initial_capital,
        )

    with chart_right:
        _setup_panel(data)

    st.html(
        "<div style='height:14px'></div>"
    )

    _recent_trades(data)
