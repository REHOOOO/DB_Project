import requests
import uuid
import time
import base64
import json

def input_info(): # 사용자 정보를 입력받아 리턴하는 함수
    height = float(input("키를 입력하세요 (cm): "))
    weight = float(input("몸무게를 입력하세요 (kg): "))
    age = int(input("나이를 입력하세요: "))
    return height, weight, age

def ocr(file_path):
    api_url = 'https://2bwclle49c.apigw.ntruss.com/custom/v1/26532/9032c8f9fe48076d9b1fe6ee6c9f0e47170cb4cb33e1df43afac3fa35ad1f3c5/general'
    secret_key = 'QlVZenhLZHN1VHNtSGlkcXplY0VuZm9SWERLWVBMVVQ='
    image_file = ''
    with open(image_file,'rb') as f:
        file_data=f.read()

    request_json = {
        'images':[
            {
                'format': 'jpg',
                'name': 'demo',
                'data': base64.b64encode(file_data).decode()
            }
        ],
        'requestId': str(uuid.uuid4()),
        'version': 'V2',
        'timestamp': int(round(time.time() * 1000))
    }

    payload = json.dumps(request_json).encode('UTF-8')
    headers = {
        'X-OCR-SECRET': secret_key,
        'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", api_url, headers=headers,data=payload)
    return response

if __name__ == '__main__':
    height, weight, age = input_info()
    response = ocr()

