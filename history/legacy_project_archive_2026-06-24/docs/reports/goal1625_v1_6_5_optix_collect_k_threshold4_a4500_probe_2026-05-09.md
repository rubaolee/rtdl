# Goal1625 v1.6.5 OptiX Collect-K Threshold-4 A4500 Probe

## Verdict

`internal_threshold4_a4500_probe_recorded`

## Scope

- Git commit: `30c8cb9bb44c53544156163602509d57a13867b6`
- GPU summary: `NVIDIA RTX A4500, 550.127.05, 20470 MiB`
- Counts: `[65536, 65537, 65538, 65552, 69632, 69633]`
- Rounds: `5`
- Repeats per probe: `31`

## Results

| Count | Avg delta ms | Median delta ms | Faster rounds | Payload copies baseline/gated | Parity |
|---:|---:|---:|---:|---|---|
| 65536 | 0.016252 | 0.026940 | 1/5 | 0/0 | True |
| 65537 | -0.028319 | -0.023551 | 5/5 | 5/0 | True |
| 65538 | -0.022211 | -0.022162 | 4/5 | 5/0 | True |
| 65552 | -0.023413 | -0.022011 | 4/5 | 5/0 | True |
| 69632 | -0.014968 | -0.017811 | 5/5 | 4/0 | True |
| 69633 | -0.009190 | -0.001880 | 4/5 | 4/4 | True |

## Claim Boundary

Goal1625 is internal same-host OptiX collect-k threshold-4 diagnostic evidence only. It does not authorize public speedup wording, true zero-copy wording, stable COLLECT_K_BOUNDED promotion, broad RTX/GPU wording, whole-app speedup claims, release tags, or release action.
