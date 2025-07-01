from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils import PROMPT_GENERATOR_SYSTEM_PROMPT
from typing_extensions import TypedDict

load_dotenv()

prompt_generator = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=PROMPT_GENERATOR_SYSTEM_PROMPT,
    retries=2
)

async def main():
    # Create a sample event based on user input
    user_input = "Event name is cleanliness, it is a beach cleaning drive in mumbai on 25 june. I want to create a linkedin post for impact showcase that focuses on environment cleaning and my username is luv29. ['Content Creation Agent']"

    print("User Input: ", user_input)
    
    try:
        import json
        response = await prompt_generator.run(user_input)
        print(response.output[7:-3])
        ptr = json.loads(response.output[7:-3])
        print(ptr)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())