import requests
from pathlib import Path

def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError

if __name__ == '__main__':
    Path('book').mkdir(exist_ok=True)
    for book_id in range(1, 11):
        url = "https://tululu.org/txt.php?id={}".format(book_id)
        response = requests.get(url)
        try:
            check_for_redirect(response)
        except:
            continue
        response.raise_for_status()
        filename = 'book/{}.txt'.format(book_id)
        with open(filename, 'wb') as file:
            file.write(response.content)
