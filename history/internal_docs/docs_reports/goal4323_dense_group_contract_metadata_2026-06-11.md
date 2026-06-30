# Goal4323: Dense Group Contract Metadata

Date: 2026-06-11

## Verdict

`accept-with-boundary` for the next Fable5 P2 shared partner-column contract
slice.

Goal4306 introduced the shared partner-column contract layer and wired the
equal-contiguous grouped top-k path. Goal4323 adds the matching dense
zero-based group-id contract helper and starts applying it to grouped argmin,
grouped argmax, and non-Numba grouped top-k front-door metadata.

In short, this is the dense zero-based group-id contract metadata slice for
grouped argmin, grouped argmax, and non-Numba grouped top-k.

## What Changed

- Added `make_dense_zero_based_group_id_contract(...)` to
  `src/rtdsl/partner_column_contracts.py`.
- Extended `validate_group_id_contract(...)` so dense zero-based group ids
  reject nonsensical `rows_per_group` metadata and reject non-empty rows with
  `group_count <= 0`.
- Exported the partner-column contract helpers and constants through
  `rtdsl.__all__`.
- Added a `_dense_group_id_contract_metadata(...)` helper in
  `src/rtdsl/partner_adapters.py`.
- Added shared dense contract metadata to grouped argmin, grouped argmax, and
  non-Numba grouped top-k partner front doors.
- Added dense contract metadata to the direct Numba grouped argmin/argmax
  runner result.
- Added `tests/goal4323_dense_group_contract_metadata_test.py`.

Goal4324 follow-up: Claude correctly rejected the first local draft because
the Windows-only validation skipped the CUDA execution test and the dense
contract metadata assignment had not actually landed inside
`_run_numba_grouped_arg_reduce_f64`. The follow-up fix adds that assignment at
the validated grouped arg-reduce location and removes the misplaced assignment
from an unrelated segmented extreme helper.

## Boundary

Goal4323 does not authorize new public claims or release action.

Goal4323 does not move implementation bodies out of `partner_adapters.py`,
change algorithm behavior, add a new partner, authorize release action,
authorize public speedup wording, authorize broad RT-core wording, authorize
true-zero-copy wording, authorize automatic partner selection, or authorize
app-specific native-engine logic.

This is contract-hardening work: more front doors now publish their group-id
layout and validation mode through the same metadata vocabulary.

## Validation

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4323_dense_group_contract_metadata_test tests.goal4306_partner_column_contracts_foundation_test tests.goal4317_grouped_reduction_adapter_route_test
```

Observed result after the Goal4324 follow-up fix on the Windows shell: 14 tests
passed with 2 expected optional Numba CUDA skips. Python compile checks passed
for the touched runtime and test modules.

Local Linux validation also copied the touched runtime/test/report files into
the validation checkout and ran the same suite with Numba CUDA available:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal4323_dense_group_contract_metadata_test tests.goal4306_partner_column_contracts_foundation_test tests.goal4317_grouped_reduction_adapter_route_test
```

Observed result: 14 tests ran in 0.844s and passed. The Numba warnings were
small-grid occupancy warnings from focused correctness tests, not failures.
