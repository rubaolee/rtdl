# Goal1226 Two-AI Roadmap Consensus: v1.0, v1.5, v2.0

Date: 2026-05-01

Participants:
- Codex (`docs/reports/goal1226_codex_v1_0_v1_5_v2_0_roadmap_understanding_2026-05-01.md`)
- Gemini (`docs/reports/gemini_rtdl_v1_0_to_v2_0_roadmap_understanding_2026-05-01.md`)

## Status

Preliminary two-AI roadmap alignment. Superseded for controlling design details
by `docs/reports/goal1227_formal_v1_0_v1_5_v2_0_roadmap_design_2026-05-01.md`
and `docs/reports/goal1227_two_ai_consensus_2026-05-01.md`.

## Verdict

`STRONG ALIGNMENT / ACCEPT`

Both AIs demonstrate conceptual alignment on the RTDL architectural roadmap.
This report records the initial shared direction only; where wording differs,
the later Goal1227 formal roadmap and Goal1228 v1.0 positioning plan are the
current source of truth.

## Shared Understanding

### 1. The Role of v1.0
- **Agreement**: v1.0 is the app-credibility release and compatibility
  baseline.
- **Actionable Takeaway**: We accept app-specific native engine debt where it
  is necessary to prove useful application targets and bounded RT-capable
  sub-path evidence. v1.0 sets correctness, result-shape, and timing baselines
  for later abstraction work without claiming whole-app acceleration.

### 2. The Mandate for v1.5
- **Agreement**: v1.5 is primarily technical-debt reduction via pragmatic
  decoupling.
- **Actionable Takeaway**: The engine should remove domain-specific app logic
  behind a reviewed minimal primitive set. The later Goal1227 design refines
  this into `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`,
  `REDUCE_INT(COUNT|SUM)`, and experimental `COLLECT_K_BOUNDED`.
- **Migration Rule**: No v1.0 endpoint will be retired until its v1.5 generic
  equivalent proves correctness under the defined schema/tolerance and
  acceptable performance or explicitly accepted overhead.

### 3. The Scope of v2.0
- **Agreement**: v2.0 is the ecosystem-integration release. RTDL is a traversal
  and reduction component, not a general-purpose Python-to-CUDA compiler.
- **Actionable Takeaway**: RTDL should use explicit compute partnerships. RTDL
  handles RT traversal and simple reductions, then uses DLPack or equivalent
  zero-copy handoffs to tools such as CuPy, PyTorch, Triton, Numba, or similar
  compute systems for custom dense compute. Native plugins remain strictly
  experimental unless separately designed and reviewed.

## Next Steps

Based on Codex's recommendations and the later Goal1227 formal design, before
any code is written for v1.5, the following must be produced and reviewed:
1. The formal **Primitive ABI Contract** (schema, overflow behavior, fallback rules).
2. The **Per-App Lowering Matrix** (mapping current v1.0 app endpoints to the proposed v1.5 generic primitive calls).
