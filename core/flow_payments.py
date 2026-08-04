from __future__ import annotations

import hashlib
import hmac
import re
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any
from urllib.parse import urlencode

import requests
import streamlit as st

from core.config import APP_URL, SUPABASE_URL

REQUEST_TIMEOUT = 45


class FlowPaymentError(RuntimeError):
    """Error controlado para operaciones con Flow."""


@dataclass(frozen=True)
class FlowCheckout:
    token: str
    flow_order: str
    commerce_order: str
    checkout_url: str
    plan_code: str
    amount: float
    currency: str
    raw_response: dict[str, Any]


def _secret(name: str, default: str = "") -> str:
    try:
        value = st.secrets.get(name, default)
    except Exception:
        value = default
    if value is None:
        return default
    return str(value).strip()


def _required_secret(name: str) -> str:
    value = _secret(name)
    if not value:
        raise FlowPaymentError(f"Falta {name} en Streamlit Secrets.")
    return value


def get_flow_mode() -> str:
    mode = _secret("FLOW_MODE", "production").lower()
    aliases = {
        "prod": "production",
        "production": "production",
        "live": "production",
        "test": "sandbox",
        "testing": "sandbox",
        "sandbox": "sandbox",
    }
    normalized = aliases.get(mode)
    if not normalized:
        raise FlowPaymentError("FLOW_MODE debe ser 'production' o 'sandbox'.")
    return normalized


def get_flow_api_url() -> str:
    configured = _secret("FLOW_API_URL").rstrip("/")
    if configured:
        return configured
    if get_flow_mode() == "sandbox":
        return "https://sandbox.flow.cl/api"
    return "https://www.flow.cl/api"


def get_flow_currency() -> str:
    currency = _secret("FLOW_CURRENCY", "CLP").upper()
    if not re.fullmatch(r"[A-Z]{3}", currency):
        raise FlowPaymentError(
            "FLOW_CURRENCY debe tener tres letras, por ejemplo CLP."
        )
    return currency


def _app_url() -> str:
    value = str(APP_URL or _secret("APP_URL") or "").strip().rstrip("/")
    if not value:
        raise FlowPaymentError("Falta APP_URL en Streamlit Secrets.")
    if not value.startswith(("https://", "http://localhost", "http://127.0.0.1")):
        raise FlowPaymentError("APP_URL debe ser una URL válida.")
    return value


def get_flow_return_url() -> str:
    configured = _secret("FLOW_RETURN_URL").rstrip("/")
    return configured or _app_url()


def get_flow_confirmation_url() -> str:
    configured = _secret("FLOW_CONFIRMATION_URL").rstrip("/")
    if configured:
        return configured
    supabase_url = str(SUPABASE_URL or _secret("SUPABASE_URL") or "").strip().rstrip("/")
    if not supabase_url:
        raise FlowPaymentError("Falta FLOW_CONFIRMATION_URL o SUPABASE_URL.")
    return f"{supabase_url}/functions/v1/flow-webhook"


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        dumped = value.model_dump()
        if isinstance(dumped, dict):
            return dumped
    except Exception:
        pass
    return {}


def get_current_user() -> dict[str, Any]:
    user = _safe_dict(st.session_state.get("user", {}))
    if not user:
        raise FlowPaymentError("No se encontró un usuario autenticado.")
    return user


def get_current_user_id() -> str:
    user = get_current_user()
    metadata = _safe_dict(user.get("user_metadata", {}))
    for value in (user.get("id"), user.get("sub"), metadata.get("sub")):
        clean_value = str(value or "").strip()
        if clean_value:
            return clean_value
    raise FlowPaymentError("No se encontró el ID del usuario autenticado.")


def get_current_user_email() -> str:
    user = get_current_user()
    email = str(user.get("email", "") or "").strip().lower()
    if not email:
        raise FlowPaymentError("El usuario autenticado no tiene correo.")
    return email


def _clean_parameter_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).strip()


