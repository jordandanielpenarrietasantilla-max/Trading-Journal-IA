from __future__ import annotations

import datetime as dt
import html
import io
from typing import Any
from urllib.parse import quote

import qrcode
import streamlit as st
import streamlit.components.v1 as components

from core.crypto_payments import (
    CryptoPaymentError,
    apply_verified_membership_to_session,
    create_usdt_order,
    list_crypto_payments,
    verify_usdt_order,
)
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


/* =========================================================
   USDT AUTOMÁTICO Y SOPORTE
   ========================================================= */

.ax-usdt-order {
    margin-top: 14px;
    padding: 18px;
    border: 1px solid rgba(43,220,255,.42);
    border-radius: 17px;
    background:
        radial-gradient(circle at 100% 0%,rgba(43,220,255,.13),transparent 36%),
        linear-gradient(145deg,rgba(7,16,37,.99),rgba(5,9,24,.99));
}

.ax-usdt-head {
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:12px;
    flex-wrap:wrap;
}

.ax-usdt-head strong {
    color:#2bdcff;
    font-size:15px;
    font-weight:950;
}

.ax-usdt-head span {
    color:#31ff9c;
    font-size:10px;
    font-weight:950;
}

.ax-support-panel {
    margin-top: 16px;
    padding: 16px;
    border: 1px solid rgba(126,102,255,.38);
    border-radius: 15px;
    background:
        radial-gradient(circle at 100% 0%,rgba(157,61,255,.12),transparent 35%),
        linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));
}

.ax-support-panel strong {
    display:block;
    color:#f4f7ff;
    font-size:14px;
    font-weight:950;
}

.ax-support-panel p {
    margin:7px 0 0;
    color:#b9c5da;
    font-size:11px;
    line-height:1.55;
}


.ax-order-progress {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 9px;
    margin: 12px 0;
}

.ax-order-progress div {
    padding: 12px;
    border: 1px solid rgba(72,96,158,.24);
    border-radius: 11px;
    background: rgba(5,11,28,.88);
}

.ax-order-progress small {
    display: block;
    color: #8ea0bd;
    font-size: 9px;
    font-weight: 900;
}

.ax-order-progress strong {
    display: block;
    margin-top: 5px;
    color: #eef4ff;
    font-size: 12px;
    overflow-wrap: anywhere;
}

.ax-countdown-ok {
    color: #31ff9c !important;
}

.ax-countdown-warn {
    color: #ffc400 !important;
}

.ax-countdown-expired {
    color: #ff6688 !important;
}

.ax-auto-check {
    margin-top: 10px;
    padding: 10px 12px;
    color: #bcd7ff;
    font-size: 11px;
    line-height: 1.5;
    border-left: 3px solid #2bdcff;
    border-radius: 5px 11px 11px 5px;
    background: rgba(43,220,255,.055);
}

@media (max-width:700px) {
    .ax-order-progress {
        grid-template-columns: 1fr;
    }
}


.ax-verification-steps {
    margin-top: 12px;
    padding: 14px;
    border: 1px solid rgba(43,220,255,.22);
    border-radius: 12px;
    background: rgba(5,11,28,.82);
}

.ax-history-card {
    margin-top: 10px;
    padding: 14px;
    border: 1px solid rgba(72,96,158,.24);
    border-radius: 13px;
    background: rgba(5,11,28,.86);
}

.ax-history-grid {
    display: grid;
    grid-template-columns: 1.15fr .8fr .8fr .8fr;
    gap: 8px;
}

.ax-history-grid small {
    display: block;
    color: #8fa0bd;
    font-size: 9px;
    font-weight: 900;
}

.ax-history-grid strong {
    display: block;
    margin-top: 4px;
    color: #eef4ff;
    font-size: 11px;
    overflow-wrap: anywhere;
}

