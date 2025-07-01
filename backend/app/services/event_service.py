from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from app.utils.db import events, Event, User

class EventService:
    def create_event(
        name: str,
        description: str,
        location: str,
        time: datetime,
        users_list: Optional[List[User]] = None,
        guidelines: Optional[str] = None,
        resources: Optional[dict] = None,
        certificate_url: Optional[str] = None,
        attendance: Optional[List[User]] = None,
        feedback_form_url: Optional[str] = None,
        feed_back: Optional[dict] = None
    ) -> str:
        event: dict = {
            "name": name,
            "description": description,
            "location": location,
            "time": time
        }
        if users_list is not None:
            event["users"] = users_list
        if guidelines is not None:
            event["guidelines"] = guidelines
        if resources is not None:
            event["resources"] = resources
        if certificate_url is not None:
            event["certificate_url"] = certificate_url
        if attendance is not None:
            event["attendance"] = attendance
        if feedback_form_url is not None:
            event["feedback_form_url"] = feedback_form_url
        if feed_back is not None:
            event["feed_back"] = feed_back

        result = events.insert_one(event)
        return str(result.inserted_id)

    def get_event_by_id(event_id: str) -> Optional[dict]:
        return events.find_one({"_id": ObjectId(event_id)})

    def update_event(event_id: str, update_fields: dict) -> bool:
        result = events.update_one({"_id": ObjectId(event_id)}, {"$set": update_fields})
        return result.modified_count > 0

    def delete_event(event_id: str) -> bool:
        result = events.delete_one({"_id": ObjectId(event_id)})
        return result.deleted_count > 0

    def list_all_events() -> List[dict]:
        return list(events.find())

if __name__ == '__main__':
    # print(EventService.list_all_events())

    id = "68542bfbe636c0c4f5dcfc93"
    # id = "68542bfbe636c0c4f5dcfc94"
    try:
        event = EventService.get_event_by_id(id)
    except Exception as e:
        print('event not found')
        print(e)