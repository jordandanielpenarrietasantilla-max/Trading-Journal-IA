from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import streamlit as st
from supabase import Client, create_client

import os
from datetime import datetime, timedelta, timezone
from typing import Any



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

    # Optional nested structure:
    # [supabase]
    # url = "..."
    # service_role_key = "..."
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
        raise RuntimeError(
            "Falta SUPABASE_URL en los Secrets de Streamlit."
        )

    if not key:
        raise RuntimeError(
            "Falta SUPABASE_SERVICE_ROLE_KEY en los Secrets de Streamlit. "
            "La clave se usa únicamente del lado del servidor y nunca se envía al navegador."
        )

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


def _fetch_all(
    *,
    table: str,
    columns: str,
    symbol: str,
    cutoff_iso: str,
    page_size: int = 1000,
) -> list[dict[str, Any]]:
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

        # Safety guard: more than enough for the AXION chart.
        if offset >= 30_000:
            break

    return rows


def _downsample_evenly(
    rows: list[dict[str, Any]],
    max_points: int,
) -> list[dict[str, Any]]:
    if len(rows) <= max_points:
        return rows

    if max_points <= 1:
        return [rows[-1]]

    last = len(rows) - 1

    indices = sorted(
        {
            round(i * last / (max_points - 1))
            for i in range(max_points)
        }
    )

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

def _load_orderflow_history_fast_rpc(
    symbol: str = "BTCUSDT",
    minutes: int = 360,
    depth_step_seconds: int = 10,
    trade_step_seconds: int = 10,
) -> dict:
    client = _client()
    resp = client.rpc(
        "axion_orderflow_history_fast",
        {
            "p_symbol": symbol,
            "p_minutes": minutes,
            "p_depth_step_seconds": depth_step_seconds,
            "p_trade_step_seconds": trade_step_seconds,
        },
    ).execute()

    payload = resp.data or {}
    if isinstance(payload, list) and payload:
        payload = payload[0]

    depth = []
    for row in payload.get("depth") or []:
        buckets = row.get("buckets") or []
        compact = []
        for b in buckets:
            if isinstance(b, dict):
                p = float(b.get("price") or 0)
                bid = float(b.get("bid") or 0)
                ask = float(b.get("ask") or 0)
                qty = float(b.get("qty") or 0)
            elif isinstance(b, (list, tuple)) and len(b) >= 4:
                p, bid, ask, qty = [float(x or 0) for x in b[:4]]
            else:
                continue
            if p > 0 and qty > 0:
                compact.append([p, bid, ask, qty])

        depth.append({
            "t": _epoch_ms(row.get("ts")),
            "m": float(row.get("mid") or 0),
            "bb": float(row.get("best_bid") or 0),
            "ba": float(row.get("best_ask") or 0),
            "sp": float(row.get("spread") or 0),
            "s": float(row.get("bucket_step") or 5),
            "x": compact,
        })

    trades = []
    for row in payload.get("trades") or []:
        trades.append([
            _epoch_ms(row.get("ts")),
            0.0, 0.0, 0.0, 0.0,
            float(row.get("volume") or 0),
            float(row.get("buy_volume") or 0),
            float(row.get("sell_volume") or 0),
            float(row.get("delta") or 0),
            float(row.get("vwap") or 0),
            int(row.get("trade_count") or 0),
        ])

    return {
        "symbol": payload.get("symbol") or symbol,
        "minutes": int(payload.get("minutes") or minutes),
        "depth": depth,
        "trades": trades,
        "depth_count": len(depth),
        "trade_count": len(trades),
        "source": "rpc_fast",
        "error": None,
    }


