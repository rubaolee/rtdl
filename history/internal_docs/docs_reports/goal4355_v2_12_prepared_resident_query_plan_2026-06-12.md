# Goal4355 v2.12 Prepared Resident Query Plan

Date: 2026-06-12

Status: v2.12 performance work started. This report does not authorize release action, public speedup wording, broad RT-core wording, whole-app speedup wording, true-zero-copy wording, paper reproduction claims, hidden partner/backend selection, or app-specific native-engine dispatch.

## Why This Starts v2.12

v2.11 closed the OptiX-vs-Embree comparison packet with prepared hot-query rows, but the RayJoin same-stream evidence exposes the next real debt. LSI shows RTDL OptiX can be strong on a scalar count path, while RayJoin PIP shows RTDL is slow when exact point-in-polygon is still routed through the current exact membership path.

The v2.12 gate is therefore prepared resident query execution: keep the scene and query contract prepared, run the hot query in a native repeat loop, time it with duration-bounded aggregates, and require the same prepared ABI for OptiX and Embree before speedup wording is computed.

## First Rows

| Priority | Row | Why It Comes Now | Required Outcome |
| ---: | --- | --- | --- |
| 1 | RayJoin PIP exact native resident scalar count | Goal4354 measured RayJoin RT PIP at 0.613610 ms and RTDL OptiX exact PIP at 7.081935 ms on the same stream. The faster relation-status path is diagnostic-only until exact semantics match. | Build a native repeat loop for exact scalar PIP count, or report phase data that accounts for the full remaining gap. |
| 2 | RayJoin LSI Embree packet scalar count | Goal4354 measured RTDL OptiX LSI at 0.237690 ms but RTDL Embree LSI at 183730.426896 ms, so the CPU opponent is not yet a serious packet traversal path. | Profile and fix packet layout/thread scheduling, or label the specific native Embree bottleneck. |
| 3 | Cross-app duration-bounded native runner | v2.11 already targets 1-10s hot-query aggregates, but artifacts still express repeats in row-specific shapes. | Emit one native prepared-query timing schema for all comparison rows. |
| 4 | Cross-app same prepared ABI | Public wording needs a mechanical proof that the OptiX and Embree rows use the same prepared-session boundary. | Compare only rows that assert the same prepared ABI. |
| 5 | Cross-app fused scalar reductions | Several benchmark rows reduce to scalar count or scalar summary output. Materializing a row stream for one scalar is the wrong hot path. | Fuse traversal and scalar reduction where the benchmark contract is scalar. |

## Apple-to-Apple Rule

For every v2.12 comparison row:

- Cold prepare is outside the hot query loop.
- OptiX and Embree must expose the same prepared ABI boundary.
- Per-iteration work is identical.
- Repeat counts may differ only to accumulate stable duration-bounded wall time.
- Scalar-count rows must not materialize hit rows in the measured hot path.
- Partner work is allowed only when both sides use the same continuation contract.
- Exactness gates outrank speed. RayJoin PIP cannot use the faster relation-status route for claims until it matches exact point-in-polygon semantics.

## What This Does Not Claim

This is not an optimization result yet. It is an executable v2.12 optimization contract in `src/rtdsl/v2_12_prepared_resident_query_plan.py`, with tests in `tests/goal4355_v2_12_prepared_resident_query_plan_test.py`.

The plan intentionally keeps release and public-speedup flags false. The first real performance result must come from a measured native repeat loop, not from rewording the v2.11 table.
