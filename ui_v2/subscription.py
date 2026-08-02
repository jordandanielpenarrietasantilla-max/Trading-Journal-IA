from __future__ import annotations

import datetime as dt
import html
from typing import Any

import streamlit as st

from ui_v2.theme import apply_v2_theme


SUBSCRIPTION_CSS = """
<style>
.block-container{max-width:1600px;padding-top:1rem;padding-bottom:2rem}
.ax-sub-stage{position:relative;isolation:isolate}
.ax-sub-stage:before{content:"";position:fixed;inset:0 0 0 200px;z-index:-2;pointer-events:none;background:radial-gradient(circle at 82% 8%,rgba(130,78,255,.14),transparent 24%),radial-gradient(circle at 60% 55%,rgba(39,216,255,.07),transparent 30%),linear-gradient(180deg,#030713 0%,#050419 58%,#030711 100%)}
.ax-sub-stage:after{content:"";position:fixed;inset:0 0 0 200px;z-index:-1;pointer-events:none;opacity:.16;background-image:linear-gradient(rgba(62,91,166,.055) 1px,transparent 1px),linear-gradient(90deg,rgba(62,91,166,.055) 1px,transparent 1px);background-size:44px 44px}
.ax-sub-hero{position:relative;overflow:hidden;min-height:320px;padding:38px 42px;margin-bottom:18px;border:1px solid rgba(81,91,255,.48);border-radius:24px;background:radial-gradient(circle at 88% 8%,rgba(255,70,205,.14),transparent 27%),radial-gradient(circle at 74% 34%,rgba(42,216,255,.12),transparent 31%),linear-gradient(145deg,rgba(5,12,31,.99),rgba(6,7,25,.99));box-shadow:0 28px 90px rgba(0,0,0,.42),0 0 46px rgba(78,74,255,.10),inset 0 1px 0 rgba(255,255,255,.045)}
.ax-sub-hero:before{content:"";position:absolute;inset:0;background:linear-gradient(rgba(60,91,170,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(60,91,170,.04) 1px,transparent 1px);background-size:40px 40px}
.ax-sub-hero-copy{position:relative;z-index:3;max-width:59%}
.ax-sub-kicker{color:#2bdcff;font-size:9px;font-weight:950;letter-spacing:2.7px}
.ax-sub-title{margin-top:14px;font-size:clamp(48px,5vw,80px);line-height:.92;font-weight:950;letter-spacing:-4px;background:linear-gradient(90deg,#c043ff,#815dff 30%,#3ba8ff 68%,#2bdcff);-webkit-background-clip:text;background-clip:text;color:transparent}
.ax-sub-slogan{margin-top:16px;color:#eef3ff;font-size:18px;font-weight:850}
.ax-sub-description{max-width:700px;margin-top:10px;color:#9eacc7;font-size:12px;line-height:1.65}
.ax-trial-badge{display:inline-flex;margin-top:20px;padding:9px 13px;color:#31ff9c;font-size:8px;font-weight:950;letter-spacing:.8px;background:rgba(49,255,156,.07);border:1px solid rgba(49,255,156,.32);border-radius:999px}
.ax-sub-orb{position:absolute;right:7%;top:50%;width:250px;height:250px;transform:translateY(-50%);border-radius:50%;background:radial-gradient(circle at 38% 34%,rgba(255,255,255,.30),transparent 4%),radial-gradient(circle,rgba(39,216,255,.19) 0 16%,transparent 17%),radial-gradient(circle,transparent 0 34%,rgba(75,102,255,.44) 35% 36%,transparent 37%),radial-gradient(circle,transparent 0 49%,rgba(190,60,255,.38) 50% 51%,transparent 52%),radial-gradient(circle,rgba(42,61,185,.35),rgba(8,10,35,.05) 66%,transparent 67%);border:1px solid rgba(89,91,255,.50);box-shadow:0 0 30px rgba(39,216,255,.24),0 0 72px rgba(123,92,255,.34),inset 0 0 38px rgba(39,216,255,.16);animation:axSubOrb 5s ease-in-out infinite alternate}
.ax-sub-orb:before,.ax-sub-orb:after{content:"";position:absolute;inset:-24px;border-radius:50%;border:1px solid rgba(112,86,255,.30)}
.ax-sub-orb:after{inset:-48px;border-color:rgba(39,216,255,.18)}
@keyframes axSubOrb{from{transform:translateY(-50%) scale(.96) rotate(0)}to{transform:translateY(-50%) scale(1.04) rotate(8deg)}}
.ax-status-grid{display:grid;grid-template-columns:1.2fr .8fr .8fr;gap:12px;margin-bottom:16px}
.ax-status-card{padding:16px;border:1px solid rgba(68,98,165,.30);border-radius:15px;background:radial-gradient(circle at 100% 0%,rgba(39,216,255,.08),transparent 38%),linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99))}
.ax-status-card small{display:block;color:#7889aa;font-size:7px;font-weight:900;letter-spacing:.8px}.ax-status-card strong{display:block;margin-top:8px;color:#eef4ff;font-size:23px;font-weight:950}.ax-status-card span{display:block;margin-top:7px;color:#93a6c7;font-size:8px}
.ax-progress{height:7px;margin-top:12px;overflow:hidden;border-radius:999px;background:rgba(255,255,255,.06)}.ax-progress>div{height:100%;width:var(--progress);background:linear-gradient(90deg,#2bdcff,#725cff,#ff4bd0);box-shadow:0 0 14px rgba(113,92,255,.38)}
.ax-plan-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin-top:16px}
.ax-plan-card{position:relative;overflow:hidden;min-height:560px;padding:24px;border-radius:20px;background:radial-gradient(circle at 100% 0%,rgba(var(--rgb),.15),transparent 38%),linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99));border:1px solid rgba(var(--rgb),.45);box-shadow:0 20px 56px rgba(0,0,0,.30);transition:.25s}
.ax-plan-card:hover{transform:translateY(-6px);border-color:rgba(var(--rgb),.90);box-shadow:0 26px 68px rgba(0,0,0,.38),0 0 34px rgba(var(--rgb),.13)}
.ax-plan-card.popular{border-color:rgba(255,191,56,.66);box-shadow:0 24px 70px rgba(0,0,0,.40),0 0 40px rgba(255,191,56,.12)}
.ax-popular-badge{position:absolute;right:18px;top:18px;padding:6px 10px;color:#ffd166;font-size:7px;font-weight:950;border-radius:999px;background:rgba(255,209,102,.08);border:1px solid rgba(255,209,102,.34)}
.ax-plan-name{color:#eef4ff;font-size:18px;font-weight:950}.ax-plan-desc{margin-top:7px;color:#92a3c2;font-size:9px;line-height:1.5}
.ax-plan-price{margin-top:24px;color:rgb(var(--rgb));font-size:52px;line-height:1;font-weight:950;letter-spacing:-2px}.ax-plan-price span{color:#7d8dab;font-size:12px;letter-spacing:0}
.ax-saving{display:inline-flex;margin-top:12px;padding:6px 9px;color:#31ff9c;font-size:7px;font-weight:950;border-radius:999px;background:rgba(49,255,156,.07);border:1px solid rgba(49,255,156,.25)}
.ax-feature-list{margin-top:25px}.ax-feature{display:flex;align-items:center;gap:10px;padding:10px 0;color:#b0bdd3;font-size:9px;border-bottom:1px solid rgba(72,96,158,.14)}
.ax-feature:before{content:"✓";display:grid;place-items:center;width:20px;height:20px;flex:0 0 20px;color:rgb(var(--rgb));font-weight:950;border-radius:50%;background:rgba(var(--rgb),.09);border:1px solid rgba(var(--rgb),.28)}
.ax-plan-cta-note{margin-top:20px;color:#7182a3;font-size:7px;text-align:center}
.ax-payment-panel,.ax-compare-panel,.ax-security-panel{margin-top:16px;padding:18px;border:1px solid rgba(68,98,165,.30);border-radius:16px;background:linear-gradient(145deg,rgba(7,15,35,.99),rgba(5,9,24,.99))}
.ax-panel-title{display:flex;justify-content:space-between;gap:12px;margin-bottom:15px}.ax-panel-title strong{color:#eef4ff;font-size:11px}.ax-panel-title span{color:#7182a3;font-size:7px}
.ax-payment-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}.ax-payment-method{padding:13px;color:#aebbd1;font-size:8px;text-align:center;border:1px solid rgba(74,96,160,.27);border-radius:12px;background:rgba(6,12,28,.82)}.ax-payment-method strong{display:block;margin-top:7px;color:#eef4ff;font-size:9px}
.ax-compare{width:100%;border-collapse:collapse;color:#aebbd1;font-size:9px}.ax-compare th,.ax-compare td{padding:12px 10px;text-align:left;border-bottom:1px solid rgba(72,96,158,.15)}.ax-compare th{color:#eef4ff;font-size:8px}.ax-yes{color:#31ff9c;font-weight:950}.ax-no{color:#ff6688;font-weight:950}
.ax-security-panel{text-align:center;color:#92a3c2;font-size:9px;line-height:1.6}.ax-security-panel strong{display:block;margin-bottom:6px;color:#eef4ff;font-size:12px}
.stButton>button[kind="primary"]{min-height:52px;background:linear-gradient(90deg,#2bdcff,#4e72ff,#9e3dff,#ff46c8)!important;border:1px solid rgba(126,102,255,.55)!important;border-radius:14px!important;font-weight:950!important}
@media(max-width:1000px){.ax-sub-hero-copy{max-width:68%}.ax-sub-orb{width:190px;height:190px;right:3%}.ax-status-grid{grid-template-columns:1fr}.ax-payment-grid{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:760px){.ax-sub-hero{min-height:auto;padding:28px}.ax-sub-hero-copy{max-width:100%}.ax-sub-orb{display:none}.ax-plan-grid,.ax-payment-grid{grid-template-columns:1fr}}
</style>
"""


