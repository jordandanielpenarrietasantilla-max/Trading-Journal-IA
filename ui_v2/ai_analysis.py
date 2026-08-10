from __future__ import annotations

import html
from typing import Any

import requests
import streamlit as st

from core.config import OPENROUTER_API_KEY, OPENROUTER_MODEL
from core.vision import VisionError, scan_trade


# =========================================================
# AXION PRIME X10 PRO
# AUDITORÍA / ANÁLISIS IA · UI V2
# =========================================================


ANALYSIS_CSS = """
<style>
.ax-ai-hero{
    position:relative;
    overflow:hidden;
    padding:22px 24px;
    margin:0 0 18px 0;
    border:1px solid rgba(89,104,255,.28);
    border-radius:22px;
    background:
      radial-gradient(circle at 85% 15%, rgba(126,74,255,.16), transparent 30%),
      radial-gradient(circle at 10% 90%, rgba(38,204,255,.10), transparent 34%),
      linear-gradient(145deg, rgba(6,13,31,.99), rgba(5,7,23,.99));
    box-shadow:0 24px 70px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.03);
}
.ax-ai-kicker{
    color:#8c7cff;
    font-size:11px;
    font-weight:950;
    letter-spacing:1.7px;
}
.ax-ai-title{
    margin-top:8px;
    color:#f5f7ff;
    font-size:30px;
    line-height:1.05;
    font-weight:950;
    letter-spacing:-.8px;
}
.ax-ai-sub{
    max-width:760px;
    margin-top:9px;
    color:#9eabc7;
    font-size:14px;
    line-height:1.55;
}
.ax-ai-scanner{
    padding:26px;
    margin:8px 0 14px;
    text-align:center;
    border:1px dashed rgba(120,87,255,.72);
    border-radius:20px;
    background:
      radial-gradient(circle at 50% 5%, rgba(113,64,255,.15), transparent 35%),
      linear-gradient(145deg, rgba(9,13,34,.97), rgba(7,9,26,.98));
    box-shadow:inset 0 0 45px rgba(80,54,255,.05);
}
.ax-ai-scanner-icon{
    width:56px;
    height:56px;
    margin:0 auto 13px;
    display:grid;
    place-items:center;
    border:1px solid rgba(127,92,255,.42);
    border-radius:18px;
    background:rgba(112,67,255,.10);
    font-size:26px;
}
.ax-ai-scanner strong{
    display:block;
    color:#f5f7ff;
    font-size:16px;
    font-weight:950;
}
.ax-ai-scanner span{
    display:block;
    max-width:640px;
    margin:8px auto 0;
    color:#91a0bd;
    font-size:12px;
    line-height:1.55;
}
.ax-ai-status{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    padding:12px 15px;
    margin:12px 0;
    border:1px solid rgba(52,215,255,.18);
    border-radius:14px;
    background:rgba(9,18,42,.76);
}
.ax-ai-status-left{
    color:#b6c3dc;
    font-size:12px;
}
.ax-ai-ready{
    color:#35e9a2;
    font-size:11px;
    font-weight:900;
}
.ax-ai-grid{
    display:grid;
    grid-template-columns:repeat(3,minmax(0,1fr));
    gap:12px;
    margin:14px 0;
}
.ax-ai-card{
    min-height:128px;
    padding:16px;
    border:1px solid rgba(75,98,160,.28);
    border-radius:17px;
    background:
      radial-gradient(circle at 100% 0%, rgba(84,71,255,.09), transparent 38%),
      linear-gradient(145deg, rgba(7,14,33,.98), rgba(5,8,24,.98));
}
.ax-ai-card.featured{
    border-color:rgba(123,78,255,.58);
    box-shadow:0 0 28px rgba(108,64,255,.10);
}
.ax-ai-label{
    color:#7f8ca8;
    font-size:9px;
    font-weight:950;
    letter-spacing:1px;
}
.ax-ai-value{
    margin-top:12px;
    color:#f4f7ff;
    font-size:24px;
    font-weight:950;
    line-height:1.05;
    overflow-wrap:anywhere;
}
.ax-ai-value.small{
    font-size:18px;
}
.ax-ai-caption{
    margin-top:9px;
    color:#8fa0bd;
    font-size:11px;
    line-height:1.45;
}
.ax-ai-positive{color:#35e9a2;}
.ax-ai-warning{color:#ffb454;}
.ax-ai-danger{color:#ff647c;}
.ax-ai-score{
    display:flex;
    align-items:end;
    gap:4px;
    margin-top:10px;
}
.ax-ai-score strong{
    color:#f7f9ff;
    font-size:38px;
    line-height:1;
}
.ax-ai-score span{
    color:#8494b4;
    font-size:12px;
    padding-bottom:4px;
}
.ax-ai-bar{
    height:6px;
    margin-top:12px;
    border-radius:999px;
    overflow:hidden;
    background:#18233d;
}
.ax-ai-bar > div{
    height:100%;
    border-radius:999px;
    background:linear-gradient(90deg,#2bdcff,#7454ff,#35e9a2);
}
.ax-ai-summary{
    padding:18px;
    margin-top:14px;
    border:1px solid rgba(70,95,158,.26);
    border-radius:18px;
    background:linear-gradient(145deg,rgba(7,14,33,.98),rgba(5,8,24,.98));
}
.ax-ai-summary h4{
    margin:0 0 10px;
    color:#f4f7ff;
    font-size:13px;
    letter-spacing:.3px;
}
.ax-ai-summary p{
    margin:0;
    color:#a4b1ca;
    font-size:12px;
    line-height:1.65;
}
.ax-ai-minirow{
    display:grid;
    grid-template-columns:repeat(4,minmax(0,1fr));
    gap:10px;
    margin-top:12px;
}
.ax-ai-mini{
    padding:13px;
    border:1px solid rgba(72,96,159,.23);
    border-radius:14px;
    background:rgba(6,12,29,.78);
}
.ax-ai-mini small{
    display:block;
    color:#7584a4;
    font-size:8px;
    font-weight:950;
    letter-spacing:.8px;
}
.ax-ai-mini strong{
    display:block;
    margin-top:7px;
    color:#ecf2ff;
    font-size:15px;
    font-weight:900;
    overflow-wrap:anywhere;
}

.ax-outlook{
    margin-top:16px;
    padding:18px;
    border:1px solid rgba(94,111,255,.32);
    border-radius:18px;
    background:
      radial-gradient(circle at 100% 0%, rgba(121,75,255,.12), transparent 34%),
      linear-gradient(145deg,rgba(7,14,33,.98),rgba(5,8,24,.98));
}
.ax-outlook-head{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:12px;
    margin-bottom:12px;
}
.ax-outlook-title{
    color:#f5f7ff;
    font-size:14px;
    font-weight:950;
}
.ax-outlook-badge{
    color:#9f91ff;
    font-size:9px;
    font-weight:950;
    letter-spacing:1px;
}
.ax-prob-grid{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px;
}
.ax-prob{
    padding:16px;
    border:1px solid rgba(75,98,160,.26);
    border-radius:16px;
    background:rgba(6,12,29,.78);
}
.ax-prob small{
    display:block;
    color:#7f8ca8;
    font-size:9px;
    font-weight:950;
    letter-spacing:.8px;
}
.ax-prob strong{
    display:block;
    margin-top:7px;
    color:#f5f7ff;
    font-size:30px;
    font-weight:950;
}
.ax-prob.good strong{color:#35e9a2;}
.ax-prob.bad strong{color:#ff647c;}
.ax-factors{
    display:grid;
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:12px;
    margin-top:12px;
}
.ax-factor-box{
    padding:15px;
    border:1px solid rgba(75,98,160,.24);
    border-radius:15px;
    background:rgba(6,12,29,.70);
}
.ax-factor-box h5{
    margin:0 0 8px;
    color:#f4f7ff;
    font-size:11px;
}
.ax-factor-box p{
    margin:4px 0;
    color:#a4b1ca;
    font-size:11px;
    line-height:1.5;
}
.ax-disclaimer{
    margin-top:12px;
    color:#70809f;
    font-size:9px;
    line-height:1.5;
}

@media (max-width:900px){
    .ax-ai-grid{grid-template-columns:1fr;}
    .ax-ai-minirow{grid-template-columns:repeat(2,minmax(0,1fr));}
}
</style>
"""


