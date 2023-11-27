from line_chatbot_api import *
from application import *
def call_meal_record(event):
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://1111ainutrition.blob.core.windows.net/nutrition/meal.png',
            title='記錄三餐熱量',
            text='請在下方點選您需要的服務項目',
            actions=[
                MessageAction(
                    label='辨識營養標籤',
                    text='辨識營養標籤'
                ),
                MessageAction(
                    label='手動輸入熱量',
                    text='手動輸入熱量'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

def call_send_liff(event, url, label):
    message = FlexSendMessage(
        alt_text="新增or修改商品",
        contents= {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "請您到以下網址填寫資料",
                    "weight": "bold",
                    "size": "lg"
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": label,
                    "uri": url
                    }
                }
                ],
                "flex": 0
            }
            }
    )
    line_bot_api.reply_message(event.reply_token, message)

def call_send_liff_noData(event, url):
    message = FlexSendMessage(
        alt_text="尚未新增商品",
        contents= {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "您尚未填寫個人基本資料\n請您到以下網址填寫資料",
                    "weight": "bold",
                    "size": "lg"
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                    "type": "uri",
                    "label": "新增使用者基本資料",
                    "uri": url
                    }
                }
                ],
                "flex": 0
            }
            }
    )
    line_bot_api.reply_message(event.reply_token, message)
