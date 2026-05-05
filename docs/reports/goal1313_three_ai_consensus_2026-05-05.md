# Goal1313 3-AI Consensus: Native Jaccard Device-Level Plan

Date: 2026-05-05

## Verdict

Proceed with the native Jaccard device-level plan after applying the required corrections. The plan remains diagnostic-only and does not authorize public speedup wording.

## Review Inputs

- Codex plan: `docs/reports/goal1313_v1_5_native_jaccard_device_plan_2026-05-05.md`
- Claude review: `docs/reports/goal1313_claude_review_2026-05-05.md`
- Gemini review: `docs/reports/goal1313_gemini_review_2026-05-05.md`

## Consensus

All three AIs agree on the main direction:

- Keep `polygon_set_jaccard` diagnostic.
- Do not add an app-specific `polygon_set_jaccard_fast` native shortcut.
- Use generic polygon-pair bounded collection and guarded reduction contracts.
- Keep Vulkan, HIPRT, and Apple RT frozen before v2.1.
- Prioritize OptiX native bounded collection because NVIDIA RT performance is the critical path.

## Required Corrections Applied

Claude identified three required fixes:

| Finding | Resolution |
|---|---|
| Empty score rows for non-empty candidates could silently produce zero Jaccard | Fixed in `run_generic_polygon_set_jaccard_summary`; now raises before summary emission |
| Embree bounded-wrapper decision was deferred | Plan now requires a symmetric Embree bounded wrapper contract in the same native slice |
| ABI naming was asymmetric | Plan now documents backend-keyed collection wrappers and backend-neutral reduction |

Gemini accepted the original plan and listed no required fixes.

## Validation

Local gate after corrections:

```bash
PYTHONPATH=src:. python3 -m unittest \
  tests.goal1311_v1_5_jaccard_generic_fail_closed_collection_test \
  tests.goal1312_v1_5_jaccard_optix_slower_reason_test \
  tests.goal1310_v1_5_jaccard_collect_k_bounded_contract_test \
  tests.goal1304_v1_5_generic_migration_inventory_test
python3 -m py_compile \
  src/rtdsl/generic_polygon_primitives.py \
  src/rtdsl/jaccard_performance_diagnostics.py \
  src/rtdsl/v1_5_migration_inventory.py \
  src/rtdsl/__init__.py
git diff --check
```

Result: passed on 2026-05-05.

## Next Implementation Slice

Implement native bounded polygon-pair candidate collection for OptiX first, with a symmetric Embree bounded-wrapper contract in the same slice. The collection ABI must fail closed on overflow and publish the same metadata contract across both backends. Native score reduction follows only after collection is pod-validated.
