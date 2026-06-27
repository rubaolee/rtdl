# Goal2878 Goal2868 Residual Closure Map After Conformance

Date: 2026-05-31

Verdict: **accept-with-boundary**

## Purpose

Claude's Goal2868 review is still valuable, but it reviewed the v2.5 tree before
Goals2871-2876 landed. Goal2878 records a precise closure map so the project
does not accidentally mix two different evidence timelines.

This map is not a replacement for the requested Goal2877 external review. It is
a local index that says which Goal2868 residuals are now directly covered by
newer evidence, which ones remain bounded release-review concerns, and which
newer artifacts the next reviewer should inspect.

## Residual Mapping

| Goal2868 residual | Newer evidence | Current status |
| --- | --- | --- |
| F1: legacy torch carrier is bounded and labeled, not removed | Goal2871 guards neutral-seam authority. The seam remains the only transfer/copy/lifetime authority; the legacy carrier is advisory and must not originate neutral-buffer metadata. | **Partially closed for internal readiness.** Still a release-watch item unless removed or fully seam-routed before release review. |
| F2: "7/7 harnesses pass" must not be read as Tier A/B parity | Goal2876 reran the seven-app packet after conformance closure and preserved empty claim-boundary violations. The readiness packet still blocks release, speedup, true-zero-copy, package-install, automatic Triton selection, and app-specific native-engine claims. | **Closed as wording/metadata guard.** It remains intentionally not a parity or release claim. |
| F4: CuPy/Numba conformance role is declared; confirm per-op evidence | Goal2873 added the partner x operation conformance matrix. Goal2874 backfilled Triton preview pod runtime rows. Goal2875 added Numba runtime smoke evidence and left CuPy as descriptor-only except the event-ordered hit-stream preview evidence. | **Closed for preview-runtime conformance bookkeeping.** The matrix reports zero runtime conformance gaps and still keeps release conformance false. |
| F5: determinism policy exists, but kernel-level tie-break enforcement is unproven | Goal2872 added Triton tie-break conformance smoke for grouped argmin, grouped argmax, and grouped top-k rows. Goal2873 requires those high-risk rows to point at Goal2872 evidence. | **Closed for the current high-risk Triton preview rows.** Broader future kernels must add the same kind of tie/tolerance smoke before promotion. |

## Evidence Links

Newer reports to inspect:

- `docs/reports/goal2871_hit_stream_torch_carrier_seam_authority_guard_2026-05-31.md`
- `docs/reports/goal2872_triton_tie_break_conformance_smoke_2026-05-31.md`
- `docs/reports/goal2873_v2_5_partner_conformance_matrix_2026-05-31.md`
- `docs/reports/goal2874_triton_preview_current_pod_conformance_backfill_2026-05-31.md`
- `docs/reports/goal2875_numba_runtime_conformance_smoke_2026-05-31.md`
- `docs/reports/goal2876_current_packet_after_partner_conformance_closure_2026-05-31.md`
- `docs/handoff/CALL_FOR_REVIEW_GOAL2877_V2_5_CONFORMANCE_CLOSURE_AND_CURRENT_PACKET_2026-05-31.md`

## Reviewer Instruction

Future reviewers should treat Goal2868 as a historical support review for the
Goal2773-2867 burst, not as the final review of the conformance-closure work.
The active review target is Goal2877, covering Goals2873-2876 and verifying the
partner conformance matrix, Numba/Triton/CuPy evidence boundaries, and the clean
Goal2876 seven-app packet.

## Boundary

Goal2878 is not a v2.5 release authorization.
It is not a public speedup claim.
It is not a broad RT-core claim.
It is not a whole-app speedup claim.
It is not true-zero-copy wording.
It is not package-install wording.

It does not declare v2.5 release-ready. It keeps the release gate blocked until
the user explicitly requests a release packet and a fresh 3-AI release consensus
is produced.

## Validation

Focused local validation:

```text
py -3 -m unittest tests.goal2878_goal2868_residual_closure_mapping_test
```

Expanded local v2.5 residual/conformance slice:

```text
py -3 -m unittest \
  tests.goal2878_goal2868_residual_closure_mapping_test \
  tests.goal2876_current_packet_after_partner_conformance_closure_test \
  tests.goal2875_numba_runtime_conformance_smoke_test \
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test \
  tests.goal2873_v2_5_partner_conformance_matrix_test \
  tests.goal2872_triton_tie_break_conformance_smoke_test \
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test \
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test \
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 47 tests in 1.411s
OK (skipped=6)
```

Pod validation from pushed `main`:

```text
commit: d8d63b26
scope:
  tests.goal2878_goal2868_residual_closure_mapping_test
  tests.goal2876_current_packet_after_partner_conformance_closure_test
  tests.goal2875_numba_runtime_conformance_smoke_test
  tests.goal2874_triton_preview_current_pod_conformance_backfill_test
  tests.goal2873_v2_5_partner_conformance_matrix_test
  tests.goal2872_triton_tie_break_conformance_smoke_test
  tests.goal2871_hit_stream_torch_carrier_seam_authority_guard_test
  tests.goal2870_v2_5_last_day_review_intake_and_runner_fail_closed_hardening_test
  tests.goal2806_v2_5_internal_readiness_packet_test

Ran 47 tests in 1.887s
OK
```

## Codex Verdict

`accept-with-boundary`
