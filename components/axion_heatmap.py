from __future__ import annotations

import streamlit as st


HTML = r"""
<div class="axion-live-shell" id="axion-live-shell">
  <header class="live-header">
    <div class="live-brand">
      <div class="brand-emblem">
        <span class="brand-a">A</span>
        <i></i>
      </div>
      <div class="brand-copy">
        <div class="brand-name">AXION <span>PRIME</span></div>
        <div class="brand-sub">MARKET INTELLIGENCE · ORDER FLOW</div>
      </div>
    </div>

    <div class="market-identity">
      <div class="market-symbol-row">
        <span class="market-orb">◎</span>
        <strong id="instrument-name">XAU/USD</strong>
        <span class="market-badge">GOLD</span>
      </div>
      <div class="market-desc" id="instrument-sub">Oro / Dólar estadounidense</div>
    </div>

    <div class="market-quote">
      <div class="quote-price" id="header-price">—</div>
      <div class="quote-change waiting" id="header-change">Esperando feed</div>
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

    <div class="terminal-status">
      <div class="status-chip">
        <span class="status-led amber"></span>
        <div><b>MARKET DEPTH</b><small>PENDIENTE</small></div>
      </div>
      <div class="status-chip session-chip">
        <span class="status-led cyan"></span>
        <div><b>SESIÓN</b><small id="header-session">—</small></div>
      </div>
      <div class="server-clock">
        <span>SERVER</span>
        <b id="server-clock">--:--:--</b>
      </div>
    </div>

    <div class="header-actions">
      <button class="header-action" type="button" title="Replay">↺ <span>Replay</span></button>
      <button class="header-action" type="button" title="Backtesting">⌁ <span>Backtesting</span></button>
      <button class="icon-btn" id="fullscreen-btn" type="button" title="Pantalla completa">⛶</button>
    </div>
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
  grid-template-rows:58px minmax(0,1fr);
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
  position:relative;
  display:grid;
  grid-template-columns:210px 190px 118px minmax(290px,1fr) auto auto;
  align-items:center;
  gap:12px;
  min-height:58px;
  padding:0 12px 0 15px;
  border-bottom:1px solid rgba(75,105,160,.28);
  background:
    radial-gradient(circle at 15% 0%,rgba(52,210,235,.11),transparent 28%),
    radial-gradient(circle at 80% 0%,rgba(112,79,255,.10),transparent 25%),
    linear-gradient(180deg,#08111e 0%,#040a13 100%);
  box-shadow:0 8px 28px rgba(0,0,0,.18);
}
.live-header:after{
  content:"";
  position:absolute;
  left:0;right:0;bottom:-1px;height:1px;
  background:linear-gradient(90deg,transparent,#24d4ec 22%,#745cff 72%,transparent);
  opacity:.42;
}
.live-brand{display:flex;align-items:center;gap:10px;min-width:0}
.brand-emblem{
  position:relative;
  width:34px;height:34px;
  display:grid;place-items:center;
  border:1px solid rgba(73,207,234,.48);
  border-radius:11px;
  background:
    radial-gradient(circle at 30% 20%,rgba(77,225,243,.28),transparent 38%),
    linear-gradient(145deg,#0b2130,#13133a);
  box-shadow:0 0 24px rgba(43,207,236,.13),inset 0 0 18px rgba(80,108,255,.12);
}
.brand-emblem:before{
  content:"";position:absolute;inset:4px;border:1px solid rgba(120,102,255,.26);
  border-radius:8px;transform:rotate(45deg)
}
.brand-emblem i{
  position:absolute;width:6px;height:6px;border-radius:50%;right:-2px;top:-2px;
  background:#28e7a2;box-shadow:0 0 12px #28e7a2
}
.brand-a{position:relative;z-index:2;font-size:19px;font-weight:950;color:#eefaff}
.brand-name{font-size:15px;font-weight:920;letter-spacing:.8px;color:#f5f8ff}
.brand-name span{color:#5ee0f0}
.brand-sub{font-size:5.8px;letter-spacing:1.7px;color:#697a95;margin-top:2px;white-space:nowrap}

.market-identity{
  min-width:0;
  padding-left:13px;
  border-left:1px solid rgba(80,106,151,.28)
}
.market-symbol-row{display:flex;align-items:center;gap:6px}
.market-orb{color:#f6c757;font-size:14px}
.market-symbol-row strong{font-size:13px;color:#f4f7fc;letter-spacing:.2px}
.market-badge{
  padding:3px 5px;border-radius:4px;
  color:#f3c75c;background:rgba(244,190,68,.08);border:1px solid rgba(244,190,68,.23);
  font-size:5.5px;font-weight:900;letter-spacing:.6px
}
.market-desc{margin-top:2px;color:#657792;font-size:7px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}

.market-quote{min-width:0}
.quote-price{
  font-size:17px;font-weight:920;line-height:1;color:#f4f8ff;letter-spacing:.2px
}
.quote-change{margin-top:4px;font-size:6.5px;font-weight:850}
.quote-change.waiting{color:#c5a35c}
.quote-change.positive{color:#31d99a}
.quote-change.negative{color:#ff6078}

.tf-nav{
  display:flex;align-items:center;justify-content:center;
  gap:1px;min-width:0;
  padding:3px;
  border:1px solid rgba(70,96,139,.22);
  border-radius:8px;
  background:rgba(5,12,22,.58)
}
.tf-nav button{
  position:relative;
  height:29px;min-width:34px;padding:0 7px;
  border:0;border-radius:5px;
  color:#72819a;background:transparent;cursor:pointer;font-size:8px
}
.tf-nav button:hover{background:#111b29;color:#dfe9f7}
.tf-nav button.active{
  color:#66deef;background:linear-gradient(180deg,#102a40,#0c1c2e);
  box-shadow:inset 0 0 0 1px rgba(66,201,228,.18)
}
.tf-nav button.active:after{
  content:"";position:absolute;left:8px;right:8px;bottom:-4px;height:2px;border-radius:2px;
  background:#43d8ed;box-shadow:0 0 8px rgba(67,216,237,.55)
}

.terminal-status{display:flex;align-items:center;gap:5px}
.status-chip{
  height:32px;display:flex;align-items:center;gap:6px;
  padding:0 8px;border:1px solid #26364d;border-radius:7px;background:rgba(7,15,26,.84)
}
.status-chip b{display:block;color:#aeb9c9;font-size:6px;letter-spacing:.65px}
.status-chip small{display:block;color:#717e93;font-size:5.5px;margin-top:1px}
.status-led{width:6px;height:6px;border-radius:50%;flex:0 0 6px}
.status-led.amber{background:#e3b75d;box-shadow:0 0 9px rgba(227,183,93,.55)}
.status-led.cyan{background:#45d8ec;box-shadow:0 0 9px rgba(69,216,236,.48)}
.server-clock{
  height:32px;min-width:67px;padding:6px 8px;
  border:1px solid #26364d;border-radius:7px;background:rgba(7,15,26,.84)
}
.server-clock span{display:block;color:#5f6e84;font-size:5px;letter-spacing:.7px}
.server-clock b{display:block;margin-top:2px;color:#dce5f2;font-size:7px;font-variant-numeric:tabular-nums}

.header-actions{display:flex;align-items:center;gap:5px}
.header-action,.icon-btn{
  height:32px;border:1px solid #263a54;border-radius:7px;
  color:#9cabbe;background:linear-gradient(180deg,#0b1624,#07101c);
  cursor:pointer
}
.header-action{padding:0 9px;font-size:7px}
.header-action span{margin-left:3px}
.header-action:hover,.icon-btn:hover{
  color:#eef7ff;border-color:#3d617f;background:#0e1d2e
}
.icon-btn{width:34px;padding:0;font-size:14px}

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
.side-btn span{font-size:6.5px}
.side-btn:hover{background:#111a28;color:#dce6f5}
.side-btn.active{color:#55d7eb;background:#0b1c2c;box-shadow:inset 2px 0 #45d7ef}
.side-spacer{flex:1}

.live-main{
  grid-column:2;grid-row:2;min-width:0;min-height:0;
  display:grid;grid-template-rows:44px minmax(0,1fr) 138px
}
.module-tabs{
  min-width:0;display:flex;align-items:center;gap:8px;
  padding:6px 9px;border-bottom:1px solid rgba(65,90,132,.26);background:#060c15
}
.tab-group{display:flex;align-items:center;gap:4px;min-width:0;overflow-x:auto;scrollbar-width:none}
.tab-group::-webkit-scrollbar{display:none}
.module-tab{
  height:28px;padding:0 10px;border:1px solid transparent;border-radius:5px;
  color:#738198;background:transparent;cursor:pointer;font-size:8px;white-space:nowrap
}
.module-tab:hover{background:#0d1725;color:#d9e4f4}
.module-tab.active{background:#10213a;border-color:#255d8a;color:#59d9ec}
.toolbar-right{margin-left:auto;display:flex;align-items:center;gap:7px}
.toolbar-right select{
  height:28px;border:1px solid #24364f;border-radius:6px;background:#08111e;color:#c8d4e5;
  padding:0 8px;font-size:8px
}
.slider-control{
  height:28px;display:flex;align-items:center;gap:7px;padding:0 8px;
  border:1px solid #24364f;border-radius:6px;color:#718099;font-size:7px
}
.slider-control input{width:90px}

.terminal-workspace{
  min-height:0;min-width:0;
  display:grid;grid-template-columns:minmax(0,1fr) 230px;
  background:#030812
}
.chart-area{position:relative;min-width:0;min-height:0;border-right:1px solid rgba(65,90,132,.24)}
.chart-head{
  position:absolute;top:0;left:0;right:0;height:34px;z-index:4;
  display:flex;align-items:center;justify-content:space-between;padding:0 10px;
  border-bottom:1px solid rgba(65,90,132,.15);background:rgba(3,8,18,.88);
  color:#73839b;font-size:8px
}
.chart-head strong{font-size:12px;color:#eef4fc}
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
  width:min(430px,62%);padding:18px 22px;text-align:center;
  border:1px solid rgba(78,106,154,.30);border-radius:12px;
  background:rgba(5,12,22,.88);backdrop-filter:blur(8px);
  box-shadow:0 18px 45px rgba(0,0,0,.28)
}
.warning-eyebrow{font-size:7px;font-weight:900;letter-spacing:1.4px;color:#54d8ec}
.feed-warning strong{display:block;margin-top:6px;font-size:13px;color:#eef4fc}
.feed-warning p{margin:7px auto 0;max-width:360px;color:#718098;font-size:7.5px;line-height:1.5}
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
.profile-head strong{font-size:9px;color:#dfe7f3}
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
  .live-header{grid-template-columns:210px 180px 120px minmax(260px,1fr) auto}
  .terminal-status{display:none}
  .header-action span{display:none}
  .module-tab:nth-child(n+4){display:none}
  .terminal-workspace{grid-template-columns:minmax(0,1fr) 190px}
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

  function updateServerClock(){
    const d=new Date();
    const hh=String(d.getHours()).padStart(2,'0');
    const mm=String(d.getMinutes()).padStart(2,'0');
    const ss=String(d.getSeconds()).padStart(2,'0');
    const clock=parentElement.querySelector('#server-clock');
    if(clock) clock.textContent=`${hh}:${mm}:${ss}`;

    const hour=d.getUTCHours();
    let session='Fuera de sesión';
    if(hour>=21 || hour<6) session='Sídney';
    if(hour>=0 && hour<9) session='Tokio';
    if(hour>=7 && hour<16) session='Londres';
    if(hour>=13 && hour<22) session='Nueva York';
    const sessionEl=parentElement.querySelector('#header-session');
    if(sessionEl) sessionEl.textContent=session;
  }
  updateServerClock();
  const clockTimer=setInterval(updateServerClock,1000);

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

  return ()=>{clearInterval(clockTimer)};
}
"""

_component = st.components.v2.component(
    "axion_live_heatmap_v4",
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
    height: int = 860,
):
    """
    Renderiza AXION LIVE / Heatmap V4.
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
