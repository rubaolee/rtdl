# Phoenix V3 M21 All-App POD Protocol Report

Status: `protocol_prepared_external_review_required_no_run`

I prepared the M21 all-app POD protocol packet and patched the serious paired runner so it explicitly uses the project venv interpreter instead of relying on `python3` through `PATH`.

Artifacts:

```text
docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.json
docs/rebuild/v3/phoenix_v3_m21_all_app_pod_protocol_2026-06-23.md
scripts/phoenix_v3_serious_paired_v2x_runner.sh
scripts/v3_phoenix_m21_all_app_protocol_gate.py
```

The protocol follows the M20 Claude verdict:

```text
all_app_pod_run_authorized_now: false
release_authorized: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
```

## What Changed

The runner now has a fail-closed interpreter preflight:

```text
PYTHON_BIN defaults to /root/rtdl_v3_rebuild_20260620/.venv/bin/python
exit 65 if the venv interpreter is missing or not executable
exit 66 if sys.executable does not resolve to the venv interpreter
exit 67 if GPU name / driver / compute capability differ from the required RTX 4000 Ada pod
exit 68 if CuPy or Numba cannot import under the same venv interpreter
all three benchmark suites are launched through the same python_bin
```

This directly addresses the M18/M19 wrong-interpreter failure mode.

I also added a dedicated M21 protocol gate:

```text
scripts/v3_phoenix_m21_all_app_protocol_gate.py
```

It evaluates a completed paired-run `summary.json` against the M21 protocol instead of reusing the older baseline-oriented Set-A/B gate. This matters because the older gate was written to describe the current failure baseline; the M21 gate is written to decide whether a future run cleared or failed the frozen bars.

POD access uses the historical working key:

```text
C:\Users\Lestat\.ssh\id_ed25519_rtdl_codex_current_pod
```

Latest no-benchmark POD preflight:

```text
status: pass
hostname: 2bcb58b259e4
GPU: NVIDIA RTX 4000 Ada Generation
driver: 550.127.05
compute capability: 8.9
python: /root/rtdl_v3_rebuild_20260620/.venv/bin/python
cupy: 14.1.1
numba: 0.65.1
all_app_pod_run_started: false
```

## Protocol Bars

Hard fail conditions:

| Bar | Fail Condition |
| --- | --- |
| Barnes-Hut app geomean | `< 0.90x` |
| `librts_embree_aabb_index` row | `< 0.95x` |
| Set-B geomean | `< 0.98x` |
| Any new app-level severe regression | `< 0.90x` |

Documented but not pass/fail for this evidence run:

```text
Set-A geomean V3 vs V2.14
Set-A apps over 1.05x
overall geomean V3 vs V2.14
```

## Resource Estimate

If later authorized, one all-app POD run is estimated at 5.5-7.0 hours, with an 8.0 hour hard cap before new review. At USD 1 per 4 hours, that is about USD 1.38-1.75 expected, USD 2.00 hard cap.

## Current Boundary

This protocol does not authorize a POD run. The next step is external review. Only a clear M21 authorization verdict can unlock the all-app run.

## Goal-Level Decision Audit

1. Was I foolish?

No for this decision.

2. If yes, what actions made the decision foolish?

It would be foolish to start a long all-app POD run before freezing the failure bars, interpreter checks, and post-run evaluator.

3. Was there another path?

Yes: immediately run all-app now that the focused probe precondition is closed. That path risks wasting POD and producing another ambiguous result.

4. Can I now try a different path?

Yes: gate the run through a written protocol and external authorization first.
