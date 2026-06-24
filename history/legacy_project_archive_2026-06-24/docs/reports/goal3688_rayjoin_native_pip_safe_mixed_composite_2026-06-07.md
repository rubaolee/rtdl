# Goal3688 RayJoin Native-PIP Safe Mixed Composite

Date: 2026-06-07

## Purpose

Goals3684 and 3686 fixed the dense-boundary scalar-count weakness for exact point/closed-shape membership count by moving relation-status correction into a generic native OptiX scalar-count primitive and then making it resident/reusable.

Goal3688 tests whether that primitive can replace the older CuPy PIP continuation inside the current safe RayJoin count composite, without changing the rest of the composite:

- PIP: native resident relation-status corrected scalar count,
- LSI: existing exact prepared RTDL/OptiX route with host double refinement,
- overlay seed: existing RTDL/OptiX active-count route.

This is an internal candidate route. It does not promote a default public RayJoin route and does not claim paper reproduction.

## Implementation

New runner:

- `scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py`

New test:

- `tests/goal3688_rayjoin_native_pip_safe_mixed_composite_test.py`

The runner compares the candidate composite against the same dense all-CuPy count contracts used by the recent RayJoin comparison packets. It fails closed on count mismatch.

The native PIP leg uses:

`PreparedOptixPointClosedShapeMembership2D.prepare_relation_status_corrected_scalar_count_executor(...)`

The runner records both full `git status --short` and a scoped source-clean check over the exact files defining this route. The active pod checkout had untracked benchmark data and old artifact directories, so the full status was not clean; the scoped route source was clean.

## A5000 Evidence

Artifact:

`docs/reports/goal3688_rayjoin_native_pip_safe_mixed_composite_a5000/summary.json`

Pod:

- GPU: `NVIDIA RTX A5000, 580.126.09`
- source commit: `f55ba72d`
- `goal3688_scoped_source_dirty=false`
- OptiX library: `/root/rtdl/build/librtdl_optix.so`
- point primitive predicate epsilon: `1e-9`

Datasets:

- PIP: `br_county_start256_count4096.cdb`
- LSI and overlay seed: `br_county_start256_count4096.cdb + br_soil_start256_count4096.cdb`

Run shape:

- `repeat=20`
- `warmup=5`
- `chain_count=4096`

## Results

Composite timing:

| Route | Sum of hot medians (s) | Count status |
| --- | ---: | --- |
| dense all-CuPy baseline | `1.430913273` | all match |
| native-PIP safe mixed candidate | `0.006967423` | all match |

Composite speedup versus dense all-CuPy:

`205.372x`

Per workload:

| Workload | Dense all-CuPy median (s) | Candidate median (s) | Candidate speedup | Count |
| --- | ---: | ---: | ---: | ---: |
| PIP | `0.000885802` | `0.000336909` | `2.629x` | `11316` |
| LSI | `1.267117743` | `0.001227182` | `1032.542x` | `4977` |
| overlay seed | `0.162909728` | `0.005403331` | `30.150x` | `4250` |

Correctness:

- all per-workload counts match the dense all-CuPy same-contract baseline,
- composite `all_counts_match=true`,
- source-scoped route code was clean at the measured commit.

## Interpretation

The important engineering result is not the headline composite ratio alone. The useful lesson is narrower:

1. The generic resident native scalar-count executor can replace the older CuPy PIP correction leg for this safe mixed RayJoin count packet.
2. The PIP leg is now faster than the dense all-CuPy baseline while preserving exact count parity.
3. The composite is now dominated by the already-fast LSI and overlay prepared OptiX legs rather than the dense-boundary PIP correction problem.

This is also a good example of the v2.x direction the user asked for: when an app only needs a scalar count, the runtime should offer a generic native scalar primitive instead of forcing users to materialize a dense row stream and write a partner continuation.

## Boundary

This report does not authorize:

- release,
- default-route promotion,
- public speedup claims,
- RTDL-beats-RayJoin claims,
- RayJoin paper reproduction claims,
- broad RT-core speedup claims,
- true zero-copy claims.

The evidence authorizes only this internal engineering conclusion: the current native-PIP safe mixed candidate is exact on the measured public-CDB 4096-chain packet and is substantially faster than the dense all-CuPy same-contract baseline for this packet.

## Next Work

Recommended next steps:

1. external review of Goal3688 before promoting the candidate route in any benchmark summary,
2. test the same candidate on additional counts if the pod remains available,
3. decide whether the native scalar-count executor should become the standard PIP leg in the internal RayJoin recommended composite,
4. keep the public documentation explicit that this is a generic closed-shape scalar-count primitive, not app-specific native RayJoin logic.
