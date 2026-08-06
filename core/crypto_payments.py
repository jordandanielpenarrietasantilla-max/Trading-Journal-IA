from __future__ import annotations

from typing import Any

import requests
import streamlit as st

from core.api import ensure_access_token
from core.config import SUPABASE_KEY, SUPABASE_URL


REQUEST_TIMEOUT = 45


class CryptoPaymentError(RuntimeError):
    """Error controlado para pagos cripto automáticos."""


def _base_url() -> str:
    value = str(SUPABASE_URL or "").strip().rstrip("/")

    if not value:
        raise CryptoPaymentError(
            "SUPABASE_URL no está configurada."
        )

    return value


def _api_key() -> str:
    value = str(SUPABASE_KEY or "").strip()

    if not value:
        raise CryptoPaymentError(
            "SUPABASE_KEY no está configurada."
        )

    return value


def _safe_json(response: requests.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except ValueError:
        payload = {}

    return payload if isinstance(payload, dict) else {}


def _extract_error(payload: dict[str, Any], response: requests.Response) -> str:
    for key in (
        "error",
        "message",
        "detail",
        "hint",
    ):
        value = payload.get(key)

        if value:
            return str(value)

    text = str(response.text or "").strip()

    return text[:1200] if text else (
        f"Supabase respondió con HTTP {response.status_code}."
    )


def _invoke_function(
    function_name: str,
    body: dict[str, Any],
) -> dict[str, Any]:
    access_token = ensure_access_token()

    url = (
        f"{_base_url()}"
        f"/functions/v1/{function_name}"
    )

    try:
        response = requests.post(
            url,
            headers={
                "apikey": _api_key(),
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=body,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.Timeout as exc:
        raise CryptoPaymentError(
            "La verificación tardó demasiado. Intenta nuevamente."
        ) from exc
    except requests.RequestException as exc:
        raise CryptoPaymentError(
            f"No se pudo conectar con el servicio de pagos: {exc}"
        ) from exc

    payload = _safe_json(response)

    # crypto-verify usa HTTP 202 cuando la transacción aún está pendiente.
    if response.status_code >= 400:
        raise CryptoPaymentError(
            _extract_error(payload, response)
        )

    return payload


def create_usdt_order(plan_code: str) -> dict[str, Any]:
    """Crea o reutiliza una orden USDT TRC20 pendiente."""

    clean_plan = str(plan_code or "").strip().upper()

    if clean_plan not in {
        "PRO_MONTHLY",
        "PRO_ANNUAL",
    }:
        raise CryptoPaymentError(
            "El plan seleccionado no es válido para USDT."
        )

    payload = _invoke_function(
        "crypto-create-order",
        {
            "plan_code": clean_plan,
        },
    )

    order = payload.get("order")

    if not payload.get("ok") or not isinstance(order, dict):
        raise CryptoPaymentError(
            str(
                payload.get("error")
                or "No se pudo crear la orden USDT."
            )
        )

    return order


def verify_usdt_order(
    order_id: str,
    txid: str,
) -> dict[str, Any]:
    """Verifica el TXID y activa PRO cuando la función lo aprueba."""

    clean_order_id = str(order_id or "").strip()
    clean_txid = str(txid or "").strip()

    if not clean_order_id:
        raise CryptoPaymentError(
            "Primero debes generar una orden de pago."
        )

    if not clean_txid:
        raise CryptoPaymentError(
            "Debes pegar el TXID de la transacción."
        )

    payload = _invoke_function(
        "crypto-verify",
        {
            "order_id": clean_order_id,
            "txid": clean_txid,
        },
    )

    return payload


def apply_verified_membership_to_session(
    payload: dict[str, Any],
) -> None:
    """Refleja inmediatamente en Streamlit la membresía aprobada."""

    if not payload.get("ok"):
        return

    membership = payload.get("membership")

    if not isinstance(membership, dict):
        return

    user = st.session_state.get("user")

    if not isinstance(user, dict):
        return

    metadata = user.get("user_metadata")

    if not isinstance(metadata, dict):
        metadata = {}

    plan = str(membership.get("plan") or "").strip()
    status = str(membership.get("status") or "active").strip()

    updated_metadata = {
        **metadata,
        "plan": plan,
        "plan_code": plan,
        "subscription_plan": plan,
        "membership_plan": plan,
        "membership_status": status,
        "subscription_status": status,
        "plan_started_at": membership.get("started_at") or "",
        "plan_expires_at": membership.get("expires_at") or "",
        "payment_provider": "crypto_usdt_trc20",
        "provider": "crypto_usdt_trc20",
        "plan_source": "crypto_usdt_trc20",
    }

    st.session_state.user = {
        **user,
        "user_metadata": updated_metadata,
    }
    st.session_state.user_metadata = updated_metadata
