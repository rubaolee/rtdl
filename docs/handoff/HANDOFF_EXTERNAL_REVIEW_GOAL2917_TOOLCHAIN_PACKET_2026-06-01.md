# Handoff: External Review Goal2916-2917 Toolchain Packet

Please review the Goal2916-2917 v2.5 work and write an independent review to:

- Gemini: `docs/reviews/goal2918_gemini_review_goal2916_2917_toolchain_packet_2026-06-01.md`
- Claude: `docs/reviews/goal2919_claude_review_goal2916_2917_toolchain_packet_2026-06-01.md`

Use one verdict: `accept`, `accept-with-boundary`, `needs-more-evidence`, or
`reject`.

## Scope

Review these files:

- `scripts/goal2855_v2_5_current_canonical_harness_packet_runner.py`
- `src/rtdsl/v2_5_internal_readiness.py`
- `docs/reports/goal2916_packet_toolchain_provenance_metadata_2026-06-01.md`
- `docs/reports/goal2917_current_packet_with_toolchain_provenance_2026-06-01.md`
- `docs/reports/goal2917_current_packet_with_toolchain_pod/goal2855_summary.json`
- `docs/reports/goal2917_current_packet_with_toolchain_pod/goal2917_triage.json`
- `tests/goal2916_packet_toolchain_provenance_test.py`
- `tests/goal2917_current_packet_toolchain_provenance_test.py`

Relevant context:

- Goal2897 flagged compiler flag alignment before any v2.5 release packet.
- Goal2914 repeated that compiler flag alignment and second-architecture or
  multivendor checks remain open.
- Goal2916 adds `runner_metadata.toolchain` to the canonical packet runner.
- Goal2917 reruns the seven-app packet on the RTX A5000 pod at commit
  `b21ff72dbfdb0653cace6cd9e353269ae75bcaf0`.

## Questions

1. Does Goal2916 correctly record CUDA/OptiX/PTX/compiler/partner provenance
   in the packet runner without changing pass/fail semantics for local smoke
   runs?
2. Does Goal2917 prove the current seven-app packet still passes cleanly with
   the new metadata?
3. Is the readiness packet now pointing at the Goal2917 packet and validating
   the presence of toolchain metadata?
4. Does the report language correctly state that this is provenance only, not
   a compiler fairness proof, not a multivendor/second-architecture result,
   and not release/public-claim authorization?
5. What residual risk remains before any v2.5 release packet?

## Facts To Verify

Goal2917 packet expected facts:

- `all_pass: true`
- artifact count: `7`
- source commit: `b21ff72dbfdb0653cace6cd9e353269ae75bcaf0`
- `dirty_artifacts: {}`
- `claim_boundary_violations: {}`
- toolchain metadata version: `rtdl.goal2916.toolchain_provenance.v1`
- PTX arch/compiler: `compute_86`, `nvcc`
- OptiX header exists: `true`
- RTDL OptiX library exists: `true`
- partner versions: Triton `3.4.0`, Torch `2.8.0+cu128`, CuPy `14.1.0`,
  Numba `0.65.1`
- triage performance targets: `[]`

## Boundaries

This review must not authorize:

- v2.5 release;
- public speedup claims;
- broad RT-core claims;
- whole-app speedup claims;
- true-zero-copy claims;
- automatic Triton selection;
- package-install claims;
- paper-reproduction claims;
- app-specific native engine logic.

Likely verdict is `accept-with-boundary` if the facts hold, because compiler
fairness and second-architecture/multivendor evidence remain separate release
packet cautions.

## Validation Command

```powershell
$env:PYTHONPATH='src;.'
py -3 -m unittest `
  tests.goal2916_packet_toolchain_provenance_test `
  tests.goal2917_current_packet_toolchain_provenance_test `
  tests.goal2806_v2_5_internal_readiness_packet_test
```
