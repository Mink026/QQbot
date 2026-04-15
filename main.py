import asyncio
import json
from src.handler.dispatcher import handle_event
from src.scheduler.broadcast import proactive_scheduler_loop
from websockets.asyncio.client import connect
from config import BOT_TOKEN, NAPCAT_WS_URL, PROACTIVE_GROUP_IDS


async def connect_to_napcat():
    """连接到 NapCat WebSocket 服务"""
    url = f"{NAPCAT_WS_URL}?access_token={BOT_TOKEN}"
    headers = {}
    if BOT_TOKEN:
        headers["Authorization"] = f"Bearer {BOT_TOKEN}"

    while True:
        try:
            async with connect(url, additional_headers=headers) as websocket:
                print(f"已连接到 NapCat: {NAPCAT_WS_URL}")
                sched_task = asyncio.create_task(proactive_scheduler_loop(websocket))
                try:
                    async for message in websocket:
                        try:
                            event_data = json.loads(message)
                            await handle_event(event_data, websocket)
                        except json.JSONDecodeError as e:
                            print(f"JSON 解析错误: {e}")
                        except Exception as e:
                            print(f"处理事件时出错: {e}")
                finally:
                    sched_task.cancel()
                    try:
                        await sched_task
                    except asyncio.CancelledError:
                        pass
                        
        except Exception as e:
            print(f"连接断开，5秒后重试... 错误: {e}")
            # Linux ECONNREFUSED=111，Windows WSAECONNREFUSED=10061
            if isinstance(e, ConnectionRefusedError) or getattr(e, "errno", None) in (111, 10061):
                print(
                    f"NapCat 正向ws未开启: {NAPCAT_WS_URL}"
                )
            await asyncio.sleep(5)


async def main():
    """主函数"""
    print("正在启动 QQ Bot...")
    print(f"NapCat 地址: {NAPCAT_WS_URL}")
    if PROACTIVE_GROUP_IDS:
        print(f"定时群发已启用，群: {PROACTIVE_GROUP_IDS}（每天约 08:00 / 19:00 本地时间）")
    await connect_to_napcat()


if __name__ == "__main__":
    asyncio.run(main())
