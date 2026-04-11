from typing import Literal, Sequence

from langchain.tools import tool
import config
from tavily import AsyncTavilyClient
from ..action import interaction

tavily_client = AsyncTavilyClient(config.TAVILY_KEY)


@tool
async def qq_send_group_msg(group_id: int, text: str) -> str:
    """
    Send a plain text message to a QQ group (not a reply to any message).
    Use this to post short status updates to the group, for example before
    invoking slow or functional tools (web search, crawl, etc.) so users know
    what you are doing. Do not use this for the final answer to the user who
    @-mentioned you; that answer is delivered separately by the host application.
    """
    try:
        await interaction.send_group_msg(group_id, text)
    except RuntimeError as e:
        return f"Failed: {e}"
    return "Plain group message sent."


@tool
async def qq_send_group_ai_record(
    group_id: int, text: str, character: str | None = None
) -> str:
    """
    Send an AI voice message to a QQ group (synthesized speech from text).
    `text` is what will be spoken. `character` is the NapCat voice profile id;
    omit it to use the default from server configuration (e.g. lucy-voice-female1).
    This is not a reply to a specific message; it posts a new voice record in the group.
    """
    try:
        await interaction.send_group_ai_record(group_id, text, character)
    except RuntimeError as e:
        return f"Failed: {e}"
    return "AI voice record sent to the group."


@tool
async def search(
    query: str,
    topic: Literal["general", "news", "finance"] = None,
    time_range: Literal["day", "week", "month", "year"] = None,
    include_domains: Sequence[str] = None,
    exclude_domains: Sequence[str] = None,
) -> dict:
    """
    Search the web using Tavily and return relevant results with content snippets.
    Use for real-time information, current events, or questions needing up-to-date
    web sources. Prefer `crawl_website` when deep multi-page exploration is needed.

    Args:
        query: Search query, e.g. "latest AI research papers 2025".
        topic: "news" for current events; "general" for broad searches; "finance" for markets.
        time_range: Filter by recency: "day", "week", "month", or "year".
        include_domains: Optional allowlist of domains (max 300).
        exclude_domains: Optional blocklist of domains (max 150).
    """
    try:
        response = await tavily_client.search(
            query,
            "advanced",
            topic,
            time_range,
            include_domains=include_domains,
            exclude_domains=exclude_domains,
        )
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def crawl_website(url: str, instructions: str) -> dict:
    """
    Crawl a site from a root URL and extract content across pages per natural-language
    instructions. Use when information is scattered across a site. Prefer `search`
    for quick real-time queries.

    Args:
        url: Root URL to start from, e.g. "https://docs.tavily.com".
        instructions: What to look for, e.g. "Find Python SDK authentication pages".
    """
    try:
        response = await tavily_client.crawl(
            url, instructions=instructions, max_breadth=20
        )
        return response
    except Exception as e:
        return {"error": str(e)}


tools_lst = [qq_send_group_msg, qq_send_group_ai_record, search, crawl_website]
