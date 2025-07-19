.PHONY: help install test run down clean build bash

# Default target - show help
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make install  - Install all requirements and dependencies"
	@echo "  make test     - Run tests"
	@echo "  make run      - Run the service and all related services in Docker"
	@echo "  make down     - Teardown all running services"
	@echo "  make clean    - Teardown and removal of all containers"
	@echo "  make build    - Build Docker image"
	@echo "  make bash     - Open bash shell in container"

# Virtual environment name (can be overridden with VENV_NAME=myenv make install)
VENV_NAME ?= debater-env

# Detect which docker compose command is available
DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; elif docker compose version >/dev/null 2>&1; then echo "docker compose"; else echo "docker-compose"; fi)

# Check if Docker is installed
check-docker:
	@if ! command -v docker >/dev/null 2>&1; then \
		echo "Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop"; \
		exit 1; \
	fi

# Check if docker compose is available
check-docker-compose:
	@if ! $(DOCKER_COMPOSE) version >/dev/null 2>&1; then \
		echo "Docker Compose is not available. Please install Docker Desktop or docker-compose"; \
		exit 1; \
	fi

# Install all requirements
install: check-docker check-docker-compose
	@echo "Installing requirements..."
	@echo "Docker and Docker Compose are available."
	@echo "Installing Python requirements..."
	@if [ ! -d "$(VENV_NAME)" ]; then \
		echo "Creating virtual environment '$(VENV_NAME)'..."; \
		python3 -m venv $(VENV_NAME); \
	fi
	@echo "Activating virtual environment and installing requirements..."
	@. $(VENV_NAME)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
	@echo "Installation complete!"
	@echo "Run 'make build' to build the Docker image."
	@echo "Run 'source $(VENV_NAME)/bin/activate' to activate the virtual environment."

# Build Docker image
build: check-docker check-docker-compose
	$(DOCKER_COMPOSE) build

# Run tests
test: check-docker check-docker-compose
	@echo "Running tests..."
	@if [ -d "$(VENV_NAME)" ]; then \
		echo "Running tests in virtual environment..."; \
		. $(VENV_NAME)/bin/activate && python -m pytest tests/ -v; \
	else \
		echo "Running tests in Docker..."; \
		$(DOCKER_COMPOSE) run --rm --profile test test; \
	fi

# Run the service and all related services
run: check-docker check-docker-compose
	$(DOCKER_COMPOSE) up

# Teardown all running services
down: check-docker check-docker-compose
	$(DOCKER_COMPOSE) down

# Teardown and removal of all containers
clean: check-docker check-docker-compose
	$(DOCKER_COMPOSE) down --rmi all --volumes --remove-orphans

# Open bash shell in container
bash: check-docker check-docker-compose
	$(DOCKER_COMPOSE) run --rm --entrypoint=bash app
