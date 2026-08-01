from __future__ import annotations

import ast
import base64
import json
import re
from typing import Any

import requests

from core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


# =========================================================
# AXION PRIME X10 PRO
# INTELIGENCIA ARTIFICIAL VISUAL
# =========================================================


class VisionError(RuntimeError):
    """
    Error controlado del escáner visual.
    """

    pass


# =========================================================
# ACTIVOS DISPONIBLES
# =========================================================

ASSET_ALIASES = {

    "XAUUSD": "🥇 XAU/USD (Oro)",
    "XAU/USD": "🥇 XAU/USD (Oro)",
    "GOLD": "🥇 XAU/USD (Oro)",
    "ORO": "🥇 XAU/USD (Oro)",

    "XAGUSD": "🥈 XAG/USD (Plata)",
    "XAG/USD": "🥈 XAG/USD (Plata)",
    "SILVER": "🥈 XAG/USD (Plata)",
    "PLATA": "🥈 XAG/USD (Plata)",

    "US30": "📊 US30 (Dow Jones)",
    "DJI": "📊 US30 (Dow Jones)",
    "DOW": "📊 US30 (Dow Jones)",
    "DOWJONES": "📊 US30 (Dow Jones)",

    "US100": "📊 US100 (Nasdaq 100)",
    "NAS100": "📊 US100 (Nasdaq 100)",
    "NASDAQ": "📊 US100 (Nasdaq 100)",
    "NASDAQ100": "📊 US100 (Nasdaq 100)",
    "USTEC": "📊 US100 (Nasdaq 100)",

    "US500": "📊 US500 (S&P 500)",
    "SP500": "📊 US500 (S&P 500)",
    "S&P500": "📊 US500 (S&P 500)",

    "BTCUSD": "🪙 BTC/USD (Bitcoin)",
    "BTC/USD": "🪙 BTC/USD (Bitcoin)",
    "BTCUSDT": "🪙 BTC/USD (Bitcoin)",
    "BITCOIN": "🪙 BTC/USD (Bitcoin)",

    "ETHUSD": "🪙 ETH/USD (Ethereum)",
    "ETH/USD": "🪙 ETH/USD (Ethereum)",
    "ETHUSDT": "🪙 ETH/USD (Ethereum)",
    "ETHEREUM": "🪙 ETH/USD (Ethereum)",

    "EURUSD": "💱 EUR/USD",
    "EUR/USD": "💱 EUR/USD",

    "GBPUSD": "💱 GBP/USD",
    "GBP/USD": "💱 GBP/USD",

    "USDJPY": "💱 USD/JPY",
    "USD/JPY": "💱 USD/JPY",

    "EURJPY": "💱 EUR/JPY",
    "EUR/JPY": "💱 EUR/JPY",

    "GBPJPY": "💱 GBP/JPY",
    "GBP/JPY": "💱 GBP/JPY",
}


# =========================================================
# TIMEFRAMES
# =========================================================

TIMEFRAME_ALIASES = {

    "1M": "M1",
    "M1": "M1",
    "1MIN": "M1",
    "1MINUTE": "M1",

    "5M": "M5",
    "M5": "M5",
    "5MIN": "M5",
    "5MINUTE": "M5",

    "15M": "M15",
    "M15": "M15",
    "15MIN": "M15",
    "15MINUTE": "M15",

    "30M": "M30",
    "M30": "M30",
    "30MIN": "M30",
    "30MINUTE": "M30",

    "1H": "H1",
    "H1": "H1",
    "60M": "H1",
    "60MIN": "H1",

    "4H": "H4",
    "H4": "H4",
    "240M": "H4",

    "1D": "D1",
    "D1": "D1",
    "DAILY": "D1",

    "1W": "W1",
    "W1": "W1",
    "WEEKLY": "W1",
}


# =========================================================
# LIMPIAR TEXTO
# =========================================================

def compact_text(
    value: Any,
) -> str:
    """
    Convierte un texto en formato comparable.
    """

    if value is None:

        return ""


    text = str(
        value
    ).upper().strip()


    text = text.replace(
        "_",
        "",
    )


    text = text.replace(
        "-",
        "",
    )


    text = text.replace(
        "/",
        "",
    )


    text = text.replace(
        " ",
        "",
    )


    return re.sub(
        r"[^A-Z0-9&]",
        "",
        text,
    )


# =========================================================
# NORMALIZAR ACTIVO
# =========================================================

