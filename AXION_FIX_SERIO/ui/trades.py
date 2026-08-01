from __future__ import annotations

import datetime
from typing import Any

import streamlit as st

from core.api import save_trade_rpc
from core.images import image_to_data_url
from core.vision import (
    VisionError,
    scan_trade,
)


# =========================================================
# AXION PRIME X10 PRO
# REGISTRO DE OPERACIONES
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


TIMEFRAMES = [
    "",
    "M1",
    "M5",
    "M15",
    "M30",
    "H1",
    "H4",
    "D1",
    "W1",
]


RESULTS = [
    "WIN 🟢",
    "LOSS 🔴",
    "BE ⚪",
]


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
.ax-trade-hero {
    position: relative;
    overflow: hidden;
    padding: 24px 26px;
    margin-bottom: 18px;
    background:
        radial-gradient(circle at 88% 15%, rgba(139,77,255,.16), transparent 29%),
        linear-gradient(145deg, rgba(7,16,35,.98), rgba(5,10,25,.98));
    border: 1px solid rgba(62,112,184,.34);
    border-radius: 20px;
    box-shadow: 0 22px 65px rgba(0,0,0,.30);
}

.ax-trade-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(59,94,157,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(59,94,157,.035) 1px, transparent 1px);
    background-size: 42px 42px;
}

.ax-trade-hero > * {
    position: relative;
    z-index: 2;
}

.ax-kicker {
    color: #25e5ff;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 1.9px;
}

.ax-title {
    margin-top: 8px;
    color: #f7f9ff;
    font-size: clamp(30px, 3vw, 46px);
    line-height: 1;
    font-weight: 950;
    letter-spacing: -1.6px;
}

.ax-sub {
    max-width: 720px;
    margin-top: 10px;
    color: #91a0bf;
    font-size: 11px;
    line-height: 1.55;
}

.ax-vision-card {
    padding: 17px;
    margin: 10px 0 14px;
    background:
        radial-gradient(circle at 100% 0%, rgba(25,228,255,.10), transparent 35%),
        linear-gradient(145deg, rgba(7,15,33,.98), rgba(4,9,23,.98));
    border: 1px solid rgba(25,228,255,.28);
    border-radius: 16px;
}

.ax-vision-kicker {
    color: #25e5ff;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 1.5px;
}

.ax-vision-title {
    margin-top: 7px;
    color: #f7f9ff;
    font-size: 16px;
    font-weight: 900;
}

.ax-vision-copy {
    margin-top: 7px;
    color: #8794b6;
    font-size: 10px;
    line-height: 1.5;
}

.ax-scan-result {
    padding: 14px;
    margin-bottom: 12px;
    background: rgba(0,245,138,.045);
    border: 1px solid rgba(0,245,138,.22);
    border-radius: 14px;
}

