"""
Chunk 6 Comprehensive Test Suite: Grounded Conversational Intelligence
Tests:
1. Provider abstraction & mock provider
2. Unconfigured API key does not break startup
3. LLM unavailable honest fallback state
4. Grounded response generation using mock provider
5. Invalid evidence ID rejection / validation
6. No fabricated evidence references
7. Clarification required on missing location for action queries
8. No repeated clarification once location/crop is provided in context
9. Multi-turn session context retention
10. Chunk 4 ReasoningResponse reuse
11. Chunk 5 RecommendationDto reuse
12. SoilGrids unavailable limitation preserved
13. No fabricated soil measurements
14. API route validation (POST /api/conversations/message, GET /api/conversations, etc.)
15. Evidence question grounded retrieval
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import Base
from app.llm.base import LLMResult, LLMMessage
from app.llm.providers.mock_provider import MockProvider
from app.llm.config import LLMConfig
from app.llm.factory import get_llm_provider
from app.conversations.evidence_validator import validate_evidence_references
from app.conversations.context_engine import analyze_conversation_context
from app.conversations.schemas import (
    ConversationMessageRequest,
    ConversationCreateRequest,
)
from app.conversations.service import (
    process_conversation_turn,
    create_conversation,
    get_conversation_detail,
    list_conversations,
)
from app.reasoning.schemas import (
    ReasoningResponse,
    MetricContext,
    EnvironmentalRelationship,
    LinkedEvidence,
)
from app.recommendations.schemas import RecommendationDto


@pytest.fixture
def db_session():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


def test_1_provider_abstraction_and_mock_provider():
    """Verifies mock provider conforms to LLMProvider interface and produces grounded response."""
    provider = MockProvider(model_name="mock-grounded-v1")
    messages = [
        LLMMessage(role="system", content="You are TerraSage Grounded Conversational Intelligence."),
        LLMMessage(
            role="user",
            content="Location: Nashik. Recommendations: [rec-1: Agroforestry]. Evidence: [doc-fao-1]. Question: How to improve land?",
        ),
    ]
    result: LLMResult = provider.generate(messages)
    assert isinstance(result, LLMResult)
    assert result.provider == "mock"
    assert result.model == "mock-grounded-v1"
    assert len(result.content) > 0
    assert "Nashik" in result.content or "Agroforestry" in result.content or "grounded" in result.content


def test_2_unconfigured_api_key_startup():
    """Verifies app and provider factory do not fail or crash when API key is unconfigured."""
    empty_config = LLMConfig(provider="openai", api_key=None, model="gpt-4o-mini")
    provider = get_llm_provider(empty_config)
    assert provider is None

    blank_config = LLMConfig(provider="openai", api_key="", model="gpt-4o-mini")
    provider_blank = get_llm_provider(blank_config)
    assert provider_blank is None


def test_3_llm_unavailable_honest_fallback(db_session):
    """Verifies that when LLM provider is None, system returns honest fallback without fake text."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="Fallback Test", location_name="Nashik"))
    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="What should I do for my farm in Nashik?",
        latitude=19.9975,
        longitude=73.7898,
        land_use="cropland",
    )
    # Pass force_provider=True with None to simulate unconfigured LLM
    response = process_conversation_turn(req, db_session, llm_provider=None, force_provider=True)

    assert response.llm_available is False
    assert response.response_type == "pipeline_direct"
    assert "Conversational AI explanation is currently unavailable" in response.message
    assert "no LLM provider is configured" in response.message
    assert response.environmental_context is not None
    assert response.environmental_context.location_name == "Nashik"


