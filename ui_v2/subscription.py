from __future__ import annotations

import datetime as dt
import html
import io
from typing import Any

import qrcode
import streamlit as st

from core.flow_payments import (
    FlowPaymentError,
    create_flow_plan_checkout,
    get_flow_plan_data,
)
from core.paddle_payments import (
    PaddlePaymentError,
    get_paddle_plan_data,
    render_paddle_checkout,
)
from ui_v2.theme import apply_v2_theme


# =========================================================
# AXION PRIME PRO
# SUSCRIPCIONES · TRIAL · FLOW · CRIPTO
# =========================================================


SUBSCRIPTION_CSS = """
<style>
.block-container {
    max-width: 1640px;
    padding-top: .7rem;
    padding-bottom: 1.5rem;
}

.ax-sub-root {
    position: relative;
    isolation: isolate;
}

.ax-sub-root::before {
    content: "";
    position: fixed;
    inset: 0 0 0 200px;
    z-index: -2;
    pointer-events: none;
    background:
        radial-gradient(circle at 83% 5%, rgba(137,75,255,.14), transparent 25%),
        radial-gradient(circle at 55% 48%, rgba(31,213,255,.06), transparent 30%),
        linear-gradient(180deg,#020713 0%,#050419 58%,#020711 100%);
}

.ax-sub-root::after {
    content: "";
    position: fixed;
    inset: 0 0 0 200px;
    z-index: -1;
    pointer-events: none;
    opacity: .15;
    background-image:
        linear-gradient(rgba(62,91,166,.05) 1px, transparent 1px),
        linear-gradient(90deg,rgba(62,91,166,.05) 1px, transparent 1px);
    background-size: 44px 44px;
}

/* =========================================================
   HERO COMPACTO
   ========================================================= */

.ax-top-hero {
    position: relative;
    overflow: hidden;
    padding: 24px 28px;
    margin-bottom: 14px;
    border: 1px solid rgba(75,93,217,.45);
    border-radius: 20px;
    background:
        radial-gradient(circle at 88% 0%,rgba(255,70,205,.12),transparent 28%),
        radial-gradient(circle at 70% 40%,rgba(42,216,255,.09),transparent 30%),
        linear-gradient(145deg,rgba(5,12,31,.99),rgba(6,7,25,.99));
    box-shadow:
        0 22px 65px rgba(0,0,0,.38),
        inset 0 1px 0 rgba(255,255,255,.04);
}

.ax-top-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background:
        linear-gradient(rgba(60,91,170,.035) 1px,transparent 1px),
        linear-gradient(90deg,rgba(60,91,170,.035) 1px,transparent 1px);
    background-size: 38px 38px;
}

.ax-top-copy {
    position: relative;
    z-index: 2;
}

.ax-kicker {
    color: #2bdcff;
    font-size: 10px;
    font-weight: 950;
    letter-spacing: 2px;
}

.ax-title {
    margin-top: 7px;
    color: #f4f7ff;
    font-size: clamp(34px,4vw,58px);
    line-height: .95;
    letter-spacing: -2.6px;
    font-weight: 950;
}

.ax-title span {
    color: transparent;
    background: linear-gradient(90deg,#2bdcff,#6d7cff,#c64cff);
    -webkit-background-clip: text;
    background-clip: text;
}

.ax-subtitle {
    margin-top: 9px;
    color: #bcc8df;
    font-size: 13px;
    line-height: 1.55;
}

/* =========================================================
   ELEGIR EXPERIENCIA
   ========================================================= */

.ax-choice-title {
    margin: 2px 0 12px;
    text-align: center;
}

.ax-choice-title strong {
    display: block;
    color: #f4f7ff;
    font-size: 28px;
    font-weight: 950;
}

.ax-choice-title strong span {
    color: transparent;
    background: linear-gradient(90deg,#2bdcff,#7d67ff,#d14dff);
    -webkit-background-clip: text;
    background-clip: text;
}

.ax-choice-title small {
    display: block;
    margin-top: 5px;
    color: #aebbd2;
    font-size: 12px;
}

.ax-choice-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 14px;
    margin-bottom: 14px;
}

.ax-choice-card {
    min-height: 112px;
    padding: 18px;
    border-radius: 16px;
    background:
        radial-gradient(circle at 100% 0%,rgba(var(--rgb),.14),transparent 38%),
        linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));
    border: 1px solid rgba(var(--rgb),.48);
    box-shadow: 0 16px 45px rgba(0,0,0,.25);
}

.ax-choice-card strong {
    display: block;
    color: #f2f6ff;
    font-size: 16px;
    font-weight: 950;
}

.ax-choice-card p {
    margin: 7px 0 0;
    color: #b7c3d9;
    font-size: 12px;
    line-height: 1.5;
}

.ax-choice-card span {
    display: inline-flex;
    margin-top: 10px;
    padding: 6px 9px;
    color: rgb(var(--rgb));
    font-size: 10px;
    font-weight: 950;
    border: 1px solid rgba(var(--rgb),.28);
    border-radius: 999px;
    background: rgba(var(--rgb),.07);
}

/* =========================================================
   ESTADO
   ========================================================= */

.ax-status-strip {
    display: grid;
    grid-template-columns: repeat(4,minmax(0,1fr));
    gap: 10px;
    margin-bottom: 14px;
}

.ax-status-box {
    padding: 13px;
    border: 1px solid rgba(71,99,166,.27);
    border-radius: 13px;
    background: rgba(6,12,29,.86);
}

.ax-status-box small {
    display: block;
    color: #8fa0bd;
    font-size: 9px;
    font-weight: 900;
    letter-spacing: .5px;
}

.ax-status-box strong {
    display: block;
    margin-top: 6px;
    color: #f3f6ff;
    font-size: 17px;
    font-weight: 950;
}

/* =========================================================
   COMPARACIÓN
   ========================================================= */

.ax-panel {
    margin-top: 14px;
    padding: 17px;
    border: 1px solid rgba(68,98,165,.30);
    border-radius: 16px;
    background:
        radial-gradient(circle at 100% 0%,rgba(39,216,255,.06),transparent 34%),
        linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));
}

.ax-panel-head {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 13px;
}

.ax-panel-head strong {
    color: #f0f4ff;
    font-size: 14px;
}

.ax-panel-head span {
    color: #8292af;
    font-size: 10px;
}

.ax-compare {
    width: 100%;
    border-collapse: collapse;
    color: #bdc8dd;
    font-size: 11px;
}

.ax-compare th,
.ax-compare td {
    padding: 10px 9px;
    text-align: left;
    border-bottom: 1px solid rgba(72,96,158,.15);
}

.ax-compare th {
    color: #eef4ff;
    font-size: 10px;
}

.ax-yes {
    color: #31ff9c;
    font-size: 15px;
    font-weight: 950;
}

.ax-no {
    color: #ff6688;
    font-size: 15px;
    font-weight: 950;
}

/* =========================================================
   PAGOS Y PLANES
   ========================================================= */

.ax-payment-strip {
    display: grid;
    grid-template-columns: .72fr 1.28fr;
    gap: 12px;
    align-items: center;
    margin-top: 14px;
    padding: 15px;
    border: 1px solid rgba(68,98,165,.30);
    border-radius: 15px;
    background: linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));
}

.ax-payment-copy strong {
    display: block;
    color: #f0f4ff;
    font-size: 13px;
}

.ax-payment-copy span {
    display: block;
    margin-top: 5px;
    color: #aebbd2;
    font-size: 10px;
    line-height: 1.45;
}

.ax-payment-icons {
    display: grid;
    grid-template-columns: repeat(6,minmax(0,1fr));
    gap: 8px;
}

.ax-pay-icon {
    padding: 10px 7px;
    text-align: center;
    color: rgb(var(--rgb));
    font-size: 11px;
    font-weight: 950;
    border: 1px solid rgba(var(--rgb),.30);
    border-radius: 10px;
    background: rgba(var(--rgb),.06);
}

.ax-plan-grid {
    display: grid;
    grid-template-columns: repeat(2,minmax(0,1fr));
    gap: 14px;
    margin-top: 14px;
}

.ax-plan {
    position: relative;
    padding: 20px;
    border: 1px solid rgba(var(--rgb),.50);
    border-radius: 18px;
    background:
        radial-gradient(circle at 100% 0%,rgba(var(--rgb),.14),transparent 38%),
        linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));
    box-shadow: 0 18px 48px rgba(0,0,0,.28);
}

.ax-plan.popular {
    border-color: rgba(255,196,0,.60);
}

.ax-plan-badge {
    position: absolute;
    right: 15px;
    top: 15px;
    padding: 5px 8px;
    color: #31ff9c;
    font-size: 9px;
    font-weight: 950;
    border: 1px solid rgba(49,255,156,.28);
    border-radius: 999px;
    background: rgba(49,255,156,.07);
}

.ax-plan-name {
    color: rgb(var(--rgb));
    font-size: 14px;
    font-weight: 950;
}

.ax-plan-price {
    margin-top: 8px;
    color: #f4f7ff;
    font-size: 42px;
    line-height: 1;
    letter-spacing: -1.5px;
    font-weight: 950;
}

.ax-plan-price span {
    color: #a9b5cc;
    font-size: 13px;
    letter-spacing: 0;
}

.ax-plan-note {
    margin-top: 7px;
    color: #b6c1d7;
    font-size: 11px;
}

.ax-plan-features {
    margin-top: 14px;
}

.ax-plan-feature {
    padding: 7px 0;
    color: #c2cce0;
    font-size: 11px;
    border-bottom: 1px solid rgba(72,96,158,.13);
}

.ax-plan-feature::before {
    content: "✓";
    margin-right: 8px;
    color: #31ff9c;
    font-weight: 950;
}

/* =========================================================
   CRIPTO
   ========================================================= */

.ax-crypto-panel {
    margin-top: 14px;
    padding: 18px;
    border: 1px solid rgba(106,82,255,.38);
    border-radius: 17px;
    background:
        radial-gradient(circle at 100% 0%,rgba(141,72,255,.13),transparent 35%),
        linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));
}

.ax-wallet-summary {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 9px;
    margin: 12px 0;
}

.ax-wallet-summary div {
    padding: 11px;
    border: 1px solid rgba(72,96,158,.22);
    border-radius: 11px;
    background: rgba(5,11,28,.86);
}

.ax-wallet-summary small {
    display: block;
    color: #8ea0bd;
    font-size: 9px;
    font-weight: 900;
}

.ax-wallet-summary strong {
    display: block;
    margin-top: 5px;
    color: #eef4ff;
    font-size: 12px;
}

/* =========================================================
   STREAMLIT
   ========================================================= */

.stButton > button[kind="primary"] {
    min-height: 52px;
    border: 1px solid rgba(126,102,255,.55) !important;
    border-radius: 13px !important;
    background: linear-gradient(90deg,#2bdcff,#4e72ff,#9e3dff,#ff46c8) !important;
    font-weight: 950 !important;
}

.stButton > button {
    min-height: 48px;
    border-radius: 12px !important;
}

@media (max-width: 1000px) {
    .ax-choice-grid,
    .ax-status-strip,
    .ax-plan-grid,
    .ax-payment-strip {
        grid-template-columns: 1fr;
    }

    .ax-payment-icons {
        grid-template-columns: repeat(3,minmax(0,1fr));
    }
}

@media (max-width: 700px) {
    .ax-payment-icons,
    .ax-wallet-summary {
        grid-template-columns: 1fr;
    }
}

/* =========================================================
   CONTRASTE STREAMLIT · SELECTORES · ALERTAS · FORMULARIOS
   ========================================================= */

.ax-sub-root,
.ax-sub-root p,
.ax-sub-root span,
.ax-sub-root div,
.ax-sub-root small,
.ax-sub-root strong,
.ax-sub-root label {
    opacity: 1 !important;
}

/* Etiquetas de widgets */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] div {
    color: #edf3ff !important;
    opacity: 1 !important;
}

/* Selectbox cerrado */
[data-baseweb="select"] > div,
[data-baseweb="select"] input,
[data-baseweb="select"] span,
[data-baseweb="select"] svg {
    color: #f4f7ff !important;
    -webkit-text-fill-color: #f4f7ff !important;
    opacity: 1 !important;
}

[data-baseweb="select"] > div {
    min-height: 48px;
    background:
        linear-gradient(
            145deg,
            rgba(7, 16, 37, .99),
            rgba(4, 10, 25, .99)
        ) !important;
    border:
        1px solid
        rgba(74, 110, 190, .48) !important;
    border-radius: 12px !important;
}

/* Menú desplegable */
[data-baseweb="popover"],
[data-baseweb="menu"],
[data-baseweb="menu"] ul,
[role="listbox"] {
    color: #f4f7ff !important;
    background: #071024 !important;
}

[data-baseweb="menu"] li,
[role="option"],
[role="option"] span,
[role="option"] div {
    color: #f4f7ff !important;
    -webkit-text-fill-color: #f4f7ff !important;
    background: #071024 !important;
    opacity: 1 !important;
}

[data-baseweb="menu"] li:hover,
[role="option"]:hover,
[aria-selected="true"][role="option"] {
    color: #ffffff !important;
    background: rgba(43, 220, 255, .13) !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    color: #f4f7ff !important;
    -webkit-text-fill-color: #f4f7ff !important;
    caret-color: #2bdcff !important;
    background:
        linear-gradient(
            145deg,
            rgba(7, 16, 37, .99),
            rgba(4, 10, 25, .99)
        ) !important;
    border:
        1px solid
        rgba(74, 110, 190, .46) !important;
    opacity: 1 !important;
}

[data-testid="stTextInput"] input::placeholder,
[data-testid="stTextArea"] textarea::placeholder {
    color: #8fa0bd !important;
    -webkit-text-fill-color: #8fa0bd !important;
    opacity: 1 !important;
}

/* Alertas */
[data-testid="stAlert"] {
    color: #eef4ff !important;
    background: rgba(7, 16, 37, .97) !important;
    border:
        1px solid
        rgba(75, 110, 190, .36) !important;
    border-radius: 13px !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div,
[data-testid="stAlert"] strong,
[data-testid="stAlert"] li {
    color: #eef4ff !important;
    opacity: 1 !important;
}

/* Captions, Markdown y código en esta pantalla */
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
.stCaption,
.stCaption * {
    color: #aebbd2 !important;
    opacity: 1 !important;
}

[data-testid="stCodeBlock"] {
    color: #edf6ff !important;
    background: #030916 !important;
    border:
        1px solid
        rgba(43, 220, 255, .25) !important;
    border-radius: 12px !important;
}

[data-testid="stCodeBlock"] code,
[data-testid="stCodeBlock"] pre,
[data-testid="stCodeBlock"] span {
    color: #edf6ff !important;
    opacity: 1 !important;
}

/* Panel Binance Pay */
.ax-binance-panel {
    margin-top: 14px;
    padding: 18px;
    border:
        1px solid
        rgba(255, 196, 0, .46);
    border-radius: 17px;
    background:
        radial-gradient(
            circle at 100% 0%,
            rgba(255, 196, 0, .12),
            transparent 36%
        ),
        linear-gradient(
            145deg,
            rgba(8, 16, 35, .99),
            rgba(5, 9, 24, .99)
        );
}

.ax-binance-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
}

.ax-binance-head strong {
    color: #ffc400;
    font-size: 15px;
    font-weight: 950;
}

.ax-binance-head span {
    color: #f4f7ff;
    font-size: 11px;
    font-weight: 900;
}

.ax-binance-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 9px;
    margin-top: 13px;
}

.ax-binance-grid div {
    padding: 11px;
    border:
        1px solid
        rgba(255, 196, 0, .22);
    border-radius: 11px;
    background: rgba(5, 11, 28, .86);
}

.ax-binance-grid small {
    display: block;
    color: #9eabc2;
    font-size: 9px;
    font-weight: 900;
}

.ax-binance-grid strong {
    display: block;
    margin-top: 5px;
    color: #f4f7ff;
    font-size: 12px;
    overflow-wrap: anywhere;
}

.ax-binance-instructions {
    margin-top: 13px;
    padding: 13px;
    color: #d5def0;
    font-size: 11px;
    line-height: 1.6;
    border-left: 3px solid #ffc400;
    border-radius: 5px 11px 11px 5px;
    background: rgba(255, 196, 0, .055);
}

@media (max-width: 700px) {
    .ax-binance-grid {
        grid-template-columns: 1fr;
    }
}


/* FLOW · WEBPAY · VISA · MASTERCARD */
.ax-flow-panel {
    margin-top: 14px;
    padding: 18px;
    border: 1px solid rgba(43,220,255,.48);
    border-radius: 17px;
    background:
        radial-gradient(circle at 100% 0%,rgba(43,220,255,.14),transparent 36%),
        linear-gradient(145deg,rgba(7,16,37,.99),rgba(5,9,24,.99));
}
.ax-flow-head {
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
    flex-wrap:wrap;
}
.ax-flow-head strong { color:#2bdcff; font-size:15px; font-weight:950; }
.ax-flow-head span { color:#f4f7ff; font-size:11px; font-weight:900; }
.ax-flow-grid {
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:9px;
    margin-top:13px;
}
.ax-flow-grid div {
    padding:11px;
    border:1px solid rgba(43,220,255,.22);
    border-radius:11px;
    background:rgba(5,11,28,.86);
}
.ax-flow-grid small {
    display:block;
    color:#9eabc2;
    font-size:9px;
    font-weight:900;
}
.ax-flow-grid strong {
    display:block;
    margin-top:5px;
    color:#f4f7ff;
    font-size:12px;
    overflow-wrap:anywhere;
}
.ax-flow-note {
    margin-top:13px;
    padding:13px;
    color:#d5def0;
    font-size:11px;
    line-height:1.6;
    border-left:3px solid #2bdcff;
    border-radius:5px 11px 11px 5px;
    background:rgba(43,220,255,.06);
}
.ax-flow-secure {
    display:inline-flex;
    margin-top:12px;
    padding:7px 10px;
    color:#31ff9c;
    font-size:10px;
    font-weight:900;
    border:1px solid rgba(49,255,156,.24);
    border-radius:999px;
    background:rgba(49,255,156,.055);
}
@media (max-width:700px) {
    .ax-flow-grid { grid-template-columns:1fr; }
}

</style>
"""


