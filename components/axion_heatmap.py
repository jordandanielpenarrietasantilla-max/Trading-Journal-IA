from __future__ import annotations

import streamlit as st


HTML = r"""
<div class="axion-orderflow" id="axion-orderflow">
  <header class="of-header">
    <div class="of-brand">
      <div class="brand-logo">A</div>
      <div>
        <div class="brand-title">AXION <span>PRIME</span></div>
        <div class="brand-sub">ORDER FLOW TERMINAL</div>
      </div>
    </div>

    <div class="instrument-box">
      <div class="instrument-row">
        <strong id="instrument-name">BTC/USDT</strong>
        <span class="star">☆</span>
      </div>
      <small id="instrument-sub">Bitcoin / TetherUS · Binance Spot</small>
    </div>

    <div class="quote-box">
      <b id="header-price">—</b>
      <span id="header-change">Esperando feed</span>
    </div>

    <nav class="timeframes" id="timeframes">
      <button data-tf="1m" class="active">1m</button>
      <button data-tf="5m">5m</button>
      <button data-tf="15m">15m</button>
      <button data-tf="30m">30m</button>
      <button data-tf="1H">1h</button>
      <button data-tf="4H">4h</button>
      <button data-tf="1D">D</button>
    </nav>

    <div class="header-tools">
      <button type="button">◫ <span>Indicadores</span></button>
      <button type="button">◴ <span>Alertas</span></button>
      <button type="button">≪ <span>Repetición</span></button>
    </div>

    <div class="header-actions">
      <button class="square-btn" type="button" title="Diseño">▦</button>
      <button class="square-btn" type="button" title="Ajustes">⚙</button>
      <button class="square-btn" id="fullscreen-btn" type="button" title="Pantalla completa">⛶</button>
    </div>
  </header>

  <aside class="of-sidebar">
    <button class="nav-btn active" type="button"><span>⌁</span><small>Gráfico</small></button>
    <button class="nav-btn" type="button"><span>⠿</span><small>Heatmap</small></button>
    <button class="nav-btn" type="button"><span>≋</span><small>Órdenes</small></button>
    <button class="nav-btn" type="button"><span>⌗</span><small>Posiciones</small></button>
    <button class="nav-btn" type="button"><span>▥</span><small>Libro DOM</small></button>
    <button class="nav-btn" type="button"><span>▤</span><small>Noticias</small></button>
    <button class="nav-btn" type="button"><span>▣</span><small>Calendario</small></button>
    <div class="sidebar-spacer"></div>
    <button class="nav-btn" type="button"><span>⚙</span><small>Ajustes</small></button>
    <div class="sidebar-brand">AXION<br><span>PRIME</span></div>
  </aside>

  <main class="of-main">
    <section class="modebar">
      <div class="mode-tabs">
        <button class="mode active" type="button">Heatmap Order Flow</button>
        <button class="mode" type="button">Volumen</button>
        <button class="mode" type="button">VWAP</button>
        <button class="mode" type="button">Zonas de Liquidez</button>
        <button class="mode" type="button">Bloques de Órdenes</button>
        <button class="mode plus" type="button">＋</button>
      </div>
      <div class="mode-right">
        <select id="symbol-select">
          <option value="BTCUSDT">BTC/USDT</option>
          <option value="XAUUSD">XAU/USD</option>
        </select>
        <span>Intensidad</span>
        <input id="intensity" type="range" min="20" max="100" value="76">
        <button class="square-btn small" id="stage-fullscreen" type="button">⛶</button>
      </div>
    </section>

    <section class="chart-shell">
      <div class="chart-wrap">
        <canvas id="main-canvas"></canvas>

        <div class="feed-state" id="feed-state">
          <div class="feed-kicker" id="feed-kicker">ORDER FLOW</div>
          <strong id="feed-title">Conectando datos reales...</strong>
          <span id="feed-message">Sincronizando libro, trades y velas.</span>
        </div>

        <div class="chart-tags">
          <span class="tag seller" id="seller-zone">ZONA DE LIQUIDEZ VENDEDORA</span>
          <span class="tag buyer" id="buyer-zone">ZONA DE LIQUIDEZ COMPRADORA</span>
          <span class="tag order" id="order-block">BLOQUE DE ÓRDENES</span>
        </div>
      </div>

      <aside class="profile">
        <div class="profile-title">PERFIL DE FLUJO <span>REAL</span></div>
        <canvas id="profile-canvas"></canvas>
        <div class="profile-stats">
          <div><span>POC</span><b id="poc-value">—</b></div>
          <div><span>VWAP</span><b id="vwap-value">—</b></div>
          <div><span>SPREAD</span><b id="spread-value">—</b></div>
        </div>
      </aside>
    </section>

    <section class="metric-strip">
      <article>
        <div class="metric-head buy">♟ LIQUIDEZ COMPRADORA</div>
        <div class="metric-main"><b id="buy-liquidity">—</b><span id="buy-pct">—</span></div>
        <div class="meter"><i id="buy-meter"></i></div>
        <div class="metric-foot"><span>Baja</span><span>Alta</span></div>
      </article>

      <article>
        <div class="metric-head sell">♟ LIQUIDEZ VENDEDORA</div>
        <div class="metric-main"><b id="sell-liquidity">—</b><span id="sell-pct">—</span></div>
        <div class="meter sell-meter"><i id="sell-meter"></i></div>
        <div class="metric-foot"><span>Baja</span><span>Alta</span></div>
      </article>

      <article>
        <div class="metric-head delta">△ DELTA (ACUMULADO)</div>
        <div class="metric-main"><b id="delta-value">—</b><span id="delta-pct">—</span></div>
        <div class="delta-track"><i id="delta-meter"></i></div>
        <div class="metric-foot"><span>Venta</span><span>0</span><span>Compra</span></div>
      </article>

      <article>
        <div class="metric-head session">▣ SESIÓN</div>
        <div class="metric-main session-main"><b id="session-name">—</b></div>
        <div class="session-time" id="session-time">—</div>
        <div class="session-dots"><i></i><i></i><i></i><i></i><i></i></div>
      </article>

      <article class="visual-card">
        <div class="metric-head">VISUALIZACIÓN</div>
        <div class="visual-body">
          <div>
            <span>Esquema de color</span>
            <div class="schemes">
              <button class="scheme active" data-scheme="axion"></button>
              <button class="scheme fire" data-scheme="fire"></button>
              <button class="scheme ice" data-scheme="ice"></button>
              <button class="scheme mono" data-scheme="mono"></button>
            </div>
          </div>
          <label>
            <span>Contraste</span>
            <input id="contrast" type="range" min="40" max="100" value="72">
          </label>
        </div>
      </article>
    </section>

    <footer class="of-footer">
      <span id="footer-status">AXION · esperando feed</span>
      <span id="server-time">Hora del servidor: —</span>
    </footer>
  </main>
</div>
"""

