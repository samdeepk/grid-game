from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from nsw_api import NWSWeatherAPI, ValidationError

app = FastAPI()
weather_api = NWSWeatherAPI()


def translate_forecast_response(raw: dict) -> dict:
    """Map the NWS forecast payload into the simplified structure we expose."""
    props = raw.get("properties", {})
    periods = props.get("periods", [])

    simplified_periods = []
    for period in periods[:3]:  # keep sample small
        simplified_periods.append(
            {
                "number": period.get("number"),
                "name": period.get("name"),
                "startTime": period.get("startTime"),
                "endTime": period.get("endTime"),
                "temperature": period.get("temperature"),
                "temperatureUnit": period.get("temperatureUnit"),
                "windSpeed": period.get("windSpeed"),
                "windDirection": period.get("windDirection"),
                "shortForecast": period.get("shortForecast"),
                "detailedForecast": period.get("detailedForecast"),
                "icon": period.get("icon"),
                "probabilityOfPrecipitation": period.get("probabilityOfPrecipitation"),
            }
        )

    return {
        "type": raw.get("type", "Feature"),
        "properties": {
            "updated": props.get("updated"),
            "periods": simplified_periods,
        },
        "geometry": raw.get("geometry", {}),
    }


@app.get("/api")
def read_root(query: str = "San Francisco, CA", hourly: bool = False):
    """Demo endpoint that fetches a forecast for the given query string."""
    try:
        raw = weather_api.get_forecast_for(query, hourly=hourly)
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch forecast") from exc

    return translate_forecast_response(raw)


app.mount("/", StaticFiles(directory="../weather-app/dist/weather-app/browser", html=True), name="static")
