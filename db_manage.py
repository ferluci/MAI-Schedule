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
from sqlite3 import connect
import parser


def db_connect(func):
    def wrapped(self, *args, **kwargs):
        con = connect(self.db_name)
        cur = con.cursor()
        result = func(self, *args, **kwargs, cur=cur)
        con.commit()
        con.close()
        return result

    return wrapped


class Database:
    """Класс обеспечивающий работу с базой данных."""
    def __init__(self, db_name):
        self.db_name = db_name
        self.tables = self.get_tables()
        self.create_notification_table()
        # Если таблицы отсутствуют в базе данных, то они создаются
        # и автоматически заполняются
        if len(self.tables) == 0:
            self.create_users_table()
            self.create_groups_table()
            self.create_schedule_table()
            self.create_session_table()
            self.fill_groups_table()
            self.groups = tuple(self.get_groups())
            self.fill_schedule_table()
            self.fill_session_table()
            self.create_notification_table()
        self.groups = tuple(self.get_groups())

    @db_connect
    def get_tables(self, cur):
        """Возвращает список таблиц"""
        cur.execute("SELECT name FROM sqlite_master " +
                    "WHERE type = 'table';")
        result = cur.fetchall()
        return result

    # Users table api
    # ===============

    @db_connect
    def create_users_table(self, cur):
        """Создание таблицы пользователей."""
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Users(id INTEGER, name CHAR(20), group_name CHAR(20))")

    @db_connect
    def insert_user(self, user_id, name, group=None, cur=None):
        """Вставка пользователя в таблицу."""
        cur.execute("INSERT INTO Users (id, name, group_name) " +
                    "VALUES (?, ?, ?)",
                    [user_id, name, group])

    @db_connect
    def check_id(self, user_id, cur=None):
        """Проверка наличия пользователя в таблице по его id."""

        cur.execute("SELECT * FROM Users WHERE id=?", [user_id])
        result = cur.fetchone()
        return result

    @db_connect
    def get_group(self, user_id, cur=None):
        """Получение группы пользователя."""
        cur.execute("SELECT group_name FROM Users WHERE id=?", [user_id])
        group = cur.fetchone()
        if group is not None:
            group = group[0]
        return group

    @db_connect
    def update_group(self, user_id, group, cur=None):
        """Изменение группы пользователя."""
        cur.execute('UPDATE Users SET group_name=? WHERE id=?',
                    [group, user_id])

    # Groups table api
    # ================

    @db_connect
    def create_groups_table(self, cur=None):
        """Создание таблицы групп."""
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Groups(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name CHAR(20))")

    @db_connect
    def fill_groups_table(self, cur=None):
        """Заполнение таблицы групп."""
        group_list = parser.parse_groups()
        for group in group_list:
            cur.execute('INSERT INTO Groups (group_name) VALUES (?)',
                        [group])

    @db_connect
    def get_groups(self, cur=None):
        """Получить список групп."""
        groups_list = []
        for row in cur.execute("SELECT group_name FROM Groups"):
            groups_list.append(row[0])
        return groups_list

    # Notification table api
    # ======================

    @db_connect
    def create_notification_table(self, cur=None):
        """Создание таблицы уведомлений."""
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Notification(" +
                    "id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT," +
                    "user_id INTEGER," +
                    "note TEXT," +
                    "date CHAR(20)," +
                    "time CHAR(5))")

    @db_connect
    def insert_note(self, user_id, note, date, time, cur=None):
        """Добавление уведомления."""
        cur.execute("INSERT INTO Notification " +
                    "(user_id, note, date, time)" +
                    "VALUES (?, ?, ?, ?)",
                    [user_id, note, date, time])

    @db_connect
    def get_notes(self, cur=None):
        """Получение списка уведомлений."""
        notes_list = []
        for row in cur.execute("SELECT * FROM Notification"):
            notes_list.append(row)
        return notes_list

    @db_connect
    def delete_note(self, note_id, cur=None):
        """Удаление уведомления."""
        cur.execute("DELETE FROM Notification WHERE id=?", [note_id])

    # Session table api
    # =================

    @db_connect
    def create_session_table(self, cur=None):
        """Создание таблицы расписания сессии."""
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Session(" +
                    "id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name CHAR(20), " +
                    "date CHAR(8), " +
                    "time CHAR(15), " +
                    "subject CHAR(70), " +
                    "teacher CHAR(70), " +
                    "location CHAR(25))")

    @db_connect
    def fill_session_table(self, cur=None):
        """Заполнение таблицы расписания сессии."""
        for group in parser.parse_examining_groups():
            session = parser.parse_session_schedule(group)
            for exam in session:
                # Иногда на сайте не указывается имя преподавателя,
                # из-за чего необходимо выполнять данную проверку, дабы
                # не выйти за границы списка.
                if len(exam) == 6:
                    date = exam[0].replace(u'\xa0', u'')
                    time = exam[1].replace(u'\xa0', u'')
                    subject = exam[3].replace(u'\xa0', u'')
                    teacher = exam[4].replace(u'\xa0', u'')
                    location = exam[5].replace(u'\xa0', u'')
                    cur.execute("INSERT INTO Session " +
                                "(group_name, date, time," +
                                " subject, teacher, location) " +
                                "VALUES (?, ?, ?, ?, ?, ?)",
                                [group, date, time,
                                 subject, teacher, location])
                else:
                    date = exam[0].replace(u'\xa0', u'')
                    time = exam[1].replace(u'\xa0', u'')
                    subject = exam[3].replace(u'\xa0', u'')
                    location = exam[4].replace(u'\xa0', u'')
                    cur.execute("INSERT INTO Session " +
                                "(group_name, date, time," +
                                " subject, location) " +
                                "VALUES (?, ?, ?, ?, ?)",
                                [group, date, time, subject, location])

            sleep(0.5)

    @db_connect
    def get_session(self, group, cur=None):
        """Возвращает все экзамены для данной группы."""
        result = []
        for row in cur.execute("SELECT date, time, subject, "
                               "teacher, location " +
                               "FROM Session WHERE group_name=?",
                               [group]):
            result.append(list(row))
        if not result:
            return None
        return result

    # Schedule table api
    # ==================

    @db_connect
    def create_schedule_table(self, cur=None):
        """Создание таблицы расписания."""
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Schedule(" +
                    "id INTEGER  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name CHAR(20), " +
                    "week_type INTEGER, " +
                    "week_day CHAR(2), " +
                    "time CHAR(15), " +
                    "lesson_type CHAR(5), " +
                    "subject CHAR(70), " +
                    "teacher CHAR(70), " +
                    "location CHAR(25))")

    def fill_schedule_table(self):
        """Заполнение таблицы расписания."""
        for group in self.groups:
            down_week = parser.parse_academic_schedule(group, 4)
            up_week = parser.parse_academic_schedule(group, 5)

            self._fill_week(up_week, group, 0)
            self._fill_week(down_week, group, 1)

    def _fill_week(self, week, group, week_type):
        """Вставка в таблицу расписания на неделю."""
        for day in week:
            week_day = day.pop(0)[-2:]
            day = self._sepate_by_lessons(day)
            for lesson in day:
                if lesson[0] == 'Военная подготовка':
                    subject = 'Военная подготовка'
                    time = lesson[-1].replace(u'\xa0', u'')
                    location = lesson[-2].replace(u'\xa0', u'')
                    self._fill_day(group, week_type, week_day,
                                   time, subject, location)
                    continue

                time = lesson[-1].replace(u'\xa0', u'')
                location = lesson[-2].replace(u'\xa0', u'')
                lesson_type = lesson[0].replace(u'\xa0', u'')
                subject = lesson[1].replace(u'\xa0', u'')
                if len(lesson) == 4:
                    teacher = ''
                else:
                    teacher = lesson[2].replace(u'\xa0', u'')
                self._fill_day(group, week_type, week_day, time,
                               subject, location, lesson_type, teacher)

    def _sepate_by_lessons(self, day):
        """Преобразовывает массив с расписанием.
        Получает на вход массив с расписанием на день с сайта МАИ.
        Преобразует в двумерный массив: [[занятие1], [занятие2]...].
        """
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
        return day

    @db_connect
    def _fill_day(self, group, week_type, week_day, time, subject, location,
                  lesson_type='', teacher='', cur=None):
        """Вставка в таблицу расписания на определенный день."""
        cur.execute("INSERT INTO Schedule " +
                    "(group_name, week_type, week_day," +
                    " time, lesson_type, subject, " +
                    "teacher, location) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [group, week_type, week_day,
                     time, lesson_type, subject, teacher, location])

    @db_connect
    def get_week_schedule(self, group, week_type, cur=None):
        """Возвращает расписание на неделю (верхнюю или нижнюю)."""
        result = []
        for row in cur.execute("SELECT week_day, time, lesson_type, subject, " +
                               "teacher, location FROM Schedule WHERE " +
                               "group_name=? AND week_type=?",
                               [group, week_type]):
            result.append(list(row))
        return result

    @db_connect
    def get_day_schedule(self, group, week_type, week_day, cur=None):
        """Возвращает расписание на заданный день."""
        result = []
        for row in cur.execute("SELECT week_day, time, lesson_type, subject," +
                               "teacher, location FROM Schedule WHERE " +
                               "group_name=? AND week_type=? AND week_day=?",
                               [group, week_type, week_day]):
            result.append(list(row))
        return result