from __future__ import annotations

import base64
import io

from PIL import Image


# =========================================================
# AXION PRIME X10 PRO
# PROCESAMIENTO DE IMÁGENES
# =========================================================


def image_to_data_url(
    uploaded_file,
    max_size: tuple[int, int] = (
        1200,
        900,
    ),
    quality: int = 78,
) -> str:
    """
    Convierte una imagen subida en una cadena Base64
    lista para guardarse en Supabase.
    """

    if uploaded_file is None:

        return ""


    try:

        image = Image.open(
            uploaded_file
        )


        if image.mode in (
            "RGBA",
            "LA",
            "P",
        ):

            if image.mode == "P":

                image = image.convert(
                    "RGBA"
                )


            background = Image.new(
                "RGB",
                image.size,
                "white",
            )


            if "A" in image.getbands():

                background.paste(
                    image,
                    mask=image.getchannel(
                        "A"
                    ),
                )

            else:

                background.paste(
                    image
                )


            image = background

        else:

            image = image.convert(
                "RGB"
            )


        image.thumbnail(
            max_size
        )


        buffer = io.BytesIO()


        image.save(
            buffer,
            format="JPEG",
            quality=quality,
            optimize=True,
        )


        encoded = base64.b64encode(
            buffer.getvalue()
        ).decode(
            "utf-8"
        )


        return (
            "data:image/jpeg;base64,"
            + encoded
        )


    except Exception as exc:

        raise RuntimeError(
            "No se pudo procesar la imagen: "
            f"{exc}"
        ) from exc


# =========================================================
# VALIDAR IMAGEN GUARDADA
# =========================================================

def normalize_image_value(
    value,
) -> str:
    """
    Normaliza imágenes antiguas o nuevas para mostrarlas
    correctamente en Streamlit.
    """

    if not value:

        return ""


    text = str(
        value
    ).strip()


    if text.startswith(
        "data:image"
    ):

        return text


    if len(text) > 100:

        return (
            "data:image/jpeg;base64,"
            + text
        )


    return ""


# =========================================================
# CALCULAR TAMAÑO APROXIMADO
# =========================================================

def approximate_data_url_size_mb(
    value: str,
) -> float:
    """
    Calcula el tamaño aproximado de una imagen Base64.
    """

    if not value:

        return 0.0


    text = str(
        value
    )


    if "," in text:

        text = text.split(
            ",",
            1,
        )[1]


    size_bytes = (
        len(text)
        * 3
        / 4
    )


    return (
        size_bytes
        / 1024
        / 1024
    )
