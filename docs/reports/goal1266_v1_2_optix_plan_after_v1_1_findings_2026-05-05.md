# Goal1266 v1.2 OptiX Plan After v1.1 Findings

Date: 2026-05-05

Status: internal v1.2 execution plan. This does not authorize public wording,
release claims, or new backend scope.

## Scope

This plan supersedes the pre-Goal1263/Goal1264 v1.1 triage table for planning
purposes only. Historical reports remain unchanged.

Active implementation scope before v2.1:

- NVIDIA OptiX/RTX performance is the top priority.
- Embree remains the same-contract CPU RT/BVH baseline and fallback.
- Vulkan, HIPRT, and Apple RT receive no new implementation work before v2.1.
- Existing Vulkan/HIPRT/Apple proof surfaces remain documented and tested where
  already present.

## Source Inputs

- `docs/reports/goal1255_three_ai_v1_1_to_v1_5_roadmap_consensus_2026-05-04.md`
- `docs/reports/goal1262_v1_1_patched_full_matrix_intake_2026-05-04.md`
- `docs/reports/goal1263_three_ai_consensus_polygon_pair_v1_1_2026-05-04.md`
- `docs/reports/goal1264_db_graph_scale_probe_intake_2026-05-04.md`
- `docs/v1_1_optix_status.md`
- `docs/performance_model.md`

## Outcome Rule

v1.2 does not need every investigated OptiX path to beat Embree. A slower OptiX
result can close as `optix_still_slower_with_reason` when correctness is clean,
the same-contract comparison is valid, and the bottleneck is identified. That is
engineering evidence and v1.5/v2.0 design input, not positive public RTX speedup
wording.

Positive public wording still requires a separate exact-sub-path wording packet
and external review.

## Current v1.1 Findings

| App row | Current state | Primary v1.2 work | Acceptable v1.2 exit |
| --- | --- | --- | --- |
| `polygon_pair_overlap_area_rows` | Goal1263 accepted bounded positive wording for RT-assisted LSI/PIP positive candidate discovery plus native C++ exact area continuation at 40k, 80k, and 160k copies. `candidate_count_matches_expected: false` remains disclosed. | Reconcile candidate-count diagnostics without weakening the accepted summary-parity boundary. Keep timing split between candidate discovery, native exact continuation, and output work. | `diagnostic_reconciled` or `diagnostic_disclosed_with_no_claim_expansion`; no broader polygon/GIS/whole-app claim. |
| `graph_analytics` | Goal1264 confirms graph visibility correctness and a very fast OptiX any-hit kernel, but total OptiX time remains slower than Embree because host-side input construction, scene/ray prepare, and ray packing dominate. | Remove or amortize host preparation and ray packing overhead; keep traversal timing separate from BFS/frontier, triangle-set, graph database, and Python orchestration work. | `optix_improved` if total same-contract timing beats Embree, otherwise `optix_still_slower_with_reason` with the overhead source quantified. |
| `database_analytics` | Goal1262/Goal1264 show execution-unblocked but mixed evidence. `sales_risk` compact-summary reaches 300k on the retained probe, but warm-query median still favors Embree; `scenario=all 300k` and broad DB speedup remain outside the claim. | Preserve materialization-free compact-summary contract; investigate warm-query overhead, row/candidate ceiling behavior, and streaming/chunked native processing for broader scenarios. | `optix_improved` only if warm-query same-contract evidence beats Embree; otherwise `optix_still_slower_with_reason` or `baseline_contract_incomplete`. |
| `polygon_set_jaccard` | Goal1262 confirms correctness at chunk `1024`, including 8192 copies, but OptiX remains slower than Embree; no positive Jaccard speedup wording is authorized. | Keep chunk `1024` as the safe correctness default; investigate chunk sensitivity, candidate discovery cost, and native exact continuation/output split. | `optix_improved` only with same-contract candidate-discovery evidence; otherwise `optix_still_slower_with_reason` with chunk policy preserved. |

## Priority Order

1. `graph_analytics`: largest explained total-path gap; most directly teaches
   host-preparation and ray-packing overhead reduction.
2. `polygon_pair_overlap_area_rows`: already has bounded positive wording, but
   the candidate-count diagnostic should be reconciled before claim expansion.
3. `database_analytics`: useful because execution is unblocked, but positive
   wording requires warm-query evidence, not one-shot cherry-picking.
4. `polygon_set_jaccard`: correctness-ready safe chunk exists; performance work
   should wait until candidate-discovery and chunk-sensitivity instrumentation is
   clean.

## Pod Policy

Do more local inspection before starting a pod. Use a pod only after the local
packet identifies exact commands, expected artifacts, and the phase fields that
must be compared. Once a pod is running, prioritize same-contract OptiX timings
and artifact copy-back over broad exploratory work.

## Non-Goals

- No whole-app speedup claims.
- No SQL-engine, DBMS, graph-database, PostGIS, FAISS/HNSW, full GIS, or
  arbitrary polygon-geometry claims.
- No public wording updates from this plan.
- No v1.5 generic native refactor before v1.3 contracts are written and
  externally reviewed.
- No new Vulkan, HIPRT, or Apple RT implementation work before v2.1.
