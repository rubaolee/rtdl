# Goal1625 v1.6.5 OptiX Collect-K Threshold-4 A4500 Probe

## Verdict

`internal_threshold4_a4500_probe_recorded`

## Scope

- Git commit: `d659bf0e80725128715e5758bb0ec1a3c8fc66ce`
- GPU summary: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`
- Counts: `[65537, 98305, 131072]`
- Rounds: `1`
- Repeats per probe: `1`

## Results

| Count | Avg delta ms | Median delta ms | Faster rounds | Payload copies baseline/gated | Parity |
|---:|---:|---:|---:|---|---|
| 65537 | -0.032470 | -0.032470 | 1/1 | 5/0 | True |
| 98305 | -0.000690 | -0.000690 | 1/1 | 4/4 | True |
| 131072 | -0.003810 | -0.003810 | 1/1 | 0/0 | True |

## Claim Boundary

Goal1625 is internal same-host OptiX collect-k threshold-4 diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, whole-app speedup claims, release tags, or release action.
