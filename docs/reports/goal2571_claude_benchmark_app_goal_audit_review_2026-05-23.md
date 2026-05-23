I now have a complete picture from all the primary documents. Let me write my independent audit review.

---

# Goal2571 Independent Audit Review — Claude

**VERDICT: ACCEPT-WITH-BOUNDARY**

No blocker prevents treating the current internal benchmark-app snapshot as closed. All required review and consensus debts from the Goal2392–Goal2570 sequence are either satisfied or correctly reclassified as compatibility or future-work items. The specific questions raised in the audit brief are answered below, followed by the constraints that must travel with this verdict.

---

## 1. Goal2491 Robot 2-AI Debt — Closed

Goal2491 explicitly required "at least 2-AI consensus before final project closure." Goal2529 satisfied this with a 3-AI consensus (Codex, Claude, Gemini) that classified robot-collision as a finished sampled static-scene feasibility-screening benchmark and adopted explicit claim boundaries. The stronger coverage (3-AI ≥ 2-AI) is unambiguous closure. The cross-app debt ledger in the audit records this correctly as "Closed / Goal2529 3-AI consensus."

No residual debt here.

---

## 2. Barnes-Hut Goal2550 — Covered by Goal2551 3-AI Consensus

Barnes-Hut was promoted after Goal2529 was run, so it is correctly absent from Goal2529's coverage table. The audit acknowledges this explicitly and correctly points to Goal2551 as the covering consensus. Goal2551's three participants (Codex, Gemini, Claude) all:

- accepted Goal2549's rejection of native inverse-square force math;
- agreed the next acceptable engine target is a math-agnostic frontier/traversal primitive;
- agreed that further benchmark-specific tuning is not the right next step.

Goal2550 itself closes with a claim boundary that blocks public speedup wording, same-contract authors-code comparison, and native Barnes-Hut primitives. Critically, the "orientation" timing row (RTDL-side `0.502848 ms` vs. authors `new`-mode `5.405 ms` on the same RTX A5000) appears in the closeout alongside an explicit statement that it "must not be presented as an apples-to-apples speedup." That boundary is visible in the documented artifacts and the evidence manifest.

One ongoing constraint: the authors `treelogy` mode segfaulted on same-input reload, so no same-contract performance comparison is possible. The audit records this correctly as a non-debt deferral. Future work referencing Barnes-Hut must treat the two timing rows as orientation-only, not as a performance ratio.

---

## 3. Goal2551 Findings — Addressed or Properly Deferred

The Goal2551 consensus raised six main findings. Their current status:

| Finding | Priority | Disposition | Evidence |
|---|---|---|---|
| Capacity/overflow contract gap in `_with_capacity` APIs | P0 | **Fully addressed** | Goal2552 adds `overflowed_out`, fail-closed policy, Python raise-on-overflow |
| DB/DBSCAN-shaped internal naming in active OptiX/Embree | P0 | **Addressed for active implementation names** | Goal2553 renames `DbScan*` → `ColumnarPredicateScan*`; Goal2554 renames `RtdlDb*` types in impl code; `RtdlDb*` prelude aliases preserved as compatibility layer |
| App-specific adapters in shared `partner_adapters.py` | P1 | **Fully addressed** | Goal2562 moves robot adapter; Goal2563 moves Barnes-Hut inverse-square adapter; top-level `rtdsl` exports preserved for compatibility |
| Columnar partner wording was RayDB-shaped | P1 | **Addressed** | Goal2561 |
| Device column descriptors fragmented | P1 | **Partially addressed** | Goal2565 adds `DeviceColumnDescriptor` for input columns; output-buffer descriptors remain future work |
| Grouped-reduction machinery fragmented | P1 | **Partially addressed** | Goal2567–2569 add shared Python contract layer, operation tokens, fail-closed capacity status; full native migration remains future work |
| Evidence manifest | P2 | **Addressed** | Goal2566 + Goal2570 refresh |

The two "partially addressed" P1 items are documented as incomplete and carry explicit boundaries that prohibit external ABI stabilization claims. This is an appropriate disposition for an internal snapshot: the Python substrate contracts exist, the migration path is defined, but the claim boundaries correctly do not extend to native backend stability.

One note on P0 naming: Goal2553's boundary statement is precise about what was NOT renamed — `RtdlDbField`, `RtdlDbScalar`, `RtdlDbClause`, `RtdlDbGrouped*Row` remain as prelude-only compatibility aliases, and `DbPrimaryAxis`, `DbRowBox`, and `kDb*` helpers in implementation details remain for a future migration slice. The audit's debt ledger characterizes this as "Addressed for active implementation names," which is the right qualifier. The public ABI rename remains an open forward P0 item before any external ABI stabilization.

