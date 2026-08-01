from __future__ import annotations

import datetime
import html
from typing import Any

import streamlit as st

from core.api import save_trade_rpc
from core.images import image_to_data_url
from core.vision import VisionError, scan_trade


# =========================================================
# AXION PRIME X10 PRO
# REGISTRO DE OPERACIONES · UI V4
# =========================================================


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


TRADE_CSS = """
<style>
.block-container {
    max-width: 1600px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.ax-trade-hero {
    position: relative;
    overflow: hidden;
    padding: 25px 27px;
    margin-bottom: 20px;
    background:
        radial-gradient(circle at 88% 12%, rgba(123,92,255,.17), transparent 30%),
        linear-gradient(145deg, rgba(7,14,32,.99), rgba(5,8,22,.99));
    border: 1px solid rgba(39,216,255,.27);
    border-radius: 20px;
    box-shadow: 0 24px 70px rgba(0,0,0,.34);
}

.ax-trade-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(60,91,157,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(60,91,157,.035) 1px, transparent 1px);
    background-size: 42px 42px;
}

.ax-trade-hero > * {
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
    max-width: 760px;
    margin-top: 10px;
    color: #93a6c7;
    font-size: 11px;
    line-height: 1.55;
}

.ax-section-title {
    margin: 5px 0 12px;
    color: #eef4ff;
    font-size: 25px;
    font-weight: 950;
    letter-spacing: -0.7px;
}

.ax-scan-shell {
    margin: 10px 0 14px;
    padding: 15px;
    background:
        radial-gradient(circle at 100% 0%, rgba(39,216,255,.10), transparent 36%),
        linear-gradient(145deg, rgba(8,16,36,.98), rgba(5,10,24,.98));
    border: 1px solid rgba(39,216,255,.27);
    border-radius: 16px;
}

.ax-scan-kicker {
    color: #27d8ff;
    font-size: 7px;
    font-weight: 950;
    letter-spacing: 1.5px;
}

.ax-scan-title {
    margin-top: 7px;
    color: #eef4ff;
    font-size: 15px;
    font-weight: 900;
}

.ax-scan-copy {
    margin-top: 6px;
    color: #93a6c7;
    font-size: 9px;
    line-height: 1.5;
}

.ax-ai-card {
    margin: 8px 0 14px;
    padding: 14px;
    background:
        linear-gradient(145deg, rgba(9,18,39,.98), rgba(5,10,24,.98));
    border: 1px solid rgba(39,216,255,.28);
    border-radius: 16px;
}

.ax-ai-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    margin-bottom: 12px;
}

.ax-ai-card-head strong {
    color: #eef4ff;
    font-size: 12px;
}

.ax-ai-badge {
    padding: 4px 7px;
    color: white;
    font-size: 6px;
    font-weight: 950;
    background: linear-gradient(90deg,#5d42ff,#8f49ff);
    border-radius: 999px;
}

.ax-ai-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0,1fr));
    gap: 9px;
}

.ax-ai-item {
    min-width: 0;
    padding: 11px;
    background: rgba(8,14,31,.92);
    border: 1px solid rgba(61,88,148,.30);
    border-radius: 11px;
}

.ax-ai-item small {
    display: block;
    color: #8190ae;
    font-size: 6.5px;
    font-weight: 850;
    letter-spacing: .45px;
}

.ax-ai-item strong {
    display: block;
    overflow: hidden;
    margin-top: 6px;
    color: #eef4ff;
    font-size: 15px;
    line-height: 1.1;
    font-weight: 950;
    white-space: nowrap;
    text-overflow: ellipsis;
}

.ax-ai-item strong.green { color:#31ff9c; }
.ax-ai-item strong.red { color:#ff3d6e; }
.ax-ai-item strong.cyan { color:#27d8ff; }

.ax-scan-note {
    padding: 11px 13px;
    margin-bottom: 12px;
    color: #31ff9c;
    font-size: 10px;
    background: rgba(49,255,156,.08);
    border: 1px solid rgba(49,255,156,.22);
    border-radius: 12px;
}

.ax-image-frame {
    margin: 8px 0 12px;
    padding: 8px;
    background: linear-gradient(145deg,rgba(8,16,35,.98),rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.27);
    border-radius: 15px;
}

[data-testid="stMetricValue"] {
    font-size: 24px !important;
}

[data-testid="stMetricLabel"] {
    font-size: 10px !important;
}

div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: #070b1e !important;
    border-color: rgba(56,91,166,.44) !important;
}

div[data-baseweb="select"] > div {
    background: #0b1023 !important;
    border-color: rgba(56,91,166,.42) !important;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg,#27d8ff,#3d73ff,#7b5cff) !important;
    border: 1px solid rgba(111,212,255,.40) !important;
    box-shadow: 0 10px 28px rgba(61,115,255,.20) !important;
}

@media (max-width: 1100px) {
    .ax-ai-grid {
        grid-template-columns: repeat(2,minmax(0,1fr));
    }
}

@media (max-width: 700px) {
    .ax-ai-grid {
        grid-template-columns: 1fr;
    }
}
</style>
"""


