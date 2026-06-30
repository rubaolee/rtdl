# Handoff: Gemini Review For Goal2924/2925 Radius Guard And Current Packet

Please perform an independent read-only review of the recent Goal2924/Goal2925 work in the RTDL repository.

Expected output path:

`docs/reviews/goal2926_gemini_review_goal2924_2925_radius_guard_packet_2026-06-01.md`

## Context

Goal2924 fixed a small-input Hausdorff/X-HD portability failure found on the local Linux GTX 1070 smoke host:

```text
RuntimeError: point_group_nearest_max_distance radius exceeds prepared max_radius
```

The fix added an app-level `_prepared_radius_guard(radius)` in:

`examples/v2_0/research_benchmarks/hausdorff_xhd/rtdl_hausdorff_v2_function.py`

The key design claim is narrow:

- prepared OptiX point-group scenes may use a tiny conservative preparation envelope,
- exact query radius and exact Hausdorff result semantics are unchanged,
- no native engine ABI or app-specific native customization was added,
- the fix is app-level robustness, not performance promotion.

Goal2925 reran the full seven-app v2.5 canonical packet on the RTX A5000 pod from source commit:

`6ad6314192e9db0f659c76acc58a20767a194697`

Artifacts:

- `docs/reports/goal2924_hausdorff_prepared_radius_guard_second_arch_smoke_2026-06-01.md`
- `docs/reports/goal2924_second_arch_smoke_after_radius_guard/`
- `docs/reports/goal2925_current_packet_after_radius_guard_2026-06-01.md`
- `docs/reports/goal2925_current_packet_after_radius_guard_pod/`
- `tests/goal2924_hausdorff_prepared_radius_guard_test.py`
- `tests/goal2924_second_arch_smoke_report_test.py`
- `tests/goal2925_current_packet_after_radius_guard_test.py`
- `src/rtdsl/v2_5_internal_readiness.py`

## Review Questions

1. Does the radius guard preserve exact Hausdorff semantics and avoid native engine app-customization?
2. Does the second-architecture GTX 1070 smoke correctly remain bounded as functional/toolchain smoke only, not RT-core release evidence?
3. Does the Goal2925 RTX packet genuinely pass cleanly with 7/7 artifacts, `source_dirty = []`, toolchain provenance including `rtdl_optix_ptx_compiler = "nvcc"`, and empty claim-boundary violations?
4. Is the Hausdorff row honestly described as near-parity rather than a speedup claim (`RTDL/CuPy ratio ~= 1.044x`)?
5. Does `v2_5_internal_readiness.py` correctly point to Goal2925 as the current packet while preserving release blocks?
6. Are there any overclaims, missing tests, stale references, or hidden release blockers introduced by this work?

## Required Review Shape

Use one of these verdicts: `accept`, `accept-with-boundary`, `needs-more-evidence`, or `reject`.

Please include:

- a concise verdict,
- findings ordered by severity,
- exact file paths inspected,
- whether the work can count as Codex + Gemini 2-AI consensus for this internal goal,
- explicit statement that it does not authorize v2.5 release, public speedup wording, broad RT-core claims, true zero-copy claims, package-install claims, or paper-reproduction claims.

Do not edit source code. Only write the review file above.
