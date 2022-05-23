# Парсер книг с сайта [tululu.org](https://tululu.org)

Скрипт предназначен для скачивания файлов книг и их обложек из онлайн-библиотеки [tululu.org](https://tululu.org)

### Как установить

Python3 должен быть уже установлен. 
Затем используйте `pip` (или `pip3`, если есть конфликт с Python2) для установки зависимостей:
```
pip install -r requirements.txt
```

### Аргументы и пример запуска скрипта

Пример команды для запуска скрипта
```
parse_tululu_category.py --start_page 700 --json_path 1.json --dest_folder result --skip_imgs
```
Описание параметров:

```--start_id``` стартовый номер страницы

```--end_id``` конечный номер страницы

`--dest_folder` путь к каталогу с результатами парсинга: картинкам, книгам, JSON.

`--json_path` путь к *.json файлу с результатами

`--skip_txt` не скачивать книги

`--skip_imgs` не скачивать картинки

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).