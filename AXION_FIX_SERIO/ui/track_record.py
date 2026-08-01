from __future__ import annotations

import datetime
import html
from typing import Any

import pandas as pd
import streamlit as st

from core.api import delete_trade, update_trade
from core.images import image_to_data_url, normalize_image_value
from ui.trades import ASSETS, EMOTIONS, RESULTS, TIMEFRAMES


# =========================================================
# AXION PRIME X10 PRO
# TRACK RECORD VISUAL + EDICIÓN COMPLETA
# =========================================================


TRACK_CSS = """
<style>
.ax-track-hero {
    padding: 23px 25px;
    margin-bottom: 17px;
    background:
        radial-gradient(circle at 88% 12%, rgba(139,77,255,.15), transparent 30%),
        linear-gradient(145deg, rgba(7,16,35,.98), rgba(5,10,25,.98));
    border: 1px solid rgba(62,112,184,.34);
    border-radius: 19px;
}
.ax-track-kicker { color:#25e5ff; font-size:8px; font-weight:950; letter-spacing:1.8px; }
.ax-track-title { margin-top:8px; color:#f7f9ff; font-size:36px; line-height:1; font-weight:950; letter-spacing:-1.4px; }
.ax-track-sub { max-width:760px; margin-top:10px; color:#91a0bf; font-size:10px; line-height:1.55; }
.ax-day-card {
    position:relative;
    min-height:138px;
    overflow:hidden;
    padding:15px;
    background:linear-gradient(145deg,rgba(7,15,33,.98),rgba(4,9,23,.98));
    border:1px solid var(--day-color);
    border-radius:15px;
}
.ax-day-top { display:flex; justify-content:space-between; align-items:center; gap:8px; }
.ax-day-date { color:#8d99b9; font-size:9px; font-weight:850; }
.ax-day-icon { font-size:18px; }
.ax-day-pnl { margin-top:17px; color:var(--day-solid); font-size:23px; font-weight:950; }
.ax-day-trades { margin-top:9px; color:#7785a8; font-size:8px; }
.ax-day-line { position:absolute; left:14px; right:14px; bottom:10px; height:3px; border-radius:999px; background:var(--day-solid); box-shadow:0 0 14px var(--day-solid); }
.ax-edit-help {
    padding:12px 14px;
    margin:8px 0 12px;
    color:#91a0bf;
    font-size:9px;
    line-height:1.5;
    background:rgba(25,228,255,.045);
    border:1px solid rgba(25,228,255,.20);
    border-radius:12px;
}
.ax-image-label { margin:5px 0 7px; color:#dfe7f8; font-size:10px; font-weight:850; }
</style>
"""


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return default


def _money(value: Any) -> str:
    return f"${_safe_float(value):,.2f}"


def _result_color(pnl: float) -> str:
    if pnl > 0:
        return "#00ff88"
    if pnl < 0:
        return "#ff1744"
    return "#ffd740"


def _result_icon(pnl: float) -> str:
    if pnl > 0:
        return "🟢"
    if pnl < 0:
        return "🔴"
    return "⚪"


