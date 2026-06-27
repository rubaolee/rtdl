# Phoenix V3 M21 All-App POD Protocol

Status: `protocol_prepared_external_review_required_no_run`

This is the protocol for a serious same-RT-hardware V2.14 vs current Phoenix V3 all-app paired POD run. It does not authorize the run. It does not authorize release. It does not authorize public V3-over-V2 speedup claims.

```text
source_external_verdict: authorize_m20_all_app_protocol_preparation_no_run
all_app_pod_run_authorized_now: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
release_based_on_all_app_run_outcome: false
```

## Non-Release Header

No outcome of this all-app paired run, including full clearance of Barnes-Hut and LibRTS Embree AABB blocking bars, constitutes release authorization or public V3-over-V2 speedup authorization.

The purpose of the run is narrower: test whether the focused fixes transfer into the full all-app context and whether the frozen blockers clear under the same serious paired benchmark conditions.

## Resource Estimate

Previous serious paired run: `phoenix_v3_serious_v2x_paired_20260622_074100`, about 5.78 hours.

Expected if later authorized: 5.5-7.0 POD hours. Hard cap before a new review: 8.0 hours. At USD 1 per 4 hours, expected cost is about USD 1.38-1.75, hard cap about USD 2.00.

This M21 protocol/review work itself does not start the long POD run.

## Frozen Scope

The run must use the frozen classification and case whitelist from:

`docs/rebuild/v3/phoenix_v3_set_a_set_b_classification_2026-06-22.json`

Unknown `app_id`, unknown `case_id`, newly introduced benchmark rows, or reclassified rows make the run out-of-scope until a separate preregistration review approves the change.

Frozen app classification:

| App | Set |
| --- | --- |
| `barnes_hut` | A |
| `hausdorff_xhd` | A |
| `rt_dbscan` | A |
| `rtnn` | A |
| `spatial_rayjoin` | A |
| `triangle_counting` | A |
| `contact_manifold` | B |
| `librts_spatial_index` | B |
| `raydb_style` | B |
| `robot_collision` | B |

The focused productized material probe precondition is closed at 3/2:

```text
aabb_runner_m2_1
hausdorff_threshold_runner_m5_after_m6_1
triangle_m19_env_corrected_productized_runner
```

## Hardware Gate

Required hardware:

