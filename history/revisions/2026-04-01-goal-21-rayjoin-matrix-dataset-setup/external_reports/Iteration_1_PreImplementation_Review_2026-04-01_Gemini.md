I will read the specified files to review the Goal 21 setup.
### Findings
- **Decomposition Logic:** The split into Goal 21 (Planning/Data), 22 (Implementation), and 23 (Execution) is a deliberate risk-mitigation strategy. It prevents scope inflation by requiring Goal 22 to only address blockers explicitly identified during the Goal 21 data mapping phase.
- **Isolation of Concerns:** Goal 21 correctly prioritizes freezing the reproduction matrix, dataset provenance, and runtime profiles. This ensures the "what" and "with what data" are settled before any "how" (code changes) begins in Goal 22.
- **Runtime Policy:** The `5–10 minute` local runtime budget is clearly defined and serves as a hard constraint for the profile definitions. This policy effectively prevents open-ended execution times on the Embree backend.
- **Fidelity Transparency:** The requirement for explicit fidelity labels (`exact-input`, `derived-input`, `synthetic-input`) ensures technical honesty regarding which parts of the RayJoin paper are being reproduced directly versus through substitutes.

### Decision
The setup for Goal 21 is structurally sound, evidence-based, and provides the necessary constraints to ensure a disciplined reproduction program. The plan is ready for execution.

Consensus to begin implementation.
