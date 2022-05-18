import argparse
import os
import time
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_file(url, filename, folder='books/'):
    Path(folder).mkdir(exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def parse_book_page(soup):
    tululu_title = soup.find('td', class_='ow_px_td').find('h1').text.split('::')
    img_src = soup.find('div', class_='bookimage').find('img')['src']
    comments = [comment.find('span').text for comment
                in soup.find_all('div', class_='texts')]
    genres = [genre.text for genre in soup.find('span', class_='d_book').find_all('a')]
    book = {
        'title': tululu_title[0].strip(),
        'author': tululu_title[1].strip(),
        'image_src': img_src,
        'image_filename': os.path.basename(img_src),
        'comments': comments,
        'genres': genres
    }
    return book


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Скрипт для парсинга онлайн библиотеки tululu.org'
    )
    parser.add_argument('--start_id', default=1, help='Стартовый id книги', type=int)
    parser.add_argument('--end_id', default=10, help='Конечный id книги', type=int)
    parser.add_argument('--max_retries', default=10,
                        help='Максимальное кол-во попыток переподключения', type=int)
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id + 1):
        url = "https://tululu.org/b{}/".format(book_id)

        for current_attempt in range(args.max_retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                check_for_redirect(response)

                soup = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(soup)

                url_txt = "https://tululu.org/txt.php?id={}".format(book_id)
                download_file(url_txt, f'{book_id}.{book["title"]}.txt', 'books/')
                url_image = urllib.parse.urljoin(url, book['image_src'])
                download_file(url_image, book["image_filename"], 'images/')
            except requests.HTTPError as error:
                print(f'Ошибка при попытке загрузки книги с id={book_id}\n')
                break
            except (requests.ConnectTimeout, requests.ConnectionError):
                if current_attempt == args.max_retries - 1:
                    print('Ошибка соединения с сайтом. Выполнение скрипта прервано')
                    exit()
                time.sleep(1 if current_attempt == 0 else 5)
                continue

            print('Заголовок: {}\nАвтор: {}\n'.format(book['title'], book['author']))
            break
