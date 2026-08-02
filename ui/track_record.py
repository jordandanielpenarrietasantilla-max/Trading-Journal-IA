from __future__ import annotations

import datetime as dt
import html
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.api import delete_trade, update_trade
from core.images import image_to_data_url, normalize_image_value


# =========================================================
# AXION PRIME V4
# TRACK RECORD FUTURISTA + EDICIÓN COMPLETA
# =========================================================


CYAN = "#27D8FF"
BLUE = "#3D73FF"
PURPLE = "#7B5CFF"
GREEN = "#31FF9C"
RED = "#FF3D6E"
YELLOW = "#FFD166"
WHITE = "#EEF4FF"
MUTED = "#93A6C7"
CARD = "#0B1023"
BG = "#050816"


ASSETS = [
    "🥇 XAU/USD (Oro)",
    "🥈 XAG/USD (Plata)",
    "🛢️ USOIL (Petróleo WTI)",
    "🛢️ UKOIL (Petróleo Brent)",
    "🌾 NGAS (Gas Natural)",
    "🪙 BTC/USD (Bitcoin)",
    "🪙 ETH/USD (Ethereum)",
    "🪙 SOL/USD (Solana)",
    "🪙 XRP/USD (Ripple)",
    "🪙 BNB/USD (Binance Coin)",
    "🪙 ADA/USD (Cardano)",
    "🪙 DOGE/USD (Dogecoin)",
    "📊 US100 (Nasdaq 100)",
    "📊 US30 (Dow Jones)",
    "📊 US500 (S&P 500)",
    "📊 GER40 (DAX)",
    "📊 UK100 (FTSE 100)",
    "📊 JP225 (Nikkei 225)",
    "💱 EUR/USD",
    "💱 GBP/USD",
    "💱 USD/JPY",
    "💱 AUD/USD",
    "💱 USD/CAD",
    "💱 USD/CHF",
    "💱 NZD/USD",
    "💱 EUR/GBP",
    "💱 EUR/JPY",
    "💱 GBP/JPY",
    "💱 AUD/JPY",
    "📈 NVDA (Nvidia)",
    "📈 TSLA (Tesla)",
    "📈 AAPL (Apple)",
    "📈 AMZN (Amazon)",
    "📈 MSFT (Microsoft)",
    "📈 GOOGL (Google)",
    "📈 META (Meta)",
    "📈 AMD",
    "📈 NFLX (Netflix)",
    "📈 COIN (Coinbase)",
]

TIMEFRAMES = ["", "M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1"]

RESULTS = ["WIN 🟢", "LOSS 🔴", "BE ⚪"]

EMOTIONS = [
    "Disciplinado / Neutro 🧘",
    "Ansioso ⚡",
    "FOMO 🚀",
    "Frustrado / Venganza 🛑",
    "Eufórico / Sobreconfiado 😎",
    "Miedo 😨",
    "Impaciente ⏳",
]


