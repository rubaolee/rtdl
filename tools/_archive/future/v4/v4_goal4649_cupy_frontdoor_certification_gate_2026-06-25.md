# V4 Goal4649: CuPy Front-Door Certification Gate

Date: 2026-06-25
Status: candidate completion record, pending 3-AI completion review
Previous goal:
`future/v4/reviews/goal4648_completion_consensus_2026-06-25.md`
Code:
`src/rtdsl/v4_cupy_certification.py`
Gate script:
`scripts/v4_goal4649_cupy_grouped_reduction_certification_gate.py`
POD evidence:
`future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json`

## Purpose

Goal4649 certifies the first CuPy V4 partner front-door surface under the
Goal4648 numeric contract.

This is deliberately narrow:

```text
Certified now: CuPy grouped_vector_sum_f64x2 front-door gate for two grouped
reduction sizes.

Not certified now: all CuPy, all apps, Hausdorff CuPy, hitcount CuPy, RT-core
Tier-2 CuPy, true zero-copy, or whole-application speedup.
```

## Target Selection

The Goal4649 target matrix is code-visible in:

```text
src/rtdsl/v4_cupy_certification.py
```

Ready-for-POD targets:

| Candidate | Operator | Rows | Groups | Repeat | Frozen speed floor |
|---|---|---:|---:|---:|---:|
| `cupy_grouped_reduction_device_columns_262144` | `grouped_vector_sum_f64x2` | 262144 | 1024 | 100 | `>=1.20x` |
| `cupy_grouped_reduction_device_columns_524288` | `grouped_vector_sum_f64x2` | 524288 | 2048 | 100 | `>=1.20x` |

Mapping debt, not certified:

| Candidate | Status |
|---|---|
| `cupy_segment_polygon_hitcount_prepared_scaling` | `requires_v4_adapter_mapping_before_pod` |
| `cupy_hausdorff_witness_continuation` | `requires_v4_adapter_mapping_before_pod` |

This separation prevents a narrow grouped-reduction pass from being inflated
into broad CuPy support.

## POD Environment

POD command target:

```text
root@194.68.245.170 -p 22089
key: id_ed25519_rtdl_codex_current_pod
```

Environment recorded in evidence:

| Field | Value |
|---|---|
| GPU | NVIDIA RTX A5000 |
| Driver | 570.195.03 |
| Python | 3.12.3 |
| CuPy | 14.1.1 |
| CUDA runtime | 12090 |

CuPy was installed into a venv on the POD:

```text
/root/rtdl_v4_venv
```

## POD Result

Final live evidence:

```text
future/v4/evidence/v4_goal4649_cupy_grouped_reduction_gate_2026-06-25/pod_live_summary.json
```

Summary:

```text
status: goal4649_cupy_gate_passed_pending_review
ready_target_count: 2
live_rows_passed: 2
live_rows_failed: 0
all_correctness_parity: true
all_no_hot_host_materialization: true
min_representative_speedup: 1716.8217704918034
cupy_performance_claim_authorized: false
```

Rows:

| Candidate | Rows | Groups | Median CuPy hot replay | CPU row-loop denominator | Ratio | Correct | Hot host materialization | Pass |
|---|---:|---:|---:|---:|---:|---|---|---|
| `cupy_grouped_reduction_device_columns_262144` | 262144 | 1024 | `2.840534e-05s` | `0.048767s` | `1716.822x` | true | false | true |
| `cupy_grouped_reduction_device_columns_524288` | 524288 | 2048 | `4.093163e-05s` | `0.097864s` | `2390.916x` | true | false | true |

The denominator is a same-contract Python CPU row loop over every input row.
It is intentionally not public speedup wording; it is a certification gate
floor check against the pre-frozen `>=1.20x` requirement.

## Local Verification

Commands:

```text
py -m unittest tests.v4_goal4649_cupy_certification_gate_test
py -m unittest tests.v4_goal4649_cupy_certification_pod_evidence_test
py -m unittest tests.v4_goal4648_partner_promotion_contract_test
```

Observed:

```text
10 Goal4648/4649 setup tests OK
Goal4649 dry-run OK
POD live JSON parsed successfully
```

## Catalog Status

This goal creates a certification gate and evidence for the CuPy
`grouped_vector_sum_f64x2` partner front door. It does not automatically add
CuPy to the public V4 measured Tier-2 operator catalog before completion review.

If external review accepts this goal, Goal4651 may promote the exact certified
surface into the appropriate partner catalog row with this scope:

```text
partner: cupy
surface: grouped_vector_sum_f64x2
claim class: certified partner front-door surface
not claim class: broad V4 speedup, all CuPy, all apps, RT-core Tier-2 win
```

## Non-Authorization

Goal4649 does not authorize:

- public V4 release/tag wording;
- broad V4 speedup claims;
- whole-app or all-benchmark V4 speedup claims;
- blanket CuPy support;
- CuPy RT-core Tier-2 claims;
- Hausdorff CuPy claims;
- hitcount CuPy claims;
- arbitrary Numba callback claims;
- C ABI / embedding claims;
- true-zero-copy claims;
- partner migration or partner parity as V4 speed evidence.

## Goal-Level Decision Audit

1. Did I make a foolish decision?

Partly, and it was corrected before review. The first live gate used a
misleading "CPU formula" denominator that looped over groups rather than every
input row.

2. If yes, what actions made it foolish?

I let a convenient synthetic denominator stand in for a same-contract row loop.
That would have made the result hard to audit and vulnerable to overclaiming.

3. Was there another possibility that avoided being trapped in one idea?

Yes. Use a real CPU row-loop denominator over all rows, even though it makes the
ratio larger and requires explicitly saying it is only a certification floor
check, not public performance wording.

4. Can I start a different path that actually solves the problem?

Yes. The corrected final POD run uses full row-loop denominators, records
environment metadata, and keeps all public claims blocked pending review.

## Exit Status

Goal4649 has enough local and POD evidence for completion review:

- two ready CuPy grouped-reduction candidates passed;
- correctness parity passed with zero error;
- hot-path host materialization remained false;
- frozen `>=1.20x` speed floor cleared;
- mapping debt for Hausdorff/hitcount remains explicit;
- no public claim or catalog promotion is authorized before review.
