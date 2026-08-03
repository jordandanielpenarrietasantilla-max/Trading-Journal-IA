from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# ESTILOS FUTURISTAS GLOBALES
# =========================================================


GLOBAL_CSS = """
<style>

/* ========================================================
   VARIABLES
   ======================================================== */

:root {
    --ax-bg: #020611;
    --ax-bg-2: #050a17;
    --ax-panel: rgba(5, 13, 29, 0.96);
    --ax-panel-soft: rgba(8, 17, 37, 0.92);

    --ax-border: rgba(63, 105, 177, 0.34);
    --ax-border-soft: rgba(72, 100, 165, 0.22);

    --ax-white: #f6f8ff;
    --ax-text: #e8eefc;
    --ax-muted: #8e9ab8;
    --ax-dim: #596582;

    --ax-cyan: #20ddf5;
    --ax-blue: #367cff;
    --ax-purple: #8b4dff;
    --ax-green: #00f58a;
    --ax-red: #ff1744;

    --ax-radius: 16px;
}


/* ========================================================
   BASE
   ======================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    color: var(--ax-text);

    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(32, 221, 245, 0.09),
            transparent 27%
        ),
        radial-gradient(
            circle at 88% 10%,
            rgba(139, 77, 255, 0.14),
            transparent 31%
        ),
        linear-gradient(
            135deg,
            #020611,
            #040818 52%,
            #09041b
        ) !important;
}


html,
body,
button,
input,
textarea,
select,
label,
p,
span,
div {
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    position: relative;
    z-index: 2;
}


[data-testid="stHeader"] {
    background:
        rgba(2, 6, 17, 0.91) !important;

    border-bottom:
        1px solid
        rgba(73, 101, 166, 0.16);

    backdrop-filter:
        blur(16px);
}


.block-container {
    width: 100%;
    max-width: 1740px;

    padding-top: 1.4rem;
    padding-bottom: 3rem;
}


/* ========================================================
   CUADRÍCULA DE MERCADO
   ======================================================== */

[data-testid="stAppViewContainer"]::after {
    content: "";

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(83, 112, 177, 0.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(83, 112, 177, 0.035) 1px,
            transparent 1px
        );

    background-size:
        52px 52px;

    opacity: 0.65;
}


/* ========================================================
   VELAS JAPONESAS PEQUEÑAS
   ======================================================== */

[data-testid="stAppViewContainer"]::before {
    content: "";

    position: fixed;
    left: 200px;
    right: 0;
    top: 72px;
    height: 145px;

    z-index: 1;
    pointer-events: none;

    opacity: 0.42;

    background-image:

        linear-gradient(
            to bottom,
            transparent 0 16%,
            rgba(0, 245, 138, 0.85) 16% 84%,
            transparent 84%
        ),

        linear-gradient(
            to bottom,
            transparent 0 35%,
            rgba(0, 245, 138, 1) 35% 63%,
            transparent 63%
        ),

        linear-gradient(
            to bottom,
            transparent 0 10%,
            rgba(255, 23, 68, 0.85) 10% 88%,
            transparent 88%
        ),

        linear-gradient(
            to bottom,
            transparent 0 30%,
            rgba(255, 23, 68, 1) 30% 61%,
            transparent 61%
        );

    background-size:
        1px 92px,
        8px 92px,
        1px 108px,
        8px 108px;

    background-position:
        30px 15px,
        27px 15px,
        105px 25px,
        102px 25px;

    background-repeat:
        repeat-x;

    filter:
        drop-shadow(
            0 0 6px
            rgba(0, 245, 138, 0.28)
        )
        drop-shadow(
            0 0 6px
            rgba(255, 23, 68, 0.25)
        );

    animation:
        ax-candle-drift
        42s
        linear
        infinite;
}


@keyframes ax-candle-drift {
    from {
        background-position:
            30px 15px,
            27px 15px,
            105px 25px,
            102px 25px;
    }

    to {
        background-position:
            990px 15px,
            987px 15px,
            1065px 25px,
            1062px 25px;
    }
}


/* ========================================================
   SIDEBAR
   ======================================================== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 50% -5%,
            rgba(32, 221, 245, 0.11),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            rgba(3, 9, 23, 0.995),
            rgba(2, 6, 17, 0.995)
        ) !important;

    border-right:
        1px solid
        rgba(63, 95, 160, 0.30);
}


[data-testid="stSidebarContent"] {
    padding:
        1.05rem
        0.85rem
        1.5rem;
}


.ax-brand {
    display: flex;
    align-items: center;
    gap: 12px;

    padding:
        7px 5px 19px;

    margin-bottom: 15px;

    border-bottom:
        1px solid
        rgba(79, 104, 166, 0.18);
}


.ax-logo {
    width: 46px;
    height: 46px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    color: white;
    font-size: 18px;
    font-weight: 950;

    border-radius: 14px;

    background:
        linear-gradient(
            145deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        );

    box-shadow:
        0 0 24px
        rgba(32, 221, 245, 0.30);
}


.ax-brand b {
    display: block;

    color: var(--ax-white);

    font-size: 13px;
    font-weight: 950;
}


.ax-brand small {
    display: block;

    margin-top: 4px;

    color: var(--ax-dim);

    font-size: 6px;
    font-weight: 850;

    letter-spacing: 1.5px;
}


.ax-brand-online {
    width: 7px;
    height: 7px;

    margin-left: auto;

    border-radius: 50%;

    background: var(--ax-green);

    box-shadow:
        0 0 12px
        var(--ax-green);
}


.ax-profile {
    padding: 15px;
    margin-bottom: 10px;

    background:
        linear-gradient(
            145deg,
            rgba(8, 18, 42, 0.98),
            rgba(4, 10, 25, 0.98)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.30);

    border-radius: 18px;

    box-shadow:
        0 16px 45px
        rgba(0, 0, 0, 0.25);
}


.ax-profile-top {
    display: flex;
    align-items: center;
    gap: 11px;
}


.ax-profile-avatar {
    width: 54px;
    height: 54px;

    display: grid;
    place-items: center;

    flex-shrink: 0;
    overflow: hidden;

    color: white;
    font-weight: 950;

    border-radius: 50%;

    background:
        linear-gradient(
            145deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        );

    border:
        2px solid
        rgba(255, 255, 255, 0.12);

    box-shadow:
        0 0 21px
        rgba(32, 221, 245, 0.31);
}


.ax-profile-photo {
    padding: 0;
}


.ax-profile-photo img {
    width: 100%;
    height: 100%;

    display: block;

    object-fit: cover;
    object-position: center;

    border-radius: 50%;
}


.ax-profile-identity {
    min-width: 0;
    flex: 1;
}


.ax-profile-name-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 6px;

    color: var(--ax-white);

    font-size: 12px;
}


.ax-profile-role {
    padding:
        3px
        7px;

    color: white;

    font-size: 6px;
    font-weight: 950;

    background:
        linear-gradient(
            90deg,
            var(--ax-purple),
            #ad43ff
        );

    border-radius: 999px;
}


.ax-profile-email {
    overflow: hidden;

    margin-top: 4px;

    color: #65718f;

    font-size: 7px;

    text-overflow: ellipsis;
    white-space: nowrap;
}


.ax-profile-capital-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;

    margin-top: 14px;
}


.ax-profile-capital {
    color: var(--ax-white);

    font-size: 18px;
    font-weight: 950;
}


.ax-profile-capital-label {
    margin-top: 4px;

    color: var(--ax-cyan);

    font-size: 6px;
    font-weight: 900;

    letter-spacing: 1.35px;
}


.ax-profile-target {
    color: #6d7996;

    font-size: 6px;
}


.ax-progress-track {
    height: 4px;

    overflow: hidden;

    margin-top: 10px;

    background: #16203a;

    border-radius: 999px;
}


.ax-progress-value {
    height: 100%;

    background:
        linear-gradient(
            90deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        );

    border-radius: 999px;
}


.ax-progress-labels {
    display: flex;
    justify-content: space-between;

    margin-top: 6px;

    color: #62708f;

    font-size: 6px;
}


.ax-section-title {
    margin:
        22px
        4px
        9px;

    color: #5e6c89;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 2px;
}


.ax-system-card {
    padding: 13px;

    background:
        rgba(6, 11, 27, 0.90);

    border:
        1px solid
        rgba(72, 97, 157, 0.24);

    border-radius: 14px;
}


.ax-system-row {
    display: flex;
    justify-content: space-between;

    margin-bottom: 10px;

    color: #dae3f8;

    font-size: 8px;
}


.ax-system-row:last-child {
    margin-bottom: 0;
}


.ax-system-row b {
    color: var(--ax-green);

    font-size: 7px;
}


/* ========================================================
   BOTONES
   ======================================================== */

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 42px;

    color: white !important;

    font-size: 12px !important;
    font-weight: 850 !important;

    background:
        linear-gradient(
            95deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        ) !important;

    border:
        1px solid
        rgba(92, 217, 255, 0.39) !important;

    border-radius:
        10px !important;

    transition:
        transform 0.18s ease,
        filter 0.18s ease,
        box-shadow 0.18s ease;
}


.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform:
        translateY(-2px);

    filter:
        brightness(1.08)
        saturate(1.08);

    box-shadow:
        0 12px 30px
        rgba(54, 124, 255, 0.22);
}


.stButton > button[kind="secondary"] {
    background:
        linear-gradient(
            145deg,
            rgba(10, 18, 40, 0.98),
            rgba(5, 10, 25, 0.98)
        ) !important;

    border:
        1px solid
        rgba(76, 102, 165, 0.36) !important;
}


/* ========================================================
   CABECERA FUTURISTA
   ======================================================== */

.ax-future-header {
    position: relative;

    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 24px;
    flex-wrap: wrap;

    overflow: hidden;

    padding:
        26px
        29px;

    margin-bottom: 18px;

    background:
        radial-gradient(
            circle at 83% 15%,
            rgba(139, 77, 255, 0.20),
            transparent 36%
        ),
        linear-gradient(
            135deg,
            rgba(3, 14, 33, 0.98),
            rgba(13, 7, 39, 0.97)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.43);

    border-radius: 22px;

    box-shadow:
        0 24px 70px
        rgba(0, 0, 0, 0.37);
}


.ax-future-header::after {
    content: "";

    position: absolute;
    right: 0;
    top: 0;

    width: 42%;
    height: 100%;

    pointer-events: none;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(32, 221, 245, 0.035),
            transparent
        );
}


.ax-future-kicker {
    color: var(--ax-cyan);

    font-size: 8px;
    font-weight: 950;

    letter-spacing: 2px;
}


.ax-future-header h1 {
    margin:
        8px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(29px, 3vw, 44px);

    line-height: 1.05;
    font-weight: 950;

    letter-spacing: -1.8px;
}


.ax-future-header p {
    margin:
        8px
        0
        0;

    color: var(--ax-muted);

    font-size: 12px;
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

    color: #e2e8f8;

    font-size: 9px;
    font-weight: 850;
}


.ax-future-date span {
    width: 1px;
    height: 13px;

    background:
        rgba(105, 123, 169, 0.45);
}


.ax-future-market-status {
    display: flex;
    align-items: center;

    gap: 7px;

    padding:
        8px
        13px;

    color: var(--ax-green);

    font-size: 7px;
    font-weight: 950;

    background:
        rgba(0, 245, 138, 0.07);

    border:
        1px solid
        rgba(0, 245, 138, 0.34);

    border-radius: 999px;
}


.ax-future-market-status i {
    width: 7px;
    height: 7px;

    display: block;

    border-radius: 50%;

    background: var(--ax-green);

    box-shadow:
        0 0 11px
        var(--ax-green);
}


/* ========================================================
   MÉTRICAS FUTURISTAS
   ======================================================== */

.ax-future-metric {
    min-height: 158px;

    display: flex;
    flex-direction: column;

    padding: 15px;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 10% 0%,
            rgba(32, 221, 245, 0.06),
            transparent 42%
        ),
        linear-gradient(
            145deg,
            rgba(7, 17, 38, 0.98),
            rgba(4, 10, 25, 0.98)
        );

    border:
        1px solid
        rgba(66, 100, 166, 0.32);

    border-radius: 16px;

    box-shadow:
        0 16px 45px
        rgba(0, 0, 0, 0.29);

    transition:
        transform 0.18s ease,
        border-color 0.18s ease;
}


.ax-future-metric:hover {
    transform:
        translateY(-3px);

    border-color:
        rgba(32, 221, 245, 0.48);
}


.ax-future-metric-head {
    display: flex;
    align-items: center;

    gap: 11px;
}


.ax-future-metric-icon {
    width: 40px;
    height: 40px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    border:
        1px solid;

    border-radius: 11px;

    font-size: 19px;
    font-weight: 950;
}


.ax-future-metric-label {
    color: #818da9;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 1.35px;
}


.ax-future-metric-value {
    margin-top: 6px;

    font-size:
        clamp(20px, 1.6vw, 28px);

    line-height: 1;
    font-weight: 950;

    white-space: nowrap;
}


.ax-future-metric-meta {
    display: flex;
    justify-content: space-between;

    gap: 8px;

    margin-top: 12px;

    color: #75819e;

    font-size: 7px;
}


.ax-future-sparkline {
    width: 100%;
    height: 39px;

    margin-top: auto;
}


/* ========================================================
   TÍTULOS DE PANELES
   ======================================================== */

.ax-future-panel-title {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 10px;

    padding:
        13px
        15px;

    margin-top: 16px;
    margin-bottom: 9px;

    background:
        linear-gradient(
            145deg,
            rgba(7, 15, 33, 0.98),
            rgba(5, 10, 25, 0.98)
        );

    border:
        1px solid
        rgba(67, 98, 160, 0.30);

    border-radius: 14px;
}


.ax-future-panel-title > div {
    display: flex;
    align-items: center;

    gap: 8px;
}


.ax-future-panel-title strong {
    color: var(--ax-white);

    font-size: 12px;
}


.ax-future-panel-title > div > span {
    color: var(--ax-cyan);

    font-size: 14px;
}


.ax-future-panel-title small {
    color: #64718e;

    font-size: 6px;

    letter-spacing: 1.2px;
}


/* ========================================================
   PLOTLY
   ======================================================== */

[data-testid="stPlotlyChart"] {
    overflow: hidden;

    padding: 6px;

    background:
        radial-gradient(
            circle at 50% 100%,
            rgba(32, 221, 245, 0.06),
            transparent 45%
        ),
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.97),
            rgba(4, 9, 23, 0.97)
        );

    border:
        1px solid
        rgba(66, 98, 160, 0.30);

    border-radius: 16px;
}


/* ========================================================
   TABLA FUTURISTA
   ======================================================== */

.ax-future-table-shell {
    width: 100%;

    overflow: hidden;

    min-height: 430px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.98),
            rgba(4, 9, 23, 0.98)
        );

    border:
        1px solid
        rgba(66, 98, 160, 0.30);

    border-radius: 16px;
}


.ax-future-table {
    width: 100%;

    border-collapse: collapse;

    color: var(--ax-text);

    font-size: 10px;
}


.ax-future-table th {
    padding:
        13px
        10px;

    color: #71809f;

    font-size: 7px;
    font-weight: 950;

    text-align: left;

    letter-spacing: 1px;

    background:
        rgba(8, 17, 38, 0.98);

    border-bottom:
        1px solid
        rgba(68, 96, 155, 0.27);
}


.ax-future-table td {
    padding:
        13px
        10px;

    white-space: nowrap;

    border-bottom:
        1px solid
        rgba(68, 96, 155, 0.13);
}


.ax-future-table tr:last-child td {
    border-bottom: none;
}


.ax-future-table tbody tr:hover {
    background:
        rgba(32, 221, 245, 0.04);
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
    color: var(--ax-green);

    background:
        rgba(0, 245, 138, 0.12);

    border:
        1px solid
        rgba(0, 245, 138, 0.25);
}


.ax-future-short {
    color: #ff758d;

    background:
        rgba(255, 23, 68, 0.13);

    border:
        1px solid
        rgba(255, 23, 68, 0.27);
}


.ax-future-neutral {
    color: var(--ax-muted);

    background:
        rgba(125, 141, 176, 0.11);
}


.ax-future-win {
    color: var(--ax-green);

    background:
        rgba(0, 245, 138, 0.12);
}


.ax-future-loss {
    color: #ff758d;

    background:
        rgba(255, 23, 68, 0.14);
}


.ax-future-be {
    color: #c1cae0;

    background:
        rgba(130, 145, 179, 0.11);
}


.ax-future-pnl {
    font-weight: 950;
}


/* ========================================================
   SETUP E IMÁGENES
   ======================================================== */

[data-testid="stImage"] {
    overflow: hidden;

    padding: 7px;

    background:
        rgba(5, 11, 27, 0.96);

    border:
        1px solid
        rgba(67, 98, 160, 0.30);

    border-radius: 16px;
}


[data-testid="stImage"] img {
    border-radius: 11px;
}


/* ========================================================
   RESUMEN
   ======================================================== */

.ax-future-summary {
    padding: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.97),
            rgba(4, 9, 23, 0.97)
        );

    border:
        1px solid
        rgba(66, 98, 160, 0.30);

    border-radius: 16px;
}


.ax-future-summary-row {
    display: flex;
    justify-content: space-between;

    gap: 12px;

    padding:
        9px 0;

    color: #8c98b5;

    font-size: 9px;

    border-bottom:
        1px solid
        rgba(67, 96, 156, 0.14);
}


.ax-future-summary-row:last-child {
    border-bottom: none;
}


.ax-future-summary-row strong {
    font-size: 10px;
}


/* ========================================================
   VACÍOS
   ======================================================== */

.ax-future-empty {
    min-height: 300px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    padding: 22px;

    text-align: center;

    background:
        rgba(5, 11, 27, 0.94);

    border:
        1px dashed
        rgba(32, 221, 245, 0.30);

    border-radius: 16px;
}


.ax-future-empty > div {
    color: var(--ax-cyan);

    font-size: 31px;
}


.ax-future-empty strong {
    margin-top: 11px;

    color: var(--ax-white);

    font-size: 13px;
}


.ax-future-empty p {
    margin-top: 7px;

    color: #7b88a5;

    font-size: 9px;
    line-height: 1.5;
}


.ax-future-setup-empty {
    min-height: 245px;
}


/* ========================================================
   BANNER INTELIGENCIA
   ======================================================== */

.ax-future-intelligence {
    position: relative;

    display: grid;

    grid-template-columns:
        1.15fr
        0.9fr
        0.85fr;

    gap: 22px;

    overflow: hidden;

    margin-top: 20px;
    padding: 27px;

    background:
        radial-gradient(
            circle at 60% 50%,
            rgba(32, 221, 245, 0.10),
            transparent 28%
        ),
        radial-gradient(
            circle at 82% 50%,
            rgba(255, 23, 68, 0.10),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            rgba(4, 14, 32, 0.98),
            rgba(10, 6, 31, 0.98)
        );

    border:
        1px solid
        rgba(65, 101, 168, 0.34);

    border-radius: 22px;

    box-shadow:
        0 25px 70px
        rgba(0, 0, 0, 0.34);
}


.ax-future-intelligence-copy h2 {
    margin:
        12px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(32px, 3vw, 48px);

    line-height: 0.98;
    font-weight: 950;

    letter-spacing: -2px;
}


.ax-future-intelligence-copy h2 span {
    display: block;

    color: var(--ax-cyan);
}


.ax-future-intelligence-copy p {
    max-width: 540px;

    margin-top: 15px;

    color: #95a1be;

    font-size: 11px;
    line-height: 1.65;
}


.ax-future-feature-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 9px;

    margin-top: 19px;
}


.ax-future-feature-grid div {
    display: flex;
    align-items: center;

    gap: 8px;

    padding: 11px;

    color: #e2e8f7;

    font-size: 9px;
    font-weight: 780;

    background:
        rgba(4, 10, 25, 0.70);

    border:
        1px solid
        rgba(68, 96, 155, 0.23);

    border-radius: 11px;
}


.ax-future-feature-grid i {
    color: var(--ax-cyan);

    font-size: 14px;
    font-style: normal;
}


.ax-future-market-visual {
    position: relative;

    min-height: 230px;

    display: flex;
    align-items: center;
    justify-content: center;

    gap: 12px;

    overflow: hidden;

    border-radius: 18px;

    background:
        radial-gradient(
            circle at 32% 50%,
            rgba(0, 245, 138, 0.13),
            transparent 33%
        ),
        radial-gradient(
            circle at 72% 50%,
            rgba(255, 23, 68, 0.13),
            transparent 33%
        );
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
    color: var(--ax-green);

    text-shadow:
        0 0 24px
        rgba(0, 245, 138, 0.45);
}


.ax-future-bear {
    color: var(--ax-red);

    text-shadow:
        0 0 24px
        rgba(255, 23, 68, 0.45);
}


.ax-future-center-logo {
    position: relative;
    z-index: 2;

    width: 72px;
    height: 72px;

    display: grid;
    place-items: center;

    color: white;

    font-size: 31px;
    font-weight: 950;

    background:
        linear-gradient(
            145deg,
            rgba(32, 221, 245, 0.18),
            rgba(139, 77, 255, 0.25)
        );

    border:
        1px solid
        rgba(102, 137, 215, 0.42);

    border-radius: 20px;

    box-shadow:
        0 0 38px
        rgba(54, 124, 255, 0.25);
}


.ax-future-market-line {
    position: absolute;
    left: 5%;
    right: 5%;
    bottom: 25%;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent,
            var(--ax-green),
            var(--ax-blue),
            var(--ax-purple),
            var(--ax-red),
            transparent
        );

    box-shadow:
        0 0 18px
        rgba(54, 124, 255, 0.35);

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
    padding: 14px;

    text-align: center;

    background:
        rgba(4, 10, 25, 0.76);

    border:
        1px solid
        rgba(68, 96, 155, 0.24);

    border-radius: 13px;
}


.ax-future-global-stats strong {
    display: block;

    color: var(--ax-cyan);

    font-size: 19px;
    font-weight: 950;
}


.ax-future-global-stats span {
    display: block;

    margin-top: 5px;

    color: #7c89a6;

    font-size: 8px;
}


/* ========================================================
   INPUTS
   ======================================================== */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    color: var(--ax-white) !important;

    background:
        rgba(4, 10, 25, 0.97) !important;

    border:
        1px solid
        rgba(89, 112, 171, 0.42) !important;

    border-radius:
        10px !important;
}


[data-baseweb="select"] > div {
    color: var(--ax-white) !important;

    background:
        rgba(4, 10, 25, 0.97) !important;

    border-color:
        rgba(89, 112, 171, 0.42) !important;

    border-radius:
        10px !important;
}


label,
[data-testid="stWidgetLabel"] {
    color: #dce4f7 !important;

    font-size: 11px !important;
}


/* ========================================================
   OTROS
   ======================================================== */

[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        rgba(6, 12, 29, 0.74);

    border-color:
        rgba(75, 99, 158, 0.25) !important;

    border-radius: 15px;
}


[data-testid="stAlert"] {
    border:
        1px solid
        rgba(91, 109, 167, 0.24);

    border-radius: 12px;
}


[data-testid="stFileUploader"] {
    padding: 10px;

    background:
        rgba(5, 11, 28, 0.82);

    border:
        1px dashed
        rgba(32, 221, 245, 0.35);

    border-radius: 14px;
}


/* ========================================================
   SCROLLBAR
   ======================================================== */

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}


::-webkit-scrollbar-track {
    background: #040713;
}


::-webkit-scrollbar-thumb {
    background:
        linear-gradient(
            var(--ax-cyan),
            var(--ax-purple)
        );

    border:
        2px solid
        #040713;

    border-radius: 999px;
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


@media (max-width: 850px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .ax-future-header {
        align-items: flex-start;
    }

    .ax-future-intelligence {
        grid-template-columns: 1fr;
    }

    .ax-future-global-stats {
        grid-template-columns:
            repeat(2, 1fr);
    }

    .ax-future-feature-grid {
        grid-template-columns: 1fr;
    }

    [data-testid="stAppViewContainer"]::before {
        left: 0;
        opacity: 0.20;
    }
}


@media (max-width: 560px) {

    .ax-future-global-stats {
        grid-template-columns: 1fr;
    }

    .ax-future-header h1 {
        font-size: 29px;
    }
}


/* ========================================================
   CHAT IA — CONTRASTE, BURBUJAS Y CAMPO DE ESCRITURA
   ======================================================== */

[data-testid="stChatMessage"] {
    position: relative;
    overflow: hidden;
    padding: 16px 18px !important;
    margin-bottom: 13px !important;
    color: var(--ax-white) !important;
    background:
        linear-gradient(
            145deg,
            rgba(8, 18, 40, 0.97),
            rgba(5, 11, 28, 0.97)
        ) !important;
    border:
        1px solid
        rgba(76, 110, 183, 0.34) !important;
    border-radius: 18px !important;
    box-shadow:
        0 14px 40px
        rgba(0, 0, 0, 0.26) !important;
    opacity: 1 !important;
    filter: none !important;
    mix-blend-mode: normal !important;
}

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarUser"]
) {
    background:
        linear-gradient(
            145deg,
            rgba(26, 51, 90, 0.98),
            rgba(16, 31, 61, 0.98)
        ) !important;
    border-color:
        rgba(32, 221, 245, 0.40) !important;
}

[data-testid="stChatMessage"]:has(
    [data-testid="stChatMessageAvatarAssistant"]
) {
    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(139, 77, 255, 0.10),
            transparent 35%
        ),
        linear-gradient(
            145deg,
            rgba(8, 15, 34, 0.98),
            rgba(10, 7, 31, 0.98)
        ) !important;
    border-color:
        rgba(139, 77, 255, 0.38) !important;
}

[data-testid="stChatMessage"],
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] label,
[data-testid="stChatMessage"] small,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4,
[data-testid="stChatMessage"] h5,
[data-testid="stChatMessage"] h6 {
    color: var(--ax-white) !important;
    opacity: 1 !important;
    visibility: visible !important;
    text-shadow: none !important;
    filter: none !important;
    mix-blend-mode: normal !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] * {
    color: var(--ax-white) !important;
    opacity: 1 !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] p {
    margin: 0 0 10px !important;
    color: #eef3ff !important;
    font-size: 14px !important;
    line-height: 1.72 !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] p:last-child {
    margin-bottom: 0 !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] strong {
    color: var(--ax-cyan) !important;
    font-weight: 900 !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] a {
    color: #63e9ff !important;
    text-decoration: underline !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] ul,
[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] ol {
    margin: 8px 0 12px !important;
    padding-left: 24px !important;
    color: #eef3ff !important;
}

[data-testid="stChatMessage"]
[data-testid="stMarkdownContainer"] li {
    margin-bottom: 7px !important;
    color: #eef3ff !important;
    line-height: 1.62 !important;
}

[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {
    opacity: 1 !important;
    filter: none !important;
}

[data-testid="stChatMessage"] code {
    color: #93f5ff !important;
    background: rgba(2, 8, 22, 0.96) !important;
    border:
        1px solid
        rgba(32, 221, 245, 0.26) !important;
    border-radius: 7px !important;
    padding: 2px 6px !important;
}

[data-testid="stChatMessage"] pre {
    overflow-x: auto;
    padding: 14px !important;
    color: #edf6ff !important;
    background: #030916 !important;
    border:
        1px solid
        rgba(32, 221, 245, 0.26) !important;
    border-radius: 12px !important;
}

[data-testid="stChatMessage"] pre code {
    padding: 0 !important;
    color: #edf6ff !important;
    background: transparent !important;
    border: none !important;
}

[data-testid="stChatInput"] {
    overflow: hidden;
    color: var(--ax-white) !important;
    background:
        linear-gradient(
            145deg,
            rgba(7, 16, 37, 0.99),
            rgba(4, 10, 25, 0.99)
        ) !important;
    border:
        1px solid
        rgba(32, 221, 245, 0.42) !important;
    border-radius: 17px !important;
    box-shadow:
        0 16px 48px
        rgba(0, 0, 0, 0.34) !important;
}

[data-testid="stChatInput"] textarea {
    color: var(--ax-white) !important;
    background: transparent !important;
    caret-color: var(--ax-cyan) !important;
    opacity: 1 !important;
    filter: none !important;
}

[data-testid="stChatInput"] textarea::placeholder {
    color: #8795b5 !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button {
    color: white !important;
    background:
        linear-gradient(
            145deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        ) !important;
    border:
        1px solid
        rgba(255, 255, 255, 0.10) !important;
    border-radius: 12px !important;
    opacity: 1 !important;
}

[data-testid="stChatInput"] button:hover {
    filter:
        brightness(1.10)
        saturate(1.08) !important;
}

[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"] {
    color: var(--ax-white) !important;
    background: transparent !important;
}

[data-testid="stChatMessage"] *,
[data-testid="stChatInput"] * {
    text-shadow: none !important;
}

</style>
"""


# =========================================================
# FUNCIÓN PRINCIPAL OBLIGATORIA
# =========================================================


def apply_styles() -> None:
    """
    Aplica todos los estilos de AXION PRIME.
    """

    st.html(
        GLOBAL_CSS
    )