def _safe_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_number(value: Any) -> str:
    number = _safe_float(value)
    if number is None:
        return "No detectado"
    if abs(number) >= 1000:
        return f"{number:,.2f}"
    return f"{number:.5f}".rstrip("0").rstrip(".")


def _clean(value: Any, fallback: str = "No detectado") -> str:
    raw = str(value or "").strip()
    return html.escape(raw if raw else fallback)


def _rr_from_result(result: dict[str, Any]) -> tuple[str, str]:
    entry = _safe_float(result.get("entry"))
    sl = _safe_float(result.get("sl"))
    tp = _safe_float(result.get("tp"))

    if entry is None or sl is None or tp is None:
        return "—", "Faltan precios para calcularlo"

    risk = abs(entry - sl)
    reward = abs(tp - entry)

    if risk <= 0:
        return "—", "Stop Loss no válido para calcular R:R"

    rr = reward / risk
    quality = "R:R favorable" if rr >= 1.5 else "R:R bajo"
    return f"1:{rr:.2f}", quality


def _completeness_score(result: dict[str, Any]) -> int:
    fields = ("asset", "direction", "entry", "sl", "tp", "timeframe")
    present = 0

    for field in fields:
        value = result.get(field)
        if value not in (None, ""):
            present += 1

    completeness = (present / len(fields)) * 100
    confidence = _safe_float(result.get("confidence"))
    if confidence is None:
        confidence = 0.0

    # AXION SCORE = calidad técnica de la lectura, no calidad del trade.
    score = (completeness * 0.55) + (max(0.0, min(confidence, 100.0)) * 0.45)
    return int(round(max(0.0, min(score, 100.0))))


