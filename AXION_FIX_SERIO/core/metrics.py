from __future__ import annotations

import pandas as pd


# =========================================================
# AXION PRIME X10 PRO
# MÉTRICAS Y PREPARACIÓN DE DATOS
# =========================================================


def prepare_df(
    trades: list[dict],
) -> pd.DataFrame:
    """
    Convierte los trades recibidos desde Supabase
    en un DataFrame preparado para gráficos y métricas.
    """

    df = pd.DataFrame(
        trades
    )

    if df.empty:

        return df


    numeric_columns = [
        "beneficio_usd",
        "rr",
        "precio_entrada",
        "stop_loss",
        "take_profit",
    ]


    for column in numeric_columns:

        if column not in df.columns:

            df[column] = 0.0


        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        ).fillna(0.0)


    if "fecha" not in df.columns:

        df["fecha"] = None


    df["fecha_dt"] = pd.to_datetime(
        df["fecha"],
        errors="coerce",
    )


    if "created_at" in df.columns:

        df["created_at_dt"] = pd.to_datetime(
            df["created_at"],
            errors="coerce",
        )

    else:

        df["created_at_dt"] = (
            df["fecha_dt"]
        )


    return df


# =========================================================
# RESUMEN GENERAL
# =========================================================

def calculate_summary(
    df: pd.DataFrame,
    initial_capital: float,
) -> dict:
    """
    Calcula las métricas principales del dashboard.
    """

    initial_capital = float(
        initial_capital
    )


    if df.empty:

        return {

            "pnl": 0.0,

            "balance": initial_capital,

            "total": 0,

            "wins": 0,

            "losses": 0,

            "break_even": 0,

            "win_rate": 0.0,

            "profit_factor": 0.0,

            "average_rr": 0.0,

            "average_win": 0.0,

            "average_loss": 0.0,

            "drawdown": 0.0,

            "drawdown_percent": 0.0,

            "best_trade": 0.0,

            "worst_trade": 0.0,
        }


    pnl_series = pd.to_numeric(
        df["beneficio_usd"],
        errors="coerce",
    ).fillna(0.0)


    pnl = float(
        pnl_series.sum()
    )


    wins_df = df[
        pnl_series > 0
    ]


    losses_df = df[
        pnl_series < 0
    ]


    break_even_df = df[
        pnl_series == 0
    ]


    total = len(
        df
    )


    wins = len(
        wins_df
    )


    losses = len(
        losses_df
    )


    break_even = len(
        break_even_df
    )


    win_rate = (

        wins
        / total
        * 100

        if total
        else 0.0
    )


    gross_profit = float(

        wins_df[
            "beneficio_usd"
        ].sum()

        if not wins_df.empty
        else 0.0
    )


    gross_loss = abs(
        float(

            losses_df[
                "beneficio_usd"
            ].sum()

            if not losses_df.empty
            else 0.0
        )
    )


    if gross_loss > 0:

        profit_factor = (
            gross_profit
            / gross_loss
        )

    elif gross_profit > 0:

        profit_factor = (
            gross_profit
        )

    else:

        profit_factor = 0.0


    average_rr = float(

        df["rr"].mean()

        if "rr" in df.columns
        else 0.0
    )


    average_win = float(

        wins_df[
            "beneficio_usd"
        ].mean()

        if not wins_df.empty
        else 0.0
    )


    average_loss = float(

        losses_df[
            "beneficio_usd"
        ].mean()

        if not losses_df.empty
        else 0.0
    )


    ordered_df = df.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ]
    ).copy()


    ordered_df[
        "equity"
    ] = (

        initial_capital
        + ordered_df[
            "beneficio_usd"
        ].cumsum()
    )


    ordered_df[
        "equity_peak"
    ] = (

        ordered_df[
            "equity"
        ].cummax()
    )


    ordered_df[
        "drawdown"
    ] = (

        ordered_df[
            "equity"
        ]
        -
        ordered_df[
            "equity_peak"
        ]
    )


    drawdown = float(

        ordered_df[
            "drawdown"
        ].min()

        if not ordered_df.empty
        else 0.0
    )


    peak_for_drawdown = float(

        ordered_df[
            "equity_peak"
        ].max()

        if not ordered_df.empty
        else initial_capital
    )


    drawdown_percent = (

        abs(drawdown)
        / peak_for_drawdown
        * 100

        if peak_for_drawdown > 0
        else 0.0
    )


    best_trade = float(
        pnl_series.max()
    )


    worst_trade = float(
        pnl_series.min()
    )


    return {

        "pnl":
            pnl,

        "balance":
            initial_capital
            + pnl,

        "total":
            total,

        "wins":
            wins,

        "losses":
            losses,

        "break_even":
            break_even,

        "win_rate":
            win_rate,

        "profit_factor":
            profit_factor,

        "average_rr":
            average_rr,

        "average_win":
            average_win,

        "average_loss":
            average_loss,

        "drawdown":
            drawdown,

        "drawdown_percent":
            drawdown_percent,

        "best_trade":
            best_trade,

        "worst_trade":
            worst_trade,
    }


