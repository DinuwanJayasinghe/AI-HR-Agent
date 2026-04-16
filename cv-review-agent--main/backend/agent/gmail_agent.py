"""
Gmail Agent - Handles CV downloading from Gmail and sending acknowledgment emails
"""
from typing import Annotated, TypedDict, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os

from .tools import (
    collect_and_review_cvs_from_gmail,
    download_cvs_from_gmail_by_date,
    download_and_analyze_cvs,
    send_cv_acknowledgment_email,
    send_bulk_cv_acknowledgments
)

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_API_KEY")


class GmailAgentState(TypedDict):
    """State definition for the Gmail agent"""
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0.7,
)

# Define Gmail-specific tools (only email downloading and sending)
gmail_tools = [
    collect_and_review_cvs_from_gmail,
    download_cvs_from_gmail_by_date,
    download_and_analyze_cvs,
    send_cv_acknowledgment_email,
    send_bulk_cv_acknowledgments
]

# Bind tools to LLM
llm_with_gmail_tools = llm.bind_tools(gmail_tools)


# Define the system prompt for the Gmail agent
GMAIL_AGENT_SYSTEM_PROMPT = """You are an intelligent Gmail HR assistant specialized in CV/Resume collection and acknowledgment.

Your PRIMARY ROLE is to:

1. **Download CVs from Gmail**:
   - Download CVs from Gmail inbox using date filters
   - Extract CV attachments (PDF, DOC, DOCX)
   - Save CVs to local cv_collection folder
   - Extract sender information (email, name, date)

2. **Send Acknowledgment Emails**:
   - AUTOMATICALLY send acknowledgment emails to ALL CV senders after downloading
   - Use professional acknowledgment template
   - Log all email activities to cv_senders_log.csv
   - Track sent/failed acknowledgments

3. **Batch Processing**:
   - Handle multiple CV downloads at once
   - Send bulk acknowledgment emails efficiently
   - Provide detailed summary of download and email operations

**Available Tools:**
- `download_cvs_from_gmail_by_date`: Download CVs from Gmail by date range (e.g., last 7 days)
- `download_and_analyze_cvs`: Download CVs AND analyze them (complete workflow)
- `collect_and_review_cvs_from_gmail`: Download all CVs from Gmail with analysis
- `send_cv_acknowledgment_email`: Send acknowledgment to a single CV sender
- `send_bulk_cv_acknowledgments`: Send acknowledgments to multiple CV senders at once

**Workflow:**
When user asks to download CVs:
1. Use appropriate download tool based on date range or requirements
2. Extract sender information from downloaded CVs
3. AUTOMATICALLY call `send_bulk_cv_acknowledgments` with all sender details
4. Log all activities to cv_senders_log.csv
5. Provide summary of downloads and emails sent

**Acknowledgment Email Template:**
"Dear [Name],

Thank you for submitting your CV/Resume to our team.

We have successfully received your application and it is currently being reviewed by our HR department. Our team will carefully assess your qualifications and experience.

We will contact you as soon as possible regarding the next steps in the recruitment process. This typically takes 3-5 business days.

If you have any questions in the meantime, please feel free to reach out to us.

Thank you for your interest in joining our organization.

Best regards,
HR Department
hr.agent.automation@gmail.com"

**Guidelines:**
- Always send acknowledgment emails after downloading CVs
- Log all activities to CSV for tracking
- Provide clear summaries of operations
- Handle errors gracefully and report failures
- Be professional and efficient

**Example Interaction:**

User: "Download CVs from last 3 days"
Action:
1. Call `download_cvs_from_gmail_by_date(days_back=3)`
2. Extract sender emails from downloaded CVs
3. Automatically call `send_bulk_cv_acknowledgments` with sender list
4. Report: "Downloaded 5 CVs, sent 5 acknowledgment emails, logged to CSV"

User: "Send acknowledgment to john@example.com"
Action: Call `send_cv_acknowledgment_email(recipient_email="john@example.com", recipient_name="John")`
"""


def should_continue_gmail(state: GmailAgentState) -> str:
    """Determine whether to continue with tool calls or end"""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def call_gmail_model(state: GmailAgentState) -> dict:
    """Call the LLM with the current state"""
    messages = state["messages"]

    # Add system prompt if this is the first message
    if len(messages) == 1 or not any(isinstance(m, AIMessage) for m in messages):
        system_message = HumanMessage(content=GMAIL_AGENT_SYSTEM_PROMPT)
        messages = [system_message] + messages

    response = llm_with_gmail_tools.invoke(messages)

    return {"messages": [response]}


def create_gmail_workflow():
    """Create and compile the Gmail agent workflow"""
    workflow = StateGraph(GmailAgentState)

    # Add nodes
    workflow.add_node("agent", call_gmail_model)
    workflow.add_node("tools", ToolNode(gmail_tools))

    # Set entry point
    workflow.set_entry_point("agent")

    # Add conditional edges
    workflow.add_conditional_edges(
        "agent",
        should_continue_gmail,
        {
            "tools": "tools",
            END: END
        }
    )

    # Add edge from tools back to agent
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Create the compiled workflow
gmail_workflow = create_gmail_workflow()


def serialize_message(message: BaseMessage) -> dict:
    """Convert a LangChain message to a JSON-serializable dictionary"""
    message_dict = {
        "type": message.__class__.__name__,
        "content": message.content
    }

    if hasattr(message, "tool_calls") and message.tool_calls:
        message_dict["tool_calls"] = message.tool_calls

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


def run_gmail_agent(user_message: str, conversation_history: list = None) -> dict:
    """
    Run the Gmail agent with a user message.

    Args:
        user_message (str): The user's input message
        conversation_history (list): Optional list of previous messages

    Returns:
        dict: Response containing the agent's reply and updated conversation history
    """
    try:
        messages = []
        if conversation_history:
            for msg in conversation_history:
                if isinstance(msg, dict):
                    messages.append(deserialize_message(msg))
                elif isinstance(msg, BaseMessage):
                    messages.append(msg)

        messages.append(HumanMessage(content=user_message))

        # Run the workflow
        result = gmail_workflow.invoke({"messages": messages})

        # Extract the final response
        final_messages = result["messages"]
        last_message = final_messages[-1]

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
