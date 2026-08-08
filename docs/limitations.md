# Limitations

The conclusion is bounded in several ways.

## Data

Historical real-data experiments used source material that cannot be distributed
in this repository. Public users can reproduce the package and synthetic
experiments, but not the exact private frame set.

## Metrics

Edge-spread widths and midpoint stability capture only part of contour
perception. They do not directly measure line authorship, semantic importance,
temporal consistency or style preference.

## Architecture

The evaluated candidates are local, deterministic raster operators. The result
does not cover learned redraw systems, vector reconstruction, temporal models or
materially different spatial objectives.

## Masks

Public B and D3 demonstrations use documented approximations rather than the
private historical M0 masks. Their purpose is to expose the operator safely, not
to recreate exact historical runs.

## Human review

The Oracle blind review was decisive for the tested outputs, but it remains a
bounded review protocol. A different target, display condition or renderer could
produce a different outcome.
