from __future__ import annotations

import streamlit as st


HTML = r"""
<div class="axion-live-shell" id="axion-live-shell">
  <header class="live-topbar">
    <div class="live-brand">
      <div class="brand-mark">A</div>
      <div>
        <div class="brand-name">AXION <span>PRIME</span></div>
        <div class="brand-sub">MARKET INTELLIGENCE</div>
      </div>
    </div>

    <div class="instrument-block">
      <div class="instrument-name" id="instrument-name">XAU/USD</div>
      <div class="instrument-sub" id="instrument-sub">Oro / Dólar estadounidense</div>
    </div>

    <div class="live-status">
      <span class="status-dot waiting"></span>
      <span id="live-status-text">PROFUNDIDAD PENDIENTE</span>
    </div>

    <button class="ghost-btn" id="backtesting-btn" type="button">⟲ Backtesting</button>
    <button class="primary-btn" id="live-btn" type="button">⚡ Mercado Live</button>
  </header>

  <aside class="live-sidebar">
    <button class="side-btn active" type="button" data-view="chart" title="Gráfico">⌁<span>Gráfico</span></button>
    <button class="side-btn" type="button" data-view="heatmap" title="Heatmap">⠿<span>Heatmap</span></button>
    <button class="side-btn" type="button" data-view="orders" title="Órdenes">≋<span>Órdenes</span></button>
    <button class="side-btn" type="button" data-view="positions" title="Posiciones">⌗<span>Posiciones</span></button>
    <button class="side-btn" type="button" data-view="dom" title="Libro DOM">▥<span>Libro DOM</span></button>
    <button class="side-btn" type="button" data-view="news" title="Noticias">▤<span>Noticias</span></button>
    <button class="side-btn" type="button" data-view="calendar" title="Calendario">▣<span>Calendario</span></button>
    <div class="side-spacer"></div>
    <button class="side-btn" type="button" data-view="settings" title="Ajustes">⚙<span>Ajustes</span></button>
  </aside>

  <main class="live-main">
    <section class="live-toolbar">
      <button class="mode-tab active" type="button">Heatmap Order Flow</button>
      <button class="mode-tab" type="button">Volumen</button>
      <button class="mode-tab" type="button">VWAP</button>
      <button class="mode-tab" type="button">Zonas de Liquidez</button>
      <button class="mode-tab" type="button">Bloques de Órdenes</button>

      <div class="toolbar-spacer"></div>

      <select id="symbol-select" class="top-select">
        <option value="XAUUSD">XAU/USD</option>
        <option value="BTCUSDT">BTC/USDT</option>
      </select>

      <select id="tf-select" class="top-select compact">
        <option>1m</option>
        <option>5m</option>
        <option selected>15m</option>
        <option>30m</option>
        <option>1H</option>
      </select>

      <label class="intensity-control">
        <span>Intensidad</span>
        <input id="intensity" type="range" min="10" max="100" value="70">
      </label>

      <button class="icon-btn" id="fullscreen-btn" type="button" title="Pantalla completa">⛶</button>
    </section>

    <section class="heatmap-stage">
      <div class="chart-meta">
        <div>
          <strong id="meta-symbol">XAU/USD</strong>
          <span> · ORDER FLOW</span>
        </div>
        <div class="ohlc-muted" id="ohlc-line">Esperando feed real de mercado...</div>
      </div>

      <div class="chart-grid" id="chart-grid"></div>

      <div class="heatmap-locked" id="heatmap-locked">
        <div class="lock-icon">◫</div>
        <div class="lock-title">HEATMAP DE LIQUIDEZ</div>
        <div class="lock-copy">
          Fuente de profundidad real todavía no conectada.
          AXION no mostrará liquidez sintética.
        </div>
        <div class="lock-chip">ORDER BOOK / MARKET DEPTH REQUIRED</div>
      </div>

      <div class="price-axis">
        <span>—</span><span>—</span><span>—</span><span>—</span><span>—</span>
      </div>
    </section>

    <section class="live-metrics">
      <article class="metric-card">
        <div class="metric-label buy">● LIQUIDEZ COMPRADORA</div>
        <div class="metric-value muted">Sin datos</div>
        <div class="metric-bar"><i></i></div>
        <div class="metric-foot"><span>Baja</span><span>Alta</span></div>
      </article>

      <article class="metric-card">
        <div class="metric-label sell">● LIQUIDEZ VENDEDORA</div>
        <div class="metric-value muted">Sin datos</div>
        <div class="metric-bar sellbar"><i></i></div>
        <div class="metric-foot"><span>Baja</span><span>Alta</span></div>
      </article>

      <article class="metric-card">
        <div class="metric-label delta">△ DELTA ACUMULADO</div>
        <div class="metric-value muted">Sin datos</div>
        <div class="delta-line"></div>
        <div class="metric-foot"><span>Venta</span><span>0</span><span>Compra</span></div>
      </article>

      <article class="metric-card">
        <div class="metric-label session">▣ SESIÓN</div>
        <div class="metric-value" id="session-name">—</div>
        <div class="metric-small">Se activará con feed horario real</div>
      </article>

      <article class="metric-card visualization-card">
        <div class="metric-label">VISUALIZACIÓN</div>
        <div class="visual-row">
          <button class="scheme active" data-scheme="axion" type="button">◫</button>
          <button class="scheme" data-scheme="fire" type="button">◫</button>
          <button class="scheme" data-scheme="ice" type="button">◫</button>
          <button class="scheme" data-scheme="mono" type="button">◫</button>
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
:host{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}
button,select,input{font:inherit}
.axion-live-shell{
  width:100%;height:920px;min-height:720px;overflow:hidden;
  display:grid;grid-template-columns:76px minmax(0,1fr);
  grid-template-rows:70px minmax(0,1fr);
  color:#dce7f7;background:#040913;border:1px solid #142137;border-radius:14px;
  box-shadow:0 24px 80px rgba(0,0,0,.28)
}
.live-topbar{
  grid-column:1/3;display:grid;
  grid-template-columns:300px minmax(220px,1fr) auto auto auto;
  align-items:center;gap:12px;padding:0 18px;
  background:linear-gradient(180deg,#07101d,#040a14);
  border-bottom:1px solid #17243a
}
.live-brand{display:flex;align-items:center;gap:11px}
.brand-mark{
  width:37px;height:37px;border-radius:10px;display:grid;place-items:center;
  font-size:22px;font-weight:900;color:#06111c;
  background:linear-gradient(135deg,#57ddf0,#7470ff)
}
.brand-name{font-weight:850;font-size:17px;letter-spacing:.7px}
.brand-name span{color:#58dced}
.brand-sub{font-size:7px;letter-spacing:2px;color:#60718e;margin-top:2px}
.instrument-block{padding-left:17px;border-left:1px solid #1a2940}
.instrument-name{font-size:16px;font-weight:800}
.instrument-sub{font-size:9px;color:#6e809e;margin-top:2px}
.live-status{display:flex;align-items:center;gap:7px;font-size:9px;font-weight:800;color:#a1aec2}
.status-dot{width:8px;height:8px;border-radius:50%;background:#6c7688}
.status-dot.waiting{box-shadow:0 0 12px rgba(255,190,87,.2);background:#d5a95b}
.ghost-btn,.primary-btn,.icon-btn{
  border-radius:8px;height:34px;padding:0 12px;cursor:pointer
}
.ghost-btn{background:#081221;color:#a9b9d1;border:1px solid #223652}
.primary-btn{
  color:white;border:1px solid #2e7ff0;
  background:linear-gradient(135deg,#168cde,#6354f5)
}
.live-sidebar{
  grid-column:1;grid-row:2;background:#050c17;border-right:1px solid #18263a;
  padding:9px 8px;display:flex;flex-direction:column;align-items:center;gap:4px
}
.side-btn{
  width:58px;height:54px;border:1px solid transparent;border-radius:10px;
  background:transparent;color:#6e819f;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:3px;cursor:pointer;font-size:18px
}
.side-btn span{font-size:7px}
.side-btn:hover{background:#0a1728;color:#dce8fa}
.side-btn.active{background:#0b1b2e;border-color:#1d5270;color:#56d9eb}
.side-spacer{flex:1}
.live-main{grid-column:2;grid-row:2;min-width:0;display:grid;grid-template-rows:54px minmax(0,1fr) 178px}
.live-toolbar{
  display:flex;align-items:center;gap:6px;padding:7px 10px;
  border-bottom:1px solid #15243a;background:#060d18;min-width:0
}
.mode-tab{
  height:32px;padding:0 13px;border-radius:5px;border:1px solid #17263b;
  color:#7f90aa;background:#07111f;cursor:pointer;font-size:9px
}
.mode-tab.active{
  color:#ecf8ff;border-color:#2873c9;
  background:linear-gradient(135deg,#126bc1,#4e52ed)
}
.toolbar-spacer{flex:1}
.top-select{
  height:32px;min-width:108px;border:1px solid #233651;border-radius:6px;
  background:#07111f;color:#c8d6ea;padding:0 8px;font-size:9px
}
.top-select.compact{min-width:66px}
.intensity-control{
  height:32px;display:flex;align-items:center;gap:7px;padding:0 9px;
  border:1px solid #20324c;border-radius:6px;color:#70829d;font-size:8px
}
.intensity-control input{width:95px}
.icon-btn{width:36px;padding:0;background:#081323;border:1px solid #233854;color:#9eb0c9}
.heatmap-stage{
  position:relative;min-height:0;overflow:hidden;background:
  radial-gradient(circle at 60% 35%,rgba(35,54,93,.12),transparent 34%),
  linear-gradient(180deg,#050a13,#040812)
}
.chart-meta{
  position:absolute;top:11px;left:14px;right:74px;z-index:5;
  display:flex;justify-content:space-between;align-items:center;
  color:#a7b6cb;font-size:10px
}
.chart-meta strong{color:#eff7ff;font-size:13px}
.ohlc-muted{font-size:8px;color:#667894}
.chart-grid{
  position:absolute;inset:42px 66px 18px 0;
  background-image:
    linear-gradient(rgba(41,62,94,.32) 1px,transparent 1px),
    linear-gradient(90deg,rgba(41,62,94,.26) 1px,transparent 1px);
  background-size:100% 64px,105px 100%;
  border-top:1px solid rgba(48,72,109,.22)
}
.chart-grid:after{
  content:"";
  position:absolute;left:5%;right:3%;top:54%;
  border-top:1px dashed rgba(64,213,231,.42)
}
.heatmap-locked{
  position:absolute;left:50%;top:49%;transform:translate(-50%,-50%);
  width:min(460px,70%);padding:27px;text-align:center;z-index:6;
  border:1px solid rgba(88,120,174,.24);border-radius:14px;
  background:rgba(5,12,24,.82);backdrop-filter:blur(9px);
  box-shadow:0 18px 55px rgba(0,0,0,.32)
}
.lock-icon{font-size:28px;color:#55d8ec}
.lock-title{font-size:15px;font-weight:900;letter-spacing:1.5px;margin-top:7px}
.lock-copy{font-size:10px;line-height:1.55;color:#8294b0;max-width:340px;margin:8px auto 0}
.lock-chip{
  display:inline-block;margin-top:13px;padding:6px 9px;border-radius:999px;
  border:1px solid #3f536f;color:#95a6bf;font-size:7px;letter-spacing:.8px
}
.price-axis{
  position:absolute;right:0;top:50px;bottom:20px;width:66px;
  border-left:1px solid rgba(48,72,109,.28);
  display:flex;flex-direction:column;justify-content:space-around;
  color:#576984;font-size:8px;padding-left:8px
}
.live-metrics{
  min-width:0;display:grid;grid-template-columns:1fr 1fr 1fr .85fr 1.2fr;
  border-top:1px solid #17263b;background:#07101c
}
.metric-card{padding:17px 18px;border-right:1px solid #18263a;min-width:0}
.metric-card:last-child{border-right:0}
.metric-label{font-size:8px;font-weight:800;color:#8191a9;letter-spacing:.25px}
.metric-label.buy{color:#45d9ba}.metric-label.sell{color:#ff6b7e}.metric-label.delta{color:#9d7cff}
.metric-label.session{color:#63a8ff}
.metric-value{font-size:20px;font-weight:850;margin-top:13px;color:#eff5ff}
.metric-value.muted{color:#66758b}
.metric-bar{height:8px;border-radius:999px;background:#11273b;margin-top:14px;overflow:hidden}
.metric-bar i{display:block;width:0;height:100%;background:#39c8a9}
.metric-bar.sellbar i{background:#ec586e}
.metric-foot{display:flex;justify-content:space-between;color:#55657c;font-size:7px;margin-top:5px}
.metric-small{font-size:8px;color:#687994;margin-top:7px}
.delta-line{height:8px;margin-top:14px;border-radius:999px;background:linear-gradient(90deg,#5e2231 0 48%,#1c292e 48% 52%,#174837 52%)}
.visual-row{display:flex;gap:7px;margin-top:12px}
.scheme{
  width:39px;height:28px;border-radius:5px;border:1px solid #273954;cursor:pointer;
  background:linear-gradient(135deg,#151030,#0f4f6f,#c96825)
}
.scheme:nth-child(2){background:linear-gradient(135deg,#241013,#8e301c,#ffc24a)}
.scheme:nth-child(3){background:linear-gradient(135deg,#07152c,#174a88,#46d8eb)}
.scheme:nth-child(4){background:linear-gradient(135deg,#111,#444,#999)}
.scheme.active{outline:1px solid #4f8cff}
.contrast-control{display:flex;align-items:center;gap:8px;margin-top:12px;color:#65758d;font-size:8px}
.contrast-control input{width:100px}
@media(max-width:1100px){
  .live-topbar{grid-template-columns:230px minmax(160px,1fr) auto auto}
  .live-status{display:none}
  .mode-tab:nth-of-type(n+4){display:none}
  .live-metrics{grid-template-columns:1fr 1fr 1fr}
  .metric-card:nth-child(n+4){display:none}
}
"""

