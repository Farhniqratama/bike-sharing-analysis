import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# --- Safety: kolom wajib agar grafik & KPI tidak error
REQUIRED_DAY_COLS = {
    "season", "workingday", "temp", "atemp", "hum",
    "windspeed", "casual", "registered", "cnt"
}
REQUIRED_HOUR_COLS = REQUIRED_DAY_COLS.union({"hr"})

@st.cache_data
def load_data():
    """
    Cari data di beberapa lokasi agar aman untuk lokal & Streamlit Cloud.
    """
    base_dir = Path(__file__).resolve().parent         # .../dashboard
    data_dir = (base_dir / ".." / "data").resolve()    # .../data
    candidates = [data_dir, Path.cwd() / "data"]

    last_err = None
    for d in candidates:
        try:
            day_df = pd.read_csv(d / "day.csv")
            hour_df = pd.read_csv(d / "hour.csv")
            return day_df, hour_df
        except Exception as e:
            last_err = e
            continue

    raise FileNotFoundError(
        f"Tidak dapat memuat data. Pastikan berkas 'data/day.csv' dan 'data/hour.csv' tersedia. "
        f"Error terakhir: {last_err}"
    )

# --- Load & validasi struktur kolom
try:
    day, hour = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

missing_day = REQUIRED_DAY_COLS - set(day.columns)
missing_hour = REQUIRED_HOUR_COLS - set(hour.columns)
if missing_day or missing_hour:
    st.error(
        f"Kolom wajib hilang. day kurang: {sorted(list(missing_day))}; "
        f"hour kurang: {sorted(list(missing_hour))}"
    )
    st.stop()

# --- Feature engineering ringan
season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
day["season_name"] = day["season"].map(season_map)
hour["season_name"] = hour["season"].map(season_map)

season_order = ["Spring", "Summer", "Fall", "Winter"]
day["season_name"] = pd.Categorical(day["season_name"], categories=season_order, ordered=True)
hour["season_name"] = pd.Categorical(hour["season_name"], categories=season_order, ordered=True)

weekday_map = {0:"Sun", 1:"Mon", 2:"Tue", 3:"Wed", 4:"Thu", 5:"Fri", 6:"Sat"}
if "weekday" in day.columns:
    day["weekday_name"] = day["weekday"].map(weekday_map)

# --- UI
st.title("🚲 Bike Sharing — Analysis Dashboard")
st.write("Explore patterns in bike rental demand using daily and hourly datasets.")

with st.sidebar:
    st.header("Filters")
    season_sel = st.multiselect("Season", season_order, default=season_order)
    workingday_sel = st.selectbox(
        "Working Day", ["All", "Working Day Only", "Weekend/Holiday"], index=0
    )

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if "season_name" in df.columns:
        df = df[df["season_name"].isin(season_sel)]
    if workingday_sel == "Working Day Only" and "workingday" in df.columns:
        df = df[df["workingday"] == 1]
    elif workingday_sel == "Weekend/Holiday" and "workingday" in df.columns:
        df = df[df["workingday"] == 0]
    return df

day_f = apply_filters(day.copy())
hour_f = apply_filters(hour.copy())

if day_f.empty or hour_f.empty:
    st.warning("⚠️ Filter saat ini menghasilkan dataset kosong. Ubah filter di sidebar.")
    st.stop()

# --- KPI
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Rentals (daily)", int(day_f["cnt"].sum()))
c2.metric("Avg Rentals / Day", round(float(day_f["cnt"].mean()), 2))
c3.metric("Max Rentals / Day", int(day_f["cnt"].max()))
c4.metric("Records", int(len(day_f)))

# --- Chart 1: Hourly demand
st.subheader("Hourly Demand Pattern")
hourly = hour_f.groupby("hr", as_index=False)["cnt"].mean().sort_values("hr")
fig1, ax1 = plt.subplots()
ax1.plot(hourly["hr"], hourly["cnt"])
ax1.set_xlabel("Hour (0–23)")
ax1.set_ylabel("Avg Rentals")
ax1.set_title("Average Rentals by Hour")
ax1.set_ylim(bottom=0)  # integritas visual
st.pyplot(fig1)

# --- Chart 2: Daily by season
st.subheader("Daily Demand by Season")
season_daily = (
    day_f.groupby("season_name", as_index=False)["cnt"]
        .mean().sort_values("cnt", ascending=False)
)
fig2, ax2 = plt.subplots()
ax2.bar(season_daily["season_name"].astype(str), season_daily["cnt"])
ax2.set_xlabel("Season")
ax2.set_ylabel("Average Daily Rentals")
ax2.set_title("Average Daily Rentals by Season")
ax2.set_ylim(bottom=0)
st.pyplot(fig2)

# --- Chart 3: Korelasi
st.subheader("Correlation with Total Rentals (Daily)")
corr_cols = ["temp", "atemp", "hum", "windspeed", "casual", "registered", "cnt"]
available = [c for c in corr_cols if c in day_f.columns]
if "cnt" not in available:
    st.error("Kolom 'cnt' tidak ditemukan pada data harian terfilter.")
else:
    corr_series = day_f[available].corr(numeric_only=True)["cnt"].sort_values(ascending=False)
    st.dataframe(corr_series.to_frame("corr_with_cnt"))

# --- Download data terfilter
st.divider()
st.caption("Download data terfilter:")
col_dl1, col_dl2 = st.columns(2)
with col_dl1:
    st.download_button(
        label="Download Daily (CSV)",
        data=day_f.to_csv(index=False).encode("utf-8"),
        file_name="daily_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_dl2:
    st.download_button(
        label="Download Hourly (CSV)",
        data=hour_f.to_csv(index=False).encode("utf-8"),
        file_name="hourly_filtered.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption("Notebook & dashboard selaras: hourly pattern, daily by season, korelasi. Sumbu Y mulai dari 0 untuk integritas visual.")