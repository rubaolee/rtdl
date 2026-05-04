# Goal1251 v1.0 Full Local Discovery

Date: 2026-05-04

## Summary

- verdict: `PASS`
- command: `PYTHONPATH=src:. python3 -m unittest discover -s tests -p '*_test.py' -v`
- tests run: `2422`
- skipped: `196`
- failures: `0`
- errors: `0`
- runtime: `166.940s`
- pod needed now: `False`

## Context

This run follows the Goal1248 v1.0 release-candidate package, the Goal1249
release-candidate audit gate, and the Goal1250 release-surface documentation
audit. The earlier full-discovery attempt exposed stale historical audit
expectations that still required detailed public-speedup phrases on the slim
front page. Those expectations were repaired so the root README keeps a concise
front-page role while detailed claim boundaries remain in source-of-truth
status documents.

## Repaired Stale Audit Expectations

The following historical audit gates were adjusted before this full discovery:

- `scripts/goal1024_final_public_surface_audit.py`
- `scripts/goal1186_current_release_readiness_after_goal1185_audit.py`
- `scripts/goal1210_v0_9_8_release_readiness_audit.py`
- `tests/goal1186_current_release_readiness_after_goal1185_audit_test.py`

The repair does not remove the underlying public-claim boundary. It moves
detailed phrases out of the root front page and into the dedicated status pages
that already carry the detailed RTX wording boundaries, especially
`docs/v1_0_rtx_app_status.md`.

## Focused Preflight

Before the full discovery run, these focused checks passed:

- stale historical audit repair modules: `10` tests OK
- current v1.0 release/package/public-doc gates: `22` tests OK

## Full Discovery Result

The full local discovery run completed successfully:

```text
----------------------------------------------------------------------
Ran 2422 tests in 166.940s

OK (skipped=196)
```

Expected local skips include unavailable local GPU backend libraries such as
OptiX and Vulkan on the macOS development machine. Those skips are not new v1.0
release blockers because the release-candidate package is local documentation
and correctness readiness evidence, not fresh NVIDIA public-speedup promotion.

## Release Boundary

This report does not release v1.0, update `VERSION`, authorize a tag, or
authorize new public speedup wording. `VERSION` remains `v0.9.8` until final
release authorization. A pod is not needed for this local release-readiness
gate; use a pod only if new RTX evidence is needed or a blocked/not-reviewed
row is promoted into public speedup wording.

## Recommendation

Current main has passed the full local discovery gate needed for final v1.0
release-candidate review. The next step is external review and two-AI consensus
for this Goal1251 evidence, then final release authorization if no blocker is
raised.
