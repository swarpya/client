import requests
import json
from bs4 import BeautifulSoup
from datetime import datetime

SERPAPI_API_KEY = "YOUR_REAL_SERPAPI_API_KEY"

def fetch_google_news_with_story(query, num_results=10, news_date=None):
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google_news",
        "q": query,
        "num": num_results
    }

    search = requests.get("https://serpapi.com/search", params=params)
    response = search.json()
    news_json_list = []

    if not news_date:
        news_date = datetime.now().strftime("%Y-%m-%d")

    if "news_results" in response:
        for news in response["news_results"]:
            # SerpApi returns date string, typically like "10/15/2025, 07:12 PM, +0000 UTC"
            news_time = news.get("date", "")
            # Try to match the date in yyyy-mm-dd
            matches = False
            try:
                if news_time:
                    date_obj = datetime.strptime(news_time.split(',')[0], "%m/%d/%Y")
                    date_str = date_obj.strftime("%Y-%m-%d")
                    matches = date_str == news_date
            except Exception:
                matches = False

            if matches:
                article_url = news.get("link", "")
                full_story = ""
                if article_url:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0'}
                        article_response = requests.get(article_url, headers=headers, timeout=10)
                        soup = BeautifulSoup(article_response.content, 'html.parser')
                        paragraphs = soup.find_all('p')
                        full_story = ' '.join(p.get_text() for p in paragraphs)
                    except Exception:
                        full_story = ""
                news_item = {
                    "title": news.get("title", ""),
                    "time": news_time,
                    "story": full_story
                }
                news_json_list.append(news_item)

    return news_json_list

# Example usage
news_date = "2025-01-01"  # or "2025-10-14"
news_json_list = fetch_google_news_with_story("iPhone", num_results=20, news_date=news_date)

with open("news_results.json", "w", encoding="utf-8") as f:
    json.dump(news_json_list, f, ensure_ascii=False, indent=4)

print("News results saved to news_results.json")
