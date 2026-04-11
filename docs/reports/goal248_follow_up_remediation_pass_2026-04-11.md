# Goal 248 Report: Follow-Up Remediation Pass

Date: 2026-04-11
Status: implemented

## Summary

Goal 248 reduces the noisy follow-up set created by the first audit tiers.

The main pattern was clear:

- several archive files were historically useful but still carried stale local
  paths or internal host details
- one public package file was marked for duplication follow-up even though the
  broad re-export surface is intentional in `v0.4.0`
- the only truly live quality follow-up is still the native CPU/oracle build
  friction on this macOS host

## Direct Outcome

Resolved in this pass:

- `docs/handoff/CURRENT_STATUS.md`
- `docs/handoff/KEY_REPORTS.md`
- `docs/handoff/GEMINI_V0_4_RESTART_PROCESS_AUDIT_2026-04-10.md`
- `docs/reports/goal175_windows_render_status_2026-04-08.md`
- `docs/reports/goal199_fixed_radius_neighbors_cpu_oracle_2026-04-10.md`
- `src/rtdsl/__init__.py`

Still intentionally open after this pass:

- `src/rtdsl/runtime.py`
- `src/rtdsl/oracle_runtime.py`

## Why The Remaining Follow-Ups Stay Open

The remaining runtime follow-ups are not archive-noise problems. They are
environment-quality issues:

- `run_cpu(...)` depends on the native oracle path
- the native oracle build still requires a working GEOS toolchain on this macOS
  environment

Those are real supportability concerns, so they should remain visible instead
of being flattened into `pass`.

## Result

After Goal 248, the audit DB should primarily show live follow-up pressure in
the native CPU/oracle path rather than in stale archive documentation.
