from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.storage.blob import BlobServiceClient
from array import array
import os
from PIL import Image
import sys
import time
from datetime import datetime
from os.path import exists

#for cv
subscription_key = "bd5d3e51b6cf4fec8512dbd4eeafb2fd"
endpoint = "https://1111-aitestcv1129.cognitiveservices.azure.com/"
COMPUTERVISION_LOCATION = os.environ.get(
    "COMPUTERVISION_LOCATION", "eastus")
client = ComputerVisionClient(
    endpoint="https://" + COMPUTERVISION_LOCATION + ".api.cognitive.microsoft.com/",
    credentials=CognitiveServicesCredentials(subscription_key)
)

#for blob storage
storage_key = "3t0d2MKVMQzcYMG3v8KLSSPYnMchGLz2Lxf5s5ySi+eCsSoFS+WHClaSlvkhF/CKpOSb3x0YPgih+ASt5V3Avw=="
storage_account_name = "1111ainutrition"
connection_string = "DefaultEndpointsProtocol=https;AccountName=1111ainutrition;AccountKey=/Z0+zkkW593yYmZmWidzwm6nrVk1lr2Re7+Xi6O/Jhfev32IUH/VxY/XqhgJaf9TT5kqAkPC2H+5+AStn8t1kA==;EndpointSuffix=core.windows.net"
container_name = "nutrition"

def uploadImage(path):
    blob_name = "nutrition_tag"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container_name, blob=blob_name)
    with open(path, 'rb') as data:
        blob_client.upload_blob(data, overwrite = True)
    url = "https://" + storage_account_name + ".blob.core.windows.net/" + container_name + "/" + blob_name
    return url


def readImage():
    path = "./static/tag.png"
    if exists(path) == True:
        with open(path, "rb") as image_stream:
                image_analysis = client.recognize_printed_text_in_stream(
                    image=image_stream,
                )
    text_list = []
    for r in image_analysis.regions:
        for line in r.lines:
            for word in line.words:
                words = ""
                for word in line.words:
                    words += word.text
            text_list.append(words)
    per = []
    for i in range(len(text_list)):
        if text_list[i].__contains__('大卡'):
            per.append(text_list[i])
    print(text_list)
    return per

def return_intake_num(event):
    receive_text = event.message.text
    if receive_text.__contains__('公克'):
        return float(receive_text.split('公克')[0])
    elif receive_text.__contains__('毫升'):
        return float(receive_text.split('毫升')[0])

#每份 每100公克 每100毫升
# 1. 202大卡65·3大卡
# 2. 0，2大卡 0，2大卡
# 3. 20大卡 2大卡

def countCalories(event):
    per = readImage()
    intake_num = return_intake_num(event)
    calories = 0
    per_100 = ""
    if len(per) == 2:
        if per[1].__contains__('，'):
            per_100 = per[1].split('，')[1].split('大卡')[0]
        else:
            per_100 = per[1].split('大卡')[0]
        if intake_num != 0 and per_100 != "":
            c = float(intake_num / 100.0 * float(per_100))
            calories = format(c, '.1f')
    elif len(per) == 1:
        if per[0].__contains__(' '):
            per_100 = per[0].split(' ')[1].split('大卡')[0]
        elif per[0].__contains__('·'):
            per[0] = per[0].replace('·', '.')
            per_100 = per[0].split('大卡')[1]
        if intake_num != 0 and per_100 != "":
            c = float(intake_num / 100.0 * float(per_100))
            calories = format(c, '.1f')
    return calories