from __future__ import annotations

import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

import requests
import streamlit as st

from core.api import ensure_access_token
from core.config import SUPABASE_KEY, SUPABASE_URL


# =========================================================
# AXION PRIME X10 PRO
# GESTIÓN SEGURA DEL PERFIL Y AVATAR
# =========================================================


REQUEST_TIMEOUT = 50

AVATAR_BUCKET = "avatars"

MAX_AVATAR_BYTES = 5 * 1024 * 1024

ALLOWED_AVATAR_TYPES = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
}


class ProfileError(RuntimeError):
    """
    Error controlado para operaciones del perfil.
    """


# =========================================================
# CONFIGURACIÓN
# =========================================================


def _base_url() -> str:
    """
    Devuelve la URL de Supabase sin barra final.
    """

    url = str(
        SUPABASE_URL or ""
    ).strip().rstrip("/")

    if not url:
        raise ProfileError(
            "SUPABASE_URL no está configurada."
        )

    return url


def _api_key() -> str:
    """
    Devuelve la clave pública de Supabase.
    """

    key = str(
        SUPABASE_KEY or ""
    ).strip()

    if not key:
        raise ProfileError(
            "SUPABASE_KEY no está configurada."
        )

    return key


# =========================================================
# UTILIDADES DEL USUARIO
# =========================================================


def _current_user() -> dict[str, Any]:
    """
    Devuelve el usuario autenticado guardado en sesión.
    """

    user = st.session_state.get(
        "user",
        {},
    )

    if isinstance(user, dict):
        return user

    return {}


def get_user_id() -> str:
    """
    Obtiene el UUID del usuario autenticado.
    """

    user = _current_user()

    possible_values = [
        user.get("id"),
        user.get("sub"),
    ]

    metadata = user.get(
        "user_metadata",
        {},
    )

    if isinstance(metadata, dict):
        possible_values.append(
            metadata.get("sub")
        )

    for value in possible_values:
        clean_value = str(
            value or ""
        ).strip()

        if clean_value:
            return clean_value

    raise ProfileError(
        "No se encontró el ID del usuario autenticado."
    )


def get_user_metadata() -> dict[str, Any]:
    """
    Obtiene los metadatos pequeños del usuario.
    """

    user = _current_user()

    metadata = user.get(
        "user_metadata",
        {},
    )

    if isinstance(metadata, dict):
        return metadata.copy()

    return {}


def get_profile_name() -> str:
    """
    Devuelve el nombre actual del trader.
    """

    metadata = get_user_metadata()

    possible_names = [
        metadata.get("username"),
        metadata.get("full_name"),
        metadata.get("display_name"),
        metadata.get("name"),
        metadata.get("nombre"),
        metadata.get("nombre_trader"),
        st.session_state.get("nombre_trader"),
    ]

    for value in possible_names:
        clean_value = str(
            value or ""
        ).strip()

        if clean_value:
            return clean_value

    return "Trader Pro"


def get_avatar_url() -> str:
    """
    Devuelve la URL pequeña del avatar.

    Nunca devuelve una imagen Base64.
    """

    metadata = get_user_metadata()

    possible_values = [
        metadata.get("avatar_url"),
        metadata.get("photo_url"),
        metadata.get("profile_photo_url"),
        st.session_state.get("avatar_url"),
    ]

    for value in possible_values:
        clean_value = str(
            value or ""
        ).strip()

        if (
            clean_value
            and not clean_value.startswith("data:")
            and len(clean_value) < 3000
        ):
            return clean_value

    return ""


def get_profile_capital() -> float:
    """
    Devuelve el capital actual guardado.
    """

    metadata = get_user_metadata()

    value = metadata.get(
        "capital_actual",
        st.session_state.get(
            "capital_actual",
            10000.0,
        ),
    )

    try:
        return float(
            value or 10000.0
        )

    except (TypeError, ValueError):
        return 10000.0


def get_profile_target() -> float:
    """
    Devuelve la meta de capital guardada.
    """

    metadata = get_user_metadata()

    value = metadata.get(
        "capital_meta",
        st.session_state.get(
            "capital_meta",
            15000.0,
        ),
    )

    try:
        return float(
            value or 15000.0
        )

    except (TypeError, ValueError):
        return 15000.0


# =========================================================
# RESPUESTAS HTTP
# =========================================================


