from __future__ import annotations

import io
import time
from typing import Any
from uuid import uuid4

import streamlit as st
from PIL import Image

from core.api import get_supabase_client
from ui_v2.theme import apply_v2_theme


# =========================================================
# AXION PRIME V2
# PERFIL Y CONFIGURACIÓN
# =========================================================


PROFILE_CSS = """
<style>

.v2-profile-hero {
    display: grid;
    grid-template-columns: 160px 1fr auto;
    gap: 22px;
    align-items: center;

    padding: 24px;
    margin-bottom: 18px;

    background:
        radial-gradient(
            circle at 85% 20%,
            rgba(139, 77, 255, 0.18),
            transparent 32%
        ),
        linear-gradient(
            145deg,
            rgba(7, 16, 35, 0.98),
            rgba(5, 10, 25, 0.98)
        );

    border:
        1px solid rgba(62, 112, 184, 0.35);
    border-radius: 22px;

    box-shadow:
        0 24px 70px rgba(0, 0, 0, 0.36);
}


.v2-profile-avatar-ring {
    width: 132px;
    height: 132px;

    display: grid;
    place-items: center;

    padding: 4px;

    border-radius: 50%;

    background:
        conic-gradient(
            var(--v2-cyan),
            var(--v2-blue),
            var(--v2-purple),
            var(--v2-red),
            var(--v2-cyan)
        );

    box-shadow:
        0 0 34px rgba(25, 228, 255, 0.24);
}


.v2-profile-avatar {
    width: 124px;
    height: 124px;

    display: grid;
    place-items: center;

    overflow: hidden;

    color: white;
    font-size: 30px;
    font-weight: 950;

    background:
        linear-gradient(
            145deg,
            #0b152c,
            #090d1e
        );

    border:
        4px solid #050a18;
    border-radius: 50%;
}


.v2-profile-avatar img {
    width: 100%;
    height: 100%;

    object-fit: cover;
    object-position: center;
}


.v2-profile-copy h1 {
    margin: 0;

    color: var(--v2-white);

    font-size: clamp(30px, 3vw, 46px);
    line-height: 1;
    font-weight: 950;
    letter-spacing: -1.8px;
}


.v2-profile-email {
    margin-top: 8px;

    color: var(--v2-muted);

    font-size: 11px;
}


.v2-profile-badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;

    margin-top: 14px;
}


.v2-profile-badge {
    padding: 6px 10px;

    font-size: 7px;
    font-weight: 950;
    letter-spacing: 1px;

    border-radius: 999px;
}


.v2-profile-founder {
    color: #fff;
    background: linear-gradient(90deg, #8b4dff, #b44cff);
}


.v2-profile-secure {
    color: var(--v2-green);
    background: rgba(0, 245, 138, 0.08);
    border: 1px solid rgba(0, 245, 138, 0.26);
}


.v2-profile-score {
    min-width: 150px;

    padding: 16px;

    text-align: center;

    background: rgba(4, 10, 25, 0.74);
    border: 1px solid rgba(73, 104, 171, 0.28);
    border-radius: 16px;
}


.v2-profile-score strong {
    display: block;

    color: var(--v2-cyan);

    font-size: 36px;
    font-weight: 950;
}


.v2-profile-score span {
    display: block;

    margin-top: 5px;

    color: var(--v2-dim);

    font-size: 7px;
    font-weight: 900;
    letter-spacing: 1.2px;
}


.v2-profile-panel {
    padding: 18px;

    background:
        linear-gradient(
            145deg,
            rgba(7, 15, 33, 0.96),
            rgba(4, 9, 23, 0.96)
        );

    border:
        1px solid rgba(66, 98, 160, 0.30);
    border-radius: 18px;
}


.v2-profile-panel h3 {
    margin: 0 0 6px;

    color: var(--v2-white);

    font-size: 16px;
}


.v2-profile-panel p {
    margin: 0 0 16px;

    color: var(--v2-muted);

    font-size: 10px;
    line-height: 1.5;
}


.v2-profile-stat-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;

    margin-top: 18px;
}


.v2-profile-stat {
    padding: 14px;

    text-align: center;

    background: rgba(4, 10, 25, 0.72);
    border: 1px solid rgba(72, 99, 162, 0.24);
    border-radius: 13px;
}


.v2-profile-stat strong {
    display: block;

    color: var(--v2-cyan);

    font-size: 18px;
}


.v2-profile-stat span {
    display: block;

    margin-top: 5px;

    color: var(--v2-dim);

    font-size: 7px;
}


@media (max-width: 900px) {

    .v2-profile-hero {
        grid-template-columns: 1fr;
        text-align: center;
    }

    .v2-profile-avatar-ring {
        margin: auto;
    }

    .v2-profile-badges {
        justify-content: center;
    }

    .v2-profile-score {
        max-width: 220px;
        margin: auto;
    }
}

</style>
"""


