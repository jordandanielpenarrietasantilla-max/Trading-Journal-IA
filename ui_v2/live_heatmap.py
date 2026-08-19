from __future__ import annotations

import streamlit as st

HTML = r"""
<div class="axion-orderflow" id="axion-orderflow">
  <header class="of-header">
    <div class="of-brand">
      <div class="brand-logo">A</div>
      <div>
        <div class="brand-title">AXION <span>PRIME</span></div>
        <div class="brand-sub">RECORDED MARKET DEPTH · ORDER FLOW</div>
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


  <main class="of-main">
    <section class="modebar">
      <div class="mode-tabs">
        <button class="mode active" type="button">Heatmap Liquidity Matrix</button>
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

        <div class="price-scale" id="price-scale">
          <span>—</span><span>—</span><span>—</span><span>—</span><span>—</span><span>—</span>
        </div>

        <div class="chart-tags">
          <span class="tag seller" id="seller-zone">ZONA DE LIQUIDEZ VENDEDORA</span>
          <span class="tag buyer" id="buyer-zone">ZONA DE LIQUIDEZ COMPRADORA</span>
          <span class="tag seller" id="secondary-seller-zone">LIQUIDEZ DESTACADA</span>
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
  width:100%;height:880px;min-height:720px;overflow:hidden;
  display:grid;grid-template-columns:minmax(0,1fr);grid-template-rows:64px minmax(0,1fr);
  color:#dce5f4;background:#030812;border:1px solid #162337;border-radius:12px
}
.axion-orderflow:fullscreen{width:100vw;height:100vh;border:0;border-radius:0}

.of-header{
  grid-column:1;display:grid;
  grid-template-columns:185px 185px 130px minmax(260px,1fr) auto auto;
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


.of-main{grid-column:1;grid-row:2;min-width:0;min-height:0;display:grid;grid-template-rows:46px minmax(0,1fr) 150px 22px}
.modebar{
  display:flex;align-items:center;justify-content:space-between;padding:6px 10px;
  border-bottom:1px solid #17263a;background:#060d17
}
.mode-tabs{display:flex;gap:4px;align-items:center}.mode{
  height:30px;padding:0 12px;border:1px solid #1b293d;border-radius:5px;
  background:#07101c;color:#748299;cursor:pointer;font-size:8px
}
.mode.active{color:#eaf9ff;background:linear-gradient(135deg,#145ca9,#4166ff);border-color:#3579ce}
.mode.plus{width:34px;padding:0}
.mode-right{display:flex;align-items:center;gap:8px;color:#718099;font-size:7px}
.mode-right select{
  height:30px;border:1px solid #24354d;border-radius:6px;background:#07111d;color:#c6d2e2;padding:0 8px;font-size:8px
}
.mode-right input{width:105px}

.chart-shell{min-width:0;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 190px;background:#030711}
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


.price-scale{
  position:absolute;right:6px;top:10px;bottom:10px;z-index:7;
  display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end;
  pointer-events:none;color:#8596af;font-size:7px;font-variant-numeric:tabular-nums
}
.price-scale span{
  padding:2px 4px;border-radius:4px;background:rgba(4,10,18,.58)
}

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
  const MAX_HEAT_COLS=900;        // ~15 min at 1 snapshot/sec
  const LEVELS_SIDE=180;
  const STORAGE_KEY='axion_btcusdt_depth_v11';
  const STORAGE_MAX_AGE=6*60*60*1000; // keep up to 6h of REAL captured depth
  let recordingStartedAt=null;
  let lastPersistAt=0;

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

  function binanceInterval(){
    if(currentTf==='1H') return '1h';
    if(currentTf==='4H') return '4h';
    if(currentTf==='1D') return '1d';
    return currentTf;
  }


  async function fetchCandles(){
    const interval=binanceInterval();
    const res=await fetch(`https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=${interval}&limit=500`,{cache:'no-store'});
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
    if(i>=0)candles[i]=c;else{candles.push(c);if(candles.length>600)candles.shift()}
  }

  function loadRecordedDepth(){
    try{
      const raw=localStorage.getItem(STORAGE_KEY);
      if(!raw) return;
      const payload=JSON.parse(raw);
      if(!payload || !Array.isArray(payload.history)) return;

      const cutoff=Date.now()-STORAGE_MAX_AGE;
      heatHistory=payload.history
        .filter(col=>Number(col?.t)>=cutoff && Array.isArray(col?.buckets))
        .slice(-MAX_HEAT_COLS);

      if(heatHistory.length){
        recordingStartedAt=heatHistory[0].t;
      }
    }catch(err){
      console.warn('AXION depth restore',err);
    }
  }

  function persistRecordedDepth(force=false){
    if(currentSymbol!=='BTCUSDT' || !heatHistory.length) return;
    const now=Date.now();
    if(!force && now-lastPersistAt<5000) return;
    lastPersistAt=now;

    try{
      const cutoff=now-STORAGE_MAX_AGE;
      const history=heatHistory
        .filter(col=>Number(col?.t)>=cutoff)
        .slice(-MAX_HEAT_COLS);

      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          version:11,
          symbol:'BTCUSDT',
          savedAt:now,
          history
        })
      );
    }catch(err){
      console.warn('AXION depth persist',err);
    }
  }

  function recordedWindow(){
    if(!heatHistory.length) return null;
    return {
      start:Number(heatHistory[0].t),
      end:Number(heatHistory[heatHistory.length-1].t)
    };
  }

  function bucketStepFor(price){
    if(!Number.isFinite(price) || price<=0) return 1;
    if(price>=50000) return 5;     // BTC around current range
    if(price>=10000) return 2;
    if(price>=1000) return .5;
    if(price>=100) return .1;
    return .01;
  }

  function bucketPrice(price,step){
    return Math.round(price/step)*step;
  }

  function aggregateBookToBuckets(){
    const {bids,asks}=sortedBook();
    const mid=midPrice();
    if(mid==null) return {mid:null,step:1,buckets:[]};

    const step=bucketStepFor(mid);
    const map=new Map();

    const add=(side,levels)=>{
      for(const [price,qty] of levels.slice(0,LEVELS_SIDE)){
        if(!Number.isFinite(price)||!Number.isFinite(qty)||qty<=0) continue;
        const p=bucketPrice(price,step);
        let row=map.get(p);
        if(!row){
          row={p,bid:0,ask:0,total:0};
          map.set(p,row);
        }
        row[side]+=qty;
        row.total+=qty;
      }
    };

    add('bid',bids);
    add('ask',asks);

    return {
      mid,
      step,
      buckets:[...map.values()].sort((a,b)=>a.p-b.p)
    };
  }

  function percentile(sorted,p){
    if(!sorted.length) return 0;
    const idx=Math.max(0,Math.min(sorted.length-1,Math.floor((sorted.length-1)*p)));
    return sorted[idx];
  }

  function heatPalette(norm,sideBias=0){
    const n=Math.max(0,Math.min(1,norm));

    // Bookmap-like dark -> purple -> red -> orange -> yellow.
    if(n<.16){
      return `rgba(18,23,64,${.18+n*.7})`;
    }
    if(n<.34){
      const a=.18+n*.85;
      return sideBias<0
        ? `rgba(29,82,128,${a})`
        : sideBias>0
          ? `rgba(75,35,118,${a})`
          : `rgba(58,37,117,${a})`;
    }
    if(n<.56){
      return `rgba(133,42,139,${.22+n*.85})`;
    }
    if(n<.76){
      return `rgba(220,59,78,${.28+n*.82})`;
    }
    if(n<.91){
      return `rgba(255,112,39,${.42+n*.60})`;
    }
    return `rgba(255,209,48,${.62+n*.36})`;
  }

  function normalizedBucketIntensity(value,q50,q85,q97){
    if(!(value>0)) return 0;

    // Log transform stops one whale order from flattening everything else.
    const lv=Math.log1p(value);
    const l50=Math.log1p(Math.max(q50,1e-9));
    const l85=Math.log1p(Math.max(q85,q50,1e-9));
    const l97=Math.log1p(Math.max(q97,q85,1e-9));

    if(lv<=l50){
      return .08 + .28*(lv/Math.max(l50,1e-9));
    }
    if(lv<=l85){
      return .36 + .28*((lv-l50)/Math.max(l85-l50,1e-9));
    }
    if(lv<=l97){
      return .64 + .24*((lv-l85)/Math.max(l97-l85,1e-9));
    }
    return Math.min(1,.88 + .12*((lv-l97)/Math.max(l97*.18,1e-9)));
  }

  function captureHeat(){
    if(!snapshotReady)return;
    const snap=aggregateBookToBuckets();
    if(snap.mid==null || !snap.buckets.length)return;

    heatHistory.push({
      t:Date.now(),
      mid:snap.mid,
      step:snap.step,
      buckets:snap.buckets
    });

    if(heatHistory.length>MAX_HEAT_COLS)heatHistory.shift();
    if(recordingStartedAt==null && heatHistory.length){
      recordingStartedAt=heatHistory[0].t;
    }
    persistRecordedDepth();
    updateStats();
    drawAll();
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
    {
      const win=recordedWindow();
      const seconds=win?Math.max(0,Math.round((win.end-win.start)/1000)):0;
      const mins=Math.floor(seconds/60);
      const secs=seconds%60;
      parentElement.querySelector('#footer-status').textContent=snapshotReady
        ? `● Binance Spot · ${currentTf} · DEPTH REC ${mins}m ${String(secs).padStart(2,'0')}s`
        : 'AXION · sincronizando';
    }
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

    const mid=midPrice();
    if(mid==null && !candles.length)return;

    // Prepare the current book and the candle slice that actually overlaps
    // the REAL depth-history window. These variables must exist before the
    // viewport is calculated.
    const {bids,asks}=sortedBook();

    const depthWindow=recordedWindow();
    let recent=[];

    if(depthWindow){
      const intervalMs={
        '1m':60_000,
        '5m':300_000,
        '15m':900_000,
        '30m':1_800_000,
        '1H':3_600_000,
        '4H':14_400_000,
        '1D':86_400_000
      }[currentTf] || 60_000;

      recent=candles.filter(c=>
        Number.isFinite(c.t) &&
        c.t + intervalMs >= depthWindow.start &&
        c.t <= depthWindow.end + intervalMs
      );
    }

    // At startup, before enough depth history exists, show only the current
    // live candle. Never inject older unmatched candles into the order-flow view.
    if(!recent.length && candles.length){
      recent=[candles[candles.length-1]];
    }

    /*
      FINAL ORDER-FLOW VIEWPORT:
      Use the actual price range traversed while depth was recorded.
      We no longer try to fit older candles that have no corresponding
      historical market-depth matrix.
    */
    const center=mid ?? (recent.length ? recent[recent.length-1].c : null);
    if(center==null || !Number.isFinite(center)) return;

    let depthSamples=[];
    for(const col of heatHistory){
      if(!Array.isArray(col.buckets)) continue;
      for(const row of col.buckets){
        if(Number.isFinite(row.p)) depthSamples.push(row.p);
      }
      if(Number.isFinite(col.mid)) depthSamples.push(col.mid);
    }

    // Current book is included so viewport follows the live market immediately.
    bids.slice(0,LEVELS_SIDE).forEach(x=>depthSamples.push(x[0]));
    asks.slice(0,LEVELS_SIDE).forEach(x=>depthSamples.push(x[0]));

    if(!depthSamples.length){
      depthSamples=[center*(1-.002),center*(1+.002)];
    }

    let minP=Math.min(...depthSamples);
    let maxP=Math.max(...depthSamples);

    // Include ONLY synchronized candles.
    recent.forEach(c=>{
      if(Number.isFinite(c.l)) minP=Math.min(minP,c.l);
      if(Number.isFinite(c.h)) maxP=Math.max(maxP,c.h);
    });

    const rawRange=Math.max(maxP-minP,center*.0015);
    const pad=rawRange*.10;

    minP-=pad;
    maxP+=pad;

    const yOf=p=>h-((p-minP)/(maxP-minP))*h;

    // grid
    ctx.strokeStyle='rgba(43,62,94,.24)';
    ctx.lineWidth=1*q;
    for(let i=1;i<9;i++){
      const y=h*i/9;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();
    }
    for(let i=1;i<14;i++){
      const x=w*i/14;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();
    }

    // REAL historical liquidity matrix: price × captured timestamp.
    if(heatHistory.length){
      const visibleHistory=heatHistory.slice(-MAX_HEAT_COLS);

      const totals=[];
      for(const col of visibleHistory){
        for(const row of col.buckets){
          if(row.p>=minP && row.p<=maxP && row.total>0){
            totals.push(row.total);
          }
        }
      }
      totals.sort((a,b)=>a-b);

      const q50=percentile(totals,.50)||1;
      const q85=percentile(totals,.85)||q50;
      const q97=percentile(totals,.97)||q85;

      const t0=Number(visibleHistory[0].t);
      const t1=Math.max(t0+1000,Number(visibleHistory[visibleHistory.length-1].t));
      const xOfTime=t=>((Number(t)-t0)/(t1-t0))*w;

      visibleHistory.forEach((col,i)=>{
        const x=xOfTime(col.t);
        const nextT=i<visibleHistory.length-1
          ? Number(visibleHistory[i+1].t)
          : Number(col.t)+1000;

        const nextX=xOfTime(Math.min(nextT,t1));
        const cw=Math.max(1.5*q,nextX-x+1*q);

        const step=col.step||bucketStepFor(col.mid);
        const bucketPixelH=Math.max(
          2.3*q,
          Math.abs(yOf(center)-yOf(center+step))
        );

        for(const row of col.buckets){
          if(row.p<minP || row.p>maxP || row.total<=0) continue;

          const y=yOf(row.p);
          const norm=normalizedBucketIntensity(row.total,q50,q85,q97);
          const bias=(row.bid-row.ask)/Math.max(row.total,1e-9);

          ctx.fillStyle=heatPalette(norm,bias);
          ctx.fillRect(
            x,
            y-bucketPixelH*.50,
            cw,
            Math.max(2.4*q,bucketPixelH*.98)
          );
        }
      });
    }

    // VWAP
    if(tradeQtySum){
      const vwap=tradeValueSum/tradeQtySum;
      if(vwap>=minP&&vwap<=maxP){
        const y=yOf(vwap);
        ctx.strokeStyle='rgba(245,167,38,.92)';
        ctx.lineWidth=1.15*q;
        ctx.setLineDash([7*q,5*q]);
        ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();
        ctx.setLineDash([]);
        ctx.fillStyle='#f0ad3d';ctx.font=`${7*q}px Inter`;
        ctx.fillText('VWAP',8*q,Math.max(11*q,y-4*q));
      }
    }

    // POC from actual recent traded volume.
    const pocRow=[...tradedVolumeByBin.entries()].sort((a,b)=>b[1]-a[1])[0];
    if(pocRow && pocRow[0]>=minP && pocRow[0]<=maxP){
      const py=yOf(pocRow[0]);
      ctx.strokeStyle='rgba(246,177,48,.95)';
      ctx.lineWidth=1.1*q;
      ctx.setLineDash([8*q,5*q]);
      ctx.beginPath();ctx.moveTo(0,py);ctx.lineTo(w,py);ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle='#f2b33c';ctx.font=`${7*q}px Inter`;
      ctx.fillText('POC',44*q,Math.max(11*q,py-4*q));
    }

    // Candles share EXACTLY the same Y-axis as the heatmap.
    // Candles completely outside the live viewport are skipped rather than
    // stretched into giant vertical bars.
    if(recent.length){
      const window=recordedWindow();
      const t0=window ? window.start : recent[0].t;
      const t1=window ? Math.max(window.end,t0+1000) : Math.max(recent[recent.length-1].t,t0+1000);
      const xOfTime=t=>((Number(t)-t0)/(t1-t0))*w;
      const nominalWidth=Math.max(4*q,w/Math.max(30,recent.length));
      const body=Math.max(2.0*q,nominalWidth*.48);

      recent.forEach((c,i)=>{
        if(![c.o,c.h,c.l,c.c].every(Number.isFinite)) return;

        // Entire candle outside viewport -> do not distort the chart.
        if(c.h<minP || c.l>maxP) return;

        const x=Math.max(0,Math.min(w,xOfTime(c.t)));

        // Clip values to viewport for partially visible candles.
        const clippedH=Math.min(maxP,Math.max(minP,c.h));
        const clippedL=Math.min(maxP,Math.max(minP,c.l));
        const clippedO=Math.min(maxP,Math.max(minP,c.o));
        const clippedC=Math.min(maxP,Math.max(minP,c.c));

        const yo=yOf(clippedO);
        const yc=yOf(clippedC);
        const yh=yOf(clippedH);
        const yl=yOf(clippedL);

        const up=c.c>=c.o;
        const color=up
          ? 'rgba(48,224,185,.97)'
          : 'rgba(246,82,102,.97)';

        ctx.strokeStyle=color;
        ctx.fillStyle=color;
        ctx.lineWidth=1*q;

        ctx.beginPath();
        ctx.moveTo(x,yh);
        ctx.lineTo(x,yl);
        ctx.stroke();

        const top=Math.min(yo,yc);
        const bodyH=Math.max(1.4*q,Math.abs(yc-yo));
        ctx.fillRect(x-body/2,top,body,bodyH);
      });
    }

    // current mid
    if(mid!=null){
      const y=yOf(mid);
      ctx.strokeStyle='rgba(232,243,252,.82)';
      ctx.lineWidth=1*q;
      ctx.setLineDash([4*q,4*q]);
      ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();
      ctx.setLineDash([]);

      const label=` ${fmt(mid,2)} `;
      ctx.font=`${7.5*q}px Inter`;
      const tw=ctx.measureText(label).width;
      ctx.fillStyle='rgba(239,245,251,.96)';
      ctx.fillRect(w-tw-8*q,y-9*q,tw+5*q,14*q);
      ctx.fillStyle='#07101a';
      ctx.fillText(label,w-tw-6*q,y+1*q);
    }

    // Visible price scale.
    const scaleEls=[...parentElement.querySelectorAll('#price-scale span')];
    scaleEls.forEach((el,i)=>{
      const p=maxP-(maxP-minP)*(i/(scaleEls.length-1));
      el.textContent=fmt(p,2);
    });

    // Labels use aggregated REAL liquidity buckets.
    const bucketNow=aggregateBookToBuckets();
    const bidBuckets=bucketNow.buckets
      .filter(r=>r.bid>0 && r.p<center)
      .sort((a,b)=>b.bid-a.bid);
    const askBuckets=bucketNow.buckets
      .filter(r=>r.ask>0 && r.p>center)
      .sort((a,b)=>b.ask-a.ask);

    const strongBid=bidBuckets[0];
    const strongAsk=askBuckets[0];
    const secondAsk=askBuckets[1];
    const enoughHeat=heatHistory.length>=8;

    positionTag(
      parentElement.querySelector('#buyer-zone'),
      enoughHeat && strongBid && strongBid.p>=minP && strongBid.p<=maxP ? yOf(strongBid.p)/q : null,
      'left'
    );
    positionTag(
      parentElement.querySelector('#seller-zone'),
      enoughHeat && strongAsk && strongAsk.p>=minP && strongAsk.p<=maxP ? yOf(strongAsk.p)/q : null,
      'left'
    );
    positionTag(
      parentElement.querySelector('#secondary-seller-zone'),
      enoughHeat && secondAsk && secondAsk.p>=minP && secondAsk.p<=maxP ? yOf(secondAsk.p)/q : null,
      'center'
    );

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
      const left=w-width-3*q;
      pctx.fillStyle=`rgba(116,79,205,${.28+.58*(v/maxV)})`;pctx.fillRect(left,y-bh/2,width,bh);
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
    setFeed('connecting','Conectando Binance Spot...','Depth + aggTrades + velas sincronizadas');
    Promise.all([fetchSnapshot(),fetchCandles(),fetchAggTrades()]).then(()=>{
      setFeed('connected',`BTC/USDT · ${currentTf} conectado`,'Depth + trades + candles en un solo eje');
      updateStats();drawAll()
    }).catch(err=>{
      console.error('AXION feed error',err);setFeed('error','No se pudo sincronizar Binance',String(err?.message||err))
    });

    const interval=binanceInterval();
    const streams=`btcusdt@depth@100ms/btcusdt@aggTrade/btcusdt@kline_${interval}`;
    ws=new WebSocket(`wss://stream.binance.com:9443/stream?streams=${streams}`);
    ws.onmessage=e=>{
      if(destroyed)return;
      let msg;try{msg=JSON.parse(e.data)}catch(_){return}
      const evt=msg.data||msg;
      if(evt.e==='depthUpdate'){
        if(!snapshotReady){depthBuffer.push(evt);if(depthBuffer.length>5000)depthBuffer.shift();return}
        const expected=book.lastUpdateId+1,U=Number(evt.U),u=Number(evt.u);
        if(u<expected)return;
        if(U>expected){snapshotReady=false;fetchSnapshot().catch(()=>scheduleReconnect());return}
        applyDepth(evt)
      }else if(evt.e==='aggTrade'){
        ingestTrade(evt,true)
      }else if(evt.e==='kline'){
        updateKline(evt.k);drawAll()
      }
    };
    ws.onerror=()=>setFeed('error','WebSocket Binance interrumpido','AXION intentará reconectar.');
    ws.onclose=()=>{if(!destroyed&&currentSymbol==='BTCUSDT')scheduleReconnect()}
    heatTimer=setInterval(captureHeat,1000);
  }

  function scheduleReconnect(){
    if(reconnectTimer)clearTimeout(reconnectTimer);
    reconnectTimer=setTimeout(connect,1800)
  }
  function cleanupFeed(){
    if(ws){try{ws.onclose=null;ws.close()}catch(_){}ws=null}
    if(reconnectTimer){clearTimeout(reconnectTimer);reconnectTimer=null}
    if(heatTimer){clearInterval(heatTimer);heatTimer=null}
    book={bids:new Map(),asks:new Map(),lastUpdateId:0};snapshotReady=false;depthBuffer=[];
    candles=[];resetTradeStats();firstPrice=null
  }

  symbolSelect.onchange=()=>{currentSymbol=symbolSelect.value;setTriggerValue('symbol',currentSymbol);connect()};
  tfButtons.forEach(btn=>btn.onclick=()=>{
    tfButtons.forEach(x=>x.classList.remove('active'));
    btn.classList.add('active');
    currentTf=btn.dataset.tf;
    setTriggerValue('timeframe',currentTf);

    // Reconnect the combined stream so the kline stream changes too.
    if(currentSymbol==='BTCUSDT'){
      setFeed(
        'connecting',
        `Cambiando a ${currentTf}...`,
        'Sincronizando velas y microestructura en el mismo timeframe.'
      );
      connect();
    }
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
  loadRecordedDepth();
  resizeAll();
  connect();

  return()=>{destroyed=true;persistRecordedDepth(true);cleanupFeed();if(clockTimer)clearInterval(clockTimer);resizeObserver?.disconnect()}
}
"""

_component = st.components.v2.component(
    "axion_live_heatmap_v11_1_fixed",
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
    height: int = 900,
):
    return _component(
        data={"symbol": symbol, "timeframe": timeframe},
        default=None,
        key=key,
        width="stretch",
        height=height,
    )



def _init_live_state() -> None:
    defaults = {
        "live_symbol": "BTCUSDT",
        "live_timeframe": "1m",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _handle_result(result) -> None:
    if result is None:
        return

    symbol = getattr(result, "symbol", None)
    if symbol and symbol != st.session_state.live_symbol:
        st.session_state.live_symbol = symbol
        st.rerun()

    timeframe = getattr(result, "timeframe", None)
    if timeframe and timeframe != st.session_state.live_timeframe:
        st.session_state.live_timeframe = timeframe
        st.rerun()


def render_live_heatmap() -> None:
    _init_live_state()

    result = render_axion_live_heatmap(
        symbol=st.session_state.live_symbol,
        timeframe=st.session_state.live_timeframe,
        key="axion_live_heatmap_workspace",
        height=900,
    )
    _handle_result(result)
