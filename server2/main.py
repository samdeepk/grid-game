from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Create a FastAPI instance
app = FastAPI()

data = {
  "type": "Feature",
  "properties": {
    "updated": "2025-11-16T12:00:00Z",
    "periods": [
      {
        "number": 1,
        "name": "Today",
        "startTime": "2025-11-16T12:00:00Z",
        "endTime": "2025-11-16T18:00:00Z",
        "temperature": 68,
        "temperatureUnit": "F",
        "windSpeed": "5 mph",
        "windDirection": "NW",
        "shortForecast": "Partly Sunny",
        "detailedForecast": "Partly sunny, with a high near 68.",
        "icon": "https://api.weather.gov/icons/land/day/partly_cloudy",
        "probabilityOfPrecipitation": { "value": 10 }
      },
      {
        "number": 2,
        "name": "Tonight",
        "startTime": "2025-11-16T18:00:00Z",
        "endTime": "2025-11-17T06:00:00Z",
        "temperature": 55,
        "temperatureUnit": "F",
        "windSpeed": "3 mph",
        "windDirection": "N",
        "shortForecast": "Clear",
        "detailedForecast": "Clear, with a low around 55.",
        "icon": "https://api.weather.gov/icons/land/night/clear",
        "probabilityOfPrecipitation": { "value": 0 }
      },
      {
        "number": 3,
        "name": "Monday",
        "startTime": "2025-11-17T06:00:00Z",
        "endTime": "2025-11-17T18:00:00Z",
        "temperature": 70,
        "temperatureUnit": "F",
        "windSpeed": "7 mph",
        "windDirection": "NE",
        "shortForecast": "Mostly Sunny",
        "detailedForecast": "Mostly sunny, with a high near 70.",
        "icon": "https://api.weather.gov/icons/land/day/mostly_sunny",
        "probabilityOfPrecipitation": { "value": 5 }
      }
    ]
  },
  "geometry": {
    "type": "Point",
    "coordinates": [-122.4194, 37.7749]
  }
}
@app.get("/api")
def read_root():
    return data
    

app.mount("/", StaticFiles(directory="../weather-app/dist/weather-app/browser", html=True), name="static")

# Define a path operation decorator for a GET request at the root URL ("/")

