# RayJoin Section 5.7 V4+Numba Auto-Primitive Planner

Schema: `rtdl.v4.rayjoin.section57_numba_auto_primitive_planner.v1`
Claim classification: `blocked_missing_inputs`
Dataset root: `data\rayjoin_section57_cdb`

## User Semantics

| Field | Value |
|---|---|
| `workload` | `rayjoin_section57_polygon_overlay` |
| `partner` | `numba` |
| `select` | `fastest_valid` |
| `primitive_names_required_from_user` | `False` |

## Candidate Scoreboard

| Pair | Plan | Status | Skip Reason | Correctness | Numba JIT | Boundary |
|---|---|---|---|---|---:|---|
| LKAU x PKAU | `v4_numba_post_traversal_mask_compact` | `skipped_missing_inputs` | Section 5.7 exact or same-source CDB inputs are missing. | `not_run` | True | post-traversal only |
| LKAU x PKAU | `v4_numba_post_traversal_segmented_counts` | `skipped_missing_inputs` | Section 5.7 exact or same-source CDB inputs are missing. | `not_run` | True | post-traversal only |

## Author / V2.14 / V4 Columns

| Pair | Author Code | V2.14 Exact Suite | V4+Numba Candidates |
|---|---|---|---:|
| LKAU x PKAU | `blocked_missing_author_baseline` | `blocked_missing_inputs` | 2 |

## Boundaries

- Primitive names are not required from the user.
- Numba partner work must use `numba.cuda.jit` on device-resident arrays.
- Numba stays outside the OptiX traversal loop in V4.0.
- Full paper reproduction requires author-code correctness and timing.
