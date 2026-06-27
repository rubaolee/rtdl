# Phoenix V3 M48 LibRTS Stability Harness Execution Safety

Date: 2026-06-23

Status: `local_harness_hardened_no_run_not_release`

M48 hardens the M47 LibRTS stability/cold-start harness so that a future
review-authorized focused POD run fails early and leaves auditable evidence
instead of silently producing ambiguous timing rows.

This is local harness work only. It does not authorize execution, paid POD,
all-app benchmarking, release, public speedup wording, broad V3-over-V2 claims,
V4 work, embedding, C ABI, or true-zero-copy claims.

## Changes

Updated:

- `scripts/v3_phoenix_m47_librts_stability_protocol.py`
- `tests/v3_phoenix_m47_librts_stability_protocol_test.py`

Behavior added:

- dry-run now emits a preflight command plan;
- authorized execution runs preflight checks before measured samples;
- preflight captures `nvidia-smi`, Python versions, Git revisions, and current
  preflight unittest modules;
- current and V2.14 measured commands execute from their own root directories;
- preflight and measured commands receive a root-specific `PYTHONPATH`
  containing `<root>/src` and `<root>`, so the harness does not depend on the
  caller's shell state;
- a command timeout is available through `--command-timeout-sec`;
- output paths are serialized relative to the repo when possible and as
  absolute paths otherwise;
- pair analysis records fixture/contract mismatches;
- current-run metadata failures force the scenario to red instead of allowing a
  green/yellow performance interpretation.

## Evidence

Dry-run packet:

```text
docs/rebuild/v3/evidence/phoenix_v3_m48_librts_stability_harness_execution_safety_dry_run_20260623/
```

Dry-run summary:

```text
status: m47_librts_stability_protocol_dry_run_no_pod_not_release
execute: false
scenario_count: 2
sample_count_per_scenario: 8
schedule_row_count: 32
failed_check_count: 0
release_authorized: false
all_app_pod_spend_authorized: false
focused_pod_spend_authorized_now: false
public_speedup_claim_authorized: false
broad_v3_faster_than_v2_claim_authorized: false
v4_work_authorized: false
```

Focused validation:

```text
PYTHONPATH=src;. py -3 -m unittest \
  tests.v3_phoenix_m47_librts_stability_protocol_test \
  tests.v3_phoenix_review_debt_and_completion_gate_test \
  tests.v3_phoenix_librts_aabb_count_runner_test

Ran 15 tests
OK
```

Compile validation:

```text
PYTHONPATH=src;. py -3 -m py_compile scripts/v3_phoenix_m47_librts_stability_protocol.py
```

Full local V3 rebuild matrix:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 122
Ran 632 tests in 75.022s
OK
```

Whitespace validation:

```text
git diff --check -- scripts/v3_phoenix_m47_librts_stability_protocol.py \
  tests/v3_phoenix_m47_librts_stability_protocol_test.py \
  tests/v3_phoenix_review_debt_and_completion_gate_test.py
```

Result: no whitespace errors.

## Interpretation

M48 improves the quality of a future focused LibRTS stability run, but it does
not change the current authorization state:

- M47 focused LibRTS run is still not authorized.
- All-app POD is still not authorized.
- V3 release is still not authorized.
- M44 goal completion still waits for Claude as the third completion-audit
  seat.

## Non-Authorization

This report does not authorize:

- V3 release
- all-app benchmark run
- paid POD spend
- public speedup wording
- broad V3-over-V2 claim
- V4 work
- embedding
- C ABI
- true zero-copy claim

## Goal-Level Decision Audit

Decision: harden the M47 LibRTS stability harness locally while Claude is
unavailable, without executing the focused run.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   waiting idle for Claude or running POD without execution-safety checks.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Prepare the harness so that a later reviewed run is cleaner, cheaper,
   and harder to misinterpret.
4. Can I now try a different path that actually solves the problem? Yes. Keep
   the run blocked until external review, but make the eventual run protocol
   more reliable and auditable.
