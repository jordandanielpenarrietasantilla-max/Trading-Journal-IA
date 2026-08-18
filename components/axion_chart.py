from __future__ import annotations

import streamlit as st


HTML = r"""
<div id="axion-terminal" class="axion-terminal">
  <header class="axion-topbar">
    <div class="brand-block">
      <div class="brand">AXION <span>REPLAY</span></div>
      <div class="brand-sub">Trading workspace · verified historical data</div>
    </div>

    <div class="market-block">
      <button class="symbol-button" id="symbol-button" type="button">
        <span class="status-dot"></span>
        <span id="symbol-label">BTC/USDT</span>
      </button>

      <div class="tf-strip" id="tf-strip">
        <button type="button" data-tf="1m">1m</button>
        <button type="button" data-tf="5m">5m</button>
        <button type="button" data-tf="15m">15m</button>
        <button type="button" data-tf="30m">30m</button>
        <button type="button" data-tf="1H">1H</button>
        <button type="button" data-tf="4H">4H</button>
        <button type="button" data-tf="1D">D</button>
      </div>
    </div>

    <div class="top-actions">
      <label class="mini-switch">
        <input id="heatmap-toggle" type="checkbox" disabled>
        <span></span><em>Heatmap</em>
      </label>
      <label class="mini-switch">
        <input id="session-toggle" type="checkbox" disabled>
        <span></span><em>Sesiones</em>
      </label>
      <label class="mini-switch">
        <input id="volume-toggle" type="checkbox" checked>
        <span></span><em>Volumen</em>
      </label>
      <button class="icon-button" id="settings-btn" type="button" title="Personalización">⚙</button>
      <button class="fullscreen-button" id="fullscreen-btn" type="button" title="Pantalla completa">⛶</button>
    </div>
  </header>

  <section class="terminal-body">
    <aside class="drawing-toolbar" id="drawing-toolbar">
      <button class="draw-btn active" type="button" data-tool="cursor" title="Cursor">
        <svg viewBox="0 0 24 24"><path d="M5 3l12 8-6 2-3 6z"/></svg><span>Cursor</span>
      </button>
      <button class="draw-btn" type="button" data-tool="trend" title="Línea de tendencia">
        <svg viewBox="0 0 24 24"><path d="M5 18L19 6"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="6" r="2"/></svg><span>Tendencia</span>
      </button>
      <button class="draw-btn" type="button" data-tool="horizontal" title="Línea horizontal">
        <svg viewBox="0 0 24 24"><path d="M4 12h16"/></svg><span>Horizontal</span>
      </button>
      <button class="draw-btn" type="button" data-tool="rectangle" title="Rectángulo">
        <svg viewBox="0 0 24 24"><rect x="5" y="6" width="14" height="12"/></svg><span>Zona</span>
      </button>
      <button class="draw-btn" type="button" data-tool="fib" title="Fibonacci">
        <svg viewBox="0 0 24 24"><path d="M5 6h14M5 10h10M5 14h14M5 18h8"/></svg><span>Fibonacci</span>
      </button>
      <button class="draw-btn" type="button" data-tool="text" title="Texto">
        <svg viewBox="0 0 24 24"><path d="M5 6h14M12 6v13M8 19h8"/></svg><span>Texto</span>
      </button>
      <button class="draw-btn long-btn" type="button" data-tool="long" title="Posición larga">
        <svg viewBox="0 0 24 24"><path d="M12 20V5M7 10l5-5 5 5"/></svg><span>Long</span>
      </button>
      <button class="draw-btn short-btn" type="button" data-tool="short" title="Posición corta">
        <svg viewBox="0 0 24 24"><path d="M12 4v15M7 14l5 5 5-5"/></svg><span>Short</span>
      </button>
      <button class="draw-btn" type="button" data-tool="measure" title="Medición">
        <svg viewBox="0 0 24 24"><path d="M5 18L18 5M6 14l4 4M10 10l4 4M14 6l4 4"/></svg><span>Medir</span>
      </button>
      <button class="draw-btn" type="button" data-tool="magnet" title="Imán">
        <svg viewBox="0 0 24 24"><path d="M7 5v7a5 5 0 0010 0V5M7 5h4v5M17 5h-4v5"/></svg><span>Imán</span>
      </button>
      <button class="draw-btn" type="button" data-tool="clear" title="Borrar dibujos">
        <svg viewBox="0 0 24 24"><path d="M7 7h10M9 7V5h6v2M9 10v8M12 10v8M15 10v8M8 7l1 13h6l1-13"/></svg><span>Borrar</span>
      </button>
    </aside>

    <main class="chart-column">
      <div class="chart-meta">
        <div class="asset-title-wrap">
          <div class="asset-title">
            <strong id="chart-symbol">BTC/USDT</strong>
            <span id="chart-interval">· 1H</span>
            <span class="verified">● VERIFIED OHLCV</span>
          </div>
          <div class="asset-subtitle" id="asset-subtitle">Bitcoin / TetherUS · AXION PRIME</div>
        </div>
        <div class="ohlc" id="ohlc-label">—</div>
      </div>

      <div class="chart-stage" id="chart-stage">
        <div id="chart-host"></div>
        <canvas id="drawing-layer"></canvas>

        <div class="floating-tool-panel" id="fib-panel">
          <div class="floating-title"><span>Fibonacci</span><button type="button" data-close-panel>×</button></div>
          <div class="fib-levels">
            <label><input type="checkbox" checked data-fib-level="0"><span>0</span></label>
            <label><input type="checkbox" checked data-fib-level="0.236"><span>0.236</span></label>
            <label><input type="checkbox" checked data-fib-level="0.382"><span>0.382</span></label>
            <label><input type="checkbox" checked data-fib-level="0.5"><span>0.5</span></label>
            <label><input type="checkbox" checked data-fib-level="0.618"><span>0.618</span></label>
            <label><input type="checkbox" checked data-fib-level="0.705"><span>0.705</span></label>
            <label><input type="checkbox" checked data-fib-level="0.786"><span>0.786</span></label>
            <label><input type="checkbox" checked data-fib-level="1"><span>1</span></label>
          </div>
          <div class="panel-note">Marca dos puntos en el gráfico. Los niveles pueden personalizarse después.</div>
        </div>

        <div class="floating-tool-panel position-panel" id="position-panel">
          <div class="floating-title"><span>Herramienta de posición</span><button type="button" data-close-panel>×</button></div>
          <div class="position-tabs">
            <button id="position-long" type="button" class="selected long">LONG</button>
            <button id="position-short" type="button" class="short">SHORT</button>
          </div>
          <label class="field-label">R:R inicial
            <select id="rr-select">
              <option value="1.5">1 : 1.5</option>
              <option value="2" selected>1 : 2</option>
              <option value="2.5">1 : 2.5</option>
              <option value="3">1 : 3</option>
            </select>
          </label>

          <div class="position-color-row">
            <label>
              <span>Entrada</span>
              <input type="color" id="position-color-entry" value="#2f8cff">
            </label>
            <label>
              <span>Stop</span>
              <input type="color" id="position-color-stop" value="#ff4969">
            </label>
            <label>
              <span>Target</span>
              <input type="color" id="position-color-target" value="#12db99">
            </label>
          </div>

          <div class="panel-note">
            Haz clic para crear la posición. Arrastra Entry, SL o TP por separado.
            Arrastra el centro del bloque para mover la posición completa.
          </div>
        </div>

        <div class="replay-dock">
          <div class="replay-left">
            <button type="button" data-replay="start" title="Inicio">⏮</button>
            <button type="button" data-replay="back" title="1 vela atrás">◀</button>
            <button type="button" id="play-btn" title="Reproducir">▶</button>
            <button type="button" id="pause-btn" title="Pausa">Ⅱ</button>
            <button type="button" data-replay="next" title="1 vela adelante">▶|</button>
            <button type="button" data-replay="end" title="Fin">⏭</button>
          </div>
          <div class="replay-progress">
            <div class="replay-date" id="replay-date">—</div>
            <input id="replay-range" type="range" min="0" max="1" value="0">
          </div>
          <div class="replay-right">
            <select id="speed-select">
              <option value="1">1x</option>
              <option value="2">2x</option>
              <option value="4">4x</option>
              <option value="8">8x</option>
            </select>
            <input id="replay-date-input" type="date" title="Saltar a fecha">
          </div>
        </div>
      </div>
    </main>

    <aside class="info-sidebar">
      <section class="side-panel market-panel">
        <div class="panel-heading">INFORMACIÓN DE MERCADO</div>
        <div class="big-price" id="market-price">—</div>
        <div class="market-source" id="market-source">Binance Spot · Historical</div>
        <div class="info-grid">
          <div><span>Activo</span><b id="info-symbol">—</b></div>
          <div><span>Timeframe</span><b id="info-timeframe">—</b></div>
          <div><span>Máximo visible</span><b id="info-high">—</b></div>
          <div><span>Mínimo visible</span><b id="info-low">—</b></div>
          <div><span>Velas</span><b id="info-bars">—</b></div>
          <div><span>Replay</span><b id="info-progress">—</b></div>
        </div>
      </section>

      <section class="side-panel position-info">
        <div class="panel-heading">POSICIÓN</div>
        <div id="empty-position" class="empty-position">Selecciona LONG o SHORT y marca una entrada en el gráfico.</div>
        <div id="position-details" hidden>
          <div class="position-direction" id="position-direction">LONG</div>
          <div class="info-grid single">
            <div><span>Entrada</span><b id="position-entry">—</b></div>
            <div><span>Stop Loss</span><b id="position-stop" class="negative">—</b></div>
            <div><span>Take Profit</span><b id="position-target" class="positive">—</b></div>
            <div><span>R:R</span><b id="position-rr">—</b></div>
          </div>
          <button id="execute-position" type="button" class="primary-action">▶ Ejecutar en AXION</button>
        </div>
      </section>

      <section class="side-panel settings-panel" id="workspace-settings">
        <div class="panel-heading">PERSONALIZACIÓN</div>
        <label class="field-label">Workspace
          <input id="workspace-name" value="Workspace Trader">
        </label>

        <div class="settings-section-title">APARIENCIA DEL GRÁFICO</div>
        <div class="color-grid">
          <label>Vela alcista <input type="color" id="color-up" value="#15d9c3"></label>
          <label>Vela bajista <input type="color" id="color-down" value="#ff4969"></label>
          <label>Fondo <input type="color" id="color-bg" value="#020711"></label>
          <label>Rejilla <input type="color" id="color-grid" value="#24334e"></label>
        </div>

        <div class="settings-section-title">POSICIONES</div>
        <div class="color-grid">
          <label>Entrada <input type="color" id="color-entry" value="#2f8cff"></label>
          <label>Stop Loss <input type="color" id="color-stop" value="#ff4969"></label>
          <label>Take Profit <input type="color" id="color-target" value="#12db99"></label>
          <label>Fibonacci <input type="color" id="color-fib" value="#43d6e8"></label>
        </div>

        <label class="field-label">Plantilla Fibonacci
          <select id="fib-template">
            <option>AXION PRIME</option>
            <option>ICT / OTE</option>
            <option>Personalizada</option>
          </select>
        </label>
        <label class="field-label">Riesgo predeterminado
          <select id="risk-template">
            <option>0.5%</option>
            <option selected>1.0%</option>
            <option>2.0%</option>
          </select>
        </label>

        <button id="reset-colors" class="secondary-action" type="button">Restablecer colores</button>
        <button id="save-workspace" class="secondary-action" type="button">Guardar workspace</button>
      </section>
    </aside>
  </section>

  <div class="symbol-modal" id="symbol-modal" hidden>
    <div class="symbol-modal-card">
      <div class="floating-title"><span>Cambiar mercado</span><button id="symbol-close" type="button">×</button></div>
      <input id="symbol-input" placeholder="BTCUSDT, ETHUSDT, SOLUSDT">
      <button id="symbol-apply" type="button" class="primary-action">Abrir mercado</button>
      <div class="panel-note">AXION solo cargará mercados que pueda verificar en la fuente conectada.</div>
    </div>
  </div>
</div>
"""