# =========================================================
# HELPERS
# =========================================================


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value

    try:
        dumped = value.model_dump()
        return dumped if isinstance(dumped, dict) else {}
    except Exception:
        return {}


def _secret(name: str, default: str = "") -> str:
    try:
        return str(
            st.secrets.get(name, default)
            or default
        ).strip()
    except Exception:
        return default


def _is_owner() -> bool:
    user = _safe_dict(
        st.session_state.get("user", {})
    )

    email = str(
        user.get("email", "")
        or ""
    ).strip().lower()

    admin_email = _secret(
        "ADMIN_EMAIL",
    ).lower()

    return bool(
        admin_email
        and email == admin_email
    )


def _parse_date(value: Any) -> dt.datetime | None:
    if not value:
        return None

    try:
        if isinstance(value, dt.datetime):
            parsed = value
        else:
            parsed = dt.datetime.fromisoformat(
                str(value).replace("Z", "+00:00")
            )
    except (TypeError, ValueError):
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=dt.timezone.utc,
        )

    return parsed.astimezone(
        dt.timezone.utc,
    )


def _membership_information() -> dict[str, Any]:
    now = dt.datetime.now(
        dt.timezone.utc,
    )

    if _is_owner():
        return {
            "plan": "FOUNDER",
            "status": "ACTIVO",
            "days_remaining": None,
            "end": None,
            "is_owner": True,
        }

    user = _safe_dict(
        st.session_state.get("user", {})
    )

    metadata = _safe_dict(
        user.get("user_metadata", {})
    )

    stored_plan = str(
        metadata.get("plan", "")
        or ""
    ).strip().upper()

    if stored_plan in {
        "PRO",
        "PRO_MONTHLY",
        "PRO_ANNUAL",
    }:
        return {
            "plan": stored_plan,
            "status": "ACTIVO",
            "days_remaining": None,
            "end": None,
            "is_owner": False,
        }

    created_at = (
        user.get("created_at")
        or metadata.get("trial_started_at")
        or st.session_state.get("trial_started_at")
    )

    start = _parse_date(
        created_at,
    )

    if start is None:
        start = now
        st.session_state.trial_started_at = (
            start.isoformat()
        )

    end = start + dt.timedelta(
        days=7,
    )

    remaining_seconds = max(
        0,
        int(
            (end - now).total_seconds()
        ),
    )

    days_remaining = max(
        0,
        int(
            (remaining_seconds + 86399)
            // 86400
        ),
    )

    return {
        "plan": "TRIAL",
        "status": (
            "ACTIVO"
            if remaining_seconds > 0
            else "FINALIZADO"
        ),
        "days_remaining": days_remaining,
        "end": end,
        "is_owner": False,
    }


