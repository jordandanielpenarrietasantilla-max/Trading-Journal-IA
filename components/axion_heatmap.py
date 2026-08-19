from __future__ import annotations

import streamlit as st


HTML = r"""
<div class="axion-live-shell" id="axion-live-shell">
  <header class="live-header">
    <div class="live-brand">
      <div class="brand-mark">A</div>
      <div class="brand-copy">
        <div class="brand-name">AXION <span>PRIME</span></div>
        <div class="brand-sub">ORDER FLOW TERMINAL</div>
      </div>
    </div>

    <div class="instrument">
      <strong id="instrument-name">XAU/USD</strong>
      <span id="instrument-sub">Oro / Dólar estadounidense</span>
    </div>

    <nav class="tf-nav" id="tf-nav">
      <button data-tf="1m">1m</button>
      <button data-tf="5m">5m</button>
      <button data-tf="15m" class="active">15m</button>
      <button data-tf="30m">30m</button>
      <button data-tf="1H">1h</button>
      <button data-tf="4H">4h</button>
      <button data-tf="1D">D</button>
    </nav>

    <div class="header-status">
      <span class="status-dot"></span>
      <div>
        <b>MARKET DEPTH</b>
        <small>PENDIENTE DE CONEXIÓN</small>
      </div>
    </div>

    <button class="icon-btn" id="fullscreen-btn" type="button" title="Pantalla completa">⛶</button>
  </header>

  <aside class="live-sidebar">
    <button class="side-btn active" data-view="chart" type="button" title="Gráfico">
      <svg viewBox="0 0 24 24"><path d="M4 17l4-5 4 3 5-8 3 3"/></svg><span>Gráfico</span>
    </button>
    <button class="side-btn" data-view="heatmap" type="button" title="Heatmap">
      <svg viewBox="0 0 24 24"><path d="M5 5h4v4H5zM10 5h4v4h-4zM15 5h4v4h-4zM5 10h4v4H5zM10 10h4v4h-4zM15 10h4v4h-4zM5 15h4v4H5zM10 15h4v4h-4zM15 15h4v4h-4z"/></svg><span>Heatmap</span>
    </button>
    <button class="side-btn" data-view="orders" type="button" title="Órdenes">
      <svg viewBox="0 0 24 24"><path d="M6 7h12M6 12h9M6 17h6"/></svg><span>Órdenes</span>
    </button>
    <button class="side-btn" data-view="positions" type="button" title="Posiciones">
      <svg viewBox="0 0 24 24"><path d="M6 18V8m6 10V4m6 14v-7"/></svg><span>Posiciones</span>
    </button>
    <button class="side-btn" data-view="dom" type="button" title="Libro DOM">
      <svg viewBox="0 0 24 24"><path d="M5 6h14v4H5zM5 14h14v4H5z"/></svg><span>Libro DOM</span>
    </button>
    <div class="side-spacer"></div>
    <button class="side-btn" data-view="settings" type="button" title="Ajustes">
      <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 00-.1-1.2l2-1.5-2-3.4-2.4 1a8 8 0 00-2-.9L14 3h-4l-.5 3a8 8 0 00-2 .9l-2.4-1-2 3.4 2 1.5A7 7 0 005 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.4-1a8 8 0 002 .9L10 21h4l.5-3a8 8 0 002-.9l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/></svg><span>Ajustes</span>
    </button>
  </aside>

  <main class="live-main">
    <section class="module-tabs">
      <div class="tab-group">
        <button class="module-tab active" type="button">Heatmap Order Flow</button>
        <button class="module-tab" type="button">Volumen</button>
        <button class="module-tab" type="button">VWAP</button>
        <button class="module-tab" type="button">Zonas de liquidez</button>
        <button class="module-tab" type="button">Bloques de órdenes</button>
      </div>

      <div class="toolbar-right">
        <select id="symbol-select">
          <option value="XAUUSD">XAU/USD</option>
          <option value="BTCUSDT">BTC/USDT</option>
        </select>
        <label class="slider-control">
          <span>Intensidad</span>
          <input id="intensity" type="range" min="10" max="100" value="70">
        </label>
      </div>
    </section>

    <section class="terminal-workspace">
      <div class="chart-area">
        <div class="chart-head">
          <div>
            <strong id="meta-symbol">XAU/USD</strong>
            <span> · 15m · AXION PRIME</span>
          </div>
          <div id="ohlc-line">O — H — L — C —</div>
        </div>

        <div class="heatmap-canvas">
          <div class="grid"></div>

          <div class="feed-warning">
            <div class="warning-eyebrow">HEATMAP ORDER FLOW</div>
            <strong>Esperando profundidad real de mercado</strong>
            <p>
              El precio puede conectarse de forma independiente, pero las bandas de liquidez,
              órdenes pasivas, DOM y delta permanecerán vacías hasta recibir un order book verificable.
            </p>
            <div class="warning-badges">
              <span>NO DATA SYNTHESIS</span>
              <span>MARKET DEPTH REQUIRED</span>
            </div>
          </div>

          <div class="current-price-line"></div>
        </div>

        <div class="time-axis">
          <span>21:00</span><span>00:00</span><span>03:00</span><span>06:00</span>
          <span>09:00</span><span>12:00</span>
        </div>
      </div>

      <aside class="profile-panel">
        <div class="profile-head">
          <strong>VOLUME PROFILE</strong>
          <span>REAL DATA ONLY</span>
        </div>

        <div class="profile-empty">
          <div class="profile-axis">
            <span>—</span><span>—</span><span>—</span><span>—</span><span>—</span>
          </div>
          <div class="profile-message">
            <b>Perfil pendiente</b>
            <small>Se activará cuando la fuente entregue volumen válido.</small>
          </div>
        </div>

        <div class="profile-footer">
          <span>POC</span><b>—</b>
          <span>VAH</span><b>—</b>
          <span>VAL</span><b>—</b>
        </div>
      </aside>
    </section>

    <section class="live-metrics">
      <article class="metric-card">
        <div class="metric-title buy">LIQUIDEZ COMPRADORA</div>
        <div class="metric-value disabled">—</div>
        <div class="metric-sub">Order book requerido</div>
        <div class="meter"><i></i></div>
      </article>

      <article class="metric-card">
        <div class="metric-title sell">LIQUIDEZ VENDEDORA</div>
        <div class="metric-value disabled">—</div>
        <div class="metric-sub">Order book requerido</div>
        <div class="meter sell-meter"><i></i></div>
      </article>

      <article class="metric-card">
        <div class="metric-title delta">DELTA ACUMULADO</div>
        <div class="metric-value disabled">—</div>
        <div class="metric-sub">Trades agresores requeridos</div>
        <div class="delta-meter"><i></i></div>
      </article>

      <article class="metric-card">
        <div class="metric-title session">SESIÓN</div>
        <div class="metric-value small-value" id="session-name">—</div>
        <div class="metric-sub">Horario de mercado</div>
        <div class="session-track"><i></i></div>
      </article>

      <article class="metric-card visual-card">
        <div class="metric-title">VISUALIZACIÓN</div>
        <div class="scheme-row">
          <button class="scheme active" data-scheme="axion" type="button"></button>
          <button class="scheme fire" data-scheme="fire" type="button"></button>
          <button class="scheme ice" data-scheme="ice" type="button"></button>
          <button class="scheme mono" data-scheme="mono" type="button"></button>
        </div>
        <label class="contrast-control">
          <span>Contraste</span>
          <input id="contrast" type="range" min="30" max="100" value="70">
        </label>
      </article>
    </section>
  </main>
</div>
"""

