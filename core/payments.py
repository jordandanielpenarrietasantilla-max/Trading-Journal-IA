from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlencode

import requests
import streamlit as st

from core.config import APP_URL, SUPABASE_URL


# =========================================================
# AXION PRIME
# MERCADO PAGO · CHECKOUT PRO
# =========================================================


MERCADOPAGO_API_URL = "https://api.mercadopago.com"
REQUEST_TIMEOUT = 45


class PaymentError(RuntimeError):
    """
    Error controlado del sistema de pagos.
    """


@dataclass(frozen=True)
class CheckoutPreference:
    """
    Resultado normalizado de una preferencia de Mercado Pago.
    """

    preference_id: str
    checkout_url: str
    external_reference: str
    mode: str
    raw_response: dict[str, Any]


# =========================================================
# SECRETS Y CONFIGURACIÓN
# =========================================================


def _secret(
    name: str,
    default: str = "",
) -> str:
    """
    Lee una variable desde Streamlit Secrets.
    """

    try:
        value = st.secrets.get(
            name,
            default,
        )

    except Exception:
        value = default

    if value is None:
        return default

    return str(
        value
    ).strip()


def _access_token() -> str:
    """
    Devuelve el Access Token privado de Mercado Pago.
    """

    token = _secret(
        "MERCADOPAGO_ACCESS_TOKEN",
    )

    if not token:
        raise PaymentError(
            "Falta MERCADOPAGO_ACCESS_TOKEN en Streamlit Secrets."
        )

    return token


def get_mercadopago_mode() -> str:
    """
    Devuelve 'test' o 'production'.
    """

    mode = _secret(
        "MERCADOPAGO_MODE",
        "test",
    ).lower()

    if mode not in {
        "test",
        "production",
    }:
        raise PaymentError(
            "MERCADOPAGO_MODE debe ser 'test' o 'production'."
        )

    return mode


def get_mercadopago_currency() -> str:
    """
    Moneda utilizada por Checkout Pro.

    Para una cuenta chilena normalmente se utilizará CLP.
    Se puede cambiar desde Secrets con:

    MERCADOPAGO_CURRENCY = "CLP"
    """

    currency = _secret(
        "MERCADOPAGO_CURRENCY",
        "CLP",
    ).upper()

    if not re.fullmatch(
        r"[A-Z]{3}",
        currency,
    ):
        raise PaymentError(
            "MERCADOPAGO_CURRENCY debe tener tres letras, "
            "por ejemplo CLP."
        )

    return currency


def _app_url() -> str:
    """
    Devuelve la URL pública de la aplicación sin barra final.
    """

    url = str(
        APP_URL
        or _secret(
            "APP_URL",
        )
        or ""
    ).strip().rstrip("/")

    if not url:
        raise PaymentError(
            "Falta APP_URL en Streamlit Secrets."
        )

    if not url.startswith(
        (
            "https://",
            "http://localhost",
            "http://127.0.0.1",
        )
    ):
        raise PaymentError(
            "APP_URL debe ser una URL pública válida."
        )

    return url


def get_webhook_url() -> str:
    """
    Devuelve la URL del webhook.

    Primero respeta MERCADOPAGO_WEBHOOK_URL.
    Si no existe, prepara la URL estándar de una
    Supabase Edge Function llamada mercadopago-webhook.
    """

    configured_url = _secret(
        "MERCADOPAGO_WEBHOOK_URL",
    ).rstrip("/")

    if configured_url:
        return configured_url

    supabase_url = str(
        SUPABASE_URL
        or _secret(
            "SUPABASE_URL",
        )
        or ""
    ).strip().rstrip("/")

    if not supabase_url:
        return ""

    return (
        f"{supabase_url}"
        "/functions/v1/mercadopago-webhook"
    )


# =========================================================
# USUARIO AUTENTICADO
# =========================================================


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    """
    Convierte objetos compatibles en diccionario.
    """

    if isinstance(
        value,
        dict,
    ):
        return value

    try:
        dumped = value.model_dump()

        if isinstance(
            dumped,
            dict,
        ):
            return dumped

    except Exception:
        pass

    return {}


