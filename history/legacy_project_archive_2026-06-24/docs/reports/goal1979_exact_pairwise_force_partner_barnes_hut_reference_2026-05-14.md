# Goal1979 Exact Pairwise Force Partner Reference

Date: 2026-05-14

Status: implementation slice with pod timing

## Why This Goal Exists

`barnes_hut_force_app` previously had a fast v2 threshold row for node
coverage. That row is useful, but it does not compute force vectors. The app's
richer user-facing requirement is vector accumulation.

Goal1979 adds a generic partner continuation:

```text
pairwise_inverse_square_force_2d_partner_columns(source_weighted_points,
                                                 target_weighted_points,
                                                 softening=...)
```

It also adds:

```text
weighted_point_rows_to_partner_columns(...)
```

The Barnes-Hut example now exposes `--backend partner_exact_force --partner
torch|cupy`. That mode computes exact all-pairs softened inverse-square force
vectors over generic weighted point columns. It is a semantic reference row for
force-vector accumulation, not a Barnes-Hut tree-opening accelerator.

## Boundary

This goal deliberately keeps the native RTDL engine app-agnostic. The native
engine receives no Barnes-Hut continuation, no force-specific ABI, and no
app-shaped tree primitive.

The claim boundary is:

- exact force-vector partner reference: yes;
- Barnes-Hut hierarchical opening acceleration: no;
- RT-core force-vector speedup claim: no;
- v2.0 release authorization: no.

## Pod Timing

The RTX 2000 Ada pod ran the exact CuPy force path with a validation-on
correctness row and larger skip-validation timing rows:

| Body count | Force rows | CPU Python exact median s | v2 CuPy exact median s | Ratio | Correct |
| ---: | ---: | ---: | ---: | ---: | --- |
| 512 | 512 | 0.103554 | 0.002056 | 0.01986x | row-count parity |
| 2048 | 2048 | not run | 0.006755 | n/a | shape |
| 4096 | 4096 | not run | 0.015608 | n/a | shape |
| 8192 | 8192 | not run | 0.035596 | n/a | shape |

The validation-on row at 256 bodies matched the CPU oracle with max relative
error below `6e-15`. Larger timing rows skip CPU validation so they measure the
partner force kernel rather than a Python oracle.

Artifact:

- `docs/reports/goal1979_pod_exact_pairwise_force_barnes_hut_cupy_perf.json`