.ax-form-section {
    margin: 10px 0 8px;
    color: #f7f9ff;
    font-size: 25px;
    font-weight: 950;
    letter-spacing: -0.8px;
}
</style>
"""


def _render_trade_styles() -> None:
    st.markdown(
        TRADE_CSS,
        unsafe_allow_html=True,
    )


# =========================================================
# ESTADO INICIAL
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


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================


def _safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:
        return float(value or 0)

    except (TypeError, ValueError):
        return default


def _calculate_rr(
    entry: float,
    stop_loss: float,
    take_profit: float,
) -> float:

    entry = _safe_float(entry)
    stop_loss = _safe_float(stop_loss)
    take_profit = _safe_float(take_profit)

    risk = abs(
        entry - stop_loss
    )

    reward = abs(
        take_profit - entry
    )

    if risk <= 0:
        return 0.0

    return reward / risk


def _clear_trade_form() -> None:

    st.session_state.trade_asset = ""
    st.session_state.trade_direction = "LONG 🟢"
    st.session_state.trade_entry = 0.0
    st.session_state.trade_sl = 0.0
    st.session_state.trade_tp = 0.0
    st.session_state.trade_timeframe = ""
    st.session_state.trade_result = "BE ⚪"
    st.session_state.trade_emotion = EMOTIONS[0]
    st.session_state.trade_notes = ""

    st.session_state.trade_scan_result = None
    st.session_state.trade_scan_message = ""
    st.session_state.trade_scan_error = ""


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
    ]

    for key in widget_keys:
        st.session_state.pop(key, None)

    uploader_keys = [
        "trade_image_before",
        "trade_image_after",
    ]

    for key in uploader_keys:

        if key in st.session_state:
            del st.session_state[key]


def _apply_scan_result(
    result: dict[str, Any],
) -> None:
    """
    Aplica los valores detectados por AXION Vision tanto al
    estado lógico como a los widgets visibles del formulario.
    """

    asset = result.get("asset")
    direction = result.get("direction")
    entry = result.get("entry")
    stop_loss = result.get("sl")
    take_profit = result.get("tp")
    timeframe = result.get("timeframe")

    if asset in ASSETS:
        st.session_state.trade_asset = asset
        st.session_state.trade_asset_widget = asset

    if direction in ["LONG 🟢", "SHORT 🔴"]:
        st.session_state.trade_direction = direction
        st.session_state.trade_direction_widget = direction

    if entry is not None:
        entry_value = float(entry)
        st.session_state.trade_entry = entry_value
        st.session_state.trade_entry_widget = entry_value

    if stop_loss is not None:
        sl_value = float(stop_loss)
        st.session_state.trade_sl = sl_value
        st.session_state.trade_sl_widget = sl_value

    if take_profit is not None:
        tp_value = float(take_profit)
        st.session_state.trade_tp = tp_value
        st.session_state.trade_tp_widget = tp_value

    if timeframe in TIMEFRAMES:
        st.session_state.trade_timeframe = timeframe
        st.session_state.trade_timeframe_widget = timeframe


# =========================================================
# ENCABEZADO
# =========================================================


def _render_trade_header() -> None:
    st.html(
        """
        <section class="ax-trade-hero">
            <div class="ax-kicker">
                AXION PRIME · EXECUTION JOURNAL
            </div>

            <div class="ax-title">
                Registrar nueva operación
            </div>

            <div class="ax-sub">
                Documenta el contexto, la ejecución, el riesgo,
                las emociones y el resultado de cada trade.
            </div>
        </section>
        """
    )


# =========================================================
# ESCÁNER VISUAL
# =========================================================


def _render_ai_scanner(
    uploaded_file,
) -> None:
    st.html(
        """
        <section class="ax-vision-card">
            <div class="ax-vision-kicker">
                AXION VISION
            </div>

            <div class="ax-vision-title">
                🧠 Extracción automática del setup
            </div>

            <div class="ax-vision-copy">
                Sube una captura de TradingView y la IA intentará
                completar activo, dirección, entrada, Stop Loss,
                Take Profit y timeframe.
            </div>
        </section>
        """
    )

    if uploaded_file is None:
        st.info(
            "Sube la captura ANTES de entrar para activar "
            "el escáner automático."
        )
        return

    scan_column, clear_column = st.columns(
        [1.7, 1],
        gap="small",
    )

    with scan_column:
        scan_clicked = st.button(
            "🧠 ESCANEAR Y RELLENAR CAMPOS",
            use_container_width=True,
            key="scan_trade_button",
            type="primary",
        )

    with clear_column:
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
        with st.spinner(
            "AXION Vision está leyendo el gráfico..."
        ):
            result = scan_trade(
                uploaded_file.getvalue(),
                uploaded_file.type or "image/jpeg",
            )

        st.session_state.trade_scan_result = result
        st.session_state.trade_scan_error = ""

        _apply_scan_result(result)

        st.session_state.trade_scan_message = (
            "Lectura completada. Revisa los campos antes de guardar."
        )

        st.rerun()

    except VisionError as exc:
        st.session_state.trade_scan_error = str(exc)
        st.session_state.trade_scan_message = ""
        st.error(
            f"No se pudo escanear la captura: {exc}"
        )

    except Exception as exc:
        st.session_state.trade_scan_error = str(exc)
        st.session_state.trade_scan_message = ""
        st.error(
            f"Error inesperado de AXION Vision: {exc}"
        )


# =========================================================
# RESULTADO DEL ESCÁNER
# =========================================================


def _render_scan_result() -> None:

    result = st.session_state.get(
        "trade_scan_result"
    )

    if not result:
        return

    if st.session_state.get(
        "trade_scan_message"
    ):
        st.success(
            st.session_state.trade_scan_message
        )

    st.html(
        """
        <div class="ax-scan-result">
            <strong>Datos detectados por AXION Vision</strong>
        </div>
        """
    )

    confidence = _safe_float(
        result.get("confidence")
    )

    columns = st.columns(4)

    columns[0].metric(
        "Activo detectado",
        result.get("asset")
        or "No detectado",
    )

    columns[1].metric(
        "Dirección",
        result.get("direction")
        or "No detectada",
    )

    columns[2].metric(
        "Entrada",
        (
            f"{result.get('entry'):.5f}"
            if result.get("entry") is not None
            else "No detectada"
        ),
    )

    columns[3].metric(
        "Confianza IA",
        f"{confidence:.0f}%",
    )

    secondary = st.columns(3)

    secondary[0].metric(
        "Stop Loss",
        (
            str(result.get("sl"))
            if result.get("sl") is not None
            else "No detectado"
        ),
    )

    secondary[1].metric(
        "Take Profit",
        (
            str(result.get("tp"))
            if result.get("tp") is not None
            else "No detectado"
        ),
    )

    secondary[2].metric(
        "Timeframe",
        result.get("timeframe")
        or "No detectado",
    )


# =========================================================
# GUARDAR EN SUPABASE
# =========================================================


def _save_trade(
    trade_data: dict[str, Any],
) -> dict[str, Any]:

    response = save_trade_rpc(
        trade_data
    )

    if not isinstance(
        response,
        dict,
    ):

        raise RuntimeError(
            "Supabase devolvió una respuesta inesperada."
        )

    return response


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================


def render_register_trade() -> None:

    _initialize_trade_state()
    _render_trade_styles()

    _render_trade_header()


    widget_defaults = {
        "trade_asset_widget": st.session_state.trade_asset,
        "trade_direction_widget": st.session_state.trade_direction,
        "trade_entry_widget": float(st.session_state.trade_entry),
        "trade_sl_widget": float(st.session_state.trade_sl),
        "trade_tp_widget": float(st.session_state.trade_tp),
        "trade_timeframe_widget": st.session_state.trade_timeframe,
    }

    for widget_key, widget_value in widget_defaults.items():
        if widget_key not in st.session_state:
            st.session_state[widget_key] = widget_value

    left, right = st.columns(
        [1.12, 1],
        gap="large",
    )

    # =====================================================
    # CAPTURAS
    # =====================================================

    with right:

        st.html('<div class="ax-form-section">🖼️ Capturas del setup</div>')

        image_before = st.file_uploader(
            "Captura ANTES de entrar",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            key="trade_image_before",
        )

        if image_before is not None:

            st.image(
                image_before,
                caption="SETUP ANTES",
                use_container_width=True,
            )

        _render_ai_scanner(
            image_before
        )

        image_after = st.file_uploader(
            "Captura DESPUÉS de cerrar",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            key="trade_image_after",
        )

        if image_after is not None:

            st.image(
                image_after,
                caption="RESULTADO",
                use_container_width=True,
            )

        pnl = st.number_input(
            "Ganancia / Pérdida ($)",
            value=0.0,
            step=10.0,
            format="%.2f",
            key="trade_pnl_widget",
        )

    # =====================================================
    # FORMULARIO
    # =====================================================

    with left:

        st.html('<div class="ax-form-section">📝 Datos de la operación</div>')

        _render_scan_result()

        fecha = st.date_input(
            "Fecha",
            value=datetime.date.today(),
            key="trade_date_widget",
        )

        asset_options = [
            "— Seleccionar activo —"
        ] + ASSETS

        current_asset = st.session_state.trade_asset

        asset_index = (
            asset_options.index(current_asset)
            if current_asset in asset_options
            else 0
        )

        asset = st.selectbox(
            "Activo / Par",
            asset_options,
            key="trade_asset_widget",
        )

        if asset.startswith("—"):
            asset = ""

        st.session_state.trade_asset = asset

        direction_options = [
            "LONG 🟢",
            "SHORT 🔴",
        ]

        current_direction = (
            st.session_state.trade_direction
            if st.session_state.trade_direction
            in direction_options
            else direction_options[0]
        )

        direction = st.radio(
            "Dirección",
            direction_options,
            horizontal=True,
            key="trade_direction_widget",
        )

        st.session_state.trade_direction = direction

        c1, c2 = st.columns(2)

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
                value=float(
                    st.session_state.trade_tp
                ),
                format="%.5f",
                key="trade_tp_widget",
            )

            current_timeframe = (
                st.session_state.trade_timeframe
                if st.session_state.trade_timeframe
                in TIMEFRAMES
                else ""
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

        rr = _calculate_rr(
            entry,
            stop_loss,
            take_profit,
        )

        st.metric(
            "Risk : Reward",
            f"1 : {rr:.2f}",
        )

        result = st.selectbox(
            "Resultado",
            RESULTS,
            index=RESULTS.index(
                st.session_state.trade_result
            ),
            key="trade_result_widget",
        )

        st.session_state.trade_result = result

        st.html('<div class="ax-form-section">🧠 Psicotrading</div>')

        emotion = st.selectbox(
            "Estado emocional",
            EMOTIONS,
            index=EMOTIONS.index(
                st.session_state.trade_emotion
            ),
            key="trade_emotion_widget",
        )

        notes = st.text_area(
            "Notas del trade",
            value=st.session_state.trade_notes,
            height=150,
            placeholder=(
                "¿Por qué entraste? ¿Respetaste tu plan? "
                "¿Qué sentiste antes, durante y después?"
            ),
            key="trade_notes_widget",
        )

        st.session_state.trade_emotion = emotion
        st.session_state.trade_notes = notes

        save_column, clear_column = st.columns(2)

        with save_column:

            save_button = st.button(
                "💾 GUARDAR TRADE",
                use_container_width=True,
                key="save_trade_button",
            )

        with clear_column:

            clear_button = st.button(
                "🧹 LIMPIAR",
                use_container_width=True,
                key="clear_trade_button",
            )

        if clear_button:

            _clear_trade_form()

            st.rerun()

        if save_button:

            validation_errors = []

            if not asset:
                validation_errors.append(
                    "Debes seleccionar un activo."
                )

            if entry <= 0:
                validation_errors.append(
                    "La entrada debe ser mayor que cero."
                )

            if stop_loss <= 0:
                validation_errors.append(
                    "El Stop Loss es obligatorio."
                )

            if take_profit <= 0:
                validation_errors.append(
                    "El Take Profit es obligatorio."
                )

            if not timeframe:
                validation_errors.append(
                    "Selecciona un timeframe."
                )

            if validation_errors:

                for error in validation_errors:
                    st.error(error)

            else:

                try:

                    with st.spinner(
                        "Guardando la operación en Supabase..."
                    ):

                        before_value = (
                            image_to_data_url(
                                image_before
                            )
                            if image_before
                            else ""
                        )

                        after_value = (
                            image_to_data_url(
                                image_after
                            )
                            if image_after
                            else ""
                        )

                        trade_data = {
                            "fecha": str(fecha),
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
                            "trades_cant": 1,
                            "img_before": before_value,
                            "img_after": after_value,
                        }

                        saved_trade = _save_trade(
                            trade_data
                        )

                    st.success(
                        "✅ Trade guardado correctamente "
                        "en Supabase."
                    )

                    st.session_state[
                        "last_saved_trade"
                    ] = saved_trade

                    _clear_trade_form()

                    st.session_state.page = (
                        "Track Record"
                    )

                    st.rerun()

                except Exception as exc:

                    st.error(
                        "❌ No se pudo guardar la operación."
                    )

                    st.error(
                        str(exc)
                    )

                    with st.expander(
                        "Ver datos enviados a Supabase"
                    ):

                        safe_preview = {
                            key: value
                            for key, value
                            in trade_data.items()
                            if key not in [
                                "img_before",
                                "img_after",
                            ]
                        }

                        st.json(
                            safe_preview
                        )
