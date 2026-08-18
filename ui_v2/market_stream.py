from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.market_data import MarketDataError, fetch_recent_klines


TIMEFRAMES = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1H": "1h",
    "4H": "4h",
    "1D": "1d",
}


def _candles(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "time": int(pd.Timestamp(row["open_time"]).timestamp()),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
        }
        for _, row in frame.iterrows()
    ]


def _volumes(frame: pd.DataFrame) -> list[dict]:
    data = []
    for _, row in frame.iterrows():
        up = float(row["close"]) >= float(row["open"])
        data.append(
            {
                "time": int(pd.Timestamp(row["open_time"]).timestamp()),
                "value": float(row["volume"]),
                "color": "rgba(0,245,138,.30)" if up else "rgba(255,23,68,.28)",
            }
        )
    return data


def render_market_stream() -> None:
    # Selector visible en Dashboard.
    c1, c2 = st.columns([2.6, 1.0])
    with c1:
        st.caption("📡 Mercado real · Binance Spot")
    with c2:
        timeframe = st.selectbox(
            "Timeframe Market Stream",
            list(TIMEFRAMES.keys()),
            index=0,
            key="dashboard_market_stream_tf",
            label_visibility="collapsed",
        )

    try:
        frame = fetch_recent_klines("BTCUSDT", timeframe, limit=220)
    except MarketDataError as exc:
        st.warning(f"Market Stream temporalmente no disponible: {exc}")
        return

    candles_json = json.dumps(_candles(frame))
    volumes_json = json.dumps(_volumes(frame))
    last_price = float(frame.iloc[-1]["close"])
    ws_tf = TIMEFRAMES[timeframe]

    html = f"""
    <div style="font-family:Inter,system-ui;background:#030712;border:1px solid rgba(62,111,183,.34);
                border-radius:18px;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;
                  padding:12px 15px;border-bottom:1px solid rgba(62,111,183,.20);
                  background:linear-gradient(90deg,#071125,#050915);">
        <div>
          <strong style="color:#f7f9ff;font-size:12px;letter-spacing:.7px;">
            MARKET STREAM · BTC/USDT · {timeframe}
          </strong>
          <div style="color:#71809f;font-size:9px;margin-top:3px;">
            BINANCE SPOT · LIVE CANDLE STREAM · V3
          </div>
        </div>
        <div style="text-align:right;">
          <div id="live-price" style="color:#f7f9ff;font-size:18px;font-weight:900;">
            {last_price:,.2f}
          </div>
          <div id="live-status" style="color:#19e4ff;font-size:8px;font-weight:900;">
            ● CONNECTING LIVE…
          </div>
        </div>
      </div>

      <div id="market-chart" style="height:300px;width:100%;"></div>
    </div>

    <script src="https://unpkg.com/lightweight-charts@4.2.3/dist/lightweight-charts.standalone.production.js"></script>
    <script>
      const container = document.getElementById('market-chart');
      const priceEl = document.getElementById('live-price');
      const statusEl = document.getElementById('live-status');

      const chart = LightweightCharts.createChart(container, {{
        layout: {{
          background: {{ type:'solid', color:'#030712' }},
          textColor:'#8fa0be'
        }},
        grid: {{
          vertLines: {{ color:'rgba(58,83,132,.12)' }},
          horzLines: {{ color:'rgba(58,83,132,.12)' }}
        }},
        rightPriceScale: {{ borderColor:'rgba(72,105,170,.25)' }},
        timeScale: {{
          borderColor:'rgba(72,105,170,.25)',
          timeVisible:true,
          secondsVisible:false,
          rightOffset:4
        }}
      }});

      const series = chart.addCandlestickSeries({{
        upColor:'#00f58a',
        downColor:'#ff3158',
        wickUpColor:'#00f58a',
        wickDownColor:'#ff3158',
        borderUpColor:'#00f58a',
        borderDownColor:'#ff3158'
      }});

      const volume = chart.addHistogramSeries({{
        priceFormat: {{type:'volume'}},
        priceScaleId:'',
        scaleMargins: {{top:.82,bottom:0}}
      }});

      series.setData({candles_json});
      volume.setData({volumes_json});
      chart.timeScale().fitContent();

      const ws = new WebSocket(
        'wss://stream.binance.com:9443/ws/btcusdt@kline_{ws_tf}'
      );

      ws.onopen = () => {{
        statusEl.textContent = '● LIVE · VERIFIED BINANCE';
        statusEl.style.color = '#00f58a';
      }};

      ws.onmessage = (event) => {{
        const msg = JSON.parse(event.data);
        const k = msg.k;
        if (!k) return;

        const t = Math.floor(k.t / 1000);
        const o = Number(k.o);
        const c = Number(k.c);

        series.update({{
          time:t,
          open:o,
          high:Number(k.h),
          low:Number(k.l),
          close:c
        }});

        volume.update({{
          time:t,
          value:Number(k.v),
          color:c >= o
            ? 'rgba(0,245,138,.30)'
            : 'rgba(255,23,68,.28)'
        }});

        priceEl.textContent = c.toLocaleString(
          'en-US',
          {{minimumFractionDigits:2, maximumFractionDigits:2}}
        );
      }};

      ws.onerror = () => {{
        statusEl.textContent = '● LIVE CONNECTION ERROR';
        statusEl.style.color = '#ffd166';
      }};

      new ResizeObserver(entries => {{
        if (!entries.length) return;
        chart.applyOptions({{
          width: entries[0].contentRect.width
        }});
      }}).observe(container);
    </script>
    """

    components.html(html, height=348, scrolling=False)