CSS = r"""
:host {
  display:block;
  width:100%;
  height:100%;
  color:#eaf2ff;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
*{box-sizing:border-box}
button,input,select{font:inherit}
button{user-select:none}
.axion-terminal{
  width:100%;
  height:100%;
  min-height:720px;
  overflow:hidden;
  background:#030812;
  border:1px solid rgba(86,124,191,.28);
  border-radius:14px;
  display:grid;
  grid-template-rows:62px minmax(0,1fr);
  color:#dce7fb;
}
.axion-terminal:fullscreen{
  width:100vw;height:100vh;min-height:100vh;border:0;border-radius:0;background:#020711;
}
.axion-topbar{
  min-width:0;
  display:grid;
  grid-template-columns:250px minmax(410px,1fr) auto;
  align-items:center;
  gap:16px;
  padding:0 16px;
  background:linear-gradient(180deg,#06101f,#040a14);
  border-bottom:1px solid rgba(80,118,186,.22);
}
.brand{font-size:20px;font-weight:850;letter-spacing:.7px;color:#f4f7fd}
.brand span{color:#45d9ee}
.brand-sub{font-size:10px;color:#6e7f9d;margin-top:2px}
.market-block{display:flex;align-items:center;gap:18px;min-width:0}
.symbol-button{
  border:1px solid rgba(70,118,197,.28);
  background:#071225;color:#f6f8fc;border-radius:9px;padding:8px 11px;
  font-weight:750;cursor:pointer;white-space:nowrap
}
.status-dot{display:inline-block;width:7px;height:7px;background:#00eba0;border-radius:50%;margin-right:7px}
.tf-strip{display:flex;gap:3px;align-items:center;overflow:auto}
.tf-strip button{
  min-width:38px;border:1px solid transparent;background:transparent;color:#7f91b0;
  padding:7px 8px;border-radius:7px;cursor:pointer;font-size:12px
}
.tf-strip button:hover{background:#0a1730;color:#dce8ff}
.tf-strip button.active{background:#0b2341;border-color:#195b82;color:#55d9ed}
.top-actions{display:flex;align-items:center;gap:9px}
.icon-button,.fullscreen-button{
  width:37px;height:37px;border-radius:9px;border:1px solid rgba(80,118,186,.28);
  background:#071224;color:#becce4;cursor:pointer;font-size:16px
}
.fullscreen-button{border-color:rgba(119,84,255,.48);color:#e3dfff}
.mini-switch{display:flex;align-items:center;gap:6px;color:#7d8ca7;font-size:10px}
.mini-switch input{display:none}
.mini-switch span{
  width:31px;height:17px;border-radius:999px;background:#142038;position:relative;border:1px solid #263653
}
.mini-switch span:after{
  content:"";position:absolute;width:11px;height:11px;border-radius:50%;background:#68758c;left:2px;top:2px
}
.mini-switch input:checked + span{background:#0a5260}
.mini-switch input:checked + span:after{left:16px;background:#37dbe8}
.mini-switch em{font-style:normal}
.terminal-body{
  min-height:0;
  display:grid;
  grid-template-columns:64px minmax(0,1fr) 255px;
}
.drawing-toolbar{
  min-height:0;background:#050b16;border-right:1px solid rgba(80,118,186,.22);
  padding:7px 6px;display:flex;flex-direction:column;align-items:center;gap:3px;overflow:auto
}
.draw-btn{
  width:50px;min-height:49px;border:1px solid transparent;background:transparent;color:#7185a7;
  border-radius:9px;cursor:pointer;padding:5px 2px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:3px
}
.draw-btn svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
.draw-btn span{font-size:7px}
.draw-btn:hover{background:#07162b;color:#d8e6ff}
.draw-btn.active{background:#092239;color:#48dbed;border-color:#176277}
.long-btn{color:#14d998}.short-btn{color:#ff4968}
.chart-column{min-width:0;min-height:0;display:grid;grid-template-rows:34px minmax(0,1fr)}
.chart-meta{
  display:flex;align-items:center;justify-content:space-between;padding:0 11px;
  border-bottom:1px solid rgba(80,118,186,.14);background:#030914;font-size:11px
}
.asset-title-wrap{display:flex;flex-direction:column;justify-content:center;min-width:0}
.asset-title{display:flex;align-items:center;gap:3px;min-width:0}
.chart-meta strong{color:#eef4ff;font-size:12px}
.chart-meta span{color:#7f91ad;margin-left:5px}
.chart-meta .verified{color:#1fd7a1;font-size:8px}
.asset-subtitle{font-size:8px;color:#617390;margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ohlc{color:#7f91ad;font-size:9px}
.chart-stage{min-height:0;position:relative;background:#020711}
#chart-host{position:absolute;inset:0 0 54px 0}
#drawing-layer{position:absolute;inset:0 0 54px 0;width:100%;height:calc(100% - 54px);pointer-events:none;touch-action:none;z-index:4}
.replay-dock{
  position:absolute;left:0;right:0;bottom:0;height:54px;
  background:rgba(4,10,20,.96);border-top:1px solid rgba(80,118,186,.22);
  display:grid;grid-template-columns:auto minmax(220px,1fr) auto;align-items:center;gap:12px;padding:0 12px;z-index:9
}
.replay-left{display:flex;gap:4px}
.replay-left button{
  width:36px;height:34px;border-radius:8px;border:1px solid rgba(80,118,186,.24);
  background:#071225;color:#9dadc7;cursor:pointer
}
#play-btn{color:#fff;background:linear-gradient(135deg,#28cce4,#7956ff);border:0}
.replay-progress{display:grid;grid-template-columns:120px 1fr;gap:8px;align-items:center}
.replay-date{font-size:9px;color:#9baccc;white-space:nowrap}
#replay-range{width:100%;accent-color:#45cfe6}
.replay-right{display:flex;gap:7px;align-items:center}
.replay-right select,.replay-right input{
  height:32px;background:#071225;color:#c7d4ea;border:1px solid rgba(80,118,186,.25);border-radius:7px;padding:0 7px;font-size:10px
}
.info-sidebar{
  background:#050b16;border-left:1px solid rgba(80,118,186,.22);
  padding:9px;overflow:auto;min-height:0
}
.side-panel{
  border:1px solid rgba(70,111,181,.25);background:#071225;border-radius:10px;padding:11px;margin-bottom:9px
}
.panel-heading{font-size:9px;font-weight:800;letter-spacing:.6px;color:#dce7fa;margin-bottom:9px}
.big-price{font-size:23px;font-weight:850;color:#28e0c2}
.market-source{font-size:8px;color:#687a99;margin-top:1px;margin-bottom:9px}
.info-grid{display:grid;gap:7px}.info-grid.single{gap:8px}
.info-grid>div{display:flex;justify-content:space-between;gap:8px;font-size:8px;color:#7183a2}
.info-grid b{color:#e6eefc;font-weight:700}.positive{color:#15dc9a!important}.negative{color:#ff4f6d!important}
.empty-position{font-size:9px;line-height:1.5;color:#6f809e;padding:6px 0}
.position-direction{font-size:12px;font-weight:800;color:#19d99b;margin-bottom:9px}
.primary-action,.secondary-action{
  width:100%;border-radius:8px;padding:9px 10px;cursor:pointer;margin-top:10px;font-weight:750;font-size:10px
}
.primary-action{border:0;background:linear-gradient(90deg,#21cde5,#7657ff);color:white}
.secondary-action{border:1px solid rgba(67,209,228,.28);background:#08182c;color:#64d8e7}
.field-label{display:block;font-size:8px;color:#7486a4;margin-top:8px}
.field-label input,.field-label select{
  width:100%;margin-top:4px;border:1px solid rgba(80,118,186,.25);border-radius:7px;
  background:#050c18;color:#d7e3f6;padding:7px;font-size:9px
}
.settings-section-title{font-size:7px;font-weight:800;letter-spacing:.7px;color:#5f7396;margin-top:12px;margin-bottom:5px}
.color-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.color-grid label{font-size:7px;color:#7b8eac;display:flex;align-items:center;justify-content:space-between;gap:5px}
.color-grid input[type=color]{width:34px;height:23px;padding:0;border:1px solid #31445f;border-radius:5px;background:#050c18;cursor:pointer}
.floating-tool-panel{
  display:none;position:absolute;left:12px;top:12px;width:220px;background:rgba(5,12,25,.97);
  border:1px solid rgba(59,206,225,.28);border-radius:10px;padding:10px;z-index:15
}
.floating-tool-panel.open{display:block}
.floating-title{display:flex;align-items:center;justify-content:space-between;font-size:10px;font-weight:800;color:#e6eefb}
.floating-title button{border:0;background:transparent;color:#7e8daa;font-size:18px;cursor:pointer}
.fib-levels{display:grid;grid-template-columns:1fr 1fr;gap:5px;margin-top:8px}
.fib-levels label{display:flex;align-items:center;gap:5px;font-size:9px;color:#91a1ba}
.panel-note{font-size:8px;color:#697a96;line-height:1.45;margin-top:9px}
.position-tabs{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:9px}
.position-tabs button{padding:8px;border-radius:7px;border:1px solid #28405e;background:#071225;color:#8695ae;cursor:pointer}
.position-tabs .long.selected{border-color:#117e66;color:#14d99a;background:#06251f}
.position-tabs .short.selected{border-color:#873047;color:#ff526e;background:#2a0b15}
.position-color-row{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:6px;
  margin-top:9px;
}
.position-color-row label{
  display:flex;
  flex-direction:column;
  gap:4px;
  color:#7f91ad;
  font-size:7px;
}
.position-color-row input[type=color]{
  width:100%;
  height:28px;
  border:1px solid #30445f;
  border-radius:6px;
  padding:2px;
  background:#050c18;
  cursor:pointer;
}
.symbol-modal{
  position:absolute;inset:0;background:rgba(0,0,0,.72);z-index:50;display:flex;align-items:flex-start;justify-content:center;padding-top:90px
}
.symbol-modal[hidden]{display:none}
.symbol-modal-card{
  width:min(420px,90%);padding:14px;border-radius:12px;background:#071225;border:1px solid rgba(84,124,192,.35)
}
.symbol-modal-card input{
  width:100%;padding:10px;margin-top:12px;border-radius:8px;border:1px solid #293b5b;background:#050c18;color:#e5eefc
}
@media(max-width:1050px){
  .axion-topbar{grid-template-columns:190px 1fr auto}
  .mini-switch em{display:none}
  .terminal-body{grid-template-columns:58px minmax(0,1fr) 220px}
}
"""


