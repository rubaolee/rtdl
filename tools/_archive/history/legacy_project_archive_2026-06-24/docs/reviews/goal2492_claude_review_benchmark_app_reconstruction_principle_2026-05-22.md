**Verdict: APPROVE_WITH_NON_BLOCKING_NOTES**

---

### Assessment

**Reconstruction principle — sound and correctly bounded.**
Both documents use consistent language ("reconstruction instruments", "partial app slices are allowed", "success condition is the language/runtime design pressure extracted from the app"). The six pressure categories in Goal2492 match the README's enumeration (`missing RTDL primitive, memory contract, partner boundary, prepared execution model, or result contract`). The principle correctly rejects "add because it is interesting" without RTDL pressure. No issues here.

**App-agnosticism — well guarded.**
The Python/RTDL split in the minimal RayDB slice is explicit and clean: Python owns schema names, query names, SQL-like API, and paper-specific interpretation; RTDL owns only generic execution contracts. The non-goals explicitly block `raydb`, `sql`, `table`, and `database` vocabulary from Embree/OptiX implementation paths. The "What Recent Apps Already Forced" table phrases all results as generic primitives (e.g., "Generic grouped fixed-radius continuation"), not app product claims.

**RayDB scope — correctly bounded as RTDL pressure, not DBMS.**
The six database-shaped pressure points are genuinely about RTDL contract gaps (columnar descriptors, prepared-scene lifetime separation, declarative result modes), not about building a query optimizer or storage engine. Non-goals explicitly rule out SQL engine/DBMS claims and broad "general database engine" claims. The conditional guard on authors-code comparison ("until code is verified available and licensed") is exactly the right gate.

**Overclaims — none found.**
The existing-app table explicitly disclaims that apps are not claims to full GIS/DBSCAN/Hausdorff/collision products. The exit criteria are posed as open questions to be answered, not commitments to performance numbers. Goal2497 gates speedup claims behind a separate review.

**Goal2493–2497 sequence — reasonable.**
Intake → contract design → CPU reference → Embree → OptiX is the correct order. Goal2493's fallback ("if code not available, use synthetic fixture, no authors-code comparison") is the right safety valve. Goal2497's "pod available" precondition is properly conditional.

---

### Non-Blocking Notes

1. **Date stamp.** The document is dated 2026-05-22; today is 2026-05-21. Presumably intentional (staged for tomorrow), but worth confirming before it becomes the canonical artifact.

2. **"2-AI consensus" is undefined.** The consensus requirement section mentions "at least 2-AI consensus" without specifying what qualifies as a second AI, what form the review takes, or where the sign-off is recorded. If this roadmap becomes project-facing, that process should be tightened to avoid ambiguity.

3. **Exit criteria have no owner or time trigger.** The campaign exit criteria are well-posed questions, but there is no stated point at which the campaign is declared done if only Goal2495 (CPU reference) is completed and OptiX pods remain unavailable. A fallback closure condition ("campaign may close after Goal2496 if pod availability cannot be confirmed within N goals") would prevent indefinite open scope.

None of these block approval. The document is technically sound, app-agnostic, and correctly bounded.
