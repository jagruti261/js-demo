"""Unit and integration tests for the Hello World agent."""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture(autouse=True)
def use_agent_path(add_agent_to_path):
    """Ensure app/ is on sys.path for all tests in this module."""
    pass


class TestHelloWorldUnit:
    """Unit tests: verify the agent always returns 'Hello World'."""

    @pytest.mark.asyncio
    async def test_run_agent_returns_hello_world(self):
        """_run_agent() must always return 'Hello World' regardless of query."""
        from agent import SampleAgent

        agent = SampleAgent()
        result = await agent._run_agent("What is the weather today?")
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_run_agent_with_empty_query(self):
        """_run_agent() must return 'Hello World' even for empty input."""
        from agent import SampleAgent

        agent = SampleAgent()
        result = await agent._run_agent("")
        assert result == "Hello World"

    @pytest.mark.asyncio
    async def test_run_agent_with_any_question(self):
        """_run_agent() must return 'Hello World' for any question text."""
        from agent import SampleAgent

        agent = SampleAgent()
        for question in [
            "What is 2+2?",
            "Tell me a story",
            "Who are you?",
            "Explain quantum physics",
        ]:
            result = await agent._run_agent(question)
            assert result == "Hello World", f"Expected 'Hello World' for query: {question!r}"

    @pytest.mark.asyncio
    async def test_stream_yields_hello_world(self):
        """stream() must yield final content 'Hello World'."""
        from agent import SampleAgent

        agent = SampleAgent()
        results = []
        async for chunk in agent.stream("What is the capital of France?", "ctx-1"):
            results.append(chunk)

        assert len(results) >= 1
        final = results[-1]
        assert final["is_task_complete"] is True
        assert final["content"] == "Hello World"

    @pytest.mark.asyncio
    async def test_invoke_returns_hello_world(self):
        """invoke() must return AgentResponse with message 'Hello World'."""
        from agent import SampleAgent

        agent = SampleAgent()
        response = await agent.invoke("Any question here", "ctx-2")
        assert response.status == "completed"
        assert response.message == "Hello World"


class TestHelloWorldIntegration:
    """Integration test: end-to-end agent flow via invoke()."""

    @pytest.mark.asyncio
    async def test_end_to_end_hello_world(self):
        """Full end-to-end: agent receives question and responds with Hello World."""
        from agent import SampleAgent

        agent = SampleAgent()
        response = await agent.invoke(
            "Can you tell me something interesting?",
            context_id="integration-test-ctx",
        )
        assert response.status == "completed"
        assert response.message == "Hello World"
