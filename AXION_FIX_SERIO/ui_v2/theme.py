from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME V2
# SISTEMA VISUAL CENTRALIZADO
# =========================================================


V2_THEME_CSS = """
<style>

/* ========================================================
   VARIABLES
   ======================================================== */

:root {
    --v2-bg-0: #02040b;
    --v2-bg-1: #050915;
    --v2-bg-2: #080d1d;

    --v2-panel: rgba(7, 14, 31, 0.86);
    --v2-panel-strong: rgba(5, 10, 24, 0.96);
    --v2-panel-soft: rgba(11, 20, 42, 0.72);

    --v2-border: rgba(83, 118, 187, 0.28);
    --v2-border-strong: rgba(69, 157, 255, 0.42);

    --v2-white: #f7f9ff;
    --v2-text: #dfe7f8;
    --v2-muted: #91a0bf;
    --v2-dim: #5f6c89;

    --v2-cyan: #19e4ff;
    --v2-blue: #3c7dff;
    --v2-purple: #8b4dff;
    --v2-green: #00f58a;
    --v2-red: #ff1744;
    --v2-gold: #ffd166;

    --v2-radius-sm: 10px;
    --v2-radius-md: 16px;
    --v2-radius-lg: 24px;

    --v2-shadow:
        0 24px 70px rgba(0, 0, 0, 0.38),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


/* ========================================================
   BASE
   ======================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    color: var(--v2-text);

    background:
        radial-gradient(
            circle at 8% 4%,
            rgba(25, 228, 255, 0.08),
            transparent 27%
        ),
        radial-gradient(
            circle at 88% 12%,
            rgba(139, 77, 255, 0.12),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            var(--v2-bg-0),
            var(--v2-bg-1) 52%,
            #090416
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


[data-testid="stHeader"] {
    background:
        rgba(2, 4, 11, 0.84) !important;

    backdrop-filter:
        blur(18px);

    border-bottom:
        1px solid
        rgba(78, 108, 170, 0.14);
}


.block-container {
    width: 100%;
    max-width: 1760px;

    padding-top: 1.4rem;
    padding-bottom: 3rem;
}


/* ========================================================
   CUADRÍCULA Y ATMÓSFERA
   ======================================================== */

[data-testid="stAppViewContainer"]::after {
    content: "";

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(83, 112, 177, 0.034) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(83, 112, 177, 0.034) 1px,
            transparent 1px
        );

    background-size:
        52px 52px;

    opacity: 0.62;
}


/* ========================================================
   COMPONENTES BASE
   ======================================================== */

.v2-glass {
    background:
        linear-gradient(
            145deg,
            rgba(10, 20, 43, 0.84),
            rgba(4, 10, 24, 0.92)
        );

    border:
        1px solid
        var(--v2-border);

    border-radius:
        var(--v2-radius-md);

    box-shadow:
        var(--v2-shadow);

    backdrop-filter:
        blur(18px);
}


.v2-eyebrow {
    color:
        var(--v2-cyan);

    font-size: 8px;
    font-weight: 950;

    letter-spacing: 2.1px;
}


.v2-title {
    margin:
        8px
        0
        0;

    color:
        var(--v2-white);

    font-size:
        clamp(30px, 3vw, 48px);

    line-height: 1.02;
    font-weight: 950;

    letter-spacing: -2px;
}


.v2-muted {
    color:
        var(--v2-muted);
}


/* ========================================================
   BOTONES
   ======================================================== */

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
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
            var(--v2-cyan),
            var(--v2-blue),
            var(--v2-purple)
        ) !important;

    border:
        1px solid
        rgba(102, 220, 255, 0.40) !important;

    border-radius:
        var(--v2-radius-sm) !important;

    box-shadow:
        0 12px 30px
        rgba(60, 125, 255, 0.18);

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
        0 16px 36px
        rgba(60, 125, 255, 0.25);
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
        rgba(76, 104, 169, 0.37) !important;

    box-shadow:
        none;
}


/* ========================================================
   INPUTS
   ======================================================== */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    color:
        var(--v2-white) !important;

    background:
        rgba(4, 10, 25, 0.96) !important;

    border:
        1px solid
        rgba(88, 114, 177, 0.40) !important;

    border-radius:
        var(--v2-radius-sm) !important;
}


[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color:
        var(--v2-cyan) !important;

    box-shadow:
        0 0 0 2px
        rgba(25, 228, 255, 0.10) !important;
}


[data-baseweb="select"] > div {
    min-height: 43px !important;

    color:
        var(--v2-white) !important;

    background:
        rgba(4, 10, 25, 0.96) !important;

    border-color:
        rgba(88, 114, 177, 0.40) !important;

    border-radius:
        var(--v2-radius-sm) !important;
}


/* ========================================================
   ALERTAS, TABLAS Y GRÁFICOS
   ======================================================== */

[data-testid="stAlert"] {
    border:
        1px solid
        rgba(88, 112, 171, 0.24);

    border-radius:
        12px;
}


[data-testid="stDataFrame"],
[data-testid="stTable"],
[data-testid="stPlotlyChart"],
[data-testid="stVegaLiteChart"] {
    overflow: hidden;

    background:
        rgba(4, 9, 23, 0.90);

    border:
        1px solid
        rgba(74, 102, 166, 0.26);

    border-radius:
        var(--v2-radius-md);
}


/* ========================================================
   SCROLLBAR
   ======================================================== */

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}


::-webkit-scrollbar-track {
    background:
        #040713;
}


::-webkit-scrollbar-thumb {
    background:
        linear-gradient(
            var(--v2-cyan),
            var(--v2-purple)
        );

    border:
        2px solid
        #040713;

    border-radius:
        999px;
}


/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .v2-title {
        font-size: 31px;
    }
}


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


/* ========================================================
   LIMPIEZA DE ESTILOS HEREDADOS
   Elimina franjas verdes/rojas y fondos antiguos.
   ======================================================== */

.stApp::before,
.stApp::after,
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after,
[data-testid="stSidebar"]::before,
[data-testid="stSidebar"]::after,
[data-testid="stMain"]::before,
[data-testid="stMain"]::after,
.main::before,
.main::after {
    content: none !important;
    display: none !important;
    background: none !important;
    box-shadow: none !important;
}


html,
body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background:
        radial-gradient(
            circle at 82% 10%,
            rgba(60, 125, 255, 0.10),
            transparent 32%
        ),
        radial-gradient(
            circle at 18% 86%,
            rgba(139, 77, 255, 0.08),
            transparent 34%
        ),
        linear-gradient(
            180deg,
            #02050d 0%,
            #050914 52%,
            #030611 100%
        ) !important;
}


[data-testid="stAppViewContainer"] {
    position: relative;
    isolation: isolate;
}


[data-testid="stAppViewContainer"] > .main {
    background: transparent !important;
}


[data-testid="stAppViewContainer"] .block-container {
    position: relative;
    z-index: 2;
}


[data-testid="stAppViewContainer"] > div:first-child {
    background: transparent !important;
}


/* Rejilla azul tenue y profesional */
[data-testid="stAppViewContainer"]::after {
    content: "" !important;
    display: block !important;

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(54, 90, 151, 0.025) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(54, 90, 151, 0.025) 1px,
            transparent 1px
        ) !important;

    background-size:
        48px 48px !important;

    opacity: 0.55;
}


/* Encabezado oscuro y limpio */
[data-testid="stHeader"] {
    background:
        rgba(2, 5, 13, 0.90) !important;

    border-bottom:
        1px solid
        rgba(69, 101, 164, 0.16) !important;

    backdrop-filter:
        blur(18px);
}


/* Sidebar sin franjas heredadas */
[data-testid="stSidebar"] {
    background:
        radial-gradient(
            circle at 50% -12%,
            rgba(25, 228, 255, 0.08),
            transparent 28%
        ),
        linear-gradient(
            180deg,
            #030814 0%,
            #02050d 100%
        ) !important;
}

</style>
"""


def apply_v2_theme() -> None:
    """
    Aplica la identidad visual central de AXION PRIME V2.
    """

    st.html(
        V2_THEME_CSS
    )
