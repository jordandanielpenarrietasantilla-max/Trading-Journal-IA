from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.flow_payments import (
    FlowCheckout,
    FlowPaymentError,
    create_flow_payment,
    create_flow_plan_checkout,
    flow_payment_is_paid,
    get_flow_payment_status,
    get_flow_plan_data,
    get_flow_status_by_commerce_order,
)


# =========================================================
# AXION PRIME
# COMPATIBILIDAD DE PAGOS · FLOW
# =========================================================


class PaymentError(FlowPaymentError):
    """Alias compatible para errores de pago."""
    pass


@dataclass(frozen=True)
class CheckoutPreference:
    """Estructura compatible con el antiguo sistema de pagos."""

    preference_id: str
    checkout_url: str
    external_reference: str
    mode: str
    raw_response: dict[str, Any]


def _to_compatible_checkout(
    checkout: FlowCheckout,
) -> CheckoutPreference:
    return CheckoutPreference(
        preference_id=checkout.token,
        checkout_url=checkout.checkout_url,
        external_reference=checkout.commerce_order,
        mode="FLOW",
        raw_response=checkout.raw_response,
    )


def create_checkout_preference(
    *,
    plan_code: str,
    plan_label: str,
    amount: Any,
    currency_id: str | None = None,
    description: str = "",
) -> CheckoutPreference:
    """Crea un checkout de Flow manteniendo la firma antigua."""

    try:
        checkout = create_flow_payment(
            plan_code=plan_code,
            plan_label=plan_label,
            amount=amount,
            currency=currency_id,
        )
    except FlowPaymentError as exc:
        raise PaymentError(str(exc)) from exc

    return _to_compatible_checkout(checkout)


def create_plan_checkout(
    plan_code: str,
) -> CheckoutPreference:
    """Crea un checkout para PRO_MONTHLY o PRO_ANNUAL."""

    try:
        checkout = create_flow_plan_checkout(plan_code)
    except FlowPaymentError as exc:
        raise PaymentError(str(exc)) from exc

    return _to_compatible_checkout(checkout)


def get_plan_checkout_data(
    plan_code: str,
) -> dict[str, Any]:
    """Devuelve los datos del plan en formato compatible."""

    try:
        plan = get_flow_plan_data(plan_code)
    except FlowPaymentError as exc:
        raise PaymentError(str(exc)) from exc

    return {
        "plan_code": plan["plan_code"],
        "plan_label": plan["plan_label"],
        "amount": plan["amount"],
        "currency_id": plan["currency"],
        "currency": plan["currency"],
        "duration_days": plan["duration_days"],
        "provider": "flow",
    }


def get_payment(
    payment_id: str | int,
) -> dict[str, Any]:
    """Consulta un pago en Flow usando su token."""

    try:
        return get_flow_payment_status(str(payment_id))
    except FlowPaymentError as exc:
        raise PaymentError(str(exc)) from exc


def get_preference(
    preference_id: str,
) -> dict[str, Any]:
    """Alias compatible; en Flow usa el token de la orden."""

    return get_payment(preference_id)


def get_payment_by_commerce_order(
    commerce_order: str,
) -> dict[str, Any]:
    """Consulta una orden por commerceOrder."""

    try:
        return get_flow_status_by_commerce_order(commerce_order)
    except FlowPaymentError as exc:
        raise PaymentError(str(exc)) from exc


def payment_is_approved(
    payment: dict[str, Any],
) -> bool:
    """Devuelve True cuando Flow informa estado pagado."""

    return flow_payment_is_paid(payment)


def get_payment_provider() -> str:
    return "flow"


def get_payment_provider_label() -> str:
    return "Flow · Webpay · Visa · Mastercard"
