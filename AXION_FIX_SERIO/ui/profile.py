from __future__ import annotations

from typing import Any

import streamlit as st

from core.profile import (
    ProfileError,
    get_avatar_url,
    get_profile_capital,
    get_profile_name,
    get_profile_target,
    save_profile,
)


# =========================================================
# AXION PRIME X10 PRO
# PANTALLA MODIFICAR PERFIL
# =========================================================


def _safe_float(
    value: Any,
    default: float,
) -> float:
    """
    Convierte un valor en número sin romper la aplicación.
    """

    try:
        return float(
            value
        )

    except (TypeError, ValueError):
        return default


def _initials(
    name: str,
) -> str:
    """
    Genera iniciales para mostrar cuando no hay fotografía.
    """

    words = [
        word
        for word in str(name).split()
        if word
    ]

    if not words:
        return "AX"

    if len(words) == 1:
        return words[0][:2].upper()

    return (
        words[0][0]
        + words[-1][0]
    ).upper()


def _render_header() -> None:
    """
    Encabezado de la pantalla de perfil.
    """

    st.html(
        """
        <section class="ax-profile-page-header">
            <div>
                <div class="ax-profile-page-eyebrow">
                    AXION PRIME · CONFIGURACIÓN PERSONAL
                </div>

                <h1>
                    Modificar perfil
                </h1>

                <p>
                    Personaliza tu identidad, fotografía y objetivos
                    de capital sin comprometer la seguridad de tu cuenta.
                </p>
            </div>

            <div class="ax-profile-page-badge">
                PERFIL SEGURO
            </div>
        </section>
        """
    )


def _render_current_avatar(
    avatar_url: str,
    trader_name: str,
) -> None:
    """
    Muestra la foto actual o las iniciales.
    """

    if avatar_url:
        st.html(
            f"""
            <div class="ax-profile-editor-avatar">
                <img
                    src="{avatar_url}"
                    alt="Foto actual del perfil"
                >
            </div>
            """
        )

    else:
        initials = _initials(
            trader_name
        )

        st.html(
            f"""
            <div class="
                ax-profile-editor-avatar
                ax-profile-editor-avatar-fallback
            ">
                {initials}
            </div>
            """
        )


def _render_security_notice() -> None:
    """
    Explica cómo se guarda la imagen.
    """

    st.html(
        """
        <div class="ax-profile-security-card">
            <div class="ax-profile-security-icon">
                🔐
            </div>

            <div>
                <strong>
                    Fotografía almacenada de forma segura
                </strong>

                <p>
                    La imagen se guarda en Supabase Storage.
                    En tu perfil solamente se almacena una URL pequeña,
                    evitando que el token de sesión vuelva a crecer.
                </p>
            </div>
        </div>
        """
    )


def _render_profile_summary(
    trader_name: str,
    capital_actual: float,
    capital_meta: float,
) -> None:
    """
    Muestra un resumen de los datos actuales.
    """

    progress = (
        capital_actual
        / capital_meta
        * 100
        if capital_meta > 0
        else 0.0
    )

    progress = min(
        100.0,
        max(
            0.0,
            progress,
        ),
    )

    st.html(
        f"""
        <div class="ax-profile-summary-card">
            <div class="ax-profile-summary-label">
                PERFIL ACTUAL
            </div>

            <div class="ax-profile-summary-name">
                {trader_name}
            </div>

            <div class="ax-profile-summary-grid">
                <div>
                    <span>CAPITAL ACTUAL</span>
                    <strong>${capital_actual:,.2f}</strong>
                </div>

                <div>
                    <span>META DE CAPITAL</span>
                    <strong>${capital_meta:,.2f}</strong>
                </div>
            </div>

            <div class="ax-profile-summary-progress">
                <div style="width:{progress:.1f}%"></div>
            </div>

            <div class="ax-profile-summary-progress-label">
                {progress:.1f}% de la meta
            </div>
        </div>
        """
    )


