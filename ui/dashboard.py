from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st


def _number(
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
    return f"${_number(value):,.2f}"


def _prepare_dashboard_df(
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

    return result


def _metric_card(
    title: str,
    value: str,
    subtitle: str,
    color: str,
) -> None:
    st.markdown(
        f"""
        <div class="ax-card" style="min-height:145px;">
            <div style="
                color:#7f8bad;
                font-size:9px;
                font-weight:900;
                letter-spacing:1.4px;
            ">
                {title}
            </div>

            <div style="
                color:{color};
                font-size:28px;
                font-weight:950;
                margin-top:16px;
            ">
                {value}
            </div>

            <div style="
                color:#8290b1;
                font-size:10px;
                margin-top:12px;
            ">
                {subtitle}
            </div>

            <div style="
                height:3px;
                border-radius:999px;
                margin-top:18px;
                background:linear-gradient(
                    90deg,
                    {color},
                    #9146ff
                );
            "></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(
    df: pd.DataFrame,
    trader_name: str = "Trader Pro",
    initial_capital: float | None = None,
) -> None:
    """
    Dashboard principal de AXION PRIME.
    """

    if initial_capital is None:
        initial_capital = float(
            st.session_state.get(
                "capital_actual",
                10000.0,
            )
        )

    data = _prepare_dashboard_df(df)

    total_trades = len(data)

    pnl_total = (
        float(data["beneficio_usd"].sum())
        if not data.empty
        else 0.0
    )

    balance = initial_capital + pnl_total

    wins = (
        int((data["beneficio_usd"] > 0).sum())
        if not data.empty
        else 0
    )

    losses = (
        int((data["beneficio_usd"] < 0).sum())
        if not data.empty
        else 0
    )

    win_rate = (
        wins / total_trades * 100
        if total_trades > 0
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

    st.markdown(
        f"""
        <div class="ax-hero">
            <div style="
                color:#25e5ff;
                font-size:9px;
                font-weight:950;
                letter-spacing:2px;
            ">
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
        """,
        unsafe_allow_html=True,
    )

    top_left, top_right = st.columns(
        [3, 2]
    )

    with top_left:
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

    with top_right:
        if st.button(
            "＋ REGISTRAR NUEVA OPERACIÓN",
            use_container_width=True,
            key="dashboard_new_trade",
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

    cards = st.columns(5)

    with cards[0]:
        _metric_card(
            "BALANCE ACTUAL",
            _money(balance),
            f"{total_trades} operaciones",
            "#ffffff",
        )

    with cards[1]:
        pnl_color = (
            "#00ff88"
            if pnl_total >= 0
            else "#ff1744"
        )

        _metric_card(
            "P&L TOTAL",
            _money(pnl_total),
            "Resultado acumulado",
            pnl_color,
        )

    with cards[2]:
        _metric_card(
            "WIN RATE",
            f"{win_rate:.1f}%",
            f"{wins} ganadas · {losses} perdidas",
            "#25e5ff",
        )

    with cards[3]:
        _metric_card(
            "PROFIT FACTOR",
            f"{profit_factor:.2f}",
            "Objetivo recomendado ≥ 1.50",
            "#9146ff",
        )

    with cards[4]:
        score = min(
            100,
            max(
                0,
                round(
                    50
                    + win_rate * 0.25
                    + min(profit_factor, 3) * 8
                ),
            ),
        )

        _metric_card(
            "PROP FIRM SCORE",
            str(score),
            "Puntuación AXION",
            "#00ff88",
        )

    st.markdown("## 📈 Curva de equity")

    if data.empty:
        st.markdown(
            """
            <div class="ax-card" style="
                min-height:330px;
                display:flex;
                align-items:center;
                justify-content:center;
                text-align:center;
            ">
                <div>
                    <div style="
                        font-size:42px;
                        color:#25e5ff;
                    ">
                        ◇
                    </div>

                    <div style="
                        font-size:18px;
                        font-weight:900;
                        margin-top:14px;
                    ">
                        Tu curva comienza con tu primer trade
                    </div>

                    <div style="
                        color:#8290b1;
                        font-size:11px;
                        margin-top:8px;
                    ">
                        Registra una operación para activar
                        métricas, estadísticas y Track Record.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        return

    chart_data = data.copy()

    chart_data = chart_data.sort_values(
        "fecha_dt"
    )

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
    )

    st.markdown("## 🧾 Últimas operaciones")

    display_columns = [
        column
        for column in [
            "fecha",
            "par",
            "direccion",
            "precio_entrada",
            "stop_loss",
            "take_profit",
            "resultado",
            "beneficio_usd",
        ]
        if column in data.columns
    ]

    st.dataframe(
        data.tail(10)[display_columns],
        use_container_width=True,
        hide_index=True,
    )