CSS = r"""
:host{
  display:block;
  width:100%;
  height:100%;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
*{box-sizing:border-box}
button,select,input{font:inherit}
button{user-select:none}
.axion-live-shell{
  width:100%;
  height:920px;
  min-height:720px;
  display:grid;
  grid-template-columns:64px minmax(0,1fr);
  grid-template-rows:64px minmax(0,1fr);
  overflow:hidden;
  color:#dce6f7;
  background:#030812;
  border:1px solid rgba(65,94,143,.34);
  border-radius:14px;
  box-shadow:0 24px 80px rgba(0,0,0,.32);
}
.axion-live-shell:fullscreen{width:100vw;height:100vh;border:0;border-radius:0}

.live-header{
  grid-column:1/3;
  display:grid;
  grid-template-columns:250px 240px minmax(350px,1fr) auto 38px;
  align-items:center;
  gap:14px;
  padding:0 12px 0 16px;
  border-bottom:1px solid rgba(64,88,132,.28);
  background:linear-gradient(180deg,#07101c,#040a13);
}
.live-brand{display:flex;align-items:center;gap:10px;min-width:0}
.brand-mark{
  width:34px;height:34px;display:grid;place-items:center;
  border-radius:8px;
  font-size:20px;font-weight:950;color:#06111a;
  background:linear-gradient(135deg,#4cdaf0,#6464ff);
}
.brand-name{font-size:16px;font-weight:900;letter-spacing:.6px;color:#f2f6fc}
.brand-name span{color:#61dced}
.brand-sub{font-size:6px;letter-spacing:1.8px;color:#5e708b;margin-top:1px}
.instrument{padding-left:14px;border-left:1px solid #1c2a40;min-width:0}
.instrument strong{display:block;font-size:14px;color:#f3f7fd}
.instrument span{display:block;margin-top:2px;font-size:8px;color:#6d7e99}
.tf-nav{display:flex;align-items:center;gap:2px;overflow:hidden}
.tf-nav button{
  height:31px;min-width:36px;padding:0 7px;border:0;border-radius:6px;
  color:#71819b;background:transparent;cursor:pointer;font-size:9px
}
.tf-nav button:hover{background:#101a29;color:#dce8f8}
.tf-nav button.active{background:#0f2238;color:#53d8ee}
.header-status{
  height:34px;display:flex;align-items:center;gap:8px;
  padding:0 10px;border:1px solid #27354a;border-radius:7px;background:#08111e
}
.status-dot{width:7px;height:7px;border-radius:50%;background:#d7a855;box-shadow:0 0 12px rgba(215,168,85,.24)}
.header-status b{display:block;color:#aeb9ca;font-size:7px;letter-spacing:.7px}
.header-status small{display:block;color:#6d7a90;font-size:6px;margin-top:1px}
.icon-btn{
  width:34px;height:34px;border:1px solid #253850;border-radius:7px;
  background:#081321;color:#aebcd1;cursor:pointer;font-size:15px
}

.live-sidebar{
  grid-column:1;grid-row:2;
  display:flex;flex-direction:column;align-items:center;gap:3px;
  padding:7px 6px;
  background:#050b14;border-right:1px solid rgba(65,90,132,.28)
}
.side-btn{
  width:48px;height:48px;display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:2px;border:0;border-radius:7px;background:transparent;color:#6e7c94;cursor:pointer
}
.side-btn svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.45;stroke-linecap:round;stroke-linejoin:round}
.side-btn span{font-size:6px}
.side-btn:hover{background:#111a28;color:#dce6f5}
.side-btn.active{color:#55d7eb;background:#0b1c2c;box-shadow:inset 2px 0 #45d7ef}
.side-spacer{flex:1}

.live-main{
  grid-column:2;grid-row:2;min-width:0;min-height:0;
  display:grid;grid-template-rows:48px minmax(0,1fr) 162px
}
.module-tabs{
  min-width:0;display:flex;align-items:center;gap:8px;
  padding:6px 9px;border-bottom:1px solid rgba(65,90,132,.26);background:#060c15
}
.tab-group{display:flex;align-items:center;gap:4px;min-width:0;overflow-x:auto;scrollbar-width:none}
.tab-group::-webkit-scrollbar{display:none}
.module-tab{
  height:30px;padding:0 11px;border:1px solid transparent;border-radius:5px;
  color:#738198;background:transparent;cursor:pointer;font-size:8px;white-space:nowrap
}
.module-tab:hover{background:#0d1725;color:#d9e4f4}
.module-tab.active{background:#10213a;border-color:#255d8a;color:#59d9ec}
.toolbar-right{margin-left:auto;display:flex;align-items:center;gap:7px}
.toolbar-right select{
  height:30px;border:1px solid #24364f;border-radius:6px;background:#08111e;color:#c8d4e5;
  padding:0 8px;font-size:8px
}
.slider-control{
  height:30px;display:flex;align-items:center;gap:7px;padding:0 8px;
  border:1px solid #24364f;border-radius:6px;color:#718099;font-size:7px
}
.slider-control input{width:90px}

.terminal-workspace{
  min-height:0;min-width:0;
  display:grid;grid-template-columns:minmax(0,1fr) 190px;
  background:#030812
}
.chart-area{position:relative;min-width:0;min-height:0;border-right:1px solid rgba(65,90,132,.24)}
.chart-head{
  position:absolute;top:0;left:0;right:0;height:34px;z-index:4;
  display:flex;align-items:center;justify-content:space-between;padding:0 10px;
  border-bottom:1px solid rgba(65,90,132,.15);background:rgba(3,8,18,.88);
  color:#64738a;font-size:7px
}
.chart-head strong{font-size:11px;color:#eef4fc}
.chart-head span{color:#7888a1}
.heatmap-canvas{position:absolute;inset:34px 0 22px 0;overflow:hidden;background:#030711}
.grid{
  position:absolute;inset:0;
  background-image:
    linear-gradient(rgba(51,71,103,.20) 1px,transparent 1px),
    linear-gradient(90deg,rgba(51,71,103,.18) 1px,transparent 1px);
  background-size:100% 54px,90px 100%
}
.current-price-line{
  position:absolute;left:0;right:0;top:56%;
  border-top:1px dashed rgba(69,214,235,.32)
}
.feed-warning{
  position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:min(500px,72%);padding:23px 26px;text-align:center;
  border:1px solid rgba(78,106,154,.30);border-radius:12px;
  background:rgba(5,12,22,.88);backdrop-filter:blur(8px);
  box-shadow:0 18px 45px rgba(0,0,0,.28)
}
.warning-eyebrow{font-size:7px;font-weight:900;letter-spacing:1.4px;color:#54d8ec}
.feed-warning strong{display:block;margin-top:7px;font-size:14px;color:#eef4fc}
.feed-warning p{margin:8px auto 0;max-width:400px;color:#718098;font-size:8px;line-height:1.55}
.warning-badges{display:flex;justify-content:center;gap:6px;margin-top:12px}
.warning-badges span{
  padding:5px 7px;border:1px solid #34445e;border-radius:999px;
  color:#8997ab;background:#08111d;font-size:6px;font-weight:800;letter-spacing:.55px
}
.time-axis{
  position:absolute;left:0;right:0;bottom:0;height:22px;
  display:flex;align-items:center;justify-content:space-around;
  color:#55657c;font-size:7px;border-top:1px solid rgba(65,90,132,.16)
}

.profile-panel{min-height:0;display:grid;grid-template-rows:36px minmax(0,1fr) 58px;background:#050b15}
.profile-head{
  display:flex;align-items:center;justify-content:space-between;padding:0 10px;
  border-bottom:1px solid rgba(65,90,132,.18)
}
.profile-head strong{font-size:8px;color:#dfe7f3}
.profile-head span{font-size:5px;color:#65748a;letter-spacing:.7px}
.profile-empty{position:relative;min-height:0}
.profile-axis{
  position:absolute;right:8px;top:12px;bottom:12px;
  display:flex;flex-direction:column;justify-content:space-around;
  color:#5a6980;font-size:7px
}
.profile-message{
  position:absolute;left:12px;right:45px;top:50%;transform:translateY(-50%);
  padding:12px;border:1px dashed #2b3c55;border-radius:8px;background:#07101b
}
.profile-message b{display:block;font-size:8px;color:#9eacbf}
.profile-message small{display:block;margin-top:5px;font-size:6px;line-height:1.4;color:#65748a}
.profile-footer{
  display:grid;grid-template-columns:auto 1fr auto 1fr auto 1fr;align-items:center;gap:5px;
  padding:0 9px;border-top:1px solid rgba(65,90,132,.18);font-size:6px;color:#65748a
}
.profile-footer b{color:#aab6c8;font-size:7px}

.live-metrics{
  min-width:0;display:grid;grid-template-columns:1fr 1fr 1fr .8fr 1.1fr;
  background:#060d17;border-top:1px solid rgba(65,90,132,.26)
}
.metric-card{min-width:0;padding:14px 15px;border-right:1px solid rgba(65,90,132,.20)}
.metric-card:last-child{border-right:0}
.metric-title{font-size:7px;font-weight:900;letter-spacing:.45px;color:#8090a8}
.metric-title.buy{color:#46d7b6}.metric-title.sell{color:#ff6c80}.metric-title.delta{color:#a07bff}.metric-title.session{color:#68a9ff}
.metric-value{margin-top:10px;font-size:18px;font-weight:900;color:#eef4fb}
.metric-value.disabled{color:#617086}
.metric-value.small-value{font-size:15px}
.metric-sub{margin-top:3px;color:#607087;font-size:6px}
.meter{height:6px;border-radius:999px;background:#11202d;margin-top:12px;overflow:hidden}
.meter i{display:block;width:0;height:100%;background:#36c6a5}
.sell-meter i{background:#ed536b}
.delta-meter{height:6px;margin-top:12px;border-radius:999px;background:linear-gradient(90deg,#542331 0 48%,#1c252c 48% 52%,#174236 52%)}
.delta-meter i{display:none}
.session-track{height:4px;border-radius:999px;background:#142033;margin-top:14px}.session-track i{display:block;width:0}
.scheme-row{display:flex;gap:5px;margin-top:11px}
.scheme{width:34px;height:25px;border:1px solid #2b3b52;border-radius:5px;cursor:pointer;background:linear-gradient(135deg,#0a1330,#163b70,#922563)}
.scheme.fire{background:linear-gradient(135deg,#241014,#8e3020,#ffc84e)}
.scheme.ice{background:linear-gradient(135deg,#06142a,#175191,#48dce9)}
.scheme.mono{background:linear-gradient(135deg,#111,#555,#aaa)}
.scheme.active{outline:1px solid #4d8cff}
.contrast-control{display:flex;align-items:center;gap:7px;margin-top:10px;color:#637187;font-size:6px}
.contrast-control input{width:90px}

@media(max-width:1150px){
  .live-header{grid-template-columns:210px 180px minmax(280px,1fr) 38px}
  .header-status{display:none}
  .module-tab:nth-child(n+4){display:none}
  .terminal-workspace{grid-template-columns:minmax(0,1fr) 160px}
  .live-metrics{grid-template-columns:repeat(3,1fr)}
  .metric-card:nth-child(n+4){display:none}
}
"""

