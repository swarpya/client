import requests
import csv

API_KEY = ""
ticker = "DNA"
input_csv = "DNA_finnhub_with_sentiment_event.csv"
output_csv = "DNA_news_with_prices.csv"

def get_open_close_alpha(date_to_get, ticker, api_key):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "apikey": api_key,
        "outputsize": "full",
    }
    resp = requests.get(url, params=params)
    data = resp.json()
    if "Time Series (Daily)" in data:
        prices = data["Time Series (Daily)"]
        if date_to_get in prices:
            open_price = prices[date_to_get]['1. open']
            close_price = prices[date_to_get]['4. close']
            return open_price, close_price, date_to_get
        else:
            # Fallback: Get previous available date
            available_dates = sorted(prices.keys(), reverse=True)
            earlier_dates = [d for d in available_dates if d < date_to_get]
            if earlier_dates:
                fallback_date = earlier_dates[0]
                open_price = prices[fallback_date]['1. open']
                close_price = prices[fallback_date]['4. close']
                return open_price, close_price, fallback_date
            else:
                return "", "", ""
    else:
        return "", "", ""

# Download price data for the whole ticker once to avoid many API calls
url = "https://www.alphavantage.co/query"
params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": ticker,
    "apikey": API_KEY,
    "outputsize": "full",
}
resp = requests.get(url, params=params)
data = resp.json()
prices_dict = data["Time Series (Daily)"] if "Time Series (Daily)" in data else {}

def lookup_prices(date_to_get):
    if date_to_get in prices_dict:
        open_price = prices_dict[date_to_get]['1. open']
        close_price = prices_dict[date_to_get]['4. close']
        return open_price, close_price, date_to_get
    else:
        available_dates = sorted(prices_dict.keys(), reverse=True)
        earlier_dates = [d for d in available_dates if d < date_to_get]
        if earlier_dates:
            fallback_date = earlier_dates[0]
            open_price = prices_dict[fallback_date]['1. open']
            close_price = prices_dict[fallback_date]['4. close']
            return open_price, close_price, fallback_date
        else:
            return "", "", ""

with open(input_csv, "r", encoding="utf-8") as f, open(output_csv, "w", newline="", encoding="utf-8") as out_f:
    reader = csv.reader(f)
    rows = list(reader)
    header = rows[0]
    writer = csv.writer(out_f)
    header_plus = header + ["Open", "Close", "Price Date"]
    writer.writerow(header_plus)
    for row in rows[1:]:
        date_field = row[0]  # Expects date in first column (e.g. 2025-01-09 13:00:00 UTC)
        date_only = date_field.split()[0]
        open_p, close_p, price_dt = lookup_prices(date_only)
        writer.writerow(row + [open_p, close_p, price_dt])

print(f"CSV enriched with open/close prices saved to {output_csv}")
