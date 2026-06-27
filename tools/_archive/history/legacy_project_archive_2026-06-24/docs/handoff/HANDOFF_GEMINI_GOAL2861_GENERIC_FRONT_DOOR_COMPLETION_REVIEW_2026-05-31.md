# Handoff: Gemini Review for Goal2861 Generic Front-Door Completion

Please perform an independent read-only review of Goal2861.

## Files to Inspect

- `src/rtdsl/partner_adapters.py`
- `src/rtdsl/__init__.py`
- `src/rtdsl/adapters/reductions.py`
- `src/rtdsl/adapters/collection.py`
- `src/rtdsl/v2_5_triton_app_migration.py`
- `tests/goal2681_v2_5_triton_partner_adapter_front_door_test.py`
- `tests/goal2861_v2_5_generic_partner_front_door_completion_test.py`
- `docs/reports/goal2861_v2_5_generic_partner_front_door_completion_2026-05-31.md`
- `docs/reports/goal2681_v2_5_triton_partner_adapter_front_door_2026-05-27.md`

## Questions

1. Do the new wrappers expose generic app-agnostic front doors for grouped
   argmin, grouped argmax, grouped top-k, and bounded collect/finalize?
2. Does `v2_5_triton_front_door_coverage()` honestly move the promoted
   benchmark-app operation set from 4/10 to 10/10 without pretending this is a
   speedup, release, or auto-selection claim?
3. Are deterministic tie-breaking, bounded-collect overflow, and claim-boundary
   wording preserved?
4. Are there any app-shaped semantics or native-engine customization leaks?

## Expected Output

Return markdown only. Use one of the allowed verdicts:

- `accept`
- `accept-with-boundary`
- `needs-more-evidence`
- `reject`

If accepted, state any boundaries precisely. Do not write files.
