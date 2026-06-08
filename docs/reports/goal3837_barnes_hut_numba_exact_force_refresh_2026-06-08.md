# Goal3837 Barnes-Hut Numba Exact-Force Refresh

Date: 2026-06-08

Status: internal current-head A5000 evidence.

## Purpose

Barnes-Hut is one of the benchmark apps where the promoted RTDL primitive path
collects generic frontier/candidate information, while the force-law
continuation remains application code. The project requirement is that users
who need that continuation should have a high-performance Numba reference path,
not only a CuPy RawKernel path.

Goal3837 refreshes current-head A5000 evidence for the existing no-RawKernel
Numba exact all-pairs force-vector reference and compares it against the CuPy
RawKernel baseline under the same app contract. This is not a native engine change
and not a Barnes-Hut tree-opening acceleration claim.

## Evidence

Pod:

`ssh root@69.30.85.203 -p 22057 -i ~/.ssh/id_ed25519`

Repository commit:

`576a5ba7`

GPU:

`NVIDIA RTX A5000, 580.126.09`

Command:

```bash
PYTHONPATH=.pydeps_goal3788_numba:src:. \
python scripts/goal3762_barnes_hut_numba_block_reduce_force_probe.py \
  --body-counts 1024,2048,4096,8192,16384 \
  --repeat 10 \
  --warmup 3 \
  --correctness-body-count 256 \
  --output docs/reports/goal3837_barnes_hut_numba_exact_force_refresh_a5000/summary.json
```

Artifact:

- `docs/reports/goal3837_barnes_hut_numba_exact_force_refresh_a5000/summary.json`

The artifact reports `all_force_counts_match: true`, `matches_oracle: true` for
the correctness probe, and all claim-boundary flags false.

## Results

| Body count | CuPy median seconds | Numba median seconds | Numba/CuPy speedup |
| ---: | ---: | ---: | ---: |
| 1,024 | 0.005178 | 0.006035 | 0.858x |
| 2,048 | 0.010118 | 0.010610 | 0.954x |
| 4,096 | 0.017415 | 0.017653 | 0.986x |
| 8,192 | 0.034735 | 0.038030 | 0.913x |
| 16,384 | 0.081339 | 0.093814 | 0.867x |

Summary:

- minimum Numba/CuPy speedup: `0.858x`;
- geomean Numba/CuPy speedup: `0.914x`;
- force-row counts match on every scale.

## Tuning Notes

Two remote-only tuning probes were run before changing source:

- smaller 128/256-thread block-reduction variants;
- a higher threshold that kept smaller cases on the one-thread-per-source Numba
  kernel.

Those probes did not produce a decisive improvement. The current 512-thread block-reduction strategy remains the default because the threshold probe fell
to `0.831x` geomean versus CuPy, and the 256-thread variant only produced a
small/noisy improvement without changing the large-scale conclusion.

## Interpretation

The Barnes-Hut Numba reference is acceptable as a no-RawKernel user path, but
it is not the fastest measured exact-force continuation. The practical guidance
is:

```text
Use the primitive-first Barnes-Hut path for generic RTDL candidate/frontier
work. When exact force-vector continuation is needed, Numba is a valid
no-RawKernel reference, while CuPy remains the faster measured continuation on
this A5000 packet.
```

This means Barnes-Hut does not block the partner-choice documentation goal:
users can write the continuation with Numba. It also means Barnes-Hut remains a
performance-development target if the project wants Numba to beat CuPy, not
merely approach it.

## Claim Boundary

This report does not authorize:

- release action;
- public speedup wording;
- broad N-body acceleration claims;
- hierarchical Barnes-Hut acceleration claims;
- RT-core speedup claims;
- true zero-copy claims;
- automatic partner selection.

It is internal current-head evidence for the current Barnes-Hut exact
force-vector continuation contract.