def _wallets() -> dict[str, dict[str, str]]:
    return {
        "Bitcoin BEP20": {
            "symbol": "BTC",
            "network": "BNB Smart Chain · BEP20",
            "address": (
                _secret("BTC_BEP20_WALLET_ADDRESS")
                or _secret("BTC_WALLET_ADDRESS")
            ),
        },
        "Ethereum BEP20": {
            "symbol": "ETH",
            "network": "BNB Smart Chain · BEP20",
            "address": (
                _secret("ETH_BEP20_WALLET_ADDRESS")
                or _secret("ETH_WALLET_ADDRESS")
            ),
        },
        "USDT TRC20": {
            "symbol": "USDT",
            "network": "TRON · TRC20",
            "address": _secret(
                "USDT_TRC20_WALLET_ADDRESS",
            ),
        },
    }


def _make_qr(value: str) -> bytes:
    qr = qrcode.QRCode(
        version=None,
        error_correction=(
            qrcode.constants.ERROR_CORRECT_M
        ),
        box_size=8,
        border=3,
    )

    qr.add_data(
        value,
    )

    qr.make(
        fit=True,
    )

    image = qr.make_image(
        fill_color="black",
        back_color="white",
    )

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG",
    )

    return buffer.getvalue()


def _select_checkout(
    plan_code: str,
    plan_label: str,
    clp_amount: int,
    usd_amount: int,
) -> None:
    """
    Guarda por separado el precio para Chile y el precio internacional.
    """

    st.session_state.subscription_checkout = {
        "plan_code": str(plan_code or "").strip().upper(),
        "plan_label": str(plan_label or "AXION PRIME PRO").strip(),
        "clp_amount": int(clp_amount or 0),
        "usd_amount": int(usd_amount or 0),
    }



