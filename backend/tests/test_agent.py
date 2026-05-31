import pytest
from unittest.mock import patch, MagicMock
from backend.app.agent.graph import generate_documentation


def test_generate_documentation_returns_string():
    mock_response = MagicMock()
    mock_response.content = '{"summary": "Adds two numbers", "description": "Simple addition", "parameters": [{"name": "a", "type": "int", "description": "first number"}, {"name": "b", "type": "int", "description": "second number"}], "returns": {"type": "int", "description": "sum"}, "raises": [], "warnings": [], "complexity": "O(1)"}'

    with patch("backend.app.agent.graph.ChatGoogleGenerativeAI") as mock_llm:
        mock_llm.return_value.invoke.return_value = mock_response
        result = generate_documentation(
            code="def add(a, b): return a + b",
            function_name="add",
            language="python",
        )
        assert isinstance(result, str)
        assert "add" in result


def test_generate_documentation_graceful_failure():
    with patch("backend.app.agent.graph.ChatGoogleGenerativeAI") as mock_llm:
        mock_llm.return_value.invoke.side_effect = Exception("invalid api error")
        result = generate_documentation(
            code="def add(a, b): return a + b",
            function_name="add",
            language="python",
        )
        assert isinstance(result, str)
        assert result is not None


def test_parse_response_strips_markdown_fences():
    from backend.app.agent.graph import parse_response
    state = {
        "raw_response": '```json\n{"summary": "test", "description": "desc", "parameters": [], "returns": {}, "raises": [], "warnings": [], "complexity": "O(1)"}\n```',
        "error": None,
        "retry_count": 0,
        "code": "",
        "language": "python",
        "function_name": "test",
        "parsed_doc": None,
        "formatted_markdown": None,
    }
    result = parse_response(state)
    assert result["parsed_doc"] is not None
    assert result["parsed_doc"]["summary"] == "test"