def _missing_fields(result: dict[str, Any]) -> list[str]:
    labels = {
        "asset": "activo",
        "direction": "dirección",
        "entry": "entrada",
        "sl": "Stop Loss",
        "tp": "Take Profit",
        "timeframe": "timeframe",
    }
    missing: list[str] = []
    for field, label in labels.items():
        if result.get(field) in (None, ""):
            missing.append(label)
    return missing


def _render_header() -> None:
    st.html(ANALYSIS_CSS)
    st.html(
        '<section class="ax-ai-hero">'
        '<div class="ax-ai-kicker">AXION PRIME · VISION ENGINE</div>'
        '<div class="ax-ai-title">Auditoría / Análisis IA</div>'
        '<div class="ax-ai-sub">Sube tu gráfico y deja que AXION Vision extraiga los parámetros visibles de la operación. La captura se analiza sin guardarse como trade.</div>'
        '</section>'
    )


def _render_upload_intro() -> None:
    st.html(
        '<section class="ax-ai-scanner">'
        '<div class="ax-ai-scanner-icon">⌁</div>'
        '<strong>SUBE TU GRÁFICO PARA ANALIZARLO</strong>'
        '<span>AXION Vision buscará activo, dirección, entrada, Stop Loss, Take Profit y timeframe visibles en la captura.</span>'
        '</section>'
    )