def load_orderflow_history(
    *,
    symbol: str = "BTCUSDT",
    minutes: int = 30,
    max_depth_columns: int = 900,
) -> dict[str, Any]:
    """
    Load real historical order-flow data recorded by AXION.

    Depth is downsampled only in the time dimension to keep the Streamlit
    component payload performant. Bucket quantities themselves are unchanged.
    Trade-second rows are preserved at 1-second resolution.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=minutes)
    cutoff_iso = cutoff.isoformat()

    depth_rows = _fetch_all(
        table="orderflow_depth",
        columns=(
            "ts,mid,best_bid,best_ask,spread,"
            "bucket_step,buckets"
        ),
        symbol=symbol,
        cutoff_iso=cutoff_iso,
    )

    trade_rows = _fetch_all(
        table="orderflow_trade_seconds",
        columns=(
            "ts,open,high,low,close,volume,"
            "buy_volume,sell_volume,delta,vwap,trade_count"
        ),
        symbol=symbol,
        cutoff_iso=cutoff_iso,
    )

    depth_rows = _downsample_evenly(
        depth_rows,
        max_points=max_depth_columns,
    )

    depth = [
        _compact_depth_row(row)
        for row in depth_rows
        if row.get("ts")
    ]

    trades = [
        _compact_trade_row(row)
        for row in trade_rows
        if row.get("ts")
    ]

    return {
        "symbol": symbol,
        "minutes": minutes,
        "generated_at_ms": int(now.timestamp() * 1000),
        "depth": depth,
        "trades": trades,
        "depth_count": len(depth),
        "trade_count": len(trades),
    }



HTML = r"""
<div id="axion-b3-root" class="axion-b3">
  <header class="b3-header">
    <div class="brand">
      <div class="brand-mark">A</div>
      <div>
        <div class="brand-title">AXION <span>PRIME</span></div>
        <div class="brand-sub">ORDER FLOW TERMINAL</div>
      </div>
    </div>

    <div class="instrument">
      <div>
        <div class="instrument-main">BTC / USDT <span>★</span></div>
        <div class="instrument-sub">BINANCE SPOT · MARKET DEPTH</div>
      </div>
      <div class="quote">
        <b id="quote-price">—</b>
        <span id="quote-change">—</span>
      </div>
    </div>

    <div class="timeframes" id="timeframes">
      <button data-tf="1m" class="active">1m</button>
      <button data-tf="5m">5m</button>
      <button data-tf="15m">15m</button>
      <button data-tf="30m">30m</button>
      <button data-tf="1H">1H</button>
    </div>

    <div class="header-actions">
      <div class="feed-live"><i></i><span id="feed-status">HIST + LIVE</span></div>
      <button id="fullscreen-btn" type="button">⛶</button>
    </div>
  </header>

  <section class="b3-toolbar">
    <div class="tabs">
      <button class="tab active">Heatmap Order Flow</button>
      <button class="tab">Volumen</button>
      <button class="tab">VWAP</button>
      <button class="tab">Liquidez</button>
    </div>

    <div class="toolbar-controls">
      <span>Intensidad</span>
      <input id="heat-intensity" type="range" min="45" max="100" value="70">
      <span>Histórico</span>
      <strong id="history-label">30m</strong>
    </div>
  </section>

  <main class="b3-workspace">
    <section class="chart-stage">
      <canvas id="heat-canvas"></canvas>
      <canvas id="overlay-canvas"></canvas>

      <div class="price-axis" id="price-axis">
        <span>—</span><span>—</span><span>—</span><span>—</span>
        <span>—</span><span>—</span><span>—</span><span>—</span>
      </div>

      <div class="chart-watermark">
        <b>AXION PRIME</b>
        <span>LIQUIDITY MATRIX</span>
      </div>

      <div class="history-badge">
        <i></i>
        <span id="history-badge-text">Cargando histórico…</span>
      </div>

      <div class="loading-card" id="loading-card">
        <div>AXION ORDER FLOW</div>
        <strong id="loading-title">Cargando profundidad histórica…</strong>
        <span id="loading-message">
          Supabase histórico + Binance live
        </span>
      </div>
    </section>

    <aside class="flow-profile">
      <div class="profile-header">
        <span>FLOW PROFILE</span>
        <small>1s VWAP BINS</small>
      </div>

      <canvas id="profile-canvas"></canvas>

      <div class="profile-footer">
        <div>
          <span>FLOW POC</span>
          <b id="poc-value">—</b>
        </div>
        <div>
          <span>VWAP</span>
          <b id="vwap-value">—</b>
        </div>
        <div>
          <span>SPREAD</span>
          <b id="spread-value">—</b>
        </div>
      </div>
    </aside>
  </main>

  <section class="b3-metrics">
    <article>
      <div class="metric-title bid">LIQUIDEZ COMPRADORA</div>
      <div class="metric-value">
        <b id="bid-value">—</b>
        <span id="bid-pct">—</span>
      </div>
      <div class="bar"><i id="bid-bar"></i></div>
      <div class="metric-foot"><span>Baja</span><span>Alta</span></div>
    </article>

    <article>
      <div class="metric-title ask">LIQUIDEZ VENDEDORA</div>
      <div class="metric-value">
        <b id="ask-value">—</b>
        <span id="ask-pct">—</span>
      </div>
      <div class="bar askbar"><i id="ask-bar"></i></div>
      <div class="metric-foot"><span>Baja</span><span>Alta</span></div>
    </article>

    <article>
      <div class="metric-title delta">DELTA ACUMULADO</div>
      <div class="metric-value">
        <b id="delta-value">—</b>
        <span id="delta-pct">—</span>
      </div>
      <div class="delta-track"><i id="delta-bar"></i></div>
      <div class="metric-foot"><span>Venta</span><span>0</span><span>Compra</span></div>
    </article>

    <article>
      <div class="metric-title session">SESIÓN</div>
      <div class="metric-value single">
        <b id="session-name">—</b>
      </div>
      <div class="session-time" id="session-time">—</div>
      <div class="session-dots"><i></i><i></i><i></i><i></i><i></i></div>
    </article>
  </section>

  <footer class="b3-footer">
    <span id="footer-left">AXION · preparando datos</span>
    <span id="footer-right">UTC —</span>
  </footer>
</div>
"""


CSS = r"""
:host{
  display:block;width:100%;height:100%;
  font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif
}
*{box-sizing:border-box}
button,input{font:inherit}

.axion-b3{
  width:100%;height:820px;min-height:700px;overflow:hidden;
  display:grid;grid-template-rows:64px 44px minmax(0,1fr) 140px 24px;
  color:#dce6f4;background:#02060d;border:1px solid #172338;border-radius:12px
}
.axion-b3:fullscreen{width:100vw;height:100vh;border:0;border-radius:0}

