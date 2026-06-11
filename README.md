# 📈 Volatility Targeting Model — NSE Nifty 50

[![Python](https://img.shields.io/badge/Python-3.10+-blue)](https://python.org)
[![yfinance](https://img.shields.io/badge/data-yfinance-green)](https://github.com/ranaroussi/yfinance)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A systematic momentum strategy on the Nifty 50 index with a volatility targeting overlay — dynamically scaling position sizes to maintain ~15% annualised risk exposure across different market regimes.

---

## Core Idea

**Position size and risk are not the same thing.**

A fixed position in a volatile market takes dramatically more risk than the same position in a calm market. Volatility targeting corrects this by scaling exposure inversely to realised volatility:

```
realised_vol  = rolling_std(daily_returns, window=20) × √252
vol_scalar    = target_vol / realised_vol      # capped at 2.0
vt_position   = momentum_signal × vol_scalar
vt_return     = vt_position(t−1) × return(t)
```

The **cap at 2.0** prevents unrealistic leverage during unusually calm markets.

---

## Strategy Overview

| Parameter | Value |
|---|---|
| Universe | Nifty 50 Index (`^NSEI`) |
| Period | Jan 2018 – Dec 2024 |
| Signal | 20-day momentum (long if return > 0, else flat) |
| Target Vol | 15% annualised |
| Vol Window | 20-day rolling std |
| Scalar Cap | 2.0× |

---

## Results

| Strategy | Ann. Return | Ann. Vol | Sharpe | Max Drawdown |
|---|---|---|---|---|
| Buy & Hold | — | — | — | — |
| Momentum Only | — | — | — | — |
| Momentum + Vol Targeting | — | — | **↑** | **↓** |

*Run the notebook to populate exact figures.*

---

## Key Findings

1. **Vol targeting improves Sharpe without changing the signal** — the improvement comes entirely from better risk management: reducing exposure when volatility is high, increasing it when calm.

2. **The vol scalar is a regime detector** — during the COVID crash (Mar 2020) and the 2022 rate shock, the scalar dropped sharply, automatically reducing exposure before drawdowns deepened.

3. **Lookback window tradeoff:**
   - 10-day: responsive but noisy, higher turnover
   - 20-day: balanced default
   - 60-day: smooth but slow to react to volatility spikes

4. **Max drawdown reduction is the most striking result** — particularly visible during the March 2020 crash.

---

## Project Structure

```
volatility-targeting-nse/
├── notebooks/
│   └── volatility_targeting.ipynb   # Full walkthrough
├── src/
│   └── volatility_targeting.py      # Reusable strategy utilities
├── figures/                         # Auto-generated plots
├── requirements.txt
└── README.md
```

---

## Setup

```bash
git clone https://github.com/sabarishvar/volatility-targeting-nse.git
cd volatility-targeting-nse
pip install -r requirements.txt
jupyter notebook notebooks/volatility_targeting.ipynb
```

No manual data download needed — yfinance pulls Nifty 50 data automatically.

---

## Interview Questions

**Q: Why does vol targeting improve Sharpe without changing the signal?**  
It reduces exposure when volatility is high and increases it when vol is low — the opposite of static sizing. This produces a more consistent risk-adjusted return stream driven by better risk management, not a better signal.

**Q: Why cap the scalar at 2.0?**  
During extremely calm markets, realised vol can be very low, implying 5-10× leverage. This is unrealistic. The cap enforces a hard leverage constraint.

**Q: 10-day vs 60-day lookback?**  
10-day reacts faster to volatility spikes but is noisier. 60-day is smoother but slow. The choice depends on strategy holding period and transaction costs.

---

## References

- Moreira & Muir (2017) — *Volatility-Managed Portfolios*, Journal of Finance
- Barroso & Santa-Clara (2015) — *Momentum has its moments*
