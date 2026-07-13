# Goal5470: Generic Partitioned AABB Native Spike - No-Go

Date: 2026-07-11

Status:

```text
completed_partitioned_aabb_native_spike__exact_but_no_material_end_to_end_win__prototype_reverted
```

## Objective

Test whether the app-neutral partitioned-traversal contract from Goal5469 can
produce a material same-host end-to-end improvement in RTDL's generic OptiX 2-D
AABB range-intersection row route.

This was a bounded spike. Promotion required all of the following:

1. exact canonical pair-row parity with the existing `k=1` route;
2. no LibRTS, RTSpatial, paper, or author identity in the native/public ABI;
3. a same-host median end-to-end win above 2% after separately recording query
   GAS preparation and query work;
4. no hidden warm-only or author-performance claim.

## Temporary Prototype

The spike temporarily implemented:

- a prepared box-query GAS with power-of-two `partition_count`;
- stable query assignment by ordinal modulo `k`;
- disjoint z-layer placement for query AABBs;
- `indexed_count * k` backward rays carrying source ordinal and partition id;
- partition filtering in the OptiX intersection program;
- exact app-neutral `{query_id, indexed_id}` rows;
- per-backward-ray intersection-program invocation telemetry;
- Python wrappers with generic names and fail-closed partition validation.

The native library compiled on local Linux with CUDA/OptiX for `sm_61`, and the
runtime gate passed on one GTX 1070. A 4-indexed-by-8-query discriminator proved:

```text
k=1 rows == existing rows == k=4 rows
backward intersection invocations: 32 for k=1 and k=4
maximum invocations per backward ray: 8 for k=1, 2 for k=4
```

This established that the layered traversal mechanism really executed. It did
not establish useful end-to-end speedup.

## Same-Host Matrix

Machine:

```text
local Linux
NVIDIA GeForce GTX 1070
driver 580.126.09
```

Regime for every matrix row:

- one prepared indexed-box GAS reused across samples;
- query GAS rebuilt inside every measured sample;
- one discarded warmup per partition count;
- five measured repeats with rotated `k` order;
- canonical row count and SHA-256 checked on every repeat;
- preparation, query, and end-to-end time recorded separately;
- no author timing and no paper-hardware comparison.

| Shape | Canonical rows | Best k | k=1 total | Best total | Best speedup | Peak backward work | Decision |
|---|---:|---:|---:|---:|---:|---:|---|
| sparse 128x128, radius 0.1 | 145,924 | 1 | 124.44 ms | 124.44 ms | 1.000x | 7 -> 7 | no-go |
| representative 64x64, radius 2 | 190,096 | 2 | 127.30 ms | 126.13 ms | 1.009x | 65 -> 33 | no-go |
| large 128x128, radius 2 | 781,456 | 4 | 557.15 ms | 555.51 ms | 1.003x | 65 -> 18 | no-go |
| dense 64x64, radius 8 | 1,267,876 | 8 | 854.64 ms | 847.25 ms | 1.009x | 496 -> 69 | no-go |

All partition counts in all four artifacts produced the same canonical rows as
`k=1`. The mechanism substantially reduced the maximum work carried by one
backward ray, but the total route did not improve materially. The best observed
end-to-end movement was only 0.9%, below the predeclared 2% gate and within the
range where noise and row-output work dominate.

## Evidence

| Artifact | SHA-256 |
|---|---|
| `librts_goal5470_partitioned_range_probe_sparse_gtx1070.json` | `7dde02150c4d56ad20a9f0bac8b2d4fa573b8b3937cec3766972ab6654de1dc2` |
| `librts_goal5470_partitioned_range_probe_gtx1070.json` | `eccfc4938ed59f5c76e62fdb724d02de0a7ef2271adbcaf328dfe493e1424160` |
| `librts_goal5470_partitioned_range_probe_large_gtx1070.json` | `ffafbbb342603e4322c681772c692c33b36022b669fa08a588e3369563178f05` |
| `librts_goal5470_partitioned_range_probe_dense_gtx1070.json` | `f94f763bc0f55dca673e8e66da7ae8d4b4753ffc3b18418b3d87eb15e1b69569` |

The committed regression test verifies exact-row stability, the no-go decision,
and absence of the unpromoted native/public symbols after revert.

## Decision

The temporary native/public implementation was reverted. RTDL does not ship a
partitioned OptiX AABB execution API from this spike.

Goal5469 remains useful as a tested, app-neutral reference/planning contract:

- exact partition coverage;
- fanout selection from generic cost inputs;
- non-LibRTS consumer proof.

Goal5470 adds negative systems evidence: reducing maximum per-ray traversal work
does not by itself make the current host-materialized, canonical-row route
faster. Reopening native partitioned traversal requires a changed execution
model or new evidence, such as a device-resident downstream that avoids the
current row download/sort boundary. Repeating `k` tuning on this same route is
not authorized.

## Claim Boundary

Authorized:

- the temporary prototype was exact on the tested inputs;
- it reduced peak backward-ray intersection work;
- it did not produce a material same-host end-to-end win;
- the prototype was reverted under the predeclared kill gate.

Not authorized:

- LibRTS Ray-Multicast performance reproduction;
- author-performance comparison or parity;
- paper-hardware evidence;
- native partitioned traversal completion;
- a public RTDL partitioned OptiX API;
- a claim that partitioning can never help another execution model.
