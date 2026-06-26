from typing import TypedDict, Annotated, Optional
from langgraph.graph import add_messages,StateGraph,END
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.memory import MemorySaver
from uuid import uuid4

from langchain_core.messages import AIMessageChunk, SystemMessage, HumanMessage, AIMessage, ToolMessage

from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

import json


load_dotenv()

# model = ChatGoogleGenerativeAI(model="gemini-3.5-flash", google_api_key=os.getenv("GEMINI_API_KEY"),temperature=0.2, max_output_tokens=1024)\
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))
model = ChatGroq(
    # api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0.2
)

search_tool = TavilySearchResults(max_results=3)

tools = [search_tool]

memory = MemorySaver()

llm_with_tools = model.bind_tools(tools=tools)

# ----------------------------------------------------------------

class State(TypedDict):
    messages: Annotated[list,add_messages]

async def model(state: State):
    messages = state["messages"]
    response = await llm_with_tools.ainvoke(messages)
    return {
        "messages": [response]
    }

async def tools_router(state: State):
    last_message = state["messages"][-1]
    if(hasattr(last_message,"tool_calls") and len(last_message.tool_calls) > 0):
        return "tool_node"
    else:
        return END
    
async def tool_node(state):
    """Custom tool node that handles tool calls from the LLM."""
    # Get the tool calls from the last message
    tool_calls = state["messages"][-1].tool_calls

    tool_messages = []
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_id = tool_call["id"]

        # handle the search tool
        if tool_name == "tavily_search_results_json":
            search_results = await search_tool.ainvoke(tool_args)
            tool_messages.append(ToolMessage(
                content=json.dumps(search_results),
                # tool_name=tool_name,
                # tool_args=tool_args,
                tool_call_id=tool_id
            ))
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    return {
        "messages": tool_messages  
    }
# ---------------------------------------------------------------

graph_builder = StateGraph(State)

graph_builder.add_node("model", model)
graph_builder.add_node("tool_node", tool_node)

graph_builder.set_entry_point("model")
graph_builder.add_conditional_edges(
    "model",
    tools_router,
    {
        "tool_node": "tool_node",
        END: END,
    }
)
graph_builder.add_edge("tool_node", "model")

graph = graph_builder.compile(checkpointer=memory)

# ---------------------------------------------------------------

app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Type"]
)

# ---------------------------------------------------------------

def serialise_ai_message_chunk(chunk):
    if(isinstance(chunk, AIMessageChunk)):
        return chunk.content
    else:
        raise TypeError(f"Expected AIMessageChunk, got {type(chunk)}")
    
# ---------------------------------------------------------------

async def generate_chat_responses(message: str, checkpoint_id: Optional[str] = None):
    is_new_conversation = checkpoint_id is None
    
    if is_new_conversation:
        # Generate new checkpoint ID for first message in conversation
        new_checkpoint_id = str(uuid4())

        config = {
            "configurable": {
                "thread_id": new_checkpoint_id
            }
        }
        
        # Initialize with first message
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )
        
        # First send the checkpoint ID
        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    else:
        config = {
            "configurable": {
                "thread_id": checkpoint_id
            }
        }
        # Continue existing conversation
        events = graph.astream_events(
            {"messages": [HumanMessage(content=message)]},
            version="v2",
            config=config
        )

    async for event in events:
        event_type = event["event"]
        
        if event_type == "on_chat_model_stream":
            chunk_content = serialise_ai_message_chunk(event["data"]["chunk"])
            # Escape single quotes and newlines for safe JSON parsing
            safe_content = chunk_content.replace("'", "\\'").replace("\n", "\\n")
            
            yield f"data: {{\"type\": \"content\", \"content\": \"{safe_content}\"}}\n\n"
            
        elif event_type == "on_chat_model_end":
            # Check if there are tool calls for search
            tool_calls = event["data"]["output"].tool_calls if hasattr(event["data"]["output"], "tool_calls") else []
            search_calls = [call for call in tool_calls if call["name"] == "tavily_search_results_json"]
            
            if search_calls:
                # Signal that a search is starting
                search_query = search_calls[0]["args"].get("query", "")
                # Escape quotes and special characters
                safe_query = search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                yield f"data: {{\"type\": \"search_start\", \"query\": \"{safe_query}\"}}\n\n"
                
        elif event_type == "on_tool_end" and event["name"] == "tavily_search_results_json":
            # Search completed - send results or error
            output = event["data"]["output"]
            
            # Check if output is a list 
            if isinstance(output, list):
                # Extract URLs from list of search results
                urls = []
                for item in output:
                    if isinstance(item, dict) and "url" in item:
                        urls.append(item["url"])
                
                # Convert URLs to JSON and yield them
                urls_json = json.dumps(urls)
                yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"
    
    # Send an end event
    yield f"data: {{\"type\": \"end\"}}\n\n"

# ---------------------------------------------------------------
@app.get("/chat_stream/{message}")
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    # print("=" * 50)
    # print("🚀 Request received")
    # print("Query:", message)
    # print("=" * 50)
    return StreamingResponse(
        generate_chat_responses(message, checkpoint_id),
        media_type="text/event-stream"
    )
# SSE - Server-Sent Events endpoint for chat streaming

# pip install uvicorn

