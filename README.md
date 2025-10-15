# Will It Rain On My Parade? 🌦️

A friendly weather forecast app that tells you if rain is coming to your location — with a dash of AI-powered advice!

## Project Description
This app was originally created as a hackathon project during the NASA Space Apps Challenge 2025. It provides hourly precipitation forecasts based on location input, enhanced by an AI/ML layer that offers personalized tips and predictions. The app uses Meteomatics data for accurate weather information and OpenStreetMap for geocoding.

## Features
- Input a city name or latitude,longitude coordinates to receive detailed weather forecasts.
- Hourly precipitation forecast visualized with interactive charts.
- AI-powered chat layer provides friendly, rule-based advice based on precipitation data.
- Global coverage with geocoding support for any city worldwide.

## Live Demo (v3)
Try the latest version live with Open-Meteo API integration here:  
https://rain-cast-ai.streamlit.app/

## Original Hackathon Submission (v2)
Explore the original hackathon version using Meteomatics data here:  
https://github.com/ida/WillItRainApp-v2

## Setup Instructions
1. Clone the repository:
   ```
   git clone https://github.com/ida/WillItRainApp.git
   ```
2. Create and activate a Python virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install streamlit pandas requests
   ```
4. Run the app:
   ```
   streamlit run app.py
   ```

## Notes
- The original Meteomatics API access used in the hackathon is limited and replaced in the latest version by Open-Meteo for free, open weather data.
- The AI/ML layer remains rule-based and interprets precipitation data to provide helpful and friendly advice.
- Contributions and feedback are welcome!
