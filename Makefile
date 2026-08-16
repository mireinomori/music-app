PYTHON ?= python3
VENV := .venv
BIN := $(VENV)/bin

.PHONY: install test lint frontend-build dev-backend dev-frontend open-chrome

install:
	$(PYTHON) -m venv $(VENV)
	$(BIN)/python -m pip install --upgrade pip
	$(BIN)/python -m pip install -e './backend[transcription,dev]'
	npm install --prefix frontend

test:
	$(BIN)/pytest backend/tests -q

lint:
	$(BIN)/ruff check backend/app backend/tests

frontend-build:
	npm run build --prefix frontend

dev-backend:
	$(BIN)/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

dev-frontend:
	npm run dev --prefix frontend -- --host 127.0.0.1

open-chrome:
	open -a 'Google Chrome' http://127.0.0.1:5173/
