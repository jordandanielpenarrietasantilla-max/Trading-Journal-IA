from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone
from typing import Iterable

import streamlit as st

from ui_v2.theme import apply_v2_theme


# =========================================================
# AXION PRIME X10 PRO
# SESIONES DE TRADING EN TIEMPO REAL
# =========================================================


SESSION_CSS = """
<style>
.block-container {
    max-width: 1600px;
    padding-top: 1rem;
    padding-bottom: 2rem;
}

.ax-session-hero {
    position: relative;
    overflow: hidden;
    padding: 24px 27px;
    margin-bottom: 16px;
    background:
        radial-gradient(circle at 88% 12%, rgba(123,92,255,.17), transparent 30%),
        linear-gradient(145deg, rgba(7,14,32,.99), rgba(5,8,22,.99));
    border: 1px solid rgba(39,216,255,.27);
    border-radius: 20px;
    box-shadow: 0 24px 70px rgba(0,0,0,.34);
}

.ax-session-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(60,91,157,.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(60,91,157,.035) 1px, transparent 1px);
    background-size: 42px 42px;
}

.ax-session-hero > * {
    position: relative;
    z-index: 2;
}

.ax-session-kicker {
    color: #27d8ff;
    font-size: 8px;
    font-weight: 950;
    letter-spacing: 1.9px;
}

.ax-session-title {
    margin-top: 8px;
    color: #eef4ff;
    font-size: clamp(31px, 3vw, 46px);
    line-height: 1;
    font-weight: 950;
    letter-spacing: -1.7px;
}

.ax-session-sub {
    margin-top: 10px;
    color: #93a6c7;
    font-size: 11px;
}

.ax-live-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-top: 12px;
    padding: 6px 10px;
    color: #31ff9c;
    font-size: 7px;
    font-weight: 950;
    background: rgba(49,255,156,.07);
    border: 1px solid rgba(49,255,156,.23);
    border-radius: 999px;
}

.ax-live-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #31ff9c;
    box-shadow: 0 0 12px #31ff9c;
}

.ax-session-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 14px;
}

.ax-session-card {
    position: relative;
    overflow: hidden;
    min-height: 205px;
    padding: 18px;
    background:
        radial-gradient(circle at 100% 0%, rgba(39,216,255,.09), transparent 38%),
        linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.28);
    border-radius: 16px;
}

.ax-session-card.open {
    border-color: rgba(49,255,156,.28);
}

.ax-session-card.soon {
    border-color: rgba(255,209,102,.30);
}

.ax-session-card.closed {
    border-color: rgba(255,61,110,.25);
}

.ax-session-card::after {
    content: "";
    position: absolute;
    inset: auto -40px -55px auto;
    width: 190px;
    height: 190px;
    border-radius: 50%;
    filter: blur(16px);
    opacity: .15;
}

.ax-session-card.open::after {
    background: #31ff9c;
}

.ax-session-card.soon::after {
    background: #ffd166;
}

.ax-session-card.closed::after {
    background: #ff3d6e;
}

.ax-session-card > * {
    position: relative;
    z-index: 2;
}

.ax-session-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
}

.ax-session-name {
    color: #eef4ff;
    font-size: 18px;
    font-weight: 950;
}

.ax-session-status {
    padding: 5px 8px;
    font-size: 6.5px;
    font-weight: 950;
    border-radius: 999px;
}

.ax-session-status.open {
    color: #31ff9c;
    background: rgba(49,255,156,.08);
    border: 1px solid rgba(49,255,156,.24);
}

.ax-session-status.soon {
    color: #ffd166;
    background: rgba(255,209,102,.08);
    border: 1px solid rgba(255,209,102,.24);
}

.ax-session-status.closed {
    color: #ff6e95;
    background: rgba(255,61,110,.08);
    border: 1px solid rgba(255,61,110,.23);
}

.ax-session-hours {
    margin-top: 16px;
    color: #27d8ff;
    font-size: 24px;
    font-weight: 950;
    letter-spacing: -.7px;
}

.ax-session-countdown {
    margin-top: 8px;
    color: #eef4ff;
    font-size: 12px;
    font-weight: 850;
}

.ax-session-copy {
    margin-top: 12px;
    color: #93a6c7;
    font-size: 10px;
    line-height: 1.55;
}

.ax-timeline-shell {
    margin-top: 16px;
    padding: 18px;
    background: linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.28);
    border-radius: 16px;
}

.ax-timeline-title {
    color: #eef4ff;
    font-size: 12px;
    font-weight: 950;
}

.ax-timeline-sub {
    margin-top: 4px;
    color: #71809e;
    font-size: 8px;
}

.ax-timeline-hours {
    display: grid;
    grid-template-columns: repeat(7,1fr);
    gap: 0;
    margin: 18px 0 8px 118px;
    color: #71809e;
    font-size: 7px;
}

.ax-timeline-row {
    display: grid;
    grid-template-columns: 105px 1fr 90px;
    gap: 12px;
    align-items: center;
    margin-bottom: 11px;
}

.ax-timeline-label strong {
    display: block;
    color: #eef4ff;
    font-size: 10px;
}

.ax-timeline-label span {
    display: block;
    margin-top: 2px;
    color: #71809e;
    font-size: 6px;
}

.ax-track {
    position: relative;
    height: 22px;
    overflow: hidden;
    background:
        repeating-linear-gradient(
            90deg,
            rgba(75,102,162,.09) 0,
            rgba(75,102,162,.09) 1px,
            transparent 1px,
            transparent 12.5%
        ),
        rgba(5,9,22,.82);
    border: 1px solid rgba(61,91,158,.20);
    border-radius: 999px;
}

.ax-bar {
    position: absolute;
    top: 4px;
    height: 12px;
    border-radius: 999px;
    box-shadow: 0 0 16px currentColor;
}

.ax-bar.open {
    color: #31ff9c;
    background: linear-gradient(90deg, rgba(49,255,156,.35), #31ff9c);
}

.ax-bar.soon {
    color: #ffd166;
    background: linear-gradient(90deg, rgba(255,209,102,.35), #ffd166);
}

.ax-bar.closed {
    color: #ff3d6e;
    background: linear-gradient(90deg, rgba(255,61,110,.35), #ff3d6e);
}

.ax-now-line {
    position: absolute;
    top: -4px;
    bottom: -4px;
    width: 2px;
    background: #27d8ff;
    box-shadow: 0 0 12px #27d8ff;
}

.ax-now-line::before {
    content: "AHORA";
    position: absolute;
    top: -16px;
    left: 50%;
    transform: translateX(-50%);
    color: #27d8ff;
    font-size: 6px;
    font-weight: 950;
}

.ax-status-mini {
    text-align: right;
    font-size: 7px;
    font-weight: 950;
}

.ax-status-mini.open {
    color: #31ff9c;
}

.ax-status-mini.soon {
    color: #ffd166;
}

.ax-status-mini.closed {
    color: #ff3d6e;
}

.ax-session-summary-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0,1fr));
    gap: 12px;
    margin-top: 16px;
}

.ax-session-summary {
    padding: 14px;
    background: linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.27);
    border-radius: 14px;
}

.ax-session-summary strong {
    color: #eef4ff;
    font-size: 12px;
}

.ax-session-summary span {
    display: block;
    margin-top: 8px;
    font-size: 8px;
    font-weight: 950;
}

.ax-session-summary p {
    margin: 8px 0 0;
    color: #93a6c7;
    font-size: 8px;
}

.ax-info {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    margin-top: 16px;
    padding: 13px 15px;
    background: linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.27);
    border-radius: 14px;
}

.ax-info div {
    color: #93a6c7;
    font-size: 9px;
}

.ax-info strong {
    color: #27d8ff;
}

@media (max-width: 1000px) {
    .ax-session-grid,
    .ax-session-summary-grid {
        grid-template-columns: 1fr;
    }

    .ax-timeline-hours {
        margin-left: 0;
    }

    .ax-timeline-row {
        grid-template-columns: 1fr;
    }
}
</style>
"""


