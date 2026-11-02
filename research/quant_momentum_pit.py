"""
quant_momentum_pit.py  —  robustness check for the live momentum strategy
==========================================================================

Same strategy as quant_momentum.py (12-1 momentum, top 6, max 2 per GICS
sector, monthly rebalance, three stop variants), run twice:

  TODAY_LIST     the old way: every month picks from TODAY's S&P 500 list
                 (survivorship / look-ahead bias built into the universe)
  POINT_IN_TIME  each month picks only from stocks that were actually in the
                 index at that month-end (fja05680/sp500 historical membership)

Three realism fixes vs quant_momentum.py, applied to BOTH universes:
  1. Trading costs: COST_BPS per side, charged whenever a name is bought or
     sold (new entry, rotation out, or stop exit). Held-over names pay nothing.
  2. Stops fill at the NEXT DAY'S OPEN after the close that breaches the stop,
     not at the stop price. Gaps through the stop show up as extra loss.
  3. No look-ahead history filter: a stock only needs 13 months of prices up
     to the formation date (the old 47-month filter looked at the whole
     sample, including the future).

Known limitation (cannot be fixed with free data): Yahoo has no prices for
most delisted companies (Lehman, WaMu, ...). Point-in-time members without
data are skipped, so some survivorship bias remains. The script prints how
much of each month's index has price data ("coverage") so you can see how big
that hole is.

Does NOT touch the live script, positions.json, or the live CSVs.
Outputs: backtest_pit_monthly_returns.csv, backtest_pit_positions.csv
"""
import logging
import time
import warnings
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ============================================================
# CONFIG
# ============================================================
TOP_N = 6
SECTOR_CAP = 2
LOOKBACK_YEARS = 20
MIN_HISTORY_MONTHS = 13      # 12-1 signal needs 13 month-ends of prices
RISK_FREE_ANNUAL = 0.04
COST_BPS = 15                # per side: commission + half-spread + impact, rough

FIXED_STOP_PCT = 0.10
VOL_K = 1.5                  # keep in sync with the live rule
VOL_WINDOW_DAYS = 63
VOL_FLOOR = 0.08
VOL_CAP = 0.25
VARIANTS = ["NO_STOP", "FIXED", "VOL_SCALED"]

HIST_URL = ("https://raw.githubusercontent.com/fja05680/sp500/master/"
            "S%26P%20500%20Historical%20Components%20%26%20Changes%20(Updated).csv")
CURR_URL = ("https://raw.githubusercontent.com/datasets/s-and-p-500-companies/"
            "main/data/constituents.csv")

# windows are HOLDING months (inclusive)
CRASH_WINDOWS = {
    "GFC crash       Sep08-Feb09": ("2008-09", "2009-02"),
    "Momentum crash  Mar09-May09": ("2009-03", "2009-05"),
    "COVID           Feb20-Apr20": ("2020-02", "2020-04"),
    "2022 bear       Jan22-Oct22": ("2022-01", "2022-10"),
}


def yahoo(t):
    return t.strip().replace(".", "-")


# ============================================================
# DATA
# ============================================================
def load_membership():
    hist = pd.read_csv(HIST_URL, parse_dates=["date"]).sort_values("date")
    hist["members"] = hist["tickers"].str.split(",").apply(
        lambda lst: frozenset(yahoo(t) for t in lst if t.strip()))
    return hist[["date", "members"]].reset_index(drop=True)


def members_at(hist, t):
    i = hist["date"].searchsorted(t, side="right") - 1
    return hist["members"].iloc[max(i, 0)]


def download(tickers, start, end, chunk=150):
    import yfinance as yf
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)
    opens, closes = [], []
    for i in range(0, len(tickers), chunk):
        part = tickers[i:i + chunk]
        df = None
        for attempt in range(3):
            try:
                df = yf.download(part, start=start, end=end, auto_adjust=True,
                                 progress=False, threads=True)
                break
            except Exception as e:  # network hiccup / rate limit
                print(f"    retry {attempt + 1}: {e}")
                time.sleep(5 * (attempt + 1))
        if df is None or df.empty:
            continue
        if isinstance(df.columns, pd.MultiIndex):
            opens.append(df["Open"])
            closes.append(df["Close"])
        else:  # single ticker, flat columns
            opens.append(df[["Open"]].rename(columns={"Open": part[0]}))
            closes.append(df[["Close"]].rename(columns={"Close": part[0]}))
        print(f"    downloaded {min(i + chunk, len(tickers))}/{len(tickers)}")
        time.sleep(1)
    o = pd.concat(opens, axis=1)
    c = pd.concat(closes, axis=1)
    o = o.loc[:, ~o.columns.duplicated()]
    c = c.loc[:, ~c.columns.duplicated()]
    keep = c.columns[c.notna().any()]
    return o[keep].sort_index(), c[keep].sort_index()


