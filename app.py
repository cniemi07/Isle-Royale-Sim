import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import sys
sys.path.append('simulation')
from model import run_simulation

st.set_page_config(page_title="Isle Royale Wolf-Moose Simulator", page_icon="🐺", layout="wide")

st.title("🐺 Isle Royale Wolf-Moose Population Simulator")
st.markdown("60+ years of real field data meets ecological modeling. Adjust the parameters to run your own scenarios.")

@st.cache_data
def load_historical():
    conn = sqlite3.connect('db/isle_royale.db')
    df = pd.read_sql('SELECT * FROM population ORDER BY year', conn)
    conn.close()
    return df

df = load_historical()

st.sidebar.header("Simulation Parameters")
initial_moose = st.sidebar.slider("Initial Moose Population", 100, 2000, 664, step=50)
initial_wolves = st.sidebar.slider("Initial Wolf Population", 1, 60, 50)
birth_rate = st.sidebar.slider("Moose Birth Rate", 0.1, 1.0, 0.4, step=0.01)
predation_rate = st.sidebar.slider("Predation Rate", 0.001, 0.05, 0.01, step=0.001, format="%.3f")
efficiency = st.sidebar.slider("Wolf Reproductive Efficiency", 0.01, 0.2, 0.075, step=0.005)
death_rate = st.sidebar.slider("Wolf Death Rate", 0.1, 1.0, 0.5, step=0.01)
winter_severity = st.sidebar.slider("Winter Severity Multiplier", 0.5, 2.0, 1.0, step=0.1)
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

with col1:
    st.subheader("📊 Historical Data (1980–2026)")
    fig1, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))
    ax1.plot(df['year'], df['wolves'], color='steelblue', linewidth=2, marker='o', markersize=3)
    ax1.set_ylabel('Wolves')
    ax1.grid(True, alpha=0.3)
    ax2.plot(df['year'], df['moose'], color='sienna', linewidth=2, marker='o', markersize=3)
    ax2.set_ylabel('Moose')
    ax2.set_xlabel('Year')
    ax2.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig1)

with col2:
    st.subheader("🔮 Your Simulation")
    fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(8, 6))
    ax3.plot(t, wolves, color='steelblue', linewidth=2)
    ax3.set_ylabel('Wolves')
    ax3.grid(True, alpha=0.3)
    ax4.plot(t, moose, color='sienna', linewidth=2)
    ax4.set_ylabel('Moose')
    ax4.set_xlabel('Years from start')
    ax4.grid(True, alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig2)

st.subheader("🔄 Phase Space — Predator-Prey Spiral")
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
c1.metric("Peak Moose", f"{int(max(moose)):,}")
c2.metric("Peak Wolves", f"{int(max(wolves)):,}")
c3.metric("Final Moose", f"{int(moose[-1]):,}")
c4.metric("Final Wolves", f"{int(wolves[-1]):,}")