# =========================================================
# ESTADO
# =========================================================


def _initialize_trade_state() -> None:
    defaults = {
        "trade_asset": "",
        "trade_direction": "LONG 🟢",
        "trade_entry": 0.0,
        "trade_sl": 0.0,
        "trade_tp": 0.0,
        "trade_timeframe": "",
        "trade_result": "BE ⚪",
        "trade_emotion": EMOTIONS[0],
        "trade_notes": "",
        "trade_scan_result": None,
        "trade_scan_message": "",
        "trade_scan_error": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _initialize_widget_state() -> None:
    asset_options = ["— Seleccionar activo —"] + ASSETS

    defaults = {
        "trade_asset_widget": (
            st.session_state.trade_asset
            if st.session_state.trade_asset in asset_options
            else "— Seleccionar activo —"
        ),
        "trade_direction_widget": st.session_state.trade_direction,
        "trade_entry_widget": float(st.session_state.trade_entry),
        "trade_sl_widget": float(st.session_state.trade_sl),
        "trade_tp_widget": float(st.session_state.trade_tp),
        "trade_timeframe_widget": st.session_state.trade_timeframe,
        "trade_result_widget": st.session_state.trade_result,
        "trade_emotion_widget": st.session_state.trade_emotion,
        "trade_notes_widget": st.session_state.trade_notes,
        "trade_pnl_widget": 0.0,
        "trade_date_widget": datetime.date.today(),
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =========================================================
# AUXILIARES
# =========================================================


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def _calculate_rr(entry: float, stop_loss: float, take_profit: float) -> float:
    risk = abs(_safe_float(entry) - _safe_float(stop_loss))
    reward = abs(_safe_float(take_profit) - _safe_float(entry))
    return reward / risk if risk > 0 else 0.0


def _format_price(value: Any) -> str:
    number = _safe_float(value, default=float("nan"))

    if number != number:
        return "No detectado"

    if abs(number) >= 1000:
        return f"{number:,.2f}"

    if abs(number) >= 10:
        return f"{number:,.3f}"

    return f"{number:.5f}"


def _clear_trade_form() -> None:
    logical_keys = {
        "trade_asset": "",
        "trade_direction": "LONG 🟢",
        "trade_entry": 0.0,
        "trade_sl": 0.0,
        "trade_tp": 0.0,
        "trade_timeframe": "",
        "trade_result": "BE ⚪",
        "trade_emotion": EMOTIONS[0],
        "trade_notes": "",
        "trade_scan_result": None,
        "trade_scan_message": "",
        "trade_scan_error": "",
    }

    for key, value in logical_keys.items():
        st.session_state[key] = value

    widget_keys = [
        "trade_asset_widget",
        "trade_direction_widget",
        "trade_entry_widget",
        "trade_sl_widget",
        "trade_tp_widget",
        "trade_timeframe_widget",
        "trade_result_widget",
        "trade_emotion_widget",
        "trade_notes_widget",
        "trade_pnl_widget",
        "trade_date_widget",
        "trade_image_before",
        "trade_image_after",
    ]

    for key in widget_keys:
        st.session_state.pop(key, None)


def _apply_scan_result(result: dict[str, Any]) -> None:
    asset = result.get("asset")
    direction = result.get("direction")
    entry = result.get("entry")
    stop_loss = result.get("sl")
    take_profit = result.get("tp")
    timeframe = result.get("timeframe")

    if asset in ASSETS:
        st.session_state.trade_asset = asset
        st.session_state.trade_asset_widget = asset

    if direction in ("LONG 🟢", "SHORT 🔴"):
        st.session_state.trade_direction = direction
        st.session_state.trade_direction_widget = direction

    if entry is not None:
        value = float(entry)
        st.session_state.trade_entry = value
        st.session_state.trade_entry_widget = value

    if stop_loss is not None:
        value = float(stop_loss)
        st.session_state.trade_sl = value
        st.session_state.trade_sl_widget = value

    if take_profit is not None:
        value = float(take_profit)
        st.session_state.trade_tp = value
        st.session_state.trade_tp_widget = value

    if timeframe in TIMEFRAMES:
        st.session_state.trade_timeframe = timeframe
        st.session_state.trade_timeframe_widget = timeframe


# =========================================================
# VISUAL
# =========================================================


def _render_trade_header() -> None:
    st.html(
        """
        <section class="ax-trade-hero">
            <div class="ax-kicker">AXION PRIME · EXECUTION JOURNAL</div>
            <div class="ax-title">Registrar nueva operación</div>
            <div class="ax-sub">
                Documenta el contexto, la ejecución, el riesgo,
                las emociones y el resultado de cada trade.
            </div>
        </section>
        """
    )


def _render_ai_scanner(uploaded_file) -> None:
    st.html(
        """
        <section class="ax-scan-shell">
            <div class="ax-scan-kicker">AXION VISION</div>
            <div class="ax-scan-title">🧠 Extracción automática del setup</div>
            <div class="ax-scan-copy">
                La IA intentará completar activo, dirección, entrada,
                Stop Loss, Take Profit y timeframe.
            </div>
        </section>
        """
    )

    if uploaded_file is None:
        st.info("Sube la captura del setup para activar AXION Vision.")
        return

    scan_col, clear_col = st.columns([1.7, 1], gap="small")

    with scan_col:
        scan_clicked = st.button(
            "🧠 ESCANEAR Y RELLENAR CAMPOS",
            use_container_width=True,
            type="primary",
            key="scan_trade_button",
        )

    with clear_col:
        if st.button(
            "Limpiar lectura IA",
            use_container_width=True,
            key="clear_scan_button",
        ):
            st.session_state.trade_scan_result = None
            st.session_state.trade_scan_message = ""
            st.session_state.trade_scan_error = ""
            st.rerun()

    if not scan_clicked:
        return

    try:
        with st.spinner("AXION Vision está leyendo el gráfico..."):
            result = scan_trade(
                uploaded_file.getvalue(),
                uploaded_file.type or "image/jpeg",
            )

        st.session_state.trade_scan_result = result
        st.session_state.trade_scan_error = ""
        st.session_state.trade_scan_message = (
            "Lectura completada. Revisa los campos antes de guardar."
        )

        _apply_scan_result(result)
        st.rerun()

    except VisionError as exc:
        st.session_state.trade_scan_error = str(exc)
        st.session_state.trade_scan_message = ""
        st.error(f"No se pudo escanear la captura: {exc}")

    except Exception as exc:
        st.session_state.trade_scan_error = str(exc)
        st.session_state.trade_scan_message = ""
        st.error(f"Error inesperado de AXION Vision: {exc}")


def _render_scan_result() -> None:
    result = st.session_state.get("trade_scan_result")

    if not result:
        return

    message = st.session_state.get("trade_scan_message")

    if message:
        st.html(
            f'<div class="ax-scan-note">✓ {html.escape(str(message))}</div>'
        )

    confidence = _safe_float(result.get("confidence"))
    direction = str(result.get("direction") or "No detectada")
    direction_class = "red" if "SHORT" in direction else "green"

    values = [
        ("Activo detectado", result.get("asset") or "No detectado", ""),
        ("Dirección", direction, direction_class),
        ("Entrada", _format_price(result.get("entry")), "cyan"),
        ("Confianza IA", f"{confidence:.0f}%", "green"),
        ("Stop Loss", _format_price(result.get("sl")), "red"),
        ("Take Profit", _format_price(result.get("tp")), "green"),
        ("Timeframe", result.get("timeframe") or "No detectado", ""),
        (
            "Riesgo / Beneficio",
            f"{_calculate_rr(result.get('entry'), result.get('sl'), result.get('tp')):.2f}R",
            "cyan",
        ),
    ]

    cards = "".join(
        f"""
        <div class="ax-ai-item">
            <small>{html.escape(label)}</small>
            <strong class="{css_class}" title="{html.escape(str(value))}">
                {html.escape(str(value))}
            </strong>
        </div>
        """
        for label, value, css_class in values
    )

    st.html(
        f"""
        <section class="ax-ai-card">
            <div class="ax-ai-card-head">
                <strong>Datos detectados por AXION Vision</strong>
                <span class="ax-ai-badge">IA</span>
            </div>
            <div class="ax-ai-grid">{cards}</div>
        </section>
        """
    )


# =========================================================
# GUARDAR
# =========================================================


def _save_trade(trade_data: dict[str, Any]) -> dict[str, Any]:
    response = save_trade_rpc(trade_data)

    if not isinstance(response, dict):
        raise RuntimeError("Supabase devolvió una respuesta inesperada.")

    return response


# =========================================================
# PANTALLA
# =========================================================


def render_register_trade() -> None:
    _initialize_trade_state()
    _initialize_widget_state()

    st.markdown(TRADE_CSS, unsafe_allow_html=True)
    _render_trade_header()

    left, right = st.columns([1.08, 1], gap="large")

    with left:
        st.html('<div class="ax-section-title">📝 Datos de la operación</div>')

        _render_scan_result()

        fecha = st.date_input(
            "Fecha",
            key="trade_date_widget",
        )

        asset_options = ["— Seleccionar activo —"] + ASSETS

        asset = st.selectbox(
            "Activo / Par",
            asset_options,
            key="trade_asset_widget",
        )

        clean_asset = "" if asset.startswith("—") else asset
        st.session_state.trade_asset = clean_asset

        direction = st.radio(
            "Dirección",
            ["LONG 🟢", "SHORT 🔴"],
            horizontal=True,
            key="trade_direction_widget",
        )

        st.session_state.trade_direction = direction

        c1, c2 = st.columns(2, gap="medium")

        with c1:
            entry = st.number_input(
                "Precio de entrada",
                min_value=0.0,
                format="%.5f",
                key="trade_entry_widget",
            )

            stop_loss = st.number_input(
                "Stop Loss",
                min_value=0.0,
                format="%.5f",
                key="trade_sl_widget",
            )

        with c2:
            take_profit = st.number_input(
                "Take Profit",
                min_value=0.0,
                format="%.5f",
                key="trade_tp_widget",
            )

            timeframe = st.selectbox(
                "Timeframe",
                TIMEFRAMES,
                key="trade_timeframe_widget",
            )

        st.session_state.trade_entry = entry
        st.session_state.trade_sl = stop_loss
        st.session_state.trade_tp = take_profit
        st.session_state.trade_timeframe = timeframe

        rr = _calculate_rr(entry, stop_loss, take_profit)

        st.metric("Risk : Reward", f"1 : {rr:.2f}")

        result = st.selectbox(
            "Resultado",
            RESULTS,
            key="trade_result_widget",
        )

        st.session_state.trade_result = result

        st.html('<div class="ax-section-title">🧠 Psicotrading</div>')

        emotion = st.selectbox(
            "Estado emocional",
            EMOTIONS,
            key="trade_emotion_widget",
        )

        notes = st.text_area(
            "Notas del trade",
            height=145,
            placeholder=(
                "¿Por qué entraste? ¿Respetaste tu plan? "
                "¿Qué sentiste antes, durante y después?"
            ),
            key="trade_notes_widget",
        )

        st.session_state.trade_emotion = emotion
        st.session_state.trade_notes = notes

    with right:
        st.html('<div class="ax-section-title">🖼️ Capturas del setup</div>')

        image_before = st.file_uploader(
            "Captura ANTES de entrar",
            type=["png", "jpg", "jpeg", "webp"],
            key="trade_image_before",
        )

        if image_before is not None:
            st.html('<div class="ax-image-frame">')
            st.image(
                image_before,
                caption="SETUP ANTES",
                use_container_width=True,
            )
            st.html("</div>")

        _render_ai_scanner(image_before)

        image_after = st.file_uploader(
            "Captura DESPUÉS de cerrar",
            type=["png", "jpg", "jpeg", "webp"],
            key="trade_image_after",
        )

        if image_after is not None:
            st.html('<div class="ax-image-frame">')
            st.image(
                image_after,
                caption="RESULTADO",
                use_container_width=True,
            )
            st.html("</div>")

        pnl = st.number_input(
            "Ganancia / Pérdida ($)",
            step=10.0,
            format="%.2f",
            key="trade_pnl_widget",
        )

    st.write("")

    action_left, action_middle, action_right = st.columns(
        [1, 1.2, 1.45],
        gap="medium",
    )

    with action_left:
        clear_button = st.button(
            "🧹 Limpiar campos",
            use_container_width=True,
            key="clear_trade_button",
        )

    with action_middle:
        rescan_button = st.button(
            "🔄 Escanear otra imagen",
            use_container_width=True,
            key="rescan_trade_button",
        )

    with action_right:
        save_button = st.button(
            "💾 Guardar operación",
            use_container_width=True,
            type="primary",
            key="save_trade_button",
        )

    if clear_button:
        _clear_trade_form()
        st.rerun()

    if rescan_button:
        st.session_state.trade_scan_result = None
        st.session_state.trade_scan_message = ""
        st.session_state.trade_scan_error = ""
        st.session_state.pop("trade_image_before", None)
        st.rerun()

    if not save_button:
        return

    validation_errors = []

    if not clean_asset:
        validation_errors.append("Debes seleccionar un activo.")

    if entry <= 0:
        validation_errors.append("La entrada debe ser mayor que cero.")

    if stop_loss <= 0:
        validation_errors.append("El Stop Loss es obligatorio.")

    if take_profit <= 0:
        validation_errors.append("El Take Profit es obligatorio.")

    if not timeframe:
        validation_errors.append("Selecciona un timeframe.")

    if validation_errors:
        for error in validation_errors:
            st.error(error)
        return

    trade_data: dict[str, Any] = {}

    try:
        with st.spinner("Guardando la operación en Supabase..."):
            before_value = (
                image_to_data_url(image_before)
                if image_before
                else ""
            )

            after_value = (
                image_to_data_url(image_after)
                if image_after
                else ""
            )

            trade_data = {
                "fecha": str(fecha),
                "par": clean_asset,
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
                "trades_cant": 1,
                "img_before": before_value,
                "img_after": after_value,
            }

            saved_trade = _save_trade(trade_data)

        st.success("✅ Trade guardado correctamente en Supabase.")

        st.session_state["last_saved_trade"] = saved_trade
        _clear_trade_form()
        st.session_state.page = "Track Record"
        st.rerun()

    except Exception as exc:
        st.error("❌ No se pudo guardar la operación.")
        st.error(str(exc))

        with st.expander("Ver datos enviados a Supabase"):
            safe_preview = {
                key: value
                for key, value in trade_data.items()
                if key not in ("img_before", "img_after")
            }
            st.json(safe_preview)
