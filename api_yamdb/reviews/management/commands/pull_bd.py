import csv
import sqlite3

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Заполняет базу данных'

    def handle(self, *args, **options):

        DELIMITER = ','  # Разделитель в файле с данными

        # Подключаемся к БД в файле db.sqlite3
        con = sqlite3.connect('db.sqlite3')
        cur = con.cursor()

        # Открываем на чтение файл static/data/users.csv
        with open('static/data/users.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            # Генерируем список кортежей с данными из csv в to_users
            to_users = [(i['id'],
                         i['username'],
                         i['first_name'],
                         i['last_name'],
                         i['email'],
                         i['bio'],
                         i['role']) for i in file_data]

        with open('static/data/category.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            to_category = [(i['id'], i['name'], i['slug']) for i in file_data]

        with open('static/data/genre.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            to_genre = [(i['id'], i['name'], i['slug']) for i in file_data]

        with open('static/data/titles.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            to_titles = [(i['id'], i['name'], i['year'], i['category'])
                         for i in file_data]

        with open('static/data/genre_title.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            to_genre_title = [(i['id'], i['title_id'], i['genre_id'])
                              for i in file_data]

        with open('static/data/comments.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            to_comments = [(i['id'], i['text'], i['pub_date'], i['author'],
                            i['review_id'])
                           for i in file_data]

        with open('static/data/review.csv', 'r', encoding="utf8") as fin:
            file_data = csv.DictReader(fin, delimiter=DELIMITER)
            to_review = [(i['id'], i['text'], i['score'], i['pub_date'],
                          i['author'], i['title_id'])
                         for i in file_data]

        try:
            cur.executemany(
                "INSERT INTO users_user VALUES \
(?, '123', '0','Falce', ?, ?, ?, ?, 'Falce', 'Falce', '0', ?, ?);",
                to_users)
            cur.executemany(
                "INSERT INTO reviews_category VALUES (?, ?, ?);",
                to_category)
            cur.executemany(
                "INSERT INTO reviews_genre VALUES (?, ?, ?);",
                to_genre)
            cur.executemany(
                "INSERT INTO reviews_title VALUES (?, ?, ?,' ',?);",
                to_titles)
            cur.executemany(
                "INSERT INTO reviews_title_genre VALUES (?, ?, ?);",
                to_genre_title)
            cur.executemany(
                "INSERT INTO reviews_comments VALUES (?, ?, ?, ?, ?);",
                to_comments)
            cur.executemany(
                "INSERT INTO reviews_review VALUES (?, ?, ?, ?, ?, ?);",
                to_review)
            print('База данных заполнена.')
        except Exception:
            print('При заполнении базы данных возникли ошибки.')

        con.commit()
        con.close()
