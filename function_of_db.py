import sqlite3
from line_chatbot_api import *
import datetime

# 新增使用者資料
def get_user_info(userinfo):

    if (userinfo[1] == 'male'):
        bmr = round(
            (66 + (13.7 * userinfo[4]) + (5 * userinfo[3]) - (6.8 * userinfo[2])), 2)
    else:
        bmr = round(
            (655 + (9.6 * userinfo[4]) + (1.8 * userinfo[3]) - (4.7 * userinfo[2])), 2)
    BMI = userinfo[4] / (userinfo[3]/100)**2
    if BMI < 18.5:
        suggest = 35*userinfo[4]
    elif BMI >= 24:
        suggest = 25*userinfo[4]
    else:
        suggest = 30*userinfo[4]
    
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute("INSERT INTO user(`Line_id`, `gender`, `age`, `height`, `weight`, `BMR`, `suggest`) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(userinfo[0],userinfo[1],userinfo[2],userinfo[3],userinfo[4],bmr,suggest))
    con.commit()
    con.close()
    return 0

#檢查使用者是否已有資料
def check_user_info(line_id):
    flag = False
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    userdata = cur.execute("SELECT Line_id FROM user")
    for row in userdata:
        if line_id == row[0]:
            flag = True
            break
        else:
            flag = False
    con.close()
    return flag

def call_userinfo_event(event):
    message = TemplateSendMessage(
        alt_text='Buttons template',
        template=ButtonsTemplate(
            thumbnail_image_url='https://1111ainutrition.blob.core.windows.net/nutrition/meal.png',
            title='個人基本資料',
            text='請在下方點選您需要的服務項目',
            actions=[
                MessageAction(
                    label='查詢個人基本資料',
                    text='查詢個人基本資料'
                ),
                MessageAction(
                    label='修改個人基本資料',
                    text='修改個人基本資料'
                )
            ]
        )
    )
    line_bot_api.reply_message(event.reply_token, message)

#更新使用者資料
def update_user_info(change_info):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    if (change_info[1] == 'male'):
       bmr = round(
           (66 + (13.7 * change_info[4]) + (5 * change_info[3]) - (6.8 * change_info[2])), 2)
    else:
       bmr = round(
          (655 + (9.6 * change_info[4]) + (1.8 * change_info[3]) - (4.7 * change_info[2])), 2)
    BMI = change_info[4] / (change_info[3]/100)**2
    if BMI < 18.5:
        suggest = 35*change_info[4]
    elif BMI >= 24:
        suggest = 25*change_info[4]
    else:
        suggest = 30*change_info[4]
    cur.execute("UPDATE user SET gender = '{}', age = '{}', height = '{}', weight = '{}', BMR = '{}', suggest = '{}' WHERE Line_id = '{}'".format(change_info[1], change_info[2], change_info[3], change_info[4], bmr, suggest, change_info[0]))
    con.commit()
    con.close()
    return 0

# 讀取使用者資料
def read_user_info(line_id):
    user = []
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    user_data = cur.execute("SELECT * FROM user WHERE Line_id = '{}'".format(line_id))
    for row in user_data:
        for i in range(len(row)):
            user.append(row[i])
    con.close()
    return user

# 日提醒
def daily_reminder(line_id,date):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    user = cur.execute("SELECT BMR, suggest FROM user WHERE Line_id = '{}'".format(line_id))
    user_list = []
    for row in user:
        user_list.append(row[0])
        user_list.append(row[1])
    TEDD = cur.execute("SELECT TEDD FROM record WHERE Line_id = '{}' AND date = '{}'".format(line_id,date))
    TEDD_list = []
    for row in TEDD:
        if row[0] < user_list[0]:
            con.close()
            return '營養攝取不足'
        elif row[0] < user_list[1]-100:
                con.close()
                return '未達每日建議量'
        elif row[0] > user_list[1]+100:
                over = row[0] - user_list[1]
                con.close()
                return '\n超過每日建議量{}大卡'.format(int(over))
        else:
            con.close()
            return '已達成每日建議量'

#平均提醒
def week_reminder(line_id, heat):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    user = cur.execute("SELECT BMR, suggest FROM user WHERE Line_id = '{}'".format(line_id))
    for row in user:
            if heat < row[0]:
                con.close()
                return '營養攝取不足'
            elif heat < row[1]-100:
                con.close()
                return '未達建議攝取量'
            elif heat > row[1]+100:
                over = heat - row[1]
                con.close()
                return '超過建議量{}'.format(int(over))
            else:
                con.close()
                return '已達成建議攝取量'

            
# 熱量紀錄並回報總值
def record_heat(meal_record):
    flag_id = False
    flag_date = False
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    user = cur.execute("SELECT Line_id, date FROM record")
    for row in user:
        if row[0] == meal_record[0] and row[1] == meal_record[1]:
            flag = True
            break
        else:
            flag = False
    if flag:
        info = cur.execute("SELECT TEDD FROM record WHERE Line_id = '{}' AND date = '{}'".format(meal_record[0], meal_record[1]))
        for row in info:
            tmp = row[0] + meal_record[2]
            if tmp >= 0:
                cur.execute("UPDATE record SET TEDD='{}' WHERE Line_id = '{}' AND date = '{}'".format(tmp, meal_record[0], meal_record[1]))
                con.commit()
                con.close()
                return tmp
            else:
                con.commit()
                con.close()
                raise ValueError
    else:
        cur.execute("INSERT INTO record(`Line_id`, `date`, `TEDD`) VALUES('{}', '{}' ,'{}')".format(meal_record[0], meal_record[1], meal_record[2]))
        con.commit()
        con.close()
        return meal_record[2]


# 清除過期資料(資料過多會導致查詢功能延遲)
def delete_record():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    date = cur.execute("SELECT date FROM record")
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    for row in date:
        days = (datetime.datetime.strptime(today, "%Y-%m-%d") - datetime.datetime.strptime(row[0], "%Y-%m-%d")).days
        if days >= 7:
            cur.execute("DELETE FROM record WHERE date = '{}'".format(row[0]))
    con.commit()
    con.close()
    return 0

# 查詢一週熱量
def week_record(user_id):
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    delete_record()
    data = cur.execute("SELECT * FROM record WHERE Line_id = '{}' ORDER BY date".format(user_id))
    record =[]
    for row in data:
        for i in range(7):
            if row[2] == (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d"):
                record.append([row[2], row[3]])
    con.close()
    return record
    