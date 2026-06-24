# Goal1322: Three-AI Jaccard Internal Status Consensus

Date: 2026-05-05

## Decision

`polygon_set_jaccard / chunked_candidate_scoring` may move from
`diagnostic_blocked` to `pod_verified_generic` in the internal v1.5 migration
inventory.

This is an internal implementation status only. It does not authorize public
speedup wording.

## Inputs

- Goal1318: native bounded collection routed and pod-validated.
- Goal1320: generic Jaccard score-reduction surface added and pod-validated.
- Goal1321: backend-neutral native polygon-pair area summary ABI added,
  app-named Jaccard native continuation removed from the active app route, and
  pod-validated.

## External Reviews

- Claude review:
  `docs/reports/goal1322_claude_review_jaccard_internal_status_2026-05-05.md`
  returned `ACCEPT`.
- Gemini review:
  `docs/reports/goal1322_gemini_review_jaccard_internal_status_2026-05-05.md`
  returned `ACCEPT`.

## Consensus

Codex, Claude, and Gemini agree:

- status may become `pod_verified_generic`;
- `remaining_app_specific_work` may become empty;
- `public_wording_authorized` must remain `false`;
- boundary must retain that OptiX remains slower than Embree;
- no fused GPU Jaccard kernel claim is allowed;
- Vulkan/HIPRT/Apple RT remain frozen before v2.1.

## Applied Inventory Shape

```python
{
    "goal": "Goal1322",
    "app": "polygon_set_jaccard",
    "subpath": "chunked_candidate_scoring",
    "status": "pod_verified_generic",
    "generic_primitive": "COLLECT_K_BOUNDED",
    "summary_primitive": "REDUCE_FLOAT(SUM)",
    "backend_scope": ACTIVE_V1_5_BACKENDS,
    "remaining_app_specific_work": (),
    "public_wording_authorized": False,
}
```

The retained boundary states that the implementation is a diagnostic native
candidate-plus-backend-neutral area-summary pipeline, OptiX remains slower than
Embree, no public speedup wording is authorized, and no fused GPU Jaccard kernel
claim is made.
