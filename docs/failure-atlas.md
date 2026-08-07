# Failure atlas

The candidate lineages failed in different ways. Keeping those categories
separate avoids treating every negative result as “the effect was too weak.”

| Failure class | Example | What it means |
|---|---|---|
| Self-blocking activation | A | The eligibility logic removes the region the operator needs before a valid test can occur |
| Incomplete or wrong direction | B | One measured half moves acceptably while other required widths move the wrong way |
| Halo and angular bias | C | Raster behavior depends on orientation or introduces energy outside the intended contour |
| Invalid measurement harness | C | The harness reports requested parameters instead of independently measuring output pixels |
| Synthetic-to-real activation gap | D3 | Controlled fixtures pass, but the operator produces identity on the real-data smoke test |
| Measurable but visually irrelevant change | Oracle | Pixel deltas are nonzero, yet native blind review cannot see a useful difference |

These classes imply different next steps. A self-blocking mask needs a new
eligibility model; halo needs a different renderer; exact real-data inactivity
needs distribution-aware activation; an invisible Oracle result questions the
perceptual target itself.
