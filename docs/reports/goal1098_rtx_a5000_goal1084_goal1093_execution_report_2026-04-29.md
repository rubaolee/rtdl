# Goal1098 RTX A5000 Goal1084/Goal1093 Execution Report

Date: 2026-04-29

## Scope

Goal1098 records the RTX A5000 pod execution for the current post-Goal1094 evidence path:

- Goal1084 facility recentered same-scale validation/timing;
- Goal1093 Barnes-Hut depth-8 validation;
- Goal1093 Barnes-Hut depth-8 20M timing-only repeat;
- Goal1096 local artifact intake after copyback.

This report is evidence intake only. It does not authorize public wording, release, or public RTX speedup claims.

## Environment

| Field | Value |
| --- | --- |
| Pod SSH | `root@194.68.245.13 -p 22061` |
| GPU | NVIDIA RTX A5000, 24,564 MiB |
| Driver | 565.57.01 |
| CUDA toolkit | `/usr/local/cuda-12.4`, `nvcc` 12.4.131 |
| OptiX headers | `/workspace/vendor/optix-dev-8.0.0`, NVIDIA `optix-dev` tag `v8.0.0` |
| Source commit | `58ca06f2573d53754663a2dd10a76207113ab044` |
| Checkout method | `git archive` staged to `/workspace/rtdl_python_only` plus `.rtdl_source_commit` |

GEOS was installed on the pod with `apt-get install libgeos-dev`. The first OptiX build linked without `-lgeos_c` and failed a tiny runtime smoke with `undefined symbol: GEOSPreparedGeom_destroy_r`. The backend was rebuilt with `GEOS_LIBS="-lgeos_c"`, after which the tiny facility recentered OptiX smoke passed.

## Artifact Results

| Artifact | Validation | Median OptiX Query | Status |
| --- | --- | ---: | --- |
| `docs/reports/goal1084_facility_recentered_rtx_pod_packet/facility_recentered_coverage_threshold_2_5m_optix_validation.json` | `matches_oracle: true`, 10,000,000 / 10,000,000 covered | `0.13505441695451736` sec | Passed parity and 100 ms floor |
| `docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_4096_validation.json` | `matches_oracle: true`, depth 8, 65,536 nodes | `0.007581695914268494` sec | Passed validation row |
| `docs/reports/goal1093_barnes_hut_20m_contract/barnes_hut_depth8_20m_timing.json` | timing-only with `--skip-validation`, 20,000,000 / 20,000,000 threshold reached | `0.23063642531633377` sec | Passed 100 ms timing floor |

The Goal887 profiler did not embed `source_commit` in its JSON payloads during this pod run. The runner logs recorded the source commit, and Codex stamped the three copied artifacts with the same commit from `.rtdl_source_commit`, adding `source_commit_note` without changing timing or result fields. A follow-up local patch now makes Goal887 embed `source_commit` directly for future runs.

## Intake

After copying back the Goal1084 directory, Goal1093 directory, cloud session logs, and bootstrap artifact, Codex ran:

```bash
PYTHONPATH=src:. python3 scripts/goal1096_current_rtx_pod_artifact_intake.py
PYTHONPATH=src:. python3 -m unittest tests.goal1096_current_rtx_pod_artifact_intake_test tests.goal1097_runbook_goal1096_sync_audit_test
```

Results:

- Goal1096 intake: `overall_status: ready_for_2ai_review_not_public_claim`, `valid: true`
- Local tests: 11 tests, OK
- Present artifacts: 3 / 3
- Blocked rows: 0
- Public speedup claims authorized: 0

## Copied Evidence

- `docs/reports/goal763_rtx_cloud_bootstrap_check_goal1098.json`
- `docs/reports/cloud_session_2026_04_29/env_goal1098.txt`
- `docs/reports/cloud_session_2026_04_29/goal1084_runner.log`
- `docs/reports/cloud_session_2026_04_29/goal1093_runner.log`
- `docs/reports/goal1084_facility_recentered_rtx_pod_packet/`
- `docs/reports/goal1093_barnes_hut_20m_contract/`
- `docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.json`
- `docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.md`

## Boundary

The copied artifacts are engineering evidence that passed local intake and now require 2+ AI review. This report does not claim whole-app speedup, does not compare against baselines, does not authorize public README/front-page wording, and does not authorize a release.
