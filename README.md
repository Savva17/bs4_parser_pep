# Проект парсинга pep и документации python

[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)

## Описание
Парсер документации python
```
https://docs.python.org/3/
```
```
https://peps.python.org/
```

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
https://github.com/Savva17/bs4_parser_pep.git
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
### Зайти в папку с main.py
```
cd src/
```
### запустите файл main.py выбрав необходимый парсер и аргументы(приведены ниже)
```
python main.py [вариант парсера] [аргументы]
```
### Встроенные парсеры
- whats-new   
Парсер выводящий спсок изменений в python.
```
python main.py whats-new [аргументы]
```
- latest_versions
Парсер выводящий список версий python и ссылки на их документацию.
```
python main.py latest-versions [аргументы]
```
- download   
Парсер скачивающий zip архив с документацией python в pdf формате.
```
python main.py download [аргументы]
```
- pep
Парсер выводящий список статусов документов pep
и количество документов в каждом статусе. 
```
python main.py pep [аргументы]
```
### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache
Очистка кеша перед выполнением парсинга.
```
python main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python main.py [вариант парсера] -o file
```

Автор проекта: Морозов Савва

Профили автора на GitHub:
- **GitHub**: [Профиль Савва Морозов](https://github.com/Savva17)
