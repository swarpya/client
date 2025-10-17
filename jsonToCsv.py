# --- Part 2: Write CSV with Sentiment & Event Type ---

import json
import csv

input_json_filename = "DNA_finnhub_news_structured.json"
output_csv_filename = "DNA_finnhub_with_sentiment_event.csv"

with open(input_json_filename, "r", encoding="utf-8") as jf, open(output_csv_filename, "w", newline="", encoding="utf-8") as cf:
    data = json.load(jf)
    writer = csv.writer(cf)
    writer.writerow(["Datetime", "Headline", "Summary", "URL", "Source", "Sentiment", "EventType"])
    for item in data:
        writer.writerow([
            item["Datetime"],
            item["Headline"],
            item["Summary"],
            item["URL"],
            item["Source"],
            item["Sentiment"],
            item["EventType"]
        ])

print(f"Combined CSV with sentiment and event type saved to {output_csv_filename}")
