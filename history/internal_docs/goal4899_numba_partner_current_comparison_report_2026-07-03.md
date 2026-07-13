# Goal4899 — Current RayJoin Representative Comparison: AuthorOfficial vs Python+RTDL vs Python+Numba+RTDL

Date: 2026-07-03

## Verdict

`completed_numba_partner_app_continuation_integration__correct_but_not_author_hot_performance`

Goal4899 integrated the existing Numba partner continuation with the current public-primitives Section 5.7 representative harness after Goal4898. It produced a real improvement over the Python-only RTDL app route, while preserving byte-for-byte correctness.

The result is not a broad performance victory over the author implementation. It is a bounded partner win in the application continuation layer.

## Route

The current Numba route is:

```text
public RTDL planar-map LSI primitive
→ public RTDL planar-map point-location/PIP primitive
→ Python application overlay assembly
→ Numba partner kernels for app-layer skip planning / continuation helpers
→ Python streaming output writer
```

Important boundary:

- Numba does not replace RTDL LSI/PIP primitives.
- Numba is not on the RTDL primitive traversal path.
- Numba is on the app-layer continuation/writer path.
- No `rtdsl.rayjoin_overlay` import is used.
- No RTDL core/native semantics were changed for Goal4899.

## Artifacts

- `history/internal_docs/goal4899_numba_prepared_query_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4898_prepared_query_overlay_summary_2026-07-03.json`
- `history/internal_docs/goal4899_author_python_rtdl_numba_rtdl_comparison_2026-07-03.json`

## Correctness

The current Numba+RTDL run is byte-identical to AuthorOfficial on the Australia current-source lakes x parks representative:

```text
byte_equal_to_author: true
sha256: a15e0dd4f3a4ffa6a4f8595a317cb53f31979aed02c78f4de243bb40ef40493e
lines: 276320
bytes: 6189260
```

## Performance Table

| Route | Total wall | Load | Compute+write excluding load | Compute excluding load+write | Write | Correct |
|---|---:|---:|---:|---:|---:|---|
| AuthorOfficial C++/CUDA/OptiX | `145.138s` | `144.262s` | `0.876s` | `0.074s` | `0.802s` | yes |
| Python+RTDL public primitives | `51.317s` | `24.283s` | `27.034s` | `9.932s` | `17.101s` | yes |
| Python+Numba+RTDL public primitives | `39.373s` | `25.437s` | `13.936s` | `11.578s` | `2.358s` | yes |

The AuthorOfficial total includes raw CDB reading. The RTDL totals use the current packed-cache path. Therefore, do not headline total wall-clock ratios as a language-stack speedup. The cleaner comparison is by phase.

## What Numba Improved

Numba improved the application continuation/writer path:

- Python-only writer: `17.101s`
- Numba+RTDL writer: `2.358s`
- writer speedup: `7.25x`

It also improved the non-load route as a whole:

- Python-only compute+write excluding load: `27.034s`
- Numba+RTDL compute+write excluding load: `13.936s`
- speedup: `1.94x`

This is a real partner effect.

## What Numba Did Not Improve

Numba did not close the author hot-compute gap:

- AuthorOfficial compute excluding read/write: about `0.074s`
- Python+Numba+RTDL compute excluding load/write: about `11.578s`
- gap: about `155x`

This is not because Numba "failed." It is because the author implementation fuses more work inside C++/CUDA/OptiX kernels, while the current RTDL app still has multiple materialized, Python-visible stages:

- LSI rows;
- reprojection;
- sorting;
- point-location/PIP rows;
- output-chain assembly.

This confirms the architecture discussion: Numba helps downstream continuation, but the remaining author gap is primarily about traversal/fusion/dataflow placement, not about merely replacing a Python loop.

## Important Interpretation

For a user asking "can Python+Numba+RTDL do what C++/CUDA/OptiX does?":

- Correctness on this representative workload: yes.
- Public RTDL primitives used for LSI/PIP: yes.
- Numba partner use: yes, for app continuation/writer skip planning.
- Performance comparable to author hot compute: no.
- Honest state: correct bounded reproduction with meaningful app-layer partner acceleration, but still far from author fused-kernel hot path.

## Why This Is Still Useful

Goal4899 proves the intended division of labor works:

- RTDL supplies RT-core spatial primitives.
- Numba supplies CUDA-core style app continuation.
- Python coordinates the application.

The system is usable, but the next high-performance version must reduce materialization and push more dataflow into runtime-managed/fused stages. That is a product/runtime R&D goal, not something a user app can fully solve with Numba alone.

## Next Engineering Target

The next serious target should not be another LSI micro-optimization. It should be one of:

1. move more output-chain assembly into Numba without changing RTDL core;
2. create a generic RTDL continuation surface for row-stream to chain/output transformations;
3. begin the measured dataflow pushdown work described in the post-v2.14 high-performance plan.

For the current v2.14 paper-reproduction app, the cleanest immediate next step is option 1: continue moving app-layer writer assembly into Numba while keeping all RTDL primitive semantics unchanged.

## Non-Authorization

This report does not authorize:

- broad RTDL/RayJoin speedup claims;
- full eight-pair Section 5.7 claims;
- claims that Numba accelerates RTDL primitive traversal;
- claims that total wall time beats AuthorOfficial in a fair same-IO comparison;
- V3/V4 release resurrection claims.
