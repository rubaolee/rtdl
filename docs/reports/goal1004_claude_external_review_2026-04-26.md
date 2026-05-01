# Goal1004 External Review — RTX A5000 Cloud Artifacts

**Verdict: ACCEPT**

Date: 2026-04-26
Reviewer: Claude Sonnet 4.6 (external)
Commit under review: `914122ecd2f2c73f6a51ec2d5b04ca3d575d5681`
Branch: `codex/rtx-cloud-run-2026-04-22`

---

## Q1 — Does the evidence support 17 gates executed on real RTX A5000 hardware?

**Yes.**

- `nvidia-smi` output is embedded verbatim in the merged JSON (`nvidia_smi` field), showing `NVIDIA RTX A5000`, Driver 570.211.01, CUDA 12.8, 24564 MiB VRAM.
- `dry_run: false` is set at the top of the merged summary; all entries show `execution_mode: executed` (except `dbscan_clustering`, see §Observations).
- `entry_count: 17`, `failed_count: 0`, `status: ok` in the merged JSON.
- All 17 `result.status` fields are `"ok"` and all `returncode` values are `0`.
- Commit hash matches across the pod run summary, final artifact report, and merged JSON.
- OptiX backend build time (11.55 s) and 34/34 native OptiX tests passing confirm real hardware execution, not a stub.
- Pod IP and UTC timestamps (`2026-04-26T14:30:44+0000` to `~14:35`) provide audit traceability.

---

## Q2 — Does the evidence avoid overclaiming?

**Yes, consistently.**

Every manifest entry carries a `non_claim` field and a `baseline_review_contract` with `status: "required_before_public_speedup_claim"`. The artifact report repeats the boundary explicitly: "does not authorize RTX speedup claims; claims require review of phase separation, correctness parity, hardware metadata, and comparison baselines." The pod run summary adds the same constraint. No timing is presented alongside a speedup ratio vs. a baseline.

---

## Q3 — Does the audit script check the right hard facts?

The script covers:

| Check | Coverage |
|---|---|
| Required files present | Yes |
| Exact commit `914122e…` | Yes |
| `entry_count == 17` | Yes |
| `failed_count == 0` | Yes |
| All result statuses ok (17 of 17) | Yes |
| Final `Status: ok` in report | Yes |
| No-speedup boundary text | Yes |
| RTX A5000 named in run summary | Yes |
| GEOS incident documented (`libgeos-dev` + `-lgeos_c`) | Yes |
| `Manifest entries executed: 17` / `Final failed entries: 0` | Yes |

**Two gaps identified (recommended fixes, not release blockers):**

1. **`dry_run` not checked.** The audit reads `payload.get("failed_count")` and `payload.get("status")` but never asserts `payload.get("dry_run") == False`. A future dry-run would pass all checks with zero real execution. Add `"dry_run_false": payload.get("dry_run") == False` to the `checks` dict.

2. **`nvidia-smi` JSON field not cross-checked.** The hardware check is done by searching for `"NVIDIA RTX A5000"` in the human-authored run-summary text. The embedded `nvidia_smi` field in the merged JSON is a stronger, machine-readable source. Add `"nvidia_smi_json_confirms_rtx_a5000": "NVIDIA RTX A5000" in payload.get("nvidia_smi", "")`.

---

## Q4 — Is the GEOS remediation release-blocking?

**No.**

The remediation is clean:

- The failed first bundle is preserved as `goal1003_rtx_a5000_artifacts_with_report_2026-04-26.tgz` (v1). Evidence of the failure is not deleted.
- The root cause is clearly documented: pod image lacked `libgeos-dev`, so the native oracle could not link `-lgeos_c` for graph BFS and triangle-count validation.
- The fix (`apt-get install libgeos-dev pkg-config`) is narrowly scoped to a missing system package; it does not alter the commit, the profiler scripts, or the benchmark parameters.
- Only Group F (graph) was rerun, not the full suite. The rerun passed (`graph_analytics / graph_visibility_edges_gate`, returncode 0, strict_pass true).
- The v2 bundle contains the corrected graph artifact.
- The audit script gates on both `libgeos-dev` and `-lgeos_c` appearing in the run summary, so future automated checks will confirm the incident was recorded.

The only mild note: the pod summary calls this section "Important Incident" but does not record the failing stderr output or the v1 returncode. That is acceptable — the failure mode (linker error on `-lgeos_c`) is described precisely enough to reconstruct the cause.

---

## Additional Observations (Non-Blocking)

- **`reused_command_result` for `dbscan_clustering`.** The `outlier_detection` and `dbscan_clustering` entries share one command invocation; dbscan_clustering is marked `execution_mode: reused_command_result`. The audit script does not surface this. Both apps draw from the same profiler output, which is valid (the script emits both app results in one pass), but reviewers should know only 16 unique commands ran, not 17 (the merged JSON records `unique_command_count: 16`). Not a quality concern, just worth documenting.
- **Test app-set count is 16 unique apps, entry count is 17.** The test `test_expected_app_set_is_preserved` correctly checks 16 unique app names (database_analytics has two paths). No bug; a comment would help future readers.

---

## Summary

All 11 audit checks pass. Hardware identity is confirmed by embedded `nvidia-smi` output. No speedup claims are made anywhere in the artifacts. The GEOS incident is properly preserved and remediated. The two recommended audit script patches (check `dry_run == False`, cross-check `nvidia_smi` JSON field) close minor gate weaknesses but do not affect the current evidence.

**ACCEPT** — evidence is sufficient to record that all 17 RTX app gates executed successfully on real RTX A5000 hardware at commit `914122e`. No public speedup claims are authorized by this run.
