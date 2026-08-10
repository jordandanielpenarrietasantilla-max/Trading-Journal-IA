from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# PROYECCIONES · UI V2
# =========================================================


PROJECTION_CSS = """
<style>
.ax-proj-hero{
    position:relative;
    overflow:hidden;
    padding:22px 24px;
    margin:0 0 18px 0;
    border:1px solid rgba(91,105,255,.30);
    border-radius:22px;
    background:
      radial-gradient(circle at 88% 12%, rgba(126,74,255,.16), transparent 30%),
      radial-gradient(circle at 10% 90%, rgba(38,204,255,.10), transparent 34%),
      linear-gradient(145deg, rgba(6,13,31,.99), rgba(5,7,23,.99));
    box-shadow:0 24px 70px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.03);
}
.ax-proj-kicker{
    color:#8d7cff;
    font-size:11px;
    font-weight:950;
    letter-spacing:1.7px;
}
.ax-proj-title{
    margin-top:8px;
    color:#f5f7ff;
    font-size:30px;
    line-height:1.05;
    font-weight:950;
    letter-spacing:-.8px;
}
.ax-proj-sub{
    max-width:780px;
    margin-top:9px;
    color:#9eabc7;
    font-size:14px;
    line-height:1.55;
}
.ax-proj-main{
    padding:20px;
    margin:0 0 14px;
    border:1px solid rgba(79,101,168,.30);
    border-radius:20px;
    background:
      radial-gradient(circle at 100% 0%, rgba(80,68,255,.10), transparent 38%),
      linear-gradient(145deg, rgba(7,14,33,.98), rgba(5,8,24,.98));
}
.ax-proj-main-label{
    color:#7e8ba7;
    font-size:9px;
    font-weight:950;
    letter-spacing:1.2px;
}
.ax-proj-main-value{
    margin-top:9px;
    color:#f7f9ff;
    font-size:38px;
    line-height:1;
    font-weight:950;
    letter-spacing:-1px;
}
.ax-proj-main-row{
    display:flex;
    flex-wrap:wrap;
    align-items:center;
    gap:10px;
    margin-top:10px;
}
.ax-proj-chip{
    display:inline-flex;
    align-items:center;
    padding:6px 10px;
    border:1px solid rgba(54,232,161,.24);
    border-radius:999px;
    background:rgba(54,232,161,.07);
    color:#35e9a2;
    font-size:10px;
    font-weight:900;
}
.ax-proj-note{
    color:#8493af;
    font-size:11px;
}
.ax-scenario-grid{
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:12px;
    margin:14px 0;
}
.ax-scenario{
    padding:15px;
    border:1px solid rgba(75,98,160,.27);
    border-radius:16px;
    background:linear-gradient(145deg,rgba(7,14,33,.97),rgba(5,8,24,.98));
}
.ax-scenario.base{
    border-color:rgba(125,79,255,.65);
    box-shadow:0 0 28px rgba(107,67,255,.10);
}
.ax-scenario small{
    color:#7886a4;
    font-size:8px;
    font-weight:950;
    letter-spacing:.9px;
}
.ax-scenario strong{
    display:block;
    margin-top:8px;
    color:#f4f7ff;
    font-size:22px;
    font-weight:950;
}
.ax-scenario span{
    display:block;
    margin-top:7px;
    color:#8494b2;
    font-size:10px;
    line-height:1.45;
}
.ax-proj-section{
    margin-top:18px;
    margin-bottom:8px;
}
.ax-proj-section-title{
    color:#eef3ff;
    font-size:13px;
    font-weight:950;
}
.ax-proj-section-sub{
    margin-top:4px;
    color:#7686a6;
    font-size:10px;
}
.ax-proj-metrics{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:11px;
    margin:14px 0;
}
.ax-proj-metric{
    min-height:104px;
    padding:15px;
    border:1px solid rgba(75,98,160,.25);
    border-radius:16px;
    background:linear-gradient(145deg,rgba(7,14,33,.98),rgba(5,8,24,.98));
}
.ax-proj-metric small{
    display:block;
    color:#7785a3;
    font-size:8px;
    font-weight:950;
    letter-spacing:.8px;
}
.ax-proj-metric strong{
    display:block;
    margin-top:10px;
    color:#f3f6ff;
    font-size:23px;
    font-weight:950;
    overflow-wrap:anywhere;
}
.ax-proj-metric span{
    display:block;
    margin-top:6px;
    color:#8595b4;
    font-size:10px;
}
.ax-proj-disclaimer{
    margin-top:12px;
    padding:12px 14px;
    border:1px solid rgba(75,98,160,.22);
    border-radius:14px;
    background:rgba(7,12,29,.65);
    color:#7483a1;
    font-size:10px;
    line-height:1.55;
}
@media (max-width:900px){
    .ax-scenario-grid{grid-template-columns:1fr;}
    .ax-proj-metrics{grid-template-columns:repeat(2,minmax(0,1fr));}
}
</style>
"""


