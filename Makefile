install:
	poetry install

dev: install
	docker-compose -f docker/docker-compose-dev.yml --env-file .env-example --project-directory . up --build -d
	poetry run python3 src/main.py

revision:
	poetry run alembic revision --autogenerate

run_migrations:
	poetry run alembic upgrade head