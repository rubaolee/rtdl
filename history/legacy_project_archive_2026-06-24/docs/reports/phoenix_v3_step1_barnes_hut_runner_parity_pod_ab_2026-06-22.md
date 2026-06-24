# Phoenix V3 Step-1 Replacement: Barnes-Hut Runner Parity POD A/B

Date: 2026-06-22
Status: `step1_replacement_candidate_evidence_not_release`
Evidence: `docs/rebuild/v3/evidence/phoenix_v3_barnes_hut_runner_parity_pod_ab_fixed_20260622_182718/`
Local base commit before uncommitted Phoenix V3 runner edits: `8e0f052bffec02507aaf5ed05f75dfe995f39883`
Remote source tree: `/root/rtdl_v3_rebuild_20260620/current` on `213.173.108.14:11592`; this remote tree is not a git checkout, so evidence `summary.json` correctly records `git_commit: null`.

## Result

The Barnes-Hut aggregate-tree fused weighted-vector route is now productized through the Phoenix V3 prepared-execution session runner and preserves the existing app-front-door fused Numba CUDA route's hot-call performance.

Primary control: existing app-front-door `fused_frontier_force_sum_bucketized_numba_cuda`.

Historical reference: old prepared OptiX frontier-emission route, included only as a no-go reference.

| Bodies | Runner hot median (s) | Existing fused control hot median (s) | Runner/control speedup | Historical OptiX hot median (s) | Historical OptiX / runner |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 32,768 | 0.010791808 | 0.010797493 | 1.000527x | 0.094951779 | 8.798505x |
| 65,536 | 0.015773401 | 0.015763111 | 0.999348x | 0.214636602 | 13.607503x |
| 131,072 | 0.041481458 | 0.041403107 | 0.998111x | 0.714862727 | 17.233308x |

Geomean runner/control: `0.999328063165968x`.

Geomean historical OptiX/runner: `12.730691398985789x`.

## Gates

- `failed_checks`: `[]`
- `runner_used_all_samples`: `true`
- `runner_runtime_trunk_executes_all_samples`: `true`
- `runner_internal_device_residency_all_samples`: `true`
- `runner_hot_path_host_materialization_absent`: `true`
- `runner_no_frontier_or_contribution_host_materialization`: `true`
- `runner_control_output_equivalence_all_sizes`: `true`
- `all_claim_flags_false`: `true`

Output equivalence against the existing fused control passed at all three sizes by contribution count and checksum X/Y parity.

## Interpretation

This is a valid Phoenix V3 Step-1 replacement candidate for one Set-A family: a real aggregate-tree/vector-accumulation route now flows through the productized runner without losing the existing fused partner performance.

This is not evidence that the runner wrapper itself is faster than the existing fused route. It is evidence that the reusable runtime path can carry that high-performance route at parity while preserving internal residency and claim boundaries.

The large speedup versus the old prepared OptiX frontier route is historical no-go reference only. It must not become the primary performance claim.

## Second-AI Blocker And Fix Record

Initial second-AI review returned `blocked_needs_fix` and found three blockers:

- skip-historical mode could still produce candidate/material status;
- runner/control correctness equivalence was not gated;
- the helper could mark trunk execution true from weak output metadata.

All three were fixed before the recorded POD run:

- skip-historical is smoke-only and cannot produce candidate/material status;
- `runner_control_equivalence_rows` and `runner_control_output_equivalence_all_sizes` gate output equivalence;
- the helper requires returned contract, partner, and source/target/tree counts to match before `runtime_trunk_executes_end_to_end=True`.

Initial review record: `docs/reviews/second_ai_phoenix_v3_barnes_hut_runner_initial_review_2026-06-22.md`.

Fixed implementation review: `docs/reviews/second_ai_phoenix_v3_barnes_hut_runner_fixed_review_2026-06-22.md`, verdict `accept_ready_for_pod_report`, remaining blockers `none`.

## Goal-Level Decision Audit

Decision: accept the fixed Barnes-Hut runner parity POD A/B as Step-1 replacement candidate evidence, not release evidence.

1. Was I foolish? Partly before the fix: yes, because I launched the first full pod run before the second-AI review returned.
2. If yes, what actions made the decision foolish? The initial script allowed skip-historical smoke to look like a candidate, missed a runner/control checksum gate, and allowed weak helper metadata to overstate trunk success.
3. Was there another path? Yes. Wait for review, fix those gates, then run pod.
4. Can I now try a different path? Yes. The fixed path has been run: strict dual comparison, runner/control output equivalence, exact helper metadata gates, and all release/public/all-app authorizations closed.

## Non-Authorization

This packet authorizes no Phoenix V3 release, no broad V3-over-V2.x wording, no public speedup claim, no RT-core speedup claim, no true-zero-copy claim, no automatic partner selection, and no all-app pod run.
