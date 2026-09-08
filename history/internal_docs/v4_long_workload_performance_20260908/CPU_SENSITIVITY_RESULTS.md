# Post-Formal CPU-Affinity Sensitivity Results

Date: 2026-09-08, America/New_York.

Status:
`PASS__RAW_AND_INDEPENDENT_RECOUNT_COMPLETE__ADVERSE_TO_CPU_INVARIANCE__NOT_POOLED`.

## Answer first

The fixed 384-worker study completed without retry, discard, timeout, output
mismatch, or non-zero worker exit. Independent recounts from clean Git
checkouts passed under ordinary and optimized Python and produced
byte-identical output. The custody result is therefore complete.

The performance result does **not** establish CPU or short-row invariance. Most
logical-CPU medians met the remediation target, but not all CPUs and not all
individual blocks did. More importantly, CPU 8 was not uniformly favorable:
Particle's two-block CPU-8 median was `1.399874x`, rank 47 of 48 from lowest to
highest, whereas its separate formal eight-block median had been `0.772559x`.
LibRTS range on CPU 8 had a `0.804614x` median and rank 6 of 48.

This does not alter or invalidate the exact formal transaction: all ten formal
rows still met their preregistered gates in that retained population. It does
show that the sub-millisecond prepared rows are temporally unstable and cannot
support a general performance guarantee. This study is descriptive, is not
pooled with the formal transaction, and authorizes no public claim.

## Fixed contract

The plan was committed before observing any sensitivity performance result as
`CPU_SENSITIVITY_PLAN.md` at commit `c54bce034`. It fixed:

- all allowed logical CPUs `0..47`, in ascending order;
- `particle_tracking` and `librts__parks__range_contains`, prepared endpoint;
- two blocks per CPU and unit, one in each arm order;
- `new_v4` and public `pyoptix` only;
- one fresh process per arm, 384 workers total;
- one warmup per worker, then 32 Particle or four LibRTS samples;
- no retry or discard and a 900-second worker timeout; and
- full reporting of all CPUs and adverse rows.

The measured application source remained commit
`02e84374fc092d2bb916cca633eda9592b4ecf07`, tree
`8aad15d686bbc9e1c3b11df998898a0a063a01f1`. This study did not modify a
workload, implementation, output contract, timer, estimator, or threshold.

## Custody and independent reconstruction

| Object | Identity |
| --- | --- |
| GPU | NVIDIA RTX A4500, CC 8.6, UUID `GPU-5dbda20d-af85-650e-7250-10b265a77143` |
| Driver / OptiX / PyOptiX | `550.127.05` / `8.0.0` / `9.1.0` |
| Host CPU allocation | AMD EPYC 7352; 48 logical CPUs, 24 cores; cpuset `0-47`; cgroup quota about 10.2 cores |
| Start / completion | `2026-09-08T13:53:14.049722232+00:00` / `2026-09-08T14:51:32.577638968+00:00` |
| Controller | 7,480 bytes; SHA-256 `c7072ce8867f9dd11f0719daa52336636440525bd272fae64b1e646863a6c0bd` |
| Raw archive | 877,815 bytes; 2,003 members; SHA-256 `1f6f25512cbb781df2b75a204e1d3baad1e853179473a6616df6ec39e5629959` |
| Recount implementation | commit `98cce4a0fe8ec817b2d9610b651a8a8e54f25062`, tree `7ab07c5644a0c8d9183a104367acdd850d89744d` |
| Recount script | SHA-256 `c8d5866c9e29ead42b8cf401e4f8ce2b2e64b01ac854497ffb156320819794ee` |
| Recount output | 93,641 bytes; SHA-256 `005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0` |

The hardened recount validates the exact 384-row schedule, all raw member
sets and hashes, all launch and progress records, all worker and journal event
populations, 384 distinct process IDs, exact source/tree/native/Python/config
identities, pre/post singleton affinity, input parity, and output hashes. It
also requires both pre-run and post-run GPU compute-process snapshots to be
empty. A mutation making the post-run snapshot non-empty was rejected.

The following recounts were byte-identical:

- ordinary Python in a clean Pod checkout of `98cce4a0f...`;
- optimized Python in the same clean Pod checkout;
- ordinary Python after copying and extracting the normalized archive on
  macOS; and
- optimized Python after the same local extraction.

The original Pod recount at `f7d2505b2...` was also byte-identical. The later
analysis hardening added only the missing post-run compute-process rejection;
it did not change any result field or statistic.

## Summary

Ratios are `new_v4 / pyoptix`; lower is better. Each CPU median is the median
of its two block ratios. `Both blocks` counts CPUs whose maximum block ratio is
at most `1.35`.

| Unit | CPU-median median | CPU-median min--max | CPU medians <=1.20 | Both blocks <=1.35 | CPU 8 blocks | CPU 8 median / rank |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Particle | 0.737869 | 0.361269--1.445494 | 45/48 | 36/48 | 1.405721, 1.394026 | 1.399874 / 47 of 48 |
| LibRTS range | 0.953280 | 0.750164--1.534651 | 43/48 | 41/48 | 0.664025, 0.945203 | 0.804614 / 6 of 48 |

The primary-thread and SMT summaries required by the fixed plan are:

