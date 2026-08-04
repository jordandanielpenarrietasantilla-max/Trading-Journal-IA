from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

import streamlit as st

from core.config import ADMIN_EMAIL


# =========================================================
# AXION PRIME X10 PRO
# CONTROL CENTRAL DE MEMBRESÍAS
# =========================================================


FREE_PLAN = "FREE"
TRIAL_PLAN = "TRIAL"
MONTHLY_PLAN = "PRO_MONTHLY"
ANNUAL_PLAN = "PRO_ANNUAL"
FOUNDER_PLAN = "FOUNDER"

ACTIVE_STATUS = "active"
EXPIRED_STATUS = "expired"
INACTIVE_STATUS = "inactive"


PRO_PLANS = {
    MONTHLY_PLAN,
    ANNUAL_PLAN,
    FOUNDER_PLAN,
}


@dataclass(frozen=True)
class MembershipInfo:
    """
    Estado normalizado de la membresía de un usuario.
    """

    user_id: str
    email: str
    plan: str
    status: str

    is_owner: bool
    is_pro: bool
    is_active: bool
    is_expired: bool

    started_at: dt.datetime | None
    expires_at: dt.datetime | None

    provider: str
    source: str

    label: str
    badge: str
    days_remaining: int | None


# =========================================================
# CONVERSIÓN SEGURA
# =========================================================


def _safe_dict(
    value: Any,
) -> dict[str, Any]:
    """
    Convierte un objeto compatible en diccionario.
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

    try:
        dumped = dict(
            value
        )

        if isinstance(
            dumped,
            dict,
        ):
            return dumped

    except Exception:
        pass

    return {}


def _clean_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Convierte un valor en texto limpio.
    """

    text = str(
        value
        if value is not None
        else default
    ).strip()

    return text or default


def _normalize_email(
    value: Any,
) -> str:
    """
    Normaliza un correo para comparaciones.
    """

    return _clean_text(
        value
    ).lower()


def _normalize_plan(
    value: Any,
) -> str:
    """
    Normaliza los nombres posibles de los planes.
    """

    plan = _clean_text(
        value,
        FREE_PLAN,
    ).upper()

    aliases = {
        "": FREE_PLAN,
        "FREE": FREE_PLAN,
        "GRATIS": FREE_PLAN,
        "BASIC": FREE_PLAN,

        "TRIAL": TRIAL_PLAN,
        "FREE_TRIAL": TRIAL_PLAN,

        "PRO": MONTHLY_PLAN,
        "MONTHLY": MONTHLY_PLAN,
        "MENSUAL": MONTHLY_PLAN,
        "PRO_MONTHLY": MONTHLY_PLAN,

        "ANNUAL": ANNUAL_PLAN,
        "YEARLY": ANNUAL_PLAN,
        "ANUAL": ANNUAL_PLAN,
        "PRO_ANNUAL": ANNUAL_PLAN,

        "OWNER": FOUNDER_PLAN,
        "ADMIN": FOUNDER_PLAN,
        "FOUNDER": FOUNDER_PLAN,
    }

    return aliases.get(
        plan,
        plan,
    )


def _normalize_status(
    value: Any,
) -> str:
    """
    Normaliza el estado de la suscripción.
    """

    status = _clean_text(
        value,
        INACTIVE_STATUS,
    ).lower()

    aliases = {
        "activo": ACTIVE_STATUS,
        "active": ACTIVE_STATUS,
        "approved": ACTIVE_STATUS,
        "paid": ACTIVE_STATUS,
        "completed": ACTIVE_STATUS,

        "expired": EXPIRED_STATUS,
        "vencido": EXPIRED_STATUS,

        "inactive": INACTIVE_STATUS,
        "inactivo": INACTIVE_STATUS,
        "cancelled": INACTIVE_STATUS,
        "canceled": INACTIVE_STATUS,
        "pending": INACTIVE_STATUS,
    }

    return aliases.get(
        status,
        status,
    )


# =========================================================
# FECHAS
# =========================================================


def _utc_now() -> dt.datetime:
    """
    Devuelve la fecha actual en UTC.
    """

    return dt.datetime.now(
        dt.timezone.utc
    )


def _parse_datetime(
    value: Any,
) -> dt.datetime | None:
    """
    Convierte fechas ISO, fechas SQL o timestamps
    en datetime con zona horaria UTC.
    """

    if value is None:
        return None

    if isinstance(
        value,
        dt.datetime,
    ):
        parsed = value

    elif isinstance(
        value,
        dt.date,
    ):
        parsed = dt.datetime.combine(
            value,
            dt.time.min,
        )

    else:
        text = _clean_text(
            value
        )

        if not text:
            return None

        normalized = text.replace(
            "Z",
            "+00:00",
        )

        try:
            parsed = dt.datetime.fromisoformat(
                normalized
            )

        except ValueError:
            formats = (
                "%Y-%m-%d %H:%M:%S.%f%z",
                "%Y-%m-%d %H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            )

            parsed = None

            for format_string in formats:
                try:
                    parsed = dt.datetime.strptime(
                        text,
                        format_string,
                    )

                    break

                except ValueError:
                    continue

            if parsed is None:
                return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=dt.timezone.utc
        )

    return parsed.astimezone(
        dt.timezone.utc
    )


