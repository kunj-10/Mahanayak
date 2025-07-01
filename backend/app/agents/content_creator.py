from pydantic_ai import Agent
from dotenv import load_dotenv
from app.utils.prompts  import CONTENT_CREATION_SYSTEM_PROMPT

load_dotenv()

content_creation_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=CONTENT_CREATION_SYSTEM_PROMPT,
    retries=2,
)

@content_creation_agent.tool_plain
def post_on_linkedin(linkedin_user: str, content: str) -> dict:
    """
    Posts on linkedin

    Args:
    - linkedin_user: the username of the account to be posted.
    - content: the content to be posted

    Return:
    A dictionary containing the metadata of the post
    """

    # Linkedin API Call

    return {
        "message": "Posted Successfully"
    }

@content_creation_agent.tool_plain
def post_on_x(X_user: str, content: str) -> dict:
    """
    Tweets on X

    Args:
    - x_user: the X username of the account to be posted.
    - content: the content to be posted

    Return:
    A dictionary containing the metadata of the post
    """

    # X API Call

    return {
        "message": "Posted Successfully"
    }

# Main function to demonstrate usage
async def main():
    # Create a sample event based on user input
    # user_input = "I want to plan the river clean up event to may 29 near bhavnagar beach at morning 11 AM. Create a linkedin post regarding it.please give me posts and post is only for the volunteer "

    user_input = "Tell me all the inputs you need."

    print("User Input: ", user_input)
    
    try:
        response = await content_creation_agent.run(user_input)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())