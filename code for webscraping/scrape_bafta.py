import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Define function to convert year to ordinal ceremony number
def ordinal(year):
    n = year - 1947
    suffix = 'th' if 10 <= n % 100 <= 20 else {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Define function to isolate/clean actor's name by stripping text after dash
def clean_name(text):
    name = re.split(r'\s*[–—-]\s*', text)[0]
    name = re.sub(r'\[.*?\]', '', name)
    return name.strip()

# Define function to scrape BAFTA nominees and winner for a given year and category
def scrape_bafta(year, category):
    ceremony = ordinal(year)
    url = f"https://en.wikipedia.org/wiki/{ceremony}_British_Academy_Film_Awards"
    print(f"Scraping {year}")
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Could not load page for {year}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    data = []

    # Search for the section in any <td> or <li>
    for tag in soup.find_all(['td', 'li']):
        if category in tag.get_text():
            ul = tag.find("ul")
            if not ul:
                continue
            lis = ul.find_all("li")
            if not lis:
                continue

            # First <li> is the winner (usually in <b>) while the others are nominees
            for i, li in enumerate(lis):
                nominee_text = li.get_text(strip=True)
                winner_tag = li.find("b")
                name = clean_name(winner_tag.get_text()) if winner_tag else clean_name(nominee_text)
                status = "Won" if i == 0 else "Lost"
                data.append({"Year": year, "Name": name, "BAFTA": status})
            break

    if not data:
        print(f"Award not found for {year}")
    return data

# Choose category
categories = ["Best Actor in a Leading Role",
              "Best Actress in a Leading Role",
              "Best Actor in a Supporting Role",
              "Best Actress in a Supporting Role"]
abbreviations = ["best_actor",
                "best_actress",
                "best_supp_actor",
                "best_supp_actress"]
category = categories[3]
abbreviation = abbreviations[3]

# Run scrape_bafta() for each year
all_data = []
for year in range(1969, 2026):
    yearly_data = scrape_bafta(year, category)
    all_data.extend(yearly_data)

# Save output
df = pd.DataFrame(all_data)
output_path = f"/Users/rickytruong/Desktop/Oscar Predictor/Python for Webscraping/bafta_{abbreviation}.csv"
df.to_csv(output_path, index=False)
print(f"Data saved to: {output_path}")