def _calculate_days_remaining(
    expires_at: dt.datetime | None,
) -> int | None:
    """
    Calcula los días restantes del plan.
    """

    if expires_at is None:
        return None

    difference = (
        expires_at
        - _utc_now()
    )

    total_seconds = (
        difference.total_seconds()
    )

    if total_seconds <= 0:
        return 0

    seconds_per_day = 86400

    return max(
        1,
        int(
            (
                total_seconds
                + seconds_per_day
                - 1
            )
            // seconds_per_day
        ),
    )


# =========================================================
# USUARIO Y METADATOS
# =========================================================


def get_session_user() -> dict[str, Any]:
    """
    Devuelve el usuario almacenado en la sesión.
    """

    return _safe_dict(
        st.session_state.get(
            "user",
            {},
        )
    )


def get_user_metadata(
    user: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Devuelve los metadatos del usuario.

    Soporta distintas formas de respuesta de Supabase.
    """

    clean_user = (
        _safe_dict(user)
        if user is not None
        else get_session_user()
    )

    possible_metadata = (
        clean_user.get(
            "user_metadata"
        ),
        clean_user.get(
            "raw_user_meta_data"
        ),
        clean_user.get(
            "metadata"
        ),
    )

    for metadata in possible_metadata:
        clean_metadata = _safe_dict(
            metadata
        )

        if clean_metadata:
            return clean_metadata

    return {}


def get_user_id(
    user: dict[str, Any] | None = None,
) -> str:
    """
    Obtiene el UUID del usuario.
    """

    clean_user = (
        _safe_dict(user)
        if user is not None
        else get_session_user()
    )

    metadata = get_user_metadata(
        clean_user
    )

    possible_values = (
        clean_user.get(
            "id"
        ),
        clean_user.get(
            "sub"
        ),
        metadata.get(
            "sub"
        ),
        metadata.get(
            "user_id"
        ),
    )

    for value in possible_values:
        clean_value = _clean_text(
            value
        )

        if clean_value:
            return clean_value

    return ""


def get_user_email(
    user: dict[str, Any] | None = None,
) -> str:
    """
    Obtiene el correo del usuario.
    """

    clean_user = (
        _safe_dict(user)
        if user is not None
        else get_session_user()
    )

    metadata = get_user_metadata(
        clean_user
    )

    return _normalize_email(
        clean_user.get(
            "email"
        )
        or metadata.get(
            "email"
        )
    )


# =========================================================
# PROPIETARIO
# =========================================================


def is_owner_email(
    email: str,
) -> bool:
    """
    Comprueba si el correo pertenece al propietario.
    """

    clean_email = _normalize_email(
        email
    )

    clean_admin = _normalize_email(
        ADMIN_EMAIL
    )

    return bool(
        clean_email
        and clean_admin
        and clean_email == clean_admin
    )


# =========================================================
# LECTURA DE MEMBRESÍA
# =========================================================


def get_membership_info(
    user: dict[str, Any] | None = None,
) -> MembershipInfo:
    """
    Construye el estado completo de la membresía.

    Prioridad de datos:
    1. Propietario de la aplicación.
    2. Plan guardado en user_metadata.
    3. Estado y fecha de vencimiento.
    """

    clean_user = (
        _safe_dict(user)
        if user is not None
        else get_session_user()
    )

    metadata = get_user_metadata(
        clean_user
    )

    user_id = get_user_id(
        clean_user
    )

    email = get_user_email(
        clean_user
    )

    owner = is_owner_email(
        email
    )

    plan = _normalize_plan(
        metadata.get(
            "plan"
        )
        or metadata.get(
            "plan_code"
        )
        or metadata.get(
            "subscription_plan"
        )
        or metadata.get(
            "membership_plan"
        )
    )

    status = _normalize_status(
        metadata.get(
            "membership_status"
        )
        or metadata.get(
            "subscription_status"
        )
        or metadata.get(
            "status"
        )
    )

    started_at = _parse_datetime(
        metadata.get(
            "plan_started_at"
        )
        or metadata.get(
            "subscription_started_at"
        )
        or metadata.get(
            "started_at"
        )
    )

    expires_at = _parse_datetime(
        metadata.get(
            "plan_expires_at"
        )
        or metadata.get(
            "subscription_expires_at"
        )
        or metadata.get(
            "expires_at"
        )
    )

    provider = _clean_text(
        metadata.get(
            "payment_provider"
        )
        or metadata.get(
            "provider"
        )
    )

    source = _clean_text(
        metadata.get(
            "plan_source"
        )
        or metadata.get(
            "source"
        )
        or provider
    )

    now = _utc_now()

    expired_by_date = bool(
        expires_at is not None
        and expires_at <= now
    )

    if owner:
        plan = FOUNDER_PLAN
        status = ACTIVE_STATUS
        expired_by_date = False
        expires_at = None

    is_pro_plan = (
        plan in PRO_PLANS
    )

    active_status = (
        status == ACTIVE_STATUS
    )

    is_active = bool(
        owner
        or (
            is_pro_plan
            and active_status
            and not expired_by_date
        )
    )

    is_expired = bool(
        not owner
        and is_pro_plan
        and (
            expired_by_date
            or status == EXPIRED_STATUS
        )
    )

    is_pro = bool(
        owner
        or is_active
    )

    if owner:
        label = "FOUNDER · ACCESO TOTAL"
        badge = "FOUNDER"

    elif is_active and plan == MONTHLY_PLAN:
        label = "PRO MENSUAL"
        badge = "PRO"

    elif is_active and plan == ANNUAL_PLAN:
        label = "PRO ANUAL"
        badge = "PRO"

    elif is_expired:
        label = "PLAN VENCIDO"
        badge = "EXPIRED"

    elif plan == TRIAL_PLAN:
        label = "TRIAL"
        badge = "TRIAL"

    else:
        label = "PLAN FREE"
        badge = "FREE"

    days_remaining = _calculate_days_remaining(
        expires_at
    )

    return MembershipInfo(
        user_id=user_id,
        email=email,
        plan=plan,
        status=status,

        is_owner=owner,
        is_pro=is_pro,
        is_active=is_active,
        is_expired=is_expired,

        started_at=started_at,
        expires_at=expires_at,

        provider=provider,
        source=source,

        label=label,
        badge=badge,
        days_remaining=days_remaining,
    )


# =========================================================
# FUNCIONES RÁPIDAS
# =========================================================


def user_has_pro_access(
    user: dict[str, Any] | None = None,
) -> bool:
    """
    Devuelve True cuando el usuario tiene acceso PRO activo.
    """

    return get_membership_info(
        user
    ).is_pro


def user_membership_expired(
    user: dict[str, Any] | None = None,
) -> bool:
    """
    Devuelve True cuando el plan ya venció.
    """

    return get_membership_info(
        user
    ).is_expired


def get_membership_label(
    user: dict[str, Any] | None = None,
) -> str:
    """
    Devuelve el texto visible del plan.
    """

    return get_membership_info(
        user
    ).label


def get_membership_badge(
    user: dict[str, Any] | None = None,
) -> str:
    """
    Devuelve una etiqueta corta del plan.
    """

    return get_membership_info(
        user
    ).badge


# =========================================================
# CONTROL DE ACCESO
# =========================================================


def require_pro_access(
    *,
    feature_name: str = "esta función",
    show_subscription_hint: bool = True,
) -> bool:
    """
    Comprueba el acceso PRO y muestra un aviso si no está activo.

    Uso:

        if not require_pro_access(
            feature_name="Auditoría con IA"
        ):
            return
    """

    membership = get_membership_info()

    if membership.is_pro:
        return True

    if membership.is_expired:
        st.error(
            f"Tu plan PRO venció. Renueva tu membresía "
            f"para utilizar {feature_name}."
        )

    else:
        st.warning(
            f"{feature_name} requiere una membresía "
            "AXION PRIME PRO activa."
        )

    if show_subscription_hint:
        st.info(
            "Puedes activar o renovar el plan desde "
            "la sección AXION PRIME PRO."
        )

    return False


# =========================================================
# DATOS PARA LA INTERFAZ
# =========================================================


def membership_to_dict(
    user: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Convierte MembershipInfo en un diccionario
    fácil de utilizar en la interfaz.
    """

    membership = get_membership_info(
        user
    )

    return {
        "user_id":
            membership.user_id,

        "email":
            membership.email,

        "plan":
            membership.plan,

        "status":
            membership.status,

        "is_owner":
            membership.is_owner,

        "is_pro":
            membership.is_pro,

        "is_active":
            membership.is_active,

        "is_expired":
            membership.is_expired,

        "started_at":
            (
                membership.started_at.isoformat()
                if membership.started_at
                else ""
            ),

        "expires_at":
            (
                membership.expires_at.isoformat()
                if membership.expires_at
                else ""
            ),

        "provider":
            membership.provider,

        "source":
            membership.source,

        "label":
            membership.label,

        "badge":
            membership.badge,

        "days_remaining":
            membership.days_remaining,
    }
