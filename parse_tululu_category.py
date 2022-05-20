import urllib.parse

import requests
from bs4 import BeautifulSoup


if __name__ == '__main__':
    url = 'https://tululu.org/l55/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    book_urls = [
        urllib.parse.urljoin(url, table.find('a')['href']) for table in soup.find_all('table', class_='d_book')
    ]
    for book in book_urls:
        print(book)