# ============================================================
# STRATEGY PIECES
# ============================================================
def pick_sector_capped(scores, n, cap, sector_map):
    """Highest scores first, max `cap` per sector. Unknown sector = no cap
    (stocks that left the index have no current GICS label)."""
    picked, counts = [], {}
    for s in scores.sort_values(ascending=False).index:
        sec = sector_map.get(s) or f"UNKNOWN:{s}"
        if counts.get(sec, 0) >= cap:
            continue
        picked.append(s)
        counts[sec] = counts.get(sec, 0) + 1
        if len(picked) == n:
            break
    return picked


def run_stop(c, o, entry, stop_pct):
    """c, o: daily closes/opens over the holding month (same index).
    Returns (return, stopped?, exit return if stopped else nan).
    Stop checked on closes; exit at the NEXT day's open."""
    ratio = c / entry
    if stop_pct is None:
        return ratio.iloc[-1] - 1, False, np.nan
    hit = (ratio <= 1 - stop_pct).values
    if not hit.any():
        return ratio.iloc[-1] - 1, False, np.nan
    k = int(np.argmax(hit))
    if k + 1 < len(c):
        px = o.iloc[k + 1]
        if pd.isna(px):
            px = c.iloc[k + 1]
    else:  # breached on the last day of the month: out at that close
        px = c.iloc[k]
    r = px / entry - 1
    return r, True, r


def metrics(r):
    rf = RISK_FREE_ANNUAL / 12
    cum = (1 + r).cumprod()
    return {
        "CAGR": cum.iloc[-1] ** (12 / len(r)) - 1,
        "Ann. vol": r.std() * np.sqrt(12),
        "Sharpe": (r.mean() - rf) / r.std() * np.sqrt(12),
        "Max DD": ((cum - cum.cummax()) / cum.cummax()).min(),
        "Worst month": r.min(),
        "Best month": r.max(),
    }


# ============================================================
# BACKTEST
# ============================================================
def backtest(name, universe_fn, close, open_, monthly, momentum, vol_1m,
             hist_count, sector_map, cutoff):
    cost = COST_BPS / 1e4
    months = monthly.index

    # pass 1: picks for every formation month
    picks_by_t, coverage, bottom_rows, unknown = {}, [], [], 0
    for i in range(len(months) - 1):
        t, tn = months[i], months[i + 1]
        if tn >= cutoff:
            break
        uni = universe_fn(t)
        have = [s for s in uni if s in monthly.columns
                and pd.notna(monthly.at[t, s])]
        coverage.append({"date": t, "members": len(uni), "with_data": len(have)})
        ok = [s for s in have if hist_count.at[t, s] >= MIN_HISTORY_MONTHS]
        scores = momentum.loc[t, ok].dropna()
        if scores.empty:
            continue
        picks = pick_sector_capped(scores, TOP_N, SECTOR_CAP, sector_map)
        unknown += sum(1 for s in picks if s not in sector_map)
        picks_by_t[t] = picks
        bottom = scores.sort_values().index[:TOP_N]
        fwd = (monthly.loc[tn, bottom] / monthly.loc[t, bottom] - 1).mean()
        bottom_rows.append({"date": tn, "bottom": fwd})

    # pass 2: simulate holding months, with costs
    ts = list(picks_by_t)
    rows = []
    held_prev = {v: set() for v in VARIANTS}
    for k, t in enumerate(ts):
        tn = months[months.get_loc(t) + 1]
        next_picks = set(picks_by_t[ts[k + 1]]) if k + 1 < len(ts) else set()
        entry_row = close.loc[:t].iloc[-1]
        mask = (close.index > t) & (close.index <= tn)
        cpath, opath = close.loc[mask], open_.loc[mask]
        held_now = {v: set() for v in VARIANTS}
        for s in picks_by_t[t]:
            entry = entry_row.get(s, np.nan)
            c = cpath[s].ffill().dropna() if s in cpath else pd.Series(dtype=float)
            if pd.isna(entry) or c.empty:
                continue
            o = opath[s].reindex(c.index) if s in opath else c
            v = vol_1m.loc[:t, s].dropna()
            vstop = FIXED_STOP_PCT if v.empty else float(
                np.clip(VOL_K * v.iloc[-1], VOL_FLOOR, VOL_CAP))
            row = {"date": tn, "formed": t, "stock": s,
                   "sector": sector_map.get(s, "UNKNOWN"), "vol_stop_pct": vstop}
            for var, sp in (("NO_STOP", None), ("FIXED", FIXED_STOP_PCT),
                            ("VOL_SCALED", vstop)):
                r, hit, _ = run_stop(c, o, entry, sp)
                buy = s not in held_prev[var]
                sell = hit or (s not in next_picks)
                row[var] = r
                row[f"{var}_net"] = r - cost * (int(buy) + int(sell))
                row[f"{var}_hit"] = hit
                row[f"{var}_stop"] = sp if sp is not None else np.nan
                if not hit:
                    held_now[var].add(s)
            rows.append(row)
        held_prev = held_now

    trades = pd.DataFrame(rows)
    gross = trades.groupby("date")[VARIANTS].mean()
    net = trades.groupby("date")[[f"{v}_net" for v in VARIANTS]].mean()
    net.columns = VARIANTS
    bottom = pd.DataFrame(bottom_rows).set_index("date")["bottom"]
    cov = pd.DataFrame(coverage).set_index("date")
    return {"name": name, "trades": trades, "gross": gross, "net": net,
            "bottom": bottom, "coverage": cov, "unknown": unknown}


