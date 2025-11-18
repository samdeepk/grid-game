import os
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Generator, Any, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from nws_utils import get_coordinates_from_address

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('nws_api')

class NWSConfig:
    """Configuration for the National Weather Service API."""
    BASE_URL = os.environ.get("NWS_BASE_URL", "https://api.weather.gov")
    USER_EMAIL = os.environ.get("NWS_USER_EMAIL")
    USER_AGENT = os.environ.get("NWS_USER_AGENT", "PythonNWSAPIWrapper/1.0")
    USER_AGENT_STR = f"{USER_AGENT} ({USER_AGENT})"
    CACHE_EXPIRY = int(os.environ.get("NWS_CACHE_EXPIRY", "600"))  # 10 minutes default
    TIMEOUT = int(os.environ.get("NWS_TIMEOUT", "10"))  # 10 seconds default

class NWSCache:
    """Simple in-memory cache for API responses."""
    
    def __init__(self):
        self._cache = {}
    
    def get(self, key: str) -> Optional[Dict]:
        """Get a value from the cache if it exists and is not expired."""
        if key in self._cache:
            data, expiry = self._cache[key]
            if expiry > time.time():
                return data
            else:
                # Clean up expired entry
                del self._cache[key]
        return None
    
    def set(self, key: str, value: Dict, ttl: int) -> None:
        """Store a value in the cache with an expiration time."""
        expiry = time.time() + ttl
        self._cache[key] = (value, expiry)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache = {}
    
    def clean_expired(self) -> None:
        """Remove all expired entries from the cache."""
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._cache.items() if exp <= now]
        for key in expired_keys:
            del self._cache[key]

class NWSAPIError(Exception):
    """Base exception for NWS API errors."""
    pass

class NotFoundError(NWSAPIError):
    """Raised when a resource is not found."""
    pass

class RateLimitError(NWSAPIError):
    """Raised when the API rate limit is exceeded."""
    pass

class TimeoutError(NWSAPIError):
    """Raised when the API request times out."""
    pass

class ValidationError(NWSAPIError):
    """Raised when input validation fails."""
    pass

