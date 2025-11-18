import pytest
from unittest.mock import MagicMock, patch

from nsw_api import NWSWeatherAPI, ValidationError
from weather_models import Coordinates


def test_get_forecast_for_lat_lon_string():
    api = NWSWeatherAPI()
    fake_response = {'ok': True}
    api.get_forecast = MagicMock(return_value=fake_response)

    result = api.get_forecast_for('38.8895 -77.0352')

    api.get_forecast.assert_called_once_with(38.8895, -77.0352, hourly=False)
    assert result == fake_response


def test_get_forecast_for_address_uses_geocoder():
    api = NWSWeatherAPI()
    fake_response = {'success': 1}
    api.get_forecast = MagicMock(return_value=fake_response)

    with patch('nsw_api.get_coordinates_from_address') as fake_geo:
        fake_geo.return_value = Coordinates(latitude=35.0, longitude=-120.0)
        result = api.get_forecast_for('San Luis Obispo, CA', hourly=True)

    fake_geo.assert_called_once_with('San Luis Obispo, CA')
    api.get_forecast.assert_called_once_with(35.0, -120.0, hourly=True)
    assert result == fake_response


def test_get_forecast_for_invalid_query_raises():
    api = NWSWeatherAPI()

    with pytest.raises(ValidationError):
        api.get_forecast_for('')

    with patch('nsw_api.get_coordinates_from_address', return_value=None):
        with pytest.raises(ValidationError):
            api.get_forecast_for('Not a place either')

