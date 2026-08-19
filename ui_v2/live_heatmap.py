from __future__ import annotations

import streamlit as st


# ============================================================================
# AXION PRIME — MARKET LIVE / ORDER FLOW
# Clean rebuild
#
# Design rule:
#   1. OrderFlowEngine owns market data + synchronization + aggregation.
#   2. OrderFlowRenderer owns geometry + drawing only.
#   3. No synthetic depth. Historical depth only exists from AXION recording.
# ============================================================================


HTML = r"""
<div id="axion-of-root" class="axion-of">
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">A</div>
      <div>
        <div class="brand-name">AXION <span>PRIME</span></div>
        <div class="brand-sub">MARKET LIVE · ORDER FLOW</div>
      </div>
    </div>

    <div class="instrument">
      <div class="instrument-title">
        <strong>BTC/USDT</strong>
        <span>BINANCE SPOT</span>
      </div>
      <div class="quote">
        <b id="last-price">—</b>
        <small id="quote-change">—</small>
      </div>
    </div>

    <div class="tf-group" id="tf-group">
      <button data-tf="1m" class="active">1m</button>
      <button data-tf="5m">5m</button>
      <button data-tf="15m">15m</button>
      <button data-tf="30m">30m</button>
      <button data-tf="1H">1H</button>
    </div>

    <div class="status-group">
      <span class="live-dot"></span>
      <span id="feed-status">Conectando…</span>
      <button id="fullscreen-btn" type="button">⛶</button>
    </div>
  </header>

  <section class="toolbar">
    <div class="toolbar-left">
      <button class="tool active">Heatmap</button>
      <button class="tool">Volumen</button>
      <button class="tool">VWAP</button>
      <button class="tool">POC</button>
    </div>
    <div class="toolbar-right">
      <span>Intensidad</span>
      <input id="heat-intensity" type="range" min="40" max="100" value="78">
    </div>
  </section>

  <main class="workspace">
    <section class="chart-panel">
      <canvas id="main-canvas"></canvas>

      <div class="price-scale" id="price-scale">
        <span>—</span>
        <span>—</span>
        <span>—</span>
        <span>—</span>
        <span>—</span>
        <span>—</span>
        <span>—</span>
      </div>

      <div class="watermark">
        <b>AXION PRIME</b>
        <span>Order Flow</span>
      </div>

      <div class="recording-pill" id="recording-pill">
        <span class="rec-dot"></span>
        <span id="recording-text">DEPTH REC 0m 00s</span>
      </div>

      <div class="startup-card" id="startup-card">
        <div class="startup-kicker">REAL MARKET DEPTH</div>
        <strong id="startup-title">Sincronizando Binance…</strong>
        <span id="startup-message">
          AXION está construyendo el libro local y la matriz de liquidez.
        </span>
      </div>
    </section>

    <aside class="side-panel">
      <div class="side-title">
        <span>VOLUME PROFILE</span>
        <small>TRADES REALES</small>
      </div>
      <canvas id="profile-canvas"></canvas>

      <div class="side-stats">
        <div>
          <span>POC</span>
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

  <section class="bottom-metrics">
    <article>
      <div class="metric-label buy">LIQUIDEZ BID</div>
      <div class="metric-value-row">
        <b id="bid-liq">—</b>
        <span id="bid-pct">—</span>
      </div>
      <div class="meter"><i id="bid-meter"></i></div>
    </article>

    <article>
      <div class="metric-label sell">LIQUIDEZ ASK</div>
      <div class="metric-value-row">
        <b id="ask-liq">—</b>
        <span id="ask-pct">—</span>
      </div>
      <div class="meter ask"><i id="ask-meter"></i></div>
    </article>

    <article>
      <div class="metric-label delta">DELTA ACUMULADO</div>
      <div class="metric-value-row">
        <b id="delta-value">—</b>
        <span id="delta-pct">—</span>
      </div>
      <div class="delta-meter">
        <i id="delta-bar"></i>
      </div>
    </article>

    <article>
      <div class="metric-label session">SESIÓN</div>
      <div class="metric-value-row single">
        <b id="session-name">—</b>
      </div>
      <div class="session-time" id="session-time">—</div>
    </article>
  </section>

  <footer class="footer">
    <span id="footer-left">AXION · inicializando</span>
    <span id="footer-right">UTC —</span>
  </footer>
</div>
"""


