import requests
import json
from linebot import (
    LineBotApi, WebhookHandler
)

line_access_token = "7JIAiRRjpm1ZoUKNVoA2w5tNxufx8QwZWX/M7kIwE71o6XaQrJdfrcSbv5mA48zyP5LXFTnJZ9sIQvABj31lBTXvt+Yd/YYjjj0g6MVbXks6t7YWpMfuzSbxPTHE13FkRrqUezfVNrgwW+EgtwA5sgdB04t89/1O/w1cDnyilFU="

Authorization_token = "Bearer " + line_access_token

headers = {"Authorization":Authorization_token, "Content-Type":"application/json"}

#---------------------------------------------------------------------------------

# body = {
#     "size": {"width": 2500, "height": 1680},
#     "selected": "false",
#     "name": "Menu",
#     "chatBarText": "選單",
#     "areas":[
#         {
#           "bounds": {"x": 0, "y": 0, "width": 2500, "height": 840},
#           "action": {"type": "message", "text": "個人基本資訊"}
#         },
#         {
#           "bounds": {"x": 0, "y": 841, "width": 1250, "height": 840},
#           "action": {"type": "message", "text": "一週熱量紀錄"}
#         },
#         {
#           "bounds": {"x": 1251, "y": 841, "width": 1250, "height": 840},
#           "action": {"type": "message", "text": "記錄三餐熱量"}
#         }
#     ]
#   }

# req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
#                        headers=headers,data=json.dumps(body).encode('utf-8'))

# print(req.text)

#---------------------------------------------------------------------------------

line_bot_api = LineBotApi(line_access_token)

rich_menu_id = "richmenu-30ca5a54a632b1223bcdd151761affd5" # 設定成我們的 Rich Menu ID

path = "./static/rich_menu.png"

with open(path, 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)

req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/'+rich_menu_id,
                       headers=headers)
print(req.text)

rich_menu_list = line_bot_api.get_rich_menu_list()