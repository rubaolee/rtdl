# Codex Consensus: Goal 506 v0.8 Public Entry Alignment

Date: 2026-04-17

Verdict: ACCEPT

## Reviewed Artifacts

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/docs/current_architecture.md`
- `/Users/rl2025/rtdl_python_only/tests/goal506_public_entry_v08_alignment_test.py`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal506_v0_8_public_entry_alignment_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal506_claude_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/reports/goal506_gemini_review_2026-04-17.md`
- `/Users/rl2025/rtdl_python_only/docs/handoff/GOAL506_SINGLE_SENTENCE_EXTERNAL_REVIEW_REQUEST_2026-04-17.md`

## Consensus

Codex, Claude, and Gemini agree that Goal506 fixes a real public-entry
freshness issue after Goal505:

- `README.md` now tells users that `v0.7.0` is the current released version
  while `main` also carries accepted `v0.8` app-building work.
- `docs/README.md` routes new users and ten-minute evaluators to the v0.8
  app-building tutorial.
- `docs/current_architecture.md` describes the architecture as released v0.7
  plus accepted v0.8 app-building direction on `main`.
- The three current v0.8 apps are named with their existing RTDL features:
  `knn_rows(k=1)`, `ray_triangle_hit_count`, and `fixed_radius_neighbors`.

## Boundary

No reviewed public doc claims that v0.8 is a new released support-matrix line,
new backend, or new language-internal release. The docs consistently frame
v0.8 as existing RTDL rows plus Python-owned application logic.

## Validation

Local validation passed:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal506_public_entry_v08_alignment_test tests.goal505_v0_8_app_suite_test -v
PYTHONPATH=src:. python3 -m py_compile tests/goal506_public_entry_v08_alignment_test.py
git diff --check
```

No blockers remain for treating Goal506 as the public-entry alignment layer for
the accepted v0.8 app-building work on `main`.
