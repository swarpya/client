import finnhub
import csv
from datetime import datetime, timezone

api_key = "d3ospphr01quo6o5qu4gd3ospphr01quo6o5qu50"
symbol = "AAPL"

# Use today's date (UTC) as default
today = datetime.now(timezone.utc).strftime('%Y-%m-%d')

# Or set to a specific date:
today = "2025-10-16"

finnhub_client = finnhub.Client(api_key=api_key)

# Finnhub API expects a date range, so use the same day for start and end
news = finnhub_client.company_news(symbol, _from=today, to=today)

csv_filename = f"{symbol}_news_{today}.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Datetime", "Headline", "Summary", "URL", "Source"])
    for article in news:
        ts = article.get('datetime')
        if isinstance(ts, (int, float)):
            pub_date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S %Z')
        else:
            pub_date = ''
        writer.writerow([
            pub_date,
            article.get('headline', ''),
            article.get('summary', ''),
            article.get('url', ''),
            article.get('source', '')
        ])

print(f"News for {symbol} on {today} saved to {csv_filename}")
