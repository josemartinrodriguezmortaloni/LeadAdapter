"""
Message generation API endpoints.

This module exposes the core functionality of LeadAdapter: generating
personalized outreach messages based on lead data and playbook strategies.

Endpoints:
    POST /messages/generate: Generate a personalized message for a lead

Error Handling:
    - 400: Invalid lead or playbook data
    - 422: Quality threshold not met after max attempts
    - 500: Unexpected server errors
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.container import get_generate_message_use_case
from application.dtos.requests import GenerateMessageRequest
from application.dtos.responses import ErrorResponse, GenerateMessageResponse
from application.use_cases.generate_message import GenerateMessageUseCase
from domain.exceptions.domain_exceptions import (
    InvalidLeadError,
    InvalidPlaybookError,
    QualityThresholdNotMetError,
)

router = APIRouter(prefix="/messages", tags=["Messages"])

GenerateMessageUseCaseDep = Annotated[
    GenerateMessageUseCase, Depends(get_generate_message_use_case)
]


@router.post(
    "/generate",
    response_model=GenerateMessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request data provided"},
        422: {"model": ErrorResponse, "description": "Validation failed"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def generate_message(
    request: GenerateMessageRequest,
    use_case: GenerateMessageUseCaseDep,
) -> GenerateMessageResponse:
    """
    Generate a personalized outreach message for a lead.

    Takes lead information, sender context, and a playbook strategy to
    generate a high-quality, personalized message suitable for the
    specified channel and sequence step.

    The generation process includes:
    1. Seniority inference from job title
    2. ICP profile matching
    3. Strategy selection based on context
    4. Quality-controlled message generation with retries

    Args:
        request: Contains lead data, sender info, playbook, channel,
            and sequence step for message generation.
        use_case: Injected use case (provided by FastAPI Depends).

    Returns:
        Generated message with quality metrics and metadata.

    Raises:
        HTTPException 400: If lead or playbook data is invalid.
        HTTPException 422: If quality threshold cannot be met.

    Example:
        >>> response = await client.post("/messages/generate", json={
        ...     "lead": {"first_name": "John", ...},
        ...     "sender": {"name": "Jane", ...},
        ...     "playbook": {...},
        ...     "channel": "linkedin",
        ...     "sequence_step": "initial"
        ... })
        >>> assert response.status_code == 200
        >>> assert response.json()["quality"]["passes_threshold"] is True
    """
    try:
        return await use_case.execute(request)
    except InvalidLeadError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid lead data", "detail": str(e), "code": "INVALID_LEAD"},
        ) from e
    except InvalidPlaybookError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid playbook data", "detail": str(e), "code": "INVALID_PLAYBOOK"},
        ) from e
    except QualityThresholdNotMetError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Quality threshold not met",
                "detail": f"Best score: {e.score}, threshold: {e.threshold}",
                "code": "QUALITY_THRESHOLD_NOT_MET",
            },
        ) from e
