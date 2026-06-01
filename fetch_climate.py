import requests
import pandas as pd
import sqlite3

TOKEN = "hDqIlfPZJKLdLDwmDzTJrfGGPhjcipCK"

headers = {"token": TOKEN}

params = {
    "datasetid": "GHCND",
    "stationid": "GHCND:USW00094850",  # Houghton County Airport — closest to Isle Royale
    "datatypeid": "TMIN",
    "startdate": "2024-01-01",
    "enddate": "2024-03-31",
    "limit": 100,
    "units": "standard"
}

response = requests.get(
    "https://www.ncdc.noaa.gov/cdo-web/api/v2/data",
    headers=headers,
    params=params
)

print(f"Status: {response.status_code}")
data = response.json()

if 'results' in data:
    df = pd.DataFrame(data['results'])
    print(df.head())
    print(f"Fetched {len(df)} records")

    # Save to database
    conn = sqlite3.connect('db/isle_royale.db')
    df.to_sql('climate', conn, if_exists='replace', index=False)
    conn.close()
    print("Saved to database")
else:
    print("Error:", data)

# Calculate a simple Winter Severity Index
# WSI = average of daily minimum temps for Jan-Mar, inverted
# Lower temps = harsher winter = higher severity
conn = sqlite3.connect('db/isle_royale.db')
climate_df = pd.read_sql('SELECT * FROM climate', conn)

avg_min_temp = climate_df['value'].mean()

# Normalize: 32F = mild (severity 1.0), 0F = severe (severity 2.0)
# Linear scale between those bounds
wsi = 1.0 + max(0, (32 - avg_min_temp) / 32)
wsi = round(min(wsi, 2.0), 2)  # cap at 2.0

print(f"\nAverage minimum temp (Jan-Mar 2024): {avg_min_temp:.1f}°F")
print(f"Calculated Winter Severity Index: {wsi}")

# Save WSI to database
import sqlite3 as sl
conn2 = sl.connect('db/isle_royale.db')
conn2.execute('''CREATE TABLE IF NOT EXISTS winter_severity 
                 (year INTEGER, wsi REAL, avg_min_temp REAL)''')
conn2.execute('DELETE FROM winter_severity WHERE year = 2024')
conn2.execute('INSERT INTO winter_severity VALUES (?, ?, ?)',
              (2024, wsi, avg_min_temp))
conn2.commit()
conn2.close()
print("WSI saved to database")