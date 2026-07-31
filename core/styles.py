from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10
# ESTILOS PREMIUM Y VELAS ANIMADAS
# =========================================================


GLOBAL_CSS = """
<style>

:root {
    --ax-bg: #030612;
    --ax-bg-soft: #070b1c;
    --ax-panel: rgba(8, 14, 34, 0.92);
    --ax-card: rgba(10, 17, 39, 0.92);

    --ax-text: #f5f7ff;
    --ax-muted: #8d99ba;
    --ax-dim: #667393;

    --ax-cyan: #25e5ff;
    --ax-blue: #258cff;
    --ax-purple: #9146ff;
    --ax-green: #00ff88;
    --ax-red: #ff1744;
}


html,
body,
.stApp,
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 10% 5%,
            rgba(37, 229, 255, 0.11),
            transparent 30%
        ),
        radial-gradient(
            circle at 85% 20%,
            rgba(145, 70, 255, 0.15),
            transparent 35%
        ),
        linear-gradient(
            135deg,
            #030612,
            #050919 50%,
            #090419
        ) !important;

    color: var(--ax-text);
}


/* ========================================================
   VELAS JAPONESAS ANIMADAS
   ======================================================== */

[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;

    background-image:
        linear-gradient(
            to bottom,
            transparent 0 18%,
            rgba(0, 255, 136, 0.82) 18% 73%,
            transparent 73% 100%
        ),
        linear-gradient(
            to bottom,
            transparent 0 33%,
            rgba(255, 23, 68, 0.82) 33% 79%,
            transparent 79% 100%
        ),
        linear-gradient(
            to bottom,
            transparent 0 7%,
            rgba(0, 255, 136, 0.42) 7% 91%,
            transparent 91% 100%
        ),
        linear-gradient(
            to bottom,
            transparent 0 15%,
            rgba(255, 23, 68, 0.42) 15% 94%,
            transparent 94% 100%
        );

    background-size:
        11px 175px,
        12px 210px,
        2px 235px,
        2px 250px;

    background-position:
        30px 80px,
        105px 175px,
        34px 45px,
        110px 145px;

    background-repeat: repeat-x;

    opacity: 0.52;

    filter:
        drop-shadow(
            0 0 9px
            rgba(0, 255, 136, 0.40)
        )
        drop-shadow(
            0 0 9px
            rgba(255, 23, 68, 0.34)
        );

    animation:
        ax-candle-scroll 27s linear infinite,
        ax-candle-glow 5s ease-in-out infinite alternate;
}


[data-testid="stAppViewContainer"]::after {
    content: "";
    position: fixed;
    left: 12%;
    right: 0;
    bottom: -24px;
    height: 210px;
    pointer-events: none;
    z-index: 0;

    background:
        repeating-linear-gradient(
            90deg,
            transparent 0 18px,
            rgba(0, 255, 136, 0.62) 18px 27px,
            transparent 27px 43px,
            rgba(255, 23, 68, 0.60) 43px 52px,
            transparent 52px 70px
        );

    -webkit-mask-image:
        linear-gradient(
            to top,
            black 0%,
            rgba(0, 0, 0, 0.88) 45%,
            transparent 100%
        );

    mask-image:
        linear-gradient(
            to top,
            black 0%,
            rgba(0, 0, 0, 0.88) 45%,
            transparent 100%
        );

    opacity: 0.55;

    filter:
        drop-shadow(
            0 0 10px
            rgba(0, 255, 136, 0.28)
        )
        drop-shadow(
            0 0 10px
            rgba(255, 23, 68, 0.25)
        );

    animation:
        ax-volume-scroll 19s linear infinite;
}


@keyframes ax-candle-scroll {
    from {
        background-position:
            30px 80px,
            105px 175px,
            34px 45px,
            110px 145px;
    }

    to {
        background-position:
            870px 80px,
            945px 175px,
            874px 45px,
            950px 145px;
    }
}


@keyframes ax-candle-glow {
    from {
        opacity: 0.40;
    }

    to {
        opacity: 0.66;
    }
}


@keyframes ax-volume-scroll {
    from {
        background-position-x: 0;
    }

    to {
        background-position-x: 560px;
    }
}


[data-testid="stMain"],
[data-testid="stSidebar"],
[data-testid="stHeader"] {
    position: relative;
    z-index: 2;
}


[data-testid="stHeader"] {
    background:
        rgba(3, 6, 18, 0.82) !important;

    backdrop-filter:
        blur(18px);

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
        1.2rem
        1rem
        1.5rem;
}


.ax-brand {
    display: flex;
    align-items: center;
    gap: 12px;

    position: relative;

    padding:
        8px
        6px
        21px;

    margin-bottom:
        15px;

    border-bottom:
        1px solid
        rgba(82, 103, 158, 0.18);
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
        0 0 25px
        rgba(37, 229, 255, 0.32);
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
            rgba(11, 21, 47, 0.94),
            rgba(7, 11, 27, 0.94)
        );

    border:
        1px solid
        rgba(37, 229, 255, 0.30);

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
    padding:
        3px
        7px;

    border-radius:
        999px;

    background:
        var(--ax-purple);

    color: white;
    font-size: 7px;
    font-weight: 950;
}


.ax-profile-email {
    overflow: hidden;

    margin-top:
        5px;

    color:
        #697696;

    font-size:
        8px;

    text-overflow:
        ellipsis;

    white-space:
        nowrap;
}


.ax-profile-capital-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;

    margin-top:
        15px;
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

    background:
        #18213d;
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
        24px
        4px
        10px;

    color: #647291;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 2px;
}


.ax-system-card {
    padding: 14px;

    background:
        rgba(7, 12, 28, 0.82);

    border:
        1px solid
        rgba(77, 99, 157, 0.25);

    border-radius:
        14px;
}


.ax-system-row {
    display: flex;
    justify-content: space-between;

    margin-bottom:
        11px;

    color:
        #dbe4fb;

    font-size:
        9px;
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
            rgba(6, 15, 34, 0.96),
            rgba(15, 8, 40, 0.93)
        );

    border:
        1px solid
        rgba(37, 229, 255, 0.42);

    border-radius:
        22px;

    box-shadow:
        0 25px 70px
        rgba(0, 0, 0, 0.35);
}


.ax-dashboard-eyebrow {
    color:
        var(--ax-cyan);

    font-size:
        9px;

    font-weight:
        950;

    letter-spacing:
        2px;
}


.ax-dashboard-hero h1 {
    margin:
        10px
        0
        0;

    color:
        white;

    font-size:
        clamp(
            29px,
            3vw,
            45px
        );

    line-height:
        1.06;

    font-weight:
        950;

    letter-spacing:
        -1.8px;
}


.ax-dashboard-hero p {
    margin:
        10px
        0
        0;

    color:
        var(--ax-muted);

    font-size:
        13px;

    line-height:
        1.6;
}


.ax-dashboard-status-area {
    display:
        flex;

    align-items:
        center;

    gap:
        12px;

    flex-wrap:
        wrap;
}


.ax-dashboard-date {
    color:
        #dce6ff;

    font-size:
        11px;

    font-weight:
        900;
}


.ax-market-status {
    display:
        flex;

    align-items:
        center;

    gap:
        8px;

    padding:
        10px
        15px;

    color:
        var(--ax-green);

    font-size:
        9px;

    font-weight:
        950;

    border:
        1px solid
        rgba(0, 255, 136, 0.35);

    border-radius:
        999px;

    background:
        rgba(0, 255, 136, 0.08);
}


.ax-market-status span {
    width:
        8px;

    height:
        8px;

    border-radius:
        50%;

    background:
        var(--ax-green);

    box-shadow:
        0 0 12px
        var(--ax-green);
}


.ax-metric-card {
    min-height:
        150px;

    position:
        relative;

    overflow:
        hidden;

    padding:
        18px;

    background:
        linear-gradient(
            145deg,
            rgba(11, 20, 44, 0.94),
            rgba(7, 12, 29, 0.94)
        );

    border:
        1px solid
        rgba(77, 100, 162, 0.28);

    border-radius:
        17px;

    box-shadow:
        0 15px 45px
        rgba(0, 0, 0, 0.31);
}


.ax-metric-label {
    color:
        #7f8bad;

    font-size:
        8px;

    font-weight:
        950;

    letter-spacing:
        1.4px;
}


.ax-metric-value {
    margin-top:
        15px;

    font-size:
        27px;

    line-height:
        1;

    font-weight:
        950;
}


.ax-metric-bottom {
    display:
        flex;

    justify-content:
        space-between;

    gap:
        8px;

    margin-top:
        13px;

    color:
        #8794b4;

    font-size:
        8px;
}


.ax-metric-line {
    position:
        absolute;

    left:
        17px;

    right:
        17px;

    bottom:
        12px;

    height:
        3px;

    border-radius:
        999px;
}


.ax-panel-title {
    display:
        flex;

    justify-content:
        space-between;

    align-items:
        center;

    gap:
        12px;

    padding:
        15px
        18px;

    margin-top:
        15px;

    margin-bottom:
        9px;

    background:
        rgba(8, 14, 34, 0.88);

    border:
        1px solid
        rgba(77, 99, 157, 0.25);

    border-radius:
        15px;
}


.ax-panel-title strong {
    color:
        white;
}


.ax-panel-title span {
    color:
        #7180a4;

    font-size:
        7px;

    letter-spacing:
        1.2px;
}


.ax-empty-panel {
    min-height:
        355px;

    display:
        flex;

    flex-direction:
        column;

    align-items:
        center;

    justify-content:
        center;

    text-align:
        center;

    padding:
        25px;

    background:
        rgba(6, 11, 29, 0.81);

    border:
        1px dashed
        rgba(37, 229, 255, 0.30);

    border-radius:
        17px;
}


.ax-empty-icon {
    color:
        var(--ax-cyan);

    font-size:
        42px;
}


.ax-empty-panel strong {
    margin-top:
        14px;

    color:
        white;

    font-size:
        16px;
}


.ax-empty-panel p {
    margin-top:
        8px;

    color:
        #8290b1;

    font-size:
        10px;
}


.ax-image-placeholder {
    min-height:
        230px;

    display:
        grid;

    place-items:
        center;

    color:
        #7f8bad;

    background:
        rgba(6, 11, 29, 0.81);

    border:
        1px dashed
        rgba(37, 229, 255, 0.30);

    border-radius:
        17px;
}


/* ========================================================
   BOTONES, INPUTS Y TARJETAS
   ======================================================== */

.stButton > button,
.stDownloadButton > button {
    min-height:
        44px;

    color:
        white !important;

    font-weight:
        850 !important;

    background:
        linear-gradient(
            90deg,
            var(--ax-cyan),
            var(--ax-blue),
            var(--ax-purple)
        ) !important;

    border:
        1px solid
        rgba(99, 219, 255, 0.40) !important;

    border-radius:
        11px !important;

    transition:
        transform
        0.18s
        ease;
}


.stButton > button:hover {
    transform:
        translateY(-1px);

    filter:
        brightness(1.08);
}


.stButton > button[kind="secondary"] {
    background:
        linear-gradient(
            145deg,
            rgba(13, 22, 48, 0.95),
            rgba(7, 12, 29, 0.95)
        ) !important;

    border:
        1px solid
        rgba(83, 105, 166, 0.35) !important;
}


[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stDateInput"] input {
    color:
        white !important;

    background:
        rgba(6, 11, 29, 0.95) !important;

    border:
        1px solid
        rgba(94, 112, 169, 0.38) !important;

    border-radius:
        10px !important;
}


[data-baseweb="select"] > div {
    color:
        white !important;

    background:
        rgba(6, 11, 29, 0.95) !important;

    border-color:
        rgba(94, 112, 169, 0.38) !important;
}


[data-testid="stMetric"] {
    padding:
        15px;

    background:
        rgba(8, 14, 34, 0.88);

    border:
        1px solid
        rgba(77, 100, 162, 0.28);

    border-radius:
        15px;
}


[data-testid="stDataFrame"],
[data-testid="stPlotlyChart"] {
    overflow:
        hidden;

    border:
        1px solid
        rgba(77, 100, 162, 0.25);

    border-radius:
        16px;

    background:
        rgba(6, 11, 29, 0.82);
}


::-webkit-scrollbar {
    width:
        9px;
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
}


@media (max-width: 900px) {
    .ax-dashboard-hero {
        align-items:
            flex-start;
    }

    .ax-metric-card {
        min-height:
            135px;
    }
}

</style>
"""


def apply_styles() -> None:
    st.html(GLOBAL_CSS)
