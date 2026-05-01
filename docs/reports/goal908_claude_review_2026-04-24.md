## External Review: Goal908 Pre-Cloud Batch Rehearsal

---

### Review Scope

Checked: orchestration shape, entry count, graph gate presence, step sequence, dry-run boundary integrity, runbook/rehearsal alignment, runner code logic.

---

### Findings

**Entry count: PASS**

Manifest has 5 active entries (`prepared_db_session_sales_risk`, `prepared_db_session_regional_dashboard`, `prepared_fixed_radius_density_summary`, `prepared_fixed_radius_core_flags`, `prepared_pose_flags`) plus 12 deferred entries. Total = 17. Matches `entry_count: 17` and the table in the rehearsal report.

**Graph gate presence: PASS**

`graph_visibility_edges_gate` is present in `deferred_entries` and maps to `goal889_graph_visibility_optix_gate.py --copies 20000 --output-mode summary --strict`. This is the combined visibility any-hit + native BFS/triangle-count gate documented after Goal907. The rehearsal report's claim "manifest includes the combined graph gate after Goal907" is accurate.

**Step sequence: PASS**

With `--skip-git-update` and `--skip-optix-install`, `run_one_shot()` in goal769 skips `git_fetch`, `git_checkout_branch`, and `install_optix_dev_headers`, leaving exactly: `goal763_bootstrap → goal761_run_manifest → goal762_analyze_artifacts`. Matches reported steps.

**Dry-run status logic: PASS**

In dry-run mode, `_run()` returns `{"status": "dry_run"}` for every step. The overall status expression `"ok" if not any(step["result"]["status"] == "failed" ...)` correctly evaluates to `"ok"` since no step returns `"failed"`. Same logic in goal761: `failed = [item for item in command_results if item["result"]["status"] == "failed"]` → empty → `status: ok`. Both reported results are mechanically correct.

**Bundle status: PASS**

`_tar_reports()` returns `{"status": "dry_run"}` when `dry_run=True` without writing a file. Reported `bundle status: dry_run` is correct.

**Deduplication behavior: NOTED, NOT BLOCKING**

`prepared_fixed_radius_density_summary` (outlier) and `prepared_fixed_radius_core_flags` (dbscan) share the identical command and output JSON (`goal759_outlier_dbscan_fixed_radius_rtx.json`). The second entry will show `execution_mode: "reused_command_result"` on a real pod run. This is by design — the manifest entries cover different interpretive sections of the same script output. Both `claim_scope` and `path_name` are distinct. No fix needed, but reviewer must not count them as two independent timings.

**Runbook / rehearsal alignment: PASS**

The runbook pod command carries `--include-deferred`, `--branch`, `--optix-prefix`, and `docs/reports/` output paths. The rehearsal adds `--dry-run --skip-git-update --skip-optix-install` and redirects to `build/`. All structurally significant flags are consistent. The pod command does not carry skip flags — correct.

**Pre-cloud gate: NOT RUN IN GOAL908, REQUIRED BEFORE POD**

The runbook requires `goal824_pre_cloud_rtx_readiness_gate.py` to return `"valid": true` before starting a pod. Goal908 does not run it — this is appropriate, as Goal908 is an orchestration shape check only. The requirement remains active for actual pod start.

**Minor observation: rehearsal output files use `goal907_` prefix**

`build/goal907_one_shot_dry_run.json`, `build/goal907_bundle.tgz`, etc. are labeled goal907, not goal908. These are local dry-run artifacts only and have no effect on the pod run. Cosmetic only.

**Boundary statement: PASS**

The report correctly states: "Goal908 is a dry-run orchestration check only. It does not execute OptiX workloads, does not use NVIDIA RT cores, and does not authorize any speedup claim." Nothing in the runner or manifest contradicts this.

---

### Verdict: ACCEPT

This is dry-run only. Orchestration shape is verified. The 17-entry batch (5 active + 12 deferred) is internally consistent with the manifest. The combined graph gate is present and correctly gated as deferred. The step sequence, bundle logic, and status propagation all behave correctly.

**Do not start cloud until:**
1. An RTX-class pod (RTX 4090, A5000/A6000, L4, or A10/A10G) is available and ready.
2. `goal824_pre_cloud_rtx_readiness_gate.py` returns `"valid": true` on that pod.
3. You are prepared to run the full active+deferred batch in one session without per-app restarts, per the runbook.

No code or document changes required before cloud.
