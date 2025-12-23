import pandas as pd
import re

df = pd.read_csv("data/raw_items.csv")

def clean_price(price):
    if pd.isna(price):
        return None
    price = re.sub(r"[^\d.]", "", price)
    return float(price) if price else None

df["listed_price_numeric"] = df["listed_price"].apply(clean_price)

df["description_clean"] = (
    df["description_raw"]
    .fillna("")
    .str.replace(r"<.*?>", "", regex=True)
    .str.strip()
)

df = df.drop_duplicates(
    subset=["item_title", "description_clean"]
)

df.to_csv("data/clean_items.csv", index=False)
print("Saved clean_items.csv")
