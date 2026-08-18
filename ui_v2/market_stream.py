from __future__ import annotations

import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.market_data import MarketDataError, fetch_recent_klines


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
    result = []
    for _, row in frame.iterrows():
        is_up = float(row["close"]) >= float(row["open"])
        result.append(
            {
                "time": int(pd.Timestamp(row["open_time"]).timestamp()),
                "value": float(row["volume"]),
                "color": "rgba(0,245,138,.30)" if is_up else "rgba(255,23,68,.28)",
            }
        )
    return result


def render_market_stream() -> None:
    """
    Panel de mercado real del dashboard.
    Carga OHLCV reciente desde Binance Spot y actualiza la vela activa
    mediante WebSocket público de Binance.
    """
    try:
        frame = fetch_recent_klines("BTCUSDT", "1m", limit=180)
    except MarketDataError as exc:
        st.warning(f"Market Stream temporalmente no disponible: {exc}")
        return

    candles_json = json.dumps(_candles(frame))
    volumes_json = json.dumps(_volumes(frame))
    last_price = float(frame.iloc[-1]["close"])

    html = f"""
    <div style="font-family:Inter,system-ui;background:#030712;border:1px solid rgba(62,111,183,.34);
                border-radius:18px;overflow:hidden;">
      <div style="display:flex;justify-content:space-between;gap:12px;align-items:center;
                  padding:12px 15px;border-bottom:1px solid rgba(62,111,183,.20);
                  background:linear-gradient(90deg,#071125,#050915);">
        <div>
          <strong style="color:#f7f9ff;font-size:12px;letter-spacing:.7px;">
            MARKET STREAM · BTC/USDT · 1m
          </strong>
          <div style="color:#71809f;font-size:9px;margin-top:3px;">
            BINANCE SPOT · LIVE CANDLE STREAM
          </div>
        </div>
        <div style="text-align:right;">
          <div id="live-price" style="color:#f7f9ff;font-size:18px;font-weight:900;">
            {last_price:,.2f}
          </div>
          <div id="live-status" style="color:#00f58a;font-size:8px;font-weight:900;">
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
          background: {{ type: 'solid', color: '#030712' }},
          textColor: '#8fa0be'
        }},
        grid: {{
          vertLines: {{ color: 'rgba(58,83,132,.12)' }},
          horzLines: {{ color: 'rgba(58,83,132,.12)' }}
        }},
        rightPriceScale: {{
          borderColor: 'rgba(72,105,170,.25)'
        }},
        timeScale: {{
          borderColor: 'rgba(72,105,170,.25)',
          timeVisible: true,
          secondsVisible: false,
          rightOffset: 4
        }}
      }});

      const series = chart.addCandlestickSeries({{
        upColor: '#00f58a',
        downColor: '#ff3158',
        wickUpColor: '#00f58a',
        wickDownColor: '#ff3158',
        borderUpColor: '#00f58a',
        borderDownColor: '#ff3158'
      }});

      const volume = chart.addHistogramSeries({{
        priceFormat: {{ type: 'volume' }},
        priceScaleId: '',
        scaleMargins: {{ top: 0.82, bottom: 0 }}
      }});

      series.setData({candles_json});
      volume.setData({volumes_json});
      chart.timeScale().fitContent();

      function formatPrice(value) {{
        return Number(value).toLocaleString('en-US', {{
          minimumFractionDigits: 2,
          maximumFractionDigits: 2
        }});
      }}

      const ws = new WebSocket(
        'wss://stream.binance.com:9443/ws/btcusdt@kline_1m'
      );

      ws.onopen = () => {{
        statusEl.textContent = '● LIVE · VERIFIED BINANCE';
        statusEl.style.color = '#00f58a';
      }};

      ws.onmessage = (event) => {{
        const msg = JSON.parse(event.data);
        const k = msg.k;
        if (!k) return;

        const timestamp = Math.floor(k.t / 1000);
        const open = Number(k.o);
        const close = Number(k.c);

        series.update({{
          time: timestamp,
          open: open,
          high: Number(k.h),
          low: Number(k.l),
          close: close
        }});

        volume.update({{
          time: timestamp,
          value: Number(k.v),
          color: close >= open
            ? 'rgba(0,245,138,.30)'
            : 'rgba(255,23,68,.28)'
        }});

        priceEl.textContent = formatPrice(close);
      }};

      ws.onerror = () => {{
        statusEl.textContent = '● LIVE CONNECTION ERROR';
        statusEl.style.color = '#ffd166';
      }};

      ws.onclose = () => {{
        statusEl.textContent = '● LIVE DISCONNECTED';
        statusEl.style.color = '#ffd166';
      }};

      const observer = new ResizeObserver((entries) => {{
        if (!entries.length) return;
        chart.applyOptions({{
          width: entries[0].contentRect.width
        }});
      }});
      observer.observe(container);
    </script>
    """

    components.html(html, height=348, scrolling=False)
