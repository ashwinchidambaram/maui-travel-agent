"""Core weather logic - fetches climate data from Open-Meteo API."""

import httpx
from datetime import date
from core.models import WeatherForecast

# Kahului Airport Coordinates
MAUI_LATITUDE = 20.8987
MAUI_LONGITUDE = -156.4305

# WMO Weather Code lookup table
WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Icy fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Heavy drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}

SEVERE_WEATHER_CODES = {82, 95, 96, 99}

# Open-Meteo only forecasts ~16 days ahead
FORECAST_LIMIT_DAYS = 16


def get_weather_forecast(start_date: str, end_date: str) -> WeatherForecast:
    """
    Fetches weather data for Maui for a given date range.
    
    Routing logic:
    - Past dates → archive API (historical actuals)
    - Within 16 days → forecast API (real forecast)
    - Beyond 16 days → archive API with 2023 baseline (typical conditions)
    """
    
    start = date.fromisoformat(start_date)
    days_until_start = (start - date.today()).days
    
    if days_until_start < 0:
        # Past date - use archive API for historical actuals
        data = _fetch_archive(start_date, end_date)
        source = "historical actuals"
    elif days_until_start <= FORECAST_LIMIT_DAYS:
        # Near-future - use real forecast
        data = _fetch_forecast(start_date, end_date)
        source = "actual forecast"
    else:
        # Far future - use 2023 baseline as proxy for typical conditions
        data = _fetch_climate_normals(start_date, end_date)
        source = "historical climate averages"
    
    return _parse_forecast(data, start_date, end_date, source)


def _fetch_forecast(start_date: str, end_date: str) -> dict:
    """Fetches real weather forecast from Open-Meteo."""
    
    response = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": MAUI_LATITUDE,
            "longitude": MAUI_LONGITUDE,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "temperature_unit": "fahrenheit",
            "start_date": start_date,
            "end_date": end_date,
        },
        timeout=10.0
    )
    response.raise_for_status()
    
    return response.json()


def _fetch_archive(start_date: str, end_date: str, reference_year: int = None) -> dict:
    """
    Fetches historical weather from Open-Meteo archive API.
    
    If reference_year is provided, remaps dates to that year (for future date proxies).
    If not provided, uses the actual dates (for past date lookups).
    """
    
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)
    
    if reference_year:
        # Remap to reference year for future date proxies
        archive_start = start.replace(year=reference_year)
        archive_end = end.replace(year=reference_year)
        
    else:
        # Use actual dates for past lookups
        archive_start = start
        archive_end = end
    
    response = httpx.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": MAUI_LATITUDE,
            "longitude": MAUI_LONGITUDE,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
            "temperature_unit": "fahrenheit",
            "start_date": archive_start.isoformat(),
            "end_date": archive_end.isoformat(),
        },
        timeout=10.0
    )
    response.raise_for_status()
    return response.json()


def _fetch_climate_normals(start_date: str, end_date: str) -> dict:
    """Fetches typical seasonal conditions using 2023 as reference year."""
    
    return _fetch_archive(start_date, end_date, reference_year=2023)


def _parse_forecast(data: dict, start_date: str, end_date: str, source: str = "forecast") -> WeatherForecast:
    """Parses Open-Meteo API response into a WeatherForecast model."""
    
    daily = data["daily"]
    
    highs = daily["temperature_2m_max"]
    lows = daily["temperature_2m_min"]
    weather_codes = daily["weathercode"]
    precipitation = daily["precipitation_sum"]
    
    temp_high = round(max(highs))
    temp_low = round(min(lows))
    temp_average = round(sum(highs + lows) / len(highs + lows))
    
    # Check for severe weather
    severe_days = [
        WMO_WEATHER_CODES.get(code, "Unknown")
        for code in weather_codes
        if code in SEVERE_WEATHER_CODES
    ]
    has_severe_weather = len(severe_days) > 0
    
    # Build conditions summary
    most_common_code = max(set(weather_codes), key=weather_codes.count)
    conditions = WMO_WEATHER_CODES.get(most_common_code, "Unknown conditions")
    
    total_rain_mm = sum(precipitation)
    rain_inches = round(total_rain_mm / 25.4, 1)
    
    conditions_summary = (
        f"Based on {source}: {conditions} conditions expected. "
        f"Total precipitation: {rain_inches} inches over the period."
    )
    
    severe_weather_description = None
    if has_severe_weather:
        severe_weather_description = (
            f"Severe weather expected on {len(severe_days)} day(s): "
            f"{', '.join(severe_days)}"
        )
    
    return WeatherForecast(
        date_range=(start_date, end_date),
        temp_average=temp_average,
        temp_high=temp_high,
        temp_low=temp_low,
        conditions_summary=conditions_summary,
        has_severe_weather=has_severe_weather,
        severe_weather_description=severe_weather_description
    )
