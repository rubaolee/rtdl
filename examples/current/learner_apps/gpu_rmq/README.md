# GPU-RMQ-Style Range Minimum Query Learner App

This directory is a learner app for understanding how RTDL can express an
RMQ-shaped problem with generic primitives. It is not a promoted benchmark app
and it is not a public speedup claim.

## Contract

For an array `A` and inclusive query interval `[left, right]`, return:

- `query_id`;
- `left`;
- `right`;
- the leftmost minimum index in the interval;
- the minimum value.

Tie-breaking is fixed to the leftmost minimum so the CPU oracle, partner paths,
and RT-shaped lowering can be compared exactly.

## Why It Exists

RMQ is useful as a design-pressure app because it can be described in more than
one way:

- a normal CPU oracle over intervals;
- a hierarchy over block summaries;
- a paper-style closest-hit lowering over rays and triangles;
- a grouped candidate argmin continuation.

That makes it a good learning case for the RTDL boundary: Python owns the app
contract and scheduling policy, partners own regular array work, and RTDL owns
only generic RT primitives.

## Local Commands

Run from the repository root:

```bash
PYTHONPATH=src:. python3 examples/current/learner_apps/gpu_rmq/rtdl_gpu_rmq_learner_app.py --mode scope
PYTHONPATH=src:. python3 examples/current/learner_apps/gpu_rmq/rtdl_gpu_rmq_learner_app.py --mode compare_local --dataset random --value-count 4096 --query-count 1024 --max-width 256
PYTHONPATH=src:. python3 examples/current/learner_apps/gpu_rmq/rtdl_gpu_rmq_learner_app.py --mode paper_rt_lowering_reference --dataset repeated --value-count 4096 --query-count 1024 --max-width 256 --block-size 64
```

On Windows PowerShell:

```powershell
$env:PYTHONPATH='src;.'; py -3 examples\current\learner_apps\gpu_rmq\rtdl_gpu_rmq_learner_app.py --mode compare_local
```

## Current Modes

| Mode | Purpose |
| --- | --- |
| `scope` | Emit learner-app boundary and paper relationship. |
| `cpu_reference` | Exact leftmost-argmin CPU oracle. |
| `local_hierarchical` | Dependency-light hierarchy path using block summaries plus sparse table over block minima. |
| `compare_local` | Compare local hierarchy path against the CPU oracle. |
| `paper_rt_lowering_reference` | Lower RMQ into 3-D ray/triangle geometry and run generic closest-hit rows. |

The `paper_rt_lowering_reference` mode is the RTDL-relevant path. It encodes
array values as triangle distance, maps query intervals to rays, and decodes
closest-hit primitive ids back into RMQ argmin rows in Python. The native engine
sees only generic rays and triangles; it does not know RMQ.

## Boundary

This learner app is intentionally kept outside the benchmark set. It is useful
for learning and primitive design pressure, but current RTDL should not claim
RMQ speedup from this directory.