# =========================================================
# UTILIDADES
# =========================================================


def _value(
    obj: Any,
    key: str,
    default: Any = None,
) -> Any:
    if obj is None:
        return default

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


def _metadata(
    user: Any,
) -> dict[str, Any]:
    data = _value(
        user,
        "user_metadata",
        {},
    )

    return data if isinstance(data, dict) else {}


def _initials(
    name: str,
) -> str:
    pieces = [
        part
        for part in name.split()
        if part
    ]

    if not pieces:
        return "TP"

    if len(pieces) == 1:
        return pieces[0][:2].upper()

    return (
        pieces[0][0]
        + pieces[-1][0]
    ).upper()


def _safe_float(
    value: Any,
    default: float,
) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _normalize_image(
    uploaded_file: Any,
) -> tuple[bytes, str]:
    image = Image.open(uploaded_file)

    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    image.thumbnail((1200, 1200))

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=88,
        optimize=True,
    )

    return (
        buffer.getvalue(),
        "image/jpeg",
    )


def _upload_avatar(
    uploaded_file: Any,
    user_id: str,
) -> str:
    image_bytes, content_type = (
        _normalize_image(uploaded_file)
    )

    client = get_supabase_client()

    path = (
        f"{user_id}/avatar-"
        f"{int(time.time())}-"
        f"{uuid4().hex[:8]}.jpg"
    )

    client.storage.from_("avatars").upload(
        path,
        image_bytes,
        {
            "content-type": content_type,
            "upsert": "true",
        },
    )

    public_result = (
        client.storage
        .from_("avatars")
        .get_public_url(path)
    )

    if isinstance(public_result, str):
        return public_result

    public_url = _value(
        public_result,
        "public_url",
        "",
    )

    if public_url:
        return str(public_url)

    data = _value(
        public_result,
        "data",
        {},
    )

    if isinstance(data, dict):
        return str(
            data.get("publicUrl")
            or data.get("public_url")
            or ""
        )

    return ""


def _update_user_metadata(
    new_metadata: dict[str, Any],
) -> Any:
    client = get_supabase_client()

    result = client.auth.update_user(
        {
            "data": new_metadata,
        }
    )

    user = _value(
        result,
        "user",
        None,
    )

    if user is None:
        raise RuntimeError(
            "Supabase no devolvió el usuario actualizado."
        )

    st.session_state.user = user

    return user


# =========================================================
# CABECERA
# =========================================================


def _render_profile_header(
    *,
    name: str,
    email: str,
    avatar_url: str,
    score: int,
) -> None:
    avatar_html = (
        f"""
        <div class="v2-profile-avatar">
            <img src="{avatar_url}" alt="Avatar" />
        </div>
        """
        if avatar_url
        else f"""
        <div class="v2-profile-avatar">
            {_initials(name)}
        </div>
        """
    )

    st.html(
        f"""
        <section class="v2-profile-hero">

            <div class="v2-profile-avatar-ring">
                {avatar_html}
            </div>

            <div class="v2-profile-copy">

                <div class="v2-eyebrow">
                    AXION IDENTITY CORE
                </div>

                <h1>
                    {name}
                </h1>

                <div class="v2-profile-email">
                    {email}
                </div>

                <div class="v2-profile-badges">

                    <span class="
                        v2-profile-badge
                        v2-profile-founder
                    ">
                        FOUNDER
                    </span>

                    <span class="
                        v2-profile-badge
                        v2-profile-secure
                    ">
                        PERFIL PROTEGIDO
                    </span>

                </div>

            </div>

            <div class="v2-profile-score">

                <strong>
                    {score}
                </strong>

                <span>
                    AXION PROFILE SCORE
                </span>

            </div>

        </section>
        """
    )


# =========================================================
# PANTALLA PRINCIPAL
# =========================================================


