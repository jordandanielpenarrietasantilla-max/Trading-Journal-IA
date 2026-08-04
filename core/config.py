from __future__ import annotations

from typing import Any

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


def _read_float_secret(
    key: str,
    default: float,
) -> float:
    """
    Lee un número desde Streamlit Secrets.
    """

    value = _read_secret(
        key,
        str(default),
    )

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return float(
            default
        )


def _configured(
    value: Any,
) -> str:
    """
    Devuelve un estado seguro para diagnóstico.
    """

    return (
        "Sí"
        if str(value or "").strip()
        else "No"
    )


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
).rstrip("/")


# =========================================================
# FLOW · VISA / MASTERCARD / WEBPAY
# =========================================================


FLOW_API_KEY = _read_secret(
    "FLOW_API_KEY"
)

FLOW_SECRET_KEY = _read_secret(
    "FLOW_SECRET_KEY"
)

FLOW_MODE = _read_secret(
    "FLOW_MODE",
    "production",
).lower()

FLOW_API_URL = _read_secret(
    "FLOW_API_URL",
    (
        "https://sandbox.flow.cl/api"
        if FLOW_MODE == "sandbox"
        else "https://www.flow.cl/api"
    ),
).rstrip("/")

FLOW_CURRENCY = _read_secret(
    "FLOW_CURRENCY",
    "CLP",
).upper()

FLOW_MONTHLY_AMOUNT = _read_float_secret(
    "FLOW_MONTHLY_AMOUNT",
    3000.0,
)

FLOW_ANNUAL_AMOUNT = _read_float_secret(
    "FLOW_ANNUAL_AMOUNT",
    20000.0,
)

FLOW_RETURN_URL = _read_secret(
    "FLOW_RETURN_URL",
    APP_URL,
).rstrip("/")

FLOW_CONFIRMATION_URL = _read_secret(
    "FLOW_CONFIRMATION_URL",
    (
        f"{SUPABASE_URL.rstrip('/')}"
        "/functions/v1/flow-webhook"
        if SUPABASE_URL
        else ""
    ),
).rstrip("/")


# =========================================================
# MERCADO PAGO · DESACTIVADO TEMPORALMENTE
# =========================================================


MERCADOPAGO_PUBLIC_KEY = _read_secret(
    "MERCADOPAGO_PUBLIC_KEY"
)

MERCADOPAGO_ACCESS_TOKEN = _read_secret(
    "MERCADOPAGO_ACCESS_TOKEN"
)

MERCADOPAGO_MODE = _read_secret(
    "MERCADOPAGO_MODE",
    "disabled",
).lower()

MERCADOPAGO_CURRENCY = _read_secret(
    "MERCADOPAGO_CURRENCY",
    "CLP",
).upper()

MERCADOPAGO_MONTHLY_AMOUNT = _read_float_secret(
    "MERCADOPAGO_MONTHLY_AMOUNT",
    3000.0,
)

MERCADOPAGO_ANNUAL_AMOUNT = _read_float_secret(
    "MERCADOPAGO_ANNUAL_AMOUNT",
    20000.0,
)

MERCADOPAGO_WEBHOOK_URL = _read_secret(
    "MERCADOPAGO_WEBHOOK_URL"
)


# =========================================================
# BINANCE PAY
# =========================================================


BINANCE_PAY_ID = _read_secret(
    "BINANCE_PAY_ID"
)

BINANCE_PAY_EMAIL = _read_secret(
    "BINANCE_PAY_EMAIL"
)

BINANCE_PAY_PHONE = _read_secret(
    "BINANCE_PAY_PHONE"
)

BINANCE_PAY_MERCHANT_ID = _read_secret(
    "BINANCE_PAY_MERCHANT_ID"
)

BINANCE_PAY_LINK = _read_secret(
    "BINANCE_PAY_LINK"
)


# =========================================================
# BILLETERAS CRIPTO
# =========================================================


BTC_BEP20_WALLET_ADDRESS = _read_secret(
    "BTC_BEP20_WALLET_ADDRESS"
)

ETH_BEP20_WALLET_ADDRESS = _read_secret(
    "ETH_BEP20_WALLET_ADDRESS"
)