.ax-status-approved { color: #31ff9c !important; }
.ax-status-pending { color: #ffc400 !important; }
.ax-status-problem { color: #ff6688 !important; }

@media (max-width:700px) {
    .ax-history-grid {
        grid-template-columns: 1fr 1fr;
    }
}


/* =========================================================
   CHECKOUT USDT PREMIUM
   ========================================================= */

.ax-pro-hero {
    margin: 0 0 14px;
    padding: 22px 24px;
    border: 1px solid rgba(80,99,210,.42);
    border-radius: 18px;
    background:
        radial-gradient(circle at 92% 0%,rgba(219,55,255,.13),transparent 30%),
        radial-gradient(circle at 68% 42%,rgba(43,220,255,.08),transparent 34%),
        linear-gradient(145deg,rgba(7,15,34,.99),rgba(4,8,22,.99));
    box-shadow: 0 22px 55px rgba(0,0,0,.28);
}

.ax-pro-hero h2 {
    margin: 0;
    color: #f5f7ff;
    font-size: 30px;
    line-height: 1.05;
    font-weight: 950;
    letter-spacing: -1px;
}

.ax-pro-hero h2 span {
    color: transparent;
    background: linear-gradient(90deg,#26dfff,#6d75ff,#e23cff);
    -webkit-background-clip: text;
    background-clip: text;
}

.ax-pro-hero p {
    margin: 8px 0 0;
    color: #aebbd2;
    font-size: 12px;
}

.ax-benefits-row {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 10px;
    margin-bottom: 14px;
}

.ax-benefit {
    display: flex;
    gap: 11px;
    align-items: center;
    padding: 13px;
    border: 1px solid rgba(67,97,166,.28);
    border-radius: 13px;
    background: rgba(5,11,28,.84);
}

.ax-benefit-icon {
    display: grid;
    place-items: center;
    flex: 0 0 42px;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    color: rgb(var(--rgb));
    font-size: 21px;
    background: rgba(var(--rgb),.10);
    border: 1px solid rgba(var(--rgb),.22);
}

.ax-benefit strong {
    display: block;
    color: #f1f5ff;
    font-size: 12px;
}

.ax-benefit span {
    display: block;
    margin-top: 3px;
    color: #9eacc4;
    font-size: 10px;
    line-height: 1.4;
}

.ax-order-shell {
    padding: 16px;
    border: 1px solid rgba(43,220,255,.35);
    border-radius: 17px;
    background:
        radial-gradient(circle at 100% 0%,rgba(43,220,255,.08),transparent 34%),
        linear-gradient(145deg,rgba(6,14,32,.99),rgba(4,9,24,.99));
}

.ax-order-titlebar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 12px;
}

.ax-order-titlebar strong {
    color: #2bdcff;
    font-size: 14px;
    font-weight: 950;
}

.ax-order-titlebar span {
    color: #31ff9c;
    font-size: 10px;
    font-weight: 950;
}

.ax-status-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 10px;
    color: #ffc400;
    font-size: 10px;
    font-weight: 950;
    border: 1px solid rgba(255,196,0,.28);
    border-radius: 999px;
    background: rgba(255,196,0,.075);
}

.ax-payment-amount {
    margin-top: 8px;
    color: #f4f7ff;
    font-size: 14px;
}

.ax-payment-amount strong {
    color: #31ff9c;
    font-size: 34px;
    letter-spacing: -1px;
}

.ax-network-pill {
    display: inline-flex;
    margin-left: 8px;
    padding: 5px 8px;
    color: #cbd5eb;
    font-size: 10px;
    font-weight: 900;
    border: 1px solid rgba(91,112,181,.30);
    border-radius: 8px;
    background: rgba(90,110,180,.10);
}

.ax-progress-card {
    padding: 16px;
    border: 1px solid rgba(72,96,158,.28);
    border-radius: 16px;
    background:
        radial-gradient(circle at 100% 0%,rgba(151,65,255,.09),transparent 34%),
        rgba(5,11,28,.90);
}

.ax-countdown-box {
    margin-bottom: 15px;
    padding: 16px;
    text-align: center;
    border: 1px solid rgba(78,102,171,.34);
    border-radius: 13px;
    background: rgba(3,8,22,.82);
}

.ax-countdown-box small {
    display: block;
    color: #aab6cb;
    font-size: 10px;
}

.ax-countdown-box strong {
    display: block;
    margin-top: 6px;
    color: #f4f7ff;
    font-size: 34px;
    letter-spacing: 2px;
}

.ax-step {
    position: relative;
    display: grid;
    grid-template-columns: 28px 1fr auto;
    gap: 10px;
    align-items: start;
    padding: 10px 0;
}

.ax-step:not(:last-child)::after {
    content: "";
    position: absolute;
    left: 13px;
    top: 37px;
    width: 2px;
    height: 28px;
    background: rgba(94,112,173,.28);
}

.ax-step-number {
    display: grid;
    place-items: center;
    width: 28px;
    height: 28px;
    color: #aab7cf;
    font-size: 11px;
    font-weight: 950;
    border-radius: 50%;
    background: rgba(85,100,157,.20);
    border: 1px solid rgba(85,100,157,.32);
}

.ax-step.complete .ax-step-number {
    color: #06120b;
    background: #31ff9c;
    border-color: #31ff9c;
}

.ax-step.current .ax-step-number {
    color: #0a0a08;
    background: #ffc400;
    border-color: #ffc400;
}

.ax-step strong {
    display: block;
    color: #edf3ff;
    font-size: 11px;
}

.ax-step span {
    display: block;
    margin-top: 3px;
    color: #8fa0bd;
    font-size: 9px;
}

.ax-step-badge {
    color: #ffc400;
    font-size: 9px;
    font-weight: 950;
}

.ax-security-note {
    margin-top: 14px;
    padding: 12px;
    color: #c9c0ff;
    font-size: 10px;
    line-height: 1.5;
    border: 1px solid rgba(141,81,255,.24);
    border-radius: 11px;
    background: rgba(141,81,255,.065);
}

.ax-qr-card {
    padding: 12px;
    text-align: center;
    border: 1px solid rgba(68,98,165,.25);
    border-radius: 14px;
    background: rgba(5,11,28,.88);
}

.ax-qr-tip {
    margin-top: 8px;
    color: #9faec6;
    font-size: 10px;
    line-height: 1.45;
}

.ax-tip-card {
    margin-top: 10px;
    padding: 11px;
    text-align: left;
    border: 1px solid rgba(255,196,0,.20);
    border-radius: 10px;
    background: rgba(255,196,0,.045);
}

.ax-tip-card strong {
    color: #ffc400;
    font-size: 10px;
}

.ax-tip-card div {
    margin-top: 5px;
    color: #b8c4d8;
    font-size: 9px;
    line-height: 1.5;
}

.ax-support-premium {
    padding: 17px;
    border: 1px solid rgba(72,96,158,.28);
    border-radius: 16px;
    background: rgba(5,11,28,.88);
}

.ax-support-premium h3 {
    margin: 0;
    color: #f2f6ff;
    font-size: 18px;
}

.ax-support-premium p {
    margin: 6px 0 0;
    color: #9eabc2;
    font-size: 10px;
}

.ax-history-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.ax-history-title strong {
    color: #f2f6ff;
    font-size: 15px;
}

.ax-history-title span {
    color: #8fa0bd;
    font-size: 9px;
}

@media (max-width: 1050px) {
    .ax-benefits-row {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 700px) {
    .ax-pro-hero h2 {
        font-size: 25px;
    }
}


/* =========================================================
   CHECKOUT USDT ULTRA PREMIUM
   ========================================================= */

.ax-ultra-hero {
    position: relative;
    overflow: hidden;
    margin: 0 0 15px;
    padding: 24px 26px;
    border: 1px solid rgba(84,103,218,.45);
    border-radius: 19px;
    background:
        radial-gradient(circle at 88% 0%,rgba(225,55,255,.16),transparent 28%),
        radial-gradient(circle at 68% 48%,rgba(43,220,255,.10),transparent 34%),
        linear-gradient(145deg,rgba(7,15,34,.99),rgba(4,8,22,.99));
    box-shadow:
        0 24px 64px rgba(0,0,0,.34),
        inset 0 1px 0 rgba(255,255,255,.035);
}

.ax-ultra-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    opacity: .28;
    background-image:
        linear-gradient(rgba(70,98,180,.05) 1px,transparent 1px),
        linear-gradient(90deg,rgba(70,98,180,.05) 1px,transparent 1px);
    background-size: 34px 34px;
}

.ax-ultra-hero-content {
    position: relative;
    z-index: 2;
}

.ax-ultra-kicker {
    color: #2bdcff;
    font-size: 9px;
    font-weight: 950;
    letter-spacing: 1.8px;
}

.ax-ultra-hero h2 {
    margin: 7px 0 0;
    color: #f5f7ff;
    font-size: 34px;
    line-height: 1.03;
    font-weight: 950;
    letter-spacing: -1.4px;
}

.ax-ultra-hero h2 span {
    color: transparent;
    background: linear-gradient(90deg,#28dcff,#6f73ff,#e83cff);
    -webkit-background-clip: text;
    background-clip: text;
}

.ax-ultra-hero p {
    margin: 9px 0 0;
    color: #aebbd2;
    font-size: 12px;
}

.ax-ultra-checks {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 14px;
}

.ax-ultra-checks span {
    display: inline-flex;
    padding: 7px 10px;
    color: #c9d4e8;
    font-size: 9px;
    font-weight: 850;
    border: 1px solid rgba(79,103,178,.25);
    border-radius: 999px;
    background: rgba(7,16,36,.64);
}

.ax-order-invoice {
    margin-bottom: 13px;
    padding: 15px;
    border: 1px solid rgba(49,255,156,.22);
    border-radius: 13px;
    background:
        radial-gradient(circle at 100% 0%,rgba(49,255,156,.08),transparent 34%),
        rgba(5,12,28,.90);
}

.ax-order-invoice-grid {
    display: grid;
    grid-template-columns: 1.3fr .8fr .7fr .75fr;
    gap: 9px;
}

.ax-order-invoice-grid div {
    min-width: 0;
}

.ax-order-invoice-grid small {
    display: block;
    color: #8fa0bd;
    font-size: 8px;
    font-weight: 900;
}

.ax-order-invoice-grid strong {
    display: block;
    margin-top: 4px;
    color: #eff4ff;
    font-size: 10px;
    overflow-wrap: anywhere;
}

.ax-qr-frame {
    padding: 14px;
    border: 1px solid rgba(43,220,255,.30);
    border-radius: 15px;
    background:
        radial-gradient(circle at 50% 0%,rgba(43,220,255,.07),transparent 40%),
        rgba(5,11,28,.92);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.025);
}

.ax-qr-title {
    margin-bottom: 10px;
    color: #eef4ff;
    font-size: 12px;
    font-weight: 950;
    text-align: center;
}

.ax-amount-mega {
    margin: 9px 0 12px;
    color: #aebbd2;
    font-size: 11px;
}

.ax-amount-mega strong {
    display: inline-block;
    margin-top: 2px;
    color: #31ff9c;
    font-size: 43px;
    line-height: 1;
    letter-spacing: -1.8px;
    font-weight: 950;
    text-shadow: 0 0 24px rgba(49,255,156,.18);
}

.ax-chain-live {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin: 11px 0;
    padding: 11px 12px;
    border: 1px solid rgba(49,255,156,.22);
    border-radius: 11px;
    background: rgba(49,255,156,.05);
}

.ax-chain-live strong {
    color: #eef4ff;
    font-size: 10px;
}

.ax-chain-live span {
    color: #31ff9c;
    font-size: 9px;
    font-weight: 950;
}

.ax-chain-dot {
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-right: 6px;
    border-radius: 50%;
    background: #31ff9c;
    box-shadow: 0 0 13px rgba(49,255,156,.70);
}

.ax-countdown-track {
    overflow: hidden;
    width: 100%;
    height: 7px;
    margin-top: 11px;
    border-radius: 999px;
    background: rgba(81,99,157,.20);
}

.ax-countdown-track span {
    display: block;
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg,#31ff9c,#2bdcff,#7e66ff);
    box-shadow: 0 0 18px rgba(43,220,255,.22);
}

.ax-support-card-grid {
    display: grid;
    grid-template-columns: repeat(3,minmax(0,1fr));
    gap: 9px;
    margin-top: 12px;
}

.ax-support-info {
    padding: 12px;
    border: 1px solid rgba(70,96,164,.24);
    border-radius: 12px;
    background: rgba(5,11,28,.82);
}

.ax-support-info strong {
    display: block;
    color: #f0f4ff;
    font-size: 11px;
}

.ax-support-info span {
    display: block;
    margin-top: 5px;
    color: #8fa0bd;
    font-size: 9px;
    line-height: 1.45;
}

.ax-success-screen {
    position: relative;
    overflow: hidden;
    padding: 34px 28px;
    text-align: center;
    border: 1px solid rgba(49,255,156,.35);
    border-radius: 20px;
    background:
        radial-gradient(circle at 50% 0%,rgba(49,255,156,.13),transparent 36%),
        radial-gradient(circle at 84% 25%,rgba(43,220,255,.10),transparent 32%),
        linear-gradient(145deg,rgba(6,15,31,.99),rgba(4,9,23,.99));
    box-shadow: 0 26px 70px rgba(0,0,0,.35);
}

.ax-success-crown {
    font-size: 52px;
    filter: drop-shadow(0 0 18px rgba(255,196,0,.24));
}

.ax-success-screen h2 {
    margin: 10px 0 0;
    color: #f5f7ff;
    font-size: 34px;
    line-height: 1.05;
    font-weight: 950;
}

.ax-success-screen h2 span {
    color: transparent;
    background: linear-gradient(90deg,#31ff9c,#2bdcff,#8c58ff);
    -webkit-background-clip: text;
    background-clip: text;
}

.ax-success-screen p {
    margin: 10px auto 0;
    max-width: 620px;
    color: #b8c5da;
    font-size: 12px;
    line-height: 1.6;
}

.ax-success-features {
    display: grid;
    grid-template-columns: repeat(4,minmax(0,1fr));
    gap: 9px;
    margin-top: 20px;
}

.ax-success-features div {
    padding: 11px;
    color: #dce7f7;
    font-size: 10px;
    font-weight: 850;
    border: 1px solid rgba(72,96,158,.24);
    border-radius: 11px;
    background: rgba(5,11,28,.76);
}

@media (max-width: 900px) {
    .ax-order-invoice-grid,
    .ax-success-features {
        grid-template-columns: 1fr 1fr;
    }

    .ax-support-card-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 620px) {
    .ax-ultra-hero h2 {
        font-size: 27px;
    }

    .ax-order-invoice-grid,
    .ax-success-features {
        grid-template-columns: 1fr;
    }

    .ax-amount-mega strong {
        font-size: 36px;
    }
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




def _parse_iso_datetime(
    value: Any,
) -> dt.datetime | None:
    """Convierte una fecha ISO a UTC."""

    if not value:
        return None

    try:
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


def _order_countdown(
    created_at: Any,
    *,
    duration_minutes: int = 30,
) -> tuple[str, bool, str]:
    """
    Devuelve texto, expiración y clase visual del contador.
    """

    created = _parse_iso_datetime(
        created_at
    )

    if created is None:
        return "30:00", False, "ax-countdown-ok"

    expires_at = created + dt.timedelta(
        minutes=duration_minutes,
    )

    remaining = int(
        (
            expires_at
            - dt.datetime.now(
                dt.timezone.utc
            )
        ).total_seconds()
    )

    if remaining <= 0:
        return "EXPIRADA", True, "ax-countdown-expired"

    minutes, seconds = divmod(
        remaining,
        60,
    )

    css_class = (
        "ax-countdown-warn"
        if remaining <= 5 * 60
        else "ax-countdown-ok"
    )

    return (
        f"{minutes:02d}:{seconds:02d}",
        False,
        css_class,
    )


def _render_copy_button(
    value: str,
    *,
    label: str = "📋 COPIAR DIRECCIÓN",
) -> None:
    """Botón de copiar que funciona dentro del navegador."""

    safe_value = html.escape(
        value,
        quote=True,
    )

    safe_label = html.escape(
        label,
    )

    components.html(
        f"""
        <button id="copy-value" style="
            width:100%;
            min-height:44px;
            border:1px solid rgba(43,220,255,.35);
            border-radius:11px;
            color:#f4f7ff;
            background:rgba(43,220,255,.07);
            font-weight:850;
            cursor:pointer;
        ">{safe_label}</button>

        <script>
        const button = document.getElementById("copy-value");

        button.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText("{safe_value}");
                button.textContent = "✅ COPIADO";
            }} catch (error) {{
                button.textContent = "COPIA MANUALMENTE";
            }}

            setTimeout(() => {{
                button.textContent = "{safe_label}";
            }}, 1800);
        }});
        </script>
        """,
        height=52,
        scrolling=False,
    )


def _support_whatsapp_url(
    *,
    plan_label: str,
    order_id: str,
    txid: str,
) -> str:
    """URL opcional de WhatsApp configurada en Secrets."""

    phone = (
        _secret("SUPPORT_WHATSAPP")
        or _secret("SUPPORT_WHATSAPP_NUMBER")
    ).strip()

    if not phone:
        return ""

    clean_phone = "".join(
        character
        for character in phone
        if character.isdigit()
    )

    if not clean_phone:
        return ""

    message = "\n".join(
        [
            "Hola, necesito ayuda con un pago de AXION PRIME.",
            f"Plan: {plan_label}",
            f"Order ID: {order_id or 'No generado'}",
            f"TXID: {txid or 'No indicado'}",
        ]
    )

    return (
        f"https://wa.me/{clean_phone}"
        f"?text={quote(message)}"
    )


def _support_telegram_url() -> str:
    """URL opcional de Telegram configurada en Secrets."""

    value = (
        _secret("SUPPORT_TELEGRAM_URL")
        or _secret("SUPPORT_TELEGRAM")
    ).strip()

    if not value:
        return ""

    if value.startswith("http://") or value.startswith("https://"):
        return value

    username = value.lstrip("@").strip()

    return (
        f"https://t.me/{username}"
        if username
        else ""
    )


def _automatic_tx_verification(
    *,
    order_id: str,
    txid: str,
    order_key: str,
) -> None:
    """
    Reintenta la verificación automáticamente cada 12 segundos.

    Solo se activa después de que el usuario pega un TXID.
    """

    if not order_id or not txid:
        return

    def _run_check() -> None:
        try:
            result = verify_usdt_order(
                order_id,
                txid,
            )
        except CryptoPaymentError as exc:
            st.caption(
                f"Verificación automática: {exc}"
            )
            return
        except Exception as exc:
            st.caption(
                f"Verificación automática temporalmente no disponible: {exc}"
            )
            return

        if result.get("ok") and result.get("activated"):
            apply_verified_membership_to_session(
                result
            )

            st.session_state.pop(
                order_key,
                None,
            )

            membership_data = result.get(
                "membership",
                {},
            )

            if not isinstance(
                membership_data,
                dict,
            ):
                membership_data = {}

            st.session_state[
                "crypto_payment_success"
            ] = {
                "plan": membership_data.get(
                    "plan",
                    "PRO",
                ),
                "expires_at": membership_data.get(
                    "expires_at",
                    "",
                ),
            }

            st.balloons()
            st.rerun()

        if result.get("pending"):
            st.caption(
                "🔄 Seguimos esperando confirmación en TRON. "
                "La página revisará nuevamente."
            )
        elif result.get("manual_review"):
            st.warning(
                str(
                    result.get("error")
                    or "El pago requiere revisión de soporte."
                )
            )

    fragment_factory = getattr(
        st,
        "fragment",
        None,
    )

    if callable(fragment_factory):
        fragment_factory(
            run_every="12s"
        )(
            _run_check
        )()
    else:
        st.caption(
            "Tu versión de Streamlit no admite revisión automática "
            "periódica. Usa el botón Verificar pago."
        )



def _format_payment_datetime(value: Any) -> str:
    parsed = _parse_iso_datetime(value)

    if parsed is None:
        return "Sin fecha"

    return parsed.strftime("%d/%m/%Y · %H:%M UTC")


def _payment_status_view(
    status: Any,
) -> tuple[str, str]:
    normalized = str(
        status
        or "pending"
    ).strip().lower()

    mapping = {
        "approved": ("✅ CONFIRMADO", "ax-status-approved"),
        "pending": ("🟡 ESPERANDO", "ax-status-pending"),
        "verifying": ("🔄 VERIFICANDO", "ax-status-pending"),
        "manual_review": ("🛟 REVISIÓN", "ax-status-problem"),
        "rejected": ("❌ RECHAZADO", "ax-status-problem"),
        "expired": ("⌛ EXPIRADO", "ax-status-problem"),
    }

    return mapping.get(
        normalized,
        (normalized.upper(), "ax-status-pending"),
    )


def _render_crypto_payment_history() -> None:
    """Historial de órdenes cripto del usuario."""

    with st.expander(
        "🧾 HISTORIAL DE PAGOS CRIPTO",
        expanded=False,
    ):
        if st.button(
            "🔄 ACTUALIZAR HISTORIAL",
            use_container_width=True,
            key="subscription_refresh_crypto_history",
        ):
            st.session_state.pop(
                "crypto_payment_history_cache",
                None,
            )

        history = st.session_state.get(
            "crypto_payment_history_cache",
        )

        if not isinstance(history, list):
            try:
                with st.spinner("Cargando historial..."):
                    history = list_crypto_payments(limit=20)

                st.session_state[
                    "crypto_payment_history_cache"
                ] = history

            except CryptoPaymentError as exc:
                st.error(str(exc))
                return

            except Exception as exc:
                st.error(
                    "No se pudo cargar el historial de pagos."
                )

                with st.expander(
                    "Detalle técnico",
                    expanded=False,
                ):
                    st.code(str(exc), language="text")
                return

        if not history:
            st.info(
                "Todavía no tienes órdenes de pago cripto."
            )
            return

        for payment in history:
            status_text, status_class = (
                _payment_status_view(
                    payment.get("status")
                )
            )

            plan_code = str(
                payment.get("plan_code", "")
                or ""
            ).replace(
                "PRO_",
                "",
            ).replace(
                "_",
                " ",
            )

            expected = payment.get(
                "expected_amount",
                "",
            )

            received = payment.get(
                "received_amount",
                "",
            )

            amount_text = (
                f"{received} USDT"
                if received not in {None, ""}
                else f"{expected} USDT"
            )

            txid = str(
                payment.get("txid", "")
                or ""
            ).strip()

            short_txid = (
                f"{txid[:10]}…{txid[-8:]}"
                if len(txid) > 22
                else (txid or "Sin TXID")
            )

            st.html(
                f"""
                <section class="ax-history-card">
                    <div class="ax-history-grid">
                        <div>
                            <small>FECHA</small>
                            <strong>{html.escape(_format_payment_datetime(payment.get("created_at")))}</strong>
                        </div>
                        <div>
                            <small>PLAN</small>
                            <strong>{html.escape(plan_code or "PRO")}</strong>
                        </div>
                        <div>
                            <small>IMPORTE</small>
                            <strong>{html.escape(str(amount_text))}</strong>
                        </div>
                        <div>
                            <small>ESTADO</small>
                            <strong class="{status_class}">
                                {html.escape(status_text)}
                            </strong>
                        </div>
                    </div>

                    <div style="margin-top:10px">
                        <small style="color:#8fa0bd;font-size:9px;font-weight:900">
                            TXID
                        </small>
                        <strong style="display:block;margin-top:4px;color:#eef4ff;font-size:11px">
                            {html.escape(short_txid)}
                        </strong>
                    </div>
                </section>
                """
            )

            message = str(
                payment.get(
                    "verification_message",
                    "",
                )
                or ""
            ).strip()

            if message:
                st.caption(message)


def _support_email() -> str:
    """Correo de soporte: SUPPORT_EMAIL o ADMIN_EMAIL."""

    return (
        _secret("SUPPORT_EMAIL")
        or _secret("ADMIN_EMAIL")
    ).strip()


def _support_mailto_url(
    *,
    plan_label: str,
    payment_method: str,
    order_id: str = "",
    txid: str = "",
) -> str:
    """Genera un correo prellenado para soporte."""

    email = _support_email()

    if not email:
        return ""

    user = _safe_dict(
        st.session_state.get("user", {})
    )

    account_email = str(
        user.get("email", "")
        or ""
    ).strip()

    subject = "Soporte de pago · AXION PRIME"

    body = "\n".join(
        [
            "Hola, necesito ayuda con un pago de AXION PRIME.",
            "",
            f"Plan: {plan_label}",
            f"Método: {payment_method}",
            f"Correo de mi cuenta: {account_email or 'No indicado'}",
            f"Order ID: {order_id or 'No generado'}",
            f"TXID: {txid or 'No indicado'}",
            "",
            "Descripción del problema:",
            "",
        ]
    )

    return (
        f"mailto:{email}"
        f"?subject={quote(subject)}"
        f"&body={quote(body)}"
    )


def _render_support_panel(
    *,
    plan_label: str,
    payment_method: str,
    order_id: str = "",
    txid: str = "",
) -> None:
    """Panel de soporte visible para problemas de pago."""

    st.html(
        """
        <section class="ax-support-premium">
            <h3>🛟 ¿Necesitas ayuda?</h3>
            <p>
                Nuestro equipo responde normalmente en menos de 24 horas.
                Incluye el TXID, tu correo y una captura del pago.
            </p>

            <div class="ax-support-card-grid">
                <div class="ax-support-info">
                    <strong>📧 Correo</strong>
                    <span>Soporte detallado para casos de pago.</span>
                </div>

                <div class="ax-support-info">
                    <strong>💬 WhatsApp</strong>
                    <span>Respuesta rápida para incidencias urgentes.</span>
                </div>

                <div class="ax-support-info">
                    <strong>✈ Telegram</strong>
                    <span>Soporte para pagos internacionales.</span>
                </div>
            </div>
        </section>
        """
    )

    support_url = _support_mailto_url(
        plan_label=plan_label,
        payment_method=payment_method,
        order_id=order_id,
        txid=txid,
    )

    support_email = _support_email()

    if support_email:
        st.caption(
            f"Correo de soporte: {support_email}"
        )

    button_columns = st.columns(
        3,
        gap="small",
    )

    with button_columns[0]:
        if support_url:
            st.link_button(
                "📧 CORREO",
                support_url,
                use_container_width=True,
            )

    whatsapp_url = _support_whatsapp_url(
        plan_label=plan_label,
        order_id=order_id,
        txid=txid,
    )

    with button_columns[1]:
        if whatsapp_url:
            st.link_button(
                "💬 WHATSAPP",
                whatsapp_url,
                use_container_width=True,
            )

    telegram_url = _support_telegram_url()

    with button_columns[2]:
        if telegram_url:
            st.link_button(
                "✈️ TELEGRAM",
                telegram_url,
                use_container_width=True,
            )

    if not any(
        [
            support_url,
            whatsapp_url,
            telegram_url,
        ]
    ):
        st.warning(
            "Configura SUPPORT_EMAIL, SUPPORT_WHATSAPP o "
            "SUPPORT_TELEGRAM_URL en Streamlit Secrets."
        )


def _usdt_order_key(plan_code: str) -> str:
    return (
        "usdt_crypto_order_"
        f"{str(plan_code or '').strip().upper()}"
    )




def _countdown_progress_percent(
    created_at: Any,
    *,
    duration_minutes: int = 30,
) -> int:
    """Porcentaje restante de la orden."""

    created = _parse_iso_datetime(created_at)

    if created is None:
        return 100

    total_seconds = max(
        1,
        duration_minutes * 60,
    )

    expires_at = created + dt.timedelta(
        minutes=duration_minutes,
    )

    remaining = max(
        0,
        int(
            (
                expires_at
                - dt.datetime.now(dt.timezone.utc)
            ).total_seconds()
        ),
    )

    return max(
        0,
        min(
            100,
            int(
                remaining
                / total_seconds
                * 100
            ),
        ),
    )


def _render_crypto_success_screen() -> bool:
    """
    Muestra una pantalla final premium tras activar PRO.

    Devuelve True si la pantalla fue renderizada.
    """

    success = st.session_state.get(
        "crypto_payment_success",
    )

    if not isinstance(success, dict):
        return False

    plan = str(
        success.get("plan", "PRO")
        or "PRO"
    ).replace("_", " ")

    expires_at = str(
        success.get("expires_at", "")
        or ""
    ).strip()

    st.html(
        f"""
        <section class="ax-success-screen">
            <div class="ax-success-crown">👑</div>

            <h2>
                PAGO CONFIRMADO<br>
                <span>BIENVENIDO A AXION PRIME PRO</span>
            </h2>

            <p>
                Tu membresía {html.escape(plan)} ya está activa.
                Desde este momento tienes acceso a todas las
                herramientas premium de la plataforma.
            </p>

            <div class="ax-success-features">
                <div>🤖 Chat IA avanzado</div>
                <div>🧠 Psicotrading</div>
                <div>🔎 Auditoría IA</div>
                <div>📈 Herramientas PRO</div>
            </div>

            {
                f'<p>Vigencia hasta: {html.escape(expires_at)}</p>'
                if expires_at
                else ''
            }
        </section>
        """
    )

    if st.button(
        "🚀 IR AL DASHBOARD PRO",
        use_container_width=True,
        type="primary",
        key="crypto_success_go_dashboard",
    ):
        st.session_state.pop(
            "crypto_payment_success",
            None,
        )
        st.session_state.page = "Dashboard"
        st.rerun()

    return True


def _order_progress_html(
    *,
    has_order: bool,
    has_txid: bool,
    activated: bool = False,
) -> str:
    """Construye la línea de progreso visual del pago."""

    states = [
        (
            "complete" if has_order else "current",
            "Orden creada",
            "Tu orden fue generada",
            "Completado" if has_order else "Actual",
        ),
        (
            "complete" if has_txid else ("current" if has_order else ""),
            "Esperando pago",
            "Envía el importe exacto",
            "Completado" if has_txid else ("Actual" if has_order else ""),
        ),
        (
            "complete" if activated else ("current" if has_txid else ""),
            "Verificando blockchain",
            "Buscando tu transacción",
            "Completado" if activated else ("Actual" if has_txid else ""),
        ),
        (
            "complete" if activated else "",
            "Activando PRO",
            "Activando tu membresía",
            "Completado" if activated else "",
        ),
    ]

    rows = []

    for index, (
        state_class,
        title,
        subtitle,
        badge,
    ) in enumerate(
        states,
        start=1,
    ):
        rows.append(
            f"""
            <div class="ax-step {state_class}">
                <div class="ax-step-number">{index}</div>
                <div>
                    <strong>{html.escape(title)}</strong>
                    <span>{html.escape(subtitle)}</span>
                </div>
                <div class="ax-step-badge">
                    {html.escape(badge)}
                </div>
            </div>
            """
        )

    return "".join(rows)


def _tronscan_url(txid: str) -> str:
    clean_txid = str(txid or "").strip()

    if not clean_txid:
        return ""

    return (
        "https://tronscan.org/#/transaction/"
        f"{clean_txid}"
    )


def _render_usdt_automatic_checkout(
    *,
    checkout: dict[str, Any],
    plan_label: str,
    usd_amount: int,
    address: str,
) -> None:
    """Checkout USDT TRC20 premium con activación automática."""

    plan_code = str(
        checkout.get("plan_code", "")
        or ""
    ).strip().upper()

    if not plan_code:
        st.error("No se pudo identificar el plan.")
        return

    order_key = _usdt_order_key(plan_code)
    order = st.session_state.get(order_key, {})

    if not isinstance(order, dict):
        order = {}

    if _render_crypto_success_screen():
        return

    st.html(
        """
        <section class="ax-ultra-hero">
            <div class="ax-ultra-hero-content">
                <div class="ax-ultra-kicker">
                    AXION PRIME · CHECKOUT BLOCKCHAIN
                </div>

                <h2>
                    Activa tu membresía en
                    <span>menos de 60 segundos</span>
                </h2>

                <p>
                    Pago protegido, confirmación directa desde TRON y
                    activación automática sin intervención manual.
                </p>

                <div class="ax-ultra-checks">
                    <span>✓ Activación automática</span>
                    <span>✓ Verificación blockchain</span>
                    <span>✓ Sin revisión manual</span>
                    <span>✓ Acceso PRO inmediato</span>
                </div>
            </div>
        </section>

        <section class="ax-benefits-row">
            <div class="ax-benefit">
                <div class="ax-benefit-icon" style="--rgb:255,196,0">⚡</div>
                <div>
                    <strong>Activación automática</strong>
                    <span>Al confirmar el pago, tu plan se activa de inmediato.</span>
                </div>
            </div>

            <div class="ax-benefit">
                <div class="ax-benefit-icon" style="--rgb:49,255,156">🛡</div>
                <div>
                    <strong>Pago seguro</strong>
                    <span>Verificación directa mediante TRON (TRC20).</span>
                </div>
            </div>

            <div class="ax-benefit">
                <div class="ax-benefit-icon" style="--rgb:49,255,156">✓</div>
                <div>
                    <strong>Sin revisión manual</strong>
                    <span>La blockchain confirma la operación automáticamente.</span>
                </div>
            </div>
        </section>
        """
    )

    if not order:
        main_column, status_column = st.columns(
            [.72, .28],
            gap="medium",
        )

        with main_column:
            st.html(
                f"""
                <section class="ax-order-shell">
                    <div class="ax-order-titlebar">
                        <strong>₮ USDT TRC20 · ACTIVACIÓN AUTOMÁTICA</strong>
                        <span>IMPORTE EXACTO: {usd_amount} USDT</span>
                    </div>

                    <div class="ax-security-note">
                        Primero genera una orden segura. Quedará vinculada
                        a tu cuenta, al plan seleccionado y al importe exacto.
                    </div>
                </section>
                """
            )

            if st.button(
                f"⚡ GENERAR ORDEN DE {usd_amount} USDT",
                use_container_width=True,
                type="primary",
                key=f"subscription_create_usdt_order_{plan_code}",
            ):
                try:
                    with st.status(
                        "Creando orden segura...",
                        expanded=True,
                    ) as create_status:
                        st.write("🔐 Vinculando la orden a tu cuenta...")
                        created_order = create_usdt_order(plan_code)
                        st.write("✅ Orden vinculada correctamente.")

                        create_status.update(
                            label="Orden creada correctamente",
                            state="complete",
                            expanded=True,
                        )

                    st.session_state[order_key] = created_order
                    st.session_state.pop(
                        "crypto_payment_history_cache",
                        None,
                    )
                    st.rerun()

                except CryptoPaymentError as exc:
                    st.error(str(exc))

                except Exception as exc:
                    st.error("No se pudo crear la orden USDT.")
                    with st.expander(
                        "Ver detalle técnico",
                        expanded=False,
                    ):
                        st.code(str(exc), language="text")

        with status_column:
            st.html(
                f"""
                <section class="ax-progress-card">
                    <div class="ax-history-title">
                        <strong>Estado de tu orden</strong>
                    </div>

                    <div class="ax-countdown-box">
                        <small>Genera una orden para comenzar</small>
                        <strong>-- : --</strong>
                    </div>

                    {_order_progress_html(
                        has_order=False,
                        has_txid=False,
                    )}

                    <div class="ax-security-note">
                        🔒 El plan solo se activa después de confirmar
                        el pago real en la blockchain.
                    </div>
                </section>
                """
            )

        support_column, history_column = st.columns(
            2,
            gap="medium",
        )

        with support_column:
            _render_support_panel(
                plan_label=plan_label,
                payment_method="USDT TRC20",
            )

        with history_column:
            _render_crypto_payment_history()

        return

    order_id = str(
        order.get("id", "")
        or ""
    ).strip()

    order_address = str(
        order.get("destination_address", "")
        or address
    ).strip()

    expected_amount = float(
        order.get("expected_amount", usd_amount)
        or usd_amount
    )

    order_status = str(
        order.get("status", "pending")
        or "pending"
    ).strip().upper()

    countdown_text, order_expired, countdown_class = (
        _order_countdown(
            order.get("created_at"),
            duration_minutes=30,
        )
    )

    countdown_percent = _countdown_progress_percent(
        order.get("created_at"),
        duration_minutes=30,
    )

    main_column, status_column = st.columns(
        [.72, .28],
        gap="medium",
    )

    transaction_hash = ""

    with main_column:
        st.html(
            f"""
            <section class="ax-order-invoice">
                <div class="ax-order-invoice-grid">
                    <div>
                        <small>ORDER ID</small>
                        <strong>{html.escape(order_id)}</strong>
                    </div>

                    <div>
                        <small>IMPORTE</small>
                        <strong>{expected_amount:.4f} USDT</strong>
                    </div>

                    <div>
                        <small>RED</small>
                        <strong>TRON · TRC20</strong>
                    </div>

                    <div>
                        <small>ESTADO</small>
                        <strong>ESPERANDO PAGO</strong>
                    </div>
                </div>
            </section>
            """
        )

        qr_column, details_column = st.columns(
            [.34, .66],
            gap="medium",
        )

        with qr_column:
            st.html(
                """
                <section class="ax-qr-frame">
                    <div class="ax-qr-title">
                        📱 Escanea este código
                    </div>
                """
            )

            st.image(
                _make_qr(order_address),
                caption="USDT · TRON · TRC20",
                width=220,
            )

            st.html(
                f"""
                <div class="ax-qr-tip">
                    Escanea con una wallet compatible con TRON.
                </div>

                <div class="ax-tip-card">
                    <strong>💡 Consejos importantes</strong>
                    <div>
                        ✓ Envía exactamente {expected_amount:g} USDT<br>
                        ✓ Usa únicamente TRC20<br>
                        ✓ No utilices ERC20, BEP20 u otras redes
                    </div>
                </div>
                </section>
                """
            )

        with details_column:
            st.html(
                f"""
                <div class="ax-status-chip">◉ ESPERANDO PAGO</div>

                <div class="ax-amount-mega">
                    Envía exactamente<br>
                    <strong>{expected_amount:.4f} USDT</strong>
                    <span class="ax-network-pill">TRC20</span>
                </div>

                <div class="ax-chain-live">
                    <strong>🔗 Blockchain TRON</strong>
                    <span>
                        <i class="ax-chain-dot"></i>
                        ONLINE · ESPERANDO TRANSACCIÓN
                    </span>
                </div>
                """
            )

            st.markdown("#### Dirección de pago (TRC20)")
            st.code(order_address, language=None)

            _render_copy_button(
                order_address,
                label="📋 COPIAR DIRECCIÓN TRC20",
            )

            transaction_hash = st.text_input(
                "Hash de la transacción (TXID)",
                placeholder="Pega aquí el TXID de tu pago",
                key=f"subscription_usdt_txid_{plan_code}",
            )

            with st.expander(
                "🔎 ¿Dónde encuentro el TXID?",
                expanded=False,
            ):
                st.write(
                    "En Binance o tu wallet abre el retiro enviado, "
                    "entra en los detalles y copia el identificador "
                    "de transacción o TXID."
                )

            proof_file = st.file_uploader(
                "Captura del comprobante (opcional)",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"subscription_usdt_proof_{plan_code}",
                help=(
                    "La captura sirve como respaldo. La activación "
                    "depende de la verificación real del TXID."
                ),
            )

            if proof_file is not None:
                st.image(
                    proof_file,
                    caption="Comprobante seleccionado",
                    width=280,
                )

            verify_column, cancel_column = st.columns(
                [1.55, .85],
                gap="small",
            )

            with verify_column:
                verify_clicked = st.button(
                    "⚡ VERIFICAR PAGO Y ACTIVAR PRO",
                    use_container_width=True,
                    type="primary",
                    key=f"subscription_verify_usdt_{plan_code}",
                )

            with cancel_column:
                cancel_clicked = st.button(
                    "🗑️ CANCELAR ORDEN",
                    use_container_width=True,
                    key=f"subscription_cancel_usdt_{plan_code}",
                )

            if cancel_clicked:
                st.session_state.pop(order_key, None)
                st.rerun()

            clean_txid = str(
                transaction_hash
                or ""
            ).strip()

            if verify_clicked:
                if not clean_txid:
                    st.warning(
                        "Debes pegar el TXID antes de verificar."
                    )
                    return

                try:
                    with st.status(
                        "Verificando pago en la blockchain TRON...",
                        expanded=True,
                    ) as verification_status:
                        st.write("🔎 Buscando la transacción confirmada...")
                        result = verify_usdt_order(
                            order_id,
                            clean_txid,
                        )

                        if result.get("ok") and result.get("activated"):
                            st.write("✅ Transacción encontrada.")
                            st.write("✅ Importe y billetera verificados.")
                            st.write("👑 Activando AXION PRIME PRO...")

                            verification_status.update(
                                label="Pago confirmado y PRO activado",
                                state="complete",
                                expanded=True,
                            )

                        elif result.get("pending"):
                            verification_status.update(
                                label="Transacción pendiente de confirmación",
                                state="running",
                                expanded=True,
                            )

                        else:
                            verification_status.update(
                                label="La transacción necesita atención",
                                state="error",
                                expanded=True,
                            )

                    if result.get("ok") and result.get("activated"):
                        apply_verified_membership_to_session(result)

                        st.session_state.pop(order_key, None)
                        st.session_state.pop(
                            "crypto_payment_history_cache",
                            None,
                        )

                        membership_data = result.get(
                            "membership",
                            {},
                        )

                        if not isinstance(
                            membership_data,
                            dict,
                        ):
                            membership_data = {}

                        st.session_state[
                            "crypto_payment_success"
                        ] = {
                            "plan": membership_data.get(
                                "plan",
                                plan_code,
                            ),
                            "expires_at": membership_data.get(
                                "expires_at",
                                "",
                            ),
                        }

                        st.balloons()
                        st.rerun()

                    elif result.get("pending"):
                        st.info(
                            str(
                                result.get("error")
                                or "La transacción aún está pendiente."
                            )
                        )

                    elif result.get("manual_review"):
                        st.warning(
                            str(
                                result.get("error")
                                or "El pago requiere revisión."
                            )
                        )

                    else:
                        st.warning(
                            str(
                                result.get("error")
                                or result.get("message")
                                or "No fue posible confirmar el pago."
                            )
                        )

                except CryptoPaymentError as exc:
                    st.error(str(exc))

                except Exception as exc:
                    st.error("No se pudo verificar el pago USDT.")
                    with st.expander(
                        "Ver detalle técnico",
                        expanded=False,
                    ):
                        st.code(str(exc), language="text")

            if clean_txid:
                tronscan_url = _tronscan_url(clean_txid)

                if tronscan_url:
                    st.link_button(
                        "🔍 VER TRANSACCIÓN EN TRONSCAN",
                        tronscan_url,
                        use_container_width=True,
                    )

                st.html(
                    """
                    <div class="ax-auto-check">
                        ● Verificación automática activa: la app revisará
                        TRON cada 12 segundos mientras esta pantalla siga abierta.
                    </div>
                    """
                )

                _automatic_tx_verification(
                    order_id=order_id,
                    txid=clean_txid,
                    order_key=order_key,
                )

    with status_column:
        st.html(
            f"""
            <section class="ax-progress-card">
                <div class="ax-history-title">
                    <strong>Estado de tu orden</strong>
                    <span>{html.escape(order_status)}</span>
                </div>

                <div class="ax-countdown-box">
                    <small>Esta orden expira en</small>
                    <strong class="{countdown_class}">
                        {html.escape(countdown_text)}
                    </strong>

                    <div class="ax-countdown-track">
                        <span style="width:{countdown_percent}%"></span>
                    </div>
                </div>

                {_order_progress_html(
                    has_order=True,
                    has_txid=bool(
                        str(transaction_hash or "").strip()
                    ),
                )}

                <div class="ax-security-note">
                    🔒 Una vez confirmado el pago, tu plan se
                    activará automáticamente.
                </div>
            </section>
            """
        )

    if order_expired:
        st.error(
            "Esta orden expiró. No envíes fondos usando esta orden."
        )

        if st.button(
            "🔄 GENERAR NUEVA ORDEN",
            use_container_width=True,
            type="primary",
            key=f"subscription_regenerate_usdt_{plan_code}",
        ):
            st.session_state.pop(order_key, None)
            st.rerun()

        return

    support_column, history_column = st.columns(
        2,
        gap="medium",
    )

    with support_column:
        _render_support_panel(
            plan_label=plan_label,
            payment_method="USDT TRC20",
            order_id=order_id,
            txid=str(transaction_hash or "").strip(),
        )

    with history_column:
        _render_crypto_payment_history()

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

        _render_support_panel(
            plan_label=plan_label,
            payment_method="Binance Pay",
        )
        return

    wallets = _wallets()

    if payment_method == "USDT TRC20":
        usdt_wallet = wallets.get("USDT TRC20", {})
        usdt_address = str(
            usdt_wallet.get("address", "")
            or ""
        ).strip()

        if not usdt_address:
            st.warning(
                "USDT_TRC20_WALLET_ADDRESS no está configurada "
                "en Streamlit Secrets."
            )
            return

        _render_usdt_automatic_checkout(
            checkout=checkout,
            plan_label=plan_label,
            usd_amount=usd_amount,
            address=usdt_address,
        )
        return

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


    _render_support_panel(
        plan_label=plan_label,
        payment_method=payment_method,
        txid=str(transaction_hash or "").strip(),
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
