from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from dotenv import load_dotenv
from app.utils.prompts  import VOLUNTEER_GUIDELINES
from xhtml2pdf import pisa
import markdown2
import os
from supabase import create_client
from supabase import Client

load_dotenv()

@dataclass
class VolunteerGuidelinesDeps:
    SUPABASE_API_KEY: str
    SUPABASE_PROJECT_URL: str

volunteer_guidelines_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=VOLUNTEER_GUIDELINES,
    retries=2,
    deps_type = VolunteerGuidelinesDeps
)

@volunteer_guidelines_agent.tool
def generate_pdf(ctx: RunContext[VolunteerGuidelinesDeps], content: str, mode: str = "md", filename: str = "output.pdf") -> dict:
    """
    Generate a PDF from markdown/html and upload to Supabase Storage.

    Args:
    - content: The input content in markdown or HTML format.
    - mode: Set to 'md' for Markdown or 'html' for raw HTML (default: 'md').
    - filename: Desired output file name (default: 'output.pdf').

    Return:
    - dict: {
        "message": status message,
        "pdf_path": absolute path of the saved PDF (if successful)
      }
    """
    print("Generating PDF...")
    print(f"Mode: {mode}")
    print(f"Output File: {filename}")

    if mode not in {"html", "md"}:
        return {"error": "Mode must be 'html' or 'md'"}

    if mode == "md":
        content = markdown2.markdown(content)

    try:
        with open(filename, "wb") as f:
            status = pisa.CreatePDF(content, dest=f)
        if status.err:
            return {"message": "PDF generation failed rendering error."}
    except Exception as e:
        return {"message": f"PDF generation failed: {e}"}

    try:
        supabase: Client = create_client(ctx.deps.SUPABASE_PROJECT_URL, ctx.deps.SUPABASE_API_KEY)
        bucket="kakushin"
        with open(filename, "rb") as f:
            path = f"{filename}"
            result = supabase.storage.from_(bucket).upload(
                path,
                f,
                file_options={
                    "content-type": "application/pdf",
                    "x-upsert": "true"
                }
            )
        public_url = supabase.storage.from_(bucket).get_public_url(path)
        return {"message": "Uploaded successfully", "pdf_url": public_url}
    except Exception as e:
        return {"message": f"Upload failed: {e}"}

async def main():
    # Create a sample event based on user input
    # user_input = "This is a test. Do not ask for confirmation. If any required data is missing, fill in dummy data. Generate a PDF report titled 'Volunteer Supply Report' for a beach cleaning drive happening on 21st June 2025 at Vadgaon Beach, Pune - 400101. The event is organized by John Doe, mobile number 1234567890, with around 100 volunteers expected. The report should list required items such as trash bags, gloves, water bottles, and cola cans along with their estimated quantities and prices. The file should be saved as supply_report.pdf."

    user_input = "Tell me all the inputs you need."

    print("User Input: ", user_input)
    
    try:

        dependencies = VolunteerGuidelinesDeps(
            SUPABASE_API_KEY=os.getenv("SUPABASE_API_KEY"),
            SUPABASE_PROJECT_URL=os.getenv("SUPABASE_PROJECT_URL")
        )

        response = await volunteer_guidelines_agent.run(user_input, deps=dependencies)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())