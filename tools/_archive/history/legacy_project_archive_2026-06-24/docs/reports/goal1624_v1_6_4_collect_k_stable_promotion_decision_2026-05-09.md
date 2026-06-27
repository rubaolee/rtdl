# Goal1624 v1.6.4 COLLECT_K_BOUNDED Stable-Promotion Decision

Date: 2026-05-09

## Verdict

DEFER STABLE PROMOTION. Keep `COLLECT_K_BOUNDED` experimental.

The v1.6.4 evidence chain is now strong enough to say that the collect-k
candidate is reproducible, bounded, externally reviewed, and green on a
representative RTX A4500 collect-k test sweep. It is not yet strong enough to
promote `COLLECT_K_BOUNDED` into the stable primitive set.

The accepted evidence is not public speedup evidence.

## Evidence Accepted

| Evidence | Status | Artifact |
| --- | --- | --- |
| Exact bounds stress | Accepted | `docs/reports/goal1614_v1_6_4_collect_k_bounds_stress_2026-05-09.md` |
| Reduced-copy/prepared-output benchmark package | Accepted | `docs/reports/goal1615_v1_6_4_collect_k_reduced_copy_benchmark_2026-05-09.md` |
| RTX A4500 required-backend packet | Accepted | `docs/reports/goal1620_v1_6_4_rtx_a4500_collect_k_packet_evidence_2026-05-09.md` |
| Latest-main RTX A4500 packet replay | Accepted | `docs/reports/goal1622_v1_6_4_rtx_a4500_latest_main_repro_packet_2026-05-09_report.md` |
| Latest-main RTX A4500 collect-k sweep | Accepted | `docs/reports/goal1623_v1_6_4_rtx_a4500_collect_k_test_sweep_2026-05-09.md` |

## Deferral Reasons

Stable primitive promotion is deferred for four concrete reasons:

1. The standing stable primitive target still excludes `COLLECT_K_BOUNDED`.
2. The current collect-k implementation still contains multiple diagnostic,
   gated-candidate, and environment-flagged optimization paths.
3. The accepted RTX evidence is packet/sweep/reproducibility evidence, not
   public speedup evidence and not broad GPU evidence.
4. The accepted reduced-copy evidence is not true zero-copy evidence.

## Accepted Classification

For v1.6.4, the accepted classification is:

`documented_experimental_candidate_with_representative_rtx_reproducibility_evidence`

This classification allows continued engineering, benchmarking, and bounded
experimental documentation. It does not move `COLLECT_K_BOUNDED` into the
stable primitive set.

## Next Stable-Promotion Requirements

Before a future stable-promotion decision can be accepted, the project should
prepare a new package that includes:

- a stable public API contract for collect-k, not only diagnostic/candidate
  flags;
- reviewed documentation explaining exact semantics, overflow behavior, output
  bounds, ordering guarantees, and backend coverage;
- measured same-contract performance evidence if any public performance wording
  is desired;
- a claim-boundary audit proving no true-zero-copy or broad-GPU wording leaks
  into public docs;
- fresh 3-AI consensus for the stable-promotion decision.

## Claim Boundary

Goal1624 does not authorize public speedup wording, true zero-copy wording,
whole-app speedup claims, broad RTX/GPU wording, stable `COLLECT_K_BOUNDED`
promotion, release tags, or release action.

This decision closes the current v1.6.4 promotion-decision loop by explicitly
deferring stable promotion rather than leaving the blocker ambiguous.