def _first_secret(
    *names: str,
) -> tuple[str, str]:
    """
    Devuelve el primer secreto configurado junto a su nombre.

    No imprime ni expone claves privadas.
    """

    for name in names:
        value = _secret(
            name,
        )

        if value:
            return name, value

    return "", ""


def _binance_payment_information() -> dict[str, str]:
    """
    Obtiene la información pública disponible para Binance Pay.

    Este flujo es manual: registra una referencia de pago para
    revisión. No afirma verificar ni activar automáticamente
    una orden sin credenciales comerciales y webhook.
    """

    identifier_name, identifier = _first_secret(
        "BINANCE_PAY_ID",
        "BINANCE_PAY_EMAIL",
        "BINANCE_PAY_PHONE",
        "BINANCE_PAY_MERCHANT_ID",
    )

    payment_link = _secret(
        "BINANCE_PAY_LINK",
    )

    display_labels = {
        "BINANCE_PAY_ID": "PAY ID",
        "BINANCE_PAY_EMAIL": "CORREO BINANCE",
        "BINANCE_PAY_PHONE": "TELÉFONO BINANCE",
        "BINANCE_PAY_MERCHANT_ID": "MERCHANT ID",
    }

    return {
        "identifier_name": identifier_name,
        "identifier_label": display_labels.get(
            identifier_name,
            "IDENTIFICADOR",
        ),
        "identifier": identifier,
        "payment_link": payment_link,
    }