JS = r"""
async function ensureLightweightCharts() {
  if (window.LightweightCharts) return window.LightweightCharts;

  await new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-axion-lwc]');
    if (existing) {
      const check = setInterval(() => {
        if (window.LightweightCharts) {
          clearInterval(check);
          resolve();
        }
      }, 30);
      setTimeout(() => {
        clearInterval(check);
        if (window.LightweightCharts) resolve();
        else reject(new Error('Lightweight Charts no cargó.'));
      }, 6000);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://unpkg.com/lightweight-charts@4.2.3/dist/lightweight-charts.standalone.production.js';
    script.dataset.axionLwc = '1';
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });

  return window.LightweightCharts;
}

function fmt(value, digits = 2) {
  const n = Number(value);
  if (!Number.isFinite(n)) return '—';
  return n.toLocaleString('en-US', {minimumFractionDigits: digits, maximumFractionDigits: digits});
}

function dateText(epochSeconds) {
  const d = new Date(epochSeconds * 1000);
  return d.toLocaleString('es-CL', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}

export default async function(component) {
  const { parentElement, data, setTriggerValue, setStateValue } = component;
  const root = parentElement.querySelector('#axion-terminal');
  if (!root || !data) return;

  let cleanupFns = [];
  let playTimer = null;

  try {
    const LWC = await ensureLightweightCharts();

    const candles = Array.isArray(data.candles) ? data.candles : [];
    const volumes = Array.isArray(data.volumes) ? data.volumes : [];

    const marketNames = {
      BTCUSDT: 'Bitcoin / TetherUS',
      ETHUSDT: 'Ethereum / TetherUS',
      SOLUSDT: 'Solana / TetherUS',
      BNBUSDT: 'BNB / TetherUS',
      XRPUSDT: 'XRP / TetherUS'
    };

    const defaultColors = {
      up:'#15d9c3',
      down:'#ff4969',
      background:'#020711',
      grid:'#24334e',
      entry:'#2f8cff',
      stop:'#ff4969',
      target:'#12db99',
      fib:'#43d6e8'
    };

    let themeColors = {
      ...defaultColors,
      ...((data.workspace && data.workspace.colors) || {})
    };
    let currentCursor = Math.max(0, Math.min(Number(data.cursor ?? 0), Math.max(0, candles.length - 1)));
    let activeTool = 'cursor';
    let drawingStart = null;
    let drawingDraft = null;
    let drawings = [];
    let position = null;
    let draggingPositionHandle = null;
    let draggingWholePosition = false;
    let dragStartPrice = null;
    let dragStartPosition = null;

    const chartHost = parentElement.querySelector('#chart-host');
    const canvas = parentElement.querySelector('#drawing-layer');
    const ctx = canvas.getContext('2d');
    const chartStage = parentElement.querySelector('#chart-stage');

    const chart = LWC.createChart(chartHost, {
      width: chartHost.clientWidth,
      height: chartHost.clientHeight,
      layout: {background: {type:'solid', color:themeColors.background}, textColor:'#8292ad'},
      grid: {
        vertLines: {color:themeColors.grid},
        horzLines: {color:themeColors.grid}
      },
      rightPriceScale: {borderColor:'rgba(69,99,154,.24)'},
      timeScale: {
        borderColor:'rgba(69,99,154,.24)',
        timeVisible:true,
        secondsVisible:false,
        rightOffset:5
      },
      crosshair: {mode:LWC.CrosshairMode.Normal}
    });

    const series = chart.addCandlestickSeries({
      upColor:themeColors.up,
      downColor:themeColors.down,
      borderUpColor:themeColors.up,
      borderDownColor:themeColors.down,
      wickUpColor:themeColors.up,
      wickDownColor:themeColors.down
    });

    const volumeSeries = chart.addHistogramSeries({
      priceFormat:{type:'volume'},
      priceScaleId:'',
      scaleMargins:{top:.83,bottom:0}
    });

    function visibleCandles() {
      return candles.slice(0, currentCursor + 1);
    }
    function visibleVolumes() {
      return volumes.slice(0, currentCursor + 1);
    }
    function applyReplayData(fit = false) {
      series.setData(visibleCandles());
      volumeSeries.setData(visibleVolumes());
      if (fit) chart.timeScale().fitContent();
      updateReplayUI();
      drawAll();
    }

    function currentCandle() {
      return candles[currentCursor] || candles[candles.length - 1] || null;
    }

    function updateReplayUI() {
      const c = currentCandle();
      if (!c) return;

      parentElement.querySelector('#replay-date').textContent = dateText(c.time);
      const range = parentElement.querySelector('#replay-range');
      range.max = Math.max(0, candles.length - 1);
      range.value = currentCursor;

      parentElement.querySelector('#market-price').textContent = fmt(c.close, 2);
      parentElement.querySelector('#info-progress').textContent =
        candles.length ? Math.round(((currentCursor + 1) / candles.length) * 100) + '%' : '0%';
      parentElement.querySelector('#info-bars').textContent = String(currentCursor + 1);

      const visible = visibleCandles();
      if (visible.length) {
        parentElement.querySelector('#info-high').textContent = fmt(Math.max(...visible.map(x => Number(x.high))), 2);
        parentElement.querySelector('#info-low').textContent = fmt(Math.min(...visible.map(x => Number(x.low))), 2);
      }

      parentElement.querySelector('#ohlc-label').textContent =
        `O ${fmt(c.open,2)}  H ${fmt(c.high,2)}  L ${fmt(c.low,2)}  C ${fmt(c.close,2)}`;
    }

    // Header / market labels
    parentElement.querySelector('#symbol-label').textContent = data.symbol_label || data.symbol || '—';
    parentElement.querySelector('#chart-symbol').textContent = data.symbol_label || data.symbol || '—';
    parentElement.querySelector('#asset-subtitle').textContent =
      (data.market_name || marketNames[String(data.symbol || '').toUpperCase()] || 'Mercado verificado') + ' · AXION PRIME';
    parentElement.querySelector('#chart-interval').textContent = '· ' + (data.interval || '—');
    parentElement.querySelector('#info-symbol').textContent = data.symbol_label || data.symbol || '—';
    parentElement.querySelector('#info-timeframe').textContent = data.interval || '—';
    parentElement.querySelector('#market-source').textContent = (data.source || 'Verified source') + ' · Historical';

    parentElement.querySelectorAll('[data-tf]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.tf === data.interval);
      btn.onclick = () => {
        if (btn.dataset.tf !== data.interval) {
          setTriggerValue('timeframe', btn.dataset.tf);
        }
      };
    });

    // Symbol modal
    const symbolModal = parentElement.querySelector('#symbol-modal');
    parentElement.querySelector('#symbol-button').onclick = () => {
      symbolModal.hidden = false;
      parentElement.querySelector('#symbol-input').value = String(data.symbol || '');
      setTimeout(() => parentElement.querySelector('#symbol-input').focus(), 10);
    };
    parentElement.querySelector('#symbol-close').onclick = () => symbolModal.hidden = true;
    parentElement.querySelector('#symbol-apply').onclick = () => {
      const value = parentElement.querySelector('#symbol-input').value.trim().toUpperCase();
      if (value && value !== data.symbol) setTriggerValue('symbol', value);
      symbolModal.hidden = true;
    };
    parentElement.querySelector('#symbol-input').onkeydown = e => {
      if (e.key === 'Enter') parentElement.querySelector('#symbol-apply').click();
    };

    // Fullscreen real
    const fullscreenBtn = parentElement.querySelector('#fullscreen-btn');
    fullscreenBtn.onclick = async () => {
      try {
        if (!document.fullscreenElement) {
          await root.requestFullscreen();
        } else {
          await document.exitFullscreen();
        }
      } catch (err) {
        console.error('Fullscreen error', err);
      }
    };

    const onFullscreen = () => {
      fullscreenBtn.textContent = document.fullscreenElement ? '⤢' : '⛶';
      setTimeout(() => resizeAll(), 60);
    };
    document.addEventListener('fullscreenchange', onFullscreen);
    cleanupFns.push(() => document.removeEventListener('fullscreenchange', onFullscreen));

    // Replay controls entirely in chart frontend.
    function stepTo(nextCursor, fit = false) {
      currentCursor = Math.max(0, Math.min(nextCursor, candles.length - 1));
      applyReplayData(fit);
    }

    parentElement.querySelectorAll('[data-replay]').forEach(btn => {
      btn.onclick = () => {
        const action = btn.dataset.replay;
        if (action === 'start') stepTo(Math.min(Number(data.context_cursor ?? 80), candles.length - 1), true);
        if (action === 'back') stepTo(currentCursor - 1);
        if (action === 'next') stepTo(currentCursor + 1);
        if (action === 'end') stepTo(candles.length - 1, true);
      };
    });

    const playBtn = parentElement.querySelector('#play-btn');
    const pauseBtn = parentElement.querySelector('#pause-btn');
    const speedSelect = parentElement.querySelector('#speed-select');

    function stopPlay() {
      if (playTimer) clearInterval(playTimer);
      playTimer = null;
      playBtn.classList.remove('playing');
    }
    function startPlay() {
      stopPlay();
      const speed = Number(speedSelect.value || 1);
      playBtn.classList.add('playing');
      playTimer = setInterval(() => {
        if (currentCursor >= candles.length - 1) {
          stopPlay();
          return;
        }
        stepTo(currentCursor + 1);
      }, Math.max(90, 650 / speed));
    }

    playBtn.onclick = startPlay;
    pauseBtn.onclick = stopPlay;
    cleanupFns.push(stopPlay);

    const range = parentElement.querySelector('#replay-range');
    range.oninput = () => {
      stopPlay();
      stepTo(Number(range.value));
    };

    const dateInput = parentElement.querySelector('#replay-date-input');
    if (data.start_date) dateInput.value = data.start_date;
    dateInput.onchange = () => {
      if (dateInput.value) setTriggerValue('date', dateInput.value);
    };

    // Drawing engine
    function canvasRect() {
      return canvas.getBoundingClientRect();
    }
    function pointerPoint(e) {
      const r = canvasRect();
      return {x:e.clientX-r.left, y:e.clientY-r.top};
    }
    function priceFromY(y) {
      const p = series.coordinateToPrice(y);
      const c = currentCandle();
      return p == null ? Number(c?.close || 0) : Number(p);
    }
    function yFromPrice(p) {
      const y = series.priceToCoordinate(Number(p));
      return y == null ? 0 : Number(y);
    }
    function drawLine(a,b,color='#47d8eb',dash=[]) {
      ctx.save();
      ctx.strokeStyle=color; ctx.lineWidth=1.4; ctx.setLineDash(dash);
      ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
      ctx.restore();
    }
    function drawZone(a,b) {
      const x=Math.min(a.x,b.x), y=Math.min(a.y,b.y);
      const w=Math.abs(a.x-b.x), h=Math.abs(a.y-b.y);
      ctx.save();
      ctx.fillStyle='rgba(44,172,208,.09)';
      ctx.strokeStyle='rgba(69,211,231,.86)';
      ctx.lineWidth=1.2;
      ctx.fillRect(x,y,w,h);ctx.strokeRect(x,y,w,h);
      ctx.restore();
    }
    function fibLevels() {
      return [...parentElement.querySelectorAll('[data-fib-level]')]
        .filter(x => x.checked)
        .map(x => Number(x.dataset.fibLevel));
    }
    function drawFib(a,b,levels) {
      const left=Math.min(a.x,b.x), right=Math.max(a.x,b.x);
      const top=Math.min(a.y,b.y), bottom=Math.max(a.y,b.y);
      const colors=['#d5dfef',themeColors.fib,themeColors.fib,'#8b74e9','#d1a539','#e19635','#c7773c','#d5dfef'];
      levels.forEach((lv,i) => {
        const y=top+(bottom-top)*lv;
        drawLine({x:left,y},{x:right+220,y},colors[i%colors.length],[5,4]);
        ctx.save();ctx.font='11px Inter,system-ui';ctx.fillStyle=colors[i%colors.length];
        ctx.fillText(String(lv),right+226,y+4);ctx.restore();
      });
      drawLine(a,b,'#9caac0',[6,5]);
    }
    function drawLabel(p,text) {
      ctx.save();ctx.font='12px Inter,system-ui';ctx.fillStyle='#edf4ff';
      ctx.fillText(text,p.x+5,p.y-6);ctx.restore();
    }

    function updatePositionPanel() {
      const empty = parentElement.querySelector('#empty-position');
      const details = parentElement.querySelector('#position-details');
      if (!position) {
        empty.hidden=false;details.hidden=true;return;
      }
      empty.hidden=true;details.hidden=false;
      const dir=parentElement.querySelector('#position-direction');
      dir.textContent=position.direction;
      dir.style.color=position.direction==='LONG' ? '#14d99a' : '#ff526e';
      parentElement.querySelector('#position-entry').textContent=fmt(position.entry,4);
      parentElement.querySelector('#position-stop').textContent=fmt(position.stop,4);
      parentElement.querySelector('#position-target').textContent=fmt(position.target,4);
      const risk=Math.max(Math.abs(position.entry-position.stop),1e-12);
      const reward=Math.abs(position.target-position.entry);
      parentElement.querySelector('#position-rr').textContent='1 : '+(reward/risk).toFixed(2);
    }

    function drawRightPriceTag(y, text, bg, opts = {}) {
      const r = canvasRect();
      const padX = 8;
      const h = opts.height || 22;
      const x = r.width - (opts.offsetRight || 4);
      ctx.save();
      ctx.font = '10px Inter,system-ui';
      const w = Math.max(opts.minWidth || 66, ctx.measureText(text).width + padX * 2);
      ctx.fillStyle = bg;
      ctx.beginPath();
      ctx.roundRect(x - w, y - h / 2, w, h, 4);
      ctx.fill();
      ctx.fillStyle = opts.textColor || '#ffffff';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, x - w + padX, y);
      ctx.restore();
      return {x: x - w, w, h};
    }

    function drawPosition() {
      if (!position) return;
      const r = canvasRect();

      const anchorX = Math.max(160, r.width * 0.62);
      const boxWidth = Math.max(130, Math.min(240, r.width * 0.22));
      const left = anchorX;
      const right = Math.min(r.width - 92, left + boxWidth);

      const ye = yFromPrice(position.entry);
      const ys = yFromPrice(position.stop);
      const yt = yFromPrice(position.target);

      const topRisk = Math.min(ye, ys);
      const riskH = Math.max(1, Math.abs(ye - ys));
      const topReward = Math.min(ye, yt);
      const rewardH = Math.max(1, Math.abs(ye - yt));

      // TradingView-like compact block: red risk area, green reward area
      ctx.save();
      ctx.globalAlpha = .34;
      ctx.fillStyle = position.direction === 'LONG' ? themeColors.target : themeColors.stop;
      ctx.fillRect(left, topReward, right - left, rewardH);
      ctx.fillStyle = position.direction === 'LONG' ? themeColors.stop : themeColors.target;
      ctx.fillRect(left, topRisk, right - left, riskH);
      ctx.globalAlpha = 1;

      ctx.strokeStyle = 'rgba(255,255,255,.08)';
      ctx.lineWidth = 1;
      ctx.strokeRect(left, Math.min(topRisk, topReward), right - left, Math.max(ys, yt) - Math.min(ys, yt));
      ctx.restore();

      // entry line stretches through chart; stop/target only over block
      drawLine({x:0, y:ye}, {x:r.width, y:ye}, themeColors.entry, [3, 3]);
      drawLine({x:left, y:ys}, {x:right, y:ys}, themeColors.stop, []);
      drawLine({x:left, y:yt}, {x:right, y:yt}, themeColors.target, []);

      // Small handles at the right edge of the position block
      [
        {y:ys, c:themeColors.stop},
        {y:ye, c:themeColors.entry},
        {y:yt, c:themeColors.target},
      ].forEach(item => {
        ctx.save();
        ctx.fillStyle = item.c;
        ctx.beginPath();
        ctx.arc(right, item.y, 4.5, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      // Right-side scale labels like TradingView
      drawRightPriceTag(ys, fmt(position.stop, 2), themeColors.stop, {minWidth: 86});
      drawRightPriceTag(ye, fmt(position.entry, 2), '#a7aeb9', {textColor:'#142032', minWidth: 86});
      drawRightPriceTag(yt, fmt(position.target, 2), themeColors.target, {minWidth: 86});

      // Optional tiny current marker text inside block
      const risk = Math.max(Math.abs(position.entry - position.stop), 1e-12);
      const reward = Math.abs(position.target - position.entry);
      const rr = (reward / risk).toFixed(2);
      const centerY = (ye + yt) / 2;
      const rrText = `1:${rr}`;
      ctx.save();
      ctx.font = '10px Inter,system-ui';
      const rrW = Math.max(44, ctx.measureText(rrText).width + 16);
      ctx.fillStyle = 'rgba(8,16,30,.94)';
      ctx.strokeStyle = 'rgba(107,194,233,.65)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.roundRect(left + 10, centerY - 12, rrW, 24, 6);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle = '#eff7ff';
      ctx.textBaseline = 'middle';
      ctx.fillText(rrText, left + 18, centerY);
      ctx.restore();
    }

    function drawAll() {
      const r=canvasRect();
      ctx.clearRect(0,0,r.width,r.height);

      drawings.forEach(d => {
        if (d.type==='trend') drawLine(d.a,d.b);
        if (d.type==='horizontal') drawLine({x:0,y:d.a.y},{x:r.width,y:d.a.y},'#d3a63a',[6,5]);
        if (d.type==='rectangle') drawZone(d.a,d.b);
        if (d.type==='fib') drawFib(d.a,d.b,d.levels);
        if (d.type==='measure') {
          drawLine(d.a,d.b,'#bdc9dc',[4,4]);
          drawLabel({x:(d.a.x+d.b.x)/2,y:(d.a.y+d.b.y)/2}, Math.round(Math.hypot(d.a.x-d.b.x,d.a.y-d.b.y))+' px');
        }
        if (d.type==='text') drawLabel(d.a,d.text);
      });

      if (drawingStart && drawingDraft) {
        if (activeTool==='trend') drawLine(drawingStart,drawingDraft);
        if (activeTool==='rectangle') drawZone(drawingStart,drawingDraft);
        if (activeTool==='fib') drawFib(drawingStart,drawingDraft,fibLevels());
        if (activeTool==='measure') drawLine(drawingStart,drawingDraft,'#bdc9dc',[4,4]);
      }

      drawPosition();
    }

    function setTool(tool) {
      activeTool=tool;
      drawingStart=null;drawingDraft=null;draggingPositionHandle=null;

      parentElement.querySelectorAll('[data-tool]').forEach(btn => {
        btn.classList.toggle('active',btn.dataset.tool===tool);
      });

      parentElement.querySelector('#fib-panel').classList.toggle('open',tool==='fib');
      parentElement.querySelector('#position-panel').classList.toggle('open',tool==='long'||tool==='short');

      const longTab = parentElement.querySelector('#position-long');
      const shortTab = parentElement.querySelector('#position-short');
      if (longTab && shortTab) {
        longTab.classList.toggle('selected', tool === 'long');
        shortTab.classList.toggle('selected', tool === 'short');
      }

      canvas.style.pointerEvents = tool==='cursor' ? 'none' : 'auto';
      canvas.style.cursor = tool==='cursor' ? 'default' : 'crosshair';
    }

    parentElement.querySelectorAll('[data-tool]').forEach(btn => {
      btn.onclick = () => {
        const tool=btn.dataset.tool;
        if (tool==='clear') {
          drawings=[];position=null;updatePositionPanel();drawAll();return;
        }
        setTool(tool);
      };
    });

    parentElement.querySelectorAll('[data-close-panel]').forEach(btn => {
      btn.onclick = () => setTool('cursor');
    });

    const longBtn=parentElement.querySelector('#position-long');
    const shortBtn=parentElement.querySelector('#position-short');
    longBtn.onclick=()=>{setTool('long');longBtn.classList.add('selected');shortBtn.classList.remove('selected')};
    shortBtn.onclick=()=>{setTool('short');shortBtn.classList.add('selected');longBtn.classList.remove('selected')};

    function positionGeometry() {
      if (!position) return null;
      const r=canvasRect();
      const anchorX=Math.max(160,r.width*0.62);
      const boxWidth=Math.max(130,Math.min(240,r.width*0.22));
      const left=anchorX;
      const right=Math.min(r.width-92,left+boxWidth);
      const ye=yFromPrice(position.entry);
      const ys=yFromPrice(position.stop);
      const yt=yFromPrice(position.target);
      return {
        left,right,ye,ys,yt,
        top:Math.min(ys,yt),
        bottom:Math.max(ys,yt)
      };
    }

    function nearestPositionHandle(y) {
      if (!position) return null;
      const candidates = [
        ['entry',Math.abs(y-yFromPrice(position.entry))],
        ['stop',Math.abs(y-yFromPrice(position.stop))],
        ['target',Math.abs(y-yFromPrice(position.target))]
      ].sort((a,b)=>a[1]-b[1]);
      return candidates[0][1] <= 11 ? candidates[0][0] : null;
    }

    function pointInsidePositionBlock(p) {
      const g=positionGeometry();
      if (!g) return false;
      return p.x >= g.left && p.x <= g.right && p.y >= g.top && p.y <= g.bottom;
    }

    canvas.onpointerdown = e => {
      e.preventDefault();
      const p=pointerPoint(e);

      if ((activeTool==='long'||activeTool==='short') && position) {
        const handle=nearestPositionHandle(p.y);

        // 1) Individual level dragging: Entry / SL / TP.
        if (handle) {
          draggingPositionHandle=handle;
          canvas.setPointerCapture?.(e.pointerId);
          canvas.style.cursor='ns-resize';
          return;
        }

        // 2) Drag whole position block freely.
        if (pointInsidePositionBlock(p)) {
          draggingWholePosition=true;
          dragStartPrice=priceFromY(p.y);
          dragStartPosition={
            entry:position.entry,
            stop:position.stop,
            target:position.target
          };
          canvas.setPointerCapture?.(e.pointerId);
          canvas.style.cursor='grabbing';
          return;
        }
      }

      // 3) Create a new position if click is outside current block.
      if (activeTool==='long'||activeTool==='short') {
        const entry=priceFromY(p.y);
        const rr=Number(parentElement.querySelector('#rr-select').value||2);
        const risk=Math.max(Math.abs(entry)*0.005,1e-8);
        position=activeTool==='long'
          ? {direction:'LONG',entry,stop:entry-risk,target:entry+risk*rr}
          : {direction:'SHORT',entry,stop:entry+risk,target:entry-risk*rr};
        updatePositionPanel();drawAll();return;
      }

      if (activeTool==='horizontal') {
        drawings.push({type:'horizontal',a:p});drawAll();return;
      }
      if (activeTool==='text') {
        const text=window.prompt('Texto para el gráfico:','Nota');
        if (text) drawings.push({type:'text',a:p,text});
        drawAll();return;
      }
      if (['trend','rectangle','fib','measure'].includes(activeTool)) {
        drawingStart=p;drawingDraft=p;
        canvas.setPointerCapture?.(e.pointerId);
      }
    };

    canvas.onpointermove = e => {
      const p=pointerPoint(e);

      if (draggingPositionHandle && position) {
        position[draggingPositionHandle]=priceFromY(p.y);
        updatePositionPanel();drawAll();return;
      }

      if (draggingWholePosition && position && dragStartPosition) {
        const currentPriceAtPointer=priceFromY(p.y);
        const delta=currentPriceAtPointer-dragStartPrice;

        position.entry=dragStartPosition.entry+delta;
        position.stop=dragStartPosition.stop+delta;
        position.target=dragStartPosition.target+delta;

        updatePositionPanel();
        drawAll();
        return;
      }

      // Cursor feedback while hovering an existing position.
      if ((activeTool==='long'||activeTool==='short') && position) {
        const handle=nearestPositionHandle(p.y);
        if (handle) canvas.style.cursor='ns-resize';
        else if (pointInsidePositionBlock(p)) canvas.style.cursor='grab';
        else canvas.style.cursor='crosshair';
      }

      if (!drawingStart) return;
      drawingDraft=p;drawAll();
    };

    canvas.onpointerup = e => {
      if (draggingPositionHandle) {
        draggingPositionHandle=null;
        canvas.style.cursor='crosshair';
        drawAll();
        return;
      }

      if (draggingWholePosition) {
        draggingWholePosition=false;
        dragStartPrice=null;
        dragStartPosition=null;
        canvas.style.cursor='grab';
        drawAll();
        return;
      }

      if (!drawingStart) return;
      const end=pointerPoint(e);
      const d={type:activeTool,a:drawingStart,b:end};
      if (activeTool==='fib') d.levels=fibLevels();
      drawings.push(d);
      drawingStart=null;drawingDraft=null;drawAll();
    };

    canvas.onpointercancel = () => {
      draggingPositionHandle=null;
      draggingWholePosition=false;
      dragStartPrice=null;
      dragStartPosition=null;
      drawingStart=null;
      drawingDraft=null;
      canvas.style.cursor=activeTool==='cursor'?'default':'crosshair';
      drawAll();
    };

    parentElement.querySelector('#execute-position').onclick = () => {
      if (!position) return;
      setTriggerValue('position_execute', {...position, cursor:currentCursor});
    };


    // TradingView-style color personalization
    const colorFields = {
      up:'#color-up',
      down:'#color-down',
      background:'#color-bg',
      grid:'#color-grid',
      entry:'#color-entry',
      stop:'#color-stop',
      target:'#color-target',
      fib:'#color-fib'
    };

    function syncColorInputs() {
      Object.entries(colorFields).forEach(([key, selector]) => {
        const el=parentElement.querySelector(selector);
        if (el) el.value=themeColors[key] || defaultColors[key];
      });

      const pEntry=parentElement.querySelector('#position-color-entry');
      const pStop=parentElement.querySelector('#position-color-stop');
      const pTarget=parentElement.querySelector('#position-color-target');
      if (pEntry) pEntry.value=themeColors.entry;
      if (pStop) pStop.value=themeColors.stop;
      if (pTarget) pTarget.value=themeColors.target;
    }

    function applyTheme() {
      chart.applyOptions({
        layout:{background:{type:'solid',color:themeColors.background},textColor:'#8292ad'},
        grid:{
          vertLines:{color:themeColors.grid},
          horzLines:{color:themeColors.grid}
        }
      });

      series.applyOptions({
        upColor:themeColors.up,
        downColor:themeColors.down,
        borderUpColor:themeColors.up,
        borderDownColor:themeColors.down,
        wickUpColor:themeColors.up,
        wickDownColor:themeColors.down
      });

      drawAll();
    }

    Object.entries(colorFields).forEach(([key, selector]) => {
      const el=parentElement.querySelector(selector);
      if (!el) return;
      el.oninput=() => {
        themeColors[key]=el.value;
        applyTheme();
      };
    });

    [
      ['#position-color-entry','entry'],
      ['#position-color-stop','stop'],
      ['#position-color-target','target']
    ].forEach(([selector,key]) => {
      const el=parentElement.querySelector(selector);
      if (!el) return;
      el.oninput=() => {
        themeColors[key]=el.value;

        // Keep right-side Personalización inputs in sync too.
        const mirrorSelector = key==='entry'
          ? '#color-entry'
          : key==='stop'
            ? '#color-stop'
            : '#color-target';
        const mirror=parentElement.querySelector(mirrorSelector);
        if (mirror) mirror.value=el.value;

        drawAll();
      };
    });

    parentElement.querySelector('#reset-colors').onclick=() => {
      themeColors={...defaultColors};
      syncColorInputs();
      applyTheme();
    };

    syncColorInputs();

    // Workspace personalization is persistent frontend state.
    const workspaceName=parentElement.querySelector('#workspace-name');
    parentElement.querySelector('#save-workspace').onclick = () => {
      setStateValue('workspace', {
        name:workspaceName.value || 'Workspace Trader',
        fib_template:parentElement.querySelector('#fib-template').value,
        risk_template:parentElement.querySelector('#risk-template').value,
        colors:{...themeColors}
      });
    };

    const currentWorkspace=data.workspace || {};
    if (currentWorkspace.name) workspaceName.value=currentWorkspace.name;
    if (currentWorkspace.fib_template) parentElement.querySelector('#fib-template').value=currentWorkspace.fib_template;
    if (currentWorkspace.risk_template) parentElement.querySelector('#risk-template').value=currentWorkspace.risk_template;

    function resizeCanvas() {
      const rect=canvas.getBoundingClientRect();
      const dpr=window.devicePixelRatio||1;
      canvas.width=Math.max(1,Math.floor(rect.width*dpr));
      canvas.height=Math.max(1,Math.floor(rect.height*dpr));
      ctx.setTransform(dpr,0,0,dpr,0,0);
      drawAll();
    }

    function resizeAll() {
      chart.applyOptions({width:chartHost.clientWidth,height:chartHost.clientHeight});
      resizeCanvas();
    }

    const ro=new ResizeObserver(resizeAll);
    ro.observe(chartStage);
    cleanupFns.push(()=>ro.disconnect());

    chart.timeScale().subscribeVisibleTimeRangeChange(drawAll);
    chart.subscribeCrosshairMove(drawAll);

    setTool('cursor');
    applyReplayData(true);
    resizeAll();

    return () => {
      cleanupFns.forEach(fn => {
        try { fn(); } catch (_) {}
      });
      try { chart.remove(); } catch (_) {}
    };
  } catch (err) {
    console.error('AXION Chart Component error', err);
    root.innerHTML = `<div style="padding:24px;color:#ff8b9d;background:#160810;border:1px solid #51202a;border-radius:12px">
      AXION Chart no pudo inicializarse: ${String(err?.message || err)}
    </div>`;
  }
}
"""


_axion_chart_component = st.components.v2.component(
    "axion_prime_chart_workspace_v5",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=True,
)


def render_axion_chart(
    *,
    data: dict,
    key: str = "axion_chart_workspace",
    height: int = 820,
):
    """Monta AXION REPLAY V5: Position Tool libre y colores personalizables."""
    workspace = data.get("workspace") or {
        "name": "Workspace Trader",
        "fib_template": "AXION PRIME",
        "risk_template": "1.0%",
    }

    return _axion_chart_component(
        data={**data, "workspace": workspace},
        default={"workspace": workspace},
        key=key,
        width="stretch",
        height=height,
        on_workspace_change=lambda: None,
        on_timeframe_change=lambda: None,
        on_symbol_change=lambda: None,
        on_date_change=lambda: None,
        on_position_execute_change=lambda: None,
    )
