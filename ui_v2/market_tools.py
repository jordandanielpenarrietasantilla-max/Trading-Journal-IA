from __future__ import annotations

import base64
import html
from pathlib import Path
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any, Callable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import streamlit as st

from ui_v2.theme import apply_v2_theme


# =========================================================
# AXION PRIME
# SESIONES DE TRADING · HORA LOCAL AUTOMÁTICA
# =========================================================


@dataclass(frozen=True)
class MarketSession:
    key: str
    city: str
    country: str
    flag: str
    timezone_name: str
    open_local: time
    close_local: time
    description: str
    color: str
    rgb: str
    landmark: str


SESSIONS: tuple[MarketSession, ...] = (
    MarketSession(
        key="sydney",
        city="SÍDNEY",
        country="Australia",
        flag="🇦🇺",
        timezone_name="Australia/Sydney",
        open_local=time(8, 0),
        close_local=time(17, 0),
        description="Inicio de la semana y transición asiática.",
        color="#24F09B",
        rgb="36,240,155",
        landmark="opera",
    ),
    MarketSession(
        key="tokyo",
        city="TOKIO",
        country="Japón",
        flag="🇯🇵",
        timezone_name="Asia/Tokyo",
        open_local=time(9, 0),
        close_local=time(18, 0),
        description="Mayor actividad en JPY, AUD y mercados asiáticos.",
        color="#27B9FF",
        rgb="39,185,255",
        landmark="tower",
    ),
    MarketSession(
        key="london",
        city="LONDRES",
        country="Reino Unido",
        flag="🇬🇧",
        timezone_name="Europe/London",
        open_local=time(8, 0),
        close_local=time(17, 0),
        description="Alta liquidez en oro, índices europeos y pares principales.",
        color="#FFAA19",
        rgb="255,170,25",
        landmark="bigben",
    ),
    MarketSession(
        key="new_york",
        city="NUEVA YORK",
        country="Estados Unidos",
        flag="🇺🇸",
        timezone_name="America/New_York",
        open_local=time(8, 0),
        close_local=time(17, 0),
        description="Volatilidad fuerte en XAU/USD, USD e índices de EE. UU.",
        color="#FF2F7D",
        rgb="255,47,125",
        landmark="liberty",
    ),
)


# =========================================================
# FONDOS FUTURISTAS DESDE ASSETS LOCALES
# Ruta esperada: assets/sessions/*.webp
# =========================================================


def _asset_data_url(relative_path: str) -> str:
    project_root = Path(__file__).resolve().parents[1]
    image_path = project_root / relative_path

    if not image_path.exists():
        return ""

    mime = "image/webp"
    encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


CITY_IMAGES: dict[str, str] = {
    "sydney": _asset_data_url("assets/sessions/sydney.webp"),
    "tokyo": _asset_data_url("assets/sessions/tokyo.webp"),
    "london": _asset_data_url("assets/sessions/london.webp"),
    "new_york": _asset_data_url("assets/sessions/new_york.webp"),
}


# =========================================================
# CSS
# =========================================================