def normalize_asset(
    value: Any,
) -> str | None:
    """
    Convierte el activo detectado por la IA
    al nombre utilizado en el formulario.
    """

    if value is None:

        return None


    original = str(
        value
    ).upper().strip()


    if not original:

        return None


    if original in ASSET_ALIASES:

        return ASSET_ALIASES[
            original
        ]


    compact = compact_text(
        original
    )


    for alias, normalized in ASSET_ALIASES.items():

        alias_compact = compact_text(
            alias
        )


        if compact == alias_compact:

            return normalized


    for alias, normalized in ASSET_ALIASES.items():

        alias_compact = compact_text(
            alias
        )


        if (
            alias_compact
            and alias_compact in compact
        ):

            return normalized


    return None


# =========================================================
# NORMALIZAR DIRECCIÓN
# =========================================================

def normalize_direction(
    value: Any,
) -> str | None:
    """
    Convierte LONG, SHORT, BUY o SELL
    al formato utilizado por AXION PRIME.
    """

    if value is None:

        return None


    text = str(
        value
    ).upper().strip()


    long_words = [
        "LONG",
        "BUY",
        "COMPRA",
        "ALCISTA",
        "LARGO",
    ]


    short_words = [
        "SHORT",
        "SELL",
        "VENTA",
        "BAJISTA",
        "CORTO",
    ]


    if any(
        word in text
        for word in long_words
    ):

        return "LONG 🟢"


    if any(
        word in text
        for word in short_words
    ):

        return "SHORT 🔴"


    return None


# =========================================================
# NORMALIZAR TIMEFRAME
# =========================================================

def normalize_timeframe(
    value: Any,
) -> str | None:
    """
    Convierte el timeframe detectado
    a M1, M5, M15, H1, H4, etc.
    """

    if value is None:

        return None


    compact = compact_text(
        value
    )


    return TIMEFRAME_ALIASES.get(
        compact
    )


# =========================================================
# LIMPIAR NÚMEROS
# =========================================================

def normalize_number(
    value: Any,
) -> float | None:
    """
    Convierte números recibidos como texto
    a float sin perder decimales.
    """

    if value is None:

        return None


    if isinstance(
        value,
        bool,
    ):

        return None


    if isinstance(
        value,
        (
            int,
            float,
        ),
    ):

        return float(
            value
        )


    text = str(
        value
    ).strip()


    if not text:

        return None


    text = (
        text
        .replace("$", "")
        .replace("USD", "")
        .replace("USDT", "")
        .replace(" ", "")
    )


    # Formato europeo:
    # 1.234,56

    if re.match(
        r"^-?\d{1,3}(\.\d{3})+,\d+$",
        text,
    ):

        text = (
            text
            .replace(".", "")
            .replace(",", ".")
        )

    # Si solo existe coma,
    # se interpreta como decimal.

    elif (
        "," in text
        and "." not in text
    ):

        text = text.replace(
            ",",
            ".",
        )

    else:

        text = text.replace(
            ",",
            "",
        )


    match = re.search(
        r"-?\d+(?:\.\d+)?",
        text,
    )


    if not match:

        return None


    try:

        return float(
            match.group(0)
        )

    except ValueError:

        return None


# =========================================================
# EXTRAER JSON
# =========================================================


def _content_to_text(content: Any) -> str:
    """Convierte las variantes de contenido de OpenRouter a texto."""

    if content is None:
        return ""

    if isinstance(content, dict):
        for key in ("content", "text", "output_text", "reasoning"):
            value = content.get(key)
            if value:
                return _content_to_text(value)
        return json.dumps(content, ensure_ascii=False)

    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, dict):
                value = (
                    item.get("text")
                    or item.get("content")
                    or item.get("output_text")
                    or ""
                )
                if value:
                    parts.append(str(value))
            elif item is not None:
                parts.append(str(item))
        return "\n".join(parts)

    return str(content)


def _balanced_json_candidates(text: str) -> list[str]:
    """Encuentra objetos JSON balanceados dentro de una respuesta larga."""

    candidates: list[str] = []
    depth = 0
    start = None
    in_string = False
    escaped = False

    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
            continue

        if char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                candidates.append(text[start:index + 1])
                start = None

    return candidates


