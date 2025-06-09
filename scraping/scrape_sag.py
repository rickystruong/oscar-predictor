import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Define function to convert year to ordinal ceremony number
def ordinal(year):
    n = year - 1995 + 1
    suffix = 'th' if 10 <= n % 100 <= 20 else {1:'st', 2:'nd', 3:'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

# Define function to isolate/clean actor's name by stripping text after dash
def clean_name(text):
    return re.split(r'\s*[–—-]\s*', text)[0].strip()

# Define function to scrape SAG nominees and winner for a given year and category
def scrape_sag(year, category):
    url = f"https://en.wikipedia.org/wiki/{ordinal(year)}_Screen_Actors_Guild_Awards"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []

    # Use newer structure (2021–2025): complex nested <ul> under <td>
    if year >= 2021:
        for td in soup.find_all("td"):
            if category in td.get_text():
                ul = td.find("ul")
                if not ul:
                    break

                first_li = ul.find("li")
                if not first_li:
                    break

                winner_tag = first_li.find("b")
                winner = clean_name(winner_tag.get_text(strip=True)) if winner_tag else None

                if winner:
                    data.append({"Year": year, "Name": winner, "SAG": "Won"})

                # Remaining nominees are in a nested <ul>
                nested_ul = first_li.find("ul")
                if nested_ul:
                    for li in nested_ul.find_all("li"):
                        nominee = clean_name(li.get_text())
                        if nominee != winner:
                            data.append({"Year": year, "Name": nominee, "SAG": "Lost"})
                break

    # Use older structure (1995–2020): header rows with <tr>/<th>/<td>
    else:
        for row in soup.find_all("tr"):
            header = row.find_all("th")
            if len(header) == 2 and category in header[1].get_text():
                next_row = row.find_next_sibling("tr")
                if not next_row:
                    break

                tds = next_row.find_all("td")
                if not tds:
                    continue

                female_td = tds[1] if len(tds) > 1 else tds[0]
                winner_tag = female_td.find("b")
                winner = clean_name(winner_tag.get_text(strip=True)) if winner_tag else None

                if winner:
                    data.append({"Year": year, "Name": winner, "SAG": "Won"})

                nominees_list = female_td.find_all("li")
                for li in nominees_list:
                    nominee = clean_name(li.get_text(strip=True))
                    if nominee != winner:
                        data.append({"Year": year, "Name": nominee, "SAG": "Lost"})
                break

    return data

# Combine all years into a single DataFrame
all_data = []

# Choose category
categories = ["Outstanding Performance by a Male Actor in a Leading Role",
              "Outstanding Performance by a Female Actor in a Leading Role",
              "Outstanding Performance by a Male Actor in a Supporting Role",
              "Outstanding Performance by a Female Actor in a Supporting Role"]
abbreviations = ["best_actor",
                "best_actress",
                "best_supp_actor",
                "best_supp_actress"]
category = categories[3]
abbreviation = abbreviations[3]

# Run scrape_sag() for each year
for year in range(1995, 2026):
    print(f"Scraping {year}")
    yearly_data = scrape_sag(year, category)
    if yearly_data:
        all_data.extend(yearly_data)

# Save output
df = pd.DataFrame(all_data)
output_path = f"/Users/rickytruong/Desktop/Oscar Predictor/Python for Webscraping/sag_{abbreviation}.csv"
df.to_csv(output_path, index=False)
print(f"Data saved to: {output_path}")