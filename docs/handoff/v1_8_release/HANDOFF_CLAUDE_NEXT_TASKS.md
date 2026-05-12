# Handoff: Claude Next Task

Claude is currently out; when available again, pick up only after reviewing
Goal1708 and Gemini's follow-up review if present.

## Current State

The tracked native ABI cleanup is structurally complete, the Goal1707 truncated
Embree files were recovered, and Goal1708 added a local guard for the recovery:

- `docs/reports/goal1708_source_recovery_and_semantic_cleanup_2026-05-11.md`
- `tests/goal1708_source_recovery_and_semantic_cleanup_test.py`

The focused migration gates pass locally. The remaining release blocker is pod
or hardware execution evidence plus the local Windows SDK/UCRT toolchain issue
that prevents `tests.goal903_embree_graph_ray_traversal_test` from completing
because Oracle native summary helpers fail to build.

## Task

Do a read-first toolchain/pod validation triage, not another source rename.

1. Verify the local toolchain failure from `tests.goal903_embree_graph_ray_traversal_test`.
2. Determine whether `RTDL_VCVARS64` / Visual Studio environment setup can fix
   the Oracle build locally.
3. If pod access is available, run the minimal hardware validation slice for
   Embree/oracle summaries and then the broader v1.8 native gate.
4. Record exact commands, environment, pass/fail result, and any remaining
   blocker without overclaiming release readiness.

## Boundaries

- Preserve Python compatibility names for public app/demo APIs.
- Keep native C ABI generic and app-agnostic.
- Do not touch `docs/reports/goal1204_rtdl_source_2026-05-01.tar.gz`.
- Do not overclaim release readiness.

## Output

If validating, write:

- `docs/reports/goal1710_pod_or_toolchain_validation_after_source_recovery_2026-05-11.md`

If only planning, write:

- `docs/reviews/goal1710_claude_toolchain_pod_validation_plan_2026-05-11.md`

Verdict must remain `needs-more-evidence` unless hardware execution evidence is
actually produced and independently reviewed.
