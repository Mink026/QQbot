"""Per-group local cache: last N user prompts + combined assistant (tool plain sends + final text)."""

from __future__ import annotations

import json
import re
import threading
from collections import defaultdict, deque

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

MAX_TURNS = 20

_PLAIN_POST_TOOLS = frozenset({"qq_send_group_msg", "qq_send_group_ai_record"})

_lock = threading.Lock()
_store: dict[int, deque[tuple[str, str]]] = defaultdict(lambda: deque(maxlen=MAX_TURNS))


def history_as_messages(group_id: int) -> list[HumanMessage | AIMessage]:
    """Prior turns as alternating HumanMessage / AIMessage for agent context."""
    with _lock:
        dq = _store.get(group_id)
        if not dq:
            return []
        out: list[HumanMessage | AIMessage] = []
        for user_content, assistant_content in dq:
            out.append(HumanMessage(content=user_content))
            out.append(AIMessage(content=assistant_content))
        return out


def append_turn(group_id: int, user_content: str, assistant_combined: str) -> None:
    with _lock:
        _store[group_id].append((user_content, assistant_combined))


def _tool_call_name(tc: object) -> str:
    if isinstance(tc, dict):
        return str(tc.get("name") or "")
    return str(getattr(tc, "name", None) or "")


def _tool_call_args(tc: object) -> dict:
    raw: object
    if isinstance(tc, dict):
        raw = tc.get("args")
    else:
        raw = getattr(tc, "args", None)
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def extract_plain_tool_texts_from_messages(messages: list[BaseMessage]) -> list[str]:
    """Collect text sent to the group via plain-message tools, in chronological order."""
    lines: list[str] = []
    for msg in messages:
        if not isinstance(msg, AIMessage):
            continue
        for tc in getattr(msg, "tool_calls", None) or []:
            name = _tool_call_name(tc)
            if name not in _PLAIN_POST_TOOLS:
                continue
            args = _tool_call_args(tc)
            text = args.get("text")
            if isinstance(text, str) and text.strip():
                label = "voice" if name == "qq_send_group_ai_record" else "plain"
                lines.append(f"[{label}] {text.strip()}")
    return lines


def strip_markdown_for_qq(text: str) -> str:
    """Remove common Markdown so final replies are plain text in QQ."""
    if not text or not text.strip():
        return text
    t = text
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    t = re.sub(r"~~(.+?)~~", r"\1", t)
    while "**" in t:
        nt = re.sub(r"\*\*(.+?)\*\*", r"\1", t, flags=re.DOTALL)
        if nt == t:
            t = t.replace("**", "")
            break
        t = nt
    while "__" in t:
        nt = re.sub(r"__(.+?)__", r"\1", t, flags=re.DOTALL)
        if nt == t:
            t = t.replace("__", "")
            break
        t = nt
    t = re.sub(r"(?m)^#{1,6}\s+", "", t)
    t = re.sub(r"(?m)^\s*>\s?", "", t)
    t = re.sub(r"(?m)^\s*(\*{3,}|-{3,}|_{3,})\s*$", "", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def extract_final_assistant_text(messages: list[BaseMessage]) -> str:
    """Last AIMessage with no tool calls; used as the reply body for the @ message."""
    raw = ""
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
                raw = content
                break
        elif isinstance(content, list):
            parts = []
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif isinstance(block, str):
                    parts.append(block)
            joined = "".join(parts).strip()
            if joined:
                raw = joined
                break
        else:
            s = str(content).strip()
            if s:
                raw = s
                break
    return strip_markdown_for_qq(raw.strip()) if raw else ""


def build_assistant_combined_for_cache(messages: list[BaseMessage]) -> str:
    """Single assistant string: tool plain/voice texts + final model output."""
    plain_lines = extract_plain_tool_texts_from_messages(messages)
    final = extract_final_assistant_text(messages).strip()
    parts: list[str] = []
    if plain_lines:
        parts.append("Tool posts to group:\n" + "\n".join(plain_lines))
    if final:
        parts.append("Final reply (sent as @-reply):\n" + final)
    return "\n\n".join(parts) if parts else "(no assistant output)"
