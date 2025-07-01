"""Pydantic models for API requests and responses."""

from pydantic import BaseModel
from typing import Dict, Any, Optional


class OrganiserRequest(BaseModel):
    chat_id: str
    event_id: Optional[str] = None
    event: Optional[Dict[str, Any]] = None
    user_input: str