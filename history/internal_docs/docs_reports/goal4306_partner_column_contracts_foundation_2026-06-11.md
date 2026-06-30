# Goal4306: Partner-Column Contracts Foundation

Date: 2026-06-11

## Verdict

`accept-with-boundary` for the first Fable5 P2 engineering slice.

Goal4306 adds a shared partner-column contract layer and wires it into the
current Numba grouped top-k path. This starts reducing the `partner_adapters.py`
N-by-M growth problem identified in Goal4302 without attempting a risky
whole-file rewrite.

## What Changed

- Added `src/rtdsl/partner_column_contracts.py`.
- Added `RtdlGroupIdContract`, a shared contract for grouped partner columns.
- Added `RtdlPartnerClaimBoundary`, a false-by-default metadata helper for
  release, speedup, zero-copy, package-install, paper-reproduction, automatic
  partner-selection, and app-specific-native-engine claims.
- Added `make_equal_contiguous_group_id_contract(...)`,
  `validate_group_id_contract(...)`, `require_group_id_contract(...)`,
  `default_partner_claim_boundary_metadata()`, and
  `validate_partner_claim_boundary(...)`.
- Exported the new contract objects and helpers from `rtdsl.__init__`.
- Wired the contract into `run_numba_grouped_topk_f64(...)`.
- Wired the same contract metadata through
  `grouped_topk_f64_partner_columns(..., partner="numba")`.
- Added standardized false claim-boundary metadata to the grouped top-k and
  top-k-nearest partner front-door metadata.

## Why This Matters

Goal4302 correctly flagged that the partner path is growing through repeated
hand-written implementations and repeated metadata blocks. The fix should not
be another app-specific shortcut. The first useful step is to make shared
contracts explicit:

- group-id layout,
- group count,
- row count,
- rows per group,
- validation mode,
- public-claim boundary flags.

The current Numba top-k path is the right first integration point because its
layout rule is precise: `equal_contiguous_group_segments`. The producer emits
one dense, contiguous, equal-length segment per group; the top-k runner validates
that rule and now reports it through the shared contract metadata.

## Claim Boundary

Goal4306 does not authorize:

- release action,
- package-install wording,
- public speedup wording,
- whole-app acceleration wording,
- broad RT-core wording,
- true-zero-copy wording,
- automatic partner selection,
- paper reproduction claims,
- app-specific native-engine logic.

This goal is an internal architecture cleanup and contract-hardening slice.

## Validation

Focused Windows validation:

```text
$env:PYTHONPATH='src;.'; py -3 -m unittest tests.goal4306_partner_column_contracts_foundation_test tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4303_current_security_redaction_guard_test tests.goal4305_fable5_evidence_and_process_docs_test

Ran 18 tests in 0.338s
OK (skipped=4)
```

The test suite checks:

- valid and invalid `RtdlGroupIdContract` cases,
- false-by-default `RtdlPartnerClaimBoundary` behavior,
- source integration into the Numba top-k runtime and partner adapter,
- report coverage,
- executable Numba CUDA metadata emission when CUDA is available.

Local Linux executable validation, using the current validation checkout:

```text
PYTHONPATH=src:. python3 -m unittest tests.goal4306_partner_column_contracts_foundation_test tests.goal4301_numba_grouped_topk_device_rank_test tests.goal4303_current_security_redaction_guard_test tests.goal4305_fable5_evidence_and_process_docs_test tests.goal4299_numba_topk_partner_reference_test

Ran 18 tests in 0.835s
OK
```

The Linux run executed the Numba CUDA tests and produced only small-grid Numba
occupancy warnings, which are expected for focused correctness tests.

## Remaining Work

Goal4306 is only the first shared-contract slice. The remaining Fable5 P2 work
is to migrate more repeated partner-column families onto this layer:

- grouped sum/min/max/count,
- row-offset grouped reductions,
- pairwise score-row producers,
- fixed-radius partner outputs,
- route-level claim-boundary metadata.

That broader migration should proceed incrementally, with each contract family
kept app-agnostic and tested before any claim or release wording changes.
