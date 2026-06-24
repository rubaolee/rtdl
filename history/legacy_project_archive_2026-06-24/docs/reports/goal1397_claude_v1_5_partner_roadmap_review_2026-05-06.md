**Verdict: ACCEPTABLE**

**Why it passes:**

All five named constraints are explicitly honored within the document:

1. **v1.0 immovability** — The proposal does not touch `v1.0`, does not retag it, and doesn't reference it except to preserve it. No conflict.

2. **Source-tree usage only** — Preserved verbatim: `PYTHONPATH=src:. python ...`; packaging/install claims are listed as non-goals.

3. **Public speedup wording gated on evidence/review** — The proposal requires "fresh evidence and required review" for any promoted speedup wording; broad whole-app speedup is explicitly a non-goal. This is stricter than the prior Goal1394 primitive-only constraint, not weaker.

4. **Vulkan/HIPRT/Apple RT frozen before v2.1** — Preserved exactly; the proposal adds "except for preserving existing proof surfaces," which is consistent with Goal1395/Goal1396 wording.

5. **No v1.5 tag from primitive-only readiness** — Stated unambiguously: "do not tag `v1.5` from the current primitive-only state."

**Handling of prior reports is correct:**

- Goal1395's "ready for release" conclusion is correctly downgraded to *prerequisite evidence only*, not invalidated. The primitive packet stays as a required artifact, not a sufficient one.
- Goal1393 and Goal1394 consensus are correctly scoped as valid for the primitive packet and carried forward, not voided.

**Known risk, properly disclosed:**

The scope expansion is real — v1.5 now requires `COLLECT_K_BOUNDED` resolution, app migration matrix, per-app Embree/OptiX benchmark suites, and support/maturity matrix. Codex flags this in the document itself. This is the project owner's deliberate decision and is gated by explicit new completion requirements before any tag action.

**Required fixes: none.** The following warrant attention but are not blocking:

- The v2.0 redefinition (from "broader runtime/performance architecture" to "partner-ready RTDL") is a material target change. If v2.0 has been communicated externally under the prior meaning, that external communication needs updating before v2.0 work begins.
- The proposal requires 3-AI consensus to take effect; this review counts as one. The record should confirm all three AIs before updating project memory or execution order.
