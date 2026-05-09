## Verdict

**ACCEPTED.** No blockers found. The ledger correctly records RTX required-backend packet-execution evidence as satisfied and explicitly holds stable `COLLECT_K_BOUNDED` promotion blocked. No prohibited claims appear.

---

## Findings

**Ledger structure is sound.**
- Verdict section states "RTX PACKET EVIDENCE SATISFIED" and immediately blocks stable promotion pending a separate decision package and fresh 3-AI review — no ambiguity.
- Satisfied Evidence table qualifies the RTX row as "Satisfied as required-backend packet-execution evidence, not public speedup evidence" — the qualifier is in the cell, not just in the boundary section.
- Still-Blocking table names `v1_6_x_collect_k_stable_promotion_3ai_consensus` as "Not satisfied" with a clear reason.
- Claim Boundary paragraph enumerates all six prohibited claims: public speedup wording, true zero-copy wording, whole-app speedup claims, broad RTX/GPU wording, stable `COLLECT_K_BOUNDED` promotion, release tags/action.

**Underlying evidence is cited correctly.**
- Goal1620 report (`accepted_packet_execution`, all three required backends, no failed subpackages, timing diagnostic only) matches what the ledger records.
- Goal1620 3-AI consensus (Codex, Claude, Gemini all `ACCEPTED`, same claim boundary) is cited as the review artifact for the RTX row.

**Test suite validates all three invariants.**
- `test_ledger_marks_rtx_packet_evidence_satisfied` — checks verdict string, evidence-item key, qualifier phrase, and source file reference.
- `test_ledger_keeps_stable_promotion_blocked` — checks blocking text, evidence-item key, "Not satisfied", and "fresh 3-AI review".
- `test_ledger_claim_boundary_blocks_overclaiming` — checks all five prohibited-wording phrases including the raw-newline form of `` stable `COLLECT_K_BOUNDED`\npromotion ``, which matches the wrapped line in the actual report text.

No overclaiming language, no authorization of speedup/zero-copy/promotion/release, no wording drift between the ledger body and its claim boundary.

---

## Claim Boundary

The ledger is scoped to: RTX required-backend packet-execution evidence is satisfied for the v1.6.4 collect-k chain. It does not extend to any of the following, all of which remain explicitly blocked:

| Prohibited claim | Blocked in ledger |
|---|---|
| Public speedup wording | Yes |
| True zero-copy wording | Yes |
| Whole-app speedup claims | Yes |
| Broad RTX/GPU wording | Yes |
| Stable `COLLECT_K_BOUNDED` promotion | Yes |
| Release tags or release action | Yes |

---

## Recommendation

Ledger is acceptable as-is. No edits required. The next action, if the project intends to pursue stable promotion, is to create the separate stable-promotion decision package and request fresh 3-AI review — consistent with what the ledger and the Goal1620 consensus both specify.
