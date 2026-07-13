# Goals 5482-5483: LibRTS Exact Figure-6 Point-Contains Matrix

Date: 2026-07-11

Status: `externally_reviewed_and_approved__six_of_six_exact_input_count_gates_matched__count_level_only`

## Objective

Extend the first exact LibRTS gate (`dtl_cnty`, Goal5481) to the five remaining
Figure-6 point-contains geometry/query pairs available in the verified PPoPP AE
archive. Keep the comparison at the author contract's exposed output: an exact
integer result count. Do not turn this count matrix into a Figure-6, full-paper,
or performance claim.

## Input provenance

The work uses the official Zenodo v2 archive, verified at:

```text
size = 23,062,425,365 bytes
MD5  = 89e589f086038f1cd3af9e3ed67da8c8
inventory = 1,694 safe members / 88,229,246,574 expanded file bytes
```

The full archive is not expanded into the POD's working quota. Goal5482
selected ten members (five geometry files and five 100,000-query files),
promoted them atomically, and recorded each member path, size, and SHA-256 in
`Paper-reproduction-apps/librts-paper/results/librts_goal5482_point_contains_remaining_subset.json`.
The gate rechecks containment, size, and SHA-256 immediately before execution.

This establishes exact identity for these selected official archive members.
It does not change the project-level `exact_paper_inputs_available=false`
boundary: the complete paper input set and complete paper execution have not
been established merely by selecting these ten members.

## POD evidence

All five cases were run on the same RTX 4000 Ada POD. The exact same extracted
files were passed to the patched author `query` binary and to RTDL OptiX.

| Case | Author count | RTDL count | Match |
|---|---:|---:|---|
| `USACensusBlockGroupBoundaries` | 148,970 | 148,970 | yes |
| `USADetailedWaterBodies` | 118,622 | 118,622 | yes |
| `parks_Europe` | 109,279 | 109,279 | yes |
| `lakes.bz2` | 103,189 | 103,189 | yes |
| `parks.bz2` | 112,729 | 112,729 | yes |

Together with Goal5481's exact `dtl_cnty` result of `136,475`, the current
point-contains matrix is six of six matched on exact official archive members.
This is **count-level agreement only**. Equal counts do not establish that the
same individual query points were assigned to the same polygons. The standard
author query binary does not expose pair rows, so pointwise containment
equivalence cannot be claimed for these six cases.
The aggregate evidence is in:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5482_exact_point_contains_remaining_batch.json
```

## System/API change

Goal5483 adds an app-owned count-only gate using the existing generic public API:

```python
result = rt.query_aabb_index_2d(
    boxes,
    point_queries=points,
    operation="point_contains",
    backend="optix",
)
```

This is a better contract match for the author binary, which exposes a count
but not pair rows. The largest `parks.bz2` case showed why the distinction
matters: materializing a large relation-row buffer was unnecessary for a count
gate and created cleanup pressure. The count-only route completed and matched
without requesting row output. The batch runner now defaults all cases to this
count-only route for future reproduction runs.

This change does not add a LibRTS-specific RTDL primitive. It exercises the
existing generic AABB query API from the app layer. Embree remains outside the
campaign.

Separate relation-level evidence exists for the Goal5467 app-instrumented
representative PIP workload, where all `71,626` author/RTDL pair rows matched
with canonical SHA-256:

```text
Paper-reproduction-apps/librts-paper/results/librts_goal5467_representative_same_input_pip.json
```

That is a different representative PIP workload, not evidence that the six
exact Figure-6 point-contains cases have pair-row equality.

## Tests and verification

The new local contract tests cover:

- verified member resolution and root containment;
- size/SHA-256 tamper rejection;
- the five-case exact member contract;
- count-only use of `query_aabb_index_2d`;
- no call to the row-producing membership API in the count-only gate.

The focused local suite for Goals5482-5483 passed. The corresponding Goal5483
contract test also passed on the POD before the large-input run.

## Claim boundary

Authorized:

- exact archive identity and selected-member identity;
- same-input author/RTDL integer count agreement for six official-input cases;
- explicit count-only boundary: pointwise containment equivalence is not
  claimed for these six cases;
- use of a generic public RTDL count API;
- an app-owned, fail-closed exact-input gate.

Not authorized:

- Figure 6 reproduction or its published timing plot;
- author/RTDL pair-row equality for point-contains;
- any author-vs-RTDL performance ratio;
- whole LibRTS paper reproduction;
- native author algorithm equivalence;
- Embree comparison.

The raw timing evidence also shows that the current RTDL route is far slower
than the author's internal query metric on these cases (seconds of RTDL route
wall versus sub-millisecond author Query Time). Those numbers have different
phase boundaries, so this is a warning about the current route, not an
authorized performance ratio.

## Next step

The next work should inspect the remaining Figure-6 denominator and output
contract before timing anything. Count correctness is now broad enough to
support that audit, but it does not by itself authorize a performance matrix.
