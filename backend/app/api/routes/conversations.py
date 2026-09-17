from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.conversations.schemas import (
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationDto,
    ConversationCreateRequest,
)
from app.conversations import service as conv_service

router = APIRouter(prefix="", tags=["conversations"])


@router.post(
    "/message",
    response_model=ConversationMessageResponse,
    summary="Process multi-turn conversation turn with grounded intelligence and clarification",
)
def post_conversation_message(
    request: ConversationMessageRequest,
    db: Session = Depends(get_db),
) -> ConversationMessageResponse:
    try:
        return conv_service.process_conversation_turn(request, db=db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversation turn processing failed: {err}",
        )


@router.get(
    "",
    response_model=list[ConversationDto],
    summary="List conversation sessions",
)
def list_conversations(
    db: Session = Depends(get_db),
) -> list[ConversationDto]:
    return conv_service.list_conversations(db=db)


@router.get(
    "/{conversation_id}",
    response_model=ConversationDto,
    summary="Get conversation detail with message history",
)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
) -> ConversationDto:
    conv = conv_service.get_conversation_detail(conversation_id, db=db)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation '{conversation_id}' not found.",
        )
    return conv


@router.post(
    "",
    response_model=ConversationDto,
    summary="Create new conversation session",
)
def create_conversation(
    request: ConversationCreateRequest,
    db: Session = Depends(get_db),
) -> ConversationDto:
    return conv_service.create_conversation(request, db=db)