TRACK_CSS = """
<style>
.block-container {
    max-width: 1720px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.ax-track-hero {
    position: relative;
    overflow: hidden;
    padding: 24px 27px;
    margin-bottom: 16px;
    background:
        radial-gradient(circle at 88% 12%, rgba(123,92,255,.17), transparent 30%),
        linear-gradient(145deg, rgba(7,14,32,.99), rgba(5,8,22,.99));
    border: 1px solid rgba(39,216,255,.27);
    border-radius: 20px;
    box-shadow: 0 24px 70px rgba(0,0,0,.34);
}

.ax-track-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(60,91,157,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(60,91,157,.035) 1px, transparent 1px);
    background-size: 42px 42px;
}

.ax-track-hero > * {
    position: relative;
    z-index: 2;
}

.ax-kicker {
    color: #27d8ff;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 1.9px;
}

.ax-title {
    margin-top: 8px;
    color: #eef4ff;
    font-size: clamp(31px, 3vw, 46px);
    line-height: 1;
    font-weight: 950;
    letter-spacing: -1.7px;
}

.ax-sub {
    margin-top: 9px;
    color: #93a6c7;
    font-size: 11px;
}

.ax-kpi {
    min-height: 125px;
    padding: 15px;
    background:
        radial-gradient(circle at 100% 0%, rgba(39,216,255,.07), transparent 42%),
        linear-gradient(145deg, rgba(9,18,39,.98), rgba(5,10,24,.98));
    border: 1px solid rgba(39,216,255,.23);
    border-radius: 15px;
}

.ax-kpi small {
    display: block;
    color: #8190ae;
    font-size: 7px;
    font-weight: 900;
    letter-spacing: .8px;
}

.ax-kpi strong {
    display: block;
    overflow: hidden;
    margin-top: 10px;
    color: #eef4ff;
    font-size: clamp(23px, 2.1vw, 34px);
    line-height: 1;
    font-weight: 950;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.ax-kpi span {
    display: block;
    margin-top: 10px;
    color: #93a6c7;
    font-size: 8px;
}

.ax-kpi.green strong,
.ax-kpi.green span {
    color: #31ff9c;
}

.ax-kpi.red strong {
    color: #ff3d6e;
}

.ax-panel-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin: 18px 0 9px;
    padding: 13px 15px;
    background: linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.28);
    border-radius: 14px;
}

.ax-panel-head strong {
    color: #eef4ff;
    font-size: 12px;
}

.ax-panel-head span {
    color: #71809e;
    font-size: 7px;
    font-weight: 850;
    letter-spacing: 1px;
}

.ax-trade-row {
    padding: 11px 12px;
    margin-bottom: 7px;
    background:
        linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.24);
    border-radius: 12px;
}

.ax-cell-label {
    color: #71809e;
    font-size: 6px;
    font-weight: 900;
    letter-spacing: .75px;
}

.ax-cell-value {
    overflow: hidden;
    margin-top: 5px;
    color: #eef4ff;
    font-size: 10px;
    font-weight: 850;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.ax-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 48px;
    padding: 5px 8px;
    font-size: 7px;
    font-weight: 950;
    border-radius: 999px;
}

.ax-long {
    color: #31ff9c;
    background: rgba(49,255,156,.08);
    border: 1px solid rgba(49,255,156,.22);
}

.ax-short {
    color: #ff3d6e;
    background: rgba(255,61,110,.08);
    border: 1px solid rgba(255,61,110,.22);
}

.ax-detail {
    padding: 16px;
    margin: 6px 0 12px;
    background:
        radial-gradient(circle at 100% 0%, rgba(123,92,255,.11), transparent 37%),
        linear-gradient(145deg, rgba(8,16,35,.99), rgba(5,9,22,.99));
    border: 1px solid rgba(123,92,255,.38);
    border-radius: 16px;
    box-shadow: 0 14px 44px rgba(0,0,0,.24);
}

.ax-detail-title {
    color: #eef4ff;
    font-size: 16px;
    font-weight: 950;
}

.ax-detail-sub {
    margin-top: 5px;
    color: #93a6c7;
    font-size: 9px;
}

.ax-photo-card {
    padding: 8px;
    background: linear-gradient(145deg,rgba(8,16,35,.98),rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.27);
    border-radius: 14px;
}

.ax-empty-photo {
    min-height: 210px;
    display: grid;
    place-items: center;
    color: #71809e;
    font-size: 10px;
    background: rgba(5,9,22,.78);
    border: 1px dashed rgba(61,91,158,.35);
    border-radius: 12px;
}

.ax-danger {
    padding: 12px;
    color: #ff90aa;
    font-size: 9px;
    background: rgba(255,61,110,.06);
    border: 1px solid rgba(255,61,110,.22);
    border-radius: 12px;
}

div[data-baseweb="select"] > div,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #0b1023 !important;
    border-color: rgba(56,91,166,.42) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#27d8ff,#3d73ff,#7b5cff) !important;
    border: 1px solid rgba(111,212,255,.40) !important;
    box-shadow: 0 10px 28px rgba(61,115,255,.20) !important;
}
</style>
"""


# =========================================================
# HELPERS
# =========================================================


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def _money(value: Any) -> str:
    return f"${_safe_float(value):,.2f}"


def _safe_text(value: Any, default: str = "—") -> str:
    text = str(value or "").strip()
    return text if text else default


def _trade_key(row: pd.Series, index: Any) -> str:
    trade_id = str(row.get("id") or "").strip()
    return trade_id or f"row_{index}"


def _result_name(row: pd.Series) -> str:
    raw = str(row.get("resultado") or "").upper()
    pnl = _safe_float(row.get("beneficio_usd"))

    if "WIN" in raw or "GAN" in raw or pnl > 0:
        return "WIN"
    if "LOSS" in raw or "PERD" in raw or pnl < 0:
        return "LOSS"
    return "BE"


