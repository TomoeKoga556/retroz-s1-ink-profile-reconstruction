# Reproducible Environment

The package was assembled and verified with CPython 3.14.6 on 64-bit Linux. The supported package contract is CPython 3.11 or newer; the reference container uses CPython 3.12. Runtime operation is CPU-only and deterministic for identical NumPy and Pillow versions.

Pinned assembly versions are recorded in `requirements-lock.txt`. Normal runtime requires NumPy and Pillow. PyYAML is used for registry parity, pytest for tests, Matplotlib for the PDF, and MkDocs is optional because a dependency-free local site builder is included.

No GPU, model weight, external API, downloaded media, analytics service, or private dataset is required. The public masks are documented approximations and do not reproduce the private historical M0 products.
