# Call For Review: V3 Repair Pass 1

Date: 2026-06-20.

Reviewer: Gemini or Claude.

Requester: Codex, on behalf of the V3-only rescue work.

## Review Goal

Critically review the current V3 Repair Pass 1 state. The user does not want
another polished but weak V3. The question is whether the repaired V3 evidence,
classification, docs, and tutorials now form a credible base to continue V3, and
what must still be fixed before any public release claim.

## Files To Read

Read these files first:

```text
docs/rebuild/v3/README.md
docs/rebuild/v3/v3_design_intent_and_v2x_problem_statement_2026-06-20.md
docs/rebuild/v3/v3_current_status_2026-06-20.md
docs/rebuild/v3/v2_14_vs_v3_rebuild_pod_evidence_2026-06-20.md
docs/rebuild/v3/v3_benchmark_app_classification_2026-06-20.json
docs/rebuild/v3/v3_gpu_environment_gate_2026-06-20.md
tutorials/current/README.md
tutorials/current/01_first_run.md
tutorials/current/02_hello_world.md
tutorials/current/03_backend_choice.md
tutorials/current/04_benchmark_evidence.md
tutorials/current/05_gpu_partner_gate.md
tutorials/current/06_claim_boundaries.md
tests/v3_rebuild_evidence_classification_test.py
tests/v3_rebuild_tutorial_surface_test.py
tests/v3_gpu_python_env_gate_script_test.py
scripts/v3_gpu_python_env_gate.py
docs/handoff/CLAUDE_V3_REBUILD_TAKEOVER_HANDOFF_2026-06-20.md
```

Useful raw artifacts:

```text
docs/rebuild/v3/evidence/v3_current_goal2626_clean_env_20260620_055523/summary.json
docs/rebuild/v3/evidence/v3_current_goal2636_full_clean_20260620_060726/summary.json
docs/rebuild/v3/evidence/v3_current_goal3828_full_clean_20260620_060412/summary.json
docs/rebuild/v3/evidence/v3_gpu_python_env_gate_script_20260620_062113/summary.json
```

## Known Current Facts

- V3 is not release-authorized.
- Current-side Repair Pass 1 passed:
  - `goal2626_standard_all_rows`: 22 ok / 0 failed.
  - `goal2636_standard_all_rows`: 28 ok / 0 failed.
  - `goal3828_full_clean`: 10 pass / 0 fail.
  - GPU Python environment gate: pass.
- The initial V2.14 comparison still does not prove a broad V3-over-V2.x speed
  claim across all shared rows.
- Strong current-side OptiX-over-Embree rows exist, but claims must remain
  row-scoped.
- `librts_spatial_index` and standard all-workload `spatial_rayjoin` are
  explicitly not OptiX speedup claims.

## Questions

Please answer bluntly:

1. Does the current Repair Pass 1 evidence justify continuing V3 rather than
   deleting/restarting it?
2. Does any current doc or tutorial overclaim release readiness, V3-over-V2.x
   performance, broad RT-core acceleration, or automatic backend/partner choice?
3. Are the app classifications accurate and conservative enough?
4. Is the GPU Python environment gate sufficiently reproducible and visible?
5. What are the P0 blockers before V3 can be release-authorized?
6. What are the P1/P2 improvements that would make V3 more user-responsible?
7. Are the tests guarding the right things? What test is missing?

## Required Output Shape

Write a markdown review with:

- verdict: `accept-as-repair-base`, `accept-with-P0`, or `reject`;
- findings ordered by severity;
- concrete file/action suggestions;
- final release authorization answer.

Do not edit files during the review.
