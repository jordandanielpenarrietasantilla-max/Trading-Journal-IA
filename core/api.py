from __future__ import annotations

import time
from typing import Any

import requests
import streamlit as st

from core.config import (
    SUPABASE_KEY,
    SUPABASE_URL,
)


# =========================================================
# AXION PRIME X10
# CONEXIÓN REST Y AUTENTICACIÓN CON SUPABASE
# =========================================================


REQUEST_TIMEOUT = 50
MAX_TOKEN_LENGTH = 10_000


class ApiError(RuntimeError):
    """
    Error controlado para mostrar mensajes claros
    cuando Supabase rechaza una petición.
    """


# =========================================================
# UTILIDADES
# =========================================================


def _base_url() -> str:
    """
    Devuelve la URL de Supabase sin barra final.
    """

    url = str(
        SUPABASE_URL or ""
    ).strip().rstrip("/")

    if not url:
        raise ApiError(
            "SUPABASE_URL no está configurada."
        )

    return url


def _api_key() -> str:
    """
    Devuelve la clave pública configurada.
    """

    key = str(
        SUPABASE_KEY or ""
    ).strip()

    if not key:
        raise ApiError(
            "SUPABASE_KEY no está configurada."
        )

    return key


def _safe_json(
    response: requests.Response,
) -> Any:
    """
    Convierte una respuesta en JSON cuando sea posible.
    """

    try:
        return response.json()

    except ValueError:
        return None


def _error_message(
    response: requests.Response,
) -> str:
    """
    Extrae un mensaje legible de una respuesta fallida.
    """

    payload = _safe_json(
        response
    )

    if isinstance(payload, dict):
        message = (
            payload.get("message")
            or payload.get("msg")
            or payload.get("error_description")
            or payload.get("error")
            or payload.get("hint")
            or payload.get("details")
        )

        if message:
            return str(message)

    text = str(
        response.text or ""
    ).strip()

    if text:
        return text[:1_500]

    return (
        f"Supabase respondió con HTTP "
        f"{response.status_code}."
    )


def _validate_response(
    response: requests.Response,
    action: str,
) -> Any:
    """
    Comprueba una respuesta de Supabase.
    """

    if response.status_code >= 400:
        raise ApiError(
            f"{action}. "
            f"HTTP {response.status_code}: "
            f"{_error_message(response)}"
        )

    payload = _safe_json(
        response
    )

    if payload is not None:
        return payload

    return {}


def _request(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json: Any = None,
) -> requests.Response:
    """
    Ejecuta una petición HTTP con errores controlados.
    """

    try:
        return requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.Timeout as exc:
        raise ApiError(
            "Supabase tardó demasiado en responder."
        ) from exc

    except requests.ConnectionError as exc:
        raise ApiError(
            "No se pudo establecer conexión con Supabase."
        ) from exc

    except requests.RequestException as exc:
        raise ApiError(
            f"Error de comunicación con Supabase: {exc}"
        ) from exc


# =========================================================
# MANEJO SEGURO DE TOKENS
# =========================================================


def _normalize_token(
    value: Any,
) -> str:
    """
    Obtiene únicamente un access token válido como texto.

    Evita enviar diccionarios, listas, objetos de usuario
    o el session_state completo dentro de Authorization.
    """

    if value is None:
        return ""

    if isinstance(value, dict):
        value = value.get(
            "access_token",
            "",
        )

    if isinstance(value, (list, tuple, set)):
        return ""

    token = str(value).strip()

    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if not token:
        return ""

    if token.startswith("{") or token.startswith("["):
        return ""

    if len(token) > MAX_TOKEN_LENGTH:
        return ""

    return token


def _save_auth_payload(
    payload: dict[str, Any],
) -> None:
    """
    Guarda exclusivamente tokens y usuario necesarios.
    """

    access_token = _normalize_token(
        payload.get("access_token")
    )

    refresh_token = str(
        payload.get(
            "refresh_token",
            "",
        )
        or ""
    ).strip()

    user = payload.get(
        "user",
        {},
    )

    if not access_token:
        raise ApiError(
            "Supabase no devolvió un access token válido."
        )

    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.user = (
        user
        if isinstance(user, dict)
        else {}
    )
    st.session_state.authenticated = True


