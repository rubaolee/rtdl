# Handoff: Review Goal4285-4286 Pod Driver Hardening

Please perform a read-only external review of the latest RTDL `main` work for
Goal4285 and Goal4286.

## Scope

- Goal4285: genericized the OptiX SDK candidate list in
  `scripts/rtdl_pod_bootstrap_probe.py` by replacing a developer-specific
  `/home/lestat/vendor/optix-dev` path with `$HOME/vendor/optix-dev` via
  `Path.home() / "vendor" / "optix-dev"`, and updated the runbook/tests.
- Goal4286: added `scripts/rtdl_remote_pod_validation_driver.py`, a dry-run-by-
  default SSH driver for v2.10 pod validation. It uses a fresh remote `mktemp`
  checkout, prints progress markers, runs the bootstrap probe, optionally builds
  OptiX, then runs the v2.10 validation bundle.

## Files To Inspect

- `scripts/rtdl_pod_bootstrap_probe.py`
- `docs/audit/runbooks/v2_10_pod_bootstrap_probe.md`
- `tests/goal4281_pod_bootstrap_probe_test.py`
- `docs/reports/goal4285_pod_probe_generic_optix_candidate_2026-06-11.md`
- `tests/goal4285_pod_probe_generic_optix_candidate_test.py`
- `scripts/rtdl_remote_pod_validation_driver.py`
- `docs/audit/runbooks/v2_10_remote_pod_validation_driver.md`
- `docs/audit/runbooks/v2_10_pod_validation_bundle.md`
- `docs/reports/goal4286_remote_pod_validation_driver_2026-06-11.md`
- `tests/goal4286_remote_pod_validation_driver_test.py`

## Questions

1. Does Goal4285 close the machine-specific OptiX path concern without making
   the probe less useful on local Linux or pods?
2. Is the Goal4286 remote driver safe by default, especially regarding dry-run
   behavior, fresh checkout use, progress output, and no destructive commands?
3. Are the claim boundaries still intact: no release authorization, no
   package-install claim, no broad RT-core or whole-app speedup claim?
4. Are the tests enough for this local tooling layer before a real pod run?
5. What must be fixed before using this driver on the next NVIDIA pod?

## Expected Output

Write one review file:

- Claude:
  `docs/reviews/goal4287_claude_review_goal4285_4286_pod_driver_2026-06-11.md`
- Gemini:
  `docs/reviews/goal4288_gemini_review_goal4285_4286_pod_driver_2026-06-11.md`

Use one of: `accept`, `accept-with-boundary`, `needs-more-evidence`, `reject`.
This is a tooling review only. Do not move tags, run pod hardware validation,
or authorize release/performance claims.