def _safe_json(
    response: requests.Response,
) -> Any:
    """
    Convierte una respuesta HTTP en JSON cuando es posible.
    """

    try:
        return response.json()

    except ValueError:
        return None


def _error_message(
    response: requests.Response,
) -> str:
    """
    Extrae el mensaje de error devuelto por Supabase.
    """

    payload = _safe_json(
        response
    )

    if isinstance(payload, dict):
        for key in (
            "message",
            "msg",
            "error",
            "error_description",
            "details",
            "hint",
            "code",
        ):
            value = payload.get(
                key
            )

            if value:
                return str(value)

    text = str(
        response.text or ""
    ).strip()

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
    """
    Verifica que una petición haya sido exitosa.
    """

    if response.status_code >= 400:
        raise ProfileError(
            f"{action}. HTTP {response.status_code}: "
            f"{_error_message(response)}"
        )

    payload = _safe_json(
        response
    )

    if payload is None:
        return {}

    return payload


# =========================================================
# AVATAR
# =========================================================


def _avatar_extension(
    mime_type: str,
    filename: str,
) -> str:
    """
    Determina una extensión de imagen permitida.
    """

    clean_mime = str(
        mime_type or ""
    ).strip().lower()

    if clean_mime in ALLOWED_AVATAR_TYPES:
        return ALLOWED_AVATAR_TYPES[
            clean_mime
        ]

    suffix = Path(
        filename or ""
    ).suffix.lower().lstrip(".")

    if suffix == "jpeg":
        suffix = "jpg"

    if suffix in {
        "jpg",
        "png",
        "webp",
    }:
        return suffix

    raise ProfileError(
        "La foto debe ser JPG, PNG o WEBP."
    )


def _public_avatar_url(
    object_path: str,
) -> str:
    """
    Construye la URL pública del avatar.
    """

    encoded_path = quote(
        object_path,
        safe="/",
    )

    base_public_url = (
        f"{_base_url()}"
        f"/storage/v1/object/public/"
        f"{AVATAR_BUCKET}/"
        f"{encoded_path}"
    )

    return (
        f"{base_public_url}"
        f"?v={int(time.time())}"
    )


