# Goal2583 Continuous Frechet Benchmark Promotion

Date: 2026-05-24
Status: superseded by demotion decision
Verdict: demoted to learner/demo app

## Purpose

This document records the attempted promotion of the existing continuous
Frechet learner app into the research benchmark tree. The promotion is now
superseded: after pod comparison against a compiled CPU reference and a
same-contract Torch CUDA baseline, the app should remain a learner/demo app.

It remains useful as a reconstruction lesson, but it is not a suitable active
benchmark app because no paper/authors-code target is available and the current
RTDL OptiX path does not beat optimized CPU C++.

## Implementation

The attempted promotion added, then removed from the active benchmark tree:

- `examples/v2_0/research_benchmarks/continuous_frechet/`
- `rtdl_continuous_frechet_benchmark_app.py`
- `README.md`

The active code path is now only the learner app at
`examples/v2_0/apps/trajectory/rtdl_continuous_frechet_distance_app.py`.

## Former Benchmark Modes

| Mode | Contract |
| --- | --- |
| `scope` | benchmark scope and boundary |
| `cpu_reference` | Python all-cells continuous Frechet decision/search |
| `cpp_reference` | learner-owned C++ all-cells decision/search |
| `rtdl_broadphase_cpu` | CPU-reference RTDL broadphase plus C++ continuation |
| `embree_broadphase` | Embree broadphase plus C++ continuation |
| `optix_broadphase` | OptiX broadphase plus C++ continuation |
| `local_comparison` | local C++ all-cells versus RTDL-broadphase orientation |

## Demotion Boundary

Do not list Continuous Frechet in `examples/v2_0/research_benchmarks/`.

Do not call it a benchmark app.

Do keep it as a learner/demo app because it demonstrates:

- RTDL can express generic segment/expanded-shape free-space-cell broadphase.
- The exact continuous Frechet decision/search remains outside the native
  engine.
- The app identifies missing generic contracts, especially compact masks,
  segment-pair distance thresholds, batched decisions, prepared segment-set
  lifetime, and partner-owned DP continuations.

## Engine Principle

No Frechet-specific native ABI is added. Native Embree/OptiX paths must remain
app-name-free. Continuous Frechet-specific logic stays in learner/demo Python
and learner-owned C++ helper code.

## Local Validation

Historical attempted-promotion check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2583_continuous_frechet_benchmark_promotion_test
```

Result:

```text
Ran 5 tests in 0.148s
OK
```

Additional compatibility check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal2583_continuous_frechet_benchmark_promotion_test tests.goal1771_continuous_frechet_python_rtdl_learner_app_test

Ran 10 tests in 0.675s
OK
```

Front-page example smoke check:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal513_public_example_smoke_test

Ran 3 tests in 3.589s
OK
```

Historical local orientation command, no longer runnable because the attempted
benchmark directory was removed:

```text
PYTHONPATH=src:. python3 examples/v2_0/research_benchmarks/continuous_frechet/rtdl_continuous_frechet_benchmark_app.py --mode local_comparison --iterations 12 --no-oracle
```

Observed on this Mac:

| Path | Distance-search seconds | Distance estimate | Notes |
| --- | ---: | ---: | --- |
| C++ all-cells | `0.003559` | `0.200196` | learner-owned C++ baseline |
| RTDL broadphase + C++ continuation | `0.031752` | `0.200196` | falls back to all cells because pruning is too weak |

The reported `rtdl_vs_cpp_speed` is `0.112x`, meaning the RTDL broadphase path
is slower on this tiny authored fixture. This is expected and reinforces the
claim boundary: the benchmark is useful for runtime reconstruction, not for
public speedup wording.

## Next Evidence Gate

No next benchmark gate. Future Continuous Frechet work should be treated as
learner/demo or primitive-design exploration only. A future benchmark promotion
would require a stronger same-contract GPU implementation or a paper/authors
target, plus a performance story that beats optimized CPU C++.
