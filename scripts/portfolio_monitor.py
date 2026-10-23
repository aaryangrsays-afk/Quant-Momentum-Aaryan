import yfinance as yf
import smtplib
import os
import json
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIG ---
EMAIL = "aaryangrsays@gmail.com"
APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")  # set in shell profile, never hardcode
ALERT_THRESHOLD = 0.03
# Paths are overridable so the same script runs on the Mac and in GitHub Actions.
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_FILE = os.environ.get("STATE_FILE", os.path.expanduser("~/portfolio_state.txt"))
POSITIONS_FILE = os.environ.get("POSITIONS_FILE",
                                os.path.join(_REPO_ROOT, "live", "positions.json"))
# PER-STOCK VOL-SCALED STOP (keep in sync with VOL_* in quant_momentum.py)
#   stop_pct = clip(VOL_K x stdev(last VOL_WINDOW_DAYS daily returns) x sqrt(21),
#                   VOL_FLOOR, VOL_CAP)
#   SELL when close <= avg_price x (1 - stop_pct); then hold cash until the
#   next monthly rebalance.
# stop_pct is computed ONCE per position (first run after you add it to
# positions.json) and saved back into positions.json, so the stop doesn't
# drift with volatility while you hold. To reset a name's stop, delete its
# "stop_pct" field.
VOL_K = 1.5
VOL_WINDOW_DAYS = 63
VOL_FLOOR = 0.08
VOL_CAP = 0.25

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("portfolio_monitor")


# ---------------- POSITIONS ----------------
def load_positions():
    """
    positions.json expected shape:
    {
        "MRNA": {"shares": 0.6866, "avg_price": 59.84},
        "FIX":  {"shares": 0.0192, "avg_price": 1676.01},
        ...
    }
    Entry capital is derived from this file (sum of shares * avg_price),
    so it self-corrects on every rebalance instead of relying on a
    hand-maintained constant.
    """
    try:
        with open(POSITIONS_FILE, "r") as f:
            positions = json.load(f)
    except FileNotFoundError:
        log.error(f"positions.json not found at {POSITIONS_FILE}")
        raise SystemExit(1)
    except json.JSONDecodeError as e:
        log.error(f"positions.json is not valid JSON: {e}")
        raise SystemExit(1)

    if not positions:
        log.error("positions.json is empty")
        raise SystemExit(1)

    return positions


def save_positions(positions):
    tmp = POSITIONS_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(positions, f, indent=2)
    os.replace(tmp, POSITIONS_FILE)


def vol_stop_pct(hist_close):
    rets = hist_close.pct_change().dropna().iloc[-VOL_WINDOW_DAYS:]
    if len(rets) < 20:
        return None
    return float(min(max(VOL_K * rets.std() * (21 ** 0.5), VOL_FLOOR), VOL_CAP))


def compute_entry_capital(positions, tickers=None):
    """Entry capital for the names we could actually price.

    If a fetch fails, total_value loses that name's market value. Summing
    entry capital over ALL positions would then show a fake loss, so the
    caller passes the set of tickers that were priced.
    """
    if tickers is not None:
        return sum(pos["shares"] * pos["avg_price"]
                   for t, pos in positions.items() if t in tickers)
    return sum(pos["shares"] * pos["avg_price"] for pos in positions.values())


# ---------------- STATE ----------------
def load_last_state():
    if not os.path.exists(STATE_FILE):
        return None, None, False
    try:
        with open(STATE_FILE, "r") as f:
            parts = f.read().strip().split(",")
            return parts[0], float(parts[1]), parts[2] == "True"
    except Exception as e:
        log.warning(f"Could not parse state file, resetting: {e}")
        return None, None, False


def save_state(value, daily_sent):
    with open(STATE_FILE, "w") as f:
        f.write(f"{datetime.now().date()},{value},{daily_sent}")


