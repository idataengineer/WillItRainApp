import streamlit as st
import datetime as dt
import pandas as pd
import requests

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

# --- Dynamic, chatty AI/ML prediction ---
def ai_predict_rain(df, location_name):
    """
    Chatty AI prediction based on hourly precipitation.
    - Varies message by rain intensity
    - Highlights peak rain hour if any
    """
    total_rain = df["precip_mm"].sum()
    
    if total_rain == 0:
        return f"☀️ Great news! No rain is expected today in {location_name}. Perfect weather to enjoy outdoor activities! 😎"
    
    max_rain = df["precip_mm"].max()
    peak_hour = df["precip_mm"].idxmax().hour
    
    if max_rain <= 2:
        intensity = "light rain"
        advice = "You might just need a small umbrella. ☔"
    elif max_rain <= 5:
        intensity = "moderate rain"
        advice = "Make sure to wear a raincoat or carry an umbrella! ☔"
    else:
        intensity = "heavy rain"
        advice = "Stay safe and consider postponing outdoor plans! ⚠️☔"
    
    return (
        f"🌧️ Attention! {intensity.capitalize()} is expected today in {location_name}. "
        f"Total forecasted precipitation is {total_rain:.2f} mm. "
        f"Peak rainfall is around {peak_hour}:00. {advice}"
    )

# --- Streamlit App ---
st.title("🌦️ Will It Rain On My Parade? (v3)")
st.markdown(
    "Enter a city name or latitude,longitude to see the precipitation forecast and AI/ML prediction. "
    "This version uses Open-Meteo API (free, no credentials required)."
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
        # --- Open-Meteo API request ---
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=precipitation&timezone=auto&start={event_date}&end={event_date}"
        response = requests.get(url)
        if response.status_code != 200:
            st.error(f"Error fetching data: {response.text}")
        else:
            data = response.json()
            df = pd.DataFrame({
                "datetime": pd.to_datetime(data["hourly"]["time"]),
                "precip_mm": data["hourly"]["precipitation"]
            })
            df.set_index("datetime", inplace=True)

            # --- Precipitation forecast ---
            st.subheader("📡 Hourly Precipitation Forecast")
            st.line_chart(df["precip_mm"])

            total_rain = df["precip_mm"].sum()
            st.subheader("Rain Summary")
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