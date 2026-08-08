PYTHON ?= python

.PHONY: install dev lint test synthetic-demo report docs-build docs-serve verify release clean

install:
	$(PYTHON) -m pip install -e .

dev:
	$(PYTHON) -m pip install -e ".[dev,reproduce]"

lint:
	$(PYTHON) -m ruff check .

test:
	$(PYTHON) -m pytest

synthetic-demo:
	$(PYTHON) scripts/generate_synthetic_demo.py

report:
	$(PYTHON) scripts/build_report.py

docs-build:
	$(PYTHON) scripts/build_docs.py

docs-serve:
	$(PYTHON) -m mkdocs serve

verify:
	$(PYTHON) scripts/update_registry_provenance.py
	$(PYTHON) scripts/validate_documents.py
	$(PYTHON) scripts/build_manifests.py
	$(PYTHON) scripts/verify_repository.py

release: synthetic-demo report docs-build verify
	$(PYTHON) scripts/build_release.py

clean:
	rm -rf build dist release site-preview .pytest_cache .ruff_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