---

## 4. Compatibility DB-Shaped Aliases — Correctly Treated as Compatibility Debt

The audit has a dedicated "Compatibility Debt Versus Review Debt" section and correctly separates these two categories. The following surfaces carry the DB vocabulary as accepted compatibility aliases, not open review debt:

- `RtdlDb*` prelude aliases in native headers (Goal2554)
- Python ctypes `_RtdlDb*` / `_DB_KIND_*` / `_encode_db_*` names, with generic aliases added alongside (Goal2558)
- Python `db_*` user-facing mode strings in routing and wrappers (Goal2557)
- Top-level `rtdsl` exports of moved app adapters for compatibility (Goal2562, Goal2563)
- Native C symbol names (not renamed)

Goal2558 is the key compatibility report: it adds generic columnar aliases (`_RtdlColumnField`, `_COLUMN_KIND_*`, `_encode_columnar_*`, etc.) while explicitly preserving the legacy names for "older tests and wrappers." The test verifies that each generic alias points to the same object as the legacy name. This is proper alias-layer hygiene.

The boundary condition that must travel with these aliases: they do not authorize ABI stability, external ABI stabilization claims, or any claim that the compatibility surface is app-name-free.

---

## 5. Performance and Release Claims — Not Over-Authorized

Every reviewed report and closeout explicitly limits performance language. Spot-checks:

- Goal2491 (robot): "internal exact-subpath ratios only… not authorized for public speedup claims"
- Goal2550 (Barnes-Hut): "No public speedup ratio is authorized. No same-contract authors-code comparison is authorized."
- Goal2529 (consensus): "This consensus does not authorize release tagging, package-install support, full paper reproduction claims…"
- Goal2551 (consensus): "Not approved: public release wording; broad speedup wording; external ABI stability claims"
- Goal2566/2570 (manifest): "does not authorize public release wording, speedup claims, true zero-copy claims, or new native backend support"

The evidence manifest test explicitly validates that `public_speedup_authorized` and `native_app_specific_abi_authorized` flags remain false for every benchmark app entry. This is a machine-checkable boundary.

No report contains a public speedup claim, author-code parity claim, paper reproduction claim, or SQL/DBMS/robot-solver claim.

---

## 6. Remaining Observations

**Native GPU validation gap for Goal2552**: The overflow contract change is validated locally (31 tests pass) but Goal2552's own boundary notes "Native GPU validation is still required before treating this ABI revision as externally consumable." This is correctly scoped to the internal snapshot and does not block internal closure, but it must not be presented as an externally stable ABI change until that validation runs.

**Goal2571 self-review completeness**: The audit's own ledger marks "Post-cleanup audit itself needs independent review" as pending. At the time this review is written, only a Codex preliminary verdict and this Claude review exist as Goal2571 artifacts. A Gemini review artifact does not yet appear in the repository. The audit's stated intent is to add both Claude and Gemini reviews as artifacts. Until the Gemini review is added, the three-party coverage for the audit itself is incomplete, though this does not block the internal snapshot since the audit is scoped as internal-only.

---

## Verdict and Constraints

**ACCEPT-WITH-BOUNDARY**

The following constraints apply to any use of this audit as authorization:

1. **Internal snapshot only.** The internal-benchmark-apps-2026-05-23 label is appropriate. No public release wording, public speedup wording, or external ABI stability claim is authorized by this audit.

2. **No public speedup claim from Barnes-Hut orientation timings.** The RTDL `0.502848 ms` vs. authors `5.405 ms` figures must not be presented as a same-contract speedup ratio. The authors same-input `treelogy` mode segfaulted; the two rows are not comparable under a common contract.

3. **RtdlDb* public ABI rename remains an open forward P0.** Before any external ABI stabilization is claimed, the prelude-only `RtdlDb*` aliases must be promoted through a staged alias/deprecation migration with explicit source-purity test coverage.

4. **Goal2552 overflow contract requires native GPU validation** before the revised `_with_capacity` ABI is described as externally consumable.

5. **Partial P1 substrate work is not an ABI stability claim.** `DeviceColumnDescriptor` and `rtdl.grouped_reduction.v1` are internal Python contract layers. Output-buffer descriptors and full native-path migration remain future work.

6. **Gemini review for Goal2571 itself is still pending** as of this review. The audit is internally self-consistent, but the three-party review of the audit record is not yet complete.
