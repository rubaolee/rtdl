# Goal1657 v1.6.x OptiX Collect-K Four-Way Merge Probe

## Verdict

`four_way_merge_candidate_rejected`

This records a diagnostic native four-way merge probe for OptiX
`COLLECT_K_BOUNDED`. The probe preserves parity against a two-level binary
reference merge, but the production-relevant measured shape is slower.

## Scope

- Host: pod `root@213.173.98.25 -p 17374`.
- GPU: NVIDIA RTX A4500.
- Base commit: `3877f6f40b0158e2ae284eec3ddbf8748c1d0071` plus the local
  Goal1657 diagnostic patch.
- OptiX SDK: `/root/vendor/optix-sdk`.
- CUDA prefix: `/usr/local/cuda`.
- Probe script: `scripts/goal1657_v1_6_x_optix_collect_k_four_way_merge_probe.py`.
- Native ABI: `rtdl_optix_collect_k_four_way_merge_probe`.

## Results

The diagnostic compares:

- Reference: two binary compact-level merge blocks over four sorted segments.
- Candidate: one four-way materialize+mark block plus prefix and compact.

At `segment_capacity=2048` and `repeats=1000`:

| groups | reference us/replay | four-way us/replay | reference/four-way | mismatches |
|---:|---:|---:|---:|---:|
| 1 | 28.105750 | 26.291391 | 1.069x | 0 |
| 4 | 32.214820 | 32.567389 | 0.989x | 0 |
| 16 | 53.450896 | 60.102464 | 0.889x | 0 |
| 32 | 76.026628 | 103.894742 | 0.732x | 0 |

Artifacts:

- `docs/reports/goal1657_four_way_smoke.json`
- `docs/reports/goal1657_four_way_smoke.md`
- `docs/reports/goal1657_four_way_groups_1_4_16_32_seg2048_repeats1000.json`
- `docs/reports/goal1657_four_way_groups_1_4_16_32_seg2048_repeats1000.md`

## Decision

`do_not_promote`

The four-way probe has useful correctness evidence, but it does not produce the
needed performance signal at the production-relevant first-level shape
(`group_count=32`). The reduced merge depth is outweighed by heavier per-row
rank/search work and atomic mark-count accumulation.

The diagnostic ABI remains isolated for reproducibility. It is not enabled by
`RTDL_OPTIX_COLLECT_K_FASTEST_CANDIDATE` and does not alter production
`COLLECT_K_BOUNDED` behavior.

## Claim Boundary

This report records a rejected diagnostic candidate only. It does not authorize
public speedup wording, stable `COLLECT_K_BOUNDED` promotion, fastest-candidate
promotion, release tags, or release action.
