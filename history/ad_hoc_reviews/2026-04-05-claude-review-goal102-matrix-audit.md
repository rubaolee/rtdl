---

## Verdict

The evidence base is internally consistent and well-documented. No surface is silently omitted. However, **no row qualifies as `exact`** under Goal 102's schema — even the strongest County/Zipcode rows use a top-4-state subset, not the paper's full dataset. The current coverage is a sound but partially bounded analogue package.

---

## Findings

### Classification of evidence by term used internally vs. Goal 102 schema

The project uses "long exact-source" to mean "exact code/implementation path with real dataset provenance" (as opposed to synthetic or cached BVH inputs). This is **not** the same as Goal 102's `exact` class, which would require paper-identical datasets.

**Table 3 surface (LSI + PIP across 8 dataset pairs)**

| Paper row | Current status | Goal 102 class | Evidence basis |
|---|---|---|---|
| County ⊲⊳ Zipcode (LSI, PIP) | done-bounded | `bounded_analogue` | top-4-state subset (`top4_tx_ca_ny_pa`); Goals 50/59/79/84/89 |
| Block ⊲⊳ Water (LSI, PIP) | done-bounded | `bounded_analogue` | different family (`BlockGroup ⊲⊳ WaterBodies county2300_s10`); Goal 79 covers end-to-end PIP only |
| LKAU ⊲⊳ PKAU (LSI, PIP) | done-bounded | `bounded_analogue` | derived synthetic input `sunshine_tiny`; Goals 54/59 |
| LKAF ⊲⊳ PKAF | deferred-unavailable | `unavailable` | acquisition path unstable |
| LKAS ⊲⊳ PKAS | deferred-unavailable | `unavailable` | unstaged |
| LKEU ⊲⊳ PKEU | deferred-unavailable | `unavailable` | unstaged |
| LKNA ⊲⊳ PKNA | deferred-unavailable | `unavailable` | unstaged |
| LKSA ⊲⊳ PKSA | deferred-unavailable | `unavailable` | unstaged |

Key gap: accepted Table 3 LSI rows exist only at the bounded-package level (Goals 50/59). The long exact-source surface (Goals 81–89) covers **PIP only**. There is no accepted LSI run on the long exact-source `county_zipcode` surface.

**Figure 13 (LSI scalability) / Figure 14 (PIP scalability)**

All 8 sub-figures (13a–d, 14a–d): deterministic synthetic generator, correct shape (R=5M, S=1M–5M, uniform + gaussian). Classification: `bounded_analogue`. Evidence is accepted from the scalability goals.

**Table 4 / Figure 15 (polygon overlay)**

Classification: `bounded_analogue` — with a material caveat: RTDL overlay is seed generation only, not full polygon materialization. The accepted closure is Goal 56 (LKAU sunshine_tiny four-system row) + Goal 23 (Embree analogue rows). The paper's full overlay output is `not_applicable` in the current codebase.

**Long exact-source county_zipcode PIP (main performance surface)**

This is the trust anchor for performance claims. Both OptiX and Embree beat PostGIS on prepared and repeated raw-input boundaries (Goals 84/89). Vulkan is parity-clean but slower. Classification for Goal 102 purposes: `bounded_analogue` (subset dataset). This is the best row in the package.

**blockgroup_waterbodies**

Goal 79 covers only end-to-end PIP. No accepted prepared or repeated-raw-input boundary exists for this family. Goal 102 would need to classify this as a gap if those boundaries matter for the release matrix.

---

## Proposed Row Classification Summary

| Paper surface | Goal 102 class | Notes |
|---|---|---|
| Table 3 County/Zipcode LSI | `bounded_analogue` | bounded-package closure only; no long exact-source LSI run |
| Table 3 County/Zipcode PIP | `bounded_analogue` | strongest row; long exact-source with performance wins |
| Table 3 Block/Water LSI | `bounded_analogue` | different family analogue; bounded-package only |
| Table 3 Block/Water PIP | `bounded_analogue` | end-to-end only (Goal 79); no prepared/repeated boundary |
| Table 3 LKAU LSI, PIP | `bounded_analogue` | synthetic-derived input |
| Table 3 LKAF/LKAS/LKEU/LKNA/LKSA | `unavailable` | dataset acquisition path unstable or missing |
| Figure 13 LSI scalability (all 4) | `bounded_analogue` | synthetic generator; correct structure |
| Figure 14 PIP scalability (all 4) | `bounded_analogue` | synthetic generator; correct structure |
| Table 4 overlay | `bounded_analogue` | seed-generation analogue only |
| Figure 15 overlay speedup | `bounded_analogue` | derived from same seed-generation runs |

No row currently qualifies as `exact`. No row is `not_applicable` except full polygon overlay materialization (paper produces materialized output; RTDL does not).

---

## Recommended Next Execution Rows

These are the rows where accepted artifacts are absent or have boundary gaps, and which are runnable with existing datasets and backends (Embree + OptiX only, per Goal 102 scope):

1. **County/Zipcode LSI — long exact-source boundary.** PIP has accepted wins on prepared and repeated raw-input; LSI on the same surface has not been run outside bounded-package closure. This is the single highest-value missing row for Goal 102 Table 3 coverage.

2. **BlockGroup/WaterBodies PIP — prepared and repeated raw-input boundaries.** Goal 79 covers only end-to-end. Adding prepared/repeated rows would make the Block/Water analogue comparable in depth to the County/Zipcode story.

3. **BlockGroup/WaterBodies LSI — any boundary.** Currently no accepted LSI run on this family outside bounded-package closure.

4. **LKAU/PKAU LSI — long or bounded boundary (Embree + OptiX).** The bounded package closure covers LSI at the package level but the depth of the LKAU LSI story in the exact-source sense is unclear from these files.

5. **Scalability re-run confirmation (Figures 13/14) under Embree + OptiX only.** Goal 102 explicitly restricts to these two backends; confirm the scalability artifacts carry forward cleanly under that restriction before freezing Phase 1.
