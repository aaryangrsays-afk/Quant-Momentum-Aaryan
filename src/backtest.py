import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime, timedelta

print("Step 1: Libraries loaded")

# --- PULL S&P 500 TICKERS AND SECTORS ---
print("Step 2: Fetching S&P 500 universe...")
url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
sp500 = pd.read_csv(url)
tickers = sp500['Symbol'].str.replace('.', '-', regex=False).tolist()
sector_map = dict(zip(
    sp500['Symbol'].str.replace('.', '-', regex=False),
    sp500['GICS Sector']
))
print(f"Step 3: Universe ready — {len(tickers)} stocks across sectors")

# --- DOWNLOAD DATA ---
end_date = datetime.today()
start_date = end_date - timedelta(days=365*3)
print("Step 4: Downloading 3 years of data...")
data = yf.download(tickers, start=start_date, end=end_date)["Close"]
print(f"Step 5: Download complete. Shape: {data.shape}")

# --- MONTHLY RETURNS ---
monthly_prices = data.resample("ME").last()
monthly_returns = monthly_prices.pct_change().dropna(how="all")
print("Step 6: Monthly returns computed")

# --- RESHAPE ---
df = monthly_returns.stack().reset_index()
df.columns = ["date", "stock", "return"]
df["sector"] = df["stock"].map(sector_map)
df = df.sort_values(["stock", "date"]).reset_index(drop=True)
df = df.dropna(subset=["sector"])
print("Step 7: Data reshaped")

# --- NEXT MONTH RETURNS (before ranking so shift works correctly) ---
df["next_return"] = df.groupby("stock")["return"].shift(-1)
print("Step 8: Next month returns computed")

# --- GLOBAL MOMENTUM RANKING ---
df["rank"] = df.groupby("date")["return"].rank(ascending=False)
print("Step 9: Ranking complete")

# --- SEPARATE FULL DF FROM TODAY'S SLICE ---
df_full = df.copy()

# --- TOP AND BOTTOM 25 FOR BACKTEST (exclude last month — no next_return) ---
top_n = 25
df_backtest = df_full[df_full["next_return"].notna()].copy()

top_portfolio_df = (
    df_backtest.sort_values(["date", "rank"])
               .groupby("date", group_keys=False)
               .head(top_n)
)
bottom_portfolio_df = (
    df_backtest.sort_values(["date", "rank"], ascending=[True, False])
               .groupby("date", group_keys=False)
               .head(top_n)
)
print("Step 10: Portfolios built")

print("\n--- DEBUG ---")
print(f"df shape: {df.shape}")
print(f"Unique dates: {df['date'].nunique()}")
print(f"Sample of df:\n{df[['date','stock','return','next_return']].head(10)}")
print(f"next_return non-null: {df['next_return'].notna().sum()}")
print(f"df_backtest shape: {df_backtest.shape}")
print("--- END DEBUG ---\n")
# --- PERFORMANCE METRICS ---
top_portfolio = top_portfolio_df.groupby("date")["next_return"].mean()
bottom_portfolio = bottom_portfolio_df.groupby("date")["next_return"].mean()

risk_free = 0.04 / 12
sharpe = (top_portfolio.mean() - risk_free) / top_portfolio.std()
annualised_sharpe = sharpe * np.sqrt(12)
cumulative = (1 + top_portfolio).cumprod()
max_drawdown = ((cumulative - cumulative.cummax()) / cumulative.cummax()).min()
hit_rate = (top_portfolio > bottom_portfolio).mean()

print("\n===== RESULTS =====")
print(f"Top {top_n} Avg Monthly Return:    {top_portfolio.mean():.4f}")
print(f"Bottom {top_n} Avg Monthly Return: {bottom_portfolio.mean():.4f}")
print(f"Top {top_n} Cumulative Return:     {(1 + top_portfolio).prod() - 1:.4f}")
print(f"Annualised Sharpe Ratio:  {annualised_sharpe:.4f}")
print(f"Maximum Drawdown:         {max_drawdown:.2%}")
print(f"Hit Rate:                 {hit_rate:.2%}")

# --- TODAY'S RANKINGS (use latest month from full df) ---
latest = df_full[df_full["date"] == df_full["date"].max()].copy()
latest = latest.sort_values("rank")

print(f"\n===== TODAY'S TOP 25 MOMENTUM STOCKS =====")
print(f"Signal date: {df_full['date'].max().strftime('%B %Y')}")
for _, row in latest.head(25).iterrows():
    print(f"#{int(row['rank']):3d} | {row['stock']:6s} | {row['sector']:30s} | {row['return']:.2%}")

# --- CHART ---
cumulative_top = (1 + top_portfolio).cumprod()
cumulative_bottom = (1 + bottom_portfolio).cumprod()

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(cumulative_top.index, cumulative_top.values,
        color='#00C897', linewidth=2.5, label=f'Top {top_n} Momentum')
ax.plot(cumulative_bottom.index, cumulative_bottom.values,
        color='#FF4D4D', linewidth=2.5, label=f'Bottom {top_n} Momentum')
ax.set_title(f'S&P 500 Cross-Sectional Momentum — Top vs Bottom {top_n} (3 Year)',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xlabel('Date')
ax.set_ylabel('Portfolio Value ($1 Invested)')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.1f}x'))
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('momentum_chart_sp500.png', dpi=150, bbox_inches='tight')
plt.show()

print("\nDone.")