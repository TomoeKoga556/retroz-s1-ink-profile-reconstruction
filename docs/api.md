# API and CLI

## Console entry point

The package installs `retroz-s1`. The module form is equivalent:

```bash
retroz-s1 list-candidates
python -m retroz_s1 list-candidates
```

## Candidate inspection

```bash
retroz-s1 inspect --candidate D3
```

The command prints the registry entry, including status, known failure,
capabilities and provenance hashes.

## Rendering B or D3

```bash
retroz-s1 render \
  --candidate D3 \
  --input input.png \
  --output output.png \
  --allow-rejected-research-candidate
```

A provenance sidecar is written as `output.png.provenance.json`.

## Comparison panel

```bash
retroz-s1 compare \
  --input input.png \
  --candidates B,D3 \
  --output comparison \
  --allow-rejected-research-candidate
```

## Synthetic failure reproduction

```bash
retroz-s1 reproduce-failure \
  --candidate C \
  --output failure_c \
  --allow-rejected-research-candidate
```

Only A and C support this path.

## Oracle rendering

```bash
retroz-s1 oracle-render \
  --input input.png \
  --labels labels.json \
  --method P1 \
  --tier R0 \
  --output oracle.png \
  --allow-rejected-research-candidate
```

The label file must contain a non-empty `segments` list. Inputs and labels remain
local; the package performs no network access.