def _money(value: float) -> str:
    try:
        return f"${float(value):,.2f}"
    except (TypeError, ValueError):
        return "$0.00"


def _expectancy(
    win_rate: float,
    average_rr: float,
) -> float:
    p_win = win_rate / 100.0
    p_loss = 1.0 - p_win
    return (p_win * average_rr) - p_loss


def _monthly_percent(
    win_rate: float,
    average_rr: float,
    risk_percent: float,
    trades_month: int,
) -> float:
    return (
        _expectancy(
            win_rate,
            average_rr,
        )
        * risk_percent
        * trades_month
    )


def _project_capital(
    capital: float,
    monthly_percent: float,
    months: int,
) -> float:
    return float(
        capital
        * (
            1.0
            + monthly_percent / 100.0
        ) ** months
    )


def _scenario(
    *,
    name: str,
    capital: float,
    win_rate: float,
    average_rr: float,
    risk_percent: float,
    trades_month: int,
    months: int,
) -> dict[str, Any]:
    monthly = _monthly_percent(
        win_rate,
        average_rr,
        risk_percent,
        trades_month,
    )
    projected = _project_capital(
        capital,
        monthly,
        months,
    )
    return {
        "name": name,
        "win_rate": win_rate,
        "average_rr": average_rr,
        "risk_percent": risk_percent,
        "monthly_percent": monthly,
        "projected": projected,
    }


def _projection_df(
    capital: float,
    monthly_percent: float,
    months: int,
) -> pd.DataFrame:
    rows = [
        {
            "Mes": 0,
            "Capital proyectado": float(capital),
        }
    ]

    current = float(capital)

    for month in range(
        1,
        months + 1,
    ):
        current *= (
            1.0
            + monthly_percent / 100.0
        )

        rows.append(
            {
                "Mes": month,
                "Capital proyectado": current,
            }
        )

    return pd.DataFrame(rows)


