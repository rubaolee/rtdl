## Goal 2: Multi-Workload Datasets - Review and Planning Report

**Date:** 2026-03-29

### Scope Agreement

The primary objective of Goal 2 is to expand the RTDL framework beyond its current single segment-join path. This involves extending the compiler, IR, and Python data pipeline to support at least three distinct RayJoin workload surfaces, without immediately targeting GPU runtime execution. This goal is crucial as it addresses the current narrowness of the DSL and IR, integrates RayJoin datasets, and establishes a CPU-side validation pipeline for multiple workload semantics prior to OptiX runtime integration.

**Non-Goals:**
- Real OptiX runtime execution.
- GPU performance claims.
- Robust/exact precision parity with RayJoin.
- Full production overlay implementation if the overlay surface is represented compositionally.

**Success Criteria (as per Goal_2_Spec_2026-03-29_Codex.md):**
- RTDL can express at least three RayJoin workload surfaces.
- Each supported workload successfully lowers into a backend plan.
- Selected RayJoin datasets are ingestible via a Python pipeline.
- Tests cover both compiler artifacts and dataset-to-workload transformations.
- Consensus is reached between Codex and Gemini that the work materially advances v0.1 workload coverage.

### Recommended Workload Set

Based on the proposed scope in `Goal_2_Spec_2026-03-29_Codex.md` and `Iteration_1_PreImplementation_Report_2026-03-29_Codex.md`, the recommended workload set is:

1.  **Line Segment Intersection (LSI):** This forms a foundational geometric operation and is explicitly mentioned.
2.  **Point-in-Polygon (PIP):** Another fundamental spatial predicate, critical for many GIS and spatial analysis tasks.
3.  **Polygon Overlay Preparation/Composition:** This workload, grounded in LSI and PIP results, aims to model how complex spatial operations like polygon overlay would be composed. Implementing this as an explicit IR/workflow, even if not a full final overlay runtime, is valuable for extending the language and plan model beyond simple predicates. This addresses the "overlay count if implemented as composition" open question by affirming its value for IR/DSL growth.

### Recommended Dataset Set

To ground the development in realistic data and ensure compatibility with the eventual RayJoin backend, the following dataset strategy is recommended:

1.  **RayJoin Sample Data:** Begin with sample data provided under `test/dataset` from a public RayJoin repository (as referenced in `Goal_2_Spec_2026-03-29_Codex.md`). This provides a direct alignment with the target system.
2.  **Public Polygon Datasets:** Incorporate one or more public polygon datasets such as County/Zipcode or BlockGroup/WaterBodies (as practical). These datasets offer larger-scale, real-world examples to validate the dataset pipeline's ability to handle more complex geometries and data volumes. The focus should be on practical integration for CPU-only validation.

The dataset pipeline should support fetching/registering sources, parsing RayJoin-aligned formats, normalizing data into RTDL-friendly Python structures, and deriving workload-specific views (segments, polygons, point sets).

### Review Method Proposal

The review of the implementation will be structured to ensure all deliverables and success criteria are met, focusing on the CPU-side validation without requiring GPU runtime.

1.  **Code Review:** Thorough examination of:
    *   Python DSL extensions for clarity, expressiveness, and alignment with proposed workloads.
    *   IR extensions for clean representation of workload semantics.
    *   Lowering support to ensure correct translation to backend plan structures.
    *   Python dataset loaders and preprocessing logic.
2.  **Functional Verification:**
    *   **Unit and Integration Tests:** Verify the correctness of DSL extensions, IR transformations, and lowering logic for each selected workload with representative data from the recommended dataset set.
    *   **End-to-End CPU-Side Semantic Tests:** Implement tests that take selected RayJoin datasets, apply the defined workloads via RTDL, and produce verifiable results. These results should be semantically correct, acknowledging that exact precision parity with a potential RayJoin GPU implementation is a non-goal. This will confirm the "dataset-to-workload transformations."
3.  **Documentation Review:** Confirm that supported workloads, DSL syntax, and the dataset pipeline are clearly documented.
4.  **Consensus Meeting:** A final review meeting between Codex and Gemini to confirm all success criteria have been demonstrably met and that the work sufficiently advances v0.1 workload coverage.

### Evidence Required For Consensus

To reach consensus, the following concrete evidence will be required:

1.  **Implemented Codebase:**
    *   Python DSL code for LSI, PIP, and Polygon Overlay (compositional approach).
    *   IR definitions and manipulation logic supporting these workloads.
    *   Lowering passes translating RTDL IR to backend plan representations for each workload.
    *   Python modules for loading, parsing, and normalizing RayJoin sample and public polygon datasets.
2.  **Comprehensive Test Suite:**
    *   Unit tests covering new DSL constructs, IR nodes, and lowering rules.
    *   Integration tests demonstrating the end-to-end flow from dataset ingestion, through RTDL processing, to generated backend plans for each workload.
    *   CPU-side semantic tests for LSI, PIP, and a representative Polygon Overlay composition, with assertions on expected logical outcomes.
3.  **Generated Artifacts:**
    *   Example backend plan (`plan.json`) files generated by RTDL for each of the three workloads using the specified datasets.
4.  **Updated Documentation:**
    *   Clear documentation outlining the new DSL features, supported workload types, and instructions for using the new dataset pipeline.
5.  **Review Report:** A concise report from Codex detailing how each success criterion has been met, referencing specific code, tests, and documentation.

### Risks or Scope Changes

The following open questions from the `Goal_2_Spec_2026-03-29_Codex.md` are identified as potential risks or areas requiring explicit confirmation/clarification during implementation:

1.  **Exact Workload Definition:** While LSI, PIP, and compositional Polygon Overlay are recommended, the precise scope of "Polygon Overlay Preparation/Composition" needs careful definition to avoid feature creep while ensuring material extension of the language. This should be clarified early in the implementation phase.
2.  **Dataset Selection Specificity:** "Which RayJoin datasets are the best fit for a CPU-only validation pipeline?" While general categories are recommended, specific dataset names or sources should be identified and agreed upon to ensure reproducible testing. This could be a minor scope expansion if additional effort is needed to integrate a new, larger public dataset.

### Final Recommendation

The proposed Goal 2 for extending RTDL to support multiple RayJoin workloads and integrate relevant datasets is well-justified and critical for the project's evolution beyond a single use-case. The recommended workload and dataset sets provide a balanced approach to extending functionality and ensuring real-world applicability. The outlined review method and evidence requirements offer a clear path to assessing the implementation's success. It is recommended to proceed with implementation based on this plan, with a focus on clarifying the precise scope of the compositional Polygon Overlay workload and specific large-scale public datasets at the outset.
