# RTDL V4.0 Active ABI Slice

Status: active V4 engineering note.
Date: 2026-06-19.

This note records the first implementation slice after the V4 design review
packet accepted D1-D5. After the reframing note
`docs/reviews/v4_reframing_note_rt_core_operator_for_python_gpu_ecosystem_2026-06-19.md`,
this slice is classified as Phase 2 substrate work. It is useful and should be
kept, but it is not the Phase 1 V4.0 product proof.

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
- D5: pre-1.0 experimental substrate wording only.

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
milestones and capability gates. Non-Python hosts and public multi-language SDK
packaging are V4.x under the current Python-only V4.0 scope decision. This
slice also is not the V4.0 product headline: the product headline is the
Python GPU ecosystem calling RTDL as an RT-core operator on host-owned device
arrays.

## Next Engineering Work

1. Keep the M1 scope decision visible: V4.0 is Python actors only; non-Python
   hosts and public SDK packaging are V4.x.
2. Select the first benchmark-valuable Python device-array route, likely
   fixed-radius neighbors or ray/triangle any-hit.
3. Prototype CuPy/Numba/PyTorch device-array intake and caller-stream metadata.
4. Add layout and old-size descriptor compatibility tests for the substrate.
5. Connect the substrate to the first device-buffer route once the product
   route is selected.
