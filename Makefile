.PHONY: help install build run test lint clean docker-build docker-run

help:
	@echo "Women Safety & Emergency Assistance Platform Commands:"
	@echo "  make install      Install Python dependencies"
	@echo "  make build        Validate and compile application bytecode"
	@echo "  make run          Run the Flask web server on port 5000"
	@echo "  make test         Execute full pytest test suite"
	@echo "  make lint         Check code syntax and cleanliness"
	@echo "  make docker-build Build Docker container image"
	@echo "  make docker-run   Run Docker container"

install:
	pip install -r requirements.txt

build:
	python -m compileall app/
	python measure.py

run:
	python app.py

test:
	pytest -v

lint:
	python -m py_compile app.py main.py run.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docker-build:
	docker build -t womensafety-platform:latest .

docker-run:
	docker run -p 5000:5000 womensafety-platform:latest
