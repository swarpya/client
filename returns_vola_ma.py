import pandas as pd

input_csv = "DNA_news_with_prices.csv"
output_csv = "DNA_news_with_returns_only.csv"

# Load your CSV into pandas DataFrame
df = pd.read_csv(input_csv)

# Ensure 'Price Date' and 'Close' columns exist and are properly formatted
df['Price Date'] = pd.to_datetime(df['Price Date'], errors='coerce')
df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

# Sort by date to ensure chronological order
df = df.sort_values('Price Date').reset_index(drop=True)

# --- Price Returns (close-to-close percent change) ---
df['Close_Return'] = df['Close'].pct_change().fillna(0) * 100  # percent

# --- Intraday open-to-close return ---
df['Open'] = pd.to_numeric(df['Open'], errors='coerce')
df['Intraday_Return'] = ((df['Close'] - df['Open']) / df['Open']).fillna(0) * 100

# --- Save to new CSV ---
df.to_csv(output_csv, index=False)

print(f"Features (returns only) saved to {output_csv}")