def upload_avatar(
    uploaded_file: Any,
) -> str:
    """
    Sube o reemplaza la foto del usuario.

    El archivo se guarda en:

    avatars/<user_id>/avatar.<ext>
    """

    if uploaded_file is None:
        raise ProfileError(
            "Selecciona una foto antes de guardar."
        )

    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        raise ProfileError(
            "La fotografía está vacía."
        )

    if len(file_bytes) > MAX_AVATAR_BYTES:
        raise ProfileError(
            "La fotografía supera el límite de 5 MB."
        )

    mime_type = str(
        getattr(
            uploaded_file,
            "type",
            "",
        )
        or ""
    ).strip().lower()

    filename = str(
        getattr(
            uploaded_file,
            "name",
            "",
        )
        or ""
    )

    extension = _avatar_extension(
        mime_type,
        filename,
    )

    if not mime_type:
        mime_type = {
            "jpg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
        }[extension]

    user_id = get_user_id()

    object_path = (
        f"{user_id}/avatar.{extension}"
    )

    encoded_path = quote(
        object_path,
        safe="/",
    )

    access_token = ensure_access_token()

    try:
        response = requests.post(
            (
                f"{_base_url()}"
                f"/storage/v1/object/"
                f"{AVATAR_BUCKET}/"
                f"{encoded_path}"
            ),
            headers={
                "apikey": _api_key(),
                "Authorization": (
                    f"Bearer {access_token}"
                ),
                "Content-Type": mime_type,
                "x-upsert": "true",
            },
            data=file_bytes,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.Timeout as exc:
        raise ProfileError(
            "Supabase tardó demasiado en subir la foto."
        ) from exc

    except requests.ConnectionError as exc:
        raise ProfileError(
            "No se pudo conectar con Supabase Storage."
        ) from exc

    except requests.RequestException as exc:
        raise ProfileError(
            f"Error al subir la fotografía: {exc}"
        ) from exc

    _validate_response(
        response,
        "No se pudo subir la fotografía",
    )

    return _public_avatar_url(
        object_path
    )


# =========================================================
# ACTUALIZAR METADATOS
# =========================================================


def _small_text(
    value: Any,
    maximum: int,
) -> str:
    """
    Limpia textos para evitar metadatos gigantes.
    """

    clean_value = str(
        value or ""
    ).strip()

    return clean_value[:maximum]


def _update_local_user(
    metadata: dict[str, Any],
) -> None:
    """
    Actualiza inmediatamente la sesión local.
    """

    user = _current_user().copy()

    user["user_metadata"] = (
        metadata.copy()
    )

    st.session_state.user = user

    st.session_state.nombre_trader = (
        metadata.get(
            "username",
            "Trader Pro",
        )
    )

    st.session_state.capital_actual = float(
        metadata.get(
            "capital_actual",
            10000.0,
        )
    )

    st.session_state.capital_meta = float(
        metadata.get(
            "capital_meta",
            15000.0,
        )
    )

    st.session_state.avatar_url = str(
        metadata.get(
            "avatar_url",
            "",
        )
        or ""
    )


def update_profile_metadata(
    *,
    trader_name: str,
    capital_actual: float,
    capital_meta: float,
    avatar_url: str = "",
) -> dict[str, Any]:
    """
    Guarda datos pequeños del perfil en Supabase Auth.

    La fotografía nunca se guarda como Base64.
    Solamente se guarda su URL pública.
    """

    clean_name = _small_text(
        trader_name,
        80,
    )

    if not clean_name:
        raise ProfileError(
            "El nombre del trader no puede estar vacío."
        )

    try:
        clean_capital = float(
            capital_actual
        )

        clean_target = float(
            capital_meta
        )

    except (TypeError, ValueError) as exc:
        raise ProfileError(
            "El capital y la meta deben ser números válidos."
        ) from exc

    if clean_capital < 0:
        raise ProfileError(
            "El capital actual no puede ser negativo."
        )

    if clean_target <= 0:
        raise ProfileError(
            "La meta de capital debe ser mayor que cero."
        )

    clean_avatar_url = _small_text(
        avatar_url,
        2500,
    )

    if clean_avatar_url.startswith(
        "data:"
    ):
        raise ProfileError(
            "La fotografía no puede guardarse como Base64."
        )

    current_metadata = get_user_metadata()

    safe_metadata = {
        "sub": _small_text(
            current_metadata.get(
                "sub",
                get_user_id(),
            ),
            80,
        ),
        "username": clean_name,
        "full_name": clean_name,
        "name": clean_name,
        "capital_actual": clean_capital,
        "capital_meta": clean_target,
    }

    if clean_avatar_url:
        safe_metadata["avatar_url"] = (
            clean_avatar_url
        )

    access_token = ensure_access_token()

    try:
        response = requests.put(
            (
                f"{_base_url()}"
                "/auth/v1/user"
            ),
            headers={
                "apikey": _api_key(),
                "Authorization": (
                    f"Bearer {access_token}"
                ),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json={
                "data": safe_metadata,
            },
            timeout=REQUEST_TIMEOUT,
        )

    except requests.Timeout as exc:
        raise ProfileError(
            "Supabase tardó demasiado en guardar el perfil."
        ) from exc

    except requests.ConnectionError as exc:
        raise ProfileError(
            "No se pudo conectar con Supabase Auth."
        ) from exc

    except requests.RequestException as exc:
        raise ProfileError(
            f"Error al guardar el perfil: {exc}"
        ) from exc

    payload = _validate_response(
        response,
        "No se pudo actualizar el perfil",
    )

    if isinstance(payload, dict):
        returned_metadata = payload.get(
            "user_metadata",
            safe_metadata,
        )

        if not isinstance(
            returned_metadata,
            dict,
        ):
            returned_metadata = safe_metadata

    else:
        returned_metadata = safe_metadata

    _update_local_user(
        returned_metadata
    )

    return returned_metadata


def save_profile(
    *,
    trader_name: str,
    capital_actual: float,
    capital_meta: float,
    uploaded_file: Any = None,
) -> dict[str, Any]:
    """
    Guarda el perfil completo.

    Si existe una foto nueva:
    1. La sube a Storage.
    2. Guarda únicamente su URL en Auth.
    """

    avatar_url = get_avatar_url()

    if uploaded_file is not None:
        avatar_url = upload_avatar(
            uploaded_file
        )

    return update_profile_metadata(
        trader_name=trader_name,
        capital_actual=capital_actual,
        capital_meta=capital_meta,
        avatar_url=avatar_url,
    )
