---

## Review: Back-Half Sections of RTDL/RayJoin Paper

### 1. Verdict

**APPROVE-WITH-NOTES**

The paper is substantively honest and has good claim-discipline instincts throughout. One issue approaches blocking (abstract vs. table contradiction on PIP performance), but it can be resolved editorially without restructuring the work.

---

### 2. Findings

**Design Considerations and Evaluation Methodology (§5)**

- The three design considerations are clear and grounded. The "layered systems story" framing in Optimization Strategy is the right rhetorical move; it protects against reviewer expectations of a raw GPU-beats-database result.
- The correctness methodology is the strongest part of the section: layered oracle → Embree/OptiX → PostGIS, checked at hash level. That is auditable and precise.
- **Issue (methodological transparency):** The GEOS dependency is disclosed but not fully unpacked. The paper adopted GEOS-backed `covers(point)` semantics for RTDL's native oracle and Embree, and PostGIS also uses GEOS internally. A reviewer may flag this as partially circular: parity is achieved partly by aligning both systems to the same geometric engine. One sentence acknowledging this — and explaining it's a deliberate choice to remove ambiguity, not a shortcut — would preempt that question.
- **Minor:** "about 15 GiB" in Table 1 is informal language for a hardware spec. Should be a measured value or a range.
- The five optimization bullets in §5.2 include vague entries ("canonical-record fast paths"). The term "conservative backend candidate generation" should say "over-approximating" or "returning false positives filtered in the host refine step" — the current phrasing is not self-explanatory.

**Results (§6)**

- **Issue (near-blocking — abstract vs. table):** The abstract states: *"RTDL with Embree and RTDL with OptiX both outperform PostGIS on the published prepared-execution and repeated-call boundaries."* But Table 2 shows `PostGIS = 0.43s` vs. `Embree = 16.8s` on County⋈Zipcode PIP. The Performance Interpretation subsection explains the difference in contracts (GiST short-circuit vs. full materialization), but it never provides the specific timing boundary where RTDL *does* beat PostGIS. The abstract claim therefore currently floats with no supporting numbers. Either: (a) add a row or footnote with the prepared-execution comparison numbers, or (b) revise the abstract to drop or qualify that claim.
- The LSI rows in Table 2 show PostGIS at 34s vs. Native Oracle at 89s — a 2.6× advantage for PostGIS that is never discussed in the text. The Performance Interpretation subsection explains the PIP gap but says nothing about LSI. That asymmetry will be noticed by reviewers.
- The scalability figures (Figures 13/14 analogs) receive no textual interpretation of findings. The section says only that they "preserve the experiment shape." What does the shape show? Do throughput and query time behave as expected under scale-up? Even one sentence of finding per figure is needed.
- The overlay speedup figure (Figure 15 analog) reports "Embree speedup over the native CPU oracle" — the LKAU table already shows Embree at 0.085s vs. oracle at 5.14s (~60×). That is a striking number. The text around Figure 3 does not acknowledge or explain the magnitude. Readers will want to know why the oracle is so much slower (is it instrumented? debug mode?).

**Relationship to RayJoin (§7)**

- Honest and appropriately scoped. The four differences are a good enumeration.
- The artifact structure subsection (§7.2) is only a list of figure references — it reads as a table of contents, not analysis. Even one sentence on what the coverage achieves would improve it.

**Limitations (§8)**

- The explicitness here is commendable and correct. Naming the five deferred continent-scale families is exactly the right move for a reproducibility-conscious paper.
- The phrase "must not be erased in downstream summaries" is correct in intent but awkward in a formal paper. Replace with a neutral declarative: *"This scoping qualifier is material to interpretation."*

**Conclusion (§9)**

- Five sentences is lean for a conference conclusion. It correctly avoids overclaiming but also fails to summarize the key quantitative findings (row counts, exact parity, largest timing comparison). A reviewer reading only the abstract and conclusion will not come away knowing what was actually measured.
- No mention of future work — typical expectations for a conference conclusion include at least one forward-looking sentence (e.g., deferred dataset families, Vulkan maturation, overlay materialization).

---

### 3. Agreement and Disagreement

**Agreement:**
- The paper's core discipline — restricting claims to what the validated artifacts prove — is the right approach and is applied consistently throughout these sections.
- The overlay-seed contract definition is clear and its scope is honestly bounded in both Results and Limitations. This is well done.
- The distinction between "validated," "deferred-unavailable," and "not claimed" is a sound organizing principle; applying it explicitly in §5.3 is good methodology.

**Disagreement:**
- The paper treats the abstract's performance claim ("outperform PostGIS") as adequately supported by the Performance Interpretation discussion. It is not. The interpretation explains why the comparison involves different contracts, but the specific prepared-execution timing boundary where RTDL wins is never shown in the results. The claim exists in the abstract without a corresponding number anywhere in the paper. This is the most significant honesty risk in the document.
- The paper's conclusion frames the work as "a defensible baseline for subsequent workload expansion." That framing undersells the overlay-seed result, which is the first such validated four-system result reported. The conclusion could acknowledge what was actually achieved without overstating.

---

### 4. Recommended Next Step

**Priority 1 (near-blocking):** Resolve the abstract vs. PIP table contradiction. Either add a table row or clearly bounded footnote with the specific prepared-execution timing where RTDL beats PostGIS, or revise the abstract to remove the "outperform PostGIS" phrasing in favor of a scoped claim that matches what Table 2 actually shows (e.g., "*on the prepared-execution boundary, Embree and OptiX are competitive with PostGIS on the full-materialization contract*").

**Priority 2:** Add 1–2 sentences of textual interpretation for the scalability figures — what trend does the study confirm? Also explain the ~60× Embree-vs-oracle speedup on the overlay-seed case, or it will read as an unexplained anomaly.

**Priority 3 (editorial):** Expand the conclusion by 2–3 sentences: summarize the key quantitative results (row counts and parity, largest validated package, overlay-seed four-system result), and add one forward-looking sentence on the deferred dataset families or Vulkan path. Fix "must not be erased" phrasing in Limitations and "about 15 GiB" in Table 1.
