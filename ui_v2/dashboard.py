from __future__ import annotations

import html
from typing import Any

import streamlit as st


# =========================================================
# AXION PRIME V2
# COMPONENTES VISUALES REUTILIZABLES
# =========================================================


def safe_text(
    value: Any,
    default: str = "",
) -> str:
    """
    Limpia un texto antes de insertarlo dentro de HTML.
    """

    clean_value = str(
        value
        if value is not None
        else default
    ).strip()

    return html.escape(clean_value)


def money(
    value: Any,
    default: float = 0.0,
) -> str:
    """
    Formatea un valor numérico como dinero.
    """

    try:
        numeric_value = float(
            value
            if value is not None
            else default
        )

    except (TypeError, ValueError):
        numeric_value = default

    return f"${numeric_value:,.2f}"


def _metric_value_class(value: str) -> str:
    """
    Define una clase según la longitud del valor.

    Esto evita que cifras largas como $13,450.00
    se salgan de la tarjeta.
    """

    clean = str(value or "").strip()
    length = len(clean)

    if length >= 15:
        return "v2-value-xxl"

    if length >= 12:
        return "v2-value-xl"

    if length >= 10:
        return "v2-value-lg"

    if length >= 8:
        return "v2-value-md"

    return "v2-value-sm"


def render_section_header(
    *,
    eyebrow: str,
    title: str,
    description: str = "",
    status: str = "",
) -> None:
    """
    Encabezado reutilizable para las pantallas V2.
    """

    safe_eyebrow = safe_text(eyebrow)
    safe_title = safe_text(title)
    safe_description = safe_text(description)
    safe_status = safe_text(status)

    status_html = (
        f"""
        <div class="v2-section-status">
            <span></span>
            {safe_status}
        </div>
        """
        if safe_status
        else ""
    )

    description_html = (
        f"""
        <p>
            {safe_description}
        </p>
        """
        if safe_description
        else ""
    )

    st.html(
        f"""
        <section class="v2-section-header v2-glass">

            <div class="v2-section-copy">
                <div class="v2-eyebrow">
                    {safe_eyebrow}
                </div>

                <h1 class="v2-title">
                    {safe_title}
                </h1>

                {description_html}
            </div>

            {status_html}

        </section>
        """
    )


def render_metric_card(
    *,
    label: str,
    value: str,
    subtitle: str = "",
    footer: str = "",
    accent: str = "#19E4FF",
    icon: str = "◈",
) -> None:
    """
    Tarjeta de métrica reutilizable con ajuste automático.

    La cifra cambia de tamaño según su longitud para evitar
    desbordamientos en balance, P&L y otras métricas.
    """

    safe_label = safe_text(label)
    safe_value = safe_text(value)
    safe_subtitle = safe_text(subtitle)
    safe_footer = safe_text(footer)
    safe_icon = safe_text(icon)

    value_class = _metric_value_class(str(value))

    st.html(
        f"""
        <article class="v2-metric-card v2-glass">

            <div
                class="v2-metric-icon"
                style="
                    color:{accent};
                    border-color:{accent}55;
                    background:{accent}12;
                    box-shadow:0 0 24px {accent}14;
                "
            >
                {safe_icon}
            </div>

            <div class="v2-metric-copy">

                <div class="v2-metric-label">
                    {safe_label}
                </div>

                <div
                    class="v2-metric-value {value_class}"
                    style="color:{accent}"
                    title="{safe_value}"
                >
                    {safe_value}
                </div>

                <div class="v2-metric-meta">
                    <span title="{safe_subtitle}">
                        {safe_subtitle}
                    </span>

                    <span title="{safe_footer}">
                        {safe_footer}
                    </span>
                </div>

            </div>

        </article>
        """
    )


def render_panel_title(
    *,
    icon: str,
    title: str,
    subtitle: str = "",
) -> None:
    """
    Encabezado pequeño para paneles y módulos.
    """

    st.html(
        f"""
        <div class="v2-panel-title">

            <div>
                <span class="v2-panel-icon">
                    {safe_text(icon)}
                </span>

                <strong>
                    {safe_text(title)}
                </strong>
            </div>

            <small>
                {safe_text(subtitle)}
            </small>

        </div>
        """
    )


def render_empty_state(
    *,
    icon: str,
    title: str,
    description: str,
) -> None:
    """
    Estado vacío reutilizable.
    """

    st.html(
        f"""
        <div class="v2-empty-state v2-glass">

            <div class="v2-empty-icon">
                {safe_text(icon)}
            </div>

            <strong>
                {safe_text(title)}
            </strong>

            <p>
                {safe_text(description)}
            </p>

        </div>
        """
    )


def render_status_badge(
    *,
    label: str,
    tone: str = "green",
) -> None:
    """
    Insignia visual de estado.

    tone puede ser:
    green, red, cyan, purple o neutral.
    """

    allowed_tones = {
        "green",
        "red",
        "cyan",
        "purple",
        "neutral",
    }

    clean_tone = (
        tone
        if tone in allowed_tones
        else "neutral"
    )

    st.html(
        f"""
        <span class="
            v2-status-badge
            v2-status-{clean_tone}
        ">
            {safe_text(label)}
        </span>
        """
    )


def render_feature_grid(
    features: list[tuple[str, str]],
) -> None:
    """
    Renderiza una cuadrícula de características.

    Cada elemento debe ser:
    (icono, texto)
    """

    items = []

    for icon, text in features:
        items.append(
            f"""
            <div class="v2-feature-item">
                <span>
                    {safe_text(icon)}
                </span>

                <b>
                    {safe_text(text)}
                </b>
            </div>
            """
        )

    st.html(
        f"""
        <div class="v2-feature-grid">
            {''.join(items)}
        </div>
        """
    )
