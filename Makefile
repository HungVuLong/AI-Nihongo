# Makefile for AI-Nihongo

.PHONY: help install dev-install test lint format type-check clean docs server

# Default target
help:
	@echo "Available commands:"
	@echo "  install      Install the package"
	@echo "  dev-install  Install in development mode with all dependencies"
	@echo "  test         Run tests"
	@echo "  lint         Run linting"
	@echo "  format       Format code with black"
	@echo "  type-check   Run type checking with mypy"
	@echo "  clean        Clean build artifacts"
	@echo "  docs         Start documentation server"
	@echo "  server       Start API server"
	@echo "  chat         Start interactive chat"

# Installation
install:
	pip install .

dev-install:
	pip install -e ".[dev,ml]"
	pre-commit install

# Testing
test:
	pytest

test-cov:
	pytest --cov=ai_nihongo --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 ai_nihongo tests

format:
	black ai_nihongo tests examples
	isort ai_nihongo tests examples

type-check:
	mypy ai_nihongo

# Comprehensive quality check
check: lint type-check test

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# Documentation
docs:
	@echo "Opening documentation..."
	@echo "API docs will be available at http://localhost:8000/docs when server is running"

# Development servers
server:
	ai-nihongo server

chat:
	ai-nihongo chat

# Build and release
build: clean
	python -m build

release: build
	python -m twine upload dist/*

# Setup development environment
setup-dev: dev-install
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify installation"

# Docker commands (if you add Docker later)
docker-build:
	docker build -t ai-nihongo .

docker-run:
	docker run -p 8000:8000 ai-nihongo