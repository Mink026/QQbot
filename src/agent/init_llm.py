import asyncio
import config
from datetime import datetime

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.messages import SystemMessage

from .conversation_history import (
    append_turn,
    build_assistant_combined_for_cache,
    extract_final_assistant_text,
    history_as_messages,
)
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
    current_time = datetime.now().astimezone().isoformat(timespec="seconds")
    return (
        "Context for this @-mention (use these values in tools; do not make up IDs):\n"
        f"- current_time: {current_time}\n"
        f"- group_id: {group_id}\n"
        f"- group_name: {group_name}\n"
        f"- sender_name: {sender_name}\n"
        f"- sender_id: {sender_id}\n"
        f"- msg_id: {msg_id}\n"
        f"- text: {text}\n"
    )


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
        `create_agent` / LangGraph agent output. Prepends up to 20 prior turns for this
        group and appends this turn to local cache after completion.
        """
        user_content = _build_group_at_human_content(
            group_id=group_id,
            group_name=group_name,
            sender_name=sender_name,
            sender_id=sender_id,
            msg_id=msg_id,
            text=text,
        )
        prior = history_as_messages(group_id)
        messages_in = prior + [HumanMessage(content=user_content)]
        result = await self.agent.ainvoke({"messages": messages_in})
        messages_full = result.get("messages", [])
        # Only this round (exclude re-injected history) so cache is not duplicated.
        suffix = messages_full[len(prior) :]
        assistant_combined = build_assistant_combined_for_cache(suffix)
        append_turn(group_id, user_content, assistant_combined)
        return result


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
