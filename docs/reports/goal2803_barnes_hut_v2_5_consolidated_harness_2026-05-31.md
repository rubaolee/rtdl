# Goal2803 Barnes-Hut v2.5 Consolidated Harness

Date: 2026-05-31

Status: implemented and clean-from-Git pod validated.

Verdict: accept-with-boundary.

## Purpose

Goal2803 replaces the `barnes_hut` manifest row's "needs consolidated harness" status with one canonical v2.5 harness.

The harness records two current, generic halves of the Barnes-Hut benchmark lane:

- Embree versus OptiX expanded-membership aggregate-frontier lowering, proving the RT-assisted membership subpath still matches the same contract;
- Torch versus Triton grouped vector-sum partner continuation, proving the vector reduction path remains generic while keeping Triton auto-selection blocked unless it beats the same-contract Torch/CuPy opponent.

This is not a paper-reproduction claim and not a public speedup claim. Barnes-Hut tree policy, opening semantics, and force interpretation remain app-owned Python or partner code; the native engine sees only generic membership/frontier/vector-sum contracts.

## Files

| File | Purpose |
| --- | --- |
| `scripts/goal2803_barnes_hut_v25_consolidated_harness.py` | Canonical v2.5 Barnes-Hut consolidated harness with progress logging, default three-case execution, three repeats, two vector warmups, and explicit validation policy metadata. |
| `tests/goal2803_barnes_hut_v25_consolidated_harness_test.py` | Focused regression test for the harness, manifest row, pod artifact, and boundary wording. |
| `src/rtdsl/v2_5_triton_app_migration.py` | Marks `barnes_hut` as ready with Goal2803 while keeping Triton vector-sum auto-selection blocked. |
| `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness.json` | First pod evidence artifact. |
| `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness.stdout` | Captured stdout from the first pod run. |
| `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness_clean_from_git.json` | Clean-from-Git pod evidence artifact at `60237c66`. |
| `docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness_clean_from_git.stdout` | Captured stdout from the clean-from-Git pod run. |

## Pod Environment

Pod:

```text
ssh root@69.30.85.171 -p 22167 -i C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
NVIDIA RTX A5000, driver 570.211.01
```

Installed during Goal2803 setup:

```text
libembree-dev / libembree4-4
libgeos-dev
RTDL_EMBREE_PREFIX=/usr
```

First evidence checkout:

```text
feed82707a0947e3876adfb3e96809075c9b7db0
```

The Goal2803 script was copied into that checkout for the first artifact run.

Command:

```bash
timeout 900s python3 scripts/goal2803_barnes_hut_v25_consolidated_harness.py \
  --case 512:16 \
  --case 2048:32 \
  --repeats 2 \
  --vector-group-count 4096 \
  --vector-rows-per-group 16 \
  --output docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness.json
```

Membership lowering results:

| Bodies | Bucket | Frontier Rows | Near-Zone Rows | Embree Total (s) | OptiX Total (s) | OptiX Total Speedup | Embree Membership (s) | OptiX Membership (s) | OptiX Membership Speedup | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 512 | 16 | 54,178 | 13,106 | 0.749551 | 0.880134 | 0.852x | 0.156956 | 0.280260 | 0.560x | pass; setup-scale OptiX loss |
| 2,048 | 32 | 514,055 | 65,400 | 5.970259 | 3.841082 | 1.554x | 2.296993 | 0.089146 | 25.767x | pass |

Vector-sum partner result:

| Groups | Rows/Group | Rows | Torch Median (s) | Triton Median (s) | Triton/Torch Ratio | Match | Selection |
| ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 4,096 | 16 | 65,536 | 0.000532 | 0.003639 | 6.844x slower | pass | Triton auto-selection remains blocked |

Artifact checks:

- `status`: `pass`
- membership rows match between Embree and OptiX
- OptiX membership rows report RT-core acceleration
- vector-sum rows match Torch
- Triton vector-sum preview uses presegmented offsets and no global atomic add
- Triton vector-sum remains slower than Torch on this fixture, so auto-selection stays blocked
- Triton vector-sum auto-selection remains blocked

Validation policy:

- The first artifact validates the 512-body case against the reference frontier collection and checks Embree/OptiX shape parity for every measured case.
- The clean-from-Git rerun must use the default three cases, three repeats, and two vector warmups. If full reference validation is not enabled for every case, the artifact must retain the explicit `membership_validation_policy` field and explain that larger-case evidence is same-contract Embree/OptiX shape parity plus first-case reference validation.

