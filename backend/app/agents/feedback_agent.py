from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv
from dataclasses import dataclass
from app.utils import FEEDBACK_AGENT_SYSTEM_PROMPT 
from typing import List, Dict, Any, Optional
from app.services import EventService
from app.services import UserService
from app.services.auth import GoogleAuth
import httpx
import asyncio

load_dotenv()

@dataclass
class FeedbackDeps:
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

feedback_agent = Agent(
    model='google-gla:gemini-2.0-flash',
    system_prompt=FEEDBACK_AGENT_SYSTEM_PROMPT,
    retries=2,
    deps_type=FeedbackDeps
)

@feedback_agent.tool
def create_google_form(
    ctx: RunContext[FeedbackDeps],
    user_id: str,
    event_id: str, 
    questions: List[Dict[str, Any]],
    form_title: Optional[str] = None,
    form_description: Optional[str] = None
) -> dict:
    """
    Creates a Google Form for an event with custom questions
    
    Args:
    - ctx: The context containing dependencies
    - user_id: MongoDB ObjectId of the user creating the form
    - event_id: MongoDB ObjectId of the event to create form for
    - questions: List of question dictionaries with structure:
        {
            "title": str,  # Question text
            "type": str,   # "TEXT", "PARAGRAPH_TEXT", "MULTIPLE_CHOICE", "CHECKBOX", "DROPDOWN", "LINEAR_SCALE", "DATE", "TIME", "EMAIL"
            "required": bool,  # Whether question is required (default: False)
            "options": List[str],  # For MULTIPLE_CHOICE, CHECKBOX, DROPDOWN (optional)
            "scale": Dict[str, int],  # For LINEAR_SCALE: {"low": 1, "high": 5} (optional)
            "description": str  # Question description (optional)
        }
    - form_title: Custom title for the form (default: uses event name)
    - form_description: Custom description for the form (default: auto-generated)
    
    Returns:
    A dictionary containing:
    - `message`: Human-readable message indicating the result
    - `form_url`: Direct URL to the created Google Form
    - `form_id`: Google Form ID
    - `auth_url` (optional): Google OAuth URL if user needs to authenticate
    """
    
    if not user_id:
        return {"message": "Missing user_id parameter"}
    if not event_id:
        return {"message": "Missing event_id parameter"}
    if not questions or len(questions) == 0:
        return {"message": "At least one question is required"}
    
    valid_question_types = [
        "TEXT", "PARAGRAPH_TEXT", "MULTIPLE_CHOICE", "CHECKBOX", 
        "DROPDOWN", "LINEAR_SCALE", "DATE", "TIME", "EMAIL"
    ]
    
    for i, question in enumerate(questions):
        if not isinstance(question, dict):
            return {"message": f"Question {i+1} must be a dictionary"}
        if not question.get("title"):
            return {"message": f"Question {i+1} missing 'title' field"}
        if not question.get("type"):
            return {"message": f"Question {i+1} missing 'type' field"}
        if question["type"] not in valid_question_types:
            return {"message": f"Question {i+1} has invalid type. Must be one of: {', '.join(valid_question_types)}"}
        
        if question["type"] in ["MULTIPLE_CHOICE", "CHECKBOX", "DROPDOWN"]:
            if not question.get("options") or len(question["options"]) == 0:
                return {"message": f"Question {i+1} of type '{question['type']}' requires 'options' list"}
        
        if question["type"] == "LINEAR_SCALE":
            scale = question.get("scale", {})
            if not isinstance(scale, dict) or "low" not in scale or "high" not in scale:
                return {"message": f"Question {i+1} of type 'LINEAR_SCALE' requires 'scale' dict with 'low' and 'high' keys"}
    
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
                "message": "User not authenticated with Google",
                "auth_url": auth.get_authorization_url()
            }
                
        default_title = form_title or f"{event.get('name', 'Event')} - Feedback Form"
        default_description = form_description or f"""
        Thank you for attending {event.get('name', 'our event')}! 
        
        Please take a few minutes to provide your feedback. Your responses will help us improve future events.
        
        Event Details:
        - Location: {event.get('location', 'N/A')}
        - Date: {event.get('time', 'N/A')}
        """
        
        form_data = {
            "info": {
                "title": default_title,
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        create_response = httpx.post(
            "https://forms.googleapis.com/v1/forms",
            headers=headers,
            json=form_data
        )

        if create_response.status_code == 401 and refresh_token:
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
                create_response = httpx.post(
                    "https://forms.googleapis.com/v1/forms",
                    headers=headers,
                    json=form_data
                )
            else:
                return {
                    "message": "User not authenticated with Google",
                    "auth_url": auth.get_authorization_url()
                }
        
        create_response.raise_for_status()
        form = create_response.json()
        form_id = form.get("formId")
        
        requests = []
        
        for i, question in enumerate(questions):
            question_item = {
                "title": question["title"],
                "questionItem": {
                    "question": {
                        "required": question.get("required", False)
                    }
                }
            }
            
            if question.get("description"):
                question_item["description"] = question["description"]
            
            question_type = question["type"]
            
            if question_type == "TEXT":
                question_item["questionItem"]["question"]["textQuestion"] = {}
            
            elif question_type == "PARAGRAPH_TEXT":
                question_item["questionItem"]["question"]["textQuestion"] = {
                    "paragraph": True
                }
            
            elif question_type in ["MULTIPLE_CHOICE", "CHECKBOX", "DROPDOWN"]:
                options = [{"value": option} for option in question["options"]]
                
                if question_type == "MULTIPLE_CHOICE":
                    question_item["questionItem"]["question"]["choiceQuestion"] = {
                        "type": "RADIO",
                        "options": options
                    }
                elif question_type == "CHECKBOX":
                    question_item["questionItem"]["question"]["choiceQuestion"] = {
                        "type": "CHECKBOX",
                        "options": options
                    }
                else:
                    question_item["questionItem"]["question"]["choiceQuestion"] = {
                        "type": "DROP_DOWN",
                        "options": options
                    }
            
            elif question_type == "LINEAR_SCALE":
                scale = question.get("scale", {"low": 1, "high": 5})
                question_item["questionItem"]["question"]["scaleQuestion"] = {
                    "low": scale["low"],
                    "high": scale["high"]
                }
            
            elif question_type == "DATE":
                question_item["questionItem"]["question"]["dateQuestion"] = {}
            
            elif question_type == "TIME":
                question_item["questionItem"]["question"]["timeQuestion"] = {}
            
            elif question_type == "EMAIL":
                question_item["questionItem"]["question"]["textQuestion"] = {}
                question_item["questionItem"]["question"]["textQuestion"]["paragraph"] = False
            
            requests.append({
                "createItem": {
                    "item": question_item,
                    "location": {
                        "index": i
                    }
                }
            })
        
        # requests.append({
        #     "updateFormInfo":
        #     {
        #         "info": {
        #             "description": default_description.strip()
        #         },
        #         "updateMask": "info.description"
        #     }
        # })

        if requests:
            batch_update_data = {
                "requests": requests
            }
            
            batch_response = httpx.post(
                f"https://forms.googleapis.com/v1/forms/{form_id}:batchUpdate",
                headers=headers,
                json=batch_update_data
            )
            batch_response.raise_for_status()
        
        form_url = f"https://docs.google.com/forms/d/{form_id}/edit"
        public_url = f"https://docs.google.com/forms/d/{form_id}/viewform"
        
        EventService.update_event(event_id, {
            "feedback_form_url": public_url
        })
        
        return {
            "message": f"Google Form created successfully with {len(questions)} questions for '{event.get('name')}'",
            "form_url": form_url,
            "public_url": public_url,
            "form_id": form_id,
            "questions_count": len(questions)
        }
        
    except httpx.HTTPStatusError as http_err:
        error_detail = ""
        try:
            error_detail = http_err.response.json().get("error", {}).get("message", "")
        except:
            error_detail = http_err.response.text
        
        return {"message": f"Google Forms API error: {error_detail}"}
        
    except Exception as e:
        return {"message": f"Failed to create Google Form: {str(e)}"}

@feedback_agent.tool
def get_google_auth_link(ctx: RunContext[FeedbackDeps]):
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


async def main():
    # Create a sample event based on user input
    user_input = "Create a feedback form for the event with eventid: \"\" asking user their name and email and also a para about if they liked the event. my userid is: \"\" and whatever message you recieve print it as it also along with wathever you are aldready printing."

    print("User Input: ", user_input)
    
    try:
        import os
        dependencies = FeedbackDeps(
            GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID"),
            GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET"),
            GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI")
        )
        response = await feedback_agent.run(user_input, deps=dependencies)
        print("Agent Response:", response.output)
    except Exception as e:
        print(f"Agent run failed: {e}")
        
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())