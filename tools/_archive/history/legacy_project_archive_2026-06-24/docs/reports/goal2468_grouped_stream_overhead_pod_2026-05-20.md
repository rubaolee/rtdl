# Goal2468 - RT-DBSCAN grouped-stream overhead pod evidence

Date: 2026-05-20

Status: pod timing evidence for host-overhead attribution only. This report
does not authorize a paper, broad RT-core, or whole-app speedup claim.

## Pod

Connection provided by user:

```text
ssh root@213.173.108.173 -p 26219 -i ~/.ssh/id_ed25519
```

Mac Codex used the locally available RTDL key:

```text
ssh root@213.173.108.173 -p 26219 -i ~/.ssh/id_ed25519_rtdl_codex
```

Environment:

```text
GPU: NVIDIA RTX PRO 4500 Blackwell
Driver: 580.126.20
CUDA: /usr/local/cuda-12.8, nvcc 12.8
OptiX SDK headers: /root/vendor/optix-dev-9.0.0
Source base: a9193856547bf692069955a3dbaf6c3e00c09b1b plus local Goal2467/2468 overlay
```

Bootstrap:

```text
apt-get install -y git make build-essential pkg-config libgeos-dev python3-pip python3-venv
python3 -m pip install --break-system-packages cupy-cuda12x numpy
make build-optix OPTIX_PREFIX=/root/vendor/optix-dev-9.0.0 \
  CUDA_PREFIX=/usr/local/cuda-12.8 \
  NVCC=/usr/local/cuda-12.8/bin/nvcc
```

Focused verification:

```text
tests.goal2468_rt_dbscan_overhead_breakdown_instrumentation_test
tests.goal2467_blocked_grouped_continuation_design_test
tests.goal2465_grouped_union_all_items_intersection_cull_test
tests.goal2463_grouped_union_all_items_path_test
tests.goal2461_grouped_stream_self_query_device_path_test

Ran 22 tests in 0.233s - OK
```

Tiny OptiX smoke produced:

```text
schema = rt_dbscan_grouped_stream_host_overhead_breakdown_v1
```

## Command

```text
python3 scripts/goal2467_grouped_stream_baseline_pod_runner.py \
  --output-dir docs/reports/goal2468_grouped_stream_overhead_pod \
  --point-count 32768 \
  --point-count 65536 \
  --repeat-count 5
```

Artifacts copied back:

- `docs/reports/goal2468_grouped_stream_overhead_pod/summary.json`
- `docs/reports/goal2468_grouped_stream_overhead_pod/clustered3d_32768_grouped_stream.json`
- `docs/reports/goal2468_grouped_stream_overhead_pod/clustered3d_65536_grouped_stream.json`

## Results

Five repeats per point count; tail medians exclude repeat 1.

| clustered3d points | full runner tail median | native grouped RT median | rows materialization | densify labels | signature | adapter non-native estimate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 32,768 | 0.052438 sec | 0.021820 sec | 0.014084 sec | 0.011278 sec | 0.005154 sec | 0.000273 sec |
| 65,536 | 0.125688 sec | 0.058946 sec | 0.030645 sec | 0.025340 sec | 0.010421 sec | 0.000303 sec |

Both rows reported `signatures_match = true`; the tiny smoke reported
`tiny_smoke_matches_reference = true`.

## Interpretation

The remaining gap is no longer hidden in the native grouped RT primitive. It is
almost entirely host-visible row handling in the benchmark runner:

- 32,768 points: native grouped RT is about 21.8 ms; row materialization plus
  densification plus signature is about 30.5 ms.
- 65,536 points: native grouped RT is about 58.9 ms; row materialization plus
  densification plus signature is about 66.4 ms.

The estimated non-native work inside the prepared adapter is below 0.4 ms in
both tail rows. The next benchmark-app optimization should therefore avoid
Python dictionary row materialization and host-side label densification when
the caller only needs component labels, a signature, or a scalar summary.

## Next Work

Recommended next step before closing the benchmark app:

1. Add a column/raw-label result mode for the grouped-stream benchmark path so
   the app can report device/partner columns without converting every point to
   Python dictionaries.
2. Add a benchmark-only signature path that summarizes device/partner label
   columns directly, or at least from dense arrays instead of row dictionaries.
3. Preserve the existing row-returning mode as the compatibility/correctness
   path.

The native blocked/segmented grouped continuation remains a separate deeper
optimization. This evidence says the immediate benchmark-app bottleneck is
row/label materialization, not more RT traversal work.

## Boundary

- No native ABI was added by Goal2468.
- No historical artifacts were rewritten.
- No paper reproduction or authors-implementation comparison is claimed.
- No broad RT-core speedup or whole-app speedup claim is authorized.