## Clean-From-Git Pod Rerun

Clean evidence checkout:

```text
60237c663c64b3322310817f0e0ece28e15e0f30
source_dirty: []
```

Command:

```bash
timeout 2400s python3 scripts/goal2803_barnes_hut_v25_consolidated_harness.py \
  --repeats 3 \
  --vector-warmups 2 \
  --output docs/reports/goal2803_pod_artifacts/barnes_hut_v25_consolidated_harness_clean_from_git.json
```

Clean membership lowering results:

| Bodies | Bucket | Frontier Rows | Near-Zone Rows | Embree Total (s) | OptiX Total (s) | OptiX Total Speedup | Embree Membership (s) | OptiX Membership (s) | OptiX Membership Speedup | Validation | Status |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 512 | 16 | 54,178 | 13,106 | 0.702014 | 0.587315 | 1.195x | 0.153582 | 0.017712 | 8.671x | reference checked | pass |
| 2,048 | 32 | 514,055 | 65,400 | 5.658076 | 3.619626 | 1.563x | 2.133502 | 0.086982 | 24.528x | Embree/OptiX shape parity | pass |
| 8,192 | 32 | 2,469,712 | 381,692 | 94.872008 | 18.773798 | 5.053x | 76.913951 | 0.498393 | 154.324x | Embree/OptiX shape parity | pass |

Clean vector-sum partner result:

| Groups | Rows/Group | Rows | Torch Median (s) | Triton Median (s) | Triton/Torch Ratio | Warmups | Match | Selection |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 8,192 | 16 | 131,072 | 0.000694 | 0.003013 | 4.345x slower | 2 | pass | Triton vector-sum auto-selection remains blocked |

Clean artifact checks:

- `status`: `pass`
- `source_dirty`: `[]`
- `repeats`: `3`
- `vector_warmups`: `2`
- all three default cases present
- membership validation policy: first-case reference validation plus all-case Embree/OptiX shape parity
- all membership rows match between Embree and OptiX
- all OptiX membership rows report RT-core acceleration
- maximum OptiX membership-wrapper speedup versus Embree: `154.324x`
- vector-sum rows match Torch
- Triton vector-sum preview remains slower than Torch, so auto-selection stays blocked

## Boundary

Not claimed:

- not a public speedup claim;
- not a whole-app speedup claim;
- not a paper-reproduction claim;
- not an authors-code comparison;
- not a paper-level speedup claim;
- not a Triton vector-sum auto-selection claim;
- not a native app-specific engine path.

## Manifest Update

`barnes_hut` now records:

- `canonical_harness_status`: `ready_with_goal2803_consolidated_harness`
- `pod_evidence_status`: `Goal2803 current OptiX expanded-membership and Torch/Triton grouped-vector-sum same-contract evidence recorded`
- `next_action`: keep the consolidated harness current and keep Triton vector-sum auto-selection blocked until it beats the same-contract Torch/CuPy vector-sum opponent.

## Validation And Review

Distinct-AI reviews:

- `docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md`: `accept-with-boundary`; requested clean-from-Git rerun with default cases, three repeats, and at least two vector warmups.
- `docs/reviews/goal2803_gemini_review_barnes_hut_consolidated_harness_2026-05-31.md`: `accept-with-boundary`; confirms the harness is live, covers both halves, preserves boundary wording, and left clean-from-Git validation pending at review time.

Focused local tests:

```text
tests.goal2803_barnes_hut_v25_consolidated_harness_test
tests.goal2786_batched_vector_sum_offsets_tuning_test
tests.goal2785_presegmented_vector_sum_triton_offsets_test
tests.goal2781_grouped_vector_sum_adapter_test
tests.goal2641_barnes_hut_expanded_membership_lowering_test

Ran 19 tests in 0.946s
OK (skipped=4)
```

Focused clean pod tests:

```text
tests.goal2803_barnes_hut_v25_consolidated_harness_test
tests.goal2786_batched_vector_sum_offsets_tuning_test
tests.goal2785_presegmented_vector_sum_triton_offsets_test
tests.goal2781_grouped_vector_sum_adapter_test
tests.goal2641_barnes_hut_expanded_membership_lowering_test

Ran 19 tests in 3.215s
OK
```