CSS = r"""
:host {
  display: block;
  width: 100%;
  height: 100%;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}

* { box-sizing: border-box; }

button, input { font: inherit; }

.axion-of {
  width: 100%;
  height: 900px;
  min-height: 760px;
  display: grid;
  grid-template-rows: 64px 42px minmax(0, 1fr) 128px 24px;
  overflow: hidden;
  border: 1px solid #172237;
  border-radius: 12px;
  background: #030711;
  color: #dce6f3;
}

.axion-of:fullscreen {
  width: 100vw;
  height: 100vh;
  border: 0;
  border-radius: 0;
}

.topbar {
  display: grid;
  grid-template-columns: 240px 260px 1fr auto;
  align-items: center;
  gap: 14px;
  padding: 0 14px;
  background:
    linear-gradient(180deg, rgba(7, 15, 26, .98), rgba(4, 9, 16, .98));
  border-bottom: 1px solid #182439;
}

.brand {
  display: flex;
  align-items: center;
  gap: 11px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  font-weight: 900;
  font-size: 20px;
  color: white;
  border: 1px solid rgba(70, 215, 239, .42);
  background: linear-gradient(145deg, #0e96c0, #5d4cff);
  box-shadow: 0 0 18px rgba(70, 150, 255, .16);
}

.brand-name {
  font-size: 14px;
  font-weight: 900;
  letter-spacing: .4px;
}

.brand-name span { color: #59d7ec; }

.brand-sub {
  margin-top: 2px;
  font-size: 6px;
  color: #66778f;
  letter-spacing: 1.3px;
}

.instrument {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding-left: 14px;
  border-left: 1px solid #1b293d;
}

.instrument-title strong {
  display: block;
  font-size: 13px;
}

.instrument-title span {
  display: block;
  margin-top: 2px;
  font-size: 6px;
  color: #718198;
  letter-spacing: .7px;
}

.quote {
  text-align: right;
}

.quote b {
  display: block;
  font-size: 16px;
  font-variant-numeric: tabular-nums;
}

.quote small {
  display: block;
  margin-top: 2px;
  font-size: 7px;
  color: #76869a;
}

.tf-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
}

.tf-group button {
  height: 30px;
  min-width: 38px;
  padding: 0 8px;
  border: 0;
  border-radius: 5px;
  background: transparent;
  color: #74849a;
  cursor: pointer;
  font-size: 8px;
}

.tf-group button:hover {
  color: #dfe9f6;
  background: #0d1724;
}

.tf-group button.active {
  color: #58d9ee;
  background: #0d2134;
  box-shadow: inset 0 -2px #43cfe9;
}

.status-group {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7e8da2;
  font-size: 7px;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #25d698;
  box-shadow: 0 0 10px rgba(37, 214, 152, .65);
}

#fullscreen-btn {
  width: 32px;
  height: 30px;
  margin-left: 4px;
  border: 1px solid #26374d;
  border-radius: 6px;
  background: #08111d;
  color: #8fa0b6;
  cursor: pointer;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 10px;
  border-bottom: 1px solid #172338;
  background: #050b14;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tool {
  height: 29px;
  padding: 0 13px;
  border: 1px solid #1c2a3e;
  border-radius: 5px;
  color: #77879d;
  background: #07101b;
  font-size: 7px;
}

.tool.active {
  color: #eaf8ff;
  border-color: #2e74bc;
  background: linear-gradient(135deg, #145594, #485bde);
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 9px;
  color: #718197;
  font-size: 7px;
}

.toolbar-right input { width: 120px; }

.workspace {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 210px;
}

.chart-panel {
  position: relative;
  min-width: 0;
  min-height: 0;
  overflow: hidden;
  background: #02060d;
  border-right: 1px solid #182439;
}

#main-canvas {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.price-scale {
  position: absolute;
  top: 10px;
  right: 7px;
  bottom: 10px;
  z-index: 4;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  color: #8a9ab0;
  font-size: 7px;
  font-variant-numeric: tabular-nums;
  pointer-events: none;
}

.price-scale span {
  padding: 2px 5px;
  border-radius: 4px;
  background: rgba(2, 7, 13, .68);
}

.watermark {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  opacity: .04;
  pointer-events: none;
}

.watermark b {
  font-size: 34px;
  letter-spacing: 2px;
}

.watermark span {
  font-size: 10px;
  letter-spacing: 4px;
}

.recording-pill {
  position: absolute;
  left: 12px;
  bottom: 10px;
  z-index: 5;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border: 1px solid rgba(44, 208, 161, .22);
  border-radius: 6px;
  background: rgba(4, 12, 20, .76);
  color: #7f91a8;
  font-size: 6.5px;
  backdrop-filter: blur(5px);
}

.rec-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #2bd69f;
  box-shadow: 0 0 7px rgba(43, 214, 159, .55);
}

.startup-card {
  position: absolute;
  z-index: 6;
  left: 14px;
  top: 14px;
  width: 260px;
  padding: 10px 12px;
  border: 1px solid rgba(55, 214, 173, .20);
  border-radius: 8px;
  background: rgba(4, 12, 20, .84);
  backdrop-filter: blur(7px);
}

.startup-card.hide { display: none; }

.startup-kicker {
  color: #42dcb0;
  font-size: 6px;
  font-weight: 900;
  letter-spacing: .9px;
}

.startup-card strong {
  display: block;
  margin-top: 4px;
  font-size: 9px;
}

.startup-card span {
  display: block;
  margin-top: 3px;
  color: #75859b;
  font-size: 6.5px;
  line-height: 1.4;
}

.side-panel {
  position: relative;
  min-height: 0;
  background: #050b14;
}

.side-title {
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  border-bottom: 1px solid #172439;
  font-size: 7px;
  font-weight: 800;
}

.side-title small {
  color: #64748a;
  font-size: 5.5px;
}

#profile-canvas {
  position: absolute;
  left: 0;
  right: 0;
  top: 34px;
  bottom: 62px;
  width: 100%;
  height: calc(100% - 96px);
}

.side-stats {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 62px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  border-top: 1px solid #172439;
}

.side-stats > div {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-left: 8px;
  border-right: 1px solid #172439;
}

.side-stats > div:last-child { border-right: 0; }

.side-stats span {
  color: #64758b;
  font-size: 5.5px;
}

.side-stats b {
  margin-top: 4px;
  font-size: 8px;
  font-variant-numeric: tabular-nums;
}

.bottom-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border-top: 1px solid #182439;
  background: #07101a;
}

.bottom-metrics article {
  padding: 14px 18px;
  border-right: 1px solid #182439;
}

.bottom-metrics article:last-child { border-right: 0; }

.metric-label {
  font-size: 7px;
  font-weight: 800;
  letter-spacing: .3px;
}

.metric-label.buy { color: #43d9b0; }
.metric-label.sell { color: #f05d73; }
.metric-label.delta { color: #aa7cff; }
.metric-label.session { color: #6da9ff; }

.metric-value-row {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
  margin-top: 10px;
}

.metric-value-row.single { justify-content: flex-start; }

.metric-value-row b {
  font-size: 17px;
  color: #edf4fc;
  font-variant-numeric: tabular-nums;
}

.metric-value-row span {
  font-size: 8px;
  font-weight: 800;
}

.meter,
.delta-meter {
  position: relative;
  height: 6px;
  margin-top: 11px;
  overflow: hidden;
  border-radius: 999px;
  background: #182635;
}

.meter i {
  display: block;
  height: 100%;
  width: 0;
  background: #36caa5;
}

.meter.ask i { background: #e8566c; }

.delta-meter {
  background:
    linear-gradient(
      90deg,
      rgba(145, 45, 71, .46) 0 49%,
      #22303d 49% 51%,
      rgba(30, 115, 86, .45) 51%
    );
}

.delta-meter i {
  position: absolute;
  top: 0;
  left: 50%;
  width: 0;
  height: 100%;
  background: #38d39c;
}

.session-time {
  margin-top: 4px;
  color: #718197;
  font-size: 6.5px;
}

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 10px;
  border-top: 1px solid #152136;
  background: #050a12;
  color: #64758b;
  font-size: 6px;
}

@media (max-width: 1100px) {
  .topbar {
    grid-template-columns: 190px 220px 1fr auto;
  }

  .workspace {
    grid-template-columns: minmax(0, 1fr) 175px;
  }
}
"""


