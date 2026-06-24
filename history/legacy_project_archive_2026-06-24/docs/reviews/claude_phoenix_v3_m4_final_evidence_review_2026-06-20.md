# Claude Review: Phoenix V3 M4 Final Evidence Classification

Date: 2026-06-20

Scope: final external review of the Phoenix V3 M4 internal pod evidence after
M9/M10/M11/M18/M23/M28 execution.

## Verdict

VERDICT: ACCEPT_WITH_REQUIRED_AMENDMENTS

## Required Amendments

- Explicitly label M10 as a non-clean pass in the evidence index, with
  `accounting_warning_count=1` and `true_zero_copy_ready=false`, rather than
  grouping it alongside clean passes.
- Record the system `python3` gate failure, missing CuPy/Numba, as an open
  packaging gap with an owner and target fix milestone.
- Confirm and document that all M9/M10/M11/M18/M23/M28 result sets carry false
  public/release claim flags in machine-readable metadata, not only prose.
- Attach `source_manifest.sha256` and the `no_git_worktree` identity note to
  each module result record so provenance travels with extracted numbers.
- State explicitly that M28's same-contract ratios, count 9.864x and sum
  202.774x, are internal CPU-reference comparisons only and must not be cited as
  cross-backend speedup until M7 qualification.

## Risk Notes

- The largest residual risk is silent reclassification: internal ratios or pass
  results must not be lifted into public material.
- M10's accounting warning means it is not equivalent to clean-pass rows.
- The system Python packaging gap narrows what the evidence attests to until
  standard packaging is repaired.
- Zero Phoenix M7-qualified rows remains the controlling fact for the next gate.

## Codex Follow-Up

Codex applied the required amendments to:

- `docs/rebuild/v3/evidence/phoenix_v3_m4_grouped_continuation_20260620/phoenix_v3_m4_evidence_index_2026-06-20.json`
- `docs/rebuild/v3/phoenix_v3_m4_grouped_continuation_pod_evidence_2026-06-20.md`
- `tests/v3_phoenix_m4_grouped_continuation_evidence_test.py`
- `scripts/v3_release_wording_gate.py`

