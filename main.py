import json
import telebot
from telebot import types
from telegram import ParseMode
import config
from random import randint

bot = telebot.TeleBot(config.TOKEN)


def find_film_genre(message):
    with open('films.json', 'r', encoding='utf-8') as f:
        films = []
        js = json.load(f)

        if message.text == '🌏Все фильмы':
            for film in js:
                films.append(film)
            return films

        else:
            genr = message.text.lower()
            for film in js:
                if genr in js[film]['genre']:
                    films.append(film)
            if len(films) > 1:
                return films
            else:
                return None


def print_films_genre(message, films):
    if films is None:
        bot.send_message(message.chat.id, 'Фильмов по указанному жанру не найдено, '
                                          'проверьте написание или попробуйте другой.')
    with open('films.json', 'r', encoding='utf-8') as f:
        js = json.load(f)

    if len(js) <= len(films):
        text = 'Список всех фильмов:\n\n'

    else:
        text = 'Список фильмов по выбранному жанру:\n\n'

    keyboard = home_keyboard()
    i = 1

    for film in films:
        minidesk = js[film]['desc'].split()
        minidesk = minidesk[0] + ' ' + minidesk[1] + ' ' + minidesk[2] + '...\n'
        lss = f"[{minidesk}]({js[film]['link']})"
        text += '*' + js[film]['name'] + '*' + \
                f"({js[film]['year']}): " + lss + "\n"
        i += 1

    bot.send_message(message.chat.id,
                     text,
                     reply_markup=keyboard,
                     parse_mode=ParseMode.MARKDOWN,
                     disable_web_page_preview=True)


def print_film(message, film):
    with open('films.json', 'r', encoding='utf-8') as f:
        js = json.load(f)
        photo = js[film]['image']
        text = '*' + js[film]['name'] + '*' + ':\n' + js['1']['desc'] + \
               '\n\n*Год выпуска:* ' + js['1']['year']
        keyboard = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Кинопоиск",
                                          url=js[film]['link'])
        keyboard.add(btn1)
        bot.send_photo(message.chat.id,
                       photo,
                       caption=text,
                       reply_markup=keyboard,
                       parse_mode=ParseMode.MARKDOWN)


@bot.message_handler(commands=['start', 'home', 'help'])
def start(message):
    if message.text in ['/start', '/home', '/help']:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['🎲Случайный фильм', '🌏Все фильмы', '🎬По жанрам']])
        bot.send_message(message.chat.id,
                         'Привет, _{}_! Я бот с коллекцией лучших фильмов!\n\n'
                         'Ты можешь воспользоваться кнопками и выбрать:\n\n'
                         '*Случайный фильм* - я присылаю тебе абсолютно случайный фильм, но из лучшей коллекции!\n'
                         '*Все фильмы* - полный список всех фильмов!\n'
                         '*По жанрам* - ты можешь выбрать любой жанр и посмотреть список фильмов с этим жанром!'
                         .format(message.from_user.first_name),
                         reply_markup=keyboard,
                         parse_mode=ParseMode.MARKDOWN)
        bot.register_next_step_handler(message, start_1)

    elif message.text == '🔙Домой':
        home(message)

    else:
        bot.send_message(message.chat.id,
                         'Такого варианта нет, воспользуйся кнопками.')
        bot.register_next_step_handler(message, start)


def start_1(message):
    if message.text == '🎲Случайный фильм':
        with open('films.json', 'r', encoding='utf-8') as f:
            js = json.load(f)
            n = len(js)
            x = randint(1, n)
            print_film(message, str(x))
        bot.register_next_step_handler(message, start_1)

    elif message.text == '🌏Все фильмы':
        print_films_genre(message, find_film_genre(message))
        bot.register_next_step_handler(message, start)

    elif message.text == '🎬По жанрам':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*[types.KeyboardButton(name) for name in
                       ['Драма', 'Комедия', 'Ужасы', '🔙Домой']])
        bot.send_message(message.chat.id,
                         'Напишите любой жанр или выберите популярные с помощью кнопок.',
                         reply_markup=keyboard)
        bot.register_next_step_handler(message, genre)

    else:
        bot.send_message(message.chat.id,
                         'Такого варианта нет, воспользуйся кнопками.')
        bot.register_next_step_handler(message, start_1)


def genre(message):
    if message.text == '🔙Домой':
        home(message)
        return None

    try:
        print_films_genre(message,
                          find_film_genre(message))

    except:
        bot.send_message(message.chat.id,
                         'Что-то не так с жанром, проверьте правильность написания!')
        bot.register_next_step_handler(message, genre)
        return None

    bot.register_next_step_handler(message, start)


def home(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in
                   ['🎲Случайный фильм', '🌏Все фильмы', '🎬По жанрам']])
    bot.send_message(message.chat.id, 'Вы вернулись домой.',
                     reply_markup=keyboard)
    bot.register_next_step_handler(message, start_1)


def home_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    menus = types.KeyboardButton("🔙Домой")
    keyboard.add(menus)
    return keyboard


bot.infinity_polling()
