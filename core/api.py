from __future__ import annotations

from typing import Any
from urllib.parse import quote

import base64
import json
import time

import requests
import streamlit as st

from core.config import SUPABASE_KEY, SUPABASE_URL


# =========================================================
# AXION PRIME X10
# API DE SUPABASE COMPLETA
# =========================================================


REQUEST_TIMEOUT = 45


class ApiError(RuntimeError):
    """Error controlado de conexión con Supabase."""


# =========================================================
# CONFIGURACIÓN
# =========================================================


def _base_url() -> str:
    url = str(SUPABASE_URL or "").strip().rstrip("/")

    if not url:
        raise ApiError(
            "SUPABASE_URL no está configurada."
        )

    return url


def _api_key() -> str:
    key = str(SUPABASE_KEY or "").strip()

    if not key:
        raise ApiError(
            "SUPABASE_KEY no está configurada."
        )

    return key


# =========================================================
# RESPUESTAS HTTP
# =========================================================


def _safe_json(
    response: requests.Response,
) -> Any:
    try:
        return response.json()

    except ValueError:
        return None


def _extract_error(
    response: requests.Response,
) -> str:
    payload = _safe_json(response)

    if isinstance(payload, dict):
        for key in (
            "message",
            "msg",
            "error_description",
            "error",
            "hint",
            "details",
            "code",
        ):
            value = payload.get(key)

            if value:
                return str(value)

    text = str(response.text or "").strip()

    if text:
        return text[:1200]

    return (
        f"Supabase respondió con HTTP "
        f"{response.status_code}."
    )


def _validate_response(
    response: requests.Response,
    action: str,
) -> Any:
    if response.status_code >= 400:
        raise ApiError(
            f"{action}. HTTP {response.status_code}: "
            f"{_extract_error(response)}"
        )

    payload = _safe_json(response)

    if payload is None:
        return {}

    return payload


def _request(
    method: str,
    endpoint: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json: Any = None,
) -> requests.Response:
    url = (
        endpoint
        if endpoint.startswith("http")
        else f"{_base_url()}{endpoint}"
    )

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
            "No se pudo conectar con Supabase."
        ) from exc

    except requests.RequestException as exc:
        raise ApiError(
            f"Error de comunicación: {exc}"
        ) from exc


# =========================================================
# TOKENS
# =========================================================


def _clean_token(
    value: Any,
) -> str:
    if value is None:
        return ""

    if isinstance(value, (dict, list, tuple, set)):
        return ""

    token = str(value).strip()

    if token.lower().startswith("bearer "):
        token = token[7:].strip()

    if token.startswith("{") or token.startswith("["):
        return ""

    return token


