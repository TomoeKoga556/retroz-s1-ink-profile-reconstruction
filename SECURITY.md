# Security policy

## Reporting a vulnerability

Please use GitHub's private security-advisory flow for vulnerabilities, secret
exposure or path-disclosure issues. Do not post credentials, private paths or
sensitive sample data in a public issue.

## Scope

The package performs no network requests, model API calls or automatic media
downloads. The main security boundary is local input handling: image files,
label JSON and output paths should be treated as untrusted.

Run unknown inputs in a constrained environment, keep Pillow and NumPy current,
and avoid processing decompression bombs or files from an untrusted source on a
privileged account. The CLI writes only to paths supplied by the user and emits
provenance sidecars next to generated images.

Security fixes should include a regression test and should not weaken the public
asset or provenance checks.
