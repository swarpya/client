# --- Part 1: LLM Classification to JSON ---

from groq import Groq
import csv
import json

client = Groq(api_key="")
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

SENTIMENTS = ["positive", "negative", "neutral"]
EVENT_TYPES = [
    "product_launch", "earnings", "merger_acquisition", "management_change", "regulatory",
    "partnership", "legal", "analyst_rating", "market_trend", "innovation", "other"
]

def classify_news(summary):
    prompt = (
        "Classify the following market news summary into:\n"
        "1. Sentiment: one of ['positive', 'negative', 'neutral']\n"
        f"2. EventType: one of {EVENT_TYPES}\n"
        "Return JSON: {\"sentiment\": ..., \"event_type\": ...}.\n"
        "Use ONLY values from the provided lists. If unsure, use 'neutral' for sentiment and 'other' for event_type.\n\n"
        f"SUMMARY: {summary}\nJSON:"
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a market news classifier. Only output valid JSON per instructions."},
            {"role": "user", "content": prompt}
        ],
        model=MODEL_NAME
    )
    # Parse and validate
    try:
        output = chat_completion.choices[0].message.content.strip()
        result = json.loads(output)
        sentiment = result.get("sentiment", "neutral")
        event_type = result.get("event_type", "other")
        if sentiment not in SENTIMENTS:
            sentiment = "neutral"
        if event_type not in EVENT_TYPES:
            event_type = "other"
        return sentiment, event_type
    except Exception:
        return "neutral", "other"

csv_filename = "DNA_finnhub_news_20250101_to_20251015.csv"
out_json = []
with open(csv_filename, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        summary = row["Summary"]
        sentiment, event_type = classify_news(summary)
        out_json.append({
            "Datetime": row["Datetime"],
            "Headline": row["Headline"],
            "Summary": summary,
            "URL": row["URL"],
            "Source": row["Source"],
            "Sentiment": sentiment,
            "EventType": event_type
        })

with open("DNA_finnhub_news_structured.json", "w", encoding="utf-8") as f:
    json.dump(out_json, f, indent=2)

print("Sentiment & event classification results saved to DNA_finnhub_news_structured.json")
