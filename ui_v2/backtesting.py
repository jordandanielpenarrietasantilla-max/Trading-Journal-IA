from __future__ import annotations

from datetime import date, timedelta
import json
import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.backtest_engine import TradePlan, evaluate_trade
from core.market_data import MarketDataError, fetch_recent_klines, get_backtest_dataset, resolve_symbol
from ui_v2.theme import apply_v2_theme


BACKTEST_CSS = """
<style>
.ax-bt-hero {
    margin-bottom: 16px;
    padding: 20px 22px;
    background:
        radial-gradient(circle at 86% 18%, rgba(255,209,102,.10), transparent 25%),
        radial-gradient(circle at 10% 0%, rgba(25,228,255,.10), transparent 28%),
        linear-gradient(145deg, rgba(7,16,36,.98), rgba(3,8,20,.99));
    border:1px solid rgba(78,128,210,.34);
    border-radius:20px;
}
.ax-bt-kicker {color:#19e4ff;font-size:9px;font-weight:950;letter-spacing:2px;}
.ax-bt-title {margin-top:7px;color:#f7f9ff;font-size:34px;font-weight:950;letter-spacing:-1.4px;}
.ax-bt-sub {margin-top:7px;color:#91a0bf;font-size:12px;line-height:1.55;}
.ax-bt-badges {display:flex;flex-wrap:wrap;gap:7px;margin-top:12px;}
.ax-bt-badge {padding:5px 9px;border-radius:999px;border:1px solid rgba(25,228,255,.25);background:rgba(25,228,255,.07);color:#b9f7ff;font-size:8px;font-weight:900;letter-spacing:.7px;}
.ax-bt-badge.gold {border-color:rgba(255,209,102,.32);background:rgba(255,209,102,.08);color:#ffe6a1;}
.ax-bt-panel-title {margin:12px 0 8px;color:#f3f6ff;font-size:11px;font-weight:950;letter-spacing:.9px;}
.ax-bt-source {padding:10px 12px;border:1px solid rgba(0,245,138,.25);background:rgba(0,245,138,.055);border-radius:12px;color:#a7fbd2;font-size:9px;}
.ax-bt-warning {padding:10px 12px;border:1px solid rgba(255,209,102,.27);background:rgba(255,209,102,.055);border-radius:12px;color:#e5d9b5;font-size:9px;line-height:1.5;}
.ax-bt-metric-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:12px 0 16px;}
.ax-bt-metric {padding:13px;border:1px solid rgba(77,111,179,.28);background:linear-gradient(145deg,rgba(9,18,39,.95),rgba(4,9,23,.96));border-radius:14px;}
.ax-bt-metric small {display:block;color:#71809f;font-size:7px;font-weight:900;letter-spacing:1px;}
.ax-bt-metric strong {display:block;margin-top:6px;color:#f7f9ff;font-size:18px;font-weight:950;}
.ax-bt-metric span {display:block;margin-top:4px;color:#19e4ff;font-size:8px;}
@media(max-width:850px){.ax-bt-metric-grid{grid-template-columns:repeat(2,minmax(0,1fr));}.ax-bt-title{font-size:28px;}}
</style>
"""


