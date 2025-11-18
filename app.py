"""
TravelMind Web Application

FastAPI backend that serves the frontend and provides API endpoints
for trip planning queries.
"""

import asyncio
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.travelmind.exceptions import (
    InsufficientPOIsError,
    InvalidDateError,
    InvalidDurationError,
    MissingDestinationError,
    NoPOIsFoundError,
    POISearchError,
    TravelMindError,
)
from src.travelmind.workflow.graph import create_workflow

# Create FastAPI app
app = FastAPI(
    title="TravelMind",
    description="AI-powered travel itinerary planner",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class TripRequest(BaseModel):
    """User trip planning request."""

    query: str


class TripResponse(BaseModel):
    """Trip planning response."""

    success: bool
    itinerary: dict | None = None
    error: str | None = None
    error_type: str | None = None


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the main frontend page."""
    with open("static/index.html", "r") as f:
        return f.read()


@app.post("/api/plan", response_model=TripResponse)
async def plan_trip(request: TripRequest):
    """
    Plan a trip based on natural language query.

    Args:
        request: User query (e.g., "4 days in Kyoto, love temples and coffee")

    Returns:
        Complete itinerary or error message
    """
    try:
        # Initialize workflow
        workflow = create_workflow()

        # Initial state
        initial_state = {
            "user_query": request.query,
            "conversation_history": [],
            "errors": [],
            "retry_count": 0,
            "completed_steps": [],
            "status": "running",
            "needs_clarification": False,
            "clarification_questions": [],
            "user_approved": True,  # Auto-approve for web UI
            "mobility": "walking",
        }

        # Run the workflow
        result = await workflow.ainvoke(initial_state)

        # Check if workflow succeeded
        if result.get("error"):
            return TripResponse(
                success=False,
                error=result["error"],
                error_type="WorkflowError",
            )

        # Return the itinerary
        return TripResponse(
            success=True,
            itinerary=result.get("itinerary"),
        )

    except MissingDestinationError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type="MissingDestination",
        )

    except InvalidDateError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type="InvalidDate",
        )

    except InvalidDurationError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type="InvalidDuration",
        )

    except NoPOIsFoundError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type="NoPOIsFound",
        )

    except POISearchError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type="POISearchError",
        )

    except InsufficientPOIsError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type="InsufficientPOIs",
        )

    except TravelMindError as e:
        return TripResponse(
            success=False,
            error=str(e),
            error_type=type(e).__name__,
        )

    except Exception as e:
        # Catch-all for unexpected errors
        return TripResponse(
            success=False,
            error=f"An unexpected error occurred: {str(e)}",
            error_type="UnexpectedError",
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "TravelMind API"}


# Mount static files (CSS, JS, images)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except RuntimeError:
    # Directory doesn't exist yet, will be created
    pass


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting TravelMind server...")
    print("📍 Frontend: http://localhost:8000")
    print("📍 API docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
