Quant Project Journal

So what i started off doing was reading into the basics of what are stock how do they function and what the markets look like. The basics invioled terms like returns be it monthly or yearly. I got to know what y finance is, what are tickers, what is the method of a momentum strategy that basically ranks stocks by their trailing 21-day return and assumes recent winners will continue to outperform on a relative basis the following month. Now we also looked into something called the burn-in period? Which allowed us to understand why you need x-21 days if you are claulatying it for x days. I also learned how to effectively use pandas to clean the data extract it from finance and do stuff like iloc[-1] and things of that nature.
 
A naive momentum strategy on 20 stocks produced 40% Tech concentration in the top 5. This creates correlated drawdown risk. A more robust approach would either cap sector exposure at X% or run momentum rankings within each sector separately.

My first R² of 90% was caused by overlapping observations in rolling returns — a classic data error that inflates model performance. After correcting to non-overlapping monthly returns, R² dropped to 0.0003. This is why backtests must be scrutinised carefully.

"Linear regression on clean non-overlapping monthly returns produced R² of 0.0003 and slope of 0.017 — essentially no predictive power. This is consistent with academic literature showing that simple momentum signals require large universes and long time horizons to be statistically significant. This motivates our use of a more flexible ML model and a cross-sectional ranking approach rather than absolute return prediction."

"Cross-sectional momentum strategy on 20 S&P 500 stocks over 3 years produced 2.66% average monthly return vs 1.30% for bottom quintile. Annualised Sharpe of 1.64, maximum drawdown of -12.92%, and hit rate of 58.33%. Results suggest momentum effect is present in this universe but require stress testing across different market regimes."
"Robustness testing across 2, 3 and 4 year windows shows Sharpe ratio range of 1.29-1.64, suggesting strategy performance is not purely a product of a specific market regime. Hit rate remains 54-58% across all windows. Maximum drawdown worsens to -17.52% in the 4 year window including the 2022 bear market, consistent with known momentum crashes during sharp market reversals."

Robustness is not about finding the best parameters — it's about checking whether results survive when you change the conditions. A strategy that only works in one specific window is a lucky sample, not an edge.

I considered using every permutation of monthly return windows as features but recognised this would cause overfitting given our small universe of 20 stocks and 36 months of data. The 1, 3, 6 and 12 month windows were chosen based on academic literature on momentum factors rather than data-driven selection, avoiding look-ahead bias in feature engineering."

Random Forest on test set produced R² of -0.0617, worse than a naive mean prediction. This is attributed to insufficient data — 20 stocks over 24 months yields too few clean observations after feature engineering and train/test split for the model to generalise. Feature importance analysis showed 1-month momentum as the dominant signal at 49.6%, with 12-month momentum contributing 0%, likely due to data scarcity. This motivates either expanding the stock universe or extending the historical window for the ML layer. 
12 month momentum showed zero feature importance across all tests. With only 5 years of monthly data across 20 stocks, the 12 month rolling signal lacks sufficient variation relative to return noise for the model to extract a reliable pattern. Academic studies validating 12 month momentum typically use 20+ years of data across hundreds of stocks. 

With 20 stocks and 5 years of monthly data, we have insufficient observations for a Random Forest to generalise meaningfully. The model underperforms a naive mean prediction on the test set. This is a data limitation, not a model failure.
