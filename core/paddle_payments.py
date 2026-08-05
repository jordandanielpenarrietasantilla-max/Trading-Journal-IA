from __future__ import annotations

import html
import json
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

from core.config import (
    APP_URL,
    PADDLE_ANNUAL_PRICE_ID,
    PADDLE_CLIENT_TOKEN,
    PADDLE_ENVIRONMENT,
    PADDLE_MONTHLY_PRICE_ID,
)


class PaddlePaymentError(RuntimeError):
    """Error controlado para el checkout internacional de Paddle."""


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


def _current_user() -> dict[str, Any]:
    user = _safe_dict(st.session_state.get("user", {}))
    if not user:
        raise PaddlePaymentError("No se encontró un usuario autenticado.")
    return user


def _current_user_id() -> str:
    user = _current_user()
    metadata = _safe_dict(user.get("user_metadata", {}))
    for value in (user.get("id"), user.get("sub"), metadata.get("sub")):
        clean = str(value or "").strip()
        if clean:
            return clean
    raise PaddlePaymentError("No se encontró el ID del usuario autenticado.")


def _current_user_email() -> str:
    email = str(_current_user().get("email", "") or "").strip().lower()
    if not email:
        raise PaddlePaymentError("El usuario autenticado no tiene correo.")
    return email


def get_paddle_price_id(plan_code: str) -> str:
    normalized = str(plan_code or "").strip().upper()
    if normalized == "PRO_MONTHLY":
        price_id = PADDLE_MONTHLY_PRICE_ID
    elif normalized == "PRO_ANNUAL":
        price_id = PADDLE_ANNUAL_PRICE_ID
    else:
        raise PaddlePaymentError(f"Plan Paddle no permitido: {normalized}.")

    if not price_id:
        raise PaddlePaymentError(
            "Falta el Price ID de Paddle en Streamlit Secrets."
        )
    return price_id


def get_paddle_plan_data(plan_code: str) -> dict[str, Any]:
    normalized = str(plan_code or "").strip().upper()
    if normalized == "PRO_MONTHLY":
        return {
            "plan_code": normalized,
            "plan_label": "AXION PRIME PRO MENSUAL",
            "price_id": get_paddle_price_id(normalized),
            "amount": 6,
            "currency": "USD",
            "billing": "mensual",
        }
    if normalized == "PRO_ANNUAL":
        return {
            "plan_code": normalized,
            "plan_label": "AXION PRIME PRO ANUAL",
            "price_id": get_paddle_price_id(normalized),
            "amount": 40,
            "currency": "USD",
            "billing": "anual",
        }
    raise PaddlePaymentError(f"Plan Paddle no permitido: {normalized}.")


def paddle_is_configured() -> bool:
    return bool(
        PADDLE_CLIENT_TOKEN
        and PADDLE_MONTHLY_PRICE_ID
        and PADDLE_ANNUAL_PRICE_ID
    )


def render_paddle_checkout(plan_code: str) -> None:
    """Renderiza un botón que abre Paddle Checkout en un iframe de Streamlit."""

    if not paddle_is_configured():
        raise PaddlePaymentError(
            "Paddle todavía no está configurado completamente en Streamlit Secrets."
        )

    plan = get_paddle_plan_data(plan_code)
    user_id = _current_user_id()
    email = _current_user_email()

    environment = str(PADDLE_ENVIRONMENT or "production").strip().lower()
    if environment not in {"production", "sandbox"}:
        raise PaddlePaymentError(
            "PADDLE_ENVIRONMENT debe ser 'production' o 'sandbox'."
        )

    app_url = str(APP_URL or "").strip().rstrip("/")
    success_url = (
        f"{app_url}?provider=paddle&status=success"
        if app_url
        else ""
    )

    token_js = json.dumps(PADDLE_CLIENT_TOKEN)
    price_js = json.dumps(plan["price_id"])
    user_id_js = json.dumps(user_id)
    email_js = json.dumps(email)
    plan_code_js = json.dumps(plan["plan_code"])
    success_url_js = json.dumps(success_url)
    environment_js = json.dumps(environment)

    components.html(
        f"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <script src="https://cdn.paddle.com/paddle/v2/paddle.js"></script>
  <style>
    html, body {{ margin: 0; padding: 0; background: transparent; }}
    .wrap {{ font-family: Inter, Arial, sans-serif; padding: 2px 0; }}
    .pay {{
      width: 100%; min-height: 54px; border: 0; border-radius: 12px;
      color: #fff; font-size: 15px; font-weight: 800; cursor: pointer;
      background: linear-gradient(90deg,#21c7ef,#7a42f4,#ee35bf);
      box-shadow: 0 12px 28px rgba(80,70,255,.25);
    }}
    .pay:disabled {{ opacity: .6; cursor: wait; }}
    .note {{ color: #9ba8c9; font-size: 12px; text-align: center; margin-top: 10px; }}
    .error {{ color: #ff8fa3; font-size: 12px; margin-top: 8px; text-align: center; }}
  </style>
</head>
<body>
  <div class="wrap">
    <button id="paddle-pay" class="pay">🌎 PAGAR CON PADDLE · {html.escape(plan['currency'])} {plan['amount']}</button>
    <div class="note">Visa, Mastercard y métodos internacionales. Paddle procesa el pago de forma segura.</div>
    <div id="error" class="error"></div>
  </div>

  <script>
    const environment = {environment_js};
    if (environment === "sandbox") {{
      Paddle.Environment.set("sandbox");
    }}

    Paddle.Initialize({{
      token: {token_js},
      eventCallback: function(event) {{
        if (event && event.name === "checkout.completed") {{
          document.getElementById("paddle-pay").textContent = "✅ PAGO RECIBIDO · VERIFICANDO ACCESO";
        }}
      }}
    }});

    const button = document.getElementById("paddle-pay");
    button.addEventListener("click", function() {{
      button.disabled = true;
      document.getElementById("error").textContent = "";
      try {{
        const checkout = {{
          items: [{{ priceId: {price_js}, quantity: 1 }}],
          customer: {{ email: {email_js} }},
          customData: {{
            user_id: {user_id_js},
            email: {email_js},
            plan_code: {plan_code_js}
          }},
          settings: {{
            displayMode: "overlay",
            theme: "dark",
            locale: "es"
          }}
        }};

        const successUrl = {success_url_js};
        if (successUrl) checkout.settings.successUrl = successUrl;
        Paddle.Checkout.open(checkout);
      }} catch (error) {{
        button.disabled = false;
        document.getElementById("error").textContent = String(error && error.message ? error.message : error);
      }}
      setTimeout(() => {{ button.disabled = false; }}, 2500);
    }});
  </script>
</body>
</html>
        """,
        height=105,
        scrolling=False,
    )
