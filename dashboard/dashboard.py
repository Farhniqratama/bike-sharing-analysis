import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path   # ✅ tambahan penting untuk path yang stabil

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

@st.cache_data
def load_data():
    # Pastikan path relatif aman baik di lokal maupun di Streamlit Cloud
    base_dir = Path(__file__).resolve().parent      # .../dashboard
    data_dir = (base_dir / ".." / "data").resolve() # .../data
    day = pd.read_csv(data_dir / "day.csv")
    hour = pd.read_csv(data_dir / "hour.csv")
    return day, hour

day, hour = load_data()

st.title("🚲 Bike Sharing — Analysis Dashboard")
st.write("Explore patterns in bike rental demand using daily and hourly datasets.")

# Sidebar filters
season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
day['season_name'] = day['season'].map(season_map)
hour['season_name'] = hour['season'].map(season_map)

st.sidebar.header("Filters")
season_sel = st.sidebar.multiselect(
    "Season",
    list(season_map.values()),
    default=list(season_map.values())
)
workingday_sel = st.sidebar.selectbox(
    "Working Day",
    ["All", "Working Day Only", "Weekend/Holiday"]
)

def apply_filters(df):
    df = df[df['season_name'].isin(season_sel)]
    if workingday_sel == "Working Day Only":
        df = df[df['workingday'] == 1]
    elif workingday_sel == "Weekend/Holiday":
        df = df[df['workingday'] == 0]
    return df

day_f = apply_filters(day.copy())
hour_f = apply_filters(hour.copy())

# KPI cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Rentals (daily)", int(day_f["cnt"].sum()))
col2.metric("Avg Rentals / Day", round(day_f["cnt"].mean(), 2))
col3.metric("Max Rentals / Day", int(day_f["cnt"].max()))
col4.metric("Records", len(day_f))

# Chart 1: Hourly pattern
st.subheader("Hourly Demand Pattern")
hourly = hour_f.groupby('hr', as_index=False)['cnt'].mean()
fig1, ax1 = plt.subplots()
ax1.plot(hourly['hr'], hourly['cnt'])
ax1.set_xlabel("Hour")
ax1.set_ylabel("Avg Rentals")
ax1.set_title("Average Rentals by Hour")
st.pyplot(fig1)

# Chart 2: Demand by Season (Daily)
st.subheader("Daily Demand by Season")
season_daily = (
    day_f.groupby('season_name', as_index=False)['cnt']
    .mean()
    .sort_values('cnt', ascending=False)
)
fig2, ax2 = plt.subplots()
ax2.bar(season_daily['season_name'], season_daily['cnt'])
ax2.set_xlabel("Season")
ax2.set_ylabel("Average Daily Rentals")
ax2.set_title("Average Daily Rentals by Season")
st.pyplot(fig2)

# Chart 3: Correlations (Daily)
st.subheader("Correlation with Total Rentals (Daily)")
corr_cols = ['temp', 'atemp', 'hum', 'windspeed', 'casual', 'registered', 'cnt']
corr = day_f[corr_cols].corr(numeric_only=True)['cnt'].sort_values(ascending=False)
st.dataframe(corr.to_frame("corr_with_cnt"))