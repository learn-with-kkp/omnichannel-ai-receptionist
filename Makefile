.PHONY: help install run test lint docker-up docker-down clean

PYTHON ?= python3

help:
	@echo "Available commands:"
	@echo "  make install     - Install Python dependencies"
	@echo "  make run         - Run FastAPI webhook server locally"
	@echo "  make test        - Run test suite"
	@echo "  make docker-up   - Start FastAPI + n8n via Docker Compose"
	@echo "  make docker-down - Stop containers"
	@echo "  make clean       - Remove SQLite database and cache artifacts"

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

test:
	$(PYTHON) -m pytest tests/ -v

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

clean:
	rm -f *.db test_salon.db
	find . -type d -name "__pycache__" -exec rm -rf {} +

