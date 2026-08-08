# Visual results

All visuals on this page are generated from an original geometric fixture.
They demonstrate package behavior and failure modes without including protected
media.

## Candidate comparison

![Input, Candidate B, Candidate D3 and Oracle output](assets/generated/candidate-comparison.png)

At native scale the outputs are intentionally difficult to distinguish. That is
the point of the result: a technically valid render path can still be too close
to identity to justify production use.

## Oracle delta

![Oracle output and amplified delta](assets/generated/oracle-delta.png)

The right panel amplifies the absolute RGB delta by 32×. The amplified view shows
that the renderer changed pixels, while the native output on the left explains
why the blind review still returned “no visible difference.”

## Regeneration

```bash
make synthetic-demo
```

The command recreates the comparison, amplified delta, candidate fixtures,
synthetic A/C failure cases and the GitHub social-preview image.