CSS = r"""
:host{
  display:block;width:100%;height:100%;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif
}
*{box-sizing:border-box}
button,select,input{font:inherit}
button{user-select:none}
.axion-orderflow{
  width:100%;height:920px;min-height:760px;overflow:hidden;
  display:grid;grid-template-columns:70px minmax(0,1fr);grid-template-rows:70px minmax(0,1fr);
  color:#dce5f4;background:#030812;border:1px solid #162337;border-radius:12px
}
.axion-orderflow:fullscreen{width:100vw;height:100vh;border:0;border-radius:0}

.of-header{
  grid-column:1/3;display:grid;
  grid-template-columns:190px 190px 140px minmax(250px,1fr) auto auto;
  align-items:center;gap:10px;padding:0 12px;
  border-bottom:1px solid #172437;background:linear-gradient(180deg,#07101a,#040a13)
}
.of-brand{display:flex;align-items:center;gap:10px}
.brand-logo{
  width:38px;height:38px;display:grid;place-items:center;border-radius:9px;
  color:#eefcff;font-size:22px;font-weight:950;
  background:linear-gradient(145deg,#0c2b48,#122060);
  border:1px solid rgba(74,210,235,.42);box-shadow:0 0 18px rgba(55,207,234,.13)
}
.brand-title{font-size:16px;font-weight:900;letter-spacing:.5px}.brand-title span{color:#55d8ed}
.brand-sub{font-size:5.5px;letter-spacing:1.6px;color:#5d6d85;margin-top:2px}
.instrument-box{padding-left:12px;border-left:1px solid #1b293d}.instrument-row{display:flex;align-items:center;gap:5px}
.instrument-row strong{font-size:14px;color:#f2f6fb}.star{color:#d7a84d}
.instrument-box small{display:block;color:#697992;font-size:7px;margin-top:2px}
.quote-box b{display:block;font-size:18px;color:#eef5fc}.quote-box span{display:block;margin-top:3px;font-size:6.5px;color:#8b9ab1}
.timeframes{display:flex;align-items:center;justify-content:center;gap:2px}
.timeframes button{
  min-width:35px;height:31px;padding:0 7px;border:0;border-radius:5px;
  color:#7a89a0;background:transparent;cursor:pointer;font-size:8px
}
.timeframes button:hover{background:#101b2a;color:#dce7f7}
.timeframes button.active{color:#52dbef;background:#0e2034;box-shadow:inset 0 -2px #39d1e9}
.header-tools,.header-actions{display:flex;align-items:center;gap:4px}
.header-tools button{
  height:32px;border:0;background:transparent;color:#7a899f;cursor:pointer;font-size:7px;padding:0 7px
}
.header-tools button:hover{color:#edf6ff;background:#0e1724;border-radius:5px}
.square-btn{
  width:34px;height:32px;border:1px solid #25364d;border-radius:6px;
  background:#08111d;color:#95a5bc;cursor:pointer
}
.square-btn:hover{color:white;border-color:#3d5e7e}.square-btn.small{width:32px;height:29px}

.of-sidebar{
  grid-column:1;grid-row:2;display:flex;flex-direction:column;align-items:center;
  gap:3px;padding:8px 5px;background:#050b14;border-right:1px solid #18263a
}
.nav-btn{
  width:56px;height:54px;border:1px solid transparent;border-radius:8px;
  background:transparent;color:#66758d;display:flex;flex-direction:column;
  align-items:center;justify-content:center;gap:2px;cursor:pointer
}
.nav-btn span{font-size:17px}.nav-btn small{font-size:6.5px}
.nav-btn:hover{background:#0e1724;color:#dce8f7}.nav-btn.active{background:#0a1a2a;color:#4fd8ec;box-shadow:inset 2px 0 #28cff0}
.sidebar-spacer{flex:1}
.sidebar-brand{font-size:10px;line-height:1.05;font-weight:850;letter-spacing:1px;color:#d8e3f1;padding-bottom:8px}
.sidebar-brand span{color:#50d8ed}

.of-main{grid-column:2;grid-row:2;min-width:0;min-height:0;display:grid;grid-template-rows:48px minmax(0,1fr) 166px 24px}
.modebar{
  display:flex;align-items:center;justify-content:space-between;padding:6px 10px;
  border-bottom:1px solid #17263a;background:#060d17
}
.mode-tabs{display:flex;gap:4px;align-items:center}.mode{
  height:32px;padding:0 14px;border:1px solid #1b293d;border-radius:5px;
  background:#07101c;color:#748299;cursor:pointer;font-size:8px
}
.mode.active{color:#eaf9ff;background:linear-gradient(135deg,#145ca9,#4166ff);border-color:#3579ce}
.mode.plus{width:34px;padding:0}
.mode-right{display:flex;align-items:center;gap:8px;color:#718099;font-size:7px}
.mode-right select{
  height:30px;border:1px solid #24354d;border-radius:6px;background:#07111d;color:#c6d2e2;padding:0 8px;font-size:8px
}
.mode-right input{width:105px}

.chart-shell{min-width:0;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 205px;background:#030711}
.chart-wrap{position:relative;min-width:0;min-height:0;border-right:1px solid #1a293d}
#main-canvas{position:absolute;inset:0;width:100%;height:100%}
.profile{position:relative;min-height:0;background:#050b14}
.profile-title{
  height:34px;display:flex;align-items:center;justify-content:space-between;padding:0 10px;
  border-bottom:1px solid #17263a;color:#dce6f4;font-size:8px;font-weight:800
}
.profile-title span{font-size:5px;color:#66758d;letter-spacing:.8px}
#profile-canvas{position:absolute;left:0;right:0;top:34px;bottom:58px;width:100%;height:calc(100% - 92px)}
.profile-stats{
  position:absolute;left:0;right:0;bottom:0;height:58px;display:grid;grid-template-columns:repeat(3,1fr);
  border-top:1px solid #17263a
}
.profile-stats div{display:flex;flex-direction:column;justify-content:center;padding-left:8px;border-right:1px solid #162337}
.profile-stats div:last-child{border-right:0}.profile-stats span{font-size:5.5px;color:#697990}.profile-stats b{font-size:8px;margin-top:3px;color:#dce7f4}

.feed-state{
  position:absolute;left:14px;top:12px;z-index:8;padding:7px 10px;border-radius:7px;
  border:1px solid rgba(46,218,170,.2);background:rgba(4,14,23,.78);backdrop-filter:blur(6px)
}
.feed-state.hidden{display:none}.feed-kicker{font-size:6px;color:#41dba9;font-weight:900;letter-spacing:.9px}
.feed-state strong{display:block;margin-top:2px;font-size:9px}.feed-state span{display:block;margin-top:2px;font-size:6px;color:#718199}
.chart-tags{position:absolute;inset:0;pointer-events:none}.tag{
  position:absolute;display:none;padding:5px 8px;border-radius:6px;font-size:6px;font-weight:800;
  background:rgba(5,15,25,.82);backdrop-filter:blur(4px)
}
.tag.seller{color:#ff6d7c;border:1px solid rgba(255,77,99,.56)}
.tag.buyer{color:#46d9b3;border:1px solid rgba(48,220,170,.52)}
.tag.order{color:#ff835d;border:1px solid rgba(255,98,66,.48)}

.metric-strip{display:grid;grid-template-columns:1fr 1fr 1fr .8fr 1.25fr;background:#07101b;border-top:1px solid #18283c}
.metric-strip article{padding:16px 18px;border-right:1px solid #18283c;min-width:0}.metric-strip article:last-child{border-right:0}
.metric-head{font-size:8px;color:#8b99ad;letter-spacing:.2px}.metric-head.buy{color:#46d8b3}.metric-head.sell{color:#ff6679}.metric-head.delta{color:#a579ff}.metric-head.session{color:#69a7ff}
.metric-main{display:flex;align-items:end;justify-content:space-between;gap:10px;margin-top:12px}.metric-main b{font-size:19px;color:#f2f6fb}.metric-main span{font-size:9px;font-weight:800;color:#38d9a3}
.meter,.delta-track{height:7px;border-radius:999px;background:#172535;margin-top:13px;overflow:hidden}.meter i{display:block;height:100%;width:0;background:#36c7a8}.sell-meter i{background:#e9546b}
.delta-track{position:relative;background:linear-gradient(90deg,#632638 0 49%,#202a32 49% 51%,#174738 51%)}.delta-track i{position:absolute;left:50%;top:0;height:100%;width:0;background:#3bda9e}
.metric-foot{display:flex;justify-content:space-between;color:#66758b;font-size:6.5px;margin-top:5px}
.session-main{justify-content:flex-start}.session-time{font-size:7px;color:#75859b;margin-top:5px}.session-dots{display:flex;gap:4px;margin-top:15px}.session-dots i{width:5px;height:5px;border-radius:50%;background:#24334a}.session-dots i:first-child{background:#386cff}
.visual-body{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:11px}.visual-body span{font-size:6.5px;color:#76869d}.schemes{display:flex;gap:5px;margin-top:6px}.scheme{width:38px;height:29px;border:1px solid #2a3b53;border-radius:5px;background:linear-gradient(135deg,#0b1230,#192c69,#a12a55);cursor:pointer}.scheme.fire{background:linear-gradient(135deg,#231015,#9f381e,#ffc34a)}.scheme.ice{background:linear-gradient(135deg,#06162c,#175895,#50ddec)}.scheme.mono{background:linear-gradient(135deg,#111,#555,#aaa)}.scheme.active{outline:1px solid #4588ff}.visual-body label input{width:100%;margin-top:12px}
.of-footer{display:flex;align-items:center;justify-content:space-between;padding:0 10px;border-top:1px solid #142137;color:#5f6f85;font-size:5.8px;background:#050b14}

@media(max-width:1200px){
  .of-header{grid-template-columns:175px 160px 120px minmax(220px,1fr) auto}
  .header-tools{display:none}.mode:nth-child(n+4){display:none}
  .chart-shell{grid-template-columns:minmax(0,1fr) 175px}
  .metric-strip{grid-template-columns:repeat(3,1fr)}.metric-strip article:nth-child(n+4){display:none}
}
"""

