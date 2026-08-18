from __future__ import annotations

from datetime import date, timedelta
import json
import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.backtest_engine import TradePlan, evaluate_trade
from core.market_data import MarketDataError, fetch_recent_klines, get_backtest_dataset, resolve_symbol
from ui_v2.theme import apply_v2_theme


BACKTEST_CSS = """
<style>
/* ---------- AXION REPLAY UX ---------- */
.ax-rp-shell {
    margin-bottom: 14px;
    padding: 18px 20px 16px;
    background:
        radial-gradient(circle at 9% 10%, rgba(25,228,255,.11), transparent 27%),
        radial-gradient(circle at 91% 15%, rgba(126,87,255,.12), transparent 28%),
        linear-gradient(145deg, rgba(6,14,31,.99), rgba(3,7,18,.99));
    border:1px solid rgba(69,119,201,.32);
    border-radius:20px;
}
.ax-rp-head {
    display:flex; align-items:flex-start; justify-content:space-between;
    gap:16px; flex-wrap:wrap;
}
.ax-rp-brand {color:#19e4ff;font-size:10px;font-weight:950;letter-spacing:2.1px;}
.ax-rp-title {
    margin-top:5px;color:#f7f9ff;font-size:36px;font-weight:950;
    letter-spacing:-1.6px;line-height:1;
}
.ax-rp-title .cyan {color:#19e4ff;}
.ax-rp-sub {margin-top:8px;color:#91a0bf;font-size:11px;line-height:1.5;}
.ax-rp-badges {display:flex;gap:7px;flex-wrap:wrap;}
.ax-rp-badge {
    padding:7px 10px;border-radius:999px;border:1px solid rgba(25,228,255,.26);
    background:rgba(25,228,255,.065);color:#b9f7ff;
    font-size:8px;font-weight:900;letter-spacing:.55px;white-space:nowrap;
}
.ax-rp-badge.purple {border-color:rgba(126,87,255,.34);background:rgba(126,87,255,.08);color:#d6ccff;}
.ax-rp-badge.green {border-color:rgba(0,245,138,.26);background:rgba(0,245,138,.06);color:#a7fbd2;}

.ax-rp-mode-note {
    padding:10px 12px;border:1px solid rgba(25,228,255,.18);
    background:linear-gradient(90deg,rgba(8,32,64,.68),rgba(15,22,55,.72));
    border-radius:12px;color:#9ecbff;font-size:9px;line-height:1.45;
}
.ax-rp-stepbar {
    margin:12px 0 8px;padding:10px 13px;border-radius:14px;
    border:1px solid rgba(69,119,201,.23);
    background:rgba(5,12,27,.72);
    display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;
}
.ax-rp-step {
    min-height:45px;padding:9px 10px;border-radius:11px;
    border:1px solid rgba(77,111,179,.18);background:rgba(8,17,37,.68);
}
.ax-rp-step small {display:block;color:#6f80a2;font-size:7px;font-weight:950;letter-spacing:.9px;}
.ax-rp-step strong {display:block;margin-top:4px;color:#eef4ff;font-size:10px;}
.ax-rp-step.go {border-color:rgba(126,87,255,.34);background:linear-gradient(135deg,rgba(25,228,255,.08),rgba(126,87,255,.11));}

.ax-rp-source {
    margin:8px 0 10px;padding:8px 11px;border-radius:10px;
    border:1px solid rgba(0,245,138,.22);background:rgba(0,245,138,.045);
    color:#9af2c7;font-size:8px;
}
.ax-rp-toolbar {
    margin:6px 0 8px;padding:8px 10px;border-radius:11px;
    border:1px solid rgba(77,111,179,.20);background:rgba(6,13,29,.78);
    color:#94a7c9;font-size:8px;
}
.ax-rp-panel-title {
    margin:10px 0 7px;color:#f3f6ff;font-size:10px;font-weight:950;letter-spacing:.9px;
}
.ax-rp-warning {
    padding:9px 11px;border:1px solid rgba(255,209,102,.24);
    background:rgba(255,209,102,.045);border-radius:11px;
    color:#ddd2ae;font-size:8px;line-height:1.45;
}
.ax-rp-metric-grid {
    display:grid;grid-template-columns:repeat(4,minmax(0,1fr));
    gap:9px;margin:10px 0 13px;
}
.ax-rp-metric {
    padding:11px 12px;border:1px solid rgba(77,111,179,.24);
    background:linear-gradient(145deg,rgba(8,17,37,.95),rgba(4,9,23,.96));
    border-radius:13px;
}
.ax-rp-metric small {display:block;color:#6f80a2;font-size:7px;font-weight:950;letter-spacing:.9px;}
.ax-rp-metric strong {display:block;margin-top:5px;color:#f7f9ff;font-size:17px;font-weight:950;}
.ax-rp-metric span {display:block;margin-top:3px;color:#19e4ff;font-size:7.5px;}

.ax-rp-progress-wrap {
    margin:8px 0 12px;padding:10px 12px;border-radius:12px;
    border:1px solid rgba(77,111,179,.20);background:rgba(5,12,27,.78);
}
.ax-rp-progress-top {display:flex;justify-content:space-between;gap:12px;color:#9aa9c3;font-size:8px;}
.ax-rp-progress-track {height:7px;border-radius:999px;background:#101b38;margin-top:8px;overflow:hidden;}
.ax-rp-progress-fill {height:100%;background:linear-gradient(90deg,#15d9cc,#4d70ff,#7d57ff);border-radius:999px;}
.ax-rp-progress-value {color:#19e4ff;font-size:13px;font-weight:950;}

.ax-rp-trade-summary {
    margin-top:8px;padding:10px;border-radius:12px;border:1px solid rgba(25,228,255,.22);
    background:rgba(25,228,255,.045);
}
.ax-rp-trade-summary div {display:flex;justify-content:space-between;gap:8px;margin:4px 0;color:#9aabc6;font-size:8px;}
.ax-rp-trade-summary b {color:#eef4ff;}
.ax-rp-trade-summary .good {color:#00f58a;font-weight:900;}

.ax-rp-bottom-grid {
    display:grid;grid-template-columns:repeat(6,minmax(0,1fr));
    gap:8px;margin:12px 0;
}
.ax-rp-bottom-card {
    padding:11px;border:1px solid rgba(77,111,179,.22);
    border-radius:12px;background:linear-gradient(145deg,rgba(8,17,37,.92),rgba(4,9,23,.95));
}
.ax-rp-bottom-card small {color:#6f80a2;font-size:7px;font-weight:950;letter-spacing:.8px;}
.ax-rp-bottom-card strong {display:block;margin-top:5px;color:#f7f9ff;font-size:16px;}
.ax-rp-bottom-card .pos {color:#00f58a}.ax-rp-bottom-card .neg {color:#ff516e}

div[data-testid="stRadio"] > div {gap:6px;}
div[data-testid="stRadio"] label {
    border:1px solid rgba(77,111,179,.26);
    background:rgba(7,15,33,.88);
    padding:7px 12px !important;border-radius:10px;
}
div[data-testid="stButton"] button {
    border-radius:10px !important;
    border:1px solid rgba(77,111,179,.30) !important;
}
div[data-testid="stButton"] button[kind="primary"] {
    background:linear-gradient(90deg,#19cfea,#7857ff) !important;
}
@media(max-width:1000px){
    .ax-rp-stepbar{grid-template-columns:repeat(2,minmax(0,1fr));}
    .ax-rp-bottom-grid{grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media(max-width:720px){
    .ax-rp-title{font-size:29px}
    .ax-rp-metric-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
    .ax-rp-bottom-grid{grid-template-columns:repeat(2,minmax(0,1fr));}
}
</style>
"""


