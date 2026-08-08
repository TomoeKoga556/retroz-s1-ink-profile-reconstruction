# Project overview

## The narrow problem

S1 isolates line-edge reconstruction from the rest of a retro-animation look.
It does not add grain, color drift, halation, scan texture or temporal cadence.
That separation matters because a pleasant global grade can hide a failed line
operator.

The working hypothesis was that selected modern digital contours could be moved
toward broader, more asymmetric edge profiles with a local transform. The
operator had to preserve the contour midpoint, color plateaus, junctions,
backgrounds and explicitly protected regions.

## What counted as success

A candidate needed all three kinds of evidence:

- **activation:** the operator must actually affect eligible pixels;
- **technical safety:** no unacceptable contour shift, halo, clipping or protected-region change;
- **visible utility:** the native output must show a useful effect, not merely a nonzero delta.

A numerical change without visible value was not accepted as a production win.
Likewise, success on procedural shapes was treated as software evidence, not as
proof of real-image usefulness.

## Final decision

A, B, C and D3 failed for different reasons. The final Oracle study removed
localization uncertainty by using human-labelled contour segments, but its
native blind panels still produced 50 out of 50 “no visible difference”
judgements. That result closed the tested renderer family and left S1 in
identity/bypass.

The project remains useful because it preserves the evaluation protocol,
provenance system, public-safe reproductions and the reasons each branch was
closed.
