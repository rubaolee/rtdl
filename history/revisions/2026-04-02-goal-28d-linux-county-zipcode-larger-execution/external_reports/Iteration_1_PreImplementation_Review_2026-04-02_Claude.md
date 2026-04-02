## Goal 28D Pre-Implementation Review

### Technical Correctness

**What is correct:**
- Goal 28C results are accurately carried forward: USCounty fully staged (3144 features, 12273 chains), Zipcode at a 7000-feature checkpoint from 28 valid pages, CPU/Embree parity demonstrated on a 1×1 feature slice.
- The "honest boundary" clause in the goal doc is real and correctly scoped — it explicitly allows bounded slices as long as they are honestly reported.
- The ArcGIS service dependency for completing Zipcode staging is acknowledged with "if the service still responds," which is the correct hedge.
- The spec's five execution steps are logically sequenced and consistent with the 28C artifacts on the host.

**Design gaps acknowledged but not yet resolved (appropriate for execution phase):**

1. **lsi_cpu scaling wall.** In 28C, 1 county chain × 6 zipcode chains → 3.6s CPU for LSI. One zipcode feature alone produced 5,600 segments; full county is 12.4M segments. The current driver always runs CPU and Embree in parallel for parity. "Extend the driver as needed" must mean either (a) bounding-box pre-filter to reduce segment counts, (b) run CPU parity only on a small verified sub-slice while running Embree on a larger slice, or (c) accept that the larger execution is Embree-timed with a small parity-checked anchor. The spec correctly leaves this as a decision for execution rather than a pre-implementation specification.

2. **Geographic co-location.** The 28C driver selects first-N features by page order. The 28C LSI result was 0 rows because the first county feature (Alabama) and first zipcode feature (Alaska) are spatially disjoint. Increasing N to even 10–20 should naturally include co-located pairs, but this is not guaranteed by the current driver. The driver extension needs to account for this.

Both of these are correctly scoped as implementation decisions, not pre-implementation blockers, given the goal doc's explicit allowance for bounded and honestly-documented results.

### Honest Scope

The scope documents are honest: "larger" is not defined as paper-scale, the goal doc explicitly warns against claiming paper-scale unless the host actually sustains those runs, and the pre-implementation report frames the right open questions without overclaiming answers. No inflated promises.

### Blockers

None. The Zipcode staging external dependency is properly hedged. The lsi_cpu and co-location design decisions are appropriate to resolve during execution. The host is confirmed ready from 28C.

---

`Consensus to begin execution`
