# Goal4824 RayJoin Goal4806 Reuse Audit And Second-Priority Plan

Date: 2026-06-30

## Purpose

The user asked whether the "second priority" RayJoin Section 5.7 work had
already been done during the earlier V4/Goal4806 reproduction attempt. This
audit answers that before any new data acquisition or benchmark work continues.

The short answer is: **yes, a large part of the second-priority route was
already done in Goal4806, and it must be reused rather than repeated.** It was
not a complete eight-pair exact-paper reproduction.

## Boundary

This is a reuse and planning audit. It does not authorize new RTDL runtime
changes, new public claims, or broad performance conclusions.

This work is **not a continuation of V4**. V3/V4 work has been isolated under
`exp-project-1/` and is not part of the current user-facing project. Goal4824
uses the archived Goal4806 material only as a historical data/artifact cache:

- reusable dataset locations;
- generated CDB files;
- author-code paths;
- source URLs and availability checks;
- measured debug artifacts that identify bottlenecks or missing inputs.

It does **not** reuse V4 as a product, API, architecture, release claim, or
performance claim. Any archived V4/Goal4806 result must be relabeled before
use, and most of it can only serve as a clue until revalidated under the current
v2.14-centered line.

Current product/runtime edits remain only the already exposed core repairs from
Goal4820:

- directed-segment point-location SoS reported-distance repair in OptiX;
- per-map midpoint-face storage repair for overlay continuation.

This audit does not add another runtime modification.

## Sources Read

Archived Goal4806 directory:

`exp-project-1/untracked-current/tools___archive__goal4806_released_rtdl_rayjoin_attempt_2026-06-30/`

Key archived reports:

- `docs_reports/goal4806_rayjoin_section57_current_status_and_8pair_data_audit_2026-06-30.md`
- `docs_reports/goal4806_rayjoin_section57_county_zipcode_byte_equal_and_numba_candidate_2026-06-30.md`
- `docs_reports/goal4806_section57_data_acquisition_audit_network_2026-06-30.json`
- `docs_reports/goal4806_section57_arcgis_full_us_build_block_water_2026-06-30.json`
- `docs_reports/goal4806_section57_matrix_same_source_block_water_rtdl_only_2026-06-30.md`

Current POD verification command confirmed the old working data still exists:

```text
HOST=e7820d339c40
GPU=NVIDIA RTX 4000 Ada Generation
PRESENT:/workspace/rtdl_goal4806_fast_min
PRESENT:/workspace/rayjoin_section57_same_source_cdb
PRESENT:/workspace/RayJoin_fresh
PRESENT:/workspace/rayjoin_section57_arcgis_stage
PRESENT:/workspace/rtdl_goal4806
PRESENT:/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_matrix_exact_county_20260630
PRESENT:/workspace/rtdl_goal4806_fast_min/artifacts/goal4806_section57_arcgis_full_us_20260630
```

## What Goal4806 Already Did

| Area | Result | Reuse status |
|---|---|---|
| Paper/source contract | Read paper Section 3.2/5.7 and author code; established that full overlay means LSI + PIP + output-chain construction. | Reuse. Do not re-derive unless a specific claim is challenged. |
| Dryad/preprocessed data link | Rechecked and found HTTP 404. | Reuse as missing exact-data evidence. |
| Eight Section 5.7 pair list | Enumerated County x Zipcode, Block x Water, and six Lakes/Parks continent pairs. | Reuse. |
| ArcGIS source audit | Four U.S. FeatureServer sources were live and feature counts matched: counties 3,144; zip codes 32,294; block groups 239,203; water bodies 463,591. | Reuse after current-live spot check if needed. |
| Same-source generation support | Registered only for the two U.S. pairs: `county_zipcode` and `block_water`. | Reuse. |
| Lakes/Parks support | No registered same-source generator targets for the six Lakes/Parks pairs. | Remains open. |
| County x Zipcode byte-equal slice | Goal4806 reported author output and RTDL output byte-equal, both 87,758,310 bytes, chain count 29,254,027, face count 115,490. | Useful clue, but this came from the dirty Goal4806 line and must be revalidated under the current repaired product line before any new claim. |
| County x Zipcode V4+Numba candidate | Post-traversal segmented-counts candidate ran correctly without hot-path host materialization, steady-state 0.016283 sec. | Candidate-stage evidence only; not full overlay performance. |
| Block x Water same-source CDB | Built large same-source regenerated CDBs from ArcGIS rings: block group CDB 3,146,767,020 bytes; water bodies CDB 2,402,941,772 bytes. | Reuse as `same_source_regenerated_cdb`, not exact paper-preprocessed input. |
| Block x Water same-source RTDL run | RTDL OptiX completed: total 367.231680 sec, load/pack 303.999034 sec, compute without load/pack 63.232646 sec, LSI 649,605. | Reuse as performance/debug baseline, not final evidence. |
| Block x Water LSI phase probes | LSI count matched author at 649,605; wrapper/setup overhead dominated around millisecond-scale traversal. | Reuse to target future engineering, if product work resumes. |
| Block x Water full-output summary | Summary path improved but still slow; output-chain summary assembly dropped from 134.54 sec to 6.96 sec in a two-point fast path, but total remained hundreds of seconds. | Reuse as bottleneck evidence. |

