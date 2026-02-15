"""Combined MCP server exposing all travel planning tools."""

from fastmcp import FastMCP
from core.mock_data import create_mock_user_profile
from core.weather import get_weather_forecast as fetch_weather_forecast
from core.models import UserProfile, WeatherForecast

mcp = FastMCP("travel-assistant-tools")


@mcp.tool
def get_user_profile() -> UserProfile:
    """
    Returns the user's travel preferences and constraints for trip planning.
    
    WHEN TO USE: Call this FIRST before making any recommendations.
    You need to know their temperature preferences, budget limits,
    and trip duration before searching for flights or hotels.
    """
    return create_mock_user_profile()


@mcp.tool
def get_weather_forecast(start_date: str, end_date: str) -> WeatherForecast:
    """
    Returns weather forecast for Maui for a given date range.
    
    WHEN TO USE: Call this AFTER getting the user profile to check
    if weather matches their temperature preferences.
    
    Args:
        start_date: Trip start date in YYYY-MM-DD format. Example: '2026-03-15'
        end_date: Trip end date in YYYY-MM-DD format. Example: '2026-03-24'
    """
    return fetch_weather_forecast(start_date, end_date)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)