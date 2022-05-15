import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    Path(folder).mkdir(exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    path = os.path.join(folder, sanitize_filename(f'{filename}.txt'))
    with open(path, 'wb') as file:
        file.write(response.content)
    return path


if __name__ == '__main__':
    for book_id in range(1, 11):
        url = "https://tululu.org/b{}/".format(book_id)
        response = requests.get(url)
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        tululu_title = soup.find('td', class_='ow_px_td').find('h1').text.split('::')
        book_title = tululu_title[0].strip()
        book_author = tululu_title[1].strip()
        url = "https://tululu.org/txt.php?id={}".format(book_id)
        download_txt(url, f'{book_id}.{book_title}')