## What Goal4806 Did Not Finish

| Missing item | Why it matters |
|---|---|
| Exact paper-preprocessed CDBs for all eight pairs | Without the exact CDBs, a full Section 5.7 paper reproduction cannot be claimed. |
| Author answer files for all eight pairs | Without answers, RTDL output correctness cannot be verified. |
| Equivalence proof between same-source regenerated CDB and paper-preprocessed CDB | Same source is not automatically the same topology. It must not be mislabeled as exact paper input. |
| Six Lakes/Parks source targets/converters | The all-eight-pair matrix cannot be completed from current registered sources. |
| Full Block x Water author-vs-RTDL byte-equal output | Existing Block x Water evidence is same-source RTDL/debug evidence, not a complete correctness/performance row. |
| Full V4+Numba overlay route | Existing V4+Numba evidence is candidate-stage only. |

## Reuse Rules

1. Do not repeat the Goal4806 network audit unless checking current liveness of a specific source.
2. Do not rebuild the U.S. same-source CDBs unless the existing POD artifacts are missing or corrupted.
3. Do not call same-source regenerated CDBs "exact Section 5.7 paper inputs."
4. Do not call V4+Numba candidate-stage numbers "full polygon overlay performance."
5. Do not treat dirty Goal4806 output as current product evidence without revalidation under the current repaired tree.
6. Do not pursue performance before the corresponding correctness row is byte-equal or has an explicitly accepted equivalence oracle.

## Recommended Continuation

### Goal4825 — Promote Reusable Goal4806 Artifacts Into The Current RayJoin Evidence Index

Purpose: create a small machine-readable index under `history/internal_docs`
that points to the reusable old artifacts and labels each as one of:

- `exact_public_sample_current_line`
- `goal4806_dirty_line_needs_revalidation`
- `same_source_regenerated_cdb`
- `candidate_stage_only`
- `missing_exact_input_or_answer`

Exit gate: every reused artifact has a provenance label, and no old artifact is
silently promoted to current evidence.

### Goal4826 — Revalidate The County x Zipcode Slice Under The Current Core Fix

Purpose: determine whether the old Goal4806 County x Zipcode byte-equal result
still holds under the current repaired product code, without relying on dirty
V4 helper changes.

Exit gate:

- same input paths recorded;
- author output path recorded;
- RTDL output path recorded;
- byte equality or exact mismatch diagnosis recorded.

If it passes, it becomes a current-line correctness row. If it fails, stop and
diagnose before performance.

### Goal4827 — Decide The Block x Water Route

Purpose: choose the honest next action for Block x Water.

Allowed paths:

- if exact paper CDB/answer appears, run exact author-vs-RTDL correctness first;
- otherwise, keep it as `same_source_regenerated_cdb` and run only a bounded
  engineering row, clearly not a paper reproduction row.

Exit gate: no performance claim without correctness/equivalence boundary.

### Goal4828 — Lakes/Parks Source Gap

Purpose: determine whether the six Lakes/Parks pairs can be reconstructed from
author-listed sources and author-compatible preprocessing.

Exit gate: either register source targets and conversion plan, or close the 8/8
route as blocked by missing inputs.

## Current Honest State

The project has:

- one current-line exact public sample after Goal4820/4821: County x Soil;
- old Goal4806 evidence that can speed up the next steps;
- old same-source U.S. CDB artifacts for County x Zipcode and Block x Water;
- no valid all-eight-pair exact Section 5.7 paper reproduction yet.

The next work should be reuse-first, not rediscovery-first.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   I would be foolish if I restarted data acquisition from zero, ignored
   Goal4806, or promoted dirty V4 artifacts as current evidence.

2. **What actions would make the decision foolish?**
   Re-downloading the U.S. ArcGIS sources blindly; rebuilding existing CDBs
   without checking POD artifacts; treating same-source data as exact paper
   data; using candidate-stage Numba timings as full overlay timings.

3. **Is there another path that avoids being stuck on the same thought?**
   Yes: reuse and relabel existing Goal4806 artifacts first, then revalidate
   only the rows that can become current-line evidence.

4. **Can I start a different path that truly solves the problem?**
   Yes: Goal4825 should build the provenance index, then Goal4826 should
   revalidate County x Zipcode under the current repaired core. That directly
   converts old work into usable current evidence or exposes the next real gap.
