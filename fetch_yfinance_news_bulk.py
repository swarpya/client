import requests
from datetime import datetime, timezone
import csv
import time

ticker = "AAPL"
start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
end_date = datetime.now(timezone.utc)

articles_data = []

# Yahoo Finance API endpoint for news
offset = 0
count = 100  # Fetch 100 articles per request
max_articles = 1000  # Maximum to fetch

while offset < max_articles:
    url = f"https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        'q': ticker,
        'quotesCount': 0,
        'newsCount': count,
        'enableFuzzyQuery': False,
        'offset': offset
    }
    
    try:
        response = requests.get(url, params=params, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        data = response.json()
        
        news_items = data.get('news', [])
        
        if not news_items:
            print(f"No more articles found. Total fetched: {offset}")
            break
        
        for article in news_items:
            pub_time = article.get('providerPublishTime')
            
            if pub_time:
                pub_date = datetime.fromtimestamp(pub_time, tz=timezone.utc)
                
                # Filter articles between start and end date
                if start_date <= pub_date <= end_date:
                    title = article.get('title', 'No title')
                    url = article.get('link', 'No URL')
                    provider = article.get('publisher', 'Unknown')
                    
                    articles_data.append({
                        'Date': pub_date.strftime('%Y-%m-%d'),
                        'Time': pub_date.strftime('%H:%M:%S'),
                        'Title': title,
                        'URL': url,
                        'Provider': provider,
                        'Timestamp': pub_time
                    })
                elif pub_date < start_date:
                    # If we've reached articles before our start date, stop
                    print(f"Reached articles before start date. Stopping.")
                    offset = max_articles  # Exit loop
                    break
        
        offset += count
        print(f"Fetched {offset} articles so far...")
        time.sleep(0.5)  # Rate limiting
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        break

# Remove duplicates based on URL
seen_urls = set()
unique_articles = []
for article in articles_data:
    if article['URL'] not in seen_urls:
        seen_urls.add(article['URL'])
        unique_articles.append(article)

# Sort by timestamp (newest first)
unique_articles.sort(key=lambda x: x['Timestamp'], reverse=True)

# Save to CSV
csv_filename = f'{ticker}_news_articles_2025_complete.csv'
if unique_articles:
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Date', 'Time', 'Title', 'URL', 'Provider']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for article in unique_articles:
            writer.writerow({k: v for k, v in article.items() if k != 'Timestamp'})
    
    print(f"\nSuccessfully saved {len(unique_articles)} unique articles to {csv_filename}")
    print(f"Date range: January 1, 2025 to {end_date.strftime('%Y-%m-%d')}")
else:
    print(f"No articles found for {ticker} between January 1, 2025 and today")