def _render_results(result: dict[str, Any]) -> None:
    confidence = _safe_float(result.get("confidence")) or 0.0
    confidence = max(0.0, min(confidence, 100.0))
    score = _completeness_score(result)
    rr_value, rr_caption = _rr_from_result(result)
    missing = _missing_fields(result)

    asset = _clean(result.get("asset"))
    direction = _clean(result.get("direction"))
    timeframe = _clean(result.get("timeframe"))
    entry = html.escape(_format_number(result.get("entry")))
    sl = html.escape(_format_number(result.get("sl")))
    tp = html.escape(_format_number(result.get("tp")))

    if missing:
        issue_count = len(missing)
        issue_class = "ax-ai-warning" if issue_count <= 2 else "ax-ai-danger"
        issue_text = f"{issue_count} campo{'s' if issue_count != 1 else ''} sin detectar"
        issue_detail = "Falta: " + ", ".join(missing)
    else:
        issue_class = "ax-ai-positive"
        issue_text = "Lectura completa"
        issue_detail = "Todos los parámetros principales fueron detectados."

    quality_label = (
        "Lectura alta" if score >= 80
        else "Lectura media" if score >= 55
        else "Lectura parcial"
    )

    st.html(
        '<div class="ax-ai-status">'
        '<div class="ax-ai-status-left">RESULTADOS DEL ANÁLISIS</div>'
        '<div class="ax-ai-ready">● LECTURA COMPLETADA</div>'
        '</div>'
    )

    st.html(
        '<div class="ax-ai-grid">'
        f'<div class="ax-ai-card"><div class="ax-ai-label">ACTIVO DETECTADO</div><div class="ax-ai-value small">{asset}</div><div class="ax-ai-caption">Instrumento identificado en la captura.</div></div>'
        f'<div class="ax-ai-card"><div class="ax-ai-label">DIRECCIÓN</div><div class="ax-ai-value">{direction}</div><div class="ax-ai-caption">Sesgo visible de la operación.</div></div>'
        f'<div class="ax-ai-card"><div class="ax-ai-label">CONFIANZA DE VISIÓN</div><div class="ax-ai-score"><strong>{confidence:.0f}</strong><span>/100</span></div><div class="ax-ai-bar"><div style="width:{confidence:.0f}%"></div></div></div>'
        f'<div class="ax-ai-card"><div class="ax-ai-label">R:R IDENTIFICADO</div><div class="ax-ai-value">{html.escape(rr_value)}</div><div class="ax-ai-caption">{html.escape(rr_caption)}</div></div>'
        f'<div class="ax-ai-card"><div class="ax-ai-label">VALIDACIÓN DE DATOS</div><div class="ax-ai-value small {issue_class}">{html.escape(issue_text)}</div><div class="ax-ai-caption">{html.escape(issue_detail)}</div></div>'
        f'<div class="ax-ai-card featured"><div class="ax-ai-label">AXION SCORE · CALIDAD DE LECTURA</div><div class="ax-ai-score"><strong>{score}</strong><span>/100</span></div><div class="ax-ai-caption">{quality_label}. Este score mide detección y confianza, no la calidad de tu estrategia.</div></div>'
        '</div>'
    )

    st.html(
        '<div class="ax-ai-minirow">'
        f'<div class="ax-ai-mini"><small>ENTRADA</small><strong>{entry}</strong></div>'
        f'<div class="ax-ai-mini"><small>STOP LOSS</small><strong>{sl}</strong></div>'
        f'<div class="ax-ai-mini"><small>TAKE PROFIT</small><strong>{tp}</strong></div>'
        f'<div class="ax-ai-mini"><small>TIMEFRAME</small><strong>{timeframe}</strong></div>'
        '</div>'
    )

    if missing:
        summary = (
            "AXION Vision pudo leer parte de la configuración visible. "
            "Para mejorar la precisión, usa una captura donde se distingan claramente "
            "el activo, timeframe y niveles de entrada, SL y TP."
        )
    else:
        summary = (
            "La lectura visual contiene los parámetros principales de la operación. "
            "Revisa los valores detectados antes de utilizarlos: el análisis depende de "
            "lo que sea visible y legible en la captura."
        )

    st.html(
        '<section class="ax-ai-summary">'
        '<h4>RESUMEN DE LA AUDITORÍA</h4>'
        f'<p>{html.escape(summary)}</p>'
        '</section>'
    )

    with st.expander("Ver datos técnicos detectados", expanded=False):
        st.json(result)



