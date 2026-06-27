**RTDL v1.3 Primitive ABI and Lowering Contract — Architecture Review**

---

## Verdict: ACCEPT

The draft is architecturally consistent with the Goal1255 consensus and the Goal1273 validated evidence. No blocking issues found.

---

## Question-by-Question Analysis

**Q1 — Primitive set and REDUCE split**

The draft preserves the exact Goal1255/Goal1042/Goal1227 primitive set: `ANY_HIT`, `COUNT_HITS`, `REDUCE_FLOAT(MIN|MAX|SUM)`, `REDUCE_INT(COUNT|SUM)`, and `COLLECT_K_BOUNDED` experimental-only. The split into individually typed rows per dtype/op is strictly correct. The rationale given — "a single untyped REDUCE bucket hides result shape, tolerance, overflow, grouping, and determinism requirements" — is sound and adds clarity the roadmap consensus didn't require but clearly intended. No deviation detected.

**Q2 — Backend freeze discipline**

The draft is fully compliant. The purpose section, the ABI contract table (`backend: embree or optix for active v1.3/v1.4 work`), and the boundary section all independently state the Vulkan/HIPRT/Apple RT freeze. Active engineering scope is limited to Embree and OptiX with NVIDIA performance as the top priority. This matches Goal1255 verbatim.

**Q3 — Per-app lowering matrix fidelity and overclaim avoidance**

All four rows trace cleanly to Goal1272/Goal1273 evidence:

| Row | Evidence match | Exclusion discipline |
|---|---|---|
| `graph_analytics.visibility_edges` | `ANY_HIT` + `COUNT_HITS`/`REDUCE_INT(COUNT)` maps to the prepared-repeat tens-of-microseconds finding | BFS, triangle counting, graph DB, frontier ops correctly excluded |
| `database_analytics.sales_risk` | `COUNT_HITS`/`REDUCE_INT(COUNT)` over numeric predicate maps to compact-summary warm-query result with `row_materializing_operation_count=0` | SQL, DBMS, broad DB, row-materializing output excluded |
| `polygon_pair_overlap_area_rows` | `ANY_HIT` candidate discovery + deferred `REDUCE_FLOAT(SUM)` correctly reflects the two-phase finding; conservative candidate upper-bound mismatch remains explicit | Exact-area continuation stays app-specific pending generic float reduction contract |
| `polygon_set_jaccard` | Correctly remains `optix_still_slower_with_reason`; `ANY_HIT` + experimental `COLLECT_K_BOUNDED` + deferred `REDUCE_FLOAT(SUM)` | Chunk policy, pair collection, exact/native continuation remain diagnostic — wording expansion explicitly blocked |

No overclaims. Public wording forbidden-wording list is specific and correctly prevents the common failure modes (whole-app acceleration, bare `--backend optix` as proof, internal intake treated as release evidence).

**Q4 — Gate sufficiency**

The migration gate table is thorough and the ordering is correct: contract → parity → phase → performance → wording → review. Specific assessments:

- *Parity gate*: CPU oracle + Embree + OptiX triple-comparison is the right standard. Tolerance-based parity for float reductions with declared absolute/relative tolerance and NaN policy is appropriate.
- *Phase gate*: prepare / traversal / reduction / copyback / output-pack separation is exactly what Goal1273's findings require (preparation and packing dominate wall time, not the query itself).
- *Performance gate*: requiring generic primitive to be performance-neutral or documenting an accepted overhead is correct and not too strict.
- *v1.4 readiness criteria*: explicitly lists all five v1.3 acceptance items that must be met before migration starts. This is sufficient to prevent premature refactoring.

The `one_shot` / `prepared` execution shape distinction is mandatory for v1.5 review — correct, directly supported by the Goal1273 evidence that prepared repeat is the differentiating path.

**Q5 — Blocking fixes**

None. The draft is architecturally sound.

---

## Non-Blocking Suggestions

1. **Quantify "performance-neutral" in the performance gate.** "At least performance-neutral" is directionally correct but leaves acceptance margin undefined. A concrete bound — e.g., within 10% of app-specific continuation median, or an explicit accepted overhead ratio with sign-off — would make the gate mechanically reviewable rather than judgment-dependent.

2. **Add a `retained_scale_range` field to the ABI contract.** The v1.2 evidence is scale-specific (30k/60k graph, 100k/300k DB, 40k–160k polygon). The current contract declares dtype and tolerance but not the scale domain over which parity must hold. A declared scale range per plan would prevent future plans from narrowing to a cherry-picked point.

3. **Clarify scene vs. probe reuse semantics in `prepared_state`.** The field currently states "whether scene/build data, probe buffers, or both are reusable." Goal1273 shows the scene is the expensive frozen state and probe buffers are the per-query variable. The contract would be stronger if it required explicit declaration of which buffer class is frozen and under what immutability constraint (same geometry, same BVH, etc.).

4. **NaN policy declaration scope.** `precision_policy` requires a NaN policy but doesn't specify minimum coverage (NaN propagation behavior, NaN-as-input behavior, and whether NaN in a reduction is an error or treated as identity). A one-sentence minimum coverage requirement here would prevent under-specified plans.

---

## Rationale

The draft's primary purpose is to translate v1.2 evidence into contracts that gate v1.4/v1.5 implementation. It succeeds: the primitive set matches the accepted roadmap, the per-app lowering matrix is grounded in actual measured evidence rather than aspirational claims, the backend freeze is consistently applied, and the v1.4 readiness criteria close the loop with an explicit acceptance dependency. The non-blocking suggestions would make individual plans more mechanically reviewable but do not undermine the contract's architecture or boundary discipline.

**ACCEPT** — v1.4 compatibility-wrapper planning may begin once 3-AI consensus on this contract is obtained per the boundary section's requirement.
