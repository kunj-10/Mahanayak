from typing import Annotated, Dict, List, Any
from typing_extensions import TypedDict

class State(TypedDict):
    event_id: str
    event: Dict[str, Any]

    user_input: str
    messages: Annotated[List[str], lambda x, y: x + y]

    required_agents: List[str]
    agent_prompts: Dict[str, str]
    
    info_gathered: bool