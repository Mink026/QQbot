import asyncio
import json
import config
from websockets.asyncio.server import serve

HOST = "127.0.0.1"
PORT = 22222
TOKEN = config.BOT_TOKEN  # 填你在 NapCat TUI 设置的 token，没有则设 None


async def handler(websocket):
    # 验证 Token（从握手请求头取）
    if TOKEN:
        auth = websocket.request.headers.get("Authorization", "")
        if auth != f"Bearer {TOKEN}":
            print(f"❌ Token 验证失败: [{auth}]")
            await websocket.close(1008, "Unauthorized")
            return

    # 打印连接信息
    self_id = websocket.request.headers.get("X-Self-ID", "未知")
    print(f"✅ NapCat 已连接！Bot QQ: {self_id}")
    print(f"   来自: {websocket.remote_address}")
    print("-" * 40)

    try:
        async for raw in websocket:
            event = json.loads(raw)
            post_type = event.get("post_type", "")

            # 过滤心跳，避免刷屏
            if post_type == "meta_event" and event.get("meta_event_type") == "heartbeat":
                print("[心跳] ♥")
                continue

            # 打印所有事件
            print(f"[{post_type}] {json.dumps(event, ensure_ascii=False, indent=2)}")

    except Exception as e:
        print(f"❌ 异常断开: {e}")
    finally:
        print("🔌 NapCat 断开")


async def main():
    print(f"🚀 监听 ws://{HOST}:{PORT}")
    print(f"📝 NapCat 反向WS 填写: ws://{HOST}:{PORT}")
    async with serve(handler, HOST, PORT) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
