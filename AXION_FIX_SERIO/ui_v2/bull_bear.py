from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st


BULL_BEAR_CSS = """
<style>
.axion-bull-bear {
    position: relative;
    min-height: 260px;
    overflow: hidden;
    margin: 18px 0;
    background:
        linear-gradient(90deg, rgba(0,245,138,.06), transparent 38% 62%, rgba(255,23,68,.06)),
        #040913;
    border: 1px solid rgba(79,111,181,.34);
    border-radius: 20px;
    box-shadow: 0 24px 70px rgba(0,0,0,.38);
}

.axion-bull-bear-bg {
    position: absolute;
    inset: 0;
    background-image: var(--image);
    background-position: center;
    background-size: cover;
    filter: saturate(1.08) contrast(1.06);
}

.axion-bull-bear-overlay {
    position: absolute;
    inset: 0;
    background:
        linear-gradient(90deg, rgba(1,8,17,.06), rgba(1,8,17,.20) 48%, rgba(1,8,17,.06)),
        linear-gradient(to bottom, transparent 65%, rgba(2,5,12,.72));
}

.axion-bull-bear-copy {
    position: absolute;
    z-index: 3;
    left: 50%;
    bottom: 16px;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 10px 16px;
    color: #f7f9ff;
    font-size: 8px;
    font-weight: 900;
    letter-spacing: 1.2px;
    background: rgba(3,8,20,.72);
    border: 1px solid rgba(87,124,198,.34);
    border-radius: 999px;
    backdrop-filter: blur(12px);
}

.axion-bull-bear-copy .bull { color:#00f58a; }
.axion-bull-bear-copy .bear { color:#ff1744; }
</style>
"""


def _to_data_uri(path: Path) -> str:
    data = path.read_bytes()
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def render_bull_bear(asset_path: str = "assets/bull_bear_futurista.png") -> None:
    st.markdown(BULL_BEAR_CSS, unsafe_allow_html=True)

    path = Path(asset_path)

    if not path.exists():
        st.warning(
            "Falta el archivo assets/bull_bear_futurista.png"
        )
        return

    image_uri = _to_data_uri(path)

    st.html(
        f"""
        <section class="axion-bull-bear">
            <div
                class="axion-bull-bear-bg"
                style="--image:url('{image_uri}')">
            </div>

            <div class="axion-bull-bear-overlay"></div>

            <div class="axion-bull-bear-copy">
                <span class="bull">BULL · IMPULSO</span>
                <span>AXION CORE</span>
                <span class="bear">BEAR · PROTECCIÓN</span>
            </div>
        </section>
        """
    )