JS = r"""
export default function(component) {
  const { parentElement, data, setTriggerValue } = component;

  const root = parentElement.querySelector('#axion-of-root');
  const mainCanvas = parentElement.querySelector('#main-canvas');
  const profileCanvas = parentElement.querySelector('#profile-canvas');

  if (!root || !mainCanvas || !profileCanvas) return;

  const ctx = mainCanvas.getContext('2d');
  const pctx = profileCanvas.getContext('2d');

  let destroyed = false;
  let raf = null;
  let resizeObserver = null;
  let clockTimer = null;

  // =========================================================================
  // Utility
  // =========================================================================

  const $ = (selector) => parentElement.querySelector(selector);
  const $$ = (selector) => [...parentElement.querySelectorAll(selector)];

  const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

  const fmt = (v, d = 2) => {
    if (!Number.isFinite(v)) return '—';
    return v.toLocaleString('en-US', {
      minimumFractionDigits: d,
      maximumFractionDigits: d,
    });
  };

  const compact = (v) => {
    if (!Number.isFinite(v)) return '—';
    const a = Math.abs(v);
    if (a >= 1e9) return `${(v / 1e9).toFixed(2)}B`;
    if (a >= 1e6) return `${(v / 1e6).toFixed(2)}M`;
    if (a >= 1e3) return `${(v / 1e3).toFixed(2)}K`;
    return v.toFixed(2);
  };

  const percentile = (sorted, p) => {
    if (!sorted.length) return 0;
    const i = clamp(Math.floor((sorted.length - 1) * p), 0, sorted.length - 1);
    return sorted[i];
  };

  const dpr = () => clamp(window.devicePixelRatio || 1, 1, 2);

  const resizeCanvas = (canvas) => {
    const r = canvas.getBoundingClientRect();
    const q = dpr();
    const w = Math.max(1, Math.round(r.width * q));
    const h = Math.max(1, Math.round(r.height * q));

    if (canvas.width !== w || canvas.height !== h) {
      canvas.width = w;
      canvas.height = h;
    }
  };

  // =========================================================================
  // OrderFlowEngine
  // =========================================================================

  class OrderFlowEngine {
    constructor() {
      this.symbol = 'BTCUSDT';
      this.requestedTf = String(data?.timeframe || '1m');

      this.ws = null;
      this.reconnectTimer = null;
      this.captureTimer = null;

      this.snapshotReady = false;
      this.depthBuffer = [];
      this.lastUpdateId = 0;

      this.bids = new Map();
      this.asks = new Map();

      this.depthHistory = [];
      this.baseCandles = [];

      this.buyAgg = 0;
      this.sellAgg = 0;
      this.tradeValue = 0;
      this.tradeQty = 0;

      this.profile = new Map();
      this.profileBuy = new Map();
      this.profileSell = new Map();

      this.firstPrice = null;
      this.lastTradePrice = null;

      this.storageKey = 'axion_orderflow_clean_v1_btcusdt';
      this.maxDepthColumns = 900;
      this.maxStorageAgeMs = 6 * 60 * 60 * 1000;
      this.maxRenderWindowMs = 15 * 60 * 1000;

      this.onChange = () => {};

      this.restore();
    }

    now() {
      return Date.now();
    }

    sortedBook() {
      return {
        bids: [...this.bids.entries()].sort((a, b) => b[0] - a[0]),
        asks: [...this.asks.entries()].sort((a, b) => a[0] - b[0]),
      };
    }

    mid() {
      const { bids, asks } = this.sortedBook();
      if (!bids.length || !asks.length) return null;
      return (bids[0][0] + asks[0][0]) / 2;
    }

    spread() {
      const { bids, asks } = this.sortedBook();
      if (!bids.length || !asks.length) return null;
      return asks[0][0] - bids[0][0];
    }

    visibleWindow() {
      if (!this.depthHistory.length) return null;

      const end = Number(this.depthHistory[this.depthHistory.length - 1].t);
      const first = Number(this.depthHistory[0].t);

      return {
        start: Math.max(first, end - this.maxRenderWindowMs),
        end,
      };
    }

    recordedDurationMs() {
      const win = this.visibleWindow();
      return win ? Math.max(0, win.end - win.start) : 0;
    }

    requestedTfMs() {
      return {
        '1m': 60_000,
        '5m': 300_000,
        '15m': 900_000,
        '30m': 1_800_000,
        '1H': 3_600_000,
      }[this.requestedTf] || 60_000;
    }

    effectiveTf() {
      const dur = this.recordedDurationMs();

      if (this.requestedTf === '1m') return '1m';
      if (this.requestedTf === '5m' && dur >= 10 * 60_000) return '5m';
      if (this.requestedTf === '15m' && dur >= 30 * 60_000) return '15m';
      if (this.requestedTf === '30m' && dur >= 60 * 60_000) return '30m';
      if (this.requestedTf === '1H' && dur >= 120 * 60_000) return '1H';

      return '1m';
    }

    effectiveTfMs() {
      return {
        '1m': 60_000,
        '5m': 300_000,
        '15m': 900_000,
        '30m': 1_800_000,
        '1H': 3_600_000,
      }[this.effectiveTf()] || 60_000;
    }

    bucketStep(price) {
      if (!Number.isFinite(price) || price <= 0) return 1;

      // BTC/USDT practical heatmap aggregation.
      if (price >= 100_000) return 10;
      if (price >= 50_000) return 5;
      if (price >= 20_000) return 2;
      if (price >= 5_000) return 1;
      return 0.5;
    }

    bucketPrice(price, step) {
      return Math.round(price / step) * step;
    }

    normalizeLevels(raw) {
      if (!Array.isArray(raw)) return [];

      return raw
        .map((x) => [Number(x[0]), Number(x[1])])
        .filter(
          ([p, q]) =>
            Number.isFinite(p) &&
            Number.isFinite(q) &&
            p > 0 &&
            q >= 0
        );
    }

    applySide(map, raw) {
      for (const [p, q] of this.normalizeLevels(raw)) {
        if (q === 0) map.delete(p);
        else map.set(p, q);
      }
    }

    applyDepthEvent(evt) {
      this.applySide(this.bids, evt.b);
      this.applySide(this.asks, evt.a);
      this.lastUpdateId = Number(evt.u || this.lastUpdateId);
    }

    aggregateBook() {
      const mid = this.mid();
      if (mid == null) return null;

      const step = this.bucketStep(mid);
      const { bids, asks } = this.sortedBook();
      const buckets = new Map();

      const add = (side, levels) => {
        for (const [price, qty] of levels.slice(0, 500)) {
          if (!(qty > 0)) continue;

          const p = this.bucketPrice(price, step);

          let row = buckets.get(p);
          if (!row) {
            row = { p, bid: 0, ask: 0, total: 0 };
            buckets.set(p, row);
          }

          row[side] += qty;
          row.total += qty;
        }
      };

      add('bid', bids);
      add('ask', asks);

      return {
        t: this.now(),
        mid,
        step,
        buckets: [...buckets.values()].sort((a, b) => a.p - b.p),
      };
    }

    captureDepth() {
      if (!this.snapshotReady) return;

      const col = this.aggregateBook();
      if (!col || !col.buckets.length) return;

      this.depthHistory.push(col);

      if (this.depthHistory.length > this.maxDepthColumns) {
        this.depthHistory.splice(
          0,
          this.depthHistory.length - this.maxDepthColumns
        );
      }

      this.persist();
      this.onChange();
    }

    buildBaseCandle(price, qty, ts) {
      const minute = 60_000;
      const t = Math.floor(ts / minute) * minute;

      let candle =
        this.baseCandles.length > 0
          ? this.baseCandles[this.baseCandles.length - 1]
          : null;

      if (!candle || candle.t !== t) {
        candle = {
          t,
          firstObserved: ts,
          lastObserved: ts,
          o: price,
          h: price,
          l: price,
          c: price,
          v: qty,
        };

        this.baseCandles.push(candle);

        if (this.baseCandles.length > 500) {
          this.baseCandles.splice(0, this.baseCandles.length - 500);
        }
      } else {
        candle.h = Math.max(candle.h, price);
        candle.l = Math.min(candle.l, price);
        candle.c = price;
        candle.v += qty;
        candle.lastObserved = ts;
      }
    }

    ingestTrade(evt, buildCandle = true) {
      const price = Number(evt.p);
      const qty = Number(evt.q);
      const ts = Number(evt.T || this.now());

      if (!Number.isFinite(price) || !Number.isFinite(qty)) return;

      const aggressiveBuy = !Boolean(evt.m);

      if (aggressiveBuy) this.buyAgg += qty;
      else this.sellAgg += qty;

      this.tradeValue += price * qty;
      this.tradeQty += qty;

      this.lastTradePrice = price;
      if (this.firstPrice == null) this.firstPrice = price;

      const step = this.bucketStep(price);
      const bin = this.bucketPrice(price, step);

      this.profile.set(bin, (this.profile.get(bin) || 0) + qty);

      if (aggressiveBuy) {
        this.profileBuy.set(bin, (this.profileBuy.get(bin) || 0) + qty);
      } else {
        this.profileSell.set(bin, (this.profileSell.get(bin) || 0) + qty);
      }

      if (buildCandle) this.buildBaseCandle(price, qty, ts);

      this.onChange();
    }

    candles() {
      const tfMs = this.effectiveTfMs();
      const grouped = [];

      for (const src of this.baseCandles) {
        const t = Math.floor(src.t / tfMs) * tfMs;

        let dst = grouped.length ? grouped[grouped.length - 1] : null;

        if (!dst || dst.t !== t) {
          dst = {
            t,
            firstObserved: src.firstObserved,
            lastObserved: src.lastObserved,
            o: src.o,
            h: src.h,
            l: src.l,
            c: src.c,
            v: src.v,
          };

          grouped.push(dst);
        } else {
          dst.h = Math.max(dst.h, src.h);
          dst.l = Math.min(dst.l, src.l);
          dst.c = src.c;
          dst.v += src.v;
          dst.lastObserved = src.lastObserved;
        }
      }

      const win = this.visibleWindow();

      if (!win) return grouped.slice(-1);

      return grouped.filter((c) => {
        const end = Number(c.lastObserved || c.t + tfMs);
        return end >= win.start && c.t <= win.end;
      });
    }

    stats() {
      const { bids, asks } = this.sortedBook();

      const bidQty = bids
        .slice(0, 180)
        .reduce((acc, x) => acc + x[1], 0);

      const askQty = asks
        .slice(0, 180)
        .reduce((acc, x) => acc + x[1], 0);

      const liqTotal = bidQty + askQty;
      const delta = this.buyAgg - this.sellAgg;
      const tradeTotal = this.buyAgg + this.sellAgg;

      const vwap =
        this.tradeQty > 0 ? this.tradeValue / this.tradeQty : null;

      const profileSorted = [...this.profile.entries()].sort(
        (a, b) => b[1] - a[1]
      );

      return {
        mid: this.mid(),
        spread: this.spread(),
        bidQty,
        askQty,
        bidPct: liqTotal > 0 ? bidQty / liqTotal : 0,
        askPct: liqTotal > 0 ? askQty / liqTotal : 0,
        delta,
        deltaPct: tradeTotal > 0 ? delta / tradeTotal : 0,
        vwap,
        poc: profileSorted.length ? profileSorted[0][0] : null,
        firstPrice: this.firstPrice,
        effectiveTf: this.effectiveTf(),
        requestedTf: this.requestedTf,
      };
    }

    async fetchSnapshot() {
      const url =
        'https://data-api.binance.vision/api/v3/depth?symbol=BTCUSDT&limit=1000';

      const res = await fetch(url, { cache: 'no-store' });

      if (!res.ok) {
        throw new Error(`Depth HTTP ${res.status}`);
      }

      const snap = await res.json();

      const bids = new Map();
      const asks = new Map();

      for (const [p, q] of this.normalizeLevels(snap.bids)) {
        if (q > 0) bids.set(p, q);
      }

      for (const [p, q] of this.normalizeLevels(snap.asks)) {
        if (q > 0) asks.set(p, q);
      }

      this.bids = bids;
      this.asks = asks;
      this.lastUpdateId = Number(snap.lastUpdateId || 0);

      this.depthBuffer = this.depthBuffer.filter(
        (evt) => Number(evt.u) > this.lastUpdateId
      );

      let startIndex = -1;

      for (let i = 0; i < this.depthBuffer.length; i += 1) {
        const evt = this.depthBuffer[i];

        if (
          Number(evt.U) <= this.lastUpdateId + 1 &&
          Number(evt.u) >= this.lastUpdateId + 1
        ) {
          startIndex = i;
          break;
        }
      }

      if (startIndex >= 0) {
        for (let i = startIndex; i < this.depthBuffer.length; i += 1) {
          const evt = this.depthBuffer[i];

          if (Number(evt.u) > this.lastUpdateId) {
            this.applyDepthEvent(evt);
          }
        }
      }

      this.depthBuffer = [];
      this.snapshotReady = true;
    }

    async fetchRecentTrades() {
      const url =
        'https://data-api.binance.vision/api/v3/aggTrades?symbol=BTCUSDT&limit=1000';

      const res = await fetch(url, { cache: 'no-store' });

      if (!res.ok) {
        throw new Error(`aggTrades HTTP ${res.status}`);
      }

      const rows = await res.json();

      // These are used for initial POC / VWAP / delta context only.
      // They do NOT build candles because they predate AXION depth recording.
      for (const row of rows) {
        this.ingestTrade(row, false);
      }
    }

    handleDepth(evt) {
      if (!this.snapshotReady) {
        this.depthBuffer.push(evt);

        if (this.depthBuffer.length > 5000) {
          this.depthBuffer.shift();
        }

        return;
      }

      const expected = this.lastUpdateId + 1;
      const U = Number(evt.U);
      const u = Number(evt.u);

      if (u < expected) return;

      if (U > expected) {
        this.snapshotReady = false;

        this.fetchSnapshot().catch(() => {
          this.scheduleReconnect();
        });

        return;
      }

      this.applyDepthEvent(evt);
    }

    connect() {
      this.disconnectSocketOnly();

      this.snapshotReady = false;
      this.depthBuffer = [];

      Promise.all([
        this.fetchSnapshot(),
        this.fetchRecentTrades(),
      ])
        .then(() => {
          setFeedUI(
            'ok',
            'BTC/USDT conectado',
            'Depth + aggTrades reales. Grabando matriz de liquidez.'
          );

          this.onChange();
        })
        .catch((err) => {
          console.error('AXION initial sync:', err);

          setFeedUI(
            'error',
            'No se pudo sincronizar Binance',
            String(err?.message || err)
          );
        });

      const streams =
        'btcusdt@depth@100ms/btcusdt@aggTrade';

      this.ws = new WebSocket(
        `wss://stream.binance.com:9443/stream?streams=${streams}`
      );

      this.ws.onmessage = (event) => {
        if (destroyed) return;

        let packet;

        try {
          packet = JSON.parse(event.data);
        } catch (_) {
          return;
        }

        const evt = packet.data || packet;

        if (evt.e === 'depthUpdate') {
          this.handleDepth(evt);
        } else if (evt.e === 'aggTrade') {
          this.ingestTrade(evt, true);
        }
      };

      this.ws.onerror = () => {
        setFeedUI(
          'error',
          'Conexión interrumpida',
          'AXION intentará reconectar automáticamente.'
        );
      };

      this.ws.onclose = () => {
        if (!destroyed) this.scheduleReconnect();
      };

      if (this.captureTimer) clearInterval(this.captureTimer);

      this.captureTimer = setInterval(() => {
        this.captureDepth();
      }, 1000);
    }

    scheduleReconnect() {
      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
      }

      this.reconnectTimer = setTimeout(() => {
        this.connect();
      }, 1800);
    }

    disconnectSocketOnly() {
      if (this.ws) {
        try {
          this.ws.onclose = null;
          this.ws.close();
        } catch (_) {}

        this.ws = null;
      }

      if (this.reconnectTimer) {
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = null;
      }
    }

    setTf(tf) {
      this.requestedTf = tf;
      this.onChange();
    }

    restore() {
      try {
        const raw = localStorage.getItem(this.storageKey);
        if (!raw) return;

        const payload = JSON.parse(raw);
        if (!payload) return;

        const cutoff = this.now() - this.maxStorageAgeMs;

        if (Array.isArray(payload.depthHistory)) {
          this.depthHistory = payload.depthHistory
            .filter(
              (col) =>
                Number(col?.t) >= cutoff &&
                Array.isArray(col?.buckets)
            )
            .slice(-this.maxDepthColumns);
        }

        if (Array.isArray(payload.baseCandles)) {
          this.baseCandles = payload.baseCandles
            .filter(
              (c) =>
                Number(c?.t) >= cutoff &&
                [c.o, c.h, c.l, c.c].every(Number.isFinite)
            )
            .slice(-500);
        }
      } catch (err) {
        console.warn('AXION restore:', err);
      }
    }

    persist() {
      try {
        const cutoff = this.now() - this.maxStorageAgeMs;

        const depthHistory = this.depthHistory
          .filter((col) => Number(col.t) >= cutoff)
          .slice(-this.maxDepthColumns);

        const baseCandles = this.baseCandles
          .filter((c) => Number(c.t) >= cutoff)
          .slice(-500);

        localStorage.setItem(
          this.storageKey,
          JSON.stringify({
            version: 1,
            savedAt: this.now(),
            depthHistory,
            baseCandles,
          })
        );
      } catch (err) {
        console.warn('AXION persist:', err);
      }
    }

    destroy() {
      this.persist();

      this.disconnectSocketOnly();

      if (this.captureTimer) {
        clearInterval(this.captureTimer);
        this.captureTimer = null;
      }
    }
  }

  // =========================================================================
  // OrderFlowRenderer
  // =========================================================================

  class OrderFlowRenderer {
    constructor(engine) {
      this.engine = engine;
      this.heatIntensity = 0.78;
      this.pending = false;
    }

    requestDraw() {
      if (this.pending) return;

      this.pending = true;

      raf = requestAnimationFrame(() => {
        this.pending = false;

        if (!destroyed) {
          this.draw();
        }
      });
    }

    robustPriceRange(history, candles, mid) {
      const samples = [];

      for (const col of history) {
        if (!Array.isArray(col.buckets)) continue;

        for (const row of col.buckets) {
          if (Number.isFinite(row.p)) samples.push(row.p);
        }

        if (Number.isFinite(col.mid)) samples.push(col.mid);
      }

      for (const c of candles) {
        if (Number.isFinite(c.h)) samples.push(c.h);
        if (Number.isFinite(c.l)) samples.push(c.l);
      }

      if (!samples.length) {
        const center = mid || 1;

        return {
          min: center * 0.997,
          max: center * 1.003,
        };
      }

      samples.sort((a, b) => a - b);

      let min = percentile(samples, 0.015);
      let max = percentile(samples, 0.985);

      if (Number.isFinite(mid)) {
        const half = Math.max(
          Math.abs(mid - min),
          Math.abs(max - mid),
          mid * 0.0012
        );

        min = mid - half;
        max = mid + half;
      }

      const range = Math.max(max - min, (mid || max) * 0.001);
      const pad = range * 0.07;

      return {
        min: min - pad,
        max: max + pad,
      };
    }

    heatNorm(value, q50, q85, q97) {
      if (!(value > 0)) return 0;

      const lv = Math.log1p(value);
      const a = Math.log1p(Math.max(q50, 1e-9));
      const b = Math.log1p(Math.max(q85, q50, 1e-9));
      const c = Math.log1p(Math.max(q97, q85, 1e-9));

      if (lv <= a) {
        return 0.08 + 0.24 * (lv / Math.max(a, 1e-9));
      }

      if (lv <= b) {
        return 0.32 + 0.28 * ((lv - a) / Math.max(b - a, 1e-9));
      }

      if (lv <= c) {
        return 0.60 + 0.26 * ((lv - b) / Math.max(c - b, 1e-9));
      }

      return clamp(
        0.86 + 0.14 * ((lv - c) / Math.max(c * 0.18, 1e-9)),
        0,
        1
      );
    }

    heatColor(n, bias) {
      const alphaScale = this.heatIntensity;

      if (n < 0.18) {
        return `rgba(19,24,64,${(0.10 + n * 0.55) * alphaScale})`;
      }

      if (n < 0.38) {
        if (bias < -0.2) {
          return `rgba(31,80,127,${(0.15 + n * 0.65) * alphaScale})`;
        }

        if (bias > 0.2) {
          return `rgba(81,43,132,${(0.15 + n * 0.65) * alphaScale})`;
        }

        return `rgba(65,43,124,${(0.15 + n * 0.65) * alphaScale})`;
      }

      if (n < 0.58) {
        return `rgba(136,47,148,${(0.18 + n * 0.62) * alphaScale})`;
      }

      if (n < 0.78) {
        return `rgba(217,58,82,${(0.22 + n * 0.60) * alphaScale})`;
      }

      if (n < 0.92) {
        return `rgba(255,112,40,${(0.30 + n * 0.52) * alphaScale})`;
      }

      return `rgba(255,207,49,${(0.40 + n * 0.44) * alphaScale})`;
    }

    drawGrid(w, h, q) {
      ctx.strokeStyle = 'rgba(48,67,98,.22)';
      ctx.lineWidth = 1 * q;

      for (let i = 1; i < 8; i += 1) {
        const y = (h * i) / 8;

        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      for (let i = 1; i < 12; i += 1) {
        const x = (w * i) / 12;

        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, h);
        ctx.stroke();
      }
    }

    draw() {
      resizeCanvas(mainCanvas);
      resizeCanvas(profileCanvas);

      const q = dpr();
      const w = mainCanvas.width;
      const h = mainCanvas.height;

      ctx.clearRect(0, 0, w, h);

      ctx.fillStyle = '#02060d';
      ctx.fillRect(0, 0, w, h);

      this.drawGrid(w, h, q);

      const engine = this.engine;
      const stats = engine.stats();
      const win = engine.visibleWindow();

      const history = win
        ? engine.depthHistory.filter(
            (col) => Number(col.t) >= win.start && Number(col.t) <= win.end
          )
        : [];

      const candles = engine.candles();

      const range = this.robustPriceRange(
        history,
        candles,
        stats.mid
      );

      const minP = range.min;
      const maxP = range.max;

      const yOf = (price) =>
        h - ((price - minP) / (maxP - minP)) * h;

      this.drawHeatmap(history, win, minP, maxP, yOf, w, h, q);
      this.drawVWAP(stats, yOf, minP, maxP, w, q);
      this.drawPOC(stats, yOf, minP, maxP, w, q);
      this.drawCandles(candles, win, yOf, minP, maxP, w, q);
      this.drawCurrentPrice(stats, yOf, minP, maxP, w, q);
      this.drawPriceScale(minP, maxP);
      this.drawProfile(stats, minP, maxP);

      updateMetricUI(engine, stats);
    }

    drawHeatmap(history, win, minP, maxP, yOf, w, h, q) {
      if (!history.length || !win) return;

      const totals = [];

      for (const col of history) {
        for (const row of col.buckets || []) {
          if (
            row.p >= minP &&
            row.p <= maxP &&
            row.total > 0
          ) {
            totals.push(row.total);
          }
        }
      }

      totals.sort((a, b) => a - b);

      const q50 = percentile(totals, 0.50) || 1;
      const q85 = percentile(totals, 0.85) || q50;
      const q97 = percentile(totals, 0.97) || q85;

      const span = Math.max(1000, win.end - win.start);
      const xOf = (t) =>
        ((Number(t) - win.start) / span) * w;

      for (let i = 0; i < history.length; i += 1) {
        const col = history[i];

        const x = xOf(col.t);

        const nextT =
          i < history.length - 1
            ? Number(history[i + 1].t)
            : Math.min(win.end, Number(col.t) + 1000);

        const x2 = xOf(nextT);

        const cw = Math.max(1 * q, x2 - x + 0.6 * q);

        const step =
          Number(col.step) ||
          this.engine.bucketStep(Number(col.mid));

        const mid =
          Number(col.mid) ||
          (minP + maxP) / 2;

        const bucketH = Math.max(
          1.8 * q,
          Math.abs(yOf(mid + step) - yOf(mid)) * 0.88
        );

        for (const row of col.buckets || []) {
          if (
            row.p < minP ||
            row.p > maxP ||
            !(row.total > 0)
          ) {
            continue;
          }

          const norm = this.heatNorm(
            row.total,
            q50,
            q85,
            q97
          );

          const bias =
            (row.bid - row.ask) /
            Math.max(row.total, 1e-9);

          ctx.fillStyle = this.heatColor(norm, bias);

          ctx.fillRect(
            x,
            yOf(row.p) - bucketH / 2,
            cw,
            bucketH
          );
        }
      }
    }

    drawCandles(candles, win, yOf, minP, maxP, w, q) {
      if (!candles.length || !win) return;

      const span = Math.max(1000, win.end - win.start);
      const xOf = (t) =>
        ((Number(t) - win.start) / span) * w;

      const tfMs = this.engine.effectiveTfMs();

      const theoreticalWidth =
        (tfMs / span) * w;

      const bodyW = clamp(
        theoreticalWidth * 0.42,
        3.5 * q,
        9 * q
      );

      const wickW = clamp(
        bodyW * 0.18,
        1 * q,
        1.6 * q
      );

      for (const c of candles) {
        if (
          ![c.o, c.h, c.l, c.c].every(Number.isFinite)
        ) {
          continue;
        }

        if (c.h < minP || c.l > maxP) continue;

        const observedStart = clamp(
          Number(c.firstObserved || c.t),
          win.start,
          win.end
        );

        const observedEnd = clamp(
          Number(c.lastObserved || c.t),
          win.start,
          win.end
        );

        const x = xOf(
          (observedStart + observedEnd) / 2
        );

        if (!Number.isFinite(x) || x < 0 || x > w) {
          continue;
        }

        const yh = yOf(c.h);
        const yl = yOf(c.l);
        const yo = yOf(c.o);
        const yc = yOf(c.c);

        const up = c.c >= c.o;

        const fill = up ? '#27d7ad' : '#ef5368';
        const edge = up ? '#7ce9ca' : '#ff8e9d';

        // Dark halo wick.
        ctx.strokeStyle = 'rgba(1,6,12,.94)';
        ctx.lineWidth = wickW + 1.5 * q;

        ctx.beginPath();
        ctx.moveTo(x, yh);
        ctx.lineTo(x, yl);
        ctx.stroke();

        // Real wick.
        ctx.strokeStyle = edge;
        ctx.lineWidth = wickW;

        ctx.beginPath();
        ctx.moveTo(x, yh);
        ctx.lineTo(x, yl);
        ctx.stroke();

        const top = Math.min(yo, yc);
        const bodyH = Math.max(
          2.2 * q,
          Math.abs(yc - yo)
        );

        // Dark body border.
        ctx.fillStyle = 'rgba(1,6,12,.95)';
        ctx.fillRect(
          x - bodyW / 2 - 0.8 * q,
          top - 0.8 * q,
          bodyW + 1.6 * q,
          bodyH + 1.6 * q
        );

        // Candle.
        ctx.fillStyle = fill;
        ctx.fillRect(
          x - bodyW / 2,
          top,
          bodyW,
          bodyH
        );
      }
    }

    drawVWAP(stats, yOf, minP, maxP, w, q) {
      if (
        !Number.isFinite(stats.vwap) ||
        stats.vwap < minP ||
        stats.vwap > maxP
      ) {
        return;
      }

      const y = yOf(stats.vwap);

      ctx.strokeStyle = 'rgba(78,168,255,.72)';
      ctx.lineWidth = 1 * q;
      ctx.setLineDash([7 * q, 5 * q]);

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      ctx.setLineDash([]);

      ctx.fillStyle = '#69adff';
      ctx.font = `${7 * q}px Inter`;

      ctx.fillText(
        'VWAP',
        8 * q,
        Math.max(11 * q, y - 4 * q)
      );
    }

    drawPOC(stats, yOf, minP, maxP, w, q) {
      if (
        !Number.isFinite(stats.poc) ||
        stats.poc < minP ||
        stats.poc > maxP
      ) {
        return;
      }

      const y = yOf(stats.poc);

      ctx.strokeStyle = 'rgba(246,177,48,.88)';
      ctx.lineWidth = 1 * q;
      ctx.setLineDash([7 * q, 5 * q]);

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      ctx.setLineDash([]);

      ctx.fillStyle = '#f2b33c';
      ctx.font = `${7 * q}px Inter`;

      ctx.fillText(
        'POC',
        44 * q,
        Math.max(11 * q, y - 4 * q)
      );
    }

    drawCurrentPrice(stats, yOf, minP, maxP, w, q) {
      if (
        !Number.isFinite(stats.mid) ||
        stats.mid < minP ||
        stats.mid > maxP
      ) {
        return;
      }

      const y = yOf(stats.mid);

      ctx.strokeStyle = 'rgba(241,247,253,.88)';
      ctx.lineWidth = 1 * q;
      ctx.setLineDash([4 * q, 4 * q]);

      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();

      ctx.setLineDash([]);

      const label = ` ${fmt(stats.mid, 2)} `;

      ctx.font = `${7.5 * q}px Inter`;

      const tw = ctx.measureText(label).width;

      ctx.fillStyle = '#eaf1f8';

      ctx.fillRect(
        w - tw - 9 * q,
        y - 9 * q,
        tw + 6 * q,
        14 * q
      );

      ctx.fillStyle = '#07101a';

      ctx.fillText(
        label,
        w - tw - 7 * q,
        y + 1 * q
      );
    }

    drawPriceScale(minP, maxP) {
      const els = $$('#price-scale span');

      els.forEach((el, i) => {
        const p =
          maxP -
          (maxP - minP) *
            (i / Math.max(1, els.length - 1));

        el.textContent = fmt(p, 2);
      });
    }

    drawProfile(stats, minP, maxP) {
      resizeCanvas(profileCanvas);

      const q = dpr();
      const w = profileCanvas.width;
      const h = profileCanvas.height;

      pctx.clearRect(0, 0, w, h);

      pctx.fillStyle = '#050b14';
      pctx.fillRect(0, 0, w, h);

      const rows = [...this.engine.profile.entries()]
        .filter(([price]) => price >= minP && price <= maxP);

      if (!rows.length) return;

      const maxV = Math.max(
        1,
        ...rows.map((x) => x[1])
      );

      const yOf = (price) =>
        h -
        ((price - minP) / (maxP - minP)) *
          h;

      for (const [price, volume] of rows) {
        const buy =
          this.engine.profileBuy.get(price) || 0;

        const sell =
          this.engine.profileSell.get(price) || 0;

        const total = Math.max(volume, 1e-9);
        const width = (volume / maxV) * w * 0.88;
        const y = yOf(price);
        const bh = Math.max(2 * q, h / 95);

        const left = w - width;

        pctx.fillStyle =
          'rgba(103,76,185,.46)';

        pctx.fillRect(
          left,
          y - bh / 2,
          width,
          bh
        );

        if (buy >= sell) {
          const bw = width * (buy / total);

          pctx.fillStyle =
            'rgba(47,202,171,.72)';

          pctx.fillRect(
            w - bw,
            y - bh / 2,
            bw,
            bh
          );
        } else {
          const sw = width * (sell / total);

          pctx.fillStyle =
            'rgba(226,82,101,.72)';

          pctx.fillRect(
            w - sw,
            y - bh / 2,
            sw,
            bh
          );
        }
      }

      if (
        Number.isFinite(stats.poc) &&
        stats.poc >= minP &&
        stats.poc <= maxP
      ) {
        const y = yOf(stats.poc);

        pctx.strokeStyle =
          'rgba(245,176,47,.92)';

        pctx.lineWidth = 1 * q;
        pctx.setLineDash([5 * q, 4 * q]);

        pctx.beginPath();
        pctx.moveTo(0, y);
        pctx.lineTo(w, y);
        pctx.stroke();

        pctx.setLineDash([]);
      }
    }
  }

  // =========================================================================
  // UI adapters
  // =========================================================================

  function setFeedUI(kind, title, message) {
    const card = $('#startup-card');
    const titleEl = $('#startup-title');
    const messageEl = $('#startup-message');
    const statusEl = $('#feed-status');

    titleEl.textContent = title;
    messageEl.textContent = message;

    if (kind === 'ok') {
      statusEl.textContent = 'LIVE · Binance';
      statusEl.style.color = '#38d5a3';

      setTimeout(() => {
        if (!destroyed) {
          card.classList.add('hide');
        }
      }, 2500);
    } else {
      card.classList.remove('hide');

      statusEl.textContent =
        kind === 'error'
          ? 'Reconectando…'
          : 'Conectando…';

      statusEl.style.color =
        kind === 'error'
          ? '#ef6d7f'
          : '#8a9ab0';
    }
  }

  function sessionInfo() {
    const d = new Date();
    const h = d.getUTCHours();

    let name = 'Fuera de sesión';
    let range = '—';

    if (h >= 0 && h < 9) {
      name = 'Asia';
      range = '00:00–09:00 UTC';
    }

    if (h >= 7 && h < 16) {
      name = 'Londres';
      range = '07:00–16:00 UTC';
    }

    if (h >= 13 && h < 22) {
      name = 'Nueva York';
      range = '13:00–22:00 UTC';
    }

    $('#session-name').textContent = name;
    $('#session-time').textContent = range;

    const hh = String(d.getUTCHours()).padStart(2, '0');
    const mm = String(d.getUTCMinutes()).padStart(2, '0');
    const ss = String(d.getUTCSeconds()).padStart(2, '0');

    $('#footer-right').textContent =
      `UTC ${hh}:${mm}:${ss}`;
  }

  function updateMetricUI(engine, stats) {
    if (Number.isFinite(stats.mid)) {
      $('#last-price').textContent =
        fmt(stats.mid, 2);

      if (Number.isFinite(stats.firstPrice)) {
        const pct =
          ((stats.mid - stats.firstPrice) /
            stats.firstPrice) *
          100;

        const ch = $('#quote-change');

        ch.textContent =
          `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`;

        ch.style.color =
          pct >= 0 ? '#37d6a2' : '#f05b70';
      }
    }

    $('#bid-liq').textContent =
      `${compact(stats.bidQty)} BTC`;

    $('#ask-liq').textContent =
      `${compact(stats.askQty)} BTC`;

    $('#bid-pct').textContent =
      `${Math.round(stats.bidPct * 100)}%`;

    $('#ask-pct').textContent =
      `${Math.round(stats.askPct * 100)}%`;

    $('#bid-meter').style.width =
      `${stats.bidPct * 100}%`;

    $('#ask-meter').style.width =
      `${stats.askPct * 100}%`;

    $('#delta-value').textContent =
      `${stats.delta >= 0 ? '+' : ''}${compact(stats.delta)} BTC`;

    $('#delta-pct').textContent =
      `${stats.deltaPct >= 0 ? '+' : ''}${(stats.deltaPct * 100).toFixed(1)}%`;

    const deltaBar = $('#delta-bar');
    const deltaWidth =
      clamp(Math.abs(stats.deltaPct) * 50, 0, 50);

    deltaBar.style.width = `${deltaWidth}%`;

    deltaBar.style.left =
      stats.deltaPct >= 0
        ? '50%'
        : `${50 - deltaWidth}%`;

    deltaBar.style.background =
      stats.deltaPct >= 0
        ? '#38d39c'
        : '#e5576d';

    $('#poc-value').textContent =
      Number.isFinite(stats.poc)
        ? fmt(stats.poc, 2)
        : '—';

    $('#vwap-value').textContent =
      Number.isFinite(stats.vwap)
        ? fmt(stats.vwap, 2)
        : '—';

    $('#spread-value').textContent =
      Number.isFinite(stats.spread)
        ? fmt(stats.spread, 2)
        : '—';

    const dur = engine.recordedDurationMs();
    const totalSec = Math.floor(dur / 1000);
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;

    $('#recording-text').textContent =
      `DEPTH REC ${mins}m ${String(secs).padStart(2, '0')}s`;

    const eff = stats.effectiveTf;

    $('#footer-left').textContent =
      stats.requestedTf === eff
        ? `● Binance Spot · ${eff} · recorder activo`
        : `● Binance Spot · ${stats.requestedTf} → ${eff} efectivo · recorder activo`;
  }

  // =========================================================================
  // Init
  // =========================================================================

  const engine = new OrderFlowEngine();
  const renderer = new OrderFlowRenderer(engine);

  engine.onChange = () => {
    renderer.requestDraw();
  };

  $$('#tf-group button').forEach((btn) => {
    btn.onclick = () => {
      $$('#tf-group button').forEach((x) =>
        x.classList.remove('active')
      );

      btn.classList.add('active');

      const tf = btn.dataset.tf || '1m';

      engine.setTf(tf);

      setTriggerValue('timeframe', tf);

      renderer.requestDraw();
    };
  });

  $('#heat-intensity').oninput = (event) => {
    renderer.heatIntensity =
      clamp(
        Number(event.target.value) / 100,
        0.4,
        1
      );

    renderer.requestDraw();
  };

  $('#fullscreen-btn').onclick = async () => {
    try {
      if (!document.fullscreenElement) {
        await root.requestFullscreen();
      } else {
        await document.exitFullscreen();
      }
    } catch (_) {}
  };

  sessionInfo();

  clockTimer = setInterval(
    sessionInfo,
    1000
  );

  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      renderer.requestDraw();
    });

    resizeObserver.observe(
      parentElement.querySelector('.workspace')
    );
  }

  resizeCanvas(mainCanvas);
  resizeCanvas(profileCanvas);

  renderer.requestDraw();

  setFeedUI(
    'loading',
    'Sincronizando Binance…',
    'Construyendo libro local y matriz de liquidez.'
  );

  engine.connect();

  return () => {
    destroyed = true;

    if (raf) cancelAnimationFrame(raf);
    if (clockTimer) clearInterval(clockTimer);

    resizeObserver?.disconnect();

    engine.destroy();
  };
}
"""