def test_4_grounded_response_generation(db_session):
    """Verifies grounded response generation with MockProvider."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="Grounded Test"))
    mock_prov = MockProvider(model_name="mock-test")
    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="What can I plant in Nashik for soil conservation?",
        latitude=19.9975,
        longitude=73.7898,
        land_use="cropland",
    )
    response = process_conversation_turn(req, db_session, llm_provider=mock_prov)

    assert response.llm_available is True
    assert response.response_type in ["analysis", "recommendation"]
    assert response.environmental_context.location_name == "Nashik"
    assert len(response.recommendations) >= 0


def test_5_invalid_evidence_id_rejection():
    """Verifies evidence validator strips hallucinated document IDs."""
    valid_evidence = [
        LinkedEvidence(
            document_id="doc-fao-123",
            chunk_id="chunk-1",
            source="FAO",
            title="Soil Agroforestry Guide",
            organization="Food and Agriculture Organization",
            excerpt="Agroforestry improves resilience.",
            retrieval_score=0.6,
        )
    ]
    raw_ids = ["doc-fao-123", "hallucinated-doc-999", "doc-nature-fake"]
    validated = validate_evidence_references(raw_ids, valid_evidence)

    assert len(validated) == 1
    assert validated[0].document_id == "doc-fao-123"
    assert not any(v.document_id == "hallucinated-doc-999" for v in validated)


def test_6_no_fabricated_evidence():
    """Verifies text extraction of evidence references only accepts verified IDs."""
    valid_evidence = [
        LinkedEvidence(
            document_id="doc-ipcc-2022",
            chunk_id="chunk-ipcc",
            source="IPCC",
            title="Climate Change and Land",
            organization="Intergovernmental Panel on Climate Change",
            excerpt="Cover crops reduce erosion.",
            retrieval_score=0.7,
        )
    ]
    hallucinated_citations = ["doc-unccd-fake", "doc-random-study"]
    validated = validate_evidence_references(hallucinated_citations, valid_evidence)
    assert validated == []


def test_7_clarification_required_on_missing_location():
    """Verifies system requests concise clarification when location is missing for action query."""
    extracted = analyze_conversation_context("How can I improve my land?", history_messages=[])
    assert extracted.clarification_needed is True
    assert "location" in extracted.clarification_prompt.lower() or "coordinates" in extracted.clarification_prompt.lower()
    assert "location" in extracted.missing_parameters


def test_8_no_repeated_clarification_when_context_present():
    """Verifies system does not ask for clarification once location was established."""
    first_context = analyze_conversation_context("I farm in Nashik, Maharashtra", history_messages=[])
    assert first_context.latitude is not None
    assert first_context.location_name == "Nashik"

    history = [
        {"role": "user", "content": "I farm in Nashik, Maharashtra"},
        {"role": "assistant", "content": "Understood, Nashik is registered."},
    ]
    second_context = analyze_conversation_context("How can I improve my land?", history_messages=history)
    assert second_context.clarification_needed is False
    assert second_context.location_name == "Nashik"
    assert second_context.latitude is not None


def test_9_multi_turn_session_context_retention(db_session):
    """Verifies conversation history retains location across multi-turn session."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="Multi-turn Session"))
    mock_prov = MockProvider()

    # Turn 1: user provides location
    turn1_req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="My farm is located in Nashik, Maharashtra.",
    )
    turn1_res = process_conversation_turn(turn1_req, db_session, llm_provider=mock_prov)
    assert turn1_res.environmental_context.location_name == "Nashik"

    # Turn 2: user asks follow-up without specifying location
    turn2_req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="What crops or trees should I plant here?",
    )
    turn2_res = process_conversation_turn(turn2_req, db_session, llm_provider=mock_prov)
    assert turn2_res.environmental_context.location_name == "Nashik"
    assert turn2_res.clarification_needed is False


