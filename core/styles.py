from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# ESTILOS GENERALES
# =========================================================


def apply_styles() -> None:
    """
    Aplica toda la identidad visual de AXION PRIME:

    - Fondo oscuro tipo Prop Firm.
    - Tarjetas premium.
    - Sidebar futurista.
    - Botones con degradado.
    - Velas japonesas animadas.
    - Colores neón intensos.
    """

    css = """
    <style>

    /* =====================================================
       VARIABLES
    ===================================================== */

    :root {

        --ax-bg:
            #030713;

        --ax-bg-soft:
            #070b18;

        --ax-panel:
            rgba(
                8,
                13,
                31,
                0.96
            );

        --ax-panel-soft:
            rgba(
                12,
                19,
                43,
                0.92
            );

        --ax-border:
            rgba(
                91,
                119,
                196,
                0.26
            );

        --ax-cyan:
            #25e5ff;

        --ax-blue:
            #218cff;

        --ax-violet:
            #8b46ff;

        --ax-purple:
            #ba38ff;

        --ax-green:
            #00ff88;

        --ax-red:
            #ff1744;

        --ax-yellow:
            #ffd740;

        --ax-text:
            #f5f7ff;

        --ax-muted:
            #7f8bad;
    }


    /* =====================================================
       APP
    ===================================================== */

    html,
    body,
    [class*="css"] {

        font-family:
            Inter,
            "Segoe UI",
            Arial,
            sans-serif;
    }


    .stApp {

        color:
            var(
                --ax-text
            );

        background:

            radial-gradient(
                circle at 15% 10%,
                rgba(
                    0,
                    229,
                    255,
                    0.15
                ),
                transparent 28%
            ),

            radial-gradient(
                circle at 88% 9%,
                rgba(
                    132,
                    65,
                    255,
                    0.19
                ),
                transparent 30%
            ),

            radial-gradient(
                circle at 65% 92%,
                rgba(
                    169,
                    39,
                    255,
                    0.12
                ),
                transparent 30%
            ),

            linear-gradient(
                145deg,
                #020611,
                #070919 58%,
                #03040c
            ) !important;

        min-height:
            100vh;
    }


    .block-container {

        max-width:
            1750px !important;

        padding-top:
            1rem !important;

        padding-left:
            1.8rem !important;

        padding-right:
            1.8rem !important;

        padding-bottom:
            4rem !important;

        position:
            relative;

        z-index:
            3;
    }


    header[data-testid="stHeader"] {

        background:
            rgba(
                3,
                6,
                18,
                0.84
            ) !important;

        backdrop-filter:
            blur(
                14px
            );

        border-bottom:
            1px solid
            rgba(
                255,
                255,
                255,
                0.04
            );
    }


    /* =====================================================
       TEXTO
    ===================================================== */

    h1,
    h2,
    h3,
    h4 {

        color:
            var(
                --ax-text
            ) !important;

        letter-spacing:
            -0.03em;

        font-weight:
            900 !important;
    }


    p,
    label,
    span,
    div {

        color:
            inherit;
    }


    a {

        color:
            var(
                --ax-cyan
            ) !important;
    }


    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[
        data-testid="stSidebar"
    ] {

        min-width:
            305px !important;

        max-width:
            305px !important;

        background:

            radial-gradient(
                circle at 15% 8%,
                rgba(
                    0,
                    225,
                    255,
                    0.10
                ),
                transparent 27%
            ),

            linear-gradient(
                180deg,
                #050a16,
                #080a17 58%,
                #040611
            ) !important;

        border-right:
            1px solid
            rgba(
                41,
                218,
                255,
                0.23
            ) !important;

        box-shadow:
            16px 0 70px
            rgba(
                0,
                0,
                0,
                0.32
            );
    }


    section[
        data-testid="stSidebar"
    ] > div {

        padding-top:
            1rem;
    }


    section[
        data-testid="stSidebar"
    ] .block-container {

        padding-left:
            1rem !important;

        padding-right:
            1rem !important;
    }


    /* =====================================================
       BOTONES SIDEBAR
    ===================================================== */

    section[
        data-testid="stSidebar"
    ] .stButton > button {

        min-height:
            50px !important;

        width:
            100% !important;

        border-radius:
            13px !important;

        justify-content:
            flex-start !important;

        text-align:
            left !important;

        padding-left:
            17px !important;

        color:
            #f2f6ff !important;

        background:

            linear-gradient(
                145deg,
                rgba(
                    16,
                    27,
                    56,
                    0.98
                ),
                rgba(
                    6,
                    11,
                    26,
                    0.98
                )
            ) !important;

        border:
            1px solid
            rgba(
                89,
                118,
                196,
                0.28
            ) !important;

        font-weight:
            800 !important;

        font-size:
            14px !important;

        transition:
            all 0.22s ease !important;

        box-shadow:
            inset 0 1px 0
            rgba(
                255,
                255,
                255,
                0.025
            );
    }


    section[
        data-testid="stSidebar"
    ] .stButton > button:hover {

        transform:
            translateX(
                5px
            );

        border-color:
            rgba(
                37,
                229,
                255,
                0.62
            ) !important;

        background:

            linear-gradient(
                100deg,
                rgba(
                    13,
                    88,
                    120,
                    0.98
                ),
                rgba(
                    84,
                    34,
                    153,
                    0.98
                )
            ) !important;

        box-shadow:

            0 0 22px
            rgba(
                37,
                229,
                255,
                0.16
            ),

            0 0 40px
            rgba(
                139,
                70,
                255,
                0.12
            );
    }


    /* =====================================================
       BOTONES GENERALES
    ===================================================== */

    .stButton > button {

        min-height:
            46px;

        border:
            none !important;

        border-radius:
            12px !important;

        color:
            white !important;

        font-weight:
            850 !important;

        background:

            linear-gradient(
                110deg,
                #22dffc 0%,
                #258dff 48%,
                #9146ff 100%
            ) !important;

        box-shadow:

            0 10px 30px
            rgba(
                33,
                140,
                255,
                0.22
            ),

            inset 0 1px 0
            rgba(
                255,
                255,
                255,
                0.18
            );

        transition:
            all 0.22s ease !important;
    }


    .stButton > button:hover {

        transform:
            translateY(
                -2px
            );

        box-shadow:

            0 16px 38px
            rgba(
                33,
                140,
                255,
                0.29
            ),

            0 0 28px
            rgba(
                142,
                69,
                255,
                0.23
            );
    }


    .stButton > button:active {

        transform:
            translateY(
                0
            )
            scale(
                0.99
            );
    }


    /* =====================================================
       INPUTS
    ===================================================== */

    .stTextInput input,
    .stNumberInput input,
    .stTextArea textarea,
    .stDateInput input {

        color:
            #eaf3ff !important;

        background:

            linear-gradient(
                145deg,
                rgba(
                    13,
                    21,
                    44,
                    0.98
                ),
                rgba(
                    7,
                    11,
                    26,
                    0.98
                )
            ) !important;

        border:
            1px solid
            rgba(
                79,
                111,
                186,
                0.35
            ) !important;

        border-radius:
            11px !important;

        box-shadow:
            inset 0 1px 0
            rgba(
                255,
                255,
                255,
                0.03
            );
    }


    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stTextArea textarea:focus,
    .stDateInput input:focus {

        border-color:
            var(
                --ax-cyan
            ) !important;

        box-shadow:

            0 0 0 1px
            rgba(
                37,
                229,
                255,
                0.30
            ),

            0 0 24px
            rgba(
                37,
                229,
                255,
                0.11
            ) !important;
    }


    /* =====================================================
       SELECTBOX
    ===================================================== */

    div[
        data-baseweb="select"
    ] > div {

        color:
            #eaf3ff !important;

        background:

            linear-gradient(
                145deg,
                rgba(
                    13,
                    21,
                    44,
                    0.98
                ),
                rgba(
                    7,
                    11,
                    26,
                    0.98
                )
            ) !important;

        border:
            1px solid
            rgba(
                79,
                111,
                186,
                0.35
            ) !important;

        border-radius:
            11px !important;
    }


    div[
        data-baseweb="popover"
    ],
    div[
        role="listbox"
    ] {

        background:
            #090f21 !important;

        border:
            1px solid
            rgba(
                37,
                229,
                255,
                0.33
            ) !important;

        border-radius:
            12px !important;
    }


    div[
        role="option"
    ] {

        color:
            #edf2ff !important;

        background:
            #090f21 !important;
    }


    div[
        role="option"
    ]:hover {

        color:
            white !important;

        background:

            linear-gradient(
                90deg,
                rgba(
                    20,
                    104,
                    141,
                    0.94
                ),
                rgba(
                    91,
                    37,
                    153,
                    0.94
                )
            ) !important;
    }


    /* =====================================================
       TABS
    ===================================================== */

    button[
        data-baseweb="tab"
    ] {

        color:
            #9ca7c3 !important;

        font-weight:
            750 !important;
    }


    button[
        data-baseweb="tab"
    ][
        aria-selected="true"
    ] {

        color:
            var(
                --ax-cyan
            ) !important;
    }


    div[
        data-baseweb="tab-highlight"
    ] {

        background:

            linear-gradient(
                90deg,
                var(
                    --ax-cyan
                ),
                var(
                    --ax-violet
                )
            ) !important;
    }


    /* =====================================================
       MÉTRICAS
    ===================================================== */

    div[
        data-testid="stMetric"
    ] {

        padding:
            17px;

        border-radius:
            15px;

        background:

            linear-gradient(
                150deg,
                rgba(
                    11,
                    18,
                    39,
                    0.98
                ),
                rgba(
                    5,
                    9,
                    22,
                    0.98
                )
            );

        border:
            1px solid
            rgba(
                87,
                108,
                177,
                0.26
            );

        box-shadow:

            0 18px 45px
            rgba(
                0,
                0,
                0,
                0.24
            ),

            inset 0 1px 0
            rgba(
                255,
                255,
                255,
                0.025
            );
    }


    div[
        data-testid="stMetricLabel"
    ] {

        color:
            var(
                --ax-muted
            ) !important;

        font-weight:
            850;

        letter-spacing:
            0.05em;
    }


    div[
        data-testid="stMetricValue"
    ] {

        color:
            white !important;

        font-weight:
            950 !important;
    }


    /* =====================================================
       ALERTAS
    ===================================================== */

    div[
        data-testid="stAlert"
    ] {

        border-radius:
            13px !important;

        border:
            1px solid
            rgba(
                93,
                119,
                192,
                0.20
            ) !important;

        background:

            linear-gradient(
                120deg,
                rgba(
                    10,
                    25,
                    49,
                    0.96
                ),
                rgba(
                    12,
                    16,
                    42,
                    0.96
                )
            ) !important;
    }


    /* =====================================================
       FILE UPLOADER
    ===================================================== */

    section[
        data-testid="stFileUploaderDropzone"
    ] {

        border:
            1px dashed
            rgba(
                37,
                229,
                255,
                0.48
            ) !important;

        border-radius:
            14px !important;

        background:

            linear-gradient(
                145deg,
                rgba(
                    11,
                    21,
                    42,
                    0.94
                ),
                rgba(
                    9,
                    8,
                    27,
                    0.94
                )
            ) !important;
    }


    /* =====================================================
       DATAFRAME
    ===================================================== */

    div[
        data-testid="stDataFrame"
    ] {

        border-radius:
            14px;

        overflow:
            hidden;

        border:
            1px solid
            rgba(
                87,
                110,
                181,
                0.24
            );
    }


    /* =====================================================
       EXPANDERS
    ===================================================== */

    details {

        background:
            rgba(
                8,
                13,
                30,
                0.96
            ) !important;

        border:
            1px solid
            rgba(
                81,
                108,
                182,
                0.24
            ) !important;

        border-radius:
            14px !important;
    }


    details summary {

        font-weight:
            800 !important;
    }


    /* =====================================================
       CLASES AXION
    ===================================================== */

    .ax-brand {

        display:
            flex;

        align-items:
            center;

        gap:
            12px;

        padding:
            8px 5px 18px;

        border-bottom:
            1px solid
            rgba(
                255,
                255,
                255,
                0.06
            );
    }


    .ax-logo {

        width:
            48px;

        height:
            48px;

        border-radius:
            14px;

        display:
            grid;

        place-items:
            center;

        background:

            linear-gradient(
                145deg,
                var(
                    --ax-cyan
                ),
                var(
                    --ax-violet
                )
            );

        color:
            white;

        font-size:
            21px;

        font-weight:
            950;

        box-shadow:

            0 0 28px
            rgba(
                36,
                220,
                255,
                0.27
            ),

            0 0 42px
            rgba(
                139,
                70,
                255,
                0.18
            );
    }


    .ax-brand b {

        font-size:
            15px;

        font-weight:
            950;
    }


    .ax-brand small {

        display:
            block;

        color:
            #687594;

        letter-spacing:
            1.65px;

        font-size:
            7px;

        margin-top:
            4px;
    }


    .ax-profile {

        margin:
            15px 0;

        padding:
            16px;

        border:
            1px solid
            rgba(
                45,
                210,
                255,
                0.31
            );

        border-radius:
            19px;

        background:

            radial-gradient(
                circle at 15% 10%,
                rgba(
                    32,
                    177,
                    255,
                    0.08
                ),
                transparent 35%
            ),

            linear-gradient(
                145deg,
                rgba(
                    11,
                    18,
                    40,
                    0.98
                ),
                rgba(
                    8,
                    9,
                    25,
                    0.98
                )
            );

        box-shadow:
            0 18px 42px
            rgba(
                0,
                0,
                0,
                0.24
            );
    }


    .ax-section {

        font-size:
            8px;

        letter-spacing:
            1.85px;

        color:
            #606d8e;

        font-weight:
            900;

        margin:
            21px 5px 10px;
    }


    .ax-hero {

        padding:
            23px;

        border-radius:
            19px;

        background:

            linear-gradient(
                135deg,
                rgba(
                    7,
                    17,
                    37,
                    0.97
                ),
                rgba(
                    19,
                    8,
                    44,
                    0.96
                )
            );

        border:
            1px solid
            rgba(
                61,
                211,
                255,
                0.25
            );

        margin-bottom:
            17px;

        box-shadow:

            0 20px 60px
            rgba(
                0,
                0,
                0,
                0.27
            ),

            inset 0 1px 0
            rgba(
                255,
                255,
                255,
                0.025
            );

        position:
            relative;

        overflow:
            hidden;
    }


    .ax-hero::after {

        content:
            "";

        position:
            absolute;

        inset:
            0;

        background:

            linear-gradient(
                90deg,
                transparent,
                rgba(
                    37,
                    229,
                    255,
                    0.04
                ),
                transparent
            );

        transform:
            translateX(
                -100%
            );

        animation:
            axShine 7s infinite;
    }


    .ax-title {

        font-size:
            32px;

        font-weight:
            950;

        line-height:
            1.12;

        position:
            relative;

        z-index:
            2;
    }


    .ax-sub {

        color:
            #8794b6;

        font-size:
            12px;

        margin-top:
            8px;

        position:
            relative;

        z-index:
            2;
    }


    .ax-card {

        padding:
            18px;

        border-radius:
            16px;

        background:

            linear-gradient(
                150deg,
                rgba(
                    11,
                    18,
                    39,
                    0.98
                ),
                rgba(
                    5,
                    9,
                    22,
                    0.98
                )
            );

        border:
            1px solid
            rgba(
                86,
                106,
                176,
                0.25
            );

        box-shadow:

            0 18px 45px
            rgba(
                0,
                0,
                0,
                0.24
            ),

            inset 0 1px 0
            rgba(
                255,
                255,
                255,
                0.025
            );

        transition:
            all 0.22s ease;
    }


    .ax-card:hover {

        transform:
            translateY(
                -4px
            );

        border-color:
            rgba(
                37,
                229,
                255,
                0.44
            );

        box-shadow:

            0 25px 55px
            rgba(
                0,
                0,
                0,
                0.30
            ),

            0 0 30px
            rgba(
                37,
                229,
                255,
                0.08
            );
    }


    .ax-label {

        font-size:
            9px;

        letter-spacing:
            1.25px;

        color:
            #7c89aa;

        font-weight:
            900;
    }


    .ax-value {

        font-size:
            29px;

        font-weight:
            950;

        margin-top:
            12px;
    }


    .ax-positive {

        color:
            var(
                --ax-green
            ) !important;
    }


    .ax-negative {

        color:
            var(
                --ax-red
            ) !important;
    }


    .ax-trade-card {

        padding:
            17px;

        border-radius:
            16px;

        margin:
            11px 0;

        background:
            rgba(
                8,
                13,
                29,
                0.97
            );

        border:
            1px solid
            rgba(
                88,
                110,
                178,
                0.25
            );

        box-shadow:
            0 15px 36px
            rgba(
                0,
                0,
                0,
                0.24
            );
    }


    .ax-status {

        display:
            inline-flex;

        align-items:
            center;

        gap:
            8px;

        padding:
            8px 13px;

        border-radius:
            999px;

        background:
            rgba(
                0,
                255,
                136,
                0.08
            );

        border:
            1px solid
            rgba(
                0,
                255,
                136,
                0.33
            );

        color:
            #52ffae;

        font-size:
            10px;

        font-weight:
            900;
    }


    /* =====================================================
       VELAS ANIMADAS
    ===================================================== */

    .ax-candle-background {

        position:
            fixed;

        inset:
            0;

        z-index:
            0;

        pointer-events:
            none;

        opacity:
            0.47;

        overflow:
            hidden;
    }


    .ax-candle-background span {

        position:
            absolute;

        bottom:
            -120px;

        width:
            9px;

        border-radius:
            2px;

        animation-name:
            axCandleFloat;

        animation-timing-function:
            linear;

        animation-iteration-count:
            infinite;

        filter:

            drop-shadow(
                0 0 10px
                currentColor
            )

            drop-shadow(
                0 0 23px
                currentColor
            );
    }


    .ax-candle-background span::before {

        content:
            "";

        position:
            absolute;

        left:
            4px;

        top:
            -22px;

        width:
            1px;

        height:
            calc(
                100% + 44px
            );

        background:
            currentColor;
    }


    /* =====================================================
       ANIMACIONES
    ===================================================== */

    @keyframes axCandleFloat {

        0% {

            transform:
                translateY(
                    0
                );

            opacity:
                0;
        }


        12% {

            opacity:
                0.88;
        }


        75% {

            opacity:
                0.60;
        }


        100% {

            transform:
                translateY(
                    -118vh
                );

            opacity:
                0;
        }
    }


    @keyframes axShine {

        0% {

            transform:
                translateX(
                    -110%
                );
        }


        45% {

            transform:
                translateX(
                    110%
                );
        }


        100% {

            transform:
                translateX(
                    110%
                );
        }
    }


    /* =====================================================
       RESPONSIVE
    ===================================================== */

    @media (
        max-width:
            900px
    ) {

        section[
            data-testid="stSidebar"
        ] {

            min-width:
                280px !important;

            max-width:
                280px !important;
        }


        .ax-title {

            font-size:
                25px;
        }


        .block-container {

            padding-left:
                1rem !important;

            padding-right:
                1rem !important;
        }
    }

    </style>
    """

    st.markdown(
        css,
        unsafe_allow_html=True,
    )


    # =====================================================
    # CREAR VELAS ANIMADAS
    # =====================================================

    candle_items = []


    for index in range(
        44
    ):

        is_green = (
            index % 2 == 0
        )


        color = (

            "#00ff88"

            if is_green

            else "#ff1744"
        )


        left = (
            index
            * 2.29
            + 0.5
        ) % 100


        height = (

            28
            +
            (
                index
                * 19
            )
            % 75
        )


        delay = (
            -index
            * 0.71
        )


        duration = (

            15
            +
            (
                index
                % 9
            )
        )


        opacity = (

            0.38
            +
            (
                index
                % 5
            )
            * 0.08
        )


        candle_items.append(

            f"""
            <span
                style="
                    left:{left:.2f}%;
                    height:{height}px;
                    color:{color};
                    background:{color};
                    animation-delay:{delay:.2f}s;
                    animation-duration:{duration}s;
                    opacity:{opacity:.2f};
                "
            ></span>
            """
        )


    candle_html = (

        '<div class="ax-candle-background">'

        + "".join(
            candle_items
        )

        + "</div>"
    )


    st.markdown(
        candle_html,
        unsafe_allow_html=True,
    )