def clear_api_session() -> None:
    """
    Elimina los datos locales de autenticación.
    """

    for key in (
        "access_token",
        "refresh_token",
        "user",
        "authenticated",
    ):
        if key in st.session_state:
            del st.session_state[key]


def _refresh_access_token() -> str:
    """
    Renueva la sesión utilizando el refresh token.
    """

    refresh_token = str(
        st.session_state.get(
            "refresh_token",
            "",
        )
        or ""
    ).strip()

    if not refresh_token:
        return ""

    response = _request(
        "POST",
        (
            f"{_base_url()}/auth/v1/token"
            "?grant_type=refresh_token"
        ),
        headers={
            "apikey": _api_key(),
            "Content-Type": "application/json",
        },
        json={
            "refresh_token": refresh_token,
        },
    )

    payload = _validate_response(
        response,
        "No se pudo renovar la sesión",
    )

    if not isinstance(payload, dict):
        raise ApiError(
            "Supabase devolvió una renovación inválida."
        )

    _save_auth_payload(
        payload
    )

    return _normalize_token(
        payload.get("access_token")
    )


def ensure_access_token() -> str:
    """
    Devuelve únicamente el JWT del usuario.

    Nunca convierte el usuario, el payload ni todo
    session_state en el encabezado Authorization.
    """

    token = _normalize_token(
        st.session_state.get(
            "access_token",
            "",
        )
    )

    if token:
        return token

    token = _refresh_access_token()

    if token:
        return token

    clear_api_session()

    raise ApiError(
        "La sesión expiró. Cierra sesión y vuelve a entrar."
    )


# =========================================================
# CABECERAS
# =========================================================


def _auth_headers() -> dict[str, str]:
    """
    Cabeceras para endpoints de Supabase Auth.
    """

    return {
        "apikey": _api_key(),
        "Content-Type": "application/json",
    }


