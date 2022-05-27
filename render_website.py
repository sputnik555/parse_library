import json

from more_itertools import grouper
from jinja2 import Environment, FileSystemLoader, select_autoescape


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('template.html')
    with open("books.json", "r") as my_file:
        books_json = my_file.read()
    books_grouped = list(grouper(json.loads(books_json), 2))
    rendered_page = template.render({'books': books_grouped})
    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    on_reload()
