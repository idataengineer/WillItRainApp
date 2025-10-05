import streamlit as st
import datetime as dt
import pandas as pd
import os
import requests
from requests.auth import HTTPBasicAuth
from io import StringIO

# --- Load credentials from environment variables ---
username = os.getenv("METEO_USERNAME")
password = os.getenv("METEO_PASSWORD")

if not username or not password:
    st.error("Meteomatics credentials not found. Set METEO_USERNAME and METEO_PASSWORD as environment variables.")
    st.stop()

# --- Streamlit App ---
st.title("🌦️ Will It Rain On My Parade?")
st.markdown("Enter your event location and date to see the precipitation forecast.")

# Input: location and date
location = st.text_input("Enter location (lat,lon)", "52.5200,13.4050")  # default: Berlin
event_date = st.date_input("Pick a date", dt.date.today())

if st.button("Check Forecast"):
    try:
        # --- Validate input ---
        parts = location.split(",")
        if len(parts) != 2:
            st.error("Please enter location as lat,lon — e.g., 52.52,13.41")
            st.stop()
        lat, lon = map(float, map(str.strip, parts))

        # --- Prepare API request ---
        date_str = event_date.strftime("%Y-%m-%d")
        url = f"https://api.meteomatics.com/{date_str}T00:00:00Z--{date_str}T23:00:00Z:PT1H/precip_1h:mm/{lat},{lon}/csv"

        # --- Fetch data ---
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        if response.status_code != 200:
            st.error(f"Error fetching data: {response.text}")
        else:
            df = pd.read_csv(StringIO(response.text), sep=";")

            # --- Dynamic column handling & renaming for safe plotting ---
            st.write("Columns returned:", df.columns.tolist())  # debug: remove after confirming
            df.rename(columns={df.columns[0]: "datetime", df.columns[1]: "precip_mm"}, inplace=True)

            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            # --- Display chart ---
            st.subheader("Hourly Precipitation Forecast")
            st.line_chart(df["precip_mm"])

            # --- Total precipitation & summary ---
            total_rain = df["precip_mm"].sum()
            st.subheader("Rain Summary")
            if total_rain > 0:
                st.success(f"☔ Yes! Total forecast: {total_rain:.2f} mm")
            else:
                st.info("🌞 No rain expected on this date.")

    except Exception as e:
        st.error(f"Error fetching data: {e}")