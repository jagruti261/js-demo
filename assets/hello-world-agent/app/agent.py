import logging
from dataclasses import dataclass
from typing import AsyncGenerator, Literal, Sequence

from langchain_core.tools import BaseTool
from opentelemetry import trace
from sap_cloud_sdk.agent_decorators import agent_config, agent_model, prompt_section

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

HELLO_WORLD_RESPONSE = "Hello World"


@agent_model(
    key="config.model",
    label="LLM Model",
    description="The language model powering this agent",
)
def get_model_name() -> str:
    return "sap/anthropic--claude-4.5-sonnet"


@agent_config(
    key="config.temperature",
    label="LLM Temperature",
    description="Controls randomness of responses (0.0 = deterministic, 1.0 = creative)",
)
def get_temperature() -> float:
    return 0.0


@agent_config(
    key="config.checkpointer.ttl_seconds",
    label="Thread TTL (seconds)",
    description="Evict inactive conversation threads after this period of "
                "inactivity. Set to 0 to disable eviction.",
)
def thread_ttl_seconds() -> int:
    return 3600  # 1 hour


@prompt_section(
    key="prompts.system",
    label="System Prompt",
    description="The full system prompt defining the agent's role and behavior",
    validation={"format": "markdown", "max_length": 5000},
)
def get_system_prompt() -> str:
    return "You are a simple Hello World agent. No matter what question the user asks, you MUST always respond with exactly: Helllo World\n\nDo not use any tools. Do not provide any other response. Just say Hello World."


@dataclass
class AgentResponse:
    status: Literal["input_required", "completed", "error"]
    message: str


class SampleAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self):
        pass

    @tracer.start_as_current_span("hello_world_agent._run_agent")
    async def _run_agent(self, query: str) -> str:
        """Core business logic: always returns Hello World.

        Args:
            query: The user's question (ignored — always returns Hello World)

        Returns:
            The string "Hello World"
        """
        # M1: Question received
        if query:
            logger.info("M1.achieved: question received by agent")
        else:
            logger.warning("M1.missed: no question payload received")

        # M2: Generate Hello World response
        try:
            response = HELLO_WORLD_RESPONSE
            logger.info("M2.achieved: hello world response generated")
        except Exception:
            logger.error("M2.missed: response generation failed")
            raise

        return response

    async def stream(
        self,
        query: str,
        context_id: str,
        tools: Sequence[BaseTool] | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Stream agent responses.

        Args:
            query: User query to process
            context_id: Context identifier for the conversation
            tools: Optional sequence of LangChain tools (not used by this agent)

        Yields:
            Status updates and final response
        """
        yield {
            "is_task_complete": False,
            "require_user_input": False,
            "content": "Processing...",
        }

        try:
            response = await self._run_agent(query)

            # M3: Response delivered
            logger.info("M3.achieved: hello world response delivered to user")

            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": response,
            }

        except Exception:
            logger.exception("Agent stream() failed")
            logger.error("M3.missed: response delivery failed")
            yield {
                "is_task_complete": True,
                "require_user_input": False,
                "content": "I encountered an error while processing your request. Please try again.",
            }

    async def invoke(
        self,
        query: str,
        context_id: str,
        tools: Sequence[BaseTool] | None = None,
    ) -> AgentResponse:
        """Invoke agent and return final response.

        Args:
            query: User query to process
            context_id: Context identifier for the conversation
            tools: Optional sequence of LangChain tools (not used by this agent)

        Returns:
            AgentResponse with status and message
        """
        last: dict = {}
        async for chunk in self.stream(query, context_id, tools=tools):
            last = chunk
        if last.get("is_task_complete"):
            return AgentResponse(status="completed", message=last["content"])
        if last.get("require_user_input"):
            return AgentResponse(status="input_required", message=last["content"])
        return AgentResponse(
            status="error", message=last.get("content", "Unknown error")
        )
