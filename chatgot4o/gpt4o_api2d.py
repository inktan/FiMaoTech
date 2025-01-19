import json
import requests
from PIL import Image
from io import BytesIO
import base64
from tqdm import tqdm
import os
import time

# 100点/0.35元
# 单纯的代码解答需要84点 0.294元 包含上下文
# 单纯的代码解答需要40点 0.14元 不包含上下文

# 本代码案例是图文一起
# 39279 27506 = 11773
# 612 800 = 188 
# 11773/188=62.62
# 当前每个请求花费65个点

# 27506/382=72
# all 4541+2026 =6567
# start 10+800+382=1192
# end 6567-1192 = 5375*100=537500个点


query_text="请根据以下三个标准对提供的街景图片进行评分分析：\
    1、街道清洁度评分，满分为3分，最低为0分。评分内容包括：生态清洁（行道树绿化、沿街绿地卫生、花卉状况、隔离带绿化、口袋公园情况）、\
    路面清洁（路面垃圾、建筑垃圾、施工垃圾、道路破损情况、道路标识、斑马线、路缘石、人行道、盲道破损情况）、运输清洁（重型货车覆盖、\
    垃圾车辆覆盖、非机动车运输覆盖、扬尘情况）、夜间照明（道路照明、非机动车道照明、人行道照明、交叉口照明）、\
    污染治理（空气质量、噪声、光污染）；2、街道整洁度评分，满分为3分，最低为0分。\
    评分内容包括：设施完整性（消防栓、变电箱、空调外机、信号灯、窨井盖、架空线情况）、\
    家具完整性（街道座椅、电话亭、交通隔离护栏、垃圾桶、公交站台、路灯、人行道路灯、租车等候牌、公共卫生间\、雕塑小品、邮筒、报刊亭）、\
    停放规范性（自行车、电动车、机动车停放、路边摊贩情况）；3、街道界面有序度评分，满分为3分，最低为0分。\
    评分内容包括：职能有序性（功能区划分、商业、工业、交通、居住布局）、路权有序性（机动车、非机动车、人行道宽度比例、数量比例、\
    过街设施、公交专用道、盲道、无障碍设施、非机动车等候区、公交等候区、骑行道提示、人行道隔离设施）、界面有序性（广告牌、店招牌、\
    街廓连续性、街道高宽比、开阔度、建筑外立面和谐度、街道整体视觉效果）。\
    请依据这三个评分标准对街景图片进行打分，计算三个评分的平均值，得出最终评分结果，最终评分在0到3之间。"

headers = {
# 'Authorization': 'Bearer fk192489-7dCTdBKwtYid3GzzAvy3om3gVEwSRBNU',
'Authorization': 'Bearer fk192612-pLVI3zuqAZCoCaeeDaZqmhia1uHmz4RE',
'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
'Content-Type': 'application/json'
}

url = "https://oa.api2d.net/v1/chat/completions"

def chat_gpt4o(img_info):
    if '.jpg' in img_info['img_path']:
        tmp = img_info['img_path'].replace('ai_out','txt_out').replace('.jpg','.txt')
    elif '.png' in img_info['img_path']:
        tmp = img_info['img_path'].replace('ai_out','txt_out').replace('.png','.txt')
    elif '.JPG' in img_info['img_path']:
        tmp = img_info['img_path'].replace('ai_out','txt_out').replace('.JPG','.txt')
    elif '.jpeg' in img_info['img_path']:
        tmp = img_info['img_path'].replace('ai_out','txt_out').replace('.jpeg','.txt')

    if os.path.exists(tmp):
        return

    payload = json.dumps({
    "model": "gpt-4o",
    #    "model": "gpt-3.5-turbo",
    #    "messages": [
    #       {
    #          "role": "user",
    #          "content": query_text
    #       }
    #    ],
    "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": query_text},
                    # {"type": "text", "text": '图中有几辆车是什么车'},
                    {
                        "type": "image_url",
                        "image_url":{
                            "url": f"data:image/jpeg;base64,{img_info['base64_image_data']}"
                            }
                    },
                ],
            }
        ],
        # "max_tokens":300,
        "safe_mode": False
    })

    while True:
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            converted_dict = json.loads(response.text)
            text = converted_dict['choices'][0]['message']['content']
            break
        except  Exception as e:
            print(e)
            print("Connection error. Trying again in 2 seconds.")
            time.sleep(2)
            # text = ''
            return

    string_without_empty_lines = '\n'.join([line for line in text.split('\n') if line.strip()])

    folder_path = os.path.dirname(tmp)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    with open(tmp, "w", encoding="utf-8") as file:
        file.write(string_without_empty_lines)

def main(img_folder):
    roots = []
    img_names = []
    img_paths = []
    accepted_formats = (".png", ".jpg", ".JPG", ".jpeg")
    for root, dirs, files in os.walk(img_folder):
        for file in files:
            if file.endswith(accepted_formats):
                roots.append(root)
                img_names.append(file)
                file_path = os.path.join(root, file)
                img_paths.append(file_path)

    # img_paths =[r'E:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai\sv_degree_10_ai\work']
    # img_paths =[r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai-分析数据\ai_out\拉萨传统商业街景筛选-ai\181(180)-1.png']
    
    # 单张图片消耗点数 计算前点数 23839
    # 单张图片消耗点数 计算后点数 23781 差 58点=0.203元

    # 1000P 人民币 ¥3.50

    for i, img_path in enumerate(tqdm(img_paths)):
        # if i>5: 
        #     continue
        # if i<=107:
        #     continue

        with Image.open(img_path) as img:
            image_bytes = BytesIO()
            img.save(image_bytes, format=img.format)
            image_bytes = image_bytes.getvalue()

        base64_image_data = base64.b64encode(image_bytes).decode('utf-8')
        print(img_path)
        img_info={
            'img_path':img_path,
            'base64_image_data':base64_image_data,
        }

        chat_gpt4o(img_info)

if __name__ == '__main__':
    img_folder = r'e:\work\spatio_evo_urbanvisenv_svi_leo371\风貌评估-gpt4o\ai-分析数据\ai_out'
    main(img_folder)