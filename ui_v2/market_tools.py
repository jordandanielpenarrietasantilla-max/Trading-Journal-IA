from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from ui_v2.theme import apply_v2_theme


TOOLS_CSS = """
<style>
.ax-market-title {
    padding:22px 24px;
    margin-bottom:16px;
    background:linear-gradient(145deg,rgba(7,16,35,.98),rgba(5,10,25,.98));
    border:1px solid rgba(62,112,184,.32);
    border-radius:18px;
}
.ax-market-title h1 { margin:0; color:#f7f9ff; font-size:34px; letter-spacing:-1.4px; }
.ax-market-title p { margin:8px 0 0; color:#91a0bf; font-size:11px; }
.ax-session-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }
.ax-session {
    padding:18px;
    background:linear-gradient(145deg,rgba(7,15,33,.98),rgba(4,9,23,.98));
    border:1px solid rgba(66,98,160,.30);
    border-radius:16px;
}
.ax-session-head { display:flex; justify-content:space-between; align-items:center; gap:10px; }
.ax-session h3 { margin:0; color:#f7f9ff; font-size:16px; }
.ax-session small { color:#64718d; font-size:7px; font-weight:900; letter-spacing:1px; }
.ax-session strong { display:block; margin-top:12px; color:#19e4ff; font-size:22px; }
.ax-session p { margin:8px 0 0; color:#91a0bf; font-size:10px; line-height:1.5; }
.ax-open { color:#00f58a !important; }
.ax-closed { color:#ff5b77 !important; }
.ax-news-card {
    padding:18px;
    margin-bottom:12px;
    background:linear-gradient(145deg,rgba(7,15,33,.98),rgba(4,9,23,.98));
    border:1px solid rgba(66,98,160,.30);
    border-radius:16px;
}
.ax-news-card strong { color:#f7f9ff; font-size:14px; }
.ax-news-card p { color:#91a0bf; font-size:10px; line-height:1.5; }
.ax-news-badge {
    display:inline-flex; padding:4px 8px; margin-bottom:8px;
    color:#ffd166; font-size:7px; font-weight:950;
    background:rgba(255,209,102,.08);
    border:1px solid rgba(255,209,102,.26);
    border-radius:999px;
}
@media(max-width:800px){.ax-session-grid{grid-template-columns:1fr;}}
</style>
"""


def _is_open(hour: int, start: int, end: int) -> bool:
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end


def render_sessions() -> None:
    apply_v2_theme()
    st.markdown(TOOLS_CSS, unsafe_allow_html=True)

    now_utc = datetime.now(timezone.utc)
    hour = now_utc.hour

    sessions = [
        ("Sídney", 21, 6, "Inicio de la semana y transición asiática."),
        ("Tokio", 0, 9, "Mayor actividad en JPY, AUD y mercados asiáticos."),
        ("Londres", 7, 16, "Alta liquidez en oro, índices europeos y principales pares."),
        ("Nueva York", 13, 22, "Volatilidad fuerte en XAU/USD, USD e índices de EE. UU."),
    ]

    st.html(
        f"""
        <section class="ax-market-title">
            <h1>Sesiones de trading</h1>
            <p>Hora actual UTC: {now_utc.strftime('%H:%M')} · Estado calculado automáticamente.</p>
        </section>
        """
    )

    cards = []
    for name, start, end, description in sessions:
        opened = _is_open(hour, start, end)
        state = "ABIERTA" if opened else "CERRADA"
        css = "ax-open" if opened else "ax-closed"
        cards.append(
            f"""
            <article class="ax-session">
                <div class="ax-session-head">
                    <h3>{name}</h3>
                    <small class="{css}">{state}</small>
                </div>
                <strong>{start:02d}:00 – {end:02d}:00 UTC</strong>
                <p>{description}</p>
            </article>
            """
        )

    st.html(f'<div class="ax-session-grid">{"".join(cards)}</div>')


def render_news() -> None:
    apply_v2_theme()
    st.markdown(TOOLS_CSS, unsafe_allow_html=True)

    st.html(
        """
        <section class="ax-market-title">
            <h1>Noticias de impacto</h1>
            <p>Centro preparado para conectar un calendario económico en tiempo real.</p>
        </section>
        """
    )

    st.warning(
        "La app todavía no tiene una API de calendario económico configurada. "
        "Por eso no sería responsable mostrar noticias inventadas o desactualizadas."
    )

    st.html(
        """
        <article class="ax-news-card">
            <div class="ax-news-badge">SIGUIENTE INTEGRACIÓN</div>
            <strong>Calendario económico en tiempo real</strong>
            <p>
                Aquí aparecerán eventos de alto impacto, país, hora, previsión,
                dato anterior y resultado real. Para activarlo necesitaremos una
                fuente de datos o API compatible.
            </p>
        </article>

        <article class="ax-news-card">
            <div class="ax-news-badge">CONTROL DE RIESGO</div>
            <strong>Bloqueo preventivo de operaciones</strong>
            <p>
                Podremos avisar cuando falten pocos minutos para una noticia roja
                y marcar las operaciones registradas dentro de una ventana de riesgo.
            </p>
        </article>
        """
    )
