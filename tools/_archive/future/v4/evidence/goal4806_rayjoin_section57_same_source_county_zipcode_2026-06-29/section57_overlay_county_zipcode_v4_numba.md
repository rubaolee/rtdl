# RayJoin Section 5.7 V4+Numba Auto-Primitive Planner

Schema: `rtdl.v4.rayjoin.section57_numba_auto_primitive_planner.v1`
Claim classification: `candidate_stage_measured_no_app_speedup_claim`
Dataset root: `/workspace/rayjoin_section57_same_source_cdb`

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
| County x Zipcode | `v4_numba_post_traversal_mask_compact` | `ready_for_measurement` |  | `not_run` | True | post-traversal only |
| County x Zipcode | `v4_numba_post_traversal_segmented_counts` | `measured` |  | `pass` | True | post-traversal only |

## Measurement Import

| Field | Value |
|---|---|
| Provided | `True` |
| Accepted rows | `1` |
| Rejected rows | `1` |

## Author / V2.14 / V4 Columns

| Pair | Author Code | V2.14 Exact Suite | V4+Numba Candidates |
|---|---|---|---:|
| County x Zipcode | `ready` | `ready` | 2 |

## Boundaries

- Primitive names are not required from the user.
- Numba partner work must use `numba.cuda.jit` on device-resident arrays.
- Numba stays outside the OptiX traversal loop in V4.0.
- Full paper reproduction requires author-code correctness and timing.
