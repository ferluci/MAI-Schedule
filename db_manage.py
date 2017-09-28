# -*- coding: utf8 -*-

# Copyright (c) 2017 Anischenko Konstantin Maximovich

# Permission is hereby granted, free of CHARge, to any person obtaining a copy
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


import re
from time import sleep
from requests import get
from sqlite3 import connect
from bs4 import BeautifulSoup


class Database:
    """Класс обеспечивающий работу с базой данных."""
    def __init__(self, db_name):
        self.db_name = db_name
        self.tables = self.get_tables()
        if len(self.tables) == 0:
            self.create_users_table()
            self.create_groups_table()
            self.create_schedule_table()
            self.create_session_table()
            print('start')
            self.fill_groups_table()
            print(1)
            self.groups = tuple(self.get_groups())
            self.fill_schedule_table()
            print(2)
            self.fill_session_table()
            print('end')
            self.create_notification_table()
        self.groups = tuple(self.get_groups())

    def get_tables(self):
        """Возвращает список таблиц"""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master " +
                    "WHERE type = 'table';")
        result = cur.fetchall()
        con.close()
        return result

    # Users table api

    def create_users_table(self):
        """Создание таблицы пользователей."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Users(id INTEGER, name CHAR(20), group_name CHAR(20))")
        con.close()

    def insert_user(self, user_id, name, group=None):
        """Вставка пользователя в таблицу."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO Users (id, name, group_name) " +
                    "VALUES (?, ?, ?)",
                    [user_id, name, group])
        con.commit()
        con.close()

    def check_id(self, user_id):
        """Проверка наличия пользователя в таблице по его id."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Users WHERE id=?", [user_id])
        result = cur.fetchone()
        return result

    def get_group(self, user_id):
        """Получение группы пользователя."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT group_name FROM Users WHERE id=?", [user_id])
        group = cur.fetchone()
        if group is not None:
            group = group[0]
        return group

    def update_group(self, user_id, group):
        """Изменение группы пользователя."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute('UPDATE Users SET group_name=? WHERE id=?',
                    [group, user_id])
        con.commit()
        con.close()

    # Groups table api

    def create_groups_table(self):
        """Создание таблицы групп."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Groups(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name CHAR(20))")
        con.commit()
        con.close()

    def fill_groups_table(self):
        """Заполнение таблицы групп."""
        con = connect(self.db_name)
        cur = con.cursor()
        group_list = self._parse_groups()
        for group in group_list:
            cur.execute('INSERT INTO Groups (group_name) VALUES (?)',
                        [group])
        con.commit()
        con.close()

    def _parse_groups(self):
        """Парсинг списка групп с сайта МАИ."""
        target_url = 'https://www.mai.ru/education/schedule'
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        groups = []
        for group in soup.find_all('a', class_="sc-group-item"):
            group = group.get_text()
            groups.append(group)
        return groups

    def get_groups(self):
        """Получить список групп."""
        con = connect(self.db_name)
        cur = con.cursor()
        groups_list = []
        for row in cur.execute("SELECT group_name FROM Groups"):
            groups_list.append(row[0])
        con.close()
        return groups_list

    # Notifiaction table api

    def create_notification_table(self):
        """Создание таблицы уведомлений."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Notification(" +
                    "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT," +
                    "user_id INTEGER," +
                    "note TEXT" +
                    "date CHAR(20))")
        con.close()

    def insert_note(self, user_id, note, date):
        """Добавление уведомления."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO Notification " +
                    "(user_id, note, date)" +
                    "VALUES (?, ?, ?)",
                    [user_id, note, date])
        con.commit()
        con.close()

    def get_notes(self):
        """Получение списка уведомлений."""
        con = connect(self.db_name)
        cur = con.cursor()
        notes_list = []
        for row in cur.execute("SELECT * FROM Notification"):
            notes_list.append(row)
        con.close()
        return notes_list

    def delete_note(self, note_id):
        """Удаление уведомления."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("DELETE FROM Notification WHERE id=?", [note_id])
        con.commit()
        con.close()

    # Session table api
    def create_session_table(self):
        """Создание таблицы расписания сессии."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Session(" +
                    "id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name CHAR(20), " +
                    "date CHAR(8), " +
                    "time CHAR(15), " +
                    "subject CHAR(70), " +
                    "teacher CHAR(70), " +
                    "location CHAR(25))")
        con.commit()
        con.close()

    def fill_session_table(self):
        """Заполнение таблицы расписания сессии."""
        con = connect(self.db_name)
        cur = con.cursor()
        for group in self._parse_examining_groups():
            session = self._parse_session(group)
            for exam in session:
                # Иногда на сайте не указывается имя преподавателя,
                # из-за чего необходимо выполнять данную проверку, дабы
                # не выйти за границы списка.
                if len(exam) == 6:
                    date = exam[0]
                    time = exam[1]
                    subject = exam[3]
                    teacher = exam[4]
                    location = exam[5].replace(u'\xa0', u'')
                    cur.execute("INSERT INTO Session " +
                                "(group_name, date, time," +
                                " subject, teacher, location) " +
                                "VALUES (?, ?, ?, ?, ?, ?)",
                                [group, date, time,
                                 subject, teacher, location])
                else:
                    date = exam[0]
                    time = exam[1]
                    subject = exam[3]
                    location = exam[4].replace(u'\xa0', u'')
                    cur.execute("INSERT INTO Session " +
                                "(group_name, date, time," +
                                " subject, location) " +
                                "VALUES (?, ?, ?, ?, ?)",
                                [group, date, time, subject, location])
                con.commit()

            sleep(0.5)
        con.commit()
        con.close()

    def _parse_examining_groups(self):
        """Парсинг групп, имеющих экзамен."""
        target_url = 'https://www.mai.ru/education/schedule/session'
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        groups = []
        for group in soup.find_all('a', class_="sc-group-item"):
            group = group.get_text()
            groups.append(group)
        return groups

    def _parse_session(self, group_name):
        """Парсинг экзаменов."""
        target_url = "https://www.mai.ru/" +\
                     "education/schedule/session.php?group=" +\
                     group_name
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        exams = []
        for exam in soup.find_all('div', class_="sc-container"):
            exam = exam.get_text().split('\n')
            for i in range(exam.count('')):
                exam.pop(exam.index(''))
            exams.append(exam)
        return exams

    def get_session(self, group):
        """Возвращает все экзамены для данной группы."""
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT date, time, subject, "
                               "teacher, location " +
                               "FROM Session WHERE group_name=?",
                               [group]):
            result.append(list(row))
        con.close()
        if not result:
            return None
        return result

    # Schedule table api

    def create_schedule_table(self):
        """Создание таблицы расписания."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Schedule(" +
                    "id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name CHAR(20), " +
                    "week_type INTEGER, " +
                    "day CHAR(2), " +
                    "time CHAR(15), " +
                    "lesson_type CHAR(5), " +
                    "subject CHAR(70), " +
                    "teacher CHAR(70), " +
                    "location CHAR(25))")
        con.commit()
        con.close()

    def fill_schedule_table(self):
        """Заполнение таблицы расписания."""
        for group in self.groups:
            down_week = self._parse_schedule(group, 4)
            up_week = self._parse_schedule(group, 5)

            self._fill_week(up_week, group, 0)
            self._fill_week(down_week, group, 1)

    def _parse_schedule(self, group_name, week_number):
        """Парсинг расписания."""
        target_url = "http://www.mai.ru/" +\
                     "education/schedule/detail.php?group=" +\
                     group_name + '&week=' + str(week_number)
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        result = []
        for day in soup.find_all('div', class_="sc-container"):
            day = day.get_text().split('\n')
            day = [x for x in day if x != '']
            result.append(day)
        return result

    def _fill_week(self, week, group, week_type):
        """Вставка в таблицу расписания на неделю."""
        for day in week:
            day, date = self._sepate_by_lessons(day)
            for lesson in day:
                if lesson[0] == 'Военная подготовка':
                    subject = 'Военная подготовка'
                    time = lesson[-1]
                    location = lesson[-2].replace(u'\xa0', u'')
                    self._fill_day(group, week_type, date,
                                   time, subject, location)
                    continue

                time = lesson[-1]
                location = lesson[-2].replace(u'\xa0', u'')
                lesson_type = lesson[0]
                subject = lesson[1]
                if len(lesson) == 4:
                    teacher = ''
                else:
                    teacher = lesson[2]
                self._fill_day(group, week_type, date, time,
                               subject, location, lesson_type, teacher)

    def _sepate_by_lessons(self, day):
        """Преобразовывает массив с расписанием.

        Получает на вход массив с расписанием на день с сайта МАИ.
        Преобразует в двумерный массив: [[занятие1], [занятие2]...].

        """
        date = day[0][-2:]
        day.pop(0)
        day_str = '|'.join(day)
        times = re.findall(r'\d{2}:\d{2}\s–\s\d{2}:\d{2}', day_str)
        day = []
        separated_day = re.split(r'\d{2}:\d{2}\s–\s\d{2}:\d{2}', day_str)
        for lesson in separated_day:
            if lesson != '':
                lesson = lesson.split('|')
                for i in range(lesson.count('')):
                    lesson.pop(lesson.index(''))
                day.append(lesson)
        for i in range(len(times)):
            day[i].append(times[i])
        return day, date

    def _fill_day(self, group, week_type, date, time, subject, location,
                  lesson_type='', teacher=''):
        """Вставка в таблицу расписания на определенный день."""
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO Schedule " +
                    "(group_name, week_type, day," +
                    " time, lesson_type, subject, " +
                    "teacher, location) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [group, week_type, date,
                     time, lesson_type, subject, teacher, location])
        con.commit()
        con.close()

    def get_week_schedule(self, group, week_type):
        """Возвращает расписание на неделю (верхнюю или нижнюю."""
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT day, time, lesson_type, subject, " +
                               "teacher, location FROM Schedule WHERE " +
                               "group_name=? AND week_type=?",
                               [group, week_type]):
            result.append(list(row))
        con.close()
        return result

    def get_day_schedule(self, group, week_type, day):
        """Возвращает расписание на заданный день."""
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT day, time, lesson_type, subject," +
                               "teacher, location FROM Schedule WHERE " +
                               "group_name=? AND week_type=? AND day=?",
                               [group, week_type, day]):
            result.append(list(row))
        con.close()
        return result
