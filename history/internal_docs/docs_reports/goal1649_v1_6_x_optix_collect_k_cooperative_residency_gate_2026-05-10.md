# Goal1649 v1.6.x OptiX Collect-K Cooperative Residency Gate

## Verdict

`full_level_cooperative_fusion_rejected_by_residency_gate`

## Scope

- GPU summary: `NVIDIA RTX A4500, 570.195.03, 20470 MiB`
- Capability artifact: `C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review\docs\reports\goal1647_pod_a4500_cooperative_capability_2026-05-10.json`
- Candidate count: `262144`
- Tile size: `2048`
- Threads per block: `256`
- Multiprocessor count: `56`
- Conservative max resident blocks bound: `896`
- Conservative max resident threads bound: `86016`

## Levels

| Level | Input segments | Pair count | Output capacity | Blocks/pair | Required blocks | Required threads | Fits gate |
|---:|---:|---:|---:|---:|---:|---:|---|
| 0 | 128 | 64 | 4096 | 16 | 1024 | 262144 | False |
| 1 | 64 | 32 | 8192 | 32 | 1024 | 262144 | False |
| 2 | 32 | 16 | 16384 | 64 | 1024 | 262144 | False |
| 3 | 16 | 8 | 32768 | 128 | 1024 | 262144 | False |
| 4 | 8 | 4 | 65536 | 256 | 1024 | 262144 | False |
| 5 | 4 | 2 | 131072 | 512 | 1024 | 262144 | False |
| 6 | 2 | 1 | 262144 | 1024 | 1024 | 262144 | False |

## Interpretation

A full-level cooperative fusion of the existing row-parallel merge shape is rejected when any level requires more blocks or threads than can be resident together. The current A4500 long workload shape requires all level blocks to be globally resident for `grid.sync()`, so this gate prevents spending pod time on an impossible full-level cooperative launch shape.

## Claim Boundary

Goal1649 is a cooperative residency design gate only. It rejects or permits a candidate grid shape before implementation work. It is not performance evidence and does not authorize public speedup wording, stable COLLECT_K_BOUNDED promotion, release tags, or release action.
