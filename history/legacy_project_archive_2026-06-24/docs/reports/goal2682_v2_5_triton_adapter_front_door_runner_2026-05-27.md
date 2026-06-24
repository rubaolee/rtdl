# Goal2682: v2.5 Triton Adapter Front-Door Pod Runner

Status: local runner/test slice; CUDA pod execution still required.

Date: 2026-05-27

## Purpose

Goal2681 added `partner="triton"` to generic public partner-adapter entry
points. The existing Goal2665 runner validates low-level Triton continuation
kernels, but it does not exercise the public adapter front door. Goal2682 adds
a dedicated pod runner for that API layer.

## Runner

Script:

```bash
PYTHONPATH=src:. python3 scripts/goal2682_v2_5_triton_adapter_front_door_pod_runner.py \
  --row-counts 1024,65536,1048576 \
  --group-count 4096 \
  --repeats 5 \
  --output docs/reports/artifacts/goal2682_v2_5_triton_adapter_front_door_pod.json
```

The runner validates the public `partner_adapters` front door:

- `partner_group_count_by_key(..., partner="triton")`;
- `partner_group_sum_by_key(..., partner="triton")`;
- `partner_group_min_by_key(..., partner="triton")`;
- `partner_group_max_by_key(..., partner="triton")`;
- `partner_mask_indices(..., partner="triton")`;
- `partner_columnar_predicate_reduce(..., partner="triton")`.

It compares these against Torch CUDA tensor baselines. Torch is used only as
the tensor carrier and correctness baseline; it is not the v2.5 partner.

## Validation

Local dry run:

```bash
PYTHONPATH=src:. python3 scripts/goal2682_v2_5_triton_adapter_front_door_pod_runner.py \
  --dry-run --row-counts 8,16 --group-count 4 --repeats 1
```

Unit test:

```bash
PYTHONPATH=src:. python3 -m unittest -v \
  tests.goal2682_v2_5_triton_adapter_front_door_runner_test
```

Expected locally on this Mac:

```text
Ran 2 tests
OK
```

## Claim Boundary

The runner can produce CUDA correctness/timing evidence for the public adapter
front door, but it does not by itself complete v2.5 or authorize public
performance claims. Benchmark-app claims still require app-specific integration
evidence that keeps RT traversal separate from generic partner continuation.