| Unit / class | CPU-median median | Min--max | CPU medians <=1.20 | Both blocks <=1.35 |
| --- | ---: | ---: | ---: | ---: |
| Particle, CPUs 0--23 | 0.737334 | 0.361269--1.445494 | 22/24 | 17/24 |
| Particle, CPUs 24--47 | 0.737869 | 0.519410--1.208809 | 23/24 | 19/24 |
| LibRTS, CPUs 0--23 | 0.957774 | 0.767078--1.534651 | 22/24 | 22/24 |
| LibRTS, CPUs 24--47 | 0.945114 | 0.750164--1.510175 | 21/24 | 19/24 |

These class comparisons are not causal hardware-thread comparisons. Because
the fixed schedule ran CPUs in ascending order, CPUs 0--23 are also the first
half of the one-hour run and CPUs 24--47 are the second half. Hardware-thread
class is therefore confounded with elapsed experiment time.

## Arm-order diagnostics

The two arm orders do not show a simple global order bias. Particle's median
block ratio is `0.731777x` when V4 runs first and `0.729599x` when PyOptiX runs
first; LibRTS has corresponding medians `0.960787x` and `0.950819x`. Particle
has 27 CPUs with block 0 above block 1 and 21 in the reverse direction; LibRTS
has 22 and 26.

| Unit / block | Order | Ratio median / min--max | V4 median ns | PyOptiX median ns |
| --- | --- | ---: | ---: | ---: |
| Particle / 0 | V4, PyOptiX | 0.731777 / 0.354093--1.702533 | 392,548.5 | 568,596.0 |
| Particle / 1 | PyOptiX, V4 | 0.729599 / 0.349701--1.474298 | 377,486.0 | 518,871.5 |
| LibRTS / 0 | V4, PyOptiX | 0.960787 / 0.593816--2.131912 | 248,834.5 | 259,574.5 |
| LibRTS / 1 | PyOptiX, V4 | 0.950819 / 0.521843--2.028839 | 254,454.5 | 264,134.5 |

Particle ratios form visible clusters near roughly `0.36`, `0.73`, and `1.4`
rather than a smooth per-CPU trend. The pre-run snapshot was idle P8 at 210 MHz
and the post-run snapshot was P0 at 1,650 MHz; application clocks were not
locked. There is no per-worker clock trace, so the evidence supports observed
short-row temporal instability but does not identify unlocked clocks, CPU
identity, context transitions, or another mechanism as its cause.

## CPU 8 versus the formal transaction

| Unit | Formal CPU-8 eight-block ratio [min--max] | Post-formal CPU-8 two-block ratio [min--max] |
| --- | ---: | ---: |
| Particle | 0.772559 [0.683797--0.840260] | 1.399874 [1.394026--1.405721] |
| LibRTS range | 0.984922 [0.611580--1.243333] | 0.804614 [0.664025--0.945203] |

The populations differ in time, block count, and purpose and are not pooled.
The Particle reversal is the strongest adverse result: exact CPU affinity did
not make this sub-millisecond comparison reproducibly stable. The retained
formal statement remains only that its exact eight-block population met its
registered engineering envelope. The post-formal result requires the paper to
state that short prepared rows are not stable performance guarantees.

## Complete unfiltered rows

The full 96-row population appears without filtering in
`cpu_sensitivity/CPU_SENSITIVITY_RECOUNT_POD_NORMAL.json` under `cpu_rows`.
For each of both units and all CPUs `0..47`, it records both block orders, both
arm medians, both ratios, the two-block median and range, hardware-thread class,
and both threshold decisions. The optimized-Python copy is byte-identical.

The CPUs with at least one adverse threshold decision are:

| Unit | Median >1.20 | At least one block >1.35 |
| --- | --- | --- |
| Particle | 8, 22, 32 | 0, 3, 8, 11, 17, 19, 22, 24, 27, 28, 32, 38 |
| LibRTS range | 1, 4, 29, 45, 46 | 1, 4, 25, 29, 44, 45, 46 |

## Claim and manuscript action

The retained claim boundary is:

1. The formal transaction may be reported as the exact, controlled population
   in which all ten rows met the registered engineering envelope.
2. It may not be generalized to arbitrary CPUs, clocks, times, GPUs, or all
   applications.
3. Particle and LibRTS sub-millisecond prepared rows are explicitly not stable
   performance guarantees.
4. This sensitivity population remains post-formal, descriptive, and separate;
   no row is substituted for, pooled with, or used to retune the formal result.
5. No confidence interval, CPU-causality result, hardware-thread advantage,
   public speedup, or new formal gate is claimed.

The manuscript should retain the CPU-8 selection disclosure and add the
unfavorable sensitivity result in Internal Validity. The exact concise wording
is finalized only with the next manuscript bytes and receives zero transferred
review acceptance.

## Remaining limitations

- Only two short prepared units were tested; complete endpoints and the long
  cit-Patents row were not repeated across CPUs.
- Two blocks per CPU are enough for a fixed descriptive scan, not a confidence
  interval or stable per-CPU estimate.
- CPU order was ascending, so CPU identity, hardware-thread class, and run time
  are not independently identified.
- GPU clocks were not locked and no per-worker clock, temperature, or power
  trace was retained.
- The output oracle proves equality for these inputs, not application semantics
  in general.
- This is author-side evidence with zero independent exact-byte reviews.
