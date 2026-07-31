from __future__ import annotations

import time
from typing import Any

import requests
import streamlit as st

from core.config import SUPABASE_KEY, SUPABASE_URL


# =========================================================
# AXION PRIME X10 PRO
# CONEXIÓN REST CON SUPABASE
# =========================================================


class ApiError(RuntimeError):
    """
    Error controlado para mostrar mensajes claros
    cuando Supabase rechaza una petición.
    """

    pass


# =========================================================
# CABECERAS
# =========================================================

def _build_headers(
    access_token: str = "",
    prefer: str = "",
) -> dict[str, str]:

    headers = {
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
        "Connection": "close",
    }

    if access_token:

        headers["Authorization"] = (
            f"Bearer {access_token}"
        )

    if prefer:

        headers["Prefer"] = prefer

    return headers


# =========================================================
# PETICIÓN GENERAL CON REINTENTOS
# =========================================================

def _request(
    method: str,
    url: str,
    *,
    access_token: str = "",
    json_body: Any = None,
    params: dict[str, Any] | None = None,
    prefer: str = "",
    timeout: int = 45,
) -> requests.Response:

    last_error: Exception | None = None

    for attempt in range(3):

        try:

            response = requests.request(
                method=method,
                url=url,
                headers=_build_headers(
                    access_token=access_token,
                    prefer=prefer,
                ),
                json=json_body,
                params=params,
                timeout=timeout,
            )

            if response.status_code >= 400:

                detail = response.text[:1500]

                raise ApiError(
                    f"Supabase HTTP "
                    f"{response.status_code}: "
                    f"{detail}"
                )

            return response

        except ApiError:

            raise

        except (
            requests.ConnectionError,
            requests.Timeout,
        ) as exc:

            last_error = exc

            if attempt < 2:

                time.sleep(
                    1 + attempt
                )

    raise ApiError(
        "No se pudo conectar con Supabase "
        f"después de 3 intentos: {last_error}"
    )


# =========================================================
# INICIAR SESIÓN
# =========================================================

def sign_in(
    email: str,
    password: str,
) -> dict[str, Any]:

    email = email.strip().lower()

    if not email or not password:

        raise ApiError(
            "Completa el correo y la contraseña."
        )

    response = _request(
        "POST",
        f"{SUPABASE_URL}/auth/v1/token",
        params={
            "grant_type": "password"
        },
        json_body={
            "email": email,
            "password": password,
        },
        timeout=45,
    )

    payload = response.json()

    if not payload.get(
        "access_token"
    ):

        raise ApiError(
            "Supabase no devolvió un token "
            "de acceso."
        )

    return payload


# =========================================================
# REGISTRAR USUARIO
# =========================================================

def sign_up(
    email: str,
    password: str,
) -> dict[str, Any]:

    email = email.strip().lower()

    if not email or not password:

        raise ApiError(
            "Completa el correo y la contraseña."
        )

    if len(password) < 6:

        raise ApiError(
            "La contraseña debe tener "
            "al menos 6 caracteres."
        )

    response = _request(
        "POST",
        f"{SUPABASE_URL}/auth/v1/signup",
        json_body={
            "email": email,
            "password": password,
        },
        timeout=45,
    )

    return response.json()


# =========================================================
# RECUPERAR CONTRASEÑA
# =========================================================

def reset_password(
    email: str,
    redirect_to: str = "",
) -> None:

    email = email.strip().lower()

    if not email:

        raise ApiError(
            "Introduce el correo registrado."
        )

    params = {}

    if redirect_to:

        params[
            "redirect_to"
        ] = redirect_to

    _request(
        "POST",
        f"{SUPABASE_URL}/auth/v1/recover",
        json_body={
            "email": email
        },
        params=params,
        timeout=45,
    )


# =========================================================
# RENOVAR SESIÓN
# =========================================================

def refresh_session(
    refresh_token: str,
) -> dict[str, Any]:

    if not refresh_token:

        raise ApiError(
            "No existe refresh_token."
        )

    response = _request(
        "POST",
        f"{SUPABASE_URL}/auth/v1/token",
        params={
            "grant_type":
                "refresh_token"
        },
        json_body={
            "refresh_token":
                refresh_token
        },
        timeout=45,
    )

    payload = response.json()

    if not payload.get(
        "access_token"
    ):

        raise ApiError(
            "No se pudo renovar la sesión."
        )

    return payload


# =========================================================
# OBTENER TOKEN ACTIVO
# =========================================================

def ensure_access_token() -> str:

    access_token = (
        st.session_state.get(
            "access_token",
            "",
        )
        or ""
    )

    if access_token:

        return access_token

    refresh_token = (
        st.session_state.get(
            "refresh_token",
            "",
        )
        or ""
    )

    if not refresh_token:

        raise ApiError(
            "La sesión no tiene tokens. "
            "Cierra sesión y vuelve a ingresar."
        )

    payload = refresh_session(
        refresh_token
    )

    st.session_state.access_token = (
        payload.get(
            "access_token",
            "",
        )
    )

    st.session_state.refresh_token = (
        payload.get(
            "refresh_token",
            refresh_token,
        )
    )

    if payload.get("user"):

        st.session_state.user = (
            payload["user"]
        )

    return (
        st.session_state.access_token
    )


