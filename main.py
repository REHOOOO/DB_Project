import requests
import uuid
import time
import base64
import json
import sqlite3

def input_info(): # 사용자 정보를 입력받아 리턴하는 함수
    gender = int(input(" 성별을 입력하세요 (남자 1, 여자 2) "))
    height = float(input("키를 입력하세요 (cm): "))
    weight = float(input("몸무게를 입력하세요 (kg): "))
    age = int(input("나이를 입력하세요: "))
    PA = int(input(""))
    return gender, height, weight, age, PA

def ocr(file_path):     # CLOVA OCR을 이용해 이미지에서 텍스트를 추출하는 함수
    api_url = 'https://2bwclle49c.apigw.ntruss.com/custom/v1/26532/9032c8f9fe48076d9b1fe6ee6c9f0e47170cb4cb33e1df43afac3fa35ad1f3c5/general'
    secret_key = 'QlVZenhLZHN1VHNtSGlkcXplY0VuZm9SWERLWVBMVVQ='
    image_file = file_path
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

def extraction(response):   # ocr 함수를 통해 가져온 json파일에서 text값을 추출하는 함수
    infer_texts = []    # infer_text를 추출하여 저장할 배열
    fields = response['images'][0]['fields']
    for field in fields:        # field는 fields안에 있는 각각의 요소가 된다
        infer_text = field.get('inferText', '')     # inferText 값을 찾을 수 없으면 빈 문자열을 반환
        infer_texts.append(infer_text)

    return infer_texts

def creat_db():     #데이터베이스 생성 함수
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # DV(1일 영양성분 기준치) 테이블 생성
    cursor.execute('''
        CREATE TABLE DV (
        Sodium float, 
        Carbohydrates float,
        Sugars float,
        Fat float,
        Trans_Fat float,
        Saturated_Fat float,
        Cholesterol float,
        Protein float)
    ''')
    # 위에서부터 순서대로
    # 나트륨, 탄수화물, 당류, 지방, 트랜스지방, 포화지방, 콜레스테롤, 단백질
    cursor.execute('''
        INSERT INTO DV VALUES(
        2000,
        324,
        100,
        54,
        NULL,
        15,
        300,
        55)      
    ''')

    # User 사용자의 영양성분 정보를 모아두는 테이블 생성
    cursor.execute('''
            CREATE TABLE User (
            Sodium float, 
            Carbohydrates float,
            Sugars float,
            Fat float,
            Trans_Fat float,
            Saturated_Fat float,
            Cholesterol float,
            Protein float)
        ''')

    conn.commit()
    conn.close()

def EER(gender, height, weight, age, PA):  #에너지필요추정량 계산 함수


def sort(infer_texts):     # 사용자의 영양정보를 정리하는 함수




if __name__ == '__main__':
    # creat_db()    # 데이터 베이스 생성 (데이터베이스가 없는 경우에만 실행)
    # gender, height, weight, age, PA = input_info()    # 사용자 정보를 입력 받음

    while True:
        user_input = input("사진을 업로드하려면 사진의 경로 입력 / 하루동안 먹은 영양성분을 조회하려면 show 입력 / 프로그램을 종료하려면 exit를 입력")
        if user_input == 'show':
            print('show')
        elif user_input == 'exit':
            print('프로그램이 종료됩니다')
            break
        else:
            # response = ocr('pic/IMG_1166.jpg')
            # with open('test.json', 'w', encoding='utf-8') as json_file:   # json 파일로 저장
            #     json.dump(response.json(), json_file, ensure_ascii=False, indent=4)
            with open('test.json', 'r', encoding='utf-8') as json_file:     # json 파일을 불러옴
                response = json.load(json_file)

            infer_texts = extraction(response)









