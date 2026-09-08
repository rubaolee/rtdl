# Post-Formal CPU-Affinity Sensitivity Plan

Date: 2026-09-08, America/New_York. Status: fixed before observing any
performance result from this sensitivity run.

## Purpose and evidence boundary

The passing formal successor transaction used logical CPU 8 after an earlier
non-evidence scheduling diagnosis. This study tests whether the two sub-
millisecond prepared rows that previously failed an unlocked run are unusually
favorable on CPU 8. It does not alter, replace, pool with, or relabel the
formal transaction. It is post-formal descriptive sensitivity evidence only.

No sensitivity result may be used to select another CPU, rerun only an adverse
CPU, weaken a threshold, or silently broaden the manuscript claim. Every
worker, timeout, error, and adverse ratio is retained. The formal archive at
SHA-256
`ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc`
remains immutable.

## Fixed machine and implementation identities

- GPU: NVIDIA RTX A4500, UUID
  `GPU-5dbda20d-af85-650e-7250-10b265a77143`, compute capability 8.6,
  driver 550.127.05, `CUDA_VISIBLE_DEVICES=0`.
- CPU: AMD EPYC 7352, 24 physical cores and 48 logical CPUs, one socket and
  one NUMA node. The allowed cpuset is exactly `0-47`; CPUs `24-47` are SMT
  siblings of physical cores `0-23`.
- Container CPU quota: 1,020,000/100,000, approximately 10.2 aggregate cores.
- Successor source: commit
  `02e84374fc092d2bb916cca633eda9592b4ecf07`, tree
  `8aad15d686bbc9e1c3b11df998898a0a063a01f1`.
- Base formal config SHA-256:
  `491d399343fee27fbf97f6a72837ff38b4b7d04fa5324525cf3b3780caf72e1d`.
- Native DSO SHA-256:
  `5edb9ec3e542b64bf0696c6df9a164448aecd6b5b51f1fdd78ba6e8c791dd2af`.
- Frozen worker: `scripts/v4_long_workload_worker.py` from the successor
  source. The only per-CPU config change is `common.cpu_affinity.cpu_ids`.

GPU clocks cannot be locked on this provider. No other compute process was
reported by `nvidia-smi` immediately before fixing this plan.

## Fixed population

All 48 allowed logical CPUs are tested in ascending numeric order:
`0, 1, ..., 47`. This is an exhaustive cpuset study, not a sampled CPU subset.

Two units and only their prepared endpoints are tested:

| Unit | Warmups | Timed repetitions per worker | Reason |
| --- | ---: | ---: | --- |
| `particle_tracking` | 1 | 32 | Failed the unlocked transaction's worst-block gate and is host-sensitive. |
| `librts__parks__range_contains` | 1 | 4 | Failed the unlocked transaction's worst-block gate and is host-sensitive. |

The compared arms are `new_v4` and `pyoptix`. `old_v4` is excluded because
this study asks whether the successor/PyOptiX engineering conclusion depends
on CPU selection, not whether the predecessor improved.

For every `(unit, cpu)` pair there are exactly two paired blocks:

1. block 0 order: `new_v4`, then `pyoptix`;
2. block 1 order: `pyoptix`, then `new_v4`.

Each arm is a fresh worker process. Workers run serially. The fixed population
is `48 CPUs x 2 units x 2 blocks x 2 arms = 384 workers`. Retry and discard are
forbidden. The per-worker timeout remains 900 seconds. A timeout or invalid
worker remains in the raw population and makes that CPU/unit pair incomplete;
it is not replaced.

## Fixed validation and analysis

For every worker, require the frozen worker's `PASS` status, exact registered
source/tree/library/config identities, exact pre/post singleton CPU affinity,
the registered sample and warmup counts, and zero retry/discard. Within each
pair, require identical input identity and output SHA-256 across arms.

For each valid block, compute
`median(new_v4 primary samples) / median(pyoptix primary samples)`. For each
CPU and unit, report both block ratios, their median, and their full range.
Report all 48 CPU rows without filtering. Then report, per unit:

- the median, minimum, and maximum of the 48 per-CPU medians;
- the count of CPU medians at or below 1.20;
- the count of CPUs whose two block ratios are both at or below 1.35;
- CPU 8's exact two ratios, median, and rank among all 48 CPU medians;
- separate summaries for primary hardware threads `0-23` and SMT siblings
  `24-47`.

No confidence interval, broad hardware claim, or formal gate pass is inferred
from these two-block descriptive rows. Formal CPU 8 numbers may be shown next
to sensitivity CPU 8 numbers but are never pooled. If the study is incomplete,
the missing/error population is reported exactly and the limitation remains
open.

## Output custody

The run directory is create-only and separate from `FORMAL_V2`. It retains the
fixed schedule, all per-CPU configs, worker JSON, append-only journals, raw
stdout/stderr, launch records, machine snapshots, and the final descriptive
projection. The directory is archived once, hashed, copied to the repository
without changing bytes, and independently recounted from a different clean
checkout without importing project modules before any use in manuscript
wording.
