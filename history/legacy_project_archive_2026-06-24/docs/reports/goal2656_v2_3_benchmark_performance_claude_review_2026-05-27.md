## Review: RTDL v2.3 Benchmark-App Performance Appendix

---

### Criterion 1 — Numerical accuracy against source evidence

All 11 primary-row speedup values in the appendix match Goal2654 exactly. I verified each one:

| Row | Appendix | Goal2654 | Δ |
|---|---:|---:|---|
| Hausdorff | 3.29x | 3.29x | ✓ |
| Spatial RayJoin | 38.36x | 38.36x | ✓ |
| RT-DBSCAN | 12.71x | 12.71x | ✓ |
| Robot collision | 5.29x | 5.29x | ✓ |
| RayDB count | 27.67x | 27.67x | ✓ |
| RayDB sum | 104.00x | 104.00x | ✓ |
| Barnes-Hut | 4.55x | 4.55x | ✓ |
| LibRTS | 29.95x | 29.95x | ✓ |
| RTNN | 172.14x | 172.14x | ✓ |
| Triangle counting | 107.16x | 107.16x | ✓ |
| Bounded contact | 26.29x | 26.29x | ✓ |

The summary statistics (10 apps, 11 rows, 11/11, min 3.29x, median 27.67x, geomean 24.13x, max 172.14x) are all independently verifiable:

- **Median**: sorted 11 values, 6th element is 27.67x ✓
- **Geomean**: computed ln-sum/11 = 3.1834, e^3.1834 ≈ 24.14x ✓ (24.13x within rounding)
- **10 apps / 11 rows**: RayDB-style is one app with two distinct contracts ✓

**No numerical errors.**

---

### Criterion 2 — RayDB count/sum combination

The appendix handles this correctly. The executive summary explicitly says "11 primary comparison rows because RayDB has distinct grouped `count` and grouped `sum` contracts," and the table combines them into one cell as "27.67x count; 104.00x sum" with a boundary note that preserves both contracts distinctly. This matches Goal2655's compact-view design.

**One non-blocking issue:** A reader who counts table rows arrives at 10 and must read the executive summary prose to understand why the stat says 11. The table has no footnote pointing back to this explanation. The mismatch is not wrong but will cause reader confusion.

**Recommended fix:** Add a one-line note below the table:

```
RayDB count and sum are distinct primary rows in the statistics above;
combined here for compact display.
```

---

### Criterion 3 — Forbidden claim disciplines

The "What This Does Not Support" list in the appendix covers all nine forbidden categories explicitly:

- public speedup wording ✓
- whole-application speedup wording ✓
- author-code comparison claims ✓
- CUDA baseline victory claims ✓
- SQL/DBMS performance claims ✓
- full paper-reproduction claims ✓
- package-install support claims ✓
- true zero-copy claims ✓
- universal-input-shape claims ✓

The allowed wording paragraph is lifted word-for-word from Goal2655's approved "Correct Claim Shape" text. The incorrect-interpretation footnote in the executive summary is phrased slightly differently from Goal2655 ("or every input shape" vs. "or provides public benchmark speedups") but both are accurate and the appendix's phrasing is more complete.

**No forbidden claims found.**

---

### Criterion 4 — Release README update acceptability

The README was released 2026-05-25; the appendix is dated 2026-05-27. The Evidence section in the README was updated to add one line: `- [v2.3 benchmark-app performance appendix](benchmark_app_performance.md)`.

The appendix header correctly says "This is not a new release tag" and the README does not imply one. Adding an evidence link to a living release README is appropriate for a v2.3-family doc. The README status header ("released source-tree Python+partner+RTDL app-portfolio boundary") remains accurate since no new tag was cut.

**Acceptable as-is.** However, there is no note in the README that the appendix supersedes the prior benchmark table wording in the README body. The README's "Promoted Benchmark Apps" table still lacks performance columns (it only has contract/boundary), so there is no direct conflict — the appendix adds rather than contradicts. This is fine.

---

### Criterion 5 — Native-engine / app-boundary discipline

Every boundary cell in the appendix table correctly describes what the native engine does and explicitly excludes domain semantics:

- RT-DBSCAN: "No DBSCAN-native ABI; cluster semantics stay in app/partner code." ✓
- RayDB: "Generated 2M fixture, steady-state prepared-query phase only; no whole-app, DBMS, authors-code, or public claim." ✓ — this matches the Goal2653 3-AI consensus accepted claim verbatim
- Barnes-Hut: "Python owns opening decisions and force math; no native Barnes-Hut force ABI." ✓
- Contact witness: "Exact contact refinement remains app-owned; no collision/contact native ABI." ✓

The "What This Supports" prose confirms: "the native engine remains app-agnostic: app semantics stay in Python/partner code" (from Goal2655). The primitive naming (`generic_ray_triangle_primitive_grouped_i64_reduction_3d` in the RayDB closeout) is RT-shaped and app-agnostic by design.

**Fully disciplined.**

---

### Blocking Issue

**None.**

---

### Non-blocking Issues

**Issue A (required fix):** The appendix never states the measurement hardware. The accepted internal claim from Goal2653 explicitly includes "on the RTX A5000 pod." The application catalog states "NVIDIA RTX A5000 pod from commit `56e1f9b2...`." The appendix strips this qualifier, making the numbers appear hardware-independent. Anyone quoting these numbers from the appendix alone cannot attribute them to a specific platform.

**Required fix:** Change the executive summary stats line to:

```
Primary-row speedup summary: min 3.29x, median 27.67x, geomean 24.13x, max 172.14x
(measured on an NVIDIA RTX A5000 pod; see source evidence below).
```

**Issue B (recommended fix):** The table footnote on the count/sum row (issue from criterion 2 above). Not correctness-breaking but will confuse reviewers.

---

### Final Verdict: Accept with fixes

The appendix is accurate, internally consistent with all source evidence, and correctly disciplines every claim boundary. The two fixes are required before circulation:

1. **Add hardware qualifier** to the executive summary stats line (`RTX A5000 pod`).
2. **Add a one-line table footnote** explaining that RayDB count and sum are two primary rows in the statistics, combined for compact display.

No wording in the current draft crosses into forbidden territory. After those two edits, the document is acceptable as a v2.3-family internal performance appendix.
