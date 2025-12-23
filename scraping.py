import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

BASE_SEARCH_URL = "https://www.liveauctioneers.com/search/?keyword={}"

CATEGORIES = {
    "Furniture": "antique furniture",
    "Ceramics": "antique ceramic",
    "Decorative Art": "decorative art antique"
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

items = []

for category_name, query in CATEGORIES.items():
    print(f"\nScraping category: {category_name}")

    search_url = BASE_SEARCH_URL.format(query.replace(" ", "+"))

    try:
        response = requests.get(search_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed search page: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    
    cards = soup.select("a[href^='/item/']")[:12]

    if not cards:
        print("No items found on page")
        continue

    for card in cards:
        item_url = "https://www.liveauctioneers.com" + card.get("href")

        try:
            item_resp = requests.get(item_url, headers=HEADERS, timeout=30)
            item_resp.raise_for_status()
            item_soup = BeautifulSoup(item_resp.text, "html.parser")

            title = item_soup.find("h1")
            desc = item_soup.find("div", class_="lot-description")
            price = item_soup.find("span", class_="price")

            images = [
                img["src"]
                for img in item_soup.select("img")
                if img.get("src")
            ][:3]

            items.append({
                "source_url": item_url,
                "item_title": title.text.strip() if title else None,
                "category": category_name,
                "description_raw": desc.text.strip() if desc else None,
                "images": images,
                "listed_price": price.text.strip() if price else None,
                "currency": "USD",
                "seller_location": None
            })

            time.sleep(random.uniform(1.5, 3))

        except Exception as e:
            print("Skipped item:", e)
            continue

df = pd.DataFrame(items)
df.to_csv("data/raw_items.csv", index=False)

print("\n✅ Saved data/raw_items.csv")
print(f"Total items scraped: {len(df)}")
