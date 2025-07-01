from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils import INFO_GATHERER_SYSTEM_PROMPT
from typing_extensions import TypedDict

load_dotenv()

class Response(TypedDict):
    info_gathered: bool
    message: str

info_gatherer = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=INFO_GATHERER_SYSTEM_PROMPT,
    retries=2,
    output_type=Response
)

async def main():
    # Create a sample event based on user input
    user_input = "I want to create a linkedin post for impact showcase that focuses on environment cleaning and my username is luv29. ['Content Creation Agent']"

    print("User Input: ", user_input)
    
    try:
        response = await info_gatherer.run(user_input)
        print(response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())