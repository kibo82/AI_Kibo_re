from selenium import webdriver
import os
import urllib3
import screen_brightness_control as sbc
import asyncio
# from winrt.windows.devices import radios
import requests
import json
from decouple import config
import pyaudio
import wave
import sqlite3
from datetime import datetime
from konlpy.tag import Okt
from konlpy.tag import Kkma
import feedparser
import operator
import time


# async def bluetooth_power(stt):
#     all_radios = await radios.Radio.get_radios_async()
#     for this_radio in all_radios:
#         if this_radio.kind == radios.RadioKind.BLUETOOTH:
#             if stt == "True":
#                 result = await this_radio.set_state_async(radios.RadioState.ON)
#             else:
#                 result = await this_radio.set_state_async(radios.RadioState.OFF)


def errornotice():
    """
    지정된 작업이 없을 시 출력
    """
    print(ext(lang, "no_command"))


def internet_check():
    """
    인터넷 연결 확인 - 구글ip에 연결되는지 확인
    :return: 인터넷이 연결되어 있으면 True, 아니면 False 반환
    """
    http = urllib3.PoolManager()
    try:
        http.request('GET', 'http://216.58.192.142', timeout=3, retries=False)
        return True
    except urllib3.exceptions.NewConnectionError:
        return False


def mic_module(second):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = second
    WAVE_OUTPUT_FILENAME = "output.wav"

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    print(ext(lang, "mic_start"))

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print(ext(lang, "mic_end"))

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


def speech_module():
    """
    kakao api를 이용한 음성인식 모듈. 16khz, 16bit방식의 pcm 압축방식의 wav 파일만 적용가능함.
    SECRET_KEY: .env파일에 저장되어 있는 api 키
    headers: 카카오에게 파일을 넘겨줄 때 헤더
    :return:
    """
    SECRET_KEY = config('SECRET_KEY')

    headers = {
        # Transfer-Encoding: chunked # 보내는 양을 모를 때 헤더에 포함한다.
        'Host': 'kakaoi-newtone-openapi.kakao.com',
        'Content-Type': 'application/octet-stream',
        'X-DSS-Service': 'DICTATION',
        'Authorization': f'KakaoAK {SECRET_KEY}',
    }

    data = open("C:\\Users\\hyunb\\PycharmProjects\\Contrrol_Test\\output.wav",
                "rb").read()  # wav 파일을 바이너리 형태로 변수에 저장한다.
    response = requests.post('https://kakaoi-newtone-openapi.kakao.com/v1/recognize', headers=headers, data=data)
    # 요청 URL과 headers, data를 post방식으로 보내준다.

    # post방식으로 받은 텍스트를 json 라이브러리를 이용하여 결과값으로 변환
    try:
        result_json_string = response.text[response.text.index('{"type":"finalResult"'):response.text.rindex('}') + 1]
        result = json.loads(result_json_string)
    except ValueError:
        print(ext(lang, "mic_error"))
        return "re"
    else:
        return result['value']


