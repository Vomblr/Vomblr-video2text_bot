#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import telebot
from telebot import apihelper
import requests
import json
from moviepy.editor import AudioFileClip
import os
import math
import tempfile

yaToken = 'YOUR TOKEN'
folder_id = 'YOUR FOLDER ID'
telegram_token = 'YOUR TELEGRAM TOKEN'

ip = 'orbtl.s5.opennetwork.cc'
port = '999'
user = '138547602'
password = 'GZQpc7jd'

proxies = {
    'https': 'socks5://{}:{}@{}:{}'.format(user, password, ip, port)
}

apihelper.proxy = proxies

bot = telebot.TeleBot(token=telegram_token)


def getSpeech(bitData):
    header = {
        'Authorization': "Bearer {}".format(yaToken)
    }
    data = bitData
    link = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?folderId={}".format(folder_id)

    file = requests.post(link, data=data, headers=header)
    response = json.loads(file.text)
    return response['result']


@bot.message_handler(commands=['start'])
def handler_start(message):
    print('пользователь с id {} что-то тебе пишет'.format(message))
    bot.send_message(message.chat.id, "Привет! Скажи мне что-то голосом, а лучше запиши видео!")


@bot.message_handler(content_types=['voice'])
def voice_processing(message):

    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{}/{}'.format(telegram_token, file_info.file_path),
                        proxies=proxies)

    try:
        binaryContent = file.content
        text = getSpeech(binaryContent)
        bot.send_message(message.chat.id, text)
    except Exception as err:
        bot.send_message(message.chat.id, err)


@bot.message_handler(content_types=['text'])
def handler_text(message):
    print('пользователь с id {} что-то тебе пишет'.format(message))
    bot.send_message(message.chat.id, "Скажи мне что-то голосом, а лучше запиши видео!")


def extract_audio(filepath, fragment_size=10):
        fragments = []

        audio_clip = AudioFileClip(filepath, fps=15000)
        count_of_fragments = math.ceil(audio_clip.duration / fragment_size)

        for i in range(count_of_fragments):
            t_start = i * fragment_size
            t_end = min(t_start + fragment_size, audio_clip.duration)
            audio_subclip = audio_clip.subclip(t_start, t_end)

            with tempfile.NamedTemporaryFile(suffix='.ogg') as fp:
                audio_subclip.write_audiofile(fp.name, logger=None)
                fragments.append(fp.read())

        return fragments


def get_text(filepath):
        headers = {
            'Authorization': "Bearer {}".format(yaToken)
        }
        params = {
            'folderId': folder_id,
            'lang': 'ru-RU'
        }
        try:
            audio_fragments = extract_audio(filepath)
            text_fragments = []

            for audio_content in audio_fragments:
                response = requests.post(
                    'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
                    data=audio_content,
                    headers=headers,
                    params=params
                )
                data = response.json()

                error_message = data.get('error_message')
                if error_message is None:
                    text_fragments.append(data['result'])
                else:
                    raise Exception(error_message)

            return ' '.join(text_fragments)

        except Exception as err:
            print(err)
            return 'Не удалось распознать текст'


@bot.message_handler(content_types=['video'])
def video_processing(message):
	file_info = bot.get_file(message.video.file_id)
	file = requests.get('https://api.telegram.org/file/bot{}/{}'.format(telegram_token, file_info.file_path),
                        proxies=proxies)
	with open('video.mp4', 'wb') as f:
		f.write(file.content)
	try:
		path = os.path.abspath("video.mp4")
		text = get_text(path)
		print (text)
		bot.send_message(message.chat.id, str(text))
	except Exception as err:
		bot.send_message(message.chat.id, err)

print('Bot start')

bot.polling(none_stop=True, interval=0)
