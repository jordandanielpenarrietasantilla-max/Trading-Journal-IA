from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client

def _secret(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return str(value).strip()
    try:
        value = st.secrets.get(name)
        if value:
            return str(value).strip()
    except Exception:
        pass
    try:
        supabase_cfg = st.secrets.get("supabase", {})
        nested_name = {
            "SUPABASE_URL": "url",
            "SUPABASE_SERVICE_ROLE_KEY": "service_role_key",
        }.get(name)
        if nested_name:
            value = supabase_cfg.get(nested_name)
            if value:
                return str(value).strip()
    except Exception:
        pass
    return None

@st.cache_resource(show_spinner=False)
def _client() -> Client:
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_SERVICE_ROLE_KEY")
    if not url:
        raise RuntimeError("Falta SUPABASE_URL en los Secrets de Streamlit.")
    if not key:
        raise RuntimeError("Falta SUPABASE_SERVICE_ROLE_KEY en los Secrets de Streamlit. ")
    return create_client(url, key)

def _iso_to_ms(value: Any) -> int:
    if value is None:
        return 0
    text = str(value).strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp() * 1000)

def _fetch_all(*, table: str, columns: str, symbol: str, cutoff_iso: str, page_size: int = 1000) -> list[dict[str, Any]]:
    client = _client()
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        response = (
            client.table(table)
            .select(columns)
            .eq("symbol", symbol)
            .gte("ts", cutoff_iso)
            .order("ts", desc=False)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        batch = list(response.data or [])
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
        if offset >= 10_000:
            break
    return rows

def _downsample_evenly(rows: list[dict[str, Any]], max_points: int) -> list[dict[str, Any]]:
    if len(rows) <= max_points:
        return rows
    if max_points <= 1:
        return [rows[-1]]
    last = len(rows) - 1
    indices = sorted({round(i * last / (max_points - 1)) for i in range(max_points)})
    return [rows[i] for i in indices]

def _compact_depth_row(row: dict[str, Any]) -> dict[str, Any]:
    buckets_raw = row.get("buckets") or []
    compact: list[list[float]] = []
    if isinstance(buckets_raw, list):
        for item in buckets_raw:
            if not isinstance(item, dict):
                continue
            try:
                p = float(item.get("p"))
                b = float(item.get("b", 0))
                a = float(item.get("a", 0))
                q = float(item.get("q", b + a))
            except (TypeError, ValueError):
                continue
            compact.append([p, b, a, q])
    return {
        "t": _iso_to_ms(row.get("ts")),
        "m": float(row.get("mid") or 0),
        "bb": float(row.get("best_bid") or 0),
        "ba": float(row.get("best_ask") or 0),
        "sp": float(row.get("spread") or 0),
        "s": float(row.get("bucket_step") or 1),
        "x": compact,
    }

def _compact_trade_row(row: dict[str, Any]) -> list[float | int]:
    return [
        _iso_to_ms(row.get("ts")),
        float(row.get("open") or 0),
        float(row.get("high") or 0),
        float(row.get("low") or 0),
        float(row.get("close") or 0),
        float(row.get("volume") or 0),
        float(row.get("buy_volume") or 0),
        float(row.get("sell_volume") or 0),
        float(row.get("delta") or 0),
        float(row.get("vwap") or 0),
        int(row.get("trade_count") or 0),
    ]

@st.cache_data(ttl=5, show_spinner=False)
def load_orderflow_history(*, symbol: str = "BTCUSDT", minutes: int = 5, max_depth_columns: int = 900) -> dict[str, Any]:
    # IMPORTANTE: Hemos bajado a 'minutes=5' para que Supabase cargue rápido.
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes)
    cutoff_iso = cutoff.isoformat()

    depth_rows = _fetch_all(
        table="orderflow_depth",
        columns="ts,mid,best_bid,best_ask,spread,bucket_step,buckets",
        symbol=symbol,
        cutoff_iso=cutoff_iso,
    )
    trade_rows = _fetch_all(
        table="orderflow_trade_seconds",
        columns="ts,open,high,low,close,volume,buy_volume,sell_volume,delta,vwap,trade_count",
        symbol=symbol,
        cutoff_iso=cutoff_iso,
    )

    depth_rows = _downsample_evenly(depth_rows, max_points=max_depth_columns)
    depth = [_compact_depth_row(row) for row in depth_rows if row.get("ts")]
    trades = [_compact_trade_row(row) for row in trade_rows if row.get("ts")]

    return {
        "symbol": symbol,
        "minutes": minutes,
        "generated_at_ms": int(now.timestamp() * 1000),
        "depth": depth,
        "trades": trades,
        "depth_count": len(depth),
        "trade_count": len(trades),
    }

