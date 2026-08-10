from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import requests
import streamlit as st

from core.api import (
    ensure_access_token,
    list_trades,
)
from core.config import (
    ADMIN_EMAIL,
    SUPABASE_KEY,
    SUPABASE_URL,
    validate_config,
)
from core.membership import get_membership_info
from core.metrics import prepare_df
from core.state import init_state

from ui.track_record import render_track_record
from ui.trades import render_register_trade
from ui.tools import (
    render_chat,
    render_lotage,
    render_projections,
)

from ui_v2.ai_analysis import render_ai_analysis
from ui_v2.dashboard import render_v2_dashboard
from ui_v2.login import render_v2_auth
from ui_v2.market_tools import (
    render_news,
    render_sessions,
)
from ui_v2.profile import render_v2_profile
from ui_v2.psychotrading import render_psychotrading
from ui_v2.sidebar import render_v2_sidebar
from ui_v2.subscription import render_subscription


# =========================================================
# AXION PRIME X10 PRO
# APP PRINCIPAL
# =========================================================


st.set_page_config(
    page_title="AXION PRIME X10 PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


REQUEST_TIMEOUT = 30


# =========================================================
# HELPERS
# =========================================================


def _as_dict(
    value: Any,
) -> dict[str, Any]:
    """
    Convierte de forma segura objetos de usuario o metadata
    en un diccionario estándar.
    """

    if isinstance(
        value,
        dict,
    ):
        return value

    try:
        dumped = value.model_dump()

        if isinstance(
            dumped,
            dict,
        ):
            return dumped

    except Exception:
        pass

    try:
        converted = dict(
            value
        )

        if isinstance(
            converted,
            dict,
        ):
            return converted

    except Exception:
        pass

    return {}


def _first_value(
    source: dict[str, Any],
    keys: tuple[str, ...],
    default: Any = None,
) -> Any:
    """
    Devuelve el primer valor no vacío encontrado.
    """

    for key in keys:
        value = source.get(
            key
        )

        if value not in (
            None,
            "",
        ):
            return value

    return default


def _safe_float(
    value: Any,
    default: float,
) -> float:
    """
    Convierte un valor a float sin romper la aplicación.
    """

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return default


def _supabase_base_url() -> str:
    """
    Devuelve la URL de Supabase sin barra final.
    """

    return str(
        SUPABASE_URL
        or ""
    ).strip().rstrip("/")


def _supabase_api_key() -> str:
    """
    Devuelve la clave pública configurada.
    """

    return str(
        SUPABASE_KEY
        or ""
    ).strip()


# =========================================================
# REFRESCAR USUARIO DESDE SUPABASE
# =========================================================


def _refresh_authenticated_user() -> bool:
    """
    Consulta el usuario actual directamente en Supabase Auth.

    Esto es importante porque los planes PRO se guardan en
    auth.users.raw_user_meta_data. Al volver a iniciar sesión,
    esta función garantiza que Streamlit reciba los metadatos
    más recientes:

        plan
        membership_status
        plan_started_at
        plan_expires_at
        payment_provider

    Devuelve True si logró actualizar la sesión.
    """

    if not st.session_state.get(
        "authenticated",
        False,
    ):
        return False

    base_url = _supabase_base_url()
    api_key = _supabase_api_key()

    if not base_url or not api_key:
        return False

    try:
        access_token = ensure_access_token()

    except Exception:
        return False

    if not access_token:
        return False

    try:
        response = requests.get(
            f"{base_url}/auth/v1/user",
            headers={
                "apikey": api_key,
                "Authorization": (
                    f"Bearer {access_token}"
                ),
                "Accept": "application/json",
            },
            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException:
        return False

    if response.status_code >= 400:
        return False

    try:
        payload = response.json()

    except ValueError:
        return False

    if not isinstance(
        payload,
        dict,
    ):
        return False

    user_payload = payload.get(
        "user"
    )

    if isinstance(
        user_payload,
        dict,
    ):
        user = user_payload

    else:
        user = payload

    if not isinstance(
        user,
        dict,
    ):
        return False

    if not user.get(
        "id"
    ):
        return False

    st.session_state.user = user

    metadata = _as_dict(
        user.get(
            "user_metadata",
            {},
        )
    )

    st.session_state.user_metadata = (
        metadata
    )

    return True


# =========================================================
# SINCRONIZACIÓN DE PERFIL
# =========================================================


def _sync_profile_state() -> tuple[str, float, float]:
    """
    Sincroniza nombre, capital, meta y fotografía del perfil
    con st.session_state.

    También conserva los metadatos PRO ya cargados desde
    Supabase Auth.
    """

    raw_user = st.session_state.get(
        "user",
        {},
    )

    user = _as_dict(
        raw_user
    )

    raw_metadata = (
        user.get(
            "user_metadata"
        )
        or user.get(
            "raw_user_meta_data"
        )
        or st.session_state.get(
            "user_metadata"
        )
        or {}
    )

    metadata = _as_dict(
        raw_metadata
    )

    st.session_state.user_metadata = (
        metadata
    )

    trader_name = _first_value(
        metadata,
        (
            "username",
            "full_name",
            "name",
            "display_name",
            "nombre_trader",
        ),
        st.session_state.get(
            "nombre_trader",
            "Trader Pro",
        ),
    )

    capital_actual = _safe_float(
        _first_value(
            metadata,
            (
                "capital_actual",
                "current_capital",
            ),
            st.session_state.get(
                "capital_actual",
                10000.0,
            ),
        ),
        10000.0,
    )

    capital_meta = _safe_float(
        _first_value(
            metadata,
            (
                "capital_meta",
                "target_capital",
            ),
            st.session_state.get(
                "capital_meta",
                15000.0,
            ),
        ),
        15000.0,
    )

    avatar_value = _first_value(
        metadata,
        (
            "avatar_url",
            "profile_image",
            "profile_photo",
            "photo_url",
            "picture",
            "foto_perfil",
            "user_avatar",
            "user_photo",
        ),
        None,
    )

    if avatar_value in (
        None,
        "",
    ):
        avatar_value = _first_value(
            user,
            (
                "avatar_url",
                "profile_image",
                "profile_photo",
                "photo_url",
                "picture",
            ),
            st.session_state.get(
                "profile_image",
            ),
        )

    st.session_state.nombre_trader = str(
        trader_name
    )

    st.session_state.capital_actual = (
        capital_actual
    )

    st.session_state.capital_meta = (
        capital_meta
    )

    if avatar_value not in (
        None,
        "",
    ):
        st.session_state.profile_image = (
            avatar_value
        )

        st.session_state.profile_photo = (
            avatar_value
        )

        st.session_state.avatar_url = (
            avatar_value
        )

        st.session_state.user_avatar = (
            avatar_value
        )

        st.session_state.user_photo = (
            avatar_value
        )

    return (
        str(
            trader_name
        ),
        capital_actual,
        capital_meta,
    )


# =========================================================
# DATOS DEL JOURNAL
# =========================================================


def _load_trades() -> list[dict[str, Any]]:
    """
    Carga los trades desde Supabase sin detener toda la app
    si ocurre un error.
    """

    try:
        trades = list_trades()

        if isinstance(
            trades,
            list,
        ):
            return trades

        return []

    except Exception as exc:
        message = str(exc or "").lower()

        if (
            "jwt expired" in message
            or "sesión expiró" in message
            or "session expired" in message
        ):
            st.session_state.flash_error = (
                "Tu sesión expiró. Inicia sesión nuevamente para continuar."
            )
            st.session_state.authenticated = False
            st.session_state.access_token = ""
            st.rerun()

        st.error(
            "No pudimos cargar tus operaciones en este momento. "
            "Inténtalo nuevamente."
        )

        return []


# =========================================================
# ACCESO Y NAVEGACIÓN
# =========================================================


def _redirect_expired_membership() -> None:
    """
    Si el plan ya venció, permite entrar a la sección de
    membresía, perfil y dashboard, pero evita conservar una
    página PRO seleccionada.

    El bloqueo completo de funciones se conectará después
    usando require_pro_access().
    """

    membership = get_membership_info()

    allowed_pages = {
        "Dashboard",
        "Modificar perfil",
        "AXION PRIME PRO",
    }

    current_page = str(
        st.session_state.get(
            "page",
            "Dashboard",
        )
    )

    if (
        membership.is_expired
        and current_page not in allowed_pages
    ):
        st.session_state.page = (
            "AXION PRIME PRO"
        )

        st.warning(
            "Tu plan PRO venció. Renueva tu membresía "
            "para continuar utilizando las funciones premium."
        )

        st.rerun()



# =========================================================
# PÁGINAS LEGALES PÚBLICAS
# =========================================================


LEGAL_PAGE_CSS = """
<style>
[data-testid="stSidebar"] {
    display: none !important;
}

.block-container {
    max-width: 980px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.ax-legal-shell {
    padding: 28px;
    border: 1px solid rgba(73, 108, 188, .38);
    border-radius: 22px;
    background:
        radial-gradient(circle at 100% 0%, rgba(139, 77, 255, .12), transparent 30%),
        linear-gradient(145deg, rgba(6, 13, 31, .99), rgba(5, 7, 23, .99));
    box-shadow:
        0 28px 82px rgba(0, 0, 0, .38),
        inset 0 1px 0 rgba(255, 255, 255, .03);
}

.ax-legal-brand {
    color: #2bdcff;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.8px;
}

.ax-legal-title {
    margin-top: 10px;
    color: #f7f9ff;
    font-size: clamp(34px, 5vw, 56px);
    line-height: 1;
    letter-spacing: -2px;
    font-weight: 950;
}

.ax-legal-updated {
    margin-top: 10px;
    color: #98a6c2;
    font-size: 13px;
}

.ax-legal-content {
    margin-top: 24px;
    color: #c4cee1;
    font-size: 15px;
    line-height: 1.75;
}

.ax-legal-content h2 {
    margin-top: 28px;
    color: #f1f5ff;
    font-size: 20px;
}

.ax-legal-content a {
    color: #2bdcff;
    text-decoration: none;
}

.ax-legal-content strong {
    color: #f4f7ff;
}

.ax-legal-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 28px;
}

.ax-legal-nav a {
    padding: 10px 14px;
    color: #eef4ff;
    font-size: 13px;
    font-weight: 800;
    text-decoration: none;
    border: 1px solid rgba(43, 220, 255, .28);
    border-radius: 999px;
    background: rgba(43, 220, 255, .06);
}

.ax-legal-back {
    margin-top: 24px;
    padding-top: 18px;
    border-top: 1px solid rgba(72, 101, 165, .20);
}

.ax-legal-back a {
    color: #2bdcff;
    font-weight: 850;
    text-decoration: none;
}
</style>
"""


def _public_path() -> str:
    """
    Obtiene la ruta pública actual, por ejemplo /privacy.

    st.context.url incluye dominio y pathname, pero no incluye
    parámetros de consulta ni fragmentos.
    """

    try:
        current_url = str(
            st.context.url
            or ""
        ).strip()

        path = urlparse(
            current_url
        ).path

    except Exception:
        path = ""

    normalized = (
        str(
            path
            or "/"
        )
        .strip()
        .lower()
        .rstrip("/")
    )

    return normalized or "/"


def _legal_contact_email() -> str:
    email = str(
        ADMIN_EMAIL
        or ""
    ).strip()

    return (
        email
        or "soporte@axionprime.app"
    )


def _legal_document(path: str) -> tuple[str, str] | None:
    contact_email = _legal_contact_email()

    privacy_body = f"""
    <p>
        Esta Política de privacidad explica cómo AXION PRIME trata
        la información de las personas que utilizan la plataforma.
    </p>

    <h2>1. Información que tratamos</h2>
    <p>
        Podemos tratar datos de registro, como correo electrónico,
        identificadores de cuenta y metadatos necesarios para
        autenticar al usuario. También tratamos la información que
        el usuario decide guardar en su journal de trading, perfil y
        herramientas de análisis.
    </p>

    <h2>2. Finalidades</h2>
    <p>
        Utilizamos la información para crear y mantener cuentas,
        prestar las funciones de AXION PRIME, conservar registros,
        brindar soporte, prevenir abuso, gestionar membresías y
        mejorar la seguridad y el funcionamiento del servicio.
    </p>

    <h2>3. Proveedores</h2>
    <p>
        La plataforma puede utilizar proveedores externos, entre
        ellos Supabase para autenticación y almacenamiento, Paddle
        o Flow para procesamiento de pagos, y otros servicios
        técnicos necesarios para operar la aplicación. AXION PRIME
        no almacena directamente los datos completos de tarjetas.
    </p>

    <h2>4. Conservación y seguridad</h2>
    <p>
        Conservamos la información durante el tiempo necesario para
        prestar el servicio, cumplir obligaciones aplicables y
        resolver disputas. Aplicamos medidas técnicas razonables,
        aunque ningún sistema puede garantizar seguridad absoluta.
    </p>

    <h2>5. Derechos y solicitudes</h2>
    <p>
        El usuario puede solicitar acceso, corrección o eliminación
        de sus datos, sujeto a las obligaciones legales y técnicas
        aplicables, escribiendo a
        <a href="mailto:{contact_email}">{contact_email}</a>.
    </p>

    <h2>6. Cambios</h2>
    <p>
        Podemos actualizar esta política para reflejar cambios en el
        servicio o en los requisitos aplicables. La versión vigente
        será la publicada en esta página.
    </p>
    """

    terms_body = f"""
    <p>
        Estos Términos de uso regulan el acceso y uso de AXION PRIME.
        Al crear una cuenta o utilizar la plataforma, el usuario
        acepta estos términos.
    </p>

    <h2>1. Naturaleza del servicio</h2>
    <p>
        AXION PRIME ofrece herramientas de journal, análisis,
        psicotrading, métricas e inteligencia artificial orientadas
        al seguimiento de operaciones. El servicio tiene fines
        informativos y educativos.
    </p>

    <h2>2. Sin asesoría financiera</h2>
    <p>
        AXION PRIME no es un corredor, asesor financiero ni gestor
        de inversiones. Ningún contenido constituye recomendación
        personalizada de inversión. El usuario es responsable de
        sus decisiones, operaciones, riesgos y resultados.
    </p>

    <h2>3. Cuenta y seguridad</h2>
    <p>
        El usuario debe proporcionar información válida, proteger
        sus credenciales y notificar cualquier acceso no autorizado.
        No se permite utilizar la plataforma para fraude, abuso,
        actividades ilegales o interferencia con el servicio.
    </p>

    <h2>4. Prueba y planes</h2>
    <p>
        AXION PRIME puede ofrecer una prueba gratuita de siete días
        y planes mensuales o anuales. Los precios, impuestos,
        monedas y métodos disponibles se muestran antes de completar
        el pago. Los cobros internacionales pueden ser procesados por
        Paddle y los pagos en Chile por Flow.
    </p>

    <h2>5. Renovación y cancelación</h2>
    <p>
        Los planes recurrentes pueden renovarse automáticamente hasta
        que sean cancelados. La cancelación evita futuras renovaciones,
        pero normalmente mantiene el acceso hasta finalizar el periodo
        ya pagado, salvo que la ley o el proveedor indiquen otra cosa.
    </p>

    <h2>6. Disponibilidad</h2>
    <p>
        Procuramos mantener el servicio disponible, pero no garantizamos
        funcionamiento ininterrumpido ni ausencia total de errores.
        Podemos modificar, suspender o retirar funciones cuando sea
        necesario para seguridad, mantenimiento o evolución del producto.
    </p>

    <h2>7. Propiedad intelectual</h2>
    <p>
        La marca, interfaz, código, diseño y contenido propio de AXION
        PRIME están protegidos. La suscripción concede un derecho personal,
        limitado, revocable y no transferible de uso del servicio.
    </p>

    <h2>8. Contacto</h2>
    <p>
        Para consultas sobre estos términos:
        <a href="mailto:{contact_email}">{contact_email}</a>.
    </p>
    """

    refund_body = f"""
    <p>
        Esta Política de reembolsos describe cómo se gestionan las
        solicitudes relacionadas con pagos de AXION PRIME.
    </p>

    <h2>1. Revisión de solicitudes</h2>
    <p>
        Las solicitudes de reembolso se revisan considerando el motivo,
        la fecha de compra, el uso del servicio, las condiciones del
        proveedor de pago y la legislación aplicable.
    </p>

    <h2>2. Suscripciones</h2>
    <p>
        Cancelar una suscripción impide renovaciones futuras. Salvo que
        exista un derecho legal aplicable o que se apruebe expresamente
        un reembolso, la cancelación no implica automáticamente la
        devolución del periodo ya iniciado.
    </p>

    <h2>3. Problemas técnicos o cobros incorrectos</h2>
    <p>
        Si existe un cobro duplicado, un importe incorrecto o un problema
        técnico que impida utilizar el servicio, el usuario debe contactar
        soporte aportando el correo de la cuenta, fecha, importe y
        referencia de la transacción.
    </p>

    <h2>4. Compras procesadas por terceros</h2>
    <p>
        Los pagos pueden ser gestionados por Paddle, Flow u otros
        proveedores. Algunas solicitudes deben tramitarse mediante el
        proveedor correspondiente y están sujetas a sus condiciones,
        procesos antifraude y obligaciones legales.
    </p>

    <h2>5. Plazo para solicitar revisión</h2>
    <p>
        Recomendamos presentar cualquier solicitud dentro de los
        catorce días siguientes al cobro. Este plazo no limita derechos
        obligatorios que correspondan al consumidor según su jurisdicción.
    </p>

    <h2>6. Contacto</h2>
    <p>
        Envía la solicitud a
        <a href="mailto:{contact_email}">{contact_email}</a>
        indicando el motivo y los datos necesarios para localizar el pago.
    </p>
    """

    documents = {
        "/privacy": (
            "Política de privacidad",
            privacy_body,
        ),
        "/terms": (
            "Términos de uso",
            terms_body,
        ),
        "/refund": (
            "Política de reembolsos",
            refund_body,
        ),
    }

    return documents.get(
        path
    )


def _render_public_legal_page(
    title: str,
    body: str,
) -> None:
    """
    Renderiza una política pública sin pedir autenticación.
    """

    st.markdown(
        LEGAL_PAGE_CSS,
        unsafe_allow_html=True,
    )

    st.html(
        f"""
        <main class="ax-legal-shell">
            <div class="ax-legal-brand">
                AXION PRIME · INFORMACIÓN LEGAL
            </div>

            <div class="ax-legal-title">
                {title}
            </div>

            <div class="ax-legal-updated">
                Última actualización: 5 de agosto de 2026
            </div>

            <section class="ax-legal-content">
                {body}
            </section>

            <nav class="ax-legal-nav">
                <a href="/privacy" target="_self">
                    Privacidad
                </a>

                <a href="/terms" target="_self">
                    Términos
                </a>

                <a href="/refund" target="_self">
                    Reembolsos
                </a>
            </nav>

            <div class="ax-legal-back">
                <a href="/" target="_self">
                    ← Volver a AXION PRIME
                </a>
            </div>
        </main>
        """
    )


def _handle_public_page() -> None:
    """
    Atiende rutas públicas antes de ejecutar el bloqueo de login.
    """

    document = _legal_document(
        _public_path()
    )

    if document is None:
        return

    title, body = document

    _render_public_legal_page(
        title,
        body,
    )

    st.stop()


# =========================================================
# INICIALIZACIÓN
# =========================================================


_handle_public_page()

validate_config()
init_state()


# =========================================================
# AUTENTICACIÓN
# =========================================================


if not st.session_state.get(
    "authenticated",
    False,
):
    render_v2_auth()
    st.stop()


# =========================================================
# REFRESCAR DATOS DEL USUARIO
# =========================================================


_refresh_authenticated_user()

# Si el refresh token también expiró o fue revocado,
# core.api limpia la sesión. En ese caso volvemos al login
# inmediatamente y evitamos mostrar errores técnicos 401.
if not st.session_state.get(
    "authenticated",
    False,
):
    st.session_state.flash_error = (
        "Tu sesión expiró. Inicia sesión nuevamente para continuar."
    )
    st.rerun()


# =========================================================
# PERFIL Y MEMBRESÍA
# =========================================================


trader_name, capital_actual, capital_meta = (
    _sync_profile_state()
)

_redirect_expired_membership()

render_v2_sidebar()


# =========================================================
# DATOS DEL JOURNAL
# =========================================================


trades = _load_trades()

df = prepare_df(
    trades
)


# =========================================================
# NAVEGACIÓN
# =========================================================


page = st.session_state.get(
    "page",
    "Dashboard",
)


if page == "Dashboard":

    render_v2_dashboard(
        df,
        trader_name=trader_name,
        initial_capital=capital_actual,
    )


elif page == "Modificar perfil":

    render_v2_profile()


elif page == "Registrar Trade":

    render_register_trade()


elif page == "Track Record":

    render_track_record(
        df
    )


elif page == "Chat IA":

    render_chat(
        df
    )


elif page == "Psicotrading":

    render_psychotrading(
        df
    )


elif page == "Análisis IA":

    render_ai_analysis(
        df
    )


elif page == "Proyecciones":

    render_projections()


elif page == "Lotaje":

    render_lotage()


elif page == "Sesiones":

    render_sessions()


elif page == "Noticias":

    render_news()


elif page == "AXION PRIME PRO":

    render_subscription()


else:

    st.session_state.page = (
        "Dashboard"
    )

    st.rerun()
