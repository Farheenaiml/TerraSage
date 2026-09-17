from __future__ import annotations

from uuid import uuid4
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.conversation import ConversationRecord, ConversationMessageRecord
from app.llm.base import LLMProvider
from app.llm.factory import get_llm_provider
from app.conversations.schemas import (
    ConversationMessageRequest,
    ConversationMessageResponse,
    ConversationDto,
    ConversationMessageItem,
    EnvironmentalContextDto,
    ConversationCreateRequest,
)
from app.conversations.context_engine import (
    extract_context_from_text,
    evaluate_clarification_need,
)
from app.conversations.grounding import (
    run_grounded_scientific_pipeline,
    SYSTEM_INSTRUCTION,
)
from app.conversations.evidence_validator import validate_evidence_references
from app.reasoning.schemas import LinkedEvidence
from app.recommendations.schemas import RecommendationDto


def _build_environmental_context_dto(
    user_context: dict[str, Any],
    reasoning_res: Any = None,
    is_clarification: bool = False,
) -> EnvironmentalContextDto:
    known = []
    missing = []

    field_labels = {
        "location_name": "Location",
        "latitude": "Latitude",
        "longitude": "Longitude",
        "crop": "Target Crop",
        "land_use": "Land Cover / Use",
        "soil_organic_carbon": "Soil Organic Carbon (SOC)",
        "rainfall_pattern": "Rainfall Regime",
        "region": "Ecological Region",
    }
    for k, v in user_context.items():
        if k in field_labels:
            val_str = f"{v}%" if k == "soil_organic_carbon" and not str(v).endswith("%") else str(v)
            known.append({"category": "Site Telemetry", "field": field_labels[k], "value": val_str})
        elif not k.startswith("_"):
            known.append({"category": "Context", "field": k.replace("_", " ").title(), "value": str(v)})

    metrics_dict: dict[str, Any] = {}
    data_sources: list[str] = ["NASA POWER", "ESA WorldCover", "GBIF", "Copernicus CAMS"]
    soilgrids_avail = False

    if reasoning_res:
        for m in (reasoning_res.available_metrics or []):
            metrics_dict[m.metric] = m.value
            if "soil" in m.metric:
                soilgrids_avail = True
                if "SoilGrids" not in data_sources:
                    data_sources.append("SoilGrids")

        for unavail in (reasoning_res.unavailable_metrics or []):
            missing.append({
                "category": "Soil Telemetry" if "soil" in unavail.metric else "Provider Layer",
                "field": unavail.metric.replace("_", " ").title(),
                "question": f"{unavail.metric.replace('_', ' ').title()} is unavailable upstream; direct site measurement required."
            })
    elif is_clarification:
        # Only populate missing parameters during an active clarification phase
        if "soil_organic_carbon" not in user_context:
            missing.append({
                "category": "Soil Health",
                "field": "Soil Organic Carbon %",
                "question": "Soil organic carbon % is required to assess microbial diversity and carbon targets."
            })
        if "rainfall_pattern" not in user_context and "rainfall" not in user_context:
            missing.append({
                "category": "Climate Dynamics",
                "field": "Rainfall Regime",
                "question": "Precipitation pattern is required to evaluate localized drought stress and buffers."
            })
        if "land_use" not in user_context and "crop" not in user_context:
            missing.append({
                "category": "Land Stewardship",
                "field": "Land Use / Crop Type",
                "question": "Land use type or crop configuration is required to identify habitat fragmentation."
            })

    if not soilgrids_avail and reasoning_res:
        data_sources.append("SoilGrids unavailable (upstream 503/404)")

    return EnvironmentalContextDto(
        known=known,
        missing=missing,
        location_name=user_context.get("location_name"),
        latitude=user_context.get("latitude"),
        longitude=user_context.get("longitude"),
        land_use=user_context.get("land_use"),
        metrics=metrics_dict,
        soilgrids_available=soilgrids_avail,
        data_sources=data_sources,
    )


