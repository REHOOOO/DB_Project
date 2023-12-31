import requests
import uuid
import time
import base64
import json
import sqlite3
import re
from datetime import datetime

def input_info():   # 사용자 정보를 입력받아 리턴하는 함수
    name = str(input("이름을 입력하세요 ")) # 이름을 입력받아 DB에 있는 사용자이면 그 데이터를 불러와 리턴
    if check_user(name):
        name, gender, detail, height, weight, age, month, PA = check_user(name)
    else:
        gender = input_range("성별을 입력하세요 (남자 1, 여자 2) ", 'int', 1, 2)
        if gender == 2:  # 추가사항
            detail = input_range("임신초기: 1, 임신중기: 2, 임신말기: 3, 수유부: 4, 해당사항 없음: 0을 입력하세요 ", 'int', 0, 4)

        else:
            detail = 0

        height = input_range("키를 입력하세요 (cm): ", 'float', 0, 300)
        weight = input_range("몸무게를 입력하세요 (kg): ", 'float', 0, 700)

        age = input_range("나이를 입력하세요: ", 'int', 0, 200)
        if age == 0:  # 영아일 경우 개월 수를 입력 받는다
            month = input_range("개월 수를 입력해주세요 ", 'int', 0, 11)
        else:
            month = None

        PA = input_range("신체활동량을 입력하세요: 비활동적: 1, 저활동적: 2, 활동적: 3, 매우 활동적: 4를 입력하세요 ", 'int', 1, 4)
        insert_user(name, gender, detail, height, weight, age, month, PA)

    return name, gender, detail, height, weight, age, month, PA


def check_user(name):       # 사용자가 데이터베이스에 있다면 정보를 리턴
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
            SELECT *
            FROM User
            WHERE name = ?;
    '''
    ,(name,))

    result = cursor.fetchone()

    conn.close()

    return result

def insert_user(name, gender, detail, height, weight, age, month, PA):   # 입력받은 사용자 정보를 데이터베이스에 저장해준다
    insert_data = (name, gender, detail, height, weight, age, month, PA)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
            INSERT INTO User VALUES(?, ?, ?, ?, ?, ?, ?, ?); 
        ''', insert_data)

    conn.commit()
    conn.close()
    return

def input_range(str, type, min, max):  # 범위 내의 숫자만 입력받을 수 있게 해주는 함수
    while True:
        input_num = input(str)  # num을 입력받는다
        try:
            if type == 'int':
                num = int(input_num)
            elif type == 'float':
                num = float(input_num)

            if min <= num <= max:  # 입력값이 min 이상 max 이하인지 확인
                return num
            else:
                print("숫자가 범위 내에 있지 않습니다. 다시 입력해주세요")
        except ValueError:
            print("숫자가 아닙니다. 다시 입력해주세요")


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

def extract(response):   # ocr 함수를 통해 가져온 json파일에서 text값을 추출하는 함수
    infer_texts = []    # infer_text를 추출하여 저장할 배열
    fields = response['images'][0]['fields']
    for field in fields:        # field는 fields안에 있는 각각의 요소가 된다
        infer_text = field.get('inferText', '')     # inferText 값을 찾을 수 없으면 빈 문자열을 반환
        infer_texts.append(infer_text)

    return infer_texts

