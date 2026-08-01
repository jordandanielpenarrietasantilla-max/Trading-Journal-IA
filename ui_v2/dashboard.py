from __future__ import annotations

import datetime as dt
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ui_v2.components import (
    money,
    render_empty_state,
    render_metric_card,
    render_panel_title,
    render_section_header,
    safe_text,
)
from ui_v2.theme import apply_v2_theme


GREEN = "#00F58A"
RED = "#FF1744"
CYAN = "#19E4FF"
PURPLE = "#8B4DFF"
WHITE = "#F7F9FF"
MUTED = "#91A0BF"


DASHBOARD_CSS = """
<style>
.block-container {
    max-width: 1600px;
    padding-top: 1.2rem;
}

.v2-section-header {
    position:relative;
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:20px;
    flex-wrap:wrap;
    padding:24px 28px;
    margin-bottom:18px;
    overflow:hidden;
}

.v2-section-header:before {
    content:"";
    position:absolute;
    inset:0;
    pointer-events:none;
    background:
        radial-gradient(circle at 85% 18%, rgba(139,77,255,.17), transparent 30%),
        repeating-linear-gradient(90deg, transparent 0 38px, rgba(25,228,255,.025) 39px 40px);
}

.v2-section-header>* { position:relative; z-index:2; }

.v2-section-header p {
    margin:10px 0 0;
    color:#91a0bf;
    font-size:12px;
}

.v2-section-status {
    display:flex;
    align-items:center;
    gap:8px;
    padding:9px 14px;
    color:#00f58a;
    font-size:8px;
    font-weight:900;
    background:rgba(0,245,138,.07);
    border:1px solid rgba(0,245,138,.30);
    border-radius:999px;
}

.v2-section-status span {
    width:7px;
    height:7px;
    border-radius:50%;
    background:#00f58a;
    box-shadow:0 0 11px #00f58a;
}

.v2-metric-card {
    min-height:142px;
    display:flex;
    align-items:flex-start;
    gap:12px;
    padding:16px;
}

.v2-metric-icon {
    width:42px;
    height:42px;
    display:grid;
    place-items:center;
    flex-shrink:0;
    border:1px solid;
    border-radius:12px;
    font-size:18px;
    font-weight:950;
}

.v2-metric-copy { min-width:0; flex:1; }
.v2-metric-label { color:#7f8ba7; font-size:7px; font-weight:950; letter-spacing:1.2px; }
.v2-metric-value { margin-top:8px; font-size:clamp(22px,2vw,30px); line-height:1; font-weight:950; white-space:nowrap; }
.v2-metric-meta { display:flex; justify-content:space-between; gap:8px; margin-top:14px; color:#6f7d9a; font-size:7px; }

.v2-panel-title {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:13px 15px;
    margin-top:17px;
    margin-bottom:9px;
    background:linear-gradient(145deg,rgba(7,15,33,.98),rgba(5,10,25,.98));
    border:1px solid rgba(65,99,165,.28);
    border-radius:14px;
}

.v2-panel-title>div { display:flex; align-items:center; gap:8px; }
.v2-panel-title strong { color:#f7f9ff; font-size:12px; }
.v2-panel-icon { color:#19e4ff; font-size:14px; }
.v2-panel-title small { color:#64718d; font-size:6px; font-weight:850; letter-spacing:1.2px; }

.v2-trades-shell {
    width:100%;
    min-height:390px;
    overflow:hidden;
    background:linear-gradient(145deg,rgba(6,14,31,.98),rgba(4,9,23,.98));
    border:1px solid rgba(65,99,165,.30);
    border-radius:16px;
}

.v2-trades-table { width:100%; table-layout:fixed; border-collapse:collapse; color:#dfe7f8; font-size:10px; }
.v2-trades-table th { padding:13px 9px; color:#72809e; font-size:7px; font-weight:950; text-align:left; letter-spacing:1px; background:rgba(8,17,38,.99); border-bottom:1px solid rgba(68,98,160,.28); }
.v2-trades-table td { overflow:hidden; padding:13px 9px; white-space:nowrap; text-overflow:ellipsis; border-bottom:1px solid rgba(68,98,160,.13); }
.v2-badge { display:inline-flex; align-items:center; justify-content:center; min-width:44px; padding:4px 8px; border-radius:999px; font-size:7px; font-weight:950; }
.v2-long,.v2-win { color:#00f58a; background:rgba(0,245,138,.12); border:1px solid rgba(0,245,138,.24); }
.v2-short,.v2-loss { color:#ff7890; background:rgba(255,23,68,.13); border:1px solid rgba(255,23,68,.25); }
.v2-neutral,.v2-be { color:#91a0bf; background:rgba(130,145,179,.11); }

.v2-summary-card { padding:15px; }
.v2-summary-row { display:flex; justify-content:space-between; gap:12px; padding:10px 0; color:#8996b3; font-size:9px; border-bottom:1px solid rgba(67,98,160,.14); }
.v2-summary-row:last-child { border-bottom:none; }
.v2-empty-state { min-height:260px; display:flex; flex-direction:column; align-items:center; justify-content:center; padding:24px; text-align:center; }
.v2-empty-icon { color:#19e4ff; font-size:31px; }
.v2-empty-state strong { margin-top:11px; color:#f7f9ff; font-size:13px; }
.v2-empty-state p { max-width:360px; margin-top:7px; color:#7d89a5; font-size:9px; line-height:1.5; }

@media (max-width: 1000px) {
    .v2-metric-value { font-size:21px; }
}
</style>
"""


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def _prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()

    if "beneficio_usd" not in data.columns:
        data["beneficio_usd"] = 0.0

    data["beneficio_usd"] = pd.to_numeric(
        data["beneficio_usd"], errors="coerce"
    ).fillna(0.0)

    data["fecha_dt"] = pd.to_datetime(
        data["fecha"] if "fecha" in data.columns else pd.NaT,
        errors="coerce",
    )
    data["created_at_dt"] = pd.to_datetime(
        data["created_at"] if "created_at" in data.columns else data["fecha_dt"],
        errors="coerce",
    )

    for column, default in (
        ("par", "Sin activo"),
        ("direccion", ""),
        ("resultado", ""),
        ("img_before", ""),
        ("img_after", ""),
    ):
        if column not in data.columns:
            data[column] = default

    return data


