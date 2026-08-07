# Decision log

This page records the main technical decisions behind the current package.

## Isolate ink profiles

S1 was separated from color, grain, halation and temporal effects so another
stage could not make an ineffective contour operator appear successful.

## Aggregate by frame, episode and fold

The evaluation moved from frame to episode to fold rather than pooling all
eligible pixels. This reduced the chance that a long or highly eligible episode
would dominate the conclusion.

## Reject invalid evidence rather than repair the conclusion

A self-blocking candidate, an invalid raster-measurement harness or missing
provenance stopped the branch. Infrastructure changes could deny a claim but did
not promote a candidate by themselves.

## Use a manual Oracle

After automatic geometry and semantic routes failed, human-verified contour
segments were used to test whether localization was the remaining bottleneck.
The renderer changed pixels, but native blind review still found no visible
utility.

## Keep production behavior at identity

With no Full PASS and no useful Oracle rescue, S1 was closed as
`PROVISIONAL_NO_OP`. Reopening requires a materially new representation,
supervision source or perceptual target.
