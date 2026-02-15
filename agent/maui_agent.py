"""Maui Travel Agent - Main orchestration logic."""

import asyncio
import os
from datetime import date
from dotenv import load_dotenv

# Google ADK imports
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

load_dotenv()


def get_model_config():
    """
    Returns model config dict based on LLM_PROVIDER env variable.

    Returns a dict with:
      - 'model': LiteLlm object (for Anthropic/Ollama) or string (for Gemini)
      - 'label': human-readable label for logging
    """
    provider = os.getenv("LLM_PROVIDER", "gemini")

    if provider == "anthropic":
        return {
            "model": LiteLlm(model="claude-haiku-4-5"),
            "label": "Anthropic - claude-haiku-4-5"
        }
    elif provider == "ollama":
        ollama_model = os.getenv("OLLAMA_MODEL", "deepseek-r1:7b")
        return {
            "model": LiteLlm(model=f"ollama_chat/{ollama_model}"),
            "label": f"Ollama - {ollama_model}"
        }
    else:
        return {
            "model": "gemini-2.0-flash",
            "label": "Gemini - gemini-2.0-flash"
        }


def create_mcp_toolset():
    """
    Creates MCPToolset that connects to our HTTP MCP server.
    Requires tools/server.py to be running on port 9000.
    """
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url="http://127.0.0.1:9000/mcp"
        )
    )


async def run_agent():
    """Creates and runs the Maui travel planning agent."""

    # --- Step 1: Get model config ---
    config = get_model_config()
    print(f"Using LLM: {config['label']}\n")

    # --- Step 2: Build instruction with today's date injected ---
    today = date.today().isoformat()

    instruction = f"""You are an expert travel planning assistant specializing in Maui, Hawaii.
    
        Today's date is {today}.

        Your goal: Help users determine if it's a good time to visit Maui based on their preferences.

        CRITICAL WORKFLOW - follow these stages in exact order:

        STAGE 1 - EPISTEMIC REFLECTION:
        Recognize the question is underspecified. You need the user's preferences
        before you can answer. Do not guess or assume anything.

        STAGE 2 - USER PROFILE:
        Call get_user_profile. Note their:
        - temperature_range (for weather evaluation)
        - airfare_budget_preferred and airfare_budget_max (for flight filtering)
        - hotel_price_range (for hotel filtering)
        - trip_duration_days (to calculate return date)
        - home_airport (as origin for flight search)
        - comfort_preferences (ocean view, gym, non-smoking, etc.)
        - additional_notes (red-eye preference, etc.)

        STAGE 3 - WEATHER:
        Call get_weather_forecast with:
        - start_date = today ({today})
        - end_date = today + trip_duration_days

        STAGE 4 - FLIGHTS:
        Call search_flights with:
        - origin = home_airport from profile
        - departure_date = today ({today})
        - return_date = today + trip_duration_days
        Identify which options fit budget and preferences. Note why others are rejected.

        STAGE 5 - HOTELS:
        Call search_hotels with the same date range.
        Identify which options fit budget and comfort preferences.
        Note why others are rejected.

        STAGE 6 - SYNTHESIS:
        Produce a final recommendation that includes:
        - A clear yes/no/conditional recommendation
        - Recommended time window with specific dates
        - Best flight option and why
        - Best hotel option and why
        - 1-2 alternative options if the primary has trade-offs
        - Brief explanation of rejected options
        - Any important caveats (weather, budget stretch, etc.)

        Be explicit about your reasoning at every stage. 
        Be friendly and excited, like a helpful travel agent
        that wants to ensure that their clinet has the best
        possible travel experience.
        """

    # --- Step 3: Create MCP toolset ---
    mcp_toolset = create_mcp_toolset()

    # --- Step 4: Create the agent ---
    agent = LlmAgent(
        model=config["model"],
        name="maui_travel_agent",
        description="A travel planning agent specializing in Maui, Hawaii",
        tools=[mcp_toolset],
        instruction=instruction
    )

    # --- Step 5: Set up session and runner ---
    session_service = InMemorySessionService()

    session = await session_service.create_session(
        app_name="maui_travel_agent",
        user_id="user_001"
    )

    runner = Runner(
        agent=agent,
        app_name="maui_travel_agent",
        session_service=session_service
    )

    # --- Step 6: Run the agent ---
    user_query = "Is it a good time to go to Maui?"
    print(f"User: {user_query}\n")
    print("Agent is thinking...\n")
    print("=" * 60 + "\n")

    message = types.Content(
        role="user",
        parts=[types.Part(text=user_query)]
    )

    async for event in runner.run_async(
        user_id="user_001",
        session_id=session.id,
        new_message=message
    ):
        if event.is_final_response():
            print("🤖 Agent Response:\n")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)

        elif event.get_function_calls():
            for call in event.get_function_calls():
                print(f"🔧 Calling tool: {call.name}")

        elif event.get_function_responses():
            print(f"✅ Tool returned data\n")


def main():
    """Entry point for the Maui travel agent."""

    print("🌴 Maui Travel Agent Starting...\n")
    print("=" * 60 + "\n")

    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\n\nAgent stopped.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Check GOOGLE_API_KEY is set in .env")
        print("2. Make sure tools/server.py is running: python -m tools.server")
        print("3. Check LLM_PROVIDER is set correctly")


if __name__ == "__main__":
    main()
