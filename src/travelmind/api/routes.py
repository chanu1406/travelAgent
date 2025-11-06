"""
FastAPI Routes (Stub)

REST API endpoints for TravelMind.
Will be implemented in future iterations.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class TravelPlanRequest(BaseModel):
    """Request model for travel planning."""

    query: str
    export_formats: list[str] = ["markdown"]
    skip_hitl: bool = False


class TravelPlanResponse(BaseModel):
    """Response model for travel planning."""

    itinerary: dict
    output_files: dict[str, str]
    warnings: list[str] = []


@router.post("/plan", response_model=TravelPlanResponse)
async def create_travel_plan(request: TravelPlanRequest) -> TravelPlanResponse:
    """
    Create a travel plan from a natural language query.

    Args:
        request: Travel plan request with query and options

    Returns:
        Travel plan response with itinerary and export files

    Raises:
        HTTPException: If planning fails
    """
    raise HTTPException(status_code=501, detail="API implementation coming soon")


@router.get("/plan/{plan_id}")
async def get_travel_plan(plan_id: str) -> TravelPlanResponse:
    """
    Retrieve an existing travel plan.

    Args:
        plan_id: Unique plan identifier

    Returns:
        Travel plan response

    Raises:
        HTTPException: If plan not found
    """
    raise HTTPException(status_code=501, detail="API implementation coming soon")


@router.put("/plan/{plan_id}")
async def update_travel_plan(
    plan_id: str, request: TravelPlanRequest
) -> TravelPlanResponse:
    """
    Update an existing travel plan with HITL edits.

    Args:
        plan_id: Unique plan identifier
        request: Updated travel plan request

    Returns:
        Updated travel plan response

    Raises:
        HTTPException: If plan not found or update fails
    """
    raise HTTPException(status_code=501, detail="API implementation coming soon")


@router.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status message
    """
    return {"status": "ok", "message": "TravelMind API is running (stub)"}