def stop_diagnostics(trades):
    out = {}
    for var in ("FIXED", "VOL_SCALED"):
        s = trades[trades[f"{var}_hit"]]
        if s.empty:
            out[var] = None
            continue
        cost_per = s[var] - s["NO_STOP"]          # <0 = stop hurt that trade
        out[var] = {
            "stops": len(s),
            "of": len(trades),
            "hurt": int((cost_per < 0).sum()),     # month-end beat the exit
            "avg_effect": cost_per.mean(),
            "avg_gap": (s[var] + s[f"{var}_stop"]).mean(),  # exit vs stop level
        }
    return out


def fmt_table(df):
    pct = ["CAGR", "Ann. vol", "Max DD", "Worst month", "Best month", "Hit rate"]
    out = df.copy().astype(object)
    for r in out.index:
        out.loc[r] = ["" if pd.isna(x)
                      else f"{x:.2f}" if r == "Sharpe" or "Sharpe" in r
                      else f"{x:+.1%}" if r in pct or "CAGR" in r
                      else x for x in df.loc[r]]
    return out


# ============================================================
# MAIN
# ============================================================
def main():
    print("Step 1: Loading index membership...")
    hist = load_membership()
    curr = pd.read_csv(CURR_URL)
    sector_map = dict(zip(curr["Symbol"].map(yahoo), curr["GICS Sector"]))
    today_list = frozenset(sector_map)

    end = datetime.today()
    start = end - timedelta(days=365 * LOOKBACK_YEARS)
    ever = set().union(*hist.loc[hist["date"] >= start - timedelta(days=40),
                                 "members"])
    ever |= today_list
    tickers = sorted(ever) + ["SPY"]
    print(f"Step 2: {len(today_list)} current names; {len(ever)} names were in "
          f"the index at some point since {start:%Y-%m}")

    print(f"Step 3: Downloading {LOOKBACK_YEARS}y of daily open/close for "
          f"{len(tickers)} tickers (a few minutes)...")
    open_, close = download(tickers, start, end)
    spy_close = close.pop("SPY") if "SPY" in close else None
    open_ = open_.drop(columns="SPY", errors="ignore")
    print(f"Step 4: Got data for {close.shape[1]} of {len(tickers) - 1} names "
          f"({len(tickers) - 1 - close.shape[1]} with no Yahoo history, mostly "
          f"delisted/renamed)")

    monthly = close.resample("ME").last()
    momentum = monthly.shift(1).pct_change(periods=11, fill_method=None)
    hist_count = monthly.notna().cumsum()
    vol_1m = close.pct_change(fill_method=None).rolling(
        VOL_WINDOW_DAYS).std() * np.sqrt(21)
    cutoff = pd.Timestamp(datetime.today().date()) + pd.offsets.MonthEnd(0)

    args = (close, open_, monthly, momentum, vol_1m, hist_count, sector_map, cutoff)
    print("Step 5: Backtesting TODAY_LIST...")
    a = backtest("TODAY_LIST", lambda t: today_list, *args)
    print("Step 6: Backtesting POINT_IN_TIME...")
    b = backtest("POINT_IN_TIME", lambda t: members_at(hist, t), *args)

    idx = b["net"].index
    spy_m = None
    if spy_close is not None:
        spy_m = spy_close.resample("ME").last().pct_change().reindex(idx)

    # ---------------- headline tables ----------------
    for res in (a, b):
        net, gross = res["net"], res["gross"]
        tbl = pd.DataFrame({v: metrics(net[v]) for v in VARIANTS})
        for v in VARIANTS:
            tbl.loc["Hit rate", v] = (net[v] > res["bottom"].reindex(net.index)).mean()
            g = metrics(gross[v])
            tbl.loc["Gross CAGR (no costs)", v] = g["CAGR"]
            tbl.loc["Gross Sharpe (no costs)", v] = g["Sharpe"]
        if spy_m is not None:
            s = metrics(spy_m.reindex(net.index).dropna())
            tbl["SPY"] = pd.Series(s)
        print(f"\n===== {res['name']}  |  net of {COST_BPS}bp/side, stops fill "
              f"next open  |  {net.index[0]:%b %Y}-{net.index[-1]:%b %Y} "
              f"({len(net)} months) =====")
        print(fmt_table(tbl).fillna("").to_string())

    # ---------------- coverage ----------------
    cov = b["coverage"]
    frac = cov["with_data"] / cov["members"]
    print("\n===== POINT_IN_TIME data coverage (index members with Yahoo prices) =====")
    for yr in (2007, 2009, 2012, 2016, 2020, 2024):
        sl = frac[frac.index.year == yr]
        if len(sl):
            print(f"  {yr}: {sl.mean():.1%}")
    print(f"  months below 90% coverage: {(frac < 0.90).sum()} of {len(frac)}")
    print(f"  picks with unknown sector (left the index, cap not applied): "
          f"{b['unknown']}")

    # ---------------- stop diagnostics ----------------
    print("\n===== STOP DIAGNOSTICS (vs holding to month-end) =====")
    for res in (a, b):
        d = stop_diagnostics(res["trades"])
        for var, x in d.items():
            if x is None:
                continue
            print(f"  {res['name']:<14} {var:<11} {x['stops']:>4} stops of "
                  f"{x['of']} | stop hurt in {x['hurt']} ({x['hurt'] / x['stops']:.0%}) "
                  f"| avg effect per stop {x['avg_effect']:+.1%} "
                  f"| avg fill vs stop level {x['avg_gap']:+.1%}")

    # ---------------- crash windows ----------------
    print("\n===== CRASH WINDOWS: POINT_IN_TIME, net, cumulative return =====")
    net = b["net"]
    head = f"  {'window':<29}" + "".join(f"{v:>12}" for v in VARIANTS) + f"{'SPY':>10}"
    print(head)
    for label, (s0, s1) in CRASH_WINDOWS.items():
        sl = net.loc[s0:s1]
        if sl.empty:
            continue
        cells = "".join(f"{(1 + sl[v]).prod() - 1:>+12.1%}" for v in VARIANTS)
        spy_c = (f"{(1 + spy_m.loc[s0:s1]).prod() - 1:>+10.1%}"
                 if spy_m is not None else "")
        print(f"  {label:<29}{cells}{spy_c}")

    out = b["net"].add_suffix("_net").join(b["gross"])
    out = out.join(a["net"].add_suffix("_net_todaylist"))
    if spy_m is not None:
        out["SPY"] = spy_m
    out.to_csv("backtest_pit_monthly_returns.csv")
    b["trades"].to_csv("backtest_pit_positions.csv", index=False)
    print("\nSaved backtest_pit_monthly_returns.csv and backtest_pit_positions.csv")
    print("NOTE: delisted names without Yahoo data are still missing; see coverage.")


if __name__ == "__main__":
    main()