# ---------------- DATA ----------------
def check_portfolio(positions):
    alerts = []
    stop_hits = []
    summary_rows = []
    failed = []
    positions_changed = False

    for ticker, pos in positions.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="6mo", interval="1d")

            if hist is None or len(hist) < 2:
                log.warning(f"{ticker}: insufficient history, skipping")
                failed.append(ticker)
                continue

            prev_close = hist["Close"].iloc[-2]
            curr_price = hist["Close"].iloc[-1]

            if prev_close == 0:
                log.warning(f"{ticker}: prev_close is 0, skipping")
                failed.append(ticker)
                continue

            daily_change = (curr_price - prev_close) / prev_close
            market_value = pos["shares"] * curr_price
            unrealized_pnl = (curr_price - pos["avg_price"]) * pos["shares"]
            if pos.get("stop_pct") is None:
                sp = vol_stop_pct(hist["Close"])
                if sp is None:
                    log.warning(f"{ticker}: not enough history for vol stop, using {VOL_CAP:.0%}")
                    sp = VOL_CAP
                pos["stop_pct"] = round(sp, 4)
                positions_changed = True
                log.info(f"{ticker}: stop frozen at -{sp:.1%} from entry")
            stop_pct = pos["stop_pct"]
            stop_price = pos["avg_price"] * (1 - stop_pct)
            from_entry = curr_price / pos["avg_price"] - 1

            summary_rows.append({
                "ticker": ticker,
                "current_price": curr_price,
                "daily_change": daily_change,
                "market_value": market_value,
                "unrealized_pnl": unrealized_pnl,
                "stop_price": stop_price,
                "stop_pct": stop_pct,
                "from_entry": from_entry,
                "bar_date": str(hist.index[-1].date()),
            })

            if curr_price <= stop_price:
                stop_hits.append({
                    "ticker": ticker,
                    "current_price": curr_price,
                    "avg_price": pos["avg_price"],
                    "stop_price": stop_price,
                    "stop_pct": stop_pct,
                    "from_entry": from_entry,
                })

            if abs(daily_change) >= ALERT_THRESHOLD:
                alerts.append({
                    "ticker": ticker,
                    "daily_change": daily_change,
                    "current_price": curr_price,
                })

        except Exception as e:
            log.error(f"{ticker}: failed to fetch/process — {e}")
            failed.append(ticker)

    if positions_changed:
        save_positions(positions)
    total_value = sum(r["market_value"] for r in summary_rows)
    return alerts, stop_hits, summary_rows, total_value, failed


