# Goal 463: v0.7 Post-Demo Pre-Stage Refresh

Date: 2026-04-16

## Purpose

Refresh the v0.7 pre-stage ledger, validation gate, and dry-run staging command
plan after Goals 461 and 462 added app-facing and kernel-form DB examples.

## Scope

This goal must:

- keep staging, commit, tag, push, merge, and release authorization false
- classify `examples/` paths explicitly so demo files are not treated as
  unknown paths
- extend closed-goal validation coverage through Goal 462
- preserve Goal 439 as the intentionally open external-tester intake gate
- preserve the Goal 457 deferrals for v0.6 audit-history files
- preserve exclusion of `rtdsl_current.tar.gz`
- generate refreshed advisory JSON/CSV/Markdown artifacts
- receive 2-AI consensus before closure

## Acceptance Criteria

- The filelist ledger is valid.
- The pre-stage validation gate is valid.
- The dry-run staging command plan is valid.
- The git index remains empty.
- No staging or release action is performed.
