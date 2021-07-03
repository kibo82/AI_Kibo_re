(There is a document of developing process - Developing.hwp)

This program is Beta Version of AI Assistant - For Korean User - Run in Window.
This AI can do following function by STT(Korean Only)
1. WIFI/Bluetooth On, Off
2. Display brightness control
3. Write memo in windows sticky memo app (You have to write one blank memo before use this function)
4. Parsing Google News and arrange

(Emergency Notice!!! There is something fatal error with Bluetooth on off function. So I disabled it. If you want to activate, just uncomment this : line 6, line 21 to 28, line 236.)

And I wil add following function gradually.
1. Alarm & Timer
2. Run program automatically (ex. Edge, Chrome, and more app..)
3. Voice trigger
4. Using thread for multi-processing


This program needs to install following package.

  selenium, urlib3, screen_brightness_control, asyncio, winrt, requests, json, decouple, pyaudio, sqlite3, wave, datetime, konlpy, feedparser.

Some of these packages might be installed already when you install python.

And program also needs kakao stt api key. You can apply and get api keys free here (https://developers.kakao.com/)
Then make .env file and paste your api key.
(Also you can get some information in this blog : https://ai-creator.tistory.com/70)

You have to download kor.txt(eng.txt), main_second, setting.txt, chromedriver.exe for run this program.
And you also have to set the path of wav output for STT, chromedriver.exe and your chrome browser's user data directory in code. (line 104, 345, 346)

kor.txt and setting.txt must be in same directory with main_second.py.

This program must be run with administrator mode. (Run your IDE with administrator mode)




If there is any error with code, or you have any question with this code, please notice me in Issues tab.