def _save_profile_changes(
    *,
    trader_name: str,
    capital_actual: float,
    capital_meta: float,
    uploaded_file: Any,
) -> None:
    """
    Guarda los cambios del perfil y actualiza la aplicación.
    """

    clean_name = str(
        trader_name or ""
    ).strip()

    if not clean_name:
        st.warning(
            "Escribe el nombre del trader."
        )
        return

    if capital_actual < 0:
        st.warning(
            "El capital actual no puede ser negativo."
        )
        return

    if capital_meta <= 0:
        st.warning(
            "La meta debe ser mayor que cero."
        )
        return

    try:
        with st.spinner(
            "Guardando perfil y fotografía..."
        ):
            metadata = save_profile(
                trader_name=clean_name,
                capital_actual=capital_actual,
                capital_meta=capital_meta,
                uploaded_file=uploaded_file,
            )

        st.success(
            "Perfil actualizado correctamente."
        )

        st.session_state.nombre_trader = str(
            metadata.get(
                "username",
                clean_name,
            )
            or clean_name
        )

        st.session_state.capital_actual = _safe_float(
            metadata.get(
                "capital_actual",
                capital_actual,
            ),
            capital_actual,
        )

        st.session_state.capital_meta = _safe_float(
            metadata.get(
                "capital_meta",
                capital_meta,
            ),
            capital_meta,
        )

        st.session_state.avatar_url = str(
            metadata.get(
                "avatar_url",
                "",
            )
            or ""
        )

        st.session_state.page = "Dashboard"

        st.rerun()

    except ProfileError as exc:
        st.error(
            str(exc)
        )

    except Exception as exc:
        st.error(
            "No se pudo actualizar el perfil."
        )

        with st.expander(
            "Ver detalle técnico",
            expanded=False,
        ):
            st.code(
                str(exc),
                language="text",
            )


def render_profile() -> None:
    """
    Pantalla completa para modificar el perfil.
    """

    trader_name = get_profile_name()

    avatar_url = get_avatar_url()

    capital_actual = get_profile_capital()

    capital_meta = get_profile_target()

    _render_header()

    left_column, right_column = st.columns(
        [
            1,
            1.55,
        ],
        gap="large",
    )

    with left_column:
        st.html(
            """
            <div class="ax-panel-title">
                <strong>
                    👤 IDENTIDAD DEL TRADER
                </strong>

                <span>
                    VISTA ACTUAL
                </span>
            </div>
            """
        )

        _render_current_avatar(
            avatar_url,
            trader_name,
        )

        _render_profile_summary(
            trader_name,
            capital_actual,
            capital_meta,
        )

        _render_security_notice()

    with right_column:
        st.html(
            """
            <div class="ax-panel-title">
                <strong>
                    ⚙️ EDITAR INFORMACIÓN
                </strong>

                <span>
                    DATOS DEL PERFIL
                </span>
            </div>
            """
        )

        with st.container(
            border=True,
        ):
            name_input = st.text_input(
                "Nombre del trader",
                value=trader_name,
                placeholder="Trader Pro",
                max_chars=80,
                key="profile_name_input",
            )

            capital_columns = st.columns(
                2
            )

            with capital_columns[0]:
                capital_input = st.number_input(
                    "Capital actual",
                    min_value=0.0,
                    value=float(
                        capital_actual
                    ),
                    step=100.0,
                    format="%.2f",
                    key="profile_capital_input",
                )

            with capital_columns[1]:
                target_input = st.number_input(
                    "Meta de capital",
                    min_value=1.0,
                    value=float(
                        capital_meta
                    ),
                    step=100.0,
                    format="%.2f",
                    key="profile_target_input",
                )

            st.html(
                """
                <div class="ax-profile-upload-title">
                    FOTO DE PERFIL
                </div>

                <div class="ax-profile-upload-description">
                    Formatos permitidos: JPG, PNG o WEBP.
                    Tamaño máximo: 5 MB.
                </div>
                """
            )

            uploaded_file = st.file_uploader(
                "Seleccionar fotografía",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "webp",
                ],
                accept_multiple_files=False,
                label_visibility="collapsed",
                key="profile_avatar_uploader",
            )

            if uploaded_file is not None:
                st.image(
                    uploaded_file,
                    caption="Vista previa de la nueva fotografía",
                    width=220,
                )

            st.html(
                "<div style='height:12px'></div>"
            )

            button_columns = st.columns(
                [
                    1,
                    1,
                ]
            )

            with button_columns[0]:
                if st.button(
                    "← Cancelar",
                    use_container_width=True,
                    type="secondary",
                    key="profile_cancel_button",
                ):
                    st.session_state.page = "Dashboard"
                    st.rerun()

            with button_columns[1]:
                if st.button(
                    "💾 Guardar cambios",
                    use_container_width=True,
                    type="primary",
                    key="profile_save_button",
                ):
                    _save_profile_changes(
                        trader_name=name_input,
                        capital_actual=float(
                            capital_input
                        ),
                        capital_meta=float(
                            target_input
                        ),
                        uploaded_file=uploaded_file,
                    )
