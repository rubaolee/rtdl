# Phoenix V3 M55 LibRTS Authorized POD Run Intake

Date: 2026-06-23

Status: `m55_evidence_copied_back_red_watch_rows_open_pending_external_review`

## Scope

M55 executed the single M54-authorized focused LibRTS stability POD run.

Authorization source:

- `docs/reviews/codex_claude_antigravity_phoenix_v3_m54_goal_completion_3ai_consensus_2026-06-23.md`

Authorized token used exactly once:

```text
M47_FOCUSED_LIBRTS_STABILITY_AUTHORIZED
```

Run script:

```text
scripts/v3_phoenix_m47_librts_stability_protocol.py
```

## POD Environment

- Host: `2bcb58b259e4`
- GPU: `NVIDIA RTX 4000 Ada Generation`
- Driver: `550.127.05`
- Current root: `/root/rtdl_v3_rebuild_20260620/current`
- V2.14 root: `/root/rtdl_v3_rebuild_20260620/v2_14`
- Current Python: `/usr/bin/python3`
- V2.14 Python: `/usr/bin/python3`

Setup caveat:

- The current root is a pod-side benchmark tree, not a git root. The current
  git preflight is non-required and recorded stderr:
  `fatal: not a git repository (or any of the parent directories): .git`.
- The M47 harness and its test were copied into this current tree before the
  run; the benchmark app and preflight tests were already present there.

## Copy-Back Evidence

Target-machine dry-run evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339/`
- tarball:
  `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_target_dry_run_20260623_2339.tgz`
- sha256:
  `80b8fa07355ba6d45d8d294a2ee6c4c7c109a9e3af954c7fc26aa2ca589f8e81`

Execution evidence:

- `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340/`
- tarball:
  `docs/rebuild/v3/evidence/phoenix_v3_m55_librts_authorized_execution_20260623_2340.tgz`
- sha256:
  `37ae3ce65dd6d548498abf4ff71783092c2cd534c383f7ee1cf852531e1d1ac1`

Execution copy-back contents:

- file count: 80
- measured stdout JSON files: 32
- stderr/preflight text files: 38
- required `README.md`: present
- required `summary.json`: present
- driver logs: `m55_execution_driver.log`, `m55_nohup.log`

## Execution Summary

Summary status:

```text
m47_librts_stability_protocol_run_complete_not_release
```

Top-level checks:

- failed checks: `0`
- run errors: `{}`
- scenarios: `2`
- sample count per scenario: `8`
- schedule rows: `32`
- all claim-boundary booleans: false

Preflight:

- `nvidia-smi`: captured
- current Python version: captured
- V2.14 Python version: captured
- V2.14 git revision: captured
- current git revision: non-required failure because current tree is not a git
  root
- current preflight tests: `Ran 43 tests ... OK`

## Scenario Intake

| Scenario | M47 label | Geomean | Median | Min | Max | Pass count >=0.95 | First-sample-stripped geomean | First-sample-stripped median |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `optix_cold_single_shot` | `red_failure_watch_row_open` | 0.984404x | 0.979645x | 0.929253x | 1.060241x | 6/8 | 0.974022x | 0.978946x |
| `embree_32768_stress` | `red_failure_watch_row_open` | 0.931885x | 0.941006x | 0.801149x | 1.123731x | 4/8 | 0.921176x | 0.930735x |

Both scenarios are red. Do not call either watch row closed.

Primary red cause in both scenarios:

```text
current_metadata_failures: ["set_b_control_candidate_missing"]
```

Other observations:

- all measured current and V2.14 stderr files are empty;
- all fixture/contract checks match;
- no command returned a run error.

## Interpretation Boundary

This intake does not authorize or claim:

- no V3 release
- no all-app benchmark run
- no broad paid POD campaign
- no second M47 run
- no public speedup wording
- no broad V3-over-V2 claim
- no V4 work
- no embedding
- no C ABI
- no true zero-copy claim
- no watch-row closure

The correct next step is external review of this copied evidence. Any rerun,
environment repair, or metadata-fix run requires a separate authorization.

## Goal-Level Decision Audit

Decision: record M55 as a completed one-run evidence intake with both watch rows
still open/red, and request external review before any interpretation or rerun.

1. Was I foolish? No.
2. If yes, what actions made the decision foolish? The foolish action would be
   hiding the red labels, claiming closure from near-parity geomean, or rerunning
   after the metadata failure without new authorization.
3. Was there another path that would have avoided getting stuck on that idea?
   Yes. Treat the one authorized run as evidence, preserve the failure, and ask
   external review whether the missing metadata makes this a setup failure or a
   valid red result.
4. Can I now try a different path that actually solves the problem? Yes. Submit
   the copied evidence for review and only then decide whether to repair
   metadata, re-authorize a run, or leave LibRTS watch rows open.
