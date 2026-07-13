# Call For Review - Goals5461-5462 Generic OptiX AABB Native Sparse Refit

Please review:

```text
src/native/optix/rtdl_optix_core.cpp
src/native/optix/rtdl_optix_workloads.cpp
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_prelude.h
src/rtdsl/optix_runtime.py
src/rtdsl/aabb_index.py
src/rtdsl/mutable_aabb_index.py
scripts/goal5461_generic_optix_aabb_native_refit_gate.py
tests/goal5461_generic_optix_aabb_native_refit_contract_test.py
tests/goal5462_generic_optix_aabb_sparse_refit_gate_test.py
tests/goal5459_generic_mutable_aabb_optix_snapshot_rebuild_test.py
history/internal_docs/goal5461_5462_generic_optix_aabb_native_sparse_refit_2026-07-10.md
history/internal_docs/goal5463_goals5461_5462_review_amendment_response_2026-07-10.md
history/internal_docs/goal5463_generic_optix_aabb_sparse_refit_linux_4096.json
history/internal_docs/goal5463_generic_optix_aabb_sparse_refit_linux_65536.json
```

Decision-critical questions:

1. Is `ALLOW_UPDATE` isolated to the mutable prepare symbol and used consistently for build/update?
2. Does sparse refit preserve primitive cardinality, slot order, and stable IDs?
3. Are duplicate/out-of-range slots rejected before device mutation?
4. Does failure rollback restore both packed box records and OptiX AABBs?
5. Is rollback failure itself fail-closed and visible?
6. Does the Python wrapper update host metadata only after native success?
7. Does pure Update use sparse refit while Insert/Delete/Clear retain rebuild?
8. Are CPU semantics unchanged?
9. Do Linux runtime tests and the combined LibRTS gate preserve `[2,1,0,1,0]`?
10. Are 12.62x and 15.63x correctly scoped to RTDL refit-vs-rebuild on one GTX 1070?
11. Is author performance parity correctly unclaimed?
12. Is the implementation app-neutral with Embree absent?

Requested verdict:

```text
approve_goals5461_5462_generic_optix_aabb_native_sparse_refit
```

Review-amendment hardware result:

```text
local Linux GTX 1070, rebuilt native OptiX library
Goal5459 + Goal5461 + Goal5462 + Goal5463 tests: Ran 15 tests, OK
post-amendment refit-vs-rebuild confirmation: 14.69x / 16.96x
```
