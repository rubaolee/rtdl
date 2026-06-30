I will search for the relevant report files and check their content to verify the implementation details of Goals 1318, 1320, and 1321.
I will read the reports for Goals 1318, 1320, and 1321 to verify the implementation details and evidence of pod validation.
I will check the current migration inventory and the native ABI header to confirm the status and definitions.
I will check the implementation of generic polygon primitives to ensure the score reduction logic is present.
I will examine the example file to verify that it correctly utilizes the new generic APIs.
I will check the OptiX performance support for `polygon_set_jaccard` to see if the "OptiX slower" warning is still present.
I will read the test file for Goal 1321 to confirm that the native polygon pair area summary ABI is thoroughly tested.
Based on the review of the implementation and reports for Goals 1318, 1320, and 1321, the request to reclassify `polygon_set_jaccard` is **ACCEPT**.

### Technical Rationale:
1.  **Native Bounded Collection (Goal 1318):** `polygon_set_jaccard` now correctly routes Embree and OptiX summary modes through native bounded polygon-pair collection wrappers. Pod OptiX evidence confirms routing and validation on hardware.
2.  **Generic Score Reduction (Goal 1320):** A generic score-reduction surface has been implemented that runs only after complete candidate coverage is reported. It uses the `POLYGON_SET_JACCARD_SCORE_REDUCTION` metadata and ensures integer parity for the oracle.
3.  **Backend-Neutral ABI (Goal 1321):** The app now uses the backend-neutral `rtdl_native_reduce_polygon_pair_exact_area_summary` ABI for scoring, removing the app-named native continuation and fulfilling the requirement for a unified reduction path.
4.  **Consistency:** The implementation maintains the diagnostic status by keeping public wording unauthorized and explicitly recording that OptiX remains slower than Embree.

### Inventory Update:
The `v1_5_migration_inventory.py` entry for `polygon_set_jaccard` / `chunked_candidate_scoring` may be updated as follows:
- **status:** `"pod_verified_generic"`
- **remaining_app_specific_work:** `()`
- **public_wording_authorized:** `False`
- **boundary:** `"diagnostic only; native bounded collection and backend-neutral score reduction are routed and pod-validated; OptiX remains slower than Embree; public speedup wording remains unauthorized"`

Additionally, the following blocker in `v1_5_migration_blockers()` should be removed:
- `"Jaccard remains diagnostic until native REDUCE_FLOAT(SUM) score reduction runs after complete bounded collection"`
