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
11. [RTDL v3.0 Release Package](../release_reports/v3_0/README.md)
12. [Primitive Discovery Workflow](primitive_discovery_workflow.md)
13. [Prepared Execution Pattern](prepared_execution_pattern.md)
14. [Prepared Session Reuse](prepared_session_reuse.md)
15. [Application Catalog](../application_catalog.md)
16. [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
17. [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)
18. [Benchmark Evidence Index](benchmark_evidence_index.md)
19. [RT-Core Evidence Matrix](rt_core_evidence_matrix.md)
20. [Feature Guide](../rtdl_feature_guide.md)
21. [Programming Guide](../rtdl/programming_guide.md)
22. [DSL Reference](../rtdl/dsl_reference.md)

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

## V4 Preparatory Embedding Docs

These files remain in the repository as historical or preparatory material.
They are not part of the V3.0 release scope, V3.0 completion criteria, or V3.0
success claims:

- [V3.0 Embeddability Architecture Strategy](v3_0_embeddability_architecture_strategy.md)
- [V3.0 C ABI Draft](v3_0_c_abi_draft.md)
- [V3.0 C ABI Stability Policy](v3_0_c_abi_stability_policy.md)
- [V3.0 C ABI Ownership And Threading Contract](v3_0_c_abi_ownership_threading_contract.md)
- [V3.0 Zero-Copy Interop Contract](v3_0_zero_copy_interop_contract.md)
- [V3.0 C ABI Staging Contract](v3_0_c_abi_staging_contract.md)
- [V3.0 Toolchain Support Matrix](v3_0_toolchain_support_matrix.md)
- [V3.0 Binding And Device Interop Matrix](v3_0_binding_and_device_interop_matrix.md)
- [C ABI Embedding Examples](../../examples/current/embedding/README.md)

## Historical V2 Snapshot

The V2.14 app-author strategy is preserved as release-history evidence only.
For current guidance, use the V3.0 path above:

- [v2.14 App-Author Implementation Strategy](v2_14_app_author_implementation_strategy.md)
