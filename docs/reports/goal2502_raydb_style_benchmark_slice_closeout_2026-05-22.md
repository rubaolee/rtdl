# Goal2502: RayDB-Style Benchmark Slice Closeout

Date: 2026-05-22

## Verdict

The CPU + Embree local portion of the RayDB-style benchmark slice is complete as
a reconstruction harness, not as a RayDB reproduction. The slice forced a
concrete RTDL contract and exposed the next engine improvement target.

Post-pod update: Goal2501 subsequently collected OptiX runtime parity evidence
for grouped `count` and grouped `sum` on an RTX A5000 pod. The evidence is
recorded in
`docs/reports/goal2501_raydb_style_optix_pod_validation_results_2026-05-22.md`.

Completed locally:

- CPU reference for generic columnar grouped aggregates;
- Embree count/sum parity through existing generic columnar payload support;
- OptiX count/sum app path and skip-safe tests;
- explicit lowering metadata for current backend capability and gaps;
- diagnostic backend matrix runner;
- OptiX pod validation packet.

Original local-closeout pod gap, now closed by Goal2501:

- fresh OptiX runtime parity for count/sum;
- OptiX backend matrix JSON with `cases.optix.status == "ok"`.

## What The App Taught RTDL

RayDB-style pressure should not push RTDL toward a DBMS or SQL engine. The useful
RTDL reconstruction is narrower and more general:

```text
typed columnar records
+ predicate ranges
+ grouped reductions
+ prepared backend state
+ bounded compact result metadata
```

This app confirms that the current engine can express `count` and `sum` on
Embree and OptiX through generic columnar payloads. It also confirms that the
current Python path still materializes row mappings before the native columnar
payload preparation call.

## Current Capability

| Capability | Status |
| --- | --- |
| CPU oracle count/sum/min/max/avg_as_sum_count | Complete |
| Embree count/sum parity | Complete locally |
| OptiX count/sum app path | Implemented; pod runtime parity evidence collected in Goal2501 |
| App-specific native ABI | Not added |
| Authors-code timing | Not attempted |
| SQL/DBMS behavior | Not claimed |
| Direct `ColumnarRecordSet` native preparation | Not implemented |
| True zero-copy wording | Not authorized |

## Main Design Conclusion

The next real RTDL reconstruction target is:

```text
direct_columnar_record_set_preparation_without_row_mapping
```

That target is more valuable than copying RayDB internals. It would let Python
pass normalized column descriptors directly into backend preparation. After that
exists, a later partner path can decide whether columns originate from NumPy,
CuPy, Torch, Numba, Triton, or another partner.

## Deferred Work

Completed when a pod became available:

1. Ran the Goal2501 packet.
2. Saved OptiX pod JSON evidence under `docs/reports/`.
3. Recorded exact pod commit, build command, environment, and runtime evidence.

Do next locally after OptiX parity is recorded:

1. Design the direct columnar preparation API.
2. Decide whether Embree and OptiX can share the same Python descriptor.
3. Decide whether native min/max reductions should be added as generic
   reductions or routed through a partner continuation.

## Claim Boundary

Allowed internal wording:

- RayDB-style benchmark slice for RTDL columnar aggregate reconstruction.
- CPU and Embree parity are locally validated.
- OptiX path is implemented but needs pod runtime evidence.
- Current native count/sum paths use generic columnar payloads.

Blocked wording:

- RayDB reproduction;
- SQL engine or DBMS support;
- authors-code performance comparison;
- public speedup claim;
- true zero-copy claim;
- whole-app acceleration claim;
- new app-specific native ABI.