def sign_flow_parameters(
    parameters: dict[str, Any],
    *,
    secret_key: str | None = None,
) -> str:
    key = secret_key or _required_secret("FLOW_SECRET_KEY")
    unsigned_parameters = {
        name: value
        for name, value in parameters.items()
        if name != "s" and value is not None
    }
    to_sign = "".join(
        str(name) + _clean_parameter_value(unsigned_parameters[name])
        for name in sorted(unsigned_parameters.keys())
    )
    return hmac.new(
        key.encode("utf-8"),
        to_sign.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _signed_parameters(parameters: dict[str, Any]) -> dict[str, str]:
    clean_parameters = {
        str(name): _clean_parameter_value(value)
        for name, value in parameters.items()
        if value is not None
    }
    clean_parameters["s"] = sign_flow_parameters(clean_parameters)
    return clean_parameters


def _safe_json(response: requests.Response) -> Any:
    try:
        return response.json()
    except ValueError:
        return None


def _flow_error_message(response: requests.Response) -> str:
    payload = _safe_json(response)
    if isinstance(payload, dict):
        for key in ("message", "error", "description", "detail", "code"):
            value = payload.get(key)
            if value not in (None, ""):
                return str(value)
    text = str(response.text or "").strip()
    if text:
        return text[:1500]
    return f"Flow respondió con HTTP {response.status_code}."


def _validate_response(response: requests.Response, action: str) -> dict[str, Any]:
    if response.status_code >= 400:
        raise FlowPaymentError(
            f"{action}. HTTP {response.status_code}: {_flow_error_message(response)}"
        )
    payload = _safe_json(response)
    if not isinstance(payload, dict):
        raise FlowPaymentError(f"{action}. Flow devolvió una respuesta inválida.")
    if payload.get("error"):
        raise FlowPaymentError(f"{action}: {payload.get('error')}")
    return payload


def _post_form(endpoint: str, parameters: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_flow_api_url()}{endpoint}"
    signed = _signed_parameters(parameters)
    try:
        response = requests.post(
            url,
            data=signed,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.Timeout as exc:
        raise FlowPaymentError("Flow tardó demasiado en responder.") from exc
    except requests.ConnectionError as exc:
        raise FlowPaymentError("No se pudo conectar con Flow.") from exc
    except requests.RequestException as exc:
        raise FlowPaymentError(f"Error de comunicación con Flow: {exc}") from exc
    return _validate_response(response, "No se pudo completar la operación con Flow")


def _get(endpoint: str, parameters: dict[str, Any]) -> dict[str, Any]:
    url = f"{get_flow_api_url()}{endpoint}"
    signed = _signed_parameters(parameters)
    try:
        response = requests.get(
            url,
            params=signed,
            headers={"Accept": "application/json"},
            timeout=REQUEST_TIMEOUT,
        )
    except requests.Timeout as exc:
        raise FlowPaymentError("Flow tardó demasiado en responder.") from exc
    except requests.ConnectionError as exc:
        raise FlowPaymentError("No se pudo conectar con Flow.") from exc
    except requests.RequestException as exc:
        raise FlowPaymentError(f"Error de comunicación con Flow: {exc}") from exc
    return _validate_response(response, "No se pudo consultar Flow")


def _decimal_amount(value: Any) -> float:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise FlowPaymentError("El importe del plan no es válido.") from exc
    if amount <= 0:
        raise FlowPaymentError("El importe debe ser mayor que cero.")
    return float(amount)


def get_flow_plan_data(plan_code: str) -> dict[str, Any]:
    clean_plan = str(plan_code or "").strip().upper()
    plans = {
        "PRO_MONTHLY": {
            "plan_code": "PRO_MONTHLY",
            "plan_label": "AXION PRIME PRO MENSUAL",
            "amount": _secret("FLOW_MONTHLY_AMOUNT", "3000"),
            "currency": get_flow_currency(),
            "duration_days": 30,
        },
        "PRO_ANNUAL": {
            "plan_code": "PRO_ANNUAL",
            "plan_label": "AXION PRIME PRO ANUAL",
            "amount": _secret("FLOW_ANNUAL_AMOUNT", "20000"),
            "currency": get_flow_currency(),
            "duration_days": 365,
        },
    }
    if clean_plan not in plans:
        raise FlowPaymentError(f"El plan '{clean_plan}' no está configurado.")
    selected = plans[clean_plan].copy()
    selected["amount"] = _decimal_amount(selected["amount"])
    return selected


def _commerce_order(
    *,
    user_id: str,
    plan_code: str,
) -> str:
    """
    Genera un commerceOrder único de máximo 45 caracteres.

    Flow rechaza valores superiores a 45 caracteres.
    El user_id y el plan completo siguen viajando por
    separado dentro del campo optional.
    """

    normalized_plan = str(
        plan_code
        or ""
    ).strip().upper()

    plan_aliases = {
        "PRO_MONTHLY": "PM",
        "PRO_ANNUAL": "PA",
    }

    plan_tag = plan_aliases.get(
        normalized_plan,
        "PX",
    )

    clean_user = re.sub(
        r"[^A-Za-z0-9]",
        "",
        str(
            user_id
            or ""
        ),
    )[:8]

    if not clean_user:
        clean_user = "USER"

    unique = uuid.uuid4().hex[:20]

    commerce_order = (
        f"AX-{plan_tag}-"
        f"{clean_user}-"
        f"{unique}"
    )

    return commerce_order[:45]


def _return_url(commerce_order: str) -> str:
    query = urlencode({
        "provider": "flow",
        "commerce_order": commerce_order,
    })
    return f"{get_flow_return_url()}?{query}"


def create_flow_payment(
    *,
    plan_code: str,
    plan_label: str,
    amount: Any,
    currency: str | None = None,
    email: str | None = None,
    payment_method: int | None = None,
) -> FlowCheckout:
    clean_plan = str(plan_code or "").strip().upper()
    clean_label = str(plan_label or "").strip()[:120]
    if not clean_plan:
        raise FlowPaymentError("Falta el código del plan.")
    if not clean_label:
        raise FlowPaymentError("Falta el nombre del plan.")

    clean_amount = _decimal_amount(amount)
    clean_currency = str(currency or get_flow_currency()).strip().upper()
    user_id = get_current_user_id()
    payer_email = str(email or get_current_user_email()).strip().lower()
    commerce_order = _commerce_order(user_id=user_id, plan_code=clean_plan)

    parameters: dict[str, Any] = {
        "apiKey": _required_secret("FLOW_API_KEY"),
        "commerceOrder": commerce_order,
        "subject": clean_label,
        "currency": clean_currency,
        "amount": clean_amount,
        "email": payer_email,
        "urlConfirmation": get_flow_confirmation_url(),
        "urlReturn": _return_url(commerce_order),
        "optional": f"user_id={user_id}&plan_code={clean_plan}",
    }
    if payment_method is not None:
        parameters["paymentMethod"] = int(payment_method)

    data = _post_form("/payment/create", parameters)
    token = str(data.get("token", "") or "").strip()
    flow_order = str(data.get("flowOrder", "") or "").strip()
    base_checkout_url = str(data.get("url", "") or "").strip()

    if not token:
        raise FlowPaymentError("Flow no devolvió el token de pago.")
    if not base_checkout_url:
        raise FlowPaymentError("Flow no devolvió la URL del checkout.")

    checkout_url = f"{base_checkout_url}?{urlencode({'token': token})}"

    return FlowCheckout(
        token=token,
        flow_order=flow_order,
        commerce_order=commerce_order,
        checkout_url=checkout_url,
        plan_code=clean_plan,
        amount=clean_amount,
        currency=clean_currency,
        raw_response=data,
    )


def create_flow_plan_checkout(plan_code: str) -> FlowCheckout:
    plan = get_flow_plan_data(plan_code)
    return create_flow_payment(
        plan_code=plan["plan_code"],
        plan_label=plan["plan_label"],
        amount=plan["amount"],
        currency=plan["currency"],
    )


def get_flow_payment_status(token: str) -> dict[str, Any]:
    clean_token = str(token or "").strip()
    if not clean_token:
        raise FlowPaymentError("Falta el token del pago.")
    return _get(
        "/payment/getStatus",
        {
            "apiKey": _required_secret("FLOW_API_KEY"),
            "token": clean_token,
        },
    )


def get_flow_status_by_commerce_order(commerce_order: str) -> dict[str, Any]:
    clean_order = str(commerce_order or "").strip()
    if not clean_order:
        raise FlowPaymentError("Falta commerceOrder.")
    return _get(
        "/payment/getStatusByCommerceId",
        {
            "apiKey": _required_secret("FLOW_API_KEY"),
            "commerceId": clean_order,
        },
    )


def flow_payment_is_paid(payment_status: dict[str, Any]) -> bool:
    try:
        status = int(payment_status.get("status", 0) or 0)
    except (TypeError, ValueError):
        return False
    return status == 2


def get_flow_public_config() -> dict[str, Any]:
    return {
        "configured": bool(_secret("FLOW_API_KEY") and _secret("FLOW_SECRET_KEY")),
        "mode": get_flow_mode(),
        "api_url": get_flow_api_url(),
        "currency": get_flow_currency(),
        "confirmation_url_configured": bool(get_flow_confirmation_url()),
        "return_url_configured": bool(get_flow_return_url()),
    }
