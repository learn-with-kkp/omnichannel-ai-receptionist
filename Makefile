.PHONY: help install test lint run deploy clean docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  make install     Install all dependencies and local packages"
	@echo "  make test        Run all 78 pytest unit and integration tests"
	@echo "  make run         Run local development server on port 8000"
	@echo "  make deploy      Execute pre-flight tests and deploy to Vercel"
	@echo "  make clean       Execute \$0.00 teardown and wipe temp files"
	@echo "  make docker-up   Spin up Docker compose services"
	@echo "  make docker-down Teardown Docker compose services"

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -e .

test:
	PYTHONPATH=. pytest tests/ -v --durations=10

run:
	uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload

deploy:
	./deploy.sh

clean:
	./clear.sh

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down -v
