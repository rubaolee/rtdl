# Goal3317 Claude Review of Goal3316 Auto Batch Stream Policy

Date: 2026-06-04
Reviewer: Claude (independent)
Verdict: **accept-with-boundary**

---

## Findings by Severity

### Blockers

None.

### Medium

None.

### Low

**L1 — `batch_stream_count_effective` in the artifact is a Python-side policy recompute, not a native readback.**

The probe script's `_effective_batch_stream_count` function mirrors the C++ policy in Python and writes its output to `batch_stream_count_effective` in the JSON. If the C++ policy were changed without updating the Python function, the artifact would record the Python value, not the actual native value selected. The test `test_native_auto_policy_is_explicit_and_conservative` guards against this by asserting specific source strings in the C++ file, so divergence would likely be caught — but only if the policy change is visible as a string change. This is acceptable for the current review scope and consistent with the probe-layer architecture, but reviewers should understand the artifact field is derived rather than observed.

**L2 (inherited from Goal3315 L2) — Per-call stream creation/destruction overhead remains uncharacterized at the auto policy threshold.**

The auto policy selects 4 streams at request_count=8, which is the first tier where streams are created at all. The Goal3316 artifact shows this row at 0.073 ms/request, compared to 0.252 ms/request at request_count=4 (1 stream). This is a plausible speedup for a GPU-resident workload, but no isolation measurement separates the stream-creation overhead from the traversal gain. For callers that call the batch path many times at exactly 8 requests, the per-call overhead at 4 streams accumulates. The report acknowledges this risk and records it in future_version_to_do_list.md; no evidence is missing for the current scope.

**L3 (inherited from Goal3315 L3) — Cumulative phase globals still apply to batch calls.**

`g_optix_last_closed_shape_raw_candidate_count` and `g_optix_last_closed_shape_emitted_count` record the sum across all batch slots, not per-request values. Unchanged by Goal3316.

---

## Review Questions

### Q1 — Does Goal3316 close the Goal3315 M1 finding?

**Yes. M1 is fully closed.**

Goal3315 M1 stated that `auto` existed in native code but was untested, unprobed, and undocumented. Goal3316 addresses each part:

- **Probe reachability**: `_parse_batch_stream_count` in the script accepts `"auto"` as a distinct case and passes it through `_temporary_env("RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT", str(...))`, making the native `auto` path reachable from the benchmarking layer. The test `test_probe_accepts_auto_and_records_effective_stream_count` verifies the function name, field name, and error text are all present.

- **Effective count recording**: `_effective_batch_stream_count` is called per row and written to `batch_stream_count_effective` in the JSON artifact. Every row in the artifact carries the policy-selected value, verified by `test_auto_artifact_is_exact_and_claim_boundary_clean`.

- **Pod measurement**: the artifact at commit `8e28f485` records six request-count rows on the RTX A5000 with `batch_stream_count: "auto"`, exact count 1430, and all claim-boundary flags false.

- **Documentation**: the report states the policy table, the default-unchanged note, the baseline speedup ratios, and the residual risk. `future_version_to_do_list.md` records the result and identifies the persistent stream-pool as the next step.

- **Test coverage**: `test_native_auto_policy_is_explicit_and_conservative` verifies the C++ source contains all five expected string patterns.

### Q2 — Is the auto policy conservative and consistent with Goal3314 evidence?

**Yes.**

The C++ policy (`prepared_closed_shape_batch_stream_count`, line 5596–5612 of `rtdl_optix_workloads.cpp`) and the Python probe policy (`_effective_batch_stream_count`, probe line 68–79) are identical in logic:

| Request count | Effective streams |
| ---: | ---: |
| `< 8` | 1 |
| `8..15` | 4 |
| `16..63` | 8 |
| `>= 64` | 16 |

Cross-checked against the artifact:

| Request count | Expected effective | Artifact effective |
| ---: | ---: | ---: |
| 1 | 1 | 1 ✓ |
| 4 | 1 | 1 ✓ |
| 8 | 4 | 4 ✓ |
| 16 | 8 | 8 ✓ |
| 32 | 8 | 8 ✓ |
| 64 | 16 | 16 ✓ |

The policy does not select 32 streams; Goal3314 showed no improvement at 32 streams over 16 at the tested sizes, so the ceiling is correctly placed at 16. The default for unset `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT` is unchanged: `PreparedClosedShapeBatchStreamPolicy` defaults to `explicit_count=1`, `auto_select=false`, and the function returns `min(request_count, 1u) = 1`. The `if (stream_count <= 1u)` branch (line 7554) routes to the null-stream path, identical to the Goal3310 baseline. No silent default change.

The policy is conservative with respect to the Goal3314 sweep: stream tiers are drawn at request counts where the sweep showed clear throughput gains (4 streams at 8 requests, 8 streams at 16 requests, 16 streams at 64 requests). The 32-stream tier is deliberately omitted.

### Q3 — Does the artifact correctly record all required fields?

**Yes.**

Verified from `goal3316_rayjoin_pip_batch_auto_stream_2026-06-04.json`:

