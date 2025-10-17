import yfinance as yf
from datetime import datetime

ticker = "AAPL"
date_to_fetch = "2025-10-15"

stock = yf.Ticker(ticker)
news_list = stock.news

found = False
for article in news_list:
    content = article.get('content', {})
    pub_date_str = content.get('pubDate')
    if pub_date_str:
        pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
        article_date = pub_date.strftime('%Y-%m-%d')
        print(f"DEBUG: {article_date} -> {content.get('title', 'No title')}")
        if article_date == date_to_fetch:
            found = True
            print(f"Title: {content.get('title', 'No title')}")
            print(f"URL: {content.get('clickThroughUrl', {}).get('url', content.get('canonicalUrl', {}).get('url', 'No URL'))}")
            print(f"Published at: {pub_date_str} UTC\n")
if not found:
    print(f"No articles found for {date_to_fetch}")
