import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://en.wikipedia.org/wiki/Golden_Globe_Award_for_Best_Supporting_Actress_%E2%80%93_Motion_Picture"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Locate the 2020s header and following table
header = soup.find("h3", id="2020s")
if not header:
    raise Exception("Could not find the 2020s header.")

table = header.find_next("table", class_="wikitable")
if not table:
    raise Exception("Could not find the table after the 2020s header.")

rows = table.find_all("tr")
data = []
current_year = None

for row in rows[1:]:
    cells = row.find_all(["th", "td"])
    if not cells:
        continue

    # Check for a new year block
    first_cell = cells[0]
    if first_cell.name == "th" and first_cell.get("rowspan"):
        try:
            current_year = int(first_cell.get_text(strip=True)) + 1
        except ValueError:
            continue
        cells = cells[1:]

    # Extract nominee info
    if len(cells) >= 3:
        name_cell = cells[0]
        is_winner = any("#B0C4DE" in cell.get("style", "") for cell in cells[:3])
        name = name_cell.get_text(strip=True)

        data.append({
            "Year": current_year,
            "Name": name,
            "Golden_Globe": "Won" if is_winner else "Lost"
        })

# Create data frame for 2021–2025
df = pd.DataFrame(data)
df = df[df["Year"].between(2021, 2025)]

# Save output
output_path = f"/Users/rickytruong/Desktop/Oscar Predictor/Python for Webscraping/globes_best_supp_actress_2021_2025.csv"
df.to_csv(output_path, index=False)
print(f"Data saved to: {output_path}")