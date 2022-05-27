import json

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open("books.json", "r") as my_file:
    books_json = my_file.read()

rendered_page = template.render(
    {
        'books': json.loads(books_json)
    }
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)