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

## Strategy Evaluation Criteria

Strategy will be considered failing if:
- Hit rate stays below 50% for 3 consecutive months
- Portfolio drops more than 25% from starting capital ($187.50)
- Live monthly returns are consistently worse than SPY for 4+ months in a row

---

## Pre-Trade Plan — June 2026

**Signal date:** June 2026
**Strategy:** Sector-neutral momentum, top 1 per sector
**Total capital deployed:** USD 250 (50% of $500 — reduced due to weak signal environment and energy concentration risk)
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

**Notes:** Weak signal environment this month vs May 2026 (top signal 8.5% vs 39.9%). Energy heavily represented in top 14 due to Iran conflict/oil price dynamics. Deployed 50% capital as risk management measure.

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

Portfolio down $6.89 (2.75%) from entry. IBM largest detractor at -$4.08 due to June 5 tech sector selloff (-4.7%) driven by strong ADP payroll data pushing rate hike expectations higher, compounded by IBM-specific whistleblower lawsuit. MDT only green position. Portfolio decline broadly in line with SPY (-2%). No action taken — holding per strategy rules until July 1 rebalance.

---

## Portfolio Update — June 13 2026

Portfolio down $6.24 (-2.50%) from entry. IBM remains the dominant detractor at -$5.42 (-10.8% on position), now responsible for the entire portfolio loss — excluding IBM, the remaining four positions are net roughly flat (-$0.83 combined). C has turned positive (+$2.07).

IBM has been hit by four separate negative catalysts since February: (1) Anthropic's Claude Code threatening IBM's COBOL modernisation consulting revenue, (2) the June 5 tech sector selloff on rising Treasury yields, (3) Gartner data showing IBM Consulting revenue fell 12.8%, validating broader IT services slowdown fears, and (4) market skepticism over IBM's $10B quantum computing investment being read as expensive and speculative. IBM's 52-week low ($212.34) is now close to the portfolio stop loss level ($212.50).

This is assessed as a structural deterioration in IBM's momentum signal, not short-term noise.

**Decision:** Run momentum script ahead of schedule to check IBM's current ranking before July 1 rebalance.

---

## Mid-Month Rebalance — June 15 2026 (Pending)

**Reason:** Ran momentum script on June 13 ahead of the scheduled July 1 rebalance due to IBM's deteriorating fundamentals (see June 13 update). Result: IBM has fallen completely out of the top 14 momentum rankings — confirming the strategy signal itself supports exiting the position, independent of the fundamental concerns.

**New Top 14 Rankings (June 2026 signal):**

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

**Action:**
- **SELL** IBM — 0.1637 shares — realised loss approx. -$5.42
- **BUY** LIN (Linde, Basic Materials) — approx. $44.57 — rank #10, fills vacant sector slot left by IBM exit

**Portfolio after rebalance:** C (Financials), MDT (Healthcare), DE (Industrials), VLO (Energy), LIN (Basic Materials)

**Note:** This is a mid-month rebalance, not the standard July 1 cycle. Justified because IBM did not merely underperform — it fell completely out of the top 14, meaning the strategy's own signal independently confirmed the exit. The July 1 rebalance will proceed as normal using fresh rankings at that time.
