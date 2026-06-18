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
12. [v2.14 App-Author Implementation Strategy](v2_14_app_author_implementation_strategy.md)
13. [Primitive Discovery Workflow](primitive_discovery_workflow.md)
14. [Prepared Execution Pattern](prepared_execution_pattern.md)
15. [Prepared Session Reuse](prepared_session_reuse.md)
16. [Application Catalog](../application_catalog.md)
17. [Choosing A Partner For Custom Logic](partner_choice_for_custom_logic.md)
18. [Benchmark Partner Reference Matrix](benchmark_partner_reference_matrix.md)
19. [Benchmark Evidence Index](benchmark_evidence_index.md)
20. [RT-Core Evidence Matrix](rt_core_evidence_matrix.md)
21. [Feature Guide](../rtdl_feature_guide.md)
22. [Programming Guide](../rtdl/programming_guide.md)
23. [DSL Reference](../rtdl/dsl_reference.md)

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