def _rest_headers(
    *,
    prefer: str = "",
) -> dict[str, str]:
    """
    Cabeceras para la Data API de Supabase.

    Authorization contiene solamente:
    Bearer <access_token>
    """

    access_token = ensure_access_token()

    headers = {
        "apikey": _api_key(),
        "Authorization": (
            f"Bearer {access_token}"
        ),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if prefer:
        headers["Prefer"] = prefer

    return headers


# =========================================================
# AUTENTICACIÓN
# =========================================================


def sign_in(
    email: str,
    password: str,
) -> dict[str, Any]:
    """
    Inicia sesión con correo y contraseña.
    """

    clean_email = str(
        email or ""
    ).strip().lower()

    clean_password = str(
        password or ""
    )

    if not clean_email:
        raise ApiError(
            "El correo electrónico es obligatorio."
        )

    if not clean_password:
        raise ApiError(
            "La contraseña es obligatoria."
        )

    response = _request(
        "POST",
        (
            f"{_base_url()}/auth/v1/token"
            "?grant_type=password"
        ),
        headers=_auth_headers(),
        json={
            "email": clean_email,
            "password": clean_password,
        },
    )

    payload = _validate_response(
        response,
        "No se pudo iniciar sesión",
    )

    if not isinstance(payload, dict):
        raise ApiError(
            "Supabase devolvió una sesión inválida."
        )

    _save_auth_payload(
        payload
    )

    return payload


def sign_up(
    email: str,
    password: str,
) -> dict[str, Any]:
    """
    Crea una cuenta mediante correo y contraseña.
    """

    clean_email = str(
        email or ""
    ).strip().lower()

    clean_password = str(
        password or ""
    )

    if not clean_email:
        raise ApiError(
            "El correo electrónico es obligatorio."
        )

    if len(clean_password) < 6:
        raise ApiError(
            "La contraseña debe tener al menos "
            "6 caracteres."
        )

    response = _request(
        "POST",
        f"{_base_url()}/auth/v1/signup",
        headers=_auth_headers(),
        json={
            "email": clean_email,
            "password": clean_password,
        },
    )

    payload = _validate_response(
        response,
        "No se pudo crear la cuenta",
    )

    if not isinstance(payload, dict):
        raise ApiError(
            "Supabase devolvió un registro inválido."
        )

    if payload.get("access_token"):
        _save_auth_payload(
            payload
        )

    return payload


def reset_password(
    email: str,
    redirect_url: str = "",
) -> dict[str, Any]:
    """
    Envía el correo de recuperación de contraseña.
    """

    clean_email = str(
        email or ""
    ).strip().lower()

    clean_redirect = str(
        redirect_url or ""
    ).strip()

    if not clean_email:
        raise ApiError(
            "El correo electrónico es obligatorio."
        )

    body: dict[str, Any] = {
        "email": clean_email,
    }

    if clean_redirect:
        body["redirect_to"] = clean_redirect

    response = _request(
        "POST",
        f"{_base_url()}/auth/v1/recover",
        headers=_auth_headers(),
        json=body,
    )

    payload = _validate_response(
        response,
        "No se pudo enviar la recuperación",
    )

    return (
        payload
        if isinstance(payload, dict)
        else {}
    )


def get_current_user() -> dict[str, Any]:
    """
    Consulta el usuario de la sesión actual.
    """

    response = _request(
        "GET",
        f"{_base_url()}/auth/v1/user",
        headers=_rest_headers(),
    )

    payload = _validate_response(
        response,
        "No se pudo consultar el usuario",
    )

    if not isinstance(payload, dict):
        return {}

    st.session_state.user = payload

    return payload


# =========================================================
# CARGAR OPERACIONES
# =========================================================


def list_trades() -> list[dict[str, Any]]:
    """
    Obtiene los trades visibles para el usuario actual.

    Las políticas RLS de Supabase deben filtrar cada usuario.
    """

    response = _request(
        "GET",
        f"{_base_url()}/rest/v1/trades",
        headers=_rest_headers(),
        params={
            "select": "*",
            "order": "fecha.desc",
        },
    )

    payload = _validate_response(
        response,
        "No se pudieron cargar los trades",
    )

    if payload is None:
        return []

    if not isinstance(payload, list):
        raise ApiError(
            "Supabase devolvió un formato inesperado "
            "al cargar los trades."
        )

    return [
        item
        for item in payload
        if isinstance(item, dict)
    ]


# =========================================================
# GUARDAR OPERACIÓN MEDIANTE RPC
# =========================================================


def _trade_rpc_payload(
    trade_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Convierte los campos del formulario en los parámetros
    esperados por la función axion_save_trade de Supabase.
    """

    return {
        "p_fecha":
            trade_data.get("fecha"),

        "p_par":
            trade_data.get("par"),

        "p_direccion":
            trade_data.get("direccion"),

        "p_precio_entrada":
            trade_data.get("precio_entrada"),

        "p_stop_loss":
            trade_data.get("stop_loss"),

        "p_take_profit":
            trade_data.get("take_profit"),

        "p_rr":
            trade_data.get("rr"),

        "p_timeframe":
            trade_data.get("timeframe"),

        "p_resultado":
            trade_data.get("resultado"),

        "p_emocion":
            trade_data.get("emocion"),

        "p_notas_emocionales":
            trade_data.get("notas_emocionales"),

        "p_beneficio_usd":
            trade_data.get("beneficio_usd"),

        "p_trades_cant":
            trade_data.get(
                "trades_cant",
                1,
            ),

        "p_img_before":
            trade_data.get(
                "img_before",
                "",
            ),

        "p_img_after":
            trade_data.get(
                "img_after",
                "",
            ),
    }


def save_trade_rpc(
    trade_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Guarda una operación utilizando axion_save_trade.
    """

    if not isinstance(trade_data, dict):
        raise ApiError(
            "Los datos del trade son inválidos."
        )

    rpc_payload = _trade_rpc_payload(
        trade_data
    )

    response = _request(
        "POST",
        (
            f"{_base_url()}"
            "/rest/v1/rpc/axion_save_trade"
        ),
        headers=_rest_headers(
            prefer="return=representation",
        ),
        json=rpc_payload,
    )

    payload = _validate_response(
        response,
        "No se pudo guardar la operación",
    )

    if isinstance(payload, list):
        if payload and isinstance(
            payload[0],
            dict,
        ):
            return payload[0]

        return {
            "success": True,
        }

    if isinstance(payload, dict):
        return payload

    return {
        "success": True,
    }


def save_trade(
    trade_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Alias compatible para módulos que llamen save_trade.
    """

    return save_trade_rpc(
        trade_data
    )


# =========================================================
# ELIMINAR OPERACIÓN
# =========================================================


def delete_trade(
    trade_id: str,
) -> bool:
    """
    Elimina una operación por ID.
    """

    clean_id = str(
        trade_id or ""
    ).strip()

    if not clean_id:
        raise ApiError(
            "El ID de la operación es obligatorio."
        )

    response = _request(
        "DELETE",
        f"{_base_url()}/rest/v1/trades",
        headers=_rest_headers(
            prefer="return=minimal",
        ),
        params={
            "id": f"eq.{clean_id}",
        },
    )

    _validate_response(
        response,
        "No se pudo eliminar la operación",
    )

    return True


# =========================================================
# ACTUALIZAR OPERACIÓN
# =========================================================


def update_trade(
    trade_id: str,
    changes: dict[str, Any],
) -> dict[str, Any]:
    """
    Actualiza campos de una operación.
    """

    clean_id = str(
        trade_id or ""
    ).strip()

    if not clean_id:
        raise ApiError(
            "El ID de la operación es obligatorio."
        )

    if not isinstance(changes, dict):
        raise ApiError(
            "Los cambios enviados son inválidos."
        )

    allowed_columns = {
        "fecha",
        "par",
        "direccion",
        "precio_entrada",
        "stop_loss",
        "take_profit",
        "rr",
        "timeframe",
        "resultado",
        "emocion",
        "notas_emocionales",
        "beneficio_usd",
        "trades_cant",
        "img_before",
        "img_after",
    }

    safe_changes = {
        key: value
        for key, value in changes.items()
        if key in allowed_columns
    }

    if not safe_changes:
        raise ApiError(
            "No existen campos válidos para actualizar."
        )

    response = _request(
        "PATCH",
        f"{_base_url()}/rest/v1/trades",
        headers=_rest_headers(
            prefer="return=representation",
        ),
        params={
            "id": f"eq.{clean_id}",
        },
        json=safe_changes,
    )

    payload = _validate_response(
        response,
        "No se pudo actualizar la operación",
    )

    if isinstance(payload, list) and payload:
        first = payload[0]

        if isinstance(first, dict):
            return first

    if isinstance(payload, dict):
        return payload

    return {
        "success": True,
    }


# =========================================================
# DIAGNÓSTICO SEGURO
# =========================================================


def connection_diagnostics() -> dict[str, Any]:
    """
    Información segura para comprobar la sesión sin mostrar
    claves ni tokens.
    """

    token = _normalize_token(
        st.session_state.get(
            "access_token",
            "",
        )
    )

    refresh_token = str(
        st.session_state.get(
            "refresh_token",
            "",
        )
        or ""
    )

    return {
        "supabase_url_configured":
            bool(SUPABASE_URL),

        "supabase_key_configured":
            bool(SUPABASE_KEY),

        "access_token_present":
            bool(token),

        "access_token_length":
            len(token),

        "refresh_token_present":
            bool(refresh_token),

        "authenticated":
            bool(
                st.session_state.get(
                    "authenticated",
                    False,
                )
            ),

        "checked_at":
            int(time.time()),
    }
