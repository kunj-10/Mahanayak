from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from app.graphs.organiser_graph.graph_state import State
from app.graphs.organiser_graph.graph_routers import *
from app.graphs.organiser_graph.graph_nodes import *

graph = StateGraph(State)

# nodes
graph.add_node("get_event", get_event)
graph.add_node("create_event", create_event)
graph.add_node("reasoner", reasoner)
graph.add_node("info_gatherer", info_gatherer_node)
graph.add_node("get_next_user_message", get_next_user_message)
graph.add_node("prompt_generator", prompt_generator_node)
graph.add_node("content_creator", content_creator_node)
graph.add_node("resource_agent", resource_agnet_node) 
graph.add_node("remainder_agent", remainder_agent_node)
graph.add_node("permission_agent", permission_agent_node) 
graph.add_node("volunteer_guidelines", volunteer_guidelines_node)
graph.add_node("feedback_agent", feedback_agent_node)
graph.add_node("bot", bot)

# edges
graph.add_conditional_edges(
    START,
    primary_router,
    {
        "get_event": "get_event",
        "create_event": "create_event"
    }
)

graph.add_edge('get_event', 'reasoner')
graph.add_edge('create_event', 'reasoner')
graph.add_edge('reasoner', 'info_gatherer')

graph.add_conditional_edges(
    'info_gatherer',
    info_router,
    {
        'prompt_generator': 'prompt_generator',
        'get_next_user_message': 'get_next_user_message'
    }
)

graph.add_edge('get_next_user_message', 'info_gatherer')  

graph.add_conditional_edges(
    "prompt_generator",
    agent_router,
    {
        "Content Creator Agent": "content_creator",  
        "Resource Agent": "resource_agent",
        "Remainder Agent": "remainder_agent",
        "Permission Agent": "permission_agent",
        "Volunteer Guidelines Agent": "volunteer_guidelines",
        "Feedback Agent": "feedback_agent",
        "Conversation Agent": "bot",
    }
)

graph.add_edge("bot", END)
graph.add_edge("content_creator", END)
graph.add_edge("resource_agent", END)
graph.add_edge("remainder_agent", END)
graph.add_edge("permission_agent", END)
graph.add_edge("volunteer_guidelines", END)
graph.add_edge("feedback_agent", END)

memory = MemorySaver()
organiser_graph = graph.compile(checkpointer=memory)

async def main():
    user_input = "What is the event all about?"
    print("input: ", user_input)
    
    initial_state = {
        "user_input": user_input,
        "event_id": "68543e17caea5fd995970d0e",
    }
    
    # Run the graph
    config = {"configurable": {"thread_id": "1"}}
    
    async for stream_mode, chunk in organiser_graph.astream(
        initial_state,
        config=config,
        stream_mode=["custom"], 
    ):
        print(chunk['content'], end="")
    
if __name__ == "__main__": 
    import asyncio
    asyncio.run(main())