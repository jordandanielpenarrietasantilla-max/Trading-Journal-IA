from __future__ import annotations

import streamlit as st


# =========================================================
# AXION PRIME X10 PRO
# CONFIGURACIÓN CENTRAL
# =========================================================


def _read_secret(
    key: str,
    default: str = "",
) -> str:
    """
    Lee una variable desde Streamlit Secrets
    sin mostrar su contenido.
    """

    try:
        value = st.secrets.get(
            key,
            default,
        )

    except Exception:
        value = default

    if value is None:
        return default

    return str(
        value
    ).strip()


# =========================================================
# SUPABASE
# =========================================================

SUPABASE_URL = _read_secret(
    "SUPABASE_URL"
)

SUPABASE_KEY = _read_secret(
    "SUPABASE_KEY"
)


# =========================================================
# OPENROUTER
# =========================================================

OPENROUTER_API_KEY = _read_secret(
    "OPENROUTER_API_KEY"
)

OPENROUTER_MODEL = _read_secret(
    "OPENROUTER_MODEL",
    "google/gemini-2.5-flash",
)


# =========================================================
# APLICACIÓN
# =========================================================

ADMIN_EMAIL = _read_secret(
    "ADMIN_EMAIL"
)

APP_URL = _read_secret(
    "APP_URL"
)


# =========================================================
# VALIDACIÓN
# =========================================================

def validate_config() -> None:
    """
    Comprueba que las variables esenciales existan.
    Nunca muestra las claves completas.
    """

    missing = []

    if not SUPABASE_URL:
        missing.append(
            "SUPABASE_URL"
        )

    if not SUPABASE_KEY:
        missing.append(
            "SUPABASE_KEY"
        )

    if missing:
        raise RuntimeError(
            "Faltan variables obligatorias en "
            "Streamlit Secrets: "
            + ", ".join(
                missing
            )
        )


def get_public_config() -> dict[str, str]:
    """
    Devuelve datos de configuración no sensibles
    para diagnóstico.
    """

    return {
        "supabase_configured":
            "Sí"
            if SUPABASE_URL and SUPABASE_KEY
            else "No",

        "openrouter_configured":
            "Sí"
            if OPENROUTER_API_KEY
            else "No",

        "openrouter_model":
            OPENROUTER_MODEL,

        "app_url":
            APP_URL,

        "admin_configured":
            "Sí"
            if ADMIN_EMAIL
            else "No",
    }
