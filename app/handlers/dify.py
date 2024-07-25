# from ..db import db
# from ..config import Config
# from ..secret import Secret
# from logger import shared_logger
# import requests
# import json

# from ..models.contexts import Contexts
# from ..handlers.slack import send_select_list_msg
# from logger import shared_logger
# from ..extensions import celery_instance


# @celery_instance.task
# def handle_clickup_request(payload):
#     text = payload["event"]["text"]
#     tag_pattern = f"<@{Config.BOT_SLACK_ID}>"
#     cleaned_msg = text.replace(tag_pattern, "").strip()
#     try:
#         response = requests.post(
#             f"{Config.DIFY_BASE_URL}/chat-messages",
#             headers={
#                 "Authorization": f"Bearer {Secret.DIFY_TOKEN}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "inputs": {},
#                 "query": cleaned_msg,
#                 "response_mode": "blocking",
#                 "conversation_id": "",
#                 "user": "hans.wu",
#             },
#         )

#         if response.ok:
#             dify_msg = response.json()
#             answer = json.loads(
#                 (dify_msg["answer"].replace("```json\n", "").replace("\n```", ""))
#             )

#             contexts = Contexts.get_contexts(slack_user_id=payload["event"]["user"])
#             if not contexts:
#                 ctx = Contexts(
#                     slack_user_id=payload["event"]["user"],
#                     last_clickup_dify_answer=answer,
#                 )
#                 db.session.add(ctx)
#             else:
#                 contexts.last_clickup_dify_answer = answer
#             db.session.commit()

#             send_select_list_msg(
#                 request_msg=cleaned_msg, slack_user_id=payload["event"]["user"]
#             )
#     except Exception as e:
#         shared_logger.error(f"Error: {e}")
#         raise e
