# Call For Review: Goal5148 Native 3D Cell-MBR Frontier

Please strictly review Goal5148.

## Files Under Review

- `history/internal_docs/goal5148_native_3d_cell_mbr_frontier_result_2026-07-08.md`
- `src/native/optix/rtdl_optix_prelude.h`
- `src/native/optix/rtdl_optix_core.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_api.cpp`
- `src/rtdsl/optix_runtime.py`
- `src/rtdsl/partner_continuations.py`
- `src/rtdsl/__init__.py`
- `tests/goal5148_native_3d_cell_mbr_frontier_test.py`
- `Paper-reproduction-apps/x-hd-paper/scripts/run_native_3d_cell_mbr_frontier_gate.py`
- `Paper-reproduction-apps/x-hd-paper/results/native_3d_cell_mbr_frontier_gate_pod_optix.json`
- `Paper-reproduction-apps/x-hd-paper/data/manifest.json`
- `history/internal_docs/xhd_review_opinions_register_2026-07-07.md`

## Review Questions

1. Does Goal5148 genuinely move exact point-to-cell-MBR radius filtering and
   nearest-state frontier kind classification into native OptiX traversal for
   3-D, rather than merely wrapping the Goal5147 broadphase-plus-NumPy route?
2. Is the new native symbol app-neutral?
   `rtdl_optix_collect_cell_mbr_nearest_frontier_3d` must not encode X-HD,
   Hausdorff, author, dataset, or paper-specific behavior.
3. Does the emitted row table conform to the existing Goal5140 schema and kind
   codes?
4. Is overflow handled fail-closed, with no usable partial row table on
   overflow?
5. Does the POD evidence prove correctness against the Goal5145
   dimension-generic 3-D oracle on the bounded fixture?
6. Is the Python wrapper a proper RTDL system API surface, not a raw app-local
   ctypes shortcut?
7. Are the claim boundaries correct: bounded native 3-D backend step only, not
   full 2-D/3-D native ABI completion, not X-HD performance, not full paper
   reproduction?
8. Does the implementation avoid app identity leakage in the generic source
   windows?
9. Is it acceptable that this is a 3-D-specific bounded symbol rather than the
   final dimension-generic `rtdl_optix_collect_cell_mbr_nearest_frontier`
   symbol?
10. Should Goal5148 be closed as
    `completed_bounded_native_3d_cell_mbr_frontier_pod_matched`?

## Expected Answer Shape

```text
Verdict:

Blocking findings:

Required amendments:

Non-blocking notes:

Answers to review questions:
1.
2.
...
10.
```
