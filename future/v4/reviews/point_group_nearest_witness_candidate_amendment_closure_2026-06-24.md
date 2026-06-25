# Point-Group Nearest-Witness Candidate Amendment Closure

Date: 2026-06-24
Status: A1/A2/A3 closed; candidate still requires external closure review before any promotion decision

Source review:

- `future/v4/reviews/claude_v4_point_group_nearest_witness_candidate_review_2026-06-24.raw.md`

Verdict:

- `accept_with_required_amendments_before_catalog_decision`

## Closed Amendments

### A1: true-zero-copy sub-field naming

Closed in code:

- `src/rtdsl/optix_runtime.py`

Point-group candidate metadata no longer emits public-claim-shaped fields named
`query_point_columns_true_zero_copy_authorized` or
`output_columns_true_zero_copy_authorized` on the candidate path. It now uses
direct-device handoff fields:

- `query_point_columns_direct_device_read_confirmed`
- `output_columns_direct_device_write_confirmed`

The authoritative public boundary remains:

- `true_zero_copy_authorized: false`

Validation:

- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_catalog_regression_gate_gpu_32768_include_candidates_point_group_2026-06-24.json`

### A2: candidate partner classification

Closed in code:

- `src/rtdsl/v4_point_group.py`
- `src/rtdsl/v4_ray_triangle.py`
- `src/rtdsl/v4_operator_catalog.py`

Candidate metadata now records Torch separately as a POD candidate partner:

- `pod_candidate_partners: ["torch"]`

CuPy remains declared but unmeasured:

- `partner_support_declared_unmeasured: ["cupy"]`

This also closes the same ambiguity for the grouped-i64 candidate.

### A3: non-trivial correctness fixture

Closed in code and evidence:

- `scripts/v4_point_group_nearest_witness_device_outputs_validation.py`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.json`
- `future/v4/evidence/v4_point_group_nearest_witness_device_outputs_pod_gate_32768_131072_2026-06-24.md`

The POD repeat gate now uses a mixed fixture with equal counts of:

- no in-radius neighbor
- nonzero nearest distances
- exact matches

No-hit rows are checked against neighbor id `0xFFFFFFFF` and float32 max
distance. Both checked sizes passed parity:

| queries | direct device-output median | legacy host-row median | ratio | parity |
|---:|---:|---:|---:|---|
| 32,768 | 0.000529401s | 0.351068474s | 663.143x | true |
| 131,072 | 0.000506975s | 0.947073404s | 1868.088x | true |

## Non-Authorization

This closure record does not authorize V4 release, measured catalog promotion,
broad speedup wording, whole-application speedup wording, true-zero-copy public
wording, CuPy performance claims, Tier-3 callback/PTX support, embedding/C-ABI,
non-Python host bindings, or app-specific native kernels.
