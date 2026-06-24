# Phoenix V3 M51 LibRTS Authorized-Run Runbook

Date: 2026-06-23

Status: `runbook_ready_no_run_not_authorized`

M51 prepares the operational runbook for the focused LibRTS stability run
defined by M47 and hardened by M48. It does not authorize execution. Its job is
to make any later reviewed POD run cheap, exact, and auditable rather than
improvised.

## Gate Before Any Run

Do not execute the M47 harness unless an external review returns exactly:

```text
authorize_m47_one_focused_librts_stability_pod_run
```

The authorization must name:

- one focused LibRTS stability run only;
- no all-app benchmark run;
- no V3 release;
- no public speedup wording;
- no broad V3-over-V2 claim;
- no V4, embedding, C ABI, or true-zero-copy work.

If the verdict is anything else, keep the run blocked.

## Required Inputs

The executor must identify these paths on the target machine before execution:

- current Phoenix V3 repo root;
- V2.14 comparison repo root;
- current Python executable;
- V2.14 Python executable;
- output directory under the current repo's `docs/rebuild/v3/evidence/`.

Do not infer V2.14 from the current tree. If a separate V2.14 tree is not
present, stop and record blocked setup.

## Dry-Run Command

Run this first on the target machine without `--execute`:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_m47_librts_stability_protocol.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_m51_librts_authorized_run_dry_run_YYYYMMDD_HHMMSS \
  --scenario all \
  --samples 8 \
  --seed 2025 \
  --current-root /path/to/current/repo \
  --v2-root /path/to/v2_14/repo \
  --current-python /path/to/current/python \
  --v2-python /path/to/v2_14/python \
  --command-timeout-sec 600
```

The dry-run must produce:

- `summary.json`;
- `README.md`;
- `execute=false`;
- `schedule_row_count=32`;
- `failed_check_count=0`;
- all claim-boundary flags false.

If the dry-run fails, do not execute.

## Authorized Execution Command

Only after the exact external verdict above:

```bash
PYTHONPATH=src:. python scripts/v3_phoenix_m47_librts_stability_protocol.py \
  --output-dir docs/rebuild/v3/evidence/phoenix_v3_m51_librts_authorized_run_YYYYMMDD_HHMMSS \
  --scenario all \
  --samples 8 \
  --seed 2025 \
  --current-root /path/to/current/repo \
  --v2-root /path/to/v2_14/repo \
  --current-python /path/to/current/python \
  --v2-python /path/to/v2_14/python \
  --command-timeout-sec 600 \
  --execute \
  --authorization-token M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED
```

Expected runtime:

```text
0.5 - 1.5 hours
estimated cost at $1 / 4 hours: $0.13 - $0.38
```

This estimate is not authorization.

## Required Copy-Back

Copy the entire output directory back into the current repo at the same relative
path. The directory must include:

- `summary.json`;
- `README.md`;
- `preflight_*.stdout.txt`;
- `preflight_*.stderr.txt`;
- one stdout JSON and stderr text file for each measured command.

Do not copy back only the summary. Missing per-command evidence makes the run
unreviewable.

## Intake Rules

After copy-back, read `summary.json` first.

Stop and record failure before interpreting speed if:

- `failed_check_count != 0`;
- `status` is not `m47_librts_stability_protocol_run_complete_not_release`;
- any preflight required check failed;
- any scenario has `red_failure_watch_row_open`;
- fixture/contract metadata mismatches appear;
- current runner metadata is missing;
- any claim-boundary flag is true.

If all scenarios are green closure candidates, still do not call the watch row
closed until external review accepts the copied evidence.

## Local Validation

Runbook dry-run evidence:

```text
docs/rebuild/v3/evidence/phoenix_v3_m51_librts_authorized_runbook_dry_run_20260623/
status: m47_librts_stability_protocol_dry_run_no_pod_not_release
execute: false
scenario_count: 2
sample_count_per_scenario: 8
schedule_row_count: 32
failed_check_count: 0
```

Focused gate:

```text
PYTHONPATH=src;. py -3 -m unittest tests.v3_phoenix_m51_librts_authorized_runbook_gate_test tests.v3_phoenix_review_debt_and_completion_gate_test tests.v3_phoenix_m47_librts_stability_protocol_test
Ran 14 tests
OK
```

Full V3 rebuild gate:

```text
PYTHONPATH=src;. py -3 scripts/run_test_matrix.py --group v3_rebuild
module_count: 124
Ran 638 tests in 75.925s
OK
```

This is local contract/gate evidence only, not POD evidence.

## Non-Authorization

M51 does not authorize:

- no V3 release
- no all-app benchmark run
- no paid POD spend
- no focused POD spend
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim

## Goal-Level Decision Audit

Decision: prepare an execution runbook for the already-designed LibRTS focused
stability harness without running it or authorizing POD.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   improvising the paid run later and losing evidence, or treating the runbook
   as authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Wait idle for Claude, but that wastes time while adding no safety.
4. Can I now try a different path that actually solves the problem? Yes. Make
   the future authorized run exact, copy-back-complete, and fail-closed before
   spending any POD time.
