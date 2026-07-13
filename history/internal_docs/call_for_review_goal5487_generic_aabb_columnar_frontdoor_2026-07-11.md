# Call For Review: Goal5487 Generic AABB Columnar Front Door

Please strictly review the implementation and result report:

```text
history/internal_docs/goal5487_generic_aabb_columnar_frontdoor_result_2026-07-11.md
src/rtdsl/aabb_columns.py
src/rtdsl/aabb_index.py
src/rtdsl/optix_runtime.py
src/rtdsl/__init__.py
tests/goal5487_generic_aabb_columnar_frontdoor_test.py
```

## Expected Answer Shape

```text
Verdict: approve / approve_with_required_amendments / revise
Blocking findings:
Required amendments:
Non-blocking notes:
Genericity assessment:
Device-residency claim assessment:
```

## Review Questions

1. Does `Aabb2DColumns` validate equal lengths, finite bounds, bound order,
   integer IDs, and uint32 range without silent conversion errors?
2. Is `prepare_aabb_index_2d_columns` app-neutral and correctly separated from
   the existing row-shaped API?
3. Does the CPU fallback preserve the existing generic semantics?
4. Does the OptiX packing path match `_RtdlAabb2D` size and field offsets?
5. Is the NumPy owner retained long enough to make the ctypes view safe?
6. Does the implementation avoid claiming device zero-copy or device-resident
   index construction?
7. Is the new surface exported consistently from `rtdsl`?
8. Do tests cover behavior, ABI layout, fail-closed validation, and app-neutral
   source boundaries?
9. Does the report correctly leave POD verification and LibRTS promotion as
   separate next gates?
10. Is any existing paper-app claim or Embree policy accidentally changed?

Please inspect the code directly. In particular, do not treat `from_buffer`
as device zero-copy: it is only a host NumPy-to-ctypes ABI view, followed by
the existing native upload path.
