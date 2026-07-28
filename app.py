/* Fondo General y Color de Texto Principal */
    .stApp {
        background-color: #0d1117 !important;
        color: #ffffff !important;
    }
    
    /* TODAS LAS ETIQUETAS Y TEXTOS EN BLANCO LUMINOSO */
    label, p, span, h1, h2, h3, h4, h5, h6, .stMarkdown {
        color: #f0f6fc !important;
        font-weight: 500 !important;
    }

    /* SUBTÍTULOS Y CABECERAS EN CIAN NEÓN */
    h2, h3 {
        color: #00f2fe !important;
        font-weight: 700 !important;
    }

    /* CAMPO DE ENTRADA Y DESPLEGABLES (Alto Contraste) */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
    }

    /* CAJAS DE TEXTO GRANDE (Notas) */
    textarea {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border: 1px solid #30363d !important;
    }
    
    /* BOTÓN PARA ABRIR/CERRAR MENÚ (GIGANTE Y RESPLANDECIENTE) */
    button[data-testid="stSidebarCollapseButton"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"],
    header button {
        background: #00f2fe !important;
        color: #000000 !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        box-shadow: 0px 0px 15px rgba(0, 242, 254, 1) !important;
        font-size: 18px !important;
    }

    /* PESTAÑAS (TABS) MÁS CLARAS Y VISIBLES */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #161b22 !important;
        border-radius: 10px;
        padding: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #c9d1d9 !important;
        font-size: 15px !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #00f2fe !important;
        border-bottom: 3px solid #00f2fe !important;
    }

    /* BOTÓN PRINCIPAL DE GUARDAR */
    .stButton > button {
        background: linear-gradient(90deg, #00f2fe 0%, #4facfe 100%) !important;
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 12px rgba(0, 242, 254, 0.5) !important;
    }