def _direction_clean(value: Any) -> str:
    raw = str(value or "").upper()
    if "SHORT" in raw or "SELL" in raw:
        return "SHORT 🔴"
    return "LONG 🟢"


def _result_clean(value: Any, pnl: float) -> str:
    raw = str(value or "").upper()

    if "WIN" in raw or "GAN" in raw or pnl > 0:
        return "WIN 🟢"

    if "LOSS" in raw or "PERD" in raw or pnl < 0:
        return "LOSS 🔴"

    return "BE ⚪"


def _to_date(value: Any) -> dt.date:
    parsed = pd.to_datetime(value, errors="coerce")

    if pd.isna(parsed):
        return dt.date.today()

    return parsed.date()


def _prepare_track_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    data = df.copy()

    defaults = {
        "id": "",
        "fecha": dt.date.today().isoformat(),
        "par": "Sin activo",
        "direccion": "",
        "precio_entrada": 0.0,
        "stop_loss": 0.0,
        "take_profit": 0.0,
        "rr": 0.0,
        "timeframe": "",
        "resultado": "",
        "emocion": "",
        "notas_emocionales": "",
        "beneficio_usd": 0.0,
        "img_before": "",
        "img_after": "",
        "created_at": "",
    }

    for column, default in defaults.items():
        if column not in data.columns:
            data[column] = default

    numeric_columns = [
        "precio_entrada",
        "stop_loss",
        "take_profit",
        "rr",
        "beneficio_usd",
    ]

    for column in numeric_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce",
        ).fillna(0.0)

    data["fecha_dt"] = pd.to_datetime(
        data["fecha"],
        errors="coerce",
    )

    data["created_at_dt"] = pd.to_datetime(
        data["created_at"],
        errors="coerce",
    )

    data["created_at_dt"] = data["created_at_dt"].fillna(
        data["fecha_dt"]
    )

    return data.sort_values(
        ["fecha_dt", "created_at_dt"],
        ascending=False,
    )