def render_v2_profile() -> None:
    """
    Perfil premium de AXION PRIME V2.
    """

    apply_v2_theme()

    st.markdown(
        PROFILE_CSS,
        unsafe_allow_html=True,
    )

    user = st.session_state.get(
        "user",
        {}
    )

    metadata = _metadata(user)

    email = str(
        _value(
            user,
            "email",
            "",
        )
        or ""
    )

    name = str(
        metadata.get("username")
        or metadata.get("full_name")
        or metadata.get("name")
        or st.session_state.get(
            "nombre_trader",
            "Trader Pro",
        )
    )

    avatar_url = str(
        metadata.get("avatar_url")
        or metadata.get("photo_url")
        or ""
    )

    capital_actual = _safe_float(
        metadata.get(
            "capital_actual",
            st.session_state.get(
                "capital_actual",
                10000.0,
            ),
        ),
        10000.0,
    )

    capital_meta = _safe_float(
        metadata.get(
            "capital_meta",
            st.session_state.get(
                "capital_meta",
                15000.0,
            ),
        ),
        15000.0,
    )

    reglas = str(
        metadata.get(
            "reglas_disciplina",
            st.session_state.get(
                "reglas_disciplina",
                "",
            ),
        )
        or ""
    )

    score = 85

    _render_profile_header(
        name=name,
        email=email,
        avatar_url=avatar_url,
        score=score,
    )

    left, right = st.columns(
        [
            1,
            1,
        ],
        gap="medium",
    )

    with left:
        st.html(
            """
            <section class="v2-profile-panel">
                <h3>Identidad del trader</h3>
                <p>
                    Personaliza tu nombre y fotografía.
                    La imagen se guarda en Supabase Storage.
                </p>
            </section>
            """
        )

        new_name = st.text_input(
            "Nombre del trader",
            value=name,
            key="v2_profile_name",
        )

        uploaded_avatar = st.file_uploader(
            "Foto de perfil",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
            ],
            key="v2_profile_avatar",
        )

        if uploaded_avatar is not None:
            st.image(
                uploaded_avatar,
                width=220,
            )

        if st.button(
            "💾 Guardar identidad",
            use_container_width=True,
            key="v2_profile_save_identity",
        ):
            try:
                user_id = str(
                    _value(
                        user,
                        "id",
                        "",
                    )
                    or ""
                )

                if not user_id:
                    raise RuntimeError(
                        "No se pudo obtener el ID del usuario."
                    )

                new_avatar_url = avatar_url

                if uploaded_avatar is not None:
                    with st.spinner(
                        "Subiendo fotografía..."
                    ):
                        new_avatar_url = (
                            _upload_avatar(
                                uploaded_avatar,
                                user_id,
                            )
                        )

                    if not new_avatar_url:
                        raise RuntimeError(
                            "Supabase no devolvió la URL "
                            "pública del avatar."
                        )

                updated_metadata = dict(metadata)

                updated_metadata.update(
                    {
                        "username": (
                            new_name.strip()
                            or "Trader Pro"
                        ),
                        "full_name": (
                            new_name.strip()
                            or "Trader Pro"
                        ),
                        "name": (
                            new_name.strip()
                            or "Trader Pro"
                        ),
                        "avatar_url": new_avatar_url,
                    }
                )

                _update_user_metadata(
                    updated_metadata
                )

                st.session_state.nombre_trader = (
                    new_name.strip()
                    or "Trader Pro"
                )

                st.success(
                    "Identidad actualizada correctamente."
                )

                st.rerun()

            except Exception as exc:
                st.error(
                    f"No se pudo actualizar el perfil: {exc}"
                )

    with right:
        st.html(
            """
            <section class="v2-profile-panel">
                <h3>Objetivos y disciplina</h3>
                <p>
                    Define tu capital, meta y reglas personales.
                </p>
            </section>
            """
        )

        new_capital = st.number_input(
            "Capital actual",
            min_value=0.0,
            value=float(capital_actual),
            step=100.0,
            key="v2_profile_capital",
        )

        new_target = st.number_input(
            "Meta de capital",
            min_value=0.0,
            value=float(capital_meta),
            step=500.0,
            key="v2_profile_target",
        )

        new_rules = st.text_area(
            "Reglas de disciplina",
            value=reglas,
            height=210,
            key="v2_profile_rules",
        )

        if st.button(
            "💾 Guardar objetivos",
            use_container_width=True,
            key="v2_profile_save_goals",
        ):
            try:
                updated_metadata = dict(metadata)

                updated_metadata.update(
                    {
                        "capital_actual": float(new_capital),
                        "capital_meta": float(new_target),
                        "reglas_disciplina": new_rules,
                    }
                )

                _update_user_metadata(
                    updated_metadata
                )

                st.session_state.capital_actual = float(
                    new_capital
                )

                st.session_state.capital_meta = float(
                    new_target
                )

                st.session_state.reglas_disciplina = (
                    new_rules
                )

                st.success(
                    "Objetivos guardados correctamente."
                )

                st.rerun()

            except Exception as exc:
                st.error(
                    f"No se pudieron guardar los objetivos: "
                    f"{exc}"
                )

    progress = (
        capital_actual
        / capital_meta
        * 100
        if capital_meta > 0
        else 0.0
    )

    progress = max(
        0.0,
        min(progress, 100.0),
    )

    st.html(
        f"""
        <div class="v2-profile-stat-grid">

            <div class="v2-profile-stat">
                <strong>
                    ${capital_actual:,.0f}
                </strong>
                <span>
                    CAPITAL ACTUAL
                </span>
            </div>

            <div class="v2-profile-stat">
                <strong>
                    ${capital_meta:,.0f}
                </strong>
                <span>
                    META DE CAPITAL
                </span>
            </div>

            <div class="v2-profile-stat">
                <strong>
                    {progress:.1f}%
                </strong>
                <span>
                    PROGRESO DE LA META
                </span>
            </div>

        </div>
        """
    )
