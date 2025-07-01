from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from uuid import uuid4
from datetime import datetime, timezone
import json

from app.services.user_service import UserService
from app.services.auth.google import GoogleAuth
from app.utils.db import db

router = APIRouter(tags=["auth"])
google_auth = GoogleAuth()

@router.post("/google")
async def google_callback_handler(request: Request):
    try:
        body_bytes = await request.body()
        body = json.loads(body_bytes)
        code = body.get("code")

        if not code:
            raise HTTPException(status_code=400, detail="Missing auth code")

        tokens = await google_auth.exchange_code_for_token(code)
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Access token not found")

        user_info = await google_auth.get_user_info(access_token)
        email = user_info.get("email")
        name = user_info.get("name")
        if not email or not name:
            raise HTTPException(status_code=400, detail="Failed to fetch Google profile")

        existing_user = UserService.get_user_by_email(email)
        if existing_user:
            user_id = str(existing_user["_id"])
            UserService.update_user(user_id, {"google_access_token": access_token, "google_refresh_token": refresh_token})
            return {
                "message": "User authenticated successfully",
                "user_id": user_id,
                "name": name,
                "email": email
            }

        temp_id = str(ObjectId())
        db.temp_sessions.insert_one({
            "_id": ObjectId(temp_id),
            "email": email,
            "name": name,
            "google_access_token": access_token,
            "google_refresh_token": refresh_token,
            "createdAt": datetime.now(timezone.utc)
        })

        return {
            "message": "New user needs registration type",
            "registration_token": temp_id,
            "name": name,
            "email": email
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Callback failed: {str(e)}")


@router.post("/complete_registration")
async def complete_registration(request: Request):
    try:
        body = await request.json()
        token = body.get("token")
        user_type = body.get("user_type")
        print(token, user_type)

        if not token or user_type not in ("volunteer", "organizer"):
            raise HTTPException(status_code=400, detail="Invalid registration data")

        session = db.temp_sessions.find_one({"_id": ObjectId(token)})
        if not session:
            raise HTTPException(status_code=400, detail="Expired or invalid token")

        user_id = UserService.create_user(
            name=session["name"],
            email=session["email"],
            user_type=user_type
        )

        UserService.update_user(user_id, {
            "google_access_token": session["google_access_token"],
            "google_refresh_token": session["google_refresh_token"]
        })

        db.temp_sessions.delete_one({"_id": ObjectId(token)})

        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "name": session["name"],
            "email": session["email"]
        }

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