def _history_context(df: Any) -> str:
    """
    Construye un resumen muy breve del historial real del trader.
    Se usa solo como contexto adicional si el DataFrame existe.
    """

    try:
        if df is None or len(df) < 5:
            return "No hay historial suficiente para usar estadísticas personales."

        total = len(df)

        win_col = None
        for candidate in (
            "resultado",
            "result",
            "outcome",
        ):
            if candidate in df.columns:
                win_col = candidate
                break

        pnl_col = None
        for candidate in (
            "pnl",
            "PnL",
            "profit_loss",
            "resultado_usd",
        ):
            if candidate in df.columns:
                pnl_col = candidate
                break

        win_rate = None

        if win_col:
            series = (
                df[win_col]
                .astype(str)
                .str.lower()
            )
            winners = series.str.contains(
                "win|ganador|winner|profit"
            ).sum()
            win_rate = (
                winners / total * 100
                if total
                else None
            )

        if win_rate is None and pnl_col:
            pnl = df[pnl_col]
            try:
                winners = (pnl.astype(float) > 0).sum()
                win_rate = winners / total * 100
            except Exception:
                win_rate = None

        if win_rate is None:
            return (
                f"Historial disponible: {total} trades. "
                "No se pudo calcular un win rate fiable."
            )

        return (
            f"Historial disponible: {total} trades. "
            f"Win rate histórico aproximado: {win_rate:.1f}%."
        )

    except Exception:
        return "No se pudo resumir el historial del usuario."


def _build_outlook_prompt(
    result: dict[str, Any],
    history_summary: str,
) -> str:
    """
    Pide un análisis probabilístico prudente.

    Importante: la IA debe tratar la probabilidad como estimación,
    no como estadística garantizada derivada de una sola captura.
    """

    return f"""
Eres AXION TRADE OUTLOOK, un analista de riesgo para traders.

Analiza SOLO la información visible ya extraída de una captura de trading.
No inventes indicadores, noticias, order flow, volumen, contexto macro,
niveles técnicos o confirmaciones que no estén presentes en los datos.

DATOS DETECTADOS:
Activo: {result.get("asset")}
Dirección: {result.get("direction")}
Entrada: {result.get("entry")}
Stop Loss: {result.get("sl")}
Take Profit: {result.get("tp")}
Timeframe: {result.get("timeframe")}
Confianza de visión: {result.get("confidence")}

HISTORIAL DEL TRADER:
{history_summary}

Tu tarea:
1. Da una probabilidad ESTIMADA favorable y desfavorable que sumen 100.
2. Si la captura/datos son insuficientes, acerca las probabilidades a 50/50.
3. Nunca presentes la probabilidad como certeza matemática.
4. Explica brevemente qué factores visibles apoyan o debilitan el trade.
5. Da una conclusión prudente.
6. No des órdenes directas de comprar/vender.
7. No prometas ganancias.

Responde EXCLUSIVAMENTE en JSON válido con esta estructura exacta:
{{
  "prob_favorable": 55,
  "prob_desfavorable": 45,
  "confianza_analisis": 62,
  "setup_score": 68,
  "lectura": "texto breve",
  "a_favor": ["factor 1", "factor 2"],
  "en_contra": ["factor 1", "factor 2"],
  "conclusion": "texto breve"
}}
""".strip()


