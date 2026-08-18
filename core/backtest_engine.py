from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


Direction = Literal["LONG", "SHORT"]


@dataclass
class TradePlan:
    direction: Direction
    entry: float
    stop: float
    target: float
    risk_amount: float

    @property
    def risk_distance(self) -> float:
        return abs(self.entry - self.stop)

    @property
    def reward_distance(self) -> float:
        return abs(self.target - self.entry)

    @property
    def rr(self) -> float:
        if self.risk_distance <= 0:
            return 0.0
        return self.reward_distance / self.risk_distance

    def validate(self) -> tuple[bool, str]:
        if self.entry <= 0 or self.stop <= 0 or self.target <= 0:
            return False, "Entrada, SL y TP deben ser mayores que cero."
        if self.risk_amount <= 0:
            return False, "El riesgo debe ser mayor que cero."
        if self.direction == "LONG" and not (self.stop < self.entry < self.target):
            return False, "Para LONG debe cumplirse SL < Entrada < TP."
        if self.direction == "SHORT" and not (self.target < self.entry < self.stop):
            return False, "Para SHORT debe cumplirse TP < Entrada < SL."
        return True, ""


def evaluate_trade(
    plan: TradePlan,
    candles: pd.DataFrame,
) -> dict:
    if candles.empty:
        return {"status": "OPEN", "r_multiple": 0.0, "pnl": 0.0, "mfe_r": 0.0, "mae_r": 0.0}

    risk = plan.risk_distance
    if risk <= 0:
        return {"status": "INVALID", "r_multiple": 0.0, "pnl": 0.0, "mfe_r": 0.0, "mae_r": 0.0}

    entered = False
    exit_price = None
    status = "PENDING"
    max_favorable = 0.0
    max_adverse = 0.0
    entry_time = None
    exit_time = None

    for _, candle in candles.iterrows():
        low = float(candle["low"])
        high = float(candle["high"])

        if not entered:
            if low <= plan.entry <= high:
                entered = True
                entry_time = candle["open_time"]
                status = "OPEN"
            else:
                continue

        if plan.direction == "LONG":
            max_favorable = max(max_favorable, high - plan.entry)
            max_adverse = max(max_adverse, plan.entry - low)

            # Conservador: si SL y TP caen dentro de la misma vela, asumir SL primero.
            hit_stop = low <= plan.stop
            hit_target = high >= plan.target
            if hit_stop:
                exit_price = plan.stop
                status = "LOSS"
                exit_time = candle["open_time"]
                break
            if hit_target:
                exit_price = plan.target
                status = "WIN"
                exit_time = candle["open_time"]
                break
        else:
            max_favorable = max(max_favorable, plan.entry - low)
            max_adverse = max(max_adverse, high - plan.entry)

            hit_stop = high >= plan.stop
            hit_target = low <= plan.target
            if hit_stop:
                exit_price = plan.stop
                status = "LOSS"
                exit_time = candle["open_time"]
                break
            if hit_target:
                exit_price = plan.target
                status = "WIN"
                exit_time = candle["open_time"]
                break

    if not entered:
        return {
            "status": "PENDING",
            "r_multiple": 0.0,
            "pnl": 0.0,
            "mfe_r": 0.0,
            "mae_r": 0.0,
            "entry_time": None,
            "exit_time": None,
        }

    if exit_price is None:
        last = float(candles.iloc[-1]["close"])
        signed = (last - plan.entry) if plan.direction == "LONG" else (plan.entry - last)
        r_multiple = signed / risk
        pnl = r_multiple * plan.risk_amount
    else:
        signed = (exit_price - plan.entry) if plan.direction == "LONG" else (plan.entry - exit_price)
        r_multiple = signed / risk
        pnl = r_multiple * plan.risk_amount

    return {
        "status": status,
        "r_multiple": float(r_multiple),
        "pnl": float(pnl),
        "mfe_r": float(max_favorable / risk),
        "mae_r": float(max_adverse / risk),
        "entry_time": entry_time,
        "exit_time": exit_time,
    }
