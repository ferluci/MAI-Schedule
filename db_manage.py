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


import re
from time import sleep
from requests import get
from sqlite3 import connect
from bs4 import BeautifulSoup


class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.tables = self.get_tables()
        if len(self.tables) == 0:
            self.create_users_table()
            self.create_groups_table()
            self.create_scheldule_table()
            self.create_session_table()
            self.fill_groups_table()
            self.groups = tuple(self.get_groups())
            self.fill_scheldule_table()
            self.fill_session_table()
        self.groups = tuple(self.get_groups())

    def get_tables(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master " +
                    "WHERE type = 'table';")
        result = cur.fetchall()
        con.close()
        return result

    def create_users_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Users(id Integer, name char(20), group_name char(20))")
        con.close()

    def create_groups_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Groups(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name char(20))")
        con.commit()
        con.close()

    def create_session_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Session(" +
                    "id Integer  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name char(20), " +
                    "date char(8), " +
                    "time char(15), " +
                    "subject char(70), " +
                    "teacher char(70), " +
                    "location char(25))")
        con.commit()
        con.close()

    def create_scheldule_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS " +
                    "Scheldule(" +
                    "id Integer  NOT NULL PRIMARY KEY AUTOINCREMENT, " +
                    "group_name char(20), " +
                    "week_type Integer, " +
                    "day char(2), " +
                    "time char(15), " +
                    "lesson_type char(5), " +
                    "subject char(70), " +
                    "teacher char(70), " +
                    "location char(25))")
        con.commit()
        con.close()

    def _parse_groups(self):
        target_url = 'https://www.mai.ru/education/schedule'
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        groups = []
        for group in soup.find_all('a', class_="sc-group-item"):
            group = group.get_text()
            groups.append(group)
        return groups

    def _parse_examining_groups(self):
        target_url = 'https://www.mai.ru/education/schedule/session'
        request = get(target_url)
        soup = BeautifulSoup(request.text, "html.parser")
        groups = []
        for group in soup.find_all('a', class_="sc-group-item"):
            group = group.get_text()
            groups.append(group)
        return groups

    def _parse_session(self, group_name):
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

    def _parse_scheldule(self, group_name, week_number):
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

    def fill_groups_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        group_list = self._parse_groups()
        for group in group_list:
            cur.execute('INSERT INTO Groups (group_name) VALUES (?)',
                        [group.upper])
        con.commit()
        con.close()

    def fill_session_table(self):
        con = connect(self.db_name)
        cur = con.cursor()
        for group in self._parse_examining_groups():
            session = self._parse_session(group)
            for exam in session:
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

    def fill_scheldule_table(self):
        for group in self.groups:
            down_week = self._parse_scheldule(group, 4)
            up_week = self._parse_scheldule(group, 5)

            self._fill_week(up_week, group, 0)
            self._fill_week(down_week, group, 1)

    def _fill_week(self, week, group, week_type):
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
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO Scheldule " +
                    "(group_name, week_type, day," +
                    " time, lesson_type, subject, " +
                    "teacher, location) " +
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    [group, week_type, date,
                     time, lesson_type, subject, teacher, location])
        con.commit()
        con.close()

    def get_groups(self):
        con = connect(self.db_name)
        cur = con.cursor()
        groups_list = []
        for row in cur.execute("SELECT group_name FROM Groups"):
            groups_list.append(row[0])
        con.close()
        return groups_list

    def check_id(self, id):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT * FROM Users WHERE id=?", [id])
        result = cur.fetchone()
        return result

    def get_group(self, id):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("SELECT group_name FROM Users WHERE id=?", [id])
        group = cur.fetchone()
        if group is not None:
            group = group[0]
        return group

    def get_session(self, group):
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT date, time, subject, "
                               "teacher, location " +
                               "FROM Session WHERE group_name=?",
                               [group]):
            result.append(list(row))
        con.close()
        if result == []:
            return None
        return result

    def get_week_scheldule(self, group, week_type):
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT day, time, lesson_type, subject, " +
                               "teacher, location FROM Scheldule WHERE " +
                               "group_name=? AND week_type=?",
                               [group, week_type]):
            result.append(list(row))
        con.close()
        return result

    def get_day_scheldule(self, group, week_type, day):
        con = connect(self.db_name)
        cur = con.cursor()
        result = []
        for row in cur.execute("SELECT day, time, lesson_type, subject," +
                               "teacher, location FROM Scheldule WHERE " +
                               "group_name=? AND week_type=? AND day=?",
                               [group, week_type, day]):
            result.append(list(row))
        con.close()
        return result

    def insert_user(self, id, name, group=None):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute("INSERT INTO Users (id, name, group_name) " +
                    "VALUES (?, ?, ?)",
                    [id, name, group])
        con.commit()
        con.close()

    def update_group(self, id, group):
        con = connect(self.db_name)
        cur = con.cursor()
        cur.execute('UPDATE Users SET group_name=? WHERE id=?',
                    [group, id])
        con.commit()
        con.close()

