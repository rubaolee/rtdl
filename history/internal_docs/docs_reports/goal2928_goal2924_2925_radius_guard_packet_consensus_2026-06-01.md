# Goal2928: Goal2924/2925 Radius Guard Packet Consensus

Date: 2026-06-01
Verdict: `accept-with-boundary`

## Scope

Goal2928 records consensus for:

- Goal2924: app-level Hausdorff prepared-radius guard and GTX 1070
  second-architecture smoke.
- Goal2925: refreshed seven-app RTX A5000 v2.5 canonical packet after the
  radius guard.

## Evidence

Primary artifacts:

- `docs/reports/goal2924_hausdorff_prepared_radius_guard_second_arch_smoke_2026-06-01.md`
- `docs/reports/goal2924_second_arch_smoke_after_radius_guard/`
- `docs/reports/goal2925_current_packet_after_radius_guard_2026-06-01.md`
- `docs/reports/goal2925_current_packet_after_radius_guard_pod/`

External review:

- `docs/reviews/goal2926_gemini_review_goal2924_2925_radius_guard_packet_2026-06-01.md`

Gemini verdict: `accept`.

Claude note: a background Claude review was attempted for
`docs/reviews/goal2927_claude_review_goal2924_2925_radius_guard_packet_2026-06-01.md`,
but no review file was produced; it is not counted as consensus evidence.

## Consensus

Codex and Gemini agree:

- the radius guard is app-level preparation-envelope hardening,
- exact Hausdorff query radius and result semantics are preserved,
- no native engine ABI change or app-specific native customization was added,
- the GTX 1070 result is bounded as functional/toolchain smoke only,
- the refreshed RTX packet is clean: 7/7 pass, `source_dirty = []`,
  `rtdl_optix_ptx_compiler = "nvcc"`, and empty claim-boundary violations,
- the Hausdorff packet row is honestly described as near-parity, not a speedup
  claim, with RTDL/CuPy ratio about `1.044x`,
- shorthand: near-parity, not a speedup claim,
- `v2_5_internal_readiness.py` correctly points to the Goal2925 current packet
  while preserving release blocks.

This satisfies Codex + Gemini 2-AI consensus for the internal Goal2924/2925
work.

## Boundary

This consensus does not authorize v2.5 release, public speedup wording, broad
RT-core claims, whole-app speedup claims, true-zero-copy claims,
package-install claims, automatic Triton-selection claims, or
paper-reproduction claims.

Release remains blocked until the user explicitly requests a release packet and
fresh 3-AI release consensus is produced.
