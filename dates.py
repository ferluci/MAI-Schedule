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


from datetime import date, datetime
import config


def _get_up_week_check():
    '''Возвращает 0, если верхняя неделя четная, иначе 1'''
    start_week = date(config.START_YEAR,
                      config.START_MONTH,
                      config.START_DAY)

    start_week_number = datetime.isocalendar(start_week)[1]
    if start_week_number % 2 == 0:
        up_week_check = 0
    else:
        up_week_check = 1
    return up_week_check


def get_current_week_type():
    '''Возвращает текущий тип недели.'''
    today = date.today()
    up_week_check = _get_up_week_check()
    current_week_number = datetime.isocalendar(today)[1]
    if current_week_number % 2 == 0 and up_week_check == 0:
        week_type = 0
    else:
        week_type = 1

    return week_type


def get_next_week_type():
    '''Возвращает тип следующей недели.'''
    return (get_current_week_type()+1) % 2


def get_today_week_day():
    '''Возвращает текущий день недели.'''
    today = date.today()
    week_day_number = datetime.weekday(today)
    return _week_day_name(week_day_number)


def get_tomorrow_week_day():
    '''Возвращает завтрашний день недели.'''
    today = date.today()
    week_day_number = datetime.weekday(today)
    if week_day_number == 6:
        week_day_number = 0
    else:
        week_day_number += 1
    return _week_day_name(week_day_number)


def time_diff(comp_time):
    '''Возвращает разницу между текущим и сравниваемым днем недели.

    Если разница < 0, то возвращает None.

    '''
    current_time = datetime.now().strftime('%H:%M')
    current_time = current_time.split(':')
    comp_time = comp_time.split(':')
    for i in range(2):
        current_time[i] = int(current_time[i])
        comp_time[i] = int(comp_time[i])
    # Для сравнения времени берется первое число, первого месяца 2000-го года,
    # после чего находится разница.
    current_time = datetime(2000, 1, 1, current_time[0], current_time[1])
    comp_time = datetime(2000, 1, 1, comp_time[0], comp_time[1])
    if str(comp_time - current_time)[0] == '-':
        return None
    else:
        return str(comp_time - current_time)


def date_diff(date):
    '''Возвращает разницу между сравниваемой и текущей датой.

    Если разница отрицаетльная, то возвращается None.

    '''
    today = datetime.today()
    current_year = datetime.today().year
    date = datetime(current_year, int(date[3:]), int(date[:2]))
    if str(date - today)[0] == '-':
        return None
    else:
        return str(date - today)


def time_left_before_session():
    '''Возвращает колличество дней до начала сессии'''
    today = datetime.today()
    current_year = datetime.today().year
    current_month = datetime.today().month
    if 7 > current_month > 1:
        session_date_list = config.SUMMER_SESSION_DATE
        session_date = datetime(current_year, session_date_list[0],
                                session_date_list[1])
    else:
        session_date_list = config.WINTER_SESSION_DATE
        session_date = datetime(current_year + 1, session_date_list[0],
                                session_date_list[1])
    return (session_date - today).days


def holiday_check():
    '''Возвращает True, если текущий месяц - месяц каникул.'''
    current_month = datetime.today().month
    januarry, june, july, august = 1, 6, 7, 8
    return current_month in [januarry, june, july, august]


def get_next_week_day(week_day):
    '''Возвращает следующий день недели.'''
    week = {'Пн': 0, 'Вт': 1, 'Ср': 2, 'Чт': 3, 'Пт': 4, 'Сб': 5, 'Вс': 6}
    if week[week_day] == 6:
        return 'Пн'
    else:
        return _week_day_name(week[week_day] + 1)


def _week_day_name(week_day):
    week = {0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс'}
    return week[week_day]


def day_full_name(week_day):
    week = {'Пн': 'Понедельник',
            'Вт': 'Вторник',
            'Ср': 'Среда',
            'Чт': 'Четверг',
            'Пт': 'Пятница',
            'Сб': 'Суббота',
            'Вс': 'Воскресенье'}
    return week[week_day]


def week_day_check(week_day):
    week = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    return week_day in week