def _safe_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    try:
        dumped = value.model_dump()
        return dumped if isinstance(dumped, dict) else {}
    except Exception:
        return {}


def _parse_date(value: Any) -> dt.datetime | None:
    if not value:
        return None
    try:
        parsed = value if isinstance(value, dt.datetime) else dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _trial_information() -> dict[str, Any]:
    now = dt.datetime.now(dt.timezone.utc)
    user = _safe_dict(st.session_state.get("user", {}))
    metadata = _safe_dict(user.get("user_metadata", {}))
    created_at = user.get("created_at") or metadata.get("trial_started_at") or st.session_state.get("trial_started_at")
    start = _parse_date(created_at)
    if start is None:
        start = now
        st.session_state.trial_started_at = start.isoformat()
    end = start + dt.timedelta(days=7)
    remaining_seconds = max(0, int((end - now).total_seconds()))
    days_remaining = max(0, int((remaining_seconds + 86399) // 86400))
    progress = min(100.0, max(0.0, (now - start).total_seconds() / (7 * 86400) * 100))
    return {
        "plan": metadata.get("plan", "TRIAL"),
        "status": "ACTIVO" if remaining_seconds > 0 else "FINALIZADO",
        "end": end,
        "days_remaining": days_remaining,
        "progress": progress,
    }


def render_subscription() -> None:
    apply_v2_theme()
    st.markdown(SUBSCRIPTION_CSS, unsafe_allow_html=True)
    trial = _trial_information()

    st.html(
        f"""
        <div class="ax-sub-stage">
          <section class="ax-sub-hero">
            <div class="ax-sub-hero-copy">
              <div class="ax-sub-kicker">AXION PRIME · MEMBERSHIP OS</div>
              <div class="ax-sub-title">AXION PRIME PRO</div>
              <div class="ax-sub-slogan">Inteligencia para operar. Disciplina para crecer.</div>
              <div class="ax-sub-description">Desbloquea Chat IA, Vision AI, Track Record, Psicotrading, Dashboard PRO, sesiones, proyecciones y futuras actualizaciones.</div>
              <div class="ax-trial-badge">✦ 7 DÍAS DE PRUEBA GRATUITA · ACCESO COMPLETO</div>
            </div>
            <div class="ax-sub-orb"></div>
          </section>

          <div class="ax-status-grid">
            <div class="ax-status-card">
              <small>ESTADO ACTUAL</small><strong>{html.escape(str(trial["plan"]))}</strong>
              <span>Estado: {trial["status"]} · Finaliza {trial["end"].strftime("%d/%m/%Y")}</span>
              <div class="ax-progress" style="--progress:{trial["progress"]:.1f}%"><div></div></div>
            </div>
            <div class="ax-status-card"><small>DÍAS RESTANTES</small><strong style="color:#31ff9c">{trial["days_remaining"]}</strong><span>Prueba gratuita de 7 días.</span></div>
            <div class="ax-status-card"><small>ACCESO</small><strong style="color:#2bdcff">COMPLETO</strong><span>Todas las funciones durante el trial.</span></div>
          </div>

          <div class="ax-plan-grid">
            <article class="ax-plan-card" style="--rgb:39,216,255">
              <div class="ax-plan-name">PRO MENSUAL</div><div class="ax-plan-desc">Flexibilidad total con renovación cada mes.</div>
              <div class="ax-plan-price">US$3 <span>/ mes</span></div>
              <div class="ax-feature-list">
                <div class="ax-feature">Chat IA y análisis del journal</div><div class="ax-feature">AXION Vision para capturas</div>
                <div class="ax-feature">Dashboard y Track Record PRO</div><div class="ax-feature">Psicotrading y auditoría IA</div>
                <div class="ax-feature">Calculadora de lotaje avanzada</div><div class="ax-feature">Sesiones y herramientas de mercado</div>
                <div class="ax-feature">Actualizaciones incluidas</div>
              </div>
              <div class="ax-plan-cta-note">Renovación mensual · Cancela cuando quieras</div>
            </article>

            <article class="ax-plan-card popular" style="--rgb:255,191,56">
              <div class="ax-popular-badge">★ MÁS POPULAR</div>
              <div class="ax-plan-name">PRO ANUAL</div><div class="ax-plan-desc">Todo AXION PRIME PRO durante doce meses.</div>
              <div class="ax-plan-price">US$20 <span>/ año</span></div>
              <div class="ax-saving">AHORRAS US$16 FRENTE AL PLAN MENSUAL</div>
              <div class="ax-feature-list">
                <div class="ax-feature">Todas las funciones del plan mensual</div><div class="ax-feature">12 meses de acceso completo</div>
                <div class="ax-feature">Insignia PRO ANUAL</div><div class="ax-feature">Prioridad en nuevas funciones</div>
                <div class="ax-feature">Actualizaciones premium</div><div class="ax-feature">Mejor precio anual</div>
                <div class="ax-feature">Soporte prioritario futuro</div>
              </div>
              <div class="ax-plan-cta-note">Un solo pago anual · Mejor relación precio/valor</div>
            </article>
          </div>

          <section class="ax-payment-panel">
            <div class="ax-panel-title"><strong>MÉTODOS DE PAGO</strong><span>INTEGRACIÓN PRÓXIMA</span></div>
            <div class="ax-payment-grid">
              <div class="ax-payment-method">💳<strong>VISA</strong></div><div class="ax-payment-method">💳<strong>MASTERCARD</strong></div>
              <div class="ax-payment-method">🏦<strong>DÉBITO</strong></div><div class="ax-payment-method">🟢<strong>MERCADO PAGO</strong></div>
              <div class="ax-payment-method">🟡<strong>BINANCE PAY</strong></div>
            </div>
          </section>

          <section class="ax-compare-panel">
            <div class="ax-panel-title"><strong>COMPARACIÓN DE ACCESO</strong><span>TRIAL VS PRO</span></div>
            <table class="ax-compare">
              <thead><tr><th>FUNCIÓN</th><th>TRIAL 7 DÍAS</th><th>PRO</th></tr></thead>
              <tbody>
                <tr><td>Dashboard completo</td><td class="ax-yes">✓</td><td class="ax-yes">✓</td></tr>
                <tr><td>Chat IA</td><td class="ax-yes">✓</td><td class="ax-yes">✓</td></tr>
                <tr><td>AXION Vision</td><td class="ax-yes">✓</td><td class="ax-yes">✓</td></tr>
                <tr><td>Track Record y Psicotrading</td><td class="ax-yes">✓</td><td class="ax-yes">✓</td></tr>
                <tr><td>Acceso después del trial</td><td class="ax-no">✕</td><td class="ax-yes">✓</td></tr>
                <tr><td>Actualizaciones premium</td><td class="ax-no">✕</td><td class="ax-yes">✓</td></tr>
              </tbody>
            </table>
          </section>

          <section class="ax-security-panel"><strong>🔒 PAGOS PROTEGIDOS</strong>Los pagos serán procesados por proveedores externos seguros. AXION PRIME no almacenará directamente los datos de las tarjetas.</section>
        </div>
        """
    )

    monthly, annual = st.columns(2, gap="medium")
    with monthly:
        if st.button("💎 SUSCRIBIRME · US$3 / MES", use_container_width=True, type="primary", key="subscription_monthly_button"):
            st.info("La pantalla visual está lista. El siguiente paso es conectar Mercado Pago y Binance Pay.")
    with annual:
        if st.button("👑 ELEGIR PLAN ANUAL · US$20", use_container_width=True, type="primary", key="subscription_annual_button"):
            st.info("La pantalla visual está lista. El siguiente paso es conectar Mercado Pago y Binance Pay.")
