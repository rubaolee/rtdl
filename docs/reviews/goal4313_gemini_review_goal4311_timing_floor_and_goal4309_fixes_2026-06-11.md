# Gemini Review: Goal4311 Timing-Floor Guard and Goal4309 Fixes

Date: 2026-06-11
Reviewer: Gemini (autonomous CLI agent)
Verdict: `accept`

## Summary

This review evaluates Goal4311 (current scale-profile timing-floor guard) and the fixes for Goal4309 findings (F-R2/F-R4/F-R5/F-R6). The implementation of the timing-floor guard correctly addresses the Fable5 P5/F6 finding by providing per-row and per-packet exposure of timing-floor compliance. The follow-up fixes for the security guard, versioning, tutorial paths, and field naming consistently improve the project's hygiene and usability without expanding public claim boundaries.

## Findings

### 1. Timing-Floor Guard (Goal4311) — MAJOR (Evidence Integrity)
Goal4311 successfully implements the first no-pod slice of the Fable5 P5 finding. The scale-profile runner (`scripts/goal3828_current_benchmark_scale_profile_runner.py`) now correctly evaluates and reports `hot_path_floor_evaluation` per row and `hot_path_floor_summary` per packet. The four requested statuses (`floor_met_internal_evidence_only`, `subfloor_not_claim_grade`, `metric_not_numeric`, and `smoke_scale_or_internal_not_claim_grade`) are accurately distinguished. The dry-run behavior correctly exposes the floor policy and targeted rows before pod resources are consumed.

### 2. Security Guard Expansion (F-R2) — MEDIUM (Security)
The security redaction guard (`tests/goal4303_current_security_redaction_guard_test.py`) has been expanded to include `.json` artifacts in `docs/reports/`, `docs/handoff/`, and `docs/reviews/` for the current goal surface (goal42xx/goal43xx). This materially addresses the F-R1/F-R2 findings without overclaiming sanitization of the full historical archive.

### 3. Version and Usability Fixes (F-R4, F-R5) — LOW (Hygiene)
The `pyproject.toml` version has been updated to `2.11.0` to match the active development lane (F-R4). The tutorial (`tutorials/current/01_source_tree_first_run.md`) now uses a generic placeholder path (`C:\path\to\...`) instead of a local filesystem path (F-R5).

### 4. RTNN Field Naming (F-R6) — LOW (Precision)
The RTNN Embree front-door output in `examples/current/research_benchmarks/rtnn/rtdl_rtnn_benchmark_app.py` now includes an `rt_path_note` field and an `inherited_ann_optix_performance_note_present` flag, resolving the confusion caused by the inherited `optix_performance` field name (F-R6).

## Answers to Review Questions

1. **Does Goal4311 correctly expose `hot_path_floor_evaluation` per row and `hot_path_floor_summary` per packet without authorizing public performance claims?**
   Yes. The fields are present, correctly calculated, and explicitly tagged with `public_speedup_claim_authorized: false` and `decision_grade_timing_authorized: false`.

2. **Is the dry-run behavior useful before pod time is spent?**
   Yes. It exposes the `timing_floor_policy` and `targeted_floor_rows` in the summary, allowing verification of the calibration plan before execution.

3. **Does the runner correctly distinguish the four requested statuses?**
   Yes. The implementation in `_evaluate_hot_path_floor` and `_summarize_hot_path_floor` covers all four states (floor met, subfloor, non-numeric metric, and smoke/internal) correctly.

4. **Did the F-R2 response expand the security guard to current JSON artifacts without pretending to sanitize the full historical archive?**
   Yes. The test now rglobs for `.json` files in the current goal directories but maintains its stated scope boundary regarding the historical archive.

5. **Did the F-R4/F-R5/F-R6 fixes resolve the v2.11 metadata mismatch, tutorial local-path issue, and RTNN Embree `optix_performance` confusion?**
   Yes. `pyproject.toml` is 2.11.0, the tutorial path is generic, and the RTNN app clarifies the OptiX note origin.

6. **Is the next pod-needed step correctly identified as a fresh ten-app scale-profile packet with the updated runner?**
   Yes. The runner is now capable of producing floor-aware evidence, and the next pod run will generate the required visibility for all ten benchmark apps.

## Claim Boundaries

This review **does not authorize**:
- release action, tags, or publishing,
- public speedup wording or whole-app acceleration claims,
- broad RT-core wording or AMD/Intel performance claims,
- package-install or PyPI promise wording,
- true zero-copy or device-residency claims,
- automatic partner selection,
- paper-reproduction claims.

The historical Goal4215 packet remains sub-floor for several rows; Goal4311 correctly documents that a fresh pod-run packet is required before timing-floor integrity is claimed for the ten-app scale profile.

## Verdict: `accept`
The work is technically sound, addresses all findings from the Goal4309 review, and maintains strict adherence to project boundaries.
