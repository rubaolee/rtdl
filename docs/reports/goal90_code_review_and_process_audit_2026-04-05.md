# Goal 90 Report: Code Review And Process Audit

Date: 2026-04-05
Status: complete

## Scope

Audited slices:

- Goal 75 oracle trust envelope
- Goal 81 OptiX long exact raw-input win
- Goal 83 Embree long exact-source repair
- Goal 87 Vulkan long exact-source unblocked
- Goal 88 Vulkan long exact raw-input measurement
- Goal 89 backend comparison refresh

Audited code:

- `/Users/rl2025/rtdl_python_only/src/native/rtdl_optix.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_embree.cpp`
- `/Users/rl2025/rtdl_python_only/src/native/rtdl_vulkan.cpp`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/optix_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/embree_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`
- `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`

## Review state

- Codex: active
- Gemini milestone audit: completed
- Claude milestone audit: completed

Artifacts:

- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-gemini-review-goal90-milestone-audit.md`
- `/Users/rl2025/rtdl_python_only/history/ad_hoc_reviews/2026-04-05-claude-review-goal90-milestone-audit.md`

## Confirmed strengths

- OptiX and Embree remain the mature long exact-source performance backends.
- Vulkan is now fully measured and parity-clean on the accepted long exact-source
  prepared and repeated raw-input boundaries.
- The project has a strong correctness discipline:
  - PostGIS-backed comparison
  - trusted mini/small oracle envelopes
  - explicit timing-boundary separation

## Confirmed gaps from the audit

### 1. Vulkan runtime fast-path asymmetry

Before this audit pass, `vulkan_runtime.py` still lacked the identity-based
cache-key fast path and canonical prepacked input reuse already used by Embree
and OptiX.

This was a real asymmetry and a legitimate milestone-level defect.

### 2. `chains_to_polygon_refs` internal inconsistency

`datasets.py` exposed a legacy helper whose `vertex_offset` field advanced by
enumeration index rather than cumulative reference span.

It was lightly used, but still internally inconsistent and under-tested.

### 3. Coverage/documentation shape

The audit agrees that:

- milestone-level PIP coverage is much stronger than the remaining workloads
- architecture and API explanation is still too fragmented across goal reports

## Fixes already applied during Goal 90

### Vulkan fast-path alignment

Updated:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/vulkan_runtime.py`

Changes:

- added identity-token cache-key behavior
- made the prepared-cache miss path bind raw canonical inputs directly
- added reuse of `_rtdl_packed_points` and `_rtdl_packed_polygons`

### New Vulkan fast-path tests

Updated:

- `/Users/rl2025/rtdl_python_only/tests/goal80_runtime_identity_fastpath_test.py`

New coverage:

- Vulkan canonical tuple repeated-call fast path
- Vulkan reuse of primed packed CDB-derived inputs

### Legacy face-reference helper repair

Updated:

- `/Users/rl2025/rtdl_python_only/src/rtdsl/datasets.py`
- `/Users/rl2025/rtdl_python_only/tests/rtdsl_py_test.py`

Changes:

- `chains_to_polygon_refs` is now documented as a legacy face-reference summary
- `vertex_offset` is now cumulative and internally coherent
- tests now assert actual offset/count relations instead of length only

## Validation completed so far

Passed:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test
```

Result:

- `10` tests
- `OK`

Passed targeted parser/view slice:

```bash
cd /Users/rl2025/rtdl_python_only
PYTHONPATH=src:. python3 -m unittest \
  tests.rtdsl_py_test.RtDslPythonTest.test_rayjoin_cdb_parser_and_views \
  tests.goal80_runtime_identity_fastpath_test \
  tests.goal89_backend_comparison_refresh_test \
  tests.goal76_runtime_prepared_cache_test
```

Result:

- `11` tests
- `OK`

Known local limitation:

- the broader `tests.rtdsl_py_test` suite still hits the existing Mac
  `geos_c` link issue when it tries to rebuild the native oracle library
  locally; that is an environment issue, not a new regression from this audit
  work

## How Goal 90 feeds Goal 91 and Goal 92

Goal 91:

- continue adding milestone-level regression tests instead of report-helper-only
  tests
- extend backend parity/performance regression coverage where the audit found
  asymmetries

Goal 92:

- centralize architecture/API/performance explanation
- reduce fragmentation across many goal reports

## Outcome

Goal 90 completed as an audit-and-correction round.

It produced:

- two external milestone audits
- two real code fixes
- stronger milestone regression coverage
- a clearer backlog for Goal 91 test expansion and Goal 92 documentation work

The package-level follow-on work remains in Goals 91 and 92, but the audit
itself is complete and already corrected the defects it found.
