PYTHON := ./.venv/bin/python
PIP := ./.venv/bin/pip

.PHONY: help install test run run-html run-gradio

help:
	@echo "Available targets:"
	@echo "  make install     Install project dependencies into .venv"
	@echo "  make test        Run unit tests"
	@echo "  make run         Run the CLI app"
	@echo "  make run-html    Run the HTML app"
	@echo "  make run-gradio  Run the Gradio app"

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m unittest discover -s tests -v

run:
	$(PYTHON) main.py

run-html:
	$(PYTHON) html_app.py

run-gradio:
	$(PYTHON) gradio_app.py