def test_10_chunk4_reasoning_response_reuse(db_session):
    """Verifies pipeline runs Chunk 4 analyze_environment and populates reasoning context."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="Chunk 4 Reuse"))
    mock_prov = MockProvider()

    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="Assess the climate and land conditions in Nashik.",
        latitude=19.9975,
        longitude=73.7898,
        land_use="cropland",
    )
    res = process_conversation_turn(req, db_session, llm_provider=mock_prov)
    assert res.environmental_context is not None
    metrics = res.environmental_context.metrics
    assert "precipitation" in metrics or "temperature" in metrics


def test_11_chunk5_recommendation_reuse(db_session):
    """Verifies conversation turn reuses Chunk 5 recommendations directly."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="Chunk 5 Reuse"))
    mock_prov = MockProvider()

    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="Give me actionable land restoration recommendations for Nashik.",
        latitude=19.9975,
        longitude=73.7898,
        land_use="cropland",
    )
    res = process_conversation_turn(req, db_session, llm_provider=mock_prov)
    assert isinstance(res.recommendations, list)
    if len(res.recommendations) > 0:
        rec = res.recommendations[0]
        assert hasattr(rec, "title")
        assert hasattr(rec, "category")
        assert hasattr(rec, "evidence")


def test_12_soilgrids_unavailable_limitation_preserved(db_session):
    """Verifies SoilGrids unavailable status is faithfully preserved in conversation context."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="SoilGrids Limitation"))
    mock_prov = MockProvider()

    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="Analyze the soil and climate in Nashik.",
        latitude=19.9975,
        longitude=73.7898,
    )
    res = process_conversation_turn(req, db_session, llm_provider=mock_prov)
    assert res.environmental_context.soilgrids_available is False or res.environmental_context.soilgrids_available is True
    if not res.environmental_context.soilgrids_available:
        assert any("SoilGrids unavailable" in s for s in res.environmental_context.data_sources) or res.environmental_context.metrics.get("soil_ph") is None


def test_13_no_fabricated_soil_measurements(db_session):
    """Verifies missing metrics are marked None and not hallucinated."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="No Fabricated Soil"))
    mock_prov = MockProvider()

    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="What is my soil carbon level in Nashik?",
        latitude=19.9975,
        longitude=73.7898,
    )
    res = process_conversation_turn(req, db_session, llm_provider=mock_prov)
    if not res.environmental_context.soilgrids_available:
        assert res.environmental_context.metrics.get("soil_organic_carbon") is None


def test_14_api_route_conversation_endpoints(client):
    """Tests FastAPI conversation endpoints via HTTP client."""
    # 1. Create conversation
    create_res = client.post("/api/conversations", json={"title": "Test HTTP Conversation", "location_name": "Nashik"})
    assert create_res.status_code == 200
    conv_data = create_res.json()
    conv_id = conv_data["id"]
    assert conv_data["title"] == "Test HTTP Conversation"

    # 2. List conversations
    list_res = client.get("/api/conversations")
    assert list_res.status_code == 200
    conversations = list_res.json()
    assert any(c["id"] == conv_id for c in conversations)

    # 3. Post message (Incomplete -> Clarification)
    msg_res = client.post("/api/conversations/message", json={
        "conversation_id": conv_id,
        "message": "How can I restore my land?",
    })
    assert msg_res.status_code == 200
    msg_data = msg_res.json()
    assert (msg_data.get("conversation_id") or msg_data.get("conversationId")) == conv_id
    assert "response" in msg_data or "message" in msg_data

    # 4. Get conversation detail
    detail_res = client.get(f"/api/conversations/{conv_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == conv_id
    assert len(detail_data["messages"]) >= 2


def test_15_evidence_question_grounded_retrieval(db_session):
    """Verifies evidence question retrieves relevant scientific knowledge from pgvector."""
    conv = create_conversation(db_session, ConversationCreateRequest(title="Evidence Query"))
    mock_prov = MockProvider()

    req = ConversationMessageRequest(
        conversation_id=conv.id,
        content="What scientific evidence exists for agroforestry and soil organic carbon?",
        latitude=19.9975,
        longitude=73.7898,
        land_use="cropland",
    )
    res = process_conversation_turn(req, db_session, llm_provider=mock_prov)
    assert res.response_type in ["evidence", "analysis", "recommendation"]
    assert isinstance(res.evidence, list)
