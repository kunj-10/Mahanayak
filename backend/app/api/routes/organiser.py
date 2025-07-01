from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import json

from app.api.models import OrganiserRequest
from app.graphs import organiser_graph

router = APIRouter(tags=["organiser"])


@router.post("/organiser_agent")
async def organiser_endpoint(req: OrganiserRequest):
    try:
        initial_state = {}

        initial_state['user_input'] = req.user_input
        if req.event_id:
            initial_state["event_id"] = req.event_id
        if req.event:
            initial_state['event'] = req.event
        
        async def streamer():
            config = {"configurable": {"thread_id": req.chat_id}}

            async for stream_mode, chunk in organiser_graph.astream(
                initial_state,
                config=config,
                stream_mode=["custom"], 
            ):
                yield json.dumps(chunk) + "\n"
        
        return StreamingResponse(
            streamer(), 
            media_type="application/octet-stream"
        )
    except Exception as e:
        print(f"Error in organiser_agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    