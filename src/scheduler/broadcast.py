"""Daily proactive group messages at 08:00 and 19:00 (local timezone)."""

from __future__ import annotations

import asyncio
from datetime import date, datetime
from typing import Literal

import config
from websockets.asyncio.client import ClientConnection

from ..action import interaction
from ..agent.init_llm import default_group_agent, extract_final_assistant_text
from ..qq_ws_context import current_qq_websocket


async def _run_broadcast_for_group(
    websocket: ClientConnection,
    *,
    group_id: int,
    slot: Literal["morning", "evening"],
) -> None:
    result = await default_group_agent.ainvoke_scheduled_broadcast(
        group_id=group_id,
        group_name="",
        slot=slot,
    )
    body = extract_final_assistant_text(result.get("messages", []))
    if body.strip():
        await interaction.send_group_msg(group_id, body, websocket)


async def run_scheduled_broadcast(
    websocket: ClientConnection,
    slot: Literal["morning", "evening"],
) -> None:
    if not config.PROACTIVE_GROUP_IDS:
        return
    token = current_qq_websocket.set(websocket)
    try:
        for gid in config.PROACTIVE_GROUP_IDS:
            try:
                await _run_broadcast_for_group(websocket, group_id=gid, slot=slot)
            except Exception as e:
                print(f"定时群发失败 group_id={gid} slot={slot}: {e}")
    finally:
        current_qq_websocket.reset(token)


async def proactive_scheduler_loop(websocket: ClientConnection) -> None:
    """Wake periodically; fire morning/evening once per calendar day in a short window after :00."""
    last_date: date | None = None
    fired: dict[str, bool] = {"morning": False, "evening": False}
    while True:
        await asyncio.sleep(15)
        if not config.PROACTIVE_GROUP_IDS:
            continue
        now = datetime.now().astimezone()
        today = now.date()
        if today != last_date:
            last_date = today
            fired["morning"] = False
            fired["evening"] = False
        # First loop iteration in 08:00–08:01 or 19:00–19:01 local time
        if now.hour == 8 and now.minute <= 1 and not fired["morning"]:
            fired["morning"] = True
            await run_scheduled_broadcast(websocket, "morning")
        elif now.hour == 19 and now.minute <= 1 and not fired["evening"]:
            fired["evening"] = True
            await run_scheduled_broadcast(websocket, "evening")
