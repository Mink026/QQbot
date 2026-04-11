"""当前 QQ 协议 WebSocket，供 agent 工具在无参情况下发送消息。"""

from __future__ import annotations

from contextvars import ContextVar

from websockets.asyncio.client import ClientConnection

current_qq_websocket: ContextVar[ClientConnection | None] = ContextVar(
    "current_qq_websocket", default=None
)