def _render_binance_checkout(
    *,
    checkout: dict[str, Any],
    plan_label: str,
    amount: int,
) -> None:
    """
    Renderiza un pago manual con Binance Pay.

    El usuario paga desde Binance y envía una referencia,
    Order ID o comprobante para revisión administrativa.
    """

    information = _binance_payment_information()

    identifier = information[
        "identifier"
    ]

    identifier_label = information[
        "identifier_label"
    ]

    payment_link = information[
        "payment_link"
    ]

    if not identifier and not payment_link:
        st.warning(
            "Binance Pay todavía no está configurado. "
            "Añade BINANCE_PAY_ID o BINANCE_PAY_LINK en "
            "Streamlit Secrets."
        )

        st.code(
            (
                'BINANCE_PAY_ID = "TU_PAY_ID"\n'
                'BINANCE_PAY_LINK = "https://..."'
            ),
            language="toml",
        )

        return

    safe_identifier = html.escape(
        identifier,
    )

    st.html(
        f"""
        <section class="ax-binance-panel">
            <div class="ax-binance-head">
                <strong>◈ BINANCE PAY · VERIFICACIÓN MANUAL</strong>
                <span>IMPORTE EXACTO: US${amount}</span>
            </div>

            <div class="ax-binance-grid">
                <div>
                    <small>PLAN</small>
                    <strong>{html.escape(plan_label)}</strong>
                </div>

                <div>
                    <small>IMPORTE</small>
                    <strong>US${amount}</strong>
                </div>

                <div>
                    <small>{html.escape(identifier_label)}</small>
                    <strong>
                        {safe_identifier if identifier else "ABRIR ENLACE DE PAGO"}
                    </strong>
                </div>
            </div>

            <div class="ax-binance-instructions">
                1. Abre Binance y entra en Binance Pay.<br>
                2. Envía exactamente US${amount} al identificador mostrado
                o utiliza el enlace de cobro.<br>
                3. Copia el Order ID, referencia o identificador de la
                operación.<br>
                4. Envíalo abajo para revisión. El plan no se activa hasta
                confirmar el pago.
            </div>
        </section>
        """
    )

    qr_value = (
        payment_link
        or identifier
    )

    qr_column, details_column = st.columns(
        [
            .34,
            .66,
        ],
        gap="medium",
    )

    with qr_column:
        if qr_value:
            st.image(
                _make_qr(
                    qr_value,
                ),
                caption="Binance Pay",
                width=220,
            )

    with details_column:
        if identifier:
            st.markdown(
                f"### {identifier_label}"
            )

            st.code(
                identifier,
                language=None,
            )

        if payment_link:
            st.link_button(
                "🟡 ABRIR BINANCE PAY",
                payment_link,
                use_container_width=True,
            )

        payer_email = st.text_input(
            "Correo del pagador",
            placeholder="correo usado en Binance",
            key=(
                "subscription_binance_email_"
                f"{checkout.get('plan_code', 'plan')}"
            ),
        )

        payment_reference = st.text_input(
            "Order ID o referencia del pago",
            placeholder="Pega aquí la referencia de Binance Pay",
            key=(
                "subscription_binance_reference_"
                f"{checkout.get('plan_code', 'plan')}"
            ),
        )

        if st.button(
            "📨 ENVIAR BINANCE PAY PARA VERIFICACIÓN",
            use_container_width=True,
            type="primary",
            key=(
                "subscription_binance_verify_"
                f"{checkout.get('plan_code', 'plan')}"
            ),
        ):
            clean_reference = payment_reference.strip()

            if not clean_reference:
                st.warning(
                    "Debes escribir el Order ID o la referencia "
                    "del pago antes de enviarlo."
                )
                return

            st.session_state.pending_binance_payment = {
                "plan_code": checkout.get(
                    "plan_code",
                ),
                "plan_label": plan_label,
                "usd_amount": amount,
                "payment_method": "Binance Pay",
                "payer_email": payer_email.strip(),
                "reference": clean_reference,
                "merchant_identifier": identifier,
                "status": "pending_manual_review",
                "submitted_at": dt.datetime.now(
                    dt.timezone.utc,
                ).isoformat(),
            }

            st.success(
                "Pago enviado para revisión. Tu acceso PRO se "
                "activará después de confirmar la operación."
            )


def _checkout_cache_key(plan_code: str) -> str:
    """
    Clave de sesión para conservar el checkout de Flow.
    """

    return (
        "flow_checkout_"
        f"{str(plan_code or '').strip().upper()}"
    )


def _clear_other_flow_checkouts(
    current_plan_code: str,
) -> None:
    """
    Elimina checkouts anteriores de otros planes.
    """

    current_key = _checkout_cache_key(
        current_plan_code
    )

    for key in list(
        st.session_state.keys()
    ):
        if (
            str(key).startswith(
                "flow_checkout_"
            )
            and key != current_key
        ):
            st.session_state.pop(
                key,
                None,
            )


def _render_payment_return_status() -> None:
    """
    Muestra el retorno visual después de volver desde Flow.

    La activación real no depende de esta URL. El webhook
    flow-webhook consultará directamente el estado en Flow.
    """

    try:
        provider = str(
            st.query_params.get(
                "provider",
                "",
            )
            or ""
        ).strip().lower()

        commerce_order = str(
            st.query_params.get(
                "commerce_order",
                "",
            )
            or ""
        ).strip()

        token = str(
            st.query_params.get(
                "token",
                "",
            )
            or ""
        ).strip()

    except Exception:
        return

    if provider != "flow":
        return

    if token:
        st.success(
            "Flow recibió el proceso de pago. "
            "Estamos verificando la operación antes de activar PRO."
        )

    elif commerce_order:
        st.info(
            "Regresaste desde Flow. La membresía se activará "
            "cuando el webhook confirme que el pago fue aprobado."
        )


