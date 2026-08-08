# Methodology

## Measurement model

The study describes a contour with an edge-spread profile. `p10`, `p50` and
`p90` mark the positions where the transition reaches 10, 50 and 90 percent.
The dark half-width is `p10 → p50`, the bright half-width is `p50 → p90`, and the
total width is `p10 → p90`.

`p50` is treated as an approximation of perceived contour position. A candidate
that broadens an edge but moves `p50`, damages a plateau or creates a halo does
not satisfy the original question.

## Aggregation

Historical real-data measurements were aggregated in three stages:

1. frame-level measurements;
2. episode-level summaries;
3. fold-level decisions across five separated folds.

This prevented one episode with many eligible pixels from dominating the final
result.

## Advancement gates

A candidate could advance only after passing checks for:

- deterministic output and unchanged input arrays;
- expected activation on controlled fixtures;
- midpoint stability and bounded halo;
- protected-region passthrough;
- stable direction across folds;
- a useful visible effect in native review.

Missing evidence or an invalid harness counted as failure, not as an invitation
to infer a favorable result.

## Synthetic versus real evidence

Synthetic fixtures are useful for testing geometry, angle behavior, end caps,
junctions and output contracts. They are deliberately not used to claim
historical visual fidelity. D3 is the clearest example: it passed extensive
synthetic checks and still produced arrays identical to baseline on the fixed
real-data smoke test.

## Oracle study

The Oracle phase supplied human-verified contour polylines to remove uncertainty
about automatic localization. Several render methods produced local, technically
nonzero changes. A frozen native blind review then tested whether those changes
were actually visible. All 50 panels were judged to show no visible difference.
