# Goal 110 Segment-Polygon-Hitcount Closure Progress

Date: 2026-04-05
Author: Codex
Status: in_progress

## Scope of this slice

This slice does not close Goal 110. It adds the missing backend-closure tests
 that encode the remaining acceptance obligations for:

- Embree parity on authored, fixture-backed, and derived cases
- OptiX parity on authored, fixture-backed, and derived cases
- prepared-path equivalence on authored and fixture-backed cases for:
  - Embree
  - OptiX

The goal of this slice is to move Goal 110 from:

- semantics and harness progress

to:

- executable backend-closure obligations in the repo

## New artifact

Added:

- `tests/goal110_segment_polygon_hitcount_closure_test.py`

This test file encodes:

- exact row parity against `cpu_python_reference` for:
  - `authored_segment_polygon_minimal`
  - `tests/fixtures/rayjoin/br_county_subset.cdb`
  - `derived/br_county_subset_segment_polygon_tiled_x4`
- prepared-path equivalence checks on:
  - authored minimal
  - fixture-backed county subset

Prepared-path equality is checked across:

- current backend run
- prepared backend run
- prepared raw output converted back to dict rows

## Local validation

Validated locally on this Mac:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal110_segment_polygon_hitcount_semantics_test \
  tests.goal110_baseline_runner_backend_test \
  tests.goal110_segment_polygon_hitcount_closure_test
```

Observed result:

- `13` tests
- `OK`
- `5` skipped

The skips are expected in the current local environment because:

- Embree is not installed here
- OptiX is not available here
- the existing local Mac native-oracle rebuild still emits the known
  `geos_c` linker noise before skipped paths

That local native-oracle noise is not new Goal 110 behavior.

## Example confirmation

The user-facing example still runs on the new derived case:

```bash
cd /Users/rl2025/rtdl_python_only
python3 examples/rtdl_segment_polygon_hitcount.py \
  --backend cpu_python_reference \
  --dataset derived/br_county_subset_segment_polygon_tiled_x4
```

Observed high-level result:

- backend: `cpu_python_reference`
- dataset: `derived/br_county_subset_segment_polygon_tiled_x4`
- row count: `40`

The first rows remain deterministic and show the expected integer output form:

- `segment_id`
- `hit_count`

## What this proves

This slice proves that Goal 110 now has the following encoded in the repo:

- a fixed semantic contract
- authored / fixture / derived deterministic cases
- explicit backend parity obligations for Embree and OptiX
- explicit prepared-path obligations for Embree and OptiX

So the remaining Goal 110 work is no longer:

- "what should closure mean?"

It is now:

- obtaining actual capable-host evidence for the encoded Embree/OptiX closure
  checks
- completing the explicit `segment_polygon_hitcount` versus `lsi` technical
  comparison required by the Goal 110 acceptance rule
- recording the required significance proof beyond parity closure:
  - either at least `4x` probe/build scale over the basic county fixture
  - or a materially denser output-count regime than the basic county fixture
- deciding whether the final accepted package can honestly claim only
  workload-family closure or something stronger about RT-backed maturity

## What is still open

Goal 110 is still open until:

- Embree closure tests are exercised on a capable host
- OptiX closure tests are exercised on a capable host
- prepared-path evidence is recorded from those runs
- the explicit technical comparison against `lsi` is written and accepted
- the final package records which significance proof it satisfied
- the final report explains whether the closed family still sits in the
  audited local `native_loop` bucket or has stronger RT-backed evidence
