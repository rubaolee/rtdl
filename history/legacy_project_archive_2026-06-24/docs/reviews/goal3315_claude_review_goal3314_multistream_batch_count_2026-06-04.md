# Goal3315 Claude Review of Goal3314 Multi-Stream Batch Count

Date: 2026-06-04
Reviewer: Claude (independent)
Verdict: **accept-with-boundary**

---

## Findings by Severity

### Blockers

None.

### Medium

**M1 — `auto` stream-count mode exists in native code but is untested, unprobed, and undocumented.**
`prepared_closed_shape_batch_stream_count` (workloads.cpp line 5596) accepts
`RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT=auto` and applies a request-count-based
heuristic: request_count >= 64 → 16 streams; >= 16 → 8 streams; >= 8 → 4 streams; else → 1.
The probe script's `--batch-stream-count` flag only accepts integers and leaves the `auto` path
unreachable from the benchmarking layer. No test exercises `auto`; the report does not mention
it. The error message text ("must be a positive integer or auto") is the only documentation.
A future caller who discovers the `auto` value will invoke an unvalidated code path on every
batch call without knowing which stream count will be selected.

The heuristic table is broadly consistent with the measured data — 16 streams at
request_count >= 64, 8 streams at >= 16, etc. — so a correctness violation is unlikely.
The risk is behavioral divergence from any benchmarked configuration, not count mismatch.
The `auto` path should be either tested with at least one pod-measured request count, documented
explicitly in the probe and report, or removed until it has evidence behind it.

### Low

**L1 — Stream1 8-request and 16-request rows in the report table don't match the JSON artifact.**
The stream1 artifact records:

| Row | JSON per_request_ms_median | Report per_request |
|-----|----------------------------|--------------------|
| 8 requests | 0.247338 ms | 0.247555 ms |
| 16 requests | 0.243664 ms | 0.243525 ms |
| 32 requests | 0.236400 ms | 0.236400 ms ✓ |

The corresponding total_ms values diverge by similar magnitudes (1.978705 ms vs 1.980437 ms
for 8 requests). The discrepancy is consistent with the report having been transcribed from a
single-repeat print value rather than the statistical median. The critical 32-request baseline
row matches the JSON exactly, and the 6.48x speedup claim is computed from that row — the
speedup conclusion is sound. A future audit checking the 8- and 16-request stream1 rows against
the artifact will surface the mismatch.

**L2 — Per-call stream creation and destruction overhead is not characterized.**
The multi-stream path (workloads.cpp lines 7568–7597) creates `stream_count` CUDA streams at
the entry of every batch call and destroys them at return. CUDA stream creation/destruction adds
a constant overhead per call that scales with `stream_count`. At 8 streams × 32 requests on the
A5000, this overhead is amortized across warmup and absorbed by the 12-repeat median. For
callers issuing small batch counts (e.g., `request_count=4` with `stream_count=8`) the stream
creation cost applies but only 4 slots in the pool are ever used, since
`prepared_closed_shape_batch_stream_count` returns `min(request_count, explicit_count)`.
The per-call pool should be noted as unsuitable for very small `request_count` values relative
to the configured stream count.

**L3 (inherited from Goal3311 L1) — Batch phase globals remain cumulative sum.**
Lines 7611–7612 set `g_optix_last_closed_shape_raw_candidate_count` and
`g_optix_last_closed_shape_emitted_count` to `total_count` — the sum across all
`request_count` slots. This applies to both the single-stream and multistream paths. Any
caller reading these globals after a batch call expecting a single-request count observes
N× the per-request value. Not a new regression; recorded for forward debugging.

---

## Review Questions

### Q1 — Does Goal3314 remain generic and app-agnostic, with no RayJoin-specific logic in the native engine?

Pass. The multi-stream extension lives entirely within
`count_prepared_point_closed_shape_membership_device_filtered_prepared_points_batch_2d_optix`
(workloads.cpp lines 7567–7598). The stream count resolution function
`prepared_closed_shape_batch_stream_count` (line 5596) and the policy struct
`PreparedClosedShapeBatchStreamPolicy` (line 5567) carry only generic names. The test at line 32
asserts `"rayjoin"` does not appear (case-insensitive) in the batch function body and passes on
pod. The probe script imports the RayJoin dataset loader at the probe layer only; the engine
layer has no knowledge of it. The environment variable `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT`
is generic and scoped to the prepared-point / closed-shape batch path. No app-specific native
API was added.