NEWS_CSS = """
<style>
.ax-news-card {
    padding: 18px;
    margin-bottom: 12px;
    background: linear-gradient(145deg, rgba(8,16,35,.98), rgba(5,9,22,.98));
    border: 1px solid rgba(61,91,158,.27);
    border-radius: 16px;
}
.ax-news-card strong {
    color: #eef4ff;
    font-size: 14px;
}
.ax-news-card p {
    margin: 8px 0 0;
    color: #93a6c7;
    font-size: 10px;
    line-height: 1.55;
}
</style>
"""


@dataclass(frozen=True)
class TradingSession:
    name: str
    start_hour: int
    end_hour: int
    description: str


SESSIONS: tuple[TradingSession, ...] = (
    TradingSession(
        "Sídney",
        21,
        6,
        "Inicio de la semana y transición asiática.",
    ),
    TradingSession(
        "Tokio",
        0,
        9,
        "Mayor actividad en JPY, AUD y mercados asiáticos.",
    ),
    TradingSession(
        "Londres",
        7,
        16,
        "Alta liquidez en oro, índices europeos y pares principales.",
    ),
    TradingSession(
        "Nueva York",
        13,
        22,
        "Volatilidad fuerte en XAU/USD, USD e índices de EE. UU.",
    ),
)


