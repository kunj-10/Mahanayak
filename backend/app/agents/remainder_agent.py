from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from dotenv import load_dotenv
from app.utils.prompts  import REMAINDER_AGENT_SYSTEM_PROMPT
from app.services.user_service import UserService
from app.services.event_service import EventService
from app.services.auth.google import GoogleAuth
from typing import Optional
import httpx
import os

load_dotenv()

@dataclass
class RemainderDeps:
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str


remainder_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=REMAINDER_AGENT_SYSTEM_PROMPT,
    retries=2,
    deps_type = RemainderDeps
)

@remainder_agent.tool
def create_google_calender_event(
    ctx: RunContext[RemainderDeps],
    event_id: str,
    user_id: str,
    reminder_minutes: Optional[int] = 30,
    can_guests_see_others: Optional[bool] = True,
    can_guests_invite_others: Optional[bool] = False,
    reminder_method: Optional[str] = "popup"
) -> dict:
    """
    Creates a Google Calendar event for an existing event in the database
    
    Args:
    - ctx: The context containing dependencies
    - event_id: MongoDB ObjectId of the event to create calendar reminder for
    - user_id: MongoDB ObjectId of the user creating the calendar event
    - reminder_minutes: How many minutes before the event to send reminder (default: 30)
    - can_guests_see_others: Whether attendees can see other attendees (default: True)
    - can_guests_invite_others: Whether attendees can invite additional people (default: False)
    - reminder_method: Method for reminder - "popup", "email", or "sms" (default: "popup")
    
    Returns:
    A dictionary containing:
    - `message`: Human-readable message indicating the result
    - `event_link` (optional): Direct URL to the created Google Calendar event
    - `auth_url` (optional): Google OAuth URL if user needs to authenticate
    """
    
    if not event_id:
        return {"message": "Missing event_id parameter"}
    if not user_id:
        return {"message": "Missing user_id parameter"}
    if reminder_minutes is not None and reminder_minutes < 0:
        return {"message": "reminder_minutes must be non-negative"}
    if reminder_method is not None and reminder_method not in ["popup", "email", "sms"]:
        return {"message": "reminder_method must be 'popup', 'email', or 'sms'"}
    if can_guests_see_others is not None and not isinstance(can_guests_see_others, bool):
        return {"message": "can_guests_see_others must be a boolean"}
    if can_guests_invite_others is not None and not isinstance(can_guests_invite_others, bool):
        return {"message": "can_guests_invite_others must be a boolean"}
    
    reminder_minutes = reminder_minutes or 30
    can_guests_see_others = can_guests_see_others if can_guests_see_others is not None else True
    can_guests_invite_others = can_guests_invite_others if can_guests_invite_others is not None else False
    reminder_method = reminder_method or "popup"
    
    try:
        
        event = EventService.get_event_by_id(event_id)
        if not event:
            return {"message": f"Event with ID '{event_id}' not found"}
        
        
        user = UserService.get_user_by_id(user_id)
        if not user:
            return {"message": f"User with ID '{user_id}' not found"}
        
        
        access_token = user.get("google_access_token")
        refresh_token = user.get("google_refresh_token")
        if not access_token:
            auth = GoogleAuth(
                client_id=ctx.deps.GOOGLE_CLIENT_ID,
                client_secret=ctx.deps.GOOGLE_CLIENT_SECRET,
                redirect_uri=ctx.deps.GOOGLE_REDIRECT_URI
            )
            return {
                "message": "User not authenticated with Google Calendar",
                "auth_url": auth.get_authorization_url()
            }
        
        
        attendees = []
        for event_user in event.get("users", []):
            if event_user.get("email"):
                attendees.append({"email": event_user["email"]})
        
        
        event_time = event.get("time")
        if isinstance(event_time, str):
            start_time = event_time
        else:
            start_time = event_time.isoformat()
        
        from datetime import datetime, timedelta
        import dateutil.parser
        
        start_datetime = dateutil.parser.parse(start_time)
        end_datetime = start_datetime + timedelta(hours=1)
        end_time = end_datetime.isoformat()
        
        description_parts = []
        
        if event.get("description"):
            description_parts.append(f"Description: {event['description']}")
        
        if event.get("guidelines"):
            description_parts.append(f"\nGuidelines: {event['guidelines']}")
                
        event_description = "\n".join(description_parts)
        
        calendar_event_data = {
            "summary": event.get("name", "Event"),
            "description": event_description,
            "location": event.get("location", ""),
            "start": {
                "dateTime": start_time,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end_time,
                "timeZone": "UTC"
            },
            "attendees": attendees,
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {"method": reminder_method, "minutes": reminder_minutes}
                ]
            },
            "guestsCanSeeOtherGuests": can_guests_see_others,
            "guestsCanInviteOthers": can_guests_invite_others
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = httpx.post(
            "https://www.googleapis.com/calendar/v3/calendars/primary/events",
            headers=headers,
            json=calendar_event_data
        )
        if response.status_code == 401 and refresh_token:
            auth = GoogleAuth(
                client_id=ctx.deps.GOOGLE_CLIENT_ID,
                client_secret=ctx.deps.GOOGLE_CLIENT_SECRET,
                redirect_uri=ctx.deps.GOOGLE_REDIRECT_URI
            )
            response_data = asyncio.run(auth.refresh_access_token(refresh_token))
            new_access_token = response_data.get("access_token") if response_data else None

            if new_access_token:
                UserService.update_user(user_id, {"google_access_token": new_access_token})
                headers["Authorization"] = f"Bearer {new_access_token}"
                response = httpx.post(
                    "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                    headers=headers,
                    json=calendar_event_data
                )
            else:
                return {
                    "message": "User not authenticated with Google",
                    "auth_url": auth.get_authorization_url()
                }

        response.raise_for_status()
        calendar_event = response.json()
        
        EventService.update_event(event_id, {
            "google_calendar_event_id": calendar_event.get("id"),
            "google_calendar_link": calendar_event.get("htmlLink")
        })
        
        return {
            "message": f"Calendar event created successfully for '{event.get('name')}' with {len(attendees)} attendees. Reminder set for {reminder_minutes} minutes before via {reminder_method}.",
            "event_link": calendar_event.get("htmlLink"),
            "attendees_count": len(attendees),
            "reminder_settings": {
                "minutes_before": reminder_minutes,
                "method": reminder_method,
                "can_guests_see_others": can_guests_see_others,
                "can_guests_invite_others": can_guests_invite_others
            }
        }
        
    except httpx.HTTPStatusError as http_err:
        error_detail = ""
        try:
            error_detail = http_err.response.json().get("error", {}).get("message", "")
        except:
            error_detail = http_err.response.text
        
        return {"message": f"Google Calendar API error: {error_detail}"}
        
    except Exception as e:
        return {"message": f"Failed to create calendar event: {str(e)}"}
    
@remainder_agent.tool
def get_google_auth_link(ctx: RunContext[RemainderDeps]):
    """
    Gives a Link which can be used to authorise users that have not been authorised by Google

    Args:
    - ctx: The context containing dependencies
    
    Returns:
    A dictionary containing:
    - `auth_url`: Google OAuth URL to authenticate user
    """
    auth = GoogleAuth(
        client_id=ctx.deps.GOOGLE_CLIENT_ID,
        client_secret=ctx.deps.GOOGLE_CLIENT_SECRET,
        redirect_uri=ctx.deps.GOOGLE_REDIRECT_URI
    )
    return {
        "auth_url": auth.get_authorization_url()
    }


# Main function to demonstrate usage
async def main():
    # Create a sample event based on user input
    # user_input = "What can you do?"
    user_input = "Create a google calendar reminder reminding via email 10 minutes prior. for user id: \"\" and event id: \"\""


    print("User Input: ", user_input)
    
    try:
        dependencies = RemainderDeps(
            GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID"),
            GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET"),
            GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
        )
        response = await remainder_agent.run(user_input, deps=dependencies)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
# to run: uv run -m app.agents.resource_agent
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())