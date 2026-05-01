# Goal797 Local-First Cloud-Cost Policy

Date: 2026-04-23

## Verdict

Status: `active policy`.

The project should maximize local development, local tests, local docs, and local review before renting or restarting cloud GPUs. Cloud should be used only for batched NVIDIA-specific evidence after the local batch is ready.

## Policy

1. Do all possible source changes locally first.
2. Run portable correctness tests locally before any paid cloud use.
3. Update docs and machine-readable support/readiness matrices locally before cloud.
4. Prepare one replayable cloud batch that covers all pending NVIDIA-specific evidence.
5. Do not start a pod for one isolated check unless it blocks all other work.
6. Treat cloud data as disposable; pull artifacts back and commit reports immediately.

## Current Local Work Queue

| Area | Local action before cloud | Why |
|---|---|---|
| DB analytics | Improve phase visibility around prepared session timing and keep it `needs_interface_tuning`. | Current OptiX DB path is real but not claim-ready because interface/materialization costs are grouped. |
| Graph analytics | Either implement native GPU/OptiX path or keep excluded from RTX claims. | Current OptiX-facing graph path is host-indexed fallback. |
| Segment/polygon | Promote only native compact OptiX any-hit/hit-count paths after local correctness and profiler gates. | Current public app classification is host-indexed fallback. |
| Hausdorff / ANN / Barnes-Hut | Keep CUDA-through-OptiX classification unless redesigned around real RT traversal. | Current public paths are useful GPU compute, not RT-core traversal claims. |
| Cloud runner | Keep Goal769/Goal761 batch scripts ready and replayable. | Prevents ad hoc paid GPU use. |

## Immediate Next Goal

Goal798 should improve local DB analytics phase accounting so the next cloud batch can measure what actually matters instead of only one-shot versus warm-session totals.
