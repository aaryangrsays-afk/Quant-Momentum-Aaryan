# Trading Log — Quant Momentum Strategy

---

## Strategy Note — Capital Constraints

The live strategy runs 5 positions due to capital constraints ($250 deployed).
This differs from the backtested 57-stock model in key ways:

- **Concentration:** 20% per position vs ~7% in backtest (14 of 57 stocks)
- **Selection:** Sector-neutral top-1 per sector vs global top-14 ranking
- **Risk profile:** Single stock events have outsized impact at this scale

This is a capital-constrained approximation of the full strategy, not an
equivalent deployment. Live results should be interpreted in this context.

---

## Strategy Evaluation Criteria

Strategy will be considered failing if:
- Hit rate stays below 50% for 3 consecutive months
- Portfolio drops more than 25% from starting capital ($187.50)
- Live monthly returns are consistently worse than SPY for 4+ months in a row

---

## Pre-Trade Plan — June 2026

**Signal date:** June 2026
**Strategy:** Sector-neutral momentum, top 1 per sector
**Total capital deployed:** USD 250 (50% of $500 — reduced due to weak
signal environment and energy concentration risk)
**Capital held in reserve:** USD 250

| Stock | Sector | Signal Return | Allocation |
|---|---|---|---|
| DE | Industrials | 8.50% | USD 50 |
| VLO | Energy | 6.79% | USD 50 |
| MDT | Healthcare | 5.61% | USD 50 |
| C | Financials | 3.20% | USD 50 |
| IBM | Technology | 2.63% | USD 50 |

**Benchmark:** SPY price at entry = $754.24
**Stop loss:** Portfolio drops below USD 212.50 (15%)
**Next rebalance:** First trading day of July 2026

**Notes:** Weak signal environment this month vs May 2026 (top signal
8.5% vs 39.9%). Energy heavily represented in top 14 due to Iran
conflict/oil price dynamics. Deployed 50% capital as risk management measure.

---

## Trade Execution — June 5 2026

**Strategy:** Sector-neutral momentum, top 1 per sector
**Capital deployed:** USD 249.89

| Stock | Sector | Shares | Avg Price | Cost Basis |
|---|---|---|---|---|
| C | Financials | 0.3723 | $134.28 | $49.99 |
| DE | Industrials | 0.0834 | $598.81 | $49.94 |
| IBM | Technology | 0.1637 | $305.34 | $49.98 |
| MDT | Healthcare | 0.6147 | $81.34 | $50.00 |
| VLO | Energy | 0.1916 | $260.86 | $49.98 |

**Benchmark:** SPY at entry = $754
**Cash reserve:** USD 8.20
**Stop loss:** Portfolio drops below USD 212.50
**Next rebalance:** July 1 2026

---

## Portfolio Update — June 6 2026

Portfolio down $6.89 (2.75%) from entry. IBM largest detractor at -$4.08
due to June 5 tech sector selloff (-4.7%) driven by strong ADP payroll
data pushing rate hike expectations higher, compounded by IBM-specific
whistleblower lawsuit. MDT only green position. Portfolio decline broadly
in line with SPY (-2%). No action taken — holding per strategy rules
until July 1 rebalance.

---

## Portfolio Update — June 13 2026

Portfolio down $6.24 (-2.50%) from entry. IBM remains dominant detractor
at -$5.42 (-10.8% on position), responsible for the entire portfolio loss
— excluding IBM, remaining four positions net roughly flat (-$0.83
combined). C has turned positive (+$2.07).

IBM hit by four separate negative catalysts since February:
1. Anthropic's Claude Code threatening IBM's COBOL modernisation
   consulting revenue
2. June 5 tech sector selloff on rising Treasury yields
3. Gartner data showing IBM Consulting revenue fell 12.8%
4. Market skepticism over IBM's $10B quantum computing investment

Assessed as structural deterioration in IBM's momentum signal, not
short-term noise. Decision made to run momentum script ahead of schedule
to assess IBM's current ranking.

---

## Mid-Month Rebalance — June 15 2026

**Trigger:** IBM fell completely out of top 14 momentum rankings —
strategy signal independently confirmed exit regardless of fundamental
concerns.

**Momentum Rankings — June 2026 Signal:**

| Rank | Stock | Sector | Signal Return |
|---|---|---|---|
| 1 | C | Financial Services | 11.06% |
| 2 | BAC | Financial Services | 9.13% |
| 3 | MDT | Healthcare | 8.66% |
| 4 | WFC | Financial Services | 7.98% |
| 5 | UNH | Healthcare | 7.42% |
| 6 | JPM | Financial Services | 7.15% |
| 7 | JNJ | Healthcare | 6.90% |
| 8 | DE | Industrials | 6.51% |
| 9 | VLO | Energy | 5.66% |
| 10 | LIN | Basic Materials | 5.53% |
| 11 | AMGN | Healthcare | 5.47% |
| 12 | WMT | Consumer Defensive | 4.57% |
| 13 | KO | Consumer Defensive | 4.57% |
| 14 | HD | Consumer Cyclical | 4.32% |

**Rule change note:** Original strategy used sector-neutral top-1 per
sector selection. For this rebalance, switched to highest-signal stock
regardless of sector overlap — primary goal is beating SPY. This results
in 2 of 5 positions in Financials (C + BAC). Tradeoff: higher expected
return signal, higher sector concentration risk. Documented as deliberate
deviation from original rule.

**Trade Execution — June 15 2026 9:55-9:58pm SGT:**

| Action | Stock | Shares | Fill Price | Proceeds |
|---|---|---|---|---|
| SELL | IBM | 0.1630 | $269.50 | $43.93 |
| BUY | BAC | 0.9246 | $56.24 | $52.00 |

**IBM Realised P&L:** $43.93 received vs $49.98 cost basis = **-$6.05 loss**

**Portfolio after rebalance:**

| Stock | Sector | Shares | Avg Price | Cost Basis |
|---|---|---|---|---|
| C | Financials | 0.3723 | $134.28 | $49.99 |
| BAC | Financials | 0.9246 | $56.24 | $52.00 |
| DE | Industrials | 0.0834 | $598.81 | $49.94 |
| MDT | Healthcare | 0.6147 | $81.34 | $50.00 |
| VLO | Energy | 0.1916 | $260.86 | $49.98 |

**Total deployed: $251.91**
**Next rebalance: July 1 2026**
**Stop loss: Portfolio drops below $212.50**

**Post-rebalance note:** Exiting IBM recovered approximately $3.24 of
unrealised loss by removing the largest detractor. Portfolio now has
zero tech exposure — fully allocated to Financials, Healthcare,
Industrials and Energy. IBM residual position of 0.0007 shares ($0.19)
remains as a rounding artefact from fractional share execution — negligible.
