from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils import ORGANISER_REASONER_SYSTEM_PROMPT

load_dotenv()

organiser_reasoner = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=ORGANISER_REASONER_SYSTEM_PROMPT,
    retries=2,
)

async def main():
    # Create a sample event based on user input
    user_input = "Create a Linkedin post regarding the event and a google form to get the feedback"

    print("User Input: ", user_input)
    
    try:
        import json
        response = await organiser_reasoner.run(user_input)
        ptr = json.loads(response.output)
        print("Agent Response:", ptr)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())