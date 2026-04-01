# Goal 22 Iteration 3 Implementation Report

## Scope

This iteration closes the remaining Goal 22 dataset/provenance machinery slice for the RayJoin-on-Embree program.

It does not claim that the missing paper dataset families are already acquired locally. It closes the public-source and bounded-preparation machinery needed before Goal 23 can run bounded local experiments honestly.

## Implemented Changes

### 1. Public-source registry

Added machine-readable public-source metadata in [datasets.py](/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py):

- `RayJoinPublicAsset`
- `rayjoin_public_assets()`

The registry now records:

- the Dryad preprocessed share as the preferred exact-input source,
- the ArcGIS items for `USCounty`, `Zipcode`, `BlockGroup`, and `WaterBodies`,
- and the SpatialHadoop dataset catalog as the acceptable derived-input path for Lakes/Parks.

Current status is intentionally recorded as `source-identified`, not `acquired`.

### 2. Bounded-local preparation registry

Added machine-readable bounded-local preparation policy in [datasets.py](/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py):

- `RayJoinBoundedPlan`
- `rayjoin_bounded_plans()`

This freezes, for the missing paper families:

- the source requirement,
- the `5-10 minutes` bounded local runtime target,
- and the deterministic reduction rule expected when exact-input data is not directly available.

### 3. Deterministic CDB helpers

Added deterministic CDB manipulation helpers in [datasets.py](/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py):

- `write_cdb(...)`
- `slice_cdb_dataset(...)`

These are the current bounded-local preparation primitives for any CDB data already acquired or produced externally.

### 4. Goal 22 artifact generation

Extended [rayjoin_artifacts.py](/Users/rl2025/rtdl_python_only/src/rtdsl/rayjoin_artifacts.py) so the Goal 22 generator now emits:

- `dataset_sources.md`
- `dataset_bounded_preparation.md`

in addition to the earlier:

- `goal22_reproduction_registry.json`
- `table3_analogue.md`
- `table4_overlay_analogue.md`
- `figure15_overlay_speedup_analogue.md`

### 5. Public API exports

Exported the new dataset helpers via [__init__.py](/Users/rl2025/rtdl_python_only/src/rtdsl/__init__.py):

- `RayJoinPublicAsset`
- `rayjoin_public_assets`
- `RayJoinBoundedPlan`
- `rayjoin_bounded_plans`
- `slice_cdb_dataset`
- `write_cdb`

### 6. Docs

Added and updated:

- [rayjoin_public_dataset_sources.md](/Users/rl2025/rtdl_python_only/docs/rayjoin_public_dataset_sources.md)
- [goal_22_rayjoin_gap_closure.md](/Users/rl2025/rtdl_python_only/docs/goal_22_rayjoin_gap_closure.md)
- [README.md](/Users/rl2025/rtdl_python_only/README.md)

## Verification

Executed:

- `cd /Users/rl2025/rtdl_python_only && PYTHONPATH=src:. python3 -m unittest tests.goal22_reproduction_test tests.paper_reproduction_test`
- `cd /Users/rl2025/rtdl_python_only && PYTHONPATH=src:. python3 scripts/goal22_generate_reproduction_artifacts.py`
- `cd /Users/rl2025/rtdl_python_only && python3 -m py_compile src/rtdsl/datasets.py src/rtdsl/rayjoin_artifacts.py src/rtdsl/__init__.py`

All passed.

## Current Position

This slice should be accepted only if Claude and Gemini agree that:

1. the public-source picture is now explicit enough for the missing families,
2. the repo now distinguishes `source-identified` from `acquired` clearly,
3. the bounded-local preparation rule is encoded honestly,
4. and Goal 23 now has the dataset/provenance machinery it needs without over-claiming acquisition.
