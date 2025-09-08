import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from app.llm_services.knowledge_mark.extractor import KnowledgeExtractor

@pytest.mark.asyncio
@patch('app.llm_services.knowledge_mark.extractor.ChatOpenAI')
async def test_extract_knowledge_points_from_solution_success(MockChatOpenAI):
    """
    Test successful extraction of knowledge points from a solution.
    """
    # Arrange
    # 1. Mock the LLM response
    mock_llm_instance = MockChatOpenAI.return_value
    mock_response_content = {
        "used_existing_knowledge_points": [1],
        "new_knowledge_points": [
            {
                "subject": "New Subject",
                "chapter": "New Chapter",
                "section": "New Section",
                "item": "New Item",
                "details": "New details."
            }
        ]
    }
    import json
    mock_response = MagicMock()
    mock_response.content = json.dumps(mock_response_content)
    # Use AsyncMock for async methods
    mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)

    # 2. Prepare test data
    extractor = KnowledgeExtractor()
    question_text = "What is the powerhouse of the cell?"
    solution_text = "The powerhouse of the cell is the mitochondria."
    existing_kps = [
        {"id": 1, "subject": "Biology", "chapter": "Cells", "section": "Organelles", "item": "Mitochondria"},
        {"id": 2, "subject": "Biology", "chapter": "Cells", "section": "Organelles", "item": "Nucleus"},
    ]

    # Act
    used_points, new_points = await extractor.extract_knowledge_points_from_solution(
        question_text=question_text,
        solution_text=solution_text,
        existing_knowledge_points=existing_kps
    )

    # Assert
    # Check that the LLM was called
    mock_llm_instance.ainvoke.assert_called_once()

    # Check that the used points are correct
    assert len(used_points) == 1
    assert used_points[0]["id"] == 1
    assert used_points[0]["item"] == "Mitochondria"

    # Check that the new points are correct
    assert len(new_points) == 1
    assert new_points[0]["item"] == "New Item"
    assert new_points[0]["subject"] == "New Subject"


@pytest.mark.asyncio
@patch('app.llm_services.knowledge_mark.extractor.ChatOpenAI')
async def test_extract_knowledge_points_from_solution_json_error(MockChatOpenAI):
    """
    Test extraction when the LLM returns invalid JSON.
    """
    # Arrange
    # 1. Mock the LLM response with invalid JSON
    mock_llm_instance = MockChatOpenAI.return_value
    mock_response = MagicMock()
    mock_response.content = "This is not valid JSON"
    mock_llm_instance.ainvoke = AsyncMock(return_value=mock_response)

    # 2. Prepare test data
    extractor = KnowledgeExtractor()
    question_text = "Some question"
    solution_text = "Some solution"

    # Act
    used_points, new_points = await extractor.extract_knowledge_points_from_solution(
        question_text=question_text,
        solution_text=solution_text
    )

    # Assert
    # Check that the LLM was called
    mock_llm_instance.ainvoke.assert_called_once()

    # Check that the function returns empty lists on JSON error
    assert used_points == []
    assert new_points == []
