from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse, StreamingResponse
from agent import run_chat_agent, run_chat_agent_streaming
from agent.tools import (
    collect_and_review_cvs_from_gmail,
    review_resumes_from_drive,
    download_cvs_from_gmail_by_date,
    download_and_analyze_cvs
)
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import os
from pathlib import Path

router = APIRouter()


class CVReviewRequest(BaseModel):
    job_description: Optional[str] = ""
    use_drive: Optional[bool] = False
    folder_id: Optional[str] = ""


@router.post("/review-cvs")
async def review_cvs(request: CVReviewRequest):
    """
    Review CVs from Gmail or Google Drive.

    - Downloads CVs from Gmail (default) or Google Drive
    - Analyzes ATS compatibility
    - Returns top 10 ranked candidates

    Args:
        job_description: Optional job description for better matching
        use_drive: If True, uses Google Drive; if False, uses Gmail
        folder_id: Google Drive folder ID (required if use_drive=True)
    """
    try:
        if request.use_drive:
            if not request.folder_id:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "error": "folder_id is required when using Google Drive"
                    }
                )

            # Use Google Drive tool
            result = review_resumes_from_drive.invoke({
                "folder_id": request.folder_id,
                "job_description": request.job_description
            })
        else:
            # Use Gmail tool
            result = collect_and_review_cvs_from_gmail.invoke({
                "job_description": request.job_description
            })

        return JSONResponse(content={
            "status": "success",
            "result": result
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


class CVDownloadByDateRequest(BaseModel):
    days_back: Optional[int] = 7
    job_position: Optional[str] = ""
    job_description: Optional[str] = ""
    analyze: Optional[bool] = True


@router.post("/download-cvs-by-date")
async def download_cvs_by_date(request: CVDownloadByDateRequest):
    """
    Download and optionally analyze CVs from Gmail based on date range.

    This endpoint allows you to automatically download CVs from emails received
    in the last N days and optionally analyze them with AI.

    Args:
        days_back: Number of days to look back (default: 7)
        job_position: Filter emails by job position in subject line (optional)
        job_description: Job description for better CV matching (optional, used if analyze=True)
        analyze: If True, downloads AND analyzes CVs; if False, only downloads (default: True)

    Examples:
        - Download CVs from last 3 days: {"days_back": 3}
        - Download today's CVs: {"days_back": 1}
        - Download and analyze last week's CVs for R&D Engineer:
          {"days_back": 7, "job_position": "R&D Engineer", "job_description": "...", "analyze": true}

    Returns:
        JSON with download results and CV analysis (if analyze=True)
    """
    try:
        if request.analyze:
            # Download and analyze
            result = download_and_analyze_cvs.invoke({
                "days_back": request.days_back,
                "job_description": request.job_description,
                "job_position": request.job_position
            })
        else:
            # Only download
            result = download_cvs_from_gmail_by_date.invoke({
                "days_back": request.days_back,
                "job_position": request.job_position
            })

        return JSONResponse(content={
            "status": "success",
            "result": result
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Dict[str, Any]]] = []
    session_id: Optional[str] = None  # Optional: for tracking conversations


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat with the AI agent using LangGraph workflow.

    The agent can help you with:
    - **CV Reviews**: "How many CVs came for R&D engineer position?"
    - **Review CVs**: "Review all CVs from Gmail" or "Review CVs from Google Drive folder"
    - **General Questions**: Ask anything about HR processes and CV screening

    ## Simple Usage Examples:

    **New conversation (first message):**
    ```json
    {
      "message": "How many CVs came for R&D engineer?"
    }
    ```

    **Continue conversation (include history from previous response):**
    ```json
    {
      "message": "Show me the top 3 candidates",
      "conversation_history": [<copy from previous response>]
    }
    ```

    **Or just ask directly without history:**
    ```json
    {
      "message": "Review all CVs from my Gmail for Software Engineer position"
    }
    ```

    Args:
        message: Your question or request (e.g., "How many CVs for R&D engineer?")
        conversation_history: (Optional) Copy this from the previous response to continue the conversation
        session_id: (Optional) For tracking your conversation

    Returns:
        Response with agent's reply and updated conversation history
    """
    try:
        result = run_chat_agent(
            user_message=request.message,
            conversation_history=request.conversation_history
        )

        # Add session_id to response if provided
        if request.session_id:
            result["session_id"] = request.session_id

        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": str(e),
                "response": f"I apologize, but I encountered an error: {str(e)}"
            }
        )


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat with the AI agent using streaming responses.

    Same functionality as /chat endpoint but with streaming support
    for real-time responses.

    Args:
        message: User's message
        conversation_history: Optional previous conversation messages

    Returns:
        Streaming response with agent's reply chunks
    """
    async def generate():
        try:
            for chunk in run_chat_agent_streaming(
                user_message=request.message,
                conversation_history=request.conversation_history
            ):
                yield f"data: {json.dumps(chunk)}\n\n"
        except Exception as e:
            error_chunk = {
                "status": "error",
                "error": str(e)
            }
            yield f"data: {json.dumps(error_chunk)}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.get("/cvs")
async def get_cvs():
    """
    Get all CVs from the cv_collection folder.

    Returns:
        List of CV files with their metadata
    """
    try:
        cv_folder = Path("cv_collection")

        if not cv_folder.exists():
            return JSONResponse(content={
                "status": "success",
                "cvs": [],
                "total": 0,
                "message": "No CVs found. CV collection folder doesn't exist."
            })

        cvs = []
        for file_path in cv_folder.glob("*.pdf"):
            file_stats = file_path.stat()
            cvs.append({
                "filename": file_path.name,
                "size": file_stats.st_size,
                "created_at": file_stats.st_ctime,
                "modified_at": file_stats.st_mtime
            })

        # Sort by modified time (newest first)
        cvs.sort(key=lambda x: x["modified_at"], reverse=True)

        return JSONResponse(content={
            "status": "success",
            "cvs": cvs,
            "total": len(cvs)
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@router.get("/cv-analysis")
async def get_cv_analysis():
    """
    Get all CV analysis results from the cv_analysis folder.

    Returns:
        List of analyzed CVs with their scores and details
    """
    try:
        analysis_folder = Path("cv_analysis")

        if not analysis_folder.exists():
            return JSONResponse(content={
                "status": "success",
                "analyses": [],
                "total": 0,
                "message": "No analysis found. Please analyze CVs first."
            })

        analyses = []
        for file_path in analysis_folder.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    analysis_data = json.load(f)
                    analyses.append({
                        "filename": file_path.stem,  # Filename without extension
                        "data": analysis_data
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

        # Sort by ATS score (highest first) if available
        analyses.sort(
            key=lambda x: x["data"].get("ats_score", 0) if isinstance(x["data"], dict) else 0,
            reverse=True
        )

        return JSONResponse(content={
            "status": "success",
            "analyses": analyses,
            "total": len(analyses)
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )


@router.get("/dashboard-stats")
async def get_dashboard_stats():
    """
    Get dashboard statistics including CV count, analysis summary, etc.

    Returns:
        Dashboard statistics and metrics
    """
    try:
        cv_folder = Path("cv_collection")
        analysis_folder = Path("cv_analysis")

        # Count CVs
        total_cvs = len(list(cv_folder.glob("*.pdf"))) if cv_folder.exists() else 0

        # Count analyses
        total_analyses = len(list(analysis_folder.glob("*.json"))) if analysis_folder.exists() else 0

        # Calculate average ATS score
        avg_score = 0
        top_candidates = []

        if analysis_folder.exists():
            scores = []
            all_analyses = []

            for file_path in analysis_folder.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        analysis_data = json.load(f)
                        score = analysis_data.get("ats_score", 0)
                        scores.append(score)
                        all_analyses.append({
                            "filename": file_path.stem,
                            "score": score,
                            "name": analysis_data.get("candidate_name", "Unknown"),
                            "summary": analysis_data.get("summary", "")
                        })
                except Exception:
                    continue

            if scores:
                avg_score = sum(scores) / len(scores)

            # Get top 5 candidates
            all_analyses.sort(key=lambda x: x["score"], reverse=True)
            top_candidates = all_analyses[:5]

        return JSONResponse(content={
            "status": "success",
            "stats": {
                "total_cvs": total_cvs,
                "total_analyses": total_analyses,
                "pending_review": total_cvs - total_analyses,
                "average_ats_score": round(avg_score, 2),
                "top_candidates": top_candidates
            }
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"status": "error", "error": str(e)}
        )