USDT_TRC20_WALLET_ADDRESS = _read_secret(
    "USDT_TRC20_WALLET_ADDRESS"
)


# =========================================================
# VALIDACIONES INTERNAS
# =========================================================


def _validate_url(
    name: str,
    value: str,
    *,
    required: bool = False,
) -> list[str]:
    """
    Valida una URL sin exponer su contenido.
    """

    errors: list[str] = []

    clean_value = str(
        value or ""
    ).strip()

    if required and not clean_value:
        errors.append(
            name
        )

        return errors

    if (
        clean_value
        and not clean_value.startswith(
            (
                "https://",
                "http://localhost",
                "http://127.0.0.1",
            )
        )
    ):
        errors.append(
            f"{name} no tiene una URL válida"
        )

    return errors


def _validate_flow() -> list[str]:
    """
    Valida Flow únicamente cuando existe
    al menos una credencial configurada.
    """

    errors: list[str] = []

    has_any_credential = bool(
        FLOW_API_KEY
        or FLOW_SECRET_KEY
    )

    if not has_any_credential:
        return errors

    if not FLOW_API_KEY:
        errors.append(
            "FLOW_API_KEY"
        )

    if not FLOW_SECRET_KEY:
        errors.append(
            "FLOW_SECRET_KEY"
        )

    if FLOW_MODE not in {
        "sandbox",
        "production",
    }:
        errors.append(
            "FLOW_MODE debe ser "
            "'sandbox' o 'production'"
        )

    if len(
        FLOW_CURRENCY
    ) != 3:
        errors.append(
            "FLOW_CURRENCY debe usar "
            "tres letras, por ejemplo CLP"
        )

    if FLOW_MONTHLY_AMOUNT <= 0:
        errors.append(
            "FLOW_MONTHLY_AMOUNT debe "
            "ser mayor que cero"
        )

    if FLOW_ANNUAL_AMOUNT <= 0:
        errors.append(
            "FLOW_ANNUAL_AMOUNT debe "
            "ser mayor que cero"
        )

    errors.extend(
        _validate_url(
            "FLOW_API_URL",
            FLOW_API_URL,
            required=True,
        )
    )

    errors.extend(
        _validate_url(
            "FLOW_RETURN_URL",
            FLOW_RETURN_URL,
            required=True,
        )
    )

    errors.extend(
        _validate_url(
            "FLOW_CONFIRMATION_URL",
            FLOW_CONFIRMATION_URL,
            required=True,
        )
    )

    return errors


def _validate_mercadopago() -> list[str]:
    """
    Valida Mercado Pago solamente cuando está activo.
    """

    errors: list[str] = []

    if MERCADOPAGO_MODE == "disabled":
        return errors

    has_any_credential = bool(
        MERCADOPAGO_PUBLIC_KEY
        or MERCADOPAGO_ACCESS_TOKEN
    )

    if not has_any_credential:
        return errors

    if not MERCADOPAGO_PUBLIC_KEY:
        errors.append(
            "MERCADOPAGO_PUBLIC_KEY"
        )

    if not MERCADOPAGO_ACCESS_TOKEN:
        errors.append(
            "MERCADOPAGO_ACCESS_TOKEN"
        )

    if MERCADOPAGO_MODE not in {
        "test",
        "production",
    }:
        errors.append(
            "MERCADOPAGO_MODE debe ser "
            "'disabled', 'test' o 'production'"
        )

    if len(
        MERCADOPAGO_CURRENCY
    ) != 3:
        errors.append(
            "MERCADOPAGO_CURRENCY debe usar "
            "tres letras, por ejemplo CLP"
        )

    if MERCADOPAGO_MONTHLY_AMOUNT <= 0:
        errors.append(
            "MERCADOPAGO_MONTHLY_AMOUNT debe "
            "ser mayor que cero"
        )

    if MERCADOPAGO_ANNUAL_AMOUNT <= 0:
        errors.append(
            "MERCADOPAGO_ANNUAL_AMOUNT debe "
            "ser mayor que cero"
        )

    return errors


# =========================================================
# VALIDACIÓN PRINCIPAL
# =========================================================


