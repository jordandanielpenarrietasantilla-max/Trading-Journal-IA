from __future__ import annotations

import datetime
from typing import Any

import pandas as pd
import streamlit as st

from core.images import normalize_image_value


# =========================================================
# AXION PRIME X10 PRO
# TRACK RECORD VISUAL
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


def _result_color(
    pnl: float,
) -> str:
    if pnl > 0:
        return "#00ff88"

    if pnl < 0:
        return "#ff1744"

    return "#ffd740"


def _result_icon(
    pnl: float,
) -> str:
    if pnl > 0:
        return "🟢"

    if pnl < 0:
        return "🔴"

    return "⚪"


def _prepare_track_df(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Prepara el DataFrame para el calendario visual,
    aunque falten algunas columnas.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    if "fecha" not in result.columns:
        result["fecha"] = datetime.date.today().isoformat()

    result["fecha_dt"] = pd.to_datetime(
        result["fecha"],
        errors="coerce",
    )

    result = result.dropna(
        subset=["fecha_dt"]
    )

    if "beneficio_usd" not in result.columns:
        result["beneficio_usd"] = 0.0

    result["beneficio_usd"] = pd.to_numeric(
        result["beneficio_usd"],
        errors="coerce",
    ).fillna(0.0)

    if "created_at" in result.columns:
        result["created_at_dt"] = pd.to_datetime(
            result["created_at"],
            errors="coerce",
        )
    else:
        result["created_at_dt"] = result["fecha_dt"]

    return result.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ],
        ascending=False,
    )


