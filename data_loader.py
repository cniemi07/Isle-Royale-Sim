import pandas as pd
import sqlite3

# Load the CSV
df = pd.read_csv('data/isle_royale_population.csv')

print("=== Raw Data ===")
print(df.head(10))
print(f"\nShape: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"Years: {df['year'].min()} to {df['year'].max()}")
print(f"\nMissing values:\n{df.isnull().sum()}")

# Connect to SQLite and write the data
conn = sqlite3.connect('db/isle_royale.db')
df.to_sql('population', conn, if_exists='replace', index=False)

# Verify it worked
result = pd.read_sql('SELECT * FROM population LIMIT 5', conn)
print("\n=== Database Verification ===")
print(result)

total = pd.read_sql('SELECT COUNT(*) as total_rows FROM population', conn)
print(f"\nTotal rows in database: {total['total_rows'][0]}")

conn.close()
print("\nDone — database created at db/isle_royale.db")