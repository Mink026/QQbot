import json
import random

from websockets.asyncio.client import ClientConnection


async def set_msg_emoji_like(msg_id: int, websocket: ClientConnection):
    """群中向消息贴表情（随机）"""
    emoji_id_lst = [171, 75, 10024, 128147, 128522]
    await websocket.send(
        json.dumps(
            {
                "action": "set_msg_emoji_like",
                "params": {
                    "message_id": msg_id,
                    "emoji_id": emoji_id_lst[random.randint(0, len(emoji_id_lst) - 1)],
                    "set": True
                }
            }
        )
    )
    print(f"给消息 {msg_id} 添加了表情")


async def send_group_msg_reply(group_id: int, msg_id: int, websocket: ClientConnection):
    """
    回复群聊消息
    """
    await websocket.send(
        json.dumps(
            {
                "action": "send_group_msg",
                "params": {
                    "group_id": group_id,
                    "message": [
                        {
                            "type": "reply",
                            "data": {
                                "id": str(msg_id)
                            }
                        },
                        {
                            "type": "text",
                            "data": {
                                "text": "你好呀"
                            }
                        }
                    ]
                }
            }
        )
    )
    print(f"回复了 {msg_id} 消息")
