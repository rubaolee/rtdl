# Iteration 2 Implementation Report

Date: 2026-03-29
Author: Codex
Round: 2026-03-29-goal-2-multi-workload-datasets
Status: implemented, awaiting Gemini review

## Goal Implemented

Extend RTDL from one workload to three RayJoin workload surfaces and add a Python dataset pipeline for RayJoin-style CDB inputs.

## Workloads Added

1. `lsi`
   - existing segment-vs-segment path retained and generalized into the new multi-workload plan model

2. `pip`
   - added frontend predicate `rt.point_in_polygon(exact=False, boundary_mode="inclusive")`
   - added lowering path for point probes against polygon refs
   - added workload-specific plan, output record, payload contract, and generated backend skeleton

3. `overlay`
   - added frontend predicate `rt.overlay_compose()`
   - added polygon-vs-polygon compositional overlay workload surface
   - added workload-specific plan and generated backend skeleton for overlay seed generation / LSI+PIP composition

## Compiler And IR Changes

- `RayJoinPlan` now carries `workload_kind`
- `plan.json` schema widened from single-workload assumptions to `lsi`, `pip`, and `overlay`
- lowering now branches by workload predicate and geometry contract
- codegen now dispatches by workload kind instead of forcing everything through the old LSI-only device template

## Dataset Pipeline Added

New module:

- `src/rtdsl/datasets.py`

Capabilities:

- parse RayJoin-style CDB chain files
- load datasets from disk
- download selected public RayJoin sample files on demand
- derive:
  - segment views
  - point-probe views from chain starts
  - polygon-reference views from face ids

RayJoin-origin fixture subsets were added under:

- `tests/fixtures/rayjoin/br_county_subset.cdb`
- `tests/fixtures/rayjoin/br_soil_subset.cdb`

## CPU Reference Validation Added

New module:

- `src/rtdsl/reference.py`

Reference coverage:

- CPU LSI
- CPU PIP
- CPU compositional overlay seed logic

These are used for semantic checks independent of GPU runtime.

## Generated Artifact Coverage

Generated backend artifacts now exist for:

- `generated/county_zip_join/`
- `generated/point_in_counties/`
- `generated/county_soil_overlay/`

Golden fixtures exist for all three workloads under:

- `tests/golden/county_zip_join/`
- `tests/golden/point_in_counties/`
- `tests/golden/county_soil_overlay/`

## Documentation And Demo Updates

- `apps/rtdsl_python_demo.py` now demonstrates all three workloads plus the RayJoin sample fixture pipeline
- `README.md` now documents current workload coverage and dataset support
- `docs/rayjoin_datasets.md` documents the current RayJoin-oriented dataset pipeline

## Local Verification

Executed successfully:

- `make test`
- `make build`
- `make run-rtdsl-py`

Current test coverage in this round:

- workload compile/lower checks for 3 workloads
- exact golden-file checks for 3 workloads
- schema validation checks for 3 workloads
- RayJoin CDB parser and derived-view tests
- CPU semantic checks for LSI, PIP, and overlay composition
- negative tests for invalid PIP and overlay configurations

## Scope Notes

- `pip` and `overlay` codegen are workload-specific backend skeletons, not finished runtime implementations
- the RayJoin sample-data pipeline currently supports CDB parsing and derived views, not full topologically exact polygon face reconstruction
- this round is still pre-GPU and does not claim OptiX runtime correctness

## Review Request For Gemini

Review this implementation against the previously agreed evidence bar:

- workload coverage
- dataset pipeline usefulness and honesty
- adequacy of tests and generated artifacts
- whether overlay is materially implemented enough to count
- any remaining overclaims or missing evidence before Goal 2 can be accepted
