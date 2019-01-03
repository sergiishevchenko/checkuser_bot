#!/usr/bin/env python

# SQLITE BRANCH
import sys
import sqlite3
from telebot import types


def loadDB():
    # Creates SQLite database to store info.
    conn = sqlite3.connect('content.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    cur.executescript('''CREATE TABLE IF NOT EXISTS userdata
    (
    id INTEGER NOT NULL PRIMARY KEY UNIQUE, 
    firstname TEXT,
    Surname TEXT,
    Age TEXT,
    Address TEXT,
    Job TEXT);''')
    conn.commit()
    conn.close()


def checkUser(update, user_data):
    conn = sqlite3.connect('content.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    if len(cur.execute('''SELECT id FROM userdata WHERE id = ?        
            ''', (update.message.from_user.id,)).fetchall()) > 0:
        c = cur.execute('''SELECT Surname FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Surname'] = c[0]
        c = cur.execute('''SELECT Age FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Age'] = c[0]
        c = cur.execute('''SELECT Address FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Address'] = c[0]
        c = cur.execute('''SELECT Job FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['Job'] = c[0]
        print('Past user')
    else:
        cur.execute('''INSERT OR IGNORE INTO userdata (id, firstname) VALUES (?, ?)''', \
                    (update.message.from_user.id, update.message.from_user.first_name,))
        print('New user')
    conn.commit()
    conn.close()


def updateUser(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('content.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE userdata SET {} = ? WHERE id = ?'''.format(category), \
                (text, update.message.from_user.id,))
    conn.commit()
    conn.close()


# Python Telegram Bot Branch

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler, InlineQueryHandler, CallbackQueryHandler)

import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

NAMEOFUSER, CONFIRMATION, USERINFO, USERLINKS, WHOAREYOU, CHECK, DONE = range(7)


def facts_to_str(user_data):
    facts = list()

    for key, value in user_data.items():
        facts.append('{} - {}'.format(key, value))

    return "\n".join(facts).join(['\n', '\n'])


def start(bot, update, user_data):
    reply_keyboard = [['Добавить отзыв', 'Проверить пользователя']]

    update.message.reply_text(
        "Добавить отзыв можно написав боту напрямую, для этого нажмите кнопку 'Добавить отзыв'. "
        "Проверить пользователя можно нажав на кнопку 'Проверить позьзователя'",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return NAMEOFUSER


def check(bot, update, user_data):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"ыыыыы"
    )
    return ConversationHandler.END


def nameofuser(self, update):
    reply_keyboard = [['Далее']]
    update.message.reply_text(
        "Давайте добавим нового айтишника в Черный Список. "
        u"Я буду задавать вопросы, вы же на них отвечаете просто в чат и жмете кнопку “Далее”. "
        u"Для начала напишите имя и фамилию айтишника.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return CONFIRMATION


def confirmation(bot, update):
    reply_keyboard = [['Далее']]
    update.message.reply_text(
        u"Вы можете вводить информацию в любом удобном вам виде, даже на нескольких строчках. "
        u"Например на разных языках, либо если человек указывал свое имя немного иначе в разных компаниях. "
        u"Но чтобы мы поняли, что вы закончили ввод имени, нажмите кнопку Далее",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return USERINFO


def user_info(bot, update):
    reply_keyboard = [['Далее']]
    update.message.reply_text(
        "Опишите в произвольной форме что не так с этим айтишником? "
        u"Почему бы вы не рекомендовали брать его на работу? Воровал? Пропал перед релизом? "
        u"Пишите сколько хотите, потом жмите “Далее”.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return USERLINKS


def user_links(bot, update):
    reply_keyboard = [['Далее']]
    update.message.reply_text(
        "Если есть возможность пришлите одну-две (чем больше тем лучше) ссылки на какие-то соцсети айтишника, "
        u"где видно его фото. Можете просто прислать ссылку на фото.",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return WHOAREYOU


def who_are_you(bot, update, user_data):
    query = update.callback_query
    keyboard = [
        [InlineKeyboardButton(u"Коллега (тех. спец.)", callback_data=str(DONE))],
        [InlineKeyboardButton(u"Менеджер, рекрутер (не тех. спец.)", callback_data=str(DONE))]

    ]
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Выберите от чьего лица оставлен отзыв. "
             u"Если вы работали вместе с айтишником в одной команде на одном уровне и являетесь незаинтересованной "
             u"стороной (то есть не несли прямой ответственности либо убытков из-за него),"
             u" то нажмите кнопку “Коллега (тех. спец.)”. В любом другом случае, если отзыв оставляется "
             u"от лица рекрутера, менеджера, топ-менеджмента и прочих ролей, которые не могут оценить технический уровень, "
             u"а делают выводы на основании результатов, то нажмите “Менеджер, рекрутер (не тех. спец.)”. "
             u"Можете также написать в чат, если оба варианта не подходят."
    )
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot.edit_message_reply_markup(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        reply_markup=reply_markup
    )
    return DONE


def done(bot, update):
    query = update.callback_query
    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=u"Спасибо! Вам небольшой плюсик в карму и +10 очков. Что с этими очками делать, мы позже придумаем."
    )
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("your_token")
    print("Connection to Telegram established; starting bot.")
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start, pass_user_data=True)],

        states={

            NAMEOFUSER: [RegexHandler('^(Добавить отзыв|Проверить пользователя)$', nameofuser)],

            CONFIRMATION: [MessageHandler(Filters.text, confirmation)],

            USERINFO: [MessageHandler(Filters.text, user_info)],

            USERLINKS: [MessageHandler(Filters.text, user_links)],

            WHOAREYOU: [CallbackQueryHandler(who_are_you)],

            CHECK: [MessageHandler(Filters.text, check)],

            DONE: [MessageHandler(Filters.text, done)],

        },

        fallbacks=[CommandHandler('start', start, pass_user_data=True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    loadDB()
    main()