def process_module(mic_re):
    """
    음성인식한 값을 처리해서 어떤 작업을 할 지 결정한다.
    konlpy의 kkma를 이용하여 명사, 숫자, 동사의 어근을 분리하여 리스트에 저장하고,
    인식되는 명사에 따라
    :param mic_re: 음성인식 결과
    :return:
    """
    kkma = Kkma()
    okt = Okt()
    nngcontainer = []
    vvcontainer = []
    nrcontainer = []
    fact_list = []

    main_txt = kkma.pos(mic_re)
    for i in range(len(main_txt)):
        tmp = main_txt[i]
        if "NNG" in tmp:
            nngcontainer.append(i)
        elif "VV" in tmp:
            vvcontainer.append(i)
        elif "NR" in tmp:
            nrcontainer.append(i)

    for i in range(len(nngcontainer)):
        tmpcnt = nngcontainer[i]
        tmp = main_txt[tmpcnt][0]
        if tmp == "밝기":
            pr_re = "brightness"
            for j in range(len(vvcontainer)):
                vvtmp = main_txt[vvcontainer[j]][0]
                if vvtmp == "낮추":
                    fact_list.append("down")
                    fact_list.append("0")
                elif vvtmp == "높이":
                    fact_list.append("up")
                    fact_list.append("0")
                elif vvtmp == "하" or vvtmp == "맞추":
                    fact_list.append("still")
                    for k in range(len(nrcontainer)):
                        nrtmp = main_txt[nrcontainer[k]][0]
                        fact_list.append(nrtmp)

        elif tmp == "메모":
            pr_re = "memo"
            tmparr = []
            tmptxt = mic_re.split()
            print(tmptxt)
            cnt = 0
            except_txt = kkma.pos(tmptxt[len(tmptxt) - 2])
            print(except_txt)

            if except_txt[len(except_txt) - 1][0] == '라고' and cnt == 0:
                for j in range(0, len(tmptxt) - 2):
                    tmparr.append(tmptxt[j])
                tmpstring = tmptxt[len(tmptxt) - 2]
                tmpstring = tmpstring[0:len(tmpstring) - 2]
                tmparr.append(tmpstring)
                string = " ".join(tmparr)
                fact_list.append(string)
                fact_list.append(True)
                cnt = 1

            elif cnt == 0:
                for j in range(0, len(tmptxt) - 2):
                    tmparr.append(tmptxt[j])
                string = " ".join(tmparr)
                fact_list.append(string)
                fact_list.append(True)
                cnt = 1

        elif tmp == "검색":
            cnt = 0
            pr_re = "internet_search"
            tmparr = []
            tmptxt = mic_re.split()
            firsttxt = okt.pos(tmptxt[0])
            print(firsttxt)
            if cnt == 0 and len(firsttxt) == 2 and firsttxt[1][0] == '에서' and firsttxt[1][1] == 'Josa':
                for j in range(1, len(tmptxt) - 1):
                    tmparr.append(tmptxt[j])
                string = " ".join(tmparr)
                fact_list.append(firsttxt[0][0])
                fact_list.append(string)
                cnt = 1
            elif cnt == 0:
                for j in range(0, len(tmptxt) - 1):
                    tmparr.append(tmptxt[j])
                string = " ".join(tmparr)
                fact_list.append("네이버")
                fact_list.append(string)
                cnt = 1

        elif tmp == "뉴스":
            pr_re = "news_parcing"

        else:
            pr_re = "Error"

    return pr_re, fact_list


def on_off_module(what, status):
    """
    WIFI, Bluetooh on off 기능.
    :param what:Wifi인지 Bluetooth 인지
    :param status:On, Off 여부
    :return:
    """
    if status == "on":
        st = "True"
    elif status == "off":
        st = "False"

    if what == "bluetooth":
        pass  # asyncio.run(bluetooth_power(st))
    elif what == "wifi":
        if st == "True":
            os.popen('netsh interface set interface "Wi-Fi" ENABLED')
        elif st == "False":
            os.popen('netsh interface set interface "Wi-Fi" DISABLED')


def brightness_module(status, degree):
    """
    화면 밝기 조정
    :param status: 밝기를 높일 것인지, 낮출 것인지, 특정 숫자로 맞출것인지
    :param degree: 밝기를 특정 숫자로 맞출 시 값
    :return:
    """
    if status == "up":
        sbc.set_brightness('+25')
    elif status == "down":
        sbc.set_brightness('-25')
    elif status == "still":
        sbc.set_brightness(degree)
    elif status == "max":
        sbc.set_brightness(100)
    elif status == "min":
        sbc.set_brightness(0)


def alarm_module(fact1, fact2):
    pass


def timer_module(fact1, fact2):
    pass


