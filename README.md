# video2text_bot
Simple telegram speechkit bot

Оцифровщик видео. Сервис позволяет извлекать текст из видео и аудио сообщений (в т.ч. и длиннее 30 секунд)
Сделан в виде Телеграм бота с помощью сервисов YandexCloud и SpeechKit.
Доступен в телеграме: @video2text_bot

Запустите

sudo pip3 install -r requirements.txt
python3 s2t.py

Возможно понадобится установить FFMPEG командой sudo apt-get install ffmpeg

В директории также лежит простой демон, перезапускающий бот в случае ошибок.
