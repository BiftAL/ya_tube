# yatube_final
Социальная сеть Yatube.
В проекте реализованы следующие возможности: регистрация пользователей, создание и редактирование постов, подписка на других авторов, написание комментариев к постам.

### Технологии:
Python 3.7, Django 3.2

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

```
https://github.com/BiftAL/ya_tube.git
```

```
cd ya_tube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
Для Windows:
```
source venv/Scripts/activate
```
Для Linux и MacOS:
```
source venv/bin/activate
```
Обновить менеджер пакетов
```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
Перейти в каталог с файлом manage.py

```
cd yatube/
```

Переименовать и отредактировать в корне проекта файл env.example в .env
```
mv yatube/env.example yatube/.env
nano yatube/.env
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

Проект будет доступен по ссылке:

```
http://127.0.0.1:8000/
```
Для создания суперпользователя необходимо остановить сервер и ввести в консоле команду:
```
python manage.py createsuperuser
```

Для доступа к админ.пенели необходимо перейти по адресу:
```
http://127.0.0.1:8000/admin/
```
Для запуска тестов выполнить команду:
```
pytest
```