def _render_flow_checkout(
    *,
    checkout: dict[str, Any],
) -> None:
    """
    Genera y muestra el checkout externo de Flow.

    Flow procesará Webpay, Visa, Mastercard y los demás
    medios activos en la cuenta del comercio.
    """

    plan_code = str(
        checkout.get(
            "plan_code",
            "",
        )
        or ""
    ).strip().upper()

    if not plan_code:
        st.error(
            "No se pudo identificar el plan."
        )
        return

    try:
        plan = get_flow_plan_data(
            plan_code
        )

    except FlowPaymentError as exc:
        st.error(
            str(exc)
        )
        return

    local_amount = float(
        plan["amount"]
    )

    currency = str(
        plan["currency"]
    )

    plan_label = str(
        plan["plan_label"]
    )

    st.html(
        f"""
        <section class="ax-flow-panel">
            <div class="ax-flow-head">
                <strong>💳 FLOW · WEBPAY · VISA · MASTERCARD</strong>
                <span>{html.escape(currency)} {local_amount:,.0f}</span>
            </div>

            <div class="ax-flow-grid">
                <div>
                    <small>PLAN</small>
                    <strong>{html.escape(plan_label)}</strong>
                </div>

                <div>
                    <small>IMPORTE LOCAL</small>
                    <strong>{html.escape(currency)} {local_amount:,.0f}</strong>
                </div>

                <div>
                    <small>ACTIVACIÓN</small>
                    <strong>AUTOMÁTICA</strong>
                </div>
            </div>

            <div class="ax-flow-note">
                El pago se completa en el checkout protegido de Flow.
                Allí estarán disponibles Webpay, Visa, Mastercard y
                los demás medios habilitados en tu cuenta. AXION PRIME
                no almacena datos de tarjetas.
            </div>

            <div class="ax-flow-secure">
                🔒 CHECKOUT EXTERNO Y PROTEGIDO
            </div>
        </section>
        """
    )

    cache_key = _checkout_cache_key(
        plan_code
    )

    flow_checkout = st.session_state.get(
        cache_key,
        {},
    )

    if not isinstance(
        flow_checkout,
        dict,
    ):
        flow_checkout = {}

    if st.button(
        "🔗 GENERAR CHECKOUT FLOW",
        use_container_width=True,
        type="primary",
        key=(
            "subscription_create_flow_"
            f"{plan_code}"
        ),
    ):
        try:
            with st.spinner(
                "Conectando con Flow..."
            ):
                created = create_flow_plan_checkout(
                    plan_code
                )

            flow_checkout = {
                "token": created.token,
                "flow_order": created.flow_order,
                "commerce_order": created.commerce_order,
                "checkout_url": created.checkout_url,
                "plan_code": created.plan_code,
                "amount": created.amount,
                "currency": created.currency,
                "created_at": dt.datetime.now(
                    dt.timezone.utc
                ).isoformat(),
            }

            _clear_other_flow_checkouts(
                plan_code
            )

            st.session_state[
                cache_key
            ] = flow_checkout

            st.success(
                "Checkout de Flow generado correctamente."
            )

        except FlowPaymentError as exc:
            st.error(
                str(exc)
            )
            return

        except Exception as exc:
            st.error(
                "No se pudo crear el checkout de Flow."
            )

            with st.expander(
                "Ver detalle técnico",
                expanded=False,
            ):
                st.code(
                    str(exc),
                    language="text",
                )

            return

    checkout_url = str(
        flow_checkout.get(
            "checkout_url",
            "",
        )
        or ""
    ).strip()

    if checkout_url:
        st.link_button(
            "🚀 IR A FLOW Y PAGAR",
            checkout_url,
            use_container_width=True,
            type="primary",
        )

        st.caption(
            "La cuenta PRO se activará automáticamente cuando "
            "Flow confirme el pago mediante el webhook."
        )

def _render_paddle_checkout(
    *,
    checkout: dict[str, Any],
) -> None:
    """Muestra Paddle Checkout para clientes internacionales."""

    plan_code = str(
        checkout.get("plan_code", "") or ""
    ).strip().upper()

    try:
        plan = get_paddle_plan_data(plan_code)
    except PaddlePaymentError as exc:
        st.error(str(exc))
        return

    st.html(
        f"""
        <section class="ax-flow-panel">
            <div class="ax-flow-head">
                <strong>🌎 PADDLE · PAGOS INTERNACIONALES</strong>
                <span>{html.escape(plan['currency'])} {plan['amount']}</span>
            </div>
            <div class="ax-flow-grid">
                <div><small>PLAN</small><strong>{html.escape(plan['plan_label'])}</strong></div>
                <div><small>IMPORTE</small><strong>USD {plan['amount']}</strong></div>
                <div><small>ACTIVACIÓN</small><strong>AUTOMÁTICA</strong></div>
            </div>
            <div class="ax-flow-note">
                Recomendado para clientes fuera de Chile. Paddle acepta
                tarjetas internacionales, administra impuestos y envía la
                confirmación al webhook de AXION PRIME.
            </div>
            <div class="ax-flow-secure">🔒 CHECKOUT INTERNACIONAL PROTEGIDO</div>
        </section>
        """
    )

    try:
        render_paddle_checkout(plan_code)
    except PaddlePaymentError as exc:
        st.error(str(exc))


# =========================================================
# CHECKOUT
# =========================================================