# ---------------- EMAIL ----------------
def send_email(alerts, stop_hits, summary_rows, total_value, entry_capital, reason,
               failed=None):
    if not APP_PASSWORD:
        log.error(f"Cannot send '{reason}' — GMAIL_APP_PASSWORD is not set.")
        return False
    total_pnl = sum(r["unrealized_pnl"] for r in summary_rows)
    return_since_entry = (total_value - entry_capital) / entry_capital if entry_capital else 0.0

    table = ""
    for r in summary_rows:
        direction = "\U0001F7E2" if r["daily_change"] > 0 else "\U0001F534"
        table += (
            f"{direction} {r['ticker']:6s} | "
            f"${r['current_price']:.2f} | "
            f"{r['daily_change']:+.2%} | "
            f"vs entry {r['from_entry']:+.1%} | stop -{r['stop_pct']:.1%} @ ${r['stop_price']:.2f} | "
            f"P&L: ${r['unrealized_pnl']:+.2f}\n"
        )

    alert_text = "\u26A0\uFE0F ALERTS:\n"
    if alerts:
        for a in alerts:
            direction = "UP" if a["daily_change"] > 0 else "DOWN"
            alert_text += f"  {a['ticker']} is {direction} {abs(a['daily_change']):.2%} today\n"
    else:
        alert_text += "  None — all positions within 3% threshold\n"

    if stop_hits:
        stop_text = "\U0001F6D1 STOP HIT — SELL NEXT SESSION, HOLD CASH UNTIL REBALANCE:\n"
        for s in stop_hits:
            stop_text += (
                f"  {s['ticker']}: close ${s['current_price']:.2f} <= stop ${s['stop_price']:.2f} "
                f"({s['from_entry']:+.1%} vs entry ${s['avg_price']:.2f}; stop was -{s['stop_pct']:.1%})\n"
            )
        stop_text += "  After selling: remove the name from positions.json.\n"
    else:
        stop_text = (f"\u2705 No stops hit (vol-scaled per-stock stops: {VOL_K} x 1m vol, "
                     f"{VOL_FLOOR:.0%}-{VOL_CAP:.0%})\n")

    bar_dates = sorted({r.get("bar_date", "?") for r in summary_rows})
    data_note = f"Prices from daily bar(s): {', '.join(bar_dates)}\n"
    if failed:
        data_note += (f"⚠️ INCOMPLETE DATA — could not price: {', '.join(failed)}. "
                      f"Totals and Return Since Entry cover only the "
                      f"{len(summary_rows)} name(s) below.\n")

    body = f"""
Quant Portfolio Monitor — {datetime.now().strftime('%Y-%m-%d %H:%M')}
TRIGGER: {reason}

{data_note}
{stop_text}
{alert_text}
PORTFOLIO SUMMARY
{'-'*55}
{table}{'-'*55}
Total Portfolio Value:  ${total_value:.2f}
Total Unrealized P&L:   ${total_pnl:+.2f}

Entry Capital:          ${entry_capital:.2f}
Return Since Entry:     {return_since_entry:+.2%}
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = f"Quant Update — {reason} — {datetime.now().strftime('%Y-%m-%d')}"
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, APP_PASSWORD)
            server.send_message(msg)
        log.info(f"Email sent — {reason}")
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("SMTP auth failed — check GMAIL_APP_PASSWORD env var is set and valid")
        return False
    except Exception as e:
        log.error(f"Failed to send email: {e}")
        return False


# ---------------- MAIN ----------------
def main():
    # A missing credential must NEVER stop the stop-loss check from running.
    # Stops are evaluated and frozen first; only the send is skipped.
    if not APP_PASSWORD:
        log.error("GMAIL_APP_PASSWORD is not set — stops will still be checked "
                  "and frozen, but no email can be sent.")

    now = datetime.now()
    today_str = str(now.date())
    log.info("Running portfolio monitor...")

    positions = load_positions()

    alerts, stop_hits, summary_rows, total_value, failed = check_portfolio(positions)

    # Entry capital must cover exactly the names we priced, or one failed
    # fetch silently reads as a large loss.
    priced = {r["ticker"] for r in summary_rows}
    entry_capital = compute_entry_capital(positions, priced)

    if failed:
        log.warning(f"Could not price: {', '.join(failed)} — totals cover "
                    f"{len(priced)} of {len(positions)} positions.")

    if not summary_rows:
        # Scheduled runs only happen after a US trading day, so no data means the
        # price fetch broke. Fail loudly (non-zero exit -> GitHub emails you)
        # instead of skipping silently.
        log.error("No price data returned for any position — not emailing.")
        return 1

    last_date, last_value, daily_sent = load_last_state()

    is_new_day = (last_date != today_str)
    if is_new_day:
        daily_sent = False

    # One email per run. Previously a stop hit on report day sent three
    # near-identical emails and tripled the SMTP failure surface.
    # The daily report fires on the FIRST run of each day, whatever the hour.
    # It used to be gated behind `current_hour >= 15`, which the 7am cron could
    # never satisfy (7 >= 15 is False), so the report never sent from cron at
    # all — only from manual runs. Cron fires once a day, so no gate is needed.
    want_daily = not daily_sent
    reasons = []
    if stop_hits:  # most urgent, so it leads the subject line
        reasons.append("STOP HIT: SELL " + ", ".join(s["ticker"] for s in stop_hits))
    if want_daily:
        reasons.append("DAILY REPORT")
    if alerts:
        reasons.append("STOCK ALERT >3%")

    email_sent = False
    if reasons:
        email_sent = send_email(alerts, stop_hits, summary_rows, total_value,
                                entry_capital, " | ".join(reasons), failed)
        if email_sent and want_daily:
            daily_sent = True
        if not email_sent:
            log.error("Email did not send — stop/alert state was still evaluated above.")
    else:
        log.info("No email needed — already reported today, no stops hit, no alerts.")

    save_state(total_value, daily_sent)
    log.info("Done.")
    # Non-zero exit when a needed email didn't go out, so the scheduler
    # (GitHub Actions) reports the failure instead of it going unnoticed.
    return 1 if (reasons and not email_sent) else 0


if __name__ == "__main__":
    raise SystemExit(main())
