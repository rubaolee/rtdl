Here is the formal review.

---

## RTDL Goal2621 Follow-Up Promotion Review

**Date:** 2026-05-25
**Reviewer:** Claude (claude-sonnet-4-6)
**Role:** Follow-up consensus review, explicitly called for by `goal2621_bounded_contact_witness_collect_k_3ai_consensus_2026-05-25.md`

---

### Verdict

| Question | Decision |
|---|---|
| Promote app from candidate to promoted benchmark? | **APPROVE** |
| Promote `COLLECT_K_BOUNDED` from experimental to stable? | **APPROVE** with one recorded gap (Linux Embree) |

---

### Boundary Assessment

The engine boundary is clean. Specific findings:

1. Native symbols called are `rtdl_{embree,optix}_collect_k_bounded_i64` — generic, not collision-specific. No `collect_shape_pair_candidates_bounded` or any domain-name variant is present. The static source test (`test_app_source_does_not_call_collision_specific_native_symbols`) verifies this by inspecting live app source.
2. `engine_boundary["native_collision_logic_allowed"] = False` is enforced in code and reflected in every native payload.
3. The candidate oracle is passed as `candidate_source_symbol="python_exact_triangle_intersection_oracle"` — the oracle is app-owned Python, not engine logic.
4. Contact summaries (centroid midpoints) are computed in Python *after* row collection (`app_owned_contact_summaries`), with `"owner": "python_app_contact_summary_not_native_engine"` in the output. No contact-manifold geometry is computed inside RTDL.
5. `claim_boundary` annotations are present on all six payload modes and correctly state that no native collision/RT-core claim is being made.

No native collision, contact, manifold, or physics semantics were found inside engine code. The boundary is correctly maintained.

---

### Evidence Assessment

| Gate | Status | Key Evidence |
|---|---|---|
| Deterministic Python fixtures | PASS | 8 tests pass; tiny rows `((0, 10, 0), (0, 11, 1), (2, 30, 2))` match expected |
| Fail-closed overflow | PASS | Python path and OptiX native path both raise `partial_result_returned=False`; rc=1 confirmed in pod JSON |
| Local Embree parity (Mac) | PASS | `librtdl_embree.dylib`; symbol `rtdl_embree_collect_k_bounded_i64`; rows match CPU oracle on tiny and grid |
| RTX A5000 OptiX parity (Linux pod) | PASS — JSON-confirmed | tiny: `valid_count=3`, `matches_cpu_reference=True`; grid-512: `valid_count=512`, `matches_cpu_reference=True`; build rc=0, CUDA 12.8, driver 570.211.01 |
| Standalone C++ CPU baseline | PASS | grid-512 on pod: `elapsed_sec=0.0232454`, `valid_count=512`, `matches_cpu_reference=True`; no RTDL calls in baseline binary |
| Unit test suite (pod) | PASS | 8 tests, 0 failures, 1 skip (Embree library absent on pod — expected and correct) |
| Linux Embree parity | **NOT DONE** | Embree validated on Mac only; pod had OptiX only. Mac Embree + Linux OptiX covers both platforms jointly, but not Linux Embree directly |
| 3-AI follow-up consensus | **THIS REVIEW** | Prior consensus explicitly deferred to "a final promotion review" after C++ baseline, Embree evidence, and pod OptiX evidence exist together |

The pod JSON evidence (`goal2621_contact_manifold_optix_pod_evidence_2026-05-25.json`) is the authoritative record. All stated promotion gates from `scope_payload()["promotion_gates"]` are closed. The Linux Embree gap is a qualification to be documented in the stable primitive entry, not a blocking condition: the generic symbol, fail-closed overflow contract, and row schema are independently verified on two backends across two platforms.

---

### Required Fixes

The following file changes must accompany any promotion commit. No other changes are needed; the code itself is correct.

1. **`rtdl_contact_manifold_benchmark_app.py:57`** — Change `scope_payload()["status"]` from `"benchmark_candidate_until_backend_parity_and_3ai_consensus"` to promoted wording (e.g. `"promoted_benchmark"`).

2. **`docs/application_catalog.md`** — Move the contact-manifold row from the "Candidate Benchmark Apps" table into the "Promoted Benchmark Apps" table. Remove the "follow-up promotion consensus remains" text from the blocking-gates description.

3. **`docs/rtdl_primitive_catalog.md`** — Change `COLLECT_K_BOUNDED` status cell from "Experimental primitive" to "Stable primitive". Update the boundary note to record the Linux Embree gap as a documentation qualification rather than a blocking gate.

4. **`examples/v2_0/research_benchmarks/contact_manifold/README.md`** — Remove or rewrite the "Promotion State" section's candidate-only gate language.

5. **`docs/reports/goal2621_bounded_contact_witness_collect_k_3ai_consensus_2026-05-25.md`** — Append a follow-up section that records this promotion decision, cites the pod JSON evidence file and C++ baseline, and explicitly authorizes promoted benchmark wording. Do not rewrite the prior consensus; append.

6. **`tests/goal2621_contact_manifold_collect_k_bounded_benchmark_candidate_test.py`, `test_docs_record_candidate_not_promoted_boundary`** — This test asserts candidate strings (`"Accepted as a benchmark candidate only"`, `"Promoted benchmark wording is not authorized yet"`, `"follow-up promotion consensus remains"`) that will change after promotion. The test must be updated or replaced with a `test_docs_record_promoted_boundary` test asserting the promoted catalog strings. Failing to update this test will cause the suite to fail after the promotion commit.

---

### Final Recommendation

**App promotion: APPROVE.** All six gates in `scope_payload()["promotion_gates"]` are now closed. The contract is correct, the boundary is clean, and the RTX A5000 pod evidence (JSON-confirmed, CUDA 12.8, Linux, rc=0) combined with local Embree and standalone C++ baseline satisfies the evidence standard for a promoted benchmark app. This review is the follow-up 3-AI consensus.

**`COLLECT_K_BOUNDED` → stable: APPROVE with noted gap.** The primitive has app-independent semantics, typed i64 row schema, exact fail-closed overflow, backend lowering on two execution paths, correctness tests, and parity evidence across two platforms. Record in the stable entry that Linux Embree parity is unverified; Mac Embree and Linux OptiX together cover the surface, but not the exact cross. This gap does not block stable status but must be documented.

**No speedup claims authorized.** The timing data in the pod evidence (OptiX grid-512 native at 2.2 ms, C++ baseline at 23 ms, Python oracle at 9 s on the pod) is benchmark plumbing, not a public performance claim. The existing `claim_boundary` annotations on each payload mode are sufficient and must be preserved after promotion.
