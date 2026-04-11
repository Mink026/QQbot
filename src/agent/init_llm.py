import asyncio
import config
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage

from .tools import tools_lst

from .system_prompt import sys_prompt


def _build_group_at_human_content(
    *,
    group_id: int,
    group_name: str,
    sender_name: str,
    sender_id: int,
    msg_id: int,
    text: str,
) -> str:
    return (
        "Context for this @-mention (use these values in tools; do not make up IDs):\n"
        f"- group_id: {group_id}\n"
        f"- group_name: {group_name}\n"
        f"- sender_name: {sender_name}\n"
        f"- sender_id: {sender_id}\n"
        f"- msg_id: {msg_id}\n"
        f"- text: {text}\n"
    )


def extract_final_assistant_text(messages: list[BaseMessage]) -> str:
    """Last AIMessage with no tool calls; used as the reply body for the @ message."""
    for msg in reversed(messages):
        if not isinstance(msg, AIMessage):
            continue
        if getattr(msg, "tool_calls", None):
            continue
        content = msg.content
        if content is None:
            continue
        if isinstance(content, str):
            if content.strip():
                return content
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    parts.append(block)
            joined = "".join(parts).strip()
            if joined:
                return joined
        else:
            s = str(content).strip()
            if s:
                return s
    return ""


class QQGroupAgent:
    """LangChain agent for QQ group @-mentions; `ainvoke` returns a `messages` dict like LangGraph."""

    def __init__(self) -> None:
        self.model = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            temperature=0.1,
            max_tokens=4096,
            timeout=120,
            api_key=config.AI_KEY,
            base_url=config.AI_BASE_URL,
        )
        self.agent = create_agent(
            model=self.model,
            tools=tools_lst,
            system_prompt=SystemMessage(
                content=[{"type": "text", "text": sys_prompt}]
            ),
        )

    def build_messages_for_group_at(
        self,
        *,
        group_id: int,
        group_name: str,
        sender_name: str,
        sender_id: int,
        msg_id: int,
        text: str,
    ) -> list[HumanMessage]:
        return [
            HumanMessage(
                content=_build_group_at_human_content(
                    group_id=group_id,
                    group_name=group_name,
                    sender_name=sender_name,
                    sender_id=sender_id,
                    msg_id=msg_id,
                    text=text,
                )
            )
        ]

    async def ainvoke_group_at(
        self,
        *,
        group_id: int,
        group_name: str,
        sender_name: str,
        sender_id: int,
        msg_id: int,
        text: str,
    ) -> dict:
        """
        Returns a dict with key `messages` (list of LangChain messages), same shape as
        `create_agent` / LangGraph agent output.
        """
        return await self.agent.ainvoke(
            {
                "messages": self.build_messages_for_group_at(
                    group_id=group_id,
                    group_name=group_name,
                    sender_name=sender_name,
                    sender_id=sender_id,
                    msg_id=msg_id,
                    text=text,
                )
            }
        )


default_group_agent = QQGroupAgent()


async def run_group_at_agent(
    *,
    group_id: int,
    group_name: str,
    sender_name: str,
    sender_id: int,
    msg_id: int,
    text: str,
    agent: QQGroupAgent | None = None,
) -> dict:
    """Convenience wrapper using `default_group_agent` unless `agent` is provided."""
    a = agent or default_group_agent
    return await a.ainvoke_group_at(
        group_id=group_id,
        group_name=group_name,
        sender_name=sender_name,
        sender_id=sender_id,
        msg_id=msg_id,
        text=text,
    )


if __name__ == "__main__":

    async def _demo() -> None:
        result = await default_group_agent.ainvoke_group_at(
            group_id=0,
            group_name="test",
            sender_name="user",
            sender_id=1,
            msg_id=99,
            text="帮我搜索一下https://docs.langchain.com/中关于异步调用模型的功能",
        )
        print(result)
        print("--- final ---", extract_final_assistant_text(result["messages"]))

    asyncio.run(_demo())
