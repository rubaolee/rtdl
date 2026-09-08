# Long-workload successor preregistration

Date: 2026-09-08, America/New_York. This document describes the frozen
machine-readable preregistration for the CPU-affinity-controlled successor
transaction. It is not a result or a performance claim.

## Frozen identity

- Candidate source commit:
  `02e84374fc092d2bb916cca633eda9592b4ecf07`.
- Candidate source tree:
  `8aad15d686bbc9e1c3b11df998898a0a063a01f1`.
- Formal config SHA-256:
  `491d399343fee27fbf97f6a72837ff38b4b7d04fa5324525cf3b3780caf72e1d`.
- Passing dry-run summary SHA-256:
  `ce980f2863dcf6898af835514b3bd32166b7e8673c78fc3f7a20c64df4ad34d2`.
- Frozen preregistration SHA-256:
  `6099e46ef0b0ffa1048f7ea375c9a3b2df247ec9c7b6164936bf24edd7074d7a`.
- Frozen formal schedule SHA-256:
  `4edf6fbf341a6a911714768c45ed39d2c5b5a706d1177c3b65b109377587f2f3`.
- Controller SHA-256:
  `0a5fb0098b5192cb399bb9a54441144ad71d795c7675c20c212f049907ad01a7`.
- Worker SHA-256:
  `0009137c032dc13f03065898283c95ed087153eb11a36a69723fea32a4b7ed50`.
- Native DSO SHA-256:
  `5edb9ec3e542b64bf0696c6df9a164448aecd6b5b51f1fdd78ba6e8c791dd2af`.
- Triangle `.rtdlexe` SHA-256:
  `f8554f9e339f526424b09a619071c9e7bd64318f1e78b1c9dcadf129dcc17463`.

The machine-readable preregistration status is
`FROZEN_BEFORE_FORMAL_WORKER_ZERO`.

## Registered machine and scheduling

- GPU: NVIDIA RTX A4500, UUID
  `GPU-5dbda20d-af85-650e-7250-10b265a77143`, compute capability 8.6.
- Driver: 550.127.05; `CUDA_VISIBLE_DEVICES=0`.
- Every formal worker must set and observe the exact CPU affinity `{8}` before
  implementation imports and must observe the same set after execution.
- Affinity mismatch, absence of the Linux affinity API, or postflight drift is
  a fail-closed worker failure and is independently recounted.
- The container exposes 48 logical CPUs but has a cgroup quota of approximately
  10.2 CPUs. Exact affinity controls host scheduling variance; it does not
  change the GPU workload, timer, result contract, or engineering thresholds.
- A GPU application-clock lock was attempted during diagnosis and rejected by
  container permissions. No locked-clock claim is made.

## Frozen matrix

The transaction has five units, two endpoints, three arms, eight paired blocks,
and 240 fresh-process workers. The arms are immutable old RTDL, successor RTDL,
and competent public PyOptiX. The endpoints are complete and prepared.

| Unit | Prepared repetitions | Registered output |
| --- | ---: | --- |
| Particle tracking | 32 | ordered `5000 x 3` U32 rows |
| Graph RT-2A1, com-dblp/1M | 4 | checked U64 triangle count 2,224,385 |
| LibRTS Parks point contains | 4 | exact count 112,729 |
| LibRTS Parks range contains | 4 | exact count 105,826 |
| Graph RT-2A1, cit-Patents/4M | 3 | checked U64 triangle count 7,515,023 |

The eight precommitted arm orders contain four blocks in which successor RTDL
precedes PyOptiX and four in which PyOptiX precedes successor RTDL. Each block
is a fresh process. Retry and discard are forbidden. All adverse rows, failures,
timeouts, and output mismatches must be retained.

## Gates and claim boundary

For every unit and endpoint, the primary paired ratio is successor RTDL divided
by public PyOptiX. The engineering target is median paired ratio `<= 1.20` and
every block ratio `<= 1.35`. These thresholds are not a filter: a miss remains
part of the transaction and cannot be repaired by selecting or rerunning only
failed blocks.

The transaction can support only four repaired old-input units and one
preselected cit-Patents/4M long graph unit. It is not evidence for broad DSL
overhead, all benchmark applications, intrinsic language speed, or user
productivity. Public/manuscript wording remains unauthorized until the full
transaction, independent recount, evidence preservation, and review gates are
complete.

## Pre-formal validation and retained failures

The final dry run completed 15/15 workers with exact outputs, zero retry,
zero discard, and exact `{8}` affinity before and after every worker. It used
one prepared action per arm/unit and no formal sample.

Two earlier pre-formal events are retained rather than rewritten:

- A config serialized with sorted JSON keys changed the registered arm order;
  controller validation rejected it before worker zero.
- The first freeze invocation omitted `PYTHONPATH=src:.`; Python rejected the
  `scripts` import before writing a preregistration. The corrected standard
  repository invocation then created the frozen file above.

The earlier unlocked transaction at commit `0c3420f42` is a separate complete
adverse transaction. It passed 8/10 unit-endpoint rows but failed Particle
prepared at a `1.462108x` worst block and LibRTS range prepared at a `1.563658x`
worst block. Its samples cannot be pooled with this successor transaction.