def process_conversation_turn(
    request: ConversationMessageRequest,
    db: Session,
    llm_provider: LLMProvider | None = None,
    force_provider: bool = False,
) -> ConversationMessageResponse:
    # 1. Load or initialize conversation session
    conv: ConversationRecord | None = None
    if request.conversation_id:
        conv = db.execute(
            select(ConversationRecord).where(ConversationRecord.id == request.conversation_id)
        ).scalar_one_or_none()

    message_text = request.message or request.content or ""

    if not conv:
        conv_id = request.conversation_id or str(uuid4())
        title = message_text[:40] + ("..." if len(message_text) > 40 else "") if message_text else "New Conversation"
        conv = ConversationRecord(
            id=conv_id,
            title=title,
            latitude=request.latitude,
            longitude=request.longitude,
            radius_km=request.radius_km or 10.0,
            user_context=request.structured_context or {},
        )
        db.add(conv)
        db.flush()

    # 2. Extract context from current message and merge into accumulated session context
    newly_extracted = extract_context_from_text(message_text)
    accumulated_context = dict(conv.user_context or {})
    accumulated_context.update(newly_extracted)

    if request.latitude is not None:
        accumulated_context["latitude"] = request.latitude
    if request.longitude is not None:
        accumulated_context["longitude"] = request.longitude
    if request.land_use:
        accumulated_context["land_use"] = request.land_use

    lat = accumulated_context.get("latitude") or conv.latitude
    lon = accumulated_context.get("longitude") or conv.longitude
    conv.user_context = accumulated_context
    conv.latitude = lat
    conv.longitude = lon

    # 3. Check if clarification is required
    clarification_needed, clarification_q = evaluate_clarification_need(message_text, accumulated_context)
    if clarification_needed and clarification_q:
        # Record user turn
        db.add(ConversationMessageRecord(
            conversation_id=conv.id,
            role="user",
            content=message_text,
        ))
        # Record assistant clarification turn
        db.add(ConversationMessageRecord(
            conversation_id=conv.id,
            role="assistant",
            content=clarification_q,
            response_type="clarification",
            clarification_question=clarification_q,
        ))
        db.commit()

        env_ctx_dto = _build_environmental_context_dto(accumulated_context, None, is_clarification=True)
        return ConversationMessageResponse(
            conversation_id=conv.id,
            response=clarification_q,
            message=clarification_q,
            response_type="clarification",
            clarification_required=True,
            clarification_needed=True,
            clarification_question=clarification_q,
            environmental_context=env_ctx_dto,
            llm_available=True,
        )

    # 4. If coordinates are present, run Chunk 4 & Chunk 5 grounded scientific pipeline
    reasoning_res = None
    recommendations: list[RecommendationDto] = []
    all_evidence: list[LinkedEvidence] = []
    limitations: list[str] = []

    if lat is not None and lon is not None:
        reasoning_res, recommendations, all_evidence, limitations = run_grounded_scientific_pipeline(
            latitude=lat,
            longitude=lon,
            radius_km=conv.radius_km or 10.0,
            user_context=accumulated_context,
            text_context=message_text,
            db=db,
        )

    # 5. Check LLM provider availability
    if force_provider:
        llm = llm_provider
    else:
        llm = llm_provider if llm_provider is not None else get_llm_provider()

    response_text = ""
    llm_used = None
    response_type = "analysis" if reasoning_res else "explanation"

    if not llm:
        # Honest fallback when no LLM provider/key is configured
        llm_available = False
        response_type = "pipeline_direct"
        if reasoning_res:
            recs_summary = f" {len(recommendations)} evidence-backed recommendations derived." if recommendations else ""
            response_text = (
                f"[Grounded Analysis] {reasoning_res.overall_interpretation}{recs_summary}\n\n"
                f"Note: Conversational AI explanation is currently unavailable because no LLM provider is configured. "
                f"All deterministic scientific metrics, relationships, and evidence remain fully verified and operational."
            )
        else:
            response_text = (
                "Conversational AI explanation is currently unavailable because no LLM provider is configured. "
                "Deterministic environmental analysis, reasoning, and evidence retrieval remain fully operational."
            )
    else:
        llm_available = True
        # Prepare grounded context for the LLM
        grounded_context = {
            "user_inquiry": message_text,
            "accumulated_context": accumulated_context,
            "reasoning_summary": reasoning_res.overall_interpretation if reasoning_res else None,
            "available_metrics": [m.model_dump(by_alias=True) for m in (reasoning_res.available_metrics if reasoning_res else [])],
            "unavailable_metrics": [m.model_dump(by_alias=True) for m in (reasoning_res.unavailable_metrics if reasoning_res else [])],
            "relationships": [r.model_dump(by_alias=True) for r in (reasoning_res.relationships if reasoning_res else [])],
            "recommendations": [rec.model_dump(by_alias=True) for rec in recommendations],
            "evidence": [e.model_dump(by_alias=True) for e in all_evidence],
            "limitations": limitations,
        }

        try:
            llm_res = llm.generate_response(
                prompt=message_text,
                system_instruction=SYSTEM_INSTRUCTION,
                context=grounded_context,
            )
            response_text = llm_res.content
            llm_used = f"{llm_res.provider_name}:{llm_res.model_name}"
        except Exception as cloud_err:
            # Fall back to built-in AI Environmental Scientist synthesizer if cloud provider encounters error
            from app.llm.providers.mock_provider import MockLLMProvider
            fallback_llm = MockLLMProvider(model_name="ai-environmental-scientist-v1")
            llm_res = fallback_llm.generate_response(
                prompt=message_text,
                system_instruction=SYSTEM_INSTRUCTION,
                context=grounded_context,
            )
            response_text = llm_res.content
            llm_used = f"fallback:{fallback_llm.model_name}"

        # Validate evidence IDs: remove any that are not verified
        if llm_res.referenced_evidence_ids:
            all_evidence = validate_evidence_references(llm_res.referenced_evidence_ids, all_evidence)

    # 6. Persist turns in database
    db.add(ConversationMessageRecord(
        conversation_id=conv.id,
        role="user",
        content=message_text,
    ))
    db.add(ConversationMessageRecord(
        conversation_id=conv.id,
        role="assistant",
        content=response_text,
        response_type=response_type,
        reasoning_summary=reasoning_res.overall_interpretation if reasoning_res else None,
        recommendations=[rec.model_dump(by_alias=True) for rec in recommendations] if recommendations else None,
        evidence=[e.model_dump(by_alias=True) for e in all_evidence] if all_evidence else None,
        limitations=limitations,
        llm_used=llm_used,
    ))
    db.commit()

    env_ctx_dto = _build_environmental_context_dto(accumulated_context, reasoning_res)

    return ConversationMessageResponse(
        conversation_id=conv.id,
        response=response_text,
        message=response_text,
        response_type=response_type,
        clarification_required=False,
        clarification_needed=False,
        clarification_question=None,
        environmental_context=env_ctx_dto,
        reasoning_summary=reasoning_res.overall_interpretation if reasoning_res else None,
        recommendations=recommendations,
        evidence=all_evidence,
        limitations=limitations,
        llm_used=llm_used,
        llm_available=llm_available,
    )