### Q2 — Does the stream-pool implementation preserve the default single-stream behavior while enabling opt-in multi-stream batching?

Pass. When `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT` is unset,
`prepared_closed_shape_batch_stream_policy` returns a default `PreparedClosedShapeBatchStreamPolicy`
with `explicit_count = 1`. `prepared_closed_shape_batch_stream_count` then returns
`min(request_count, 1u)` = 1. The `if (stream_count <= 1u)` branch at line 7554 falls into
the exact Goal3310 null-stream path (`CUstream stream = 0`), with the same single
`cuStreamSynchronize`. There is no behavioral change for callers that do not set the environment
variable.

When `stream_count > 1`, the multi-stream path (lines 7568–7597) creates `CU_STREAM_NON_BLOCKING`
streams — which can overlap with each other and with the null stream — assigns each request to
`streams[request_index % stream_count]`, and calls `cuStreamSynchronize` per stream before
returning. Exception safety is preserved: the catch block destroys all created streams before
re-throwing. The explicit_count is hard-capped at 64 (line 5592) and further clamped to
`request_count` at the call site (line 5600), so no stream is ever created without a request.

Note: M1 applies here — the `auto` sub-path bypasses the explicit_count guard.

### Q3 — Are the pod artifacts internally consistent: commit hash, GPU, exact count 1430, scalar-count mode labels, stream counts, and all claim-boundary flags false?

Pass with L1 noted.

All six artifacts (`stream1` through `stream32`) share:
- `"rtdl_commit": "0cfc510d19c3026eef8cf409d29ecaa4eabe8d6b"` ✓
- `"gpu": "NVIDIA RTX A5000, 580.126.09"` ✓
- `"exact_count": 1430` ✓
- `"scalar_count_pipeline": true` ✓
- `"native_modes": ["prepared_points_device_filtered_batch_count"]` for every batch row ✓
- `"batch_stream_count"` matching the artifact filename (1, 2, 4, 8, 16, 32) ✓
- All six `claim_boundary` flags `false` ✓
- `count_first == count_last == 1430` for every row ✓
- `"interpretation": "Batch rows are repeated-query throughput evidence only; they do not replace one-shot RayJoin latency comparisons."` ✓

The test `test_pod_artifacts_are_exact_and_claim_boundary_clean` independently verifies all of
these fields from the raw JSON files and passes on pod. The report table's stream1/8 and
stream1/16 values differ slightly from the JSON (L1 above); the stream1/32 baseline and all
multistream rows match their artifacts exactly.

### Q4 — Does the report accurately frame the measured win as repeated-query throughput only?

Pass. The report Introduction states: "This is a repeated-query throughput probe, not a
one-shot RayJoin latency comparison." The Interpretation section states: "It does not prove a
one-shot RayJoin speedup, a RayJoin paper reproduction, a broad RT-core speedup, or a release
claim." All six claim-boundary flags are listed as false. The `future_version_to_do_list.md`
entry for Goal3314 (line 29) records the same framing: "This is repeated-query throughput
evidence only, not one-shot RayJoin latency evidence." No RayJoin-beating, paper-reproduction,
release, broad RT-core speedup, or true-zero-copy claim is made anywhere in the artifact chain.

### Q5 — Are the reported performance conclusions sound, especially the 8-stream / 32-request and 16-stream / 64-request rows?

Pass.

Cross-checked against the JSON artifacts:

| Claim | Report | JSON (raw) | Consistent |
|-------|--------|------------|------------|
| stream1/req32 per_request | 0.236400 ms | 0.23639952996745706 ms | ✓ |
| stream8/req32 per_request | 0.036487 ms | 0.03648694837465882 ms | ✓ |
| stream16/req64 per_request | 0.034520 ms | 0.034520315239205956 ms | ✓ |
| 6.48x speedup (stream8/req32 vs stream1/req32) | stated | 0.236400/0.036487 = 6.479 | ✓ |
| 6.85x speedup (stream16/req64 vs stream1/req32) | stated | 0.236400/0.034520 = 6.848 | ✓ |