def _request_trade_outlook(
    result: dict[str, Any],
    df: Any = None,
) -> dict[str, Any]:
    api_key = str(
        OPENROUTER_API_KEY
        or ""
    ).strip()

    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY no está configurada."
        )

    model = str(
        OPENROUTER_MODEL
        or "google/gemini-2.5-flash"
    ).strip()

    prompt = _build_outlook_prompt(
        result,
        _history_context(df),
    )

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "temperature": 0.2,
            "max_tokens": 650,
        },
        timeout=45,
    )

    if response.status_code >= 400:
        raise RuntimeError(
            f"OpenRouter HTTP {response.status_code}"
        )

    payload = response.json()
    content = (
        payload.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    raw = str(
        content or ""
    ).strip()

    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    import json

    data = json.loads(raw)

    favorable = int(
        round(
            float(
                data.get("prob_favorable", 50)
            )
        )
    )
    favorable = max(
        1,
        min(
            favorable,
            99,
        ),
    )

    unfavorable = 100 - favorable

    confidence = int(
        round(
            float(
                data.get(
                    "confianza_analisis",
                    50,
                )
            )
        )
    )
    confidence = max(
        0,
        min(
            confidence,
            100,
        ),
    )

    score = int(
        round(
            float(
                data.get(
                    "setup_score",
                    50,
                )
            )
        )
    )
    score = max(
        0,
        min(
            score,
            100,
        ),
    )

    return {
        "prob_favorable": favorable,
        "prob_desfavorable": unfavorable,
        "confianza_analisis": confidence,
        "setup_score": score,
        "lectura": str(
            data.get("lectura")
            or ""
        ).strip(),
        "a_favor": [
            str(item).strip()
            for item in (
                data.get("a_favor")
                or []
            )
            if str(item).strip()
        ][:4],
        "en_contra": [
            str(item).strip()
            for item in (
                data.get("en_contra")
                or []
            )
            if str(item).strip()
        ][:4],
        "conclusion": str(
            data.get("conclusion")
            or ""
        ).strip(),
    }


def _render_trade_outlook(
    outlook: dict[str, Any],
) -> None:
    favorable = int(
        outlook.get(
            "prob_favorable",
            50,
        )
    )
    unfavorable = int(
        outlook.get(
            "prob_desfavorable",
            50,
        )
    )
    confidence = int(
        outlook.get(
            "confianza_analisis",
            50,
        )
    )
    score = int(
        outlook.get(
            "setup_score",
            50,
        )
    )

    if score >= 75:
        setup_label = "Setup favorable"
    elif score >= 55:
        setup_label = "Setup mixto"
    else:
        setup_label = "Setup débil"

    st.html(
        '<section class="ax-outlook">'
        '<div class="ax-outlook-head">'
        '<div class="ax-outlook-title">AXION TRADE OUTLOOK</div>'
        '<div class="ax-outlook-badge">ESTIMACIÓN ANALÍTICA</div>'
        '</div>'
        '<div class="ax-prob-grid">'
        f'<div class="ax-prob good"><small>PROBABILIDAD FAVORABLE ESTIMADA</small><strong>{favorable}%</strong></div>'
        f'<div class="ax-prob bad"><small>PROBABILIDAD DESFAVORABLE ESTIMADA</small><strong>{unfavorable}%</strong></div>'
        '</div>'
        '<div class="ax-ai-minirow">'
        f'<div class="ax-ai-mini"><small>CONFIANZA DEL ANÁLISIS</small><strong>{confidence}/100</strong></div>'
        f'<div class="ax-ai-mini"><small>AXION SETUP SCORE</small><strong>{score}/100</strong></div>'
        f'<div class="ax-ai-mini"><small>LECTURA</small><strong>{html.escape(setup_label)}</strong></div>'
        '<div class="ax-ai-mini"><small>MODELO</small><strong>IA + Datos visibles</strong></div>'
        '</div>'
    )

    lectura = str(
        outlook.get("lectura")
        or ""
    ).strip()

    if lectura:
        st.html(
            '<div class="ax-ai-summary">'
            '<h4>LECTURA DE AXION</h4>'
            f'<p>{html.escape(lectura)}</p>'
            '</div>'
        )

    favor = outlook.get(
        "a_favor",
        [],
    )
    contra = outlook.get(
        "en_contra",
        [],
    )

    favor_html = "".join(
        f'<p>✓ {html.escape(str(item))}</p>'
        for item in favor
    ) or "<p>Sin factores claros detectados.</p>"

    contra_html = "".join(
        f'<p>⚠ {html.escape(str(item))}</p>'
        for item in contra
    ) or "<p>Sin factores claros detectados.</p>"

    st.html(
        '<div class="ax-factors">'
        '<div class="ax-factor-box">'
        '<h5>✅ A FAVOR</h5>'
        f'{favor_html}'
        '</div>'
        '<div class="ax-factor-box">'
        '<h5>⚠️ EN CONTRA</h5>'
        f'{contra_html}'
        '</div>'
        '</div>'
    )

    conclusion = str(
        outlook.get("conclusion")
        or ""
    ).strip()

    if conclusion:
        st.html(
            '<div class="ax-ai-summary">'
            '<h4>CONCLUSIÓN AXION</h4>'
            f'<p>{html.escape(conclusion)}</p>'
            '</div>'
        )

    st.html(
        '<div class="ax-disclaimer">'
        'Las probabilidades mostradas son estimaciones analíticas basadas en '
        'los datos visibles y, cuando existe suficiente historial, en métricas '
        'del usuario. No garantizan el resultado de una operación.'
        '</div>'
        '</section>'
    )



def render_ai_analysis(df: Any = None) -> None:
    """
    Interfaz premium para el escáner visual de AXION PRIME.

    Conserva la lógica real de core.vision.scan_trade():
    no inventa setups, errores estratégicos ni recomendaciones
    que el motor actual no entregue.
    """

    _render_header()
    _render_upload_intro()

    chart = st.file_uploader(
        "Seleccionar captura del gráfico",
        type=["png", "jpg", "jpeg", "webp"],
        key="v2_analysis_chart",
        help="PNG, JPG, JPEG o WEBP.",
    )

    if chart is None:
        st.html(
            '<div class="ax-ai-status">'
            '<div class="ax-ai-status-left">Esperando una captura clara del gráfico.</div>'
            '<div class="ax-ai-ready" style="color:#8fa0bd">○ LISTO PARA ANALIZAR</div>'
            '</div>'
        )
        return

    st.image(
        chart,
        caption="Vista previa · captura seleccionada",
        use_container_width=True,
    )

    analyze = st.button(
        "⚡ ANALIZAR CON AXION VISION",
        use_container_width=True,
        type="primary",
        key="v2_analysis_scan_button",
    )

    if not analyze:
        return

    try:
        with st.spinner("AXION Vision está leyendo el gráfico..."):
            result = scan_trade(
                chart.getvalue(),
                chart.type or "image/jpeg",
            )

        if not isinstance(result, dict):
            raise VisionError("El motor visual devolvió una respuesta no válida.")

        st.session_state["v2_last_vision_result"] = result
        _render_results(result)

        try:
            with st.spinner("AXION está evaluando el contexto del setup..."):
                outlook = _request_trade_outlook(
                    result,
                    df=df,
                )

            st.session_state["v2_last_trade_outlook"] = outlook
            _render_trade_outlook(outlook)

        except Exception:
            st.info(
                "La lectura visual se completó correctamente, "
                "pero AXION Trade Outlook no pudo generar la "
                "estimación probabilística en este momento."
            )

    except VisionError as exc:
        st.error(
            "No se pudo completar la lectura visual. "
            f"Detalle: {exc}"
        )

    except Exception as exc:
        st.error(
            "Ocurrió un error inesperado al analizar la captura. "
            f"Detalle: {exc}"
        )
