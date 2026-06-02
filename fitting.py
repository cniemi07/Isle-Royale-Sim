import pandas as pd
import sqlite3
import numpy as np
from scipy.optimize import minimize
import sys
sys.path.append('simulation')
from model import run_simulation

# Load real historical data
conn = sqlite3.connect('db/isle_royale.db')
df = pd.read_sql('SELECT * FROM population ORDER BY year', conn)
conn.close()

# Drop years with missing data
df_clean = df.dropna(subset=['wolves', 'moose']).reset_index(drop=True)
print(f"Fitting against {len(df_clean)} years of complete data")
print(f"Years: {df_clean['year'].min()} to {df_clean['year'].max()}")

def error(params):
    birth_rate, predation_rate, efficiency, death_rate = params

    # Keep parameters in valid range
    if any(p <= 0 for p in params):
        return 1e10

    years = len(df_clean)
    try:
        t, sim_moose, sim_wolves = run_simulation(
            years=years,
            initial_moose=df_clean['moose'].iloc[0],
            initial_wolves=df_clean['wolves'].iloc[0],
            birth_rate=birth_rate,
            predation_rate=predation_rate,
            efficiency=efficiency,
            death_rate=death_rate
        )
    except:
        return 1e10

    # Sample at annual intervals
    annual_idx = np.linspace(0, len(t) - 1, years, dtype=int)
    sim_moose_annual = sim_moose[annual_idx]
    sim_wolves_annual = sim_wolves[annual_idx]

    # Normalize each species by its mean to weight them equally
    moose_mean = df_clean['moose'].mean()
    wolf_mean = df_clean['wolves'].mean()

    moose_error = np.mean(((sim_moose_annual - df_clean['moose'].values) / moose_mean) ** 2)
    wolf_error = np.mean(((sim_wolves_annual - df_clean['wolves'].values) / wolf_mean) ** 2)

    return moose_error + wolf_error

# Starting guess
x0 = [0.4, 0.01, 0.075, 0.5]
bounds = [(0.05, 1.5), (0.0001, 0.1), (0.01, 0.5), (0.05, 2.0)]

print("\nFitting parameters — this may take a moment...")
result = minimize(error, x0, bounds=bounds, method='L-BFGS-B')

birth_rate, predation_rate, efficiency, death_rate = result.x

print(f"\n=== Best Parameters Found ===")
print(f"Birth rate:          {birth_rate:.4f}")
print(f"Predation rate:      {predation_rate:.5f}")
print(f"Efficiency:          {efficiency:.4f}")
print(f"Death rate:          {death_rate:.4f}")
print(f"Total error:         {result.fun:.4f}")
print(f"Optimization success: {result.success}")

# Save to database
conn = sqlite3.connect('db/isle_royale.db')
conn.execute('''CREATE TABLE IF NOT EXISTS fitted_params
                (birth_rate REAL, predation_rate REAL, 
                 efficiency REAL, death_rate REAL, error REAL)''')
conn.execute('DELETE FROM fitted_params')
conn.execute('INSERT INTO fitted_params VALUES (?, ?, ?, ?, ?)',
             (birth_rate, predation_rate, efficiency, death_rate, result.fun))
conn.commit()
conn.close()
print("\nParameters saved to database")