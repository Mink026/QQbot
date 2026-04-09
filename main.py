import asyncio
import json
from websockets.asyncio.server import serve

# ========== 配置 ==========
HOST = "127.0.0.1"
PORT = 22222
TOKEN = "yEVDumriPuRYRxaioBfcBxKBKAalxqVjJVdmckpQVFC"   # 填写你在 NapCat 设置的 Token，不验证则设为 None
# ==========================


def verify_token(websocket) -> bool:
    """从请求头验证 Token"""
    if TOKEN is None:
        return True

    # NapCat 将 token 放在 Authorization 请求头
    auth_header = websocket.request.headers.get("Authorization", "")

    # 格式为 "Bearer your_token"
    if auth_header.startswith("Bearer "):
        received_token = auth_header[len("Bearer "):]
        return received_token == TOKEN

    return False


async def handle_event(websocket, event: dict):
    """处理事件"""
    post_type = event.get("post_type")

    if post_type == "message":
        msg_type = event.get("message_type")
        raw_msg = event.get("raw_message", "")
        sender = event.get("sender", {})
        nickname = sender.get("nickname", "未知")

        if msg_type == "group":
            group_id = event.get("group_id")
            user_id = event.get("user_id")
            print(f"[群消息] 群:{group_id} | {nickname}({user_id}): {raw_msg}")

        elif msg_type == "private":
            user_id = event.get("user_id")
            print(f"[私聊] {nickname}({user_id}): {raw_msg}")

            # 回复私聊
            await websocket.send(json.dumps({
                "action": "send_private_msg",
                "params": {
                    "user_id": user_id,
                    "message": f"收到：{raw_msg}"
                },
                "echo": "reply"
            }, ensure_ascii=False))

    elif post_type == "meta_event":
        meta_type = event.get("meta_event_type")
        if meta_type == "heartbeat":
            print("[心跳] ♥")
        elif meta_type == "lifecycle":
            print(f"[生命周期] {event.get('sub_type')}")

    elif post_type == "notice":
        print(f"[通知] {event.get('notice_type')}: {event}")

    elif "echo" in event:
        print(f"[API响应] {event}")

    else:
        print(f"[未知事件] {event}")


async def handler(websocket):
    """处理 NapCat 连接"""

    # 验证 Token
    if not verify_token(websocket):
        print(f"❌ Token 验证失败，拒绝连接")
        await websocket.close(1008, "Invalid token")
        return

    print(f"✅ NapCat 连接成功: {websocket.remote_address}")

    try:
        async for raw_message in websocket:
            try:
                event = json.loads(raw_message)
                await handle_event(websocket, event)
            except json.JSONDecodeError:
                print(f"⚠️ JSON 解析失败: {raw_message}")

    except Exception as e:
        print(f"❌ 连接异常: {e}")
    finally:
        print(f"🔌 NapCat 断开连接")


async def main():
    print(f"🚀 启动 WS 服务器: ws://{HOST}:{PORT}")
    if TOKEN:
        print(f"🔐 Token 验证已开启")
    else:
        print(f"⚠️  Token 验证未开启")

    async with serve(handler, HOST, PORT) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