.b3-header{
  display:grid;grid-template-columns:210px 275px minmax(280px,1fr) auto;
  align-items:center;gap:14px;padding:0 14px;
  border-bottom:1px solid #17243a;
  background:linear-gradient(180deg,#07101a,#040a13)
}
.brand{display:flex;align-items:center;gap:10px}
.brand-mark{
  width:38px;height:38px;border-radius:10px;display:grid;place-items:center;
  color:#fff;font-size:20px;font-weight:950;
  border:1px solid rgba(69,213,235,.42);
  background:linear-gradient(145deg,#119dc3,#6151fb);
  box-shadow:0 0 20px rgba(60,161,255,.15)
}
.brand-title{font-size:14px;font-weight:900;letter-spacing:.45px}
.brand-title span{color:#58daed}
.brand-sub{margin-top:2px;font-size:5.5px;color:#617188;letter-spacing:1.45px}

.instrument{
  display:flex;align-items:center;justify-content:space-between;gap:14px;
  padding-left:14px;border-left:1px solid #1a293d
}
.instrument-main{font-size:13px;font-weight:850;color:#edf4fc}
.instrument-main span{color:#e8bc5a}
.instrument-sub{margin-top:3px;font-size:5.5px;color:#687991;letter-spacing:.65px}
.quote{text-align:right}
.quote b{display:block;font-size:17px;font-variant-numeric:tabular-nums}
.quote span{display:block;margin-top:2px;font-size:7px;color:#75859a}

.timeframes{display:flex;align-items:center;justify-content:center;gap:3px}
.timeframes button{
  height:30px;min-width:40px;padding:0 8px;border:0;border-radius:5px;
  background:transparent;color:#718198;cursor:pointer;font-size:8px
}
.timeframes button:hover{background:#0d1724;color:#e1e9f5}
.timeframes button.active{
  color:#59dded;background:#0c2033;box-shadow:inset 0 -2px #43cee7
}

.header-actions{display:flex;align-items:center;gap:10px}
.feed-live{display:flex;align-items:center;gap:6px;font-size:6.5px;color:#72dcb8}
.feed-live i{
  width:7px;height:7px;border-radius:50%;background:#27d49b;
  box-shadow:0 0 10px rgba(39,212,155,.7)
}
#fullscreen-btn{
  width:34px;height:31px;border:1px solid #26374e;border-radius:6px;
  background:#08111d;color:#91a2b9;cursor:pointer
}

.b3-toolbar{
  display:flex;align-items:center;justify-content:space-between;padding:6px 10px;
  border-bottom:1px solid #172439;background:#050b14
}
.tabs{display:flex;gap:4px}
.tab{
  height:30px;padding:0 13px;border:1px solid #1b2a3f;border-radius:5px;
  background:#07101b;color:#73839a;font-size:7px
}
.tab.active{
  color:#effaff;border-color:#3277c5;
  background:linear-gradient(135deg,#155b9f,#485ee1)
}
.toolbar-controls{display:flex;align-items:center;gap:9px;color:#708098;font-size:6.5px}
.toolbar-controls input{width:120px}
.toolbar-controls strong{color:#9fb0c7;font-size:7px}

.b3-workspace{min-width:0;min-height:0;display:grid;grid-template-columns:minmax(0,1fr) 220px}
.chart-stage{
  position:relative;min-width:0;min-height:0;overflow:hidden;
  background:#02060d;border-right:1px solid #18253a
}
#heat-canvas,#overlay-canvas{position:absolute;inset:0;width:100%;height:100%}
#heat-canvas{z-index:1}
#overlay-canvas{z-index:2}

.price-axis{
  position:absolute;right:7px;top:10px;bottom:10px;z-index:5;
  display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end;
  pointer-events:none;color:#8798af;font-size:7px;font-variant-numeric:tabular-nums
}
.price-axis span{padding:2px 5px;border-radius:4px;background:rgba(2,7,13,.68)}

.chart-watermark{
  position:absolute;left:50%;top:50%;z-index:0;transform:translate(-50%,-50%);
  display:flex;flex-direction:column;align-items:center;pointer-events:none;opacity:.035
}
.chart-watermark b{font-size:36px;letter-spacing:2px}
.chart-watermark span{font-size:9px;letter-spacing:4px}

.history-badge{
  position:absolute;left:12px;bottom:10px;z-index:6;
  display:flex;align-items:center;gap:6px;padding:5px 8px;border-radius:6px;
  border:1px solid rgba(67,214,176,.2);background:rgba(4,12,20,.76);
  color:#7e90a7;font-size:6.5px;backdrop-filter:blur(5px)
}
.history-badge i{
  width:5px;height:5px;border-radius:50%;background:#2bd39d;
  box-shadow:0 0 7px rgba(43,211,157,.6)
}

.loading-card{
  position:absolute;left:14px;top:14px;z-index:7;width:285px;
  padding:10px 12px;border:1px solid rgba(55,214,172,.2);border-radius:8px;
  background:rgba(4,12,20,.86);backdrop-filter:blur(7px)
}
.loading-card.hide{display:none}
.loading-card>div{font-size:6px;color:#42dab0;font-weight:900;letter-spacing:.9px}
.loading-card strong{display:block;margin-top:4px;font-size:9px}
.loading-card span{display:block;margin-top:3px;color:#74849a;font-size:6.5px;line-height:1.45}

.flow-profile{position:relative;min-height:0;background:#050b14}
.profile-header{
  height:34px;display:flex;align-items:center;justify-content:space-between;padding:0 10px;
  border-bottom:1px solid #172439;font-size:7px;font-weight:850
}
.profile-header small{font-size:5px;color:#627289}
#profile-canvas{
  position:absolute;left:0;right:0;top:34px;bottom:62px;
  width:100%;height:calc(100% - 96px)
}
.profile-footer{
  position:absolute;left:0;right:0;bottom:0;height:62px;display:grid;
  grid-template-columns:repeat(3,1fr);border-top:1px solid #172439
}
.profile-footer>div{
  display:flex;flex-direction:column;justify-content:center;padding-left:8px;
  border-right:1px solid #172439
}
.profile-footer>div:last-child{border-right:0}
.profile-footer span{font-size:5px;color:#65758b}
.profile-footer b{margin-top:4px;font-size:8px;font-variant-numeric:tabular-nums}

.b3-metrics{
  display:grid;grid-template-columns:1fr 1fr 1fr .82fr;
  border-top:1px solid #18253a;background:#07101a
}
.b3-metrics article{padding:15px 18px;border-right:1px solid #18253a}
.b3-metrics article:last-child{border-right:0}
.metric-title{font-size:7px;font-weight:850;letter-spacing:.25px}
.metric-title.bid{color:#43d9b0}
.metric-title.ask{color:#f05c72}
.metric-title.delta{color:#aa7cff}
.metric-title.session{color:#6ba9ff}
.metric-value{
  margin-top:10px;display:flex;align-items:end;justify-content:space-between;gap:10px
}
.metric-value.single{justify-content:flex-start}
.metric-value b{font-size:18px;color:#eef4fc;font-variant-numeric:tabular-nums}
.metric-value span{font-size:8px;font-weight:850}
.bar,.delta-track{
  position:relative;height:6px;margin-top:11px;overflow:hidden;border-radius:999px;background:#182635
}
.bar i{display:block;width:0;height:100%;background:#38caa7}
.askbar i{background:#e6566d}
.delta-track{
  background:linear-gradient(
    90deg,rgba(145,45,71,.45) 0 49%,#22303d 49% 51%,rgba(30,115,86,.45) 51%
  )
}
.delta-track i{position:absolute;left:50%;top:0;width:0;height:100%;background:#38d39c}
.metric-foot{display:flex;justify-content:space-between;margin-top:5px;color:#617188;font-size:6px}
.session-time{margin-top:4px;color:#708097;font-size:6.5px}
.session-dots{display:flex;gap:4px;margin-top:14px}
.session-dots i{width:5px;height:5px;border-radius:50%;background:#23334b}
.session-dots i:first-child{background:#3971ff}

.b3-footer{
  display:flex;align-items:center;justify-content:space-between;padding:0 10px;
  border-top:1px solid #142137;background:#050a12;color:#627389;font-size:6px
}

@media(max-width:1100px){
  .b3-header{grid-template-columns:180px 230px 1fr auto}
  .b3-workspace{grid-template-columns:minmax(0,1fr) 180px}
}
"""


JS = r"""
export default function(component) {
  const {parentElement,data,setTriggerValue}=component;
  const root=parentElement.querySelector('#axion-b3-root');
  if(!root)return;

  const $=s=>parentElement.querySelector(s);
  const $$=s=>[...parentElement.querySelectorAll(s)];
  const heatCanvas=$('#heat-canvas');
  const overlayCanvas=$('#overlay-canvas');
  const profileCanvas=$('#profile-canvas');
  const hctx=heatCanvas.getContext('2d');
  const octx=overlayCanvas.getContext('2d');
  const pctx=profileCanvas.getContext('2d');

  let destroyed=false;
  let ws=null;
  let reconnectTimer=null;
  let captureTimer=null;
  let drawTimer=null;
  let clockTimer=null;
  let resizeObserver=null;

  let currentTf=String(data?.timeframe||'1m');
  let intensity=.74;

  const history=data?.history||{};
  const DEPTH_RETENTION_MS=Math.max(5,Number(history.minutes||1440))*60_000;

  const MAX_DEPTH_COLS=1800;

  // Historical depth: {t,m,bb,ba,sp,s,x:[[p,b,a,q],...]}
  let depthHistory=Array.isArray(history.depth)?history.depth.slice():[];

  // Historical trade seconds are retained ONLY for delta / volume / flow profile.
  // They are NOT used to build candlesticks anymore.
  let tradeSeconds=Array.isArray(history.trades)?history.trades.slice():[];

  // Candles come exclusively from official Binance Klines.
  let klineCandles=[];
  let klinesReady=false;

  let bids=new Map(),asks=new Map(),lastUpdateId=0,snapshotReady=false,depthBuffer=[];
  let liveTradeSecond=null;
  let firstPrice=null;

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

  // Live capture pushes one column every ~1s. Historical columns loaded from
  // Supabase are pre-aggregated at 1-per-minute. A flat slice(-MAX_DEPTH_COLS)
  // ignores this resolution mismatch: after ~30 minutes of live streaming,
  // the buffer fills entirely with high-frequency live columns and evicts
  // the coarse historical ones, collapsing visible heatmap coverage down to
  // whatever the last MAX_DEPTH_COLS seconds happen to be (~30 min) instead
  // of the intended DEPTH_RETENTION_MS window (hours).
  //
  // Fix: once a column is older than DOWNSAMPLE_AFTER_MS, keep at most one
  // column per DOWNSAMPLE_BUCKET_MS bucket (same 60s granularity as the
  // historical load), so old live columns collapse in place instead of
  // pushing out real history. Recent columns stay at full 1s resolution.
  const DOWNSAMPLE_AFTER_MS=5*60_000;      // keep last 5 min at full resolution
  const DOWNSAMPLE_BUCKET_MS=60_000;       // older than that: 1 column/minute

  function trimHistory(){
    const now=Date.now(),cutoff=now-DEPTH_RETENTION_MS;
    depthHistory=depthHistory.filter(c=>Number(c.t)>=cutoff);
    tradeSeconds=tradeSeconds.filter(r=>Number(r[0])>=cutoff);

    if(depthHistory.length<=MAX_DEPTH_COLS)return;

    const recentStart=now-DOWNSAMPLE_AFTER_MS;
    const recent=[];
    const bucketed=new Map(); // bucketStartMs -> chosen column (latest wins)
    for(const c of depthHistory){
      const t=Number(c.t);
      if(t>=recentStart){recent.push(c);continue}
      const bucket=Math.floor(t/DOWNSAMPLE_BUCKET_MS)*DOWNSAMPLE_BUCKET_MS;
      const existing=bucketed.get(bucket);
      if(!existing||Number(existing.t)<t)bucketed.set(bucket,c);
    }
    const old=[...bucketed.values()].sort((a,b)=>Number(a.t)-Number(b.t));
    depthHistory=old.concat(recent);

    // Safety net only: if something pathological still overflows (e.g. a
    // retention window far longer than MAX_DEPTH_COLS minutes), fall back to
    // trimming the oldest downsampled columns rather than the recent ones.
    if(depthHistory.length>MAX_DEPTH_COLS){
      const overflow=depthHistory.length-MAX_DEPTH_COLS;
      depthHistory=depthHistory.slice(overflow);
    }
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
    const res=await fetch('https://data-api.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=180',{cache:'no-store'});
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
    depthBuffer=[];snapshotReady=true
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
    depthHistory.push(col);trimHistory();updateHistoryWindowLabel();
    drawHeat();drawOverlay()
  }

  function ingestTrade(evt){
    const p=Number(evt.p),q=Number(evt.q),t=Number(evt.T||Date.now());
    if(!Number.isFinite(p)||!Number.isFinite(q))return;
    const sec=Math.floor(t/1000)*1000,buy=!Boolean(evt.m);

    if(!liveTradeSecond||liveTradeSecond[0]!==sec){
      if(liveTradeSecond)tradeSeconds.push(liveTradeSecond);
      liveTradeSecond=[sec,p,p,p,p,0,0,0,0,p,0,0]; // last cell = notional
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

  function binanceInterval(){
    return{'1m':'1m','5m':'5m','15m':'15m','30m':'30m','1H':'1h'}[currentTf]||'1m'
  }

  async function fetchKlines(){
    klinesReady=false;

    const interval=binanceInterval();
    const url=
      `https://data-api.binance.vision/api/v3/klines`+
      `?symbol=BTCUSDT&interval=${encodeURIComponent(interval)}&limit=500`;

    const res=await fetch(url,{cache:'no-store'});
    if(!res.ok)throw new Error('Klines HTTP '+res.status);

    const raw=await res.json();
    if(!Array.isArray(raw))throw new Error('Respuesta Klines inválida');

    klineCandles=raw.map(k=>({
      t:Number(k[0]),
      closeTime:Number(k[6]),
      o:Number(k[1]),
      h:Number(k[2]),
      l:Number(k[3]),
      c:Number(k[4]),
      v:Number(k[5]),
      closed:Number(k[6])<Date.now()
    })).filter(c=>
      Number.isFinite(c.t)&&
      Number.isFinite(c.o)&&c.o>0&&
      Number.isFinite(c.h)&&c.h>0&&
      Number.isFinite(c.l)&&c.l>0&&
      Number.isFinite(c.c)&&c.c>0&&
      c.h>=c.l
    ).sort((a,b)=>a.t-b.t);

    if(klineCandles.length){
      firstPrice=klineCandles[0].o;
      klinesReady=true
    }

    return klineCandles
  }

  function ingestKline(k){
    if(!k)return;

    const candle={
      t:Number(k.t),
      closeTime:Number(k.T),
      o:Number(k.o),
      h:Number(k.h),
      l:Number(k.l),
      c:Number(k.c),
      v:Number(k.v),
      closed:Boolean(k.x)
    };

    if(
      !Number.isFinite(candle.t)||
      !Number.isFinite(candle.o)||candle.o<=0||
      !Number.isFinite(candle.h)||candle.h<=0||
      !Number.isFinite(candle.l)||candle.l<=0||
      !Number.isFinite(candle.c)||candle.c<=0||
      candle.h<candle.l
    )return;

    const idx=klineCandles.findIndex(c=>c.t===candle.t);

    if(idx>=0)klineCandles[idx]=candle;
    else{
      klineCandles.push(candle);
      klineCandles.sort((a,b)=>a.t-b.t)
    }

    // Keep a generous local buffer without growing forever.
    if(klineCandles.length>200)klineCandles=klineCandles.slice(-200);

    if(firstPrice==null&&klineCandles.length)firstPrice=klineCandles[0].o;
    klinesReady=true
  }
  function allTradeRows(){
    const arr=tradeSeconds.slice();
    if(liveTradeSecond)arr.push(liveTradeSecond);
    return arr.sort((a,b)=>a[0]-b[0])
  }
  function candles(){
    return klineCandles
      .filter(c=>
        Number.isFinite(c.t)&&
        Number.isFinite(c.o)&&c.o>0&&
        Number.isFinite(c.h)&&c.h>0&&
        Number.isFinite(c.l)&&c.l>0&&
        Number.isFinite(c.c)&&c.c>0&&
        c.h>=c.l
      )
      .sort((a,b)=>a.t-b.t)
  }

  const TARGET_VISIBLE_CANDLES=120;

  function candleWindow(){
    const cs=candles();
    if(cs.length){
      const visible=cs.slice(-TARGET_VISIBLE_CANDLES);
      const first=visible[0];
      const last=visible[visible.length-1];

      return{
        start:Number(first.t),
        end:Number(last.t)+tfMs(),
        candleCount:visible.length
      }
    }

    const end=Date.now();
    return{
      start:end-tfMs()*TARGET_VISIBLE_CANDLES,
      end,
      candleCount:0
    }
  }

  function updateHistoryWindowLabel(){
    const el=document.getElementById('history-window-label');
    if(!el)return;

    const win=candleWindow();
    const mins=Math.max(1,Math.round((win.end-win.start)/60000));

    el.textContent=
      mins>=1440
        ?`${(mins/1440).toFixed(mins%1440?1:0)}d`
        :mins>=60
          ?`${(mins/60).toFixed(mins%60?1:0)}h`
          :`${mins}m`
  }

  function timeWindow(){
    trimHistory();
    return candleWindow()
  }

  function robustRange(cols,cnds,m){
    const candlePts=[];
    for(const c of cnds){
      if(Number.isFinite(c.h))candlePts.push(c.h);
      if(Number.isFinite(c.l))candlePts.push(c.l);
    }

    let min,max;

    if(candlePts.length){
      candlePts.sort((a,b)=>a-b);
      min=percentile(candlePts,.02);
      max=percentile(candlePts,.98);
    }else{
      const center=Number.isFinite(m)?m:1;
      min=center*.9975;
      max=center*1.0025;
    }

    if(Number.isFinite(m)){
      min=Math.min(min,m);
      max=Math.max(max,m);
    }

    let range=Math.max(max-min,Math.max(Math.abs(m||max),1)*.00045);

    // symmetric breathing room around traded price only
    min-=range*.10;
    max+=range*.10;

    // hard protection against a single malformed candle/spike destroying scale
    const center=Number.isFinite(m)?m:(min+max)/2;
    const maxHalf=Math.max(center*.006,range*.75);
    min=Math.max(min,center-maxHalf);
    max=Math.min(max,center+maxHalf);

    if(!(max>min)){
      min=center*.998;
      max=center*1.002
    }

    return{min,max}
  }


  const HEAT_ROWS=150;
  const HEAT_COLS=300;

  const heatOff=document.createElement('canvas');
  heatOff.width=HEAT_COLS;
  heatOff.height=HEAT_ROWS;
  const heatOctx=heatOff.getContext('2d',{alpha:true});

  function buildObservedBandGrid(cols,minP,maxP,win){
    const grid=new Float32Array(HEAT_ROWS*HEAT_COLS);
    const spanP=Math.max(maxP-minP,1e-9);
    const rowStep=spanP/(HEAT_ROWS-1);

    const colOf=t=>clamp(
      Math.round(((Number(t)-win.start)/(win.end-win.start))*(HEAT_COLS-1)),
      0,HEAT_COLS-1
    );
    const rowOf=p=>clamp(
      Math.round((maxP-Number(p))/rowStep),
      0,HEAT_ROWS-1
    );

    let prevStrong=null;
    let prevCol=null;

    for(const col of cols){
      const c=colOf(col.t);
      const raw=[];

      for(const row of col.x||[]){
        const p=Number(row[0]),q=Number(row[3]);
        if(!(q>0)||p<minP||p>maxP)continue;
        raw.push({r:rowOf(p),q})
      }

      if(!raw.length){
        prevStrong=null;
        prevCol=c;
        continue
      }

      const quantities=raw.map(x=>x.q).sort((a,b)=>a-b);
      const strongThreshold=percentile(quantities,.60)||0;
      const current=new Map();

      for(const x of raw){
        if(x.q<strongThreshold)continue;
        const existing=current.get(x.r)||0;
        if(x.q>existing)current.set(x.r,x.q);
        const idx=x.r*HEAT_COLS+c;
        if(x.q>grid[idx])grid[idx]=x.q
      }

      if(prevStrong&&prevCol!=null){
        const gap=c-prevCol;
        if(gap>0&&gap<=10){
          for(const [r,q] of current.entries()){
            let bestPrev=0;
            for(let dr=-2;dr<=2;dr++){
              bestPrev=Math.max(bestPrev,prevStrong.get(r+dr)||0)
            }
            if(!(bestPrev>0))continue;

            const strength=Math.min(q,bestPrev);
            for(let cc=prevCol;cc<=c;cc++){
              const idx=r*HEAT_COLS+cc;
              if(strength>grid[idx])grid[idx]=strength
            }
          }
        }
      }

      prevStrong=current;
      prevCol=c
    }

    return grid
  }

  function gridQuantiles(grid){
    const vals=[];
    for(let i=0;i<grid.length;i++)if(grid[i]>0)vals.push(grid[i]);
    if(!vals.length)return{q52:1,q80:2,q94:3,q99:4};
    vals.sort((a,b)=>a-b);
    return{
      q52:percentile(vals,.52)||1,
      q80:percentile(vals,.80)||1,
      q94:percentile(vals,.94)||1,
      q99:percentile(vals,.99)||1
    }
  }

  function rasterNorm(v,q){
    if(!(v>0)||v<q.q52)return 0;
    if(v<q.q80)return .16+.26*((v-q.q52)/Math.max(q.q80-q.q52,1e-9));
    if(v<q.q94)return .42+.30*((v-q.q80)/Math.max(q.q94-q.q80,1e-9));
    if(v<q.q99)return .72+.22*((v-q.q94)/Math.max(q.q99-q.q94,1e-9));
    return 1
  }

  function heatColorRGBA(n){
    if(n<=0)return[0,0,0,0];
    let rgba;
    if(n<.28)rgba=[32,51,121,42+n*105];
    else if(n<.50)rgba=[82,52,160,55+n*120];
    else if(n<.70)rgba=[169,49,132,70+n*130];
    else if(n<.86)rgba=[228,67,77,88+n*140];
    else if(n<.96)rgba=[255,126,35,110+n*145];
    else rgba=[255,218,65,160+n*90];
    rgba[3]=clamp(Math.round(rgba[3]*intensity),0,255);
    return rgba
  }

  function paintObservedBandGrid(grid){
    const q=gridQuantiles(grid);
    const img=heatOctx.createImageData(HEAT_COLS,HEAT_ROWS);
    const d=img.data;
    for(let i=0;i<grid.length;i++){
      const n=rasterNorm(grid[i],q);
      const rgba=heatColorRGBA(n),j=i*4;
      d[j]=rgba[0];d[j+1]=rgba[1];d[j+2]=rgba[2];d[j+3]=rgba[3]
    }
    heatOctx.clearRect(0,0,HEAT_COLS,HEAT_ROWS);
    heatOctx.putImageData(img,0,0)
  }

  function heatNorm(value,q50,q85,q97){
    if(!(value>0))return 0;

    // weak liquidity is intentionally invisible
    if(value<q50)return 0;

    if(value<q85){
      return .18 + .22*((value-q50)/Math.max(q85-q50,1e-9))
    }

    if(value<q97){
      return .40 + .35*((value-q85)/Math.max(q97-q85,1e-9))
    }

    return clamp(.78 + .22*((value-q97)/Math.max(q97*.8,1e-9)),0,1)
  }


  function heatColor(n,bias){
    const a=intensity;
    if(n<=0)return'rgba(0,0,0,0)';
    if(n<.30)return`rgba(40,55,124,${(.10+n*.22)*a})`;
    if(n<.52)return`rgba(96,53,156,${(.15+n*.30)*a})`;
    if(n<.72)return`rgba(177,50,126,${(.20+n*.36)*a})`;
    if(n<.88)return`rgba(232,70,73,${(.28+n*.38)*a})`;
    if(n<.97)return`rgba(255,126,35,${(.38+n*.42)*a})`;
    return`rgba(255,215,61,${(.58+n*.34)*a})`
  }

  function drawGrid(ctx,w,h,q){
    ctx.strokeStyle='rgba(45,64,95,.22)';ctx.lineWidth=1*q;
    for(let i=1;i<9;i++){const y=h*i/9;ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke()}
    for(let i=1;i<14;i++){const x=w*i/14;ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke()}
  }

  function drawHeat(){
    resizeCanvas(heatCanvas);
    const q=dpr(),w=heatCanvas.width,h=heatCanvas.height;
    hctx.clearRect(0,0,w,h);hctx.fillStyle='#01050b';hctx.fillRect(0,0,w,h);
    drawGrid(hctx,w,h,q);

    const win=timeWindow(),cols=depthHistory.filter(c=>c.t>=win.start&&c.t<=win.end);
    const cnds=candles().filter(c=>c.t+tfMs()>=win.start&&c.t<=win.end);
    const m=mid()??(cols.length?Number(cols[cols.length-1].m):null);
    const range=robustRange(cols,cnds,m),minP=range.min,maxP=range.max;
    const yOf=p=>h-((p-minP)/(maxP-minP))*h;
    const xOf=t=>((Number(t)-win.start)/(win.end-win.start))*w;

    // Fixed-cost raster heatmap:
    // 260 time cells × 140 price cells, independent of raw history size.
    const grid=buildObservedBandGrid(cols,minP,maxP,win);
    paintObservedBandGrid(grid);

    hctx.save();
    hctx.imageSmoothingEnabled=true;
    hctx.globalAlpha=.96;
    hctx.drawImage(
      heatOff,
      0,0,HEAT_COLS,HEAT_ROWS,
      0,0,w,h
    );
    hctx.restore();

    drawPriceAxis(minP,maxP);
    window.__axionViewport={win,minP,maxP,yOf,xOf,w,h,q,m}
  }

  function drawOverlay(){
    resizeCanvas(overlayCanvas);
    const vp=window.__axionViewport;if(!vp)return;
    const{win,minP,maxP,yOf,xOf,w,h,q}=vp;
    octx.clearRect(0,0,w,h);

    const rows=allTradeRows().filter(r=>r[0]>=win.start&&r[0]<=win.end);
    const cnds=candles().filter(c=>c.t+tfMs()>=win.start&&c.t<=win.end);

    // Window VWAP
    let vol=0,notional=0,buy=0,sell=0;
    for(const r of rows){
      const v=Number(r[5]),vw=Number(r[9]);
      vol+=v;notional+=vw*v;buy+=Number(r[6]);sell+=Number(r[7])
    }
    const vwap=vol>0?notional/vol:null;
    if(Number.isFinite(vwap)&&vwap>=minP&&vwap<=maxP){
      const y=yOf(vwap);octx.strokeStyle='rgba(83,169,255,.64)';octx.lineWidth=1*q;
      octx.setLineDash([7*q,5*q]);octx.beginPath();octx.moveTo(0,y);octx.lineTo(w,y);octx.stroke();
      octx.setLineDash([]);octx.fillStyle='#6eafff';octx.font=`${7*q}px Inter`;octx.fillText('VWAP',8*q,Math.max(11*q,y-4*q))
    }

    // Flow profile / Flow POC using actual 1-second VWAP and real volume.
    const profile=new Map();
    for(const r of rows){
      const p=Number(r[9]),v=Number(r[5]);if(!(p>0)||!(v>0))continue;
      const step=bucketStep(p),bp=Math.round(p/step)*step;
      profile.set(bp,(profile.get(bp)||0)+v)
    }
    const poc=[...profile.entries()].sort((a,b)=>b[1]-a[1])[0];
    if(poc&&poc[0]>=minP&&poc[0]<=maxP){
      const y=yOf(poc[0]);octx.strokeStyle='rgba(246,177,48,.74)';octx.lineWidth=1*q;
      octx.setLineDash([8*q,5*q]);octx.beginPath();octx.moveTo(0,y);octx.lineTo(w,y);octx.stroke();
      octx.setLineDash([]);octx.fillStyle='#f2b33c';octx.font=`${7*q}px Inter`;octx.fillText('FLOW POC',45*q,Math.max(11*q,y-4*q))
    }

    // Candles clearly ABOVE heatmap.
    // Fixed terminal candle width on every timeframe.
    // No dependence on timeframe or visible-hour span.
    const bodyW=2.15*q;
    const wickW=.52*q;

    for(const c of cnds){
      if(![c.o,c.h,c.l,c.c].every(Number.isFinite)||c.h<minP||c.l>maxP)continue;

      const theoreticalCenter=c.t+tfMs()/2;
      const x=xOf(clamp(theoreticalCenter,win.start,win.end));
      if(!Number.isFinite(x)||x<0||x>w)continue;
      const yh=yOf(c.h),yl=yOf(c.l),yo=yOf(c.o),yc=yOf(c.c),up=c.c>=c.o;
      const fill=up?'#21d3a7':'#ef5368';
      const edge=up?'#77e7c5':'#ff8a98';

      // clean wick separator
      octx.strokeStyle='rgba(0,3,8,.96)';
      octx.lineWidth=wickW+.65*q;
      octx.beginPath();octx.moveTo(x,yh);octx.lineTo(x,yl);octx.stroke();

      octx.strokeStyle=edge;
      octx.lineWidth=wickW;
      octx.beginPath();octx.moveTo(x,yh);octx.lineTo(x,yl);octx.stroke();

      const top=Math.min(yo,yc);
      const bodyH=Math.max(.85*q,Math.abs(yc-yo));

      // dark border
      octx.fillStyle='rgba(0,3,8,.98)';
      octx.fillRect(x-bodyW/2-.32*q,top-.32*q,bodyW+.64*q,bodyH+.64*q);

      // candle
      octx.fillStyle=fill;
      octx.fillRect(x-bodyW/2,top,bodyW,bodyH);

      // subtle inner edge
      octx.strokeStyle=edge;
      octx.lineWidth=.55*q;
      octx.strokeRect(
        x-bodyW/2+.3*q,
        top+.3*q,
        Math.max(.8*q,bodyW-.6*q),
        Math.max(.8*q,bodyH-.6*q)
      );
    }

    const m=mid()??vp.m;
    if(Number.isFinite(m)&&m>=minP&&m<=maxP){
      const y=yOf(m);octx.strokeStyle='rgba(246,250,255,.96)';octx.lineWidth=1*q;
      octx.setLineDash([4*q,4*q]);octx.beginPath();octx.moveTo(0,y);octx.lineTo(w,y);octx.stroke();octx.setLineDash([]);
      const label=` ${fmt(m,2)} `;octx.font=`${7.5*q}px Inter`;const tw=octx.measureText(label).width;
      octx.fillStyle='#eaf2fa';octx.fillRect(w-tw-10*q,y-9*q,tw+7*q,14*q);
      octx.fillStyle='#06101a';octx.fillText(label,w-tw-8*q,y+1*q)
    }

    drawProfile(profile,minP,maxP);
    updateUI(rows,poc,vwap)
  }

  function drawPriceAxis(minP,maxP){
    const els=$$('#price-axis span');
    els.forEach((el,i)=>el.textContent=fmt(maxP-(maxP-minP)*(i/Math.max(1,els.length-1)),2))
  }

  function drawProfile(profile,minP,maxP){
    resizeCanvas(profileCanvas);
    const q=dpr(),w=profileCanvas.width,h=profileCanvas.height;
    pctx.clearRect(0,0,w,h);pctx.fillStyle='#050b14';pctx.fillRect(0,0,w,h);
    const rows=[...profile.entries()].filter(([p])=>p>=minP&&p<=maxP);
    if(!rows.length)return;
    const maxV=Math.max(1,...rows.map(x=>x[1])),yOf=p=>h-((p-minP)/(maxP-minP))*h;
    for(const[p,v]of rows){
      const width=(v/maxV)*w*.88,y=yOf(p),bh=Math.max(2*q,h/90);
      const grad=pctx.createLinearGradient(w-width,0,w,0);
      grad.addColorStop(0,'rgba(93,65,175,.28)');grad.addColorStop(.65,'rgba(126,75,199,.62)');grad.addColorStop(1,'rgba(49,206,176,.8)');
      pctx.fillStyle=grad;pctx.fillRect(w-width,y-bh/2,width,bh)
    }
  }

  function updateUI(rows,poc,vwap){
    const book=sortedBook(),m=mid();
    if(Number.isFinite(m)){
      $('#quote-price').textContent=fmt(m,2);
      if(firstPrice){
        const pct=(m-firstPrice)/firstPrice*100,ch=$('#quote-change');
        ch.textContent=`${pct>=0?'+':''}${pct.toFixed(2)}%`;ch.style.color=pct>=0?'#39d5a4':'#f05c72'
      }
    }

    const bidQty=book.bids.slice(0,180).reduce((s,x)=>s+x[1],0);
    const askQty=book.asks.slice(0,180).reduce((s,x)=>s+x[1],0);
    const liq=bidQty+askQty,bp=liq?bidQty/liq:0,ap=liq?askQty/liq:0;
    $('#bid-value').textContent=compact(bidQty)+' BTC';$('#ask-value').textContent=compact(askQty)+' BTC';
    $('#bid-pct').textContent=Math.round(bp*100)+'%';$('#ask-pct').textContent=Math.round(ap*100)+'%';
    $('#bid-bar').style.width=(bp*100)+'%';$('#ask-bar').style.width=(ap*100)+'%';

    let buy=0,sell=0;
    for(const r of rows){buy+=Number(r[6]);sell+=Number(r[7])}
    const delta=buy-sell,total=buy+sell,dp=total?delta/total:0;
    $('#delta-value').textContent=(delta>=0?'+':'')+compact(delta)+' BTC';
    $('#delta-pct').textContent=(dp>=0?'+':'')+(dp*100).toFixed(1)+'%';
    const db=$('#delta-bar'),dw=clamp(Math.abs(dp)*50,0,50);
    db.style.width=dw+'%';db.style.left=dp>=0?'50%':(50-dw)+'%';db.style.background=dp>=0?'#38d39c':'#e5576d';

    $('#poc-value').textContent=poc?fmt(poc[0],2):'—';
    $('#vwap-value').textContent=Number.isFinite(vwap)?fmt(vwap,2):'—';
    $('#spread-value').textContent=book.bids.length&&book.asks.length?fmt(book.asks[0][0]-book.bids[0][0],2):'—';

    const hc=depthHistory.length,tc=tradeSeconds.length;
    $('#history-badge-text').textContent=`HIST ${history.depth_count||0} + LIVE ${Math.max(0,hc-(history.depth_count||0))}`;
    $('#footer-left').textContent=`● Supabase Depth · Binance Klines · aggTrade LIVE`
  }

  function sessionInfo(){
    const d=new Date(),h=d.getUTCHours();let name='Fuera de sesión',range='—';
    if(h>=0&&h<9){name='Asia';range='00:00–09:00 UTC'}
    if(h>=7&&h<16){name='Londres';range='07:00–16:00 UTC'}
    if(h>=13&&h<22){name='Nueva York';range='13:00–22:00 UTC'}
    $('#session-name').textContent=name;$('#session-time').textContent=range;
    const hh=String(d.getUTCHours()).padStart(2,'0'),mm=String(d.getUTCMinutes()).padStart(2,'0'),ss=String(d.getUTCSeconds()).padStart(2,'0');
    $('#footer-right').textContent=`UTC ${hh}:${mm}:${ss}`
  }

  function connect(){
    cleanupSocket();
    $('#loading-card').classList.remove('hide');
    $('#loading-title').textContent='Sincronizando Binance LIVE…';
    $('#loading-message').textContent=`Histórico cargado: ${history.depth_count||0} columnas de depth`;

    Promise.all([fetchSnapshot(),fetchKlines()]).then(()=>{
      $('#feed-status').textContent='HIST + LIVE';
      $('#loading-title').textContent='AXION sincronizado';
      $('#loading-message').textContent='Supabase Depth + Binance Klines + aggTrade LIVE';
      setTimeout(()=>{if(!destroyed)$('#loading-card').classList.add('hide')},250);
      updateHistoryWindowLabel();
      drawHeat();drawOverlay()
    }).catch(err=>{
      console.error(err);$('#feed-status').textContent='ERROR LIVE';
      $('#loading-title').textContent='No se pudo sincronizar Binance';
      $('#loading-message').textContent=String(err?.message||err)
    });

    const kStream=`btcusdt@kline_${binanceInterval()}`;
    ws=new WebSocket(
      `wss://stream.binance.com:9443/stream?streams=`+
      `btcusdt@depth@100ms/btcusdt@aggTrade/${kStream}`
    );
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
      }else if(evt.e==='aggTrade'){
        ingestTrade(evt)
      }else if(evt.e==='kline'){
        ingestKline(evt.k);
        drawHeat();
        drawOverlay()
      }
    };
    ws.onerror=()=>{$('#feed-status').textContent='RECONNECT'};
    ws.onclose=()=>{if(!destroyed)scheduleReconnect()};
    captureTimer=setInterval(captureDepth,1000);
    drawTimer=setInterval(()=>{drawOverlay()},750)
  }

  function reconnectStreamOnly(){
    if(ws){
      try{ws.onclose=null;ws.close()}catch(_){}
      ws=null
    }

    if(captureTimer){
      clearInterval(captureTimer);
      captureTimer=null
    }
    if(drawTimer){
      clearInterval(drawTimer);
      drawTimer=null
    }

    const kStream=`btcusdt@kline_${binanceInterval()}`;
    ws=new WebSocket(
      `wss://stream.binance.com:9443/stream?streams=`+
      `btcusdt@depth@100ms/btcusdt@aggTrade/${kStream}`
    );

    ws.onmessage=e=>{
      const msg=JSON.parse(e.data||'{}'),evt=msg.data||{};
      if(evt.e==='depthUpdate'){
        if(!snapshotReady){
          depthBuffer.push(evt);
          if(depthBuffer.length>3000)depthBuffer.shift()
        }else{
          if(Number(evt.U)>lastUpdateId+1){fetchSnapshot().catch(()=>{});return}
          if(Number(evt.u)>lastUpdateId)applyDepth(evt)
        }
      }else if(evt.e==='aggTrade'){
        ingestTrade(evt)
      }else if(evt.e==='kline'){
        ingestKline(evt.k);
        drawHeat();
        drawOverlay()
      }
    };

    ws.onerror=()=>{$('#feed-status').textContent='RECONNECT'};
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
    currentTf=btn.dataset.tf||'1m';
    updateHistoryWindowLabel();

    // 100% client-side timeframe change:
    // no Streamlit rerun, no Supabase reload, no component reset.
    if(ws){
      try{ws.close()}catch(_){}
      ws=null
    }

    fetchKlines()
      .then(()=>{
        updateHistoryWindowLabel();
        drawHeat();
        drawOverlay();
        reconnectStreamOnly()
      })
      .catch(err=>console.error('Klines timeframe:',err))
  });
  $('#heat-intensity').oninput=e=>{intensity=clamp(Number(e.target.value)/100,.45,1);drawHeat();drawOverlay()};
  $('#fullscreen-btn').onclick=async()=>{try{if(!document.fullscreenElement)await root.requestFullscreen();else await document.exitFullscreen()}catch(_){}};
  sessionInfo();clockTimer=setInterval(sessionInfo,1000);

  if(typeof ResizeObserver!=='undefined'){
    resizeObserver=new ResizeObserver(()=>{drawHeat();drawOverlay()});
    resizeObserver.observe(parentElement.querySelector('.b3-workspace'))
  }

  if(history.error){
    $('#loading-title').textContent='Histórico Supabase no disponible';
    $('#loading-message').textContent=history.error;
    $('#history-badge-text').textContent='SIN HISTÓRICO';
  }else{
    $('#history-badge-text').textContent=`${history.depth_count||0} columnas históricas`;
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
    "axion_orderflow_boceto3_clean_v2",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=True,
)


def _history_minutes_for_timeframe(timeframe: str) -> int:
    # One fixed market window for every timeframe.
    # The timeframe changes candle aggregation, NOT the visible historical span.
    # Recorder retention is currently 6 hours.
    return 360


def _fetch_history_impl() -> dict:
    try:
        return _load_orderflow_history_fast_rpc(
            symbol="BTCUSDT",
            minutes=1440,
            depth_step_seconds=60,
            trade_step_seconds=60,
        )
    except Exception as fast_exc:
        try:
            payload = load_orderflow_history(
                symbol="BTCUSDT",
                minutes=1440,
                max_depth_columns=900,
            )
            payload["source"] = "fallback"
            payload["error"] = f"Fast RPC unavailable: {fast_exc}"
            return payload
        except Exception as exc:
            return {
                "symbol": "BTCUSDT",
                "minutes": 1440,
                "depth": [],
                "trades": [],
                "depth_count": 0,
                "trade_count": 0,
                "source": "error",
                "error": str(exc),
            }


def _history_payload() -> dict:
    now = datetime.now(timezone.utc)
    cached = st.session_state.get("axion_history_cache_v2")

    if cached:
        fetched_at = cached.get("_fetched_at")
        payload = cached.get("payload")
        if (
            isinstance(fetched_at, datetime)
            and payload is not None
            and (now - fetched_at).total_seconds() < 60
        ):
            return payload

    payload = _fetch_history_impl()
    st.session_state["axion_history_cache_v2"] = {
        "_fetched_at": now,
        "payload": payload,
    }
    return payload


def _init_live_state() -> None:
    """Initialize Mercado Live session state without forcing reruns."""
    defaults = {
        "live_timeframe": "1m",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_live_heatmap() -> None:
    _init_live_state()

    history = _history_payload()

    result = _component(
        data={
            "timeframe": st.session_state.live_timeframe,
            "history": history,
        },
        default=None,
        key="axion_boceto3_market_live",
        width="stretch",
        height=820,
    )

    _handle_result(result)