def _equity_frame(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    equity = df.dropna(subset=["fecha_dt"]).copy()
    equity = equity.sort_values(["fecha_dt", "created_at_dt"])

    if equity.empty:
        return pd.DataFrame()

    initial_capital = _safe_float(
        st.session_state.get("capital_actual", 10000.0),
        10000.0,
    )

    # El capital de perfil se considera el capital base.
    equity["equity"] = initial_capital + equity["beneficio_usd"].cumsum()

    return equity


# =========================================================
# HEADER Y KPIS
# =========================================================


def _render_header() -> None:
    st.html(
        """
        <section class="ax-track-hero">
            <div class="ax-kicker">AXION PRIME · PERFORMANCE JOURNAL</div>
            <div class="ax-title">Track Record</div>
            <div class="ax-sub">
                Historial completo, capturas, análisis y administración
                de todas tus operaciones.
            </div>
        </section>
        """
    )


def _render_kpis(df: pd.DataFrame) -> None:
    total = len(df)
    pnl = _safe_float(df["beneficio_usd"].sum())
    wins = int((df["beneficio_usd"] > 0).sum())
    losses = int((df["beneficio_usd"] < 0).sum())
    break_even = int((df["beneficio_usd"] == 0).sum())
    win_rate = wins / total * 100 if total else 0.0

    cards = [
        ("P&L ACUMULADO", _money(pnl), "Resultado neto", "green" if pnl >= 0 else "red"),
        ("WIN RATE", f"{win_rate:.1f}%", f"{wins} ganadoras", "green"),
        ("OPERACIONES", str(total), "Total de trades", ""),
        ("GANADAS / PERDIDAS", f"{wins} / {losses}", "Rendimiento", ""),
        ("BREAK EVEN", str(break_even), "Empates", ""),
    ]

    columns = st.columns(5, gap="medium")

    for column, (label, value, subtitle, css_class) in zip(columns, cards):
        with column:
            st.html(
                f"""
                <div class="ax-kpi {css_class}">
                    <small>{html.escape(label)}</small>
                    <strong title="{html.escape(value)}">{html.escape(value)}</strong>
                    <span>{html.escape(subtitle)}</span>
                </div>
                """
            )


# =========================================================
# GRÁFICOS
# =========================================================


def _render_equity_chart(df: pd.DataFrame) -> None:
    equity = _equity_frame(df)

    if equity.empty:
        st.info("La curva de equity aparecerá cuando existan operaciones.")
        return

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=equity["fecha_dt"],
            y=equity["equity"],
            mode="lines+markers",
            line={
                "color": CYAN,
                "width": 3,
                "shape": "spline",
                "smoothing": 0.65,
            },
            marker={
                "size": 5,
                "color": WHITE,
                "line": {
                    "color": CYAN,
                    "width": 2,
                },
            },
            fill="tozeroy",
            fillcolor="rgba(39,216,255,.09)",
            hovertemplate=(
                "<b>%{x|%d/%m/%Y}</b>"
                "<br>Equity: $%{y:,.2f}"
                "<extra></extra>"
            ),
            showlegend=False,
        )
    )

    figure.update_layout(
        height=340,
        margin={"l": 8, "r": 8, "t": 14, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        hovermode="x unified",
        font={"color": MUTED},
        xaxis={
            "showgrid": True,
            "gridcolor": "rgba(73,103,169,.10)",
            "zeroline": False,
        },
        yaxis={
            "showgrid": True,
            "gridcolor": "rgba(73,103,169,.12)",
            "zeroline": False,
            "tickprefix": "$",
            "tickformat": ",.0f",
        },
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )


def _render_result_chart(df: pd.DataFrame) -> None:
    wins = int((df["beneficio_usd"] > 0).sum())
    losses = int((df["beneficio_usd"] < 0).sum())
    break_even = int((df["beneficio_usd"] == 0).sum())

    figure = go.Figure(
        data=[
            go.Pie(
                labels=["Ganadoras", "Perdedoras", "Break Even"],
                values=[wins, losses, break_even],
                hole=.69,
                marker={
                    "colors": [GREEN, RED, BLUE],
                    "line": {
                        "color": BG,
                        "width": 4,
                    },
                },
                textinfo="none",
                hovertemplate="%{label}: %{value}<extra></extra>",
            )
        ]
    )

    figure.add_annotation(
        text=f"<b>{len(df)}</b><br><span style='font-size:10px'>Total</span>",
        x=.5,
        y=.5,
        showarrow=False,
        font={"color": WHITE, "size": 25},
    )

    figure.update_layout(
        height=340,
        margin={"l": 8, "r": 8, "t": 14, "b": 8},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=True,
        legend={
            "font": {"color": MUTED, "size": 10},
            "orientation": "h",
            "x": .5,
            "xanchor": "center",
            "y": -.02,
        },
    )

    st.plotly_chart(
        figure,
        use_container_width=True,
        config={"displayModeBar": False},
    )


# =========================================================
# CAPTURAS
# =========================================================


def _render_trade_images(row: pd.Series, key_prefix: str) -> None:
    before = normalize_image_value(row.get("img_before", ""))
    after = normalize_image_value(row.get("img_after", ""))

    st.html(
        """
        <div class="ax-panel-head">
            <strong>📸 CAPTURAS DE LA OPERACIÓN</strong>
            <span>ANTES / DESPUÉS</span>
        </div>
        """
    )

    before_column, after_column = st.columns(2, gap="medium")

    with before_column:
        st.markdown("**Captura antes de entrar**")

        if before:
            st.image(
                before,
                use_container_width=True,
                caption="SETUP ANTES",
            )
        else:
            st.html(
                '<div class="ax-empty-photo">No se guardó captura inicial.</div>'
            )

    with after_column:
        st.markdown("**Captura después de cerrar**")

        if after:
            st.image(
                after,
                use_container_width=True,
                caption="RESULTADO",
            )
        else:
            st.html(
                '<div class="ax-empty-photo">No se guardó captura final.</div>'
            )


# =========================================================
# EDICIÓN
# =========================================================


def _render_edit_form(row: pd.Series, key_prefix: str) -> None:
    trade_id = str(row.get("id") or "").strip()

    if not trade_id:
        st.error(
            "Esta operación no tiene ID. No puede editarse hasta que "
            "Supabase devuelva la columna id."
        )
        return

    st.html(
        """
        <div class="ax-panel-head">
            <strong>✏️ EDITAR OPERACIÓN</strong>
            <span>TEXTOS, PRECIOS, RESULTADO E IMÁGENES</span>
        </div>
        """
    )

    current_asset = _safe_text(row.get("par"), "")
    asset_options = list(ASSETS)

    if current_asset and current_asset not in asset_options:
        asset_options.insert(0, current_asset)

    direction_value = _direction_clean(row.get("direccion"))
    pnl_value = _safe_float(row.get("beneficio_usd"))
    result_value = _result_clean(row.get("resultado"), pnl_value)

    current_timeframe = _safe_text(row.get("timeframe"), "")
    if current_timeframe not in TIMEFRAMES:
        current_timeframe = ""

    current_emotion = _safe_text(row.get("emocion"), EMOTIONS[0])
    if current_emotion not in EMOTIONS:
        EMOTIONS_EDIT = [current_emotion] + EMOTIONS
    else:
        EMOTIONS_EDIT = EMOTIONS

    top_left, top_middle, top_right = st.columns(3, gap="medium")

    with top_left:
        edit_date = st.date_input(
            "Fecha",
            value=_to_date(row.get("fecha")),
            key=f"{key_prefix}_edit_date",
        )

        edit_asset = st.selectbox(
            "Activo / Par",
            asset_options,
            index=asset_options.index(current_asset) if current_asset in asset_options else 0,
            key=f"{key_prefix}_edit_asset",
        )

    with top_middle:
        edit_direction = st.selectbox(
            "Dirección",
            ["LONG 🟢", "SHORT 🔴"],
            index=0 if direction_value.startswith("LONG") else 1,
            key=f"{key_prefix}_edit_direction",
        )

        edit_timeframe = st.selectbox(
            "Timeframe",
            TIMEFRAMES,
            index=TIMEFRAMES.index(current_timeframe),
            key=f"{key_prefix}_edit_timeframe",
        )

    with top_right:
        edit_result = st.selectbox(
            "Resultado",
            RESULTS,
            index=RESULTS.index(result_value),
            key=f"{key_prefix}_edit_result",
        )

        edit_emotion = st.selectbox(
            "Emoción",
            EMOTIONS_EDIT,
            index=EMOTIONS_EDIT.index(current_emotion),
            key=f"{key_prefix}_edit_emotion",
        )

    price_1, price_2, price_3, price_4 = st.columns(4, gap="medium")

    with price_1:
        edit_entry = st.number_input(
            "Entrada",
            min_value=0.0,
            value=_safe_float(row.get("precio_entrada")),
            format="%.5f",
            key=f"{key_prefix}_edit_entry",
        )

    with price_2:
        edit_sl = st.number_input(
            "Stop Loss",
            min_value=0.0,
            value=_safe_float(row.get("stop_loss")),
            format="%.5f",
            key=f"{key_prefix}_edit_sl",
        )

    with price_3:
        edit_tp = st.number_input(
            "Take Profit",
            min_value=0.0,
            value=_safe_float(row.get("take_profit")),
            format="%.5f",
            key=f"{key_prefix}_edit_tp",
        )

    with price_4:
        edit_pnl = st.number_input(
            "Ganancia / Pérdida ($)",
            value=pnl_value,
            step=10.0,
            format="%.2f",
            key=f"{key_prefix}_edit_pnl",
        )

    risk = abs(edit_entry - edit_sl)
    reward = abs(edit_tp - edit_entry)
    edit_rr = reward / risk if risk > 0 else 0.0

    st.metric(
        "Riesgo / Beneficio recalculado",
        f"1 : {edit_rr:.2f}",
    )

    edit_notes = st.text_area(
        "Notas y contexto",
        value=_safe_text(row.get("notas_emocionales"), ""),
        height=130,
        key=f"{key_prefix}_edit_notes",
    )

    st.markdown("#### Gestionar imágenes")

    image_left, image_right = st.columns(2, gap="medium")

    with image_left:
        new_before = st.file_uploader(
            "Reemplazar captura ANTES",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"{key_prefix}_new_before",
        )

        remove_before = st.checkbox(
            "Eliminar captura ANTES guardada",
            key=f"{key_prefix}_remove_before",
        )

    with image_right:
        new_after = st.file_uploader(
            "Reemplazar captura DESPUÉS",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"{key_prefix}_new_after",
        )

        remove_after = st.checkbox(
            "Eliminar captura DESPUÉS guardada",
            key=f"{key_prefix}_remove_after",
        )

    save_column, cancel_column = st.columns([1.5, 1], gap="medium")

    with save_column:
        save_changes = st.button(
            "💾 Guardar cambios",
            use_container_width=True,
            type="primary",
            key=f"{key_prefix}_save_changes",
        )

    with cancel_column:
        if st.button(
            "Cancelar edición",
            use_container_width=True,
            key=f"{key_prefix}_cancel_edit",
        ):
            st.session_state.track_edit_id = None
            st.rerun()

    if not save_changes:
        return

    changes: dict[str, Any] = {
        "fecha": str(edit_date),
        "par": edit_asset,
        "direccion": edit_direction,
        "precio_entrada": float(edit_entry),
        "stop_loss": float(edit_sl),
        "take_profit": float(edit_tp),
        "rr": float(edit_rr),
        "timeframe": edit_timeframe,
        "resultado": edit_result,
        "emocion": edit_emotion,
        "notas_emocionales": edit_notes,
        "beneficio_usd": float(edit_pnl),
    }

    if new_before is not None:
        changes["img_before"] = image_to_data_url(new_before)
    elif remove_before:
        changes["img_before"] = ""

    if new_after is not None:
        changes["img_after"] = image_to_data_url(new_after)
    elif remove_after:
        changes["img_after"] = ""

    try:
        with st.spinner("Actualizando la operación en Supabase..."):
            update_trade(trade_id, changes)

        st.success("✅ Operación actualizada correctamente.")
        st.session_state.track_edit_id = None
        st.session_state.track_open_id = trade_id
        st.rerun()

    except Exception as exc:
        st.error(f"No se pudo actualizar la operación: {exc}")


def _render_delete_confirmation(row: pd.Series, key_prefix: str) -> None:
    trade_id = str(row.get("id") or "").strip()

    if not trade_id:
        st.error("La operación no tiene ID y no puede eliminarse.")
        return

    st.html(
        """
        <div class="ax-danger">
            Esta acción eliminará definitivamente el trade y sus imágenes.
            No se puede deshacer.
        </div>
        """
    )

    confirmation = st.text_input(
        'Escribe ELIMINAR para confirmar',
        key=f"{key_prefix}_delete_text",
    )

    delete_column, cancel_column = st.columns([1.2, 1], gap="medium")

    with delete_column:
        confirm_delete = st.button(
            "🗑️ Eliminar definitivamente",
            use_container_width=True,
            key=f"{key_prefix}_confirm_delete",
            disabled=confirmation.strip().upper() != "ELIMINAR",
        )

    with cancel_column:
        if st.button(
            "Cancelar",
            use_container_width=True,
            key=f"{key_prefix}_cancel_delete",
        ):
            st.session_state.track_delete_id = None
            st.rerun()

    if not confirm_delete:
        return

    try:
        with st.spinner("Eliminando la operación..."):
            delete_trade(trade_id)

        st.success("Operación eliminada.")
        st.session_state.track_delete_id = None
        st.session_state.track_open_id = None
        st.rerun()

    except Exception as exc:
        st.error(f"No se pudo eliminar la operación: {exc}")


# =========================================================
# FILA Y DETALLE
# =========================================================


def _render_trade_detail(row: pd.Series, key_prefix: str) -> None:
    pnl = _safe_float(row.get("beneficio_usd"))
    rr = _safe_float(row.get("rr"))
    direction = _direction_clean(row.get("direccion"))

    st.html(
        f"""
        <section class="ax-detail">
            <div class="ax-detail-title">
                {html.escape(_safe_text(row.get("par"), "Sin activo"))}
                · {html.escape(direction)}
            </div>
            <div class="ax-detail-sub">
                Fecha {html.escape(_safe_text(row.get("fecha")))}
                · Timeframe {html.escape(_safe_text(row.get("timeframe")))}
                · Resultado {_money(pnl)}
                · R:R 1 : {rr:.2f}
            </div>
        </section>
        """
    )

    detail_1, detail_2, detail_3, detail_4 = st.columns(4, gap="medium")

    detail_1.metric("Entrada", f"{_safe_float(row.get('precio_entrada')):.5f}")
    detail_2.metric("Stop Loss", f"{_safe_float(row.get('stop_loss')):.5f}")
    detail_3.metric("Take Profit", f"{_safe_float(row.get('take_profit')):.5f}")
    detail_4.metric("P&L", _money(pnl))

    notes = _safe_text(row.get("notas_emocionales"), "")

    if notes:
        st.markdown("**Notas y psicotrading**")
        st.info(notes)

    st.markdown(
        f"**Emoción registrada:** {_safe_text(row.get('emocion'))}"
    )

    _render_trade_images(row, key_prefix)


def _render_trade_row(row: pd.Series, index: Any) -> None:
    key_prefix = _trade_key(row, index)
    trade_id = str(row.get("id") or "").strip()
    pnl = _safe_float(row.get("beneficio_usd"))
    direction = _direction_clean(row.get("direccion"))
    direction_class = "ax-short" if direction.startswith("SHORT") else "ax-long"

    row_columns = st.columns(
        [1.05, 1.5, .9, .75, 1, 1, 1, .72, 1.75, .5, .5, .5],
        gap="small",
    )

    values = [
        ("FECHA", _safe_text(row.get("fecha"))),
        ("ACTIVO", _safe_text(row.get("par"))),
        ("DIRECCIÓN", direction.replace(" 🟢", "").replace(" 🔴", "")),
        ("TF", _safe_text(row.get("timeframe"))),
        ("ENTRADA", f"{_safe_float(row.get('precio_entrada')):.5f}"),
        ("STOP LOSS", f"{_safe_float(row.get('stop_loss')):.5f}"),
        ("TAKE PROFIT", f"{_safe_float(row.get('take_profit')):.5f}"),
        ("R", f"{_safe_float(row.get('rr')):.2f}R"),
        ("P&L / NOTAS", f"{_money(pnl)} · {_safe_text(row.get('notas_emocionales'), 'Sin notas')}"),
    ]

    for column, (label, value) in zip(row_columns[:9], values):
        with column:
            if label == "DIRECCIÓN":
                st.html(
                    f"""
                    <div class="ax-cell-label">{label}</div>
                    <div style="margin-top:5px">
                        <span class="ax-badge {direction_class}">
                            {html.escape(value)}
                        </span>
                    </div>
                    """
                )
            else:
                value_color = GREEN if label == "P&L / NOTAS" and pnl > 0 else RED if label == "P&L / NOTAS" and pnl < 0 else WHITE
                st.html(
                    f"""
                    <div class="ax-cell-label">{html.escape(label)}</div>
                    <div class="ax-cell-value" style="color:{value_color}" title="{html.escape(value)}">
                        {html.escape(value)}
                    </div>
                    """
                )

    with row_columns[9]:
        if st.button(
            "👁",
            key=f"{key_prefix}_view",
            help="Ver detalles y fotografías",
            use_container_width=True,
        ):
            st.session_state.track_open_id = (
                None
                if st.session_state.get("track_open_id") == key_prefix
                else key_prefix
            )
            st.session_state.track_edit_id = None
            st.session_state.track_delete_id = None
            st.rerun()

    with row_columns[10]:
        if st.button(
            "✏️",
            key=f"{key_prefix}_edit",
            help="Editar operación",
            use_container_width=True,
            disabled=not bool(trade_id),
        ):
            st.session_state.track_edit_id = key_prefix
            st.session_state.track_open_id = key_prefix
            st.session_state.track_delete_id = None
            st.rerun()

    with row_columns[11]:
        if st.button(
            "🗑",
            key=f"{key_prefix}_delete",
            help="Eliminar operación",
            use_container_width=True,
            disabled=not bool(trade_id),
        ):
            st.session_state.track_delete_id = key_prefix
            st.session_state.track_open_id = key_prefix
            st.session_state.track_edit_id = None
            st.rerun()

    open_id = st.session_state.get("track_open_id")
    edit_id = st.session_state.get("track_edit_id")
    delete_id = st.session_state.get("track_delete_id")

    if open_id == key_prefix:
        _render_trade_detail(row, key_prefix)

        action_view, action_edit, action_close = st.columns(
            [1.1, 1.1, 1],
            gap="medium",
        )

        with action_view:
            st.caption("El botón 👁 abre y cierra fotografías y datos.")

        with action_edit:
            if edit_id is None and st.button(
                "✏️ Editar esta operación",
                use_container_width=True,
                key=f"{key_prefix}_edit_inside",
                disabled=not bool(trade_id),
            ):
                st.session_state.track_edit_id = key_prefix
                st.rerun()

        with action_close:
            if st.button(
                "Cerrar detalle",
                use_container_width=True,
                key=f"{key_prefix}_close",
            ):
                st.session_state.track_open_id = None
                st.session_state.track_edit_id = None
                st.session_state.track_delete_id = None
                st.rerun()

        if edit_id == key_prefix:
            _render_edit_form(row, key_prefix)

        if delete_id == key_prefix:
            _render_delete_confirmation(row, key_prefix)


# =========================================================
# HISTORIAL
# =========================================================


def _render_history(df: pd.DataFrame) -> None:
    st.html(
        """
        <div class="ax-panel-head">
            <strong>🧾 HISTORIAL DE OPERACIONES</strong>
            <span>VER · EDITAR · ELIMINAR</span>
        </div>
        """
    )

    search_column, asset_column, direction_column = st.columns(
        [1.3, 1, 1],
        gap="medium",
    )

    with search_column:
        search = st.text_input(
            "Buscar",
            placeholder="Activo, nota, fecha...",
            label_visibility="collapsed",
            key="track_search",
        )

    available_assets = sorted(
        {
            _safe_text(value, "")
            for value in df["par"].dropna()
            if _safe_text(value, "")
        }
    )

    with asset_column:
        asset_filter = st.selectbox(
            "Activo",
            ["Todos"] + available_assets,
            label_visibility="collapsed",
            key="track_asset_filter",
        )

    with direction_column:
        direction_filter = st.selectbox(
            "Dirección",
            ["Todas", "LONG", "SHORT"],
            label_visibility="collapsed",
            key="track_direction_filter",
        )

    filtered = df.copy()

    if search.strip():
        query = search.strip().lower()

        mask = (
            filtered["par"].astype(str).str.lower().str.contains(query, na=False)
            | filtered["notas_emocionales"].astype(str).str.lower().str.contains(query, na=False)
            | filtered["fecha"].astype(str).str.lower().str.contains(query, na=False)
        )

        filtered = filtered[mask]

    if asset_filter != "Todos":
        filtered = filtered[filtered["par"].astype(str) == asset_filter]

    if direction_filter != "Todas":
        filtered = filtered[
            filtered["direccion"].astype(str).str.upper().str.contains(direction_filter)
        ]

    if filtered.empty:
        st.info("No hay operaciones que coincidan con los filtros.")
        return

    for index, row in filtered.iterrows():
        st.html('<div class="ax-trade-row">')
        _render_trade_row(row, index)
        st.html("</div>")


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================


def render_track_record(df: pd.DataFrame) -> None:
    st.markdown(TRACK_CSS, unsafe_allow_html=True)

    if "track_open_id" not in st.session_state:
        st.session_state.track_open_id = None

    if "track_edit_id" not in st.session_state:
        st.session_state.track_edit_id = None

    if "track_delete_id" not in st.session_state:
        st.session_state.track_delete_id = None

    _render_header()

    track_df = _prepare_track_df(df)

    if track_df.empty:
        st.info(
            "Aún no existen operaciones guardadas. "
            "Registra tu primer trade para activar el Track Record."
        )

        if st.button(
            "➕ Registrar mi primera operación",
            type="primary",
            key="track_first_trade",
        ):
            st.session_state.page = "Registrar Trade"
            st.rerun()

        return

    _render_kpis(track_df)

    chart_left, chart_right = st.columns([1.65, 1], gap="medium")

    with chart_left:
        st.html(
            """
            <div class="ax-panel-head">
                <strong>📈 EQUITY CURVE</strong>
                <span>EVOLUCIÓN DEL CAPITAL</span>
            </div>
            """
        )
        _render_equity_chart(track_df)

    with chart_right:
        st.html(
            """
            <div class="ax-panel-head">
                <strong>◉ DISTRIBUCIÓN DE RESULTADOS</strong>
                <span>WIN / LOSS / BE</span>
            </div>
            """
        )
        _render_result_chart(track_df)

    history_tab, statistics_tab = st.tabs(
        ["Historial de operaciones", "Estadísticas"]
    )

    with history_tab:
        _render_history(track_df)

    with statistics_tab:
        total_pnl = _safe_float(track_df["beneficio_usd"].sum())
        average_trade = (
            _safe_float(track_df["beneficio_usd"].mean())
            if not track_df.empty
            else 0.0
        )
        best_trade = _safe_float(track_df["beneficio_usd"].max())
        worst_trade = _safe_float(track_df["beneficio_usd"].min())
        average_rr = _safe_float(track_df["rr"].mean())

        stats = st.columns(5, gap="medium")
        stats[0].metric("Total P&L", _money(total_pnl))
        stats[1].metric("Promedio por trade", _money(average_trade))
        stats[2].metric("Mayor ganancia", _money(best_trade))
        stats[3].metric("Mayor pérdida", _money(worst_trade))
        stats[4].metric("Promedio R", f"{average_rr:.2f}R")
