from fastmcp import FastMCP
from core.models import UserProfile
from core.mock_data import create_mock_user_profile

mcp = FastMCP("travel-assistant-tools")


@mcp.tool
def get_user_profile() -> UserProfile:
    """
    Returns the User's travel preferences and constraints for trip planning.
    
    This includes temperature preferences, budget constraints, trip duration,
    hotel brand preferences, and any specific comfort or safety requirements.
    """
    # Just call the core logic
    return create_mock_user_profile()


if __name__ == "__main__":

    # Create mock User profile
    profile = create_mock_user_profile()
    
    # Then start the server
    mcp.run(transport="stdio")