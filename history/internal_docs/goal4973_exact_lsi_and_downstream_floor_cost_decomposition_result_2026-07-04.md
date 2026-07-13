# Goal4973 Result — Exact LSI And Downstream Floor Cost Decomposition

Date: 2026-07-04

## Verdict

`completed_exact_lsi_setup_decomposed__steady_state_downstream_floor_confirmed`

Exit labels:

- `exact_lsi_cost_dominated_by_workspace_setup`
- `steady_state_cost_dominated_by_downstream_floor`

Goal4973 did not implement a new optimization. It added measurement instrumentation and ran the top4 County x Zipcode representative to separate:

1. the fresh exact LSI producer cost, and
2. the persistent writer-free downstream floor.

The result is clear: fresh exact LSI is not slow because Python is hiding unmeasured work. It is slow because the first run builds native prepared state: scaled segment caches, grouped-range acceleration, exact pipeline, and split kernel. Once those are warm, bounded exact LSI replay is about `0.003s`. The remaining steady-state operator cost is downstream, around `2.54s`.

## Code Changes

Instrumentation only:

- Added optional native extended timing getter:
  - `rtdl_optix_segment_pair_intersection_get_last_extended_phase_timings`
  - fields: total native, scaled-cache ensure, grouped-range ensure, exact-pipeline ensure, split-kernel ensure, device allocation, parameter upload, OptiX launch, count download, split launch.
- Added Python runtime access:
  - `get_last_segment_pair_extended_phase_timings`
  - `PreparedOptixSegmentPairIntersection.last_extended_phase_timings`
  - legacy `last_phase_timings()` now includes an `extended` object when supported.
- Added app-level Goal4973 reporting:
  - `lsi_cost_decomposition`
  - `downstream_floor_breakdown`
  - `--bounded-exact-lsi-repeat-diagnostic`

No RayJoin output-chain logic was added to core. Core output remains generic `{left_id, right_id}` pair-id columns.

## POD Validation

POD:

```text
root@213.173.108.6 -p 10626
workspace: /root/rtdl_goal4971
```

Build:

```text
make build-optix OPTIX_PREFIX=/root/vendor/optix77-doc-headers CUDA_PREFIX=/usr/local/cuda OPTIX_CUDA_ARCH=sm_89
```

Result:

```text
build/librtdl_optix.so rebuilt successfully
```

Local structural tests:

```text
py -m unittest tests.goal4973_exact_lsi_cost_decomposition_test tests.goal4972_bounded_exact_lsi_producer_test tests.goal4964_exact_lsi_pair_id_device_columns_test
Ran 10 tests: OK
```

POD note: the remote copy is not a git worktree and has an older partial test set, so only the current Goal4973 structural test was meaningful there. The OptiX backend rebuild and runtime measurements are the decisive POD checks.

## Artifacts

Local artifact directory:

```text
history/internal_docs/goal4973_exact_lsi_and_downstream_floor_cost_decomposition_artifacts_2026-07-04/
```

Important files:

- `goal4973_cost_decomposition_gate/bounded_exact_repeat_summary.json`
- `goal4973_cost_decomposition_gate/prepared_replay_summary.json`
- `goal4973_cost_decomposition_gate/exact_device_columns_summary.json`
- `goal4973_cost_decomposition_gate/goal4973_extracted_summary.json`

## Correctness Gates

All three Goal4973 routes reported the same correctness anchors on the top4 representative:

| Gate | Value |
|---|---:|
| LSI rows | `428322` |
| xsect side0 | `428322` |
| xsect side1 | `428322` |
| vertex positives side0 in side1 | `812721` |
| vertex positives side1 in side0 | `4527305` |

Device order validation passed for routes run with `--validate-device-order`.

## Fresh Exact LSI Decomposition

### Bounded exact device columns

| Metric | Seconds |
|---|---:|
| Python LSI phase | `2.670249007642269` |
| Native total | `2.669812632` |
| Python wrapper / unaccounted | `0.0004363756422689491` |
| copy device columns to NumPy | `0.003527916967868805` |

