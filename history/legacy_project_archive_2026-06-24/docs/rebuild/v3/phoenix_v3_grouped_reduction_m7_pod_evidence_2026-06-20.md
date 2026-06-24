# Phoenix V3 Grouped-Reduction M7 Pod Evidence

Status: fresh M7-designated pod rerun intake, not M7 promotion.

This is not V3 release authorization and not public speedup wording.

Supersession note: the modeled repeat100 values in this post-run intake are no
longer the current grouped_sum candidate wording. They are superseded by actual
repeat100 pod evidence in
[Phoenix V3 Grouped-Reduction Sum Actual Repeat100 Pod Evidence](phoenix_v3_grouped_reduction_sum_repeat100_actual_pod_evidence_2026-06-20.md),
which is itself superseded for current candidate values by
[Phoenix V3 Grouped-Reduction Scalar-Broadcast Optimization Pod Evidence](phoenix_v3_grouped_reduction_scalar_broadcast_optimization_pod_evidence_2026-06-20.md).

## Scope

This run executed the reviewed grouped-reduction M7 rerun packet:

```text
docs/rebuild/v3/phoenix_v3_grouped_reduction_m7_rerun_packet_2026-06-20.md
docs/reviews/codex_phoenix_v3_grouped_reduction_m7_rerun_packet_2ai_consensus_2026-06-20.md
```

Artifact root:

```text
docs/rebuild/v3/evidence/phoenix_v3_grouped_reduction_m7_20260620
```

Pod:

```text
root@213.173.108.14 -p 11592
NVIDIA RTX 4000 Ada Generation
```

## Gates

Pre-run gates passed:

- GPU Python environment gate: pass for CuPy RawKernel, Torch CUDA, and Numba CUDA JIT.
- OptiX hardware gate: pass, RT-capable NVIDIA GPU present.
- Claim-boundary gate: pass, including `whole_app_speedup_claim_authorized=false`.
- Native Embree and OptiX build: pass.

The run completed with:

```text
m7_execution.status: 0
```

## Fresh Rerun Inputs

Both fresh source files used `warmup=3`:

```text
m7_grouped_reduction_262144_warmup3.json
m7_grouped_reduction_524288_warmup3.json
```

Post-run intake:

```text
m7_grouped_reduction_post_run_intake.json
m7_grouped_reduction_post_run_intake.md
```

## Result

```text
status: grouped_reduction_m7_post_run_intake_not_promoted
release_authorized: false
public_speedup_claim_authorized: false
whole_app_speedup_claim_authorized: false
M7-qualified release rows: 0
```

Repeat-aware summary:

| Scale | Mode | Hot OptiX/Embree | Break-even repeats | Repeat 1 end-to-end | Repeat 100 end-to-end | Main blocker |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| 262,144 | count | 9.538x | 14 | 0.736x | 2.452x | single-query loss |
| 262,144 | sum | 224.269x | 2 | 0.999x | 32.395x | single-query near-parity/loss |
| 524,288 | count | 8.819x | 14 | 0.683x | 2.633x | single-query loss |
| 524,288 | sum | 180.509x | 1 | 1.016x | 33.608x | public contract missing |

All four rows match CPU reference and all OptiX hot prepared-query rows are
faster than Embree. That is useful internal evidence for repeated prepared
queries. It is not enough for M7 promotion because three rows do not win
single-query end-to-end, and the only repeat-1 win is small at 1.016x.

## Interpretation

The fresh warmup=3 rerun changes the story from the old feasibility packet:

- the huge 213s+ old setup/cold issue is gone in this fresh run;
- the strongest hot-query row is now 224.269x, but it is not an end-to-end
  speedup;
- count rows need about 14 repeats to break even;
- sum rows become compelling for repeated queries, especially by repeat 100;
- public wording still needs a prepared-query contract, repeat policy, and
  external review of the fresh result.

## Boundary

Allowed internal reading:

```text
The generic prepared grouped-reduction primitive has fresh pod evidence for
large hot-query wins and repeat-100 end-to-end wins under warmup=3.
```

Forbidden public reading:

```text
Do not claim the fresh grouped_reduction hot-query ratios, up to 224.269x, are
end-to-end speedups. Do not claim whole-database speedup. Do not promote M7
before fresh-result external review and a public prepared-query contract.
```

## Goal-Level Decision Audit

Decision: accept the fresh pod run as post-run intake evidence, not M7
promotion.

1. Was I foolish?

   No. The run followed a reviewed packet and the post-run intake keeps release
   authorization false.

2. If yes, what actions made the decision foolish?

   The foolish action would be to turn 224.269x hot-query into an end-to-end
   claim or to ignore the repeat-1 losses.

3. Was there another path?

   Yes. I could have stopped at the feasibility packet. That would leave the
   old warmup asymmetry unresolved.

4. Can I now try a different path that actually solves the problem?

   Yes. The next path is external review of this fresh result, then either a
   public prepared-query M7 contract or an explicit decision that
   grouped_reduction remains internal.
