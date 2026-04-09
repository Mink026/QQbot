import asyncio
import json
from websockets.asyncio.client import connect
from config import BOT_TOKEN, NAPCAT_WS_URL


async def handle_event(event_data):
    """处理接收到的事件"""
    print(f"收到事件: {json.dumps(event_data, ensure_ascii=False, indent=2)}")
    
    # 在这里添加你的事件处理逻辑
    # 例如：消息事件、好友请求等
    if event_data.get("post_type") == "message":
        print(f"收到消息: {event_data.get('message')}")


async def connect_to_napcat():
    """连接到 NapCat WebSocket 服务"""
    headers = {
        "Authorization": f"Bearer {BOT_TOKEN}"
    }
    
    while True:
        try:
            async with connect(NAPCAT_WS_URL, additional_headers=headers) as websocket:
                print(f"已连接到 NapCat: {NAPCAT_WS_URL}")
                
                # 持续接收消息
                async for message in websocket:
                    try:
                        event_data = json.loads(message)
                        await handle_event(event_data)
                    except json.JSONDecodeError as e:
                        print(f"JSON 解析错误: {e}")
                    except Exception as e:
                        print(f"处理事件时出错: {e}")
                        
        except Exception as e:
            print(f"连接断开，5秒后重试... 错误: {e}")
            await asyncio.sleep(5)


async def main():
    """主函数"""
    print("正在启动 QQ Bot...")
    print(f"NapCat 地址: {NAPCAT_WS_URL}")
    await connect_to_napcat()


if __name__ == "__main__":
    asyncio.run(main())