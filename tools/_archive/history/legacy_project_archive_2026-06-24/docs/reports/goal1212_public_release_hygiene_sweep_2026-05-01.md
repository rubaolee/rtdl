# Goal1212 Public Release-Hygiene Sweep

Date: 2026-05-01

## Purpose

This checkpoint records a broader local public/release-hygiene sweep after
Goal1211. It complements the Goal1211 focused Goal1204-Goal1210 smoke by
checking higher-level public docs, historical release drift, command truth,
public examples, and consensus audit surfaces.

This is still a local audit checkpoint. It does not tag, publish, or authorize
v0.9.8.

## Primary Command

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1024_final_public_surface_audit_test \
  tests.goal1022_history_release_drift_audit_test \
  tests.goal515_public_command_truth_audit_test \
  tests.goal512_public_doc_smoke_audit_test \
  tests.goal513_public_example_smoke_test \
  tests.goal646_public_release_hygiene_test \
  tests.goal821_public_docs_require_rt_core_test \
  tests.goal707_app_rt_core_redline_audit_test \
  tests.goal1139_current_window_consensus_audit_test \
  tests.goal1120_recent_goal_consensus_audit_test \
  tests.goal1017_recent_goal_consensus_audit_test \
  -v
```

## Primary Result

The command included an operator typo: `tests.goal646_public_release_hygiene_test`
does not exist. The intended module is
`tests.goal648_public_release_hygiene_test`.

Observed result:

- Product/audit tests run before and after the typo: `25`
- Product/audit test result: `OK`
- Invocation error: `ModuleNotFoundError` for the nonexistent
  `tests.goal646_public_release_hygiene_test`

The invocation error is not evidence of a product or documentation failure.

## Corrected Command

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal648_public_release_hygiene_test -v
```

## Corrected Result

- Tests run: `3`
- Result: `OK`

## Effective Coverage

The completed sweep covered:

- final public-surface audit,
- history/release drift audit,
- public command truth audit,
- public markdown link smoke,
- public example smoke,
- public release-hygiene checks,
- public `--require-rt-core` documentation boundary,
- RT-core redline app audit,
- current-window consensus audit,
- recent-goal consensus trail audits.

## Boundary

This checkpoint records local public/release-hygiene evidence only. It does not
replace a full project test run, a fresh RTX pod replay, final release
authorization, or package/tag creation.
