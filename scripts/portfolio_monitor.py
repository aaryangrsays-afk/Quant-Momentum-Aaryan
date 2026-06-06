import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIG ---
EMAIL = "aaryangrsays@gmail.com"
APP_PASSWORD = "wiev wscy cgbl ilyr"  # paste yours here
ALERT_THRESHOLD = 0.03  # 3% move triggers alert

# --- YOUR POSITIONS ---
positions = {
    "C":   {"shares": 0.3723, "avg_price": 134.28},
    "DE":  {"shares": 0.0834, "avg_price": 598.81},
    "IBM": {"shares": 0.1637, "avg_price": 305.34},
    "MDT": {"shares": 0.6147, "avg_price": 81.34},
    "VLO": {"shares": 0.1916, "avg_price": 260.86},
}

def check_portfolio():
    alerts = []
    summary_rows = []
    
    for ticker, pos in positions.items():
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        
        if len(hist) < 2:
            continue
            
        prev_close = hist["Close"].iloc[-2]
        curr_price = hist["Close"].iloc[-1]
        daily_change = (curr_price - prev_close) / prev_close
        
        market_value = pos["shares"] * curr_price
        unrealized_pnl = (curr_price - pos["avg_price"]) * pos["shares"]
        
        summary_rows.append({
            "ticker": ticker,
            "current_price": curr_price,
            "daily_change": daily_change,
            "market_value": market_value,
            "unrealized_pnl": unrealized_pnl
        })
        
        if abs(daily_change) >= ALERT_THRESHOLD:
            alerts.append({
                "ticker": ticker,
                "daily_change": daily_change,
                "current_price": curr_price
            })
    
    return alerts, summary_rows

def send_email(alerts, summary_rows):
    total_value = sum(r["market_value"] for r in summary_rows)
    total_pnl = sum(r["unrealized_pnl"] for r in summary_rows)
    
    # Build summary table
    table = ""
    for r in summary_rows:
        direction = "🟢" if r["daily_change"] > 0 else "🔴"
        table += f"{direction} {r['ticker']:5s} | ${r['current_price']:.2f} | {r['daily_change']:+.2%} today | P&L: ${r['unrealized_pnl']:+.2f}\n"
    
    # Build alert section
    if alerts:
        alert_text = "⚠️ ALERTS — positions moved more than 3% today:\n\n"
        for a in alerts:
            direction = "UP" if a["daily_change"] > 0 else "DOWN"
            alert_text += f"  {a['ticker']} is {direction} {abs(a['daily_change']):.2%} — current price ${a['current_price']:.2f}\n"
    else:
        alert_text = "✅ No significant moves today (all positions within 3%).\n"

    body = f"""
Quant Portfolio Monitor — {datetime.today().strftime('%B %d, %Y')}

{alert_text}
---
PORTFOLIO SUMMARY

{table}
---
Total Portfolio Value: ${total_value:.2f}
Total Unrealized P&L:  ${total_pnl:+.2f}
Entry Capital:         $249.89
Return Since Entry:    {((total_value - 249.89) / 249.89):+.2%}

Stop Loss Level: $212.50
Status: {'⚠️ APPROACHING STOP LOSS' if total_value < 225 else '✅ Within normal range'}
"""

    msg = MIMEMultipart()
    msg["From"] = EMAIL
    msg["To"] = EMAIL
    msg["Subject"] = f"{'⚠️ ALERT' if alerts else '✅ Daily'} — Quant Portfolio Update {datetime.today().strftime('%b %d')}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, APP_PASSWORD)
        server.send_message(msg)
    
    print(f"Email sent — {len(alerts)} alert(s) triggered")

if __name__ == "__main__":
    print(f"Checking portfolio — {datetime.today().strftime('%B %d, %Y')}")
    alerts, summary_rows = check_portfolio()
    send_email(alerts, summary_rows)
    print("Done.")