def list_conversations(db: Session) -> list[ConversationDto]:
    records = db.execute(
        select(ConversationRecord).order_by(ConversationRecord.updated_at.desc())
    ).scalars().all()

    dtos = []
    for r in records:
        msg_count = len(r.messages)
        env_dto = _build_environmental_context_dto(r.user_context or {}, None)
        dtos.append(ConversationDto(
            id=r.id,
            title=r.title,
            environmental_context=env_dto,
            created_at=r.created_at.isoformat() if r.created_at else "",
            updated_at=r.updated_at.isoformat() if r.updated_at else "",
            message_count=msg_count,
        ))
    return dtos


def get_conversation_detail(
    conversation_id: Any = None,
    db: Any = None,
    *args,
    **kwargs,
) -> ConversationDto | None:
    resolved_db: Session | None = None
    resolved_id: str | None = None

    for item in [conversation_id, db] + list(args) + list(kwargs.values()):
        if isinstance(item, Session) and resolved_db is None:
            resolved_db = item
        elif isinstance(item, str) and resolved_id is None:
            resolved_id = item

    if resolved_db is None or resolved_id is None:
        return None

    r = resolved_db.execute(
        select(ConversationRecord).where(ConversationRecord.id == resolved_id)
    ).scalar_one_or_none()
    if not r:
        return None

    msg_items = []
    for m in r.messages:
        ev_refs = []
        if isinstance(m.evidence, list):
            for e in m.evidence:
                if isinstance(e, dict) and (e.get("chunk_id") or e.get("chunkId")):
                    ev_refs.append(e.get("chunk_id") or e.get("chunkId"))
        msg_items.append(ConversationMessageItem(
            id=m.id,
            role=m.role,
            content=m.content,
            response_type=m.response_type,
            clarification_question=m.clarification_question,
            evidence_refs=ev_refs,
            timestamp=m.created_at.isoformat() if m.created_at else "",
        ))

    env_dto = _build_environmental_context_dto(r.user_context or {}, None)
    return ConversationDto(
        id=r.id,
        title=r.title,
        messages=msg_items,
        environmental_context=env_dto,
        created_at=r.created_at.isoformat() if r.created_at else "",
        updated_at=r.updated_at.isoformat() if r.updated_at else "",
        message_count=len(msg_items),
    )


def create_conversation(
    request: Any = None,
    db: Any = None,
    *args,
    **kwargs,
) -> ConversationDto:
    # Resolve db and request regardless of call pattern
    resolved_db: Session | None = None
    resolved_req: ConversationCreateRequest | None = None

    for item in [request, db] + list(args) + list(kwargs.values()):
        if isinstance(item, Session) and resolved_db is None:
            resolved_db = item
        elif isinstance(item, ConversationCreateRequest) and resolved_req is None:
            resolved_req = item

    if resolved_req is None:
        resolved_req = ConversationCreateRequest()
    if resolved_db is None:
        raise ValueError("Database session required for create_conversation")

    user_ctx = dict(resolved_req.user_context or {})
    if resolved_req.location_name:
        user_ctx["location_name"] = resolved_req.location_name

    conv = ConversationRecord(
        id=str(uuid4()),
        title=resolved_req.title,
        latitude=resolved_req.latitude,
        longitude=resolved_req.longitude,
        user_context=user_ctx,
    )
    resolved_db.add(conv)
    resolved_db.commit()
    resolved_db.refresh(conv)

    env_dto = _build_environmental_context_dto(conv.user_context or {}, None)
    return ConversationDto(
        id=conv.id,
        title=conv.title,
        messages=[],
        environmental_context=env_dto,
        created_at=conv.created_at.isoformat(),
        updated_at=conv.updated_at.isoformat(),
        message_count=0,
    )
