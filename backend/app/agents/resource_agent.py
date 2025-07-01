from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from dotenv import load_dotenv
from app.utils.prompts  import RESOURCE_AGENT_SYSTEM_PROMPT
import os
from serpapi import GoogleSearch

load_dotenv()

@dataclass
class ResourceDeps:
    # API key for web search
    SERPAPI_API_KEY: str

resource_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=RESOURCE_AGENT_SYSTEM_PROMPT,
    retries=2,
    deps_type = ResourceDeps
)

@resource_agent.tool
def get_product_list(ctx: RunContext[ResourceDeps], query: str, location: str = "New Delhi, India", gl: str = "in") -> dict:
    """
        Fetch a list of products along with prices for comparison across various platforms.

    Args:
    - ctx: the context
    - query: The search query for the product.
    - location: Location to base the search from (default: "New Delhi, India").
    - gl: Google country code (default: "in").

    Return:
    A dictionary containing:
    - message: A short description of the result status.
    - data: A list (maximum 8) of products, each with:
        - title: Name of the product.
        - source: Online platform or retailer (e.g., Amazon, Flipkart, Zepto).
        - price: The listed price (extracted as a number).
        - link: A direct product page link (Google Shopping product link).
    """

    print("get_product_list tool call")
    print(f"Query: {query}")
    print(f"Location: {location}")
    print(f"GL: {gl}")
    print("\n-----------------------------------------------------------\n")

    results_list = []

    params = {
        "engine": "google_shopping",
        "q": query,
        "location": location,
        "gl": gl,
        "api_key": ctx.deps.SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "shopping_results" not in results:
        return {
            "message": f"No shopping results found for query: {query}",
            "data": []
        }

    for result in results["shopping_results"]:
        price = result.get("extracted_price")
        if price is not None:
            results_list.append({
                "title": result.get("title", "N/A"),
                "source": result.get("source", "N/A"),
                "price": price,
                "link": result.get("product_link", "N/A")
            })
    
    results_list.sort(key=lambda x: x["price"])
    best_products = results_list[:8]

    return {
        "message": f"Found {len(best_products)} products for '{query}'",
        "data": best_products
    }

# Main function to demonstrate usage
async def main():
    # Create a sample event based on user input
    # user_input = "We are organizing a beach cleaning drive called 'Clean Pune Initiative' on 21st June, 2025 in Vadgaon, Pune - 400101. Around 100 volunteers are expected to participate. We'll need to arrange some supplies like party poppers to celebrate the event's conclusion. I'm John, and my mobile number is 1234567890. Can you help compare prices of party poppers available online in Pune, India or nearby, and suggest a few affordable options from different platforms?"
        
    user_input = "Tell me all the inputs you need."


    print("User Input: ", user_input)
    
    try:
        dependencies = ResourceDeps(
            SERPAPI_API_KEY=os.getenv("SERPAPI_API_KEY")
        )
        response = await resource_agent.run(user_input, deps=dependencies)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
# to run: uv run -m app.agents.resource_agent
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())