def creat_db():     #데이터베이스 생성 함수
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # user 테이블 생성
    cursor.execute('''
            CREATE TABLE User (
            name TEXT NOT NULL,
            gender int NOT NULL,
            detail int NOT NULL,
            height float NOT NULL,
            weight float NOT NULL,
            age NOT NULL,
            month int,
            PA int NOT NULL,
            PRIMARY KEY (name)
            );
        ''')

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
        Protein float);
    ''')
    # 위에서부터 순서대로
    # 나트륨, 탄수화물, 당류, 지방, 트랜스지방, 포화지방, 콜레스테롤, 단백질 (트랜스지방은 DV가 정해져있지 않음)
    cursor.execute('''
        INSERT INTO DV VALUES(
        2000,
        324,
        100,
        54,
        NULL,
        15,
        300,
        55);   
    ''')

    # User_data 사용자의 영양성분 정보를 모아두는 테이블 생성
    cursor.execute('''
            CREATE TABLE User_data (
            name TEXT NOT NULL,
            timestamp DATETIME NOT NULL,
            Sodium float, 
            Carbohydrates float,
            Sugars float,
            Fat float,
            Trans_Fat float,
            Saturated_Fat float,
            Cholesterol float,
            Protein float,
            FOREIGN KEY (name) REFERENCES User(name)
            ON DELETE CASCADE ON UPDATE CASCADE);
        ''')

    conn.commit()
    conn.close()

def EER_calc(gender, detail, height, weight, age, month, PA):  #에너지필요추정량 계산 함수
    height = height/100 # cm단위를 m 단위로 변경해준다
    if age <= 2:    # 2세 이하
        EER = 89 * weight - 100
        if age == 0:
            if month>=5:
                EER+=115.5
            else:
                EER+=22
        else:
            EER+=20

    elif age <= 19:   # 19세 이하
        if gender == 1:     # 남자
            if PA == 1:     # 비활동적
                PA = 1.0
            elif PA == 2:   # 저활동적
                PA = 1.13
            elif PA == 3:   # 활동적
                PA = 1.26
            elif PA == 4:   # 매우 활동적
                PA = 1.42
            EER = 88.5 - 61.9 * age + PA * (26.7 * weight + 903 * height)
        elif gender == 2:   # 여자
            if PA == 1:     # 비활동적
                PA = 1.0
            elif PA == 2:   # 저활동적
                PA = 1.16
            elif PA == 3:   # 활동적
                PA = 1.31
            elif PA == 4:   # 매우 활동적
                PA = 1.56
            EER = 135.3 - 30.8 * age + PA * (10.0 * weight + 934 * height)

        if age <= 8:
            EER += 20
        else:
            EER += 25

    else:   # 20세 이상
        if gender == 1:
            if PA == 1:     # 비활동적
                PA = 1.0
            elif PA == 2:   # 저활동적
                PA = 1.11
            elif PA == 3:   # 활동적
                PA = 1.25
            elif PA == 4:   # 매우 활동적
                PA = 1.48
            EER = 662 - 9.53 * age + PA * (15.91 * weight + 539.6 * height)
        elif gender == 2:
            if PA == 1:     # 비활동적
                PA = 1.0
            elif PA == 2:   # 저활동적
                PA = 1.12
            elif PA == 3:   # 활동적
                PA = 1.27
            elif PA == 4:   # 매우 활동적
                PA = 1.45
            EER = 354 - 6.91 * age + PA * (9.36 * weight + 726 * height)

            if detail == 2:     # 임신중기
                EER += 340
            elif detail == 3:   # 임신말기
                EER += 450
            elif detail == 4:   # 수유부
                EER += 340

    return EER

def extract_number(input_string):   # 문자열에서 숫자와 소수점만 추출하는 함수
    number = re.sub(r'[^0-9\.]','',input_string)
    if not number: # 만약 숫자가 없다면 number는 0으로 설정
        number = 0

    return float(number)

def DV_calc(EER):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM DV;')
    result = cursor.fetchone()

    conn.close()

    Sodium, Carbohydrates, Sugars, Fat, Trans_Fat, Saturated_Fat, Cholesterol, Protein = result
    ratio = EER / 2000  # 2000칼로리 기준으로 되어있는 DV(1일 영양성분 기준치)를 사용자의 EER에 맞추기 위해 비율을 구한다

    Sodium *= ratio
    Carbohydrates *= ratio
    Sugars *= ratio
    Fat *= ratio
    # Trans_Fat *= ratio    # 트랜스지방은 DV가 정해져있지 않아 NULL 값이다
    Saturated_Fat *= ratio
    Cholesterol *= ratio
    Protein *= ratio

    return Sodium, Carbohydrates, Sugars, Fat, Trans_Fat, Saturated_Fat, Cholesterol, Protein

def per(nume, deno):    # 퍼센트를 계산해 문자열로 리턴해주는 함수
    div = nume / deno
    div = round(div*100,4)
    percent = str(div) + '%'
    return percent

def sort(infer_texts, name, DV_Sodium, DV_Carbohydrates, DV_Sugars, DV_Fat, DV_Trans_Fat, DV_Saturated_Fat, DV_Cholesterol, DV_Protein):     # 사용자의 영양정보를 정리해서 데이터베이스에 넣어주는 함수
    for index, value in enumerate(infer_texts): # index와 값을 가져온다
        if value == '나트륨':  # 나트륨이 나온 다음 index에 나트륨 값이 들어있음
            Sodium = extract_number(infer_texts[index+1])
        elif value == '탄수화물':
            Carbohydrates = extract_number(infer_texts[index+1])
        elif value == '당류':
            Sugars = extract_number(infer_texts[index+1])
        elif value == '지방':
            Fat = extract_number(infer_texts[index+1])
        elif value == '트랜스지방':
            Trans_Fat = extract_number(infer_texts[index+1])
        elif value == '포화지방':
            Saturated_Fat = extract_number(infer_texts[index+1])
        elif value == '콜레스테롤':
            Cholesterol = extract_number(infer_texts[index+1])
        elif value == '단백질':
            Protein = extract_number(infer_texts[index+1])

    timestamp = datetime.now()
    # 데이터베이스에 저장하는 부분
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO User_data (name, timestamp, Sodium, Carbohydrates, Sugars, Fat, Trans_Fat, Saturated_Fat, Cholesterol, Protein)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    ''', (name, timestamp, Sodium, Carbohydrates, Sugars, Fat, Trans_Fat, Saturated_Fat, Cholesterol, Protein))

    conn.commit()
    conn.close()

    print('현재시간: ', timestamp, '    나트륨:', Sodium,'    탄수화물: ', Carbohydrates, '    당류: ', Sugars, '    지방: ', Fat, '    트랜스지방: ', Trans_Fat,'    포화지방: ',Saturated_Fat,'    콜레스테롤: ',Cholesterol,'    단백질: ',Protein)
    print('1일 영양성분 기준치에 대한 비율(%)', '    나트륨:', per(Sodium, DV_Sodium),'    탄수화물: ', per(Carbohydrates, DV_Carbohydrates),'    당류: ', per(Sugars,DV_Sugars), '    지방: ', per(Fat,DV_Fat),'    포화지방: ',per(Saturated_Fat,DV_Saturated_Fat),'    콜레스테롤: ',per(Cholesterol,DV_Cholesterol),'    단백질: ',per(Protein,DV_Protein))

    return