| Field | Expected | Actual |
| --- | --- | --- |
| `batch_stream_count` | `"auto"` | `"auto"` ✓ |
| `rtdl_commit` | `8e28f485ed93da0d467b980e483d382f23000271` | match ✓ |
| `exact_count` | 1430 | 1430 ✓ |
| `gpu` | `NVIDIA RTX A5000, 580.126.09` | match ✓ |
| `scalar_count_pipeline` | `true` | `true` ✓ |
| request rows | [1, 4, 8, 16, 32, 64] | [1, 4, 8, 16, 32, 64] ✓ |
| `count_first` / `count_last` all rows | 1430 | 1430 ✓ |
| `native_modes` all rows | `["prepared_points_device_filtered_batch_count"]` | match ✓ |
| all `claim_boundary` flags | `false` | `false` ✓ |

The request-count set [1, 4, 8, 16, 32, 64] is the correct choice to exercise all four auto policy tiers. The test `test_auto_artifact_is_exact_and_claim_boundary_clean` independently verifies every row's effective count, count values, and mode labels from the raw JSON.

### Q4 — Does the report accurately frame the 32-request and 64-request rows as repeated-query throughput evidence only?

**Yes.**

The report states directly: "The result is still a repeated-query throughput result. It does not replace one-shot RayJoin latency comparisons and does not authorize RayJoin paper reproduction, RTDL-beats-RayJoin, broad RT-core speedup, true-zero-copy, or release claims."

The speedup ratios cited (6.59x at 32 requests, 6.90x at 64 requests) are computed against the Goal3314 single-stream 32-request baseline of 0.236400 ms/request, not against a RayJoin one-shot latency. Both ratios are arithmetically correct:

- 32-request: 0.236400 / 0.035896 = 6.586 ≈ 6.59x ✓
- 64-request: 0.236400 / 0.034279 = 6.895 ≈ 6.90x ✓

The `"interpretation"` field in the artifact JSON reads: `"Batch rows are repeated-query throughput evidence only; they do not replace one-shot RayJoin latency comparisons."` This matches the Goal3310 schema interpretation verbatim. All six claim-boundary flags are false. No RayJoin paper, RTDL-beats-RayJoin, RT-core speedup, or release claim appears anywhere in the artifact or report.

### Q5 — Did the Goal3314 report correction resolve the L1 table-mismatch finding?

**Yes, without changing the key 6.48x conclusion.**

Goal3315 L1 identified that the stream1/8-request and stream1/16-request rows in the Goal3314 report did not match the JSON artifact:

| Row | Goal3315 L1 report value | Corrected report value | JSON artifact |
| --- | ---: | ---: | ---: |
| stream1 / 8 requests | 0.247555 ms | 0.247338 ms | 0.247338 ms ✓ |
| stream1 / 16 requests | 0.243525 ms | 0.243664 ms | 0.243664 ms ✓ |
| stream1 / 32 requests | 0.236400 ms | 0.236400 ms | 0.236400 ms ✓ |

The current Goal3314 report (lines 57–58) now shows 0.247338 ms and 0.243664 ms respectively, matching the JSON. The 6.48x speedup (stream8/req32 vs stream1/req32: 0.236400 / 0.036487 = 6.479) is unchanged. The correction is a transcription fix only; no performance conclusion was altered.

### Q6 — What residual risks remain before this can become the recommended prepared batch-count route?

1. **Per-call stream pool overhead at the auto threshold (L2 above).** The auto policy selects 4 streams at request_count=8. Stream creation cost applies to every batch call, regardless of how many times it is called. For applications that invoke the batch path repeatedly at 8–15 requests, the per-call overhead at 4 streams accumulates. The current evidence does not isolate this cost. A persistent stream pool or prepared batch executor (noted in `future_version_to_do_list.md`) would amortize it. Until then, callers should measure at their actual call frequency, not just per-request median.

2. **Evidence is single-GPU, single-slice.** All measurements are on the RTX A5000 with a 512-point, 481-shape slice. Auto policy breakpoints that are optimal for this configuration may not generalize to other GPUs with different SM counts and memory hierarchies, or to larger workloads where traversal cost scales differently than stream-creation cost.

3. **Python-side policy recompute vs. native readback (L1 above).** The `batch_stream_count_effective` field reflects the Python reimplementation of the auto policy, not a native observation. The test provides a reasonable guard, but it is not watertight against all future drift.

4. **Cumulative phase globals (L3, inherited).** `g_optix_last_closed_shape_raw_candidate_count` and `g_optix_last_closed_shape_emitted_count` record batch-total values, not per-request values. Unchanged by Goal3316.

5. **CUDA graph replay (Goal3312) remains fail-closed.** The graph path returned zeros on the A5000 smoke. Not addressed by Goal3316 and not required for the auto stream policy route, but callers should not conflate the stream-pool path and the graph path.

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

Goal3316 closes Goal3315 M1. On the RTX A5000 pod with `br_county_start0_count512.cdb` at commit `8e28f485`, `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT=auto` selects 8 streams at 32 requests (0.036 ms/request) and 16 streams at 64 requests (0.034 ms/request), consistent with the Goal3314 explicit-stream sweep. The auto policy is conservative, tested, and documented. The default of one stream is unchanged. Residual risks are engineering scope items (per-call pool lifetime, single-slice evidence base), not correctness or claim-boundary violations.