def validate_config() -> None:
    """
    Comprueba las variables esenciales.

    Supabase es obligatorio para iniciar la aplicación.

    Flow, Mercado Pago, OpenRouter, Binance y las billeteras
    se validan solamente cuando están configurados.
    """

    errors: list[str] = []

    if not SUPABASE_URL:
        errors.append(
            "SUPABASE_URL"
        )

    if not SUPABASE_KEY:
        errors.append(
            "SUPABASE_KEY"
        )

    errors.extend(
        _validate_url(
            "SUPABASE_URL",
            SUPABASE_URL,
            required=bool(
                SUPABASE_URL
            ),
        )
    )

    errors.extend(
        _validate_url(
            "APP_URL",
            APP_URL,
            required=False,
        )
    )

    errors.extend(
        _validate_flow()
    )

    errors.extend(
        _validate_url(
            "MERCADOPAGO_WEBHOOK_URL",
            MERCADOPAGO_WEBHOOK_URL,
            required=False,
        )
    )

    errors.extend(
        _validate_mercadopago()
    )

    if errors:
        raise RuntimeError(
            "Hay variables incorrectas o faltantes "
            "en Streamlit Secrets: "
            + ", ".join(
                errors
            )
        )


# =========================================================
# CONFIGURACIÓN PÚBLICA
# =========================================================


def get_public_config() -> dict[str, Any]:
    """
    Devuelve únicamente información segura.

    Nunca devuelve claves, tokens ni direcciones completas.
    """

    flow_configured = bool(
        FLOW_API_KEY
        and FLOW_SECRET_KEY
    )

    binance_configured = bool(
        BINANCE_PAY_ID
        or BINANCE_PAY_EMAIL
        or BINANCE_PAY_PHONE
        or BINANCE_PAY_MERCHANT_ID
        or BINANCE_PAY_LINK
    )

    crypto_configured = bool(
        BTC_BEP20_WALLET_ADDRESS
        and ETH_BEP20_WALLET_ADDRESS
        and USDT_TRC20_WALLET_ADDRESS
    )

    mercadopago_configured = bool(
        MERCADOPAGO_MODE != "disabled"
        and MERCADOPAGO_PUBLIC_KEY
        and MERCADOPAGO_ACCESS_TOKEN
    )

    return {
        "supabase_configured":
            _configured(
                SUPABASE_URL
                and SUPABASE_KEY
            ),

        "openrouter_configured":
            _configured(
                OPENROUTER_API_KEY
            ),

        "openrouter_model":
            OPENROUTER_MODEL,

        "app_url_configured":
            _configured(
                APP_URL
            ),

        "admin_configured":
            _configured(
                ADMIN_EMAIL
            ),

        "flow_configured":
            _configured(
                flow_configured
            ),

        "flow_mode":
            FLOW_MODE,

        "flow_currency":
            FLOW_CURRENCY,

        "flow_monthly_amount":
            FLOW_MONTHLY_AMOUNT,

        "flow_annual_amount":
            FLOW_ANNUAL_AMOUNT,

        "flow_return_url_configured":
            _configured(
                FLOW_RETURN_URL
            ),

        "flow_confirmation_url_configured":
            _configured(
                FLOW_CONFIRMATION_URL
            ),

        "mercadopago_configured":
            _configured(
                mercadopago_configured
            ),

        "mercadopago_mode":
            MERCADOPAGO_MODE,

        "mercadopago_currency":
            MERCADOPAGO_CURRENCY,

        "mercadopago_monthly_amount":
            MERCADOPAGO_MONTHLY_AMOUNT,

        "mercadopago_annual_amount":
            MERCADOPAGO_ANNUAL_AMOUNT,

        "mercadopago_webhook_configured":
            _configured(
                MERCADOPAGO_WEBHOOK_URL
            ),

        "binance_pay_configured":
            _configured(
                binance_configured
            ),

        "crypto_wallets_configured":
            _configured(
                crypto_configured
            ),

        "btc_bep20_configured":
            _configured(
                BTC_BEP20_WALLET_ADDRESS
            ),

        "eth_bep20_configured":
            _configured(
                ETH_BEP20_WALLET_ADDRESS
            ),

        "usdt_trc20_configured":
            _configured(
                USDT_TRC20_WALLET_ADDRESS
            ),
    }
