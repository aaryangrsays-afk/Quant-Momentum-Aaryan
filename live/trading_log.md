# Trading Log — Quant Momentum Strategy

---

## Strategy Note — Capital Constraints

The live strategy runs 6 positions due to capital constraints ($250 deployed).
This differs from the backtested model in key ways:

- **Concentration:** ~17% per position vs smaller allocations in backtest
- **Selection:** Global top-25 ranking with max 2 positions per GICS sector
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

---

## Full Rebalance — Late June 2026

**Trigger:** Scheduled rebalance. Signal environment shifted dramatically
from June — semiconductor and biotech stocks dominated the new rankings
with momentum scores far exceeding the prior month's top signal of 8.5%.

**Strategy change:** Reverted to global top-25 ranking with a sector cap
of max 2 positions per GICS sector, replacing the highest-signal-only
approach used in the June 15 rebalance.

**Momentum Rankings — Late June 2026 (top 10 shown):**

| Rank | Stock | Sector | Signal Return |
|---|---|---|---|
| 1 | DD | Materials | 184.59% — EXCLUDED (data artifact) |
| 2 | AMAT | Information Technology | 48.42% |
| 3 | SNDK | Information Technology | 37.76% |
| 4 | MRVL | Information Technology | 37.20% |
| 5 | TECH | Health Care | 36.80% |
| 6 | KLAC | Information Technology | 34.67% |
| 7 | WDC | Information Technology | 27.17% |
| 8 | MRNA | Health Care | 26.62% |
| 9 | LRCX | Information Technology | 26.38% |
| 10 | TER | Information Technology | 26.09% |

**DD exclusion note:** DD's 184.59% signal confirmed as data artifact
from DuPont's 1-for-3 reverse stock split effective June 24 2026.
Momentum script compared post-split price against pre-split history,
inflating the score ~3x. No real return occurred. First identified
corporate action gap in signal generation.

**Exits:**

| Action | Stock | Reason |
|---|---|---|
| SELL | BAC | Dropped out of top 25 |
| SELL | DE | Dropped out of top 25 |
| SELL | MDT | Dropped out of top 25 |
| SELL | VLO | Dropped out of top 25 |

**Entries:**

| Action | Stock | Sector | Signal Return | Allocation |
|---|---|---|---|---|
| BUY | AMAT | Information Technology | 48.42% | ~$50 |
| BUY | MRVL | Information Technology | 37.20% | ~$50 |
| BUY | WDC | Information Technology | 27.17% | ~$50 |
| BUY | MRNA | Health Care | 26.62% | ~$50 |
| BUY | GEV | Industrials | — | ~$50 |

**Portfolio after rebalance:**

| Stock | Sector | Shares | Avg Price | Market Value (Jun 26) |
|---|---|---|---|---|
| AMAT | Information Technology | 0.0631 | $623.68 | $41.55 |
| C | Financials | 0.3723 | $134.28 | $53.98 |
| GEV | Industrials | 0.0351 | $1,121.00 | $37.63 |
| MRNA | Health Care | 0.6632 | $59.42 | $39.39 |
| MRVL | Information Technology | 0.1311 | $300.39 | $35.76 |
| WDC | Information Technology | 0.0520 | $749.49 | $34.33 |

**Total portfolio value:** $242.64
**Return since entry:** -2.90%
**Stop loss:** Portfolio drops below $212.50

---

## Alert Trigger — June 26 2026

**Trigger:** Automated portfolio monitor email fired — STOCK ALERT >3%
**Time:** 15:49 SGT

**Alerts fired:**
- AMAT UP 13.42% on the day
- WDC UP 4.90% on the day

**Portfolio snapshot at alert:**

| Stock | Price | Daily Change | Unrealised P&L |
|---|---|---|---|
| AMAT | $668.00 | +13.42% | +$2.80 |
| C | $144.98 | +0.97% | +$3.98 |
| GEV | $1,085.47 | +2.63% | -$1.25 |
| MRNA | $59.75 | -1.11% | +$0.22 |
| MRVL | $281.26 | +1.65% | -$2.51 |
| WDC | $675.39 | +4.90% | -$3.85 |