def _decode_json_candidate(candidate: str) -> dict[str, Any] | None:
    """Prueba JSON estricto y reparaciones seguras habituales."""

    candidate = candidate.strip()
    if not candidate:
        return None

    variants = [candidate]

    cleaned = (
        candidate
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
    )
    cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    variants.append(cleaned)

    for value in variants:
        try:
            parsed = json.loads(value)
            if isinstance(parsed, str):
                parsed = json.loads(parsed)
            if isinstance(parsed, dict):
                return parsed
        except (json.JSONDecodeError, TypeError):
            pass

    # Algunos modelos devuelven un dict estilo Python con comillas simples.
    try:
        parsed = ast.literal_eval(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, SyntaxError):
        pass

    return None


def extract_json(content: Any) -> dict[str, Any]:
    """
    Extrae un objeto JSON aunque OpenRouter devuelva Markdown,
    texto adicional, comillas inteligentes o una cadena JSON escapada.
    """

    if isinstance(content, dict) and any(
        key in content
        for key in ("asset", "symbol", "pair", "direction", "entry", "sl", "tp")
    ):
        return content

    text = _content_to_text(content).strip()

    if not text:
        raise VisionError("La IA no devolvió contenido.")

    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "").strip()
    text = re.sub(r"</?json>", "", text, flags=re.IGNORECASE).strip()

    candidates = _balanced_json_candidates(text)

    # También intentamos con todo el texto por si ya era JSON puro.
    candidates.insert(0, text)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        payload = _decode_json_candidate(candidate)
        if payload is not None:
            return payload

    preview = re.sub(r"\s+", " ", text)[:260]
    raise VisionError(
        "La respuesta de la IA no contiene JSON válido. "
        f"Vista previa: {preview}"
    )


# =========================================================
# VALIDAR RESULTADO
# =========================================================

