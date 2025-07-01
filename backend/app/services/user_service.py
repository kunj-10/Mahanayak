from typing import Literal, Optional
from bson import ObjectId
from app.utils.db import users, User

class UserService:
    def create_user(name: str, email: str, user_type: Literal["volunteer", "organizer"]) -> str:
        user: User = {"name": name, "email": email, "type": user_type}
        result = users.insert_one(user)
        return str(result.inserted_id)

    def get_user_by_email(email: str) -> Optional[dict]:
        return users.find_one({"email": email})

    def get_user_by_id(user_id: str) -> Optional[dict]:
        return users.find_one({"_id": ObjectId(user_id)})

    def update_user(user_id: str, update_fields: dict) -> bool:
        result = users.update_one({"_id": ObjectId(user_id)}, {"$set": update_fields})
        return result.modified_count > 0

    def delete_user(user_id: str) -> bool:
        result = users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0
