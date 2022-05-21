import json
import os
import urllib.parse
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


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
    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(folder, sanitize_filename(filename))
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


if __name__ == '__main__':
    books = []
    for page in range(1, 2):
        url = f'https://tululu.org/l55/{page}/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_urls = {
            urllib.parse.urljoin(url, a['href']) for a in soup.select('table.d_book a[href*="/b"]')
        }
        for book_url in book_urls:
            response = requests.get(book_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            book = parse_book_page(soup)
            if book['txt_src']:
                url_txt = urllib.parse.urljoin(book_url, book['txt_src'])
                book['txt_src'] = download_file(url_txt, f'{book["title"]}.txt', 'books/')
                url_image = urllib.parse.urljoin(url, book['image_src'])
                book['image_src'] = download_file(url_image, os.path.basename(book['image_src']), 'images/')
                books.append(book)

    with open("books.json", "w") as my_file:
        json.dump(books, my_file, sort_keys=True, ensure_ascii=False, indent=4)
