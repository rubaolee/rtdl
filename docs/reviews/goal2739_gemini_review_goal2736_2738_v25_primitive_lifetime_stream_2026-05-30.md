# Goal2739: Gemini Review Of Goals2736-2738 v2.5 Primitive/Lifetime/Stream Hardening

Date: 2026-05-30
Reviewer: Gemini 2.5 Flash
Status: recovered from Gemini CLI stdout after stdout-only review
Verdict: `accept-with-boundary`

## Independence Statement

This is an independent Gemini review distinct from Codex and Claude. Codex+Codex does not count as consensus.

The Gemini CLI produced a complete review on stdout, then began repeating the Markdown output. Codex stopped the repeating process and recovered the first complete review into this file without changing the verdict.

## Scope

This review covers the following files:

- `docs/reports/goal2736_tier_a_primitive_first_plan_alignment_2026-05-30.md`
- `tests/goal2736_tier_a_primitive_first_plan_alignment_test.py`
- `examples/v2_0/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`
- `examples/v2_0/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `docs/reports/goal2737_native_hit_stream_owner_lifecycle_guard_2026-05-30.md`
- `tests/goal2737_native_hit_stream_owner_lifecycle_guard_test.py`
- `docs/reports/goal2738_native_hit_stream_stream_ordering_boundary_2026-05-30.md`
- `tests/goal2738_native_hit_stream_stream_ordering_boundary_test.py`
- `src/rtdsl/hit_stream_handoff.py`
- `docs/reviews/goal2735_claude_review_goal2734_zero_copy_boundary_2026-05-30.md`

## Review Questions And Answers

### 1. Does Goal2736 correctly extend the primitive-first rule to Spatial RayJoin and LibRTS without relabeling fused/native count paths as Triton paths?

Yes. Goal2736 correctly extends the primitive-first rule. The documentation, source code, and tests consistently indicate that for Spatial RayJoin and LibRTS, the selected paths are `prepared_generic_rtdl_count_or_parity` and `prepared_generic_aabb_index_query_2d`. Triton is explicitly reserved only for optional post-processing and is not used for the primary fused/native count paths, as confirmed by `triton_speedup_claim_authorized: False` boundaries and `primitive_first_plan_native_rt_count_not_relabelled_as_triton` status.

### 2. Does Goal2737 materially reduce native hit-stream owner-lifetime misuse while preserving the true-zero-copy boundary?

Yes. Goal2737 introduces a Python-side fail-closed lifecycle guard for native hit-stream outputs. Key changes include `RtdlNativeDeviceHitStreamOutput` tracking a `closed` state, `close()` being idempotent, `to_handoff()` failing if the output is closed, and `RtdlRawCudaColumn.__cuda_array_interface__` rejecting access if its owner is closed. This significantly reduces stale-pointer misuse. The `true_zero_copy_authorized` flag remains false in all relevant metadata.

### 3. Does Goal2738 correctly make producer/consumer stream ordering explicit without pretending stream synchronization is already proven?

Yes. Goal2738 makes producer/consumer stream ordering explicit through `producer_consumer_stream_ordering` and `stream_synchronization_proven`. The default state is `not_proven`, and `stream_synchronization_proven` is false by default. Invalid stream-ordering states fail closed. The boundary clearly states that this is not stream-synchronization evidence and public true-zero-copy wording remains blocked.

### 4. Are public speedup, paper-reproduction, and true-zero-copy claim boundaries preserved?

Yes. Across the reviewed reports, tests, source code, and Claude review, the claim boundaries for public speedup, paper reproduction, and true zero-copy are consistently preserved.

- `public_speedup_claim_authorized: False` is consistently set.
- `true_zero_copy_authorized: False` remains enforced in `src/rtdsl/hit_stream_handoff.py` and by Goal2736-2738 tests.
- `paper_reproduction_claim_authorized: False` is present in the relevant RayJoin and LibRTS `v2_5_plan_payload` outputs.

### 5. What risks remain before broader v2.5 benchmark migration or any future zero-copy public wording?

The following risks remain:

1. Native ownership lifetime still needs lower-level native release-entrypoint enforcement beyond the Python-side guard.
2. CUDA stream synchronization still needs actual pod evidence showing the OptiX producer and Triton consumer are ordered correctly.
3. Same-pointer evidence remains single-GPU and single-driver evidence and should be broadened before general public claims.
4. Cross-partner transfer semantics for executable CuPy/Numba paths remain incomplete.
5. Claim-boundary scans should keep positive-coverage assertions as the public docs structure evolves.

## Verdict

`accept-with-boundary`

Goals2736-2738 correctly implement the intended v2.5 guardrails and preserve public speedup, paper-reproduction, and true-zero-copy boundaries. The work extends primitive-first planning to Spatial RayJoin and LibRTS without relabeling native paths as Triton paths, and adds meaningful lifecycle and stream-ordering explicitness for native hit-streams.

The boundary is that native ownership, stream synchronization, cross-GPU validation, and cross-partner transfer semantics remain unresolved for any future public true-zero-copy wording.
