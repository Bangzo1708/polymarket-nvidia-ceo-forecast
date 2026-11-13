#!/usr/bin/env python3
"""Forecast Polymarket's next NVIDIA CEO prices minute by minute, 4 hours ahead.

Entry for make.fun competition polymarket-nvidia-ceo-forecast-01.

Method (fixed in advance, tuned only on the 6 practice cases):
  median = the market's last price at the checkpoint (a martingale: 1-minute
  returns show ~zero autocorrelation, so the last price is the best median);
  quantiles = median + z_tau * sigma_i * sqrt(h), clamped to [0, 1] and
  rounded to 6 decimals, for h = 1..240 minutes after the checkpoint.

  sigma_i is per-market, estimated robustly from the market's own recent
  1-minute returns: sigma_i = 1.4826 * mean(|r - mean(r)|) over the last
  360 minutes, clipped to [0.0008, 0.003]. The mean-absolute-deviation
  estimator is used instead of the standard deviation so a single jump does
  not inflate the spread; the clip keeps dead markets wide enough to cover
  their occasional jumps and volatile markets from going absurdly wide.
  The house baseline's one-size-fits-all 0.0025 is too wide for the mostly
  quiet minutes and too narrow for the markets that actually move.

Practice score (mean pinball loss, percentage points): 0.288153, vs the
house baseline's 0.363589 on the same six practice cases (scored against
Polymarket's own recorded history). Practice is no guide to the final.

Standard library only. Deterministic: pure functions of the input file, no
randomness, no wall-clock, no network. Reads $MAKEFUN_INPUT_DIR (else
/input), writes $MAKEFUN_OUTPUT_DIR (else /output).
"""

import json
import math
import os
import sys

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

QUANTILES = [0.05, 0.25, 0.5, 0.75, 0.95]
# Standard normal quantiles at the five levels, to 6 decimals.
Z = [-1.644854, -0.67449, 0.0, 0.67449, 1.644854]

# Robust per-market spread, in price units per square-root minute.
WINDOW_MINUTES = 360
SIGMA_FLOOR = 0.0008
SIGMA_CAP = 0.003


def price6(x):
    """Clamp to [0, 1] and round to 6 decimals (0, never -0)."""
    return round(min(1.0, max(0.0, x)) * 1_000_000) / 1_000_000 + 0.0


def market_sigma(prices):
    """Robust spread of 1-minute moves over the recent window."""
    n = len(prices)
    if n < 2:
        return SIGMA_FLOOR
    seg = prices[-WINDOW_MINUTES:] if n > WINDOW_MINUTES else prices
    moves = [seg[i + 1] - seg[i] for i in range(len(seg) - 1)]
    if not moves:
        return SIGMA_FLOOR
    mu = sum(moves) / len(moves)
    mad = sum(abs(v - mu) for v in moves) / len(moves)
    sigma = 1.4826 * mad
    if sigma < SIGMA_FLOOR:
        return SIGMA_FLOOR
    if sigma > SIGMA_CAP:
        return SIGMA_CAP
    return sigma


def forecast_market(market, horizon):
    prices = market["prices"]
    if not prices:
        return [[0.5, 0.5, 0.5, 0.5, 0.5] for _ in range(horizon)]
    x = prices[-1]
    sigma = market_sigma(prices)
    rows = []
    for h in range(1, horizon + 1):
        s = sigma * math.sqrt(h)
        row = sorted(price6(x + z * s) for z in Z)
        rows.append(row)
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for fname in inputs:
        case_id = fname[: -len(".in")]
        with open(os.path.join(INPUT_DIR, fname), "r", encoding="utf-8") as f:
            case = json.load(f)
        if (
            case["quantiles"] != QUANTILES
        ):
            raise ValueError(
                "%s asks for quantiles %r, not %r"
                % (fname, case["quantiles"], QUANTILES)
            )
        horizon = case.get("horizon_minutes") or 240
        forecasts = [
            {"id": m["id"], "q": forecast_market(m, horizon)}
            for m in case["markets"]
        ]
        out_path = os.path.join(OUTPUT_DIR, case_id + ".out")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"forecasts": forecasts}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
