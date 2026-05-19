import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

conn = sqlite3.connect('db/isle_royale.db')
df = pd.read_sql('SELECT * FROM population ORDER BY year', conn)
conn.close()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 12))

ax1.plot(df['year'], df['wolves'], color='forestgreen', linewidth=2, marker='o', markersize=4)
ax1.set_ylabel('Wolf Population')
ax1.set_title('Isle Royale Wolf & Moose Populations (1980-2026)')
ax1.grid(True, alpha=0.3)

ax2.plot(df['year'], df['moose'], color='chocolate', linewidth=2, marker='o', markersize=4)
ax2.set_ylabel('Moose Population')
ax2.set_xlabel('Year')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('data/historical_populations.png', dpi=150)
plt.show()
print("Chart saved to data/historical_populations.png")