# =========================================================
# CARGAR TRADES
# =========================================================

def list_trades() -> list[dict[str, Any]]:

    access_token = (
        ensure_access_token()
    )

    response = _request(
        "GET",
        f"{SUPABASE_URL}/rest/v1/trades",
        access_token=access_token,
        params={
            "select": "*",
            "order":
                "fecha.desc,created_at.desc",
        },
        timeout=45,
    )

    payload = response.json()

    if not isinstance(
        payload,
        list,
    ):

        raise ApiError(
            "Supabase devolvió un formato "
            "inesperado al cargar trades."
        )

    return payload


# =========================================================
# GUARDAR TRADE CON RPC
# =========================================================

def save_trade_rpc(
    trade_data: dict[str, Any],
) -> dict[str, Any]:

    access_token = (
        ensure_access_token()
    )

    rpc_payload = {

        "p_fecha":
            trade_data.get("fecha"),

        "p_par":
            trade_data.get("par"),

        "p_direccion":
            trade_data.get(
                "direccion"
            ),

        "p_precio_entrada":
            trade_data.get(
                "precio_entrada"
            ),

        "p_stop_loss":
            trade_data.get(
                "stop_loss"
            ),

        "p_take_profit":
            trade_data.get(
                "take_profit"
            ),

        "p_rr":
            trade_data.get("rr"),

        "p_timeframe":
            trade_data.get(
                "timeframe"
            ),

        "p_resultado":
            trade_data.get(
                "resultado"
            ),

        "p_emocion":
            trade_data.get(
                "emocion"
            ),

        "p_notas_emocionales":
            trade_data.get(
                "notas_emocionales"
            ),

        "p_beneficio_usd":
            trade_data.get(
                "beneficio_usd",
                0,
            ),

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

    response = _request(
        "POST",
        (
            f"{SUPABASE_URL}"
            "/rest/v1/rpc/"
            "axion_save_trade"
        ),
        access_token=access_token,
        json_body=rpc_payload,
        timeout=90,
    )

    payload = response.json()

    if isinstance(
        payload,
        list,
    ) and payload:

        payload = payload[0]

    if not isinstance(
        payload,
        dict,
    ):

        raise ApiError(
            "La función de guardado no "
            "devolvió un objeto válido."
        )

    trade_id = payload.get(
        "id"
    )

    if not trade_id:

        raise ApiError(
            "Supabase respondió, pero no "
            "confirmó el ID del trade."
        )

    # Verificación real:
    # consulta inmediatamente el trade creado.

    verify_response = _request(
        "GET",
        f"{SUPABASE_URL}/rest/v1/trades",
        access_token=access_token,
        params={
            "id":
                f"eq.{trade_id}",
            "select":
                "id,user_id,fecha,par,"
                "beneficio_usd",
        },
        timeout=45,
    )

    verified_rows = (
        verify_response.json()
    )

    if not verified_rows:

        raise ApiError(
            "Supabase creó un ID, pero "
            "el trade no pudo verificarse."
        )

    return payload


# =========================================================
# ACTUALIZAR TRADE
# =========================================================

def update_trade(
    trade_id: str,
    trade_data: dict[str, Any],
) -> dict[str, Any]:

    if not trade_id:

        raise ApiError(
            "Falta el ID del trade."
        )

    access_token = (
        ensure_access_token()
    )

    response = _request(
        "PATCH",
        f"{SUPABASE_URL}/rest/v1/trades",
        access_token=access_token,
        params={
            "id":
                f"eq.{trade_id}"
        },
        json_body=trade_data,
        prefer="return=representation",
        timeout=60,
    )

    rows = response.json()

    if not rows:

        raise ApiError(
            "Supabase no confirmó "
            "la actualización."
        )

    return rows[0]


# =========================================================
# ELIMINAR TRADE
# =========================================================

def delete_trade(
    trade_id: str,
) -> None:

    if not trade_id:

        raise ApiError(
            "Falta el ID del trade."
        )

    access_token = (
        ensure_access_token()
    )

    _request(
        "DELETE",
        f"{SUPABASE_URL}/rest/v1/trades",
        access_token=access_token,
        params={
            "id":
                f"eq.{trade_id}"
        },
        timeout=45,
    )


# =========================================================
# COMPROBAR CONEXIÓN
# =========================================================

def test_connection() -> bool:

    try:

        _request(
            "GET",
            f"{SUPABASE_URL}/rest/v1/",
            timeout=20,
        )

        return True

    except Exception:

        return False
