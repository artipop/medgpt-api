install:
	poetry install

dev: install
	docker compose -f docker/docker-compose-dev.yml --project-directory . up --build -d

revision:
	poetry run alembic revision --autogenerate

run_migrations:
	poetry run alembic upgrade head
