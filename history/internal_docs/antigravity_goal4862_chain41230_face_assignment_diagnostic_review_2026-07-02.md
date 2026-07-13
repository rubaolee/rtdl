# Antigravity Review Verdict: Goal4862 Chain 41230 Face Assignment Diagnostic

**Date:** 2026-07-02
**Verdict Label:** `approve_goal4862_diagnosed_midpoint_face_selection_mismatch_authorize_goal4863`

---

## 1. Answers to Review Questions

### Question 1: Does the probe correctly preserve the boundary: diagnostic only, no runtime modification, no performance claim?
**Answer:** Yes. The probe script [goal4862_chain41230_face_assignment_probe.py](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4862_chain41230_face_assignment_probe.py) is purely diagnostic. It does not perform any persistent runtime file modifications or optimization updates. It uses memory-only monkeypatching via the [install_probe](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4862_chain41230_face_assignment_probe.py#L21) function to intercept output chain data at the targeted chain `41230`, writes the state to [goal4862_chain41230_face_assignment_probe_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4862_chain41230_face_assignment_probe_summary.json), and halts. It explicitly notes that the high execution time is a debugging-efficiency issue, making no performance optimization claims.

### Question 2: Does the face inverse mapping prove this is not merely a final dynamic face-id renumbering-only mismatch?
**Answer:** Yes. The face inverse mapping in [goal4862_chain41230_face_assignment_probe_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4862_chain41230_face_assignment_probe_summary.json) maps final face IDs back to raw keys `(left/right_polygon_id, other_map_polygon_id)`:
* Final IDs `280` and `290` (author expectations) correspond to keys `(5, 10950)` and `(22, 10950)`.
* Final IDs `294` and `295` (RTDL output) correspond to keys `(5, 10938)` and `(22, 10938)`.

Since the raw keys themselves differ (specifically the selected other-map face IDs are `10950` vs `10938`), this represents a true spatial/topological selection discrepancy rather than a simple indexing or renumbering offset.

### Question 3: Does the evidence support the raw-face conclusion: author-implied `other_map_polygon_id = 10950`, RTDL generated `other_map_polygon_id = 10938`?
**Answer:** Yes. The author's expected output for chain `41230` assigns final face IDs `280` and `290`, which map to `(5, 10950)` and `(22, 10950)`. Since the left and right raw faces are `5` and `22`, the author-implied `other_map_polygon_id` is `10950`. RTDL's output assigns final face IDs `294` and `295`, which map to `(5, 10938)` and `(22, 10938)`, meaning RTDL's generated `other_map_polygon_id` is `10938`.

### Question 4: Is it correct to stop blaming Section 5.2 LSI row materialization for this mismatch?
**Answer:** Yes. The split chain geometry, chain IDs, and point IDs align exactly with the author expectations (chain `41230` starts at point `42104` and ends at `42105` for length 2 in both outputs). Furthermore, the LSI gate passed with exact row and count consistency (`961165` rows). Therefore, LSI row materialization is not missing or producing erroneous split points for this chain.

### Question 5: Is it correct to stop blaming ordinary Section 5.3 vertex PIP for this mismatch?
**Answer:** Yes. The vertex PIP consistency gate passed perfectly at the count and normalized segment-hash level (positive count matching `47327744` and identical FNV64 hash `17585803063680255704`). The mismatch on chain `41230` occurs on a segment span between two adjacent intersections (`flush_kind: "between_adjacent_intersections"`), which relies on midpoint point-location queries rather than ordinary vertex point-in-polygon queries.

### Question 6: Is the best current classification Section 5.7 midpoint point-location / midpoint face-selection mismatch?
**Answer:** Yes. The mismatch occurs on a span between two adjacent intersections on map0 edge `43212`. The assigned face depends on point location queried at the midpoint of this segment, making it a Section 5.7 midpoint point-location / midpoint face-selection mismatch.

### Question 7: Is Goal4863, a localized midpoint point-location contract probe and repair, the right next goal?
**Answer:** Yes. The next goal (Goal4863) should isolate the midpoint point-location query for this segment (on map0 edge `43212`), compare it to the author-implied expected face `10950`, and repair any discrepancies in the generic midpoint point-location contract.

### Question 8: Should Section 5.7 correctness and performance remain unauthorized?
**Answer:** Yes. Since a mismatch occurs at chain `41230`, full byte-equal correctness is not achieved. Section 5.7 correctness and performance must remain unauthorized.

---

## 2. Technical Evaluation of Diagnostic Results

* **Target Chain:** `41230` on map0 edge `43212` ([goal4862_chain41230_face_assignment_probe_summary.json](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/history/internal_docs/goal4862_chain41230_face_assignment_probe_summary.json#L200-L211)).
* **Flush Kind:** `between_adjacent_intersections`.
* **Discrepancy Details:**
  * **Author Expectation:** Final face IDs `280 290` -> raw keys `(5, 10950)` / `(22, 10950)`.
  * **RTDL Generation:** Final face IDs `294 295` -> raw keys `(5, 10938)` / `(22, 10938)`.
  * **Underlying Root:** Point-location query on the midpoint of the split segment returned `10938` in RTDL, whereas the author's logic expects `10950`.

This localizes the issue specifically to the point-location query logic invoked by [_assemble_output_chains](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1555) calling [_midpoint_face_for_map](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1537) (which reads precomputed midpoint faces assigned in [_assign_midpoint_faces](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1515) from [_midpoints_for_sorted_xsects](file:///C:/Users/Lestat/Desktop/work/rtdl_v0_4_release_prep_review/src/rtdsl/rayjoin_overlay.py#L1451)).

---

## 3. Non-Authorization Boundaries

This review does **NOT** authorize:
* **Section 5.7 byte-equal correctness** (due to the mismatch at chain `41230`).
* **Section 5.7 topology-equivalent correctness** (out of scope).
* **Section 5.7 performance** or speedup claims.
* **Broad RayJoin paper reproduction** or general RTDL performance assertions.
* Treating bundled-helper diagnostics as generic public-language proof.

---

## 4. Next Step: Authorization of Goal4863

The next logical milestone is **Goal4863: chain 41230 midpoint point-location contract probe and repair**, authorized under the following disciplines:
1. Extract the exact two adjacent intersections around map0 edge `43212`.
2. Compute the midpoint using the same scaled/rational rule as the author.
3. Query the opposite map through RTDL point-location.
4. Compare the selected face against the author-implied expected face `10950`.
5. If a mismatch is confirmed, repair the generic directed point-location / midpoint contract (not a RayJoin-only output shortcut).
6. Add a small synthetic regression test for the midpoint face-selection case.
7. Rerun the chain `41230` probe before any full Section 5.7 rerun.