JS = r"""
export default function(component) {
  const {parentElement,data,setTriggerValue,setStateValue}=component;
  const shell=parentElement.querySelector('#axion-live-shell');
  if (!shell) return;

  const symbolSelect=parentElement.querySelector('#symbol-select');
  const tfSelect=parentElement.querySelector('#tf-select');
  const intensity=parentElement.querySelector('#intensity');
  const contrast=parentElement.querySelector('#contrast');

  if (data?.symbol) symbolSelect.value=data.symbol;
  if (data?.timeframe) tfSelect.value=data.timeframe;

  const symbolLabel=(symbolSelect.value==='XAUUSD')?'XAU/USD':'BTC/USDT';
  parentElement.querySelector('#instrument-name').textContent=symbolLabel;
  parentElement.querySelector('#meta-symbol').textContent=symbolLabel;

  symbolSelect.onchange=()=>{
    setTriggerValue('symbol',symbolSelect.value);
  };

  tfSelect.onchange=()=>{
    setTriggerValue('timeframe',tfSelect.value);
  };

  intensity.oninput=()=>{
    setStateValue('heatmap_intensity',Number(intensity.value));
  };

  contrast.oninput=()=>{
    setStateValue('heatmap_contrast',Number(contrast.value));
    shell.style.filter=`contrast(${Number(contrast.value)/70})`;
  };

  parentElement.querySelectorAll('.mode-tab').forEach(btn=>{
    btn.onclick=()=>{
      parentElement.querySelectorAll('.mode-tab').forEach(x=>x.classList.remove('active'));
      btn.classList.add('active');
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
    }catch(err){console.error('Fullscreen',err)}
  };

  parentElement.querySelector('#backtesting-btn').onclick=()=>{
    setTriggerValue('navigate','backtesting');
  };
  parentElement.querySelector('#live-btn').onclick=()=>{
    setTriggerValue('navigate','live');
  };

  return ()=>{};
}
"""

_component = st.components.v2.component(
    "axion_live_heatmap_v1",
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
    Renderiza la carcasa visual de AXION LIVE / Heatmap.
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
