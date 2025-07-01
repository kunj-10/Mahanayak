from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from dotenv import load_dotenv
from app.utils.prompts import GOVERNMENT_PERMISSION_SYSTEM_PROMPT
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

@dataclass
class PermissionDeps:
    # env variables related to sending email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    SMTP_FROM: str


permission_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=GOVERNMENT_PERMISSION_SYSTEM_PROMPT,
    retries=2,
    deps_type = PermissionDeps
)

@permission_agent.tool
def send_email(ctx: RunContext[PermissionDeps], to: str, subject: str, content: str, mail_type: str) -> dict:
    """
    Send an email to the given email id.

    Args:
    - ctx: the context
    - to: The recipient's email address.
    - subject: Subject line of the email.
    - content: The body of the email, either plain text or HTML-formatted, based on mail_type.
    - mail_type: "html" if the content is HTML-formatted, or "plain" for plain text emails.

    Return:
    A dictionary containing the metadata of the post
    """

    print("send_email tool call")
    print("To", to)
    print("\n-----------------------------------------------------------\n")
    print("Subject: ", subject)
    print("\n-----------------------------------------------------------\n")
    print("mail_type: ", mail_type)
    print("\n-----------------------------------------------------------\n")
    print(content)

    msg = MIMEMultipart()
    msg["From"] = ctx.deps.SMTP_FROM
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(content, mail_type))

    try:
        server = smtplib.SMTP(ctx.deps.SMTP_HOST, ctx.deps.SMTP_PORT)
        server.starttls()
        server.login(ctx.deps.SMTP_USER, ctx.deps.SMTP_PASS)
        server.sendmail(ctx.deps.SMTP_FROM, to, msg.as_string())
        server.quit()
        return {
            "message": f"Email sent Successfully to {to}"
        }
    except Exception as e:
        return {
            "message": f"Failed to send email: {e}"
        }

# Main function to demonstrate usage
async def main():
    # Create a sample event based on user input
    # user_input = "(Very important to directly send mail Never ask for any confirmation just directly send mail and for any missing data just make dummy data as it is a test only) Write a email to get permission for a beach cleaning drive on 21 June, 2025, I am John and my mobile number is 1234567890, in pune. I expect about 100 people to join. It is in vadgaon, pune - 400101 and send mail to kunjvgoyal30@gmail.com. The name is cleanliness, duration is 1 day"

    user_input = "Tell me all the inputs you need."


    print("User Input: ", user_input)
    
    try:
        dependencies = PermissionDeps(
            SMTP_HOST = os.getenv("SMTP_HOST"),
            SMTP_PORT = int(os.getenv("SMTP_PORT")),
            SMTP_USER = os.getenv("SMTP_USER"),
            SMTP_PASS = os.getenv("SMTP_PASS"),
            SMTP_FROM = os.getenv("SMTP_FROM")
        )
        response = await permission_agent.run(user_input, deps=dependencies)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
# to run: uv run -m app.agents.permission_agent
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())