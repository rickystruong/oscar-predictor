import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import unicodedata
from html import unescape

# Define function to convert year to ordinal ceremony number
def ordinal(year):
    n = year - 1996 + 1  # 1st awards = 1996
    suffix = 'th' if 10 <= n % 100 <= 20 else {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Define function to isolate/clean actor's name by stripping text after dash
def clean_name(text):
    name = re.split(r'\s*[–—-]\s*', text)[0]
    name = re.sub(r'\(TIE\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\[.*?\]', '', name)
    name = unescape(name.strip())
    # Manual fix for names that are missing special characters
    if name == "Zoe Saldana":
        name = "Zoe Saldaña"
    elif name == "Penelope Cruz":
        name = "Penélope Cruz"
    return name

# Normalize name for matching (i.e., remove special characters like ñ → n)
def normalize_name(name):
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("utf-8").lower()

# Define function to scrape Critics' nominees and winner for a given year and category
def scrape_critics_choice(year, category):
    ceremony = ordinal(year)
    url = f"https://en.wikipedia.org/wiki/{ceremony}_Critics%27_Choice_Awards"
    print(f"Scraping {year}")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"Could not load page for {year}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    data = []
    seen_names = set()

    # Extract winner from figcaption
    for caption in soup.find_all("figcaption"):
        if category in caption.get_text():
            a_tag = caption.find("a")
            if a_tag:
                name = clean_name(a_tag.get_text())
                norm = normalize_name(name)
                if norm not in seen_names:
                    data.append({"Year": year, "Name": name, "Critics_Choice": "Won"})
                    seen_names.add(norm)
            break

    # Extract nominees if available
    for tag in soup.find_all(['td', 'li']):
        if category in tag.get_text():
            ul = tag.find("ul")
            if not ul:
                continue
            lis = ul.find_all("li")
            if not lis:
                continue

            for li in lis:
                text = li.get_text(strip=True)
                name = clean_name(text)
                norm = normalize_name(name)
                if norm not in seen_names:
                    data.append({"Year": year, "Name": name, "Critics_Choice": "Lost"})
                    seen_names.add(norm)
            break

    return data

# Choose category
categories = ["Best Actor",
              "Best Actress",
              "Best Supporting Actor",
              "Best Supporting Actress"]
abbreviations = ["best_actor",
                "best_actress",
                "best_supp_actor",
                "best_supp_actress"]
category = categories[3]
abbreviation = abbreviations[3]

# Run scrape_critics_choice() for each year
all_data = []
for year in range(2002, 2026):
    yearly_data = scrape_critics_choice(year, category)
    all_data.extend(yearly_data)

# Save output
df = pd.DataFrame(all_data)
output_path = f"/Users/rickytruong/Desktop/Oscar Predictor/Python for Webscraping/critics_{abbreviation}.csv"
df.to_csv(output_path, index=False)
print(f"Data saved to: {output_path}")