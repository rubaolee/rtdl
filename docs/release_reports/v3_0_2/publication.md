# RTDL v3.0.2 Publication Note

Status: published source-tree release note for tag `v3.0.2`.

Version marker target: `v3.0.2`

## Publication Status

v3.0.2 is released as the current source-tree patch packet for the V3.0 line.
The V3 current-scope completion gate remains the benchmark-app/current-route
system, current docs point at V3.0.2, the release packet records allowed and
blocked wording, and maintainer authorization was given on 2026-06-18.

## Publication Shape

The v3.0.2 statement is patch-version but still claim-bounded:

```text
RTDL v3.0.2 preserves the V3.0 ten-app benchmark route matrix and publishes the
cleaned primitive-first, partner-explicit source-tree RTDL programming surface.
It is a patch release for boundary cleanup, not an embedding, SDK, broad
speedup, package-install, stable SDK, or automatic optimizer claim.
```

## Required Before Publication

- [x] Version marker moved to `v3.0.2`.
- [x] Editable metadata moved to `3.0.2`.
- [x] V3 current-scope completion gate exists and passes.
- [x] `v3_current` test matrix is registered and passes.
- [x] Source-tree doctor checks the V3 release package and keeps embedding/C
  ABI surfaces out of the V3 release critical path.
- [x] Front page, docs index, examples index, tutorials, versioning, support
  matrix, capability boundaries, partner boundaries, and claim-boundary pages
  identify v3.0.2 as current.
- [x] V3 app-author implementation strategy is linked from learner-facing docs.
- [x] Release statement, support matrix, public wording boundaries, publication
  note, tag preparation, final closeout, and major-release requirements trace
  are present.
- [x] Scope correction applied: embedding, C ABI, SDK, generated bindings,
  device-buffer execution, external stream ordering, zero-copy framework
  interop, and device-callable fusion are V4.0 scope.
- [x] Default `make help`, default source-tree doctor output, and rendered
  learner evidence pages keep V4 prep out of the normal user path.
- [x] Maintainer explicitly authorized v3.0.2 publication after pod validation.

## Current Fresh Verification

Local Windows, after V3.0.2 publication edits:

```text
PYTHONPATH=src;. py -3 scripts\rtdl_source_tree_doctor.py --json
result: ok=true, version=v3.0.2, required_failures=[]

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v3_current
result: ok=true, module_count=39, Ran 147 tests, OK

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v3_release
result: ok=true, module_count=2, Ran 12 tests, OK

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v4_prep
result: ok=true, module_count=65, Ran 206 tests, OK
```

The `v4_prep` result is a regression guard for archived preparatory embedding,
C ABI, SDK, and zero-copy material. It is not part of the V3.0 public release
surface or completion claim.

Current-doc polish scans after publication edits:

```text
current-v2 wording scan over current docs: no hits
V3 doctor packet stale C ABI wording scan: no hits
V3.0 embedding-scope drift scan: no hits
```

Optional CUDA/OptiX pod replay commands are listed in
[Final Closeout](final_closeout.md). This publication note does not claim a
fresh pod replay from the publication edit session.

## Public Wording That Must Stay Blocked

- Broad RT-core or whole-application speedups.
- Paper reproduction or RTDL-beats-specialized-code wording.
- Automatic partner selection.
- Arbitrary CuPy, Numba, CUDA, PyTorch, or JAX acceleration.
- Package-install, PyPI, wheel, or stable SDK wording.
- Generated binding package wording.
- Device-buffer C ABI query execution.
- External CUDA stream ordering.
- Public true-zero-copy or complete device residency.
- Arbitrary raw OptiX callback exposure as the stable API.
- App-specific native-engine extension claims.
