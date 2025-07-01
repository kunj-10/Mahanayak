from langgraph.types import interrupt
import json

from app.graphs.organiser_graph.graph_state import State
from app.services import EventService
from app.agents import (
    organiser_bot,
    organiser_reasoner,
    info_gatherer,
    prompt_generator,
    content_creation_agent,
    permission_agent,
    resource_agent,
    remainder_agent,
    volunteer_guidelines_agent,
    feedback_agent,
    FeedbackDeps
)

import os
from dotenv import load_dotenv

load_dotenv()

async def get_event(state: State, writer):
    writer({
        "type": "bot",
        "content": "Fetching the details of the event...\n\n"
    })
    
    event = EventService.get_event_by_id(state['event_id'])
    event =  {k: v for k, v in event.items() if k != '_id'}

    return {
        "event": event
    }

async def create_event(state: State, writer):
    writer({
        "type": "bot",
        "content": "Creating new event...\n\n"
    })
    
    event = state['event']
    id = EventService.create_event(**event)

    return {
        "event_id": id
    }

async def reasoner(state: State, writer):
    writer({
        "type": "bot",
        "content": "Mahanayak's Agent is processing the query and deciding what to do...\n\n"
    })

    result = await organiser_reasoner.run(state['user_input'])
    result = json.loads(result.output)

    print(result)

    return {
        "required_agents": result
    }

async def info_gatherer_node(state: State, writer):
    user_input = f"""
        Event: {state['event']}
        Required Agents: {state['required_agents']}
        history: {state["messages"]}
        last_user_input: {state['user_input']}
    """

    result = await info_gatherer.run(user_input)
    res = result.output

    writer({
        'type': 'info_gather',
        'content': res['message'] + '\n\n'
    })

    return {
        'info_gathered': res['info_gathered'],
        "messages": [res['message']]
    }

def get_next_user_message(state: State, writer):
    writer({
        "type": "bot",
        "content": "Waiting for user's input...\n\n"
    })

    value = interrupt({})

    return {
        "user_input": value,
        "messages": [value]
    }    

async def prompt_generator_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Combining Information and Generating prompts for various agents...\n\n"
    })

    user_input = f"""
        Event: {state['event']}
        Required Agents: {state['required_agents']}
        message_history: {state["messages"]}
        Tell the agents to give pretty outputs in markdown using emojis etc. It should be visually appealing.
    """

    result = await prompt_generator.run(user_input)
    # print(result.output)

    result = result.output[7:-3]
    result = json.loads(result)

    print(result)

    return {
        "agent_prompts": result
    }

async def content_creator_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Creating Content...\n\n"
    })

    prompt = state["agent_prompts"]['Content Creation Agent']
    

    result = await content_creation_agent.run(prompt)
    result = result.output
    writer({
        "type": "content",
        "content": result
    })

async def resource_agnet_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Executing Resource Agent...\n\n"
    })

    prompt = state["agent_prompts"]['Resource Agent']
    
    result = await resource_agent.run(prompt)
    result = result.output
    writer({
        "type": "resource",
        "content": result
    })

async def remainder_agent_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Executing Remainder Agent...\n\n"
    })

    prompt = state["agent_prompts"]['Remainder Agent']

    result = await remainder_agent.run(prompt)
    result = result.output
    writer({
        "type": "remainder",
        "content": result
    })

async def volunteer_guidelines_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Executing Volunteer Guidelines Agent...\n\n"
    })

    prompt = state["agent_prompts"]['Volunteer Guidelines Agent']

    result = await volunteer_guidelines_agent.run(prompt)
    result = result.output
    writer({
        "type": "volunteer",
        "content": result
    })

async def permission_agent_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Executing Permission Agent...\n\n"
    })

    prompt = state["agent_prompts"]['Permission Agent']

    result = await permission_agent.run(prompt)
    result = result.output
    writer({
        "type": "permission",
        "content": result
    })

dependencies = FeedbackDeps(
    GOOGLE_CLIENT_ID=os.getenv("GOOGLE_CLIENT_ID"),
    GOOGLE_CLIENT_SECRET=os.getenv("GOOGLE_CLIENT_SECRET"),
    GOOGLE_REDIRECT_URI=os.getenv("GOOGLE_REDIRECT_URI"),
    # user="685d40ffd76683cf9783eac3",
    # event="68543aaec3d68550c4b2c5e8"
)
async def feedback_agent_node(state: State, writer):
    writer({
        "type": "bot",
        "content": "Executing Feedback Agent...\n\n"
    })

    prompt = state["agent_prompts"]['Feedback Agent']


    result = await feedback_agent.run(prompt, deps=dependencies)
    result = result.output
    writer({
        "type": "feedback",
        "content": result
    })

async def bot(state: State, writer):
    writer({
        "type": "bot",
        "content": "Mahanayak Bot is preparing it's reply...\n\n"
    })

    prompt = state['agent_prompts']['Conversation Agent']
    
    result = await organiser_bot.run(prompt)
    result = result.output
    writer({
        "type": "chat",
        "content": result
    })

    # async with organiser_bot.run_stream(prompt) as result:
    #     async for chunk in result.stream_text(delta=True):
    #         writer({
    #             "type": "chat",
    #             "content": chunk
    #         })
