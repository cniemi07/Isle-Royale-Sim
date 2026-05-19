import sys
sys.path.append('simulation')
from model import run_simulation
import matplotlib.pyplot as plt

t, moose, wolves = run_simulation(
    years=46,
    initial_moose=664,
    initial_wolves=50
)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

ax1.plot(t, wolves, color='steelblue', linewidth=2)
ax1.set_ylabel('Wolf Population')
ax1.set_title('Isle Royale Simulation — Starting from 1980 conditions')
ax1.grid(True, alpha=0.3)

ax2.plot(t, moose, color='sienna', linewidth=2)
ax2.set_ylabel('Moose Population')
ax2.set_xlabel('Years from 1980')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print(f"Final wolves: {wolves[-1]:.0f}")
print(f"Final moose: {moose[-1]:.0f}")