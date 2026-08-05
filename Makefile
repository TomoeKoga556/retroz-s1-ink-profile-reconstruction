PYTHON ?= python

.PHONY: setup test verify synthetic-demo report docs-build docs-serve clean-room-test
setup:
	$(PYTHON) -m pip install -e . --no-deps
test:
	PYTHONPATH=src $(PYTHON) -m pytest
verify:
	PYTHONPATH=src $(PYTHON) scripts/update_registry_provenance.py
	PYTHONPATH=src $(PYTHON) scripts/validate_documents.py
	PYTHONPATH=src $(PYTHON) scripts/build_manifests.py
	PYTHONPATH=src $(PYTHON) scripts/verify_repository.py
synthetic-demo:
	PYTHONPATH=src $(PYTHON) scripts/generate_synthetic_demo.py
report:
	PYTHONPATH=src $(PYTHON) scripts/build_report.py
docs-build:
	PYTHONPATH=src $(PYTHON) scripts/build_docs.py
docs-serve: docs-build
	$(PYTHON) -m http.server 8000 --directory site-preview
clean-room-test:
	$(PYTHON) scripts/clean_room_test.py

.PHONY: release
release:
	PYTHONPATH=src $(PYTHON) scripts/build_release.py
