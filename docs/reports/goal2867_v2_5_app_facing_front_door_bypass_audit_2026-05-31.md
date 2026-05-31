# Goal2867: v2.5 App-Facing Front-Door Bypass Audit

Status: accepted as a local API-surface guard.

Date: 2026-05-31

## Purpose

Goal2861 made the promoted v2.5 generic continuation operations available
through public partner-column front doors. This audit checks the next layer:
examples, app adapters, adapter packages, and benchmark harness scripts should
not bypass those APIs by calling raw `run_triton_*` helpers directly.

## Result

The audit found zero app-facing bypasses.

The only remaining raw `run_triton_*` caller in the scanned app-facing tree is:

- `scripts/goal2665_v2_5_triton_grouped_continuation_pod_runner.py`

That file is intentionally a low-level conformance runner for the original
Triton grouped-continuation preview. It is not a learner tutorial, benchmark
app implementation, or promoted app-facing harness. Keeping it as the single
exception is useful because it directly exercises the dispatcher layer beneath
the public front doors.

## Scanned Areas

- `examples/`
- `scripts/`
- `src/rtdsl/app_adapters/`
- `src/rtdsl/adapters/`

## Boundary

This is a static API-surface guard, not a release authorization, speedup claim,
package-install claim, true zero-copy claim, or benchmark-result claim.

The policy is:

- app-facing code should use the public generic front doors;
- low-level continuation preview runners may call raw Triton helpers only when
  they are clearly conformance tools, not examples for normal users.
