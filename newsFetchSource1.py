from newsapi import NewsApiClient
import json
from datetime import datetime, timedelta
import time

# Initialize NewsAPI client
# IMPORTANT: Never commit your API key to GitHub - use environment variables instead
newsapi = NewsApiClient(api_key='610afd7dbeec4928beb9ea82f5b42a8c')

# Define date range: January 1, 2025 + 100 days = April 10, 2025
start_date = datetime(2025, 1, 1)
end_date = start_date + timedelta(days=100)

# Format dates for NewsAPI (YYYY-MM-DD format)
from_date = start_date.strftime('%Y-%m-%d')
to_date = end_date.strftime('%Y-%m-%d')

print(f"Fetching Apple news from {from_date} to {to_date}")
print("=" * 60)

all_articles = []
page = 1
max_results = 100  # NewsAPI free tier limits to 100 total results

# The get_everything endpoint with pagination
while True:
    try:
        print(f"\nFetching page {page}...")
        
        # Make API request
        response = newsapi.get_everything(
            q='Apple',
            from_param=from_date,
            to=to_date,
            language='en',
            sort_by='publishedAt',
            page_size=100,  # Max 100 per page
            page=page
        )
        
        # Check if we got articles
        if response['status'] == 'ok':
            articles = response['articles']
            total_results = response['totalResults']
            
            if len(articles) == 0:
                print("No more articles found.")
                break
            
            all_articles.extend(articles)
            print(f"Retrieved {len(articles)} articles (Total: {len(all_articles)}/{total_results})")
            
            # Free tier limitation: only first 100 results accessible
            if len(all_articles) >= 100:
                print("\n⚠️  Reached free tier limit: 100 articles maximum")
                break
            
            # If we got fewer than page_size articles, we're done
            if len(articles) < 100:
                print("Reached end of results.")
                break
            
            page += 1
            time.sleep(1)  # Be respectful with rate limits
        else:
            print(f"Error: {response.get('message', 'Unknown error')}")
            break
            
    except Exception as e:
        error_message = str(e)
        print(f"\n✗ Error occurred: {error_message}")
        
        # Check for specific errors
        if 'parameterInvalid' in error_message:
            print("\n❌ IMPORTANT: Your free plan does not support dates this far back!")
            print("   Free tier only allows articles from the last 30 days.")
            print("   The dates Jan 1 - Apr 10, 2025 are beyond the 30-day limit.")
            print("\n   Solutions:")
            print("   1. Change dates to last 30 days (Oct 16 - Sep 16, 2025)")
            print("   2. Upgrade to Business plan ($449/month) for full historical access")
        elif 'rateLimited' in error_message:
            print("   Rate limit hit. Wait before making more requests.")
        
        break

# Save to JSON file
output_data = {
    'api': 'NewsAPI.org',
    'search_query': 'Apple',
    'date_range': {
        'from': from_date,
        'to': to_date,
        'days': 100
    },
    'total_articles_retrieved': len(all_articles),
    'limitations': {
        'free_tier': 'Last 30 days only, 100 articles max',
        'requests_per_day': 100
    },
    'articles': all_articles
}

output_filename = 'apple_news_100days.json'

with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n{'=' * 60}")
print(f"✓ Saved {len(all_articles)} articles to {output_filename}")
print(f"{'=' * 60}")

# Display sample articles
if all_articles:
    print("\n📰 Sample articles:\n")
    for i, article in enumerate(all_articles[:5]):
        print(f"{i+1}. {article['title']}")
        print(f"   Source: {article['source']['name']}")
        print(f"   Published: {article['publishedAt']}")
        print(f"   URL: {article['url'][:80]}...")
        print()
else:
    print("\n⚠️  No articles retrieved!")
    print("\nLikely reason: NewsAPI free tier only allows last 30 days of data")
    print("January 2025 is beyond this limit.")
