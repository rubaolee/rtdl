# Claude Review: Goal3844 Current Scale-Profile Refresh

Date: 2026-06-08

Reviewer: Claude (independent read-only review)

Verdict: **accept-with-boundary**

## Summary

Goal3844 is an A5000 re-run of the ten promoted current-benchmark
scale-profile rows after Goal3842's RayJoin PIP batch-executor update. I
independently inspected the report, `summary.json`, every per-row
`stdout.json`/`stderr.txt` artifact, the pod stdout/stderr logs, the runner
script (`scripts/goal3828_current_benchmark_scale_profile_runner.py`), the
profile registry (`src/rtdsl/current_benchmark_scale_profiles.py`), and
`tests/goal3844_current_scale_profile_refresh_test.py`. The artifact is
internally consistent, the claim-boundary mechanism is fail-closed, and the
report's framing matches what the evidence actually shows.

## Findings (ordered by severity)

No correctness or honesty issues found. Notes below are confirmations, not
defects.

1. **(Info) All ten promoted rows pass with matching evidence.** `summary.json`
   reports `all_pass=true`, `json_pass_count=10`, `row_count=10`, and every row
   has `status="pass"`, `returncode=0`, `stderr_bytes=0`, and a parseable
   stdout JSON. I independently grepped every `outputs/*.stdout.json` file for
   the full `FORBIDDEN_TRUE_FLAGS` set used by the runner
   (`release_authorized`, `public_speedup_claim_authorized`,
   `broad_rt_core_claim_authorized`, `paper_reproduction_claim_authorized`,
   `true_zero_copy_authorized`, `whole_app_speedup_claim_authorized`,
   `automatic_partner_selection_authorized`, `rt_core_speedup_claim_authorized`,
   etc.) set to `true` and found zero matches across all twenty output files —
   independently corroborating `claim_flag_violations: []` for every row. The
   set of apps in `summary.json["rows"]` exactly matches
   `V2_8_PROMOTED_BENCHMARK_APPS` (`src/rtdsl/v2_8_benchmark_runtime_gap.py:12-23`).

2. **(Info) The report's framing is accurate, not a release/public-speedup
   claim.** `docs/reports/goal3844_current_scale_profile_refresh_2026-06-08.md`
   states up front "Status: internal evidence packet, not release
   authorization" and "This is not a new public speedup table. It is a health
   and readiness evidence packet." The artifact backs this: top-level
   `release_authorized`, `public_speedup_claim_authorized`,
   `broad_rt_core_claim_authorized`, and `paper_reproduction_claim_authorized`
   are all `false`, and the `claim_boundary` string is the same fail-closed
   non-authorizing text used by the Goal3828 registry
   (`rtdl.v2_10.current_benchmark_scale_profiles.goal3828.v1`).

3. **(Info) Claim-boundary checks remain fail-closed at both levels.** The
   runner (`scripts/goal3828_current_benchmark_scale_profile_runner.py:22-39,
   59-97, 160-165`) recursively scans every parsed stdout JSON payload for any
   of sixteen forbidden flags being `true` and marks the row `fail` if any
   appear or if the JSON fails to parse — this is a structural, code-level
   guarantee, not a hand-curated claim. The top-level `result` dict
   (`runner.py:228-231`) hardcodes the four release/claim flags to `false`
   regardless of row outcomes, so a clean run cannot silently flip them to
   `true`. `validation.status == "accept"` with `errors: []` confirms the
   registry itself passed `validate_current_benchmark_scale_profiles()`.

4. **(Info) Numba rows (`rt_dbscan`, `barnes_hut`) are present and honestly
   scoped.** Both rows appear with `status=pass`:
   - `rt_dbscan_optix_numba_scale_default_65536_no_validation`: I read the full
     `metadata` block in the stdout artifact directly. It shows
     `partner="numba"`, `optix_backend_used=true`,
     `raw_cuda_kernel_required=false`,
     `whole_app_speedup_claim_authorized=false`,
     `rt_core_speedup_claim_authorized=false`, and
     `paper_speedup_claim_authorized=false` — consistent with an OptiX
     RT-core threshold pass feeding a Numba prepared-grid component
     continuation, not a raw-CUDA or whole-app speedup claim.
   - `barnes_hut_numba_scale_default_8192`: `output_mode="force_summary"`,
     `rt_core_accelerated=false`, and an explicit `boundary` string stating
     "this is not Barnes-Hut tree opening acceleration and not an RT-core
     claim." This is the exact-force partner-reference path, scoped honestly.

5. **(Info) Pod artifact-backup handling is non-destructive and verifiable.**
   The report states an untracked old Goal3842 artifact blocked
   `git pull --ff-only`, was moved into a timestamped pod backup, and "nothing
   was deleted." The pod stdout log
   (`pod_goal3844_scale_profiles.stdout.log:3`) directly corroborates this with
   `[goal3844] moved untracked artifact to
   /root/rtdl_pod_untracked_backup_goal3844_20260608_011002` followed by a
   successful fast-forward (`Updating 09a31f30..ad4bea28` / `Fast-forward`).
   This is a `mv`-style relocation to a timestamped path, not a delete.

6. **(Info) Execution-context claims in the report check out against the pod
   log.**
   - Commit: report says `ad4bea28960f`; `git log -1 --format=%H ad4bea28`
     resolves to the full hash `ad4bea28960f743bc2617a172447e1cc494e9181`, and
     the pod log prints `[goal3844] commit ad4bea28960f`.
   - `timeout-scale=1.25`: the pod log prints the *pre-scale* registry timeouts
     at row start (e.g., `hausdorff_xhd ... timeout=180s`,
     `spatial_rayjoin ... timeout=240s`, `rt_dbscan ... timeout=120s`), while
     `summary.json` records the *scaled* `timeout_sec` values for the same rows
     (225, 300, 150 respectively). 180×1.25=225, 240×1.25=300, 120×1.25=150 —
     exactly consistent with `--timeout-scale=1.25` as stated.
   - `file-backed stdout`: confirmed by `stdout_policy:
     "file_backed_stdout_required"` on every row plus the on-disk
     `outputs/*.stdout.json` / `*.stderr.txt` files the runner writes via
     `subprocess.Popen(..., stdout=stdout_file, stderr=stderr_file)`
     (`runner.py:123-133`).

## Boundary (if accepted)

This is internal current-main A5000 scale-profile health evidence for the ten
promoted benchmark apps after the Goal3842 RayJoin PIP batch-executor update.
It is **not**: release authorization, a public speedup claim, paper
reproduction, a broad RT-core claim, true-zero-copy wording, package-install
readiness wording, automatic partner/backend selection, or app-specific
native-engine logic. It does not settle the v2.x benchmark-performance
direction — only that the current benchmark-app surface still runs coherently
together at calibrated default scale on this hardware.