def _init_bt_state() -> None:
    defaults = {
        "bt_symbol": "BTCUSDT",
        "bt_mode": "REPLAY",
        "bt_date": date.today() - timedelta(days=30),
        "bt_interval": "1H",
        "bt_dataset": None,
        "bt_market": None,
        "bt_cursor": 120,
        "bt_speed": 1,
        "bt_trade": None,
        "bt_trade_result": None,
        "bt_favorites": ["BTCUSDT", "ETHUSDT"],
        "bt_session_trades": 0,
        "bt_session_wins": 0,
        "bt_session_losses": 0,
        "bt_session_pnl": 0.0,
        "bt_loaded_symbol": None,
        "bt_loaded_interval": None,
        "bt_loaded_date": None,
        "bt_big_chart": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _fmt_price(value: float) -> str:
    if value >= 1000:
        return f"{value:,.2f}"
    if value >= 1:
        return f"{value:,.4f}"
    return f"{value:.6f}"


def _candles_for_chart(frame: pd.DataFrame) -> list[dict]:
    data: list[dict] = []
    for _, row in frame.iterrows():
        data.append({
            "time": int(pd.Timestamp(row["open_time"]).timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        })
    return data


def _volume_for_chart(frame: pd.DataFrame) -> list[dict]:
    result = []
    for _, row in frame.iterrows():
        up = float(row["close"]) >= float(row["open"])
        result.append({
            "time": int(pd.Timestamp(row["open_time"]).timestamp()),
            "value": float(row["volume"]),
            "color": "rgba(0,245,138,0.33)" if up else "rgba(255,23,68,0.32)",
        })
    return result



def _render_chart(
    frame: pd.DataFrame,
    symbol_label: str,
    interval: str,
    trade: dict | None = None,
    workspace_height: int = 720,
) -> None:
    """AXION Workspace: gráfico grande + herramientas visuales client-side."""
    candles = json.dumps(_candles_for_chart(frame))
    volumes = json.dumps(_volume_for_chart(frame))
    last = frame.iloc[-1]
    last_price = float(last["close"])
    min_price = float(frame["low"].min())
    max_price = float(frame["high"].max())
    span = max(max_price - min_price, last_price * 0.01, 1e-9)

    entry = float(trade["entry"]) if trade else last_price
    stop = float(trade["stop"]) if trade else last_price - span * 0.08
    target = float(trade["target"]) if trade else last_price + span * 0.16
    direction = str(trade["direction"]) if trade else "LONG"

    html = f"""
    <style>
      *{{box-sizing:border-box}}
      body{{margin:0;background:#020711;font-family:Inter,system-ui;color:#d9e5ff}}
      .axws-shell{{
        height:{workspace_height}px;width:100%;display:grid;grid-template-columns:58px 1fr 245px;
        border:1px solid rgba(79,119,196,.30);border-radius:16px;overflow:hidden;
        background:#020711;
      }}
      .axws-tools{{
        background:#050b17;border-right:1px solid rgba(79,119,196,.24);
        display:flex;flex-direction:column;gap:4px;padding:8px 5px;
      }}
      .axws-tool{{
        height:48px;border:1px solid transparent;border-radius:9px;background:transparent;
        color:#8fa0be;font-size:17px;cursor:pointer;display:flex;flex-direction:column;
        align-items:center;justify-content:center;gap:2px;
      }}
      .axws-tool span{{font-size:7px;line-height:1}}
      .axws-tool:hover,.axws-tool.active{{
        color:#fff;border-color:rgba(25,228,255,.28);background:rgba(25,228,255,.08)
      }}
      .axws-tool.long{{color:#00f58a}} .axws-tool.short{{color:#ff4867}}
      .axws-main{{display:grid;grid-template-rows:48px 1fr 48px;background:#020711}}
      .axws-top{{
        display:flex;align-items:center;justify-content:space-between;padding:0 12px;
        border-bottom:1px solid rgba(79,119,196,.18);background:#050b17
      }}
      .axws-symbol{{font-size:11px;font-weight:900;color:#f5f8ff}}
      .axws-symbol small{{color:#7486a7;font-weight:700;margin-left:7px}}
      .axws-actions{{display:flex;gap:6px;align-items:center}}
      .axws-pill{{
        font-size:8px;padding:6px 8px;border:1px solid rgba(79,119,196,.22);
        border-radius:8px;color:#91a6c8;background:#071126
      }}
      .axws-expand{{
        border:1px solid rgba(126,87,255,.40);background:rgba(126,87,255,.10);
        color:#d9d2ff;border-radius:9px;padding:7px 10px;cursor:pointer
      }}
      .axws-chart-wrap{{position:relative;overflow:hidden}}
      #axws-chart{{position:absolute;inset:0}}
      #axws-overlay{{position:absolute;inset:0;pointer-events:none}}
      .axws-footer{{
        display:flex;align-items:center;justify-content:center;gap:8px;
        border-top:1px solid rgba(79,119,196,.18);background:#050b17;padding:0 10px
      }}
      .axws-play{{
        border:1px solid rgba(126,87,255,.35);background:linear-gradient(90deg,#19cfea,#7857ff);
        color:#fff;border-radius:9px;padding:7px 14px;font-weight:900;cursor:pointer
      }}
      .axws-footbtn{{
        border:1px solid rgba(79,119,196,.22);background:#081126;color:#b9c7df;
        border-radius:8px;padding:7px 10px;cursor:pointer;font-size:9px
      }}
      .axws-side{{
        background:#050b17;border-left:1px solid rgba(79,119,196,.24);padding:10px;
        overflow:auto
      }}
      .axws-card{{
        border:1px solid rgba(79,119,196,.22);background:#071126;border-radius:11px;
        padding:10px;margin-bottom:9px
      }}
      .axws-card h4{{margin:0 0 8px;font-size:9px;letter-spacing:.6px;color:#dfe8fa}}
      .axws-row{{display:flex;justify-content:space-between;gap:8px;font-size:8px;color:#8fa0be;margin:6px 0}}
      .axws-row b{{color:#f7f9ff}}
      .axws-good{{color:#00f58a!important}} .axws-bad{{color:#ff4867!important}}
      .axws-hint{{font-size:7px;line-height:1.4;color:#6e7e9d}}
      .axws-settings label{{display:block;font-size:7px;color:#7f90ad;margin:7px 0 3px}}
      .axws-settings input,.axws-settings select{{
        width:100%;background:#050b17;color:#dbe6fb;border:1px solid rgba(79,119,196,.25);
        border-radius:7px;padding:6px;font-size:8px
      }}
      .axws-toolpanel{{
        position:absolute;left:10px;top:10px;width:210px;padding:10px;
        background:rgba(5,11,23,.96);border:1px solid rgba(25,228,255,.25);
        border-radius:11px;display:none;z-index:4
      }}
      .axws-toolpanel.show{{display:block}}
      .axws-toolpanel h4{{font-size:9px;margin:0 0 8px;color:#fff}}
      .axws-toolpanel button{{
        width:48%;margin:2px .5%;padding:7px;border-radius:7px;border:1px solid rgba(79,119,196,.25);
        background:#071126;color:#bcd0ee;cursor:pointer;font-size:8px
      }}
      .axws-toolpanel button.sel{{border-color:#19e4ff;color:#19e4ff}}
      .axws-fibrow{{display:grid;grid-template-columns:18px 1fr 52px;gap:5px;align-items:center;margin:5px 0}}
      .axws-fibrow input[type=number]{{width:100%;background:#071126;border:1px solid rgba(79,119,196,.22);color:#dce7ff;border-radius:6px;padding:4px;font-size:8px}}
      .axws-modalbg{{
        position:absolute;inset:0;background:rgba(0,0,0,.72);display:none;z-index:20
      }}
      .axws-shell.full{{position:fixed;inset:6px;z-index:99999;height:auto;border-radius:12px}}
      .axws-shell.full .axws-modalbg{{display:none}}
    </style>

    <div id="axws-shell" class="axws-shell">
      <aside class="axws-tools">
        <button class="axws-tool active" data-tool="cursor">↖<span>Cursor</span></button>
        <button class="axws-tool" data-tool="trend">╱<span>Tendencia</span></button>
        <button class="axws-tool" data-tool="horizontal">─<span>Horizontal</span></button>
        <button class="axws-tool" data-tool="rectangle">▭<span>Rectángulo</span></button>
        <button class="axws-tool" data-tool="fib">≡<span>Fibonacci</span></button>
        <button class="axws-tool" data-tool="text">T<span>Texto</span></button>
        <button class="axws-tool long" data-tool="long">↑<span>Long</span></button>
        <button class="axws-tool short" data-tool="short">↓<span>Short</span></button>
        <button class="axws-tool" data-tool="measure">⌁<span>Medición</span></button>
        <button class="axws-tool" data-tool="magnet">🧲<span>Imán</span></button>
        <button class="axws-tool" data-tool="delete">⌫<span>Borrar</span></button>
      </aside>

      <section class="axws-main">
        <div class="axws-top">
          <div class="axws-symbol">{symbol_label} · {interval}<small>AXION REPLAY · VERIFIED OHLCV</small></div>
          <div class="axws-actions">
            <span class="axws-pill">🔥 Heatmap OFF</span>
            <span class="axws-pill">🌍 Sesiones OFF</span>
            <span class="axws-pill">📊 Volumen ON</span>
            <span class="axws-pill">V4 · WORKSPACE</span>
          </div>
        </div>

        <div class="axws-chart-wrap" id="axws-wrap">
          <div id="axws-chart"></div>
          <canvas id="axws-overlay"></canvas>

          <div id="axws-pospanel" class="axws-toolpanel">
            <h4>HERRAMIENTA DE POSICIÓN</h4>
            <button id="pos-long" class="sel">LONG</button>
            <button id="pos-short">SHORT</button>
            <div class="axws-settings">
              <label>Riesgo visual</label>
              <select id="rr-template">
                <option value="2">1 : 2</option>
                <option value="2.5">1 : 2.5</option>
                <option value="3">1 : 3</option>
              </select>
            </div>
            <div class="axws-hint">Haz clic en el gráfico para colocar la entrada. Arrastra las líneas para ajustar SL y TP.</div>
          </div>

          <div id="axws-fibpanel" class="axws-toolpanel">
            <h4>FIBONACCI</h4>
            <div class="axws-fibrow"><input type="checkbox" checked><span>0</span><input type="number" value="0" step=".001"></div>
            <div class="axws-fibrow"><input type="checkbox" checked><span>0.5</span><input type="number" value=".5" step=".001"></div>
            <div class="axws-fibrow"><input type="checkbox" checked><span>0.618</span><input type="number" value=".618" step=".001"></div>
            <div class="axws-fibrow"><input type="checkbox" checked><span>0.705</span><input type="number" value=".705" step=".001"></div>
            <div class="axws-fibrow"><input type="checkbox" checked><span>0.786</span><input type="number" value=".786" step=".001"></div>
            <div class="axws-fibrow"><input type="checkbox" checked><span>1</span><input type="number" value="1" step=".001"></div>
            <div class="axws-hint">Selecciona dos puntos en el gráfico. Los niveles quedan guardados durante esta sesión del workspace.</div>
          </div>
        </div>

        <div class="axws-footer">
          <button class="axws-footbtn">⏮ Inicio</button>
          <button class="axws-footbtn">◀ 1 vela</button>
          <button class="axws-play">▶ Play</button>
          <button class="axws-footbtn">⏸ Pausa</button>
          <button class="axws-footbtn">▶ 1 vela</button>
          <button class="axws-footbtn">⏭ Fin</button>
          <button class="axws-footbtn">1x⌄</button>
        </div>
      </section>

      <aside class="axws-side">
        <div class="axws-card">
          <h4>INFORMACIÓN DE MERCADO</h4>
          <div class="axws-row"><span>Activo</span><b>{symbol_label}</b></div>
          <div class="axws-row"><span>Precio</span><b class="axws-good">{last_price:,.4f}</b></div>
          <div class="axws-row"><span>Máximo visible</span><b>{max_price:,.4f}</b></div>
          <div class="axws-row"><span>Mínimo visible</span><b>{min_price:,.4f}</b></div>
          <div class="axws-row"><span>Velas visibles</span><b>{len(frame)}</b></div>
        </div>

        <div class="axws-card">
          <h4>POSICIÓN VISUAL</h4>
          <div class="axws-row"><span>Dirección</span><b id="side-dir" class="axws-good">{direction}</b></div>
          <div class="axws-row"><span>Entrada</span><b id="side-entry">{entry:,.4f}</b></div>
          <div class="axws-row"><span>Stop Loss</span><b id="side-stop" class="axws-bad">{stop:,.4f}</b></div>
          <div class="axws-row"><span>Take Profit</span><b id="side-target" class="axws-good">{target:,.4f}</b></div>
          <div class="axws-row"><span>R:R visual</span><b id="side-rr">1 : 2.00</b></div>
          <div class="axws-hint">La posición dibujada es una herramienta visual del workspace. La ejecución estadística sigue usando el simulador de AXION debajo del gráfico.</div>
        </div>

        <div class="axws-card axws-settings">
          <h4>PERSONALIZACIÓN</h4>
          <label>Plantilla Fib</label>
          <select><option>AXION PRIME</option><option>ICT / OTE</option><option>Personalizada</option></select>
          <label>Riesgo predeterminado</label>
          <select><option>0.5%</option><option selected>1.0%</option><option>2.0%</option></select>
          <label>Workspace</label>
          <input value="Workspace Trader">
          <div class="axws-hint" style="margin-top:8px">La persistencia por usuario en Supabase se conecta en la fase de Workspace Personal.</div>
        </div>
      </aside>
    </div>

    <script src="https://unpkg.com/lightweight-charts@4.2.3/dist/lightweight-charts.standalone.production.js"></script>
    <script>
      const shell = document.getElementById('axws-shell');
      const wrap = document.getElementById('axws-wrap');
      const chartEl = document.getElementById('axws-chart');
      const canvas = document.getElementById('axws-overlay');
      const ctx = canvas.getContext('2d');

      const chart = LightweightCharts.createChart(chartEl, {{
        layout: {{ background: {{ type:'solid', color:'#020711' }}, textColor:'#899ab9' }},
        grid: {{
          vertLines: {{ color:'rgba(59,86,137,.12)' }},
          horzLines: {{ color:'rgba(59,86,137,.12)' }}
        }},
        rightPriceScale: {{ borderColor:'rgba(72,105,170,.22)' }},
        timeScale: {{ borderColor:'rgba(72,105,170,.22)', timeVisible:true, secondsVisible:false, rightOffset:4 }},
        crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }}
      }});

      const candlesSeries = chart.addCandlestickSeries({{
        upColor:'#00d9c8', downColor:'#ff4867',
        wickUpColor:'#00d9c8', wickDownColor:'#ff4867',
        borderUpColor:'#00d9c8', borderDownColor:'#ff4867'
      }});

      const volumeSeries = chart.addHistogramSeries({{
        priceFormat:{{type:'volume'}}, priceScaleId:'',
        scaleMargins:{{top:.82,bottom:0}}
      }});

      candlesSeries.setData({candles});
      volumeSeries.setData({volumes});
      chart.timeScale().fitContent();

      function resizeOverlay(){{
        const r = wrap.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        canvas.width = Math.max(1, Math.floor(r.width*dpr));
        canvas.height = Math.max(1, Math.floor(r.height*dpr));
        canvas.style.width = r.width+'px';
        canvas.style.height = r.height+'px';
        ctx.setTransform(dpr,0,0,dpr,0,0);
        drawAll();
      }}

      const drawings = [];
      let tool = 'cursor';
      let p1 = null;
      let temp = null;
      let pos = null;
      let dragging = null;

      function pointFromEvent(e){{
        const r = canvas.getBoundingClientRect();
        return {{x:e.clientX-r.left, y:e.clientY-r.top}};
      }}

      function priceFromY(y){{
        const p = candlesSeries.coordinateToPrice(y);
        return p == null ? {last_price} : Number(p);
      }}

      function yFromPrice(p){{
        const y = candlesSeries.priceToCoordinate(Number(p));
        return y == null ? 0 : Number(y);
      }}

      function drawLine(a,b,color='#19e4ff',dash=[]){{
        ctx.save(); ctx.strokeStyle=color; ctx.lineWidth=1.3; ctx.setLineDash(dash);
        ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke(); ctx.restore();
      }}

      function drawRect(a,b,color='rgba(25,228,255,.8)',fill='rgba(25,228,255,.08)'){{
        const x=Math.min(a.x,b.x), y=Math.min(a.y,b.y), w=Math.abs(a.x-b.x), h=Math.abs(a.y-b.y);
        ctx.save(); ctx.strokeStyle=color; ctx.fillStyle=fill; ctx.lineWidth=1.2;
        ctx.fillRect(x,y,w,h); ctx.strokeRect(x,y,w,h); ctx.restore();
      }}

      function drawText(p,t){{
        ctx.save();ctx.fillStyle='#e9f2ff';ctx.font='12px Inter,system-ui';
        ctx.fillText(t,p.x+5,p.y-5);ctx.restore();
      }}

      function drawFib(a,b,levels=[0,.5,.618,.705,.786,1]){{
        const top=Math.min(a.y,b.y), bottom=Math.max(a.y,b.y);
        const colors=['#d8e2f2','#19d4df','#17b8c7','#d4ad33','#d78a28','#d8e2f2'];
        levels.forEach((lv,i)=>{{
          const y=top+(bottom-top)*lv;
          drawLine({{x:Math.min(a.x,b.x),y}},{{x:Math.max(a.x,b.x)+260,y}},colors[i]||'#19e4ff',[5,4]);
          ctx.save();ctx.fillStyle=colors[i]||'#19e4ff';ctx.font='11px Inter';
          ctx.fillText(String(lv),Math.max(a.x,b.x)+265,y+3);ctx.restore();
        }});
        drawLine(a,b,'#a8b5c9',[6,5]);
      }}

      function updateSide(){{
        if(!pos) return;
        document.getElementById('side-dir').textContent=pos.direction;
        document.getElementById('side-dir').className=pos.direction==='LONG'?'axws-good':'axws-bad';
        document.getElementById('side-entry').textContent=pos.entry.toFixed(4);
        document.getElementById('side-stop').textContent=pos.stop.toFixed(4);
        document.getElementById('side-target').textContent=pos.target.toFixed(4);
        const risk=Math.max(Math.abs(pos.entry-pos.stop),1e-9);
        const reward=Math.abs(pos.target-pos.entry);
        document.getElementById('side-rr').textContent='1 : '+(reward/risk).toFixed(2);
      }}

      function drawPosition(){{
        if(!pos) return;
        const yE=yFromPrice(pos.entry), yS=yFromPrice(pos.stop), yT=yFromPrice(pos.target);
        const left=80, right=canvas.getBoundingClientRect().width-80;
        const top=Math.min(yT,yE), h1=Math.abs(yE-yT);
        const low=Math.min(yE,yS), h2=Math.abs(yE-yS);
        ctx.save();
        ctx.fillStyle=pos.direction==='LONG'?'rgba(0,245,138,.10)':'rgba(255,72,103,.10)';
        ctx.fillRect(left,top,right-left,h1);
        ctx.fillStyle=pos.direction==='LONG'?'rgba(255,72,103,.10)':'rgba(0,245,138,.10)';
        ctx.fillRect(left,low,right-left,h2);
        ctx.restore();
        drawLine({{x:left,y:yE}},{{x:right,y:yE}},'#238cff',[6,4]);
        drawLine({{x:left,y:yS}},{{x:right,y:yS}},'#ff4867',[6,4]);
        drawLine({{x:left,y:yT}},{{x:right,y:yT}},'#00f58a',[6,4]);
        ['entry','stop','target'].forEach((k)=>{{
          const y=k==='entry'?yE:k==='stop'?yS:yT;
          ctx.save();ctx.fillStyle='#fff';ctx.beginPath();ctx.arc(right-4,y,5,0,Math.PI*2);ctx.fill();ctx.restore();
        }});
      }}

      function drawAll(){{
        const w=canvas.getBoundingClientRect().width, h=canvas.getBoundingClientRect().height;
        ctx.clearRect(0,0,w,h);
        drawings.forEach(d=>{{
          if(d.type==='trend') drawLine(d.a,d.b,'#19e4ff');
          if(d.type==='horizontal') drawLine({{x:0,y:d.a.y}},{{x:w,y:d.a.y}},'#d0a52e',[6,5]);
          if(d.type==='rectangle') drawRect(d.a,d.b);
          if(d.type==='fib') drawFib(d.a,d.b,d.levels);
          if(d.type==='text') drawText(d.a,d.text);
          if(d.type==='measure') {{
            drawLine(d.a,d.b,'#b6c4dc',[4,4]);
            drawText({{x:(d.a.x+d.b.x)/2,y:(d.a.y+d.b.y)/2}},Math.round(Math.hypot(d.a.x-d.b.x,d.a.y-d.b.y))+' px');
          }}
        }});
        if(temp && p1){{
          if(tool==='trend') drawLine(p1,temp,'#19e4ff');
          if(tool==='rectangle') drawRect(p1,temp);
          if(tool==='fib') drawFib(p1,temp);
          if(tool==='measure') drawLine(p1,temp,'#b6c4dc',[4,4]);
        }}
        drawPosition();
      }}

      function setTool(t){{
        tool=t;p1=null;temp=null;
        document.querySelectorAll('.axws-tool').forEach(b=>b.classList.toggle('active',b.dataset.tool===t));
        document.getElementById('axws-pospanel').classList.toggle('show',t==='long'||t==='short');
        document.getElementById('axws-fibpanel').classList.toggle('show',t==='fib');
        canvas.style.pointerEvents=t==='cursor'?'none':'auto';
      }}

      document.querySelectorAll('.axws-tool').forEach(btn=>btn.addEventListener('click',()=>{{
        if(btn.dataset.tool==='delete'){{drawings.length=0;pos=null;drawAll();return;}}
        setTool(btn.dataset.tool);
      }}));

      document.getElementById('pos-long').addEventListener('click',()=>{{
        tool='long';document.getElementById('pos-long').classList.add('sel');
        document.getElementById('pos-short').classList.remove('sel');
      }});
      document.getElementById('pos-short').addEventListener('click',()=>{{
        tool='short';document.getElementById('pos-short').classList.add('sel');
        document.getElementById('pos-long').classList.remove('sel');
      }});

      canvas.addEventListener('mousedown',(e)=>{{
        const p=pointFromEvent(e);
        if(tool==='long'||tool==='short'){{
          const entry=priceFromY(p.y);
          const rr=Number(document.getElementById('rr-template').value||2);
          const risk={span}*0.08;
          pos = tool==='long'
            ? {{direction:'LONG',entry,stop:entry-risk,target:entry+risk*rr}}
            : {{direction:'SHORT',entry,stop:entry+risk,target:entry-risk*rr}};
          updateSide();drawAll();return;
        }}
        if(tool==='horizontal'){{drawings.push({{type:'horizontal',a:p}});drawAll();return;}}
        if(tool==='text'){{
          const label=prompt('Texto para el gráfico:','Nota');
          if(label) drawings.push({{type:'text',a:p,text:label}});
          drawAll();return;
        }}
        p1=p;temp=p;
      }});

      canvas.addEventListener('mousemove',(e)=>{{
        if(!p1) return; temp=pointFromEvent(e); drawAll();
      }});

      canvas.addEventListener('mouseup',(e)=>{{
        if(!p1) return;
        const p2=pointFromEvent(e);
        if(['trend','rectangle','fib','measure'].includes(tool)){{
          const d={{type:tool,a:p1,b:p2}};
          if(tool==='fib') d.levels=[0,.5,.618,.705,.786,1];
          drawings.push(d);
        }}
        p1=null;temp=null;drawAll();
      }});

      chart.timeScale().subscribeVisibleTimeRangeChange(()=>drawAll());
      chart.subscribeCrosshairMove(()=>drawAll());

      const ro=new ResizeObserver(()=>{{
        chart.applyOptions({{width:chartEl.clientWidth,height:chartEl.clientHeight}});
        resizeOverlay();
      }});
      ro.observe(wrap);

      // initial visual position if a trade exists
      if ({str(bool(trade)).lower()}) {{
        pos={{direction:'{direction}',entry:{entry},stop:{stop},target:{target}}};
        updateSide();
      }}
      setTool('cursor');
      resizeOverlay();
    </script>
    """
    components.html(html, height=workspace_height + 15, scrolling=False)

def _render_live_chart(frame: pd.DataFrame, market_symbol: str, symbol_label: str, interval: str) -> None:
    candles = json.dumps(_candles_for_chart(frame))
    volumes = json.dumps(_volume_for_chart(frame))
    ws_interval = {"5m":"5m","15m":"15m","30m":"30m","1H":"1h","4H":"4h","1D":"1d"}[interval]
    last_price = float(frame.iloc[-1]["close"])
    html = f"""
    <div style="font-family:Inter,system-ui;background:#030712;border:1px solid rgba(75,112,184,.34);border-radius:16px;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;border-bottom:1px solid rgba(75,112,184,.18);background:linear-gradient(90deg,#071125,#050915);">
        <div><strong style="color:#f7f9ff;font-size:12px">{symbol_label} · {interval}</strong><div style="color:#667694;font-size:9px;margin-top:3px">LIVE MARKET · BINANCE SPOT</div></div>
        <div style="text-align:right"><div id="bt-live-price" style="color:#f7f9ff;font-size:18px;font-weight:900">{last_price:,.2f}</div><div id="bt-live-status" style="color:#19e4ff;font-size:8px;font-weight:900">● CONNECTING…</div></div>
      </div>
      <div id="bt-live-chart" style="height:560px;width:100%;"></div>
    </div>
    <script src="https://unpkg.com/lightweight-charts@4.2.3/dist/lightweight-charts.standalone.production.js"></script>
    <script>
      const container = document.getElementById('bt-live-chart');
      const priceEl = document.getElementById('bt-live-price');
      const statusEl = document.getElementById('bt-live-status');
      const chart = LightweightCharts.createChart(container, {{
        layout: {{ background: {{ type:'solid', color:'#030712' }}, textColor:'#8fa0be' }},
        grid: {{ vertLines: {{ color:'rgba(58,83,132,.12)' }}, horzLines: {{ color:'rgba(58,83,132,.12)' }} }},
        rightPriceScale: {{ borderColor:'rgba(72,105,170,.25)' }},
        timeScale: {{ borderColor:'rgba(72,105,170,.25)', timeVisible:true, secondsVisible:false, rightOffset:5 }},
        crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
      }});
      const series = chart.addCandlestickSeries({{upColor:'#00f58a',downColor:'#ff3158',wickUpColor:'#00f58a',wickDownColor:'#ff3158',borderUpColor:'#00f58a',borderDownColor:'#ff3158'}});
      const volume = chart.addHistogramSeries({{priceFormat:{{type:'volume'}},priceScaleId:'',scaleMargins:{{top:0.82,bottom:0}}}});
      series.setData({candles});
      volume.setData({volumes});
      chart.timeScale().fitContent();
      const ws = new WebSocket('wss://stream.binance.com:9443/ws/{market_symbol.lower()}@kline_{ws_interval}');
      ws.onopen = () => {{ statusEl.textContent='● LIVE · VERIFIED'; statusEl.style.color='#00f58a'; }};
      ws.onmessage = (event) => {{
        const msg=JSON.parse(event.data); const k=msg.k; if(!k) return; const t=Math.floor(k.t/1000);
        series.update({{time:t,open:Number(k.o),high:Number(k.h),low:Number(k.l),close:Number(k.c)}});
        volume.update({{time:t,value:Number(k.v),color:Number(k.c)>=Number(k.o)?'rgba(0,245,138,.33)':'rgba(255,23,68,.32)'}});
        priceEl.textContent=Number(k.c).toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:8}});
      }};
      ws.onerror=()=>{{statusEl.textContent='● CONNECTION ERROR';statusEl.style.color='#ffd166';}};
      ws.onclose=()=>{{statusEl.textContent='● DISCONNECTED';statusEl.style.color='#ffd166';}};
      new ResizeObserver(entries=>{{if(entries.length)chart.applyOptions({{width:entries[0].contentRect.width}});}}).observe(container);
    </script>
    """
    components.html(html, height=625, scrolling=False)


def _load_dataset(symbol: str, interval: str, start_day: date) -> None:
    with st.spinner("Descargando datos históricos verificados…"):
        market, frame = get_backtest_dataset(symbol, interval, start_day, limit=1000)
    st.session_state.bt_market = market
    st.session_state.bt_dataset = frame
    st.session_state.bt_symbol = market.symbol
    st.session_state.bt_interval = interval
    st.session_state.bt_date = start_day
    st.session_state.bt_loaded_symbol = market.symbol
    st.session_state.bt_loaded_interval = interval
    st.session_state.bt_loaded_date = start_day
    st.session_state.bt_cursor = min(max(80, int(len(frame) * 0.20)), max(1, len(frame) - 1))
    st.session_state.bt_trade = None
    st.session_state.bt_trade_result = None


def render_backtesting_lab() -> None:
    apply_v2_theme()
    st.markdown(BACKTEST_CSS, unsafe_allow_html=True)
    _init_bt_state()

    st.html("""
    <div style="display:inline-block;margin-bottom:8px;padding:5px 9px;border-radius:999px;
                border:1px solid rgba(25,228,255,.35);background:rgba(25,228,255,.08);
                color:#19e4ff;font-size:9px;font-weight:900;letter-spacing:.8px;">
      AXION WORKSPACE V4 · AUTO TIMEFRAME · BIG CHART
    </div>
    <section class="ax-rp-shell">
      <div class="ax-rp-head">
        <div>
          <div class="ax-rp-brand">AXION PRIME · PERFORMANCE COMMAND OS</div>
          <div class="ax-rp-title"><span class="cyan">AXION</span> REPLAY</div>
          <div class="ax-rp-sub">Practica el mercado con datos reales, futuro oculto y simulación de riesgo.</div>
        </div>
        <div class="ax-rp-badges">
          <span class="ax-rp-badge">🛡 HISTORICAL DATA</span>
          <span class="ax-rp-badge purple">✓ NO LOOK-AHEAD</span>
          <span class="ax-rp-badge green">● VERIFIED MARKETS</span>
        </div>
      </div>
    </section>
    """)

    # ----- MODO -----
    mode = st.radio(
        "Modo de mercado",
        ["📡 Mercado en vivo", "🕘 Backtesting histórico"],
        horizontal=True,
        index=0 if st.session_state.bt_mode == "LIVE" else 1,
        label_visibility="collapsed",
    )
    st.session_state.bt_mode = "LIVE" if "vivo" in mode else "REPLAY"

    if st.session_state.bt_mode == "LIVE":
        st.html('<div class="ax-rp-mode-note">📡 <b>Mercado en vivo:</b> precio y vela activa actualizados desde Binance Spot. Sin precios sintéticos.</div>')

        c1, c2, c3 = st.columns([2.3, 1.0, 1.15])
        with c1:
            symbol = st.text_input(
                "1. Activo",
                value=st.session_state.bt_symbol,
                placeholder="BTCUSDT, ETHUSDT, SOLUSDT…",
                key="bt_live_symbol_input",
            )
        with c2:
            interval = st.selectbox(
                "2. Timeframe",
                ["5m", "15m", "30m", "1H", "4H", "1D"],
                index=["5m", "15m", "30m", "1H", "4H", "1D"].index(st.session_state.bt_interval),
                key="bt_live_interval",
            )
        with c3:
            st.write("")
            live_load = st.button("▶ Abrir mercado", type="primary", width="stretch")

        try:
            market = resolve_symbol(symbol)
            if live_load or st.session_state.bt_symbol != market.symbol or st.session_state.bt_interval != interval:
                st.session_state.bt_symbol = market.symbol
                st.session_state.bt_interval = interval
            live_frame = fetch_recent_klines(market.symbol, interval, limit=400)
        except MarketDataError as exc:
            st.error(str(exc))
            return

        current = live_frame.iloc[-1]
        first = live_frame.iloc[0]
        pct = ((float(current["close"]) / float(first["open"])) - 1) * 100 if float(first["open"]) else 0.0

        st.html(f"""
        <div class="ax-rp-stepbar">
          <div class="ax-rp-step"><small>1 · ACTIVO</small><strong>{market.display_symbol}</strong></div>
          <div class="ax-rp-step"><small>2 · TIMEFRAME</small><strong>{interval}</strong></div>
          <div class="ax-rp-step"><small>3 · FUENTE</small><strong>{market.provider}</strong></div>
          <div class="ax-rp-step go"><small>4 · ESTADO</small><strong>● LIVE VERIFIED</strong></div>
        </div>
        <div class="ax-rp-source">● DATOS VERIFICADOS · {market.provider} · WebSocket Binance · OHLCV real.</div>
        <div class="ax-rp-metric-grid">
          <div class="ax-rp-metric"><small>MODO</small><strong>LIVE</strong><span>mercado actual</span></div>
          <div class="ax-rp-metric"><small>PRECIO</small><strong>{_fmt_price(float(current['close']))}</strong><span>{pct:+.2f}% ventana visible</span></div>
          <div class="ax-rp-metric"><small>VELAS</small><strong>{len(live_frame)}</strong><span>{interval}</span></div>
          <div class="ax-rp-metric"><small>FUENTE</small><strong>VERIFIED</strong><span>{market.provider}</span></div>
        </div>
        """)

        t1, t2, t3 = st.columns(3)
        with t1:
            st.toggle("🔥 Heatmap", value=False, disabled=True, help="Se activará al conectar la capa de liquidez.")
        with t2:
            st.toggle("🌍 Sesiones", value=False, disabled=True)
        with t3:
            st.toggle("📊 Volumen", value=True, disabled=True)

        _render_live_chart(live_frame, market.symbol, market.display_symbol, interval)

        st.html('<div class="ax-rp-warning"><b>Heatmap:</b> reservado para datos verificables o cálculos claramente etiquetados. AXION PRIME no mostrará liquidaciones inventadas.</div>')
        return

    # ----- REPLAY HISTÓRICO -----
    st.html('<div class="ax-rp-mode-note">🕘 <b>Backtesting histórico:</b> AXION reconstruye el mercado con OHLCV real y mantiene el futuro fuera del gráfico.</div>')

    c1, c2, c3, c4 = st.columns([2.0, 1.25, .95, 1.15])
    with c1:
        symbol = st.text_input(
            "1. Activo",
            value=st.session_state.bt_symbol,
            placeholder="BTCUSDT, ETHUSDT, SOLUSDT…",
            help="La fuente gratuita actual valida mercados Binance Spot.",
            key="bt_replay_symbol_input",
        )
    with c2:
        start_day = st.date_input(
            "2. Fecha",
            value=st.session_state.bt_date,
            max_value=date.today(),
            key="bt_replay_date",
        )
    with c3:
        interval = st.selectbox(
            "3. Timeframe",
            ["5m", "15m", "30m", "1H", "4H", "1D"],
            index=["5m", "15m", "30m", "1H", "4H", "1D"].index(st.session_state.bt_interval),
            key="bt_replay_interval",
        )
    with c4:
        st.write("")
        st.session_state.bt_big_chart = st.toggle(
            "🖥️ Gráfico grande",
            value=bool(st.session_state.bt_big_chart),
            key="bt_big_chart_toggle",
        )

    # Cargar automáticamente cuando activo, fecha o timeframe cambian.
    try:
        requested_market = resolve_symbol(symbol)
        config_changed = (
            st.session_state.bt_dataset is None
            or st.session_state.bt_loaded_symbol != requested_market.symbol
            or st.session_state.bt_loaded_interval != interval
            or st.session_state.bt_loaded_date != start_day
        )
        if config_changed:
            with st.spinner(f"Cargando {requested_market.display_symbol} · {interval} · {start_day:%d/%m/%Y}…"):
                _load_dataset(symbol, interval, start_day)
            st.toast(f"Gráfico actualizado a {interval}", icon="✅")
    except MarketDataError as exc:
        st.error(str(exc))
        if st.session_state.bt_dataset is None:
            st.info("Para probar ahora mismo usa BTCUSDT o ETHUSDT. XAU/USD se activará cuando conectemos una fuente verificable para metales.")
            return

    frame: pd.DataFrame = st.session_state.bt_dataset
    market = st.session_state.bt_market
    if frame is None or market is None or frame.empty:
        st.warning("No hay datos cargados.")
        return

    max_cursor = max(1, len(frame) - 1)
    st.session_state.bt_cursor = max(1, min(int(st.session_state.bt_cursor), max_cursor))
    cursor = int(st.session_state.bt_cursor)
    visible = frame.iloc[: cursor + 1].copy()
    current = visible.iloc[-1]
    first = visible.iloc[0]
    pct = ((float(current["close"]) / float(first["open"])) - 1) * 100 if float(first["open"]) else 0.0
    progress = (cursor / max_cursor) * 100 if max_cursor else 0.0

    st.html(f"""
    <div class="ax-rp-stepbar">
      <div class="ax-rp-step"><small>1 · ACTIVO</small><strong>{market.display_symbol}</strong></div>
      <div class="ax-rp-step"><small>2 · FECHA</small><strong>{st.session_state.bt_date.strftime('%d %b %Y')}</strong></div>
      <div class="ax-rp-step"><small>3 · TIMEFRAME</small><strong>{interval}</strong></div>
      <div class="ax-rp-step go"><small>4 · SESIÓN</small><strong>REPLAY ACTIVO</strong></div>
    </div>
    <div class="ax-rp-source">● DATOS VERIFICADOS · {market.provider} · {len(frame):,} velas descargadas · Futuro oculto.</div>
    """)

    # Main workspace: gráfico grande interactivo.
    if not st.session_state.bt_big_chart:
        t1, t2, t3 = st.columns(3)
        with t1:
            st.toggle("🔥 Heatmap", value=False, disabled=True, help="Se activa en la fase de Liquidity Map.")
        with t2:
            st.toggle("🌍 Sesiones", value=False, disabled=True, help="Se activa en la fase de sesiones.")
        with t3:
            st.toggle("📊 Volumen", value=True, disabled=True)
    else:
        st.html(
            '<div class="ax-rp-source">🖥️ MODO GRÁFICO GRANDE ACTIVO · Herramientas de dibujo visibles · Usa el interruptor superior para volver a la vista normal.</div>'
        )

    workspace_height = 900 if st.session_state.bt_big_chart else 720
    _render_chart(
        visible,
        market.display_symbol,
        interval,
        st.session_state.bt_trade,
        workspace_height=workspace_height,
    )

    # Replay controls del motor Python.
    st.html('<div class="ax-rp-panel-title">CONTROLES DE REPLAY</div>')
    r1, r2, r3, r4, r5, r6, rs = st.columns([.8,.85,1.0,.95,.9,.8,1.0])
    with r1:
        if st.button("⏮ Inicio", width="stretch"):
            st.session_state.bt_cursor = min(80, max_cursor)
            st.rerun()
    with r2:
        if st.button("◀ 1 vela", width="stretch"):
            st.session_state.bt_cursor = max(1, st.session_state.bt_cursor - 1)
            st.rerun()
    with r3:
        if st.button("▶ Play", type="primary", width="stretch"):
            st.session_state.bt_cursor = min(max_cursor, st.session_state.bt_cursor + st.session_state.bt_speed)
            st.rerun()
    with r4:
        st.button("⏸ Pausa", width="stretch", disabled=True, help="Play/Pause automático llega en Fase Replay Premium.")
    with r5:
        if st.button("▶ 1 vela", width="stretch"):
            st.session_state.bt_cursor = min(max_cursor, st.session_state.bt_cursor + 1)
            st.rerun()
    with r6:
        if st.button("⏭ Fin", width="stretch"):
            st.session_state.bt_cursor = max_cursor
            st.rerun()
    with rs:
        speed = st.selectbox(
            "Velocidad",
            [1,2,4,8],
            index=[1,2,4,8].index(st.session_state.bt_speed if st.session_state.bt_speed in [1,2,4,8] else 1),
            format_func=lambda x: f"{x}x",
            label_visibility="collapsed",
        )
        st.session_state.bt_speed = speed

    start_label = pd.Timestamp(frame.iloc[0]["open_time"]).strftime("%d %b %Y")
    end_label = pd.Timestamp(frame.iloc[-1]["open_time"]).strftime("%d %b %Y")
    now_label = pd.Timestamp(current["open_time"]).strftime("%d %b %Y · %H:%M UTC")
    st.html(f"""
    <div class="ax-rp-progress-wrap">
      <div class="ax-rp-progress-top">
        <span>{start_label}</span>
        <span><b>{now_label}</b> · Progreso <span class="ax-rp-progress-value">{progress:.0f}%</span></span>
        <span>{end_label}</span>
      </div>
      <div class="ax-rp-progress-track"><div class="ax-rp-progress-fill" style="width:{progress:.2f}%"></div></div>
    </div>
    """)

    st.html(f"""
    <div class="ax-rp-metric-grid">
      <div class="ax-rp-metric"><small>REPLAY POINT</small><strong>{pd.Timestamp(current['open_time']).strftime('%d %b %Y')}</strong><span>{pd.Timestamp(current['open_time']).strftime('%H:%M UTC')}</span></div>
      <div class="ax-rp-metric"><small>PRECIO ACTUAL</small><strong>{_fmt_price(float(current['close']))}</strong><span>{pct:+.2f}% desde inicio</span></div>
      <div class="ax-rp-metric"><small>VELAS VISIBLES</small><strong>{len(visible)}</strong><span>de {len(frame)} descargadas</span></div>
      <div class="ax-rp-metric"><small>FUENTE</small><strong>VERIFIED</strong><span>{market.provider}</span></div>
    </div>
    """)

    # Execution engine remains explicit below the visual workspace.
    with st.expander("⚡ Ejecutar operación en el motor de backtesting", expanded=False):
        current_price = float(current["close"])
        default_dist = max(current_price * 0.005, 0.000001)

        direction = st.radio("Dirección", ["LONG", "SHORT"], horizontal=True)
        if direction == "LONG":
            default_sl = current_price - default_dist
            default_tp = current_price + default_dist * 2
        else:
            default_sl = current_price + default_dist
            default_tp = current_price - default_dist * 2

        cA, cB, cC, cD = st.columns(4)
        with cA:
            entry = st.number_input("Entrada", min_value=0.0, value=float(current_price), format="%.8f")
        with cB:
            sl = st.number_input("Stop Loss", min_value=0.0, value=float(max(default_sl, 0.00000001)), format="%.8f")
        with cC:
            tp = st.number_input("Take Profit", min_value=0.0, value=float(max(default_tp, 0.00000001)), format="%.8f")
        with cD:
            risk_amount = st.number_input("Riesgo $", min_value=1.0, value=100.0, step=10.0)

        plan = TradePlan(direction=direction, entry=entry, stop=sl, target=tp, risk_amount=risk_amount)
        valid, message = plan.validate()
        st.caption(f"R:R {plan.rr:.2f} · Riesgo ${risk_amount:,.2f}")

        if st.button("▶ Ejecutar en backtest", type="primary", width="stretch", disabled=not valid):
            st.session_state.bt_trade = {
                "direction": direction,
                "entry": entry,
                "stop": sl,
                "target": tp,
                "risk_amount": risk_amount,
                "created_index": cursor,
                "created_at": current["open_time"],
            }
            st.session_state.bt_trade_result = None
            st.rerun()

        if not valid:
            st.warning(message)

        if st.session_state.bt_trade:
            trade = st.session_state.bt_trade
            trade_plan = TradePlan(
                direction=trade["direction"],
                entry=float(trade["entry"]),
                stop=float(trade["stop"]),
                target=float(trade["target"]),
                risk_amount=float(trade["risk_amount"]),
            )
            from_index = int(trade["created_index"])
            trade_candles = frame.iloc[from_index: cursor + 1].copy()
            result = evaluate_trade(trade_plan, trade_candles)
            old_status = st.session_state.bt_trade_result["status"] if isinstance(st.session_state.bt_trade_result, dict) else None
            st.session_state.bt_trade_result = result

            if result["status"] in ("WIN","LOSS") and old_status not in ("WIN","LOSS"):
                st.session_state.bt_session_trades += 1
                st.session_state.bt_session_pnl += float(result["pnl"])
                if result["status"] == "WIN":
                    st.session_state.bt_session_wins += 1
                else:
                    st.session_state.bt_session_losses += 1

            status = result["status"]
            if status == "WIN":
                st.success(f"TP alcanzado · {result['r_multiple']:+.2f}R · ${result['pnl']:+,.2f}")
            elif status == "LOSS":
                st.error(f"SL alcanzado · {result['r_multiple']:+.2f}R · ${result['pnl']:+,.2f}")
            elif status == "OPEN":
                st.info(f"Abierta · {result['r_multiple']:+.2f}R · ${result['pnl']:+,.2f}")
            else:
                st.warning("Pendiente: el precio todavía no tocó la entrada.")

            if st.button("Limpiar operación", width="stretch"):
                st.session_state.bt_trade = None
                st.session_state.bt_trade_result = None
                st.rerun()

    # Session metrics strip.
    trades = int(st.session_state.bt_session_trades)
    wins = int(st.session_state.bt_session_wins)
    losses = int(st.session_state.bt_session_losses)
    pnl = float(st.session_state.bt_session_pnl)
    win_rate = (wins / trades * 100) if trades else 0.0
    latest = st.session_state.bt_trade_result if isinstance(st.session_state.bt_trade_result, dict) else {}
    mfe = float(latest.get("mfe_r", 0.0))
    mae = float(latest.get("mae_r", 0.0))
    profit_factor = (wins * 2 / losses) if losses > 0 else (wins * 2 if wins else 0.0)

    st.html(f"""
    <div class="ax-rp-bottom-grid">
      <div class="ax-rp-bottom-card"><small>RESULTADO SESIÓN</small><strong class="{'pos' if pnl >= 0 else 'neg'}">${pnl:+,.2f}</strong></div>
      <div class="ax-rp-bottom-card"><small>WIN RATE</small><strong>{win_rate:.1f}%</strong></div>
      <div class="ax-rp-bottom-card"><small>MFE ACTUAL</small><strong>{mfe:.2f}R</strong></div>
      <div class="ax-rp-bottom-card"><small>MAE ACTUAL</small><strong class="neg">-{mae:.2f}R</strong></div>
      <div class="ax-rp-bottom-card"><small>PROFIT FACTOR*</small><strong>{profit_factor:.2f}</strong></div>
      <div class="ax-rp-bottom-card"><small>TRADES CERRADOS</small><strong>{trades}</strong></div>
    </div>
    <div style="color:#566785;font-size:7px;margin-top:-6px">* Métrica provisional de sesión. El motor estadístico completo se implementa en la fase de Analytics.</div>
    """)

    # Favorites: collapse them so they don't interrupt the trading workflow.
    with st.expander("⭐ Mercados favoritos", expanded=False):
        fav_cols = st.columns(4)
        for i, fav in enumerate(st.session_state.bt_favorites[:4]):
            with fav_cols[i]:
                if st.button(f"⭐ {fav}", key=f"bt_fav_{fav}", width="stretch"):
                    try:
                        _load_dataset(fav, st.session_state.bt_interval, st.session_state.bt_date)
                        st.rerun()
                    except MarketDataError as exc:
                        st.error(str(exc))

        add_col, action_col = st.columns([3,1])
        with add_col:
            fav_input = st.text_input("Agregar favorito", placeholder="Ej: SOLUSDT", key="bt_fav_input")
        with action_col:
            st.write("")
            if st.button("Guardar", width="stretch"):
                try:
                    resolved = resolve_symbol(fav_input)
                    if resolved.symbol not in st.session_state.bt_favorites:
                        st.session_state.bt_favorites.append(resolved.symbol)
                    st.success(f"{resolved.display_symbol} agregado.")
                except MarketDataError as exc:
                    st.error(str(exc))