def _seconds_since_midnight(moment: datetime) -> int:
    return (
        moment.hour * 3600
        + moment.minute * 60
        + moment.second
    )


def _hour_seconds(hour: int) -> int:
    return hour * 3600


def _is_open(now_seconds: int, session: TradingSession) -> bool:
    start = _hour_seconds(session.start_hour)
    end = _hour_seconds(session.end_hour)

    if session.start_hour < session.end_hour:
        return start <= now_seconds < end

    return now_seconds >= start or now_seconds < end


def _seconds_until(
    now_seconds: int,
    target_hour: int,
) -> int:
    target = _hour_seconds(target_hour)

    if target > now_seconds:
        return target - now_seconds

    return 24 * 3600 - now_seconds + target


def _seconds_until_close(
    now_seconds: int,
    session: TradingSession,
) -> int:
    return _seconds_until(
        now_seconds,
        session.end_hour,
    )


def _seconds_until_open(
    now_seconds: int,
    session: TradingSession,
) -> int:
    return _seconds_until(
        now_seconds,
        session.start_hour,
    )


def _format_duration(total_seconds: int) -> str:
    total_seconds = max(0, int(total_seconds))

    hours, remainder = divmod(
        total_seconds,
        3600,
    )

    minutes, seconds = divmod(
        remainder,
        60,
    )

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _session_state(
    now_seconds: int,
    session: TradingSession,
) -> tuple[str, str, str]:
    if _is_open(now_seconds, session):
        seconds = _seconds_until_close(
            now_seconds,
            session,
        )

        return (
            "open",
            "ABIERTA",
            f"Cierra en {_format_duration(seconds)}",
        )

    seconds = _seconds_until_open(
        now_seconds,
        session,
    )

    if seconds <= 3 * 3600:
        return (
            "soon",
            f"EN {_format_duration(seconds)}",
            f"Abre en {_format_duration(seconds)}",
        )

    return (
        "closed",
        f"EN {_format_duration(seconds)}",
        f"Abre en {_format_duration(seconds)}",
    )


def _session_bars(
    session: TradingSession,
) -> Iterable[tuple[float, float]]:
    start = session.start_hour / 24 * 100
    end = session.end_hour / 24 * 100

    if session.start_hour < session.end_hour:
        yield start, end - start
        return

    yield start, 100 - start
    yield 0, end


def _render_session_cards(
    now_seconds: int,
) -> None:
    cards: list[str] = []

    for session in SESSIONS:
        css_class, badge, countdown = _session_state(
            now_seconds,
            session,
        )

        cards.append(
            f"""
            <article class="ax-session-card {css_class}">
                <div class="ax-session-top">
                    <div class="ax-session-name">{session.name}</div>
                    <div class="ax-session-status {css_class}">
                        {badge}
                    </div>
                </div>

                <div class="ax-session-hours">
                    {session.start_hour:02d}:00 – {session.end_hour:02d}:00 UTC
                </div>

                <div class="ax-session-countdown">
                    {countdown}
                </div>

                <div class="ax-session-copy">
                    {session.description}
                </div>
            </article>
            """
        )

    st.html(
        f'<div class="ax-session-grid">{"".join(cards)}</div>'
    )


