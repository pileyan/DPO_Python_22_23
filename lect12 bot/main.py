from helper import token
import telebot
import requests
from bs4 import BeautifulSoup
import random
import os
import pandas as pd
from time import sleep, localtime

import re

bot = telebot.TeleBot(token)

def get_urls():
    url = 'https://nplus1.ru/'  # сохраняем
    page = requests.get(url)  # загружаем страницу по ссылке
    soup = BeautifulSoup(page.text, 'lxml')
    urls = [link.get('href')
            for link in soup.find_all('a')
            if ('/news' in link.get('href') and not link.get('href').startswith('/news/'))]
    return urls

def GetNews(url0):
    """
    Returns a tuple with url0, author, title, final_text
    Parameters:

    url0 is a link to the news (string)
    """
    page0 = requests.get(url0)
    soup0 = BeautifulSoup(page0.text, 'lxml')
    author = soup0.find_all('a', {'class': 'underline'})[0].get_text()
    title = soup0.find_all('h1',
                           {'class': 'text-34 md:text-42 xl:text-52 break-words'})[0]\
        .get_text()\
        .replace('\xa0', ' ')\
        .strip()
    text = [t.text for t in soup0.find_all('div', {'class': 'n1_material text-18'})]
    final_text = ' '.join(text)
    final_text = final_text.replace('\n', ' ')
    final_text = final_text.replace('\xa0', ' ')
    return url0, author, title, final_text

def get_news():

    date = localtime()
    file_name = '-'.join([str(date.tm_year), str(date.tm_mon), str(date.tm_mday)])+'.csv'
    if file_name in os.listdir():
        df = pd.read_csv(file_name)
        return df
        # ['text'].sample(1).values[0]
    else:
        data_list = get_urls()
        news = []  # это будет список из кортежей, в которых будут храниться данные по каждой новости
        for link in data_list:
            try:
                res = GetNews(link)
                news.append(res)
                sleep(random.random())
            except:
                pass

        df = pd.DataFrame(news)
        df.columns = ['link', 'author', 'header', 'text']
        df.to_csv(file_name, index = False)
        return df
        # ['text'].sample(1).values[0]

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, """Hi there, I'm newsbot. You can use /news command to \
    get fresh news from nplus1""")


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: message.text.strip().lower() == '/news')
def send_news(message):
    # urls = get_urls()
    text = get_news()['text'].sample(1).values[0]
    bot.send_message(message.chat.id, text)

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: re.match(r'\d{4}/\d{2}/\d{2}$',
                                                   message.text.strip().lower()) is not None)
def send_news_by_date(message):
    print('in progress')
    # urls = get_urls()
    df = get_news()
    filtered = df[df.link.apply(lambda x: message.text.strip().lower() in x)]
    if len(filtered) == 0:
        bot.send_message(message.chat.id, 'Sorry, no news for this date')
    else:
        bot.send_message(message.chat.id, filtered['text'].sample(1).values[0])

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: message.text.strip().lower() not in
                                          ('/news', '/help', '/start') and
                                          re.match(r'\d{4}/\d{2}/\d{2}$',
                                                   message.text.strip().lower()) is None
                     )
def dont_understand(message):
    bot.send_message(message.chat.id,
                     'Sorry, I don\'t understand. Please use proper commands like /start, /news or /help')

bot.infinity_polling()
