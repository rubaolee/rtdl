# Call For Review - Goal5457 LibRTS Mutation Contract Audit

Please strictly review whether RTDL already supports true mutable AABB prepared
state or whether a new generic API is required.

Primary files:

```text
src/rtdsl/aabb_index.py
src/rtdsl/optix_runtime.py
src/native/optix/rtdl_optix_api.cpp
src/native/optix/rtdl_optix_workloads.cpp
examples/current/research_benchmarks/librts_spatial_index/rtdl_librts_spatial_index_benchmark_app.py
Paper-reproduction-apps/librts-paper/results/librts_goal5457_mutation_contract_audit.json
tests/goal5457_librts_mutation_contract_audit_test.py
history/internal_docs/goal5457_librts_generic_mutation_contract_audit_2026-07-10.md
```

Questions:

1. Are current RTDL AABB prepared handles actually immutable?
2. Is the native OptiX mutation ABI truly absent?
3. Is historical `mutation_cpu_reference` only offline rematerialization?
4. Are same-shape request updates irrelevant to geometry/GAS mutation?
5. Does the author source use stable implicit IDs plus GAS/IAS update/refit?
6. Is `requires_new_generic_api` the correct exit?
7. Is atomic snapshot rebuild an honest first semantic implementation?
8. Is native incremental refit correctly left as a separate future goal?
9. Is the dynamic obstacle/contact-broadphase consumer sufficiently non-LibRTS?
10. Is Embree fully excluded from the proposed line?

Requested verdict:

```text
approve_goal5457_requires_new_generic_mutable_aabb_api
```
