from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# SISTEMA VISUAL COMMAND CENTER
# =========================================================


GLOBAL_CSS = """
<style>

/* ========================================================
   VARIABLES
   ======================================================== */

:root {
    --ax-bg: #020611;
    --ax-bg-soft: #050b18;
    --ax-panel: rgba(6, 14, 30, 0.96);
    --ax-panel-2: rgba(8, 18, 38, 0.94);

    --ax-border: rgba(56, 101, 170, 0.34);
    --ax-border-soft: rgba(72, 96, 150, 0.22);

    --ax-white: #f6f8ff;
    --ax-text: #e8eefc;
    --ax-muted: #8895b3;
    --ax-dim: #586682;

    --ax-cyan: #20ddf5;
    --ax-blue: #367cff;
    --ax-purple: #8b4dff;
    --ax-green: #00f58a;
    --ax-red: #ff1744;

    --ax-radius-sm: 10px;
    --ax-radius-md: 15px;
    --ax-radius-lg: 22px;
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
            transparent 26%
        ),
        radial-gradient(
            circle at 90% 14%,
            rgba(139, 77, 255, 0.13),
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
        rgba(61, 88, 146, 0.16);

    backdrop-filter:
        blur(16px);
}


.block-container {
    width: 100%;
    max-width: 1720px;

    padding-top: 1.4rem;
    padding-bottom: 3rem;
}


/* ========================================================
   FONDO CON VELAS PEQUEÑAS
   ======================================================== */

[data-testid="stAppViewContainer"]::before {
    content: "";

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    opacity: 0.22;

    background-image:
        linear-gradient(
            to bottom,
            transparent 0 25%,
            rgba(0, 245, 138, 0.75) 25% 75%,
            transparent 75%
        ),
        linear-gradient(
            to bottom,
            transparent 0 39%,
            rgba(0, 245, 138, 0.95) 39% 62%,
            transparent 62%
        ),
        linear-gradient(
            to bottom,
            transparent 0 18%,
            rgba(255, 23, 68, 0.74) 18% 82%,
            transparent 82%
        ),
        linear-gradient(
            to bottom,
            transparent 0 34%,
            rgba(255, 23, 68, 0.96) 34% 60%,
            transparent 60%
        );

    background-size:
        1px 88px,
        7px 88px,
        1px 108px,
        8px 108px;

    background-position:
        32px 125px,
        29px 125px,
        111px 270px,
        108px 270px;

    background-repeat:
        repeat-x;

    filter:
        drop-shadow(
            0 0 5px
            rgba(0, 245, 138, 0.25)
        )
        drop-shadow(
            0 0 5px
            rgba(255, 23, 68, 0.23)
        );

    animation:
        ax-candles-move
        48s
        linear
        infinite;
}


[data-testid="stAppViewContainer"]::after {
    content: "";

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(79, 106, 166, 0.035) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(79, 106, 166, 0.035) 1px,
            transparent 1px
        );

    background-size:
        52px 52px;

    opacity: 0.68;
}


@keyframes ax-candles-move {
    from {
        background-position:
            32px 125px,
            29px 125px,
            111px 270px,
            108px 270px;
    }

    to {
        background-position:
            992px 125px,
            989px 125px,
            1071px 270px,
            1068px 270px;
    }
}


/* ========================================================
   SIDEBAR
   ======================================================== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 50% -5%,
            rgba(32, 221, 245, 0.10),
            transparent 29%
        ),
        linear-gradient(
            180deg,
            rgba(3, 9, 23, 0.995),
            rgba(2, 6, 17, 0.995)
        ) !important;

    border-right:
        1px solid
        rgba(63, 94, 157, 0.29);
}


[data-testid="stSidebarContent"] {
    padding:
        1.05rem
        0.85rem
        1.4rem;
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
        rgba(79, 101, 157, 0.18);
}


.ax-logo {
    width: 45px;
    height: 45px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    border-radius: 13px;

    color: white;
    font-size: 18px;
    font-weight: 950;

    background:
        linear-gradient(
            145deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        );

    box-shadow:
        0 0 22px
        rgba(32, 221, 245, 0.29);
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
        rgba(32, 221, 245, 0.29);

    border-radius: 18px;
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

    border-radius: 50%;

    color: white;
    font-weight: 950;

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

    border-radius: 999px;

    color: white;

    background:
        linear-gradient(
            90deg,
            var(--ax-purple),
            #ad43ff
        );

    font-size: 6px;
    font-weight: 950;
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

    border-radius: 999px;

    background: #16203a;
}


.ax-progress-value {
    height: 100%;

    border-radius: 999px;

    background:
        linear-gradient(
            90deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        );
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

    border-radius:
        var(--ax-radius-sm) !important;

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

    transition:
        transform 0.18s ease,
        filter 0.18s ease;
}


.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform:
        translateY(-2px);

    filter:
        brightness(1.08)
        saturate(1.08);
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
   CABECERA DASHBOARD
   ======================================================== */

.ax-command-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    gap: 24px;
    flex-wrap: wrap;

    padding:
        24px
        28px;

    margin-bottom: 18px;

    background:
        radial-gradient(
            circle at 84% 18%,
            rgba(139, 77, 255, 0.18),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            rgba(4, 14, 33, 0.98),
            rgba(13, 7, 38, 0.96)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.40);

    border-radius:
        var(--ax-radius-lg);

    box-shadow:
        0 22px 60px
        rgba(0, 0, 0, 0.34);
}


.ax-command-kicker {
    color: var(--ax-cyan);

    font-size: 8px;
    font-weight: 950;

    letter-spacing: 2px;
}


.ax-command-header h1 {
    margin:
        8px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(28px, 3vw, 43px);

    line-height: 1.05;
    font-weight: 950;

    letter-spacing: -1.8px;
}


.ax-command-header p {
    margin:
        8px
        0
        0;

    color: var(--ax-muted);

    font-size: 12px;
}


.ax-command-header-actions {
    display: flex;
    align-items: center;

    gap: 12px;
    flex-wrap: wrap;
}


.ax-command-date {
    display: flex;
    align-items: center;

    gap: 8px;

    color: #dfe6f8;

    font-size: 9px;
    font-weight: 850;
}


.ax-command-date span {
    width: 1px;
    height: 13px;

    background:
        rgba(105, 123, 169, 0.45);
}


.ax-market-status {
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


.ax-market-status span {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: var(--ax-green);

    box-shadow:
        0 0 11px
        var(--ax-green);
}


/* ========================================================
   TARJETAS DE MÉTRICAS
   ======================================================== */

.ax-command-metric {
    min-height: 150px;

    display: flex;
    flex-direction: column;

    padding: 15px;

    overflow: hidden;

    background:
        linear-gradient(
            145deg,
            rgba(8, 18, 39, 0.97),
            rgba(4, 10, 25, 0.97)
        );

    border:
        1px solid
        rgba(67, 98, 159, 0.30);

    border-radius:
        var(--ax-radius-md);

    box-shadow:
        0 14px 38px
        rgba(0, 0, 0, 0.27);
}


.ax-command-metric-top {
    display: flex;
    align-items: center;

    gap: 11px;
}


.ax-command-metric-icon {
    width: 39px;
    height: 39px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    border:
        1px solid;

    border-radius: 10px;

    font-size: 19px;
    font-weight: 950;
}


.ax-command-metric-copy {
    min-width: 0;
}


.ax-command-metric-label {
    color: #818da9;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 1.35px;
}


.ax-command-metric-value {
    margin-top: 6px;

    font-size:
        clamp(21px, 1.65vw, 28px);

    line-height: 1;
    font-weight: 950;

    white-space: nowrap;
}


.ax-command-metric-meta {
    display: flex;
    justify-content: space-between;

    gap: 8px;

    margin-top: 12px;

    color: #75819e;

    font-size: 7px;
}


.ax-sparkline {
    width: 100%;
    height: 33px;

    margin-top: auto;
}


/* ========================================================
   TÍTULOS DE PANELES
   ======================================================== */

.ax-command-panel-title {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 10px;

    padding:
        13px
        15px;

    margin-top: 15px;
    margin-bottom: 9px;

    background:
        rgba(7, 14, 31, 0.95);

    border:
        1px solid
        rgba(66, 95, 153, 0.27);

    border-radius: 13px;
}


.ax-command-panel-title > div {
    display: flex;
    align-items: center;

    gap: 8px;
}


.ax-command-panel-title strong {
    color: var(--ax-white);

    font-size: 12px;
}


.ax-command-panel-title > span {
    color: #64718e;

    font-size: 6px;

    letter-spacing: 1.2px;
}


.ax-command-panel-icon {
    color: var(--ax-cyan);

    font-size: 13px;
}


/* ========================================================
   GRÁFICO
   ======================================================== */

[data-testid="stPlotlyChart"] {
    overflow: hidden;

    padding: 5px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.95),
            rgba(4, 9, 23, 0.95)
        );

    border:
        1px solid
        rgba(67, 96, 156, 0.27);

    border-radius: 15px;
}


/* ========================================================
   TABLA DE TRADES
   ======================================================== */

.ax-command-trades-scroll {
    width: 100%;

    overflow-x: auto;
    overflow-y: auto;

    max-height: 405px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.97),
            rgba(4, 9, 23, 0.97)
        );

    border:
        1px solid
        rgba(67, 96, 156, 0.27);

    border-radius: 15px;
}


.ax-command-trades-table {
    width: 100%;
    min-width: 700px;

    border-collapse: collapse;

    color: var(--ax-text);

    font-size: 10px;
}


.ax-command-trades-table th {
    position: sticky;
    top: 0;
    z-index: 2;

    padding:
        12px
        9px;

    color: #71809f;

    font-size: 7px;
    font-weight: 950;

    text-align: left;

    letter-spacing: 1px;

    background:
        #081126;

    border-bottom:
        1px solid
        rgba(68, 96, 155, 0.27);
}


.ax-command-trades-table td {
    padding:
        11px
        9px;

    vertical-align: middle;

    white-space: nowrap;

    border-bottom:
        1px solid
        rgba(68, 96, 155, 0.13);
}


.ax-command-trades-table tr:last-child td {
    border-bottom: none;
}


.ax-command-trades-table tbody tr:hover {
    background:
        rgba(32, 221, 245, 0.035);
}


.ax-trade-asset {
    color: var(--ax-white);

    font-weight: 800;
}


.ax-trade-badge,
.ax-result-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;

    min-width: 38px;

    padding:
        4px
        7px;

    border-radius: 999px;

    font-size: 7px;
    font-weight: 950;
}


.ax-trade-long {
    color: var(--ax-green);

    background:
        rgba(0, 245, 138, 0.12);

    border:
        1px solid
        rgba(0, 245, 138, 0.25);
}


.ax-trade-short {
    color: #ff7a91;

    background:
        rgba(255, 23, 68, 0.13);

    border:
        1px solid
        rgba(255, 23, 68, 0.28);
}


.ax-trade-neutral {
    color: var(--ax-muted);

    background:
        rgba(120, 136, 173, 0.10);
}


.ax-result-win {
    color: var(--ax-green);

    background:
        rgba(0, 245, 138, 0.12);
}


.ax-result-loss {
    color: #ff7089;

    background:
        rgba(255, 23, 68, 0.14);
}


.ax-result-be {
    color: #c1cae0;

    background:
        rgba(130, 145, 179, 0.11);
}


.ax-trade-pnl {
    font-weight: 950;
}


/* ========================================================
   SETUP E IMÁGENES
   ======================================================== */

[data-testid="stImage"] {
    overflow: hidden;

    padding: 7px;

    background:
        rgba(5, 11, 27, 0.94);

    border:
        1px solid
        rgba(67, 96, 156, 0.27);

    border-radius: 15px;
}


[data-testid="stImage"] img {
    border-radius: 10px;
}


.ax-command-image-placeholder,
.ax-command-empty {
    min-height: 230px;

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding: 22px;

    text-align: center;

    background:
        rgba(5, 11, 27, 0.92);

    border:
        1px dashed
        rgba(32, 221, 245, 0.29);

    border-radius: 15px;
}


.ax-command-image-placeholder > div,
.ax-command-empty > div {
    color: var(--ax-cyan);

    font-size: 30px;
}


.ax-command-image-placeholder strong,
.ax-command-empty strong {
    margin-top: 11px;

    color: var(--ax-white);

    font-size: 13px;
}


.ax-command-image-placeholder span,
.ax-command-image-placeholder p,
.ax-command-empty p {
    margin-top: 7px;

    color: #7b88a5;

    font-size: 9px;
    line-height: 1.5;
}


.ax-command-table-empty {
    min-height: 405px;
}


.ax-command-setup-empty {
    min-height: 245px;
}


/* ========================================================
   RESUMEN RÁPIDO
   ======================================================== */

.ax-summary-card {
    padding: 15px;

    background:
        linear-gradient(
            145deg,
            rgba(6, 14, 31, 0.96),
            rgba(4, 9, 23, 0.96)
        );

    border:
        1px solid
        rgba(67, 96, 156, 0.27);

    border-radius: 15px;
}


.ax-summary-row {
    display: flex;
    justify-content: space-between;

    gap: 12px;

    padding:
        8px 0;

    color: #8c98b5;

    font-size: 9px;

    border-bottom:
        1px solid
        rgba(67, 96, 156, 0.13);
}


.ax-summary-row:last-child {
    border-bottom: none;
}


.ax-summary-row strong {
    font-size: 10px;
}


/* ========================================================
   BANNER INFERIOR
   ======================================================== */

.ax-intelligence-banner {
    position: relative;

    display: grid;

    grid-template-columns:
        1.15fr
        0.9fr
        0.75fr;

    gap: 22px;

    overflow: hidden;

    margin-top: 18px;
    padding: 25px;

    background:
        radial-gradient(
            circle at 67% 50%,
            rgba(32, 221, 245, 0.10),
            transparent 25%
        ),
        radial-gradient(
            circle at 87% 55%,
            rgba(255, 23, 68, 0.10),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            rgba(5, 14, 32, 0.97),
            rgba(9, 6, 30, 0.97)
        );

    border:
        1px solid
        rgba(65, 99, 163, 0.31);

    border-radius:
        var(--ax-radius-lg);
}


.ax-intelligence-copy h2 {
    margin:
        12px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(31px, 3vw, 47px);

    line-height: 0.98;
    font-weight: 950;

    letter-spacing: -2px;
}


.ax-intelligence-copy h2 span {
    display: block;

    color: var(--ax-cyan);
}


.ax-intelligence-copy p {
    max-width: 540px;

    margin-top: 15px;

    color: #95a1be;

    font-size: 11px;
    line-height: 1.65;
}


.ax-intelligence-features {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 9px;

    margin-top: 18px;
}


.ax-intelligence-features div {
    display: flex;
    align-items: center;

    gap: 8px;

    padding:
        11px;

    color: #e2e8f7;

    font-size: 9px;
    font-weight: 780;

    background:
        rgba(4, 10, 25, 0.68);

    border:
        1px solid
        rgba(68, 96, 155, 0.22);

    border-radius: 11px;
}


.ax-intelligence-features b {
    color: var(--ax-cyan);

    font-size: 14px;
}


.ax-intelligence-visual {
    display: flex;
    align-items: center;
    justify-content: center;

    gap: 12px;

    min-height: 210px;

    background:
        radial-gradient(
            circle,
            rgba(54, 124, 255, 0.12),
            transparent 62%
        );

    border-radius: 17px;
}


.ax-market-animal {
    font-size:
        clamp(20px, 2vw, 33px);

    font-weight: 950;

    letter-spacing: 1px;
}


.ax-bull {
    color: var(--ax-green);

    text-shadow:
        0 0 22px
        rgba(0, 245, 138, 0.46);
}


.ax-bear {
    color: var(--ax-red);

    text-shadow:
        0 0 22px
        rgba(255, 23, 68, 0.46);
}


.ax-market-logo {
    width: 70px;
    height: 70px;

    display: grid;
    place-items: center;

    color: white;

    font-size: 31px;
    font-weight: 950;

    border:
        1px solid
        rgba(100, 132, 205, 0.37);

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(32, 221, 245, 0.13),
            rgba(139, 77, 255, 0.20)
        );

    box-shadow:
        0 0 35px
        rgba(54, 124, 255, 0.20);
}


.ax-intelligence-stats {
    display: grid;

    grid-template-columns: 1fr;

    gap: 10px;

    align-content: center;
}


.ax-intelligence-stats div {
    padding: 15px;

    text-align: center;

    background:
        rgba(4, 10, 25, 0.74);

    border:
        1px solid
        rgba(68, 96, 155, 0.23);

    border-radius: 13px;
}


.ax-intelligence-stats strong {
    display: block;

    color: var(--ax-cyan);

    font-size: 20px;
    font-weight: 950;
}


.ax-intelligence-stats span {
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
   OTROS COMPONENTES
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
    border-radius: 999px;

    background:
        linear-gradient(
            var(--ax-cyan),
            var(--ax-purple)
        );

    border:
        2px solid
        #040713;
}


/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 1350px) {

    .ax-command-trades-table {
        min-width: 640px;
    }

    .ax-intelligence-banner {
        grid-template-columns:
            1.2fr
            0.8fr;
    }

    .ax-intelligence-stats {
        grid-column:
            1 / -1;

        grid-template-columns:
            repeat(3, 1fr);
    }
}


@media (max-width: 1050px) {

    .ax-command-metric {
        min-height: 140px;
    }

    .ax-intelligence-banner {
        grid-template-columns: 1fr;
    }

    .ax-intelligence-stats {
        grid-template-columns:
            repeat(3, 1fr);
    }
}


@media (max-width: 750px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .ax-command-header {
        align-items: flex-start;
    }

    .ax-command-header h1 {
        font-size: 30px;
    }

    .ax-intelligence-features {
        grid-template-columns: 1fr;
    }

    .ax-intelligence-stats {
        grid-template-columns: 1fr;
    }

    .ax-command-trades-table {
        min-width: 620px;
    }
}


/* ========================================================
   REDUCIR MOVIMIENTO
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


def apply_styles() -> None:
    st.html(
        GLOBAL_CSS
    )