def _render_checkout(
    *,
    is_owner: bool,
) -> None:
    checkout = st.session_state.get(
        "subscription_checkout",
    )

    if not isinstance(checkout, dict):
        return

    if is_owner:
        st.success(
            "👑 Tu cuenta FOUNDER ya tiene acceso "
            "total de por vida."
        )
        return

    plan_label = str(
        checkout.get(
            "plan_label",
            "AXION PRIME PRO",
        )
    )

    clp_amount = int(
        checkout.get(
            "clp_amount",
            0,
        )
        or 0
    )

    usd_amount = int(
        checkout.get(
            "usd_amount",
            0,
        )
        or 0
    )

    formatted_clp = (
        f"{clp_amount:,}"
        .replace(",", ".")
    )

    st.html(
        f"""
        <section class="ax-crypto-panel">
            <div class="ax-panel-head">
                <strong>COMPLETAR PAGO · {html.escape(plan_label)}</strong>
                <span>ELIGE TU PAÍS Y MÉTODO DE PAGO</span>
            </div>

            <div class="ax-wallet-summary">
                <div>
                    <small>PLAN SELECCIONADO</small>
                    <strong>{html.escape(plan_label)}</strong>
                </div>

                <div>
                    <small>PRECIO CHILE</small>
                    <strong>CLP {formatted_clp}</strong>
                </div>

                <div>
                    <small>PRECIO INTERNACIONAL</small>
                    <strong>USD {usd_amount}</strong>
                </div>
            </div>
        </section>
        """
    )

    payment_method = st.selectbox(
        "Elige cómo quieres pagar",
        options=[
            "Chile · Flow / Webpay",
            "Internacional · Paddle / Visa / Mastercard",
            "Binance Pay",
            "Bitcoin BEP20",
            "Ethereum BEP20",
            "USDT TRC20",
        ],
        key=f"subscription_payment_method_{checkout.get('plan_code', 'plan')}",
    )

    if payment_method == "Chile · Flow / Webpay":
        _render_flow_checkout(
            checkout=checkout,
        )
        return

    if payment_method == "Internacional · Paddle / Visa / Mastercard":
        _render_paddle_checkout(
            checkout=checkout,
        )
        return

    if payment_method == "Binance Pay":
        _render_binance_checkout(
            checkout=checkout,
            plan_label=plan_label,
            amount=usd_amount,
        )
        return

    wallets = _wallets()

    if payment_method not in wallets:
        st.error(
            "El método de pago seleccionado no está disponible."
        )
        return

    selected = wallets[
        payment_method
    ]

    address = selected[
        "address"
    ]

    st.html(
        f"""
        <div class="ax-wallet-summary">
            <div>
                <small>MONEDA</small>
                <strong>{html.escape(selected["symbol"])}</strong>
            </div>

            <div>
                <small>RED OBLIGATORIA</small>
                <strong>{html.escape(selected["network"])}</strong>
            </div>

            <div>
                <small>IMPORTE DEL PLAN</small>
                <strong>USD {usd_amount}</strong>
            </div>
        </div>
        """
    )

    if not address:
        st.warning(
            "La dirección pública todavía no está configurada "
            "en Streamlit Secrets."
        )

        st.code(
            (
                'BTC_BEP20_WALLET_ADDRESS = "..."\n'
                'ETH_BEP20_WALLET_ADDRESS = "..."\n'
                'USDT_TRC20_WALLET_ADDRESS = "..."'
            ),
            language="toml",
        )

        return

    qr_column, information_column = st.columns(
        [
            .33,
            .67,
        ],
        gap="medium",
    )

    with qr_column:
        st.image(
            _make_qr(
                address,
            ),
            caption=(
                f'{selected["symbol"]} · '
                f'{selected["network"]}'
            ),
            width=220,
        )

    with information_column:
        st.markdown(
            f"### Dirección de pago {selected['symbol']}"
        )

        st.code(
            address,
            language=None,
        )

        st.error(
            f"Envía únicamente {selected['symbol']} por la red "
            f"{selected['network']}. Usar otra red puede causar "
            "pérdida de fondos."
        )

        st.caption(
            "Para BTC y ETH se debe calcular la cantidad exacta "
            "con la cotización vigente al momento del pago. "
            "La activación automática se conectará mediante "
            "verificación blockchain o proveedor de pagos."
        )

        transaction_hash = st.text_input(
            "Hash de la transacción (TXID)",
            placeholder="Pega aquí el TXID después del pago",
            key=(
                "subscription_txid_"
                f'{selected["symbol"]}_'
                f'{checkout.get("plan_code", "plan")}'
            ),
        )

        if st.button(
            "📨 ENVIAR PAGO PARA VERIFICACIÓN",
            use_container_width=True,
            key=(
                "subscription_verify_"
                f'{selected["symbol"]}_'
                f'{checkout.get("plan_code", "plan")}'
            ),
        ):
            if not transaction_hash.strip():
                st.warning(
                    "Debes pegar el TXID antes de enviar."
                )
                return

            st.session_state.pending_crypto_payment = {
                "plan_code": checkout.get(
                    "plan_code",
                ),
                "plan_label": plan_label,
                "usd_amount": usd_amount,
                "currency": selected[
                    "symbol"
                ],
                "network": selected[
                    "network"
                ],
                "wallet_address": address,
                "txid": transaction_hash.strip(),
                "status": "pending_manual_review",
                "submitted_at": dt.datetime.now(
                    dt.timezone.utc,
                ).isoformat(),
            }

            st.success(
                "Solicitud enviada. El acceso PRO no se activará "
                "hasta verificar la transacción."
            )


# =========================================================
# RENDER PRINCIPAL
# =========================================================