def validate_scan_result(
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Normaliza todos los valores detectados.
    """

    asset = normalize_asset(

        data.get("asset")
        or data.get("symbol")
        or data.get("pair")
        or data.get("instrument")
    )


    direction = normalize_direction(

        data.get("direction")
        or data.get("side")
        or data.get("trade_direction")
    )


    entry = normalize_number(

        data.get("entry")
        or data.get("entry_price")
        or data.get("price_entry")
    )


    stop_loss = normalize_number(

        data.get("sl")
        or data.get("stop_loss")
        or data.get("stoploss")
    )


    take_profit = normalize_number(

        data.get("tp")
        or data.get("take_profit")
        or data.get("takeprofit")
    )


    timeframe = normalize_timeframe(

        data.get("timeframe")
        or data.get("tf")
    )


    confidence = normalize_number(

        data.get("confidence")
    )


    if confidence is None:

        confidence = 0.0


    confidence = max(
        0.0,
        min(
            100.0,
            confidence,
        ),
    )


    return {

        "asset":
            asset,

        "direction":
            direction,

        "entry":
            entry,

        "sl":
            stop_loss,

        "tp":
            take_profit,

        "timeframe":
            timeframe,

        "confidence":
            confidence,
    }


# =========================================================
# ESCANEAR CAPTURA
# =========================================================

def scan_trade(
    image_bytes: bytes,
    mime_type: str = "image/jpeg",
) -> dict[str, Any]:
    """
    Envía una captura a OpenRouter
    y obtiene los parámetros del trade.
    """

    if not OPENROUTER_API_KEY:

        raise VisionError(
            "OPENROUTER_API_KEY no está configurada "
            "en Streamlit Secrets."
        )


    if not image_bytes:

        raise VisionError(
            "La imagen está vacía."
        )


    encoded_image = base64.b64encode(
        image_bytes
    ).decode(
        "utf-8"
    )


    prompt = """
Eres AXION Vision, un extractor visual profesional
especializado en capturas de TradingView.

Tu única función es leer los parámetros visibles
de una operación.

Debes extraer:

1. Activo o símbolo.
2. Dirección LONG o SHORT.
3. Precio de entrada.
4. Stop Loss.
5. Take Profit.
6. Timeframe.
7. Confianza de lectura.

Reglas obligatorias:

- No inventes datos.
- No calcules precios.
- No reemplaces un activo desconocido por XAU/USD.
- Conserva todos los decimales visibles.
- Busca etiquetas como Entry, Stop, Target, TP y SL.
- Reconoce las herramientas Long Position y Short Position.
- Si un valor no puede leerse claramente, devuelve null.
- Si hay varios precios, identifica cada uno por su etiqueta
  y por la posición de la herramienta en el gráfico.
- El precio de entrada suele estar entre el TP y el SL.
- En una operación SHORT, el SL normalmente está arriba
  y el TP normalmente está abajo.
- En una operación LONG, el TP normalmente está arriba
  y el SL normalmente está abajo.
- No añadas explicaciones.

Devuelve únicamente JSON válido:

{
  "asset": null,
  "direction": null,
  "entry": null,
  "sl": null,
  "tp": null,
  "timeframe": null,
  "confidence": 0
}
"""


    headers = {

        "Authorization":
            f"Bearer {OPENROUTER_API_KEY}",

        "Content-Type":
            "application/json",

        "HTTP-Referer":
            "https://streamlit.io",

        "X-Title":
            "AXION PRIME X10 PRO",
    }


    payload = {

        "model":
            OPENROUTER_MODEL,

        "temperature":
            0,

        "max_tokens":
            900,

        "response_format": {
            "type": "json_object",
        },

        "messages": [

            {
                "role":
                    "system",

                "content":
                    "Eres un extractor visual preciso. "
                    "Nunca inventes parámetros de trading.",
            },

            {
                "role":
                    "user",

                "content": [

                    {
                        "type":
                            "text",

                        "text":
                            prompt,
                    },

                    {
                        "type":
                            "image_url",

                        "image_url": {

                            "url":
                                (
                                    f"data:{mime_type};"
                                    f"base64,{encoded_image}"
                                )
                        },
                    },
                ],
            },
        ],
    }


    def _send(request_payload: dict[str, Any]) -> requests.Response:
        try:
            return requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=request_payload,
                timeout=90,
            )
        except requests.Timeout as exc:
            raise VisionError(
                "La IA tardó demasiado en responder."
            ) from exc
        except requests.ConnectionError as exc:
            raise VisionError(
                "No se pudo conectar con OpenRouter."
            ) from exc

    response = _send(payload)

    # Algunos modelos no aceptan response_format. Reintentamos sin romper.
    if response.status_code >= 400 and "response_format" in response.text.lower():
        fallback_payload = dict(payload)
        fallback_payload.pop("response_format", None)
        response = _send(fallback_payload)

    if response.status_code != 200:
        raise VisionError(
            f"OpenRouter HTTP {response.status_code}: "
            f"{response.text[:1000]}"
        )


    try:

        response_data = response.json()

    except ValueError as exc:

        raise VisionError(
            "OpenRouter devolvió una respuesta inválida."
        ) from exc


    choices = response_data.get(
        "choices",
        [],
    )


    if not choices:

        raise VisionError(
            "OpenRouter no devolvió resultados."
        )


    message = choices[0].get(
        "message",
        {},
    )

    content = (
        message.get("content")
        or message.get("reasoning")
        or message.get("analysis")
        or message
    )

    try:
        raw_result = extract_json(content)
    except VisionError:
        # Segundo intento con una instrucción aún más corta y estricta.
        retry_payload = dict(payload)
        retry_payload.pop("response_format", None)
        retry_payload["messages"] = [
            payload["messages"][0],
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analiza esta captura y responde SOLO con un objeto JSON válido, "
                            "sin Markdown ni explicación. Usa exactamente estas claves: "
                            "asset, direction, entry, sl, tp, timeframe, confidence. "
                            "Usa null cuando no puedas leer un dato."
                        ),
                    },
                    payload["messages"][1]["content"][1],
                ],
            },
        ]

        retry_response = _send(retry_payload)
        if retry_response.status_code != 200:
            raise VisionError(
                f"OpenRouter HTTP {retry_response.status_code}: "
                f"{retry_response.text[:1000]}"
            )

        retry_data = retry_response.json()
        retry_choices = retry_data.get("choices", [])
        if not retry_choices:
            raise VisionError("OpenRouter no devolvió resultados en el reintento.")

        retry_message = retry_choices[0].get("message", {})
        retry_content = (
            retry_message.get("content")
            or retry_message.get("reasoning")
            or retry_message
        )
        raw_result = extract_json(retry_content)


    result = validate_scan_result(
        raw_result
    )


    if not any(
        [
            result.get("asset"),
            result.get("direction"),
            result.get("entry") is not None,
            result.get("sl") is not None,
            result.get("tp") is not None,
            result.get("timeframe"),
        ]
    ):

        raise VisionError(
            "La IA no pudo leer datos claros "
            "en la captura."
        )


    return result
