# Import Libraries
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User travel preferences and constraints."""

    # Define structured preferences
    temperature_range: tuple[int, int] = Field(
        description = "Preferred temperature range in Fahrenheit (min, max). Example: (70, 85)")

    airfare_budget_preferred: float | None = Field(
        default = None, 
        description = "Preferred maximum for round-trip airfare in USD. Example: 500")    
    
    airfare_budget_max: float | None = Field(
        default = None,
        description = "Absolute maximum for round-trip airfare in USD. Example: 1000")   

    hotel_price_range: tuple[float, float] | None = Field(
        default = None,
        description = "Preferred hotel price per night in USD (min, max). Example: (100, 350)")       
    
    trip_duration_days: int = Field(
        default = 7,
        description = "Preferred trip duration in days.",
        ge = 1)  # greater than or equal to 1 day

    brand_preferences: list[str] | None = Field(
        default = None,
        description = "Preferred hotel chains. Example: ['Marriott', 'Hilton']")


    # Define unstructured preferences 
    safety_preferences: str | None = Field(
        default = None,
        description = "User's safety concerns and preferences. Example: 'avoid hurricane season', 'prefer safe neighborhoods'")

    comfort_preferences: str | None = Field(
        default = None,
        description = "User's comfort requirements. Example: 'must have AC', 'prefer ocean view', 'non-smoking room'")

    additional_notes: str | None = Field(
        default = None,
        description = "Any other travel preferences not covered.")