def render_subscription() -> None:
    apply_v2_theme()

    st.html(
        SUBSCRIPTION_CSS
    )

    _render_payment_return_status()

    membership = _membership_information()

    is_owner = bool(
        membership["is_owner"]
    )

    if is_owner:
        status_text = "FOUNDER"
        time_text = "LIFETIME"
        access_text = "ILIMITADO"

    elif membership["plan"] != "TRIAL":
        status_text = membership["plan"]
        time_text = "ACTIVO"
        access_text = "PRO"

    else:
        status_text = "TRIAL"
        time_text = (
            f'{membership["days_remaining"]} DÍAS'
        )
        access_text = (
            "COMPLETO"
            if membership["status"] == "ACTIVO"
            else "FINALIZADO"
        )

    st.html(
        f"""
        <div class="ax-sub-root">
            <section class="ax-top-hero">
                <div class="ax-top-copy">
                    <div class="ax-kicker">
                        AXION PRIME · MEMBERSHIP OS
                    </div>

                    <div class="ax-title">
                        Elige tu <span>experiencia</span>
                    </div>

                    <div class="ax-subtitle">
                        Comienza con 7 días de prueba o elige un plan
                        para acceder de inmediato. No es obligatorio
                        esperar a que termine el trial.
                    </div>
                </div>
            </section>

            <div class="ax-choice-title">
                <strong>
                    Empieza gratis o <span>activa PRO ahora</span>
                </strong>

                <small>
                    Tú decides cómo comenzar.
                </small>
            </div>

            <div class="ax-choice-grid">
                <article class="ax-choice-card" style="--rgb:43,220,255">
                    <strong>🎁 PRUEBA GRATUITA · 7 DÍAS</strong>
                    <p>
                        Acceso completo durante el periodo de prueba,
                        sin necesidad de pagar al registrarte.
                    </p>
                    <span>COMENZAR GRATIS</span>
                </article>

                <article class="ax-choice-card" style="--rgb:255,196,0">
                    <strong>⚡ ACCESO PRO INMEDIATO</strong>
                    <p>
                        Elige el plan mensual o anual y abre el
                        checkout sin esperar a que termine tu prueba.
                    </p>
                    <span>PAGAR AHORA</span>
                </article>
            </div>

            <div class="ax-status-strip">
                <div class="ax-status-box">
                    <small>PLAN ACTUAL</small>
                    <strong>{html.escape(status_text)}</strong>
                </div>

                <div class="ax-status-box">
                    <small>TIEMPO / ESTADO</small>
                    <strong>{html.escape(time_text)}</strong>
                </div>

                <div class="ax-status-box">
                    <small>NIVEL DE ACCESO</small>
                    <strong>{html.escape(access_text)}</strong>
                </div>

                <div class="ax-status-box">
                    <small>CUENTA</small>
                    <strong>
                        {'PROPIETARIO' if is_owner else 'TRADER'}
                    </strong>
                </div>
            </div>
        </div>
        """
    )

    trial_column, immediate_column = st.columns(
        2,
        gap="medium",
    )

    with trial_column:
        if st.button(
            "🎁 CONTINUAR CON MI PRUEBA GRATIS",
            use_container_width=True,
            key="subscription_continue_trial",
            disabled=(
                is_owner
                or membership["plan"] != "TRIAL"
            ),
        ):
            st.session_state.pop(
                "subscription_checkout",
                None,
            )

            st.success(
                "Tu prueba gratuita continúa activa. "
                "Puedes pagar en cualquier momento."
            )

    with immediate_column:
        if st.button(
            "⚡ QUIERO ACTIVAR PRO AHORA",
            use_container_width=True,
            type="primary",
            key="subscription_immediate_access",
            disabled=is_owner,
        ):
            st.session_state.subscription_show_plans = True

    st.html(
        """
        <section class="ax-panel">
            <div class="ax-panel-head">
                <strong>COMPARACIÓN DE ACCESO</strong>
                <span>TRIAL VS PRO</span>
            </div>

            <table class="ax-compare">
                <thead>
                    <tr>
                        <th>FUNCIÓN</th>
                        <th>TRIAL 7 DÍAS</th>
                        <th>AXION PRIME PRO</th>
                    </tr>
                </thead>

                <tbody>
                    <tr>
                        <td>📊 Dashboard completo</td>
                        <td class="ax-yes">✓</td>
                        <td class="ax-yes">✓</td>
                    </tr>

                    <tr>
                        <td>🤖 Chat IA</td>
                        <td class="ax-yes">✓</td>
                        <td class="ax-yes">✓</td>
                    </tr>

                    <tr>
                        <td>👁 AXION Vision</td>
                        <td class="ax-yes">✓</td>
                        <td class="ax-yes">✓</td>
                    </tr>

                    <tr>
                        <td>📈 Track Record y Psicotrading</td>
                        <td class="ax-yes">✓</td>
                        <td class="ax-yes">✓</td>
                    </tr>

                    <tr>
                        <td>🔒 Acceso después del trial</td>
                        <td class="ax-no">✕</td>
                        <td class="ax-yes">✓</td>
                    </tr>

                    <tr>
                        <td>⭐ Actualizaciones premium</td>
                        <td class="ax-no">✕</td>
                        <td class="ax-yes">✓</td>
                    </tr>
                </tbody>
            </table>
        </section>

        <section class="ax-payment-strip">
            <div class="ax-payment-copy">
                <strong>🛡 PAGOS PROTEGIDOS</strong>
                <span>
                    Los cobros se procesarán mediante proveedores
                    externos. AXION PRIME no debe almacenar directamente
                    los datos de las tarjetas.
                </span>
            </div>

            <div class="ax-payment-icons">
                <div class="ax-pay-icon" style="--rgb:43,220,255">VISA</div>
                <div class="ax-pay-icon" style="--rgb:255,142,48">MASTERCARD</div>
                <div class="ax-pay-icon" style="--rgb:63,188,255">WEBPAY</div>
                <div class="ax-pay-icon" style="--rgb:122,84,255">PADDLE</div>
                <div class="ax-pay-icon" style="--rgb:255,196,0">BINANCE PAY</div>
                <div class="ax-pay-icon" style="--rgb:247,147,26">BTC</div>
                <div class="ax-pay-icon" style="--rgb:38,161,123">USDT</div>
            </div>
        </section>

        <div class="ax-plan-grid">
            <article class="ax-plan" style="--rgb:43,220,255">
                <div class="ax-plan-name">PLAN MENSUAL</div>
                <div class="ax-plan-price">CLP 3.000 <span>/ mes · Chile</span></div>
                <div class="ax-plan-note">Internacional: USD 6 / mes mediante Paddle.</div>
                <div class="ax-plan-note">
                    Flexibilidad mensual y acceso inmediato.
                </div>

                <div class="ax-plan-features">
                    <div class="ax-plan-feature">Acceso a todas las funciones PRO</div>
                    <div class="ax-plan-feature">Renovación mensual</div>
                    <div class="ax-plan-feature">Actualizaciones incluidas</div>
                    <div class="ax-plan-feature">Gestión del plan</div>
                </div>
            </article>

            <article class="ax-plan popular" style="--rgb:255,196,0">
                <div class="ax-plan-badge">MEJOR PRECIO ANUAL</div>
                <div class="ax-plan-name">PLAN ANUAL</div>
                <div class="ax-plan-price">CLP 20.000 <span>/ año · Chile</span></div>
                <div class="ax-plan-note">Internacional: USD 40 / año mediante Paddle.</div>
                <div class="ax-plan-note">
                    Equivale aproximadamente a CLP 1.667 por mes.
                </div>

                <div class="ax-plan-features">
                    <div class="ax-plan-feature">Acceso a todas las funciones PRO</div>
                    <div class="ax-plan-feature">Doce meses de acceso</div>
                    <div class="ax-plan-feature">Actualizaciones incluidas</div>
                    <div class="ax-plan-feature">Mejor precio anual</div>
                </div>
            </article>
        </div>
        """
    )

    monthly_column, annual_column = st.columns(
        2,
        gap="medium",
    )

    with monthly_column:
        if st.button(
            "💳 PAGAR AHORA · CLP 3.000 / MES",
            use_container_width=True,
            type="primary",
            key="subscription_monthly_checkout",
            disabled=is_owner,
        ):
            _select_checkout(
                plan_code="PRO_MONTHLY",
                plan_label="PRO MENSUAL",
                clp_amount=3000,
                usd_amount=6,
            )

            st.rerun()

    with annual_column:
        if st.button(
            "👑 PAGAR AHORA · CLP 20.000 / AÑO",
            use_container_width=True,
            type="primary",
            key="subscription_annual_checkout",
            disabled=is_owner,
        ):
            _select_checkout(
                plan_code="PRO_ANNUAL",
                plan_label="PRO ANUAL",
                clp_amount=20000,
                usd_amount=40,
            )

            st.rerun()

    _render_checkout(
        is_owner=is_owner,
    )