def _session_from_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Acepta las dos formas posibles:

    1. Respuesta REST directa:
       {
           "access_token": "...",
           "refresh_token": "...",
           "user": {...}
       }

    2. Respuesta con sesión anidada:
       {
           "session": {
               "access_token": "...",
               "refresh_token": "..."
           },
           "user": {...}
       }
    """

    nested_session = payload.get("session")

    if isinstance(nested_session, dict):
        session = nested_session.copy()

        if "user" not in session:
            session["user"] = payload.get(
                "user",
                {},
            )

        return session

    data = payload.get("data")

    if isinstance(data, dict):
        nested_data_session = data.get("session")

        if isinstance(nested_data_session, dict):
            session = nested_data_session.copy()

            if "user" not in session:
                session["user"] = data.get(
                    "user",
                    payload.get("user", {}),
                )

            return session

        if data.get("access_token"):
            return data

    return payload


def _save_auth_payload(
    payload: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ApiError(
            "Supabase devolvió una respuesta inválida."
        )

    session = _session_from_payload(payload)

    access_token = _clean_token(
        session.get("access_token")
    )

    refresh_token = _clean_token(
        session.get("refresh_token")
    )

    user = (
        session.get("user")
        or payload.get("user")
        or {}
    )

    if not access_token:
        available_keys = ", ".join(
            sorted(payload.keys())
        ) or "ninguna"

        raise ApiError(
            "Supabase no devolvió una sesión activa. "
            "Puede que el correo todavía no esté confirmado. "
            f"Campos recibidos: {available_keys}"
        )

    st.session_state.access_token = access_token
    st.session_state.refresh_token = refresh_token
    st.session_state.user = (
        user
        if isinstance(user, dict)
        else {}
    )

    st.session_state.authenticated = True
    st.session_state.page = "Dashboard"

    return session


def clear_api_session() -> None:
    for key in (
        "access_token",
        "refresh_token",
        "user",
        "authenticated",
        "page",
    ):
        st.session_state.pop(
            key,
            None,
        )


def _refresh_access_token() -> str:
    refresh_token = _clean_token(
        st.session_state.get(
            "refresh_token",
            "",
        )
    )

    if not refresh_token:
        return ""

    response = _request(
        "POST",
        "/auth/v1/token?grant_type=refresh_token",
        headers={
            "apikey": _api_key(),
            "Content-Type": "application/json",
            "Accept": "application/json",
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
        return ""

    session = _save_auth_payload(payload)

    return _clean_token(
        session.get("access_token")
    )


def _jwt_expiry(
    token: str,
) -> int | None:
    """
    Lee únicamente el campo exp del JWT para saber cuándo
    solicitar un refresh.

    No se usa para validar seguridad ni firma del token:
    Supabase sigue siendo quien valida el JWT en cada request.
    """

    clean = _clean_token(token)

    if not clean:
        return None

    parts = clean.split(".")

    if len(parts) != 3:
        return None

    try:
        payload_part = parts[1]
        padding = "=" * (-len(payload_part) % 4)

        decoded = base64.urlsafe_b64decode(
            payload_part + padding
        )

        payload = json.loads(
            decoded.decode("utf-8")
        )

        exp = payload.get("exp")

        if exp is None:
            return None

        return int(exp)

    except (
        ValueError,
        TypeError,
        json.JSONDecodeError,
    ):
        return None

    except Exception:
        return None


def _access_token_needs_refresh(
    token: str,
    leeway_seconds: int = 90,
) -> bool:
    """
    Renueva un poco antes del vencimiento para evitar que
    el token expire entre la creación de headers y Supabase.
    """

    clean = _clean_token(token)

    if not clean:
        return True

    expiry = _jwt_expiry(clean)

    # Si por alguna razón no podemos leer exp, mantenemos
    # compatibilidad y dejamos que Supabase valide el token.
    if expiry is None:
        return False

    return expiry <= int(time.time()) + leeway_seconds


def ensure_access_token() -> str:
    """
    Devuelve un access token vigente.

    Antes, AXION PRIME devolvía cualquier token no vacío,
    incluso cuando su JWT ya había expirado. Eso provocaba:
        HTTP 401: JWT expired

    Ahora comprobamos exp y usamos el refresh_token antes
    de enviar la petición a Supabase.
    """

    access_token = _clean_token(
        st.session_state.get(
            "access_token",
            "",
        )
    )

    if (
        access_token
        and not _access_token_needs_refresh(
            access_token
        )
    ):
        return access_token

    try:
        refreshed_token = _refresh_access_token()

    except ApiError:
        refreshed_token = ""

    if refreshed_token:
        return refreshed_token

    clear_api_session()

    raise ApiError(
        "Tu sesión expiró. Inicia sesión nuevamente para continuar."
    )


# =========================================================
# CABECERAS
# =========================================================


def _auth_headers() -> dict[str, str]:
    return {
        "apikey": _api_key(),
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _rest_headers(
    prefer: str = "",
) -> dict[str, str]:
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
    clean_email = str(
        email or ""
    ).strip().lower()

    clean_password = str(
        password or ""
    )

    if not clean_email:
        raise ApiError(
            "Introduce tu correo electrónico."
        )

    if not clean_password:
        raise ApiError(
            "Introduce tu contraseña."
        )

    response = _request(
        "POST",
        "/auth/v1/token?grant_type=password",
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
            "Supabase devolvió una respuesta inesperada."
        )

    _save_auth_payload(payload)

    return payload


def sign_up(
    email: str,
    password: str,
) -> dict[str, Any]:
    clean_email = str(
        email or ""
    ).strip().lower()

    clean_password = str(
        password or ""
    )

    if not clean_email:
        raise ApiError(
            "Introduce un correo electrónico."
        )

    if len(clean_password) < 6:
        raise ApiError(
            "La contraseña debe tener al menos "
            "6 caracteres."
        )

    response = _request(
        "POST",
        "/auth/v1/signup",
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

    session = _session_from_payload(payload)

    if session.get("access_token"):
        _save_auth_payload(payload)

    return payload


def reset_password(
    email: str,
    redirect_url: str = "",
) -> dict[str, Any]:
    clean_email = str(
        email or ""
    ).strip().lower()

    clean_redirect = str(
        redirect_url or ""
    ).strip()

    if not clean_email:
        raise ApiError(
            "Introduce tu correo electrónico."
        )

    body: dict[str, Any] = {
        "email": clean_email,
    }

    if clean_redirect:
        body["redirect_to"] = clean_redirect

    response = _request(
        "POST",
        "/auth/v1/recover",
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


# =========================================================
# OPERACIONES
# =========================================================


def list_trades() -> list[dict[str, Any]]:
    response = _request(
        "GET",
        "/rest/v1/trades",
        headers=_rest_headers(),
        params={
            "select": "*",
            "order": "fecha.desc,created_at.desc",
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
            "Supabase devolvió un formato inválido "
            "al cargar las operaciones."
        )

    return [
        item
        for item in payload
        if isinstance(item, dict)
    ]


def _trade_rpc_payload(
    trade_data: dict[str, Any],
) -> dict[str, Any]:
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
            trade_data.get(
                "notas_emocionales"
            ),

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
    if not isinstance(trade_data, dict):
        raise ApiError(
            "Los datos de la operación son inválidos."
        )

    response = _request(
        "POST",
        "/rest/v1/rpc/axion_save_trade",
        headers=_rest_headers(
            prefer="return=representation",
        ),
        json=_trade_rpc_payload(
            trade_data
        ),
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
    return save_trade_rpc(
        trade_data
    )


def delete_trade(
    trade_id: str,
) -> bool:
    clean_id = str(
        trade_id or ""
    ).strip()

    if not clean_id:
        raise ApiError(
            "El ID de la operación está vacío."
        )

    response = _request(
        "DELETE",
        "/rest/v1/trades",
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


def update_trade(
    trade_id: str,
    changes: dict[str, Any],
) -> dict[str, Any]:
    clean_id = str(
        trade_id or ""
    ).strip()

    if not clean_id:
        raise ApiError(
            "El ID de la operación está vacío."
        )

    if not isinstance(changes, dict):
        raise ApiError(
            "Los cambios recibidos son inválidos."
        )

    response = _request(
        "PATCH",
        "/rest/v1/trades",
        headers=_rest_headers(
            prefer="return=representation",
        ),
        params={
            "id": f"eq.{clean_id}",
        },
        json=changes,
    )

    payload = _validate_response(
        response,
        "No se pudo actualizar la operación",
    )

    if isinstance(payload, list) and payload:
        if isinstance(payload[0], dict):
            return payload[0]

    if isinstance(payload, dict):
        return payload

    return {
        "success": True,
    }


# =========================================================
# PERFIL Y STORAGE
# =========================================================


def upload_avatar(
    file_bytes: bytes,
    user_id: str,
    *,
    content_type: str = "image/jpeg",
    extension: str = "jpg",
) -> str:
    """
    Sube el avatar del usuario al bucket público `avatars`
    usando la API REST de Supabase Storage.
    """

    clean_user_id = str(user_id or "").strip()
    clean_extension = str(extension or "jpg").strip().lower()

    if not clean_user_id:
        raise ApiError(
            "No se pudo obtener el ID del usuario."
        )

    if not isinstance(file_bytes, (bytes, bytearray)):
        raise ApiError(
            "La imagen recibida no es válida."
        )

    object_path = (
        f"{clean_user_id}/avatar.{clean_extension}"
    )

    encoded_path = quote(
        object_path,
        safe="/",
    )

    url = (
        f"{_base_url()}"
        f"/storage/v1/object/avatars/"
        f"{encoded_path}"
    )

    headers = {
        "apikey": _api_key(),
        "Authorization": (
            f"Bearer {ensure_access_token()}"
        ),
        "Content-Type": content_type,
        "x-upsert": "true",
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            data=bytes(file_bytes),
            timeout=REQUEST_TIMEOUT,
        )

    except requests.Timeout as exc:
        raise ApiError(
            "La subida del avatar tardó demasiado."
        ) from exc

    except requests.RequestException as exc:
        raise ApiError(
            f"No se pudo subir el avatar: {exc}"
        ) from exc

    _validate_response(
        response,
        "No se pudo subir el avatar",
    )

    return (
        f"{_base_url()}"
        f"/storage/v1/object/public/avatars/"
        f"{encoded_path}"
    )


def update_user_metadata(
    metadata: dict[str, Any],
) -> dict[str, Any]:
    """
    Actualiza los metadatos del usuario autenticado
    mediante la API REST de Supabase Auth.
    """

    if not isinstance(metadata, dict):
        raise ApiError(
            "Los metadatos recibidos son inválidos."
        )

    response = _request(
        "PUT",
        "/auth/v1/user",
        headers={
            "apikey": _api_key(),
            "Authorization": (
                f"Bearer {ensure_access_token()}"
            ),
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json={
            "data": metadata,
        },
    )

    payload = _validate_response(
        response,
        "No se pudo actualizar el perfil",
    )

    if not isinstance(payload, dict):
        raise ApiError(
            "Supabase devolvió un perfil inválido."
        )

    st.session_state.user = payload

    return payload
