# Goal2661: v2.4 Completion Gate 3-AI Consensus

Status: accepted.

Date: 2026-05-27

## Reviewed Files

- `src/rtdsl/partner_protocol.py`
- `src/rtdsl/__init__.py`
- `tests/goal2661_v2_4_completion_gate_test.py`
- `docs/reports/goal2661_v2_4_completion_gate_2026-05-27.md`
- `docs/partner_acceleration_boundaries.md`
- prior v2.4 reports: Goal2657, Goal2658, Goal2659, Goal2660

## Reviews

- Codex implementation and validation: accepted after focused tests.
- Claude review:
  `docs/reports/goal2661_v2_4_completion_claude_review_2026-05-27.md`
- Gemini review:
  `docs/reports/goal2661_v2_4_completion_gemini_review_2026-05-27.md`

Claude verdict: accept, no blockers. Claude suggested non-blocking hardening
before v2.5 pilot acceptance.

Gemini verdict: accept, no blockers, no required fixes after hardening.

## Hardening Applied After Claude Review

- `validate_v2_4_partner_protocol_contract()` now validates the promoted-path
  tolerance ratio and opt-in tolerance ratio.
- The validator now checks the distinct benchmark-app count and the comparison
  row count from the benchmark-basis rows.
- `v2_4_completion_gate()` now carries the additional Goal2657 v2.5 gates:
  slower convenience paths must be labeled optional, compatibility,
  learner/preview, or rejected; and every non-piloted v2.5 benchmark app must
  be explicitly classified.

## Consensus Position

Codex, Claude, and Gemini agree:

```text
v2.4 is internally complete as a protocol-cleanup milestone.
It does not authorize a public release tag, package-install wording, new public
speedup claims, or whole-app performance claims.
v2.5 may begin from the tested typed-buffer, prepared-session,
segmented-row-stream, benchmark-metadata, and phase-timing contracts.
```

## Accepted Boundaries

- The current 10 promoted benchmark apps and 11 primary OptiX-vs-Embree rows
  remain the benchmark performance basis.
- The v2.5 default direction is Triton-first, with Numba fallback or
  per-pattern alternative only when evidence supports it.
- Triton and Numba may own preparation, continuation, reduction, compaction,
  and finalization around RTDL primitives.
- RT-core claims still require generic RTDL/OptiX traversal through OptiX GAS
  and `optixTrace` where applicable.
- Native engine vocabulary and native symbols remain app-agnostic.
- App-domain semantics remain Python app, adapter, documentation, or partner
  code, not native engine ABI.

## Validation

Focused validation:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2625_segmented_row_stream_test \
  tests.goal2661_v2_4_completion_gate_test \
  tests.goal2658_v2_4_partner_protocol_test \
  tests.goal2659_v2_4_benchmark_protocol_integration_test \
  tests.goal2644_raydb_paper_rt_contract_test \
  tests.goal2622_contact_manifold_generic_aabb_discovery_test \
  tests.goal2589_rt_graph_triangle_contract_test
```

Result:

```text
Ran 59 tests
OK (skipped=5)
```

Compile and whitespace validation:

```bash
PYTHONPATH=src:. python3 -m py_compile \
  src/rtdsl/partner_protocol.py \
  src/rtdsl/__init__.py \
  tests/goal2661_v2_4_completion_gate_test.py
git diff --check
```

Result: OK.

## Decision

Goal2661 is accepted. v2.4 is internally complete.

Next milestone: v2.5 Triton-first partner continuation prototype, with Numba as
fallback where evidence supports it, measured against the same-contract
benchmark basis.
