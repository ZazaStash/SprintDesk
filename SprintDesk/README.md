# SprintDesk

Учебное полнофункциональное веб-приложение для управления задачами команды. Реализовано в рамках итогового проекта «Проектный практикум», 6 семестр.

## 1. Описание проекта

SprintDesk — доска задач с разграничением прав доступа: участники управляют собственными задачами, администратор видит задачи всей команды и назначает исполнителей. Данные хранятся в PostgreSQL; для локальной разработки можно использовать SQLite. Интерфейс адаптирован для компьютеров и телефонов.

## 2. Основные возможности

- Регистрация и авторизация с защищённым подписанным токеном.
- Роли `member` и `admin`, разграничение доступа к данным.
- CRUD задач, три статуса, три приоритета, описание и исполнитель.
- Три колонки Kanban, статистика, фильтрация, поиск.
- Валидация полей и ограничения на уровне базы данных.
- Документация OpenAPI, миграции, автоматические тесты и CI.

## 3. Стек технологий

Python 3.12, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 16, Pydantic 2, HTML5, CSS3, JavaScript, pytest, Docker Compose, GitHub Actions.

## 4. Структура проекта

```text
app/                 REST API, модели, безопасность, зависимости
app/routers/         Авторизация, участники и задачи
alembic/             Управление схемой БД и миграция
web/                 HTML, CSS и JavaScript интерфейс
tests/               Тесты авторизации, ролей, CRUD и валидации
docs/                User stories, план спринтов, пример PR
scripts/             Создание администратора, защита main в GitHub
.github/             Шаблон PR и CI
Dockerfile           Контейнер приложения
docker-compose.yml   PostgreSQL и приложение
.env.example         Переменные окружения
```

## 5. Переменные окружения проекта

| Переменная | Назначение |
| --- | --- |
| `DATABASE_URL` | URL подключения SQLAlchemy; локально без переменной используется SQLite |
| `SECRET_KEY` | Секрет для подписи токенов; на сервере обязательно заменить |
| `TOKEN_TTL` | Срок жизни токена в секундах, по умолчанию 86400 |
| `ADMIN_EMAIL` | Email администратора для скрипта создания |
| `ADMIN_PASSWORD` | Пароль администратора, от 8 символов |
| `ADMIN_NAME` | Имя администратора |

Пример переменных находится в `.env.example`. При локальном запуске Python автоматически не читает `.env`; передавайте переменные через оболочку либо `docker compose --env-file .env`.

## 6. Как запустить проект

### Вариант A — Docker Compose и PostgreSQL

Установите Docker. В корневой папке проекта:

```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
docker compose up --build -d
```

Откройте `http://localhost:8000`. Приложение автоматически применяет миграции Alembic.

Создание администратора:

```bash
docker compose exec -e ADMIN_EMAIL=admin@example.com -e ADMIN_PASSWORD='MySecurePassword123' app python -m scripts.seed_admin
```

### Вариант B — Python и локальная SQLite

Нужны Python 3.11+ и pip.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Windows: активация `.venv\Scripts\activate`, затем те же команды. Создание администратора:

```bash
ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD='MySecurePassword123' python -m scripts.seed_admin
```

В Windows PowerShell переменные задаются через `$env:ADMIN_EMAIL="..."` и `$env:ADMIN_PASSWORD="..."`.

### Тестирование

```bash
pytest -q
```

Каждый тест использует собственный изолированный файл SQLite во временной папке. Рабочая БД не затрагивается. GitHub Actions проверяет тесты и миграции на каждый Pull Request.

### API

- Веб-интерфейс: `http://localhost:8000/`
- Swagger: `http://localhost:8000/api/docs`
- Проверка работоспособности: `http://localhost:8000/api/health`

### GitHub и Pull Request

Создайте GitHub-репозиторий и загрузите текущую ветку `main`. Для изменения создайте `feature/*`, отправьте ветку, откройте Pull Request. Структура описания автоматически подставится из `.github/pull_request_template.md`. Пример находится в `docs/PR_EXAMPLE.md`. Для слияния нужен review и один approve.

При наличии прав администратора GitHub и установленного `gh` настройки защиты `main` можно применить через `bash scripts/github_setup.sh`. Требования: запрет прямого push, PR, минимум 1 approve и успешный CI.

Настройка репозитория GitHub, реальное проведение review и merge выполняются в GitHub под аккаунтами участников команды.

### Дополнительные материалы

- [`docs/USER_STORIES.md`](docs/USER_STORIES.md) — роли, user stories, модель данных, API.
- [`docs/SPRINTS.md`](docs/SPRINTS.md) — выполнение 4 спринтов.
- [`docs/PR_EXAMPLE.md`](docs/PR_EXAMPLE.md) — описание PR и проверка.

### Публикация подготовленной истории Git

Если установлен `gh` и выполнен вход через `gh auth login`, можно опубликовать текущий Git-репозиторий с feature-веткой, настроить защиту `main` и открыть PR:

```bash
bash scripts/github_publish.sh sprintdesk-project
```

Для approve нужен другой участник с доступом к репозиторию. Слияние выполняется после подтверждения review.
