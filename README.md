# Quantitative Momentum Strategy
> A systematic momentum-based equity strategy built from scratch  
> by a Year 1 CS & Business student — combining pandas, yfinance,  
> and machine learning to study whether momentum actually exists in real markets.

---
*First-year independent research project — built alongside a tech internship*
## Overview
This project explores whether momentum exists in US equities using systematic backtesting and simple machine learning models. I started by building intuition around stocks, returns, and data handling using `yfinance` and pandas, then gradually moved into formal factor construction and portfolio testing.

The key finding is that momentum does exist cross-sectionally, but is highly sensitive to market regimes, data quality, and implementation details.

---

## Strategy Logic
- Universe: 20 US large-cap stocks across tech, financials, healthcare, and energy  
- Signal: Cross-sectional momentum based on past 1M, 3M, 6M, and 12M cumulative returns  
- Ranking: Each month, stocks are ranked by trailing performance (sector-aware in some tests)  
- Portfolio: Long top 5 ranked stocks, equal-weighted; compared against bottom 5  
- Rebalancing: Monthly using non-overlapping return windows to avoid lookahead bias  

---

## Backtest Results

| Metric | 2 Year | 3 Year | 5 Year |
|---|---|---|---|
| Sharpe Ratio | 1.29 | 1.64 | 0.92 |
| Max Drawdown | -12.9% | -12.9% | -30.50% |
| Hit Rate | 54% | 58% | 53% |
| Avg Monthly Return (Top 5) | 2.4% | 2.66% | 1.93% |

---

## Key Research Findings

- A naive momentum strategy on 20 stocks initially showed strong results but was heavily concentrated in tech (~40% exposure in top portfolios), increasing correlated drawdown risk.  
- Early linear regression produced an artificially high R² (~0.90) due to overlapping rolling windows, but corrected non-overlapping returns reduced it to ~0.0003, showing no predictive power.  
- Cross-sectional momentum consistently outperformed bottom quintile stocks, with top 5 averaging ~2.66% monthly vs ~1.30% for losers over a 3-year window.  
- Strategy robustness testing across multiple time windows showed relatively stable Sharpe ratios (1.29–1.64), but drawdowns worsened significantly during the 2022 market reversal, highlighting momentum crash risk.  
- Feature engineering was based on academic momentum literature (1M, 3M, 6M, 12M windows) rather than data-driven selection to avoid overfitting and lookahead bias.  

---

## ML Experiment
I applied a Random Forest model using momentum features (1M, 3M, 6M, 12M returns) to predict next-month returns. The model produced a negative test R² (-0.0617), performing worse than a naive mean prediction. Feature importance showed short-term momentum (1M) dominated (~49.6%), while 12M momentum had essentially zero contribution.

This failure was not due to the model itself, but due to data limitations: only ~20 stocks and a few years of monthly observations is insufficient for a high-variance model like Random Forest to generalise. This reinforced the idea that financial prediction is often data-constrained rather than model-constrained.

---

## Live Deployment
A simplified version of the momentum strategy is deployed with $500 capital via IBKR. The strategy follows a rule-based monthly rebalance system using top-ranked momentum stocks, with results logged and reviewed monthly. The goal is not high-frequency trading, but systematic exposure to momentum factors with controlled risk.

---

## Tech Stack
- Python  
- pandas  
- numpy  
- scikit-learn  
- yfinance  
- matplotlib  

---

## Project Structure
```
quant-momentum-aaryan/
├── src/
│ ├── backtest.py
│ ├── model.py
│ ├── features.py
│ ├── metrics.py
│ └── universe.py
├── results/
├── live/trading_log.md
├── RESEARCH_JOURNAL.md
└── requirements.txt
```

---

## How To Run
```bash
pip install -r requirements.txt
python src/backtest.py
```
## Next Steps
- Expand universe to 100+ stocks to improve statistical power and reduce idiosyncratic noise
- Extend dataset to 10–20 years of historical data to properly test long-horizon momentum effects
- Introduce sector-neutral ranking to reduce concentration risk and improve diversification stability

---
