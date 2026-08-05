# Clean-Room Reproduction Report

**Status: PASS**

The repository was copied into a fresh temporary directory. The historical research tree, private bundle, protected media, and private labels were unavailable.

| Step | Result |
|---|---|
| `/usr/bin/python -m pip install` | PASS |
| `/usr/bin/python -m compileall -q` | PASS |
| `/usr/bin/python -m retroz_s1 --help` | PASS |
| `/usr/bin/python -m retroz_s1 list-candidates` | PASS |
| `/usr/bin/python -m retroz_s1 inspect` | PASS |
| `/usr/bin/python scripts/generate_synthetic_demo.py` | PASS |
| `/usr/bin/python -m pytest -q` | PASS |
| `/usr/bin/python -m retroz_s1 reproduce-failure` | PASS |
| `/usr/bin/python -m retroz_s1 reproduce-failure` | PASS |
| `/usr/bin/python -m retroz_s1 render` | PASS |
| `/usr/bin/python -m retroz_s1 render` | PASS |
| `/usr/bin/python -m retroz_s1 oracle-render` | PASS |
| `/usr/bin/python -m retroz_s1 compare` | PASS |
| `/usr/bin/python scripts/build_report.py` | PASS |
| `/usr/bin/python scripts/build_docs.py` | PASS |
| `/usr/bin/python scripts/validate_documents.py` | PASS |
| `/usr/bin/python scripts/build_manifests.py` | PASS |
| `/usr/bin/python scripts/verify_repository.py` | PASS |

Docker verification is recorded in `DOCKER_REPRODUCTION_REPORT.md`.
