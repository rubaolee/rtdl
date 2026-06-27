# Goal1668 Native App-Agnostic Engine 3-AI Consensus

Date: 2026-05-10

Participants:

- Codex
- Gemini / Antigravity
- Claude

Reviewed artifacts:

- `docs/directives/goal1668_antigravity_directive_app_agnostic_engine_2026-05-10.md`
- `docs/reports/goal1668_native_engine_app_agnostic_directive_response_2026-05-10.md`
- `docs/reports/goal1668_native_leakage_manifest_baseline_2026-05-10.json`
- `docs/release_reports/v1_7_app_agnostic_native_gate.md`
- `tests/goal1668_native_engine_app_agnostic_directive_test.py`
- `docs/reviews/goal1668_gemini_native_app_agnostic_response_review_2026-05-10.md`
- `docs/reviews/goal1668_claude_native_app_agnostic_response_review_2026-05-10.md`
- `docs/reviews/goal1668_gemini_final_artifact_review_2026-05-10.md`
- `docs/reviews/goal1668_claude_final_artifact_review_2026-05-10.md`

## Consensus Verdict

The Antigravity/Gemini directive is accepted as the correct next-track
architecture rule: RTDL native internals must become app-agnostic before the
project can publish that claim.

The current repository does not satisfy that rule. The public Python+RTDL
primitive contract may still be described narrowly as app-generic, but the
native tree contains app/domain/workload-shaped symbols and must not be
marketed as fully app-agnostic internally.

## Agreed Current Facts

- The Phase 1 strict regex audit over `src/native/` found a non-zero dirty
  baseline.
- The dirty baseline contains 96 unique matched native symbols using the
  directive's initial leakage vocabulary.
- Representative leakage exists across OptiX, Embree, Vulkan, HIPRT, Apple RT,
  and native oracle paths.
- Wrapper-backed Python names do not solve the architecture problem when the
  underlying C++/CUDA entry point remains app-shaped.

## Agreed Required Actions

- Keep the directive snapshot in the repo so the release gate is traceable.
- Keep the machine-readable dirty-baseline manifest in the repo so future
  cleanup can be measured mechanically.
- Treat quarantine only as an interim migration path, not as permanent
  permission to keep app-shaped native APIs.
- Expand future audits beyond the initial directive terms to catch semantic
  leakage such as `table`, `column`, `edge`, `vertex`, `agent`, and
  `trajectory`.
- Add a forward release gate that can be enabled for v1.7/v2.0 to fail unless
  release-surface native app leakage is zero or mechanically quarantined
  outside public runners.

## Agreed Engineering Direction

Python must own domain lowering. Native backends must own generic spatial
primitives, primitive packets, bounded collection, and mathematical reductions.

Performance should be recovered through partner tensor handoff, true zero-copy
or reduced-copy paths, prepared generic buffers, and generic primitive/reduction
optimization. It must not be recovered by reintroducing database, graph, robot,
GIS, Hausdorff, Jaccard, or KNN-specific native backdoors.

## Release Implication

Until a superseding report proves zero/quarantine, RTDL must not publish:

```text
RTDL native internals are fully app-agnostic.
```

The allowed interim statement is:

```text
RTDL's current public Python+RTDL surface is app-generic at the stable
primitive-contract level, while older app-shaped native compatibility/proof
paths remain excluded from that claim.
```
