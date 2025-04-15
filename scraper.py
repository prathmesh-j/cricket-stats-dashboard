# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import os

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# --- Step 1: Batting Stats Page ---
batting_stats_url = "https://www.mscl.org/battingStats?season=2024&team=Huskies%20Cricket%20Club"
driver.get(batting_stats_url)

# Wait for the player profile links to load
wait = WebDriverWait(driver, 20)
player_links = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a[href*="/playerprofile/"]')))

# Extract player IDs and names
player_ids = {}
for link in player_links:
  href = link.get_attribute("href")
  name = link.text.strip()
  match = re.search(r"/playerprofile/([a-f0-9]+)", href)
  if match:
    player_ids[match.group(1)] = name

print(f"📝 Found {len(player_ids)} players.")

# Base profile URL template
base_url = "https://www.mscl.org/playerprofile/{}?statType={}&statDetails={}"

# --- Batting Scraper Function ---
def scrape_batting_data(player_id, player_name):
  url = base_url.format(player_id, "batting", "batting")
  driver.get(url)

  try:
    wait = WebDriverWait(driver, 30)
    table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'playerDetailedBattingStats')]")))

    if table:
      headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
      rows = table.find_elements(By.TAG_NAME, "tr")[1:]
      data = [[td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")] for row in rows]

      df = pd.DataFrame(data, columns=headers)
      df["Player Name"] = player_name
      df["Player ID"] = player_id
      df["Stat Type"] = "batting"

      if "Opposition" in df.columns:
        df["Opponent"] = df["Opposition"].str.extract(r'vs\s(.+)$')
      if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

      df["Runs"] = pd.to_numeric(df["Runs"], errors='coerce')
      df["Balls"] = pd.to_numeric(df["Balls"], errors='coerce')
      df["Is Not Out"] = df["Dismissal"].str.lower().eq("not out")
      df["Inns"] = df.groupby("Player Name")["Dismissal"].transform("count")
      df["NO"] = df.groupby("Player Name")["Is Not Out"].transform("sum")
      df["Dismissals"] = df["Inns"] - df["NO"]
      df["Ave"] = df.apply(lambda row: row["Runs"] / row["Dismissals"] if row["Dismissals"] > 0 else None, axis=1)
      df["SR"] = df.apply(lambda row: (row["Runs"] / row["Balls"]) * 100 if row["Balls"] > 0 else None, axis=1)

      df["Team"] = "Huskies Cricket Club"
      return df
    else:
      return pd.DataFrame()
  except Exception as e:
    print(f"[!] Error in batting for {player_name}: {e}")
    return pd.DataFrame()

# --- Bowling Scraper Function ---
def scrape_bowling_data(player_id, player_name):
  url = base_url.format(player_id, "bowling", "bowling")
  driver.get(url)

  try:
    wait = WebDriverWait(driver, 30)
    table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[contains(@id, 'playerDetailedBowlingStats')]")))

    if table:
      headers = [th.text for th in table.find_elements(By.TAG_NAME, "th")]
      rows = table.find_elements(By.TAG_NAME, "tr")[1:]
      data = [[td.text.strip() for td in row.find_elements(By.TAG_NAME, "td")] for row in rows]

      df = pd.DataFrame(data, columns=headers)
      df["Player Name"] = player_name
      df["Player ID"] = player_id
      df["Stat Type"] = "bowling"

      if "Opposition" in df.columns:
        df["Opponent"] = df["Opposition"].str.extract(r'vs\s(.+)$')
      if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

      numeric_columns = ["Overs", "Maidens", "Runs", "Wickets", "Economy", "Average", "Strike Rate"]
      for col in numeric_columns:
        if col in df.columns:
          df[col] = pd.to_numeric(df[col], errors='coerce')

      df["Team"] = "Huskies Cricket Club"
      return df
    else:
      return pd.DataFrame()
  except Exception as e:
    print(f"[!] Error in bowling for {player_name}: {e}")
    return pd.DataFrame()

# --- Main Scrape ---
batting_data = []
bowling_data = []

for pid, pname in player_ids.items():
  print(f"📊 Scraping batting for {pname}...")
  bdf = scrape_batting_data(pid, pname)
  if not bdf.empty:
    batting_data.append(bdf)

  print(f"🎯 Scraping bowling for {pname}...")
  bldf = scrape_bowling_data(pid, pname)
  if not bldf.empty:
    bowling_data.append(bldf)

  time.sleep(1.5)

driver.quit()

# --- Save CSVs ---
if batting_data:
  final_batting_df = pd.concat(batting_data, ignore_index=True)
  final_batting_df.to_csv("huskies_2024_batting_stats.csv", index=False)
  print("✅ Saved: huskies_2024_batting_stats.csv")
else:
  print("⚠️ No batting data found.")

if bowling_data:
  final_bowling_df = pd.concat(bowling_data, ignore_index=True)
  final_bowling_df.to_csv("huskies_2024_bowling_stats.csv", index=False)
  print("✅ Saved: huskies_2024_bowling_stats.csv")
else:
  print("⚠️ No bowling data found.")
