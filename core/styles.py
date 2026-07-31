from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10
# DISEÑO PREMIUM COMPLETO
# =========================================================


GLOBAL_CSS = """
<style>

/* ========================================================
   VARIABLES
   ======================================================== */

:root {
    --ax-bg-primary: #030612;
    --ax-bg-secondary: #060a18;
    --ax-bg-tertiary: #090e22;

    --ax-panel: rgba(8, 14, 34, 0.93);
    --ax-panel-soft: rgba(10, 17, 39, 0.88);
    --ax-panel-strong: rgba(6, 11, 28, 0.97);

    --ax-border: rgba(84, 107, 170, 0.27);
    --ax-border-cyan: rgba(37, 229, 255, 0.42);

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

    --ax-radius-small: 11px;
    --ax-radius-medium: 16px;
    --ax-radius-large: 22px;

    --ax-shadow:
        0 22px 70px rgba(0, 0, 0, 0.38),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
}


/* ========================================================
   BASE GENERAL
   ======================================================== */

html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 10% 4%,
            rgba(37, 229, 255, 0.10),
            transparent 29%
        ),
        radial-gradient(
            circle at 85% 18%,
            rgba(145, 70, 255, 0.14),
            transparent 34%
        ),
        radial-gradient(
            circle at 60% 95%,
            rgba(255, 23, 68, 0.045),
            transparent 25%
        ),
        linear-gradient(
            135deg,
            var(--ax-bg-primary),
            var(--ax-bg-secondary) 52%,
            #090419
        ) !important;

    color: var(--ax-text);
}


/* ========================================================
   FONDO DE VELAS JAPONESAS ANIMADAS
   ======================================================== */

/*
Las velas se crean únicamente con CSS.
No se insertan etiquetas HTML que puedan aparecer como texto.
*/

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;

    background-image:
        repeating-linear-gradient(
            90deg,
            transparent 0 38px,
            rgba(0, 255, 136, 0.00) 38px 45px,
            rgba(0, 255, 136, 0.22) 45px 50px,
            rgba(0, 255, 136, 0.00) 50px 72px,
            rgba(255, 23, 68, 0.00) 72px 80px,
            rgba(255, 23, 68, 0.22) 80px 85px,
            rgba(255, 23, 68, 0.00) 85px 118px
        );

    opacity: 0.30;

    mask-image:
        linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.28) 0%,
            rgba(0, 0, 0, 0.07) 38%,
            rgba(0, 0, 0, 0.10) 65%,
            rgba(0, 0, 0, 0.58) 100%
        );

    -webkit-mask-image:
        linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.28) 0%,
            rgba(0, 0, 0, 0.07) 38%,
            rgba(0, 0, 0, 0.10) 65%,
            rgba(0, 0, 0, 0.58) 100%
        );

    filter:
        drop-shadow(
            0 0 8px
            rgba(0, 255, 136, 0.19)
        )
        drop-shadow(
            0 0 8px
            rgba(255, 23, 68, 0.17)
        );

    animation:
        ax-background-candles 28s linear infinite,
        ax-background-pulse 6s ease-in-out infinite alternate;
}


/*
Zona inferior con velas más claras.
*/

[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    left: 11%;
    right: 0;
    bottom: -28px;
    height: 205px;
    z-index: 0;
    pointer-events: none;

    background:
        repeating-linear-gradient(
            90deg,
            transparent 0 18px,
            rgba(0, 255, 136, 0.62) 18px 26px,
            transparent 26px 42px,
            rgba(255, 23, 68, 0.60) 42px 51px,
            transparent 51px 70px
        );

    mask-image:
        linear-gradient(
            to top,
            rgba(0, 0, 0, 0.95) 0%,
            rgba(0, 0, 0, 0.72) 48%,
            transparent 100%
        );

    -webkit-mask-image:
        linear-gradient(
            to top,
            rgba(0, 0, 0, 0.95) 0%,
            rgba(0, 0, 0, 0.72) 48%,
            transparent 100%
        );

    opacity: 0.50;

    filter:
        drop-shadow(
            0 0 9px
            rgba(0, 255, 136, 0.28)
        )
        drop-shadow(
            0 0 9px
            rgba(255, 23, 68, 0.25)
        );

    animation:
        ax-volume-candles 20s linear infinite;
}


@keyframes ax-background-candles {
    from {
        background-position-x: 0;
    }

    to {
        background-position-x: 708px;
    }
}


@keyframes ax-background-pulse {
    from {
        opacity: 0.20;
    }

    to {
        opacity: 0.38;
    }
}


@keyframes ax-volume-candles {
    from {
        background-position-x: 0;
    }

    to {
        background-position-x: 560px;
    }
}


/* Contenido por encima del fondo */

[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    position: relative;
    z-index: 2;
}


[data-testid="stHeader"] {
    background:
        rgba(3, 6, 18, 0.84) !important;

    backdrop-filter: blur(18px);

    border-bottom:
        1px solid
        rgba(83, 107, 169, 0.15);
}


.block-container {
    max-width: 1680px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* ========================================================
   TIPOGRAFÍA
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
div,
button,
input,
textarea {
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
h3,
h4 {
    color: var(--ax-text);
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
            rgba(4, 12, 28, 0.97),
            rgba(10, 5, 30, 0.96)
        );

    border:
        1px solid
        rgba(69, 127, 201, 0.38);

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
            100deg,
            transparent 20%,
            rgba(37, 229, 255, 0.045) 48%,
            transparent 75%
        );

    transform: translateX(-110%);

    animation:
        ax-auth-light 8s ease-in-out infinite;
}


@keyframes ax-auth-light {
    0%,
    55% {
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
        0 0 24px rgba(37, 229, 255, 0.30),
        0 0 38px rgba(145, 70, 255, 0.19);
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
            rgba(11, 19, 43, 0.88),
            rgba(6, 10, 25, 0.88)
        );

    border:
        1px solid
        rgba(88, 109, 170, 0.29);

    border-radius: 14px;

    transition:
        transform 0.22s ease,
        border-color 0.22s ease;
}


.ax-auth-feature:hover {
    border-color:
        rgba(37, 229, 255, 0.48);

    transform:
        translateY(-2px);
}


.ax-auth-quote {
    margin-top: 39px;
    padding: 17px 18px;

    color: #91a0c1;
    font-size: 12px;

    border-left:
        3px solid
        var(--ax-cyan);

    border-radius:
        5px 12px 12px 5px;

    background:
        rgba(7, 13, 34, 0.78);
}


.ax-auth-form-header {
    margin-bottom: 22px;
}


.ax-auth-form-header h2 {
    margin: 28px 0 8px;

    color: var(--ax-cyan);

    font-size:
        clamp(30px, 3vw, 42px);

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
            rgba(9, 13, 31, 0.97),
            rgba(9, 5, 29, 0.97)
        );

    border:
        1px solid
        rgba(86, 104, 164, 0.29);

    border-radius: 26px;

    box-shadow:
        0 30px 100px
        rgba(0, 0, 0, 0.45);
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
            rgba(37, 229, 255, 0.11),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            rgba(4, 9, 24, 0.99),
            rgba(5, 7, 20, 0.99)
        ) !important;

    border-right:
        1px solid
        rgba(65, 94, 155, 0.28);
}


[data-testid="stSidebarContent"] {
    padding:
        1.2rem 1rem 1.5rem;
}


.ax-brand {
    display: flex;
    align-items: center;
    gap: 12px;

    position: relative;

    padding:
        8px 6px 21px;

    margin-bottom: 15px;

    border-bottom:
        1px solid
        rgba(82, 103, 158, 0.18);
}


.ax-brand b {
    display: block;
    color: var(--ax-text);
    font-size: 14px;
}


.ax-brand small {
    display: block;

    margin-top: 4px;

    color: var(--ax-dim);
    font-size: 7px;
    letter-spacing: 1.5px;
}


.ax-brand-online {
    width: 8px;
    height: 8px;

    margin-left: auto;

    border-radius: 50%;

    background:
        var(--ax-green);

    box-shadow:
        0 0 13px
        var(--ax-green);
}


.ax-profile {
    margin-bottom: 19px;
    padding: 16px;

    background:
        linear-gradient(
            145deg,
            rgba(11, 21, 47, 0.95),
            rgba(7, 11, 27, 0.95)
        );

    border:
        1px solid
        rgba(37, 229, 255, 0.31);

    border-radius: 18px;

    box-shadow:
        0 18px 45px
        rgba(0, 0, 0, 0.31);
}


.ax-profile-top {
    display: flex;
    align-items: center;
    gap: 12px;
}


.ax-profile-avatar {
    width: 58px;
    height: 58px;

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
        3px solid
        rgba(255, 255, 255, 0.12);

    box-shadow:
        0 0 25px
        rgba(37, 229, 255, 0.35);
}


/* FOTO REAL DEL PERFIL */

.ax-profile-photo {
    overflow: hidden;
    padding: 0;
    background: #07101f;
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
    gap: 7px;
    flex-wrap: wrap;

    color: white;
    font-size: 13px;
}


.ax-profile-role {
    padding: 3px 7px;

    border-radius: 999px;

    background:
        var(--ax-purple);

    color: white;
    font-size: 7px;
    font-weight: 950;
}


.ax-profile-email {
    overflow: hidden;

    margin-top: 5px;

    color: #697696;

    font-size: 8px;

    text-overflow: ellipsis;
    white-space: nowrap;
}


.ax-profile-capital-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;

    margin-top: 15px;
}


.ax-profile-capital {
    color: white;
    font-size: 19px;
    font-weight: 950;
}


.ax-profile-capital-label {
    margin-top: 4px;

    color: var(--ax-cyan);
    font-size: 7px;
    font-weight: 900;
    letter-spacing: 1.3px;
}


.ax-profile-target {
    color: #73809f;
    font-size: 7px;
}


.ax-progress-track {
    overflow: hidden;

    height: 5px;

    margin-top: 11px;

    border-radius: 999px;

    background: #18213d;
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
        0 0 13px
        rgba(37, 229, 255, 0.50);
}


.ax-progress-labels {
    display: flex;
    justify-content: space-between;

    margin-top: 6px;

    color: #6f7d9e;
    font-size: 7px;
}


.ax-section-title {
    margin:
        24px 4px 10px;

    color: #647291;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 2px;
}


.ax-system-card {
    padding: 14px;

    background:
        rgba(7, 12, 28, 0.84);

    border:
        1px solid
        rgba(77, 99, 157, 0.26);

    border-radius: 14px;
}


.ax-system-row {
    display: flex;
    justify-content: space-between;

    margin-bottom: 11px;

    color: #dbe4fb;
    font-size: 9px;
}


.ax-system-row:last-child {
    margin-bottom: 0;
}


.ax-system-row b {
    color: var(--ax-green);
    font-size: 8px;
}


/* ========================================================
   DASHBOARD
   ======================================================== */

.ax-dashboard-hero {
    display: flex;
    justify-content: space-between;
    align-items: center;

    gap: 25px;
    flex-wrap: wrap;

    padding: 28px 31px;
    margin-bottom: 18px;

    background:
        radial-gradient(
            circle at 85% 25%,
            rgba(145, 70, 255, 0.18),
            transparent 34%
        ),
        linear-gradient(
            135deg,
            rgba(6, 15, 34, 0.97),
            rgba(15, 8, 40, 0.94)
        );

    border:
        1px solid
        rgba(37, 229, 255, 0.43);

    border-radius: 22px;

    box-shadow:
        0 25px 70px
        rgba(0, 0, 0, 0.35);
}


.ax-dashboard-eyebrow {
    color: var(--ax-cyan);

    font-size: 9px;
    font-weight: 950;
    letter-spacing: 2px;
}


.ax-dashboard-hero h1 {
    margin: 10px 0 0;

    color: white;

    font-size:
        clamp(29px, 3vw, 45px);

    line-height: 1.06;
    font-weight: 950;
    letter-spacing: -1.8px;
}


.ax-dashboard-hero p {
    margin: 10px 0 0;

    color: var(--ax-muted);

    font-size: 13px;
    line-height: 1.6;
}


.ax-dashboard-status-area {
    display: flex;
    align-items: center;

    gap: 12px;
    flex-wrap: wrap;
}


.ax-dashboard-date {
    color: #dce6ff;

    font-size: 11px;
    font-weight: 900;
}


.ax-market-status {
    display: flex;
    align-items: center;

    gap: 8px;

    padding: 10px 15px;

    color: var(--ax-green);

    font-size: 9px;
    font-weight: 950;

    border:
        1px solid
        rgba(0, 255, 136, 0.35);

    border-radius: 999px;

    background:
        rgba(0, 255, 136, 0.08);
}


.ax-market-status span {
    width: 8px;
    height: 8px;

    border-radius: 50%;

    background: var(--ax-green);

    box-shadow:
        0 0 12px
        var(--ax-green);
}


.ax-metric-card {
    min-height: 150px;

    position: relative;
    overflow: hidden;

    padding: 18px;

    background:
        linear-gradient(
            145deg,
            rgba(11, 20, 44, 0.95),
            rgba(7, 12, 29, 0.95)
        );

    border:
        1px solid
        rgba(77, 100, 162, 0.29);

    border-radius: 17px;

    box-shadow:
        0 15px 45px
        rgba(0, 0, 0, 0.31);
}


.ax-metric-label {
    color: #7f8bad;

    font-size: 8px;
    font-weight: 950;
    letter-spacing: 1.4px;
}


.ax-metric-value {
    margin-top: 15px;

    font-size: 27px;
    line-height: 1;
    font-weight: 950;
}


.ax-metric-bottom {
    display: flex;
    justify-content: space-between;

    gap: 8px;

    margin-top: 13px;

    color: #8794b4;
    font-size: 8px;
}


.ax-metric-line {
    position: absolute;

    left: 17px;
    right: 17px;
    bottom: 12px;

    height: 3px;

    border-radius: 999px;
}


.ax-panel-title {
    display: flex;
    justify-content: space-between;
    align-items: center;

    gap: 12px;

    padding: 15px 18px;

    margin-top: 15px;
    margin-bottom: 9px;

    background:
        rgba(8, 14, 34, 0.90);

    border:
        1px solid
        rgba(77, 99, 157, 0.26);

    border-radius: 15px;
}


.ax-panel-title strong {
    color: white;
}


.ax-panel-title span {
    color: #7180a4;

    font-size: 7px;
    letter-spacing: 1.2px;
}


.ax-empty-panel {
    min-height: 355px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    text-align: center;

    padding: 25px;

    background:
        rgba(6, 11, 29, 0.83);

    border:
        1px dashed
        rgba(37, 229, 255, 0.31);

    border-radius: 17px;
}


.ax-empty-icon {
    color: var(--ax-cyan);
    font-size: 42px;
}


.ax-empty-panel strong {
    margin-top: 14px;

    color: white;
    font-size: 16px;
}


.ax-empty-panel p {
    margin-top: 8px;

    color: #8290b1;
    font-size: 10px;
}


.ax-image-placeholder {
    min-height: 230px;

    display: grid;
    place-items: center;

    color: #7f8bad;

    background:
        rgba(6, 11, 29, 0.83);

    border:
        1px dashed
        rgba(37, 229, 255, 0.31);

    border-radius: 17px;
}


/* ========================================================
   BOTONES
   ======================================================== */

.stButton > button,
.stDownloadButton > button,
[data-testid="stFormSubmitButton"] > button {
    min-height: 44px;

    color: white !important;
    font-weight: 850 !important;

    background:
        linear-gradient(
            90deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        ) !important;

    border:
        1px solid
        rgba(99, 219, 255, 0.42) !important;

    border-radius:
        var(--ax-radius-small) !important;

    box-shadow:
        0 10px 28px
        rgba(37, 140, 255, 0.15);

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
        saturate(1.10);

    box-shadow:
        0 14px 35px
        rgba(37, 140, 255, 0.25);
}


.stButton > button[kind="secondary"] {
    background:
        linear-gradient(
            145deg,
            rgba(13, 22, 48, 0.96),
            rgba(7, 12, 29, 0.96)
        ) !important;

    border:
        1px solid
        rgba(83, 105, 166, 0.36) !important;
}


.stButton > button[kind="secondary"]:hover {
    border-color:
        rgba(37, 229, 255, 0.55) !important;
}


/* ========================================================
   INPUTS Y SELECTORES
   ======================================================== */

[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input,
[data-testid="stTimeInput"] input {
    color: white !important;

    background:
        rgba(6, 11, 29, 0.96) !important;

    border:
        1px solid
        rgba(94, 112, 169, 0.39) !important;

    border-radius:
        10px !important;

    box-shadow:
        inset 0 1px 0
        rgba(255, 255, 255, 0.025);
}


[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stDateInput"] input:focus {
    border-color:
        var(--ax-cyan) !important;

    box-shadow:
        0 0 0 2px
        rgba(37, 229, 255, 0.12) !important;
}


[data-baseweb="select"] > div {
    color: white !important;

    background:
        rgba(6, 11, 29, 0.96) !important;

    border-color:
        rgba(94, 112, 169, 0.39) !important;

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
        rgba(92, 109, 164, 0.24);
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

    font-weight: 900;
}


/* ========================================================
   MÉTRICAS
   ======================================================== */

[data-testid="stMetric"] {
    min-height: 110px;

    padding: 15px;

    background:
        rgba(8, 14, 34, 0.90);

    border:
        1px solid
        rgba(77, 100, 162, 0.29);

    border-radius: 15px;

    box-shadow:
        0 14px 40px
        rgba(0, 0, 0, 0.28);
}


[data-testid="stMetricLabel"] {
    color: #7886a7;
}


[data-testid="stMetricValue"] {
    color: var(--ax-text);
}


/* ========================================================
   ALERTAS
   ======================================================== */

[data-testid="stAlert"] {
    border-radius: 13px;

    border:
        1px solid
        rgba(92, 110, 168, 0.26);

    backdrop-filter:
        blur(12px);
}


/* ========================================================
   TABLAS Y GRÁFICOS
   ======================================================== */

[data-testid="stDataFrame"],
[data-testid="stTable"] {
    overflow: hidden;

    border:
        1px solid
        rgba(80, 101, 162, 0.25);

    border-radius: 15px;

    background:
        rgba(6, 11, 29, 0.82);
}


[data-testid="stPlotlyChart"] {
    overflow: hidden;

    border:
        1px solid
        rgba(80, 101, 162, 0.23);

    border-radius: 17px;

    background:
        rgba(5, 10, 26, 0.74);
}


/* ========================================================
   CARGA DE ARCHIVOS
   ======================================================== */

[data-testid="stFileUploader"] {
    padding: 10px;

    border:
        1px dashed
        rgba(37, 229, 255, 0.36);

    border-radius: 14px;

    background:
        rgba(7, 13, 31, 0.78);
}


/* ========================================================
   EXPANDERS
   ======================================================== */

[data-testid="stExpander"] {
    overflow: hidden;

    border:
        1px solid
        rgba(77, 99, 157, 0.26);

    border-radius: 14px;

    background:
        rgba(7, 12, 28, 0.84);
}


/* ========================================================
   SCROLLBAR
   ======================================================== */

::-webkit-scrollbar {
    width: 9px;
    height: 9px;
}


::-webkit-scrollbar-track {
    background: #050817;
}


::-webkit-scrollbar-thumb {
    background:
        linear-gradient(
            var(--ax-cyan),
            var(--ax-purple)
        );

    border-radius: 999px;

    border:
        2px solid
        #050817;
}


/* ========================================================
   RESPONSIVE
   ======================================================== */

@media (max-width: 1100px) {

    .ax-auth-feature-grid {
        grid-template-columns: 1fr;
    }

    .ax-auth-title {
        font-size: 50px;
    }

    .ax-auth-hero {
        padding: 34px;
    }
}


@media (max-width: 900px) {

    .ax-dashboard-hero {
        align-items: flex-start;
    }

    .ax-metric-card {
        min-height: 135px;
    }
}


@media (max-width: 800px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .ax-auth-title {
        font-size: 42px;
    }

    .ax-auth-hero,
    .ax-auth-form-shell {
        min-height: auto;
    }
}

</style>
"""


# =========================================================
# FUNCIÓN PRINCIPAL
# =========================================================


def apply_styles() -> None:
    """
    Aplica todos los estilos de AXION PRIME.

    Las velas se generan con CSS para evitar que sus
    etiquetas aparezcan escritas en la pantalla.
    """

    st.html(
        GLOBAL_CSS
    )
