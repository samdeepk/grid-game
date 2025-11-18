from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional, Any, Union

@dataclass
class Coordinates:
    """Geographic coordinates."""
    latitude: float
    longitude: float

@dataclass
class Temperature:
    """Temperature information."""
    value: float
    unit: str
    
    @property
    def celsius(self) -> float:
        """Convert temperature to Celsius."""
        if self.unit.lower() == "f":
            return (self.value - 32) * 5/9
        return self.value
    
    @property
    def fahrenheit(self) -> float:
        """Convert temperature to Fahrenheit."""
        if self.unit.lower() == "c":
            return (self.value * 9/5) + 32
        return self.value

@dataclass
class Wind:
    """Wind information."""
    speed: float
    direction: float
    unit: str

@dataclass
class Precipitation:
    """Precipitation information."""
    value: float
    type: Optional[str]
    unit: str

@dataclass
class WeatherCondition:
    """Weather condition information."""
    description: str
    icon: Optional[str] = None

@dataclass
class ForecastPeriod:
    """A period in a forecast."""
    name: str
    start_time: datetime
    end_time: datetime
    temperature: Temperature
    wind: Wind
    short_forecast: str
    detailed_forecast: str
    icon: Optional[str] = None
    precipitation_probability: Optional[int] = None

@dataclass
class Forecast:
    """Weather forecast information."""
    updated: datetime
    periods: List[ForecastPeriod]
    
    @property
    def today(self) -> Optional[ForecastPeriod]:
        """Get today's forecast."""
        if self.periods:
            return self.periods[0]
        return None
    
    @property
    def tonight(self) -> Optional[ForecastPeriod]:
        """Get tonight's forecast."""
        for period in self.periods:
            if "night" in period.name.lower():
                return period
        return None

@dataclass
class Observation:
    """Weather observation information."""
    station: str
    timestamp: datetime
    temperature: Optional[Temperature] = None
    dewpoint: Optional[Temperature] = None
    relative_humidity: Optional[float] = None
    wind: Optional[Wind] = None
    barometric_pressure: Optional[float] = None
    visibility: Optional[float] = None
    text_description: Optional[str] = None
    precipitation_last_hour: Optional[Precipitation] = None

@dataclass
class Alert:
    """Weather alert information."""
    id: str
    event: str
    headline: str
    description: str
    instruction: Optional[str]
    severity: str
    certainty: str
    urgency: str
    sent: datetime
    effective: datetime
    onset: Optional[datetime]
    expires: datetime
    ends: Optional[datetime]
    status: str
    message_type: str
    category: str
    response_type: str
    affected_zones: List[str]
    affected_counties: List[str]
