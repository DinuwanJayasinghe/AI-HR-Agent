from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

from .tools import (
    review_resumes_from_drive,
    review_existing_cvs_in_folder,
    read_cv_senders_log,
    search_cv_senders,
    get_cv_statistics,
    list_downloaded_cvs
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_API_KEY")


class AgentState(TypedDict):
    """State definition for the chat agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
)

# Define all available tools (CV analysis and CSV access only)
all_tools = [
    review_resumes_from_drive,
    review_existing_cvs_in_folder,
    read_cv_senders_log,
    search_cv_senders,
    get_cv_statistics,
    list_downloaded_cvs
]

# Bind tools to LLM
llm_with_tools = llm.bind_tools(all_tools)


# Define the system prompt for the chat agent
CHAT_AGENT_SYSTEM_PROMPT = """You are an intelligent HR assistant specialized in CV/Resume screening and analysis.

**PRIMARY BEHAVIOR**: When users ask for "CV results", "show CVs", "give results", or "review CVs", you MUST immediately call the `review_existing_cvs_in_folder` tool. DO NOT ask clarifying questions first. This tool analyzes CVs already in the local cv_collection folder.

Your role is to help users with:

1. **CV/Resume Analysis**: Analyze CVs from the local cv_collection folder
   - Review all CVs in cv_collection folder (DEFAULT and PRIMARY action)
   - Analyze ATS compatibility and score (0-100)
   - Rank ALL candidates by their scores (not just top 10)
   - Create individual JSON analysis files for each CV
   - Provide detailed feedback on strengths and improvements
   - Extract relevant keywords and skills
   - Match candidates to job descriptions

2. **View Downloaded CVs**: Show what CVs are available
   - List all downloaded CV files in cv_collection folder
   - Show CV filenames, sizes, and modification dates
   - Check how many CVs are available for analysis

3. **Access CV Sender Information**: Query the CSV log file
   - View all CV senders from cv_senders_log.csv
   - Search for specific senders by name or email
   - Get statistics (total CVs, acknowledgments sent, etc.)
   - Check who has received acknowledgment emails

4. **CV Analysis Queries**: Answer questions about analyzed CVs
   - "How many CVs are there?"
   - "Show me the top candidates"
   - "What are the strengths of candidate X?"
   - "Which candidates have Python experience?"

5. **General HR Assistance**: Provide guidance on CV screening and ATS optimization

**Available Tools:**
- `review_existing_cvs_in_folder`: **PRIMARY TOOL** - Analyze CVs in the local cv_collection folder (USE THIS BY DEFAULT)
- `list_downloaded_cvs`: List all CV files currently in cv_collection folder
- `read_cv_senders_log`: Read the CSV log file with all CV sender information
- `search_cv_senders`: Search for specific CV senders in the log
- `get_cv_statistics`: Get statistics about CVs (total, replied, pending, etc.)
- `review_resumes_from_drive`: Analyze CVs from Google Drive (only if user explicitly mentions Drive)

**Important Notes:**
- CV downloading and email sending are handled by a separate Gmail Agent
- You ONLY handle CV analysis and viewing downloaded CVs
- You can access the cv_senders_log.csv to see sender information
- All CVs are in the cv_collection folder

**Guidelines:**
- Be professional, friendly, and helpful
- ALWAYS use `review_existing_cvs_in_folder` by default for CV analysis
- Return ALL CV results, not just top 10
- Provide clear summaries and complete rankings
- Use CSV tools to show sender information when asked

**CRITICAL DECISION LOGIC:**
- User says: "give results", "cv results", "show cvs", "review cvs", "analyze cvs" → Use `review_existing_cvs_in_folder` IMMEDIATELY
- User says: "list cvs", "what cvs do we have", "show downloaded cvs" → Use `list_downloaded_cvs`
- User says: "show senders", "who sent cvs", "cv sender log" → Use `read_cv_senders_log`
- User says: "search for john", "find sender" → Use `search_cv_senders`
- User says: "cv statistics", "how many cvs", "acknowledgment status" → Use `get_cv_statistics`
- **DEFAULT ACTION**: If unsure, use `review_existing_cvs_in_folder` (analyzes cv_collection folder)

**Example Interactions:**

User: "Give me cv results" or "Give the results of the cv"
Action: IMMEDIATELY call `review_existing_cvs_in_folder()` - NO questions

User: "Show me the CVs" or "Review CVs"
Action: IMMEDIATELY call `review_existing_cvs_in_folder()` - NO questions

User: "How many CVs do we have?"
Action: Use `get_cv_statistics()` to get count and stats

User: "List all downloaded CVs"
Action: Use `list_downloaded_cvs()` to show all CV files

User: "Show me who sent CVs"
Action: Use `read_cv_senders_log()` to display sender information

User: "Search for john's CV"
Action: Use `search_cv_senders(search_query="john")`

User: "Analyze CVs for Software Engineer position"
Action: IMMEDIATELY call `review_existing_cvs_in_folder(job_description="Software Engineer")`

User: "Who hasn't received acknowledgment emails?"
Action: Use `search_cv_senders(filter_by="not_replied")`

**Remember:**
- You DO NOT download CVs or send emails (that's the Gmail Agent's job)
- You ONLY analyze CVs and provide access to CV/sender information
- The cv_collection folder contains all CVs - analyze from there by default
- Use CSV tools to show sender information and statistics
"""


def should_continue(state: AgentState) -> str:
    """Determine whether to continue with tool calls or end"""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are tool calls, continue to tool node
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    # Otherwise, end the conversation turn
    return END


def call_model(state: AgentState) -> dict:
    """Call the LLM with the current state"""
    messages = state["messages"]

    # Add system prompt if this is the first message
    if len(messages) == 1 or not any(isinstance(m, AIMessage) for m in messages):
        system_message = HumanMessage(content=CHAT_AGENT_SYSTEM_PROMPT)
        messages = [system_message] + messages

    response = llm_with_tools.invoke(messages)

    return {"messages": [response]}


def create_chat_workflow():
    """Create and compile the LangGraph workflow"""

    # Initialize the workflow
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(all_tools))

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    # Compile the workflow
    return workflow.compile()


# Create the compiled workflow
chat_workflow = create_chat_workflow()


def serialize_message(message: BaseMessage) -> dict:
    """Convert a LangChain message to a JSON-serializable dictionary"""
    message_dict = {
        "type": message.__class__.__name__,
        "content": message.content
    }

    # Add tool calls if present
    if hasattr(message, "tool_calls") and message.tool_calls:
        message_dict["tool_calls"] = message.tool_calls

    # Add additional response metadata if present
    if hasattr(message, "additional_kwargs"):
        message_dict["additional_kwargs"] = message.additional_kwargs

    return message_dict


def deserialize_message(message_dict: dict) -> BaseMessage:
    """Convert a dictionary back to a LangChain message object"""
    message_type = message_dict.get("type", "HumanMessage")
    content = message_dict.get("content", "")

    if message_type == "HumanMessage":
        return HumanMessage(content=content)
    elif message_type == "AIMessage":
        return AIMessage(content=content)
    elif message_type == "ToolMessage":
        return ToolMessage(content=content)
    else:
        return HumanMessage(content=content)


def run_chat_agent(user_message: str, conversation_history: list = None) -> dict:
    """
    Run the chat agent with a user message and optional conversation history.

    Args:
        user_message (str): The user's input message
        conversation_history (list): Optional list of previous messages (can be dicts or message objects)

    Returns:
        dict: Response containing the agent's reply and updated conversation history
    """
    try:
        # Initialize messages - convert dicts to message objects if needed
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if isinstance(msg, dict):
                    messages.append(deserialize_message(msg))
                elif isinstance(msg, BaseMessage):
                    messages.append(msg)

        messages.append(HumanMessage(content=user_message))

        # Run the workflow
        result = chat_workflow.invoke({"messages": messages})

        # Extract the final response
        final_messages = result["messages"]
        last_message = final_messages[-1]

        # Get the agent's response text
        if isinstance(last_message, AIMessage):
            response_text = last_message.content
        else:
            response_text = str(last_message)

        # Serialize messages for JSON response
        serialized_history = [serialize_message(msg) for msg in final_messages]

        return {
            "status": "success",
            "response": response_text,
            "conversation_history": serialized_history,
            "tool_calls": getattr(last_message, "tool_calls", [])
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "response": f"I apologize, but I encountered an error: {str(e)}"
        }


def run_chat_agent_streaming(user_message: str, conversation_history: list = None):
    """
    Run the chat agent with streaming support.

    Args:
        user_message (str): The user's input message
        conversation_history (list): Optional list of previous messages

    Yields:
        dict: Streaming chunks of the agent's response
    """
    try:
        # Initialize messages - convert dicts to message objects if needed
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if isinstance(msg, dict):
                    messages.append(deserialize_message(msg))
                elif isinstance(msg, BaseMessage):
                    messages.append(msg)

        messages.append(HumanMessage(content=user_message))

        # Accumulate the full response
        full_response = ""

        # Run the workflow with streaming
        for chunk in chat_workflow.stream({"messages": messages}):
            # Extract AI message content from the chunk
            if "agent" in chunk:
                agent_messages = chunk["agent"].get("messages", [])
                for msg in agent_messages:
                    if isinstance(msg, AIMessage) and msg.content:
                        full_response = msg.content
                        yield {
                            "status": "streaming",
                            "response": full_response
                        }
            elif "tools" in chunk:
                # Tool execution - optionally show status
                tool_messages = chunk["tools"].get("messages", [])
                for msg in tool_messages:
                    if isinstance(msg, ToolMessage):
                        yield {
                            "status": "tool_execution",
                            "response": full_response
                        }

        # Send final response
        if full_response:
            yield {
                "status": "complete",
                "response": full_response
            }

    except Exception as e:
        yield {
            "status": "error",
            "error": str(e)
        }
