from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils.sarthi_prompt import  CONTENT_CREATION_PROMPT

load_dotenv()

volunteer_content_generation_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=CONTENT_CREATION_PROMPT,
    retries=2,
)

## Tools as per requirements

async def main():
    user_input = ""

    print("User Input: ", user_input)
    
    try:
        response = await volunteer_content_generation_agent.run(user_input)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())