def _filter_data(data: pd.DataFrame, period: str, asset: str) -> pd.DataFrame:
    if data.empty:
        return data

    filtered = data.copy()
    now = pd.Timestamp.now()

    if period == "Hoy":
        filtered = filtered[filtered["fecha_dt"].dt.date == now.date()]
    elif period == "Últimos 7 días":
        filtered = filtered[filtered["fecha_dt"] >= now - pd.Timedelta(days=7)]
    elif period == "Este mes":
        filtered = filtered[
            (filtered["fecha_dt"].dt.year == now.year)
            & (filtered["fecha_dt"].dt.month == now.month)
        ]

    if asset != "Todos":
        filtered = filtered[filtered["par"].astype(str) == asset]

    return filtered


def _equity_data(data: pd.DataFrame, initial_capital: float) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame()

    equity = data.dropna(subset=["fecha_dt"]).copy()
    equity = equity.sort_values(["fecha_dt", "created_at_dt"])

    if equity.empty:
        return pd.DataFrame()

    equity["equity"] = initial_capital + equity["beneficio_usd"].cumsum()
    equity["peak"] = equity["equity"].cummax()
    equity["drawdown"] = equity["equity"] - equity["peak"]
    return equity


def _result_name(value: Any, pnl: float) -> str:
    clean = str(value or "").strip().upper()
    if clean in {"WIN", "GANADOR", "GANADA", "PROFIT"}:
        return "WIN"
    if clean in {"LOSS", "PERDEDOR", "PERDIDA", "PÉRDIDA", "LOSE"}:
        return "LOSS"
    if clean in {"BE", "BREAK EVEN", "BREAKEVEN"}:
        return "BE"
    if pnl > 0:
        return "WIN"
    if pnl < 0:
        return "LOSS"
    return "BE"


