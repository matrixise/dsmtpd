.PHONY: venv install-dev build check-dist upload test clean-build clean-venv clean

PYTHON := python3
VENV := .venv
VENV_PYTHON := $(VENV)/bin/python3
VENV_PIP := $(VENV)/bin/pip

# Create virtual environment
venv:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
		echo "Virtual environment created at $(VENV)"; \
	else \
		echo "Virtual environment already exists at $(VENV)"; \
	fi

# Install development dependencies
install-dev: venv
	@echo "Installing development dependencies..."
	$(VENV_PIP) install --upgrade pip
	$(VENV_PIP) install -r requirements-dev.txt
	$(VENV_PIP) install -e .
	@echo "Development environment ready!"

build: venv
	$(VENV_PYTHON) -m build

check-dist:
	$(VENV)/bin/twine check dist/*

upload:
	$(VENV)/bin/twine upload dist/*

test: install-dev
	$(VENV)/bin/pytest

# Clean build artifacts
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf dsmtpd.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	@echo "Build artifacts removed"

# Clean virtual environment
clean-venv:
	rm -rf $(VENV)
	@echo "Virtual environment removed"

# Clean everything (build artifacts + virtual environment)
clean: clean-build clean-venv
	@echo "All cleaned!"