def memo_module(user_text, date_indicate):
    """
    스티커메모의 맨 위 메모를 수정하는 코드
    :param user_text:사용자가 원하는 텍스트
    :param date_indicate:날짜 표시 여부
    :return:
    """
    # 스티커 메모 텍스트를 connect로 연결한다.
    sticky_db = r"C:\Users\hyunb\AppData\Local\Packages\Microsoft.MicrosoftStickyNotes_8wekyb3d8bbwe\LocalState\plum.sqlite"
    con = sqlite3.connect(sticky_db)
    cur = con.cursor()
    # 텍스트에서 수정해야 할 부분을 추출한다.
    cur.execute("SELECT * FROM Note")
    data = cur.fetchall()
    data_len = len(data)
    tar_text = data[data_len - 1][0]
    text_for_edit = tar_text[0:41]
    # 텍스트를 날짜와 함께 수정한다.
    if date_indicate:
        now = datetime.now()
        current_time = " - " + str(now.year) + "/" + str(now.month) + "/" + str(now.day) + " " + str(
            now.hour) + ":" + str(now.minute)
    else:
        current_time = ""
    query = "update Note set Text=:want where Text=:target"
    parameters = {
        "target": tar_text,
        "want": text_for_edit + user_text + current_time
    }
    cur.execute(query, parameters)
    con.commit()
    con.close()


def program_module(program_name):
    pass


def search_module(pr_re, tar_search):
    """
    인터넷 검색 모듈
    :param website_def: 사이트별 쿼리 반환 함수
    :param pr_re: 자연어 처리 결과 -  검색할 사이트
    :param tar_search: 자연어 처리 결과 - 검색어
    :return:
    """

    def website_def(pr):
        """
        :param pr: 자연어 처리 결과
        :return: 사이트별 검색 쿼리
        """
        if pr == "구글":
            return "https://www.google.co.kr/search?q="
        elif pr == "네이버":
            return "https://search.naver.com/search.naver?query="
        elif pr == "다음":
            return "https://search.daum.net/search?w=tot&DA=YZR&t__nil_searchbox=btn&sug=&sugo=&sq=&o=&q="
        elif pr == "빙":
            return "https://www.bing.com/search?q="
        elif pr == "유튜브":
            return "https://www.youtube.com/results?search_query="
        elif pr == "나무위키":
            return "https://namu.wiki/w/"
        elif pr == "트위치":
            return "https://www.twitch.tv/search?term="
        else:
            return "Error"

    search_link = website_def(pr_re)
    if search_link == "Error":
        errornotice()
        return
    options = webdriver.ChromeOptions()
    options.add_argument(r"--user-data-dir=C:\users\hyunb\AppData\Local\Google\Chrome\User Data")
    driver = webdriver.Chrome(executable_path=r'C:\Users\hyunb\PycharmProjects\chromedriver.exe',
                              chrome_options=options)
    driver.get(search_link + tar_search)
    return driver