def _render_equity_chart(data: pd.DataFrame, initial_capital: float) -> None:
    render_panel_title(icon="◈", title="CURVA DE EQUITY", subtitle="BALANCE ACUMULADO")
    equity = _equity_data(data, initial_capital)

    if equity.empty:
        render_empty_state(
            icon="◇",
            title="Tu curva comienza con tu primer trade",
            description="Registra una operación para activar rendimiento y drawdown.",
        )
        return

    maximum = _safe_float(equity["equity"].max())
    last_value = _safe_float(equity["equity"].iloc[-1])

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=equity["fecha_dt"],
            y=equity["equity"],
            mode="lines",
            line={"color": CYAN, "width": 3, "shape": "spline", "smoothing": 0.75},
            fill="tozeroy",
            fillcolor="rgba(25,228,255,0.08)",
            hovertemplate="<b>%{x|%d %b %Y}</b><br>Balance: $%{y:,.2f}<extra></extra>",
            showlegend=False,
        )
    )
    figure.add_hline(
        y=maximum,
        line_width=1,
        line_dash="dot",
        line_color=GREEN,
        annotation_text=f"Máximo ${maximum:,.0f}",
        annotation_position="top right",
        annotation_font={"color": GREEN, "size": 10},
    )
    figure.add_trace(
        go.Scatter(
            x=[equity["fecha_dt"].iloc[-1]],
            y=[last_value],
            mode="markers",
            marker={"size": 11, "color": "#3C7DFF", "line": {"color": WHITE, "width": 2}},
            showlegend=False,
        )
    )
    figure.update_layout(
        height=390,
        margin={"l": 8, "r": 8, "t": 24, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        font={"color": MUTED, "family": "Inter"},
        xaxis={"showgrid": True, "gridcolor": "rgba(82,111,175,0.11)", "zeroline": False},
        yaxis={"showgrid": True, "gridcolor": "rgba(82,111,175,0.13)", "zeroline": False, "tickprefix": "$", "tickformat": ",.0f"},
    )
    st.plotly_chart(figure, use_container_width=True, config={"displayModeBar": False})


def _direction_badge(direction: Any) -> str:
    clean = str(direction or "").strip().upper()
    if clean == "LONG":
        return '<span class="v2-badge v2-long">LONG</span>'
    if clean == "SHORT":
        return '<span class="v2-badge v2-short">SHORT</span>'
    return '<span class="v2-badge v2-neutral">—</span>'


def _result_badge(value: Any, pnl: float) -> str:
    result = _result_name(value, pnl)
    class_name = {"WIN": "v2-win", "LOSS": "v2-loss", "BE": "v2-be"}[result]
    return f'<span class="v2-badge {class_name}">{result}</span>'


def _render_recent_trades(data: pd.DataFrame) -> None:
    render_panel_title(icon="▣", title="ÚLTIMAS OPERACIONES", subtitle="HISTORIAL RECIENTE")

    if data.empty:
        render_empty_state(
            icon="▤",
            title="Todavía no existen operaciones",
            description="Tus operaciones más recientes aparecerán aquí.",
        )
        return

    recent = data.sort_values(
        ["fecha_dt", "created_at_dt"], ascending=False
    ).head(6)

    rows = []
    for _, trade in recent.iterrows():
        pnl = _safe_float(trade.get("beneficio_usd"))
        date_value = trade.get("fecha_dt")
        date_text = (
            pd.Timestamp(date_value).strftime("%d/%m/%Y")
            if pd.notna(date_value)
            else "—"
        )
        pnl_color = GREEN if pnl > 0 else RED if pnl < 0 else MUTED

        rows.append(
            f"""
            <tr>
                <td>{date_text}</td>
                <td><strong>{safe_text(trade.get("par","—"))}</strong></td>
                <td>{_direction_badge(trade.get("direccion"))}</td>
                <td>{_result_badge(trade.get("resultado"), pnl)}</td>
                <td style="color:{pnl_color};font-weight:950">{money(pnl)}</td>
            </tr>
            """
        )

    st.html(
        f"""
        <div class="v2-trades-shell">
            <table class="v2-trades-table">
                <thead>
                    <tr>
                        <th>FECHA</th>
                        <th>ACTIVO</th>
                        <th>DIRECCIÓN</th>
                        <th>RESULTADO</th>
                        <th>P&amp;L</th>
                    </tr>
                </thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
        """
    )


def _render_setup(data: pd.DataFrame) -> None:
    render_panel_title(icon="▧", title="CAPTURA DEL SETUP", subtitle="AI VISION READY")

    if data.empty:
        render_empty_state(
            icon="📷",
            title="Sin captura disponible",
            description="Registra un setup para activar el análisis visual.",
        )
        return

    trade = data.sort_values(
        ["fecha_dt", "created_at_dt"], ascending=False
    ).iloc[0]

    image_value = str(
        trade.get("img_before") or trade.get("img_after") or ""
    ).strip()

    if image_value:
        st.image(image_value, use_container_width=True)
    else:
        render_empty_state(
            icon="📷",
            title="Sin captura disponible",
            description="El último trade no tiene una imagen guardada.",
        )


def _maximum_drawdown(data: pd.DataFrame, initial_capital: float) -> float:
    equity = _equity_data(data, initial_capital)
    if equity.empty:
        return 0.0

    drawdown = (
        equity["drawdown"]
        / equity["peak"].replace(0, pd.NA)
        * 100
    )
    minimum = drawdown.min()
    return 0.0 if pd.isna(minimum) else abs(_safe_float(minimum))


def _render_summary(data: pd.DataFrame, initial_capital: float) -> None:
    render_panel_title(icon="⚡", title="RESUMEN RÁPIDO", subtitle="PERFORMANCE")

    if data.empty:
        best_day = worst_day = drawdown = 0.0
        wins = 0
    else:
        dated = data.dropna(subset=["fecha_dt"])
        daily = (
            dated.groupby(dated["fecha_dt"].dt.date)["beneficio_usd"].sum()
            if not dated.empty
            else pd.Series(dtype=float)
        )
        best_day = _safe_float(daily.max()) if not daily.empty else 0.0
        worst_day = _safe_float(daily.min()) if not daily.empty else 0.0
        drawdown = _maximum_drawdown(data, initial_capital)
        wins = int((data["beneficio_usd"] > 0).sum())

    rows = [
        ("Mejor día", money(best_day), GREEN),
        ("Peor día", money(worst_day), RED if worst_day < 0 else MUTED),
        ("Operaciones ganadoras", str(wins), GREEN),
        ("Drawdown máximo", f"{drawdown:.2f}%", GREEN if drawdown < 5 else RED),
    ]

    st.html(
        '<div class="v2-summary-card v2-glass">'
        + "".join(
            f'<div class="v2-summary-row"><span>{label}</span><strong style="color:{color}">{value}</strong></div>'
            for label, value, color in rows
        )
        + "</div>"
    )


def render_v2_dashboard(
    df: pd.DataFrame,
    trader_name: str = "Trader Pro",
    initial_capital: float = 10000.0,
) -> None:
    apply_v2_theme()
    st.markdown(DASHBOARD_CSS, unsafe_allow_html=True)

    data = _prepare_data(df)
    now = dt.datetime.now()

    render_section_header(
        eyebrow="AXION PRIME · PERFORMANCE COMMAND OS X10",
        title=f"¡Buenos días, {trader_name}! 👋",
        description="Disciplina hoy, libertad mañana. Tu desempeño vive en los datos.",
        status=f"{now.strftime('%d %b %Y').upper()} · {now.strftime('%I:%M %p')} · MERCADOS ACTIVOS",
    )

    assets = ["Todos"]
    if not data.empty:
        assets.extend(sorted({str(v).strip() for v in data["par"].dropna() if str(v).strip()}))

    filters = st.columns([1, 1, 1, 1.2], gap="medium")

    with filters[0]:
        period = st.selectbox(
            "Período",
            ["Todo", "Hoy", "Últimos 7 días", "Este mes"],
            label_visibility="collapsed",
            key="v2_dashboard_period",
        )
    with filters[1]:
        asset = st.selectbox(
            "Activo",
            assets,
            label_visibility="collapsed",
            key="v2_dashboard_asset",
        )
    with filters[2]:
        st.selectbox(
            "Vista",
            ["Performance Desk", "Risk Desk", "Psychology Desk"],
            label_visibility="collapsed",
            key="v2_dashboard_view",
        )
    with filters[3]:
        if st.button(
            "＋ REGISTRAR NUEVA OPERACIÓN",
            use_container_width=True,
            key="v2_dashboard_new_trade",
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

    filtered = _filter_data(data, period, asset)

    total = len(filtered)
    pnl = _safe_float(filtered["beneficio_usd"].sum()) if not filtered.empty else 0.0
    balance = initial_capital + pnl
    wins = int((filtered["beneficio_usd"] > 0).sum()) if not filtered.empty else 0
    losses = int((filtered["beneficio_usd"] < 0).sum()) if not filtered.empty else 0
    win_rate = wins / total * 100 if total > 0 else 0.0

    gross_profit = _safe_float(
        filtered.loc[filtered["beneficio_usd"] > 0, "beneficio_usd"].sum()
    ) if not filtered.empty else 0.0
    gross_loss = abs(_safe_float(
        filtered.loc[filtered["beneficio_usd"] < 0, "beneficio_usd"].sum()
    )) if not filtered.empty else 0.0

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else float("inf") if gross_profit > 0 else 0.0
    )

    finite_pf = 3.0 if profit_factor == float("inf") else min(profit_factor, 3.0)
    score = min(100, max(0, round(50 + win_rate * 0.25 + finite_pf * 8)))

    top_metrics = st.columns(3, gap="medium")
    with top_metrics[0]:
        render_metric_card(
            icon="▣",
            label="BALANCE ACTUAL",
            value=money(balance),
            subtitle="Capital + PnL",
            footer=f"{total} trades",
            accent=WHITE,
        )
    with top_metrics[1]:
        render_metric_card(
            icon="↗",
            label="P&L TOTAL",
            value=money(pnl),
            subtitle="Resultado acumulado",
            footer="Performance",
            accent=GREEN if pnl >= 0 else RED,
        )
    with top_metrics[2]:
        render_metric_card(
            icon="◎",
            label="WIN RATE",
            value=f"{win_rate:.1f}%",
            subtitle=f"{wins}W / {losses}L",
            footer="Aciertos",
            accent=CYAN,
        )

    bottom_metrics = st.columns(2, gap="medium")
    with bottom_metrics[0]:
        render_metric_card(
            icon="Σ",
            label="PROFIT FACTOR",
            value="∞" if profit_factor == float("inf") else f"{profit_factor:.2f}",
            subtitle="Objetivo > 1.50",
            footer="Sistema",
            accent=PURPLE,
        )
    with bottom_metrics[1]:
        render_metric_card(
            icon="♢",
            label="AXION SCORE",
            value=str(score),
            subtitle="de 100",
            footer="AI Engine",
            accent=GREEN,
        )

    main_left, main_right = st.columns([1.08, 1], gap="medium")
    with main_left:
        _render_equity_chart(filtered, initial_capital)
    with main_right:
        _render_recent_trades(filtered)

    setup_column, summary_column = st.columns([1.25, 0.75], gap="medium")
    with setup_column:
        _render_setup(filtered)
    with summary_column:
        _render_summary(filtered, initial_capital)
