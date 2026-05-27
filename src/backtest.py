import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score

print("Step 1: Libraries loaded")

tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
    "JPM", "GS", "BAC", "WFC", "C",
    "JNJ", "PFE", "UNH", "MRK", "ABT",
    "XOM", "CVX", "COP", "SLB", "EOG"
]

print("Step 2: Tickers defined")

print("Step 3: Building sector map...")

sector_map = {}
for ticker in tickers:
    try:
        sector_map[ticker] = yf.Ticker(ticker).info.get("sector", "Unknown")
    except:
        sector_map[ticker] = "Unknown"

print("Step 4: Sector map complete")

end_date = datetime.today()
start_date = end_date - timedelta(days=365*5)

print("Step 5: Downloading data...")

data = yf.download(tickers, start=start_date, end=end_date)["Close"]

print("Step 6: Download complete")

monthly_prices = data.resample("ME").last()
monthly_returns = monthly_prices.pct_change().dropna()

print("Step 7: Monthly returns computed")

df = monthly_returns.stack().reset_index()
df.columns = ["date", "stock", "return"]

df["sector"] = df["stock"].map(sector_map)

# IMPORTANT: sort for correctness
df = df.sort_values(["stock", "date"]).reset_index(drop=True)

print("Step 8: Data reshaped")

df["rank"] = df.groupby(["date", "sector"])["return"].rank(ascending=False)

print("Step 9: Ranking complete")

top5 = (
    df.sort_values(["date", "rank"])
      .groupby("date", group_keys=False)
      .head(5)
)

bottom5 = (
    df.sort_values(["date", "rank"], ascending=[True, False])
      .groupby("date", group_keys=False)
      .head(5)
)

print("Step 10: Portfolios built")

df["next_return"] = df.groupby("stock")["return"].shift(-1)

# align before merge
df = df.sort_values(["date", "stock"]).reset_index(drop=True)

top5 = top5.merge(
    df[["date", "stock", "next_return"]],
    on=["date", "stock"],
    how="left"
)

bottom5 = bottom5.merge(
    df[["date", "stock", "next_return"]],
    on=["date", "stock"],
    how="left"
)

print("Step 11: Next-month returns merged")

top5_portfolio = top5.groupby("date")["next_return"].mean()
bottom5_portfolio = bottom5.groupby("date")["next_return"].mean()

print("\n===== RESULTS =====")

print("Top 5 Momentum Avg Monthly Return:", top5_portfolio.mean())
print("Bottom 5 Avg Monthly Return:", bottom5_portfolio.mean())

print("\nTop 5 Cumulative Return:", (1 + top5_portfolio).prod() - 1)
print("Bottom 5 Cumulative Return:", (1 + bottom5_portfolio).prod() - 1)

# 1. Sharpe Ratio (assume risk-free rate of ~4% annually = 0.04/12 monthly)
risk_free = 0.04 / 12
sharpe = (top5_portfolio.mean() - risk_free) / top5_portfolio.std()
annualised_sharpe = sharpe * np.sqrt(12)
print(f"Annualised Sharpe Ratio: {annualised_sharpe:.4f}")

# 2. Maximum Drawdown
cumulative = (1 + top5_portfolio).cumprod()
rolling_max = cumulative.cummax()
drawdown = (cumulative - rolling_max) / rolling_max
max_drawdown = drawdown.min()
print(f"Maximum Drawdown: {max_drawdown:.2%}")

# 3. Hit Rate — how often did top 5 beat bottom 5 monthly
hit_rate = (top5_portfolio > bottom5_portfolio).mean()
print(f"Hit Rate: {hit_rate:.2%}")
print("\nStep 12: Building ML features...")

# 1-month momentum
df["mom_1m"] = df.groupby("stock")["return"].shift(1)

# 3-month cumulative momentum
df["mom_3m"] = (
    (1 + df.groupby("stock")["return"]
        .rolling(3)
        .apply(np.prod, raw=True)
        .reset_index(level=0, drop=True)) - 1
)

# 6-month cumulative momentum
df["mom_6m"] = (
    (1 + df.groupby("stock")["return"]
        .rolling(6)
        .apply(np.prod, raw=True)
        .reset_index(level=0, drop=True)) - 1
)

# 12-month cumulative momentum
df["mom_12m"] = (
    (1 + df.groupby("stock")["return"]
        .rolling(12)
        .apply(np.prod, raw=True)
        .reset_index(level=0, drop=True)) - 1
)

df["next_return"] = df.groupby("stock")["return"].shift(-1)
ml_data = df.dropna().copy()
features = ["mom_1m", "mom_3m", "mom_6m"]

X = ml_data[features]
Y = ml_data["next_return"]
unique_dates = sorted(ml_data["date"].unique())

split_idx = int(len(unique_dates) * 0.7)

train_dates = unique_dates[:split_idx]
test_dates = unique_dates[split_idx:]
train_data = ml_data[ml_data["date"].isin(train_dates)]
test_data = ml_data[ml_data["date"].isin(test_dates)]

X_train = train_data[features]
Y_train = train_data["next_return"]

X_test = test_data[features]
Y_test = test_data["next_return"]

print("Step 13: Training Random Forest...")

rf = RandomForestRegressor(
    n_estimators=200,
    max_depth=3,
    random_state=42
)

rf.fit(X_train, Y_train)
Y_pred = rf.predict(X_test)
r2 = r2_score(Y_test, Y_pred)

print(f"\nTEST R²: {r2:.4f}")
importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": rf.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\nFeature Importances:")
print(importance_df)