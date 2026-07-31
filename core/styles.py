from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# SISTEMA VISUAL COMPLETO
# =========================================================


GLOBAL_CSS = """
<style>

/* ========================================================
   VARIABLES PRINCIPALES
   ======================================================== */

:root {
    --ax-bg-0: #030612;
    --ax-bg-1: #060a18;
    --ax-bg-2: #090e22;
    --ax-panel: rgba(8, 14, 34, 0.88);
    --ax-panel-strong: rgba(7, 12, 29, 0.96);
    --ax-card: rgba(10, 17, 39, 0.88);
    --ax-border: rgba(96, 126, 190, 0.24);
    --ax-border-bright: rgba(37, 229, 255, 0.43);

    --ax-text: #f5f7ff;
    --ax-muted: #8d99ba;
    --ax-dim: #657292;

    --ax-cyan: #25e5ff;
    --ax-blue: #258cff;
    --ax-purple: #9146ff;
    --ax-violet: #b34dff;

    --ax-green: #00ff88;
    --ax-red: #ff1744;
    --ax-yellow: #ffd740;

    --ax-radius: 18px;
    --ax-shadow:
        0 22px 70px rgba(0, 0, 0, 0.36),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


/* ========================================================
   BASE GENERAL
   ======================================================== */

html,
body,
[data-testid="stAppViewContainer"],
.stApp {
    background:
        radial-gradient(
            circle at 12% 10%,
            rgba(0, 218, 255, 0.11),
            transparent 29%
        ),
        radial-gradient(
            circle at 82% 22%,
            rgba(129, 52, 255, 0.14),
            transparent 34%
        ),
        radial-gradient(
            circle at 65% 92%,
            rgba(255, 23, 68, 0.06),
            transparent 26%
        ),
        linear-gradient(
            135deg,
            var(--ax-bg-0),
            var(--ax-bg-1) 48%,
            #090419
        ) !important;

    color: var(--ax-text);
}


/* Fondo de velas japonesas sin inyectar HTML */

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;

    background:
        linear-gradient(
            90deg,
            transparent 0 3%,
            rgba(0, 255, 136, 0.24) 3% 3.35%,
            transparent 3.35% 7%,
            rgba(255, 23, 68, 0.23) 7% 7.4%,
            transparent 7.4% 12%,
            rgba(37, 229, 255, 0.21) 12% 12.35%,
            transparent 12.35% 18%,
            rgba(145, 70, 255, 0.22) 18% 18.4%,
            transparent 18.4% 25%
        );

    background-size: 420px 100%;
    opacity: 0.34;
    filter: blur(0.1px);

    animation:
        ax-candles-slide 25s linear infinite,
        ax-candles-pulse 8s ease-in-out infinite alternate;
}


/* Sombras inferiores tipo gráfico */

[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    left: 15%;
    right: 0;
    bottom: -22px;
    height: 180px;
    z-index: 0;
    pointer-events: none;

    background:
        repeating-linear-gradient(
            90deg,
            transparent 0 22px,
            rgba(0, 255, 136, 0.30) 22px 30px,
            transparent 30px 48px,
            rgba(255, 23, 68, 0.30) 48px 57px,
            transparent 57px 79px
        );

    mask-image:
        linear-gradient(
            to top,
            rgba(0, 0, 0, 0.95),
            transparent
        );

    -webkit-mask-image:
        linear-gradient(
            to top,
            rgba(0, 0, 0, 0.95),
            transparent
        );

    opacity: 0.40;
    animation: ax-volume-move 18s linear infinite;
}


@keyframes ax-candles-slide {
    from {
        background-position-x: 0;
    }

    to {
        background-position-x: 420px;
    }
}


@keyframes ax-candles-pulse {
    from {
        opacity: 0.24;
    }

    to {
        opacity: 0.44;
    }
}


@keyframes ax-volume-move {
    from {
        background-position-x: 0;
    }

    to {
        background-position-x: 320px;
    }
}


/* Mantener el contenido por encima del fondo */

[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    position: relative;
    z-index: 2;
}


[data-testid="stHeader"] {
    background: rgba(3, 6, 18, 0.76) !important;
    backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(72, 95, 154, 0.12);
}


.block-container {
    max-width: 1680px;
    padding-top: 2.1rem;
    padding-bottom: 3rem;
}


/* ========================================================
   TEXTO
   ======================================================== */

h1,
h2,
h3,
h4,
h5,
h6,
p,
label,
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


h1,
h2,
h3 {
    color: var(--ax-text);
}


.ax-title {
    margin-top: 10px;
    color: var(--ax-text);
    font-size: clamp(30px, 3vw, 48px);
    line-height: 1.06;
    font-weight: 950;
    letter-spacing: -1.8px;
}


.ax-sub {
    margin-top: 10px;
    color: var(--ax-muted);
    font-size: 13px;
    line-height: 1.65;
}


/* ========================================================
   HERO Y TARJETAS
   ======================================================== */

.ax-hero {
    position: relative;
    overflow: hidden;

    padding: 28px 31px;
    margin-bottom: 18px;

    background:
        radial-gradient(
            circle at 85% 25%,
            rgba(145, 70, 255, 0.16),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            rgba(6, 15, 34, 0.95),
            rgba(15, 8, 40, 0.90)
        );

    border: 1px solid var(--ax-border-bright);
    border-radius: 22px;

    box-shadow:
        0 25px 70px rgba(0, 0, 0, 0.35),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


.ax-hero::after {
    content: "";
    position: absolute;
    width: 420px;
    height: 420px;
    right: -210px;
    top: -210px;

    border-radius: 50%;
    background: rgba(37, 229, 255, 0.08);
    filter: blur(25px);
}


.ax-card {
    position: relative;

    padding: 17px;

    background:
        linear-gradient(
            145deg,
            rgba(12, 20, 45, 0.92),
            rgba(7, 12, 29, 0.90)
        );

    border: 1px solid var(--ax-border);
    border-radius: var(--ax-radius);

    color: var(--ax-text);

    box-shadow: var(--ax-shadow);

    transition:
        transform 0.22s ease,
        border-color 0.22s ease,
        box-shadow 0.22s ease;
}


.ax-card:hover {
    transform: translateY(-2px);
    border-color: rgba(37, 229, 255, 0.46);

    box-shadow:
        0 20px 55px rgba(0, 0, 0, 0.42),
        0 0 24px rgba(37, 229, 255, 0.07);
}


/* ========================================================
   LOGIN
   ======================================================== */

.ax-auth-spacer {
    height: 8px;
}


.ax-auth-hero {
    position: relative;
    min-height: 650px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    padding: 46px;

    overflow: hidden;

    background:
        radial-gradient(
            circle at 82% 18%,
            rgba(37, 229, 255, 0.13),
            transparent 30%
        ),
        radial-gradient(
            circle at 25% 90%,
            rgba(145, 70, 255, 0.16),
            transparent 33%
        ),
        linear-gradient(
            145deg,
            rgba(4, 12, 28, 0.96),
            rgba(10, 5, 30, 0.95)
        );

    border:
        1px solid
        rgba(69, 127, 201, 0.35);

    border-radius: 26px;

    box-shadow:
        0 30px 100px rgba(0, 0, 0, 0.48),
        inset 0 1px 0 rgba(255, 255, 255, 0.035);
}


.ax-auth-hero::before {
    content: "";
    position: absolute;
    inset: 0;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(37, 229, 255, 0.035),
            transparent
        );

    transform: translateX(-100%);
    animation: ax-auth-shine 8s ease-in-out infinite;
}


@keyframes ax-auth-shine {
    0%,
    55% {
        transform: translateX(-100%);
    }

    80%,
    100% {
        transform: translateX(100%);
    }
}


.ax-auth-brand,
.ax-auth-mini-brand {
    display: flex;
    align-items: center;
    gap: 14px;
}


.ax-auth-logo,
.ax-auth-mini-logo,
.ax-logo {
    width: 48px;
    height: 48px;

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
        0 0 25px rgba(37, 229, 255, 0.32),
        0 0 40px rgba(145, 70, 255, 0.20);
}


.ax-auth-brand-title,
.ax-auth-mini-title {
    color: var(--ax-text);
    font-size: 18px;
    font-weight: 950;
    letter-spacing: 0.4px;
}


.ax-auth-brand-subtitle,
.ax-auth-mini-subtitle {
    margin-top: 4px;

    color: var(--ax-dim);
    font-size: 8px;
    font-weight: 800;
    letter-spacing: 2px;
}


.ax-auth-eyebrow {
    margin-top: 38px;

    color: var(--ax-cyan);
    font-size: 11px;
    font-weight: 950;
    letter-spacing: 2.2px;
}


.ax-auth-title {
    margin: 24px 0 0;

    max-width: 650px;

    color: var(--ax-text);

    font-size: clamp(49px, 5vw, 70px);
    line-height: 0.99;
    font-weight: 950;
    letter-spacing: -3.4px;
}


.ax-auth-title span {
    display: block;

    background:
        linear-gradient(
            90deg,
            var(--ax-cyan),
            #7991ff,
            var(--ax-violet)
        );

    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}


.ax-auth-description {
    max-width: 640px;

    margin-top: 27px;

    color: #9da9c7;

    font-size: 16px;
    line-height: 1.78;
}


.ax-auth-feature-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;

    gap: 12px;

    margin-top: 34px;
}


.ax-auth-feature {
    padding: 16px;

    color: #dce5ff;
    font-size: 12px;
    font-weight: 750;

    background:
        linear-gradient(
            145deg,
            rgba(11, 19, 43, 0.85),
            rgba(6, 10, 25, 0.85)
        );

    border:
        1px solid
        rgba(88, 109, 170, 0.27);

    border-radius: 14px;

    transition:
        0.22s ease;
}


.ax-auth-feature:hover {
    border-color: rgba(37, 229, 255, 0.45);
    transform: translateY(-2px);
}


.ax-auth-quote {
    margin-top: 39px;
    padding: 17px 18px;

    color: #91a0c1;
    font-size: 12px;

    border-left: 3px solid var(--ax-cyan);
    border-radius: 5px 12px 12px 5px;

    background: rgba(7, 13, 34, 0.76);
}


.ax-auth-form-header {
    margin-bottom: 22px;
}


.ax-auth-form-header h2 {
    margin: 28px 0 8px;

    color: var(--ax-cyan);

    font-size: clamp(30px, 3vw, 42px);
    line-height: 1.05;
    font-weight: 950;
    letter-spacing: -1.7px;
}


.ax-auth-form-header p {
    color: var(--ax-muted);
    font-size: 13px;
}


.ax-auth-mini-logo {
    width: 44px;
    height: 44px;
}


.ax-auth-mini-title {
    font-size: 16px;
}


.ax-auth-form-shell {
    min-height: 650px;

    padding: 32px;

    background:
        radial-gradient(
            circle at 100% 0,
            rgba(145, 70, 255, 0.16),
            transparent 30%
        ),
        linear-gradient(
            145deg,
            rgba(9, 13, 31, 0.96),
            rgba(9, 5, 29, 0.96)
        );

    border:
        1px solid
        rgba(86, 104, 164, 0.27);

    border-radius: 26px;

    box-shadow:
        0 30px 100px rgba(0, 0, 0, 0.45);
}


.ax-auth-form-inner {
    width: 100%;
}


/* ========================================================
   SIDEBAR
   ======================================================== */

[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 50% 0,
            rgba(37, 229, 255, 0.10),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            rgba(4, 9, 24, 0.99),
            rgba(5, 7, 20, 0.99)
        ) !important;

    border-right:
        1px solid
        rgba(66, 94, 155, 0.25);
}


[data-testid="stSidebarContent"] {
    padding: 1.3rem 1rem 1.5rem;
}


.ax-brand {
    display: flex;
    align-items: center;

    gap: 12px;

    padding:
        9px
        7px
        22px;

    margin-bottom: 15px;

    border-bottom:
        1px solid
        rgba(82, 103, 158, 0.18);
}


.ax-brand b {
    display: block;

    color: var(--ax-text);
    font-size: 14px;
    letter-spacing: 0.5px;
}


.ax-brand small {
    display: block;

    margin-top: 4px;

    color: var(--ax-dim);
    font-size: 7px;
    letter-spacing: 1.5px;
}


.ax-profile {
    margin-bottom: 20px;
    padding: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(11, 21, 47, 0.90),
            rgba(7, 11, 27, 0.90)
        );

    border:
        1px solid
        rgba(37, 229, 255, 0.28);

    border-radius: 18px;

    box-shadow:
        0 18px 45px rgba(0, 0, 0, 0.31);
}


.ax-section {
    margin:
        24px
        4px
        10px;

    color: #647291;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 2px;
}


/* ========================================================
   BOTONES
   ======================================================== */

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 44px;

    color: #f5f7ff !important;
    font-weight: 850 !important;

    background:
        linear-gradient(
            90deg,
            rgba(37, 229, 255, 0.95),
            rgba(37, 140, 255, 0.95),
            rgba(145, 70, 255, 0.95)
        ) !important;

    border:
        1px solid
        rgba(99, 219, 255, 0.40) !important;

    border-radius: 11px !important;

    box-shadow:
        0 10px 28px rgba(37, 140, 255, 0.14);

    transition:
        transform 0.18s ease,
        filter 0.18s ease,
        box-shadow 0.18s ease;
}


.stButton > button:hover,
.stDownloadButton > button:hover,
[data-testid="stFormSubmitButton"] > button:hover {
    transform: translateY(-1px);

    filter:
        brightness(1.08)
        saturate(1.12);

    box-shadow:
        0 14px 35px rgba(37, 140, 255, 0.25);
}


.stButton > button[kind="secondary"] {
    background:
        linear-gradient(
            145deg,
            rgba(13, 22, 48, 0.94),
            rgba(7, 12, 29, 0.94)
        ) !important;

    border:
        1px solid
        rgba(83, 105, 166, 0.33) !important;

    color:
        #e5ecff !important;
}


.stButton > button[kind="secondary"]:hover {
    border-color:
        rgba(37, 229, 255, 0.55) !important;

    background:
        linear-gradient(
            145deg,
            rgba(14, 34, 63, 0.96),
            rgba(18, 13, 53, 0.96)
        ) !important;
}


/* ========================================================
   INPUTS
   ======================================================== */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    color: var(--ax-text) !important;

    background:
        rgba(6, 11, 29, 0.94) !important;

    border:
        1px solid
        rgba(94, 112, 169, 0.35) !important;

    border-radius:
        10px !important;

    box-shadow:
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stDateInput"] input:focus {
    border-color:
        var(--ax-cyan) !important;

    box-shadow:
        0 0 0 2px rgba(37, 229, 255, 0.12) !important;
}


[data-baseweb="select"] > div {
    color: var(--ax-text) !important;

    background:
        rgba(6, 11, 29, 0.94) !important;

    border-color:
        rgba(94, 112, 169, 0.35) !important;

    border-radius:
        10px !important;
}


label,
[data-testid="stWidgetLabel"] {
    color:
        #d8e2fb !important;

    font-size:
        12px !important;
}


/* ========================================================
   TABS
   ======================================================== */

[data-baseweb="tab-list"] {
    gap: 20px;

    border-bottom:
        1px solid
        rgba(92, 109, 164, 0.23);
}


[data-baseweb="tab"] {
    height: 42px;

    color:
        #8f9bbb !important;

    background:
        transparent !important;
}


[aria-selected="true"][data-baseweb="tab"] {
    color:
        var(--ax-cyan) !important;

    font-weight:
        900;
}


/* ========================================================
   MÉTRICAS
   ======================================================== */

[data-testid="stMetric"] {
    min-height: 114px;

    padding: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(11, 20, 44, 0.92),
            rgba(7, 12, 29, 0.92)
        );

    border:
        1px solid
        rgba(77, 100, 162, 0.25);

    border-radius: 16px;

    box-shadow:
        0 14px 40px rgba(0, 0, 0, 0.28);
}


[data-testid="stMetricLabel"] {
    color:
        #7886a7;
}


[data-testid="stMetricValue"] {
    color:
        var(--ax-text);
}


/* ========================================================
   ALERTAS
   ======================================================== */

[data-testid="stAlert"] {
    border-radius:
        13px;

    border:
        1px solid
        rgba(92, 110, 168, 0.25);

    backdrop-filter:
        blur(12px);
}


/* ========================================================
   DATAFRAME Y GRÁFICOS
   ======================================================== */

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    overflow: hidden;

    border:
        1px solid
        rgba(80, 101, 162, 0.24);

    border-radius:
        15px;

    background:
        rgba(6, 11, 29, 0.80);
}


[data-testid="stPlotlyChart"] {
    overflow: hidden;

    border:
        1px solid
        rgba(80, 101, 162, 0.22);

    border-radius:
        17px;

    background:
        rgba(5, 10, 26, 0.72);
}


/* ========================================================
   FILE UPLOADER
   ======================================================== */

[data-testid="stFileUploader"] {
    padding:
        10px;

    border:
        1px dashed
        rgba(37, 229, 255, 0.35);

    border-radius:
        14px;

    background:
        rgba(7, 13, 31, 0.75);
}


/* ========================================================
   EXPANDERS
   ======================================================== */

[data-testid="stExpander"] {
    overflow: hidden;

    border:
        1px solid
        rgba(77, 99, 157, 0.25);

    border-radius:
        14px;

    background:
        rgba(7, 12, 28, 0.82);
}


/* ========================================================
   SCROLLBAR
   ======================================================== */

::-webkit-scrollbar {
    width: 9px;
    height: 9px;
}


::-webkit-scrollbar-track {
    background:
        #050817;
}


::-webkit-scrollbar-thumb {
    background:
        linear-gradient(
            var(--ax-cyan),
            var(--ax-purple)
        );

    border-radius:
        999px;

    border:
        2px solid
        #050817;
}


/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 1100px) {

    .ax-auth-feature-grid {
        grid-template-columns:
            1fr;
    }

    .ax-auth-title {
        font-size:
            50px;
    }

    .ax-auth-hero {
        padding:
            34px;
    }
}


@media (max-width: 800px) {

    .block-container {
        padding-left:
            1rem;
        padding-right:
            1rem;
    }

    .ax-auth-title {
        font-size:
            42px;
    }

    .ax-auth-hero,
    .ax-auth-form-shell {
        min-height:
            auto;
    }
}

</style>
"""


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================


def apply_styles() -> None:
    """
    Aplica el sistema visual completo de AXION PRIME.

    No genera etiquetas HTML individuales para las velas.
    Todo el fondo animado se crea mediante CSS.
    """

    st.html(GLOBAL_CSS)
