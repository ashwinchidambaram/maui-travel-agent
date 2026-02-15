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

@mcp.tool
def search_flights(origin: str, departure_date: str, return_date: str) -> str:
    """
    Returns available flight options from origin city to Maui (OGG).

    Compare prices against the user's airfare_budget_preferred (soft target)
    and airfare_budget_max (hard ceiling). A flight slightly over preferred
    but under max is acceptable if it offers better comfort or convenience.

    WHEN TO USE: Call AFTER get_user_profile. Use the user's home_airport
    as origin. Use today as departure_date and today + trip_duration_days
    as return_date.

    Args:
        origin: Departure airport code from user profile. Example: 'SEA'
        departure_date: Outbound flight date in YYYY-MM-DD format
        return_date: Return flight date in YYYY-MM-DD format

    Returns a concise summary of 3 flight options with price, schedule,
    and flags relevant to user preferences (red-eye, layovers, baggage).
    """
    return f"""FLIGHT OPTIONS: {origin} → OGG ({departure_date} to {return_date})

            Option 1 - Budget/Layover:
            Alaska Airlines | $410 round-trip
            Outbound: 6:00am → 2:30pm (8.5hrs, 1 stop PDX)
            Return: 10:00am → 8:30pm (10.5hrs, 1 stop)
            Red-eye: No | Bags: 1 free checked bag

            Option 2 - Best Value/Direct:
            Alaska Airlines | $520 round-trip
            Outbound: 8:00am → 2:00pm (6hrs, direct)
            Return: 3:30pm → 10:30pm (6hrs, direct)
            Red-eye: No | Bags: 1 free checked bag

            Option 3 - Red-eye/Direct:
            Hawaiian Airlines | $480 round-trip
            Outbound: 10:00pm → 4:00am+1 (6hrs, direct)
            Return: 11:30pm → 5:30am+1 (6hrs, direct)
            Red-eye: YES | Bags: 2 free checked bags
            """


@mcp.tool
def search_hotels(check_in: str, check_out: str) -> str:
    """
    Returns available hotel options in Maui for the given dates.

    WHEN TO USE: Call AFTER get_user_profile. Use the same dates as
    the flight search. Compare results against user's hotel_price_range,
    comfort_preferences, and brand_preferences.

    Args:
        check_in: Hotel check-in date in YYYY-MM-DD format
        check_out: Hotel check-out date in YYYY-MM-DD format

    Returns a concise summary of 3 hotel options with nightly rate,
    location, amenities, and flags relevant to user preferences.
    """
    return f"""HOTEL OPTIONS IN MAUI ({check_in} to {check_out})

            Option 1 - Budget/Functional:
            Maui Seaside Hotel | Kahului (near airport, local neighborhood)
            $145/night | Non-smoking: Yes
            Amenities: Free WiFi, Pool, Free Parking
            No gym available | No ocean view
            Rating: 3.8/5 (420 reviews)
            Note: Clean and affordable, close to local restaurants and shops

            Option 2 - Best Fit/Natural Setting:
            Kaanapali Beach Hotel | Kaanapali (natural beach, less commercialized)
            Brand: Marriott Autograph Collection
            $235/night | Non-smoking: Yes
            Amenities: Free WiFi, Pool, Gym, Direct Beach Access, Restaurant
            Ocean view: Yes (partial)
            Rating: 4.4/5 (1,240 reviews)
            Note: Authentic Hawaiian atmosphere, excellent snorkeling, away from tourist strip

            Option 3 - Luxury/Over Budget:
            Grand Wailea Resort | Wailea (upscale resort area)
            $580/night | Non-smoking: Yes
            Amenities: Free WiFi, Multiple Pools, Full Gym, Spa, 3 Restaurants, Private Beach
            Ocean view: Yes (full)
            Rating: 4.7/5 (3,100 reviews)
            Note: World-class but significantly over budget
            """

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)