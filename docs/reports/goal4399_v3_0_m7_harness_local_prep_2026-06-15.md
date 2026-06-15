# Goal4399 V3.0 M7 Benchmark Harness Local Preparation

Date: 2026-06-15

Status: M7 benchmark harness skeleton implemented and tested locally. Full release-grade benchmark packet remains blocked on pod and external-system evidence.

## Decision

M7 adds a benchmark-harness metadata layer for release-grade comparison rows. It validates row-level timing basis, phase-complete instrumentation, same-contract comparison groups, external-system timing basis, and claim boundaries.

This checkpoint does not publish V3.0 performance claims.

## Implemented Files

- `src/rtdsl/v3_0_m7_harness.py`
- `tests/goal4399_v3_0_m7_harness_test.py`
- Updated public exports in `src/rtdsl/__init__.py`

## Implemented Concepts

- `BenchmarkHarnessRow`
- `BenchmarkHarnessPacket`
- `validate_benchmark_harness_packet`
- `V3_BENCHMARK_HARNESS_VERSION`
- `V3_BENCHMARK_HARNESS_STATUS`

## Validator Coverage

The M7 harness validators enforce:

- each row has phase-complete M3 instrumentation;
- each row records graph id, dataset, scale, hardware, backend, partner, timing basis, warmups, repeats, and same-contract key;
- comparison groups must share one `same_contract_key`;
- RTDL OptiX rows require matching RTDL Embree rows in the same comparison group, and vice versa;
- external-system rows require external code version and timing-basis metadata;
- cold-total RTDL rows must include build timing;
- public claim authorization remains false.

## Test Results

Focused V3 M1-M7 stack:

```text
45 tests OK
```

## Boundary

The harness skeleton does not include:

- measured OptiX or Embree results;
- external-system measured rows;
- pod hardware evidence;
- M7 external review;
- public speedup wording.

## Full M7 Requirements

Full M7 completion requires:

- exact datasets and scale;
- scripts that reproduce RTDL OptiX, RTDL Embree, and external-system rows;
- phase-complete M3 instrumentation;
- same-contract keys across comparison groups;
- warmups/repeats/timing statistic;
- backend and partner disclosure;
- external review of exact public wording.

## Conclusion

M7 local harness preparation is complete. Release-grade V3.0 benchmark claims remain blocked until real evidence and external review exist.