def oneday(name, date, EER):   # 입력받은 날짜의 영양정보를 출력
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT *
        FROM User_data
        WHERE name = ? AND DATE(timestamp) = ?;
    ''', (name, date))

    result = cursor.fetchall()

    print(name+ ' ' + date)
    for data in result:     # 그 날짜의 영양정보 출력
        exname, exdate, Sodium, Carbohydrates, Sugars, Fat, Trans_Fat, Saturated_Fat, Cholesterol, Protein = data
        timedata = datetime.strptime(exdate,"%Y-%m-%d %H:%M:%S.%f")
        extime = timedata.strftime("%H:%M:%S")
        print(str(extime) + ' 나트륨:', Sodium,'    탄수화물: ', Carbohydrates,'    당류: ', Sugars, '    지방: ', Fat,'    트랜스지방: ', Trans_Fat,'    포화지방: ', Saturated_Fat,'    콜레스테롤: ', Cholesterol,'    단백질: ', Protein)

    cursor.execute('''
            SELECT SUM(Sodium), SUM(Carbohydrates), SUM(Sugars), SUM(Fat), SUM(Saturated_Fat), SUM(Cholesterol), SUM(Protein)
            FROM User_data
            WHERE name = ? AND DATE(timestamp) = ?;
        ''', (name, date))

    result = cursor.fetchone()
    conn.close()

    DV_Sodium, DV_Carbohydrates, DV_Sugars, DV_Fat, DV_Trans_Fat, DV_Saturated_Fat, DV_Cholesterol, DV_Protein = DV_calc(EER)
    Sodium, Carbohydrates, Sugars, Fat, Saturated_Fat, Cholesterol, Protein = result
    print('    나트륨:', per(Sodium, DV_Sodium), '    탄수화물: ', per(Carbohydrates, DV_Carbohydrates), '    당류: ', per(Sugars,DV_Sugars), '    지방: ', per(Fat, DV_Fat), '    포화지방: ', per(Saturated_Fat, DV_Saturated_Fat), '    콜레스테롤: ', per(Cholesterol,DV_Cholesterol), '    단백질: ', per(Protein, DV_Protein))

def input_date(): # 날짜를 입력받는 함수
    while True:
        date = input("조회할 날짜를 입력하세요 (YYYY-MM-DD): ")
        try:
            timedata = datetime.strptime(date,"%Y-%m-%d")
            change_date = timedata.strftime("%Y-%m-%d")
            return str(change_date)
        except ValueError:
            print("올바른 날짜 형식이 아닙니다. 다시 입력해주세요.")

if __name__ == '__main__':
    # creat_db()    # 데이터 베이스 생성 (데이터베이스가 없는 경우에만 실행)
    name, gender, detail, height, weight, age, month, PA = input_info()    # 사용자 정보를 입력 받음
    EER = EER_calc(gender, detail, height, weight, age, month, PA)   # 사용자의 에너지필요추정량을 계산
    DV_Sodium, DV_Carbohydrates, DV_Sugars, DV_Fat, DV_Trans_Fat, DV_Saturated_Fat, DV_Cholesterol, DV_Protein = DV_calc(EER)   # 사용자 정보를 바탕으로 DV를 재계산해준다
    while True:
        user_input = input("사진을 업로드하려면 사진의 경로 입력 / 하루동안 먹은 영양성분을 조회하려면 show 입력 / 프로그램을 종료하려면 exit를 입력")
        if user_input == 'show':
            date = input_date()
            oneday(name, date, EER)
        elif user_input == 'exit':
            print('프로그램이 종료됩니다')
            break
        else:
            try:
                response = ocr(user_input)
                # with open('test.json', 'w', encoding='utf-8') as json_file:   # json 파일로 저장
                #     json.dump(response.json(), json_file, ensure_ascii=False, indent=4)
                # with open('test.json', 'r', encoding='utf-8') as json_file:     # json 파일을 불러옴
                #     response = json.load(json_file)
                json_string = json.dumps(response.json(), ensure_ascii=False, indent=4)
                infer_texts = extract(json.loads(json_string))
                sort(infer_texts, name, DV_Sodium, DV_Carbohydrates, DV_Sugars, DV_Fat, DV_Trans_Fat, DV_Saturated_Fat, DV_Cholesterol, DV_Protein)
            except FileNotFoundError:
                print("파일이 존재하지 않습니다. 다시 입력해주세요")