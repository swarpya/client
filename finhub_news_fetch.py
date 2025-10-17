import finnhub
import csv
from datetime import datetime, timedelta, timezone
import time
#main
api_key = ""
symbol = "DNA"
interval_days = 5

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=api_key)

# Set up date ranges
start_dt = datetime(2025, 1, 1)
end_dt = datetime(2025, 10, 15)
all_news = []
request_count = 0
api_limit_per_sec = 30
batch_requests = []

cur_start = start_dt
while cur_start < end_dt:
    cur_end = min(cur_start + timedelta(days=interval_days-1), end_dt)
    batch_requests.append((cur_start.strftime('%Y-%m-%d'), cur_end.strftime('%Y-%m-%d')))
    cur_start = cur_end + timedelta(days=1)

for idx, (batch_start, batch_end) in enumerate(batch_requests):
    news = finnhub_client.company_news(symbol, _from=batch_start, to=batch_end)
    all_news.extend(news)
    request_count += 1
    print(f"Fetched {len(news)} articles from {batch_start} to {batch_end}")

    # Sleep if nearing the API rate limit
    if request_count % api_limit_per_sec == 0:
        print("Respecting plan's API call limit. Sleeping for 1 second...")
        time.sleep(1)

# Remove duplicates based on url
seen_urls = set()
unique_news = []
for article in all_news:
    url = article.get('url')
    if url and url not in seen_urls:
        seen_urls.add(url)
        unique_news.append(article)

csv_filename = f"{symbol}_finnhub_news_20250101_to_20251015.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Datetime", "Headline", "Summary", "URL", "Source"])
    for article in unique_news:
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

print(f"Total news articles saved to {csv_filename}: {len(unique_news)}")
