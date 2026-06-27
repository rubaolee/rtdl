# Goal4317: Grouped Reduction Adapter Route

Date: 2026-06-11

## Verdict

`accept-with-boundary` for a small Fable5 F3/P2 monolith-reduction slice.

The project already had `src/rtdsl/adapters/reductions.py`, but two important
routes still bypassed it for grouped/summary reductions: package public exports
in `src/rtdsl/__init__.py` and one generic segmented typed-stream import. Goal4317
makes the grouped/summary reduction adapter route canonical for those surfaces.

## What Changed

- Kept `src/rtdsl/adapters/reductions.py` as the canonical grouped/summary
  reduction adapter front door.
- Added the vector-sum prepared-session helpers and measured-selection helper
  to the canonical reductions route.
- Rewired `src/rtdsl/__init__.py` so public reduction exports route through
  `rtdsl.adapters.reductions` for key/value reductions, metric-table reductions,
  unique-pair keys, ranked reductions, vector sums, prepared vector-sum sessions,
  measured vector-sum selection, and the grouped-argmin/global-argmax witness
  helper.
- Rewired `src/rtdsl/v2_8_segmented_typed_stream_adapter.py` to import grouped
  vector sum, argmin, argmax, and top-k through `rtdsl.adapters.reductions`.
- Added `tests/goal4317_grouped_reduction_adapter_route_test.py`.

This does not move implementation bodies out of `partner_adapters.py`; that
larger split remains future work. The point of this slice is to stop new public
and generic stream routes from strengthening the monolith dependency while
keeping compatibility stable.

## Boundary

Goal4317 does not authorize release action, public speedup wording, broad
RT-core wording, package-install wording, automatic partner selection,
true-zero-copy wording, paper reproduction, or app-specific native-engine
logic. It is an internal adapter-route cleanup only.

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4317_grouped_reduction_adapter_route_test tests.goal2781_grouped_vector_sum_adapter_test tests.goal3008_numba_group_argmin_global_argmax_front_door_test
```

Observed result: 11 tests ran successfully with 2 expected optional CUDA/partner
skips on the Windows shell.

A broader typed-stream execution test was not used as the acceptance command on
this shell because it exercises optional Torch/Numba runtime execution paths.
Goal4317's acceptance surface is import-route identity and compatibility, not a
new partner execution claim.
