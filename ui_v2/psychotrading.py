from __future__ import annotations

import html
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.metrics import pnl_by_emotion


# =========================================================
# AXION PRIME X10 PRO · PSICOTRADING PREMIUM
# =========================================================


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value or 0.0)
    except (TypeError, ValueError):
        return default


def _money(value: Any) -> str:
    number = _safe_float(value)
    sign = "+" if number > 0 else ""
    return f"{sign}${number:,.2f}"


def _clean_emotion(value: Any) -> str:
    text = str(value or "Sin registrar").strip()
    replacements = {
        "🧘": "",
        "⚡": "",
        "🚀": "",
        "🛑": "",
        "😎": "",
        "😨": "",
        "⏳": "",
    }
    for icon, replacement in replacements.items():
        text = text.replace(icon, replacement)
    return " ".join(text.split())


def _emotion_profile(value: Any) -> dict[str, float | str]:
    """Traduce el estado registrado a señales psicológicas simples y transparentes."""
    emotion = str(value or "").lower()

    if "disciplin" in emotion or "neutro" in emotion:
        return {
            "discipline": 92,
            "fomo_control": 92,
            "confidence": 82,
            "emotional_control": 92,
            "label": "FOCALIZADO",
        }
    if "ansios" in emotion:
        return {
            "discipline": 60,
            "fomo_control": 58,
            "confidence": 56,
            "emotional_control": 48,
            "label": "ALERTA",
        }
    if "fomo" in emotion:
        return {
            "discipline": 38,
            "fomo_control": 22,
            "confidence": 66,
            "emotional_control": 35,
            "label": "IMPULSIVO",
        }
    if "frustr" in emotion or "venganza" in emotion:
        return {
            "discipline": 28,
            "fomo_control": 30,
            "confidence": 38,
            "emotional_control": 20,
            "label": "RIESGO ALTO",
        }
    if "euf" in emotion or "sobreconfi" in emotion:
        return {
            "discipline": 48,
            "fomo_control": 42,
            "confidence": 94,
            "emotional_control": 46,
            "label": "SOBRECONFIADO",
        }
    if "miedo" in emotion:
        return {
            "discipline": 56,
            "fomo_control": 72,
            "confidence": 30,
            "emotional_control": 42,
            "label": "CAUTELOSO",
        }
    if "impaciente" in emotion:
        return {
            "discipline": 44,
            "fomo_control": 38,
            "confidence": 58,
            "emotional_control": 36,
            "label": "IMPACIENTE",
        }

    return {
        "discipline": 50,
        "fomo_control": 50,
        "confidence": 50,
        "emotional_control": 50,
        "label": "SIN DATOS",
    }


