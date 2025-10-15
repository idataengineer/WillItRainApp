import streamlit as st
st.info(
    "🔄 **Update Notice:** This version of *Will It Rain On My Parade?* was developed by **Team DataNova AI** "
    "for the NASA Space Apps Challenge 2025 using Meteomatics data. "
    "The original Meteomatics API credentials have since expired. "
    "A parallel demo version using an open API is available below.\n\n"
    "### 👉 [**RainCast AI (v3)**](https://rain-cast-ai.streamlit.app/)\n\n"
    "_No functional changes were made beyond the API replacement._"
)
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
    st.error(
        "Meteomatics credentials not found. Set METEO_USERNAME and METEO_PASSWORD as environment variables."
    )
    st.stop()

# --- Geocode city name to lat/lon ---
def geocode_city(city_name):
    """
    Uses Nominatim API to get latitude and longitude for a city.
    Returns (lat, lon) as floats.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": city_name, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers={"User-Agent": "WillItRainApp/1.0"})
    data = response.json()
    if not data:
        return None, None
    return float(data[0]["lat"]), float(data[0]["lon"])

# --- Parse user input (city name or lat/lon) ---
def parse_location(input_str):
    if "," in input_str:
        try:
            lat, lon = map(float, map(str.strip, input_str.split(",")))
            return lat, lon
        except:
            return None, None
    else:
        return geocode_city(input_str)

# --- Chatty AI/ML prediction ---
def ai_predict_rain(df, location_name):
    """
    Simple chatty AI prediction based on precipitation
    """
    total_rain = df["precip_mm"].sum()
    if df["precip_mm"].max() > 0:
        return (
            f"🌧️ Heads up! There is a chance of rain today in {location_name}. "
            f"Total forecasted precipitation is {total_rain:.2f} mm. "
            "Don't forget your umbrella or raincoat! ☔"
        )
    else:
        return (
            f"☀️ Good news! It looks dry in {location_name} today. "
            "Perfect weather to enjoy outdoor activities! 😎"
        )

# --- Streamlit App ---
st.title("🌦️ Will It Rain On My Parade? (v2)")
st.markdown(
    "Enter a city name or latitude,longitude to see the Meteomatics forecast and AI/ML prediction."
)

# Input: location and date
location_input = st.text_input("Enter city name or lat,lon", "")
event_date = st.date_input("Pick a date", dt.date.today())

if st.button("Check Forecast"):
    lat, lon = parse_location(location_input)
    if lat is None or lon is None:
        st.error("Could not parse location. Enter a valid city name or lat,lon.")
        st.stop()

    try:
        # --- Prepare Meteomatics API request ---
        date_str = event_date.strftime("%Y-%m-%d")
        url = f"https://api.meteomatics.com/{date_str}T00:00:00Z--{date_str}T23:00:00Z:PT1H/precip_1h:mm/{lat},{lon}/csv"

        # --- Fetch data ---
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        if response.status_code != 200:
            st.error(f"Error fetching data: {response.text}")
        else:
            df = pd.read_csv(StringIO(response.text), sep=";")

            # --- Dynamic column handling & renaming ---
            df.rename(columns={df.columns[0]: "datetime", df.columns[1]: "precip_mm"}, inplace=True)
            df["datetime"] = pd.to_datetime(df["datetime"])
            df.set_index("datetime", inplace=True)

            # --- Meteomatics forecast ---
            st.subheader("📡 Meteomatics Hourly Precipitation Forecast")
            st.line_chart(df["precip_mm"])

            total_rain = df["precip_mm"].sum()
            st.subheader("Rain Summary (Forecast)")
            if total_rain > 0:
                st.success(f"☔ Yes! Total forecast: {total_rain:.2f} mm")
            else:
                st.info("🌞 No rain expected on this date.")

            # --- Chatty AI/ML Prediction ---
            st.subheader("🤖 AI Prediction")
            ai_result = ai_predict_rain(df, location_input)
            st.write(ai_result)

    except Exception as e:
        st.error(f"Error fetching data: {e}")
