## MEDCHAT API
### Как стартовать проект
- `git clone ...`
- `cd <project dir>`
- `make dev`

### Как работать с миграциями
- `make revision` - сгенерировать новую миграцию
- `make run_migrations` - прокатить миграцию в базу
- ! при добавлении новых моделей таблиц SQLALchemy, чтобы Alembic их увидел нужно:
  - явно импортировать модель в файл окружения Alembic `alembic/env.py`
  - в файле модели импортировать класс `Base` из `database`
  - пример см. в `src/google_auth/models/`


структура проекта взята [отсюда](https://github.com/zhanymkanov/fastapi-best-practices)