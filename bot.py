# -*- coding: utf8 -*-


'''
Copyright (c) 2017 Anischenko Konstantin Maximovich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


import dates
import config
import telebot
import db_manage


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start'])
def start(message):
    check = db.check_id(message.chat.id)

    if check is None:
        db.insert_user(message.chat.id, message.chat.username)
        group = None
    else:
        group = db.get_group(message.chat.id)

    if group is None:
        change_group_pre(message)
        return
    else:
        bot.send_message(message.chat.id, config.already_registered)
        help(message)
        return


@bot.message_handler(func=lambda message: message.text == 'Назад')
def help_redirect(message):
    help(message)
    return


@bot.message_handler(commands=['help'])
def help(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Следующая пара?', 'Следующая лабораторная?')
    markup.row('Расписание занятий', 'Сессия')
    markup.row('Настройки', 'О нас')
    bot.send_message(message.chat.id,
                     'Что ты хочешь узнать?', reply_markup=markup)


def send_scheldule(message, scheldule):
    if scheldule == []:
        bot.send_message(message.chat.id, 'Сегодня занятий нету')
    else:
        bot_message = ''
        for item in scheldule:
            bot_message += (item + '\n')
        bot.send_message(message.chat.id, bot_message)


@bot.message_handler(func=lambda message:
                     message.text == 'Следующая пара?')
def next_less(message):
    week_type = dates.get_current_week_type()
    week_day = dates.get_today_week_day()
    group = db.get_group(message.chat.id)
    scheldule = db.get_day_scheldule(group, week_type, week_day)
    for lesson in scheldule:
        lesson_time = lesson[0][:5]
        if dates.time_diff(lesson_time) is not None:
            send_scheldule(message, lesson)
            return

    week_day = dates.get_next_week_day(week_day)
    if week_day == 'Пн':
        week_type = dates.get_next_week_type()
    scheldule = db.get_day_scheldule(group, week_type, week_day)
    send_scheldule(message, scheldule[0])


@bot.message_handler(func=lambda message:
                     message.text == 'Следующая лабораторная?')
def next_lab(message):
    week_type = dates.get_current_week_type()
    week_day = dates.get_today_week_day()
    group = db.get_group(message.chat.id)
    scheldule = db.get_day_scheldule(group, week_type, week_day)
    for lesson in scheldule:
        lesson_time = lesson[0][:5]
        if lesson[1] == 'ЛР' and dates.time_diff(lesson_time) is not None:
                send_scheldule(message, lesson)
                return

    # Если в сегодняшнем дне на найдена лабораторная, то переходим к поиску
    # По всем последующим дням
    while True:
        week_day = dates.get_next_week_day(week_day)
        if week_day == 'Пн':
            week_type = dates.get_next_week_type()
        scheldule = db.get_day_scheldule(group, week_type, week_day)
        for lesson in scheldule:
            if lesson[1] == 'ЛР':
                send_scheldule(message, lesson)
                return


@bot.message_handler(func=lambda message:
                     message.text == 'Расписание занятий')
def get_schedule(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('На сегодня', 'На завтра')
    markup.row('На эту неделю', 'На следующую неделю')
    markup.row('Назад')
    bot.send_message(message.chat.id,
                     'Что конкретно тебя интересует?', reply_markup=markup)


@bot.message_handler(func=lambda message:
                     message.text == 'На сегодня')
def today_scheldule(message):
    week_type = dates.get_current_week_type()
    week_day = dates.get_today_week_day()
    group = db.get_group(message.chat.id)
    scheldule = db.get_day_scheldule(group, week_type, week_day)
    if scheldule == []:
        bot.send_message(message.chat.id, 'Сегодня занятий нет')
    else:
        for lesson in scheldule:
            send_scheldule(message, lesson)


@bot.message_handler(func=lambda message:
                     message.text == 'На завтра')
def tomorrow_scheldule(message):
    week_day = dates.get_tomorrow_week_day()
    if week_day == 'Пн':
        week_type = dates.get_next_week_type()
    else:
        week_type = dates.get_current_week_type()
    group = db.get_group(message.chat.id)
    scheldule = db.get_day_scheldule(group, week_type, week_day)
    if scheldule == []:
        bot.send_message(message.chat.id, 'Сегодня занятий нет')
    else:
        for lesson in scheldule:
            send_scheldule(message, lesson)


@bot.message_handler(func=lambda message:
                     message.text == 'На эту неделю')
def current_week_scheldule(message):
    week_type = dates.get_current_week_type()
    group = db.get_group(message.chat.id)
    scheldule = db.get_week_scheldule(group, week_type)
    for lesson in scheldule:
        send_scheldule(message, lesson)


@bot.message_handler(func=lambda message:
                     message.text == 'На следующую неделю')
def next_week_scheldule(message):
    week_type = dates.get_next_week_type()
    group = db.get_group(message.chat.id)
    scheldule = db.get_week_scheldule(group, week_type)
    for lesson in scheldule:
        send_scheldule(message, lesson)


def session_check(session_scheldule):
    if session_scheldule == [] or session_scheldule is None:
        pass


@bot.message_handler(func=lambda message:
                     message.text == 'Сессия')
def session(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Сколько дней до сессии?', 'Ближайший экзамен')
    markup.row('Расписание сессии', 'Напомни про экзамен')
    markup.row('Назад')
    bot.send_message(message.chat.id,
                     'Что конкретно тебя интересует?', reply_markup=markup)


@bot.message_handler(func=lambda message:
                     message.text == 'Сколько дней до сессии?')
def remaining_days(message):
    bot.send_message(message.chat.id, dates.time_left_before_session())


@bot.message_handler(func=lambda message: message.text == 'Ближайший экзамен')
def nearest_exam(message):
    group = db.get_group(message.chat.id)
    session_scheldule = db.get_session(group)
    for exam in session_scheldule:
        exam_date = exam[0][:5]
        if dates.date_diff(exam_date) is not None:
            send_scheldule(message, exam)
            return
    bot.send_message(message.chat.id, 'Кажется сессия закончилась')


@bot.message_handler(func=lambda message: message.text == 'Расписание сессии')
def exam_scheldule(message):
    group = db.get_group(message.chat.id)
    session_scheldule = db.get_session(group)
    for exam in session_scheldule:
        send_scheldule(message, exam)


@bot.message_handler(func=lambda message:
                     message.text == 'Напомни про экзамен')
def exam_remind(message):
    bot.send_message(message.chat.id, 'В разработке')


@bot.message_handler(func=lambda message: message.text == 'Настройки')
def settings_redirect(message):
    settings(message)
    return


@bot.message_handler(commands=['settings'])
def settings(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('📝 Изменить группу')
    markup.row('📟 Редактировать оповещения')
    markup.row('❌ Сбросить настройки')
    markup.row('Назад')
    bot.send_message(message.chat.id, 'Меню настроек', reply_markup=markup)


@bot.message_handler(func=lambda message:
                     message.text == '📝 Изменить группу')
def change_group_pre(message):
    message = bot.send_message(message.chat.id, config.get_group)
    bot.register_next_step_handler(message, change_group_post)


def change_group_post(message):
    group = message.text.upper()
    group_var = []
    group_var.append(group)

    if message.text == 'Назад':
        help(message)
        return

    # Многие вводят вместо О - 0
    # Данный цикл генерирует различные комбинации имени группы,
    # где заместо нуля ставится буква О
    for i in range(group.count('0')):
        group = group_var[-1][:group_var[-1].index('0')] + 'О' +\
                          group_var[-1][group_var[-1].index('0') + 1:]
        group_var.append(group)

    for group in group_var:
        if group in db.groups:
            db.update_group(message.chat.id, group)
            bot.send_message(message.chat.id, config.completed)
            help(message)
            return

    bot.send_message(message.chat.id, 'Вы где-то ошиблись')
    bot.register_next_step_handler(message, change_group_post)
    return


@bot.message_handler(func=lambda message:
                     message.text == '📟 Редактировать оповещения')
def edit_alerts(message):
    bot.send_message(message.chat.id, 'В разработке')


@bot.message_handler(func=lambda message:
                     message.text == '❌ Сбросить настройки')
def drop_settings(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('🔥 Да', '🚫 Нет')
    bot.send_message(message.chat.id, 'Вы уверены?', reply_markup=markup)
    bot.register_next_step_handler(message, drop_check)


def drop_check(message):
    if message.text == '🔥 Да':
        db.update_group(message.chat.id, None)
    settings(message)


@bot.message_handler(func=lambda message:
                     message.text == 'О нас')
def about(message):
    bot.send_message(message.chat.id, config.contacts)


if __name__ == '__main__':
    db = db_manage.Database('bot.db')
    bot.polling(none_stop=True)
