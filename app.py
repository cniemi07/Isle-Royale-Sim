import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import sys
sys.path.append('simulation')
from model import run_simulation

st.set_page_config(page_title="Isle Royale Wolf-Moose Simulator", page_icon="", layout="wide")

st.title("Isle Royale Wolf-Moose Population Simulator")
st.image("C:\\Users\\25nie\\isle-royal-sim\\.venv\\wolf.jpg",caption = "Isle Royale Wolves",use_container_width = True)
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
@st.cache_data
def load_fitted_params():
    try:
        conn = sqlite3.connect('db/isle_royale.db')
        result = pd.read_sql('SELECT * FROM fitted_params LIMIT 1', conn)
        conn.close()
        if len(result) > 0:
            return {
                'birth_rate': float(result['birth_rate'].iloc[0]),
                'predation_rate': float(result['predation_rate'].iloc[0]),
                'efficiency': float(result['efficiency'].iloc[0]),
                'death_rate': float(result['death_rate'].iloc[0])
            }
    except:
        pass
    return {
        'birth_rate': 0.4,
        'predation_rate': 0.01,
        'efficiency': 0.075,
        'death_rate': 0.5
    }

params = load_fitted_params()

current_wsi = load_wsi()
df = load_historical()

st.sidebar.header("Simulation Parameters")
initial_moose = st.sidebar.slider("Initial Moose Population", 100, 2000, 664, step=50)
initial_wolves = st.sidebar.slider("Initial Wolf Population", 1, 60, 50)
birth_rate = st.sidebar.slider("Moose Birth Rate", 0.1, 1.0,
                                params['birth_rate'], step=0.01)
predation_rate = st.sidebar.slider("Predation Rate", 0.001, 0.05,
                                    params['predation_rate'], step=0.001, format="%.4f")
efficiency = st.sidebar.slider("Wolf Reproductive Efficiency", 0.01, 0.2,
                                params['efficiency'], step=0.005)
death_rate = st.sidebar.slider("Wolf Death Rate", 0.1, 1.0,
                                params['death_rate'], step=0.01)
st.sidebar.caption("Default parameters fitted against 44 years of real field data using scipy.optimize")
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
st.subheader("Winter Severity Index (1980–2024)")
st.markdown("Derived from NOAA daily minimum temperature data at Houghton County Airport. Higher values indicate harsher winters — a key driver of moose vulnerability and wolf hunting success.")

@st.cache_data
def load_wsi_history():
    conn = sqlite3.connect('db/isle_royale.db')
    df = pd.read_sql('SELECT * FROM winter_severity ORDER BY year', conn)
    conn.close()
    return df

wsi_df = load_wsi_history()

fig4, ax = plt.subplots(figsize=(12, 3.5))
fig4.patch.set_facecolor(bg_color)
ax.set_facecolor(ax_color)
ax.tick_params(colors=text_color)
ax.xaxis.label.set_color(text_color)
ax.yaxis.label.set_color(text_color)
for spine in ax.spines.values():
    spine.set_edgecolor(grid_color)

ax.fill_between(wsi_df['year'], wsi_df['wsi'], alpha=0.3, color='#5BA4CF')
ax.plot(wsi_df['year'], wsi_df['wsi'], color='#5BA4CF', linewidth=2)
ax.axhline(y=wsi_df['wsi'].mean(), color='#AAAAAA', linewidth=1,
           linestyle='--', alpha=0.6, label=f"Mean WSI: {wsi_df['wsi'].mean():.3f}")

notable = [(2014, 2.000, "2014: Record cold"), (2024, 1.455, "2024: Mildest winter")]
for year, wsi_val, label in notable:
    ax.annotate(label,
        xy=(year, wsi_val),
        xytext=(5, 5),
        textcoords='offset points',
        fontsize=7, color='#AAAAAA',
        va='bottom'
    )

ax.set_ylabel('Winter Severity Index', color=text_color)
ax.set_xlabel('Year', color=text_color)
ax.set_ylim(1.0, 2.1)
ax.grid(True, alpha=0.15, color=grid_color)
ax.legend(facecolor=ax_color, labelcolor=text_color, fontsize=8)

plt.tight_layout()
st.pyplot(fig4)

w1, w2, w3 = st.columns(3)
w1.metric("Harshest Winter", f"{wsi_df.loc[wsi_df['wsi'].idxmax(), 'year']:.0f}",
          f"WSI {wsi_df['wsi'].max():.3f}")
w2.metric("Mildest Winter", f"{wsi_df.loc[wsi_df['wsi'].idxmin(), 'year']:.0f}",
          f"WSI {wsi_df['wsi'].min():.3f}")
w3.metric("45-Year Average", f"WSI {wsi_df['wsi'].mean():.3f}", "")
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