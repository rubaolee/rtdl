# Goal 511: Feature Guide v0.8 Refresh

Date: 2026-04-17

Status: accepted with 3-AI consensus

## Scope

After Goal510 refreshed the front page, tutorials, examples, architecture, and
capability-boundary docs, one remaining public orientation page was still stale:

- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`

That guide still described the live branch as only the released bounded
`v0.7.0` package and only listed older application examples. Goal511 refreshes
it so a user who starts from the feature guide sees the same current app-building
story as the rest of the public docs.

## Files Updated

- `/Users/rl2025/rtdl_python_only/docs/rtdl_feature_guide.md`
- `/Users/rl2025/rtdl_python_only/docs/README.md`
- `/Users/rl2025/rtdl_python_only/tests/goal511_feature_guide_v08_refresh_test.py`

## Corrections Made

- The feature guide now distinguishes released `v0.7.0` from accepted `v0.8`
  app-building work on `main`.
- The feature guide now lists the three v0.8 app examples:
  - Hausdorff distance
  - robot collision screening
  - Barnes-Hut force approximation
- The feature guide now links Goal507 and Goal509 performance evidence.
- The feature guide now carries the key Goal509 boundaries:
  - robot Vulkan is not exposed until the per-edge hit-count defect is fixed
  - Barnes-Hut evidence is candidate generation plus Python force reduction,
    not full N-body acceleration
  - GTX 1070 Linux app evidence is not RT-core hardware-speedup evidence
- The docs index now routes new users through the feature guide before the
  capability-boundary page.

## Validation

Command:

```bash
PYTHONPATH=src:. python3 -m unittest tests.goal511_feature_guide_v08_refresh_test tests.goal510_app_perf_doc_refresh_test tests.goal506_public_entry_v08_alignment_test -v
```

Result: `Ran 9 tests`, `OK`.

Command:

```bash
PYTHONPATH=src:. python3 -m py_compile tests/goal511_feature_guide_v08_refresh_test.py && git diff --check
```

Result: passed.

## Current Verdict

Goal511 is accepted. The remaining high-level feature-guide staleness found
after Goal510 has been corrected without changing any released support-matrix
claim.

## AI Review Consensus

- Claude review: `PASS`; the feature guide now presents the same v0.8
  app-building story as the rest of the public docs with Goal507/Goal509
  boundaries intact.
- Gemini Flash review: `ACCEPT`.
- Codex conclusion: `ACCEPT`; Goal511 closes the public feature-guide gap
  without overclaiming release status, backend performance, robot Vulkan
  support, or full Barnes-Hut/N-body acceleration.