```text
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute capability: 8.9
remote base: /root/rtdl_v3_rebuild_20260620
project venv: /root/rtdl_v3_rebuild_20260620/.venv/bin/python
ssh key: C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

A different GPU or driver requires a new hardware-gate review before this protocol may proceed.
The runner exits `67` before benchmarks if GPU name, driver, or compute capability differ from the required values.

Latest no-benchmark POD preflight:

```text
status: pass
scope: ssh/GPU/venv/import check only; no benchmark run
hostname: 2bcb58b259e4
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute capability: 8.9
python: /root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy: 14.1.1
numba: 0.65.1
all_app_pod_run_started: false
```

## Interpreter Gate

The paired runner now uses `PYTHON_BIN` or `/root/rtdl_v3_rebuild_20260620/.venv/bin/python` explicitly. It fails before any benchmark starts if the interpreter is missing or if `sys.executable` does not resolve to the project venv binary.

Required prelaunch checks:

```text
python_bin exists and is executable
sys.executable realpath equals /root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy import succeeds under the same interpreter
numba import succeeds under the same interpreter
all suite subprocesses are launched through the same python_bin
benchmark child helpers for goal2626/goal2636 and goal3828 resolve harmless child probes to the same python_bin
```

Fail exit codes:

```text
65 = missing or non-executable project venv interpreter
66 = sys.executable mismatch
67 = GPU name / driver / compute capability mismatch
68 = required CuPy/Numba import failure under project venv
69 = benchmark child interpreter mismatch
```

## Command If Later Authorized

Do not run this command until M21 external review explicitly authorizes the run.

```bash
cd /root/rtdl_v3_rebuild_20260620/current &&
PHOENIX_V3_ALLOW_ALL_APP_RUN=1 \
PHOENIX_V3_RUNTIME_TRUNK_EXECUTED=1 \
BASE=/root/rtdl_v3_rebuild_20260620 \
PYTHON_BIN=/root/rtdl_v3_rebuild_20260620/.venv/bin/python \
RUN_ID=phoenix_v3_m21_all_app_paired_$(date -u +%Y%m%d_%H%M%S) \
bash scripts/phoenix_v3_serious_paired_v2x_runner.sh
```

After artifact copy:

```powershell
py -3 scripts/phoenix_v3_serious_v2x_paired_analysis.py <copied_run_dir> --json-out docs/rebuild/v3/evidence/<run_id>/summary.json --md-out docs/rebuild/v3/evidence/<run_id>/summary.md
```

Then run the M21 protocol gate:

```powershell
py -3 scripts/v3_phoenix_m21_all_app_protocol_gate.py --summary docs/rebuild/v3/evidence/<run_id>/summary.json --protocol docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json --json-out docs/rebuild/v3/evidence/<run_id>/m21_protocol_gate.json --markdown-out docs/rebuild/v3/evidence/<run_id>/m21_protocol_gate.md --pretty
```

This gate is the run-result interpreter for M21. The older Set-A/B scorecard gate remains useful for the frozen baseline, but it is not the M21 future-run verdict.

## Correctness Gate

Performance rows are accepted only after correctness.

```text
all required suites must exit rc=0 for both v2_14 and current
goal2626_large rows must have status=ok
goal2636_stress rows must have status=ok
goal3828_full rows must have status=pass
primary_metric_source_mismatch_count must be 0
missing_promoted_apps must be empty
any required app correctness/oracle failure invalidates that app's rows and fails the protocol
```

Required suites:

```text
goal2626_large
goal2636_stress
goal3828_full
```

## Fail-Closed Bars

These are hard failure conditions. No after-the-fact explanation may convert them to success.

| Bar | Fail Condition | Result |
| --- | --- | --- |
| Barnes-Hut app geomean | `< 0.90x` | protocol FAIL |
| `goal2626_large|librts_spatial_index|aabb_index_all_count_only|embree|librts_embree_aabb_index` | `< 0.95x` | protocol FAIL |
| Set-B geomean | `< 0.98x` | protocol FAIL |
| Any new app-level severe regression | `< 0.90x` | protocol FAIL |

These values must be reported exactly, but they are not pass/fail thresholds for this evidence run:

```text
Set-A geomean V3 vs V2.14
Set-A app count over 1.05x
overall geomean V3 vs V2.14
```

Reason: the M8 projection already says that even full blocker clearance is likely still below the release bar. This run can clear blockers and advance the scorecard baseline, but it cannot itself authorize release.

## Watch Row

`goal2626_large|librts_spatial_index|aabb_index_all_count_only|optix|librts_optix_aabb_index`

Current frozen scorecard: `1.0103352224861961x`.

This row is not the current blocking row and is not the main fail bar. It is an unstable/inconclusive watch row. If it falls below `0.95x`, it must be flagged and reported without rationalization.

## Post-Run Interpretation

If all fail-closed bars clear:

```text
blocking bars cleared; scorecard baseline advances; release remains not authorized; public V3-over-V2 speedup claims remain unauthorized
```

If any fail-closed bar fails:

```text
protocol fail; no further all-app POD run before local or focused corrective work plus renewed external review
```

If case scope or correctness gates fail:

```text
run invalid/out-of-scope for performance claims
```

## Goal-Level Decision Audit

1. Was I foolish?

No for this decision.

2. If yes, what actions made the decision foolish?

It would be foolish to spend 5.5-7 POD hours before freezing case IDs, interpreter, hardware, correctness gates, fail bars, and the post-run protocol evaluator.

3. Was there another path?

Run all-app immediately because three focused probes are closed. That would repeat the earlier pattern of measuring first and arguing after.

4. Can I now try a different path?

Yes. Submit this protocol for external authorization first; only run if the review explicitly authorizes the run and accepts the non-release boundary.
