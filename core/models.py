# Import Libraries
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User travel preferences and constraints."""

    temperature_range: tuple[int, int] = Field(
        description = "Preferred temperature range in Fahrenheit (min, max). Example: (70, 85)"
    )

    airfare_budget_preferred: float = Field(
        description = "Preferred maximum for round-trip airfare in USD. Example: 500"
    )    
    
    airfare_budget_max: float = Field(
        description = "Absolute maximum for round-trip airfare in USD. Example: 1000"
    )   

    hotel_price_range: tuple[float, float] = Field(
        description = "Preferred hotel price per night in USD (min, max). Example: (100, 350)"
    )       
    
    trip_duration_days: int = Field(
        default = 7,
        description = "Preferred trip duration in days.",
        ge = 1  # greater than or equal to 1 day
    )

    brand_preferences: list[str] | None = Field(
        default = None,
        description = "Preferred hotel chains. Example: ['Marriott', 'Hilton']"
    )

    safety_preferences: str | None = Field(
        default = None,
        description = "User's safety concerns and preferences. Example: 'avoid hurricane season', 'prefer safe neighborhoods'"
    )

    comfort_preferences: str | None = Field(
        default = None,
        description = "User's comfort requirements. Example: 'must have AC', 'prefer ocean view', 'non-smoking room'"
    )

    additional_notes: str | None = Field(
        default = None,
        description = "Any other travel preferences not covered."
    )

class WeatherForecast(BaseModel):
    """Weather forecast for trip duration"""

    date_range: tuple[str, str] = Field(
        description = "Date range for forecast (start, end). Example: ('2026-03-01', '2026-03-07')"
    )

    temp_average: int = Field(
        description = "Average temperature in Fahrenheit for the date range period. Example: 75"
    )

    temp_high: int = Field(
        description = "Highest temperature in Fahrenheit for the date range period. Example: 90"
    )

    temp_low: int = Field(
        description = "Lowest temperature in Fahrenheit for the date range period. Example: 70"
    )

    conditions_summary: str = Field(
        description = "Summary of general weather conditions and forecast. Example: 'mostly sunny weather with occasional showers', 'mostly sunny weather with severe storms expected towards the end of the week"
    )

    has_severe_weather: bool = Field(
        description = "Whether there's risk of severe weather (hurricanes, tropical storms, etc.)"
    )

    severe_weather_description: str | None = Field(
        default = None,
        description = "Details about severe weather risks if applicable"
    )

class FlightOption(BaseModel):
    """A single flight option from search results."""
    
    # Pricing Details
    price_total: float = Field(
        description = "Total roundtrip price in USD. Example: 739"
    )
    
    # Route Details
    origin_airport: str = Field(
        description = "Departure airport code. Example: 'SFO'"
    )
    
    destination_airport: str = Field(
        description = "Arrival airport code. Example: 'OGG'"
    )
    
    # Timing Details
    departure_datetime: str = Field(
        description = "Departure datetime in ISO format. Example: '2026-03-15T08:30:00'"
    )
    
    return_datetime: str = Field(
        description = "Return datetime in ISO format. Example: '2026-03-22T18:45:00'"
    )
    
    departure_duration_hours: float = Field(
        description = "Outbound flight duration in hours. Example: 5.5"
    )
    
    return_duration_hours: float = Field(
        description = "Return flight duration in hours. Example: 5.5"
    )
    
    # Flight Details
    airline: str = Field(
        description = "Airline name. Example: 'Southwest Airlines', 'American Airlines'"
    )
    
    num_layovers: int = Field(
        description = "Number of layovers."
    )
    
    total_layover_duration_hours: float | None = Field(
        default = None,
        description = "Total layover time in hours, if applicable"
    )
    
    # Flight Characteristics
    is_red_eye: bool = Field(
        description = "Whether departure or return is a red-eye flight (departs after 9pm or arrives before 5am)"
    )
    
    booking_class: str = Field(
        description = "Flight cabin class. Example: 'Economy', 'Premium Economy', 'Business', 'First Class'"
    )
    
    # Baggage Details
    checked_bags_included: int = Field(
        description = "Number of free checked bags included. Example: 1"
    )

class HotelOption(BaseModel):
    """A single hotel option from search results."""
    
    # Dates and pricing
    date_range: tuple[str, str] = Field(
        description = "Check-in and check-out dates in ISO format. Example: ('2026-03-15', '2026-03-22')"
    )
    
    price_per_night: float = Field(
        description = "Nightly hotel rate in USD"
    )
    
    price_total: float = Field(
        description = "Total cost for entire hotel stay in USD"
    )
    
    # Hotel identity
    hotel_name: str = Field(
        description = "Hotel name. Example: 'Grand Wailea Resort'"
    )
    
    brand: str | None = Field(
        default = None,
        description = "Hotel brand/chain if applicable. Example: 'Marriott', 'Hilton', 'None' if not part of a chain/brand."
    )
    
    # Location
    location_area: str = Field(
        description = "Neighborhood or resort area. Example: 'Wailea', 'Kaanapali', 'Lahaina'"
    )
    
    distance_to_beach_miles: float | None = Field(
        default = None,
        description = "Distance to nearest beach in miles"
    )
    
    # Room details
    room_type: str = Field(
        description = "Room category. Example: 'Standard Room', 'Ocean View Suite', 'Deluxe King'"
    )
    
    # Reviews and ratings
    rating: float = Field(
        description = "Average guest rating out of 5.0. Example: 4.5"
    )
    
    review_count: int = Field(
        description = "Total number of guest reviews."
    )
    
    review_summary: str | None = Field(
        default = None,
        description = "Brief summary of review themes. Example: 'Great service, beautiful property, rooms were adequate', 'rude staff, dirty beds, rooms smelled bad'"
    )
    
    # Amenities
    amenities: list[str] = Field(
        description = "Available amenities. Example: ['Free WiFi', 'Pool', 'Gym', 'Continental Breakfast', 'Ocean View', 'Spa', 'Kayak Rental']"
    )

class Recommendation(BaseModel):
    """Final travel recommendation with supporting details."""
    
    # Core recommendation
    recommendation_level: str = Field(
        description = "Overall recommendation: 'recommended', 'recommended with caveats', or 'not_recommended'"
    )
    
    recommended_date_range: tuple[str, str] = Field(
        description = "Recommended travel dates (check-in, check-out). Example: ('2026-03-15', '2026-03-22')"
    )
    
    # Reasoning
    reasoning: str = Field(
        description = "Complete explanation covering weather suitability, budget fit, and overall value"
    )
    
    # Specific recommendations
    recommended_flights: list[FlightOption] = Field(
        description = "Top 2-3 flight options ranked by best fit to user preferences"
    )
    
    recommended_hotels: list[HotelOption] = Field(
        description = "Top 2-3 hotel options ranked by best fit to user preferences"
    )
    
    # Weather context
    weather_forecast: WeatherForecast = Field(
        description = "Weather forecast for recommended dates"
    )
    
    # Alternatives and caveats
    alternative_date_ranges: list[tuple[str, str]] | None = Field(
        default = None,
        description = "Alternative date ranges if flexibility needed. Example: [('2026-04-01', '2026-04-08')]"
    )
    
    important_considerations: list[str] | None = Field(
        default = None,
        description = "Important warnings or considerations. Example: ['Hurricane season starts June 1', 'Spring break prices are 40% higher']"
    )