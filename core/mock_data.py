# Mock data for testing the travel agent

from core.models import UserProfile

def create_mock_user_profile() -> UserProfile:
    """
    Creates a mock user profile for testing.
    
    This represents User's travel preferences and constraints.
    """
    return UserProfile(
        temperature_range = (70, 75),
        airfare_budget_preferred = 500,
        airfare_budget_max = 1000,
        home_airport = 'SEA',
        hotel_price_range = (100, 300),
        trip_duration_days = 9,
        brand_preferences = ["Marriott"],
        safety_preferences = None,
        comfort_preferences = "Prefer ocean view, require non-smoking room, prefer gym ameneties, prefer being located near more natural scenery than touristy areas",
        additional_notes = "no red-eye flights"
    )