def render_v2_projections() -> None:
    """
    Simulador matemático premium de AXION PRIME.

    Conserva la misma lógica de expectativa:
        E[R] = P(win) * R:R - P(loss)
    y capitalización mensual compuesta.
    """

    st.html(PROJECTION_CSS)

    st.html(
        '<section class="ax-proj-hero">'
        '<div class="ax-proj-kicker">AXION PRIME · EXPECTANCY ENGINE</div>'
        '<div class="ax-proj-title">📈 Proyecciones</div>'
        '<div class="ax-proj-sub">Simula cómo podrían evolucionar distintos escenarios matemáticos según tu win rate, frecuencia, riesgo y relación R:R. Ajusta las variables y observa cómo cambia la curva.</div>'
        '</section>'
    )

    left, right = st.columns(
        2,
        gap="large",
    )

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
            key="v2_projection_capital",
        )

        trades_month = st.slider(
            "Operaciones por mes",
            min_value=1,
            max_value=100,
            value=20,
            key="v2_projection_trades_month",
        )

        months = st.slider(
            "Meses de proyección",
            min_value=1,
            max_value=36,
            value=12,
            key="v2_projection_months",
        )

    with right:
        win_rate = st.slider(
            "Win rate estimado (%)",
            min_value=1,
            max_value=99,
            value=55,
            key="v2_projection_win_rate",
        )

        average_rr = st.number_input(
            "R:R promedio",
            min_value=0.1,
            value=2.0,
            step=0.1,
            key="v2_projection_average_rr",
        )

        risk_percent = st.number_input(
            "Riesgo por operación (%)",
            min_value=0.01,
            max_value=20.0,
            value=1.0,
            step=0.1,
            key="v2_projection_risk",
        )

    expectancy_r = _expectancy(
        win_rate,
        average_rr,
    )

    expected_monthly_percent = (
        expectancy_r
        * risk_percent
        * trades_month
    )

    expected_monthly_money = (
        capital
        * expected_monthly_percent
        / 100.0
    )

    projected_capital = _project_capital(
        capital,
        expected_monthly_percent,
        months,
    )

    growth_percent = (
        (
            projected_capital / capital - 1
        ) * 100.0
        if capital > 0
        else 0.0
    )

    expected_wins = (
        trades_month
        * win_rate
        / 100.0
    )
    expected_losses = (
        trades_month
        - expected_wins
    )

    st.html(
        '<section class="ax-proj-main">'
        '<div class="ax-proj-main-label">CAPITAL PROYECTADO · ESCENARIO BASE</div>'
        f'<div class="ax-proj-main-value">{_money(projected_capital)}</div>'
        '<div class="ax-proj-main-row">'
        f'<div class="ax-proj-chip">↗ {growth_percent:,.1f}% en {months} meses</div>'
        f'<div class="ax-proj-note">Desde {_money(capital)} · {trades_month} operaciones/mes · riesgo {risk_percent:.2f}%</div>'
        '</div>'
        '</section>'
    )

    # Escenarios transparentes derivados del escenario base.
    conservative = _scenario(
        name="Conservador",
        capital=capital,
        win_rate=max(
            1.0,
            win_rate - 8.0,
        ),
        average_rr=max(
            0.1,
            average_rr * 0.85,
        ),
        risk_percent=max(
            0.01,
            risk_percent * 0.75,
        ),
        trades_month=trades_month,
        months=months,
    )

    base = _scenario(
        name="Base",
        capital=capital,
        win_rate=float(win_rate),
        average_rr=float(average_rr),
        risk_percent=float(risk_percent),
        trades_month=trades_month,
        months=months,
    )

    aggressive = _scenario(
        name="Agresivo",
        capital=capital,
        win_rate=min(
            99.0,
            win_rate + 5.0,
        ),
        average_rr=max(
            0.1,
            average_rr * 1.10,
        ),
        risk_percent=min(
            20.0,
            risk_percent * 1.25,
        ),
        trades_month=trades_month,
        months=months,
    )

    st.html(
        '<div class="ax-scenario-grid">'
        f'<div class="ax-scenario"><small>CONSERVADOR</small><strong>{_money(conservative["projected"])}</strong><span>WR {conservative["win_rate"]:.0f}% · R:R {conservative["average_rr"]:.2f} · Riesgo {conservative["risk_percent"]:.2f}%</span></div>'
        f'<div class="ax-scenario base"><small>BASE</small><strong>{_money(base["projected"])}</strong><span>WR {base["win_rate"]:.0f}% · R:R {base["average_rr"]:.2f} · Riesgo {base["risk_percent"]:.2f}%</span></div>'
        f'<div class="ax-scenario"><small>AGRESIVO</small><strong>{_money(aggressive["projected"])}</strong><span>WR {aggressive["win_rate"]:.0f}% · R:R {aggressive["average_rr"]:.2f} · Riesgo {aggressive["risk_percent"]:.2f}%</span></div>'
        '</div>'
    )

    st.html(
        '<div class="ax-proj-metrics">'
        f'<div class="ax-proj-metric"><small>EXPECTATIVA POR TRADE</small><strong>{expectancy_r:.2f}R</strong><span>Valor esperado matemático</span></div>'
        f'<div class="ax-proj-metric"><small>EXPECTATIVA MENSUAL</small><strong>{expected_monthly_percent:.2f}%</strong><span>Según frecuencia y riesgo</span></div>'
        f'<div class="ax-proj-metric"><small>RESULTADO MENSUAL ESTIMADO</small><strong>{_money(expected_monthly_money)}</strong><span>Sobre el capital inicial</span></div>'
        f'<div class="ax-proj-metric"><small>RESULTADOS ESPERADOS / MES</small><strong>{expected_wins:.1f}W · {expected_losses:.1f}L</strong><span>Promedio estadístico, no secuencia real</span></div>'
        '</div>'
    )

    st.html(
        '<div class="ax-proj-section">'
        '<div class="ax-proj-section-title">Proyección matemática del capital</div>'
        '<div class="ax-proj-section-sub">Comparación visual de los tres escenarios durante el horizonte seleccionado.</div>'
        '</div>'
    )

    base_df = _projection_df(
        capital,
        base["monthly_percent"],
        months,
    )
    conservative_df = _projection_df(
        capital,
        conservative["monthly_percent"],
        months,
    )
    aggressive_df = _projection_df(
        capital,
        aggressive["monthly_percent"],
        months,
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=conservative_df["Mes"],
            y=conservative_df[
                "Capital proyectado"
            ],
            mode="lines",
            name="Conservador",
            line={
                "width": 2,
                "dash": "dot",
            },
        )
    )

    fig.add_trace(
        go.Scatter(
            x=base_df["Mes"],
            y=base_df[
                "Capital proyectado"
            ],
            mode="lines+markers",
            name="Base",
            line={
                "width": 3,
            },
            marker={
                "size": 6,
            },
        )
    )

    fig.add_trace(
        go.Scatter(
            x=aggressive_df["Mes"],
            y=aggressive_df[
                "Capital proyectado"
            ],
            mode="lines",
            name="Agresivo",
            line={
                "width": 2,
                "dash": "dash",
            },
        )
    )

    fig.update_layout(
        height=460,
        margin={
            "l": 20,
            "r": 20,
            "t": 20,
            "b": 20,
        },
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,10,27,.78)",
        font={
            "color": "#AEBAD1",
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        xaxis={
            "title": "Mes",
            "gridcolor": "rgba(118,135,175,.12)",
            "zeroline": False,
        },
        yaxis={
            "title": "Capital proyectado",
            "gridcolor": "rgba(118,135,175,.12)",
            "zeroline": False,
            "tickprefix": "$",
        },
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )

    st.html(
        '<div class="ax-proj-disclaimer">'
        'Esta herramienta es una simulación matemática basada en los parámetros introducidos. '
        'No incorpora secuencias reales de ganancias/pérdidas, slippage, comisiones, cambios de '
        'riesgo ni condiciones futuras del mercado, y no constituye una garantía de resultados.'
        '</div>'
    )