def _render_timeline(
    now_seconds: int,
) -> None:
    now_percent = now_seconds / (24 * 3600) * 100

    rows: list[str] = []

    for session in SESSIONS:
        css_class, badge, _ = _session_state(
            now_seconds,
            session,
        )

        bars = "".join(
            (
                f'<div class="ax-bar {css_class}" '
                f'style="left:{left:.4f}%;width:{width:.4f}%"></div>'
            )
            for left, width in _session_bars(session)
        )

        rows.append(
            f"""
            <div class="ax-timeline-row">
                <div class="ax-timeline-label">
                    <strong>{session.name}</strong>
                    <span>
                        {session.start_hour:02d}:00 – {session.end_hour:02d}:00 UTC
                    </span>
                </div>

                <div class="ax-track">
                    {bars}
                    <div
                        class="ax-now-line"
                        style="left:{now_percent:.4f}%"
                    ></div>
                </div>

                <div class="ax-status-mini {css_class}">
                    {badge}
                </div>
            </div>
            """
        )

    st.html(
        f"""
        <section class="ax-timeline-shell">
            <div class="ax-timeline-title">
                LÍNEA DE TIEMPO DIARIA
            </div>

            <div class="ax-timeline-sub">
                Vista rápida del solapamiento de sesiones en UTC.
            </div>

            <div class="ax-timeline-hours">
                <span>00:00</span>
                <span>04:00</span>
                <span>08:00</span>
                <span>12:00</span>
                <span>16:00</span>
                <span>20:00</span>
                <span>24:00</span>
            </div>

            {"".join(rows)}
        </section>
        """
    )


def _render_summary(
    now_seconds: int,
) -> None:
    cards: list[str] = []

    for session in SESSIONS:
        css_class, badge, countdown = _session_state(
            now_seconds,
            session,
        )

        cards.append(
            f"""
            <div class="ax-session-summary">
                <strong>{session.name}</strong>
                <span class="ax-status-mini {css_class}">
                    {badge}
                </span>
                <p>{countdown}</p>
            </div>
            """
        )

    st.html(
        f'<div class="ax-session-summary-grid">{"".join(cards)}</div>'
    )


def render_sessions() -> None:
    apply_v2_theme()
    st.markdown(
        SESSION_CSS,
        unsafe_allow_html=True,
    )

    now_utc = datetime.now(
        timezone.utc
    )

    now_seconds = _seconds_since_midnight(
        now_utc
    )

    st.html(
        f"""
        <section class="ax-session-hero">
            <div class="ax-session-kicker">
                AXION PRIME · GLOBAL MARKET CLOCK
            </div>

            <div class="ax-session-title">
                Sesiones de trading
            </div>

            <div class="ax-session-sub">
                Hora actual:
                <strong style="color:#27d8ff">
                    {now_utc.strftime("%H:%M:%S UTC")}
                </strong>
                · {now_utc.strftime("%d/%m/%Y")}
            </div>

            <div class="ax-live-badge">
                <span class="ax-live-dot"></span>
                Sincronizado con hora real UTC
            </div>
        </section>
        """
    )

    _render_session_cards(
        now_seconds
    )

    _render_timeline(
        now_seconds
    )

    _render_summary(
        now_seconds
    )

    st.html(
        """
        <div class="ax-info">
            <div>
                Todas las horas se muestran en
                <strong>UTC</strong>.
                La hora se recalcula cada vez que Streamlit ejecuta la página.
            </div>
        </div>
        """
    )

    st.caption(
        "Para actualizar los segundos, pulsa la tecla R, recarga la página "
        "o cambia de sección y vuelve a Sesiones de trading."
    )


def render_news() -> None:
    apply_v2_theme()

    st.markdown(
        SESSION_CSS + NEWS_CSS,
        unsafe_allow_html=True,
    )

    now_utc = datetime.now(
        timezone.utc
    )

    st.html(
        f"""
        <section class="ax-session-hero">
            <div class="ax-session-kicker">
                AXION PRIME · ECONOMIC INTELLIGENCE
            </div>

            <div class="ax-session-title">
                Noticias de impacto
            </div>

            <div class="ax-session-sub">
                Hora de referencia:
                <strong style="color:#27d8ff">
                    {now_utc.strftime("%H:%M:%S UTC")}
                </strong>
            </div>
        </section>
        """
    )

    st.warning(
        "La interfaz está preparada, pero todavía no hay una API de calendario "
        "económico conectada. No se mostrarán noticias inventadas."
    )

    st.html(
        """
        <article class="ax-news-card">
            <strong>Calendario económico en tiempo real</strong>
            <p>
                Aquí aparecerán país, moneda, hora UTC, nivel de impacto,
                previsión, dato anterior y dato real cuando conectemos
                una fuente económica.
            </p>
        </article>

        <article class="ax-news-card">
            <strong>Control preventivo de riesgo</strong>
            <p>
                La app podrá advertir cuando falten pocos minutos para
                una noticia de alto impacto y marcar trades abiertos
                dentro de esa ventana de volatilidad.
            </p>
        </article>
        """
    )
