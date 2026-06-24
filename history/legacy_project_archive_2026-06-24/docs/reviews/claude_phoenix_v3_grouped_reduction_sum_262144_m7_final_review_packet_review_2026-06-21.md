I have now read all four primary files plus the raw JSON artifact, hardware gate, GPU env gate, and source manifest. Here is my full review.

---

## Review: Phoenix V3 `grouped_reduction_sum_scalar_broadcast_repeat100_262144` — M7 Qualification

### Verdict: **Option 1 — Approve as M7-qualified**, subject to two P0 conditions listed below.

The evidence is internally consistent, the wording is correctly row-scoped, and the exclusions are honest. This review constitutes the external public-row review that the packet's own blocker list requires. A second AI reviewer is still needed before the "2-AI consensus" blocker is cleared.

---

### Arithmetic Verification (raw artifact vs. packet)

All numbers verified against `grouped_sum_scalar_broadcast_repeat100_262144.json`:

| Metric | Artifact computation | Packet claim | Match |
|---|---|---|---|
| Hot query ratio | 1.0031111 / 0.0049409 = 203.022x | 203.022x | ✓ |
| Repeat-100 loop ratio | 100.50839 / 0.50166 = 200.353x | 200.353x | ✓ |
| Embree cold + loop | 1.71020 + 100.50839 = 102.219s | 102.219s | ✓ |
| OptiX cold + loop | 3.15985 + 0.50166 = 3.662s | 3.662s | ✓ |
| Cold+loop ratio | 102.219 / 3.662 = 27.917x | 27.917x | ✓ |
| Embree workload build | artifact field | 1.620s | ✓ |
| OptiX workload build | artifact field | 1.644s | ✓ |

No arithmetic errors. The cold + loop uses `cold_prepare_total_sec` (not `workload_build_sec`), which is correct — it counts full cold prepare, not just build.

---

### Evidence Quality Checklist

| Check | Result |
|---|---|
| Hardware gate passed | ✓ NVIDIA RTX 4000 Ada, compute cap 8.9, driver 550.127.05 |
| GPU env gate passed | ✓ cupy 14.1.1, numba 0.65.1, torch 2.6.0+cu124, all pass |
| Both backends match CPU reference | ✓ `matches_cpu_reference: true` in both rows |
| Same contract | ✓ |
| Partner continuation required | ✗ (false, as required) |
| App-specific native engine | ✗ (false, as required) |
| Scalar-broadcast optimization is generic | ✓ — changes only the ray packer, not a custom grouped-reduction primitive |
| Actual repeat=100, not modeled | ✓ — artifact shows `prepared_iteration_count: 100`, loop timing is measured |
| Cold prepare disclosed | ✓ — OptiX cold prepare 3.160s is shown alongside loop timing |
| 524,288-row excluded for honest reason | ✓ — 2.983x cold+loop is materially weaker; OptiX cold is 98.96s |
| Count rows excluded for honest reason | ✓ — break-even requires 14+ repeats |

---

### Wording Review

The draft public wording is correct as written:

> *For a fixed-schema prepared grouped-sum workload on an NVIDIA RTX 4000 Ada Generation pod, 262,144 rows / 1,024 groups, warmup=3 and actual repeat=100, RTDL's OptiX route was 200.353x faster than the Embree route for the measured 100-query prepared loop. Counting cold prepare once plus that measured loop, OptiX was 27.917x faster. This is a row-scoped grouped_reduction prepared-query result, not a whole-app, whole-database, or broad V3-over-V2 speedup claim.*

Every required qualifier is present: hardware, row count, group count, warmup, repeat count, loop timing vs. cold+loop timing, and the explicit scope disclaimer. No forbidden claims appear.

---

### P0 Items — Must Close Before Promotion

**P0-1: Source provenance gap (git_head is empty)**
The artifact's `environment.git_head` field reads `"fatal: not a git repository"` — the pod ran without git. Source provenance currently rests entirely on `source_manifest.sha256`, which hashes six specific files. That file exists and covers the relevant sources:
- `src/rtdsl/optix_runtime.py`
- `examples/current/research_benchmarks/raydb_style/rtdl_raydb_style_benchmark_app.py`
- `scripts/v3_0_m28_raydb_prepared_grouped_refresh.py`
- plus three gate scripts

The SHA-256 chain is cryptographically sound, but the promotion document must explicitly state that git HEAD is unavailable and that `source_manifest.sha256` is the sole source traceability record. Without that statement, a future reader cannot evaluate the provenance chain. This is a documentation fix, not a re-run requirement.

**P0-2: 2-AI consensus not yet recorded**
The packet's own blocker list requires 2-AI consensus. This review is one. The promotion cannot be finalized until a second AI reviewer records agreement (or disagreement) against this same packet. Do not flip `m7_promotion_authorized` to `true` on the basis of this review alone.

---

### Non-P0 Findings (cleanup, not blockers)

**Row ID inconsistency**: `phoenix_v3_grouped_reduction_sum_m7_candidate_wording_2026-06-20.md` names the row `grouped_reduction_sum_repeat100_actual_262144`, while the final review packet and tutorial both use `grouped_reduction_sum_scalar_broadcast_repeat100_262144`. The wording doc predates the scalar-broadcast optimization. The final packet name is correct; the wording doc should be updated to match before public promotion.

**Hit-event count discrepancy**: Embree reports 1,853 `hit_event_count_before_dedup`; OptiX reports 3,693. Both pass CPU reference, so the final sums are correct. The discrepancy is consistent with traversal-order differences between the two kernels before deduplication, not a correctness issue. It is worth a one-line note in the promotion doc acknowledging the difference is expected.

---

### Answers to the Three Questions

**1. Approve this exact 262,144 grouped_sum row as M7-qualified?**
**Yes** — the evidence warrants M7 qualification. This review closes the "external public-row review missing" blocker. Two conditions remain before the actual flag is flipped: document the git_head gap (P0-1) and obtain a second AI review (P0-2).

**2. Approve only as final-review candidate, not M7?**
No. Deferring to candidate status would be the right call only if the evidence had a material arithmetic error, a hidden cold-prepare cost, an app-specific native engine, or a correctness failure. None of those apply here.

**3. Reject as public-row evidence?**
No. The evidence is clean, honest, and stronger than the bar requires for a row-scoped prepared-query result.

---

### What Changes After This Review

- This review closes the "fresh external public-row review missing" blocker.
- `current_packet_external_review_status` can be updated from `blocked_current_packet` to `one_ai_review_complete_second_required`.
- All other flags (`release_authorized`, `m7_promotion_authorized`, `public_speedup_claim_authorized`) remain `false` until P0-1 (provenance note) and P0-2 (second AI review) are both closed.
- The 524,288-row sum and all count rows stay internal. That determination is confirmed.
