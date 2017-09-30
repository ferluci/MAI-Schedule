from requests import get
from bs4 import BeautifulSoup


def _group_parser(target_url):
    request = get(target_url)
    soup = BeautifulSoup(request.text, "html.parser")
    groups = []
    for group in soup.find_all('a', class_="sc-group-item"):
        group = group.get_text()
        groups.append(group)
    return groups


def parse_groups():
    """Парсинг списка групп с сайта МАИ."""
    target_url = 'https://www.mai.ru/education/schedule'
    return _group_parser(target_url)


def parse_examining_groups():
    """Парсинг групп, имеющих экзамен."""
    target_url = 'https://www.mai.ru/education/schedule/session'
    return _group_parser(target_url)


def _schedule_parser(target_url):
    request = get(target_url)
    soup = BeautifulSoup(request.text, "html.parser")
    result = []
    for day in soup.find_all('div', class_="sc-container"):
        day = day.get_text().split('\n')
        day = [x for x in day if x != '']
        result.append(day)
    return result


def parse_schedule(group_name, week_number):
    """Парсинг расписания."""
    target_url = "http://www.mai.ru/" + \
                 "education/schedule/detail.php?group=" + \
                 group_name + '&week=' + str(week_number)
    return _schedule_parser(target_url)


def parse_session(group_name):
    """Парсинг экзаменов."""
    target_url = "https://www.mai.ru/" + \
                 "education/schedule/session.php?group=" + \
                 group_name
    return _schedule_parser(target_url)
