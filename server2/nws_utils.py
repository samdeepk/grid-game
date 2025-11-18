from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple

from weather_models import (
    Coordinates, Temperature, Wind, Precipitation, 
    WeatherCondition, ForecastPeriod, Forecast, 
    Observation, Alert
)

def parse_forecast(forecast_data: Dict) -> Forecast:
    """
    Parse raw forecast data into a Forecast object.
    
    Args:
        forecast_data (Dict): Raw forecast data from the API.
        
    Returns:
        Forecast: Parsed forecast object.
    """
    properties = forecast_data.get("properties", {})
    updated = properties.get("updated", "")
    if updated:
        updated = datetime.fromisoformat(updated.replace("Z", "+00:00"))

    
    periods = []
    for period_data in properties.get("periods", []):
        start_time = datetime.fromisoformat(period_data.get("startTime", "").replace("Z", "+00:00"))
        end_time = datetime.fromisoformat(period_data.get("endTime", "").replace("Z", "+00:00"))
        
        temperature = Temperature(
            value=period_data.get("temperature", 0),
            unit=period_data.get("temperatureUnit", "F")
        )
        
        wind_direction = period_data.get("windDirection", "")
        wind_speed_str = period_data.get("windSpeed", "0 mph")
        wind_speed = int(''.join(filter(str.isdigit, wind_speed_str)))
        
        wind = Wind(
            speed=wind_speed,
            direction=wind_direction,
            unit="mph"
        )
        
        period = ForecastPeriod(
            name=period_data.get("name", ""),
            start_time=start_time,
            end_time=end_time,
            temperature=temperature,
            wind=wind,
            short_forecast=period_data.get("shortForecast", ""),
            detailed_forecast=period_data.get("detailedForecast", ""),
            icon=period_data.get("icon"),
            precipitation_probability=period_data.get("probabilityOfPrecipitation", {}).get("value")
        )
        
        periods.append(period)
    
    return Forecast(updated=updated, periods=periods)

def parse_observation(observation_data: Dict) -> Observation:
    """
    Parse raw observation data into an Observation object.
    
    Args:
        observation_data (Dict): Raw observation data from the API.
        
    Returns:
        Observation: Parsed observation object.
    """
    properties = observation_data.get("properties", {})
    
    station = properties.get("station", "")
    timestamp_str = properties.get("timestamp", "")
    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else datetime.now()
    
    temperature = None
    if "temperature" in properties:
        temperature = Temperature(
            value=properties["temperature"].get("value", 0),
            unit=properties["temperature"].get("unitCode", "wmoUnit:degC").split(":")[-1]
        )
    
    dewpoint = None
    if "dewpoint" in properties:
        dewpoint = Temperature(
            value=properties["dewpoint"].get("value", 0),
            unit=properties["dewpoint"].get("unitCode", "wmoUnit:degC").split(":")[-1]
        )
    
    relative_humidity = properties.get("relativeHumidity", {}).get("value")
    
    wind = None
    if "windSpeed" in properties and "windDirection" in properties:
        wind = Wind(
            speed=properties["windSpeed"].get("value", 0),
            direction=properties["windDirection"].get("value", 0),
            unit=properties["windSpeed"].get("unitCode", "wmoUnit:km_h-1").split(":")[-1]
        )
    
    barometric_pressure = properties.get("barometricPressure", {}).get("value")
    visibility = properties.get("visibility", {}).get("value")
    text_description = properties.get("textDescription", "")
    
    precipitation_last_hour = None
    if "precipitationLastHour" in properties:
        precipitation_last_hour = Precipitation(
            value=properties["precipitationLastHour"].get("value", 0),
            type=None,
            unit=properties["precipitationLastHour"].get("unitCode", "wmoUnit:mm").split(":")[-1]
        )
    
    return Observation(
        station=station,
        timestamp=timestamp,
        temperature=temperature,
        dewpoint=dewpoint,
        relative_humidity=relative_humidity,
        wind=wind,
        barometric_pressure=barometric_pressure,
        visibility=visibility,
        text_description=text_description,
        precipitation_last_hour=precipitation_last_hour
    )

