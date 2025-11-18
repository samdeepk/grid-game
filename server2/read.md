# OpenWeatherMap Coding Tests 

This library that wraps the . 


This package provides a comprehensive Python wrapper for the [National Wether Service API](https://weather-gov.github.io/api/general-faqs). It allows developers to easily access weather data, forecasts, alerts, and aother meteorological information from the NWS.

### Installation

#### Prerequisites
- Python 3.7 or higher
- pip package manager

#### Install dependencies in a virtual environment  
```bash
python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
```


## Testing
 - Tests are in `test_nws.py' and 'test_weather_models'
 - To execute them run:

```bash
python3 -m pytest
```


## Usage Example
```python
import os
import json
from datetime import datetime, timedelta

from nws_api import NWSWeatherAPI
from nws_utils import parse_forecast, parse_observation, parse_alert

api = NWSWeatherAPI(user_agent="MyWeatherApp/1.0 (your@email.com)")

# Washington, DC coordinates
lat, lon = 38.8951, -77.0364

# Get forecast data
forecast_data = api.get_forecast(lat, lon)
assert forecast_data["properties"]["elevation"]["value"] ==  6.096

# Parse the forecast data
forecast = parse_forecast(forecast_data)

# Print forecast information
print(f"Forecast updated: {forecast.updated}")
print(f"Today: {forecast.today.name} - {forecast.today.short_forecast}")    

```


## Configuration

The NWS API wrapper can be configured using environment variables:


Environment Variable	Description	Default Value
`NWS_BASE_URL`	Base URL for the NWS API	`https://api.weather.gov`
`NWS_USER_EMAIL`	A required User email for API identification	None
`NWS_USER_AGENT`	User agent string for API requests	`PythonNWSAPIWrapper/1.0`
`NWS_CACHE_EXPIRY`	Cache TTL in seconds	`600` (10 minutes)

## Core Components

### NWSConfig

Configuration class for the National Weather Service API. Manages default settings and environment variables.


### NWSCache

Simple in-memory cache for API responses to reduce API calls and improve performance.


**Methods:**
• `get(key)`: Get a value from the cache if it exists and is not expired
• `set(key, value, ttl)`: Store a value in the cache with an expiration time
• `clear()`: Clear all cache entries
• `clean_expired()`: Remove all expired entries from the cache


### NWSWeatherAPI

The main client for interacting with the National Weather Service API. Provides methods to retrieve weather data, forecasts, alerts, and other meteorological information.


### Data Models

The package includes several data models to represent weather information:


### Coordinates

Geographic coordinates.


**Attributes:**
• `latitude`: Latitude coordinate (float)
• `longitude`: Longitude coordinate (float)


### Temperature

Temperature information with unit conversion capabilities.


**Attributes:**
• `value`: Temperature value (float)
• `unit`: Temperature unit (string, e.g., "F" or "C")


**Properties:**
• `celsius`: Convert temperature to Celsius
• `fahrenheit`: Convert temperature to Fahrenheit


### Wind

Wind information.


**Attributes:**
• `speed`: Wind speed (float)
• `direction`: Wind direction (float)
• `unit`: Speed unit (string, e.g., "mph" or "km_h-1")


### Precipitation

Precipitation information.


**Attributes:**
• `value`: Precipitation amount (float)
• `type`: Precipitation type (string, optional)
• `unit`: Measurement unit (string)


### WeatherCondition

Weather condition information.


**Attributes:**
• `description`: Weather condition description (string)
• `icon`: Icon identifier (string, optional)


#### ForecastPeriod

A period in a forecast.


**Attributes:**
• `name`: Period name (string, e.g., "Today", "Tonight")
• `start_time`: Period start time (datetime)
• `end_time`: Period end time (datetime)
• `temperature`: Temperature information (Temperature)
• `wind`: Wind information (Wind)
• `short_forecast`: Brief forecast description (string)
• `detailed_forecast`: Detailed forecast description (string)
• `icon`: Icon URL (string, optional)
• `precipitation_probability`: Probability of precipitation (int, optional)


### Forecast

Weather forecast information.


**Attributes:**
• `updated`: Last update time (datetime)
• `periods`: List of forecast periods (List[ForecastPeriod])


**Properties:**
• `today`: Get today's forecast
• `tonight`: Get tonight's forecast


### Observation

Weather observation information.


**Attributes:**
• `station`: Weather station identifier (string)
• `timestamp`: Observation time (datetime)
• `temperature`: Temperature information (Temperature, optional)
• `dewpoint`: Dewpoint temperature (Temperature, optional)
• `relative_humidity`: Relative humidity percentage (float, optional)
• `wind`: Wind information (Wind, optional)
• `barometric_pressure`: Barometric pressure (float, optional)
• `visibility`: Visibility distance (float, optional)
• `text_description`: Text description of conditions (string, optional)
• `precipitation_last_hour`: Precipitation in the last hour (Precipitation, optional)


### Alert

Weather alert information.


**Attributes:**
• `id`: Alert identifier (string)
• `event`: Event type (string)
• `headline`: Alert headline (string)
• `description`: Alert description (string)
• `instruction`: Instructions for public (string, optional)
• `severity`: Alert severity (string)
• `certainty`: Alert certainty (string)
• `urgency`: Alert urgency (string)
• `sent`: Time alert was sent (datetime)
• `effective`: Time alert becomes effective (datetime)
• `onset`: Time event is expected to begin (datetime, optional)
• `expires`: Time alert expires (datetime)
• `ends`: Time event is expected to end (datetime, optional)
• `status`: Alert status (string)
• `message_type`: Message type (string)
• `category`: Alert category (string)
• `response_type`: Recommended response type (string)
• `affected_zones`: List of affected zone identifiers (List[string])
• `affected_counties`: List of affected county identifiers (List[string])


### API Client

### NWSWeatherAPI

**Constructor:**


NWSWeatherAPI(
    user_agent: str = NWSConfig.USER_AGENT_STR,
    base_url: str = NWSConfig.BASE_URL,
    cache_expiry: int = NWSConfig.CACHE_EXPIRY,
    timeout: int = NWSConfig.TIMEOUT
)


**Methods:**


Location Data
• `get_points(latitude, longitude)`: Get metadata about a location by coordinates


Forecasts
• `get_forecast(latitude, longitude, hourly=False)`: Get weather forecast for a location
• `get_hourly_forecast(latitude, longitude)`: Get hourly weather forecast for a location
• `get_grid_forecast(wfo, x, y, hourly=False)`: Get forecast directly using grid coordinates
• `get_zone_forecast(zone_id)`: Get forecast for a specific zone


Alerts
• `get_alerts(area=None, region=None, zone=None, status=None, message_type=None, event=None, active=True)`: Get weather alerts
• `get_alert_by_id(alert_id)`: Get a specific weather alert by ID


Stations and Observations
• `get_stations(state=None)`: Get weather stations
• `get_station_observations(station_id, start=None, end=None)`: Get observations from a specific weather station
• `get_latest_station_observation(station_id)`: Get the latest observation from a specific weather station
• `get_zone_observations(zone_id)`: Get observations for a specific zone


Offices
• `get_office(office_id)`: Get information about a Weather Forecast Office
• `get_office_headlines(office_id)`: Get headlines for a Weather Forecast Office


Zones
• `get_zones(zone_type, area=None)`: Get forecast zones


Products
• `get_products(location=None, start=None, end=None, limit=50)`: Get text products
• `get_product(product_id)`: Get a specific text product


Reference Data
• `get_glossary()`: Get the NWS API glossary
• `get_icons(set_name="forecast")`: Get weather icons
• `get_icon(set_name, icon_name)`: Get a specific weather icon


Cache Management
• `clear_cache()`: Clear the API response cache
• `clean_cache()`: Remove expired entries from the cache


Utility Functions

Parsing Functions
• `parse_forecast(forecast_data)`: Parse raw forecast data into a Forecast object
• `parse_observation(observation_data)`: Parse raw observation data into an Observation object
• `parse_alert(alert_data)`: Parse raw alert data into an Alert object
• `get_coordinates_from_address(address)`: Get coordinates for an address using a geocoding service (placeholder)


Conversion Functions
• `celsius_to_fahrenheit(celsius)`: Convert Celsius to Fahrenheit
• `fahrenheit_to_celsius(fahrenheit)`: Convert Fahrenheit to Celsius
• `meters_to_miles(meters)`: Convert meters to miles
• `miles_to_meters(miles)`: Convert miles to meters
• `kph_to_mph(kph)`: Convert kilometers per hour to miles per hour
• `mph_to_kph(mph)`: Convert miles per hour to kilometers per hour


## Error Handling

The package includes several custom exception classes:

• `NWSAPIError`: Base exception for NWS API errors
• `NotFoundError`: Raised when a resource is not found
• `RateLimitError`: Raised when the API rate limit is exceeded
• `TimeoutError`: Raised when the API request times out
• `ValidationError`: Raised when input validation fails


## Examples

### Basic Usage

```python
from nws_api import NWSWeatherAPI
from nws_utils import parse_forecast

# Initialize the API client
api = NWSWeatherAPI(user_agent="MyWeatherApp/1.0 (your@email.com)")

# Get forecast for Washington, DC
lat, lon = 38.8951, -77.0364
forecast_data = api.get_forecast(lat, lon)

# Parse the forecast data
forecast = parse_forecast(forecast_data)

# Print forecast information
print(f"Forecast updated: {forecast.updated}")
print(f"Today: {forecast.today.short_forecast}")
print(f"Temperature: {forecast.today.temperature.value}°{forecast.today.temperature.unit}")
```

### Getting Weather Alerts

```python 
# Get active alerts for a state
alerts_data = api.get_alerts(area="DC")

# Process alerts
for feature in alerts_data.get("features", []):
    alert = parse_alert(feature)
    print(f"Alert: {alert.headline}")
    print(f"Severity: {alert.severity}")
    print(f"Expires: {alert.expires}")


Working with Weather Stations

# Get stations in a state
stations_data = api.get_stations(state="DC")

# Get the latest observation from a station
station_id = "KDCA"  # Washington Reagan National Airport
observation_data = api.get_latest_station_observation(station_id)
observation = parse_observation(observation_data)

print(f"Current conditions at {observation.station}:")
if observation.temperature:
    print(f"Temperature: {observation.temperature.value}°{observation.temperature.unit}")
if observation.text_description:
    print(f"Conditions: {observation.text_description}")
```

### Temperature Conversion

```python
from nws_utils import celsius_to_fahrenheit, fahrenheit_to_celsius

# Convert temperatures
temp_c = 25.0
temp_f = celsius_to_fahrenheit(temp_c)
print(f"{temp_c}°C = {temp_f}°F")

temp_f = 77.0
temp_c = fahrenheit_to_celsius(temp_f)
print(f"{temp_f}°F = {temp_c}°C")

```
