## Review of Results, Relationship to RayJoin, Limitations, and Conclusion

---

### 1. Verdict: APPROVE-WITH-NOTES

---

### 2. Findings

**Results (§5)**

- Table 1 correctly presents three distinct boundary rows (prepared, best-repeated, first-call) with separate PostGIS ranges per row and individual backend readings. The data is internally consistent: Embree (1.04–1.44s) and OptiX (2.13–2.54s) both beat PostGIS (3.02–3.40s) on prepared; same pattern holds on best-repeated. Vulkan (6.14–6.16s) is unambiguously slower on all rows.
- §5.5 Performance Interpretation is precise and correct: it explicitly restricts the "both beat PostGIS" claim to prepared and runtime-reuse-benefited repeated calls, and calls out that OptiX and Vulkan still pay cold-start cost on first call (7.05s and 16.14s, both above PostGIS).
- The bounded-package-as-trust-anchor framing (§5.2) is well-placed and does not compete with the long-surface performance story.

**Relationship to RayJoin (§6)**

- The scoping is honest and accurate. The section does not overclaim reproduction; it positions RTDL as asking a different question (DSL+multi-backend expressibility, not paper-identical rerun).
- Artifact structure list (§6.2) correctly names the five covered surfaces and ties them to their RayJoin figure/table analogues.

**Limitations (§7)**

- All five deferred continental families are enumerated. The Block⋈Water substitute qualifier is present. The "only LKAU has four-system overlay" qualifier is present. The Vulkan scope qualifier ("not part of the paper's main performance claim") is explicit and correct.

**Conclusion (§8)**

- The key sentence — *"Embree and OptiX now outperform PostGIS on the reported prepared and repeated-call boundaries, while Vulkan remains parity-clean but slower"* — is accurate. The bounded-package trust-anchor role and hash-level row agreement are both cited.

---

### 3. Agreement and Disagreement

**Agreement (all of the following hold):**
- Embree and OptiX faster than PostGIS on prepared-exact-source boundary: **confirmed by table**.
- Embree and OptiX faster than PostGIS on best-repeated boundary: **confirmed by table**.
- Vulkan parity-clean but slower on the same surface: **confirmed in table and repeated in §5.5, Limitations §7 fourth item, and Conclusion**.
- Bounded package is trust anchor (not superseded, still referenced): **confirmed in §5.2 and Conclusion**.
- Cold-start asymmetry (OptiX/Vulkan vs. Embree on first call) is disclosed, not hidden: **confirmed in §5.5 and Table 1 row 3**.

**Disagreement / precision gap (one note):**

The Conclusion states *"Embree and OptiX now outperform PostGIS on the reported **prepared and repeated-call** boundaries."* The phrase "repeated-call boundaries" is technically ambiguous: it could be read as covering both the best-repeated and first-call rows. §5.5 is more careful ("once repeated raw-input execution benefits from runtime-owned reuse"), making clear the claim applies to best-repeated only. The Conclusion does not include the matching qualifier. This is not a factual error — the first-call row is a separate boundary and the Conclusion could be read as only referring to the rows where the claim holds — but a reader skimming the Conclusion without the table could over-read it as a universal repeated-call win including first call.

---

### 4. Recommended Next Step

**One targeted Conclusion edit.** Change:

> *"Embree and OptiX now outperform PostGIS on the reported prepared and repeated-call boundaries"*

to:

> *"Embree and OptiX now outperform PostGIS on the reported prepared-execution and best-repeated-call boundaries"*

This closes the ambiguity with the first-call cold-start row without changing any other claim. No other changes are needed; all four sections are otherwise consistent with the accepted backend state.