JS = r"""
export default function(component) {
  const {parentElement,data,setTriggerValue,setStateValue}=component;
  const root=parentElement.querySelector('#axion-orderflow');
  if(!root) return;

  let destroyed=false;
  let ws=null;
  let reconnectTimer=null;
  let resizeObserver=null;
  let clockTimer=null;
  let heatTimer=null;

  const symbolSelect=parentElement.querySelector('#symbol-select');
  const tfButtons=[...parentElement.querySelectorAll('[data-tf]')];
  const mainCanvas=parentElement.querySelector('#main-canvas');
  const profileCanvas=parentElement.querySelector('#profile-canvas');
  const ctx=mainCanvas.getContext('2d');
  const pctx=profileCanvas.getContext('2d');

  const feedState=parentElement.querySelector('#feed-state');
  const feedKicker=parentElement.querySelector('#feed-kicker');
  const feedTitle=parentElement.querySelector('#feed-title');
  const feedMessage=parentElement.querySelector('#feed-message');

  let currentSymbol=String(data?.symbol || 'BTCUSDT').toUpperCase();
  let currentTf=String(data?.timeframe || '1m');
  if(currentSymbol!=='BTCUSDT') currentSymbol='XAUUSD';

  let book={bids:new Map(),asks:new Map(),lastUpdateId:0};
  let snapshotReady=false;
  let depthBuffer=[];
  let heatHistory=[];
  const MAX_HEAT_COLS=210;
  const LEVELS_SIDE=80;

  let candles=[];
  let firstPrice=null;
  let recentTrades=[];
  let buyAggVolume=0;
  let sellAggVolume=0;
  let tradedVolumeByBin=new Map();
  let tradedBuyByBin=new Map();
  let tradedSellByBin=new Map();
  let tradeValueSum=0;
  let tradeQtySum=0;

  function dpr(){return Math.max(1,Math.min(2,window.devicePixelRatio||1))}
  function resizeCanvas(canvas){
    const r=canvas.getBoundingClientRect(), q=dpr();
    const w=Math.max(1,Math.floor(r.width*q)),h=Math.max(1,Math.floor(r.height*q));
    if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h}
  }
  function resizeAll(){resizeCanvas(mainCanvas);resizeCanvas(profileCanvas);drawAll()}

  function fmt(v,d=2){
    if(!Number.isFinite(v)) return '—';
    return v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
  }
  function compact(v){
    if(!Number.isFinite(v)) return '—';
    if(Math.abs(v)>=1e9) return (v/1e9).toFixed(2)+'B';
    if(Math.abs(v)>=1e6) return (v/1e6).toFixed(2)+'M';
    if(Math.abs(v)>=1e3) return (v/1e3).toFixed(2)+'K';
    return v.toFixed(2);
  }

  function setFeed(kind,title,message){
    feedState.classList.remove('hidden');
    if(kind==='connected'){
      feedKicker.textContent='● BINANCE · REAL DATA';
      feedTitle.textContent=title;
      feedMessage.textContent=message||'Depth + trades + candles';
      setTimeout(()=>{if(!destroyed)feedState.classList.add('hidden')},2600);
    }else{
      feedKicker.textContent=kind==='unavailable'?'MARKET DEPTH NO DISPONIBLE':'ORDER FLOW';
      feedTitle.textContent=title;
      feedMessage.textContent=message||'';
    }
  }

  function updateIdentity(){
    const btc=currentSymbol==='BTCUSDT';
    symbolSelect.value=currentSymbol;
    parentElement.querySelector('#instrument-name').textContent=btc?'BTC/USDT':'XAU/USD';
    parentElement.querySelector('#instrument-sub').textContent=btc?'Bitcoin / TetherUS · Binance Spot':'Oro / Dólar estadounidense';
  }

  function sessionInfo(){
    const d=new Date(),h=d.getUTCHours();
    let name='Fuera de sesión',range='—';
    if(h>=21||h<6){name='Sídney';range='21:00 - 06:00 UTC'}
    if(h>=0&&h<9){name='Asia';range='00:00 - 09:00 UTC'}
    if(h>=7&&h<16){name='Londres';range='07:00 - 16:00 UTC'}
    if(h>=13&&h<22){name='Nueva York';range='13:00 - 22:00 UTC'}
    parentElement.querySelector('#session-name').textContent=name;
    parentElement.querySelector('#session-time').textContent=range;
    const hh=String(d.getUTCHours()).padStart(2,'0'),mm=String(d.getUTCMinutes()).padStart(2,'0'),ss=String(d.getUTCSeconds()).padStart(2,'0');
    parentElement.querySelector('#server-time').textContent=`Hora del servidor: ${hh}:${mm}:${ss} UTC`;
  }

  function sortedBook(){
    return {
      bids:[...book.bids.entries()].sort((a,b)=>b[0]-a[0]),
      asks:[...book.asks.entries()].sort((a,b)=>a[0]-b[0])
    }
  }
  function midPrice(){
    const {bids,asks}=sortedBook();
    return bids.length&&asks.length?(bids[0][0]+asks[0][0])/2:null;
  }

  function normalizeLevels(raw){
    return (Array.isArray(raw)?raw:[]).map(x=>[Number(x[0]),Number(x[1])]).filter(x=>Number.isFinite(x[0])&&Number.isFinite(x[1])&&x[0]>0&&x[1]>=0)
  }
  function applySide(map,levels){
    for(const [p,q] of normalizeLevels(levels)){if(q===0)map.delete(p);else map.set(p,q)}
  }
  function applyDepth(evt){applySide(book.bids,evt.b);applySide(book.asks,evt.a);book.lastUpdateId=Number(evt.u||book.lastUpdateId)}

  async function fetchSnapshot(){
    const res=await fetch('https://data-api.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=1000',{cache:'no-store'});
    if(!res.ok)throw new Error('Depth HTTP '+res.status);
    const snap=await res.json();
    const bids=new Map(),asks=new Map();
    for(const [p,q] of normalizeLevels(snap.bids))if(q>0)bids.set(p,q);
    for(const [p,q] of normalizeLevels(snap.asks))if(q>0)asks.set(p,q);
    book={bids,asks,lastUpdateId:Number(snap.lastUpdateId||0)};
    depthBuffer=depthBuffer.filter(e=>Number(e.u)>book.lastUpdateId);
    let start=-1;
    for(let i=0;i<depthBuffer.length;i++){
      const e=depthBuffer[i];
      if(Number(e.U)<=book.lastUpdateId+1&&Number(e.u)>=book.lastUpdateId+1){start=i;break}
    }
    if(start>=0)for(let i=start;i<depthBuffer.length;i++)if(Number(depthBuffer[i].u)>book.lastUpdateId)applyDepth(depthBuffer[i]);
    depthBuffer=[];snapshotReady=true;
  }

  async function fetchCandles(){
    const interval=currentTf==='1H'?'1h':currentTf==='4H'?'4h':currentTf==='1D'?'1d':currentTf;
    const res=await fetch(`https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=${interval}&limit=160`,{cache:'no-store'});
    if(!res.ok)throw new Error('Klines HTTP '+res.status);
    const rows=await res.json();
    candles=rows.map(r=>({t:Number(r[0]),o:Number(r[1]),h:Number(r[2]),l:Number(r[3]),c:Number(r[4]),v:Number(r[5])}));
    if(candles.length&&!firstPrice)firstPrice=candles[0].o;
  }

  async function fetchAggTrades(){
    const res=await fetch('https://data-api.binance.vision/api/v3/aggTrades?symbol=BTCUSDT&limit=1000',{cache:'no-store'});
    if(!res.ok)throw new Error('aggTrades HTTP '+res.status);
    const rows=await res.json();
    resetTradeStats();
    for(const r of rows)ingestTrade({p:r.p,q:r.q,m:r.m,T:r.T},false);
  }

  function resetTradeStats(){
    recentTrades=[];buyAggVolume=0;sellAggVolume=0;tradedVolumeByBin=new Map();tradedBuyByBin=new Map();tradedSellByBin=new Map();tradeValueSum=0;tradeQtySum=0
  }

  function tradeBin(price){
    const step=Math.max(1,Math.round(price*.00005));
    return Math.round(price/step)*step;
  }
  function ingestTrade(t,redraw=true){
    const p=Number(t.p),q=Number(t.q);if(!Number.isFinite(p)||!Number.isFinite(q))return;
    const buyerMaker=Boolean(t.m);
    const aggressiveBuy=!buyerMaker;
    if(aggressiveBuy)buyAggVolume+=q;else sellAggVolume+=q;
    tradeValueSum+=p*q;tradeQtySum+=q;
    const bin=tradeBin(p);
    tradedVolumeByBin.set(bin,(tradedVolumeByBin.get(bin)||0)+q);
    if(aggressiveBuy)tradedBuyByBin.set(bin,(tradedBuyByBin.get(bin)||0)+q);
    else tradedSellByBin.set(bin,(tradedSellByBin.get(bin)||0)+q);
    recentTrades.push({p,q,buy:aggressiveBuy,t:Number(t.T||Date.now())});
    if(recentTrades.length>5000)recentTrades.splice(0,recentTrades.length-5000);
    if(redraw)updateStats();
  }

  function updateKline(k){
    const c={t:Number(k.t),o:Number(k.o),h:Number(k.h),l:Number(k.l),c:Number(k.c),v:Number(k.v)};
    const i=candles.findIndex(x=>x.t===c.t);
    if(i>=0)candles[i]=c;else{candles.push(c);if(candles.length>180)candles.shift()}
  }

  function captureHeat(){
    if(!snapshotReady)return;
    const {bids,asks}=sortedBook();const mid=midPrice();if(mid==null)return;
    heatHistory.push({mid,bids:bids.slice(0,LEVELS_SIDE),asks:asks.slice(0,LEVELS_SIDE),t:Date.now()});
    if(heatHistory.length>MAX_HEAT_COLS)heatHistory.shift();
    updateStats();drawAll();
  }

  function updateStats(){
    const {bids,asks}=sortedBook(),mid=midPrice();
    if(mid!=null){
      parentElement.querySelector('#header-price').textContent=fmt(mid,2);
      if(!firstPrice)firstPrice=mid;
      const pct=(mid-firstPrice)/firstPrice*100;
      const ch=parentElement.querySelector('#header-change');
      ch.textContent=`${pct>=0?'+':''}${pct.toFixed(2)}%`;
      ch.style.color=pct>=0?'#36d9a0':'#ff6075';
    }
    const bq=bids.slice(0,LEVELS_SIDE).reduce((s,x)=>s+x[1],0),aq=asks.slice(0,LEVELS_SIDE).reduce((s,x)=>s+x[1],0),tot=bq+aq;
    parentElement.querySelector('#buy-liquidity').textContent=compact(bq)+' BTC';
    parentElement.querySelector('#sell-liquidity').textContent=compact(aq)+' BTC';
    parentElement.querySelector('#buy-pct').textContent=tot?Math.round(bq/tot*100)+'%':'—';
    parentElement.querySelector('#sell-pct').textContent=tot?Math.round(aq/tot*100)+'%':'—';
    parentElement.querySelector('#buy-meter').style.width=tot?`${bq/tot*100}%`:'0%';
    parentElement.querySelector('#sell-meter').style.width=tot?`${aq/tot*100}%`:'0%';

    const delta=buyAggVolume-sellAggVolume,tradeTot=buyAggVolume+sellAggVolume;
    parentElement.querySelector('#delta-value').textContent=(delta>=0?'+':'')+compact(delta)+' BTC';
    parentElement.querySelector('#delta-pct').textContent=tradeTot?`${delta>=0?'+':''}${(delta/tradeTot*100).toFixed(1)}%`:'—';
    const dm=parentElement.querySelector('#delta-meter');
    const dp=tradeTot?Math.min(50,Math.abs(delta/tradeTot)*50):0;
    dm.style.width=dp+'%';dm.style.left=delta>=0?'50%':(50-dp)+'%';dm.style.background=delta>=0?'#38d69c':'#ec536b';

    const vwap=tradeQtySum?tradeValueSum/tradeQtySum:null;
    parentElement.querySelector('#vwap-value').textContent=vwap?fmt(vwap,2):'—';
    const bins=[...tradedVolumeByBin.entries()].sort((a,b)=>b[1]-a[1]);
    parentElement.querySelector('#poc-value').textContent=bins.length?fmt(bins[0][0],2):'—';
    if(bids.length&&asks.length)parentElement.querySelector('#spread-value').textContent=fmt(asks[0][0]-bids[0][0],2);
    parentElement.querySelector('#footer-status').textContent=snapshotReady?'● Binance Spot · Depth + Trades + Klines':'AXION · sincronizando';
  }

  function heatColor(norm,ask){
    const n=Math.max(0,Math.min(1,norm));
    if(n>.82)return `rgba(255,180,35,${.30+n*.65})`;
    if(n>.58)return ask?`rgba(255,70,88,${.18+n*.62})`:`rgba(46,220,175,${.16+n*.55})`;
    if(n>.30)return `rgba(141,54,196,${.10+n*.45})`;
    return `rgba(32,47,118,${.05+n*.25})`;
  }

  function drawAll(){
    resizeCanvas(mainCanvas);resizeCanvas(profileCanvas);
    const w=mainCanvas.width,h=mainCanvas.height,q=dpr();
    ctx.clearRect(0,0,w,h);
    ctx.fillStyle='#030711';ctx.fillRect(0,0,w,h);

    let priceSamples=[];
    for(const c of candles){priceSamples.push(c.h,c.l)}
    if(heatHistory.length){
      const last=heatHistory[heatHistory.length-1];
      last.bids.forEach(x=>priceSamples.push(x[0]));last.asks.forEach(x=>priceSamples.push(x[0]))
    }
    if(!priceSamples.length)return;
    let minP=Math.min(...priceSamples),maxP=Math.max(...priceSamples),pad=(maxP-minP)*.06||1;minP-=pad;maxP+=pad;
    const yOf=p=>h-((p-minP)/(maxP-minP))*h;

    // grid
    ctx.strokeStyle='rgba(51,70,103,.22)';ctx.lineWidth=1*q;
    for(let i=1;i<9;i++){let y=h*i/9;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}
    for(let i=1;i<12;i++){let x=w*i/12;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}

    // heatmap
    if(heatHistory.length){
      const quantities=[];
      for(const col of heatHistory){col.bids.forEach(x=>quantities.push(x[1]));col.asks.forEach(x=>quantities.push(x[1]))}
      quantities.sort((a,b)=>a-b);
      const scale=quantities.length?quantities[Math.floor((quantities.length-1)*.96)]||1:1;
      const cw=w/Math.max(MAX_HEAT_COLS,heatHistory.length),offset=w-cw*heatHistory.length;
      heatHistory.forEach((col,i)=>{
        const x=offset+i*cw;
        for(const [p,qty] of col.bids){if(p<minP||p>maxP)continue;ctx.fillStyle=heatColor(Math.min(1,qty/scale),false);ctx.fillRect(x,yOf(p)-2*q,cw+1*q,4*q)}
        for(const [p,qty] of col.asks){if(p<minP||p>maxP)continue;ctx.fillStyle=heatColor(Math.min(1,qty/scale),true);ctx.fillRect(x,yOf(p)-2*q,cw+1*q,4*q)}
      });
    }

    // VWAP
    if(tradeQtySum){
      const vwap=tradeValueSum/tradeQtySum,y=yOf(vwap);
      ctx.strokeStyle='rgba(255,177,42,.9)';ctx.lineWidth=1.25*q;ctx.setLineDash([6*q,5*q]);ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();ctx.setLineDash([])
    }

    // candles
    if(candles.length){
      const visible=candles.slice(-110),cw=w/visible.length,body=Math.max(2*q,cw*.52);
      visible.forEach((c,i)=>{
        const x=i*cw+cw*.5,yo=yOf(c.o),yc=yOf(c.c),yh=yOf(c.h),yl=yOf(c.l),up=c.c>=c.o;
        ctx.strokeStyle=up?'rgba(47,218,180,.92)':'rgba(244,80,99,.92)';ctx.fillStyle=ctx.strokeStyle;ctx.lineWidth=1*q;
        ctx.beginPath();ctx.moveTo(x,yh);ctx.lineTo(x,yl);ctx.stroke();
        ctx.fillRect(x-body/2,Math.min(yo,yc),body,Math.max(1*q,Math.abs(yc-yo)))
      })
    }

    // current price
    const mid=midPrice();
    if(mid!=null){
      const y=yOf(mid);ctx.strokeStyle='rgba(238,244,252,.72)';ctx.lineWidth=1*q;ctx.setLineDash([4*q,4*q]);ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();ctx.setLineDash([]);
      ctx.fillStyle='#e9f0f8';ctx.font=`${8*q}px Inter`;ctx.fillText(fmt(mid,2),w-58*q,Math.max(10*q,y-4*q))
    }

    // labels from strongest real current book levels
    const {bids,asks}=sortedBook();
    const strongBid=bids.slice(0,LEVELS_SIDE).sort((a,b)=>b[1]-a[1])[0];
    const strongAsk=asks.slice(0,LEVELS_SIDE).sort((a,b)=>b[1]-a[1])[0];
    positionTag(parentElement.querySelector('#buyer-zone'),strongBid?yOf(strongBid[0])/q:null,'left');
    positionTag(parentElement.querySelector('#seller-zone'),strongAsk?yOf(strongAsk[0])/q:null,'left');
    positionTag(parentElement.querySelector('#order-block'),strongAsk?Math.max(40,yOf(strongAsk[0])/q-55):null,'center');

    drawProfile(minP,maxP);
  }

  function positionTag(el,y,where){
    if(!el||y==null||!Number.isFinite(y)){if(el)el.style.display='none';return}
    el.style.display='block';el.style.top=`${Math.max(18,Math.min(mainCanvas.clientHeight-38,y))}px`;
    if(where==='center'){el.style.left='58%'}else{el.style.left='7%'}
  }

  function drawProfile(minP,maxP){
    const w=profileCanvas.width,h=profileCanvas.height,q=dpr();pctx.clearRect(0,0,w,h);pctx.fillStyle='#050b14';pctx.fillRect(0,0,w,h);
    const bins=[...tradedVolumeByBin.entries()].filter(([p])=>p>=minP&&p<=maxP);
    if(!bins.length)return;
    const maxV=Math.max(...bins.map(x=>x[1]),1),yOf=p=>h-((p-minP)/(maxP-minP))*h;
    for(const [p,v] of bins){
      const buy=tradedBuyByBin.get(p)||0,sell=tradedSellByBin.get(p)||0,total=Math.max(v,1e-9),width=(v/maxV)*w*.82,y=yOf(p),bh=Math.max(2*q,h/90);
      const left=w-width;
      pctx.fillStyle=`rgba(108,70,188,${.22+.55*(v/maxV)})`;pctx.fillRect(left,y-bh/2,width,bh);
      if(buy>sell){pctx.fillStyle='rgba(44,207,172,.72)';pctx.fillRect(w-width*(buy/total),y-bh/2,width*(buy/total),bh)}
      else{pctx.fillStyle='rgba(230,98,55,.66)';pctx.fillRect(w-width*(sell/total),y-bh/2,width*(sell/total),bh)}
    }
    const poc=[...tradedVolumeByBin.entries()].sort((a,b)=>b[1]-a[1])[0];
    if(poc){
      const y=yOf(poc[0]);pctx.strokeStyle='rgba(255,176,39,.92)';pctx.lineWidth=1*q;pctx.setLineDash([5*q,4*q]);pctx.beginPath();pctx.moveTo(0,y);pctx.lineTo(w,y);pctx.stroke();pctx.setLineDash([]);
      pctx.fillStyle='#f1ad39';pctx.font=`${7*q}px Inter`;pctx.fillText('POC',6*q,Math.max(10*q,y-4*q))
    }
  }

  function connect(){
    cleanupFeed();
    updateIdentity();
    if(currentSymbol!=='BTCUSDT'){
      setFeed('unavailable','XAU/USD: profundidad pendiente','Para oro conectaremos GC/MGC. AXION no mostrará liquidez sintética.');
      parentElement.querySelector('#footer-status').textContent='XAU/USD · Market Depth pendiente';
      drawAll();return;
    }
    setFeed('connecting','Conectando Binance Spot...','Depth + aggTrades + Klines reales');
    Promise.all([fetchSnapshot(),fetchCandles(),fetchAggTrades()]).then(()=>{
      setFeed('connected','BTC/USDT · feed real conectado','Depth + trades + candles');
      updateStats();drawAll()
    }).catch(err=>{
      console.error(err);setFeed('error','No se pudo sincronizar Binance',String(err?.message||err))
    });

    const streams='btcusdt@depth@100ms/btcusdt@aggTrade/btcusdt@kline_1m';
    ws=new WebSocket(`wss://stream.binance.com:9443/stream?streams=${streams}`);
    ws.onmessage=e=>{
      if(destroyed)return;
      let msg;try{msg=JSON.parse(e.data)}catch(_){return}
      const evt=msg.data||msg;
      if(evt.e==='depthUpdate'){
        if(!snapshotReady){depthBuffer.push(evt);if(depthBuffer.length>5000)depthBuffer.shift();return}
        const expected=book.lastUpdateId+1,U=Number(evt.U),u=Number(evt.u);
        if(u<expected)return;
        if(U>expected){snapshotReady=false;heatHistory=[];fetchSnapshot().catch(()=>scheduleReconnect());return}
        applyDepth(evt)
      }else if(evt.e==='aggTrade'){
        ingestTrade(evt,true)
      }else if(evt.e==='kline'){
        updateKline(evt.k);drawAll()
      }
    };
    ws.onerror=()=>setFeed('error','WebSocket Binance interrumpido','AXION intentará reconectar.');
    ws.onclose=()=>{if(!destroyed&&currentSymbol==='BTCUSDT')scheduleReconnect()}
    heatTimer=setInterval(captureHeat,650);
  }

  function scheduleReconnect(){
    if(reconnectTimer)clearTimeout(reconnectTimer);
    reconnectTimer=setTimeout(connect,1800)
  }
  function cleanupFeed(){
    if(ws){try{ws.onclose=null;ws.close()}catch(_){}ws=null}
    if(reconnectTimer){clearTimeout(reconnectTimer);reconnectTimer=null}
    if(heatTimer){clearInterval(heatTimer);heatTimer=null}
    book={bids:new Map(),asks:new Map(),lastUpdateId:0};snapshotReady=false;depthBuffer=[];heatHistory=[];
    candles=[];resetTradeStats();firstPrice=null
  }

  symbolSelect.onchange=()=>{currentSymbol=symbolSelect.value;setTriggerValue('symbol',currentSymbol);connect()};
  tfButtons.forEach(btn=>btn.onclick=()=>{
    tfButtons.forEach(x=>x.classList.remove('active'));btn.classList.add('active');currentTf=btn.dataset.tf;
    setTriggerValue('timeframe',currentTf);
    if(currentSymbol==='BTCUSDT')fetchCandles().then(drawAll)
  });
  parentElement.querySelector('#intensity').oninput=e=>{mainCanvas.style.opacity=String(Math.max(.35,Number(e.target.value)/100));setStateValue('heatmap_intensity',Number(e.target.value))}
  parentElement.querySelector('#contrast').oninput=e=>{const v=Math.max(.75,Math.min(1.35,Number(e.target.value)/72));parentElement.querySelector('.chart-shell').style.filter=`contrast(${v})`;setStateValue('heatmap_contrast',Number(e.target.value))}
  parentElement.querySelectorAll('.mode').forEach(btn=>btn.onclick=()=>{parentElement.querySelectorAll('.mode').forEach(x=>x.classList.remove('active'));btn.classList.add('active')})
  parentElement.querySelectorAll('.scheme').forEach(btn=>btn.onclick=()=>{parentElement.querySelectorAll('.scheme').forEach(x=>x.classList.remove('active'));btn.classList.add('active')})
  parentElement.querySelector('#fullscreen-btn').onclick=async()=>{try{if(!document.fullscreenElement)await root.requestFullscreen();else await document.exitFullscreen()}catch(_){}}
  parentElement.querySelector('#stage-fullscreen').onclick=parentElement.querySelector('#fullscreen-btn').onclick;

  updateIdentity();tfButtons.forEach(b=>b.classList.toggle('active',b.dataset.tf===currentTf));
  sessionInfo();clockTimer=setInterval(sessionInfo,1000);
  if(typeof ResizeObserver!=='undefined'){resizeObserver=new ResizeObserver(resizeAll);resizeObserver.observe(parentElement.querySelector('.chart-shell'))}
  resizeAll();connect();

  return()=>{destroyed=true;cleanupFeed();if(clockTimer)clearInterval(clockTimer);resizeObserver?.disconnect()}
}
"""

_component = st.components.v2.component(
    "axion_live_heatmap_v6_mockup",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=True,
)


def render_axion_live_heatmap(
    *,
    symbol: str = "BTCUSDT",
    timeframe: str = "1m",
    key: str = "axion_live_heatmap",
    height: int = 920,
):
    return _component(
        data={"symbol": symbol, "timeframe": timeframe},
        default=None,
        key=key,
        width="stretch",
        height=height,
    )