def news_module():
    """
    구글 뉴스 파싱 기능.
    최신 구글 뉴스를 가져와 제목들의 단어의 빈도수를 분석하고 높은 빈도수의 단어가 있는 기사를 추출한다.
    :return:
    """
    print(ext(lang, "news_notice"))
    print(ext(lang, "waiting"))
    print(" ")

    okt = Okt()
    url = "https://news.google.com/rss/topics/CAAqIQgKIhtDQkFTRGdvSUwyMHZNRFp4WkRNU0FtdHZLQUFQAQ?hl=ko&gl=KR&ceid=KR%3Ako"

    arr = []
    separr = []
    tmparr = []
    sortarr = []

    rss = feedparser.parse(url)
    cnt = int(len(rss.entries))

    stop_words = "한국경제신문 한국경제 조선일보 매일경제 뉴데일리 한겨레 뉴스 일보 명 중앙 것 노컷뉴스 세 전 조선비즈 한국 곳곳 성 국민"
    stop_words = stop_words.split(" ")

    for i in range(cnt):
        article = rss['entries'][i]
        arr.append([article['title'], article['link']])

    for i in range(cnt):
        tmp = okt.nouns(arr[i][0])
        sortarr.append(tmp)
        tmparr.append(tmp)
        for w in tmp:
            if w not in stop_words:
                separr.append(w)

    word2index = {}
    bow = []

    for voca in separr:
        if voca not in word2index.keys():
            word2index[voca] = len(word2index)
            # token을 읽으면서, word2index에 없는 (not in) 단어는 새로 추가하고, 이미 있는 단어는 넘깁니다.
            bow.insert(len(word2index) - 1, 1)
            # BoW 전체에 전부 기본값 1을 넣어줍니다. 단어의 개수는 최소 1개 이상이기 때문입니다.
        else:
            index = word2index.get(voca)
            # 재등장하는 단어의 인덱스를 받아옵니다.
            bow[index] = bow[index] + 1

    word2index = list(word2index)
    sortdic = {}
    for i in range(len(bow)):
        sortdic[word2index[i]] = bow[i]

    sortdic = sorted(sortdic.items(), key=operator.itemgetter(1), reverse=True)

    exarr = []

    for j in range(3):
        tmp = sortdic[j][0]
        apcnt = 0
        print(ext(lang, "news_result1") + "'" + tmp + "'" + ext(lang, "news_result2"))
        for i in range(len(sortarr)):
            if tmp in sortarr[i] and apcnt < 3:
                exarr.append(i)
                print(arr[i][0] + " " + arr[i][1])
                apcnt = apcnt + 1
        print(" ")


def what_to_do(pr_re, arg_list):
    """
    수행할 작업을 결정하고 함수 실행
    :param arg_list: 인자 리스트
    :param pr_re: 자연어 처리 결과 - 무엇을 실행할지
    :return: 지정된 작업이 없을 시 리턴해 종료시킴
    """
    if pr_re == "on_off":
        on_off_module(arg_list[0], arg_list[1])
        pass
    elif pr_re == "brightness":
        brightness_module(arg_list[0], arg_list[1])
    elif pr_re == "alarm":
        alarm_module(arg_list[0], arg_list[1])
    elif pr_re == "timer":
        timer_module(arg_list[0], arg_list[1])
    elif pr_re == "memo":
        memo_module(arg_list[0], arg_list[1])
    elif pr_re == "program":
        program_module(arg_list[0])
    elif pr_re == "internet_search":
        search_module(arg_list[0], arg_list[1])
    elif pr_re == "news_parcing":
        news_module()
    else:
        errornotice()
        return


def ext(what, tar_txt):
    """
    txt파일에서 불러와야 되는 텍스트 추출
    :param what:설정 or 언어 결정
    :param tar_txt: 가져올 텍스트 이름
    :return:
    """
    if what == set:
        textfile = 'setting.txt'
    else:
        textfile = what + '.txt'
    f = open(textfile, 'r', encoding='UTF8')
    text = f.read().split('\n')
    string_to_find = tar_txt
    for line in range(len(text)):
        if string_to_find in text[line]:
            tmp = text[line].split(':')
            return tmp[1]


def run():
    """
    전체 실행 +인터넷 연결 확인 코드
    인터넷이 연결되어 있지 않으면 인터넷 연결을 지속적으로 확인시킨다.
    :return:
    """
    print(ext(lang, "internet_test"))
    internet_test = internet_check()
    if not internet_test:
        print(ext(lang, "internet_error1"))
        tmp = input(ext(lang, "internet_error2"))
        if tmp != "Kibo":
            return run()
    else:
        print(ext(lang, "internet_success"))
        print()
        i = True
        while (i):
            mic_module(int(ext(set, "micsecond")))
            mic_re = speech_module()
            if mic_re != "re":
                i = False
                a, b = process_module(mic_re)
                if a != "Error":
                    what_to_do(a, b)
                    time.sleep(10)
                else:
                    errornotice()


# 언어설정 : kor과 eng 가능.
lang = "kor"
run()
