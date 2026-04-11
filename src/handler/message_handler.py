import asyncio

from ..action import interaction
from ..agent.init_llm import default_group_agent, extract_final_assistant_text
from ..qq_ws_context import current_qq_websocket

from websockets.asyncio.client import ClientConnection


async def handle_message(event_data: dict, websocket: ClientConnection):
    token = current_qq_websocket.set(websocket)
    try:
        await _handle_message_inner(event_data, websocket)
    finally:
        current_qq_websocket.reset(token)


async def _handle_message_inner(event_data: dict, websocket: ClientConnection):
    # 群消息
    if event_data.get("message_type") == "group":
        group_id = event_data.get("group_id")
        group_name = event_data.get("group_name")
        sender_name = event_data.get("sender").get("nickname")
        sender_id = event_data.get("sender").get("user_id")
        msg_id = event_data.get("message_id")
        text = "".join(data.get("data").get("text") for data in event_data.get('message') if data.get("type") == "text")

        # 群@
        if "at" in [data.get("type") for data in event_data.get("message")]:
            at_info = [
                data.get("data").get("qq") for data in event_data.get("message") if data.get("type") == "at"
            ]
            print(
                f"""【{group_name}】 [{sender_name}] @{"+".join(at_info)} {text}"""
            )

            # @到自己
            if event_data.get("self_id") in [int(at_id) for at_id in at_info if at_id != "all"]:
                await interaction.set_msg_emoji_like(msg_id, websocket)
                result = await default_group_agent.ainvoke_group_at(
                    group_id=group_id,
                    group_name=group_name or "",
                    sender_name=sender_name or "",
                    sender_id=int(sender_id) if sender_id is not None else 0,
                    msg_id=int(msg_id) if msg_id is not None else 0,
                    text=text or "",
                )
                reply_body = extract_final_assistant_text(result.get("messages", []))
                if reply_body:
                    await asyncio.sleep(2)
                    await interaction.send_group_msg_reply(
                        group_id, msg_id, reply_body, websocket
                    )

        # await websocket.send(
        #     json.dumps(
        #         {
        #             "action": "send_group_msg",
        #             "params": {
        #                 "group_id": event_data.get("group_id"),
        #                 "message": "测试"
        #             }
        #         }
        #     )
        # )
    # print(datetime.datetime.now().strftime("%Y-%m-%d"))



