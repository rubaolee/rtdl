# RTDL v3.0 Release Statement

Status: released as `v3.0`.

The current released version is `v3.0`.

## Statement

RTDL `v3.0` is the source-tree major release that closes the current ten-app
benchmark route project and publishes a coherent Python+partner+RTDL
programming surface. It is the first RTDL release where current benchmark-app
routes, app-author guidance, source-tree diagnostics, and claim boundaries are
tied to one validation surface.

## What This Release May Claim

- RTDL has a current ten-app benchmark route matrix, and Goal4614 records every
  app as a closed current target.
- The current app-author rule is primitive-first, prepared where useful,
  partner-explicit when custom continuation is required, and claim-bounded.
- The canonical release validation command is
  `scripts/run_test_matrix.py --group v3_current`.
- The V3 public docs are source-tree docs: run with `PYTHONPATH=src:.` or an
  optional local editable checkout.
- Embedding, C ABI, SDK packaging, generated bindings, device-buffer execution,
  external stream ordering, zero-copy framework interop, and device-callable
  fusion are explicitly V4.0 scope.

## What This Release Must Not Claim

- package-install, PyPI, wheel, or stable SDK availability;
- generated Python/Rust/Julia/C# binding packages;
- automatic partner selection;
- arbitrary CuPy, Numba, CUDA, PyTorch, or JAX program acceleration;
- broad RT-core acceleration;
- whole-application speedups for every benchmark;
- RTDL beats RayJoin, X-HD, RTNN, RT-Graph, LibRTS, or other specialized author
  implementations as whole systems;
- paper reproduction unless a row-specific packet explicitly authorizes it;
- public true-zero-copy or complete device residency;
- C ABI device-buffer query execution;
- external CUDA stream ordering;
- arbitrary raw OptiX callback exposure as the stable user API;
- app-specific native-engine logic as the RTDL extension model.

## Evidence Pointers

- [Goal4614 V3 current-scope completion gate](../../reports/goal4614_v3_0_m215_current_scope_completion_gate_2026-06-18.md)
- [Goal4538 V3 completion review consensus](../../reports/goal4538_v3_0_m139_v3_completion_review_consensus_2026-06-17.md)
- [V3.0 app-author implementation strategy](../../learn/v3_0_app_author_implementation_strategy.md)
- [Benchmark evidence index](../../learn/benchmark_evidence_index.md)

## Short Public Wording

Use this form when a compact release sentence is needed:

```text
RTDL v3.0 is a source-tree major release that closes the current ten-app
benchmark route matrix and publishes primitive-first and partner-explicit app
author guidance, while keeping embedding/SDK work in V4.0 and performance
claims row-scoped and evidence-bound.
```