# =========================================================
# CURVA DE EQUITY
# =========================================================

def build_equity_curve(
    df: pd.DataFrame,
    initial_capital: float,
) -> pd.DataFrame:
    """
    Devuelve un DataFrame preparado para la curva de equity.
    """

    if df.empty:

        return pd.DataFrame(
            columns=[
                "fecha_dt",
                "equity",
            ]
        )


    equity_df = df.sort_values(
        [
            "fecha_dt",
            "created_at_dt",
        ]
    ).copy()


    equity_df[
        "equity"
    ] = (

        float(initial_capital)
        +
        equity_df[
            "beneficio_usd"
        ].cumsum()
    )


    return equity_df


# =========================================================
# PNL POR ACTIVO
# =========================================================

def pnl_by_asset(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrupa el beneficio o pérdida por activo.
    """

    if (
        df.empty
        or
        "par" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "par",
                "beneficio_usd",
            ]
        )


    return (
        df
        .groupby(
            "par",
            dropna=False,
        )[
            "beneficio_usd"
        ]
        .sum()
        .reset_index()
        .sort_values(
            "beneficio_usd",
            ascending=False,
        )
    )


# =========================================================
# PNL POR EMOCIÓN
# =========================================================

def pnl_by_emotion(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Agrupa resultados por estado emocional.
    """

    if (
        df.empty
        or
        "emocion" not in df.columns
    ):

        return pd.DataFrame(
            columns=[
                "emocion",
                "trades",
                "pnl_total",
                "pnl_promedio",
            ]
        )


    emotion_df = (

        df
        .groupby(
            "emocion",
            dropna=False,
        )
        .agg(

            trades=(
                "beneficio_usd",
                "count",
            ),

            pnl_total=(
                "beneficio_usd",
                "sum",
            ),

            pnl_promedio=(
                "beneficio_usd",
                "mean",
            ),
        )
        .reset_index()
    )


    return emotion_df


# =========================================================
# PROP FIRM SCORE
# =========================================================

def calculate_prop_firm_score(
    summary: dict,
) -> int:
    """
    Score aproximado de disciplina y rendimiento.
    """

    score = 50.0


    win_rate = float(
        summary.get(
            "win_rate",
            0.0,
        )
    )


    profit_factor = float(
        summary.get(
            "profit_factor",
            0.0,
        )
    )


    average_rr = float(
        summary.get(
            "average_rr",
            0.0,
        )
    )


    drawdown_percent = float(
        summary.get(
            "drawdown_percent",
            0.0,
        )
    )


    total = int(
        summary.get(
            "total",
            0,
        )
    )


    score += min(
        15,
        win_rate
        * 0.20,
    )


    score += min(
        15,
        profit_factor
        * 6,
    )


    score += min(
        10,
        average_rr
        * 3,
    )


    score -= min(
        25,
        drawdown_percent
        * 2,
    )


    if total < 5:

        score -= 8


    score = max(
        0,
        min(
            100,
            score,
        ),
    )


    return int(
        round(score)
    )