class NWSWeatherAPI:
    """
    A client for interacting with the National Weather Service (NWS) API.
    
    This wrapper provides methods to retrieve weather data, forecasts, alerts,
    and other meteorological information from the NWS API.
    
    Attributes:
        base_url (str): Base URL for the NWS API.
        user_agent (str): User agent string for API requests.
        cache (NWSCache): Cache for API responses.
        session (requests.Session): Session for making HTTP requests.
    """
    
    def __init__(
        self, 
        user_agent: str = NWSConfig.USER_AGENT_STR,
        base_url: str = NWSConfig.BASE_URL,
        cache_expiry: int = NWSConfig.CACHE_EXPIRY,
        timeout: int = NWSConfig.TIMEOUT
    ):
        """
        Initialize the NWS API client.
        
        Args:
            user_agent (str, optional): User agent string for API requests.
            base_url (str, optional): Base URL for the NWS API.
            cache_expiry (int, optional): Default cache TTL in seconds.
            timeout (int, optional): Request timeout in seconds.
        """
        self.base_url = base_url
        self.user_agent = user_agent or NWSConfig.USER_AGENT
        self.cache_expiry = cache_expiry
        self.timeout = timeout
        self.cache = NWSCache()
        
        # Set up session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set default headers
        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/geo+json"
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the NWS API.
        
        Args:
            endpoint (str): API endpoint to request.
            params (Dict, optional): Query parameters for the request.
            
        Returns:
            Dict: JSON response from the API.
            
        Raises:
            NotFoundError: If the resource is not found.
            RateLimitError: If the API rate limit is exceeded.
            TimeoutError: If the request times out.
            NWSAPIError: For other API errors.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        cache_key = f"{url}:{json.dumps(params or {})}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logger.debug(f"Cache hit for {url}")
            return cached_data
        
        logger.debug(f"Making request to {url}")
        try:
            response = self.session.get(
                url, 
                params=params, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                # Cache the successful response
                self.cache.set(cache_key, data, self.cache_expiry)
                return data
            elif response.status_code == 404:
                raise NotFoundError(f"Resource not found: {url}")
            elif response.status_code == 429:
                raise RateLimitError("API rate limit exceeded")
            else:
                raise NWSAPIError(f"API request failed with status {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout} seconds")
        except requests.exceptions.RequestException as e:
            raise NWSAPIError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise NWSAPIError("Invalid JSON response")
    
    def get_points(self, latitude: float, longitude: float) -> Dict:
        """
        Get metadata about a location by coordinates.
        
        Args:
            latitude (float): Latitude coordinate.
            longitude (float): Longitude coordinate.
            
        Returns:
            Dict: Metadata about the location.
            
        Raises:
            ValidationError: If coordinates are invalid.
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValidationError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValidationError("Longitude must be between -180 and 180")
        
        endpoint = f"points/{latitude:.4f},{longitude:.4f}"
        return self._make_request(endpoint)
    

    def get_forecast_for(self, query: str, hourly: bool = False) -> Dict:
        """
        Get weather forecast for a location specified by a query string.
        
        Args:
            query (str): Location query accepting zip, city name, or address
                (e.g., "Washington, DC", "20500", "1600 Pennsylvania Ave NW, Washington, DC 20500").
            hourly (bool, optional): Whether to get hourly forecast. Defaults to False.
        
        Returns:
            Dict: Weather forecast data.
        """
        if not query:
            raise ValidationError("Query must be a non-empty string")

        query = query.strip()
        parts = [p for p in query.replace(',', ' ').split() if p]
        if len(parts) == 2:
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                return self.get_forecast(lat, lon, hourly=hourly)
            except ValueError:
                pass

        coords = get_coordinates_from_address(query)
        if not coords:
            raise ValidationError("Unable to determine coordinates for query.")

        return self.get_forecast(coords.latitude, coords.longitude, hourly=hourly)

    
    def get_forecast(self, latitude: float, longitude: float, hourly: bool = False) -> Dict:
        """
        Get weather forecast for a location.
        
        Args:
            latitude (float): Latitude coordinate.
            longitude (float): Longitude coordinate.
            hourly (bool, optional): Whether to get hourly forecast. Defaults to False.
            
        Returns:
            Dict: Weather forecast data.
        """
        # First get the grid endpoint for the coordinates
        points_data = self.get_points(latitude, longitude)
        
        # Extract the forecast URL from the points response
        if hourly:
            forecast_url = points_data.get("properties", {}).get("forecastHourly")
        else:
            forecast_url = points_data.get("properties", {}).get("forecast")
        
        if not forecast_url:
            raise NotFoundError("Forecast URL not found in points response")
        
        # The forecast URL is a full URL, so we need to extract just the endpoint
        forecast_endpoint = forecast_url.replace(self.base_url, "")
        return self._make_request(forecast_endpoint)
    
    def get_hourly_forecast(self, latitude: float, longitude: float) -> Dict:
        """
        Get hourly weather forecast for a location.
        
        Args:
            latitude (float): Latitude coordinate.
            longitude (float): Longitude coordinate.
            
        Returns:
            Dict: Hourly weather forecast data.
        """
        return self.get_forecast(latitude, longitude, hourly=True)
    
    def get_grid_forecast(self, wfo: str, x: int, y: int, hourly: bool = False) -> Dict:
        """
        Get forecast directly using grid coordinates.
        
        Args:
            wfo (str): Weather Forecast Office identifier.
            x (int): Grid X coordinate.
            y (int): Grid Y coordinate.
            hourly (bool, optional): Whether to get hourly forecast. Defaults to False.
            
        Returns:
            Dict: Weather forecast data.
        """
        endpoint = f"gridpoints/{wfo}/{x},{y}/{'forecast/hourly' if hourly else 'forecast'}"
        return self._make_request(endpoint)
    
    def _parse_coordinate_query(self, query: str) -> Optional[Tuple[float, float]]:
        """
        Attempt to parse a latitude/longitude pair from the provided query string.
        Accepts common delimiters such as comma or whitespace.
        """
        parts = [p for p in query.replace(',', ' ').split() if p]
        if len(parts) == 2:
            try:
                lat = float(parts[0])
                lon = float(parts[1])
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError
                return lat, lon
            except ValueError:
                return None
        return None
    
    def get_alerts(
        self, 
        area: Optional[str] = None,
        region: Optional[str] = None,
        zone: Optional[str] = None,
        status: Optional[str] = None,
        message_type: Optional[str] = None,
        event: Optional[str] = None,
        active: bool = True
    ) -> Dict:
        """
        Get weather alerts.
        
        Args:
            area (str, optional): State/territory code or marine area code.
            region (str, optional): Region code.
            zone (str, optional): Zone ID.
            status (str, optional): Alert status (actual, exercise, system, test, draft).
            message_type (str, optional): Message type (alert, update, cancel).
            event (str, optional): Event name (e.g., "Tornado Warning").
            active (bool, optional): Whether to only include active alerts. Defaults to True.
            
        Returns:
            Dict: Weather alerts data.
        """
        params = {}
        if area:
            params["area"] = area
        if region:
            params["region"] = region
        if zone:
            params["zone"] = zone
        if status:
            params["status"] = status
        if message_type:
            params["message_type"] = message_type
        if event:
            params["event"] = event
        if active:
            params["active"] = "true"
        
        return self._make_request("alerts", params)
    
    def get_alert_by_id(self, alert_id: str) -> Dict:
        """
        Get a specific weather alert by ID.
        
        Args:
            alert_id (str): The alert ID.
            
        Returns:
            Dict: Weather alert data.
        """
        endpoint = f"alerts/{alert_id}"
        return self._make_request(endpoint)
    
    def get_stations(self, state: Optional[str] = None) -> Dict:
        """
        Get weather stations.
        
        Args:
            state (str, optional): State code to filter stations.
            
        Returns:
            Dict: Weather stations data.
        """
        params = {}
        if state:
            params["state"] = state
        
        return self._make_request("stations", params)
    
    def get_station_observations(
        self, 
        station_id: str, 
        start: Optional[datetime] = None,
        end: Optional[datetime] = None
    ) -> Dict:
        """
        Get observations from a specific weather station.
        
        Args:
            station_id (str): Station identifier.
            start (datetime, optional): Start time for observations.
            end (datetime, optional): End time for observations.
            
        Returns:
            Dict: Weather observations data.
        """
        endpoint = f"stations/{station_id}/observations"
        params = {}
        
        if start:
            params["start"] = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end:
            params["end"] = end.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return self._make_request(endpoint, params)
    
    def get_latest_station_observation(self, station_id: str) -> Dict:
        """
        Get the latest observation from a specific weather station.
        
        Args:
            station_id (str): Station identifier.
            
        Returns:
            Dict: Latest weather observation data.
        """
        endpoint = f"stations/{station_id}/observations/latest"
        return self._make_request(endpoint)
    
    def get_office(self, office_id: str) -> Dict:
        """
        Get information about a Weather Forecast Office.
        
        Args:
            office_id (str): Office identifier.
            
        Returns:
            Dict: Weather office data.
        """
        endpoint = f"offices/{office_id}"
        return self._make_request(endpoint)
    
    def get_office_headlines(self, office_id: str) -> Dict:
        """
        Get headlines for a Weather Forecast Office.
        
        Args:
            office_id (str): Office identifier.
            
        Returns:
            Dict: Weather office headlines.
        """
        endpoint = f"offices/{office_id}/headlines"
        return self._make_request(endpoint)
    
    def get_zones(self, zone_type: str, area: Optional[str] = None) -> Dict:
        """
        Get forecast zones.
        
        Args:
            zone_type (str): Zone type (forecast, county, fire).
            area (str, optional): State/territory code.
            
        Returns:
            Dict: Zone data.
        """
        if zone_type not in ["forecast", "county", "fire"]:
            raise ValidationError("Zone type must be one of: forecast, county, fire")
        
        endpoint = f"zones/{zone_type}"
        params = {}
        if area:
            params["area"] = area
        
        return self._make_request(endpoint, params)
    
    def get_zone_forecast(self, zone_id: str) -> Dict:
        """
        Get forecast for a specific zone.
        
        Args:
            zone_id (str): Zone identifier.
            
        Returns:
            Dict: Zone forecast data.
        """
        endpoint = f"zones/forecast/{zone_id}/forecast"
        return self._make_request(endpoint)
    
    def get_zone_observations(self, zone_id: str) -> Dict:
        """
        Get observations for a specific zone.
        
        Args:
            zone_id (str): Zone identifier.
            
        Returns:
            Dict: Zone observations data.
        """
        endpoint = f"zones/forecast/{zone_id}/observations"
        return self._make_request(endpoint)
    
    def get_products(
        self, 
        location: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        limit: int = 50
    ) -> Dict:
        """
        Get text products.
        
        Args:
            location (str, optional): WFO issuing the product.
            start (datetime, optional): Start time for products.
            end (datetime, optional): End time for products.
            limit (int, optional): Maximum number of products to return. Defaults to 50.
            
        Returns:
            Dict: Text products data.
        """
        endpoint = "products"
        params = {"limit": limit}
        
        if location:
            params["location"] = location
        if start:
            params["start"] = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end:
            params["end"] = end.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        return self._make_request(endpoint, params)
    
    def get_product(self, product_id: str) -> Dict:
        """
        Get a specific text product.
        
        Args:
            product_id (str): Product identifier.
            
        Returns:
            Dict: Text product data.
        """
        endpoint = f"products/{product_id}"
        return self._make_request(endpoint)
    
    def get_glossary(self) -> Dict:
        """
        Get the NWS API glossary.
        
        Returns:
            Dict: Glossary data.
        """
        return self._make_request("glossary")
    
    def get_icons(self, set_name: str = "forecast") -> Dict:
        """
        Get weather icons.
        
        Args:
            set_name (str, optional): Icon set name. Defaults to "forecast".
            
        Returns:
            Dict: Icons data.
        """
        endpoint = f"icons/{set_name}"
        return self._make_request(endpoint)
    
    def get_icon(self, set_name: str, icon_name: str) -> Dict:
        """
        Get a specific weather icon.
        
        Args:
            set_name (str): Icon set name.
            icon_name (str): Icon name.
            
        Returns:
            Dict: Icon data.
        """
        endpoint = f"icons/{set_name}/{icon_name}"
        return self._make_request(endpoint)
    
    def clear_cache(self) -> None:
        """Clear the API response cache."""
        self.cache.clear()
    
    def clean_cache(self) -> None:
        """Remove expired entries from the cache."""
        self.cache.clean_expired()
