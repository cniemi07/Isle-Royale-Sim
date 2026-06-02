import requests
import pandas as pd
import sqlite3
import time

TOKEN = "hDqIlfPZJKLdLDwmDzTJrfGGPhjcipCK"
headers = {"token": TOKEN}

def fetch_winter_temps(year):
    """Fetch Jan-Mar minimum temperatures for a given year."""
    params = {
        "datasetid": "GHCND",
        "stationid": "GHCND:USW00094850",
        "datatypeid": "TMIN",
        "startdate": f"{year}-01-01",
        "enddate": f"{year}-03-31",
        "limit": 100,
        "units": "standard"
    }
    response = requests.get(
        "https://www.ncdc.noaa.gov/cdo-web/api/v2/data",
        headers=headers,
        params=params
    )
    if response.status_code != 200:
        print(f"  Error {response.status_code} for {year}")
        return None
    data = response.json()
    if 'results' not in data:
        print(f"  No data for {year}")
        return None
    df = pd.DataFrame(data['results'])
    return df['value'].mean()

def calc_wsi(avg_min_temp):
    """Convert average minimum temp to Winter Severity Index."""
    if avg_min_temp is None:
        return None
    wsi = 1.0 + max(0, (32 - avg_min_temp) / 32)
    return round(min(wsi, 2.0), 3)

# Fetch data for all years 1980-2024
results = []
years = range(1980, 2025)

print(f"Fetching winter data for {len(years)} years...")
print("(This will take about 2 minutes due to API rate limits)\n")

for year in years:
    print(f"Fetching {year}...", end=" ")
    avg_temp = fetch_winter_temps(year)
    wsi = calc_wsi(avg_temp)
    results.append({
        'year': year,
        'avg_min_temp': avg_temp,
        'wsi': wsi
    })
    if avg_temp is not None:
        print(f"avg min temp: {avg_temp:.1f}°F, WSI: {wsi}")
    time.sleep(0.3)  # respect rate limits

# Save to database
df_wsi = pd.DataFrame(results)
conn = sqlite3.connect('db/isle_royale.db')
df_wsi.to_sql('winter_severity', conn, if_exists='replace', index=False)
conn.close()

print(f"\nDone. Saved {len(df_wsi)} years of winter severity data.")
print(df_wsi[['year', 'avg_min_temp', 'wsi']].to_string(index=False))