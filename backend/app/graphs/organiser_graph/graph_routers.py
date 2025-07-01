from app.graphs.organiser_graph.graph_state import State
from app.services import EventService

async def primary_router(state: State, writer):
    writer({
        "type": "chat",
        "content": "Checking whether event exists...\n\n"
    })
    
    try:
        event = EventService.get_event_by_id(state['event_id'])
        if event:
            return "get_event"
        else:
            return "create_event"
    except Exception as e:
        print(e)
        return "create_event"

def info_router(state: State):
    if state['info_gathered']:
        return "prompt_generator"
    else:
        return "get_next_user_message"

def agent_router(state: State):
    return state['required_agents']