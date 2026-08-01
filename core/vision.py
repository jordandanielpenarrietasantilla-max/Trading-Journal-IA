from __future__ import annotations

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
# EXTRAER Y REPARAR JSON
# =========================================================

def _strip_code_fences(text: str) -> str:
    cleaned = re.sub(
        r"```(?:json)?",
        "",
        text,
        flags=re.IGNORECASE,
    )
    return cleaned.replace("```", "").strip()


def _extract_balanced_object(text: str) -> str | None:
    start = text.find("{")
    if start < 0:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        character = text[index]

        if escaped:
            escaped = False
            continue

        if character == "\\":
            escaped = True
            continue

        if character == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]

    return None


def _repair_json_text(text: str) -> str:
    repaired = text.strip()

    repaired = (
        repaired
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2018", "'")
        .replace("\u2019", "'")
    )

    repaired = re.sub(
        r",\s*([}\]])",
        r"\1",
        repaired,
    )

    repaired = re.sub(r"\bNone\b", "null", repaired)
    repaired = re.sub(r"\bTrue\b", "true", repaired)
    repaired = re.sub(r"\bFalse\b", "false", repaired)

    repaired = re.sub(
        r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)(\s*:)",
        r'\1"\2"\3',
        repaired,
    )

    if "'" in repaired and '"' not in repaired:
        repaired = repaired.replace("'", '"')

    return repaired


def _content_to_text(content: Any) -> str:
    if content is None:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, dict):
        for key in (
            "text",
            "content",
            "output_text",
            "arguments",
        ):
            value = content.get(key)
            if value:
                return _content_to_text(value)

        return json.dumps(
            content,
            ensure_ascii=False,
        )

    if isinstance(content, list):
        parts: list[str] = []

        for item in content:
            item_text = _content_to_text(item)
            if item_text:
                parts.append(item_text)

        return "\n".join(parts)

    return str(content)


def extract_json(content: Any) -> dict[str, Any]:
    """
    Extrae un objeto JSON aunque OpenRouter devuelva:
    Markdown, texto adicional, listas de bloques,
    comas finales, claves sin comillas o valores Python.
    """

    text = _content_to_text(content).strip()

    if not text:
        raise VisionError(
            "La IA no devolvió contenido."
        )

    text = _strip_code_fences(text)

    candidates: list[str] = []

    balanced = _extract_balanced_object(text)
    if balanced:
        candidates.append(balanced)

    candidates.append(text)

    last_error: Exception | None = None

    for candidate in candidates:
        for attempt in (
            candidate,
            _repair_json_text(candidate),
        ):
            try:
                payload = json.loads(attempt)
            except json.JSONDecodeError as exc:
                last_error = exc
                continue

            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError as exc:
                    last_error = exc
                    continue

            if isinstance(payload, dict):
                return payload

    detail = ""

    if last_error is not None:
        detail = (
            f" Línea {getattr(last_error, 'lineno', '?')}, "
            f"columna {getattr(last_error, 'colno', '?')}."
        )

    raise VisionError(
        "La respuesta de la IA no contiene JSON válido."
        + detail
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
# EXTRAER CONTENIDO DEL MENSAJE
# =========================================================

def _extract_message_payload(
    message: dict[str, Any],
) -> Any:
    """
    Obtiene el contenido JSON desde cualquiera de las
    estructuras que puede devolver OpenRouter.
    """

    if not isinstance(message, dict):
        return message

    tool_calls = message.get("tool_calls")

    if isinstance(tool_calls, list) and tool_calls:
        first_call = tool_calls[0]

        if isinstance(first_call, dict):
            function_data = first_call.get(
                "function",
                {},
            )

            if isinstance(function_data, dict):
                arguments = function_data.get(
                    "arguments"
                )

                if arguments:
                    return arguments

    function_call = message.get("function_call")

    if isinstance(function_call, dict):
        arguments = function_call.get("arguments")

        if arguments:
            return arguments

    for key in (
        "content",
        "output_text",
        "reasoning",
    ):
        value = message.get(key)

        if value:
            return value

    return message


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
                    "Nunca inventes parámetros de trading. "
                    "Responde exclusivamente con un objeto JSON válido, "
                    "sin Markdown, sin comentarios y sin texto adicional.",
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


    try:

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers=headers,

            json=payload,

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


    if response.status_code != 200:

        # Algunos modelos no aceptan response_format.
        # Reintentamos una vez sin esa opción.
        if (
            response.status_code in {400, 422}
            and "response_format" in response.text
        ):
            fallback_payload = dict(payload)
            fallback_payload.pop(
                "response_format",
                None,
            )

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=fallback_payload,
                    timeout=90,
                )

            except requests.RequestException as exc:
                raise VisionError(
                    "Falló el segundo intento con OpenRouter."
                ) from exc

        if response.status_code != 200:
            raise VisionError(
                f"OpenRouter HTTP "
                f"{response.status_code}: "
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


    content = _extract_message_payload(
        message
    )


    raw_result = extract_json(
        content
    )


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