# =========================================================
# HTML Y CSS DEL BOCETO 4
# =========================================================
HTML = r"""
<div id="axion-pro-root" class="axion-pro-layout">
  <aside class="side-nav">
    <div class="nav-logo">A</div>
    <nav class="nav-icons">
      <button class="nav-btn active"><span>🌊</span><small>Liquidity</small></button>
      <button class="nav-btn"><span>📈</span><small>Trading</small></button>
      <button class="nav-btn"><span>🛡️</span><small>Positions</small></button>
      <button class="nav-btn"><span>📊</span><small>Analytics</small></button>
    </nav>
    <div class="nav-bottom">
      <button class="nav-btn"><span>⚙️</span></button>
    </div>
  </aside>

  <header class="top-header">
    <div class="header-brand">AXION <span>PRIME</span></div>
    <div class="header-actions">
      <span class="time-display" id="session-time">00:00:00 UTC</span>
      <button class="icon-btn" id="fullscreen-btn">⛶</button>
      <div class="user-profile">
        <div class="avatar">AP</div>
        <div class="user-info">
          <b>AXION PRIME</b>
          <span id="feed-status" style="color:#21c48a;">Iniciando...</span>
        </div>
      </div>
    </div>
  </header>

  <main class="main-content">
    <div class="asset-bar">
      <div class="asset-title">BTC/USDT <span>★</span> <b id="quote-price">—</b> <small class="up" id="quote-change">—</small></div>
      <div class="asset-stats">
        <div><span>Delta Acumulado</span><b id="delta-value">—</b></div>
      </div>
    </div>

    <div class="chart-controls">
      <span class="title">Liquidity Map ⓘ</span>
      <div class="controls-group" id="timeframes">
        <button data-tf="1m" class="active">1m</button>
        <button data-tf="5m">5m</button>
        <button data-tf="15m">15m</button>
        <button data-tf="30m">30m</button>
      </div>
    </div>

    <div class="chart-stage">
      <canvas id="heat-canvas"></canvas>
      <canvas id="overlay-canvas"></canvas>
      <div class="price-axis" id="price-axis">
        <span>—</span><span>—</span><span>—</span><span>—</span><span>—</span><span>—</span><span>—</span><span>—</span><span>—</span>
      </div>
    </div>
    
    <div class="intensity-bar-container">
       <span>Low Intensity</span>
       <div class="intensity-gradient"></div>
       <span>High Intensity</span>
       <input id="heat-intensity" type="range" min="45" max="100" value="66" style="display:none;">
    </div>
  </main>

  <aside class="right-panel">
    <div class="panel-card ai-summary">
      <div class="card-header">🤖 AI Market Summary <span class="badge">AXION AI</span></div>
      <p id="loading-message" style="color:#4db8ff;">Sincronizando profundidad y WebSockets...</p>
      <div class="confidence">
        <span>Confidence</span> <span>78%</span>
      </div>
      <div class="progress-bar"><div class="fill" style="width:78%"></div></div>
    </div>

    <div class="panel-card">
      <div class="card-header">Market View</div>
      <div class="gauge-placeholder" style="text-align: center; padding: 20px 0;">
        <h2 class="bullish" style="color:#21c48a; letter-spacing:2px; font-size: 24px; margin-bottom: 5px;">BULLISH</h2>
        <small style="color:#7a8aa8;">Strength: 72%</small>
      </div>
    </div>

    <div class="panel-card stats">
      <div><span>Bid Liquidity</span><b id="bid-value">—</b></div>
      <div><span>Ask Liquidity</span><b id="ask-value">—</b></div>
    </div>
    
    <canvas id="profile-canvas" style="display:none;"></canvas>
  </aside>
</div>
"""

