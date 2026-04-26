# Goal1007 External Review — Claude (claude-sonnet-4-6)

Date: 2026-04-26

## Verdict: ACCEPT

All four review questions pass. One non-blocking implementation quirk is noted below.

---

## Q1 — Does the plan cover exactly the seven Goal1006 held candidates?

**PASS.**

From `goal1006_public_rtx_claim_wording_gate_2026-04-26.json`, `status_counts.candidate_but_needs_larger_scale_repeat` is `7`. The seven (app, path_name) pairs with that status are:

| App | Path |
|---|---|
| `robot_collision_screening` | `prepared_pose_flags` |
| `outlier_detection` | `prepared_fixed_radius_density_summary` |
| `dbscan_clustering` | `prepared_fixed_radius_core_flags` |
| `facility_knn_assignment` | `coverage_threshold_prepared` |
| `segment_polygon_hitcount` | `segment_polygon_hitcount_native_experimental` |
| `segment_polygon_anyhit_rows` | `segment_polygon_anyhit_rows_prepared_bounded_gate` |
| `ann_candidate_search` | `candidate_threshold_prepared` |

`TARGETS` in `goal1007_larger_scale_rtx_repeat_plan.py` contains exactly these seven pairs. The `build_plan()` function re-derives the held set at runtime from the source JSON and fails with `status: "needs_attention"` if there is any mismatch. The committed JSON report confirms `held_candidate_count: 7`, `target_count: 7`, `missing_held_candidates: []`, `extra_targets: []`, `status: "ok"`. The test suite asserts all five of those values explicitly.

---

## Q2 — Are the larger-scale commands reasonable as a first cloud repeat batch?

**PASS.**

| Target | Scale parameter | Rationale | Assessment |
|---|---|---|---|
| `robot_collision_screening` | 8 M poses, 4 096 obstacles | RTX phase was ~0.5 ms at small scale; 8 M poses targets >100 ms | Reasonable but aggressive; explicit 24 GB+ VRAM requirement is documented |
| `outlier_detection` | 400 K copies → ~3.2 M points | RTX phase was ~5.8 ms at small scale | Moderate; fits VRAM headroom note |
| `dbscan_clustering` | no separate command; reuses outlier JSON | Same fixed-radius kernel emits both scalar summaries | Correct shared-output pattern |
| `facility_knn_assignment` | 800 K copies → ~3.2 M build/query points | RTX phase was ~3.1 ms | Moderate |
| `segment_polygon_hitcount` | 8 192 copies | RTX phase was ~4 ms; scalar hitcount output caps memory risk | Reasonable |
| `segment_polygon_anyhit_rows` | 8 192 copies, `--output-capacity 131072` | Bounded output preserves the no-overflow gate | Correct: overflow flag must remain false |
| `ann_candidate_search` | 800 K copies, radius 0.2 → ~2.4 M points | RTX phase was ~0.75 ms | Moderate |

All six executable commands use `--skip-validation` (cost control) and `--iterations 7` (adequate for timing statistics). The robot run is the only high-memory entry and is appropriately flagged.

---

## Q3 — Is the shell script bounded and safe?

**PASS.**

`goal1007_larger_scale_rtx_repeat_commands.sh` satisfies the safety criteria:

- `set -euo pipefail` is present on line 2.
- Header comment states the boundary on line 5: "does not create cloud resources and does not authorize speedup claims."
- The only file-system side effect is `mkdir -p docs/reports` (local).
- `nvidia-smi` is read-only diagnostics.
- No `kubectl`, `gcloud`, `aws`, `terraform`, or any other cloud-provisioning command appears anywhere in the script.
- No claim-authorization step or flag is present.
- Every profiling command writes to an explicit, named `docs/reports/goal1007_*.json` path via `--output-json`.
- The post-run audit step invokes the plan generator locally with `--audit-existing` and writes two local files (`goal1007_larger_scale_rtx_repeat_plan_pod_audit.json` / `.md`).

---

## Q4 — Are the risk notes adequate?

**PASS.**

Each target carries a risk note that is appropriate to its profile:

- **robot_collision_screening**: specifies VRAM floor (24 GB+), quantifies ray count (32 M), and gives explicit downscaling guidance — the most thorough note for the highest-risk run.
- **outlier_detection**: states memory figure (3.2 M points) and instructs to reduce `--copies` before changing semantics if memory is tight.
- **dbscan_clustering**: correctly identifies the shared-output dependency and tells the reviewer to validate both app records from one JSON.
- **facility_knn_assignment** / **ann_candidate_search**: state memory figures and explain that validation is skipped for cost control.
- **segment_polygon_hitcount**: identifies that the output is scalar, so memory risk is bounded to geometry staging.
- **segment_polygon_anyhit_rows**: states the exact capacity (131 072) and the post-run gate condition ("any overflow keeps this row out of public wording") — the most critical post-run interpretation note.

---

## Non-Blocking Observation

**Shell script self-overwrite on pod audit step.**

`main()` in `goal1007_larger_scale_rtx_repeat_plan.py` unconditionally calls `write_shell(plan, Path(args.output_sh))` on every invocation, including the `--audit-existing` path. The shell script's final step invokes the plan generator with `--audit-existing` but omits `--output-sh`, so the default (`scripts/goal1007_larger_scale_rtx_repeat_commands.sh`) applies and the script overwrites itself during the pod run.

This is not harmful — the regenerated script is functionally identical to the original — but it is unexpected behavior for a pod operator inspecting file state after the run. Since all profiling commands complete before the audit step executes, there is no risk of partial-run corruption. No code change is required to accept this plan.

---

## Summary

| Question | Result |
|---|---|
| Covers exactly seven held Goal1006 candidates | PASS |
| Commands reasonable for first cloud repeat batch | PASS |
| Shell script bounded, safe, no cloud resource creation, explicit output files | PASS |
| Risk notes adequate for pod operation and post-run interpretation | PASS |

**ACCEPT** — safe to proceed to pod execution.