def get_current_user() -> dict[str, Any]:
    """
    Devuelve el usuario autenticado de Streamlit.
    """

    user = _safe_dict(
        st.session_state.get(
            "user",
            {},
        )
    )

    if not user:
        raise PaymentError(
            "No se encontró un usuario autenticado."
        )

    return user


def get_current_user_id() -> str:
    """
    Devuelve el UUID del usuario autenticado.
    """

    user = get_current_user()

    metadata = _safe_dict(
        user.get(
            "user_metadata",
            {},
        )
    )

    possible_values = [
        user.get("id"),
        user.get("sub"),
        metadata.get("sub"),
    ]

    for value in possible_values:
        user_id = str(
            value
            or ""
        ).strip()

        if user_id:
            return user_id

    raise PaymentError(
        "No se encontró el ID del usuario autenticado."
    )


def get_current_user_email() -> str:
    """
    Devuelve el correo del usuario autenticado.
    """

    user = get_current_user()

    email = str(
        user.get(
            "email",
            "",
        )
        or ""
    ).strip()

    if not email:
        raise PaymentError(
            "El usuario autenticado no tiene un correo válido."
        )

    return email


# =========================================================
# UTILIDADES
# =========================================================


def _safe_json(
    response: requests.Response,
) -> Any:
    """
    Convierte la respuesta HTTP en JSON cuando es posible.
    """

    try:
        return response.json()

    except ValueError:
        return None


def _error_message(
    response: requests.Response,
) -> str:
    """
    Extrae un mensaje útil de una respuesta de Mercado Pago.
    """

    payload = _safe_json(
        response
    )

    if isinstance(
        payload,
        dict,
    ):
        message = str(
            payload.get(
                "message",
                "",
            )
            or ""
        ).strip()

        cause = payload.get(
            "cause",
        )

        if isinstance(
            cause,
            list,
        ) and cause:
            cause_messages = []

            for item in cause:
                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                description = str(
                    item.get(
                        "description",
                        "",
                    )
                    or item.get(
                        "code",
                        "",
                    )
                    or ""
                ).strip()

                if description:
                    cause_messages.append(
                        description
                    )

            if cause_messages:
                return (
                    f"{message}: "
                    + " | ".join(
                        cause_messages
                    )
                ).strip(": ")

        if message:
            return message

    text = str(
        response.text
        or ""
    ).strip()

    if text:
        return text[:1500]

    return (
        f"Mercado Pago respondió con HTTP "
        f"{response.status_code}."
    )