CSS = r"""
:host { display:block; width:100%; height:100vh; font-family: 'Inter', ui-sans-serif, system-ui, sans-serif; background-color: #05070a; }
* { box-sizing: border-box; margin: 0; padding: 0; }
button { background: none; border: none; cursor: pointer; font-family: inherit; }

.axion-pro-layout {
  display: grid;
  grid-template-columns: 75px 1fr 340px;
  grid-template-rows: 65px 1fr;
  grid-template-areas: "nav header header" "nav main right";
  width: 100%; height: 100vh; color: #c5d0e6; overflow: hidden; background-color: #05070a;
}
.axion-pro-layout:fullscreen { width: 100vw; height: 100vh; }

.side-nav { grid-area: nav; background: #080b10; border-right: 1px solid #141b26; display: flex; flex-direction: column; align-items: center; padding: 20px 0; }
.nav-logo { font-size: 24px; font-weight: 900; color: #4db8ff; margin-bottom: 30px; letter-spacing: -1px;}
.nav-icons { display: flex; flex-direction: column; gap: 20px; width: 100%; }
.nav-btn { color: #4b5a77; display: flex; flex-direction: column; align-items: center; gap: 5px; padding: 10px 0; width: 100%; transition: 0.3s; }
.nav-btn:hover { color: #fff; }
.nav-btn.active { color: #4db8ff; border-left: 2px solid #4db8ff; background: rgba(77, 184, 255, 0.05); }
.nav-btn span { font-size: 20px; }
.nav-btn small { font-size: 9px; font-weight: 600; letter-spacing: 0.5px;}

.top-header { grid-area: header; background: #080b10; display: flex; justify-content: space-between; align-items: center; padding: 0 25px; border-bottom: 1px solid #141b26; }
.header-brand { font-size: 18px; font-weight: 800; letter-spacing: 2px; color: #fff;}
.header-brand span { color: #5a6b8c; font-weight: 400; }
.header-actions { display: flex; align-items: center; gap: 20px; font-size: 12px; font-weight: 500; color: #7a8aa8;}
.icon-btn { color: #7a8aa8; font-size: 18px; transition: 0.3s; }
.icon-btn:hover { color: #fff; }
.user-profile { display: flex; align-items: center; gap: 10px; border-left: 1px solid #1c2638; padding-left: 20px; }
.avatar { width: 35px; height: 35px; background: #1a2538; border-radius: 50%; display: grid; place-items: center; border: 1px solid #4db8ff; color: #fff; font-size: 12px; font-weight: bold;}
.user-info b { display: block; font-size: 13px; color: #fff; }
.user-info span { font-size: 10px; color: #21c48a; }

.main-content { grid-area: main; display: flex; flex-direction: column; padding: 20px 25px; background: #05070a; min-width:0; min-height:0; }
.asset-bar { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 15px; }
.asset-title { font-size: 26px; font-weight: 600; color: #fff; display: flex; align-items: baseline; gap: 12px; }
.asset-title span { color: #4db8ff; font-size: 16px; margin-bottom: 4px;}
.asset-title .up { color: #21c48a; font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.asset-title .down { color: #f05c72; font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.asset-stats { display: flex; gap: 30px; font-size: 11px; color: #7a8aa8; text-align: right; }
.asset-stats b { display: block; color: #fff; font-size: 16px; margin-top: 4px; font-weight: 600;}

.chart-controls { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.title { font-size: 16px; font-weight: 600; color: #e2e8f0; }
.controls-group { display: flex; gap: 8px; }
.controls-group button { background: #0d121b; border: 1px solid #1c2638; color: #7a8aa8; padding: 6px 14px; border-radius: 6px; font-size: 11px; font-weight: 600; transition: 0.3s;}
.controls-group button:hover { background: #1a2538; color: #fff; }
.controls-group button.active { background: #131c2b; color: #fff; border-color: #4db8ff; }

.chart-stage { flex: 1; position: relative; border-radius: 12px; border: 1px solid #141b26; overflow: hidden; background: #020305; box-shadow: inset 0 0 40px rgba(0,0,0,0.5);}
#heat-canvas, #overlay-canvas { position: absolute; inset: 0; width: 100%; height: 100%; }
#heat-canvas { z-index: 1; } #overlay-canvas { z-index: 2; }
.price-axis { position: absolute; right: 10px; top: 10px; bottom: 10px; z-index: 5; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end; color: #5a6b8c; font-size: 10px; pointer-events: none; font-variant-numeric: tabular-nums;}
.price-axis span { background: rgba(5,7,10,0.6); padding: 2px 6px; border-radius: 4px; backdrop-filter: blur(2px);}

.intensity-bar-container { display: flex; align-items: center; gap: 15px; font-size: 10px; margin-top: 20px; color: #5a6b8c; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;}
.intensity-gradient { flex: 1; height: 6px; border-radius: 4px; background: linear-gradient(90deg, #020305, #0055ff, #f6b130, #fff); }

.right-panel { grid-area: right; background: #080b10; border-left: 1px solid #141b26; padding: 20px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto;}
.panel-card { background: #0b0f16; border: 1px solid #141b26; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);}
.card-header { font-size: 14px; color: #fff; margin-bottom: 15px; font-weight: 600; display: flex; justify-content: space-between; align-items: center;}
.badge { background: rgba(77,184,255,0.1); color: #4db8ff; border: 1px solid rgba(77,184,255,0.2); padding: 4px 8px; border-radius: 4px; font-size: 9px; font-weight: bold; letter-spacing: 0.5px;}
.ai-summary p { font-size: 12px; color: #7a8aa8; line-height: 1.6; margin-bottom: 20px; }
.confidence { display: flex; justify-content: space-between; font-size: 11px; margin-bottom: 6px; color: #c5d0e6;}
.progress-bar { width: 100%; height: 4px; background: #141b26; border-radius: 2px; }
.progress-bar .fill { height: 100%; background: #4db8ff; border-radius: 2px; box-shadow: 0 0 10px rgba(77,184,255,0.5);}
.stats div { margin-bottom: 15px; font-size: 11px; color: #7a8aa8; }
.stats div:last-child { margin-bottom: 0; }
.stats b { display: block; color: #fff; font-size: 18px; margin-top: 5px; font-variant-numeric: tabular-nums;}
"""

