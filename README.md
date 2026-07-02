# Quantitative Momentum Strategy
> A systematic momentum-based equity strategy built from scratch  
> by a Year 1 CS & Business student — live deployed on IBKR with real capital,  
> monthly rebalances, and automated daily monitoring.

*First-year independent research project, built alongside a tech internship*

---

## Overview

This project builds and deploys a cross-sectional momentum strategy on the
full S&P 500 universe. Starting from first principles — data pulling, return
calculation, signal construction — the project has evolved through multiple
iterations of backtesting, bug fixing, and live deployment.

The core finding is that momentum exists cross-sectionally in US equities,
but is highly sensitive to market regimes, data quality, and implementation
details. The most instructive lessons came from live deployment, not backtesting.

---

## Strategy Logic

- **Universe:** Full S&P 500 — 503 large-cap US stocks across 11 GICS sectors,
  filtered to 494 stocks after corporate action screening
- **Signal:** 12-1 month cross-sectional momentum — cumulative return from
  t-12 to t-1, skipping the most recent month to avoid short-term reversal
  (Jegadeesh and Titman, 1993)
- **Ranking:** Each month, all stocks ranked globally by trailing momentum score
- **Portfolio:** Long top 25 ranked stocks, equal-weighted
- **Sector cap:** Maximum 2 positions per GICS sector
- **Rebalancing:** Monthly, first trading day of each month
- **Corporate action filter:** Stocks with fewer than 47 months of price
  history excluded — removes recent IPOs and spin-offs that produce
  artifically inflated momentum scores

---

## Backtest Results

| Metric | Value |
|---|---|
| Annualised Sharpe Ratio | 1.76 |
| Average Monthly Return (Top 25) | 4.76% |
| Average Monthly Return (Bottom 25) | 0.91% |
| Cumulative Return (3 year) | 3.71x |
| Maximum Drawdown | -17.96% |
| Hit Rate | 66.67% |
| Universe | 494 stocks (S&P 500, filtered) |
| Lookback | 12-1 month momentum |
| Data window | 4 years |

---

## Key Research Findings

Cross-sectional momentum consistently separates top and bottom performers,
with the top 25 averaging 4.76% monthly vs 0.91% for the bottom 25 over
the backtest period. Hit rate of 66.67% means the top portfolio outperformed
the bottom portfolio in two out of every three months.

Early versions of the strategy used a 1-month return signal rather than
the academically standard 12-1 month lookback. The corrected signal improved
all performance metrics and is now the production version. The error and
its discovery are documented in full in the trading log.

Corporate actions are a silent source of signal corruption. Two instances
were caught in live deployment: DuPont's 1-for-3 reverse stock split in
June 2026 (DD ranked #1 at 184% — excluded) and the Western Digital
spin-off SNDK in July 2026 (ranked #1 at 5,197% — excluded after filter).
Extreme momentum scores are now manually verified against Google Finance
before execution.

Early regression experiments showed artificially high R² (~0.90) from
overlapping return windows. Corrected non-overlapping windows reduced R²
to ~0.0003, showing no predictive power — confirming momentum is better
captured cross-sectionally than via regression on individual stocks.

A Random Forest model trained on 1M, 3M, 6M, 12M momentum features
produced negative test R² (-0.0617), performing worse than a naive mean
predictor. This was attributed to data constraints (insufficient observations
for a high-variance model) rather than model failure, reinforcing the view
that financial prediction is often data-constrained rather than model-constrained.

---

## Live Deployment

The strategy runs live on IBKR Lite with $250 deployed capital. Monthly
rebalances are executed on the first trading day of each month. An automated
daily monitoring script sends portfolio updates at 3pm SGT and triggers
immediate alerts on any individual stock move exceeding 3%.

Current portfolio (as of July 1 2026):

| Stock | Sector | Momentum Score (12-1M) |
|---|---|---|
| MU | Information Technology | 959% (verified) |
| WDC | Information Technology | 714% (verified) |
| AMAT | Information Technology | 304% (verified) |
| MRVL | Information Technology | 271% (verified) |
| MRNA | Health Care | 137% |
| CAT | Industrials | 145% |

Full rebalance history, fill prices, realised P&L, and decision rationale
are documented in the trading log.

**Current performance:** +2.76% since June 5 2026 entry

---

## ML Experiment

A Random Forest model was trained using momentum features (1M, 3M, 6M,
12M returns) to predict next-month individual stock returns. The model
produced a negative test R² (-0.0617), performing worse than a naive mean
prediction. Feature importance showed short-term momentum (1M) dominated
at ~49.6%, while 12M momentum contributed essentially zero.

This failure reinforced two things: financial prediction is data-constrained
at small sample sizes, and cross-sectional ranking outperforms single-stock
return prediction as a portfolio construction method.

---

## Signal Verification Protocol

Any momentum score above 200% is manually verified against Google Finance
before execution. Verified returns from the July 2026 rebalance:

| Stock | Script Score | Google Finance 1Y | Verdict |
|---|---|---|---|
| MU | 959% | +754% | Real — HBM memory supercycle |
| WDC | 714% | +837% | Real — flash storage cycle |
| AMAT | 304% | +254% | Real — semiconductor capex cycle |
| MRVL | 271% | +257% | Real — AI infrastructure demand |

Score discrepancies between script and Google Finance reflect differing
lookback windows. All signals confirmed valid.

---

## Next Steps

- Multi-factor model incorporating value (P/B ratio) and quality
  (gross profitability) alongside momentum, drawing on Fama-French (1992)
  and Novy-Marx (2013)
- Improved corporate action detection beyond history-length filtering
- Benchmark comparison against SPY on a monthly basis
- Extended backtest to 10 years to properly test momentum crash risk

---

## Tech Stack

- Python
- pandas
- numpy
- scikit-learn
- yfinance
- matplotlib
- smtplib (automated monitoring)

---

## Project Structure
quant-momentum-aaryan/

├── src/

│   ├── quant_momentum.py       # Main signal generation and backtest

│   ├── portfolio_monitor.py    # Automated daily email monitoring

│   └── positions.json          # Live portfolio positions

├── live/

│   └── trading_log.md          # Full rebalance history and decision log

├── results/

│   └── momentum_chart_sp500.png

├── RESEARCH_JOURNAL.md

└── requirements.txt
---

## How To Run

```bash
pip install -r requirements.txt
python src/quant_momentum.py
```

---

## References

- Jegadeesh, N. and Titman, S. (1993). Returns to buying winners and
  selling losers: Implications for stock market efficiency. Journal of Finance.
- Fama, E. and French, K. (1992). The cross-section of expected stock returns.
  Journal of Finance.
- Novy-Marx, R. (2013). The other side of value: The gross profitability premium.
  Journal of Financial Economics.
- Asness, C., Moskowitz, T. and Pedersen, L. (2013). Value and momentum
  everywhere. Journal of Finance.
