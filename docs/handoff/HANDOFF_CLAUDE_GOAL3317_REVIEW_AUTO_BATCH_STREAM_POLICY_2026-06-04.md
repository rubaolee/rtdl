# Handoff: Goal3317 Claude Review Of Goal3316 Auto Batch Stream Policy

Date: 2026-06-04
Repo: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review`
Branch: `main`
Expected output: `docs/reviews/goal3317_claude_review_goal3316_auto_batch_stream_policy_2026-06-04.md`

## Task

Please perform an independent Claude review of Goal3316. Goal3316 responds directly to your Goal3315 medium finding by making `RTDL_OPTIX_POINT_PRIMITIVE_BATCH_STREAM_COUNT=auto` reachable from the probe, recording the effective stream count per request row, measuring it on the RTX A5000 RayJoin PIP slice, and documenting the result as bounded repeated-query throughput evidence only.

## Files To Inspect

- `src/native/optix/rtdl_optix_workloads.cpp`
- `scripts/goal3310_rayjoin_pip_batch_scalar_count_probe.py`
- `tests/goal3316_auto_batch_stream_policy_test.py`
- `tests/goal3314_prepared_point_multistream_batch_count_test.py`
- `docs/reports/goal3316_auto_batch_stream_policy_2026-06-04.md`
- `docs/reports/goal3316_rayjoin_pip_batch_auto_stream_2026-06-04.json`
- `docs/reports/goal3314_multistream_batch_scalar_count_2026-06-04.md`
- `docs/reviews/goal3315_claude_review_goal3314_multistream_batch_count_2026-06-04.md`
- `docs/research/future_version_to_do_list.md`

## Review Questions

1. Does Goal3316 close the Goal3315 M1 finding: `auto` is now reachable, tested, documented, and pod-probed?
2. Is the auto policy conservative and consistent with Goal3314 evidence: `<8 -> 1`, `8..15 -> 4`, `16..63 -> 8`, `>=64 -> 16`, with no silent default change?
3. Does the artifact correctly record `batch_stream_count: "auto"`, `batch_stream_count_effective` per row, commit `8e28f485...`, exact count 1430, A5000 GPU identity, scalar-count mode labels, and all claim-boundary flags false?
4. Does the report accurately frame the 32-request and 64-request rows as repeated-query throughput evidence only, not one-shot RayJoin latency or a public speedup claim?
5. Did the Goal3314 report correction resolve the low table-mismatch finding without changing the key 6.48x conclusion?
6. What residual risks remain before this can become the recommended prepared batch-count route, especially around per-call stream creation/destruction and small batch sizes?

## Required Output

Write a Markdown review at:

`docs/reviews/goal3317_claude_review_goal3316_auto_batch_stream_policy_2026-06-04.md`

Use one of the standard verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Lead with findings by severity. If there are no blockers, say so explicitly. Do not authorize release, public speedup claims, RayJoin paper reproduction claims, RTDL-beats-RayJoin claims, broad RT-core speedup claims, true-zero-copy claims, or app-specific native-engine direction.