Native extended breakdown:

| Native subphase | Seconds |
|---|---:|
| scaled cache ensure | `0.687531634` |
| grouped range ensure | `1.012860557` |
| exact pipeline ensure | `0.523575707` |
| split kernel ensure | `0.442062948` |
| device allocation | `0.001437764` |
| OptiX launch | `0.00226502` |
| count download | `0.00001931` |
| split kernel launch | `0.000019321` |
| total native | `2.669812632` |

Interpretation: bounded fresh LSI is setup-bound, not traversal-bound and not Python-bound.

### Exact device columns

| Metric | Seconds |
|---|---:|
| Python LSI phase | `2.6439320519566536` |
| Native total | `2.643482594` |
| Python wrapper / unaccounted | `0.00044945795665363164` |
| copy device columns to NumPy | `0.003561839461326599` |

Native extended breakdown:

| Native subphase | Seconds |
|---|---:|
| scaled cache ensure | `0.690948824` |
| grouped range ensure | `1.017851884` |
| exact pipeline ensure | `0.514101952` |
| split kernel ensure | `0.414131715` |
| device allocation | `0.001826547` |
| OptiX launch | `0.004503758` |
| count download | `0.000037191` |
| split kernel launch | `0.000020741` |
| total native | `2.643482594` |

Interpretation: exact and bounded agree on the same cost shape.

## Same-Process Repeat Diagnostic

Route: same process, same prepared query, bounded exact device columns, no NumPy copy.

| Run | Elapsed seconds | Native total | Main setup cost |
|---:|---:|---:|---|
| 0 | `1.7946365624666214` | `1.794330763` | scaled cache `0.742017811`, grouped range `1.048912497` |
| 1 | `0.0029818639159202576` | `0.002779356` | setup near zero |
| 2 | `0.002968832850456238` | `0.002779575` | setup near zero |

Interpretation: after the prepared state is built, bounded exact LSI itself is about `0.003s` on this input. The first-run cost is amortizable prepared-state construction.

## Downstream Floor

Prepared replay route:

| Metric | Seconds |
|---|---:|
| writer-free hot total | `2.5446515902876854` |
| LSI replay phase | `0.008617423474788666` |
| native LSI total | `0.002219028` |
| downstream floor | `2.5360341668128967` |

Largest downstream components:

| Component | Seconds |
|---|---:|
| vertex PIP map1 in map0 | `0.7538340985774994` |
| midpoint points map0 | `0.5869109332561493` |
| midpoint points map1 | `0.5812239274382591` |
| intersection reprojection | `0.23000755906105042` |
| vertex PIP map0 in map1 | `0.12450332939624786` |
| compiled carrier construction | `0.10773426294326782` |
| sort map1 | `0.0897260531783104` |
| sort map0 | `0.031683750450611115` |

Interpretation: after LSI is warm, the persistent cost is downstream, not LSI. The largest steady-state targets are:

1. vertex PIP map1 in map0,
2. midpoint point generation on both sides,
3. reprojection,
4. carrier construction / sort as secondary targets.

## Decision

Goal4973 answers the midcheck review:

- The `~2.686s` missing LSI time is native setup / workspace construction, not hidden Python.
- Same-process prepared replay proves the LSI producer itself becomes `~0.003s`.
- The persistent writer-free binary operator floor is `~2.54s`, dominated by downstream work.

Therefore the next performance goal should not spend more effort on LSI traversal unless the product objective is cold one-shot latency. For the steady-state binary operator objective, the next goal should target the largest downstream floor while preserving generic RTDL boundaries:

- point-location/PIP device-column handoff and resident results,
- midpoint point generation as generic device column map,
- reprojection/sort/carrier only after the above are measured in the same downstream-floor table.

## Not Authorized

This result does not authorize:

- any new public performance headline,
- any claim that RTDL is close to the author overlay compute,
- any Layer 4 traversal fusion claim,
- any RayJoin-specific core primitive,
- any public release wording change.
