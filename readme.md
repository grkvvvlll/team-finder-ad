# TeamFinder

Платформа, на которой разработчики, дизайнеры и другие специалисты могут находить единомышленников для совместной работы над pet-проектами. **Реализован вариант 2** - навыки пользователей и фильтрация участников по навыкам.

## Примечания для ревьюера

В `docker-compose.yml` порт изменен с `5432` на `5433`, поскольку порт 5432 был занят другим сервисом.

В `.env` нужно указать `POSTGRES_PORT=5433` и `TASK_VERSION=2`.

## 1. Виртуальное окружение

1. **Создайте виртуальное окружение (в папке проекта):**
```bash
   python3 -m venv venv
```

2. **Активируйте окружение:**
   - **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
   - **Windows (cmd):** `venv\Scripts\activate`
   - **Linux/Mac:** `source venv/bin/activate`

3. **Установите зависимости:**
```bash
   pip install -r requirements.txt
```

## 2. Создание `.env`

Скопируйте `.env_example` и заполните:
```bash
cp .env_example .env
```

| Переменная | Назначение |
|---|---|
| **DJANGO_SECRET_KEY** | Секретный ключ Django, используемый для подписи cookie и токенов. Можно сгенерировать при помощи `get_random_secret_key` из `django.core.management.utils` |
| **DJANGO_DEBUG** | Режим отладки (`True` для разработки) |
| **POSTGRES_DB** | Имя базы данных PostegreSQL |
| **POSTGRES_USER** | Имя пользователя PostgreSQL |
| **POSTGRES_PASSWORD** | Пароль пользователя PostgreSQL |
| **POSTGRES_HOST** | Адрес сервера БД (`localhost`) |
| **POSTGRES_PORT** | Порт подключения к БД (`5433`) |
| **TASK_VERSION** | Номер варианта задания (`2`) |

## 3. Запуск Docker

Откройте приложение Docker Desktop, затем в терминале выполните:
```bash
docker compose up -d
```

## 4. Применение миграций

```bash
python manage.py migrate
```

## 5. Загрузка тестовых данных

```bash
python manage.py loaddata fixtures.json
```

## 6. Запуск сервера

```bash
python manage.py runserver
```

## Остановка

Чтобы остановить контейнер с базой данных, выполните:
```bash
docker compose down
```

Проект доступен по адресу: [http://localhost:8000](http://localhost:8000).
