"""Maui Travel Agent - Main orchestration logic."""

import asyncio
import os
from dotenv import load_dotenv

# Google ADK imports (correct for version 1.24.1)
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from mcp import StdioServerParameters

load_dotenv()


def get_model_config():
    """Determines the model configuration based on LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "gemini")
    
    if provider == "anthropic":
        return {
            "model": "claude-haiku-4-5",
            "provider": "anthropic"
        }
    elif provider == "ollama":
        return {
            "model": os.getenv("OLLAMA_MODEL", "deepseek-r1:7b"),
            "base_url": os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            "provider": "ollama"
        }
    else:
        return {
            "model": "gemini-2.0-flash",
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "provider": "gemini"
        }


async def run_agent():
    """Creates and runs the Maui travel planning agent."""

    config = get_model_config()
    print(f"Using LLM: {config['provider']} - {config['model']}\n")

    # --- Step 1: Create the MCP Toolset ---
    # StdioServerParameters tells ADK how to LAUNCH your MCP server
    mcp_server_params = StdioServerParameters(
        command="python",
        args=["-m", "tools.user_profile_tool"],
    )

    # MCPToolset connects ADK to your MCP server
    mcp_toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=mcp_server_params
        )
    )

    # --- Step 2: Create the Agent ---
    agent = LlmAgent(
        model=config["model"],
        name="maui_travel_agent",
        description="A travel planning agent specializing in Maui, Hawaii",
        tools=[mcp_toolset],
        instruction="""You are an expert travel planning assistant specializing in Maui, Hawaii.

Your goal: Help users determine if it's a good time to visit Maui based on their preferences.

CRITICAL WORKFLOW (follow this EXACTLY):
1. ALWAYS start by calling get_user_profile to understand their preferences
2. Analyze the profile to understand what "good time" means for THIS user
3. Based on their preferences, reason about:
   - Temperature preferences vs typical Maui weather
   - Budget constraints
   - Trip duration
   - Any specific requirements (ocean view, no red-eye flights, etc.)

Be thoughtful and explain your reasoning step by step.
Don't make assumptions - use the tools available to you."""
    )

    # --- Step 3: Set Up Session and Runner ---
    # Session service manages conversation state (ADK's "memory")
    session_service = InMemorySessionService()

    # Create a session (one conversation)
    session = await session_service.create_session(
        app_name="maui_travel_agent",
        user_id="user_001"
    )

    # Runner orchestrates the agent execution loop
    runner = Runner(
        agent=agent,
        app_name="maui_travel_agent",
        session_service=session_service
    )

    # --- Step 4: Run the Agent ---
    user_query = "Is it a good time to go to Maui?"
    print(f"User: {user_query}\n")
    print("Agent is thinking...\n")
    print("=" * 60 + "\n")

    # Create the message in ADK's format
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_query)]
    )

    # Run the agent and stream events
    async for event in runner.run_async(
        user_id="user_001",
        session_id=session.id,
        new_message=message
    ):
        # Print agent responses as they come in
        if event.is_final_response():
            print("🤖 Agent Response:\n")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
        
        # Show tool calls (so you can see the agent working)
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
        print("2. Check LLM_PROVIDER is set correctly")


if __name__ == "__main__":
    main()