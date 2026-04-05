**Verdict**

The current RTDL evidence for RayJoin paper surfaces presents a mixed but honest picture. A significant portion of the paper's claims is addressed through either `exact` or `bounded analogue` reproductions. The project has successfully achieved an `exact` source match for the `County ⊲⊳ Zipcode` workload, which stands as the strongest piece of evidence, with demonstrated performance wins over PostGIS by the Embree and OptiX backends on specific, well-defined execution boundaries. Other real-world dataset workloads are covered by `bounded analogue` reproductions, and scalability claims are addressed with synthetic generators. Full polygon overlay materialization remains a `bounded analogue` (seed generation), and several of the paper's larger datasets are currently classified as `unavailable`.

**Findings**

Based on the provided documentation, the major RayJoin paper surfaces can be classified as follows:

*   **Exact:** The `County ⊲⊳ Zipcode` workload for `pip` queries is the only surface with a full, `exact` source reproduction. This has been rigorously tested and benchmarked, showing parity-clean results and superior performance against PostGIS in prepared and repeated raw-input scenarios for both the OptiX and Embree backends.
*   **Bounded Analogue:**
    *   The `Block ⊲⊳ Water` workload is addressed using the `BlockGroup ⊲⊳ WaterBodies` dataset, which is the closest publicly available and stable analogue.
    *   The `LKAU ⊲⊳ PKAU` workload is covered by a bounded, derived-input analogue (`sunshine_tiny`).
    *   The scalability studies from Figures 13 and 14 are reproduced using a deterministic synthetic scalability generator, making them accepted scaled analogues rather than reproductions of the original experiment's specific data.
    *   The polygon overlay surfaces (Table 4, Figure 15) are addressed via an `overlay-seed analogue`, which generates candidate pairs rather than materializing the full geometric intersection.
*   **Unavailable:** The continent-scale `Lakes ⊲⊳ Parks` datasets (e.g., Africa, Asia, Europe) are classified as `deferred-unavailable`. The public acquisition paths for these datasets proved unstable, and they have been intentionally excluded from the current reproduction package.
*   **Not Applicable:** This classification was not used, as all surfaces from the paper were considered for reproduction.

**Proposed row classification summary**

| Paper Target | Proposed Classification | Justification from Source Documents |
| :--- | :--- | :--- |
| **Table 3: LSI/PIP** | | |
| `County ⊲⊳ Zipcode` | exact | The "long exact-source `county_zipcode` positive-hit `pip`" is the strongest, most mature surface with parity-clean wins. |
| `Block ⊲⊳ Water` | bounded analogue | Reproduced with `BlockGroup ⊲⊳ WaterBodies` as the "closest stable public family available". |
| `LKAU ⊲⊳ PKAU` | bounded analogue | An accepted "bounded Australia analogue". |
| Other `LK* ⊲⊳ PK*` | unavailable | "Public acquisition path proved unstable" or "Unstaged continent pair". |
| **Figure 13: LSI Scalability** | bounded analogue | Uses a "deterministic synthetic scalability generator"; accepted as a "scaled analogue". |
| **Figure 14: PIP Scalability** | bounded analogue | Uses a "deterministic synthetic scalability generator"; accepted as a "scaled analogue". |
| **Table 4/Fig 15: Overlay** | bounded analogue | Implemented as a "compositional seed generation, not full materialization". An "overlay-seed analogue". |

**Recommended next execution rows**

Based on the goal of a "full honest RayJoin reproduction," the following actions are recommended:

1.  **Formalize LSI for `County ⊲⊳ Zipcode`:** The reports focus heavily on `pip` for the exact-source `County ⊲⊳ Zipcode` workload. The next execution should explicitly run and document the `lsi` workload on this same exact-source dataset to confirm its status and performance, aiming for the same `exact` classification.
2.  **Advance the Overlay Analogue:** The current `overlay-seed analogue` is a critical first step. A high-priority research and development effort should be directed at moving from seed generation to full polygon materialization to achieve a more faithful reproduction of the paper's overlay experiments.
3.  **Re-evaluate Dataset Availability:** Periodically re-assess the availability of the currently `unavailable` continent-scale datasets. If stable sources become available, they can be moved into the `planned` state for reproduction.
4.  **Consolidate Bounded Analogues:** Perform a consolidated run and analysis of all accepted `bounded analogue` workloads (`BlockGroup ⊲⊳ WaterBodies`, `LKAU ⊲⊳ PKAU`, and the scalability suites) to present them as a single, coherent package of evidence under the Goal 102 framework.
