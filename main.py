import asyncio
import json
import websockets


# 正向 WS（连接 NapCat）
async def connect_napcat():
    uri = "ws://127.0.0.1:3002"

    async with websockets.connect(uri) as ws:
        print("已连接 NapCat")

        async for message in ws:
            event = json.loads(message)

            if event.get("post_type") == "message":
                group_id = event.get("group_id")
                text = event.get("raw_message")
                print(f"收到消息: {text}")

                # 回复
                await ws.send(json.dumps({
                    "action": "send_group_msg",
                    "params": {
                        "group_id": group_id,
                        "message": f"收到: {text}"
                    },
                    "echo": "reply"
                }))


asyncio.run(connect_napcat())
