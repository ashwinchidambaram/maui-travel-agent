from fastmcp import FastMCP
from core.models import WeatherForecast
from core.weather import get_weather_forecast as fetch_weather_forecast

mcp = FastMCP("travel-assistant-tools")


@mcp.tool
def get_weather_forecast(start_date: str, end_date: str) -> WeatherForecast:
    """
    Returns the Weather Forecast and Summary for the User's trip timeframe. 

    WHEN TO USE: Call this AFTER getting the user profile to understand
    their temperature preferences. Use the user's trip_duration_days to
    determine the date range. Requires start_date and end_date in 
    YYYY-MM-DD format.

    Args:
        start_date: Trip start date in YYYY-MM-DD format. Example: '2026-03-15'
        end_date: Trip end date in YYYY-MM-DD format. Example: '2026-03-24'
    
    Returns overall weather forecast including: average temperature for trip,
    highest temperature during the date range, lowest temperature for the 
    date range, overall weather conditions summary, whether there will be
    severe weather, and if so, what extreme weather is expected. 
    """

    # Just call the core logic
    return get_weather_forecast(start_date, end_date)


if __name__ == "__main__":
    print("Testing weather forecast...")
    forecast = fetch_weather_forecast("2026-03-15", "2026-03-24")
    print(forecast.model_dump_json(indent=2))
    
    print("\nStarting MCP server...")
    mcp.run(transport="stdio")