**Total portfolio value:** $245.85
**Return since entry:** -1.62%

**Decision:** Alert triggered momentum re-run. Fresh signal confirmed
C and GEV dropped out of top 25. AMAT, MRVL, WDC, MRNA all remain — hold.

**Intraday rebalance decision:**
- EXIT: C (no longer in top 25), GEV (no longer in top 25)
- ENTER: LUV (Industrials, #14, 21.81%), CAT (Industrials, #15, 20.68%)
- Allocation: ~$45.50 each, equal weight
- Rationale: Two Industrials reduce IT/semiconductor concentration

**DD artifact note:** DD appeared again at #1 — excluded on same grounds
as prior rebalance. Corporate action filter identified as a priority fix.

---

## Trade Execution — June 27 2026

**Sells (limit orders, filled at open):**

| Action | Stock | Shares | Fill Price | Proceeds |
|---|---|---|---|---|
| SELL | C | 0.3723 | $144.90 | $53.94 |
| SELL | GEV | 0.0351 | $1,067.00 | $37.45 |

**Buys (placed after T+1 settlement):**

| Action | Stock | Shares | Fill Price | Cost |
|---|---|---|---|---|
| BUY | LUV | 0.7786 | $52.30 | $40.72 |
| BUY | CAT | 0.0383 | $1,016.49 | $38.93 |

**Portfolio after execution:**

| Stock | Sector | Shares | Avg Price |
|---|---|---|---|
| AMAT | Information Technology | 0.0654 | $627.50 |
| CAT | Industrials | 0.0383 | $1,016.49 |
| LUV | Industrials | 0.7786 | $52.30 |
| MRNA | Health Care | 0.6866 | $59.84 |
| MRVL | Information Technology | 0.1368 | $300.23 |
| WDC | Information Technology | 0.0520 | $749.49 |

**Sector cap rule formalised:** Max 2 positions per GICS sector.

---

## Strategy Bug Fix — July 1 2026

**Issue identified:** Momentum signal was using single-month return
(pct_change() with periods=1) instead of the academically standard
12-1 month lookback. This meant the strategy was ranking stocks on
last month's return — effectively a short-term reversal signal — rather
than true intermediate-term momentum as defined by Jegadeesh and
Titman (1993).

**Impact:** All prior live trades were executed on a 1-month signal,
not a 12-1 month signal. The backtest results reflected the 1-month
strategy, not the intended momentum strategy. Prior trades were not
necessarily wrong — June was a strong momentum environment and several
positions performed well — but the strategy being tested was not the
one originally specified.

**Fix applied:**
- Signal changed to `monthly_prices.shift(1).pct_change(periods=11)`
- Data window extended from 3 to 4 years to accommodate the longer lookback
- Corporate action filter added: stocks with fewer than 47 months of
  price history excluded from universe, removing recent IPOs and spin-offs

**Updated backtest results (12-1 month signal, full S&P 500 universe):**

| Metric | 1-Month Signal (old) | 12-1 Month Signal (new) |
|---|---|---|
| Avg Monthly Return | 0.0400 | 0.0476 |
| Annualised Sharpe | 1.74 | 1.76 |
| Hit Rate | 58.82% | 66.67% |
| Max Drawdown | -8.85% | -17.96% |

The 12-1 month signal is stronger on all return and consistency metrics.
Max drawdown increased, which is expected — the longer lookback captures
genuine momentum crashes rather than smoothing them out with short windows.

**Second corporate action artifact identified:** SNDK (Western Digital
spin-off) appeared at #1 with a 5,197% momentum score. Confirmed artifact
— SNDK began trading recently and yfinance backfills limited history,
producing a nonsense 12-month return. History-length filter successfully
removed SNDK from the universe after the fix.

---

## July 1 2026 Rebalance

**Signal date:** July 2026 (12-1 month, corrected signal)
**Universe:** S&P 500, 494 stocks after corporate action filter

**Top 25 Momentum Rankings — July 2026:**

| Rank | Stock | Sector | Momentum Score |
|---|---|---|---|
| 1 | MU | Information Technology | 959.16% |
| 2 | WDC | Information Technology | 713.89% |
| 3 | LITE | Information Technology | 679.49% |
| 4 | INTC | Information Technology | 605.20% |
| 5 | STX | Information Technology | 519.69% |
| 6 | CIEN | Information Technology | 428.39% |
| 7 | LRCX | Information Technology | 359.44% |
| 8 | TER | Information Technology | 351.53% |
| 9 | GLW | Information Technology | 308.32% |
| 10 | AMAT | Information Technology | 304.48% |
| 11 | MRVL | Information Technology | 271.35% |
| 12 | COHR | Information Technology | 266.61% |
| 13 | KLAC | Information Technology | 245.44% |
| 14 | AMD | Information Technology | 229.48% |
| 15 | DELL | Information Technology | 228.76% |
| 16 | FLEX | Information Technology | 224.98% |
| 17 | ECHO | Communication Services | 211.45% |
| 18 | FIX | Industrials | 182.44% |
| 19 | CNC | Health Care | 146.22% |
| 20 | CAT | Industrials | 144.85% |
| 21 | MRNA | Health Care | 136.91% |
| 22 | VRT | Industrials | 130.21% |
| 23 | HPE | Information Technology | 122.57% |
| 24 | KEYS | Information Technology | 113.57% |
| 25 | JBHT | Industrials | 102.86% |

**Signal verification note:** Extreme momentum scores (MU 959%, WDC 713%,
AMAT 304%, MRVL 271%) were manually verified against Google Finance
12-month price returns before execution. All confirmed as real:

| Stock | Script Score | Google Finance 1Y Return | Verdict |
|---|---|---|---|
| MU | 959.16% | +753.90% | Real — HBM memory supercycle |
| WDC | 713.89% | +837.30% | Real — flash storage cycle |
| AMAT | 304.48% | +254.22% | Real — semiconductor capex cycle |
| MRVL | 271.35% | +256.83% | Real — AI infrastructure demand |

Score discrepancies between script and Google Finance are due to
differing lookback windows (script uses monthly end prices, Google
Finance uses daily). All signals confirmed valid.

**Exits:**

| Action | Stock | Shares | Fill Price | Realised P&L |
|---|---|---|---|---|
| SELL | LUV | 0.7786 | $51.10 | -$0.93 |
| SELL | AXON | 0.0659 | $603.96 | +$0.91 |

**Note on AXON:** AXON and LUV were held from a prior rebalance and
dropped out of the top 25 on the corrected 12-1 month signal. Both
exits were signal-driven, not discretionary.

**Entries:**

| Action | Stock | Shares | Fill Price | Cost |
|---|---|---|---|---|
| BUY | MU | 0.0378 | $1,053.96 | $39.84 |
| BUY | WDC | 0.0671 | $593.01 | $39.79 |

**Portfolio after rebalance:**

| Stock | Sector | Shares | Avg Price | Market Value (Jul 1) | Unrealised P&L |
|---|---|---|---|---|---|
| MRNA | Health Care | 0.6866 | $59.84 | $50.27 | +$9.18 |
| AMAT | Information Technology | 0.0654 | $627.50 | $43.49 | +$2.45 |
| WDC | Information Technology | 0.0671 | $593.01 | $40.14 | +$0.34 |
| CAT | Industrials | 0.0383 | $1,016.49 | $38.27 | -$0.66 |
| MU | Information Technology | 0.0378 | $1,053.96 | $39.00 | -$0.84 |
| MRVL | Information Technology | 0.1368 | $300.23 | $37.50 | -$3.57 |

**Total portfolio value:** $248.67
**Total unrealised P&L:** +$6.90
**Return since entry:** +2.76%
**Stop loss:** Portfolio drops below $212.50
**Next rebalance:** First trading day of August 2026

**Sector concentration note:** 4 of 6 positions in Information Technology
(AMAT, WDC, MU, MRVL). This reflects genuine market momentum — the
semiconductor and AI infrastructure cycle dominated 12-month returns
across the S&P 500. Sector cap rule (max 2 per sector) was relaxed this
rebalance given signal strength and verification. To be reviewed before
August rebalance.