def _init_bt_state() -> None:
    defaults = {
        "bt_symbol": "BTCUSDT",
        "bt_mode": "REPLAY",
        "bt_date": date.today() - timedelta(days=30),
        "bt_interval": "1H",
        "bt_dataset": None,
        "bt_market": None,
        "bt_cursor": 120,
        "bt_speed": 1,
        "bt_trade": None,
        "bt_trade_result": None,
        "bt_favorites": ["BTCUSDT", "ETHUSDT"],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _fmt_price(value: float) -> str:
    if value >= 1000:
        return f"{value:,.2f}"
    if value >= 1:
        return f"{value:,.4f}"
    return f"{value:.6f}"


def _candles_for_chart(frame: pd.DataFrame) -> list[dict]:
    data: list[dict] = []
    for _, row in frame.iterrows():
        data.append({
            "time": int(pd.Timestamp(row["open_time"]).timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        })
    return data


def _volume_for_chart(frame: pd.DataFrame) -> list[dict]:
    result = []
    for _, row in frame.iterrows():
        up = float(row["close"]) >= float(row["open"])
        result.append({
            "time": int(pd.Timestamp(row["open_time"]).timestamp()),
            "value": float(row["volume"]),
            "color": "rgba(0,245,138,0.33)" if up else "rgba(255,23,68,0.32)",
        })
    return result


def _render_chart(frame: pd.DataFrame, symbol_label: str, interval: str, trade: dict | None) -> None:
    candles = json.dumps(_candles_for_chart(frame))
    volumes = json.dumps(_volume_for_chart(frame))
    markers = []
    if trade:
        markers.append({
            "time": int(pd.Timestamp(trade["created_at"]).timestamp()),
            "position": "belowBar" if trade["direction"] == "LONG" else "aboveBar",
            "color": "#00f58a" if trade["direction"] == "LONG" else "#ff1744",
            "shape": "arrowUp" if trade["direction"] == "LONG" else "arrowDown",
            "text": trade["direction"],
        })
    markers_json = json.dumps(markers)

    html = f"""
    <div style="font-family:Inter,system-ui;background:#030712;border:1px solid rgba(75,112,184,.34);border-radius:16px;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;border-bottom:1px solid rgba(75,112,184,.18);background:linear-gradient(90deg,#071125,#050915);">
        <div><strong style="color:#f7f9ff;font-size:12px">{symbol_label} · {interval}</strong><div style="color:#667694;font-size:9px;margin-top:3px">HISTORICAL REPLAY · FUTURE DATA HIDDEN</div></div>
        <div style="color:#00f58a;font-size:9px;font-weight:800">● VERIFIED OHLCV</div>
      </div>
      <div id="chart" style="height:560px;width:100%;"></div>
    </div>
    <script src="https://unpkg.com/lightweight-charts@4.2.3/dist/lightweight-charts.standalone.production.js"></script>
    <script>
      const container = document.getElementById('chart');
      const chart = LightweightCharts.createChart(container, {{
        layout: {{ background: {{ type:'solid', color:'#030712' }}, textColor:'#8fa0be' }},
        grid: {{ vertLines: {{ color:'rgba(58,83,132,.12)' }}, horzLines: {{ color:'rgba(58,83,132,.12)' }} }},
        rightPriceScale: {{ borderColor:'rgba(72,105,170,.25)' }},
        timeScale: {{ borderColor:'rgba(72,105,170,.25)', timeVisible:true, secondsVisible:false, rightOffset:5 }},
        crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
      }});
      const candles = chart.addCandlestickSeries({{
        upColor:'#00f58a', downColor:'#ff3158', wickUpColor:'#00f58a', wickDownColor:'#ff3158',
        borderUpColor:'#00f58a', borderDownColor:'#ff3158'
      }});
      candles.setData({candles});
      const volume = chart.addHistogramSeries({{ priceFormat:{{type:'volume'}}, priceScaleId:'', scaleMargins:{{top:0.82,bottom:0}} }});
      volume.setData({volumes});
      const markers = {markers_json};
      if (markers.length) candles.setMarkers(markers);
      chart.timeScale().fitContent();
      new ResizeObserver(entries => {{
        if (!entries.length) return;
        const rect = entries[0].contentRect;
        chart.applyOptions({{ width: rect.width }});
      }}).observe(container);
    </script>
    """
    components.html(html, height=625, scrolling=False)



def _render_live_chart(frame: pd.DataFrame, market_symbol: str, symbol_label: str, interval: str) -> None:
    candles = json.dumps(_candles_for_chart(frame))
    volumes = json.dumps(_volume_for_chart(frame))
    ws_interval = {"5m":"5m","15m":"15m","30m":"30m","1H":"1h","4H":"4h","1D":"1d"}[interval]
    last_price = float(frame.iloc[-1]["close"])
    html = f"""
    <div style="font-family:Inter,system-ui;background:#030712;border:1px solid rgba(75,112,184,.34);border-radius:16px;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:11px 14px;border-bottom:1px solid rgba(75,112,184,.18);background:linear-gradient(90deg,#071125,#050915);">
        <div><strong style="color:#f7f9ff;font-size:12px">{symbol_label} · {interval}</strong><div style="color:#667694;font-size:9px;margin-top:3px">LIVE MARKET · BINANCE SPOT</div></div>
        <div style="text-align:right"><div id="bt-live-price" style="color:#f7f9ff;font-size:18px;font-weight:900">{last_price:,.2f}</div><div id="bt-live-status" style="color:#19e4ff;font-size:8px;font-weight:900">● CONNECTING…</div></div>
      </div>
      <div id="bt-live-chart" style="height:560px;width:100%;"></div>
    </div>
    <script src="https://unpkg.com/lightweight-charts@4.2.3/dist/lightweight-charts.standalone.production.js"></script>
    <script>
      const container = document.getElementById('bt-live-chart');
      const priceEl = document.getElementById('bt-live-price');
      const statusEl = document.getElementById('bt-live-status');
      const chart = LightweightCharts.createChart(container, {{
        layout: {{ background: {{ type:'solid', color:'#030712' }}, textColor:'#8fa0be' }},
        grid: {{ vertLines: {{ color:'rgba(58,83,132,.12)' }}, horzLines: {{ color:'rgba(58,83,132,.12)' }} }},
        rightPriceScale: {{ borderColor:'rgba(72,105,170,.25)' }},
        timeScale: {{ borderColor:'rgba(72,105,170,.25)', timeVisible:true, secondsVisible:false, rightOffset:5 }},
        crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
      }});
      const series = chart.addCandlestickSeries({{upColor:'#00f58a',downColor:'#ff3158',wickUpColor:'#00f58a',wickDownColor:'#ff3158',borderUpColor:'#00f58a',borderDownColor:'#ff3158'}});
      const volume = chart.addHistogramSeries({{priceFormat:{{type:'volume'}},priceScaleId:'',scaleMargins:{{top:0.82,bottom:0}}}});
      series.setData({candles});
      volume.setData({volumes});
      chart.timeScale().fitContent();
      const ws = new WebSocket('wss://stream.binance.com:9443/ws/{market_symbol.lower()}@kline_{ws_interval}');
      ws.onopen = () => {{ statusEl.textContent='● LIVE · VERIFIED'; statusEl.style.color='#00f58a'; }};
      ws.onmessage = (event) => {{
        const msg=JSON.parse(event.data); const k=msg.k; if(!k) return; const t=Math.floor(k.t/1000);
        series.update({{time:t,open:Number(k.o),high:Number(k.h),low:Number(k.l),close:Number(k.c)}});
        volume.update({{time:t,value:Number(k.v),color:Number(k.c)>=Number(k.o)?'rgba(0,245,138,.33)':'rgba(255,23,68,.32)'}});
        priceEl.textContent=Number(k.c).toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:8}});
      }};
      ws.onerror=()=>{{statusEl.textContent='● CONNECTION ERROR';statusEl.style.color='#ffd166';}};
      ws.onclose=()=>{{statusEl.textContent='● DISCONNECTED';statusEl.style.color='#ffd166';}};
      new ResizeObserver(entries=>{{if(entries.length)chart.applyOptions({{width:entries[0].contentRect.width}});}}).observe(container);
    </script>
    """
    components.html(html, height=625, scrolling=False)


def _load_dataset(symbol: str, interval: str, start_day: date) -> None:
    with st.spinner("Descargando datos históricos verificados…"):
        market, frame = get_backtest_dataset(symbol, interval, start_day, limit=1000)
    st.session_state.bt_market = market
    st.session_state.bt_dataset = frame
    st.session_state.bt_symbol = market.symbol
    st.session_state.bt_interval = interval
    st.session_state.bt_date = start_day
    st.session_state.bt_cursor = min(max(80, int(len(frame) * 0.20)), max(1, len(frame) - 1))
    st.session_state.bt_trade = None
    st.session_state.bt_trade_result = None


def render_backtesting_lab() -> None:
    apply_v2_theme()
    st.markdown(BACKTEST_CSS, unsafe_allow_html=True)
    _init_bt_state()

    st.html("""
    <section class="ax-bt-hero">
      <div class="ax-bt-kicker">AXION PRIME · MARKET INTELLIGENCE</div>
      <div class="ax-bt-title">Backtesting Lab</div>
      <div class="ax-bt-sub">Replay histórico con datos reales, futuro oculto y simulación de riesgo. AXION PRIME solo muestra mercados que puede verificar en la fuente conectada.</div>
      <div class="ax-bt-badges"><span class="ax-bt-badge">HISTORICAL DATA</span><span class="ax-bt-badge">NO LOOK-AHEAD</span><span class="ax-bt-badge gold">NO SYNTHETIC PRICES</span></div>
    </section>
    """)

    mode_col, note_col = st.columns([1.1, 3.2])
    with mode_col:
        mode = st.radio("Modo", ["LIVE", "REPLAY"], horizontal=True, index=0 if st.session_state.bt_mode == "LIVE" else 1)
        st.session_state.bt_mode = mode
    with note_col:
        if mode == "LIVE":
            st.info("🔴 LIVE muestra el mercado actual verificado de Binance Spot. El precio y la vela activa se actualizan mediante WebSocket.")
        else:
            st.info("🔵 REPLAY reconstruye mercado historico real y mantiene las velas futuras fuera del grafico.")

    if mode == "LIVE":
        c1, c2, c3 = st.columns([2.2, 1.0, 1.1])
        with c1:
            symbol = st.text_input("Buscar activo", value=st.session_state.bt_symbol, placeholder="BTCUSDT, ETHUSDT, SOLUSDT…", key="bt_live_symbol_input")
        with c2:
            interval = st.selectbox("Timeframe", ["5m","15m","30m","1H","4H","1D"], index=["5m","15m","30m","1H","4H","1D"].index(st.session_state.bt_interval), key="bt_live_interval")
        with c3:
            st.write(""); st.write("")
            live_load = st.button("📡 Abrir LIVE", width="stretch")
        try:
            market = resolve_symbol(symbol)
            if live_load or st.session_state.bt_symbol != market.symbol or st.session_state.bt_interval != interval:
                st.session_state.bt_symbol = market.symbol
                st.session_state.bt_interval = interval
            live_frame = fetch_recent_klines(market.symbol, interval, limit=400)
        except MarketDataError as exc:
            st.error(str(exc)); return
        current = live_frame.iloc[-1]
        first = live_frame.iloc[0]
        pct = ((float(current["close"])/float(first["open"]))-1)*100 if float(first["open"]) else 0.0
        st.html(f'<div class="ax-bt-source">● REAL DATA · LIVE · Fuente: {market.provider} · Mercado: {market.display_symbol} · WebSocket Binance · Sin precios sinteticos.</div>')
        st.html(f"""<div class="ax-bt-metric-grid">
          <div class="ax-bt-metric"><small>MODO</small><strong>LIVE</strong><span>mercado actual</span></div>
          <div class="ax-bt-metric"><small>ULTIMO PRECIO REST</small><strong>{_fmt_price(float(current['close']))}</strong><span>{pct:+.2f}% ventana visible</span></div>
          <div class="ax-bt-metric"><small>VELAS CARGADAS</small><strong>{len(live_frame)}</strong><span>{interval}</span></div>
          <div class="ax-bt-metric"><small>FUENTE</small><strong>VERIFIED</strong><span>{market.provider}</span></div>
        </div>""")
        _render_live_chart(live_frame, market.symbol, market.display_symbol, interval)
        st.html('<div class="ax-bt-warning">📡 <b>Live:</b> el grafico carga OHLCV reciente por REST y la vela activa se actualiza desde el WebSocket oficial de Binance. El card superior es una instantanea REST; el precio dentro del grafico se actualiza en vivo.</div>')
        st.html('<div class="ax-bt-panel-title">LIQUIDITY MAP</div>')
        st.html('<div class="ax-bt-warning"><b>Siguiente capa.</b><br>El heatmap se conectara solo a datos observables o calculos claramente etiquetados. No pintaremos liquidaciones inventadas.</div>')
        return

    c1, c2, c3, c4 = st.columns([2.1, 1.25, 1.0, 1.1])
    with c1:
        symbol = st.text_input("Buscar activo", value=st.session_state.bt_symbol, placeholder="BTCUSDT, ETHUSDT, SOLUSDT…", help="La fuente gratuita actual valida mercados Binance Spot.", key="bt_replay_symbol_input")
    with c2:
        start_day = st.date_input("Fecha historica", value=st.session_state.bt_date, max_value=date.today(), key="bt_replay_date")
    with c3:
        interval = st.selectbox("Timeframe", ["5m","15m","30m","1H","4H","1D"], index=["5m","15m","30m","1H","4H","1D"].index(st.session_state.bt_interval), key="bt_replay_interval")
    with c4:
        st.write(""); st.write("")
        load_clicked = st.button("🔎 Cargar replay", width="stretch")
    if load_clicked or st.session_state.bt_dataset is None:
        try:
            _load_dataset(symbol, interval, start_day)
            st.success("Mercado verificado y datos historicos cargados.")
        except MarketDataError as exc:
            st.error(str(exc))
            if st.session_state.bt_dataset is None:
                st.info("Para probar ahora mismo usa BTCUSDT o ETHUSDT. XAU/USD se activara cuando conectemos una fuente verificable para metales.")
                return

    frame: pd.DataFrame = st.session_state.bt_dataset
    market = st.session_state.bt_market
    if frame is None or market is None or frame.empty:
        st.warning("No hay datos cargados.")
        return

    st.html(
        f'<div class="ax-bt-source">● REAL DATA · Fuente: {market.provider} · Mercado: {market.display_symbol} · '
        f'{len(frame):,} velas descargadas · Los precios futuros permanecen fuera del gráfico.</div>'
    )

    max_cursor = max(1, len(frame) - 1)
    st.session_state.bt_cursor = max(1, min(int(st.session_state.bt_cursor), max_cursor))

    st.html('<div class="ax-bt-panel-title">CONTROLES DE REPLAY</div>')
    b1, b2, b3, b4, b5, b6 = st.columns([.7,.7,1.1,.9,.9,1.2])
    with b1:
        if st.button("⏮", help="Volver al inicio", width="stretch"):
            st.session_state.bt_cursor = min(80, max_cursor)
            st.rerun()
    with b2:
        if st.button("◀ 1", help="Retroceder una vela", width="stretch"):
            st.session_state.bt_cursor = max(1, st.session_state.bt_cursor - 1)
            st.rerun()
    with b3:
        if st.button("▶ +1 vela", width="stretch"):
            st.session_state.bt_cursor = min(max_cursor, st.session_state.bt_cursor + 1)
            st.rerun()
    with b4:
        if st.button("+5", width="stretch"):
            st.session_state.bt_cursor = min(max_cursor, st.session_state.bt_cursor + 5)
            st.rerun()
    with b5:
        if st.button("+20", width="stretch"):
            st.session_state.bt_cursor = min(max_cursor, st.session_state.bt_cursor + 20)
            st.rerun()
    with b6:
        speed = st.selectbox("Avance rápido", [1, 2, 4, 8, 16], index=[1,2,4,8,16].index(st.session_state.bt_speed), format_func=lambda x: f"{x}x")
        st.session_state.bt_speed = speed

    cursor = int(st.session_state.bt_cursor)
    visible = frame.iloc[: cursor + 1].copy()
    current = visible.iloc[-1]
    first = visible.iloc[0]
    pct = ((float(current["close"]) / float(first["open"])) - 1) * 100 if float(first["open"]) else 0.0

    st.html(
        f"""
        <div class="ax-bt-metric-grid">
          <div class="ax-bt-metric"><small>REPLAY POINT</small><strong>{pd.Timestamp(current['open_time']).strftime('%d %b %Y')}</strong><span>{pd.Timestamp(current['open_time']).strftime('%H:%M UTC')}</span></div>
          <div class="ax-bt-metric"><small>PRECIO ACTUAL</small><strong>{_fmt_price(float(current['close']))}</strong><span>{pct:+.2f}% desde inicio</span></div>
          <div class="ax-bt-metric"><small>VELAS VISIBLES</small><strong>{len(visible)}</strong><span>de {len(frame)} descargadas</span></div>
          <div class="ax-bt-metric"><small>FUENTE</small><strong>VERIFIED</strong><span>{market.provider}</span></div>
        </div>
        """
    )

    left, right = st.columns([3.25, 1.15], gap="large")
    with left:
        _render_chart(visible, market.display_symbol, st.session_state.bt_interval, st.session_state.bt_trade)
        st.html('<div class="ax-bt-warning">🔒 <b>No look-ahead:</b> el navegador solo recibe las velas visibles hasta el punto de replay. Las velas posteriores no se envían al gráfico.</div>')

    with right:
        st.html('<div class="ax-bt-panel-title">SIMULADOR DE TRADE</div>')
        current_price = float(current["close"])
        default_dist = max(current_price * 0.005, 0.000001)

        direction = st.radio("Dirección", ["LONG", "SHORT"], horizontal=True)
        if direction == "LONG":
            default_sl = current_price - default_dist
            default_tp = current_price + default_dist * 2
        else:
            default_sl = current_price + default_dist
            default_tp = current_price - default_dist * 2

        entry = st.number_input("Entrada", min_value=0.0, value=float(current_price), format="%.8f")
        sl = st.number_input("Stop Loss", min_value=0.0, value=float(max(default_sl, 0.00000001)), format="%.8f")
        tp = st.number_input("Take Profit", min_value=0.0, value=float(max(default_tp, 0.00000001)), format="%.8f")
        risk_amount = st.number_input("Riesgo ($)", min_value=1.0, value=100.0, step=10.0)

        plan = TradePlan(direction=direction, entry=entry, stop=sl, target=tp, risk_amount=risk_amount)
        valid, message = plan.validate()
        st.metric("Riesgo / Beneficio", f"1 : {plan.rr:.2f}")

        if st.button("⚡ Ejecutar simulación", width="stretch", disabled=not valid):
            st.session_state.bt_trade = {
                "direction": direction,
                "entry": entry,
                "stop": sl,
                "target": tp,
                "risk_amount": risk_amount,
                "created_index": cursor,
                "created_at": current["open_time"],
            }
            st.session_state.bt_trade_result = None
            st.rerun()
        if not valid:
            st.caption(message)

        if st.session_state.bt_trade:
            trade = st.session_state.bt_trade
            trade_plan = TradePlan(
                direction=trade["direction"], entry=float(trade["entry"]), stop=float(trade["stop"]),
                target=float(trade["target"]), risk_amount=float(trade["risk_amount"]),
            )
            from_index = int(trade["created_index"])
            trade_candles = frame.iloc[from_index: cursor + 1].copy()
            result = evaluate_trade(trade_plan, trade_candles)
            st.session_state.bt_trade_result = result
            st.html('<div class="ax-bt-panel-title">OPERACIÓN ACTIVA</div>')
            st.write(f"**{trade['direction']}** · Entry `{_fmt_price(trade['entry'])}`")
            st.write(f"SL `{_fmt_price(trade['stop'])}` · TP `{_fmt_price(trade['target'])}`")
            status = result["status"]
            if status == "WIN":
                st.success(f"TP alcanzado · {result['r_multiple']:+.2f}R · ${result['pnl']:+,.2f}")
            elif status == "LOSS":
                st.error(f"SL alcanzado · {result['r_multiple']:+.2f}R · ${result['pnl']:+,.2f}")
            elif status == "OPEN":
                st.info(f"Abierta · {result['r_multiple']:+.2f}R · ${result['pnl']:+,.2f}")
            else:
                st.warning("Orden pendiente: el precio todavía no tocó la entrada.")
            st.metric("MFE", f"{result['mfe_r']:.2f} R")
            st.metric("MAE", f"-{result['mae_r']:.2f} R")
            if st.button("Cancelar / limpiar trade", width="stretch"):
                st.session_state.bt_trade = None
                st.session_state.bt_trade_result = None
                st.rerun()

        st.html('<div class="ax-bt-panel-title">LIQUIDITY MAP</div>')
        st.html('<div class="ax-bt-warning"><b>Preparado, no falsificado.</b><br>La capa de heatmap se conectará a datos verificables. Esta versión no pinta “liquidaciones” inventadas a partir del precio.</div>')

    st.html('<div class="ax-bt-panel-title">FAVORITOS DE LA SESIÓN</div>')
    fav_cols = st.columns(4)
    for i, fav in enumerate(st.session_state.bt_favorites[:4]):
        with fav_cols[i]:
            if st.button(f"⭐ {fav}", key=f"bt_fav_{fav}", width="stretch"):
                try:
                    _load_dataset(fav, st.session_state.bt_interval, st.session_state.bt_date)
                    st.rerun()
                except MarketDataError as exc:
                    st.error(str(exc))

    add_col, action_col = st.columns([3,1])
    with add_col:
        fav_input = st.text_input("Agregar favorito", placeholder="Ej: SOLUSDT", key="bt_fav_input")
    with action_col:
        st.write("")
        st.write("")
        if st.button("⭐ Guardar", width="stretch"):
            try:
                resolved = resolve_symbol(fav_input)
                if resolved.symbol not in st.session_state.bt_favorites:
                    st.session_state.bt_favorites.append(resolved.symbol)
                st.success(f"{resolved.display_symbol} agregado a favoritos.")
            except MarketDataError as exc:
                st.error(str(exc))