# =========================================================
# JAVASCRIPT LOGIC
# =========================================================
JS = r"""
export default function(component) {
  const {parentElement,data,setTriggerValue}=component;
  const root=parentElement.querySelector('#axion-pro-root');
  if(!root)return;

  const $=s=>parentElement.querySelector(s);
  const $$=s=>[...parentElement.querySelectorAll(s)];
  const heatCanvas=$('#heat-canvas');
  const overlayCanvas=$('#overlay-canvas');
  const hctx=heatCanvas.getContext('2d');
  const octx=overlayCanvas.getContext('2d');

  let destroyed=false;
  let ws=null;
  let reconnectTimer=null;
  let captureTimer=null;
  let drawTimer=null;
  let clockTimer=null;
  let resizeObserver=null;

  let currentTf=String(data?.timeframe||'1m');
  let intensity=.66;

  const history=data?.history||{};
  const HISTORY_MS=Math.max(5,Number(history.minutes||30))*60_000;
  const MAX_DEPTH_COLS=1200;

  let depthHistory=Array.isArray(history.depth)?history.depth.slice():[];
  let tradeSeconds=Array.isArray(history.trades)?history.trades.slice():[];

  let bids=new Map(),asks=new Map(),lastUpdateId=0,snapshotReady=false,depthBuffer=[];
  let liveTradeSecond=null;
  let firstPrice=tradeSeconds.length?Number(tradeSeconds[0][1]):null;

  const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
  const dpr=()=>clamp(window.devicePixelRatio||1,1,2);

  function fmt(v,d=2){
    if(!Number.isFinite(v))return'—';
    return v.toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
  }
  function compact(v){
    if(!Number.isFinite(v))return'—';
    const a=Math.abs(v);
    if(a>=1e9)return(v/1e9).toFixed(2)+'B';
    if(a>=1e6)return(v/1e6).toFixed(2)+'M';
    if(a>=1e3)return(v/1e3).toFixed(2)+'K';
    return v.toFixed(2);
  }
  function percentile(sorted,p){
    if(!sorted.length)return 0;
    return sorted[clamp(Math.floor((sorted.length-1)*p),0,sorted.length-1)];
  }
  function resizeCanvas(c){
    const r=c.getBoundingClientRect(),q=dpr();
    const w=Math.max(1,Math.round(r.width*q)),h=Math.max(1,Math.round(r.height*q));
    if(c.width!==w||c.height!==h){c.width=w;c.height=h}
  }

  function trimHistory(){
    const now=Date.now(),cutoff=now-HISTORY_MS;
    depthHistory=depthHistory.filter(c=>Number(c.t)>=cutoff).slice(-MAX_DEPTH_COLS);
    tradeSeconds=tradeSeconds.filter(r=>Number(r[0])>=cutoff);
  }

  function sortedBook(){
    return{
      bids:[...bids.entries()].sort((a,b)=>b[0]-a[0]),
      asks:[...asks.entries()].sort((a,b)=>a[0]-b[0])
    }
  }
  function mid(){
    const b=sortedBook();
    return b.bids.length&&b.asks.length?(b.bids[0][0]+b.asks[0][0])/2:null
  }

  function normalizeLevels(raw){
    return(Array.isArray(raw)?raw:[]).map(x=>[Number(x[0]),Number(x[1])])
      .filter(x=>Number.isFinite(x[0])&&Number.isFinite(x[1])&&x[0]>0&&x[1]>=0)
  }
  function applySide(map,levels){
    for(const[p,q]of normalizeLevels(levels)){if(q===0)map.delete(p);else map.set(p,q)}
  }
  function applyDepth(evt){
    applySide(bids,evt.b);applySide(asks,evt.a);lastUpdateId=Number(evt.u||lastUpdateId)
  }

  async function fetchSnapshot(){
    try {
        const res=await fetch('https://data-api.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=1000',{cache:'no-store'});
        if(!res.ok)throw new Error('Depth HTTP '+res.status);
        const snap=await res.json();
        bids=new Map(normalizeLevels(snap.bids).filter(x=>x[1]>0));
        asks=new Map(normalizeLevels(snap.asks).filter(x=>x[1]>0));
        lastUpdateId=Number(snap.lastUpdateId||0);

        const buffered=depthBuffer.filter(e=>Number(e.u)>lastUpdateId);
        let start=-1;
        for(let i=0;i<buffered.length;i++){
          const e=buffered[i],expected=lastUpdateId+1;
          if(Number(e.U)<=expected&&Number(e.u)>=expected){start=i;break}
        }
        if(start>=0){
          for(let i=start;i<buffered.length;i++)if(Number(buffered[i].u)>lastUpdateId)applyDepth(buffered[i])
        }
        depthBuffer=[];
        snapshotReady=true;
    } catch(err) {
        // En caso de que el adblocker bloquee Binance
        console.error("Binance Snapshot bloqueado:", err);
        snapshotReady=true;
        throw err;
    }
  }

  function bucketStep(price){
    if(price>=100000)return 10;
    if(price>=50000)return 5;
    if(price>=20000)return 2;
    if(price>=5000)return 1;
    return .5
  }
  
  function bucketBook(){
    const m=mid();if(m==null)return null;
    const step=bucketStep(m),map=new Map(),book=sortedBook();
    const add=(side,levels)=>{
      for(const[p,q]of levels.slice(0,700)){
        if(!(q>0))continue;
        const bp=Math.round(p/step)*step;
        let r=map.get(bp);if(!r){r={p:bp,b:0,a:0,q:0};map.set(bp,r)}
        r[side]+=q;r.q+=q
      }
    };
    add('b',book.bids);add('a',book.asks);
    return{
      t:Date.now(),m,bb:book.bids[0]?.[0]||0,ba:book.asks[0]?.[0]||0,
      sp:book.bids.length&&book.asks.length?book.asks[0][0]-book.bids[0][0]:0,
      s:step,x:[...map.values()].sort((a,b)=>a.p-b.p).map(r=>[r.p,r.b,r.a,r.q])
    }
  }

  function captureDepth(){
    if(!snapshotReady)return;
    const col=bucketBook();if(!col)return;
    depthHistory.push(col);trimHistory();drawHeat();drawOverlay()
  }

  function ingestTrade(evt){
    const p=Number(evt.p),q=Number(evt.q),t=Number(evt.T||Date.now());
    if(!Number.isFinite(p)||!Number.isFinite(q))return;
    const sec=Math.floor(t/1000)*1000,buy=!Boolean(evt.m);

    if(!liveTradeSecond||liveTradeSecond[0]!==sec){
      if(liveTradeSecond)tradeSeconds.push(liveTradeSecond);
      liveTradeSecond=[sec,p,p,p,p,0,0,0,0,p,0,0]; 
    }
    const r=liveTradeSecond;
    r[2]=Math.max(r[2],p);r[3]=Math.min(r[3],p);r[4]=p;r[5]+=q;
    if(buy)r[6]+=q;else r[7]+=q;
    r[8]=r[6]-r[7];r[10]+=1;r[11]+=p*q;r[9]=r[5]>0?r[11]/r[5]:p;
    if(firstPrice==null)firstPrice=p
  }

  function tfMs(){
    return{'1m':60_000,'5m':300_000,'15m':900_000,'30m':1_800_000,'1H':3_600_000}[currentTf]||60_000
  }
  function allTradeRows(){
    const arr=tradeSeconds.slice();
    if(liveTradeSecond)arr.push(liveTradeSecond);
    return arr.sort((a,b)=>a[0]-b[0])
  }
  function candles(){
    const span=tfMs(),out=[];
    for(const r of allTradeRows()){
      const t=Math.floor(Number(r[0])/span)*span;
      let c=out[out.length-1];
      if(!c||c.t!==t){
        c={t,o:Number(r[1]),h:Number(r[2]),l:Number(r[3]),c:Number(r[4]),v:Number(r[5])};
        out.push(c)
      }else{
        c.h=Math.max(c.h,Number(r[2]));c.l=Math.min(c.l,Number(r[3]));
        c.c=Number(r[4]);c.v+=Number(r[5])
      }
    }
    return out
  }

  function timeWindow(){
    trimHistory();
    const end=Math.max(Date.now(), depthHistory.length?Number(depthHistory[depthHistory.length-1].t):0);
    return{start:end-HISTORY_MS,end}
  }

  function robustRange(cols,cnds,m){
    const samples=[];
    for(const col of cols){
      for(const row of col.x||[])if(Number.isFinite(Number(row[0])))samples.push(Number(row[0]))
    }
    for(const c of cnds){samples.push(c.h,c.l)}
    if(!samples.length){
      const center=m||1;return{min:center*.997,max:center*1.003}
    }
    samples.sort((a,b)=>a-b);
    let min=percentile(samples,.035),max=percentile(samples,.965);
    if(Number.isFinite(m)){
      const half=Math.max(Math.abs(m-min),Math.abs(max-m),m*.00105);
      min=m-half;max=m+half
    }
    const range=Math.max(max-min,(m||max)*.0009);
    return{min:min-range*.035,max:max+range*.035}
  }

  function smoothColumns(cols){
    if(!cols.length)return [];
    const out=[];
    const persistence=new Map();
    const decay=.76;

    for(let i=0;i<cols.length;i++){
      const col=cols[i];
      const current=new Map();

      for(const row of col.x||[]){
        const p=Number(row[0]), bid=Number(row[1]), ask=Number(row[2]), q=Number(row[3]);
        if(!(q>0)||!Number.isFinite(p))continue;
        current.set(p,{p,bid,ask,q});
      }

      for(const [p,prev] of persistence.entries()){
        const now=current.get(p);
        if(now){
          persistence.set(p,{
            p, bid:now.bid + prev.bid*decay*.22, ask:now.ask + prev.ask*decay*.22, q:now.q + prev.q*decay*.22
          });
        }else{
          const decayed={ p, bid:prev.bid*decay, ask:prev.ask*decay, q:prev.q*decay };
          if(decayed.q>.000001)persistence.set(p,decayed);
          else persistence.delete(p)
        }
      }

      for(const [p,now] of current.entries()){
        if(!persistence.has(p))persistence.set(p,{...now})
      }

      out.push({
        ...col,
        x:[...persistence.values()].sort((a,b)=>a.p-b.p).map(r=>[r.p,r.bid,r.ask,r.q])
      })
    }
    return out
  }

  function lerp(a,b,t){return a+(b-a)*t}

  function heatColor(n,bias){
    const a=intensity;
    if(n<.24) return `rgba(11, 15, 23, ${(0.05+n*0.2)*a})`;
    if(n<.48) return `rgba(0, 102, 255, ${(0.1+n*0.4)*a})`; 
    if(n<.68) return `rgba(0, 170, 255, ${(0.2+n*0.5)*a})`; 
    if(n<.84) return `rgba(246, 177, 48, ${(0.3+n*0.6)*a})`; 
    if(n<.95) return `rgba(255, 200, 50, ${(0.5+n*0.5)*a})`; 
    return `rgba(255, 255, 200, ${(0.7+n*0.3)*a})`; 
  }

  function drawGrid(ctx,w,h,q){
    ctx.strokeStyle='rgba(28, 38, 56, .4)';ctx.lineWidth=1*q;
    for(let i=1;i<9;i++){const y=h*i/9;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}
    for(let i=1;i<14;i++){const x=w*i/14;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}
  }

  function drawHeat(){
    resizeCanvas(heatCanvas);
    const q=dpr(),w=heatCanvas.width,h=heatCanvas.height;
    hctx.clearRect(0,0,w,h);
    hctx.fillStyle='#020305'; 
    hctx.fillRect(0,0,w,h);
    drawGrid(hctx,w,h,q);

    hctx.globalCompositeOperation = 'lighter';

    const win=timeWindow(),cols=depthHistory.filter(c=>c.t>=win.start&&c.t<=win.end);
    const cnds=candles().filter(c=>c.t+tfMs()>=win.start&&c.t<=win.end);
    const m=mid()??(cols.length?Number(cols[cols.length-1].m):null);
    const range=robustRange(cols,cnds,m),minP=range.min,maxP=range.max;
    const yOf=p=>h-((p-minP)/(maxP-minP))*h;
    
    const smooth=smoothColumns(cols);

    const totals=[];
    for(const col of smooth)for(const row of col.x||[]){
      const p=Number(row[0]),v=Number(row[3]);
      if(p>=minP&&p<=maxP&&v>0)totals.push(v)
    }
    totals.sort((a,b)=>a-b);

    const q45=percentile(totals,.45)||1;
    const q72=percentile(totals,.72)||q45;
    const q90=percentile(totals,.90)||q72;
    const q98=percentile(totals,.98)||q90;

    const xOfT=t=>((Number(t)-win.start)/(win.end-win.start))*w;

    for(let i=0;i<smooth.length;i++){
      const col=smooth[i];
      const next=i<smooth.length-1?smooth[i+1]:null;

      const x1=xOfT(col.t);
      const x2=xOfT(next?next.t:Math.min(win.end,Number(col.t)+1000));
      const width=Math.max(1*q,x2-x1+1*q);

      const step=Number(col.s)||5;
      const cm=Number(col.m)||m;
      const baseH=Math.max(1.5*q,Math.abs(yOf(cm+step)-yOf(cm))*.78);

      const nextMap=new Map();
      if(next) for(const row of next.x||[])nextMap.set(Number(row[0]),row);

      for(const row of col.x||[]){
        const p=Number(row[0]), bid=Number(row[1]), ask=Number(row[2]), v=Number(row[3]);
        if(p<minP||p>maxP||!(v>0))continue;

        const nr=nextMap.get(p);
        const nextV=nr?Number(nr[3]):v*.72;
        const nextBid=nr?Number(nr[1]):bid*.72;
        const nextAsk=nr?Number(nr[2]):ask*.72;

        for(let s=0;s<3;s++){
          const t=s/3, sv=lerp(v,nextV,t), sb=lerp(bid,nextBid,t), sa=lerp(ask,nextAsk,t);

          let n;
          if(sv<=q45) n=.08+.20*(sv/Math.max(q45,1e-9));
          else if(sv<=q72) n=.28+.20*((sv-q45)/Math.max(q72-q45,1e-9));
          else if(sv<=q90) n=.48+.24*((sv-q72)/Math.max(q90-q72,1e-9));
          else if(sv<=q98) n=.72+.20*((sv-q90)/Math.max(q98-q90,1e-9));
          else n=.94;

          const bias=(sb-sa)/Math.max(sv,1e-9);
          hctx.fillStyle=heatColor(n,bias);
          const subW=width/3+1*q, sx=x1+s*(width/3);
          hctx.fillRect(sx, yOf(p)-baseH/2, subW, baseH);
        }
      }
    }
    
    hctx.globalCompositeOperation = 'source-over';
    drawPriceAxis(minP,maxP);
    window.__axionViewport={win,minP,maxP,yOf,xOf:xOfT,w,h,q,m}
  }

  function drawOverlay(){
    resizeCanvas(overlayCanvas);
    const vp=window.__axionViewport;if(!vp)return;
    const{win,minP,maxP,yOf,xOf,w,h,q}=vp;
    octx.clearRect(0,0,w,h);

    const rows=allTradeRows().filter(r=>r[0]>=win.start&&r[0]<=win.end);
    const cnds=candles().filter(c=>c.t+tfMs()>=win.start&&c.t<=win.end);

    const theoretical=(tfMs()/(win.end-win.start))*w;
    const bodyW=clamp(theoretical*.46,4.2*q,9*q);
    const wickW=clamp(bodyW*.18,1.1*q,1.7*q);

    for(const c of cnds){
      if(![c.o,c.h,c.l,c.c].every(Number.isFinite)||c.h<minP||c.l>maxP)continue;
      const x=xOf(c.t+tfMs()/2);
      if(x<0||x>w)continue;
      const yh=yOf(c.h),yl=yOf(c.l),yo=yOf(c.o),yc=yOf(c.c),up=c.c>=c.o;
      const fill=up?'#21c48a':'#f05c72';
      const edge=up?'#86ebd0':'#ffb3c0';

      const shadeTop=Math.min(yh,yl)-3*q;
      const shadeH=Math.abs(yl-yh)+6*q;
      octx.fillStyle='rgba(2,3,5,.3)'; 
      octx.fillRect(x-bodyW*.9,shadeTop,bodyW*1.8,shadeH);

      octx.strokeStyle='rgba(0,0,0,.8)';
      octx.lineWidth=wickW+2.4*q;
      octx.beginPath();octx.moveTo(x,yh);octx.lineTo(x,yl);octx.stroke();

      octx.strokeStyle=edge;
      octx.lineWidth=wickW;
      octx.beginPath();octx.moveTo(x,yh);octx.lineTo(x,yl);octx.stroke();

      const top=Math.min(yo,yc);
      const bodyH=Math.max(3.2*q,Math.abs(yc-yo));

      octx.fillStyle='rgba(0,0,0,.8)';
      octx.fillRect(x-bodyW/2-1.3*q, top-1.3*q, bodyW+2.6*q, bodyH+2.6*q);

      octx.fillStyle=fill;
      octx.fillRect(x-bodyW/2, top, bodyW, bodyH);
    }

    const m=mid()??vp.m;
    if(Number.isFinite(m)&&m>=minP&&m<=maxP){
      const y=yOf(m);octx.strokeStyle='rgba(255,255,255,.3)';octx.lineWidth=1*q;
      octx.setLineDash([4*q,4*q]);octx.beginPath();octx.moveTo(0,y);octx.lineTo(w,y);octx.stroke();octx.setLineDash([]);
      const label=` ${fmt(m,2)} `;octx.font=`600 ${10*q}px Inter`;const tw=octx.measureText(label).width;
      octx.fillStyle='#4db8ff';octx.fillRect(w-tw-10*q,y-9*q,tw+10*q,18*q);
      octx.fillStyle='#020305';octx.fillText(label,w-tw-5*q,y+4*q)
    }

    updateUI(rows)
  }

  function drawPriceAxis(minP,maxP){
    const els=$$('#price-axis span');
    els.forEach((el,i)=>el.textContent=fmt(maxP-(maxP-minP)*(i/Math.max(1,els.length-1)),2))
  }

  function updateUI(rows){
    const book=sortedBook(),m=mid();
    const qPrice = $('#quote-price'), qChange = $('#quote-change');
    const bValue = $('#bid-value'), aValue = $('#ask-value'), dValue = $('#delta-value'), sTime = $('#session-time');
    
    if(Number.isFinite(m)){
      if(qPrice) qPrice.textContent=fmt(m,2);
      if(firstPrice && qChange){
        const pct=(m-firstPrice)/firstPrice*100;
        qChange.textContent=`${pct>=0?'+':''}${pct.toFixed(2)}%`;
        qChange.className = pct>=0 ? 'up' : 'down';
      }
    }

    const bidQty=book.bids.slice(0,180).reduce((s,x)=>s+x[1],0);
    const askQty=book.asks.slice(0,180).reduce((s,x)=>s+x[1],0);
    if(bValue) bValue.textContent=compact(bidQty)+' BTC';
    if(aValue) aValue.textContent=compact(askQty)+' BTC';

    let buy=0,sell=0;
    for(const r of rows){buy+=Number(r[6]);sell+=Number(r[7])}
    const delta=buy-sell;
    if(dValue) {
        dValue.textContent=(delta>=0?'+':'')+compact(delta)+' BTC';
        dValue.style.color = delta>=0 ? '#21c48a' : '#f05c72';
    }

    if(sTime){
        const d=new Date(),hh=String(d.getUTCHours()).padStart(2,'0'),mm=String(d.getUTCMinutes()).padStart(2,'0'),ss=String(d.getUTCSeconds()).padStart(2,'0');
        sTime.textContent=`${hh}:${mm}:${ss} UTC`;
    }
    
    // CORRECCIÓN DEL BUG VISUAL: Ahora SIEMPRE actualiza el texto, aunque esté en 0.
    const msg = $('#loading-message');
    if(msg) {
        const count = history.depth_count || 0;
        msg.innerHTML = `Loaded <b style="color:#4db8ff;">${count}</b> historical depth columns.<br><span style="color:#21c48a;">⚡ Live WebSockets Sync Active</span>`;
    }
  }

  function connect(){
    cleanupSocket();
    fetchSnapshot().then(()=>{
      const fs = $('#feed-status'); if(fs) fs.textContent='Live Connected';
      drawHeat();drawOverlay();
    }).catch(err=>{
      console.error(err);
      const fs = $('#feed-status'); if(fs) fs.textContent='API Error';
      const msg = $('#loading-message');
      if(msg) msg.innerHTML = `<span style="color:#f05c72;">API Binance bloqueada. Intenta desactivar tu AdBlock/Brave Shields.</span>`;
    });

    ws=new WebSocket('wss://stream.binance.com:9443/stream?streams=btcusdt@depth@100ms/btcusdt@aggTrade');
    ws.onmessage=e=>{
      if(destroyed)return;
      let msg;try{msg=JSON.parse(e.data)}catch(_){return}
      const evt=msg.data||msg;
      if(evt.e==='depthUpdate'){
        if(!snapshotReady){depthBuffer.push(evt);if(depthBuffer.length>5000)depthBuffer.shift();return}
        const expected=lastUpdateId+1,U=Number(evt.U),u=Number(evt.u);
        if(u<expected)return;
        if(U>expected){snapshotReady=false;fetchSnapshot().catch(scheduleReconnect);return}
        applyDepth(evt)
      }else if(evt.e==='aggTrade'){ingestTrade(evt)}
    };
    ws.onclose=()=>{if(!destroyed)scheduleReconnect()};
    captureTimer=setInterval(captureDepth,1000);
    drawTimer=setInterval(()=>{drawOverlay()},750)
  }

  function scheduleReconnect(){
    if(reconnectTimer)clearTimeout(reconnectTimer);
    reconnectTimer=setTimeout(connect,1800)
  }
  function cleanupSocket(){
    if(ws){try{ws.onclose=null;ws.close()}catch(_){}ws=null}
    if(reconnectTimer){clearTimeout(reconnectTimer);reconnectTimer=null}
    if(captureTimer){clearInterval(captureTimer);captureTimer=null}
    if(drawTimer){clearInterval(drawTimer);drawTimer=null}
    snapshotReady=false;depthBuffer=[]
  }

  $$('#timeframes button').forEach(btn=>btn.onclick=()=>{
    $$('#timeframes button').forEach(x=>x.classList.remove('active'));btn.classList.add('active');
    currentTf=btn.dataset.tf||'1m';setTriggerValue('timeframe',currentTf);drawHeat();drawOverlay()
  });
  
  const fBtn = $('#fullscreen-btn');
  if(fBtn) fBtn.onclick=async()=>{try{if(!document.fullscreenElement)await root.requestFullscreen();else await document.exitFullscreen()}catch(_){}};

  if(typeof ResizeObserver!=='undefined'){
    resizeObserver=new ResizeObserver(()=>{drawHeat();drawOverlay()});
    const main = parentElement.querySelector('.main-content');
    if(main) resizeObserver.observe(main);
  }

  drawHeat();drawOverlay();connect();

  return()=>{
    destroyed=true;cleanupSocket();
    if(clockTimer)clearInterval(clockTimer);
    resizeObserver?.disconnect()
  }
}
"""

