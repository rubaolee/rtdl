Here is the full review.

---

## 1. Verdict: APPROVE-WITH-NOTES

The paper is technically sound and structurally consistent with the final accepted backend story. Numbers in Table 1 match the authoritative final-head artifacts (goal99 for OptiX prepared, goal100 for OptiX raw-input, goal100 for Embree prepared). All major scope qualifiers are in place. One stale supporting document creates a cross-reference hazard, and two minor writing issues are worth a pass before submission.

---

## 2. Findings

### 2a. Numbers: Paper Table 1 vs. canonical artifacts

All Table 1 cells cross-check correctly against the final artifacts:

| Row | Cell | Paper | Canonical source | Match |
|---|---|---|---|---|
| Prepared | Embree | 1.04–1.44 | goal100 (1.043, 1.440) | ✓ |
| Prepared | OptiX | 2.13–2.54 | goal99 (2.133, 2.537) | ✓ |
| Prepared | Vulkan | 6.14–6.16 | goal89 (6.139, 6.164) | ✓ |
| Prepared | PostGIS | 3.02–3.40 | goal99+100 (3.01–3.39) | ✓ |
| Best repeated | Embree | 1.09 | goal89 (1.092) | ✓ |
| Best repeated | OptiX | 2.11 | goal100 (2.113) | ✓ |
| Best repeated | Vulkan | 6.71 | goal89 (6.710) | ✓ |
| First call | Embree | 1.96 | goal89 (1.960) | ✓ |
| First call | OptiX | 7.05 | goal100 (7.045) | ✓ |
| First call | Vulkan | 16.14 | goal89 (16.140) | ✓ |

### 2b. Stale number in architecture_api_performance_overview.md (doc inconsistency, not paper error)

`docs/architecture_api_performance_overview.md` line ~151 reports OptiX best-repeated as "about `1.087 s`". That is the goal89 pre-repair value. The correct post-goal98/99 value is 2.113 s (goal100). The **paper uses the correct value**. But the arch doc would directly contradict the paper if a reviewer opens it.

### 2c. Abstract claim boundary is honest but imprecise

The abstract says "outperform PostGIS on the published prepared-execution and repeated-call boundaries." This is accurate—it refers to the best-repeated rows—but it could be read as "all calls." The table makes the cold-start gap (OptiX 7.05 s > PostGIS 3.13 s) explicit, so no false claim is made. The abstract does not lie, but it omits the cold-start caveat that the table provides.

### 2d. Scope disclaimers are present and correctly placed

- Overlay-seed contract: defined in §5.6, called out in every table and figure caption, restated in Limitations. ✓  
- Deferred continental families (LKAF/LKAS/LKEU/LKNA/LKSA): explicitly named in §8. ✓  
- `county2300_s10` vs. full Block×Water: correctly qualified. ✓  
- Vulkan not in main performance claim: stated in §5.4, §7, §8, Conclusion. ✓  

### 2e. Section organization anomaly

§3 ("What Ray Tracing Is and Why It Matters Beyond Graphics") contains the subsection "RayJoin as the First Application Target" which holds detailed scope disclaimers—not background. It reads as placed there to avoid adding a new section break, but it blends background motivation with scope limitations in a way reviewers may find unusual. Content is accurate; location is awkward.

### 2f. Figure coverage

All four figures referenced in the LaTeX (`rtdl_architecture.png`, `figure13_lsi_scalability.png`, `figure14_pip_scalability.png`, `figure15_overlay_speedup.png`) are present in the figures directory. ✓

### 2g. Parity claims

SHA-256 hash-level parity is asserted across the validated packages. The goal100 report confirms parity on both OptiX raw-input reruns and carries forward the Vulkan artifacts with explicit provenance. This is appropriately disclosed in the table caption ("consolidate the final reviewed backend packages rather than a single synchronized rerun"). ✓

---

## 3. Agreement and Disagreement

**Agreements between paper and canonical docs:**
- All Table 1 numbers match final-head artifacts exactly.
- Vulkan is correctly described as parity-clean but slower across all docs and the paper.
- The overlay-seed scope is identically stated in the paper, v0.1 release notes, v0.1 support matrix, and v0.1 final plan.
- Cold-start asymmetry (OptiX first-call 7.05 s) is accurately surfaced in Table 1 and the Performance Interpretation subsection.

**Disagreements (architecture doc vs. paper):**
- `architecture_api_performance_overview.md`: OptiX repeated-best stated as ~1.087 s. Paper (and goal100): 2.113 s. These conflict. The paper is right; the doc is stale from goal89 (pre-regression-repair).

**No disagreements** with v0.1 release notes, v0.1 support matrix, v0.1 final plan, v0.1 reproduction and verification docs, or goal89/goal99/goal100 canonical reports on any substantive claim.

---

## 4. Recommended next step

**Before submitting the paper:**
1. **(Required)** Update `docs/architecture_api_performance_overview.md`, "Repeated raw-input boundary" section, OptiX line: change `about 1.087 s` → `about 2.11 s`. This removes the cross-reference contradiction any reviewer, co-author, or artifact checker will hit immediately.

2. **(Optional, recommended)** In the abstract, add a parenthetical qualifying "repeated-call" as "best-repeated-call" or add one clause noting the cold-start penalty—e.g., "...on the prepared-execution and best-repeated-call boundaries, while first-call cost remains higher for the GPU backends." This makes the Table 1 cold-start row legible without even reading the body.

3. **(Low priority)** Consider moving the scope-disclaimer content from §3.1 ("RayJoin as the First Application Target") into §5 ("Design Considerations and Evaluation Methodology") where the rest of the scoping language lives. The current location is readable but organizationally surprising.