def _render_header() -> None:
    st.markdown(
        """
        <div class="ax-hero">

            <div
                style="
                    color:#25e5ff;
                    font-size:9px;
                    font-weight:950;
                    letter-spacing:2px;
                "
            >
                AXION PRIME · PERFORMANCE JOURNAL
            </div>

            <div class="ax-title">
                Track Record visual
            </div>

            <div class="ax-sub">
                Cada cuadro representa el resultado neto de un día.
                Abre una fecha para revisar operaciones, capturas,
                emociones y notas guardadas.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_summary(
    df: pd.DataFrame,
) -> None:
    total = len(df)

    total_pnl = float(
        df["beneficio_usd"].sum()
    )

    wins = int(
        (df["beneficio_usd"] > 0).sum()
    )

    losses = int(
        (df["beneficio_usd"] < 0).sum()
    )

    break_even = int(
        (df["beneficio_usd"] == 0).sum()
    )

    win_rate = (
        wins / total * 100
        if total > 0
        else 0.0
    )

    metrics = st.columns(5)

    metrics[0].metric(
        "PnL acumulado",
        _money(total_pnl),
    )

    metrics[1].metric(
        "Operaciones",
        total,
    )

    metrics[2].metric(
        "Win rate",
        f"{win_rate:.1f}%",
    )

    metrics[3].metric(
        "Ganadas / Perdidas",
        f"{wins} / {losses}",
    )

    metrics[4].metric(
        "Break Even",
        break_even,
    )


def _render_day_cards(
    daily_df: pd.DataFrame,
) -> None:
    """
    Muestra tarjetas diarias tipo calendario.
    """

    if daily_df.empty:
        return

    st.markdown(
        "### 📅 Rendimiento diario"
    )

    rows = daily_df.to_dict(
        orient="records"
    )

    for start in range(
        0,
        len(rows),
        4,
    ):
        columns = st.columns(4)

        for column, row in zip(
            columns,
            rows[start:start + 4],
        ):
            pnl = _safe_float(
                row.get("pnl_dia")
            )

            color = _result_color(
                pnl
            )

            icon = _result_icon(
                pnl
            )

            fecha_value = row.get(
                "fecha_dia"
            )

            if isinstance(
                fecha_value,
                pd.Timestamp,
            ):
                fecha_text = fecha_value.strftime(
                    "%d/%m/%Y"
                )
            else:
                fecha_text = str(
                    fecha_value
                )

            trades = int(
                row.get(
                    "operaciones",
                    0,
                )
            )

            with column:
                st.markdown(
                    f"""
                    <div
                        class="ax-card"
                        style="
                            min-height:145px;
                            border-color:{color}66;
                            position:relative;
                            overflow:hidden;
                        "
                    >
                        <div
                            style="
                                display:flex;
                                justify-content:space-between;
                                align-items:center;
                            "
                        >
                            <span
                                style="
                                    color:#8d99b9;
                                    font-size:10px;
                                    font-weight:850;
                                "
                            >
                                {fecha_text}
                            </span>

                            <span style="font-size:18px">
                                {icon}
                            </span>
                        </div>

                        <div
                            style="
                                color:{color};
                                font-size:25px;
                                font-weight:950;
                                margin-top:18px;
                            "
                        >
                            {_money(pnl)}
                        </div>

                        <div
                            style="
                                color:#7785a8;
                                font-size:9px;
                                margin-top:11px;
                            "
                        >
                            {trades} operación(es)
                        </div>

                        <div
                            style="
                                position:absolute;
                                left:16px;
                                right:16px;
                                bottom:10px;
                                height:3px;
                                border-radius:999px;
                                background:{color};
                                box-shadow:0 0 15px {color};
                            "
                        ></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def _display_trade_images(
    row: pd.Series,
) -> None:
    before = normalize_image_value(
        row.get(
            "img_before",
            "",
        )
    )

    after = normalize_image_value(
        row.get(
            "img_after",
            "",
        )
    )

    image_left, image_right = st.columns(2)

    with image_left:
        st.markdown(
            "**1️⃣ Captura antes**"
        )

        if before:
            st.image(
                before,
                use_container_width=True,
            )
        else:
            st.info(
                "No existe captura inicial."
            )

    with image_right:
        st.markdown(
            "**2️⃣ Captura después**"
        )

        if after:
            st.image(
                after,
                use_container_width=True,
            )
        else:
            st.info(
                "No existe captura final."
            )


def _render_trade_details(
    row: pd.Series,
) -> None:
    pnl = _safe_float(
        row.get(
            "beneficio_usd"
        )
    )

    color = _result_color(
        pnl
    )

    left, middle, right = st.columns(
        [
            1.1,
            1.1,
            1,
        ]
    )

    with left:
        st.markdown(
            "#### ⚙️ Ejecución"
        )

        st.write(
            f"**Activo:** {row.get('par', '-')}"
        )

        st.write(
            f"**Dirección:** {row.get('direccion', '-')}"
        )

        st.write(
            f"**Timeframe:** {row.get('timeframe', '-')}"
        )

        st.write(
            f"**Resultado:** {row.get('resultado', '-')}"
        )

    with middle:
        st.markdown(
            "#### 🎯 Precios"
        )

        st.write(
            f"**Entrada:** {row.get('precio_entrada', 0)}"
        )

        st.write(
            f"**Stop Loss:** {row.get('stop_loss', 0)}"
        )

        st.write(
            f"**Take Profit:** {row.get('take_profit', 0)}"
        )

        st.write(
            f"**R:R:** 1 : {_safe_float(row.get('rr')):.2f}"
        )

    with right:
        st.markdown(
            "#### 📊 Resultado"
        )

        st.markdown(
            f"""
            <div
                style="
                    color:{color};
                    font-size:28px;
                    font-weight:950;
                    margin:10px 0 16px;
                "
            >
                {_money(pnl)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write(
            f"**Emoción:** {row.get('emocion', '-')}"
        )

    notes = str(
        row.get(
            "notas_emocionales",
            "",
        )
        or ""
    ).strip()

    if notes:
        st.markdown(
            "#### 🧠 Notas y psicotrading"
        )

        st.info(
            notes
        )

    _display_trade_images(
        row
    )


def _render_history(
    df: pd.DataFrame,
) -> None:
    st.markdown(
        "### 🧾 Operaciones guardadas"
    )

    for index, row in df.iterrows():
        pnl = _safe_float(
            row.get(
                "beneficio_usd"
            )
        )

        icon = _result_icon(
            pnl
        )

        fecha = row.get(
            "fecha",
            "",
        )

        title = (
            f"{icon} {fecha} · "
            f"{row.get('par', 'Sin activo')} · "
            f"{row.get('direccion', '-')} · "
            f"{_money(pnl)}"
        )

        with st.expander(
            title,
            expanded=False,
        ):
            _render_trade_details(
                row
            )


def render_track_record(
    df: pd.DataFrame,
) -> None:
    """
    Pantalla principal del Track Record.
    """

    _render_header()

    track_df = _prepare_track_df(
        df
    )

    if track_df.empty:
        st.info(
            "Aún no aparecen operaciones guardadas. "
            "Registra tu primer trade para activar "
            "el Track Record."
        )

        if st.button(
            "➕ Registrar mi primera operación",
            key="track_record_first_trade",
        ):
            st.session_state.page = (
                "Registrar Trade"
            )

            st.rerun()

        return

    _render_summary(
        track_df
    )

    st.markdown("---")

    daily_df = (
        track_df
        .assign(
            fecha_dia=track_df[
                "fecha_dt"
            ].dt.normalize()
        )
        .groupby(
            "fecha_dia",
            as_index=False,
        )
        .agg(
            pnl_dia=(
                "beneficio_usd",
                "sum",
            ),
            operaciones=(
                "beneficio_usd",
                "size",
            ),
        )
        .sort_values(
            "fecha_dia",
            ascending=False,
        )
    )

    _render_day_cards(
        daily_df
    )

    st.markdown("---")

    _render_history(
        track_df
    )
