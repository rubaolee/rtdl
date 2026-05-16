# RTDL v2 User-Level Hausdorff CUDA Benchmark Lab

Date: 2026-05-15

Status: local Linux validation complete; high-end RTX pod validation still optional for larger-scale timing.

## Purpose

This lab tests whether a learner can write a high-performance exact Hausdorff
distance program using RTDL v2.0 as a Python+partner runtime without changing
RTDL itself.

The app computes the undirected 2D Hausdorff distance between two point sets:

```text
H(A, B) = max(max_a min_b distance(a, b), max_b min_a distance(b, a))
```

The benchmark intentionally separates three roles:

1. **RTDL v2 user app path**: RTDL converts Python point rows into partner-owned
   CuPy columns, then learner-owned CUDA continuation performs a tiled exact
   nearest-distance reduction.
2. **Multithreaded CPU baseline**: an independent OpenMP C++ implementation
   compiled at runtime and called through `ctypes`.
3. **Correct CUDA baseline**: an independent `nvcc` CUDA C++ implementation,
   also compiled at runtime and called through `ctypes`.

The script is:

```text
examples/rtdl_hausdorff_v2_user_benchmark.py
```

No RTDL runtime, native engine, ABI, or partner primitive implementation was
changed.

## Claim Boundary

This is a user-level v2.0 composition test, not a new RTDL primitive.

- It shows that a user can combine RTDL partner columns with custom CUDA/CuPy
  continuation code.
- It does not claim that RTDL's native engine owns exact Hausdorff acceleration.
- It does not claim exact Hausdorff is RT-core accelerated.
- It does not change the app-agnostic native-engine rule.

For exact point-cloud Hausdorff, the core operation is a dense nearest-distance
reduction. That maps naturally to CUDA tiling and partner reductions. RT cores
are more relevant for RTDL's threshold/candidate spatial query subproblems than
for this dense exact all-pairs point-distance reduction.

## Local Linux Environment

Validation host:

```text
192.168.1.20
```

Clean validation checkout:

```text
/home/lestat/work/rtdl_hausdorff_v2_lab
```

The host has:

- `g++`
- `nvcc`
- one CUDA-capable GPU
- user-site `cupy-cuda12x` installed for this lab

This GTX 1070 host is useful for development and correctness/perf shape, but it
is not final release-grade RTX/RT-core performance evidence.

## Results

### 8192 x 8192

Artifact:

```text
docs/reports/hausdorff_v2_user_benchmark_local_full_8192.json
```

| Method | Seconds | Distance | Matches OpenMP oracle |
| --- | ---: | ---: | --- |
| OpenMP CPU | 0.067117 | 0.120036182867 | oracle |
| independent nvcc CUDA C++ | 0.010118 | 0.120036182867 | yes |
| independent CuPy RawKernel | 0.009501 | 0.120036182867 | yes |
| RTDL v2 partner columns + user CUDA | 0.009537 | 0.120036182867 | yes |
| built-in v2 CuPy partner exact | 0.061649 | 0.120036182867 | yes |

Observed speedup:

```text
RTDL v2 partner columns + user CUDA vs OpenMP CPU: 7.04x
```

### 32768 x 32768

Artifact:

```text
docs/reports/hausdorff_v2_user_benchmark_local_full_32768.json
```

| Method | Seconds | Distance | Matches OpenMP oracle |
| --- | ---: | ---: | --- |
| OpenMP CPU | 1.043477 | 0.116077291553 | oracle |
| independent nvcc CUDA C++ | 0.176199 | 0.116077291553 | yes |
| independent CuPy RawKernel | 0.175775 | 0.116077291553 | yes |
| RTDL v2 partner columns + user CUDA | 0.166367 | 0.116077291553 | yes |

Observed speedup:

```text
RTDL v2 partner columns + user CUDA vs OpenMP CPU: 6.27x
```

The built-in v2 CuPy exact path was intentionally skipped at this larger scale
because it materializes the dense distance matrix. It is a correctness-oriented
partner primitive, not the high-performance tiled user continuation.

### 65536 x 65536

Artifact:

```text
docs/reports/hausdorff_v2_user_benchmark_local_full_65536.json
```

| Method | Seconds | Distance | Matches OpenMP oracle |
| --- | ---: | ---: | --- |
| OpenMP CPU | 4.184653 | 0.130850404529 | oracle |
| independent nvcc CUDA C++ | 0.628295 | 0.130850404529 | yes |
| independent CuPy RawKernel | 0.627447 | 0.130850404529 | yes |
| RTDL v2 partner columns + user CUDA | 0.627756 | 0.130850404529 | yes |

Observed speedup:

```text
RTDL v2 partner columns + user CUDA vs OpenMP CPU: 6.67x
```

## Design Lesson

This lab confirms a useful v2.0 boundary:

```text
RTDL owns generic partner-column handoff.
Users may own app-specific high-performance continuation code.
```

For this app, the high-performance continuation is a tiled CUDA reduction:

1. one thread owns one source point;
2. target points are loaded in shared-memory tiles;
3. each thread keeps its nearest target distance;
4. each block reduces to the largest per-source nearest distance;
5. the host reduces block winners into the directed Hausdorff witness;
6. the app repeats this for A->B and B->A, then takes the larger result.

This is a strong example of why v2.0 should allow partner-normal code such as
CuPy RawKernel. RTDL does not need to absorb every app-specific reduction into
the native engine to be useful.

## Next Pod Step

A pod is useful for:

- larger GPU timing on a modern RTX card;
- measuring whether high memory bandwidth and newer SMs change the speedup;
- optionally running the existing RTDL OptiX threshold-decision Hausdorff mode
  to show the separate RT-core decision subproblem.

A pod is not needed to prove basic correctness: OpenMP, independent CUDA C++,
independent CuPy RawKernel, and RTDL v2 partner-column user CUDA all agree on
the local Linux validation host.
