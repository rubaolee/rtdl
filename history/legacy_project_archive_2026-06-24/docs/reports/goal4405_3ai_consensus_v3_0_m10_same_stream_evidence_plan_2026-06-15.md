# Goal4405 3-AI Consensus: V3.0 M10 Same-Stream Evidence Plan

Date: 2026-06-15

Status: accepted with gates. M10 same-stream evidence implementation may begin.

## Consensus State

`v3_0_m10_same_stream_evidence_allowed_fail_closed_required`

## Decision

The V3.0 M10 same-stream evidence plan is accepted as the next internal V3 gate after M9.

This consensus authorizes M10 implementation only in this scope:

- same-stream/no-hidden-copy evidence wrapper over the existing generic grouped-stream OptiX route;
- explicit CuPy and Numba partner rows;
- CUDA event or Nsight stream-correlation evidence when observable;
- transfer-counter or equivalent no-hidden-copy evidence when observable;
- threshold-7 predicated mixed-core evidence, plus larger rows if needed;
- focused tests and pod execution.

This consensus does not authorize:

- public V3 performance claims;
- broad RT-core speedup claims;
- whole-path zero-copy wording;
- automatic partner/backend selection;
- app-specific public API names;
- app-specific native symbols;
- raw arbitrary OptiX callback exposure as stable user API.

## Reviewed Artifacts

- M10 plan: `docs/reports/goal4405_v3_0_m10_same_stream_evidence_plan_2026-06-15.md`
- Review handoff: `docs/handoff/HANDOFF_3AI_GOAL4405_V3_0_M10_SAME_STREAM_EVIDENCE_PLAN_2026-06-15.md`
- Codex review: `docs/reviews/goal4405_codex_review_v3_0_m10_same_stream_evidence_plan_2026-06-15.md`
- Claude-lens review: `docs/reviews/goal4405_claude_review_v3_0_m10_same_stream_evidence_plan_2026-06-15.md`
- Gemini-lens review: `docs/reviews/goal4405_gemini_review_v3_0_m10_same_stream_evidence_plan_2026-06-15.md`
- M9 evidence: `docs/reports/goal4403_v3_0_m9_grouped_stream_partner_2026-06-15.md`

## Reviewer Verdicts

| Reviewer | Verdict | Interpretation |
| --- | --- | --- |
| Codex | ACCEPT_WITH_GATES | M10 is acceptable if same-stream and true-zero-copy fields can only flip with hard evidence. |
| Claude-lens | ACCEPT_WITH_GATES | M10 should proceed as a narrow evidence gate; exact producer-consumer handoff evidence is mandatory. |
| Gemini-lens | ACCEPT_WITH_GATES | M10 should proceed internally; no-hidden-copy wording must be scoped to named values and measured windows. |

No reviewer returned `REQUEST_CHANGES`.

## Binding Gates

1. CuPy and Numba rows are both required in the same payload.
2. Both rows must use the same graph, contract, parameters, threshold, route options, and validation rule.
3. Signatures must match across partners.
4. `same_stream_ready=true` requires observed `cuda_event_pair` or `nsight_stream_correlation` evidence tied to the exact native-producer to partner-consumer handoff.
5. A generic event record, host timer, synchronization side effect, or `stream_handle: 0` is not enough.
6. `true_zero_copy_ready=true` requires device residency plus transfer-counter or equivalent no-hidden-copy evidence.
7. Pointer identity alone is not enough for true-zero-copy readiness.
8. Validation materialization must happen after the measured native plus partner window.
9. Any no-hidden-copy statement must name the covered values and measured window.
10. If native wrapper streams cannot be observed, M10 must return partial or blocked with readiness false.
11. All public claim booleans remain false.

## Required Implementation Notes

M10 validation must be stricter than the generic `InstrumentationPacket.same_stream_ready` property. It must prove the event or Nsight record belongs to the exact handoff under review, not merely that a CUDA event exists somewhere in the packet.

M10 must normalize or quarantine lower-level metadata that could be read as stronger than the top-level claim boundary. In particular, lower-level "output column zero-copy" hints do not authorize whole-path or public true-zero-copy wording.

The threshold-7 predicated case remains required because it exercises the nontrivial mixed-core route where `all_core_flags_true=false`.

## Wording Boundary

Allowed internal wording after a full M10 pass:

"Internal V3 M10 evidence gate passed for the bounded `fixed_radius_component_grouped_stream_pilot` on the tested hardware: explicit OptiX+CuPy and OptiX+Numba rows recorded device-resident result columns, hardware-observed same-stream/event-ordered handoff, and no observed hidden host/device copy in the measured native-to-partner window. `public_claim_authorized=false`."

Allowed wording after a partial or blocked M10 result:

"RTDL has device-resident grouped-stream partner evidence, but same-stream or true-zero-copy wording remains blocked until stream and transfer evidence are observable."

Forbidden wording:

- "V3.0 is zero-copy."
- "RTDL has no hidden copies."
- "RTDL has a general same-stream OptiX+partner path."
- "RTDL accelerates CuPy/Numba automatically."
- "RTDL beats Embree/CUDA/author code on this workload."
- "This authorizes a public speedup claim."
- "This proves whole-app DBSCAN or broad RT-core acceleration."

## Next Authorized Work

Proceed to M10 implementation:

1. inspect the grouped-stream OptiX ABI and partner stream APIs;
2. add an evidence wrapper that records exact handoff evidence or fails closed;
3. keep CuPy and Numba rows side by side;
4. run focused tests locally;
5. run the pod measurement on the RTX 4000 Ada pod;
6. record results in a dated M10 report.

## Final Conclusion

3-AI consensus passes with gates. M10 implementation may begin, but every claim boundary remains false until hardware-observable evidence proves otherwise.
