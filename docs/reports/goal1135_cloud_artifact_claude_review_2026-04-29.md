# Goal1135 Cloud Artifact Review — Claude

Date: 2026-04-29
Reviewer: Claude (claude-sonnet-4-6)
Artifacts reviewed: `docs/reports/goal1135_changed_path_rtx_pod_run_2026-04-29.md` plus all JSON/log files under `docs/reports/goal1135_changed_path_rtx_pod/`

## Verdict: ACCEPT

All referenced artifacts are present. Report numeric values match the JSON artifacts exactly. No public RTX speedup or release claim is made. GEOS graph rerun handling is acceptable. Four minor observations recorded below — none are blockers.

---

## Artifact-by-artifact verification

### Bootstrap (`bootstrap_goal1135.json`)

- GPU: NVIDIA RTX A5000, 24564 MiB. Driver 580.126.09. Matches report.
- nvcc: 12.8.93 at `/usr/local/cuda-12.8`. Matches report.
- OptiX headers: v9.0.0 at `/workspace/vendor/optix-dev-9.0.0`. Matches report.
- `make build-optix`: returncode 0. Matches report ("OK").
- Focused native OptiX tests: `Ran 34 tests in 6.206s OK`. Report says "34 tests OK". Matches.
- Deprecated pre-SM75 nvcc warning present in stderr. Report correctly notes it as expected.
- `git rev-parse HEAD` failed on pod (rc=128 — no git repo under /workspace). The bootstrap JSON records this failure honestly. Source commit `21fa036881bf9a0c806f69c15727d87b482ccfcf` is referenced in report and corroborated by `hausdorff_threshold_phase_gate.json:source_commit`. This is an accepted pod limitation.

### `database_analytics_compact_summary.json`

- `one_shot_total_sec`: 3.7903162809088826. Report value exact match.
- `prepared_session_warm_query_sec.median_sec`: 0.26575445383787155. Report value exact match.
- `row_materializing_operation_count`: 0. Report claims "0 row-materializing operations". Matches.
- Native DB counter status: `exported`. Matches report ("native DB counters exported").
- The JSON contains `speedup_one_shot_over_warm_query_median: 14.262...`. This is a same-backend ratio (one-shot vs warm prepared query), not an RTX vs CPU speedup. The report does not surface this number as a speedup claim. No overclaim.
- `rt_core_claim_scope` in the JSON: "partial prepared compact-summary DB traversal only; not a broad DBMS or whole-app speedup claim". Properly scoped.
- Log confirms gate passed (rc=0) at 18:10–18:11.

### `graph_visibility_edges_gate.json` + both logs

- Initial log (18:11): `status: fail, strict_pass: false`. Initial run failed.
- Report explanation: `libgeos_c` missing for the native CPU/oracle reference build. Matches log timing and failure mode.
- Rerun log (18:30): `status: pass, strict_pass: true`. rc=0.
- JSON artifact `generated_at: 2026-04-29T18:30:23` matches rerun log timestamp. The artifact correctly reflects the passing rerun.
- Scale unchanged: 20,000 copies in both runs. No parameter cherry-picking.
- All three scenarios (visibility_anyhit, BFS, triangle-count) show `parity_vs_analytic_expected: true`.
- Both log files are present and accurately disclose the failure before the fix.

### `road_hazard_native_summary_count.json`

- `strict_pass: true`, `status: pass`. Log confirms rc=0. Report says "PASS with `strict_pass: true`". Exact match.
- `parity_vs_cpu_python_reference: true`. Correct.

### `polygon_pair_overlap_phase_gate.json` and `polygon_set_jaccard_phase_gate.json`

- Both: `status: pass`, `parity_vs_cpu: true`. Logs confirm rc=0.
- Both: `candidate_count_matches_expected: false` — OptiX found 40,000 candidates vs expected 60,000. This is an RTX conservative-candidate approximation characteristic. Final result parity holds (`parity_vs_cpu: true`). The non-claim boundaries in both JSONs exclude full-parity candidate-count guarantees. The report does not flag this discrepancy explicitly, but it is within documented claim scope and is not a blocking concern.
- Both: `rt_core_accelerated: false`, `rt_core_candidate_discovery_active: true`. The report says "OptiX phase profiler passed in summary mode with analytic-summary validation" — accurately describes this phase-gate role, no RT-core acceleration overclaim.

### `hausdorff_threshold_phase_gate.json`

- `optix_query_sec.median_sec`: 0.011092765256762505. Report value exact match.
- `optix_prepare_sec`: 1.3375593619421124. Report value exact match.
- `matches_oracle: true`. Report says "Oracle parity passed for threshold decision". Matches.
- JSON `activation_status: "deferred_until_real_rtx_phase_run_and_review"`. Report says "capability/phase evidence only" and explicitly states the public speedup path remains blocked. No overclaim. Matches the contract.

---

## RTX Speedup / Release Claim Assessment

No public speedup claim appears in the report. The report header explicitly states: "It does not authorize public RTX speedup wording, release, or broad whole-app acceleration claims." Every JSON artifact carries matching non-claim and boundary fields. The Hausdorff gate defers activation. The DB gate status is `phase_clean_candidate_for_rtx_review`, not approved. No speedup ratio is surfaced in the report narrative.

The only numeric ratio in the artifacts that could be misread is `speedup_one_shot_over_warm_query_median: 14.262` in the DB JSON. This compares the same backend to itself (one-shot vs warm prepared query) and is not an RTX vs CPU comparison. The report correctly omits this from the narrative. No overclaim.

---

## GEOS Graph Rerun Assessment: Acceptable

The initial failure was purely a missing system library (`libgeos_c`/`libgeos-dev`) needed by the native CPU oracle build on the fresh pod image — not a code parity failure. After `apt install libgeos-dev pkg-config`, the exact same gate ran at the same scale (20,000 copies) and passed with `strict_pass: true`. Both logs are present and the sequence is fully disclosed in the report. The final JSON artifact reflects the passing rerun. This is standard dependency resolution for a fresh pod and does not affect the validity of the gate result.

---

## Minor Observations (non-blocking)

1. **Git commit not pod-verifiable**: `git rev-parse HEAD` fails on the pod (no git repo). The source commit `21fa036881bf9a0c806f69c15727d87b482ccfcf` is attested only by the `.rtdl_source_commit` marker and secondarily by `hausdorff_threshold_phase_gate.json:source_commit`. Acceptable for an rsync-based pod session; future sessions could include a manifest hash for stronger provenance.

2. **Polygon candidate count discrepancy not surfaced in report**: Both overlap and Jaccard gates record `candidate_count_matches_expected: false` (40k vs 60k expected). Result parity still holds. The report does not mention this, but the claim boundaries in the JSONs make it a non-blocking characteristic. Worth noting in artifact intake if promoted.

3. **`speedup_one_shot_over_warm_query_median` field**: This field in the DB JSON looks like a speedup claim at first read. As noted above, it is a same-backend operational ratio, not RTX vs CPU. If these artifacts are shared externally, this field should be renamed or annotated to avoid misreading.

4. **DB gate ran in a separate earlier session (18:10–18:11) before the GEOS fix session (18:30+)**: The DB gate does not require GEOS so this is not a problem. Session ordering is consistent with the operational notes in the report.
