import json
import os

from livereload import Server
from more_itertools import grouper, chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape


BOOKS_IN_ROW = 2
ROWS_IN_PAGE = 10


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open("books.json", "r") as my_file:
        books = json.load(my_file)
    book_rows = list(grouper(books, BOOKS_IN_ROW))
    book_pages = list(chunked(book_rows, ROWS_IN_PAGE))
    os.makedirs('pages', exist_ok=True)
    for page_num, books in enumerate(book_pages, 1):
        rendered_page = template.render(
            {
                'books': books,
                'number_of_pages': len(book_pages),
                'current_page_number': page_num
            }
        )
        with open(
                os.path.join('pages', f'index{page_num}.html'),
                'w',
                encoding="utf8"
        ) as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
    server = Server()
    server.watch('template.html', on_reload)
    server.serve(root='./')