SESSION_CSS = """
<style>
.block-container {
    max-width: 1740px;
    padding-top: .8rem;
    padding-bottom: 2rem;
}

.ax-sessions {
    --bg:#030713;
    --panel:#071020;
    --panel2:#050b18;
    --line:rgba(57,95,160,.32);
    --text:#f2f6ff;
    --muted:#91a2c2;
    --cyan:#27d8ff;
}

.ax-hero {
    position:relative;
    overflow:hidden;
    padding:24px 26px;
    margin-bottom:14px;
    border:1px solid rgba(39,216,255,.24);
    border-radius:18px;
    background:
      radial-gradient(circle at 82% 0%,rgba(123,92,255,.15),transparent 35%),
      linear-gradient(145deg,rgba(7,16,35,.99),rgba(3,7,18,.99));
    box-shadow:0 24px 70px rgba(0,0,0,.32);
}

.ax-hero:before {
    content:"";
    position:absolute;
    inset:0;
    background-image:
      linear-gradient(rgba(49,78,137,.035) 1px,transparent 1px),
      linear-gradient(90deg,rgba(49,78,137,.035) 1px,transparent 1px);
    background-size:42px 42px;
    pointer-events:none;
}

.ax-hero > * {position:relative;z-index:2}

.ax-kicker {
    color:#27d8ff;
    font-size:8px;
    font-weight:950;
    letter-spacing:1.8px;
}

.ax-title {
    margin-top:7px;
    color:#f2f6ff;
    font-size:clamp(30px,3vw,44px);
    line-height:1;
    font-weight:950;
    letter-spacing:-1.5px;
}

.ax-local-grid {
    display:grid;
    grid-template-columns:1.8fr .9fr .9fr;
    gap:12px;
    margin-top:17px;
}

.ax-local-box {
    padding:14px 15px;
    border:1px solid rgba(57,95,160,.29);
    border-radius:14px;
    background:linear-gradient(145deg,rgba(8,17,37,.96),rgba(4,9,21,.96));
}

.ax-label {
    color:#7888a8;
    font-size:7px;
    font-weight:900;
    letter-spacing:.8px;
}

.ax-local-time {
    margin-top:6px;
    color:#27d8ff;
    font-size:31px;
    line-height:1;
    font-weight:950;
    text-shadow:0 0 24px rgba(39,216,255,.28);
}

.ax-local-meta {
    margin-top:8px;
    color:#91a2c2;
    font-size:9px;
}

.ax-live {
    color:#31ff9c;
    font-size:11px;
    font-weight:900;
}

.ax-session-grid {
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:12px;
}

.ax-city-card {
    position:relative;
    min-height:325px;
    overflow:hidden;
    border:1px solid rgba(var(--rgb),.58);
    border-radius:16px;
    background:#050a15;
    box-shadow:0 24px 64px rgba(0,0,0,.42),0 0 36px rgba(var(--rgb),.14);
    transition:transform .25s ease, box-shadow .25s ease;
}

.ax-city-card:hover {
    transform:translateY(-4px);
    box-shadow:0 30px 80px rgba(0,0,0,.50),0 0 52px rgba(var(--rgb),.22);
}

@keyframes axCityDrift {
    from { transform:scale(1.04) translateX(-.4%); }
    to { transform:scale(1.10) translateX(.8%); }
}


.ax-city-bg {
    position:absolute;
    inset:0;
    background-image:
      linear-gradient(180deg,rgba(2,6,16,.16),rgba(2,6,16,.25) 38%,rgba(2,6,16,.96) 100%),
      var(--city);
    background-size:cover;
    background-position:center center;
    opacity:.98;
    transform:scale(1.04);
    filter:saturate(1.22) contrast(1.08) brightness(.90);
    animation:axCityDrift 15s ease-in-out infinite alternate;
}

.ax-city-card:after {
    content:"";
    position:absolute;
    inset:0;
    background:
      radial-gradient(circle at 100% 0%,rgba(var(--rgb),.15),transparent 38%),
      linear-gradient(180deg,rgba(2,6,16,.45),transparent 45%);
    pointer-events:none;
}

.ax-city-body {
    position:relative;
    z-index:2;
    display:flex;
    flex-direction:column;
    height:325px;
    padding:16px;
}

.ax-city-top {
    display:flex;
    justify-content:space-between;
    gap:8px;
    align-items:flex-start;
}

.ax-city-name {
    color:#f2f6ff;
    font-size:17px;
    font-weight:950;
}

.ax-country {
    margin-top:2px;
    color:#a2b0ca;
    font-size:9px;
}

.ax-status {
    padding:5px 8px;
    color:var(--color);
    font-size:6px;
    font-weight:950;
    background:rgba(var(--rgb),.09);
    border:1px solid rgba(var(--rgb),.28);
    border-radius:999px;
}

.ax-city-clock {
    margin-top:22px;
    color:var(--color);
    font-size:30px;
    line-height:1;
    font-weight:950;
    text-shadow:0 0 22px rgba(var(--rgb),.28);
}

.ax-zone {
    margin-top:7px;
    color:#c8d3e8;
    font-size:9px;
}

.ax-count {
    margin-top:16px;
    color:#f2f6ff;
    font-size:9px;
}

.ax-count strong {
    display:block;
    margin-top:4px;
    color:var(--color);
    font-size:17px;
}

.ax-copy {
    margin-top:14px;
    max-width:80%;
    color:#a4b0c8;
    font-size:9px;
    line-height:1.45;
}

.ax-card-spacer {flex:1}

.ax-session-local {
    padding-top:10px;
    color:#8fa0bf;
    font-size:7px;
    border-top:1px solid rgba(255,255,255,.08);
}

.ax-panel {
    margin-top:14px;
    padding:16px;
    border:1px solid rgba(57,95,160,.29);
    border-radius:16px;
    background:linear-gradient(145deg,rgba(7,15,32,.98),rgba(3,8,19,.98));
}

.ax-panel-head {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:14px;
}

.ax-panel-head strong {
    color:#f2f6ff;
    font-size:11px;
}

.ax-panel-head span {
    color:#7586a6;
    font-size:7px;
}

.ax-hours {
    display:grid;
    grid-template-columns:repeat(7,1fr);
    margin:0 86px 8px 120px;
    color:#7182a4;
    font-size:6px;
}

.ax-t-row {
    display:grid;
    grid-template-columns:110px 1fr 78px;
    gap:10px;
    align-items:center;
    margin:10px 0;
}

.ax-t-label strong {
    display:block;
    color:#f2f6ff;
    font-size:9px;
}

.ax-t-label span {
    color:#7182a4;
    font-size:6px;
}

.ax-track {
    position:relative;
    height:22px;
    overflow:visible;
    border:1px solid rgba(57,95,160,.20);
    border-radius:999px;
    background:
      repeating-linear-gradient(
        90deg,
        rgba(70,100,163,.09) 0,
        rgba(70,100,163,.09) 1px,
        transparent 1px,
        transparent 8.333%
      ),
      rgba(2,6,16,.80);
}

.ax-bar {
    position:absolute;
    top:4px;
    height:12px;
    border-radius:999px;
    background:linear-gradient(90deg,rgba(var(--rgb),.34),var(--color));
    box-shadow:0 0 17px rgba(var(--rgb),.58);
}

.ax-now {
    position:absolute;
    top:-12px;
    bottom:-12px;
    width:2px;
    background:#27d8ff;
    box-shadow:0 0 12px #27d8ff;
}

.ax-now:before {
    content:attr(data-time);
    position:absolute;
    top:-18px;
    left:50%;
    transform:translateX(-50%);
    padding:3px 5px;
    color:white;
    font-size:6px;
    font-weight:900;
    background:#167fff;
    border-radius:5px;
}

.ax-t-state {
    text-align:right;
    color:var(--color);
    font-size:6px;
    font-weight:950;
}

.ax-overlap {
    margin-top:14px;
    padding:14px 16px;
    border:1px solid rgba(255,170,25,.30);
    border-radius:14px;
    background:
      radial-gradient(circle at 92% 30%,rgba(255,47,125,.12),transparent 35%),
      linear-gradient(145deg,rgba(16,12,28,.98),rgba(5,9,22,.98));
}

.ax-overlap strong {
    color:#ffaa19;
    font-size:11px;
}

.ax-overlap p {
    margin:7px 0 0;
    color:#a3afc7;
    font-size:9px;
}

.ax-summary-grid {
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
    margin-top:14px;
}

.ax-summary {
    padding:13px;
    border:1px solid rgba(var(--rgb),.38);
    border-radius:13px;
    background:linear-gradient(145deg,rgba(7,15,32,.98),rgba(3,8,19,.98));
}

.ax-summary strong {
    color:#f2f6ff;
    font-size:11px;
}

.ax-summary .clock {
    margin-top:9px;
    color:var(--color);
    font-size:18px;
    font-weight:950;
}

.ax-summary small {
    display:block;
    margin-top:5px;
    color:#8798b7;
    font-size:7px;
}

.ax-info {
    margin-top:14px;
    padding:12px 14px;
    color:#91a2c2;
    font-size:8px;
    border:1px solid rgba(57,95,160,.27);
    border-radius:12px;
    background:rgba(5,10,23,.90);
}

@media(max-width:1250px){
    .ax-session-grid{grid-template-columns:repeat(2,minmax(0,1fr))}
    .ax-local-grid{grid-template-columns:1fr}
}

@media(max-width:760px){
    .ax-session-grid,.ax-summary-grid{grid-template-columns:1fr}
    .ax-hours{display:none}
    .ax-t-row{grid-template-columns:1fr}
}
.ax-city-noise {
    position:absolute;
    inset:0;
    z-index:1;
    pointer-events:none;
    opacity:.12;
    background:repeating-linear-gradient(180deg,transparent 0,transparent 3px,rgba(var(--rgb),.15) 4px);
    mix-blend-mode:screen;
}

</style>
"""


