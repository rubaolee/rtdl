# Goal2657: v2.4/v2.5 Partner Roadmap 3-AI Consensus

Status: accepted internal roadmap boundary.

Date: 2026-05-27

## Reviewed Proposal

- `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_2026-05-27.md`
- `docs/release_reports/v2_3/benchmark_app_performance.md`
- `docs/release_reports/v2_3/benchmark_app_performance_3ai_consensus.md`
- `docs/partner_acceleration_boundaries.md`
- `docs/application_catalog.md`

The proposal also cites the refreshed performance summaries:

- `docs/reports/goal2654_all_benchmark_app_perf_comparison_refresh_2026-05-27.md`
- `docs/reports/goal2655_benchmark_rt_core_speedup_summary_2026-05-27.md`

## External Reviews

- Claude review:
  `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_claude_review_2026-05-27.md`
- Gemini review:
  `docs/reports/goal2657_v2_4_v2_5_partner_roadmap_gemini_review_2026-05-27.md`

Claude verdict: accept with fixes. No blocking issues.

Gemini verdict: accept with fixes. It labeled several clarifications as
required before consensus.

## Fixes Applied

The accepted roadmap was updated after both reviews to resolve the required
fixes:

- Added the NVIDIA RTX A5000 hardware qualifier to the benchmark basis table.
- Clarified that the 10 percent tolerance applies to the same phase contract as
  the accepted benchmark row.
- Added stricter protocol-overhead handling for low-margin rows: Hausdorff,
  Barnes-Hut, and Robot collision.
- Required Triton continuation timing to be separated from RTDL/OptiX traversal.
- Narrowed typed buffer descriptors to RTDL-specific primitive handoff, not a
  general-purpose memory manager.
- Required machine-readable phase timing and a regression runner integrated
  into automated tests/CI for lightweight rows, with heavier pod rows on demand.
- Required a protocol-overhead audit for low-margin benchmark rows.
- Clarified that CuPy remains a reference/conformance baseline until a Triton
  or Numba path passes the same benchmark contract and performance gate.
- Softened Triton-first wording into a measured starting hypothesis, not a
  settled performance claim.
- Added a Numba fallback clause for continuation patterns where Triton proves
  unsuitable.
- Required non-piloted v2.5 benchmark apps to be explicitly classified rather
  than silently omitted.
- Made the v2.4 native-engine vocabulary audit a required input to v2.5 pilot
  acceptance.

## Consensus Position

Codex, Claude, and Gemini agree on the architecture after the fixes above:

```text
v2.4 should be a performance-preserving protocol cleanup release.
v2.5 should introduce a Triton-first partner path, with Numba as secondary or
per-pattern fallback when evidence supports it.
The current 10 promoted benchmark apps remain the performance basis.
Ease of use must not replace the accepted RT-vs-Embree rows with slower
convenience paths.
Partners must not replace OptiX RT traversal for RT-core claims.
Native engines must remain app-agnostic.
```

## Accepted Gates

The roadmap is accepted only with these gates:

- Preserve the current 10 benchmark-app basis and 11 primary rows.
- Compare new partner paths against the same phase contract as the accepted
  benchmark row.
- Split setup, transfer, RT traversal, continuation/reduction, materialization,
  and download where applicable.
- Track protocol overhead explicitly on low-margin rows.
- Keep Triton/Numba in preparation, continuation, reduction, compaction, and
  finalization roles around RTDL primitives.
- Keep RT-core traversal inside generic RTDL/OptiX primitive paths.
- Reject app-specific native-engine vocabulary or ABI pressure.
- Keep slower convenience paths as opt-in, learner, compatibility, or rejected
  paths rather than promoted performance paths.

## Decision

Goal2657 is consensus-accepted as the v2.4/v2.5 internal roadmap boundary.

This consensus does not authorize public speedup wording, package-install
claims, whole-app performance claims, or arbitrary PyTorch/CuPy/Triton/Numba
acceleration claims.
