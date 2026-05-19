# Goal2404 RT-DBSCAN OptiX Backend Claim Boundary Correction

Date: 2026-05-19

Status: claim-boundary correction before further RT-DBSCAN performance work

## Correction

During the follow-up audit after Goal2403, the current
`optix_core_flags_cupy_grid_components_3d` and `optix_prepared_rows` paths were
rechecked against the native implementation. They use the OptiX backend's
prepared 3-D fixed-radius uniform-cell CUDA kernels, not the `frn3d` OptiX RT
traversal pipeline.

Therefore the previous local metadata label `rt_core_accelerated=true` was too
strong for these two prepared 3-D modes. The code, README, JSON artifacts, and
reports now mark those modes as:

```text
optix_backend_used=true
native_execution_path=prepared_uniform_cell_cuda_grid_3d
rt_core_accelerated=false
```

## What Remains Valid

- The bridge is still generic and app-agnostic.
- It still avoids O(edges) neighbor-row materialization.
- It still proves that RTDL can compose backend fixed-radius summaries with a
  partner device-grid component continuation.
- It still shows the next runtime gap clearly.

## What Is Not Claimed

- No paper reproduction claim.
- No paper-level speedup claim.
- No broad RT-core DBSCAN acceleration claim.
- No RT-core claim for the prepared 3-D summary bridge until a true RT traversal
  summary or device-output path is implemented and validated on pod hardware.

## Next Engineering Target

The next useful RT-DBSCAN slice is generic, not app-specific:

```text
3-D fixed-radius threshold/count device columns
```

That can be implemented either as a true RT traversal device-output path or as a
cheaper prepared backend summary path. Either way, the contract must stay
app-agnostic: query ids, bounded neighbor counts, threshold flags, and explicit
claim metadata.
