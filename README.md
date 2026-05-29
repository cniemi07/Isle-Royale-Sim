\# Isle Royale Wolf-Moose Population Simulator


LIVE DEMO 
https://isle-royale-sim.streamlit.app
**IN PROGRESS**

An interactive ecological simulation built on 45+ years of real field data

from the Isle Royale Wolf-Moose Project. Models predator-prey population 

dynamics using Lotka-Volterra differential equations with environmental 

covariates including winter severity and ice cover data.



\## What it does

\- Loads historical wolf and moose population data (1959-present) into a 

&#x20; SQLite database

\- Simulates population dynamics using Lotka-Volterra ODEs solved with SciPy

\- Pulls live climate data from the NOAA API to feed current environmental 

&#x20; variables into the model

\- Displays an interactive dashboard with real-time parameter sliders



\## Tech Stack

Python, Pandas, NumPy, SciPy, SQLite, Streamlit, NOAA API



\## Status

🔧 In active development — simulation engine and data layer in progress



\## Background

Isle Royale National Park hosts one of the longest-running predator-prey 

studies in the world. I've followed this research since middle school and 

built this project to explore the dynamics computationally — specifically 

how predator reintroduction and environmental variables like winter severity 

drive long-term population stability.



\## Run Locally

```bash

git clone https://github.com/cniemi07/isle-royale-sim.git

cd isle-royale-sim

pip install -r requirements.txt

streamlit run app.py

```



\## Data Sources

\- Population data: Isle Royale Wolf-Moose Project annual reports 

&#x20; (isleroyalewolf.org)

\- Climate data: NOAA Climate Data Online API

