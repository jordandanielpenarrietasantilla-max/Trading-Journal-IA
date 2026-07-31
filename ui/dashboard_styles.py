from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# ESTILOS EXCLUSIVOS DEL DASHBOARD
# =========================================================


DASHBOARD_CSS = """
<style>

/* ========================================================
   VARIABLES DEL COMMAND CENTER
   ======================================================== */

:root {
    --axd-bg: #020611;
    --axd-bg-soft: #050b18;
    --axd-panel: rgba(5, 13, 29, 0.97);
    --axd-panel-soft: rgba(8, 17, 38, 0.95);

    --axd-border: rgba(57, 104, 180, 0.34);
    --axd-border-soft: rgba(70, 100, 166, 0.22);

    --axd-white: #f7f9ff;
    --axd-text: #e7edfb;
    --axd-muted: #8c99b7;
    --axd-dim: #596783;

    --axd-cyan: #20ddf5;
    --axd-blue: #367cff;
    --axd-purple: #8b4dff;

    --axd-green: #00f58a;
    --axd-red: #ff1744;

    --axd-shadow:
        0 22px 60px rgba(0, 0, 0, 0.36),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


/* ========================================================
   CORREGIR EL FONDO DEL DASHBOARD
   ======================================================== */

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 12% 2%,
            rgba(32, 221, 245, 0.075),
            transparent 26%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(139, 77, 255, 0.12),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            #020611,
            #040918 55%,
            #09041b
        ) !important;
}


/*
Elimina las franjas gigantes heredadas de core/styles.py.
*/

[data-testid="stAppViewContainer"]::before {
    display: none !important;
}


/*
Cuadrícula financiera sutil.
*/

[data-testid="stAppViewContainer"]::after {
    content: "" !important;

    display: block !important;

    position: fixed !important;
    inset: 0 !important;

    z-index: 0 !important;

    pointer-events: none !important;

    background-image:
        linear-gradient(
            rgba(76, 108, 175, 0.032) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(76, 108, 175, 0.032) 1px,
            transparent 1px
        ) !important;

    background-size:
        48px 48px !important;

    opacity: 0.58 !important;
}


/* ========================================================
   VELAS JAPONESAS DECORATIVAS
   ======================================================== */

.ax-dashboard-candles {
    position: fixed;

    left: 250px;
    right: 25px;
    top: 78px;

    height: 118px;

    z-index: 1;

    pointer-events: none;

    overflow: hidden;

    opacity: 0.42;

    mask-image:
        linear-gradient(
            90deg,
            transparent,
            black 10%,
            black 90%,
            transparent
        );

    -webkit-mask-image:
        linear-gradient(
            90deg,
            transparent,
            black 10%,
            black 90%,
            transparent
        );
}


.ax-dashboard-candles-track {
    position: absolute;

    left: 0;
    top: 0;

    width: 2200px;
    height: 100%;

    animation:
        axd-candle-track
        38s
        linear
        infinite;
}


.ax-dashboard-candle {
    position: absolute;

    width: 8px;
    height: var(--body-height);

    top: var(--body-top);
    left: var(--left);

    border-radius: 1px;

    background:
        var(--candle-color);

    box-shadow:
        0 0 8px
        color-mix(
            in srgb,
            var(--candle-color) 55%,
            transparent
        );
}


.ax-dashboard-candle::before {
    content: "";

    position: absolute;

    left: 50%;
    top: calc(var(--wick-top) * -1);

    width: 1px;
    height:
        calc(
            var(--body-height)
            + var(--wick-top)
            + var(--wick-bottom)
        );

    transform:
        translateX(-50%);

    background:
        var(--candle-color);

    opacity: 0.9;
}


.ax-dashboard-candle::after {
    content: "";

    position: absolute;

    inset: 0;

    background:
        linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.13),
            transparent 45%
        );
}


@keyframes axd-candle-track {
    from {
        transform:
            translateX(0);
    }

    to {
        transform:
            translateX(-850px);
    }
}


/* ========================================================
   ANCHO GENERAL DEL DASHBOARD
   ======================================================== */

.block-container {
    width: 100% !important;
    max-width: 1760px !important;

    padding-top: 1.35rem !important;
    padding-left: 2.2rem !important;
    padding-right: 2.2rem !important;
    padding-bottom: 3rem !important;
}


/* ========================================================
   HEADER FUTURISTA
   ======================================================== */

.ax-future-header {
    position: relative;

    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 26px;
    flex-wrap: wrap;

    overflow: hidden;

    min-height: 154px;

    padding:
        26px
        29px;

    margin-bottom: 18px;

    background:
        radial-gradient(
            circle at 83% 18%,
            rgba(139, 77, 255, 0.22),
            transparent 34%
        ),
        radial-gradient(
            circle at 5% 0%,
            rgba(32, 221, 245, 0.08),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            rgba(4, 14, 33, 0.985),
            rgba(11, 7, 38, 0.975)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.41);

    border-radius: 22px;

    box-shadow:
        var(--axd-shadow);
}


.ax-future-header::before {
    content: "";

    position: absolute;

    top: 0;
    right: -8%;

    width: 55%;
    height: 100%;

    pointer-events: none;

    background:
        repeating-linear-gradient(
            90deg,
            transparent 0 28px,
            rgba(32, 221, 245, 0.022) 29px 30px
        );

    transform:
        skewX(-12deg);
}


.ax-future-header::after {
    content: "";

    position: absolute;

    left: 0;
    right: 0;
    bottom: 0;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--axd-cyan),
            var(--axd-blue),
            var(--axd-purple),
            transparent
        );

    opacity: 0.75;
}


.ax-future-header-copy,
.ax-future-header-status {
    position: relative;
    z-index: 2;
}


.ax-future-kicker {
    color:
        var(--axd-cyan);

    font-size: 8px;
    font-weight: 950;

    letter-spacing: 2.2px;
}


.ax-future-header h1 {
    margin:
        9px
        0
        0 !important;

    color:
        var(--axd-white);

    font-size:
        clamp(31px, 3vw, 46px);

    line-height: 1.03;

    font-weight: 950;

    letter-spacing: -2px;
}


.ax-future-header p {
    margin:
        10px
        0
        0 !important;

    color:
        var(--axd-muted);

    font-size: 12px;

    line-height: 1.55;
}


.ax-future-header-status {
    display: flex;
    align-items: center;

    gap: 12px;
    flex-wrap: wrap;
}


.ax-future-date {
    display: flex;
    align-items: center;

    gap: 8px;

    padding:
        8px
        12px;

    color:
        #dce5f8;

    font-size: 9px;
    font-weight: 850;

    background:
        rgba(4, 10, 25, 0.56);

    border:
        1px solid
        rgba(82, 108, 171, 0.25);

    border-radius: 999px;
}


.ax-future-date span {
    width: 1px;
    height: 13px;

    background:
        rgba(108, 127, 176, 0.44);
}


.ax-future-market-status {
    display: flex;
    align-items: center;

    gap: 8px;

    padding:
        9px
        14px;

    color:
        var(--axd-green);

    font-size: 7px;
    font-weight: 950;

    background:
        rgba(0, 245, 138, 0.075);

    border:
        1px solid
        rgba(0, 245, 138, 0.35);

    border-radius: 999px;

    box-shadow:
        inset 0 0 20px
        rgba(0, 245, 138, 0.025);
}


.ax-future-market-status i {
    width: 7px;
    height: 7px;

    display: block;

    border-radius: 50%;

    background:
        var(--axd-green);

    box-shadow:
        0 0 12px
        var(--axd-green);

    animation:
        axd-market-pulse
        2s
        ease-in-out
        infinite;
}


@keyframes axd-market-pulse {
    0%,
    100% {
        opacity: 0.55;
        transform: scale(0.85);
    }

    50% {
        opacity: 1;
        transform: scale(1.15);
    }
}


/* ========================================================
   FILTROS
   ======================================================== */

[data-baseweb="select"] > div {
    min-height: 43px !important;

    color:
        var(--axd-white) !important;

    background:
        linear-gradient(
            145deg,
            rgba(10, 19, 41, 0.98),
            rgba(5, 11, 27, 0.98)
        ) !important;

    border:
        1px solid
        rgba(76, 104, 171, 0.36) !important;

    border-radius:
        11px !important;
}


[data-baseweb="select"] > div:hover {
    border-color:
        rgba(32, 221, 245, 0.53) !important;
}


/* ========================================================
   TARJETAS DE MÉTRICAS
   ======================================================== */

.ax-future-metric {
    position: relative;

    min-height: 162px;

    display: flex;
    flex-direction: column;

    overflow: hidden;

    padding:
        16px;

    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(32, 221, 245, 0.075),
            transparent 42%
        ),
        linear-gradient(
            145deg,
            rgba(8, 18, 39, 0.985),
            rgba(4, 10, 25, 0.985)
        );

    border:
        1px solid
        rgba(65, 101, 170, 0.34);

    border-radius: 16px;

    box-shadow:
        0 16px 44px
        rgba(0, 0, 0, 0.29);

    transition:
        transform 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease;
}


.ax-future-metric::after {
    content: "";

    position: absolute;

    left: 14px;
    right: 14px;
    bottom: 0;

    height: 1px;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(32, 221, 245, 0.55),
            rgba(139, 77, 255, 0.7),
            transparent
        );
}


.ax-future-metric:hover {
    transform:
        translateY(-4px);

    border-color:
        rgba(32, 221, 245, 0.53);

    box-shadow:
        0 20px 52px
        rgba(0, 0, 0, 0.35),
        0 0 25px
        rgba(32, 221, 245, 0.05);
}


.ax-future-metric-head {
    display: flex;
    align-items: center;

    gap: 12px;
}


.ax-future-metric-icon {
    width: 42px;
    height: 42px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    border:
        1px solid;

    border-radius: 11px;

    font-size: 20px;
    font-weight: 950;
}


.ax-future-metric-label {
    color:
        #818eab;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 1.4px;
}


.ax-future-metric-value {
    margin-top: 7px;

    font-size:
        clamp(21px, 1.7vw, 29px);

    line-height: 1;

    font-weight: 950;

    white-space: nowrap;

    letter-spacing: -0.8px;
}


.ax-future-metric-meta {
    display: flex;
    justify-content: space-between;

    gap: 8px;

    margin-top: 13px;

    color:
        #74819e;

    font-size: 7px;
}


.ax-future-sparkline {
    width: 100%;
    height: 40px;

    margin-top: auto;

    overflow: visible;
}


/* ========================================================
   TÍTULOS DE SECCIÓN
   ======================================================== */

.ax-future-panel-title {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 12px;

    padding:
        13px
        15px;

    margin-top: 17px;
    margin-bottom: 9px;

    background:
        linear-gradient(
            145deg,
            rgba(7, 15, 33, 0.98),
            rgba(5, 10, 25, 0.98)
        );

    border:
        1px solid
        rgba(65, 99, 165, 0.3);

    border-radius: 14px;

    box-shadow:
        0 10px 28px
        rgba(0, 0, 0, 0.19);
}


.ax-future-panel-title > div {
    display: flex;
    align-items: center;

    gap: 8px;
}


.ax-future-panel-title > div > span {
    color:
        var(--axd-cyan);

    font-size: 14px;

    text-shadow:
        0 0 12px
        rgba(32, 221, 245, 0.36);
}


.ax-future-panel-title strong {
    color:
        var(--axd-white);

    font-size: 12px;
    font-weight: 900;
}


.ax-future-panel-title small {
    color:
        #64718d;

    font-size: 6px;
    font-weight: 850;

    letter-spacing: 1.3px;
}


/* ========================================================
   GRÁFICO DE EQUITY
   ======================================================== */

[data-testid="stPlotlyChart"] {
    overflow: hidden;

    padding:
        7px;

    background:
        radial-gradient(
            circle at 50% 100%,
            rgba(32, 221, 245, 0.075),
            transparent 46%
        ),
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.985),
            rgba(4, 9, 23, 0.985)
        );

    border:
        1px solid
        rgba(65, 99, 165, 0.32);

    border-radius: 16px;

    box-shadow:
        0 16px 42px
        rgba(0, 0, 0, 0.25);
}


/* ========================================================
   TABLA DE OPERACIONES
   ======================================================== */

.ax-future-table-shell {
    width: 100%;

    min-height: 430px;

    overflow: hidden;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.985),
            rgba(4, 9, 23, 0.985)
        );

    border:
        1px solid
        rgba(65, 99, 165, 0.32);

    border-radius: 16px;

    box-shadow:
        0 16px 42px
        rgba(0, 0, 0, 0.25);
}


.ax-future-table {
    width: 100%;

    table-layout: fixed;

    border-collapse: collapse;

    color:
        var(--axd-text);

    font-size: 10px;
}


.ax-future-table th {
    padding:
        14px
        10px;

    color:
        #71809e;

    font-size: 7px;
    font-weight: 950;

    text-align: left;

    letter-spacing: 1px;

    background:
        rgba(8, 17, 38, 0.99);

    border-bottom:
        1px solid
        rgba(68, 98, 160, 0.29);
}


.ax-future-table td {
    overflow: hidden;

    padding:
        14px
        10px;

    white-space: nowrap;

    text-overflow: ellipsis;

    border-bottom:
        1px solid
        rgba(68, 98, 160, 0.13);
}


.ax-future-table th:nth-child(1),
.ax-future-table td:nth-child(1) {
    width: 22%;
}


.ax-future-table th:nth-child(2),
.ax-future-table td:nth-child(2) {
    width: 26%;
}


.ax-future-table th:nth-child(3),
.ax-future-table td:nth-child(3) {
    width: 18%;
}


.ax-future-table th:nth-child(4),
.ax-future-table td:nth-child(4) {
    width: 18%;
}


.ax-future-table th:nth-child(5),
.ax-future-table td:nth-child(5) {
    width: 20%;
}


.ax-future-table tr:last-child td {
    border-bottom: none;
}


.ax-future-table tbody tr {
    transition:
        background 0.16s ease;
}


.ax-future-table tbody tr:hover {
    background:
        rgba(32, 221, 245, 0.045);
}


.ax-future-badge,
.ax-future-result {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    min-width: 42px;

    padding:
        4px
        8px;

    border-radius: 999px;

    font-size: 7px;
    font-weight: 950;
}


.ax-future-long {
    color:
        var(--axd-green);

    background:
        rgba(0, 245, 138, 0.12);

    border:
        1px solid
        rgba(0, 245, 138, 0.26);
}


.ax-future-short {
    color:
        #ff718a;

    background:
        rgba(255, 23, 68, 0.14);

    border:
        1px solid
        rgba(255, 23, 68, 0.28);
}


.ax-future-neutral {
    color:
        var(--axd-muted);

    background:
        rgba(125, 141, 176, 0.11);
}


.ax-future-win {
    color:
        var(--axd-green);

    background:
        rgba(0, 245, 138, 0.12);
}


.ax-future-loss {
    color:
        #ff718a;

    background:
        rgba(255, 23, 68, 0.14);
}


.ax-future-be {
    color:
        #c1cae0;

    background:
        rgba(130, 145, 179, 0.11);
}


.ax-future-pnl {
    font-weight: 950;
}


/* ========================================================
   SETUP
   ======================================================== */

[data-testid="stImage"] {
    overflow: hidden;

    padding: 8px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.985),
            rgba(4, 9, 23, 0.985)
        );

    border:
        1px solid
        rgba(65, 99, 165, 0.32);

    border-radius: 16px;

    box-shadow:
        0 16px 42px
        rgba(0, 0, 0, 0.25);
}


[data-testid="stImage"] img {
    display: block;

    border-radius: 11px;
}


/* ========================================================
   RESUMEN RÁPIDO
   ======================================================== */

.ax-future-summary {
    padding:
        16px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.985),
            rgba(4, 9, 23, 0.985)
        );

    border:
        1px solid
        rgba(65, 99, 165, 0.32);

    border-radius: 16px;

    box-shadow:
        0 16px 42px
        rgba(0, 0, 0, 0.25);
}


.ax-future-summary-row {
    display: flex;
    justify-content: space-between;

    gap: 12px;

    padding:
        10px
        0;

    color:
        #8996b3;

    font-size: 9px;

    border-bottom:
        1px solid
        rgba(67, 98, 160, 0.14);
}


.ax-future-summary-row:last-child {
    border-bottom: none;
}


.ax-future-summary-row strong {
    font-size: 10px;
    font-weight: 900;
}


/* ========================================================
   ESTADOS VACÍOS
   ======================================================== */

.ax-future-empty {
    min-height: 300px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    padding:
        24px;

    text-align: center;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.97),
            rgba(4, 9, 23, 0.97)
        );

    border:
        1px dashed
        rgba(32, 221, 245, 0.32);

    border-radius: 16px;
}


.ax-future-empty > div {
    color:
        var(--axd-cyan);

    font-size: 32px;

    text-shadow:
        0 0 18px
        rgba(32, 221, 245, 0.34);
}


.ax-future-empty strong {
    margin-top: 12px;

    color:
        var(--axd-white);

    font-size: 13px;
}


.ax-future-empty p {
    margin-top: 7px;

    color:
        #7c89a6;

    font-size: 9px;
    line-height: 1.5;
}


.ax-future-setup-empty {
    min-height: 245px;
}


/* ========================================================
   BANNER FUTURISTA
   ======================================================== */

.ax-future-intelligence {
    position: relative;

    display: grid;

    grid-template-columns:
        1.15fr
        0.95fr
        0.85fr;

    gap: 23px;

    overflow: hidden;

    margin-top: 21px;
    padding: 28px;

    background:
        radial-gradient(
            circle at 58% 50%,
            rgba(32, 221, 245, 0.105),
            transparent 29%
        ),
        radial-gradient(
            circle at 81% 50%,
            rgba(255, 23, 68, 0.105),
            transparent 29%
        ),
        linear-gradient(
            135deg,
            rgba(4, 14, 32, 0.985),
            rgba(10, 6, 31, 0.985)
        );

    border:
        1px solid
        rgba(65, 102, 170, 0.35);

    border-radius: 22px;

    box-shadow:
        0 25px 70px
        rgba(0, 0, 0, 0.35);
}


.ax-future-intelligence::before {
    content: "";

    position: absolute;

    left: 0;
    right: 0;
    bottom: 0;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--axd-cyan),
            var(--axd-purple),
            var(--axd-red),
            transparent
        );

    opacity: 0.7;
}


.ax-future-intelligence-copy h2 {
    margin:
        12px
        0
        0;

    color:
        var(--axd-white);

    font-size:
        clamp(32px, 3vw, 49px);

    line-height: 0.98;

    font-weight: 950;

    letter-spacing: -2px;
}


.ax-future-intelligence-copy h2 span {
    display: block;

    color:
        var(--axd-cyan);

    text-shadow:
        0 0 22px
        rgba(32, 221, 245, 0.18);
}


.ax-future-intelligence-copy p {
    max-width: 550px;

    margin-top: 16px;

    color:
        #95a2bf;

    font-size: 11px;
    line-height: 1.65;
}


.ax-future-feature-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 9px;

    margin-top: 20px;
}


.ax-future-feature-grid div {
    display: flex;
    align-items: center;

    gap: 9px;

    padding:
        12px;

    color:
        #e3e9f8;

    font-size: 9px;
    font-weight: 780;

    background:
        rgba(4, 10, 25, 0.72);

    border:
        1px solid
        rgba(68, 99, 161, 0.24);

    border-radius: 11px;

    transition:
        transform 0.18s ease,
        border-color 0.18s ease;
}


.ax-future-feature-grid div:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(32, 221, 245, 0.42);
}


.ax-future-feature-grid i {
    color:
        var(--axd-cyan);

    font-size: 14px;
    font-style: normal;
}


.ax-future-market-visual {
    position: relative;

    min-height: 235px;

    display: flex;
    align-items: center;
    justify-content: center;

    gap: 13px;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 28% 50%,
            rgba(0, 245, 138, 0.14),
            transparent 35%
        ),
        radial-gradient(
            circle at 73% 50%,
            rgba(255, 23, 68, 0.14),
            transparent 35%
        );

    border:
        1px solid
        rgba(69, 101, 166, 0.16);

    border-radius: 18px;
}


.ax-future-market-visual::before,
.ax-future-market-visual::after {
    content: "";

    position: absolute;

    width: 115px;
    height: 115px;

    border-radius:
        52% 48% 47% 53%;

    opacity: 0.22;
}


.ax-future-market-visual::before {
    left: 8%;

    background:
        linear-gradient(
            145deg,
            transparent,
            var(--axd-green)
        );

    filter:
        blur(5px);

    transform:
        rotate(-26deg);
}


.ax-future-market-visual::after {
    right: 8%;

    background:
        linear-gradient(
            145deg,
            var(--axd-red),
            transparent
        );

    filter:
        blur(5px);

    transform:
        rotate(26deg);
}


.ax-future-bull,
.ax-future-bear {
    position: relative;
    z-index: 2;

    font-size:
        clamp(20px, 2vw, 33px);

    font-weight: 950;

    letter-spacing: 1px;
}


.ax-future-bull {
    color:
        var(--axd-green);

    text-shadow:
        0 0 25px
        rgba(0, 245, 138, 0.48);
}


.ax-future-bear {
    color:
        var(--axd-red);

    text-shadow:
        0 0 25px
        rgba(255, 23, 68, 0.48);
}


.ax-future-center-logo {
    position: relative;
    z-index: 3;

    width: 76px;
    height: 76px;

    display: grid;
    place-items: center;

    color:
        white;

    font-size: 32px;
    font-weight: 950;

    background:
        linear-gradient(
            145deg,
            rgba(32, 221, 245, 0.2),
            rgba(139, 77, 255, 0.28)
        );

    border:
        1px solid
        rgba(104, 139, 218, 0.45);

    border-radius: 21px;

    box-shadow:
        0 0 42px
        rgba(54, 124, 255, 0.28);
}


.ax-future-market-line {
    position: absolute;

    left: 4%;
    right: 4%;
    bottom: 23%;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--axd-green),
            var(--axd-blue),
            var(--axd-purple),
            var(--axd-red),
            transparent
        );

    box-shadow:
        0 0 20px
        rgba(54, 124, 255, 0.38);

    transform:
        rotate(-3deg);
}


.ax-future-global-stats {
    display: grid;

    grid-template-columns: 1fr;

    gap: 10px;

    align-content: center;
}


.ax-future-global-stats div {
    padding:
        15px;

    text-align: center;

    background:
        rgba(4, 10, 25, 0.78);

    border:
        1px solid
        rgba(68, 98, 160, 0.25);

    border-radius: 13px;
}


.ax-future-global-stats strong {
    display: block;

    color:
        var(--axd-cyan);

    font-size: 19px;
    font-weight: 950;
}


.ax-future-global-stats span {
    display: block;

    margin-top: 5px;

    color:
        #7d8aa7;

    font-size: 8px;
}


/* ========================================================
   BOTONES
   ======================================================== */

.stButton > button {
    min-height: 43px;

    color:
        white !important;

    font-size:
        12px !important;

    font-weight:
        850 !important;

    background:
        linear-gradient(
            95deg,
            var(--axd-cyan),
            var(--axd-blue),
            var(--axd-purple)
        ) !important;

    border:
        1px solid
        rgba(99, 219, 255, 0.4) !important;

    border-radius:
        11px !important;

    box-shadow:
        0 10px 26px
        rgba(54, 124, 255, 0.14);

    transition:
        transform 0.18s ease,
        filter 0.18s ease,
        box-shadow 0.18s ease;
}


.stButton > button:hover {
    transform:
        translateY(-2px);

    filter:
        brightness(1.08)
        saturate(1.08);

    box-shadow:
        0 15px 34px
        rgba(54, 124, 255, 0.24);
}


.stButton > button[kind="secondary"] {
    background:
        linear-gradient(
            145deg,
            rgba(10, 18, 40, 0.985),
            rgba(5, 10, 25, 0.985)
        ) !important;

    border:
        1px solid
        rgba(76, 104, 169, 0.37) !important;

    box-shadow:
        none;
}


/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 1300px) {

    .ax-future-intelligence {
        grid-template-columns:
            1.2fr
            0.8fr;
    }

    .ax-future-global-stats {
        grid-column:
            1 / -1;

        grid-template-columns:
            repeat(4, 1fr);
    }
}


@media (max-width: 900px) {

    .block-container {
        padding-left:
            1rem !important;

        padding-right:
            1rem !important;
    }

    .ax-future-header {
        align-items:
            flex-start;
    }

    .ax-future-intelligence {
        grid-template-columns:
            1fr;
    }

    .ax-future-global-stats {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .ax-future-feature-grid {
        grid-template-columns:
            1fr;
    }

    .ax-dashboard-candles {
        left: 0;

        opacity: 0.25;
    }
}


@media (max-width: 560px) {

    .ax-future-global-stats {
        grid-template-columns:
            1fr;
    }

    .ax-future-header h1 {
        font-size:
            29px;
    }
}


/* ========================================================
   REDUCIR ANIMACIÓN
   ======================================================== */

@media (prefers-reduced-motion: reduce) {

    *,
    *::before,
    *::after {
        animation-duration:
            0.001ms !important;

        animation-iteration-count:
            1 !important;
    }
}

</style>
"""


# =========================================================
# FUNCIÓN PARA APLICAR LOS ESTILOS
# =========================================================


def apply_dashboard_styles() -> None:
    """
    Aplica únicamente los estilos del dashboard.
    No altera el login ni la pantalla de perfil.
    """

    st.markdown(
        DASHBOARD_CSS,
        unsafe_allow_html=True,
    )
