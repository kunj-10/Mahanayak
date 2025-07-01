from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils import ORGANISER_BOT_SYSTEM_PROMPT

load_dotenv()

organiser_bot = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=ORGANISER_BOT_SYSTEM_PROMPT,
    retries=2,
)

async def main():
    # Create a sample event based on user input
    user_input = "What all things can the system do?"

    print("User Input: ", user_input)
    
    try:
        # response = await organiser_bot.run(user_input)
        # ptr = response.output
        print("Agent Response:")

        async with organiser_bot.run_stream(user_input) as result:
            async for chunk in result.stream_text(delta=True):
                print(chunk, end=" | ")
                
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())