_component = st.components.v2.component(
    "axion_boceto4_orderflow_pro",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=True,
)

def _history_payload() -> dict:
    try:
        return load_orderflow_history(
            symbol="BTCUSDT",
            minutes=5,  # Bajado a 5 minutos para que cargue rapidísimo
            max_depth_columns=900,
        )
    except Exception as exc:
        return {
            "symbol": "BTCUSDT",
            "minutes": 5,
            "depth": [],
            "trades": [],
            "depth_count": 0,
            "trade_count": 0,
            "error": str(exc),
        }

def _init_live_state() -> None:
    if "live_timeframe" not in st.session_state:
        st.session_state.live_timeframe = "1m"

def _handle_result(result) -> None:
    if result is None:
        return
    # Corrección de seguridad en Python para evitar fallos si llega como diccionario
    if isinstance(result, dict):
        timeframe = result.get("timeframe")
    else:
        timeframe = getattr(result, "timeframe", None)
        
    if timeframe and timeframe != st.session_state.live_timeframe:
        st.session_state.live_timeframe = timeframe
        st.rerun()

def render_live_heatmap() -> None:
    # Quitamos márgenes y forzamos ancho completo en Streamlit
    st.markdown("""
        <style>
            .block-container { padding: 0rem !important; max-width: 100% !important; margin: 0 !important; }
            [data-testid="stSidebar"] { display: none !important; }
            header { display: none !important; }
            footer { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    _init_live_state()
    history = _history_payload()

    result = _component(
        data={
            "timeframe": st.session_state.live_timeframe,
            "history": history,
        },
        default=None,
        key="axion_boceto4_market_live",
        width="stretch",
        height=900,
    )

    _handle_result(result)
