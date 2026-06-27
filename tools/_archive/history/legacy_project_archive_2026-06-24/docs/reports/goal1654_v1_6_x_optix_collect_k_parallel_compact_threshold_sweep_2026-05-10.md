# Goal1654 v1.6.x OptiX Collect-K Parallel Compact Threshold Sweep

## Verdict

`parallel_compact_min_capacity_4096_retained`

This records an OptiX `COLLECT_K_BOUNDED` threshold sweep for
`RTDL_OPTIX_COLLECT_K_PARALLEL_COMPACT_MIN_CAPACITY` after the Goal1650
fastest-capacity fix.

## Question

The accepted CUB fastest path at `candidate_count=262144` uses parallel compact
levels starting at output capacity `4096`, producing `27` merge-side launches.
This sweep tested whether delaying parallel compact could reduce launch count
enough to improve total time.

## Measured Scope

- Host: pod `root@213.173.98.25 -p 17374`.
- GPU: NVIDIA RTX A4500.
- Commit: `7fee62b0f...`.
- OptiX SDK: `/root/vendor/optix-sdk`.
- CUDA prefix: `/usr/local/cuda`.
- Candidate count: `262144`.
- Repeats: `5`.

## Results

| Min Capacity | Accepted Evidence | Parity | Total ms | Merge Launch ms | Merge Sync ms | Merge Launches | Metadata Fields |
|---:|---|---|---:|---:|---:|---:|---:|
| 4096 | true | true | 0.673688 | 0.165354 | 0.321318 | 27 | 129 |
| 8192 | false, diagnostic smoke | true | 1.76829 | 0.185695 | 1.36013 | 24 | 385 |
| 16384 | false, diagnostic smoke | true | 4.18277 | 0.211865 | 3.73605 | 21 | 513 |
| 32768 | false, diagnostic smoke | true | 9.0233 | 0.243677 | 8.52732 | 18 | 577 |
| 65536 | false, diagnostic smoke | true | 18.6545 | 0.253238 | 18.1195 | 15 | 609 |

Artifacts:

- `docs/reports/goal1654_min_cap_4096_262144.json`
- `docs/reports/goal1654_min_cap_4096_262144.jsonl`
- `docs/reports/goal1654_min_cap_4096_262144.md`
- `docs/reports/goal1654_min_cap_8192_262144.json`
- `docs/reports/goal1654_min_cap_8192_262144.jsonl`
- `docs/reports/goal1654_min_cap_8192_262144.md`
- `docs/reports/goal1654_min_cap_16384_262144.json`
- `docs/reports/goal1654_min_cap_16384_262144.jsonl`
- `docs/reports/goal1654_min_cap_16384_262144.md`
- `docs/reports/goal1654_min_cap_32768_262144.json`
- `docs/reports/goal1654_min_cap_32768_262144.jsonl`
- `docs/reports/goal1654_min_cap_32768_262144.md`
- `docs/reports/goal1654_min_cap_65536_262144.json`
- `docs/reports/goal1654_min_cap_65536_262144.jsonl`
- `docs/reports/goal1654_min_cap_65536_262144.md`

## Decision

`do_not_raise_parallel_compact_threshold`

Raising the threshold reduces merge launch count, but it regresses total time
by moving more work onto the slower non-parallel compact merge path and
increasing metadata traffic. The default `4096` threshold remains the measured
best option in this sweep.

## Claim Boundary

This report records a threshold sweep only. It does not authorize public
speedup wording, stable `COLLECT_K_BOUNDED` promotion, fastest-candidate
promotion, release tags, or release action.
