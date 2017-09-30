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


DEVELOPER_CHAT_ID = 120803423

'''
Дата понедельника, первой учебной недели
Даже если учебная неделя начинается с другого дня недели,
все равно указать дату понедельника.
Дата записывается в формате:
Год
Месяц
День
'''

START_YEAR = 2017
START_MONTH = 9
START_DAY = 4


# Даты сессий хранятся в массивах в формате: месяц, день
WINTER_SESSION_DATE = [1, 9]
SUMMER_SESSION_DATE = [6, 8]


EXCEPT_SYMBS = {'БКИ':'Бки', 'БК':'Бк', 'БкИ':'Бки', 'СКИ':'Ски', 'СЦК':'Сцк',
              'СЦ':'Сц', 'СцК':'Сцк', 'МКИ':'Мки', 'МК':'Мк', 'МкИ':'Мки'}

get_group = '''
Напиши мне свою группу. Полностью. Со всеми цифрами и буквами.\n
Примеры: М1О-101Б-16, 3О-202М-15, 2РКК-3ДБ-292
'''

holiday = '''
Каникулы. Занятий нет.
'''

already_registered = '''
Ты уже зарегестрирован в системе.
Для работы напиши /help
'''

contacts = '''
Создатель - @vakakvaka\nРепозиторий проекта на git\'е -
https://github.com/Ferluci/MAI-Schedule \n
Репозиторий Лямбды:
https://github.com/lambdafrela
'''

session_empty = '''
Судя по всему у вас нет экзаменов,
если это не так, то свяжитесь с разработчиком @vakakvaka
'''

laboratory_empty = '''
Судя по всему у вас нет лабораторных,
если это не так, то свяжитесь с разработчиком @vakakvaka
'''

day_schedule_empty = '''
Кажется у вас нет занятий,
если это не так, то свяжитесь с разработчиком @vakakvaka
'''

week_schedule_empty = '''
Кажется у вас нет занятий,
если это не так, то свяжитесь с разработчиком @vakakvaka
'''

something_going_wrong = '''
Что-то пошло не так
'''

completed = 'Успешно!'
