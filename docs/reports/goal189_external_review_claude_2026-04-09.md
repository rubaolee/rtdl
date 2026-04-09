# Goal 189 External Review: Claude

Date: 2026-04-09

## Verdict

Structurally sound and scope-clean. All four native backends were genuinely
split from single-file monoliths into modular subdirectories; public C ABI and
Python runtime contracts are preserved; bounded tests passed for each slice;
and the one GPU-verification gap (OptiX and Vulkan live execution) is honestly
disclosed.

## Findings

- The four top-level `.cpp` files are now thin include-coordinators:
  `rtdl_oracle.cpp` (3 lines), `rtdl_embree.cpp` (8 lines),
  `rtdl_optix.cpp` (8 lines), `rtdl_vulkan.cpp` (7 lines). All real logic now
  lives under `src/native/<backend>/`.
- The prelude headers carry the full public C ABI declarations unchanged; no
  entry point was renamed or removed.
- A real ABI alignment bug was found and fixed during the Embree slice:
  `RtdlRay2D` was `#pragma pack(1)` on the C side but the shared Python
  `ctypes` class in `embree_runtime.py` was missing `_pack_ = 1`. The fix is
  in place and applies to all backends sharing that runtime.
- OptiX and Vulkan bounded verification is structural (compile-check + Python
  import) rather than live GPU execution. This is accurately disclosed in the
  report and not presented as full runtime confirmation.

## Summary

Goal 189 is complete and closes cleanly. The four backends are genuinely
modularized, the ABI and Python runtime surface are intact, one real bug was
fixed in the process, and the scope boundary was respected throughout. The
only unresolved item is live GPU execution testing for OptiX and Vulkan, which
requires hardware not available on this host and is correctly flagged as
deferred.
