# Goal4395 V3.0 M3 Instrumentation

Date: 2026-06-15

Status: M3 metadata substrate implemented and tested locally. Hardware evidence collection is pending pod access.

## Decision

M3 adds a no-execution instrumentation layer for V3.0 graph runs. It records phase timings, hardware evidence records, residency evidence, and derived claim readiness without authorizing public claims.

## Implemented Files

- `src/rtdsl/v3_0_instrumentation.py`
- `tests/goal4395_v3_0_m3_instrumentation_test.py`
- Updated public exports in `src/rtdsl/__init__.py`

## Implemented Concepts

- `EvidenceRecord`
- `PhaseTimingRecord`
- `ResidencyEvidence`
- `InstrumentationPacket`
- `claim_readiness_summary`
- `empty_claim_boundary_metadata`

## Evidence Types

M3 supports these evidence kinds:

- `cuda_event_pair`
- `nsight_stream_correlation`
- `pointer_identity`
- `backend_native_handle`
- `transfer_counter`
- `no_host_materialization`
- `embree_phase_timer`
- `cpu_phase_timer`
- `host_timer`

## Validator Coverage

The instrumentation validators enforce:

- required V3 graph phases are present;
- timing seconds are non-negative;
- phase timing evidence ids reference real evidence records;
- residency evidence ids reference real evidence records;
- evidence ids are unique;
- same-stream readiness requires CUDA-event or Nsight evidence;
- device-resident readiness requires pointer or backend-handle evidence, lifetime authority, no host materialization, and evidence ids;
- true-zero-copy readiness additionally requires transfer-counter evidence and no hidden-copy observation;
- public claim authorization remains false.

## Boundary

M3 does not:

- execute native code;
- collect hardware evidence by itself;
- prove same-stream, device-resident, or zero-copy behavior without real evidence records;
- authorize public performance claims;
- implement M4 fused continuation or M5 benchmark pilots.

## Test Results

Focused M1-M3 stack:

```text
27 tests OK
```

Nearby governance suite:

```text
50 tests OK
```

## Pod Requirement

To turn M3 metadata into measured evidence, the next pod run must provide:

- CUDA event or Nsight stream correlation records for OptiX/partner paths;
- pointer identity or backend-native handle records for device-resident values;
- transfer counters or explicit no-host-stage evidence;
- phase timings for build, upload, traversal, stream handoff, continuation, materialization/download, validation, and host wrapper;
- Embree CPU phase timing records for same-contract comparisons.

## Next Authorized Work

The next milestone is M4 generic fused continuation pilot preparation. Full M4 completion requires pod hardware evidence because Goal4392 requires same-contract measurements on hardware with an OptiX-capable GPU and M3-grade phase accounting.

## Conclusion

M3 local substrate is complete. V3.0 can now attach real hardware evidence to graph runs once pod access is available.