def _prepare_track_df(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame()

    result = df.copy()

    if "fecha" not in result.columns:
        result["fecha"] = datetime.date.today().isoformat()

    result["fecha_dt"] = pd.to_datetime(result["fecha"], errors="coerce")
    result = result.dropna(subset=["fecha_dt"])

    if "beneficio_usd" not in result.columns:
        result["beneficio_usd"] = 0.0

    result["beneficio_usd"] = pd.to_numeric(
        result["beneficio_usd"], errors="coerce"
    ).fillna(0.0)

    if "created_at" in result.columns:
        result["created_at_dt"] = pd.to_datetime(
            result["created_at"], errors="coerce"
        )
    else:
        result["created_at_dt"] = result["fecha_dt"]

    return result.sort_values(
        ["fecha_dt", "created_at_dt"], ascending=False
    )


def _render_header() -> None:
    st.html(
        """
        <section class="ax-track-hero">
            <div class="ax-track-kicker">AXION PRIME · PERFORMANCE JOURNAL</div>
            <div class="ax-track-title">Track Record visual</div>
            <div class="ax-track-sub">
                Revisa cada operación guardada y modifica fecha, activo,
                precios, resultado, emoción, notas y capturas cuando lo necesites.
            </div>
        </section>
        """
    )


def _render_summary(df: pd.DataFrame) -> None:
    total = len(df)
    total_pnl = float(df["beneficio_usd"].sum())
    wins = int((df["beneficio_usd"] > 0).sum())
    losses = int((df["beneficio_usd"] < 0).sum())
    break_even = int((df["beneficio_usd"] == 0).sum())
    win_rate = wins / total * 100 if total else 0.0

    metrics = st.columns(5)
    metrics[0].metric("PnL acumulado", _money(total_pnl))
    metrics[1].metric("Operaciones", total)
    metrics[2].metric("Win rate", f"{win_rate:.1f}%")
    metrics[3].metric("Ganadas / Perdidas", f"{wins} / {losses}")
    metrics[4].metric("Break Even", break_even)


def _render_day_cards(daily_df: pd.DataFrame) -> None:
    if daily_df.empty:
        return

    st.markdown("### 📅 Rendimiento diario")
    rows = daily_df.to_dict(orient="records")

    for start in range(0, len(rows), 4):
        columns = st.columns(4)
        for column, row in zip(columns, rows[start:start + 4]):
            pnl = _safe_float(row.get("pnl_dia"))
            color = _result_color(pnl)
            icon = _result_icon(pnl)
            fecha_value = row.get("fecha_dia")
            fecha_text = (
                fecha_value.strftime("%d/%m/%Y")
                if isinstance(fecha_value, pd.Timestamp)
                else str(fecha_value)
            )
            trades = int(row.get("operaciones", 0))

            with column:
                st.html(
                    f"""
                    <article class="ax-day-card"
                        style="--day-color:{color}66;--day-solid:{color}">
                        <div class="ax-day-top">
                            <span class="ax-day-date">{html.escape(fecha_text)}</span>
                            <span class="ax-day-icon">{icon}</span>
                        </div>
                        <div class="ax-day-pnl">{_money(pnl)}</div>
                        <div class="ax-day-trades">{trades} operación(es)</div>
                        <div class="ax-day-line"></div>
                    </article>
                    """
                )


def _select_index(options: list[str], value: Any, default: int = 0) -> int:
    text = str(value or "")
    return options.index(text) if text in options else default


def _date_value(value: Any) -> datetime.date:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return datetime.date.today()
    return parsed.date()


def _display_trade_images(row: pd.Series) -> None:
    before = normalize_image_value(row.get("img_before", ""))
    after = normalize_image_value(row.get("img_after", ""))
    image_left, image_right = st.columns(2)

    with image_left:
        st.html('<div class="ax-image-label">1️⃣ Captura antes</div>')
        if before:
            st.image(before, use_container_width=True)
        else:
            st.info("No existe captura inicial.")

    with image_right:
        st.html('<div class="ax-image-label">2️⃣ Captura después</div>')
        if after:
            st.image(after, use_container_width=True)
        else:
            st.info("No existe captura final.")


def _edit_trade_form(row: pd.Series, trade_key: str) -> None:
    st.html(
        """
        <div class="ax-edit-help">
            Puedes reemplazar imágenes, borrar una captura existente y editar
            cualquier dato guardado. Si no subes una imagen nueva, se conserva la actual.
        </div>
        """
    )

    current_before = str(row.get("img_before", "") or "")
    current_after = str(row.get("img_after", "") or "")

    with st.form(f"edit_trade_form_{trade_key}"):
        c1, c2, c3 = st.columns(3)

        with c1:
            fecha = st.date_input(
                "Fecha",
                value=_date_value(row.get("fecha")),
                key=f"edit_date_{trade_key}",
            )
            asset = st.selectbox(
                "Activo / Par",
                ASSETS,
                index=_select_index(ASSETS, row.get("par")),
                key=f"edit_asset_{trade_key}",
            )
            direction_options = ["LONG 🟢", "SHORT 🔴"]
            direction = st.selectbox(
                "Dirección",
                direction_options,
                index=_select_index(direction_options, row.get("direccion")),
                key=f"edit_direction_{trade_key}",
            )

        with c2:
            entry = st.number_input(
                "Precio de entrada",
                min_value=0.0,
                value=_safe_float(row.get("precio_entrada")),
                format="%.5f",
                key=f"edit_entry_{trade_key}",
            )
            stop_loss = st.number_input(
                "Stop Loss",
                min_value=0.0,
                value=_safe_float(row.get("stop_loss")),
                format="%.5f",
                key=f"edit_sl_{trade_key}",
            )
            take_profit = st.number_input(
                "Take Profit",
                min_value=0.0,
                value=_safe_float(row.get("take_profit")),
                format="%.5f",
                key=f"edit_tp_{trade_key}",
            )

        with c3:
            timeframe = st.selectbox(
                "Timeframe",
                TIMEFRAMES,
                index=_select_index(TIMEFRAMES, row.get("timeframe")),
                key=f"edit_tf_{trade_key}",
            )
            result = st.selectbox(
                "Resultado",
                RESULTS,
                index=_select_index(RESULTS, row.get("resultado")),
                key=f"edit_result_{trade_key}",
            )
            pnl = st.number_input(
                "Ganancia / Pérdida ($)",
                value=_safe_float(row.get("beneficio_usd")),
                step=10.0,
                format="%.2f",
                key=f"edit_pnl_{trade_key}",
            )

        emotion = st.selectbox(
            "Estado emocional",
            EMOTIONS,
            index=_select_index(EMOTIONS, row.get("emocion")),
            key=f"edit_emotion_{trade_key}",
        )

        notes = st.text_area(
            "Notas del trade",
            value=str(row.get("notas_emocionales", "") or ""),
            height=130,
            key=f"edit_notes_{trade_key}",
        )

        image_left, image_right = st.columns(2)
        with image_left:
            new_before = st.file_uploader(
                "Reemplazar captura ANTES",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"edit_before_{trade_key}",
            )
            remove_before = st.checkbox(
                "Eliminar captura ANTES guardada",
                value=False,
                key=f"remove_before_{trade_key}",
            )

        with image_right:
            new_after = st.file_uploader(
                "Reemplazar captura DESPUÉS",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"edit_after_{trade_key}",
            )
            remove_after = st.checkbox(
                "Eliminar captura DESPUÉS guardada",
                value=False,
                key=f"remove_after_{trade_key}",
            )

        save_changes = st.form_submit_button(
            "💾 GUARDAR MODIFICACIONES",
            use_container_width=True,
            type="primary",
        )

    if save_changes:
        try:
            before_value = current_before
            after_value = current_after

            if remove_before:
                before_value = ""
            elif new_before is not None:
                before_value = image_to_data_url(new_before)

            if remove_after:
                after_value = ""
            elif new_after is not None:
                after_value = image_to_data_url(new_after)

            risk = abs(entry - stop_loss)
            reward = abs(take_profit - entry)
            rr = reward / risk if risk > 0 else 0.0

            update_trade(
                str(row.get("id", "")),
                {
                    "fecha": fecha.isoformat(),
                    "par": asset,
                    "direccion": direction,
                    "precio_entrada": float(entry),
                    "stop_loss": float(stop_loss),
                    "take_profit": float(take_profit),
                    "rr": float(rr),
                    "timeframe": timeframe,
                    "resultado": result,
                    "emocion": emotion,
                    "notas_emocionales": notes,
                    "beneficio_usd": float(pnl),
                    "img_before": before_value,
                    "img_after": after_value,
                },
            )

            st.success("Operación actualizada correctamente.")
            st.rerun()

        except Exception as exc:
            st.error(f"No se pudo actualizar la operación: {exc}")


def _delete_trade_controls(row: pd.Series, trade_key: str) -> None:
    with st.expander("🗑️ Zona de eliminación", expanded=False):
        confirmed = st.checkbox(
            "Confirmo que deseo eliminar esta operación definitivamente",
            key=f"confirm_delete_{trade_key}",
        )

        if st.button(
            "ELIMINAR OPERACIÓN",
            key=f"delete_trade_{trade_key}",
            disabled=not confirmed,
            use_container_width=True,
        ):
            try:
                delete_trade(str(row.get("id", "")))
                st.success("Operación eliminada.")
                st.rerun()
            except Exception as exc:
                st.error(f"No se pudo eliminar la operación: {exc}")


def _render_trade_details(row: pd.Series, trade_key: str) -> None:
    pnl = _safe_float(row.get("beneficio_usd"))
    color = _result_color(pnl)
    left, middle, right = st.columns([1.1, 1.1, 1])

    with left:
        st.markdown("#### ⚙️ Ejecución")
        st.write(f"**Activo:** {row.get('par', '-')}")
        st.write(f"**Dirección:** {row.get('direccion', '-')}")
        st.write(f"**Timeframe:** {row.get('timeframe', '-')}")
        st.write(f"**Resultado:** {row.get('resultado', '-')}")

    with middle:
        st.markdown("#### 🎯 Precios")
        st.write(f"**Entrada:** {row.get('precio_entrada', 0)}")
        st.write(f"**Stop Loss:** {row.get('stop_loss', 0)}")
        st.write(f"**Take Profit:** {row.get('take_profit', 0)}")
        st.write(f"**R:R:** 1 : {_safe_float(row.get('rr')):.2f}")

    with right:
        st.markdown("#### 📊 Resultado")
        st.html(
            f'<div style="color:{color};font-size:28px;font-weight:950;margin:10px 0 16px">{_money(pnl)}</div>'
        )
        st.write(f"**Emoción:** {row.get('emocion', '-')}")

    notes = str(row.get("notas_emocionales", "") or "").strip()
    if notes:
        st.markdown("#### 🧠 Notas y psicotrading")
        st.info(notes)

    _display_trade_images(row)

    st.markdown("#### ✏️ Modificar operación")
    _edit_trade_form(row, trade_key)
    _delete_trade_controls(row, trade_key)


def _render_history(df: pd.DataFrame) -> None:
    st.markdown("### 🧾 Operaciones guardadas")

    for position, (_, row) in enumerate(df.iterrows()):
        pnl = _safe_float(row.get("beneficio_usd"))
        icon = _result_icon(pnl)
        fecha = row.get("fecha", "")
        trade_id = str(row.get("id", "") or f"row-{position}")
        trade_key = trade_id.replace("-", "_")

        title = (
            f"{icon} {fecha} · {row.get('par', 'Sin activo')} · "
            f"{row.get('direccion', '-')} · {_money(pnl)}"
        )

        with st.expander(title, expanded=False):
            _render_trade_details(row, trade_key)


def render_track_record(df: pd.DataFrame) -> None:
    st.markdown(TRACK_CSS, unsafe_allow_html=True)
    _render_header()
    track_df = _prepare_track_df(df)

    if track_df.empty:
        st.info(
            "Aún no aparecen operaciones guardadas. "
            "Registra tu primer trade para activar el Track Record."
        )

        if st.button("➕ Registrar mi primera operación", key="track_record_first_trade"):
            st.session_state.page = "Registrar Trade"
            st.rerun()
        return

    _render_summary(track_df)

    daily_df = (
        track_df.assign(fecha_dia=track_df["fecha_dt"].dt.normalize())
        .groupby("fecha_dia", as_index=False)
        .agg(
            pnl_dia=("beneficio_usd", "sum"),
            operaciones=("beneficio_usd", "size"),
        )
        .sort_values("fecha_dia", ascending=False)
    )

    _render_day_cards(daily_df)
    st.markdown("---")
    _render_history(track_df)
