# Contributing

Contributions are welcome when they make a claim easier to inspect, reproduce or
falsify. Please open an issue before starting a new candidate lineage or changing
a scientific gate; small fixes can go directly to a pull request.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,docs]"
make test
```

Run the full public verification before opening a pull request:

```bash
make synthetic-demo
make report
make docs-build
make verify
```

## Scientific changes

A new candidate proposal must state, before results are interpreted:

- the exact operator and frozen parameters;
- expected measurable behavior;
- safety and rejection gates;
- data and asset boundaries;
- aggregation method;
- what result would count as failure;
- which files and hashes bind the implementation.

Synthetic success is not enough to claim real activation. Candidate output must
be measured independently, and a numerical change is not automatically a useful
visible change.

## Assets

Only original, licensed or synthetic assets may be committed. Do not add
protected animation frames, screenshots, frame-derived contact sheets, private
labels or raw private-session data. New public images need a deterministic
source or a short provenance note.

## Code and documentation

- Keep public APIs typed and tested.
- Preserve input arrays unless a function explicitly documents mutation.
- Fail closed on malformed input or missing evidence.
- Prefer a small, direct explanation over duplicated status prose.
- Keep project documentation focused on code, evidence and reproducible procedures.

Commits should describe one coherent change. Pull requests should explain what
changed, how it was tested and whether any scientific claim moved.