# =========================================================
# TIMEZONE Y SESIONES
# =========================================================


def _safe_zone(name: str | None, fallback: str = "UTC") -> ZoneInfo:
    try:
        return ZoneInfo(name or fallback)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        return ZoneInfo(fallback)


def _browser_timezone_name() -> str:
    """
    Streamlit 1.43+ entrega la zona IANA real del navegador.
    Ejemplos: America/Santiago, Europe/Madrid.
    """
    try:
        value = getattr(st.context, "timezone", None)
        if value:
            _safe_zone(str(value))
            return str(value)
    except Exception:
        pass

    return "UTC"


def _friendly_zone(zone_name: str) -> str:
    city = zone_name.split("/")[-1].replace("_", " ")
    region = zone_name.split("/")[0].replace("_", " ")
    return city if region in {"Etc", "UTC"} else f"{city} · {region}"


def _utc_offset_text(moment: datetime) -> str:
    offset = moment.utcoffset() or timedelta(0)
    seconds = int(offset.total_seconds())
    sign = "+" if seconds >= 0 else "-"
    seconds = abs(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes = remainder // 60
    return f"GMT{sign}{hours}" if minutes == 0 else f"GMT{sign}{hours}:{minutes:02d}"


def _session_bounds_utc(
    session: MarketSession,
    now_utc: datetime,
) -> tuple[datetime, datetime]:
    session_zone = _safe_zone(session.timezone_name)
    now_session = now_utc.astimezone(session_zone)

    open_today = datetime.combine(
        now_session.date(),
        session.open_local,
        tzinfo=session_zone,
    )
    close_today = datetime.combine(
        now_session.date(),
        session.close_local,
        tzinfo=session_zone,
    )

    if close_today <= open_today:
        close_today += timedelta(days=1)

    if now_session < open_today:
        previous_open = open_today - timedelta(days=1)
        previous_close = close_today - timedelta(days=1)
        if previous_open <= now_session < previous_close:
            return previous_open.astimezone(timezone.utc), previous_close.astimezone(timezone.utc)

    if now_session >= close_today:
        open_today += timedelta(days=1)
        close_today += timedelta(days=1)

    return open_today.astimezone(timezone.utc), close_today.astimezone(timezone.utc)


def _session_state(
    session: MarketSession,
    now_utc: datetime,
) -> dict[str, Any]:
    open_utc, close_utc = _session_bounds_utc(session, now_utc)

    if open_utc <= now_utc < close_utc:
        is_open = True
        target = close_utc
        status = "ABIERTA"
        countdown_label = "Cierra en"
    else:
        is_open = False
        target = open_utc
        remaining = target - now_utc
        status = "PRÓXIMAMENTE" if remaining <= timedelta(hours=3) else "CERRADA"
        countdown_label = "Abre en"

    remaining_seconds = max(0, int((target - now_utc).total_seconds()))
    hours, remainder = divmod(remaining_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    session_now = now_utc.astimezone(_safe_zone(session.timezone_name))

    return {
        "open_utc": open_utc,
        "close_utc": close_utc,
        "is_open": is_open,
        "status": status,
        "countdown_label": countdown_label,
        "countdown": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
        "city_now": session_now,
        "city_clock": session_now.strftime("%H:%M:%S"),
        "offset": _utc_offset_text(session_now),
    }


def _local_day_bounds(now_local: datetime) -> tuple[datetime, datetime]:
    start = datetime.combine(now_local.date(), time.min, tzinfo=now_local.tzinfo)
    return start, start + timedelta(days=1)


def _timeline_segments(
    state: dict[str, Any],
    user_zone: ZoneInfo,
    now_local: datetime,
) -> list[tuple[float, float]]:
    day_start, day_end = _local_day_bounds(now_local)

    intervals: list[tuple[datetime, datetime]] = []
    base_open = state["open_utc"].astimezone(user_zone)
    base_close = state["close_utc"].astimezone(user_zone)

    for shift in (-1, 0, 1):
        start = base_open + timedelta(days=shift)
        end = base_close + timedelta(days=shift)
        clipped_start = max(start, day_start)
        clipped_end = min(end, day_end)
        if clipped_start < clipped_end:
            intervals.append((clipped_start, clipped_end))

    segments: list[tuple[float, float]] = []
    for start, end in intervals:
        left = (start - day_start).total_seconds() / 86400 * 100
        width = (end - start).total_seconds() / 86400 * 100
        segments.append((left, width))
    return segments


def _render_clock_content() -> None:
    zone_name = _browser_timezone_name()
    user_zone = _safe_zone(zone_name)
    now_utc = datetime.now(timezone.utc)
    now_local = now_utc.astimezone(user_zone)
    states = {s.key: _session_state(s, now_utc) for s in SESSIONS}

    st.html(
        f"""
        <div class="ax-sessions">
          <section class="ax-hero">
            <div class="ax-kicker">AXION PRIME · GLOBAL MARKET CLOCK</div>
            <div class="ax-title">Sesiones de trading</div>

            <div class="ax-local-grid">
              <div class="ax-local-box">
                <div class="ax-label">TU HORA LOCAL · DETECCIÓN AUTOMÁTICA</div>
                <div class="ax-local-time">{now_local.strftime("%H:%M:%S")}</div>
                <div class="ax-local-meta">
                  {html.escape(_friendly_zone(zone_name))}
                  · {now_local.strftime("%d/%m/%Y")}
                  · {_utc_offset_text(now_local)}
                </div>
              </div>

              <div class="ax-local-box">
                <div class="ax-label">SINCRONIZACIÓN</div>
                <div class="ax-live">● EN TIEMPO REAL</div>
                <div class="ax-local-meta">Actualización automática del reloj.</div>
              </div>

              <div class="ax-local-box">
                <div class="ax-label">ZONA HORARIA DETECTADA</div>
                <div style="margin-top:7px;color:#f2f6ff;font-size:12px;font-weight:850">
                  {html.escape(zone_name)}
                </div>
                <div class="ax-local-meta">Obtenida desde el navegador.</div>
              </div>
            </div>
          </section>
        </div>
        """
    )

    city_cards: list[str] = []
    for session in SESSIONS:
        state = states[session.key]
        local_open = state["open_utc"].astimezone(user_zone)
        local_close = state["close_utc"].astimezone(user_zone)
        city_cards.append(
            f"""
            <article class="ax-city-card"
              style="--color:{session.color};--rgb:{session.rgb};
                     --city:url('{CITY_IMAGES[session.key]}')">
              <div class="ax-city-bg"></div><div class="ax-city-noise"></div>
              <div class="ax-city-body">
                <div class="ax-city-top">
                  <div>
                    <div class="ax-city-name">{session.flag} {session.city}</div>
                    <div class="ax-country">{session.country}</div>
                  </div>
                  <div class="ax-status">{state["status"]}</div>
                </div>

                <div class="ax-city-clock">{state["city_clock"]}</div>
                <div class="ax-zone">{state["offset"]} · {session.timezone_name}</div>

                <div class="ax-count">
                  {state["countdown_label"]}
                  <strong>{state["countdown"]}</strong>
                </div>

                <div class="ax-copy">{session.description}</div>
                <div class="ax-card-spacer"></div>

                <div class="ax-session-local">
                  En tu hora: {local_open.strftime("%H:%M")} – {local_close.strftime("%H:%M")}
                </div>
              </div>
            </article>
            """
        )

    st.html(f'<div class="ax-sessions"><div class="ax-session-grid">{"".join(city_cards)}</div></div>')

    now_percent = (
        (now_local.hour * 3600 + now_local.minute * 60 + now_local.second)
        / 86400
        * 100
    )

    timeline_rows: list[str] = []
    for session in SESSIONS:
        state = states[session.key]
        bars = "".join(
            f'<div class="ax-bar" style="--color:{session.color};--rgb:{session.rgb};left:{left:.3f}%;width:{width:.3f}%"></div>'
            for left, width in _timeline_segments(state, user_zone, now_local)
        )
        timeline_rows.append(
            f"""
            <div class="ax-t-row" style="--color:{session.color};--rgb:{session.rgb}">
              <div class="ax-t-label">
                <strong>{session.city.title()}</strong>
                <span>{state["offset"]}</span>
              </div>
              <div class="ax-track">
                {bars}
                <div class="ax-now" data-time="{now_local.strftime("%H:%M")}" style="left:{now_percent:.3f}%"></div>
              </div>
              <div class="ax-t-state">{state["status"]}</div>
            </div>
            """
        )

    st.html(
        f"""
        <div class="ax-sessions">
          <section class="ax-panel">
            <div class="ax-panel-head">
              <strong>LÍNEA DE TIEMPO · HORA LOCAL DEL USUARIO</strong>
              <span>{html.escape(_friendly_zone(zone_name))}</span>
            </div>
            <div class="ax-hours">
              <span>00:00</span><span>04:00</span><span>08:00</span>
              <span>12:00</span><span>16:00</span><span>20:00</span><span>24:00</span>
            </div>
            {"".join(timeline_rows)}
          </section>
        </div>
        """
    )

    london_open = states["london"]["is_open"]
    ny_open = states["new_york"]["is_open"]
    if london_open and ny_open:
        overlap_title = "🔥 OVERLAP ACTIVO · LONDRES + NUEVA YORK"
        overlap_copy = "La franja de mayor liquidez y participación institucional del día."
    else:
        overlap_title = "OVERLAP LONDRES + NUEVA YORK"
        overlap_copy = "El panel se activará automáticamente cuando ambas sesiones estén abiertas."

    st.html(
        f"""
        <div class="ax-sessions">
          <div class="ax-overlap">
            <strong>{overlap_title}</strong>
            <p>{overlap_copy}</p>
          </div>
        </div>
        """
    )

    summary_cards = "".join(
        f"""
        <div class="ax-summary" style="--color:{s.color};--rgb:{s.rgb}">
          <strong>{s.flag} {s.city}</strong>
          <div class="clock">{states[s.key]["city_clock"]}</div>
          <small>{states[s.key]["status"]} · {states[s.key]["countdown_label"]} {states[s.key]["countdown"]}</small>
        </div>
        """
        for s in SESSIONS
    )

    st.html(
        f"""
        <div class="ax-sessions">
          <div class="ax-summary-grid">{summary_cards}</div>
          <div class="ax-info">
            Las horas principales se muestran automáticamente en
            <strong>{html.escape(zone_name)}</strong>.
            Los horarios de cada sesión se calculan desde la zona de la ciudad,
            incluyendo cambios de horario de verano.
          </div>
        </div>
        """
    )


def _live_fragment() -> Callable[[], None]:
    """
    Usa actualización automática si la versión instalada de Streamlit
    incluye st.fragment. En versiones anteriores, renderiza normalmente.
    """
    fragment = getattr(st, "fragment", None)
    if callable(fragment):
        return fragment(run_every="1s")(_render_clock_content)
    return _render_clock_content


_RENDER_LIVE = _live_fragment()


def render_sessions() -> None:
    apply_v2_theme()
    st.markdown(SESSION_CSS, unsafe_allow_html=True)
    _RENDER_LIVE()

    if _browser_timezone_name() == "UTC":
        st.warning(
            "No pude obtener una zona IANA desde el navegador. "
            "Se está usando UTC como respaldo. Para detección automática completa, "
            "usa Streamlit 1.43 o superior."
        )


# =========================================================
# NOTICIAS: se conserva la función requerida por app.py
# =========================================================


def render_news() -> None:
    apply_v2_theme()
    st.markdown(SESSION_CSS, unsafe_allow_html=True)

    now_utc = datetime.now(timezone.utc)
    zone_name = _browser_timezone_name()
    local_now = now_utc.astimezone(_safe_zone(zone_name))

    st.html(
        f"""
        <div class="ax-sessions">
          <section class="ax-hero">
            <div class="ax-kicker">AXION PRIME · ECONOMIC INTELLIGENCE</div>
            <div class="ax-title">Noticias de impacto</div>
            <div class="ax-local-meta">
              Hora local: {local_now.strftime("%H:%M:%S")}
              · {html.escape(zone_name)}
            </div>
          </section>

          <div class="ax-info">
            La pantalla está preparada para conectar un calendario económico real.
            No se mostrarán eventos inventados mientras no exista una API configurada.
          </div>
        </div>
        """
    )
