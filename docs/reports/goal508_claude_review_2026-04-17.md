# Goal508 External AI Review

Date: 2026-04-17

Reviewer: Claude (claude-sonnet-4-6)

Verdict: **PASS**

## Scope

Reviewed the five updated public docs, the regression test, and the internal
Goal508 report against the bounded claim: RTDL OptiX/Vulkan beat RTDL Embree
but do not beat the strongest mature exact 2D nearest-neighbor baselines.

## File-by-file findings

### README.md

- Links the Goal507 Hausdorff Linux Performance Evidence report correctly.
- Version-status block describes the evidence as "bounded Linux Embree/OptiX/Vulkan
  performance evidence against SciPy, scikit-learn, and FAISS nearest-neighbor
  baselines."
- No overclaim. No unbounded speedup language. ✓

### docs/release_facing_examples.md

- Adds `optix` and `vulkan` CLI commands for the Hausdorff app under Linux
  (lines 113–115).
- Boundary block (lines 122–125) states: "strong OptiX/Vulkan speedups over
  RTDL Embree, but it does not show RTDL beating mature exact 2D
  nearest-neighbor baselines such as SciPy `cKDTree` or FAISS `IndexFlatL2`."
- Corrected CLI-boundary section explicitly warns not to generalize the
  Hausdorff app-specific GPU CLI path to every nearest-neighbor script.
- Wording matches the test's exact `assertIn` literals. ✓

### docs/tutorials/nearest_neighbor_workloads.md

- Adds `embree`, `optix`, and `vulkan` Hausdorff run commands for Linux.
- Links `../reports/goal507_hausdorff_linux_perf_report_2026-04-17.md`.
- Bounded readout (lines 215–217): "RTDL OptiX/Vulkan strongly beat RTDL Embree
  for this app on the measured Linux host, but mature nearest-neighbor libraries
  such as SciPy `cKDTree` and FAISS `IndexFlatL2` remain faster for exact 2D
  1-NN Hausdorff distance in that evidence."
- Wording matches the test's `assertIn` literals. ✓

### docs/tutorials/feature_quickstart_cookbook.md

- `hausdorff_distance_app` recipe (lines 215–219) states: "RTDL GPU backends
  beat RTDL Embree, but do not beat the strongest mature nearest-neighbor library
  baselines on the measured exact 2D task."
- Links Goal507 report.
- Wording matches the test's `assertIn` literals (including newline + two-space
  indent on the continuation). ✓

### docs/tutorials/v0_8_app_building.md

- App 1 section links Goal507 report and states: "RTDL OptiX/Vulkan beat RTDL
  Embree for this app on the measured Linux host, but SciPy `cKDTree` and
  FAISS `IndexFlatL2` remain stronger exact 2D nearest-neighbor baselines in
  that evidence."
- Wording matches the test's `assertIn` literals (including newline + two-space
  indent). ✓

### tests/goal508_hausdorff_perf_doc_refresh_test.py

- Three test methods cover all five updated docs.
- Assertions are specific: they check for the bounded-claim phrasing, the GPU
  CLI commands, the Goal507 report link, and the "do not generalize" guard.
- No assertion is weaker than what the doc actually says.
- All `assertIn` strings were verified against the current on-disk doc text. ✓

## Bounded claim check

The central claim is stated consistently and correctly in every updated file:

> RTDL OptiX/Vulkan beat RTDL Embree — but RTDL does not beat the strongest
> mature exact 2D nearest-neighbor baselines (SciPy `cKDTree`, FAISS
> `IndexFlatL2`) in the Goal507 evidence.

No file reverses this direction. No file claims RT-core acceleration. No file
promotes the Hausdorff app's GPU CLI support into a general nearest-neighbor
release claim. The `v0.8` app-building framing is preserved throughout: this is
an app over existing RTDL features, not a new backend or language surface.

## Issues found

None.

## Summary

Goal508 correctly and completely refreshes the public documentation after
Goal507. The bounded performance claim is faithfully propagated to all five
updated files. The regression test covers the right surface with precise
assertions. No overclaims were introduced.
