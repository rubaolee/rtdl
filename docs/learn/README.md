# Learn RTDL

Use this door if you want to understand RTDL quickly and write programs.

## Path

1. [Project Front Page](../../README.md)
2. [Current RTDL Tutorial Track](../../tutorials/current/README.md)
3. [Current Claim Boundaries](current_claim_boundaries.md)
4. [RTDL Programming Surfaces](programming_surfaces.md)
5. [Versioning Glossary](../versioning.md)
6. [Quick Tutorial](../quick_tutorial.md)
7. [Source-Tree Doctor](source_tree_doctor.md)
8. [Run From The Source Tree](../../tutorials/current/01_source_tree_first_run.md)
9. [App And Example Quickstart](../app_example_quickstart.md)
10. [V3.0 App-Author Implementation Strategy](v3_0_app_author_implementation_strategy.md)
11. [V3.0 Embeddability Architecture Strategy](v3_0_embeddability_architecture_strategy.md)
12. [V3.0 C ABI Draft](v3_0_c_abi_draft.md)
13. [V3.0 C ABI Stability Policy](v3_0_c_abi_stability_policy.md)
14. [V3.0 C ABI Ownership And Threading Contract](v3_0_c_abi_ownership_threading_contract.md)
15. [V3.0 Zero-Copy Interop Contract](v3_0_zero_copy_interop_contract.md)
16. [V3.0 C ABI Staging Contract](v3_0_c_abi_staging_contract.md)
17. [V3.0 C ABI Embedding Examples](../../examples/current/embedding/README.md)
18. [v2.14 App-Author Implementation Strategy](v2_14_app_author_implementation_strategy.md)
19. [Primitive Discovery Workflow](primitive_discovery_workflow.md)
20. [Prepared Execution Pattern](prepared_execution_pattern.md)
21. [Prepared Session Reuse](prepared_session_reuse.md)
22. [Application Catalog](../application_catalog.md)
23. [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
24. [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)
25. [Benchmark Evidence Index](benchmark_evidence_index.md)
26. [RT-Core Evidence Matrix](rt_core_evidence_matrix.md)
27. [Feature Guide](../rtdl_feature_guide.md)
28. [Programming Guide](../rtdl/programming_guide.md)
29. [DSL Reference](../rtdl/dsl_reference.md)

## Keep In Mind

```text
Python writes the application.
RTDL expresses the RT-shaped kernel.
Backends execute app-agnostic engine contracts.
Partners handle tensor-side continuation when the app needs it.
```

The kernel DSL, primitive/prepared front doors, and partner continuations are
related but distinct. Start with [RTDL Programming Surfaces](programming_surfaces.md)
when deciding which surface your program should use.

For backend and performance boundaries, read:

- [Capability Boundaries](../capability_boundaries.md)
- [Current Claim Boundaries](current_claim_boundaries.md)
- [Backend Maturity](../backend_maturity.md)
- [Performance Model](../performance_model.md)
- [Partner Acceleration Boundaries](../partner_acceleration_boundaries.md)
- [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
- [RT-Core Evidence Matrix](rt_core_evidence_matrix.md)
