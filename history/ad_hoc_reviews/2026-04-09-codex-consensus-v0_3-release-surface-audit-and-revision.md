# Codex Consensus: v0.3 Release Surface Audit And Revision

Date: 2026-04-09

## Scope

This consensus reviews the executed release-surface audit captured in:

- `/Users/rl2025/rtdl_python_only/docs/reports/v0_3_release_surface_audit_and_revision_2026-04-09.md`

External review artifacts:

- Claude:
  - `/Users/rl2025/rtdl_python_only/docs/reports/claude_v0_3_release_surface_audit_review_2026-04-09.md`
- Gemini:
  - `/Users/rl2025/rtdl_python_only/docs/reports/gemini_v0_3_release_surface_audit_review_2026-04-09.md`

## Verdict

Accepted. The audit made real release-surface improvements rather than cosmetic
churn. The most important user-facing leak, `rtdl_goal10_reference.py`, is gone
from the public example chain. The `examples/` root is cleaner after moving
generated artifacts under `examples/generated/`. The tutorial and feature-home
docs are more reproducible and easier for a fresh user to trust.

## Findings

- The file-organization decisions are directionally correct:
  - top-level examples for first-run paths
  - `examples/reference/` for readable kernels
  - `examples/generated/` for preserved generated artifacts
  - `examples/visual_demo/` for RTDL-plus-Python demos
  - `examples/internal/` for historical/internal material
- The public workload reference rename was correctly propagated through:
  - runtime code
  - scripts
  - tests
  - Makefile build path
  - feature-home docs
- Claude found one minor residual docs-index duplication in `docs/README.md`.
  That was corrected in the same audit pass before closure.
- The final verification slice stayed green after the rename/move work:
  - targeted reference/runtime tests
  - example `compileall`
  - `tests.goal187_v0_3_audit_test`
  - `make build`

## Summary

This work is closed under 3-AI review. Claude and Gemini both agree that the
release surface is materially cleaner and more user-oriented. Codex agrees with
that assessment. The reviewed scope now has cleaner names, clearer locations,
and better front-door teaching without erasing the preserved historical record.
