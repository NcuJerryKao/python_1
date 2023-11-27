from flask import *
from urllib.parse import parse_qsl, parse_qs
from line_chatbot_api import *
import datetime
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    LocationSendMessage, ImageSendMessage, StickerSendMessage,
    VideoSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackAction, MessageAction, URIAction,
    PostbackEvent, ConfirmTemplate, CarouselTemplate, CarouselColumn,
    ImageCarouselTemplate, ImageCarouselColumn, FlexSendMessage
)
from ocr import *
from service.meal_service import *
from function_of_db import *
import re

app = Flask(__name__)

@app.route("/callback", methods=['POST', 'GET'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'

@app.route("/index")
def index():
    return render_template('index.html')

@app.route("/userAdd")
def userAdd():
    return render_template('user_add.html')

@app.route("/userEdit")
def userEdit():
    return render_template('user_edit.html')

@app.route("/insert")
def insert():
    return render_template('manual_insert.html')

@app.route("/getUser/<user_id>", methods=["POST"])
def getUser(user_id):
    userinfo = read_user_info(user_id)
    return jsonify(userinfo)

@app.route("/receiveAddUser")
def receiveAddUser():
    return redirect(url_for('userAdd'))

@app.route("/receiveEditUser")
def receiveEditUser():
    return redirect(url_for('userEdit'))

@app.route("/receiveCalories")
def receiveCalories():
    return redirect(url_for('insert'))

@handler.add(MessageEvent)
def handle_something(event):
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name
    if event.message.type=='text':
        receive_text=event.message.text
        if '個人基本資訊' in receive_text:
            if check_user_info(user_id):
                call_userinfo_event(event)
            else:
                call_send_liff(event, "https://liff.line.me/1657754863-w01MLmpa", "新增使用者基本資料") #change to liff
        elif '查詢個人基本資料' in receive_text:
            try:
                userinfo = read_user_info(user_id)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(
                        text="您的基本資料如下\n\n性別: {}\n年齡: {}\n身高: {}\n體重: {}\nBMR: {}".format(userinfo[1], userinfo[2], userinfo[3], userinfo[4], userinfo[5])))
            except:
                call_send_liff_noData(event, "https://liff.line.me/1657754863-w01MLmpa", "新增使用者基本資料")
        elif '修改個人基本資料' in receive_text:
            try:
                userinfo = read_user_info(user_id)
                
                call_send_liff(event, "https://liff.line.me/1657754863-nAbY60od", "修改使用者基本資料")
            except:
                call_send_liff_noData(event, "https://liff.line.me/1657754863-w01MLmpa", "新增使用者基本資料")
            
        elif ('male' in receive_text or 'female' in receive_text) and '歲' in receive_text and '公分' in receive_text and '公斤' in receive_text:
            text = receive_text.split('\n')
            gender = text[0]
            age = int(text[1].split('歲')[0])
            height = int(text[2].split('公分')[0])
            weight = int(text[3].split('公斤')[0])
            if (gender == 'male'):
                bmr = round(
                    (66 + (13.7 * weight) + (5 * height) - (6.8 * age)), 2)
            else:
                bmr = round(
                    (655 + (9.6 * weight) + (1.8 * height) - (4.7 * age)), 2)
            
            user_info = [user_id, gender, age, height, weight]
            
            if check_user_info(user_id):
                update_user_info(user_info)
            else: 
                get_user_info(user_info)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text="您的基本資料如下\n\n性別: {}\n年齡: {}\n身高: {}\n體重: {}\nBMR: {}".format(gender, age, height, weight, bmr)))
        elif '一週熱量紀錄' in receive_text:
            if check_user_info(user_id):
                week = week_record(user_id)
                if len(week) != 0:
                    string = "以下為一週內熱量紀錄"
                    heat_total = 0
                    for i in range(len(week)):
                        string += "\n\n日期:" + str(week[i][0]) + "\n" + "熱量:" + str(week[i][1])
                        heat_total += week[i][1]
                    string += "\n\n7天內平均熱量:{}\n平均攝取狀態:{}".format(round(heat_total/len(week),2), week_reminder(user_id,(heat_total/len(week))))
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = string))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text ="您尚未記錄任何熱量"))
            else:
                line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="請先依照下列格式填寫您的基本資料\n\n性別:男/女\n年齡:XX歲\n身高:XX公分\n體重:XX公斤"))
        elif '記錄三餐熱量' in receive_text:
            call_meal_record(event)
        elif '辨識營養標籤' in receive_text:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請拍一張或上傳含有營養標籤的圖片"))
        elif '手動輸入熱量' in receive_text:
            call_send_liff(event, "https://liff.line.me/1657754863-0akgRPLG", "手動輸入熱量")
        elif '大卡' in receive_text and '日期' in receive_text:
            if check_user_info(user_id):
                text = receive_text.split('\n')
                date = text[0].split('日期:')[1]
                calories = int(text[1].split('大卡:')[1])
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                days = (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.datetime.strptime(date, "%Y-%m-%d")).days
                if days >= 0 and days < 7:
                    meal_record = [user_id, date, calories]
                    try:
                        total = record_heat(meal_record)
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "已新增{}的熱量{}大卡，共累計{}大卡".format(date, calories,total) + "\n\n當日攝取狀態:{}".format(daily_reminder(user_id,date))))
                    except ValueError :
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "修改後總值將小於0，確定無誤後請再次輸入"))
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "您輸入的日期未在過去七天內，請重新檢查日期是否錯誤"))
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "您尚未填寫資料，請您先去填寫"))
           
        elif receive_text.find('公克') != -1 or receive_text.find('毫升') != -1:
            if re.search('\d*', receive_text).group() == "" or float(re.search('\d*', receive_text).group()) <= 0:
                mess = "不符合格式，請您重新填寫"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = mess))
            path = "./static/tag.png"
            if exists(path) == True:
                if check_user_info(user_id):
                    calories = str(countCalories(event))
                    if calories == '0':
                        mess = "無法辨識，請您上傳完整營養標籤的圖片或是選擇手動輸入熱量"
                        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = mess))
                    else:
                        date = datetime.datetime.fromtimestamp(event.timestamp/ 1000).strftime("%Y-%m-%d")
                        meal_record = [user_id, date, float(countCalories(event))]
                        try:
                            total = record_heat(meal_record)
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "已新增{}的熱量{}大卡，共累計{}大卡".format(date, calories,total) + "\n當日攝取狀態:{}".format(daily_reminder(user_id,date))))
                        except ValueError :
                            line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "修改後總值將小於0，確定無誤後請再次輸入"))
                    os.remove("./static/tag.png")
                else:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "您尚未填寫資料，請您先去填寫"))
                    os.remove("./static/tag.png")
            else:
                mess = "無法紀錄，請您拍一張或上傳含有營養標籤的圖片"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text = mess))
        else:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="無法辨識的指令，請重新輸入..."))
    elif event.message.type == "image":
        message_content = line_bot_api.get_message_content(event.message.id)
        path = './static/tag.png'
        with open(path, 'wb') as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = "請填寫你攝取的量\n【請按照以下格式回答】\n\nXX公克或XX毫升"))
            
    
    
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
