from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils.sarthi_prompt import  DISCOVERY_REGISTRATION_PROMPT

load_dotenv()

event_registration = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=DISCOVERY_REGISTRATION_PROMPT,
    retries=2,
)

## Tools as per requirements

async def main():
    user_input = ""

    print("User Input: ", user_input)
    
    try:
        response = await event_registration.run(user_input)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())