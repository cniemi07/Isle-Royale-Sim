import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import sys
sys.path.append('simulation')
from model import run_simulation

st.set_page_config(page_title="Isle Royale Wolf-Moose Simulator", page_icon="", layout="wide")

st.title("Isle Royale Wolf-Moose Population Simulator")
st.markdown("Adjust the parameters to run your own scenarios.")

@st.cache_data
def load_historical():
    conn = sqlite3.connect('db/isle_royale.db')
    df = pd.read_sql('SELECT * FROM population ORDER BY year', conn)
    conn.close()
    return df
@st.cache_data
def load_wsi():
    try:
        conn = sqlite3.connect('db/isle_royale.db')
        result = pd.read_sql('SELECT wsi FROM winter_severity ORDER BY year DESC LIMIT 1', conn)
        conn.close()
        if len(result) > 0:
            return float(result['wsi'].iloc[0])
    except:
        pass
    return 1.0

current_wsi = load_wsi()
df = load_historical()

st.sidebar.header("Simulation Parameters")
initial_moose = st.sidebar.slider("Initial Moose Population", 100, 2000, 664, step=50)
initial_wolves = st.sidebar.slider("Initial Wolf Population", 1, 60, 50)
birth_rate = st.sidebar.slider("Moose Birth Rate", 0.1, 1.0, 0.4, step=0.01)
predation_rate = st.sidebar.slider("Predation Rate", 0.001, 0.05, 0.01, step=0.001, format="%.3f")
efficiency = st.sidebar.slider("Wolf Reproductive Efficiency", 0.01, 0.2, 0.075, step=0.005)
death_rate = st.sidebar.slider("Wolf Death Rate", 0.1, 1.0, 0.5, step=0.01)
winter_severity = st.sidebar.slider("Winter Severity Multiplier", 0.5, 2.0, current_wsi, step=0.1)
st.sidebar.caption(f"Current value based on live NOAA data (2024 winter avg min temp: 17.5°F)")
sim_years = st.sidebar.slider("Simulation Years", 10, 100, 46)

t, moose, wolves = run_simulation(
    years=sim_years,
    initial_moose=initial_moose,
    initial_wolves=initial_wolves,
    birth_rate=birth_rate,
    predation_rate=predation_rate,
    efficiency=efficiency,
    death_rate=death_rate,
    winter_severity=winter_severity
)

col1, col2 = st.columns(2)

st.subheader("Historical Data vs Simulation (1980–2026)")

events = [
    (1995, "Record moose (2,400)", "moose"),
    (1997, "Moose crash (500)",    "moose"),
    (2012, "Wolf crisis (9)",      "wolf"),
    (2018, "Reintroduction begins","wolf"),
    (2026, "37 wolves / 524 moose","wolf"),
]

bg_color = "#0F1117"
ax_color = "#1A1A2E"
text_color = "#FAFAFA"
grid_color = "#2A2A3E"

fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
fig1.patch.set_facecolor(bg_color)

for ax in [ax1, ax2]:
    ax.set_facecolor(ax_color)
    ax.tick_params(colors=text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    for spine in ax.spines.values():
        spine.set_edgecolor(grid_color)

# Historical data
ax1.plot(df['year'], df['wolves'], color='#5BA4CF', linewidth=2,
         marker='o', markersize=3, zorder=3, label='Historical')
ax2.plot(df['year'], df['moose'], color='#C97B4B', linewidth=2,
         marker='o', markersize=3, zorder=3, label='Historical')

# Simulation overlay — map simulation years onto historical year range
sim_years_mapped = df['year'].min() + t
ax1.plot(sim_years_mapped, wolves, color='#A8D8A8', linewidth=1.5,
         linestyle='--', alpha=0.8, zorder=2, label='Simulation')
ax2.plot(sim_years_mapped, moose, color='#F4C47E', linewidth=1.5,
         linestyle='--', alpha=0.8, zorder=2, label='Simulation')

ax1.set_ylabel('Wolf Population', color=text_color)
ax1.grid(True, alpha=0.15, color=grid_color)
ax1.legend(facecolor=ax_color, labelcolor=text_color, fontsize=8)

ax2.set_ylabel('Moose Population', color=text_color)
ax2.set_xlabel('Year', color=text_color)
ax2.grid(True, alpha=0.15, color=grid_color)
ax2.legend(facecolor=ax_color, labelcolor=text_color, fontsize=8)

for year, label, chart in events:
    for ax in [ax1, ax2]:
        ax.axvline(x=year, color='#FFFFFF', alpha=0.1,
                  linewidth=1, linestyle='--', zorder=2)

    if chart == "wolf":
        y_val = df.loc[df['year'] == year, 'wolves'].values
        if len(y_val) > 0 and not pd.isna(y_val[0]):
            ax1.annotate(label,
                xy=(year, y_val[0]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=7, color='#AAAAAA',
                va='bottom'
            )
    else:
        y_val = df.loc[df['year'] == year, 'moose'].values
        if len(y_val) > 0 and not pd.isna(y_val[0]):
            ax2.annotate(label,
                xy=(year, y_val[0]),
                xytext=(5, 5),
                textcoords='offset points',
                fontsize=7, color='#AAAAAA',
                va='bottom'
            )

plt.tight_layout()
st.pyplot(fig1)

st.subheader("Phase Space — Predator-Prey Spiral")
st.markdown("A stable ecosystem spirals inward toward equilibrium. Compare the shape to what actually happened on Isle Royale.")
fig3, ax = plt.subplots(figsize=(6, 5))
ax.plot(moose, wolves, color='purple', alpha=0.7, linewidth=1.5)
ax.scatter([moose[0]], [wolves[0]], color='green', s=100, zorder=5, label='Start')
ax.scatter([moose[-1]], [wolves[-1]], color='red', s=100, zorder=5, label='End')
ax.set_xlabel('Moose Population')
ax.set_ylabel('Wolf Population')
ax.legend()
ax.grid(True, alpha=0.3)
st.pyplot(fig3)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Peak Moose Population", f"{int(max(moose)):,}")
c2.metric("Peak Wolf Population", f"{int(max(wolves)):,}")
c3.metric("Current Moose Population", f"{int(moose[-1]):,}")
c4.metric("Current Wolf Population", f"{int(wolves[-1]):,}")

st.subheader("Historical Population Data")
st.markdown("Full dataset from Isle Royale Wolf-Moose Project annual reports (1980–2026). Gaps indicate canceled field studies.")

display_df = df[['year', 'wolves', 'moose', 'notes']].copy()
display_df.columns = ['Year', 'Wolves', 'Moose', 'Notes']
display_df['Year'] = display_df['Year'].astype(int)
display_df['Wolves'] = display_df['Wolves'].apply(lambda x: int(x) if pd.notna(x) else '—')
display_df['Moose'] = display_df['Moose'].apply(lambda x: int(x) if pd.notna(x) else '—')
display_df['Notes'] = display_df['Notes'].fillna('')

st.dataframe(
    display_df,
    use_container_width=True,
    height=400,
    hide_index=True
)

st.caption("Data source: Isle Royale Wolf-Moose Project — isleroyalewolf.org")