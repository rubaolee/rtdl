# Goal4394 V3.0 M2 Execution-Graph Skeleton

Date: 2026-06-15

Status: M2 no-execution skeleton implemented and tested.

## Decision

M2 implements the V3.0 execution-graph metadata skeleton authorized by Goal4393. It does not execute native code, does not lower to OptiX or Embree, does not select partners automatically, and does not authorize performance claims.

## Implemented Files

- `src/rtdsl/v3_0_execution_graph.py`
- `tests/goal4394_v3_0_m2_execution_graph_skeleton_test.py`
- Updated public exports in `src/rtdsl/__init__.py`
- Updated Goal4393 static test to check V3 public definitions/exports instead of rejecting the forbidden-token list itself.

## Implemented Public Concepts

- `GraphValue`
- `StreamBinding`
- `PhaseMarker`
- `ClaimBoundary`
- `PartnerPolicy`
- `BackendContract`
- `LoweringHints`
- `CapacityPolicy`
- `PrimitiveNode`
- `ContinuationNode`
- `PartnerNode`
- `MaterializeNode`
- `ValidationNode`
- `BackendPlan`
- `PreparedGraph`
- `V3ExecutionReport` as the top-level alias for the V3 report, preserving the existing v2 `ExecutionReport`
- `GraphValidationError`
- `prepare_graph`
- `validate_v3_public_name`

## Validator Coverage

The M2 skeleton validates:

- all claim-boundary flags remain false;
- partner policy forbids automatic selection;
- benchmark partner policy requires explicit partner, best partner, Numba reference, and separated partner timing unless a written Numba omission justification exists;
- device-resident non-opaque values require stream binding;
- same-stream and event-wait stream bindings require evidence labels;
- graph values and node ids use app-agnostic names;
- node inputs and outputs refer to declared graph values;
- produced values have exactly one producing node;
- mandatory phases exist;
- node phases are declared;
- graphs with PartnerNode require explicit graph-level partner policy;
- BackendPlan and V3ExecutionReport do not authorize execution or performance claims.

## Boundary

M2 explicitly does not implement:

- native fused kernels;
- backend execution;
- OptiX/Embree lowering;
- app-specific lowering;
- raw arbitrary OptiX callback user API;
- automatic partner/backend selection;
- same-stream, device-resident, or true-zero-copy promotion;
- public speedup claim generation.

## Test Results

Focused and nearby governance suite:

```text
42 tests OK
```

Focused M2/M1 suite:

```text
19 tests OK
```

## Next Authorized Work

The next milestone is M3 residency and phase instrumentation. M3 should add metadata and validation for hardware-observable evidence, including CUDA-event or Nsight evidence labels for GPU paths and explicit Embree CPU phase accounting. M3 still must not add native fused execution.

## Conclusion

M2 is complete as a no-execution skeleton. V3.0 may proceed to M3 instrumentation, while native execution remains blocked.