def parse_alert(alert_data: Dict) -> Alert:
    """
    Parse raw alert data into an Alert object.
    
    Args:
        alert_data (Dict): Raw alert data from the API.
        
    Returns:
        Alert: Parsed alert object.
    """
    properties = alert_data.get("properties", {})
    
    # Parse timestamps
    sent = datetime.fromisoformat(properties.get("sent", "").replace("Z", "+00:00"))
    effective = datetime.fromisoformat(properties.get("effective", "").replace("Z", "+00:00"))
    expires = datetime.fromisoformat(properties.get("expires", "").replace("Z", "+00:00"))
    
    onset_str = properties.get("onset")
    onset = datetime.fromisoformat(onset_str.replace("Z", "+00:00")) if onset_str else None
    
    ends_str = properties.get("ends")
    ends = datetime.fromisoformat(ends_str.replace("Z", "+00:00")) if ends_str else None
    
    # Parse affected zones
    affected_zones = []
    for zone in properties.get("affectedZones", []):
        zone_id = zone.split("/")[-1]
        affected_zones.append(zone_id)
    
    # Parse affected counties (derived from geocode)
    affected_counties = []
    for county in properties.get("geocode", {}).get("SAME", []):
        affected_counties.append(county)
    
    return Alert(
        id=properties.get("id", ""),
        event=properties.get("event", ""),
        headline=properties.get("headline", ""),
        description=properties.get("description", ""),
        instruction=properties.get("instruction"),
        severity=properties.get("severity", ""),
        certainty=properties.get("certainty", ""),
        urgency=properties.get("urgency", ""),
        sent=sent,
        effective=effective,
        onset=onset,
        expires=expires,
        ends=ends,
        status=properties.get("status", ""),
        message_type=properties.get("messageType", ""),
        category=properties.get("category", ""),
        response_type=properties.get("response", ""),
        affected_zones=affected_zones,
        affected_counties=affected_counties
    )

def get_coordinates_from_address(address: str) -> Optional[Coordinates]:
    """
    Get coordinates for an address using a geocoding service.
    
    Args:
        address (str): Address to geocode.
        
    Returns:
        Optional[Coordinates]: Coordinates for the address, or None if geocoding failed.
    """
    try:
        # This is a placeholder. In a real implementation, you would use a geocoding service
        # like Google Maps, Nominatim, or similar.

        
        # For now, return None to indicate that geocoding is not implemented
        return None
    except Exception:
        return None

def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert Celsius to Fahrenheit.
    
    Args:
        celsius (float): Temperature in Celsius.
        
    Returns:
        float: Temperature in Fahrenheit.
    """
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convert Fahrenheit to Celsius.
    
    Args:
        fahrenheit (float): Temperature in Fahrenheit.
        
    Returns:
        float: Temperature in Celsius.
    """
    return (fahrenheit - 32) * 5/9

def meters_to_miles(meters: float) -> float:
    """
    Convert meters to miles.
    
    Args:
        meters (float): Distance in meters.
        
    Returns:
        float: Distance in miles.
    """
    return meters / 1609.344

def miles_to_meters(miles: float) -> float:
    """
    Convert miles to meters.
    
    Args:
        miles (float): Distance in miles.
        
    Returns:
        float: Distance in meters.
    """
    return miles * 1609.344

def kph_to_mph(kph: float) -> float:
    """
    Convert kilometers per hour to miles per hour.
    
    Args:
        kph (float): Speed in kilometers per hour.
        
    Returns:
        float: Speed in miles per hour.
    """
    return kph * 0.621371

def mph_to_kph(mph: float) -> float:
    """
    Convert miles per hour to kilometers per hour.
    
    Args:
        mph (float): Speed in miles per hour.
        
    Returns:
        float: Speed in kilometers per hour.
    """
    return mph * 1.60934