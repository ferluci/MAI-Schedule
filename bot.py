# -*- coding: utf8 -*-

# Copyright (c) 2017 Anischenko Konstantin Maximovich

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Главный исполняемый файл.
Для работы необходимо создать файл secret_settings.py в той же
директории, в которой находится данный файл. В secret_settings.py
необходимо добавить 2 строчки
TOKEN = Ваш токен
DB_NAME = имя вашей базы данных, например bot.sqlite3

Описание модулей;
из db_manage используется класс Database для работы с бд
из dates используются функции для работы с датой и временем

"""

import re
import telebot
import db_manage
import config
import dates
import secret_settings

bot = telebot.TeleBot(secret_settings.TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    """Стартовое окно.

    Производится проверка наличия id пользователя в базе данных.
    Если он отсутствует, то в бд создается строка с его именем, после чего
    вызывается функция change_group_start(), отвечающая за ввод группы
    пользователя.

    Если же пользователь существует, но нет группы, то также вызывается
    функция change_group_start().

    Иначе, выводится сообщение о том, что пользователь уже зарегестрирован.

    """
    check = db.check_id(message.chat.id)

    if check is None:
        db.insert_user(message.chat.id, message.chat.username)
        group = None
    else:
        group = db.get_group(message.chat.id)

    if group is None:
        change_group_start(message)
        return
    else:
        bot.send_message(message.chat.id, config.already_registered)
        help(message)
        return


@bot.message_handler(func=lambda message: message.text == 'Назад')
def help_redirect(message):
    """Функция, вызывающая функцию главного меню."""
    help(message)
    return


@bot.message_handler(commands=['help'])
def help(message):
    """Функция главного меню."""
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Следующая пара', 'Следующая лабораторная')
    markup.row('Расписание занятий', 'Сессия')
    markup.row('Настройки', 'О нас')
    bot.send_message(message.chat.id,
                     'Что ты хочешь узнать?', reply_markup=markup)


def schedule_prettify(schedule):
    """ Красивый вывод расписания.

    Принимает на вход лист с занятиями, после чего
    с помощью регулярных выражений, либо заведомо зная
    позиции отдельных элементов, упорядочивает их и
    оформляет, возвращая лист с занятиями.

    """
    if not schedule:
        return 'Сегодня занятий нету'
    else:
        bot_message = ''
        location = '📍 ' + schedule[-1] + '\n'
        if 'Кафедра' in schedule[-2]:
            teacher = ''
        elif schedule[-2] != '':
            teacher = '👤 ' + schedule[-2] + '\n'
        else:
            teacher = ''
        subject = '📝 ' + schedule[-3] + '\n'

        for elem in schedule:

            if re.match(r'\d{2}:\d{2}', elem):
                time = '⌚ ' + elem + '\n'
            else:
                time = ''

            if re.match(r'\d{2}[.]\d{2}', elem):
                date = elem
                if len(date) > 5:
                    week_day = date[5:]
                    date = date[:5] + ' '
                    bot_message += '=== ' + date +\
                                   dates.day_full_name(week_day) +\
                                   ' ===' + '\n'
        bot_message += teacher + subject + time + location + '\n'
        return bot_message


@bot.message_handler(func=lambda message:
                     message.text == 'Следующая пара')
def get_next_lesson(message):
    """Функция отвечающая за вывод следующего занятия.

    Проверяет на каждое занятие из сегодняшнего дня, началось ли оно,
    если занятие не началось, то оно выводится пользователю.

    Если сегодня все занятия закончились, то выполняется проверка занятий на
    ближайшие 2 недели.  Пользователю будет выведено первое встреченное
    занятие.

    Если не будет найдено занятий, то пользователь получит об этом сообщение.
    """

    if dates.holiday_check():
        bot.send_message(message.chat.id, config.holiday)
        return

    week_type = dates.get_current_week_type()
    week_day = dates.get_today_week_day()
    group = db.get_group(message.chat.id)
    schedule = db.get_day_schedule(group, week_type, week_day)

    for lesson in schedule:
        lesson_time = lesson[1][:5]
        if dates.time_diff(lesson_time) is not None:
            chat_message = '=== ' + dates.day_full_name(week_day) +\
                               ' ===' + '\n'
            chat_message += schedule_prettify(lesson)
            bot.send_message(message.chat.id, chat_message)
            return

    TWO_WEEKS = 14
    for i in range(TWO_WEEKS):
        week_day = dates.get_next_week_day(week_day)
        # Если сегодня воскресенье, то при переходе на
        # понедельник, изменится тип недели.
        if week_day == 'Пн':
            week_type = dates.get_next_week_type()
        schedule = db.get_day_schedule(group, week_type, week_day)
        # Если в этот день есть занятия,
        # то выводит первое занятие из расписания.
        if schedule:
            chat_message = '=== ' + dates.day_full_name(week_day) +\
                               ' ===' + '\n'
            chat_message += schedule_prettify(schedule[0])
            bot.send_message(message.chat.id, chat_message)
            return
    bot.send_message(message.chat.id, config.day_schedule_empty)


@bot.message_handler(func=lambda message:
                     message.text == 'Следующая лабораторная')
def get_next_laboratory(message):
    """Функция отвечающая за вывод следующей лабораторной.

    Проверяет на каждое занятие из сегодняшнего дня, началось ли оно и
    ялвяется ли лабораторной, если не началось и лабораторная, то
    оно выводится пользователю. Если нет, то производится переход
    к проверке следующего занятия.

    Если сегодня все занятия закончились, то производится аналогичная проверка
    на следующие 2 недели. Если лабораторные не будут найдены, то пользователь
    получит об этом сообщение.

    """
    if dates.holiday_check():
        bot.send_message(message.chat.id, config.holiday)
        return

    week_type = dates.get_current_week_type()
    week_day = dates.get_today_week_day()
    group = db.get_group(message.chat.id)
    schedule = db.get_day_schedule(group, week_type, week_day)
    for lesson in schedule:
        lesson_time = lesson[1][:5]
        if lesson[2] == 'ЛР' and dates.time_diff(lesson_time) is not None:
                chat_message = '=== ' + dates.day_full_name(week_day) +\
                               ' ===' + '\n'
                chat_message += schedule_prettify(lesson)
                bot.send_message(message.chat.id, chat_message)
                return

    # Если в сегодняшнем дне на найдена лабораторная, то переходим к поиску
    # по всем последующим дням.
    TWO_WEEKS = 14
    for i in range(TWO_WEEKS):
        week_day = dates.get_next_week_day(week_day)
        if week_day == 'Пн':
            week_type = dates.get_next_week_type()
        schedule = db.get_day_schedule(group, week_type, week_day)
        for lesson in schedule:
            if lesson[2] == 'ЛР':
                chat_message = '=== ' + dates.day_full_name(week_day) +\
                               ' ===' + '\n'
                chat_message += schedule_prettify(lesson)
                bot.send_message(message.chat.id, chat_message)
                return
    bot.send_message(message.chat.id, config.laboratory_empty)


@bot.message_handler(func=lambda message:
                     message.text == 'Расписание занятий')
def get_schedule(message):
    """Функция отвечающая, за меню расписания."""
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('На сегодня', 'На завтра')
    markup.row('На эту неделю', 'На следующую неделю')
    markup.row('Назад')
    bot.send_message(message.chat.id,
                     'Что конкретно тебя интересует?', reply_markup=markup)


@bot.message_handler(func=lambda message:
                     message.text == 'На сегодня')
def get_today_schedule(message):
    """Вывод расписания на сегодня.

    Если сегодня занятий нету, выводится соответствующее сообщение.
    Иначе, выводится расписание на сегодня.

    """
    if dates.holiday_check():
        bot.send_message(message.chat.id, config.holiday)
        return
    week_type = dates.get_current_week_type()
    week_day = dates.get_today_week_day()
    group = db.get_group(message.chat.id)
    schedule = db.get_day_schedule(group, week_type, week_day)
    if not schedule:
        bot.send_message(message.chat.id, 'Сегодня занятий нет')
    else:
        chat_message = '=== ' + dates.day_full_name(week_day) + ' ===' + '\n'
        for lesson in schedule:
            chat_message += schedule_prettify(lesson)
        bot.send_message(message.chat.id, chat_message)


@bot.message_handler(func=lambda message:
                     message.text == 'На завтра')
def get_tomorrow_schedule(message):
    """Вывод расписания на завтра.

    Если завтра занятий нету, выводится соответствующее сообщение.
    Иначе, выводится расписание на завтра.

    """
    if dates.holiday_check():
        bot.send_message(message.chat.id, config.holiday)
        return
    week_day = dates.get_tomorrow_week_day()
    if week_day == 'Пн':
        week_type = dates.get_next_week_type()
    else:
        week_type = dates.get_current_week_type()
    group = db.get_group(message.chat.id)
    schedule = db.get_day_schedule(group, week_type, week_day)
    if not schedule:
        bot.send_message(message.chat.id, 'Завтра занятий нет')
    else:
        chat_message = '=== ' + dates.day_full_name(week_day) + ' ===' + '\n'
        for lesson in schedule:
            chat_message += schedule_prettify(lesson)
        bot.send_message(message.chat.id, chat_message)


@bot.message_handler(func=lambda message:
                     message.text == 'На эту неделю')
def get_current_week_schedule(message):
    """Вывод расписания на эту неделю.

    Если на этой неделе занятий нету, выводится соответствующее сообщение.
    Иначе, выводится расписание на эту неделю.

    """
    if dates.holiday_check():
        bot.send_message(message.chat.id, config.holiday)
        return
    week_type = dates.get_current_week_type()
    group = db.get_group(message.chat.id)
    schedule = db.get_week_schedule(group, week_type)
    if not schedule:
        bot.send_message(message.chat.id, config.week_schedule_empty)
    else:
        current_week_day = 'Пн'
        chat_message = '=== ' + current_week_day + ' ===' + '\n'
        for lesson in schedule:
            if lesson[0] != current_week_day:
                current_week_day = lesson[0]
                chat_message += '=== ' + current_week_day + ' ===' + '\n'
            chat_message += schedule_prettify(lesson)
        bot.send_message(message.chat.id, chat_message)


@bot.message_handler(func=lambda message:
                     message.text == 'На следующую неделю')
def get_next_week_schedule(message):
    """Вывод расписания на следующую неделю.

    Если на следующей неделе занятий нету, выводится соответствующее сообщение.
    Иначе, выводится расписание на следующую неделю.

    """
    if dates.holiday_check():
        bot.send_message(message.chat.id, config.holiday)
        return
    week_type = dates.get_next_week_type()
    group = db.get_group(message.chat.id)
    schedule = db.get_week_schedule(group, week_type)
    if not schedule:
        bot.send_message(message.chat.id, config.week_schedule_empty)
    else:
        current_week_day = 'Пн'
        chat_message = '=== ' + current_week_day + ' ===' + '\n'
        for lesson in schedule:
            if lesson[0] != current_week_day:
                current_week_day = lesson[0]
                chat_message += '=== ' + current_week_day + ' ===' + '\n'
            chat_message += schedule_prettify(lesson)
        bot.send_message(message.chat.id, chat_message)


@bot.message_handler(func=lambda message:
                     message.text == 'Сессия')
def session(message):
    """Функция отвечающая за меню сессии."""
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('Сколько дней до сессии?', 'Ближайший экзамен')
    markup.row('Расписание сессии', 'Напомни про экзамен')
    markup.row('Назад')
    bot.send_message(message.chat.id,
                     'Что конкретно тебя интересует?', reply_markup=markup)


@bot.message_handler(func=lambda message:
                     message.text == 'Сколько дней до сессии?')
def remaining_days(message):
    """Вывод информации о колличестве дней до сессии"""
    chat_message = 'До сессии осталось {} дней'.format(
        dates.time_left_before_session())
    bot.send_message(message.chat.id, chat_message)


@bot.message_handler(func=lambda message: message.text == 'Ближайший экзамен')
def get_nearest_exam(message):
    """Вывод информации о ближайшем экзамене.

    Проверятеся дата каждого экзамена. Если он прошел
    (определяется с помощью функции dates.date_diff()),
    то производится переход к следующему.
    Если был найден экзамен, подходящий под условие, то выводится.
    Иначе, выводится информация о том, что сессия закончилась.

    """
    group = db.get_group(message.chat.id)
    session_schedule = db.get_session(group)
    if session_schedule is None:
        bot.send_message(message.chat.id, config.session_empty)
        return
    for exam in session_schedule:
        exam_date = exam[0][:5]
        if dates.date_diff(exam_date) is not None:
            bot.send_message(message.chat.id, schedule_prettify(exam))
            return
    bot.send_message(message.chat.id, 'Кажется, сессия закончилась')


@bot.message_handler(func=lambda message: message.text == 'Расписание сессии')
def get_exam_schedule(message):
    """Вывод всех экзаменов.

    Если список экзаменов пуст, то выводится информация об этом.

    """
    group = db.get_group(message.chat.id)
    session_schedule = db.get_session(group)
    if session_schedule is None:
        bot.send_message(message.chat.id, config.session_empty)
        return
    for exam in session_schedule:
        bot.send_message(message.chat.id, schedule_prettify(exam))


@bot.message_handler(func=lambda message:
                     message.text == 'Напомни про экзамен')
def exam_remind(message):
    bot.send_message(message.chat.id, 'В разработке')


@bot.message_handler(func=lambda message: message.text == 'Настройки')
def settings_redirect(message):
    """Вызов меню настроек."""
    settings(message)
    return


@bot.message_handler(commands=['settings'])
def settings(message):
    """Меню настроек"""
    markup = telebot.types.ReplyKeyboardMarkup()
    markup.row('📝 Изменить группу')
    markup.row('📟 Редактировать оповещения')
    markup.row('❌ Сбросить настройки')
    markup.row('Назад')
    bot.send_message(message.chat.id, 'Меню настроек', reply_markup=markup)


@bot.message_handler(func=lambda message:
                     message.text == '📝 Изменить группу')
def change_group_start(message):
    """Функция изменения группы.

    При нажатии на кнопку "📝 Изменить группу", пользователь
    получит текущую группу (если есть).
    После чего пользователь должен осуществить ввод номера группы или
    нажать кнопку назад.

    """
    group = db.get_group(message.chat.id)
    if group is not None:
        bot.send_message(message.chat.id, 'Ваша текущая группа: ' + group)
    message = bot.send_message(message.chat.id, config.get_group)
    # Регистрация следующего handler'a. Т.е. все сообщения пользователя
    # будут обрабатываться функцией change_group_post
    bot.register_next_step_handler(message, change_group_end)


def change_group_end(message):
    """ Ввод группы.

    Формируется список возможных групп, после чего производится проверка
    для каждой группы из списка, на наличие данной группы в списке групп.
    Если она есть, то обновить бд. Иначе перейти к следующей группе.

    Если ни одной группы нет в списке, то вывести пользователю сообщение
    о том, что он ошибся при вводе.

    """
    try:
        group = message.text.upper()
        groups_list = [group]

        if message.text == 'Назад':
            help(message)
            return

        # Многие вводят вместо О - 0
        # Данный цикл генерирует различные комбинации имени группы,
        # где заместо нуля ставится буква О
        for i in range(group.count('0')):
            group = groups_list[-1][:groups_list[-1].index('0')] + 'О' +\
                              groups_list[-1][groups_list[-1].index('0') + 1:]
            groups_list.append(group)

        def _strings_correction(strings_list, pattern, correct_pattern):
            """Замена строки - pattern на строку - correct_pattern."""
            pattern = re.compile(pattern)
            for i in range(len(strings_list)):
                strings_list[i] = pattern.sub(correct_pattern, strings_list[i])
            return list

        # Сообщение пользователя приводится к верхнему регистру, но
        # если у некоторых групп ряд символов в нижнем регистре, поэтому,
        # необходимо их изменить.
        for key in config.EXCEPT_SYMBS:
            if key in group:
                groups_list = _strings_correction(groups_list, key, config.EXCEPT_SYMBS[key])

        for group in groups_list:
            if group in db.groups:
                db.update_group(message.chat.id, group)
                bot.send_message(message.chat.id, config.completed)
                help(message)
                return

        bot.send_message(message.chat.id, 'Вы где-то ошиблись, попробуйте еще раз')
        bot.register_next_step_handler(message, change_group_end())
        return
    except Exception:
        bot.send_message(message.chat.id, config.something_going_wrong)


@bot.message_handler(func=lambda message:
                     message.text == '📟 Редактировать оповещения')
def edit_alerts(message):
    bot.send_message(message.chat.id, 'В разработке')


@bot.message_handler(func=lambda message:
                     message.text == '❌ Сбросить настройки')
def drop_settings(message):
    """Сброс настроек."""
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
    db = db_manage.Database(secret_settings.DB_NAME)
    bot.polling(none_stop=True)
