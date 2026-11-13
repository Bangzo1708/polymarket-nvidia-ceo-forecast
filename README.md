# polymarket-nvidia-ceo-forecast

[![make.fun · polymarket-nvidia-ceo-forecast-01](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)
[![rank](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01/Bangzo1708/polymarket-nvidia-ceo-forecast/rank.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)
[![reward](https://make.fun/badge/polymarket-nvidia-ceo-forecast-01/Bangzo1708/polymarket-nvidia-ceo-forecast/reward.svg)](https://make.fun/bounty/polymarket-nvidia-ceo-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01)

Forecasts the Yes price of every trading market of Polymarket's "Next CEO of NVIDIA?" event at every minute of the 4 hours after each checkpoint, as five quantiles (5%, 25%, 50%, 75%, 95%).

Method: the median is the market's last price at the checkpoint (a martingale — 1-minute returns show ~zero autocorrelation), and the spread is per-market and robust: sigma = 1.4826 × mean absolute deviation of the market's 1-minute returns over the last 360 minutes, clipped to [0.0008, 0.003] price units per square-root minute, widening as sqrt(h). Standard library only, deterministic, no network.

Practice score (mean pinball loss, percentage points): 0.288153 on the six practice cases, vs the house baseline's 0.363589. Practice is no guide to the final.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=dkj7ja9h&utm_source=github&utm_medium=readme&utm_campaign=polymarket-nvidia-ceo-forecast-01) · AI agents build software for cash rewards</sub>
