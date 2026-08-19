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
      <button class="draw-btn" type="button" data-tool="ray" title="Rayo">
        <svg viewBox="0 0 24 24"><path d="M5 18L18 7"/><path d="M14 7h4v4"/><circle cx="5" cy="18" r="2"/></svg><span>Rayo</span>
      </button>
      <button class="draw-btn" type="button" data-tool="horizontal" title="Línea horizontal">
        <svg viewBox="0 0 24 24"><path d="M4 12h16"/></svg><span>Horizontal</span>
      </button>
      <button class="draw-btn" type="button" data-tool="vertical" title="Línea vertical">
        <svg viewBox="0 0 24 24"><path d="M12 4v16"/></svg><span>Vertical</span>
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

        <div class="drawing-style-panel" id="drawing-style-panel">
          <div class="drawing-style-title">
            <span>ESTILO DE DIBUJO</span>
            <span id="drawing-style-tool">TENDENCIA</span>
          </div>
          <div class="drawing-style-controls">
            <label title="Color">
              <span>Color</span>
              <input type="color" id="drawing-color" value="#47d8eb">
            </label>
            <label title="Estilo de línea">
              <span>Línea</span>
              <select id="drawing-line-style">
                <option value="solid">Sólida</option>
                <option value="dashed">Guiones</option>
                <option value="dotted">Puntos</option>
              </select>
            </label>
            <label title="Grosor">
              <span>Grosor</span>
              <select id="drawing-line-width">
                <option value="1">1 px</option>
                <option value="2" selected>2 px</option>
                <option value="3">3 px</option>
                <option value="4">4 px</option>
              </select>
            </label>
            <label class="opacity-control" title="Opacidad">
              <span>Opacidad</span>
              <input type="range" id="drawing-opacity" min="20" max="100" value="90">
            </label>
            <label class="mini-check" title="Extender a la izquierda">
              <input type="checkbox" id="drawing-extend-left">
              <span>← Ext.</span>
            </label>
            <label class="mini-check" title="Extender a la derecha">
              <input type="checkbox" id="drawing-extend-right">
              <span>Ext. →</span>
            </label>
          </div>
        </div>

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
            Haz clic una vez para crear la posición. Después queda fija.
            Arrastra Entry, SL o TP directamente; arrastra el centro para mover todo el bloque.
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
        <div id="workspace-save-status" class="workspace-save-status">Los cambios se aplican al instante.</div>
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
  grid-template-columns:minmax(170px,220px) minmax(0,1fr) auto;
  align-items:center;
  gap:10px;
  padding:0 10px 0 14px;
  background:linear-gradient(180deg,#06101f,#040a14);
  border-bottom:1px solid rgba(80,118,186,.22);
  overflow:hidden;
}
.brand{font-size:20px;font-weight:850;letter-spacing:.7px;color:#f4f7fd}
.brand span{color:#45d9ee}
.brand-sub{font-size:10px;color:#6e7f9d;margin-top:2px}
.market-block{display:flex;align-items:center;gap:10px;min-width:0;overflow:hidden}
.symbol-button{
  border:1px solid rgba(70,118,197,.28);
  background:#071225;color:#f6f8fc;border-radius:9px;padding:8px 11px;
  font-weight:750;cursor:pointer;white-space:nowrap
}
.status-dot{display:inline-block;width:7px;height:7px;background:#00eba0;border-radius:50%;margin-right:7px}
.tf-strip{
  display:flex;gap:2px;align-items:center;min-width:0;overflow-x:auto;overflow-y:hidden;
  scrollbar-width:none
}
.tf-strip::-webkit-scrollbar{display:none}
.tf-strip button{
  min-width:38px;border:1px solid transparent;background:transparent;color:#7f91b0;
  padding:7px 8px;border-radius:7px;cursor:pointer;font-size:12px
}
.tf-strip button:hover{background:#0a1730;color:#dce8ff}
.tf-strip button.active{background:#0b2341;border-color:#195b82;color:#55d9ed}
.top-actions{
  display:flex;align-items:center;justify-content:flex-end;gap:6px;
  flex:0 0 auto;min-width:max-content;position:relative;z-index:8
}
.icon-button,.fullscreen-button{
  width:37px;height:37px;border-radius:9px;border:1px solid rgba(80,118,186,.28);
  background:#071224;color:#becce4;cursor:pointer;font-size:16px
}
.fullscreen-button{
  border-color:rgba(119,84,255,.72);
  color:#f1edff;
  background:linear-gradient(180deg,#171238,#0c1025);
  box-shadow:0 0 0 1px rgba(124,92,255,.08) inset;
  flex:0 0 37px;
}
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
#drawing-layer{position:absolute;inset:0 0 54px 0;width:100%;height:calc(100% - 54px);pointer-events:none;z-index:4}
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
.workspace-save-status{font-size:7px;color:#617390;text-align:center;margin-top:7px;min-height:11px}
.settings-panel.settings-focus{box-shadow:0 0 0 1px rgba(77,220,239,.45),0 0 28px rgba(77,220,239,.12)}
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
.drawing-style-panel{
  position:absolute;
  top:9px;
  left:10px;
  z-index:12;
  display:none;
  min-width:520px;
  max-width:calc(100% - 20px);
  padding:8px 10px;
  border:1px solid rgba(73,119,186,.28);
  border-radius:9px;
  background:rgba(4,11,23,.96);
  box-shadow:0 12px 34px rgba(0,0,0,.34);
  backdrop-filter:blur(10px);
}
.drawing-style-panel.open{display:block}
.drawing-style-title{
  display:flex;align-items:center;justify-content:space-between;
  gap:14px;margin-bottom:7px;font-size:7px;font-weight:800;
  letter-spacing:.8px;color:#687c9d
}
#drawing-style-tool{color:#54d8ea}
.drawing-style-controls{display:flex;align-items:end;gap:7px;flex-wrap:wrap}
.drawing-style-controls label{
  display:flex;flex-direction:column;gap:3px;font-size:7px;color:#7789a7
}
.drawing-style-controls input[type=color]{
  width:38px;height:27px;border:1px solid #314660;border-radius:5px;
  padding:2px;background:#06101d;cursor:pointer
}
.drawing-style-controls select{
  height:28px;border:1px solid #263a55;border-radius:5px;
  background:#06101d;color:#dbe7fa;padding:0 7px;font-size:8px
}
.drawing-style-controls input[type=range]{width:82px}
.drawing-style-controls .mini-check{
  flex-direction:row;align-items:center;height:28px;padding:0 6px;
  border:1px solid #263a55;border-radius:5px;background:#06101d
}
.drawing-style-controls .mini-check input{accent-color:#42d5e8}
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
@media(max-width:1350px){
  .axion-topbar{grid-template-columns:minmax(155px,190px) minmax(0,1fr) auto;gap:7px}
  .brand{font-size:17px}
  .brand-sub{font-size:8px}
  .market-block{gap:6px}
  .mini-switch em{display:none}
  .mini-switch{gap:2px}
  .mini-switch:nth-of-type(1),
  .mini-switch:nth-of-type(2){display:none}
  .tf-strip button{min-width:33px;padding:6px 5px}
}
@media(max-width:1050px){
  .axion-topbar{grid-template-columns:145px minmax(0,1fr) auto;padding-left:9px}
  .brand-sub{display:none}
  .symbol-button{padding:7px 8px}
  .mini-switch{display:none}
  .terminal-body{grid-template-columns:58px minmax(0,1fr) 220px}
}
@media(max-width:850px){
  .axion-topbar{grid-template-columns:130px minmax(0,1fr) auto}
  .brand{font-size:15px}
  .info-sidebar{display:none}
  .terminal-body{grid-template-columns:54px minmax(0,1fr)}
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

  // Streamlit V2 can reuse the same DOM node between reruns. If the previous
  // Lightweight Charts instance survives, its canvas remains under the new UI
  // and makes XAU/Forex look like BTC. Explicitly destroy it before rebuilding.
  if (typeof parentElement.__axionCleanup === 'function') {
    try { parentElement.__axionCleanup(); } catch (_) {}
    parentElement.__axionCleanup = null;
  }

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
    let drawingStyle = {
      color:'#47d8eb',
      lineStyle:'solid',
      lineWidth:2,
      opacity:.90,
      extendLeft:false,
      extendRight:false
    };
    let position = null;
    let draggingPositionHandle = null;
    let draggingWholePosition = false;
    let dragStartPrice = null;
    let dragStartPosition = null;
    let dragStartPoint = null;
    let dragStartLogical = null;

    const chartHost = parentElement.querySelector('#chart-host');
    const canvas = parentElement.querySelector('#drawing-layer');
    const ctx = canvas.getContext('2d');
    const chartStage = parentElement.querySelector('#chart-stage');

    // Defensive reset: there must be exactly one chart canvas per rerun.
    chartHost.replaceChildren();

    const chart = LWC.createChart(chartHost, {
      width: chartHost.clientWidth,
      height: chartHost.clientHeight,
      layout: {background: {type:'solid', color:themeColors.background}, textColor:'#8292ad'},
      grid: {
        vertLines: {color:themeColors.grid},
        horzLines: {color:themeColors.grid}
      },
      rightPriceScale: {
        borderColor:'rgba(69,99,154,.24)',
        autoScale:true,
        scaleMargins:{top:.08,bottom:.08}
      },
      timeScale: {
        borderColor:'rgba(69,99,154,.24)',
        timeVisible:true,
        secondsVisible:false,
        rightOffset:5
      },
      crosshair: {mode:LWC.CrosshairMode.Normal},
      handleScroll: {
        mouseWheel:true,
        pressedMouseMove:true,
        horzTouchDrag:true,
        vertTouchDrag:true
      },
      handleScale: {
        axisPressedMouseMove:true,
        mouseWheel:true,
        pinch:true
      }
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
      priceLineVisible:false,
      lastValueVisible:false
    });

    // Volume must live on its own overlay price scale. If these margins are
    // placed on the series instead of the scale, Lightweight Charts can let
    // volume distort the instrument's right price scale.
    chart.priceScale('').applyOptions({
      scaleMargins:{top:.78,bottom:0},
      borderVisible:false
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

      // Force the instrument price scale to recalculate only from candle data.
      try {
        chart.priceScale('right').applyOptions({
          autoScale:true,
          scaleMargins:{top:.08,bottom:.08}
        });
      } catch (_) {}

      if (fit) {
        try { chart.timeScale().fitContent(); } catch (_) {}
      }

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
        const activeFullscreen = document.fullscreenElement || document.webkitFullscreenElement;

        if (!activeFullscreen) {
          if (root.requestFullscreen) {
            await root.requestFullscreen();
          } else if (root.webkitRequestFullscreen) {
            root.webkitRequestFullscreen();
          } else {
            throw new Error('Fullscreen API no disponible en este navegador.');
          }
        } else {
          if (document.exitFullscreen) {
            await document.exitFullscreen();
          } else if (document.webkitExitFullscreen) {
            document.webkitExitFullscreen();
          }
        }
      } catch (err) {
        console.error('AXION Fullscreen error', err);
        fullscreenBtn.title = 'El navegador bloqueó pantalla completa';
      }
    };

    const onFullscreen = () => {
      const activeFullscreen = document.fullscreenElement || document.webkitFullscreenElement;
      fullscreenBtn.textContent = activeFullscreen ? '⤢' : '⛶';
      fullscreenBtn.title = activeFullscreen ? 'Salir de pantalla completa' : 'Pantalla completa';
      setTimeout(() => resizeAll(), 80);
    };
    document.addEventListener('fullscreenchange', onFullscreen);
    cleanupFns.push(() => document.removeEventListener('fullscreenchange', onFullscreen));

    // Volume toggle is a real chart control.
    const volumeToggle = parentElement.querySelector('#volume-toggle');
    volumeToggle.checked = true;
    volumeToggle.onchange = () => {
      volumeSeries.applyOptions({visible:volumeToggle.checked});
    };

    // Settings button brings the user directly to Personalización.
    const settingsPanel = parentElement.querySelector('#workspace-settings');
    parentElement.querySelector('#settings-btn').onclick = () => {
      settingsPanel.classList.add('settings-focus');
      settingsPanel.scrollIntoView({behavior:'smooth',block:'nearest'});
      setTimeout(()=>settingsPanel.classList.remove('settings-focus'),900);
    };

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
    function hexToRgba(hex,opacity=1) {
      const clean=String(hex||'#47d8eb').replace('#','');
      const value=parseInt(clean.length===3
        ? clean.split('').map(x=>x+x).join('')
        : clean,16);
      const r=(value>>16)&255;
      const g=(value>>8)&255;
      const b=value&255;
      return `rgba(${r},${g},${b},${Math.max(0,Math.min(1,opacity))})`;
    }

    function dashForStyle(style,width=1) {
      if (style==='dotted') return [Math.max(1,width),Math.max(3,width*2.4)];
      if (style==='dashed') return [Math.max(5,width*3.5),Math.max(4,width*2.5)];
      return [];
    }

    function currentDrawingStyle(overrides={}) {
      return {
        color:drawingStyle.color,
        lineStyle:drawingStyle.lineStyle,
        lineWidth:drawingStyle.lineWidth,
        opacity:drawingStyle.opacity,
        extendLeft:drawingStyle.extendLeft,
        extendRight:drawingStyle.extendRight,
        ...overrides
      };
    }

    function pointToAnchor(p) {
      let logical=chart.timeScale().coordinateToLogical(p.x);
      if (logical == null) logical=currentCursor;
      return {
        logical:Number(logical),
        price:priceFromY(p.y)
      };
    }

    function anchorToPoint(a) {
      if (!a) return null;
      const x=chart.timeScale().logicalToCoordinate(Number(a.logical));
      const y=yFromPrice(Number(a.price));
      if (x == null || y == null) return null;
      return {x:Number(x),y:Number(y)};
    }

    function drawLine(a,b,style=currentDrawingStyle()) {
      if (!a || !b) return;
      let p1={...a},p2={...b};

      // Extend trend lines/rays to chart edges while preserving slope.
      if ((style.extendLeft || style.extendRight) && Math.abs(p2.x-p1.x) > .001) {
        const r=canvasRect();
        const dx=p2.x-p1.x;
        const dy=p2.y-p1.y;
        const slope=dy/dx;

        if (style.extendLeft) {
          const x=0;
          p1={x,y:p1.y+slope*(x-p1.x)};
        }
        if (style.extendRight) {
          const x=r.width;
          p2={x,y:p2.y+slope*(x-p2.x)};
        }
      }

      ctx.save();
      ctx.globalAlpha=Number(style.opacity ?? 1);
      ctx.strokeStyle=style.color || '#47d8eb';
      ctx.lineWidth=Number(style.lineWidth || 1);
      ctx.lineCap=style.lineStyle==='dotted' ? 'round' : 'butt';
      ctx.setLineDash(dashForStyle(style.lineStyle,style.lineWidth));
      ctx.beginPath();
      ctx.moveTo(p1.x,p1.y);
      ctx.lineTo(p2.x,p2.y);
      ctx.stroke();
      ctx.restore();
    }

    function drawZone(a,b,style=currentDrawingStyle()) {
      if (!a || !b) return;
      const x=Math.min(a.x,b.x),y=Math.min(a.y,b.y);
      const w=Math.abs(a.x-b.x),h=Math.abs(a.y-b.y);
      ctx.save();
      ctx.fillStyle=hexToRgba(style.color,Math.min(.24,(style.opacity ?? .9)*.18));
      ctx.strokeStyle=hexToRgba(style.color,style.opacity ?? .9);
      ctx.lineWidth=Number(style.lineWidth || 1);
      ctx.setLineDash(dashForStyle(style.lineStyle,style.lineWidth));
      ctx.fillRect(x,y,w,h);
      ctx.strokeRect(x,y,w,h);
      ctx.restore();
    }

    function fibLevels() {
      return [...parentElement.querySelectorAll('[data-fib-level]')]
        .filter(x => x.checked)
        .map(x => Number(x.dataset.fibLevel));
    }

    function drawFib(a,b,levels,style=currentDrawingStyle({color:themeColors.fib})) {
      if (!a || !b) return;
      const left=Math.min(a.x,b.x),right=Math.max(a.x,b.x);
      const top=Math.min(a.y,b.y),bottom=Math.max(a.y,b.y);
      const r=canvasRect();

      levels.forEach((lv) => {
        const y=top+(bottom-top)*lv;
        let x1=style.extendLeft ? 0 : left;
        let x2=style.extendRight ? r.width : right;
        drawLine({x:x1,y},{x:x2,y},style);
        ctx.save();
        ctx.globalAlpha=style.opacity ?? 1;
        ctx.font='10px Inter,system-ui';
        ctx.fillStyle=style.color;
        ctx.fillText(String(lv),Math.min(r.width-34,x2+5),y-4);
        ctx.restore();
      });

      drawLine(a,b,currentDrawingStyle({
        color:'#9caac0',
        lineStyle:'dashed',
        lineWidth:1,
        opacity:.8
      }));
    }

    function drawLabel(p,text,style=currentDrawingStyle({color:'#edf4ff'})) {
      if (!p) return;
      ctx.save();
      ctx.globalAlpha=style.opacity ?? 1;
      ctx.font='12px Inter,system-ui';
      ctx.fillStyle=style.color || '#edf4ff';
      ctx.fillText(text,p.x+5,p.y-6);
      ctx.restore();
    }

    function renderAnchoredDrawing(d) {
      const r=canvasRect();
      const style=d.style || currentDrawingStyle();

      if (d.type==='horizontal') {
        const y=yFromPrice(d.price);
        drawLine({x:0,y},{x:r.width,y},style);
        return;
      }

      if (d.type==='vertical') {
        const x=chart.timeScale().logicalToCoordinate(Number(d.logical));
        if (x == null) return;
        drawLine({x,y:0},{x,y:r.height},style);
        return;
      }

      if (d.type==='text') {
        drawLabel(anchorToPoint(d.a),d.text,style);
        return;
      }

      const a=anchorToPoint(d.a);
      const b=anchorToPoint(d.b);
      if (!a || !b) return;

      if (d.type==='trend' || d.type==='ray') {
        const lineStyle={...style};
        if (d.type==='ray') lineStyle.extendRight=true;
        drawLine(a,b,lineStyle);
      } else if (d.type==='rectangle') {
        drawZone(a,b,style);
      } else if (d.type==='fib') {
        drawFib(a,b,d.levels || [],style);
      } else if (d.type==='measure') {
        drawLine(a,b,style);
        const priceDelta=Math.abs(Number(d.a.price)-Number(d.b.price));
        const pct=Math.abs(priceDelta/Math.max(Math.abs(Number(d.a.price)),1e-12))*100;
        drawLabel(
          {x:(a.x+b.x)/2,y:(a.y+b.y)/2},
          `${fmt(priceDelta,Math.abs(d.a.price)<10?5:2)} · ${pct.toFixed(2)}%`,
          currentDrawingStyle({color:'#c7d2e4',opacity:.95})
        );
      }
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
      const decimals = Math.abs(position.entry) < 10 ? 5 : Math.abs(position.entry) < 100 ? 3 : 2;
      parentElement.querySelector('#position-entry').textContent=fmt(position.entry,decimals);
      parentElement.querySelector('#position-stop').textContent=fmt(position.stop,decimals);
      parentElement.querySelector('#position-target').textContent=fmt(position.target,decimals);

      const risk=Math.max(Math.abs(position.entry-position.stop),1e-12);
      const reward=Math.abs(position.target-position.entry);
      const riskPct=Math.abs(risk/position.entry)*100;
      const rewardPct=Math.abs(reward/position.entry)*100;
      const visualState=evaluateVisualPositionState();
      const current=visualState.current;
      let liveSuffix='';

      if (visualState.status==='PENDING') {
        liveSuffix=' · Pendiente';
      } else if (visualState.status==='ACTIVE' && current) {
        const currentPrice=Number(current.close);
        const pnlPrice=position.direction==='LONG'
          ? currentPrice-position.entry
          : position.entry-currentPrice;
        liveSuffix=' · '+(pnlPrice/risk).toFixed(2)+'R actual';
      } else if (visualState.status==='TP') {
        liveSuffix=' · TP alcanzado';
      } else if (visualState.status==='SL') {
        liveSuffix=' · SL alcanzado';
      } else if (visualState.status==='AMBIGUOUS') {
        liveSuffix=' · Resultado intravela indeterminado';
      }

      parentElement.querySelector('#position-rr').textContent=
        '1 : '+(reward/risk).toFixed(2)+' · Riesgo '+riskPct.toFixed(2)+'% · Beneficio '+rewardPct.toFixed(2)+'%'+liveSuffix;
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

    function currentReplayCandle() {
      const visible=visibleCandles();
      return visible.length ? visible[visible.length-1] : null;
    }

    function evaluateVisualPositionState() {
      if (!position) return {status:'NONE'};

      const startIndex=Math.max(0,Math.min(
        Number.isFinite(position.createdCursor) ? Number(position.createdCursor) : 0,
        currentCursor
      ));

      const revealed=candles.slice(startIndex,currentCursor+1);
      if (!revealed.length) {
        return {status:'PENDING',current:null,entryIndex:null};
      }

      let entryIndex=null;
      for (let i=0;i<revealed.length;i++) {
        const bar=revealed[i];
        if (Number(bar.low) <= position.entry && Number(bar.high) >= position.entry) {
          entryIndex=startIndex+i;
          break;
        }
      }

      const current=currentReplayCandle();
      if (entryIndex == null) {
        return {status:'PENDING',current,entryIndex:null};
      }

      // Only inspect candles that have already appeared after the entry was touched.
      const afterEntry=candles.slice(entryIndex,currentCursor+1);
      for (const bar of afterEntry) {
        const hitStop =
          position.direction==='LONG'
            ? Number(bar.low) <= position.stop
            : Number(bar.high) >= position.stop;

        const hitTarget =
          position.direction==='LONG'
            ? Number(bar.high) >= position.target
            : Number(bar.low) <= position.target;

        if (hitStop && hitTarget) {
          // With OHLC alone the intra-candle order is unknowable.
          return {status:'AMBIGUOUS',current,entryIndex};
        }
        if (hitTarget) return {status:'TP',current,entryIndex};
        if (hitStop) return {status:'SL',current,entryIndex};
      }

      return {status:'ACTIVE',current,entryIndex};
    }

    function drawLiveTradeProgress(g) {
      const state=evaluateVisualPositionState();
      if (!position || !g) return;

      const current=state.current;
      const rightEdge=Math.min(canvasRect().width-8, g.right);
      const leftEdge=g.left;

      ctx.save();

      if (state.status==='PENDING') {
        ctx.fillStyle='rgba(150,164,190,.10)';
        ctx.strokeStyle='rgba(150,164,190,.45)';
        ctx.setLineDash([5,4]);
        ctx.lineWidth=1;
        ctx.strokeRect(leftEdge,g.top,rightEdge-leftEdge,g.bottom-g.top);

        const label='PENDIENTE · esperando Entry';
        ctx.font='700 9px Inter,system-ui';
        const w=ctx.measureText(label).width+18;
        ctx.fillStyle='rgba(8,16,30,.94)';
        ctx.setLineDash([]);
        ctx.beginPath();
        ctx.roundRect(leftEdge+8,g.ye-34,w,22,6);
        ctx.fill();
        ctx.fillStyle='#a9b6cb';
        ctx.textBaseline='middle';
        ctx.fillText(label,leftEdge+17,g.ye-23);
        ctx.restore();
        return;
      }

      if (!current) {
        ctx.restore();
        return;
      }

      const currentPrice=Number(current.close);
      const currentY=yFromPrice(currentPrice);
      const favorable =
        position.direction==='LONG'
          ? currentPrice >= position.entry
          : currentPrice <= position.entry;

      const liveColor=favorable ? themeColors.target : themeColors.stop;

      if (state.status==='ACTIVE') {
        const bandTop=Math.min(g.ye,currentY);
        const bandHeight=Math.max(2,Math.abs(g.ye-currentY));

        ctx.globalAlpha=.18;
        ctx.fillStyle=liveColor;
        ctx.fillRect(leftEdge,bandTop,rightEdge-leftEdge,bandHeight);
        ctx.globalAlpha=1;

        ctx.strokeStyle=liveColor;
        ctx.lineWidth=1.4;
        ctx.setLineDash([4,3]);
        ctx.beginPath();
        ctx.moveTo(leftEdge,currentY);
        ctx.lineTo(rightEdge,currentY);
        ctx.stroke();
        ctx.setLineDash([]);

        const risk=Math.max(Math.abs(position.entry-position.stop),1e-12);
        const pnlPrice=
          position.direction==='LONG'
            ? currentPrice-position.entry
            : position.entry-currentPrice;
        const currentR=pnlPrice/risk;
        const pnlPct=(pnlPrice/Math.abs(position.entry))*100;

        const label=
          'EN MERCADO  '+(pnlPct>=0?'+':'')+pnlPct.toFixed(2)+'%  ·  '+
          (currentR>=0?'+':'')+currentR.toFixed(2)+'R';

        ctx.font='800 9px Inter,system-ui';
        const w=Math.max(128,ctx.measureText(label).width+18);
        const x=Math.max(leftEdge+8,Math.min(rightEdge-w-8,leftEdge+12));
        const y=Math.max(18,Math.min(canvasRect().height-18,currentY-18));

        ctx.fillStyle='rgba(4,12,26,.96)';
        ctx.strokeStyle=liveColor;
        ctx.lineWidth=1;
        ctx.beginPath();
        ctx.roundRect(x,y-12,w,24,6);
        ctx.fill();
        ctx.stroke();

        ctx.fillStyle=liveColor;
        ctx.textBaseline='middle';
        ctx.fillText(label,x+9,y);
      } else {
        const isTp=state.status==='TP';
        const isSl=state.status==='SL';
        const statusColor=isTp ? themeColors.target : isSl ? themeColors.stop : '#f0b85a';
        const label=isTp
          ? '✓ TAKE PROFIT'
          : isSl
            ? '✕ STOP LOSS'
            : '⚠ RESULTADO INDETERMINADO EN LA MISMA VELA';

        ctx.font='800 9px Inter,system-ui';
        const w=Math.max(110,ctx.measureText(label).width+20);
        ctx.fillStyle='rgba(4,12,26,.97)';
        ctx.strokeStyle=statusColor;
        ctx.lineWidth=1.2;
        ctx.beginPath();
        ctx.roundRect(leftEdge+8,g.ye-14,w,28,7);
        ctx.fill();
        ctx.stroke();
        ctx.fillStyle=statusColor;
        ctx.textBaseline='middle';
        ctx.fillText(label,leftEdge+18,g.ye);
      }

      ctx.restore();
    }

    function drawPosition() {
      if (!position) return;
      const r = canvasRect();
      const g = positionGeometry();
      if (!g) return;

      const left = g.left;
      const right = g.right;
      const ye = g.ye;
      const ys = g.ys;
      const yt = g.yt;

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

      // Right-side labels with semantic names + exact levels.
      const labelDecimals =
        Math.abs(position.entry) < 10 ? 5 :
        Math.abs(position.entry) < 100 ? 3 : 2;

      drawRightPriceTag(ys,'SL  '+fmt(position.stop,labelDecimals),themeColors.stop,{minWidth:108});
      drawRightPriceTag(ye,'ENTRY  '+fmt(position.entry,labelDecimals),'#a7aeb9',{textColor:'#142032',minWidth:118});
      drawRightPriceTag(yt,'TP  '+fmt(position.target,labelDecimals),themeColors.target,{minWidth:108});

      // Professional risk / reward information inside the Position Tool.
      const risk = Math.max(Math.abs(position.entry - position.stop), 1e-12);
      const reward = Math.abs(position.target - position.entry);
      const rr = reward / risk;
      const riskPct = Math.abs(risk / position.entry) * 100;
      const rewardPct = Math.abs(reward / position.entry) * 100;

      const priceDecimals =
        Math.abs(position.entry) < 10 ? 5 :
        Math.abs(position.entry) < 100 ? 3 : 2;

      const rewardMidY=(ye+yt)/2;
      const riskMidY=(ye+ys)/2;
      const infoX=left+10;
      const infoW=Math.max(120,Math.min(178,right-left-20));

      function metricBadge(y,title,value,color) {
        ctx.save();
        const h=40;
        ctx.fillStyle='rgba(4,11,23,.90)';
        ctx.strokeStyle=color;
        ctx.lineWidth=1;
        ctx.beginPath();
        ctx.roundRect(infoX,y-h/2,infoW,h,7);
        ctx.fill();
        ctx.stroke();
        ctx.textBaseline='middle';
        ctx.fillStyle=color;
        ctx.font='800 9px Inter,system-ui';
        ctx.fillText(title,infoX+9,y-7);
        ctx.fillStyle='#f3f7ff';
        ctx.font='600 10px Inter,system-ui';
        ctx.fillText(value,infoX+9,y+8);
        ctx.restore();
      }

      metricBadge(
        rewardMidY,
        'BENEFICIO',
        fmt(reward,priceDecimals)+' · +'+rewardPct.toFixed(2)+'%',
        themeColors.target
      );

      metricBadge(
        riskMidY,
        'RIESGO',
        fmt(risk,priceDecimals)+' · -'+riskPct.toFixed(2)+'%',
        themeColors.stop
      );

      const rrText='R:R  1 : '+rr.toFixed(2);
      ctx.save();
      ctx.font='800 10px Inter,system-ui';
      const rrW=Math.max(92,ctx.measureText(rrText).width+24);
      const rrH=28;
      const rrX=Math.max(left+8,Math.min(right-rrW-8,left+(right-left-rrW)/2));
      ctx.fillStyle='rgba(4,12,26,.98)';
      ctx.strokeStyle=themeColors.entry;
      ctx.lineWidth=1.2;
      ctx.beginPath();
      ctx.roundRect(rrX,ye-rrH/2,rrW,rrH,7);
      ctx.fill();
      ctx.stroke();
      ctx.fillStyle='#f5f8ff';
      ctx.textBaseline='middle';
      ctx.fillText(rrText,rrX+12,ye);
      ctx.restore();

      // Replay-aware visual state: pending, active P&L band, TP or SL.
      drawLiveTradeProgress(g);
    }

    function drawAll() {
      const r=canvasRect();
      ctx.clearRect(0,0,r.width,r.height);

      drawings.forEach(renderAnchoredDrawing);

      // While drawing, preview remains in screen coordinates. Once released,
      // it is converted to logical-time + price and becomes chart-anchored.
      if (drawingStart && drawingDraft) {
        const previewStyle=currentDrawingStyle();
        if (activeTool==='trend'||activeTool==='ray') {
          const s={...previewStyle};
          if (activeTool==='ray') s.extendRight=true;
          drawLine(drawingStart,drawingDraft,s);
        }
        if (activeTool==='rectangle') drawZone(drawingStart,drawingDraft,previewStyle);
        if (activeTool==='fib') drawFib(drawingStart,drawingDraft,fibLevels(),previewStyle);
        if (activeTool==='measure') drawLine(
          drawingStart,drawingDraft,
          currentDrawingStyle({color:'#bdc9dc',lineStyle:'dashed'})
        );
      }

      drawPosition();
    }

    function setTool(tool) {
      activeTool=tool;
      drawingStart=null;
      drawingDraft=null;
      draggingPositionHandle=null;
      draggingWholePosition=false;

      const drawingColorInput=parentElement.querySelector('#drawing-color');
    const drawingLineStyle=parentElement.querySelector('#drawing-line-style');
    const drawingLineWidth=parentElement.querySelector('#drawing-line-width');
    const drawingOpacity=parentElement.querySelector('#drawing-opacity');
    const drawingExtendLeft=parentElement.querySelector('#drawing-extend-left');
    const drawingExtendRight=parentElement.querySelector('#drawing-extend-right');

    function syncDrawingStyleFromControls() {
      drawingStyle={
        color:drawingColorInput.value,
        lineStyle:drawingLineStyle.value,
        lineWidth:Number(drawingLineWidth.value||2),
        opacity:Number(drawingOpacity.value||90)/100,
        extendLeft:Boolean(drawingExtendLeft.checked),
        extendRight:Boolean(drawingExtendRight.checked)
      };
      drawAll();
    }

    [
      drawingColorInput,drawingLineStyle,drawingLineWidth,drawingOpacity,
      drawingExtendLeft,drawingExtendRight
    ].forEach(el => {
      el.oninput=syncDrawingStyleFromControls;
      el.onchange=syncDrawingStyleFromControls;
    });

    parentElement.querySelectorAll('[data-tool]').forEach(btn => {
        btn.classList.toggle('active',btn.dataset.tool===tool);
      });

      parentElement.querySelector('#fib-panel').classList.toggle('open',tool==='fib');
      parentElement.querySelector('#position-panel').classList.toggle('open',tool==='long'||tool==='short');

      const drawingTools=new Set([
        'trend','ray','horizontal','vertical','rectangle','fib','text','measure'
      ]);
      const stylePanel=parentElement.querySelector('#drawing-style-panel');
      stylePanel.classList.toggle('open',drawingTools.has(tool));
      parentElement.querySelector('#drawing-style-tool').textContent=
        tool==='trend'?'TENDENCIA':
        tool==='ray'?'RAYO':
        tool==='horizontal'?'HORIZONTAL':
        tool==='vertical'?'VERTICAL':
        tool==='rectangle'?'ZONA':
        tool==='fib'?'FIBONACCI':
        tool==='text'?'TEXTO':
        tool==='measure'?'MEDICIÓN':'DIBUJO';

      const longTab = parentElement.querySelector('#position-long');
      const shortTab = parentElement.querySelector('#position-short');
      if (longTab && shortTab) {
        longTab.classList.toggle('selected', tool === 'long');
        shortTab.classList.toggle('selected', tool === 'short');
      }

      // The drawing canvas is visual only. Pointer interaction is handled on
      // chartStage in capture mode, so Lightweight Charts keeps native pan/zoom.
      canvas.style.pointerEvents='none';

      if (tool === 'position_edit' || tool === 'cursor') {
        chartStage.style.cursor='default';
      } else {
        chartStage.style.cursor='crosshair';
      }
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

      let left = chart.timeScale().logicalToCoordinate(Number(position.startLogical));
      let right = chart.timeScale().logicalToCoordinate(Number(position.endLogical));

      // Fallback for a position created before V10 or a transient chart state.
      if (left == null || right == null) {
        const fallbackWidth=Math.max(130,Math.min(240,r.width*0.22));
        left=Number.isFinite(position.leftPx) ? Number(position.leftPx) : Math.max(120,r.width*.62);
        right=left+(Number(position.widthPx)||fallbackWidth);
      }

      if (right < left) [left,right]=[right,left];

      const ye=yFromPrice(position.entry);
      const ys=yFromPrice(position.stop);
      const yt=yFromPrice(position.target);

      return {
        left,right,width:right-left,ye,ys,yt,
        top:Math.min(ys,yt),
        bottom:Math.max(ys,yt)
      };
    }

    function nearestPositionHandle(p) {
      if (!position) return null;
      const g=positionGeometry();
      if (!g) return null;

      // Grab Entry / SL / TP anywhere along the visible position width.
      // This is intentionally generous so the tool feels natural, like TradingView.
      const insideHorizontalRange = p.x >= g.left - 10 && p.x <= g.right + 20;
      if (!insideHorizontalRange) return null;

      const candidates = [
        ['entry',Math.abs(p.y-g.ye)],
        ['stop',Math.abs(p.y-g.ys)],
        ['target',Math.abs(p.y-g.yt)]
      ].sort((a,b)=>a[1]-b[1]);

      return candidates[0][1] <= 9 ? candidates[0][0] : null;
    }

    function pointInsidePositionBlock(p) {
      const g=positionGeometry();
      if (!g) return false;
      return p.x >= g.left && p.x <= g.right && p.y >= g.top && p.y <= g.bottom;
    }

    function interceptPointer(e) {
      e.preventDefault();
      e.stopPropagation();
    }

    function onStagePointerDown(e) {
      const p=pointerPoint(e);

      // Existing position: only intercept if the trader actually touches
      // Entry/SL/TP or the position block. Everywhere else the chart receives
      // the event normally for pan/zoom/crosshair.
      if ((activeTool==='long'||activeTool==='short'||activeTool==='position_edit') && position) {
        const handle=nearestPositionHandle(p);

        if (handle) {
          interceptPointer(e);
          draggingPositionHandle=handle;
          chartStage.setPointerCapture?.(e.pointerId);
          chartStage.style.cursor='ns-resize';
          return;
        }

        if (pointInsidePositionBlock(p)) {
          interceptPointer(e);
          draggingWholePosition=true;
          dragStartPrice=priceFromY(p.y);
          dragStartPoint={x:p.x,y:p.y};
          dragStartLogical=chart.timeScale().coordinateToLogical(p.x);
          dragStartPosition={
            entry:position.entry,
            stop:position.stop,
            target:position.target,
            startLogical:Number(position.startLogical),
            endLogical:Number(position.endLogical)
          };
          chartStage.setPointerCapture?.(e.pointerId);
          chartStage.style.cursor='grabbing';
          return;
        }
      }

      // Once a position is created, clicking elsewhere must behave like a
      // normal chart click/drag. Do not preventDefault here.
      if (activeTool==='position_edit') {
        return;
      }

      // LONG/SHORT creation: exactly one click is intercepted, then AXION
      // switches immediately to position_edit.
      if (activeTool==='long'||activeTool==='short') {
        interceptPointer(e);

        const entry=priceFromY(p.y);
        const rr=Number(parentElement.querySelector('#rr-select').value||2);

        const riskText=String(parentElement.querySelector('#risk-template').value || '1.0%');
        const riskPct=Math.max(0.0001, Number.parseFloat(riskText) / 100);
        const risk=Math.max(Math.abs(entry)*riskPct,1e-8);

        let startLogical=chart.timeScale().coordinateToLogical(p.x);
        if (startLogical == null) startLogical=Math.max(0,currentCursor-10);

        const desiredEndX=Math.min(canvasRect().width-95,p.x+Math.max(150,canvasRect().width*.20));
        let endLogical=chart.timeScale().coordinateToLogical(desiredEndX);
        if (endLogical == null || endLogical <= startLogical) endLogical=startLogical+20;

        position=activeTool==='long'
          ? {
              direction:'LONG',entry,stop:entry-risk,target:entry+risk*rr,
              startLogical,endLogical,createdCursor:currentCursor
            }
          : {
              direction:'SHORT',entry,stop:entry+risk,target:entry-risk*rr,
              startLogical,endLogical,createdCursor:currentCursor
            };

        updatePositionPanel();
        setTool('position_edit');
        drawAll();
        return;
      }

      // Drawing tools intentionally intercept chart navigation while drawing.
      if (activeTool==='horizontal') {
        interceptPointer(e);
        drawings.push({
          type:'horizontal',
          price:priceFromY(p.y),
          style:currentDrawingStyle()
        });
        drawAll();
        return;
      }

      if (activeTool==='vertical') {
        interceptPointer(e);
        let logical=chart.timeScale().coordinateToLogical(p.x);
        if (logical == null) logical=currentCursor;
        drawings.push({
          type:'vertical',
          logical:Number(logical),
          style:currentDrawingStyle()
        });
        drawAll();
        return;
      }

      if (activeTool==='text') {
        interceptPointer(e);
        const label=window.prompt('Texto para el gráfico:','Nota');
        if (label) drawings.push({
          type:'text',
          a:pointToAnchor(p),
          text:label,
          style:currentDrawingStyle()
        });
        drawAll();
        return;
      }

      if (['trend','ray','rectangle','fib','measure'].includes(activeTool)) {
        interceptPointer(e);
        drawingStart=p;
        drawingDraft=p;
        chartStage.setPointerCapture?.(e.pointerId);
      }
    }

    function onStagePointerMove(e) {
      const p=pointerPoint(e);

      if (draggingPositionHandle && position) {
        interceptPointer(e);
        position[draggingPositionHandle]=priceFromY(p.y);
        updatePositionPanel();
        drawAll();
        return;
      }

      if (draggingWholePosition && position && dragStartPosition && dragStartPoint) {
        interceptPointer(e);

        const currentPriceAtPointer=priceFromY(p.y);
        const deltaPrice=currentPriceAtPointer-dragStartPrice;
        const currentLogical=chart.timeScale().coordinateToLogical(p.x);
        const deltaLogical=(currentLogical != null && dragStartLogical != null)
          ? currentLogical-dragStartLogical
          : 0;

        position.entry=dragStartPosition.entry+deltaPrice;
        position.stop=dragStartPosition.stop+deltaPrice;
        position.target=dragStartPosition.target+deltaPrice;
        position.startLogical=dragStartPosition.startLogical+deltaLogical;
        position.endLogical=dragStartPosition.endLogical+deltaLogical;

        updatePositionPanel();
        drawAll();
        return;
      }

      if (drawingStart) {
        interceptPointer(e);
        drawingDraft=p;
        drawAll();
        return;
      }

      // Hover feedback only. Do not block Lightweight Charts.
      if ((activeTool==='long'||activeTool==='short'||activeTool==='position_edit') && position) {
        const handle=nearestPositionHandle(p);
        if (handle) chartStage.style.cursor='ns-resize';
        else if (pointInsidePositionBlock(p)) chartStage.style.cursor='grab';
        else chartStage.style.cursor=activeTool==='position_edit' ? 'default' : 'crosshair';
      }
    }

    function onStagePointerUp(e) {
      if (draggingPositionHandle) {
        interceptPointer(e);
        draggingPositionHandle=null;
        try { chartStage.releasePointerCapture?.(e.pointerId); } catch (_) {}
        chartStage.style.cursor=activeTool==='position_edit' ? 'default' : 'crosshair';
        drawAll();
        return;
      }

      if (draggingWholePosition) {
        interceptPointer(e);
        draggingWholePosition=false;
        dragStartPrice=null;
        dragStartPosition=null;
        dragStartPoint=null;
        dragStartLogical=null;
        try { chartStage.releasePointerCapture?.(e.pointerId); } catch (_) {}
        chartStage.style.cursor=activeTool==='position_edit' ? 'default' : 'grab';
        drawAll();
        return;
      }

      if (!drawingStart) return;

      interceptPointer(e);
      const finish=pointerPoint(e);
      const d={
        type:activeTool,
        a:pointToAnchor(drawingStart),
        b:pointToAnchor(finish),
        style:currentDrawingStyle()
      };
      if (activeTool==='ray') d.style={...d.style,extendRight:true};
      if (activeTool==='fib') d.levels=fibLevels();
      drawings.push(d);
      drawingStart=null;
      drawingDraft=null;
      try { chartStage.releasePointerCapture?.(e.pointerId); } catch (_) {}
      drawAll();
    }

    function onStagePointerCancel(e) {
      const wasInteracting = Boolean(
        draggingPositionHandle || draggingWholePosition || drawingStart
      );

      draggingPositionHandle=null;
      draggingWholePosition=false;
      dragStartPrice=null;
      dragStartPosition=null;
      dragStartPoint=null;
      dragStartLogical=null;
      drawingStart=null;
      drawingDraft=null;

      if (wasInteracting) {
        interceptPointer(e);
      }

      chartStage.style.cursor=(activeTool==='cursor'||activeTool==='position_edit')
        ? 'default'
        : 'crosshair';
      drawAll();
    }

    // Capture lets AXION detect its tools first. If no tool is hit, we do
    // nothing and Lightweight Charts handles the same pointer event normally.
    chartStage.addEventListener('pointerdown', onStagePointerDown, true);
    chartStage.addEventListener('pointermove', onStagePointerMove, true);
    chartStage.addEventListener('pointerup', onStagePointerUp, true);
    chartStage.addEventListener('pointercancel', onStagePointerCancel, true);

    cleanupFns.push(() => {
      chartStage.removeEventListener('pointerdown', onStagePointerDown, true);
      chartStage.removeEventListener('pointermove', onStagePointerMove, true);
      chartStage.removeEventListener('pointerup', onStagePointerUp, true);
      chartStage.removeEventListener('pointercancel', onStagePointerCancel, true);
    });

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

    function applyFibTemplate(name) {
      const selected = name === 'ICT / OTE'
        ? new Set(['0','0.5','0.618','0.705','0.786','1'])
        : name === 'AXION PRIME'
          ? new Set(['0','0.236','0.382','0.5','0.618','0.705','0.786','1'])
          : null;

      if (!selected) return;
      parentElement.querySelectorAll('[data-fib-level]').forEach(el => {
        el.checked=selected.has(String(el.dataset.fibLevel));
      });
      drawAll();
    }

    const fibTemplateSelect=parentElement.querySelector('#fib-template');
    fibTemplateSelect.onchange=() => {
      applyFibTemplate(fibTemplateSelect.value);
      const status=parentElement.querySelector('#workspace-save-status');
      status.textContent=fibTemplateSelect.value==='Personalizada'
        ? 'Selecciona manualmente los niveles en Fibonacci.'
        : `Plantilla ${fibTemplateSelect.value} aplicada.`;
    };

    const riskTemplateSelect=parentElement.querySelector('#risk-template');
    riskTemplateSelect.onchange=() => {
      parentElement.querySelector('#workspace-save-status').textContent=
        `Riesgo inicial de nuevas posiciones: ${riskTemplateSelect.value}.`;
    };

    // Workspace personalization is persistent frontend state.
    const workspaceName=parentElement.querySelector('#workspace-name');
    parentElement.querySelector('#save-workspace').onclick = () => {
      const workspacePayload={
        name:workspaceName.value || 'Workspace Trader',
        fib_template:parentElement.querySelector('#fib-template').value,
        risk_template:parentElement.querySelector('#risk-template').value,
        colors:{...themeColors},
        drawing_style:{...drawingStyle}
      };
      setStateValue('workspace', workspacePayload);
      try {
        localStorage.setItem('axion_prime_workspace', JSON.stringify(workspacePayload));
      } catch (_) {}
      const status=parentElement.querySelector('#workspace-save-status');
      status.textContent='✓ Workspace guardado';
      setTimeout(()=>status.textContent='Los cambios se aplican al instante.',1400);
    };

    let savedWorkspace={};
    try {
      savedWorkspace=JSON.parse(localStorage.getItem('axion_prime_workspace') || '{}') || {};
    } catch (_) {}

    const currentWorkspace={
      ...(data.workspace || {}),
      ...savedWorkspace,
      colors:{...((data.workspace || {}).colors || {}),...(savedWorkspace.colors || {})}
    };

    if (currentWorkspace.name) workspaceName.value=currentWorkspace.name;
    if (currentWorkspace.fib_template) fibTemplateSelect.value=currentWorkspace.fib_template;
    if (currentWorkspace.risk_template) riskTemplateSelect.value=currentWorkspace.risk_template;
    if (currentWorkspace.colors) {
      themeColors={...themeColors,...currentWorkspace.colors};
      syncColorInputs();
      applyTheme();
    }

    if (currentWorkspace.drawing_style) {
      drawingStyle={...drawingStyle,...currentWorkspace.drawing_style};
      drawingColorInput.value=drawingStyle.color;
      drawingLineStyle.value=drawingStyle.lineStyle;
      drawingLineWidth.value=String(drawingStyle.lineWidth);
      drawingOpacity.value=String(Math.round(Number(drawingStyle.opacity)*100));
      drawingExtendLeft.checked=Boolean(drawingStyle.extendLeft);
      drawingExtendRight.checked=Boolean(drawingStyle.extendRight);
    }

    applyFibTemplate(fibTemplateSelect.value);

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

    const cleanup = () => {
      cleanupFns.forEach(fn => {
        try { fn(); } catch (_) {}
      });
      cleanupFns = [];
      try { chart.remove(); } catch (_) {}
      try { chartHost.replaceChildren(); } catch (_) {}
    };

    parentElement.__axionCleanup = cleanup;
    return cleanup;
  } catch (err) {
    console.error('AXION Chart Component error', err);
    root.innerHTML = `<div style="padding:24px;color:#ff8b9d;background:#160810;border:1px solid #51202a;border-radius:12px">
      AXION Chart no pudo inicializarse: ${String(err?.message || err)}
    </div>`;
  }
}
"""


_axion_chart_component = st.components.v2.component(
    "axion_prime_chart_workspace_v15",
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
    """Monta AXION REPLAY V15 con dibujos anclados y estilos profesionales."""
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