def _calculate_scores(df: pd.DataFrame) -> dict[str, float | str]:
    """
    Calcula indicadores usando únicamente los estados emocionales guardados.
    Los valores no son diagnósticos clínicos: son un índice interno de consistencia.
    """
    if df.empty or "emocion" not in df.columns:
        return {
            "mental": 0,
            "discipline": 0,
            "fomo_control": 0,
            "confidence": 0,
            "emotional_control": 0,
            "dominant": "Sin datos",
            "status": "SIN DATOS",
        }

    emotions = df["emocion"].dropna().astype(str)
    emotions = emotions[emotions.str.strip() != ""]
    if emotions.empty:
        return {
            "mental": 0,
            "discipline": 0,
            "fomo_control": 0,
            "confidence": 0,
            "emotional_control": 0,
            "dominant": "Sin datos",
            "status": "SIN DATOS",
        }

    # Da más peso a las 10 operaciones más recientes sin inventar información externa.
    recent = emotions.tail(10)
    profiles = [_emotion_profile(value) for value in recent]

    discipline = sum(float(p["discipline"]) for p in profiles) / len(profiles)
    fomo_control = sum(float(p["fomo_control"]) for p in profiles) / len(profiles)
    confidence = sum(float(p["confidence"]) for p in profiles) / len(profiles)
    emotional_control = sum(float(p["emotional_control"]) for p in profiles) / len(profiles)

    mental = (
        discipline * 0.35
        + fomo_control * 0.20
        + confidence * 0.20
        + emotional_control * 0.25
    )

    dominant_raw = emotions.value_counts().index[0]
    current_profile = _emotion_profile(recent.iloc[-1])

    return {
        "mental": round(mental),
        "discipline": round(discipline),
        "fomo_control": round(fomo_control),
        "confidence": round(confidence),
        "emotional_control": round(emotional_control),
        "dominant": _clean_emotion(dominant_raw),
        "status": str(current_profile["label"]),
    }


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .block-container{max-width:1600px;padding-top:.9rem;padding-bottom:2rem}
        .ax-psy-wrap{position:relative}
        .ax-psy-hero{padding:24px 26px;margin-bottom:18px;border:1px solid rgba(83,98,255,.38);border-radius:22px;background:radial-gradient(circle at 90% 10%,rgba(120,64,255,.13),transparent 28%),linear-gradient(145deg,rgba(7,14,34,.98),rgba(6,7,25,.98));box-shadow:0 24px 72px rgba(0,0,0,.28)}
        .ax-psy-kicker{color:#39d9ff;font-size:9px;font-weight:900;letter-spacing:2.5px;text-transform:uppercase}
        .ax-psy-title{margin-top:7px;color:#f4f7ff;font-size:30px;font-weight:900;letter-spacing:-.7px}
        .ax-psy-sub{max-width:900px;margin-top:8px;color:#9ba9c4;font-size:13px;line-height:1.65}
        .ax-card{height:100%;padding:20px;border:1px solid rgba(83,98,180,.30);border-radius:18px;background:linear-gradient(145deg,rgba(10,18,42,.96),rgba(7,9,27,.96));box-shadow:0 18px 48px rgba(0,0,0,.22)}
        .ax-card-label{color:#7183a8;font-size:8px;font-weight:900;letter-spacing:1.7px;text-transform:uppercase}
        .ax-state{margin-top:9px;color:#37f4ad;font-size:11px;font-weight:900;letter-spacing:.8px}
        .ax-dominant{margin-top:10px;color:#f5f7ff;font-size:18px;font-weight:900}
        .ax-dominant span{color:#a6b6d5;font-size:11px;font-weight:600}
        .ax-quote{margin-top:14px;padding-top:14px;border-top:1px solid rgba(94,116,175,.18);color:#a8b4cc;font-size:11px;line-height:1.6}
        .ax-pillar{padding:16px;border:1px solid rgba(82,105,180,.25);border-radius:14px;background:rgba(7,12,31,.82)}
        .ax-pillar-name{color:#a9b7d1;font-size:10px;font-weight:700}
        .ax-pillar-value{margin-top:8px;color:#f6f8ff;font-size:27px;font-weight:900;letter-spacing:-1px}.ax-pillar-value span{font-size:10px;color:#7f91b3;font-weight:700}
        .ax-bar{height:5px;margin-top:11px;overflow:hidden;border-radius:999px;background:#18213a}.ax-bar>div{height:100%;border-radius:999px;background:linear-gradient(90deg,#26d9ff,#6d5cff,#39f0a8)}
        .ax-mini-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:14px 0 18px}
        .ax-section{margin-top:16px;padding:20px;border:1px solid rgba(82,105,180,.25);border-radius:18px;background:linear-gradient(145deg,rgba(8,14,34,.94),rgba(6,8,25,.94))}
        .ax-section-title{color:#eef3ff;font-size:13px;font-weight:900}.ax-section-sub{margin-top:4px;color:#7485a6;font-size:9px}
        .ax-stat-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:14px 0}
        .ax-stat{padding:14px;border:1px solid rgba(82,105,180,.23);border-radius:13px;background:rgba(5,10,28,.72)}
        .ax-stat small{display:block;color:#7183a8;font-size:8px}.ax-stat strong{display:block;margin-top:7px;color:#f5f7ff;font-size:18px;overflow-wrap:anywhere}.ax-stat em{display:block;margin-top:5px;color:#39e5a5;font-size:9px;font-style:normal}
        div[data-testid="stTextArea"] textarea{min-height:135px!important;border:1px solid rgba(83,98,255,.42)!important;border-radius:14px!important;background:rgba(6,8,28,.92)!important;color:#edf2ff!important}
        div[data-testid="stTextArea"] textarea:focus{border-color:#5e68ff!important;box-shadow:0 0 0 1px #5e68ff,0 0 28px rgba(96,84,255,.12)!important}
        div.stButton>button{min-height:44px;border:1px solid rgba(91,109,255,.48);border-radius:12px;background:linear-gradient(90deg,#594bff,#6f55ff,#287fff);color:white;font-weight:850}
        div.stButton>button:hover{border-color:#64dfff;box-shadow:0 0 25px rgba(73,108,255,.20);color:white}
        @media(max-width:900px){.ax-mini-grid,.ax-stat-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _gauge(score: float) -> go.Figure:
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": "/100", "font": {"size": 34, "color": "#F4F7FF"}},
            gauge={
                "axis": {"range": [0, 100], "visible": False},
                "bar": {"color": "#38D6FF", "thickness": 0.16},
                "bgcolor": "rgba(18,27,55,.75)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 45], "color": "rgba(255,85,110,.10)"},
                    {"range": [45, 70], "color": "rgba(126,90,255,.09)"},
                    {"range": [70, 100], "color": "rgba(47,239,167,.10)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=235,
        margin=dict(l=20, r=20, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Arial"},
    )
    return fig


def _trend_chart(df: pd.DataFrame) -> go.Figure:
    source = df.copy()
    if "created_at_dt" in source.columns and source["created_at_dt"].notna().any():
        source = source.sort_values("created_at_dt")
    elif "fecha_dt" in source.columns and source["fecha_dt"].notna().any():
        source = source.sort_values("fecha_dt")

    source = source.tail(10).reset_index(drop=True)
    x = list(range(1, len(source) + 1))

    discipline, confidence, control, fomo_control = [], [], [], []
    for emotion in source.get("emocion", pd.Series([""] * len(source))).fillna(""):
        profile = _emotion_profile(emotion)
        discipline.append(profile["discipline"])
        confidence.append(profile["confidence"])
        control.append(profile["emotional_control"])
        fomo_control.append(profile["fomo_control"])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=discipline, mode="lines+markers", name="Disciplina"))
    fig.add_trace(go.Scatter(x=x, y=confidence, mode="lines+markers", name="Confianza"))
    fig.add_trace(go.Scatter(x=x, y=control, mode="lines+markers", name="Control emocional"))
    fig.add_trace(go.Scatter(x=x, y=fomo_control, mode="lines+markers", name="Control FOMO"))
    fig.update_layout(
        height=350,
        margin=dict(l=15, r=15, t=20, b=15),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(5,10,28,.40)",
        font={"color": "#9BA9C4", "size": 10},
        legend=dict(orientation="h", y=-0.20),
        xaxis=dict(title="Últimas operaciones", gridcolor="rgba(90,110,170,.10)", dtick=1),
        yaxis=dict(range=[0, 100], title="Índice", gridcolor="rgba(90,110,170,.12)"),
        hovermode="x unified",
    )
    return fig


def render_psychotrading(df: pd.DataFrame) -> None:
    _inject_styles()

    scores = _calculate_scores(df)

    st.markdown(
        """
        <div class="ax-psy-wrap">
            <section class="ax-psy-hero">
                <div class="ax-psy-kicker">AXION PRIME · BEHAVIOR INTELLIGENCE</div>
                <div class="ax-psy-title">🧠 Psicotrading</div>
                <div class="ax-psy-sub">Conoce cómo tus emociones están influyendo en tus decisiones. Convierte cada operación en información para fortalecer disciplina, confianza y control.</div>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df.empty or "emocion" not in df.columns or df["emocion"].dropna().empty:
        st.info("Registra operaciones con estado emocional para desbloquear el panel de Psicotrading.")
        reflection = st.text_area(
            "Reflexión de la sesión",
            height=150,
            placeholder="¿Cómo te sentiste hoy? ¿Seguiste tu plan? ¿Operaste por impulso, miedo o FOMO?",
            key="psychology_reflection_v2",
        )
        if st.button("💾 Guardar reflexión", use_container_width=True, key="save_psy_reflection_v2_empty"):
            st.session_state.last_reflection = reflection
            st.success("Reflexión guardada durante esta sesión.")
        return

    left, right = st.columns([0.38, 0.62], gap="large")

    with left:
        st.markdown('<div class="ax-card"><div class="ax-card-label">Estado mental · últimas operaciones</div>', unsafe_allow_html=True)
        st.plotly_chart(_gauge(float(scores["mental"])), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        status = html.escape(str(scores["status"]))
        dominant = html.escape(str(scores["dominant"]))
        st.markdown(
            f"""
            <div class="ax-card">
                <div class="ax-card-label">Lectura conductual</div>
                <div class="ax-state">● {status}</div>
                <div class="ax-dominant"><span>Emoción dominante</span><br>{dominant}</div>
                <div class="ax-quote">“La consistencia no depende de sentir menos, sino de reconocer tu estado antes de convertirlo en una decisión.”</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    pillar_values = [
        ("Disciplina", int(scores["discipline"])),
        ("Control FOMO", int(scores["fomo_control"])),
        ("Confianza", int(scores["confidence"])),
        ("Control emocional", int(scores["emotional_control"])),
    ]

    pillar_html = '<div class="ax-mini-grid">'
    for label, value in pillar_values:
        pillar_html += f"""
        <div class="ax-pillar">
            <div class="ax-pillar-name">{html.escape(label)}</div>
            <div class="ax-pillar-value">{value}<span>/100</span></div>
            <div class="ax-bar"><div style="width:{max(0,min(value,100))}%"></div></div>
        </div>
        """
    pillar_html += "</div>"
    st.markdown(pillar_html, unsafe_allow_html=True)

    st.markdown(
        '<div class="ax-section"><div class="ax-section-title">Evolución emocional</div><div class="ax-section-sub">Lectura de las últimas 10 operaciones registradas.</div></div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(_trend_chart(df), use_container_width=True, config={"displayModeBar": False})

    emotion_df = pnl_by_emotion(df)
    if not emotion_df.empty:
        emotion_df = emotion_df.copy()
        emotion_df["emocion_limpia"] = emotion_df["emocion"].map(_clean_emotion)
        best_row = emotion_df.sort_values("pnl_total", ascending=False).iloc[0]
        worst_row = emotion_df.sort_values("pnl_total", ascending=True).iloc[0]
        total_trades = int(emotion_df["trades"].sum())

        stats_html = f"""
        <div class="ax-stat-grid">
            <div class="ax-stat"><small>TRADES ANALIZADOS</small><strong>{total_trades}</strong><em>Con estado emocional</em></div>
            <div class="ax-stat"><small>ESTADOS DETECTADOS</small><strong>{len(emotion_df)}</strong><em>Patrones registrados</em></div>
            <div class="ax-stat"><small>MEJOR ESTADO</small><strong>{html.escape(str(best_row['emocion_limpia']))}</strong><em>{_money(best_row['pnl_total'])}</em></div>
            <div class="ax-stat"><small>ESTADO A REVISAR</small><strong>{html.escape(str(worst_row['emocion_limpia']))}</strong><em>{_money(worst_row['pnl_total'])}</em></div>
        </div>
        """
        st.markdown(stats_html, unsafe_allow_html=True)

        bar_fig = go.Figure()
        bar_fig.add_trace(
            go.Bar(
                x=emotion_df["emocion_limpia"],
                y=emotion_df["pnl_total"],
                customdata=emotion_df[["trades", "pnl_promedio"]],
                hovertemplate="%{x}<br>PnL: $%{y:,.2f}<br>Trades: %{customdata[0]}<br>Promedio: $%{customdata[1]:,.2f}<extra></extra>",
            )
        )
        bar_fig.update_layout(
            title="PnL acumulado por estado emocional",
            height=360,
            margin=dict(l=15, r=15, t=50, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(5,10,28,.40)",
            font={"color": "#9BA9C4", "size": 10},
            xaxis=dict(title="", gridcolor="rgba(90,110,170,.08)"),
            yaxis=dict(title="PnL", gridcolor="rgba(90,110,170,.12)"),
        )
        st.plotly_chart(bar_fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown(
        '<div class="ax-section"><div class="ax-section-title">Reflexión de la sesión</div><div class="ax-section-sub">Registra lo que ocurrió fuera del gráfico: impulso, paciencia, miedo, confianza y disciplina.</div></div>',
        unsafe_allow_html=True,
    )
    reflection = st.text_area(
        "Reflexión de la sesión",
        height=155,
        placeholder="¿Cómo te sentiste hoy? ¿Seguiste tu plan? ¿Operaste por impulso, miedo o FOMO?",
        key="psychology_reflection_v2",
        label_visibility="collapsed",
    )

    if st.button("💾 Guardar reflexión", use_container_width=True, key="save_psy_reflection_v2"):
        st.session_state.last_reflection = reflection
        st.success("Reflexión guardada durante esta sesión.")

    st.caption("Los índices psicológicos son una lectura interna de consistencia basada en los estados emocionales registrados; no constituyen una evaluación clínica.")
