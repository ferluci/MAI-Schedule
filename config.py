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


token = '320017070:AAGgaB6LwkXssOPIXV_f9oAh3eSP7-UcX8o'

'''
Дата понедельника, первой учебной недели
Даже если учебная неделя начинается с четверга,
Все равно указать дату понедельника
В формате:
Год
Месяц
День
'''
start_year = 2017
start_month = 2
start_day = 6

# TODO bad names
winter_session_date = [9, 1]
summer_session_date = [8, 6]

get_group = '''
Напиши мне свою группу. Полностью. Со всеми цифрами и буквами.\n
Примеры: М1О-101Б-16, 3О-202М-15, 2РКК-3ДБ-292
'''

already_registered = '''
Ты уже зарегестрирован в системе.
Для работы напиши /help
'''

contacts = '''
Создатель - @vakakvaka\nРепозиторий проекта на git\'е -
https://github.com/Ferluci/schedulemai
'''

completed = 'Успешно!'
