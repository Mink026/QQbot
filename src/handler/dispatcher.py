import json
from message_handler import handle_message
from websockets.asyncio.client import ClientConnection


async def handle_event(event_data: dict, websocket: ClientConnection):
    """处理接收事件"""
    print(f"收到事件: {json.dumps(event_data, ensure_ascii=False, indent=2)}")

    if event_data.get("post_type") == "message":
        print(f"收到消息: {event_data.get('message')}")
        try:
            await handle_message(event_data, websocket)
        except Exception as e:
            print(f"处理消息时出错: {e}")
        # await websocket.send(
        #     json.dumps(
        #         {
        #             "action": "send_private_msg",
        #             "params": {
        #                 "user_id": 446952980,
        #                 "message": "测试"
        #             }
        #         }
        #     )
        # )
