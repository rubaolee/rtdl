# Goal2803 Barnes-Hut v2.5 Consolidated Harness

Date: 2026-05-31

Status: implemented locally with first Embree/OptiX/Torch/Triton pod evidence and distinct-AI review.

Verdict: accept-with-boundary pending clean-from-Git rerun.

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

## Validation

Distinct-AI reviews:

- `docs/reviews/goal2803_claude_review_barnes_hut_consolidated_harness_2026-05-31.md`: `accept-with-boundary`; requests clean-from-Git rerun with default cases, three repeats, and at least two vector warmups.
- `docs/reviews/goal2803_gemini_review_barnes_hut_consolidated_harness_2026-05-31.md`: `accept-with-boundary`; confirms the harness is live, covers both halves, preserves boundary wording, and leaves clean-from-Git validation pending.

Focused tests and clean-from-Git pod validation are still pending at the time this report was first written.