_component = st.components.v2.component(
    "axion_orderflow_clean_rebuild_v1",
    html=HTML,
    css=CSS,
    js=JS,
    isolate_styles=True,
)


def render_axion_live_heatmap(
    *,
    timeframe: str = "1m",
    key: str = "axion_orderflow_clean",
    height: int = 900,
):
    """
    Render the AXION PRIME order-flow workspace.

    Notes
    -----
    - BTC/USDT market depth comes from Binance Spot public market data.
    - No synthetic market depth is generated.
    - Historical depth only exists from the moment AXION records it.
    - Candles are built only from live aggTrade events captured while depth
      recording is active, so candle time and heatmap time remain aligned.
    """
    return _component(
        data={
            "timeframe": timeframe,
        },
        default=None,
        key=key,
        width="stretch",
        height=height,
    )


def _init_live_state() -> None:
    if "live_timeframe" not in st.session_state:
        st.session_state.live_timeframe = "1m"


def _handle_component_result(result) -> None:
    if result is None:
        return

    timeframe = getattr(result, "timeframe", None)

    if (
        timeframe
        and timeframe != st.session_state.live_timeframe
    ):
        st.session_state.live_timeframe = timeframe
        st.rerun()


def render_live_heatmap() -> None:
    """
    Entry point imported by ui_v2/dashboard.py.
    """
    _init_live_state()

    result = render_axion_live_heatmap(
        timeframe=st.session_state.live_timeframe,
        key="axion_market_live_orderflow",
        height=900,
    )

    _handle_component_result(result)
