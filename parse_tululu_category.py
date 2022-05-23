import argparse
import json
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


def get_cli_arguments():
    parser = argparse.ArgumentParser(
        description='Скрипт для парсинга категории фантастики онлайн библиотеки tululu.org'
    )
    parser.add_argument('--start_page', default=1, help='стартовый номер страницы', type=int)
    parser.add_argument('--end_page', help='конечный номер страницы', type=int)
    parser.add_argument(
        '--dest_folder',
        help='путь к каталогу с результатами парсинга: картинкам, книгам, JSON.',
        default=''
    )
    parser.add_argument(
        '--json_path',
        help='путь к *.json файлу с результатами',
        default='books.json'
    )
    parser.add_argument('--skip_txt', help='не скачивать книги', action='store_true')
    parser.add_argument('--skip_imgs', help='не скачивать картинки', action='store_true')
    parser.add_argument('--max_retries', default=10,
                        help='Максимальное кол-во попыток переподключения', type=int)
    return parser.parse_args()


def parse_book_page(soup):
    tululu_title = soup.select_one('.ow_px_td h1').text.split('::')
    img_src = soup.select_one('.bookimage img')['src']
    txt_a_tag = soup.select_one('table.d_book a[href*=txt]')
    txt_src = txt_a_tag['href'] if txt_a_tag else ''
    comments = [span.text for span in soup.select('div.texts span')]
    genres = [genre.text for genre in soup.select('span.d_book a')]
    book = {
        'title': tululu_title[0].strip(),
        'author': tululu_title[1].strip(),
        'image_src': img_src,
        'txt_src': txt_src,
        'comments': comments,
        'genres': genres
    }
    return book


def download_file(url, filename, folder='books/'):
    Path(folder).mkdir(exist_ok=True)
    response = make_request_with_reconnection(url)
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


def get_last_page_number():
    url = f'https://tululu.org/l55/'
    response = make_request_with_reconnection(url)
    soup = BeautifulSoup(response.text, 'lxml')
    return int(soup.select('p.center a')[-1].text)


def make_request_with_reconnection(url):
    for current_attempt in range(args.max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            check_for_redirect(response)
            return response
        except (requests.ConnectTimeout, requests.ConnectionError):
            time.sleep(1 if current_attempt == 0 else 5)
    else:
        raise requests.ConnectTimeout


if __name__ == '__main__':
    books = []
    args = get_cli_arguments()
    if not args.end_page:
        try:
            args.end_page = get_last_page_number() + 1
        except (requests.HTTPError, requests.ConnectTimeout, requests.ConnectionError):
            print('Ошибка при получении количества страниц. Выполнение скрипта прервано')
            exit()
    Path(args.dest_folder).mkdir(exist_ok=True)
    for page in range(args.start_page, args.end_page):
        url = f'https://tululu.org/l55/{page}/'
        go_to_nextpage = False
        try:
            response = make_request_with_reconnection(url)
        except requests.HTTPError:
            print(f'Ошибка при попытке получения списка книг, url: {url}\n')
            continue
        except requests.ConnectTimeout:
            print('Ошибка соединения с сайтом. Выполнение скрипта прервано')
            exit()
        soup = BeautifulSoup(response.text, 'lxml')
        book_urls = {
            urllib.parse.urljoin(url, a['href']) for a in soup.select('table.d_book a[href*="/b"]')
        }
        for book_url in book_urls:
            try:
                response = make_request_with_reconnection(book_url)
                soup = BeautifulSoup(response.text, 'lxml')
                book = parse_book_page(soup)
                if book['txt_src'] and not args.skip_txt:
                    url_txt = urllib.parse.urljoin(book_url, book['txt_src'])
                    folder = os.path.join(args.dest_folder, 'books')
                    book['txt_src'] = download_file(url_txt, f'{book["title"]}.txt', folder)
                if book['txt_src'] and not args.skip_imgs:
                    url_image = urllib.parse.urljoin(url, book['image_src'])
                    folder = os.path.join(args.dest_folder, 'images')
                    book['image_src'] = download_file(url_image, os.path.basename(book['image_src']), folder)
            except requests.HTTPError:
                print(f'Ошибка при попытке загрузки книги {book_url}\n')
                continue
            except (requests.ConnectTimeout, requests.ConnectionError):
                print('Ошибка соединения с сайтом. Выполнение скрипта прервано')
                exit()
            books.append(book)
    folder = os.path.join(args.dest_folder, args.json_path)
    with open(folder, "w") as my_file:
        json.dump(books, my_file, sort_keys=True, ensure_ascii=False, indent=4)
