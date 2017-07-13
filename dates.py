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


import config
from datetime import date, datetime


def _get_up_week_check():
    start_week = date(config.start_year,
                      config.start_month,
                      config.start_day)

    start_week_number = datetime.isocalendar(start_week)[1]
    if start_week_number % 2 == 0:
        up_week_check = 0
    else:
        up_week_check = 1
    return up_week_check


def get_current_week_type():
    today = date.today()
    up_week_check = _get_up_week_check()
    current_week_number = datetime.isocalendar(today)[1]
    if current_week_number % 2 == 0 and up_week_check == 0:
        week_type = 0
    else:
        week_type = 1

    return week_type


def get_next_week_type():
    return (get_current_week_type()+1) % 2


def get_today_week_day():
    today = date.today()
    week_day_number = datetime.weekday(today)
    return _week_day_name(week_day_number)


def get_tomorrow_week_day():
    today = date.today()
    week_day_number = datetime.weekday(today)
    if week_day_number == 6:
        week_day_number = 0
    else:
        week_day_number += 1
    return _week_day_name(week_day_number)


def time_diff(comp_time):
    current_time = datetime.now().strftime('%H:%M')
    current_time = current_time.split(':')
    comp_time = comp_time.split(':')
    for i in range(2):
        current_time[i] = int(current_time[i])
        comp_time[i] = int(comp_time[i])
    current_time = datetime(2000, 1, 1, current_time[0], current_time[1])
    comp_time = datetime(2000, 1, 1, comp_time[0], comp_time[1])
    return str(comp_time - current_time)


def date_diff(date):
    today = datetime.today()
    current_year = datetime.today().year
    date = datetime(current_year, int(date[3:]), int(date[:2]))
    return str(date - today)


# TODO refact, don't like function name
def session_diff():
    today = datetime.today()
    current_year = datetime.today().year
    current_month = datetime.today().month
    if 7 > current_month > 1:
        session_date_list = config.summer_session_date
        session_date = datetime(current_year, session_date_list[1],
                                session_date_list[0])
    else:
        session_date_list = config.winter_session_date
        session_date = datetime(current_year + 1, session_date_list[1],
                                session_date_list[0])
    return str(session_date - today)


def _week_day_name(week_day):
    week = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
    return week[week_day]


def get_next_week_day(week_day):
    week = {'Пн': 0, 'Вт': 1, 'Ср': 2, 'Чт': 3, 'Пт': 4, 'Сб': 5, 'Вс': 6}
    if week[week_day] == 6:
        return 'Пн'
    else:
        return _week_day_name(week[week_day] + 1)


def day_full_name(week_day):
    week = {'Пн': 'Понедельник',
            'Вт': 'Вторник',
            'Ср': 'Среда',
            'Чт': 'Четверг',
            'Пт': 'Пятница',
            'Сб': 'Суббота',
            'Вс': 'Воскресенье'}
    return week[week_day]
