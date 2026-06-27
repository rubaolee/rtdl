---

## Review Findings

### Finding 1 — **Significant: Figure 13 / 14 synthetic input type is never disclosed**

The provenance document (`rayjoin_paper_dataset_provenance.md`, line 106) is explicit:

> "Figure 13 and Figure 14 are now supported through a **scaled synthetic Embree analogue** rather than through the original paper-scale inputs."

The goal23 report classifies all Figure 13/14 inputs as `synthetic-input`. The difference report under review never states this. Specifically:

- Section 3's Figure 13/14 row says only "Same structure, different scale and environment."
- Section 6 ("Scale Differences") lists the exact profile sizes (R=100000, S=100000–500000) but calls them "bounded local analogue" with no mention that the geometry is randomly generated.
- Section 7 ("Workload Fidelity") names lsi/pip as "the strongest parts of the current RTDL reproduction effort" without qualifying that the Figure 13/14 runs are on synthetic data, not derived or real geographic inputs.

The cumulative effect: the first author will likely assume Figure 13/14 were run on real or derived geographic data. They were not. This is the one case where the report risks misleading by omission.

---

### Finding 2 — **Minor: "raw and prepared raw are close to native" collapses two different paths**

Section 8 states: "RTDL `raw` and `prepared raw` paths are close to native for `lsi` and `pip`."

From Goal 19 at fixture scale: `raw` for `pip` is 1.82x slower than native — not really "close." It is `prepared raw` that achieves close parity (0.85x). At the larger profile both converge well. The claim is directionally defensible but imprecise. A careful author will ask which path was used in Goal 23 (answer: `prepared raw`). The report should say "prepared raw" is close, not lump raw in.

---

### Finding 3 — **Minor: "Python-like DSL" vs "Python-hosted DSL"**

The goal23 report and other internal docs consistently say "Python-hosted DSL" (an embedded DSL hosted within Python). The difference report uses "Python-like DSL" (implying syntactic resemblance). For the RayJoin first author, who will likely probe the implementation, this distinction matters: is RTDL a new language, or a Python EDSL? This should be consistent with the companion documents they may read alongside this memo.

---

## Suggested Revisions

**For Finding 1** — In Section 6 ("Scale Differences"), add a sentence under the profile bullet points:

> These runs use **synthetic-input geometry** (randomly generated polygons and points), not derived or exact-input geographic data. This is labeled `synthetic-input` in the companion Goal 23 report.

Also add "synthetic-input" to the Figure 13/14 row of the Section 3 difference table, e.g.:

> Bounded local analogue; **synthetic-input geometry**; different scale and environment

**For Finding 2** — In Section 8, revise to:

> RTDL **prepared raw** path is close to native for `lsi` and `pip`; the `raw` path is within ~2x at small scale and converges at larger scale.

**For Finding 3** — Change "Python-like DSL" to "Python-hosted DSL" throughout, to match the goal23 report and avoid implying a separate language.

---

## Final Decision

**Approved with revisions**

The report's overall posture is honest and admirably cautious. The "what we cannot claim" sections are clear and well-organized. But the synthetic nature of Figure 13/14 inputs is a factual gap that must be disclosed before this goes to the first author — omitting it is the one place where a careful reader could be inadvertently misled about dataset fidelity.
