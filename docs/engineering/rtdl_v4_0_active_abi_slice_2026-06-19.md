# RTDL V4.0 Active ABI Slice

Status: active V4 engineering note.
Date: 2026-06-19.

This note records the first implementation slice after the V4 design review
packet accepted D1-D5.

## What Exists

- Active source root: `src/v4/`.
- Active experimental header: `src/v4/include/rtdl/rtdl.h`.
- Active proof implementation: `src/v4/rtdl_v4_c_api.cpp`.
- Hidden engineering targets: `make help-v4-dev`, `make build-v4-c-api`,
  `make test-v4-active`.
- Optional doctor check: `scripts/rtdl_source_tree_doctor.py --include-v4-active`.
- Test matrix group: `scripts/run_test_matrix.py --group v4_active`.
- Runtime smoke: `src/v4/examples/python_ctypes_aabb2_smoke.py`.

## Contract Shape

This slice starts ABI `0.2.0` and implements the decisions accepted from the
2026-06-19 review:

- D1: RTDL-owned result handles and caller-provided output buffers.
- D2: `struct_size` as the descriptor extensibility mechanism.
- D3: enum-keyed `rtdl_query_capability`.
- D4: fail-closed descriptor validation before pointer use.
- D5: pre-1.0 experimental SDK wording only.

The first route is host F32 AABB2 overlap with host U64 `(query_id,
primitive_id)` pair rows. That route is deliberately small, but it already
exercises query-plan handles, result handles, caller-provided output,
required-count reporting, and truncation status.

On a Linux host with a C++17 compiler:

```bash
make build-v4-c-api
python3 src/v4/examples/python_ctypes_aabb2_smoke.py
```

## What It Does Not Claim

This slice is not a stable SDK, not a package-install promise, not a true
zero-copy claim, and not a broad backend claim. CUDA, DLPack, external streams,
Embree, OptiX, generated bindings, and package staging remain behind later V4
milestones and capability gates.

## Next Engineering Work

1. Add runtime smoke coverage for the active V4 library on a compiler-capable
   host.
2. Add layout and old-size descriptor compatibility tests.
3. Decide the first native backend priority: Embree-first or OptiX-first.
4. Select the second ABI-shaping route, likely fixed-radius neighbors or
   ray/triangle any-hit.