JS = r"""
export default function(component) {
  const {parentElement,data,setTriggerValue,setStateValue}=component;
  const shell=parentElement.querySelector('#axion-live-shell');
  if (!shell) return;

  const symbolSelect=parentElement.querySelector('#symbol-select');
  const intensity=parentElement.querySelector('#intensity');
  const contrast=parentElement.querySelector('#contrast');
  const tfButtons=[...parentElement.querySelectorAll('[data-tf]')];

  const currentSymbol=String(data?.symbol || 'XAUUSD').toUpperCase();
  const currentTf=String(data?.timeframe || '15m');

  symbolSelect.value=currentSymbol;
  tfButtons.forEach(btn=>btn.classList.toggle('active',btn.dataset.tf===currentTf));

  function symbolLabel(value){
    return value==='BTCUSDT' ? 'BTC/USDT' : 'XAU/USD';
  }
  function symbolSubtitle(value){
    return value==='BTCUSDT' ? 'Bitcoin / TetherUS' : 'Oro / Dólar estadounidense';
  }
  function paintHeader(){
    const label=symbolLabel(symbolSelect.value);
    parentElement.querySelector('#instrument-name').textContent=label;
    parentElement.querySelector('#meta-symbol').textContent=label;
    parentElement.querySelector('#instrument-sub').textContent=symbolSubtitle(symbolSelect.value);
  }
  paintHeader();

  symbolSelect.onchange=()=>{
    paintHeader();
    setTriggerValue('symbol',symbolSelect.value);
  };

  tfButtons.forEach(btn=>{
    btn.onclick=()=>{
      tfButtons.forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
      setTriggerValue('timeframe',btn.dataset.tf);
    };
  });

  intensity.oninput=()=>setStateValue('heatmap_intensity',Number(intensity.value));

  contrast.oninput=()=>{
    setStateValue('heatmap_contrast',Number(contrast.value));
    const value=Math.max(.75,Math.min(1.35,Number(contrast.value)/70));
    parentElement.querySelector('.terminal-workspace').style.filter=`contrast(${value})`;
  };

  parentElement.querySelectorAll('.module-tab').forEach(btn=>{
    btn.onclick=()=>{
      parentElement.querySelectorAll('.module-tab').forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
      setStateValue('heatmap_mode',btn.textContent.trim());
    };
  });

  parentElement.querySelectorAll('.side-btn').forEach(btn=>{
    btn.onclick=()=>{
      parentElement.querySelectorAll('.side-btn').forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
      setStateValue('live_view',btn.dataset.view);
    };
  });

  parentElement.querySelectorAll('.scheme').forEach(btn=>{
    btn.onclick=()=>{
      parentElement.querySelectorAll('.scheme').forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
      setStateValue('heatmap_scheme',btn.dataset.scheme);
    };
  });

  parentElement.querySelector('#fullscreen-btn').onclick=async()=>{
    try{
      if(!document.fullscreenElement) await shell.requestFullscreen();
      else await document.exitFullscreen();
    }catch(err){console.error('AXION Heatmap fullscreen',err)}
  };

  return ()=>{};
}
"""

_component = st.components.v2.component(
    "axion_live_heatmap_v2",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=True,
)


def render_axion_live_heatmap(
    *,
    symbol: str = "XAUUSD",
    timeframe: str = "15m",
    key: str = "axion_live_heatmap",
    height: int = 920,
):
    """
    Renderiza AXION LIVE / Heatmap V2.
    No genera ni simula datos de liquidez.
    """
    payload = {
        "symbol": symbol,
        "timeframe": timeframe,
        "liquidity_connected": False,
    }
    return _component(
        data=payload,
        default=None,
        key=key,
        width="stretch",
        height=height,
    )
