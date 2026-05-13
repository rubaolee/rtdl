# Goal1899 - v2 Strict Birth Gate Current Board

Status: active-blockers-pod-and-consensus-pending

Date: 2026-05-13

## Scope

Goal1899 is the current working board for the stricter Goal1814 v2.0 birth
gate. It summarizes what moved since the first partner preview and what still
blocks the v2.0 release label.

## Current Board

| Goal1814 blocker | Current state | Evidence | Next action |
| --- | --- | --- | --- |
| True zero-copy | Partially evidenced for selected OptiX device-column input/output paths; broad release wording still blocked. | Goals1819, 1821, 1823, 1826, 1831, 1834, 1836, 1838, 1845, 1847, 1848 | Decide exact public wording after the remaining app rows and pod evidence. |
| Direct device-pointer handoff | Implemented and fail-closed for selected partner descriptors; still bounded to specific primitives and contracts. | Goals1819, 1821, 1823, 1826 | Keep descriptor/lifetime/stream wording narrow; do not generalize to arbitrary partner code. |
| Broad RT-core speedup | Not ready. Strong exact-row evidence exists for fixed-radius and segment/polygon subpaths, but the road-hazard prepared row still lacks RTX pod artifacts. | Goals1881, 1886, 1889, 1895, 1897 | Run Goal1897 on RTX pod and review results. |
| Whole-application acceleration | Not ready. Some app-level prepared rows exist, but not all app claims have same-contract RTX evidence. | Goals1878, 1881, 1886, 1889, 1895 | Finish road-hazard pod row; then decide which app claims are allowed and which remain preview-only. |
| Arbitrary PyTorch/CuPy acceleration boundary | Still blocked as a public-rule task. Existing reports block overclaims, but a user-facing positive/negative rule still needs final wording. | Goal1814 plus partner reports | Write a dedicated user-facing boundary doc before v2.0 release review. |
| Package-install support | Blocked. No packaging metadata exists; source-tree-only remains the current validated mode. | Goal1898 | Either create validated packaging metadata or get 3-AI consensus for source-tree-only v2.0. |

## Newly Added Since The Last Board

- Goal1889: road-hazard prepared partner reuse row and GTX 1070 local smoke.
- Goal1895: v2 partner performance matrix status.
- Goal1896: Gemini Flash interim review of Goal1889 labeled local smoke.
- Goal1897: one-command road-hazard RTX pod packet, local dry-run passed.
- Goal1898: package-install gate audit.

## Immediate Next Hardware Step

Run Goal1897 on an RTX pod:

```bash
OUT_DIR=docs/reports/goal1897_road_hazard_prepared_reuse_pod \
OPTIX_PREFIX=/root/vendor/optix-sdk \
bash scripts/goal1897_road_hazard_prepared_reuse_pod_runner.sh
```

Expected accepted artifacts:

- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json`
- `docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json`
- `docs/reports/goal1897_road_hazard_prepared_reuse_pod_summary.json`

## Immediate Next Non-Hardware Step

Write the v2.0 partner acceleration boundary document:

- positive rule: what RTDL does accelerate in partner programs;
- negative rule: arbitrary PyTorch/CuPy code is not optimized by RTDL;
- examples that distinguish partner-owned columns from partner program
  acceleration;
- claim examples that are allowed, blocked, and pending.

## Verdict

v2.0 is still not born. The strongest next progress is Goal1897 pod execution
plus a user-facing partner-acceleration boundary document.
