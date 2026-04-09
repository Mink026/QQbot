import asyncio
import json
from src.handler.dispatcher import handle_event
from websockets.asyncio.client import connect
from config import BOT_TOKEN, NAPCAT_WS_URL


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
                
                # 持续接收消息
                async for message in websocket:
                    try:
                        event_data = json.loads(message)
                        await handle_event(event_data, websocket)
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析错误: {e}")
                    except Exception as e:
                        print(f"处理事件时出错: {e}")
                        
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
    await connect_to_napcat()


if __name__ == "__main__":
    asyncio.run(main())