The test `test_multistream_rows_show_repeated_query_throughput_gain` independently verifies the
speedup ratios from the raw JSON files: stream8/req32 < 0.05 ms, stream16/req64 < 0.04 ms,
and stream1/req32 / stream8/req32 > 6.0.

The performance shape is internally consistent. With 2 streams at 32 requests, the per-request
time halves to ~0.124 ms. With 4 streams it drops to ~0.066 ms. With 8 streams it drops to
~0.036 ms. Gains past 8 streams are small (~5% from stream8 to stream16 at 32 requests), which
is consistent with GPU occupancy saturation for a 512-point workload on the A5000. The
32-stream runs are marginally slower than 16-stream at the same request counts, suggesting
stream-scheduling overhead dominates over additional parallelism for this workload size.

### Q6 — What residual risks or next engineering directions should be recorded before treating this as the current best repeated-query scalar-count path?

1. **`auto` mode unvalidated (M1).** The heuristic table exists and is reasonable, but it has
   never been run against the A5000 pod. Before treating this as the recommended configuration
   for production repeated-query batching, run at least one probe with `--batch-stream-count auto`
   and record the result. Until then, the only validated configurations are the six explicit
   stream counts in the artifact set.

2. **Per-call stream pool overhead at small batch sizes (L2).** The current evidence covers
   request counts of 8–64. The stream pool creates and destroys N streams per call regardless
   of batch size. For callers batching fewer than `stream_count` requests, the stream creation
   overhead could dominate. Characterize or document the minimum effective batch size for each
   stream count tier before advertising multistream as a general improvement.

3. **CUDA graph replay path still fail-closed negative (Goal3312/Goal3313).** The graph handle
   returns zeros on the A5000 and must not be used as performance evidence until the native
   replay mismatch is understood and validated. This is unchanged by Goal3314.

4. **Cumulative phase globals (L3).** `g_optix_last_closed_shape_raw_candidate_count` and
   `g_optix_last_closed_shape_emitted_count` record the sum across all batch requests. Callers
   or tests that read these globals to diagnose per-request candidate counts after a batch call
   will observe N× the expected value.

5. **Workload scale.** All evidence is on the 512-point, 481-shape `br_county_start0_count512.cdb`
   slice. Per-request traversal cost and optimal stream count may differ at larger scales. The
   multistream path should not be generalized beyond the repeated independent scalar-count
   contract on similar-scale workloads without additional pod evidence.

6. **No adaptive default is active.** The `auto` mode exists but is unvalidated. For now,
   callers must opt in explicitly and must choose a stream count with no in-process guidance.
   A validated `auto` mode would let users benefit without manual tuning.

---

## Claim Boundaries

This review does not authorize and explicitly preserves the existing prohibition on:

- release;
- public speedup claims;
- RayJoin paper reproduction claims;
- RTDL-beats-RayJoin claims;
- broad RT-core speedup claims;
- true-zero-copy claims;
- app-specific native-engine direction.

Goal3314 is repeated-query throughput evidence for the generic prepared-point / closed-shape
scalar-count batch path with an opt-in CUDA stream pool. On the RTX A5000 pod with the
`br_county_start0_count512.cdb` slice at commit `0cfc510d`, 8 streams at 32 requests improved
per-request median time from 0.236 ms to 0.036 ms (~6.48×) while preserving the exact count
of 1430. This addresses the Goal3311 null-stream serialization concern for the repeated-query
contract.

The result does not establish a one-shot latency improvement over RayJoin, a paper-reproduction
claim, a broad RT-core speedup, or any release readiness. The best-measured configuration
(16 streams, 64 requests, 0.034520 ms per request) is evidence for the throughput contract on
this slice only.

The `auto` stream-count mode (M1) must not be treated as a validated configuration until pod
evidence is recorded for it.
