# Goal1771 Continuous Frechet Python+RTDL Learner App

Date: 2026-05-12
Status: local implementation evidence
Verdict: accept-with-boundary

## Purpose

This goal records a v1.8 learner test: treat Python+RTDL as a usable programming
language surface and author a new ray-tracing-shaped application, continuous
Frechet distance over two polylines, without adding app-specific native engine
customization.

The delivered example is:

- `examples/rtdl_continuous_frechet_distance_app.py`

## Program Shape

The example computes a continuous Frechet distance estimate by binary-searching
a free-space reachability decision in Python. RTDL is used for a generic
segment-vs-expanded-shape broadphase:

- curve P segments are probe geometry,
- curve Q segments are expanded into radius-dependent boxes,
- RTDL emits candidate free-space cells through segment/shape any-hit rows,
- Python performs the exact free-space reachability decision over those cells.

This follows the v1.8 app-agnostic boundary: the native side sees generic
segment/shape traversal and row emission, not a custom Frechet engine.

## NVIDIA RT-Core Path

The claim-sensitive command shape is:

```bash
PYTHONPATH=src:. python examples/rtdl_continuous_frechet_distance_app.py --backend optix --candidate-mode rtdl_broadphase --require-rt-core
```

`--require-rt-core` deliberately requires the explicit native OptiX bounded
segment/shape pair-row path. It is not enabled by merely passing
`--backend optix`.

## Boundary

This is not a universal continuous-Frechet speedup claim. The bounded RTDL/OptiX
claim is only the free-space-cell broadphase. Python still owns:

- continuous Frechet free-space interval propagation,
- binary-search distance estimation,
- final threshold decision assembly,
- JSON application output and explanation.

This is the intended learner result: a developer can write a new app in
Python+RTDL and route RT-shaped work through an RTDL backend, while the engine
remains app-agnostic.

## Validation

Focused validation:

```text
PYTHONPATH=src;. py -3 -m unittest tests.goal1771_continuous_frechet_python_rtdl_learner_app_test
```

Result: 4 tests passed.

The public example smoke test was also updated so the app remains visible in
the release-facing example surface.

Follow-up hardware validation is recorded in
`docs/reports/goal1772_continuous_frechet_optix_pod_validation_attempt_2026-05-12.md`.
That run reached an RTX A5000 pod, installed compatible NVIDIA `optix-dev`
`v9.0.0` headers, built `librtdl_optix.so`, and executed the
`--backend optix --candidate-mode rtdl_broadphase --require-rt-core` path with
`rt_core_accelerated: true` and `matches_oracle: true`.
