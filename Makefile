install:
	poetry install

dev: install
	docker-compose -f docker/docker-compose-dev.yml --project-directory . up --build -d
	poetry run python src/main.py

revision:
	poetry run alembic revision --autogenerate

run_migrations:
	poetry run alembic upgrade head