def _request(
    method: str,
    endpoint: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
    idempotency_key: str | None = None,
) -> requests.Response:
    """
    Ejecuta una petición autenticada contra Mercado Pago.
    """

    headers = {
        "Authorization": (
            f"Bearer {_access_token()}"
        ),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if idempotency_key:
        headers["X-Idempotency-Key"] = (
            idempotency_key
        )

    url = (
        endpoint
        if endpoint.startswith(
            "http"
        )
        else (
            f"{MERCADOPAGO_API_URL}"
            f"{endpoint}"
        )
    )

    try:
        return requests.request(
            method=method,
            url=url,
            headers=headers,
            json=json,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.Timeout as exc:
        raise PaymentError(
            "Mercado Pago tardó demasiado en responder."
        ) from exc

    except requests.ConnectionError as exc:
        raise PaymentError(
            "No se pudo conectar con Mercado Pago."
        ) from exc

    except requests.RequestException as exc:
        raise PaymentError(
            f"Error de comunicación con Mercado Pago: {exc}"
        ) from exc


def _validate_response(
    response: requests.Response,
    action: str,
) -> dict[str, Any]:
    """
    Valida la respuesta y devuelve un diccionario.
    """

    if response.status_code >= 400:
        raise PaymentError(
            f"{action}. HTTP {response.status_code}: "
            f"{_error_message(response)}"
        )

    payload = _safe_json(
        response
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise PaymentError(
            f"{action}. Mercado Pago devolvió "
            "una respuesta inválida."
        )

    return payload


def _decimal_amount(
    value: Any,
) -> float:
    """
    Convierte y valida el importe.
    """

    try:
        amount = Decimal(
            str(value)
        )

    except (
        InvalidOperation,
        TypeError,
        ValueError,
    ) as exc:
        raise PaymentError(
            "El importe del plan no es válido."
        ) from exc

    if amount <= 0:
        raise PaymentError(
            "El importe del plan debe ser mayor que cero."
        )

    return float(
        amount
    )


def _clean_text(
    value: Any,
    maximum: int,
) -> str:
    """
    Limpia textos enviados a servicios externos.
    """

    clean_value = str(
        value
        or ""
    ).strip()

    return clean_value[:maximum]


def _return_url(
    result: str,
) -> str:
    """
    Construye la URL de regreso hacia Streamlit.
    """

    query = urlencode(
        {
            "payment_result": result,
            "provider": "mercadopago",
        }
    )

    return (
        f"{_app_url()}"
        f"?{query}"
    )


def _external_reference(
    *,
    user_id: str,
    plan_code: str,
) -> str:
    """
    Crea una referencia única y rastreable.
    """

    safe_plan = re.sub(
        r"[^A-Za-z0-9_-]",
        "",
        plan_code,
    )[:40]

    short_uuid = uuid.uuid4().hex

    return (
        f"axion_{safe_plan}_"
        f"{user_id}_{short_uuid}"
    )


# =========================================================
# CREAR CHECKOUT PRO
# =========================================================


def create_checkout_preference(
    *,
    plan_code: str,
    plan_label: str,
    amount: Any,
    currency_id: str | None = None,
    description: str = "",
) -> CheckoutPreference:
    """
    Crea una preferencia de Mercado Pago Checkout Pro.

    Ejemplo:

        preference = create_checkout_preference(
            plan_code="PRO_MONTHLY",
            plan_label="AXION PRIME PRO MENSUAL",
            amount=3000,
            currency_id="CLP",
        )

        st.link_button(
            "Pagar con Mercado Pago",
            preference.checkout_url,
        )

    Mercado Pago muestra dentro de Checkout Pro los medios
    disponibles para la cuenta, como saldo, débito y tarjetas.
    """

    clean_plan_code = _clean_text(
        plan_code,
        50,
    ).upper()

    clean_plan_label = _clean_text(
        plan_label,
        120,
    )

    if not clean_plan_code:
        raise PaymentError(
            "Falta el código del plan."
        )

    if not clean_plan_label:
        raise PaymentError(
            "Falta el nombre del plan."
        )

    clean_amount = _decimal_amount(
        amount
    )

    clean_currency = str(
        currency_id
        or get_mercadopago_currency()
    ).strip().upper()

    if not re.fullmatch(
        r"[A-Z]{3}",
        clean_currency,
    ):
        raise PaymentError(
            "La moneda de Mercado Pago no es válida."
        )

    user_id = get_current_user_id()

    external_reference = (
        _external_reference(
            user_id=user_id,
            plan_code=clean_plan_code,
        )
    )

    item_description = _clean_text(
        description
        or (
            f"Suscripción {clean_plan_label} "
            "de AXION PRIME"
        ),
        250,
    )

    payload: dict[str, Any] = {
        "items": [
            {
                "id": clean_plan_code,
                "title": clean_plan_label,
                "description": item_description,
                "category_id": "services",
                "quantity": 1,
                "currency_id": clean_currency,
                "unit_price": clean_amount,
            }
        ],
        "external_reference": (
            external_reference
        ),
        "statement_descriptor": "AXION PRIME",
        "back_urls": {
            "success": _return_url(
                "success"
            ),
            "pending": _return_url(
                "pending"
            ),
            "failure": _return_url(
                "failure"
            ),
        },
        "auto_return": "approved",
        "metadata": {
            "user_id": user_id,
            "plan_code": clean_plan_code,
            "plan_label": clean_plan_label,
            "source": "axion_prime_streamlit",
            "mercadopago_mode": get_mercadopago_mode(),
        },
    }

    webhook_url = get_webhook_url()

    if webhook_url:
        payload["notification_url"] = (
            webhook_url
        )

    request_id = str(
        uuid.uuid4()
    )

    response = _request(
        "POST",
        "/checkout/preferences",
        json=payload,
        idempotency_key=request_id,
    )

    data = _validate_response(
        response,
        "No se pudo crear el Checkout Pro",
    )

    preference_id = str(
        data.get(
            "id",
            "",
        )
        or ""
    ).strip()

    mode = get_mercadopago_mode()

    checkout_url = str(
        data.get(
            "init_point",
            "",
        )
        or data.get(
            "sandbox_init_point",
            "",
        )
        or ""
    ).strip()

    if not preference_id:
        raise PaymentError(
            "Mercado Pago no devolvió el ID "
            "de la preferencia."
        )

    if not checkout_url:
        raise PaymentError(
            "Mercado Pago no devolvió la URL "
            "del checkout."
        )

    return CheckoutPreference(
        preference_id=preference_id,
        checkout_url=checkout_url,
        external_reference=external_reference,
        mode=mode,
        raw_response=data,
    )


# =========================================================
# CONSULTAR MERCADO PAGO
# =========================================================


def get_preference(
    preference_id: str,
) -> dict[str, Any]:
    """
    Consulta una preferencia por su ID.
    """

    clean_id = _clean_text(
        preference_id,
        160,
    )

    if not clean_id:
        raise PaymentError(
            "Falta el ID de la preferencia."
        )

    response = _request(
        "GET",
        f"/checkout/preferences/{clean_id}",
    )

    return _validate_response(
        response,
        "No se pudo consultar la preferencia",
    )


def get_payment(
    payment_id: str | int,
) -> dict[str, Any]:
    """
    Consulta un pago directamente en Mercado Pago.

    Esta función será utilizada por el webhook.
    """

    clean_id = _clean_text(
        payment_id,
        100,
    )

    if not clean_id:
        raise PaymentError(
            "Falta el ID del pago."
        )

    response = _request(
        "GET",
        f"/v1/payments/{clean_id}",
    )

    return _validate_response(
        response,
        "No se pudo consultar el pago",
    )


def payment_is_approved(
    payment: dict[str, Any],
) -> bool:
    """
    Comprueba si Mercado Pago confirmó el pago.
    """

    status = str(
        payment.get(
            "status",
            "",
        )
        or ""
    ).strip().lower()

    return status == "approved"


# =========================================================
# PRECIOS CONFIGURABLES
# =========================================================


def get_plan_checkout_data(
    plan_code: str,
) -> dict[str, Any]:
    """
    Devuelve el precio local configurado para cada plan.

    Recomendación para Chile:

        MERCADOPAGO_CURRENCY = "CLP"
        MERCADOPAGO_MONTHLY_AMOUNT = "3000"
        MERCADOPAGO_ANNUAL_AMOUNT = "20000"

    Puedes cambiar esos importes desde Secrets sin editar código.
    """

    clean_plan = str(
        plan_code
        or ""
    ).strip().upper()

    currency = get_mercadopago_currency()

    plans = {
        "PRO_MONTHLY": {
            "plan_code": "PRO_MONTHLY",
            "plan_label": (
                "AXION PRIME PRO MENSUAL"
            ),
            "amount": _secret(
                "MERCADOPAGO_MONTHLY_AMOUNT",
                "3000",
            ),
            "currency_id": currency,
        },
        "PRO_ANNUAL": {
            "plan_code": "PRO_ANNUAL",
            "plan_label": (
                "AXION PRIME PRO ANUAL"
            ),
            "amount": _secret(
                "MERCADOPAGO_ANNUAL_AMOUNT",
                "20000",
            ),
            "currency_id": currency,
        },
    }

    if clean_plan not in plans:
        raise PaymentError(
            f"El plan '{clean_plan}' no está configurado."
        )

    selected = plans[
        clean_plan
    ].copy()

    selected["amount"] = _decimal_amount(
        selected["amount"]
    )

    return selected


def create_plan_checkout(
    plan_code: str,
) -> CheckoutPreference:
    """
    Atajo para crear el checkout de un plan configurado.

    Ejemplo:

        preference = create_plan_checkout(
            "PRO_MONTHLY"
        )
    """

    plan = get_plan_checkout_data(
        plan_code
    )

    return create_checkout_preference(
        plan_code=plan[
            "plan_code"
        ],
        plan_label=plan[
            "plan_label"
        ],
        amount=plan[
            "amount"
        ],
        currency_id=plan[
            "currency_id"
        ],
    )
