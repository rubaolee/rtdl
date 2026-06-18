# RTDL v3.0 Publication Note

Status: published source-tree release note for tag `v3.0`.

Version marker target: `v3.0`

## Publication Status

v3.0 is released as a source-tree major-version packet. The V3 current-scope
completion gate passed for the benchmark-app/current-route system, the current
docs are polished to point at V3.0, the release packet records allowed and
blocked wording, and maintainer authorization was given on 2026-06-18.

## Publication Shape

The v3.0 statement is major-version but still claim-bounded:

```text
RTDL v3.0 closes the current ten-app benchmark route matrix and publishes the
primitive-first, partner-explicit source-tree RTDL programming surface. It is a
major release for route closure and app-author guidance, not an embedding,
SDK, broad speedup, package-install, stable SDK, or automatic optimizer claim.
```

## Required Before Publication

- [x] Version marker moved to `v3.0`.
- [x] Editable metadata moved to `3.0.0`.
- [x] V3 current-scope completion gate exists and passes.
- [x] `v3_current` test matrix is registered and passes.
- [x] Source-tree doctor checks the V3 release package and keeps embedding/C
  ABI surfaces out of the V3 release critical path.
- [x] Front page, docs index, examples index, tutorials, versioning, support
  matrix, capability boundaries, partner boundaries, and claim-boundary pages
  identify V3.0 as current.
- [x] V3 app-author implementation strategy is linked from learner-facing docs.
- [x] Release statement, support matrix, public wording boundaries, publication
  note, tag preparation, final closeout, and major-release requirements trace
  are present.
- [x] Scope correction applied: embedding, C ABI, SDK, generated bindings,
  device-buffer execution, external stream ordering, zero-copy framework
  interop, and device-callable fusion are V4.0 scope.
- [x] Maintainer explicitly authorized publication.

## Current Fresh Verification

Local Windows, after V3.0 publication edits:

```text
PYTHONPATH=src;. py -3 scripts\rtdl_source_tree_doctor.py --json
result: ok=true, version=v3.0, required_failures=[]

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v3_current
result: ok=true, module_count=104, Ran 353 tests, OK

PYTHONPATH=src;. py -3 scripts\run_test_matrix.py --group v3_release
result: ok=true, module_count=1, Ran 5 tests, OK
```

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
