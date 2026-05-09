---

## Independent Review: Goal 1601 — v1.6 Release-Surface Proposal

**Reviewer role:** Independent RTDL release/architecture reviewer
**Review scope:** Proposal artifact safety, not release authorization

---

### Verdict

**ACCEPT** — as a release-surface planning artifact and the first formal external-review gate artifact for v1.6.

This is not, and does not purport to be, a release authorization. The proposal is safe to record in the project history at this stage.

---

### Architecture Boundary

The architecture framing is clear and correct:

- **Python = app/control layer.** Not optimized by RTDL; not claimed to be optimized.
- **RTDL = RT-shaped primitive contract + bridge to native Embree/OptiX.** Correctly limited to reviewed subpaths, not whole-app or arbitrary Python.
- **Backend distinction maintained.** "Embree and OptiX as the active Python+RTDL closure backends" is followed immediately by the pending/excluded exclusion of "Claims that every `--backend optix` run is a NVIDIA RT-core speedup." These two must remain coupled in any downstream artifact — the included-surface wording could be misread in isolation if the exclusion block were stripped.
- **App-leakage concern present.** The exclusion of "Claims that native internals are fully app-agnostic if compatibility/proof paths with app-shaped names or semantics remain" is the right guard, and it calls out the leakage gate by name as a required closure step. Good.

No architecture boundary overclaim found in this proposal.

---

### Performance Strategy

The framing is accurate and appropriately non-diluting:

- "Architecture anchor, not a performance freeze" — correct and explicit.
- Top priorities listed correctly: OptiX/RT-core primitive execution, `COLLECT_K_BOUNDED` optimization and promotion analysis, host/device data movement reduction, true zero-copy proof or rejection with measured hardware evidence, Embree as CPU same-contract fallback/baseline.
- The critical line "No future performance claim should be broadened merely because `v1.6` exists" is present and explicit. This is the key anti-dilution guard.
- "Each claim still needs exact-subpath evidence and external review" — correctly restates the standing evidence standard.

No performance deprioritization or freeze language found. Performance strategy is sound.

---

### Overclaim Check

Checking all prohibited claims from the review context:

| Prohibited claim | Blocked? | Where |
|---|---|---|
| Release authorization | Yes | Verdict, Claim Boundary |
| Release tag action | Yes | Claim Boundary |
| Public speedup wording | Yes | Pending/Excluded, Claim Boundary |
| True zero-copy wording | Yes | Pending/Excluded, Claim Boundary |
| Partner support claims | Yes | Pending/Excluded, Claim Boundary |
| Package-install claims | Yes | Pending/Excluded, Claim Boundary |
| Stable `COLLECT_K_BOUNDED` promotion | Yes | Pending/Excluded, Claim Boundary |
| Broad RTX/GPU acceleration wording | Yes | Claim Boundary |
| Whole-app speedup | Yes | Pending/Excluded, Claim Boundary |
| DLPack/partner tensor handoff | Yes | Pending/Excluded |
| Every `--backend optix` run = RT-core speedup | Yes | Pending/Excluded |

No overclaims found. The dual-location blocking (Pending/Excluded + Claim Boundary) is stronger than a single exclusion would be.

One non-fatal tension to track: The Included Surface lists "Embree and OptiX as the active Python+RTDL closure backends" without an inline caveat. If this section is ever quoted in isolation (e.g., a partner summary), the RT-core scope limitation is invisible. Recommend the final release package always cite the full Pending/Excluded list alongside the Included Surface, never one without the other.

---

### Required Fixes

None that block ACCEPT of this artifact. Two items to carry forward:

1. **Included Surface coupling risk (low, non-blocking).** Add a forward reference in the Included Surface section to the Pending/Excluded section — something like "See Pending/Excluded for required scope limitations on the OptiX backend claim." This prevents any downstream excerpting from orphaning the included list from its exclusions.

2. **Test fragility (low, non-blocking).** The test suite uses phrase-matching against normalized whitespace. This is appropriate for policy enforcement but will silently pass if language is weakened through synonym substitution rather than deletion. Consider adding at least one negative-phrase test that asserts no "authorizes" or "approves" language appears in the proposal, as a regression guard.

3. **Closure gate evidence files (tracking, not blocking).** The Required Evidence section references six specific files. None of those paths were verified as existing in this review. Before any closure gate is ticked, each referenced artifact must be confirmed present and reviewed. The app-leakage audit and docs overclaim audit gates are the two highest risk — they are not satisfied by this proposal.

---

### Recommendation

**Accept Goal 1601 as the formal v1.6 release-surface proposal artifact.** Record it as the first external-review gate artifact in the v1.6 closure sequence.

**Do not publish v1.6.** This proposal explicitly does not authorize publication and lists ten closure gates that remain open, including the docs overclaim audit, stable native-path app-leakage audit, Linux/Windows source-tree validation, real NVIDIA OptiX validation for the claimed surface, final 3-AI consensus, and explicit user authorization for any release or tag action.

The next required step per the proposal's own gate sequence is: public docs overclaim audit and stable native-path app-leakage audit.
