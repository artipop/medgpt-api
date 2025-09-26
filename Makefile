install:
	poetry install

dev:
	docker-compose -f docker/docker-compose-dev.yml --env-file .env --project-directory . up --build -d
	poetry run python3 src/main.py

start:
	poetry run uvicorn src.main:app --host 0.0.0.0 --reload

rev:
	poetry run alembic revision --autogenerate

mig:
	poetry run alembic upgrade head
	 
kill:
	taskkill /f /im python.exe