from ..action import interaction

from websockets.asyncio.client import ClientConnection


async def handle_message(event_data: dict, websocket: ClientConnection):

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
                # 给消息贴表情
                await interaction.set_msg_emoji_like(msg_id, websocket)
                # 回复消息
                await interaction.send_group_msg_reply(group_id, sender_id, websocket)

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



