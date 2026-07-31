from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# SISTEMA VISUAL INSTITUTIONAL NEON
# =========================================================


GLOBAL_CSS = """
<style>

/* ========================================================
   PALETA Y VARIABLES
   ======================================================== */

:root {
    --ax-bg-0: #02040c;
    --ax-bg-1: #030711;
    --ax-bg-2: #060b18;
    --ax-bg-3: #091024;

    --ax-panel: rgba(7, 13, 31, 0.94);
    --ax-panel-soft: rgba(10, 17, 38, 0.88);
    --ax-panel-strong: rgba(4, 9, 23, 0.98);

    --ax-border: rgba(81, 106, 165, 0.25);
    --ax-border-strong: rgba(82, 121, 194, 0.42);
    --ax-border-cyan: rgba(32, 221, 245, 0.42);

    --ax-white: #f6f8ff;
    --ax-text: #e9edfb;
    --ax-muted: #8e9ab8;
    --ax-dim: #596582;

    --ax-cyan: #20ddf5;
    --ax-blue: #367cff;
    --ax-purple: #8b4dff;

    --ax-green: #00f58a;
    --ax-green-soft: rgba(0, 245, 138, 0.16);

    --ax-red: #ff1744;
    --ax-red-soft: rgba(255, 23, 68, 0.16);

    --ax-yellow: #ffd34d;

    --ax-radius-sm: 10px;
    --ax-radius-md: 15px;
    --ax-radius-lg: 22px;

    --ax-shadow:
        0 22px 65px rgba(0, 0, 0, 0.38),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


/* ========================================================
   RESET Y BASE
   ======================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    color: var(--ax-text);

    background:
        radial-gradient(
            circle at 9% 4%,
            rgba(32, 221, 245, 0.085),
            transparent 27%
        ),
        radial-gradient(
            circle at 88% 18%,
            rgba(139, 77, 255, 0.12),
            transparent 32%
        ),
        radial-gradient(
            circle at 52% 105%,
            rgba(255, 23, 68, 0.035),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            var(--ax-bg-0),
            var(--ax-bg-1) 48%,
            #080418
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


.block-container {
    width: 100%;
    max-width: 1680px;

    padding-top: 1.65rem;
    padding-bottom: 3rem;
}


[data-testid="stHeader"] {
    background:
        rgba(2, 4, 12, 0.88) !important;

    backdrop-filter: blur(18px);

    border-bottom:
        1px solid
        rgba(82, 103, 158, 0.13);
}


/* ========================================================
   VELAS JAPONESAS PEQUEÑAS Y ANIMADAS
   ======================================================== */

/*
   Capa 1:
   pequeños cuerpos alcistas y bajistas distribuidos
   horizontalmente. Ya no son barras gigantes.
*/

[data-testid="stAppViewContainer"]::before {
    content: "";

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    background-image:

        /* Mecha verde 1 */
        linear-gradient(
            to bottom,
            transparent 0 26%,
            rgba(0, 245, 138, 0.58) 26% 75%,
            transparent 75% 100%
        ),

        /* Cuerpo verde 1 */
        linear-gradient(
            to bottom,
            transparent 0 39%,
            rgba(0, 245, 138, 0.95) 39% 62%,
            transparent 62% 100%
        ),

        /* Mecha roja 1 */
        linear-gradient(
            to bottom,
            transparent 0 18%,
            rgba(255, 23, 68, 0.62) 18% 81%,
            transparent 81% 100%
        ),

        /* Cuerpo rojo 1 */
        linear-gradient(
            to bottom,
            transparent 0 33%,
            rgba(255, 23, 68, 0.96) 33% 61%,
            transparent 61% 100%
        ),

        /* Mecha verde 2 */
        linear-gradient(
            to bottom,
            transparent 0 34%,
            rgba(0, 245, 138, 0.48) 34% 84%,
            transparent 84% 100%
        ),

        /* Cuerpo verde 2 */
        linear-gradient(
            to bottom,
            transparent 0 48%,
            rgba(0, 245, 138, 0.86) 48% 70%,
            transparent 70% 100%
        ),

        /* Mecha roja 2 */
        linear-gradient(
            to bottom,
            transparent 0 10%,
            rgba(255, 23, 68, 0.48) 10% 68%,
            transparent 68% 100%
        ),

        /* Cuerpo rojo 2 */
        linear-gradient(
            to bottom,
            transparent 0 23%,
            rgba(255, 23, 68, 0.86) 23% 47%,
            transparent 47% 100%
        );

    background-size:
        1px 94px,
        7px 94px,
        1px 116px,
        8px 116px,
        1px 82px,
        6px 82px,
        1px 102px,
        7px 102px;

    background-position:
        28px 130px,
        25px 130px,
        103px 255px,
        100px 255px,
        164px 82px,
        162px 82px,
        226px 330px,
        223px 330px;

    background-repeat:
        repeat-x;

    opacity: 0.28;

    filter:
        drop-shadow(
            0 0 5px
            rgba(0, 245, 138, 0.28)
        )
        drop-shadow(
            0 0 5px
            rgba(255, 23, 68, 0.26)
        );

    -webkit-mask-image:
        linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.44) 0%,
            rgba(0, 0, 0, 0.14) 35%,
            rgba(0, 0, 0, 0.12) 67%,
            rgba(0, 0, 0, 0.65) 100%
        );

    mask-image:
        linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.44) 0%,
            rgba(0, 0, 0, 0.14) 35%,
            rgba(0, 0, 0, 0.12) 67%,
            rgba(0, 0, 0, 0.65) 100%
        );

    animation:
        ax-candles-drift 44s linear infinite,
        ax-candles-breathe 7s ease-in-out infinite alternate;
}


/*
   Capa 2:
   cuadrícula financiera discreta y línea de mercado.
*/

[data-testid="stAppViewContainer"]::after {
    content: "";

    position: fixed;
    inset: 0;

    z-index: 0;
    pointer-events: none;

    background-image:
        linear-gradient(
            rgba(80, 111, 173, 0.045) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            rgba(80, 111, 173, 0.045) 1px,
            transparent 1px
        ),
        linear-gradient(
            90deg,
            transparent 0%,
            rgba(32, 221, 245, 0.05) 48%,
            transparent 100%
        );

    background-size:
        54px 54px,
        54px 54px,
        100% 1px;

    background-position:
        0 0,
        0 0,
        0 72%;

    opacity: 0.72;

    animation:
        ax-grid-drift 30s linear infinite;
}


@keyframes ax-candles-drift {
    from {
        background-position:
            28px 130px,
            25px 130px,
            103px 255px,
            100px 255px,
            164px 82px,
            162px 82px,
            226px 330px,
            223px 330px;
    }

    to {
        background-position:
            988px 130px,
            985px 130px,
            1063px 255px,
            1060px 255px,
            1124px 82px,
            1122px 82px,
            1186px 330px,
            1183px 330px;
    }
}


@keyframes ax-candles-breathe {
    from {
        opacity: 0.20;
    }

    to {
        opacity: 0.34;
    }
}


@keyframes ax-grid-drift {
    from {
        background-position:
            0 0,
            0 0,
            0 72%;
    }

    to {
        background-position:
            54px 0,
            54px 0,
            0 72%;
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
            transparent 28%
        ),
        linear-gradient(
            180deg,
            rgba(3, 9, 23, 0.995),
            rgba(3, 6, 17, 0.995)
        ) !important;

    border-right:
        1px solid
        rgba(64, 90, 151, 0.28);

    box-shadow:
        18px 0 55px
        rgba(0, 0, 0, 0.24);
}


[data-testid="stSidebarContent"] {
    padding:
        1.1rem
        0.9rem
        1.6rem;
}


.ax-brand {
    display: flex;
    align-items: center;
    gap: 12px;

    padding:
        8px
        5px
        20px;

    margin-bottom: 16px;

    border-bottom:
        1px solid
        rgba(84, 104, 158, 0.17);
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
        0 0 23px
        rgba(32, 221, 245, 0.29),
        0 0 38px
        rgba(139, 77, 255, 0.13);
}


.ax-brand b {
    display: block;

    color: var(--ax-white);

    font-size: 13px;
    font-weight: 900;
}


.ax-brand small {
    display: block;

    margin-top: 4px;

    color: var(--ax-dim);

    font-size: 6px;
    font-weight: 800;

    letter-spacing: 1.55px;
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

    animation:
        ax-online-pulse 2.2s
        ease-in-out
        infinite;
}


@keyframes ax-online-pulse {
    0%,
    100% {
        transform: scale(0.92);
        opacity: 0.68;
    }

    50% {
        transform: scale(1.15);
        opacity: 1;
    }
}


.ax-profile {
    padding: 15px;
    margin-bottom: 10px;

    background:
        radial-gradient(
            circle at 12% 8%,
            rgba(32, 221, 245, 0.09),
            transparent 38%
        ),
        linear-gradient(
            145deg,
            rgba(8, 18, 42, 0.97),
            rgba(5, 10, 26, 0.97)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.28);

    border-radius: 18px;

    box-shadow:
        0 18px 42px
        rgba(0, 0, 0, 0.28),
        inset 0 1px 0
        rgba(255, 255, 255, 0.025);
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
        rgba(255, 255, 255, 0.13);

    box-shadow:
        0 0 22px
        rgba(32, 221, 245, 0.31);
}


.ax-profile-photo {
    padding: 0;
    background: #06101f;
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
            #ab42ff
        );

    font-size: 6px;
    font-weight: 950;

    letter-spacing: 0.6px;
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
    align-items: flex-end;
    justify-content: space-between;

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

    letter-spacing: 1.4px;
}


.ax-profile-target {
    color: #697694;

    font-size: 6px;
}


.ax-progress-track {
    height: 4px;

    overflow: hidden;

    margin-top: 10px;

    background: #16213d;

    border-radius: 999px;
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

    box-shadow:
        0 0 12px
        rgba(32, 221, 245, 0.43);
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

    color: #5f6d8b;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 2.05px;
}


.ax-system-card {
    padding: 13px;

    background:
        rgba(6, 11, 27, 0.88);

    border:
        1px solid
        rgba(74, 98, 157, 0.24);

    border-radius: 14px;
}


.ax-system-row {
    display: flex;
    justify-content: space-between;

    margin-bottom: 10px;

    color: #dce4f8;

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
    font-weight: 800 !important;

    background:
        linear-gradient(
            95deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        ) !important;

    border:
        1px solid
        rgba(95, 218, 255, 0.38) !important;

    border-radius:
        var(--ax-radius-sm) !important;

    box-shadow:
        0 10px 26px
        rgba(28, 119, 255, 0.14);

    transition:
        transform 0.18s ease,
        filter 0.18s ease,
        border-color 0.18s ease,
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
        0 14px 32px
        rgba(32, 126, 255, 0.23);
}


.stButton > button[kind="secondary"] {
    color:
        #e9edfb !important;

    background:
        linear-gradient(
            145deg,
            rgba(11, 19, 42, 0.98),
            rgba(5, 10, 25, 0.98)
        ) !important;

    border:
        1px solid
        rgba(75, 101, 164, 0.35) !important;

    box-shadow: none;
}


.stButton > button[kind="secondary"]:hover {
    border-color:
        rgba(32, 221, 245, 0.56) !important;

    background:
        linear-gradient(
            145deg,
            rgba(12, 25, 52, 0.98),
            rgba(6, 13, 31, 0.98)
        ) !important;
}


/* ========================================================
   LOGIN — ESTRUCTURA PREMIUM
   ======================================================== */

.ax-auth-spacer {
    height: 3px;
}


.ax-auth-hero {
    position: relative;

    min-height: 610px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    overflow: hidden;

    padding:
        clamp(30px, 4vw, 52px);

    background:
        radial-gradient(
            circle at 83% 16%,
            rgba(32, 221, 245, 0.13),
            transparent 30%
        ),
        radial-gradient(
            circle at 20% 92%,
            rgba(139, 77, 255, 0.15),
            transparent 34%
        ),
        linear-gradient(
            145deg,
            rgba(3, 11, 27, 0.97),
            rgba(8, 5, 28, 0.97)
        );

    border:
        1px solid
        rgba(67, 105, 175, 0.35);

    border-radius: 25px;

    box-shadow:
        0 30px 90px
        rgba(0, 0, 0, 0.42),
        inset 0 1px 0
        rgba(255, 255, 255, 0.03);
}


.ax-auth-hero::before {
    content: "";

    position: absolute;
    inset: 0;

    pointer-events: none;

    background:
        linear-gradient(
            105deg,
            transparent 22%,
            rgba(32, 221, 245, 0.045) 49%,
            transparent 76%
        );

    transform: translateX(-110%);

    animation:
        ax-auth-scan
        9s
        ease-in-out
        infinite;
}


@keyframes ax-auth-scan {
    0%,
    58% {
        transform: translateX(-110%);
    }

    90%,
    100% {
        transform: translateX(110%);
    }
}


.ax-auth-brand,
.ax-auth-mini-brand {
    display: flex;
    align-items: center;
    gap: 13px;
}


.ax-auth-logo,
.ax-auth-mini-logo {
    width: 46px;
    height: 46px;

    display: grid;
    place-items: center;

    flex-shrink: 0;

    color: white;

    font-size: 17px;
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
        0 0 22px
        rgba(32, 221, 245, 0.27);
}


.ax-auth-brand-title,
.ax-auth-mini-title {
    color: var(--ax-white);

    font-size: 17px;
    font-weight: 950;
}


.ax-auth-brand-subtitle,
.ax-auth-mini-subtitle {
    margin-top: 4px;

    color: var(--ax-dim);

    font-size: 7px;
    font-weight: 800;

    letter-spacing: 1.9px;
}


.ax-auth-eyebrow {
    margin-top: 34px;

    color: var(--ax-cyan);

    font-size: 9px;
    font-weight: 950;

    letter-spacing: 2.2px;
}


.ax-auth-title {
    max-width: 680px;

    margin:
        19px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(43px, 4.4vw, 68px);

    line-height: 1;
    font-weight: 950;

    letter-spacing: -3px;
}


.ax-auth-title span {
    display: block;

    color: transparent;

    background:
        linear-gradient(
            90deg,
            var(--ax-cyan),
            #6f9cff,
            var(--ax-purple)
        );

    background-clip: text;
    -webkit-background-clip: text;
}


.ax-auth-description {
    max-width: 640px;

    margin-top: 23px;

    color: #9aa6c4;

    font-size: 14px;
    line-height: 1.75;
}


.ax-auth-feature-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 11px;

    margin-top: 29px;
}


.ax-auth-feature {
    padding: 14px;

    color: #dde5f9;

    font-size: 11px;
    font-weight: 760;

    background:
        linear-gradient(
            145deg,
            rgba(10, 18, 40, 0.90),
            rgba(5, 10, 25, 0.90)
        );

    border:
        1px solid
        rgba(80, 105, 168, 0.28);

    border-radius: 13px;

    transition:
        transform 0.18s ease,
        border-color 0.18s ease,
        background 0.18s ease;
}


.ax-auth-feature:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(32, 221, 245, 0.45);

    background:
        rgba(11, 22, 48, 0.94);
}


.ax-auth-quote {
    margin-top: 30px;

    padding:
        15px
        17px;

    color: #8f9bb8;

    font-size: 11px;

    background:
        rgba(5, 11, 28, 0.78);

    border-left:
        3px solid
        var(--ax-cyan);

    border-radius:
        5px
        12px
        12px
        5px;
}


.ax-auth-form-shell {
    position: relative;

    min-height: 610px;

    display: flex;
    flex-direction: column;
    justify-content: center;

    padding:
        clamp(26px, 3vw, 42px);

    background:
        radial-gradient(
            circle at 100% 0,
            rgba(139, 77, 255, 0.15),
            transparent 29%
        ),
        linear-gradient(
            145deg,
            rgba(7, 12, 29, 0.98),
            rgba(8, 5, 27, 0.98)
        );

    border:
        1px solid
        rgba(76, 99, 161, 0.30);

    border-radius: 25px;

    box-shadow:
        0 30px 90px
        rgba(0, 0, 0, 0.40);
}


.ax-auth-form-inner {
    width: 100%;
    max-width: 580px;

    margin: auto;
}


.ax-auth-form-header {
    margin-bottom: 20px;
}


.ax-auth-form-header h2 {
    margin:
        23px
        0
        7px;

    color: var(--ax-cyan);

    font-size:
        clamp(28px, 3vw, 41px);

    line-height: 1.05;
    font-weight: 950;

    letter-spacing: -1.6px;
}


.ax-auth-form-header p {
    color: var(--ax-muted);

    font-size: 12px;
}


/* ========================================================
   FORMULARIOS E INPUTS
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
        rgba(91, 113, 172, 0.42) !important;

    border-radius:
        10px !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.025);

    transition:
        border-color 0.16s ease,
        box-shadow 0.16s ease;
}


[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stDateInput"] input:focus,
[data-testid="stTimeInput"] input:focus {
    border-color:
        var(--ax-cyan) !important;

    box-shadow:
        0 0 0 2px
        rgba(32, 221, 245, 0.11) !important;
}


[data-baseweb="select"] > div {
    color: var(--ax-white) !important;

    background:
        rgba(4, 10, 25, 0.97) !important;

    border-color:
        rgba(91, 113, 172, 0.42) !important;

    border-radius:
        10px !important;
}


label,
[data-testid="stWidgetLabel"] {
    color:
        #dce3f5 !important;

    font-size:
        11px !important;
}


/* ========================================================
   TABS
   ======================================================== */

[data-baseweb="tab-list"] {
    gap: 18px;

    border-bottom:
        1px solid
        rgba(87, 107, 165, 0.22);
}


[data-baseweb="tab"] {
    min-height: 40px;

    padding-left: 0 !important;
    padding-right: 0 !important;

    color:
        #7f8ba8 !important;

    background:
        transparent !important;
}


[aria-selected="true"][data-baseweb="tab"] {
    color:
        var(--ax-cyan) !important;

    font-weight: 850;
}


/* ========================================================
   DASHBOARD
   ======================================================== */

.ax-dashboard-hero {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 24px;
    flex-wrap: wrap;

    padding:
        24px
        27px;

    margin-bottom: 17px;

    background:
        radial-gradient(
            circle at 86% 20%,
            rgba(139, 77, 255, 0.17),
            transparent 34%
        ),
        linear-gradient(
            135deg,
            rgba(4, 14, 33, 0.97),
            rgba(13, 7, 38, 0.95)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.38);

    border-radius: 20px;

    box-shadow:
        var(--ax-shadow);
}


.ax-dashboard-eyebrow {
    color: var(--ax-cyan);

    font-size: 8px;
    font-weight: 950;

    letter-spacing: 2px;
}


.ax-dashboard-hero h1 {
    margin:
        8px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(28px, 3vw, 43px);

    line-height: 1.06;
    font-weight: 950;

    letter-spacing: -1.8px;
}


.ax-dashboard-hero p {
    margin:
        8px
        0
        0;

    color: var(--ax-muted);

    font-size: 12px;
}


.ax-dashboard-status-area {
    display: flex;
    align-items: center;

    gap: 11px;
    flex-wrap: wrap;
}


.ax-dashboard-date {
    color: #dce4f7;

    font-size: 9px;
    font-weight: 850;
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


.ax-metric-card {
    position: relative;

    min-height: 138px;

    overflow: hidden;

    padding: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(9, 17, 38, 0.96),
            rgba(5, 10, 26, 0.96)
        );

    border:
        1px solid
        rgba(75, 100, 161, 0.28);

    border-radius: 16px;

    box-shadow:
        0 14px 36px
        rgba(0, 0, 0, 0.27);

    transition:
        transform 0.18s ease,
        border-color 0.18s ease;
}


.ax-metric-card:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(32, 221, 245, 0.36);
}


.ax-metric-label {
    color: #75829f;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 1.45px;
}


.ax-metric-value {
    margin-top: 13px;

    font-size:
        clamp(23px, 2vw, 29px);

    line-height: 1;
    font-weight: 950;
}


.ax-metric-bottom {
    display: flex;
    justify-content: space-between;

    gap: 8px;

    margin-top: 12px;

    color: #7985a3;

    font-size: 7px;
}


.ax-metric-line {
    position: absolute;

    left: 15px;
    right: 15px;
    bottom: 11px;

    height: 2px;

    border-radius: 999px;
}


.ax-panel-title {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 12px;

    margin-top: 14px;
    margin-bottom: 9px;

    padding:
        13px
        16px;

    background:
        rgba(7, 13, 31, 0.91);

    border:
        1px solid
        rgba(76, 99, 157, 0.25);

    border-radius: 14px;
}


.ax-panel-title strong {
    color: var(--ax-white);

    font-size: 13px;
}


.ax-panel-title span {
    color: #697694;

    font-size: 6px;

    letter-spacing: 1.35px;
}


.ax-empty-panel {
    min-height: 330px;

    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;

    text-align: center;

    padding: 24px;

    background:
        rgba(5, 11, 28, 0.84);

    border:
        1px dashed
        rgba(32, 221, 245, 0.29);

    border-radius: 16px;
}


.ax-empty-icon {
    color: var(--ax-cyan);

    font-size: 38px;
}


.ax-empty-panel strong {
    margin-top: 13px;

    color: var(--ax-white);

    font-size: 15px;
}


.ax-empty-panel p {
    margin-top: 7px;

    color: #7e8aa7;

    font-size: 9px;
}


/* ========================================================
   PERFIL
   ======================================================== */

.ax-profile-page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    gap: 22px;
    flex-wrap: wrap;

    padding:
        25px
        28px;

    margin-bottom: 16px;

    background:
        radial-gradient(
            circle at 86% 18%,
            rgba(139, 77, 255, 0.17),
            transparent 32%
        ),
        linear-gradient(
            135deg,
            rgba(4, 14, 33, 0.97),
            rgba(13, 7, 38, 0.95)
        );

    border:
        1px solid
        rgba(32, 221, 245, 0.37);

    border-radius: 20px;

    box-shadow:
        var(--ax-shadow);
}


.ax-profile-page-eyebrow {
    color: var(--ax-cyan);

    font-size: 8px;
    font-weight: 950;

    letter-spacing: 2px;
}


.ax-profile-page-header h1 {
    margin:
        8px
        0
        0;

    color: var(--ax-white);

    font-size:
        clamp(28px, 3vw, 42px);

    font-weight: 950;

    letter-spacing: -1.6px;
}


.ax-profile-page-header p {
    max-width: 700px;

    margin:
        8px
        0
        0;

    color: var(--ax-muted);

    font-size: 12px;
    line-height: 1.6;
}


.ax-profile-page-badge {
    padding:
        9px
        13px;

    color: var(--ax-green);

    background:
        var(--ax-green-soft);

    border:
        1px solid
        rgba(0, 245, 138, 0.32);

    border-radius: 999px;

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 1.2px;
}


.ax-profile-editor-avatar {
    width: 160px;
    height: 160px;

    display: grid;
    place-items: center;

    overflow: hidden;

    margin:
        18px
        auto;

    color: white;

    font-size: 37px;
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
        4px solid
        rgba(255, 255, 255, 0.10);

    box-shadow:
        0 0 35px
        rgba(32, 221, 245, 0.28);
}


.ax-profile-editor-avatar img {
    width: 100%;
    height: 100%;

    display: block;

    object-fit: cover;
    object-position: center;
}


.ax-profile-summary-card,
.ax-profile-security-card {
    margin-top: 13px;

    padding: 18px;

    background:
        linear-gradient(
            145deg,
            rgba(9, 17, 38, 0.95),
            rgba(5, 10, 26, 0.95)
        );

    border:
        1px solid
        rgba(76, 99, 158, 0.27);

    border-radius: 15px;
}


.ax-profile-summary-label {
    color: var(--ax-cyan);

    font-size: 7px;
    font-weight: 950;

    letter-spacing: 1.5px;
}


.ax-profile-summary-name {
    margin-top: 9px;

    color: var(--ax-white);

    font-size: 21px;
    font-weight: 950;
}


.ax-profile-summary-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

    gap: 11px;

    margin-top: 16px;
}


.ax-profile-summary-grid div {
    padding: 12px;

    background:
        rgba(4, 10, 25, 0.78);

    border:
        1px solid
        rgba(75, 98, 155, 0.22);

    border-radius: 11px;
}


.ax-profile-summary-grid span {
    display: block;

    color: #6e7a98;

    font-size: 6px;

    letter-spacing: 1px;
}


.ax-profile-summary-grid strong {
    display: block;

    margin-top: 7px;

    color: var(--ax-white);

    font-size: 14px;
}


.ax-profile-summary-progress {
    height: 5px;

    overflow: hidden;

    margin-top: 15px;

    background: #15203a;

    border-radius: 999px;
}


.ax-profile-summary-progress div {
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


.ax-profile-summary-progress-label {
    margin-top: 6px;

    color: #6f7c99;

    font-size: 7px;
}


.ax-profile-security-card {
    display: flex;
    align-items: flex-start;

    gap: 12px;
}


.ax-profile-security-icon {
    font-size: 22px;
}


.ax-profile-security-card strong {
    color: var(--ax-white);

    font-size: 12px;
}


.ax-profile-security-card p {
    margin:
        7px
        0
        0;

    color: #8793ae;

    font-size: 9px;
    line-height: 1.55;
}


.ax-profile-upload-title {
    margin-top: 15px;

    color: var(--ax-white);

    font-size: 11px;
    font-weight: 850;
}


.ax-profile-upload-description {
    margin-top: 5px;

    color: #7c88a5;

    font-size: 9px;
}


/* ========================================================
   CONTENEDORES, MÉTRICAS, TABLAS Y GRÁFICOS
   ======================================================== */

[data-testid="stVerticalBlockBorderWrapper"] {
    background:
        rgba(6, 12, 29, 0.70);

    border-color:
        rgba(79, 101, 159, 0.26) !important;

    border-radius: 15px;
}


[data-testid="stMetric"] {
    min-height: 105px;

    padding: 14px;

    background:
        rgba(7, 13, 31, 0.91);

    border:
        1px solid
        rgba(77, 101, 162, 0.27);

    border-radius: 14px;
}


[data-testid="stMetricLabel"] {
    color: #75819e;
}


[data-testid="stMetricValue"] {
    color: var(--ax-white);
}


[data-testid="stDataFrame"],
[data-testid="stTable"] {
    overflow: hidden;

    background:
        rgba(4, 9, 23, 0.91);

    border:
        1px solid
        rgba(76, 99, 158, 0.25);

    border-radius: 15px;
}


[data-testid="stPlotlyChart"],
[data-testid="stVegaLiteChart"] {
    overflow: hidden;

    background:
        rgba(4, 9, 23, 0.80);

    border:
        1px solid
        rgba(76, 99, 158, 0.23);

    border-radius: 16px;
}


[data-testid="stFileUploader"] {
    padding: 10px;

    background:
        rgba(5, 11, 28, 0.80);

    border:
        1px dashed
        rgba(32, 221, 245, 0.36);

    border-radius: 14px;
}


[data-testid="stExpander"] {
    overflow: hidden;

    background:
        rgba(6, 12, 29, 0.88);

    border:
        1px solid
        rgba(77, 99, 157, 0.25);

    border-radius: 14px;
}


[data-testid="stAlert"] {
    border:
        1px solid
        rgba(92, 110, 168, 0.25);

    border-radius: 12px;

    backdrop-filter: blur(12px);
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

@media (max-width: 1100px) {

    .ax-auth-feature-grid {
        grid-template-columns: 1fr;
    }

    .ax-auth-title {
        font-size: 48px;
    }

    .ax-auth-hero,
    .ax-auth-form-shell {
        min-height: 560px;
    }
}


@media (max-width: 900px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .ax-dashboard-hero,
    .ax-profile-page-header {
        align-items: flex-start;
    }

    .ax-metric-card {
        min-height: 128px;
    }

    .ax-auth-hero,
    .ax-auth-form-shell {
        min-height: auto;
    }

    .ax-profile-summary-grid {
        grid-template-columns: 1fr;
    }
}


@media (max-width: 700px) {

    .ax-auth-title {
        font-size: 39px;
        letter-spacing: -2px;
    }

    .ax-auth-hero,
    .ax-auth-form-shell {
        padding: 24px;
    }

    .ax-profile-editor-avatar {
        width: 130px;
        height: 130px;
    }

    [data-testid="stAppViewContainer"]::before {
        opacity: 0.18;
    }
}


/* ========================================================
   ACCESIBILIDAD: REDUCIR MOVIMIENTO
   ======================================================== */

@media (prefers-reduced-motion: reduce) {

    *,
    *::before,
    *::after {
        animation-duration:
            0.001ms !important;

        animation-iteration-count:
            1 !important;

        scroll-behavior:
            auto !important;
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
    """

    st.html(
        GLOBAL_CSS
    )
