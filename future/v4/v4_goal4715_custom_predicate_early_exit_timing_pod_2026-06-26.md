# V4 Goal4715 Custom Predicate Early-Exit Timing POD Result

Date: 2026-06-26

Status: `complete_pending_3ai_review_debt`

Decision: `pass_focused_timing_gate_not_release`

## Goal

Run the first real timing gate for the Goal4713/4714 target:

`ray_triangle_custom_predicate_early_exit_multi_hit`

The question was simple: does the Goal4714 invocation reduction become real
wall/hot-path speedup when compared against a fair V2/V3-style fallback?

## Evidence

- JSON:
  `future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.json`
- Markdown:
  `future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_pod_2026-06-26.md`
- Source:
  `src/rtdsl/v4_goal4715_custom_predicate_early_exit_timing_result.py`
- Script:
  `scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py`
- Tests:
  `tests/v4_goal4715_custom_predicate_early_exit_timing_result_test.py`

POD:

- Host: `root@194.68.245.170 -p 22089`
- GPU: NVIDIA RTX A5000, driver `570.195.03`
- Workspace: `/root/rtdl_v4_candidate_pod`
- Python: `/usr/bin/python3`

## Result

Classification:

`pass_focused_timing_gate_not_release`

Summary:

- primary V4/V3 geomean: `3.608025018751732x`
- primary V4/V2 geomean: `3.608025018751732x`
- minimum primary V4/V3 row: `1.9761904761904763x`
- control geomean V4/V3: `1.5585401086027044x`
- correctness: passed for all rows
- denominator discovery: completed before V4 timing
- early termination: passed for all primary rows

Primary rows:

| scale | regime | V4 s | fallback s | fallback/V4 | V4 invocations | fallback invocations |
|---:|---|---:|---:|---:|---:|---:|
| 65536 | `dense_early_accept_k8` | 0.000092736 | 0.000183264 | 1.976x | 65536 | 524288 |
| 65536 | `dense_early_accept_k32` | 0.000115008 | 0.000770688 | 6.701x | 65536 | 2097152 |
| 65536 | `sparse_early_accept_k32` | 0.000065312 | 0.000180864 | 2.769x | 16384 | 524288 |
| 131072 | `dense_early_accept_k8` | 0.000161696 | 0.000321280 | 1.987x | 131072 | 1048576 |
| 131072 | `dense_early_accept_k32` | 0.000182432 | 0.001483330 | 8.131x | 131072 | 4194304 |
| 131072 | `sparse_early_accept_k32` | 0.000086816 | 0.000323264 | 3.724x | 32768 | 1048576 |

Control rows:

| scale | regime | V4 s | fallback s | fallback/V4 | V4 invocations | fallback invocations |
|---:|---|---:|---:|---:|---:|---:|
| 65536 | `dense_late_accept_k32` | 0.000426336 | 0.000765920 | 1.797x | 2097152 | 2097152 |
| 65536 | `dense_reject_all_k32` | 0.000387008 | 0.000724128 | 1.871x | 2097152 | 2097152 |
| 65536 | `no_hit_empty` | 0.000040768 | 0.000044288 | 1.086x | 0 | 0 |
| 131072 | `dense_late_accept_k32` | 0.000782752 | 0.001473540 | 1.883x | 4194304 | 4194304 |
| 131072 | `dense_reject_all_k32` | 0.000708992 | 0.001388540 | 1.958x | 4194304 | 4194304 |
| 131072 | `no_hit_empty` | 0.000057024 | 0.000060704 | 1.065x | 0 | 0 |

## Denominator Boundary

V2.14 and V3.0.2 denominator discovery found no custom predicate any-hit
early-exit route in the tag roots. The selected denominator is:

`materialized_all_hit_ids_plus_device_predicate_reduce_fallback`

That fallback traces the same OptiX geometry, writes all hit layers to device
memory, then evaluates the predicate and reduces accepted flags in separate
device kernels. It does not get V4's any-hit predicate early termination.

This is a strong focused denominator for this new capability, but it is not yet
an app-level V4 release result.

## Interpretation

This is the first strong positive result after the Goal4711 failure. Goal4711
showed that post-hit custom scoring only produced about `1.029x` primary
geomean, because it did not change traversal or materialization cost.

Goal4715 changes the cost model. For early-accept regimes, V4 makes the
predicate decision in any-hit and terminates the ray, while the fallback must
materialize all candidate hit layers and filter later. The timing result shows
that the reduced candidate work does become real speedup.

## Validation

Local:

```text
py -m py_compile src/rtdsl/v4_goal4715_custom_predicate_early_exit_timing_result.py scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py src/rtdsl/v4.py
py scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py --dry-run --json-out future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_dry_run_2026-06-26.json --md-out future/v4/evidence/v4_goal4715_custom_predicate_early_exit_timing_dry_run_2026-06-26.md
py -m unittest tests.v4_goal4715_custom_predicate_early_exit_timing_result_test tests.v4_goal4714_custom_predicate_early_exit_smoke_result_test tests.v4_goal4713_custom_predicate_early_exit_protocol_test
```

Remote:

```text
/usr/bin/python3 -m py_compile src/rtdsl/v4_goal4715_custom_predicate_early_exit_timing_result.py scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py src/rtdsl/v4.py
/usr/bin/python3 scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py --dry-run
/usr/bin/python3 -m unittest tests.v4_goal4715_custom_predicate_early_exit_timing_result_test
/usr/bin/python3 scripts/v4_goal4715_custom_predicate_early_exit_timing_pod.py --json-out /root/v4_goal4715_timing_20260626.json --md-out /root/v4_goal4715_timing_20260626.md
```

Observed:

- local focused tests: `8 tests OK` for Goal4715/4714/4713 pair
- remote Goal4715 tests: `4 tests OK`
- remote POD timing: completed with status
  `goal4715_custom_predicate_early_exit_timing_measured_not_release`

## Non-Authorization

Goal4715 does not authorize:

- V4 release;
- formal high-performance V4 wording;
- whole-app speedup wording;
- all-app benchmark claims;
- public Tier-3 support;
- arbitrary callback support;
- raw OptiX callback support.

The only authorized next step is to productize this route as a measured V4
surface and broaden validation under an app-level protocol.

## Goal-Level Decision Audit

1. Was I being stupid?

No. The goal directly measured the decisive question rather than treating the
Goal4714 smoke as a speed result.

2. If yes, what actions made the decision stupid?

Not applicable.

3. Is there another path that avoids getting stuck on a bad premise?

Yes. If the timing result had failed, the correct path would be to stop this
target as high-performance evidence and reselect a runtime lever. Because it
passed, productizing and broadening this route is justified.

4. Can I now try the different path that actually solves the problem?

Yes. The next path is not wording or release polishing. It is route
productization plus app-level validation of this traversal-affecting predicate
early-exit capability.
