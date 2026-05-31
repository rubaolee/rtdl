# Handoff: Gemini Review For Goal2799 Spatial RayJoin Prepared Count Harness

Please perform an independent read-only Gemini review of Goal2799 and write the review to:

`docs/reviews/goal2799_gemini_review_spatial_rayjoin_prepared_count_harness_2026-05-31.md`

## Context

Goal2799 closes the current v2.5 manifest gap for Spatial RayJoin's Tier A count/parity track.

The important design boundary is:

- primitive-first prepared RTDL/OptiX count/parity stays canonical;
- Triton is not used merely to relabel a fused RT primitive;
- row materialization, overlay continuation, and downstream grouped processing remain deferred Tier B work;
- this is not a public speedup claim and not a RayJoin-paper reproduction claim.

## Files To Inspect

- `scripts/goal2799_spatial_rayjoin_v25_prepared_count_harness.py`
- `tests/goal2799_spatial_rayjoin_v25_prepared_count_harness_test.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2799_spatial_rayjoin_v2_5_prepared_count_harness_2026-05-31.md`
- `docs/reports/goal2799_pod_artifacts/spatial_rayjoin_v25_prepared_count_optix_fixture.json`
- `docs/reports/goal2799_pod_artifacts/spatial_rayjoin_v25_prepared_count_optix_fixture.stdout`

## Review Questions

1. Does the harness correctly test the existing prepared OptiX count/parity route for `pip`, `lsi`, and `overlay_seed`?
2. Does it compare against a CPU reference count and record the three workload statuses honestly?
3. Does the manifest update avoid overclaiming Triton, whole-app speedup, or RayJoin-paper reproduction?
4. Are row materialization and overlay continuation clearly left as deferred Tier B work?
5. Are any app-specific names or policies being pushed into the native engine contract?
6. Is the report accurate against the JSON artifact?

## Required Review Format

Use verdict `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please include:

- a short verdict summary;
- file-grounded findings if any;
- boundary notes for public claims;
- whether the review is an independent Gemini review distinct from Codex.
