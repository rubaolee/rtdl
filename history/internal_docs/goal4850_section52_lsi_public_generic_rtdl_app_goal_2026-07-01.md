# Goal4850: Section 5.2 LSI As A Public Generic RTDL App

Date: 2026-07-01

## Why This Goal Exists

The previous Section 5.2 work proved RayJoin LSI count matches through RTDL product code, but the strongest user-facing form has not been closed:

> Can an ordinary RTDL user reproduce the Section 5.2 LSI workload using public generic RTDL primitives, without calling the bundled `rayjoin_overlay` helper?

For full Section 5.7 polygon overlay, the answer is still more complicated because it needs point-location, midpoint classification, topology assembly, and output-chain formatting. For Section 5.2 LSI count, the required computation is narrower and should be expressible with existing generic prepared segment-pair primitives.

## Boundary

Allowed:

- Use public CDB loading/data helpers.
- Use generic prepared segment-pair OptiX primitives from `rtdsl.optix_runtime`.
- Use Python as the application layer.
- Use Numba only if it is naturally needed for user-side continuation or validation.

Forbidden:

- Do not call `rtdsl.rayjoin_overlay`.
- Do not call underscored bundled helpers such as `_run_lsi_rows`.
- Do not modify `src/rtdsl/**`, `src/native/**`, docs, tutorials, examples, or release surface.
- Do not claim full Section 5.7 polygon overlay reproduction.
- Do not claim all eight exact Section 5.2 paper pairs unless all exact inputs are available.

## Correct Route

For an AuthorPatch command:

```text
query_exec -poly1 A.cdb -poly2 B.cdb -query=lsi
```

the RTDL public-generic route must use the same effective direction observed in Goal4848:

```text
base/right index = A
query/left set   = B
```

Implementation shape:

```python
from rtdsl import chains_to_rayjoin_cdb_segments, load_cdb
from rtdsl.optix_runtime import (
    prepare_segment_pair_intersection_optix,
    prepare_segment_pair_left_set_optix,
)

base = load_cdb(poly1)
query = load_cdb(poly2)
base_segments = chains_to_rayjoin_cdb_segments(base)
query_segments = chains_to_rayjoin_cdb_segments(query)

with prepare_segment_pair_intersection_optix(base_segments) as base_index:
    with prepare_segment_pair_left_set_optix(query_segments) as query_left:
        result = base_index.count_prepared_left_exact_intersections(query_left)
```

## Datasets To Run

Use already validated AuthorPatch counts:

| Dataset | Label | AuthorPatch Count | Claim Level |
|---|---:|---:|---|
| County x Zipcode | available original/same-source CDB | 961165 | Section 5.2 bounded pair |
| Block x Water | available original/same-source CDB | 649605 | Section 5.2 bounded pair |
| Australia Lakes x Parks | current OSM Geofabrik representative CDB | 13622 | representative, not exact paper pair |

## Exit Criteria

Goal4850 passes only if:

1. The script imports no `rtdsl.rayjoin_overlay` module.
2. The script uses public CDB helpers plus `prepare_segment_pair_intersection_optix` and `prepare_segment_pair_left_set_optix`.
3. All available tested pairs match the expected AuthorPatch counts.
4. The report records the import list, counts, runtime timings, and claim boundaries.

## Exit Labels

- `pass_section52_lsi_public_generic_rtdl_app`: all tested pairs match through the public-generic primitive route.
- `blocked_by_public_api_gap`: the primitive exists but cannot be used cleanly by an ordinary user without private helper imports.
- `blocked_by_correctness_gap`: the public-generic route runs but does not match AuthorPatch counts.
- `blocked_by_environment_or_input_gap`: the route cannot be run because required data/environment is unavailable.

## Expected Outcome

The expected outcome is `pass_section52_lsi_public_generic_rtdl_app` for Section 5.2 LSI count. If this passes, the earlier bundled-helper result remains useful as a regression oracle, but the clean Section 5.2 user implementation becomes the primary evidence.
