# Goal 508: Hausdorff Performance Public Doc Refresh

Date: 2026-04-17

Status: accepted by external AI review and Codex consensus

Version line: `v0.8` app-building documentation refresh after Goal507

## Purpose

Goal507 added Linux performance evidence for the Hausdorff app across RTDL
Embree, OptiX, Vulkan, SciPy `cKDTree`, scikit-learn `NearestNeighbors`, and
FAISS `IndexFlatL2`. Goal508 updates the public docs that real users see so the
new evidence is discoverable and the performance boundary is not overstated.

## Public Docs Updated

- `/Users/rl2025/rtdl_python_only/README.md`
- `/Users/rl2025/rtdl_python_only/docs/release_facing_examples.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/nearest_neighbor_workloads.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/feature_quickstart_cookbook.md`
- `/Users/rl2025/rtdl_python_only/docs/tutorials/v0_8_app_building.md`

## What Changed

- The front page now links the Goal507 Hausdorff Linux performance evidence.
- Release-facing examples now show Linux `embree`, `optix`, and `vulkan`
  commands for the Hausdorff app.
- The stale nearest-neighbor CLI boundary was corrected:
  - `rtdl_fixed_radius_neighbors.py` and `rtdl_knn_rows.py` still expose only
    `cpu_python_reference`, `cpu`, and `embree`;
  - `rtdl_hausdorff_distance_app.py` now exposes `embree`, `optix`, and
    `vulkan`;
  - users are warned not to generalize the Hausdorff app-specific GPU CLI path
    to every nearest-neighbor example script.
- The nearest-neighbor tutorial, cookbook, and v0.8 app-building tutorial now
  link the Goal507 report and state the bounded result.

## Honesty Boundary

The public docs now state the exact bounded readout:

- RTDL OptiX/Vulkan beat RTDL Embree for the Hausdorff app on the measured Linux
  host.
- RTDL does not beat the strongest mature exact 2D nearest-neighbor library
  baselines in the Goal507 evidence.
- The Goal507 GTX 1070 evidence is not an RT-core acceleration claim.
- The Hausdorff app-specific OptiX/Vulkan CLI support is not a release claim for
  all nearest-neighbor example scripts.

## Regression Test

New test:

- `/Users/rl2025/rtdl_python_only/tests/goal508_hausdorff_perf_doc_refresh_test.py`

It verifies that:

- release-facing examples mention Hausdorff `optix` and `vulkan` commands;
- the stale top-level nearest-neighbor CLI boundary is replaced with the
  corrected app-specific statement;
- nearest-neighbor tutorial and v0.8 app tutorial link the Goal507 report;
- front page and cookbook expose the bounded performance evidence and do not
  claim RTDL beats the strongest mature baselines.

## Validation

Command:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal508_hausdorff_perf_doc_refresh_test tests.goal507_hausdorff_perf_harness_test -v
```

Result:

```text
Ran 5 tests in 0.108s
OK (skipped=1)
```

Command:

```text
PYTHONPATH=src:. python3 -m py_compile tests/goal508_hausdorff_perf_doc_refresh_test.py
git diff --check
```

Result:

```text
OK
```

## Verdict

Goal508 is accepted.

External AI reviews:

- Claude review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal508_claude_review_2026-04-17.md`
  - Verdict: PASS
  - Finding: the bounded performance claim is consistently propagated to all
    five updated public docs, and no overclaims were introduced.
- Gemini review:
  `/Users/rl2025/rtdl_python_only/docs/reports/goal508_gemini_review_2026-04-17.md`
  - Verdict: ACCEPT

Codex consensus:

- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-17-codex-consensus-goal508-hausdorff-perf-public-doc-refresh.md`
