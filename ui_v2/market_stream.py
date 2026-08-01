from __future__ import annotations

import math
import random

import streamlit as st


MARKET_STREAM_CSS = """
<style>
.axion-market-stream {
    position: relative;
    min-height: 220px;
    overflow: hidden;
    margin-bottom: 18px;
    padding: 18px 20px;
    background:
        radial-gradient(circle at 82% 18%, rgba(25,228,255,.08), transparent 26%),
        linear-gradient(145deg, rgba(4,12,27,.99), rgba(3,7,18,.99));
    border: 1px solid rgba(62,111,183,.34);
    border-radius: 18px;
    box-shadow: 0 24px 70px rgba(0,0,0,.34);
}

.axion-market-stream::before {
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(rgba(49,88,151,.08) 1px, transparent 1px),
        linear-gradient(90deg, rgba(49,88,151,.08) 1px, transparent 1px);
    background-size: 34px 34px;
}

.axion-market-head {
    position: relative;
    z-index: 3;
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: center;
    margin-bottom: 14px;
}

.axion-market-head strong {
    color: #f7f9ff;
    font-size: 12px;
    letter-spacing: 1.1px;
}

.axion-market-head span {
    color: #00f58a;
    font-size: 8px;
    font-weight: 900;
}

.axion-market-chart {
    position: relative;
    z-index: 2;
    height: 150px;
    overflow: hidden;
}

.axion-market-track {
    position: absolute;
    inset: 0;
    width: 2300px;
    animation: axion-market-slide 34s linear infinite;
}

.axion-candle {
    position: absolute;
    left: var(--x);
    top: var(--top);
    width: 9px;
    height: var(--body);
    border-radius: 1px;
    background: var(--c);
    box-shadow:
        0 0 12px color-mix(in srgb, var(--c) 62%, transparent),
        0 0 24px color-mix(in srgb, var(--c) 20%, transparent);
}

.axion-candle::before {
    content: "";
    position: absolute;
    left: 50%;
    top: calc(var(--wick-top) * -1);
    width: 1px;
    height: calc(var(--body) + var(--wick-top) + var(--wick-bottom));
    transform: translateX(-50%);
    background: var(--c);
}

.axion-volume {
    position: absolute;
    left: var(--x);
    bottom: 0;
    width: 8px;
    height: var(--vol);
    background: color-mix(in srgb, var(--c) 42%, transparent);
    border-radius: 2px 2px 0 0;
}

.axion-glow-line {
    position: absolute;
    left: 0;
    right: 0;
    top: 63%;
    height: 1px;
    background: linear-gradient(90deg, transparent, #19e4ff, transparent);
    opacity: .28;
    box-shadow: 0 0 18px rgba(25,228,255,.35);
}

@keyframes axion-market-slide {
    from { transform: translateX(0); }
    to { transform: translateX(-720px); }
}

@media (prefers-reduced-motion: reduce) {
    .axion-market-track { animation: none; }
}
</style>
"""


def _build_candles() -> str:
    random.seed(77)

    candles: list[str] = []
    price = 74.0

    for index in range(64):
        move = random.uniform(-8.5, 8.5)
        open_price = price
        close_price = max(18.0, min(118.0, open_price + move))
        high = max(open_price, close_price) + random.uniform(4.0, 11.0)
        low = min(open_price, close_price) - random.uniform(4.0, 11.0)

        body = max(7, int(abs(close_price - open_price) * 2.2))
        top = int(72 - max(open_price, close_price) * 0.48)
        top = max(18, min(108, top))
        wick_top = max(7, int((high - max(open_price, close_price)) * 1.4))
        wick_bottom = max(7, int((min(open_price, close_price) - low) * 1.4))
        volume = random.randint(12, 55)
        color = "#00F58A" if close_price >= open_price else "#FF1744"
        x = 58 + index * 34

        candles.append(
            f"""
            <span class="axion-candle"
                style="
                    --x:{x}px;
                    --top:{top}px;
                    --body:{body}px;
                    --wick-top:{wick_top}px;
                    --wick-bottom:{wick_bottom}px;
                    --c:{color};
                ">
            </span>
            <span class="axion-volume"
                style="
                    --x:{x}px;
                    --vol:{volume}px;
                    --c:{color};
                ">
            </span>
            """
        )

        price = close_price

    return "".join(candles)


def render_market_stream() -> None:
    st.markdown(MARKET_STREAM_CSS, unsafe_allow_html=True)

    st.html(
        f"""
        <section class="axion-market-stream">
            <div class="axion-market-head">
                <strong>MARKET STREAM · XAU/USD</strong>
                <span>● LIVE</span>
            </div>

            <div class="axion-market-chart">
                <div class="axion-glow-line"></div>
                <div class="axion-market-track">
                    {_build_candles()}
                </div>
            </div>
        </section>
        """
    )
