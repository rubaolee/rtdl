# Goal2992 - v2.6 Numba Neutral Handoff Local Linux Smoke

Date: 2026-06-01

## Purpose

Goal2992 records a local Linux smoke run for the v2.6 neutral partner handoff
created in Goal2990 and the Numba demonstrator runner prepared in Goal2991.
The run is useful because it proves that the new Numba path can execute real
CUDA partner continuations without using the legacy torch carrier. It is not release evidence and not performance evidence.

## Environment

- Host: `192.168.1.20`
- Disposable checkout: `/tmp/rtdl_goal2991_dbb06449`
- Source commit: `dbb06449c474a7df48914258b927a4cef550cc45`
- GPU: `NVIDIA GeForce GTX 1070`, compute capability 6.1
- Python: 3.12.3
- Local dependency target: `.pydeps_v26_numba`
- Artifact:
  `docs/reports/goal2992_v2_6_numba_neutral_handoff_local_linux_smoke_2026-06-01.json`

The checkout was intentionally disposable because the persistent local Linux
checkout had unrelated in-progress edits.

## Result

The smoke run passed on `65,536` rows and `1,024` groups:

- Neutral handoff validation: `accept`
- Selected partner: `numba`
- Runtime-observed descriptor count: `2`
- All columns device resident: `true`
- All leases completed: `true`
- Torch conversion used: `false`
- Torch carrier used: `false`
- Segmented count CPU parity: `true`
- Segmented sum CPU parity: `true`
- Maximum sum absolute error: `1.7053025658242404e-13`

The measured partner-continuation timings were about `0.042s` for count and
`0.044s` for sum on this local smoke host. Those timings are diagnostic only:
the GTX 1070 is a project smoke host, not an accepted v2.6 performance platform.

## Boundary

This report does not change the Goal2991 pod-runner status. Goal2991 remains
prepared for an accepted CUDA pod run with larger scale. This Goal2992 smoke
does not authorize release, public speedup wording, Numba speedup wording,
whole-app speedup wording, broad RT-core wording, true-zero-copy wording,
automatic partner selection, automatic Triton selection, or app-specific native
engine behavior.

## Next

The next evidence step is still a CUDA pod run:

```bash
PYTHONPATH=src:. python3 scripts/goal2991_v2_6_numba_neutral_handoff_pod_runner.py --rows 1000000 --groups 4096
```

That pod run should keep the same claim boundary and should be treated as a
runtime correctness/conformance checkpoint before any performance claim is
considered.
