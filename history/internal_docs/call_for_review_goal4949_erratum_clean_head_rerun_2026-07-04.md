# Call For Review: Goal4949 Erratum Clean-HEAD Rerun

Date: 2026-07-04

Please review:

- `history/internal_docs/goal4949_erratum_clean_head_rerun_2026-07-04.md`
- `history/internal_docs/goal4949_rayjoin_hot_path_remeasure_2026-07-04.md`

## Context

After Goal4949 was committed, the executor found that the POD directory used for
the first measurement was not a git checkout and still contained stale
path-split writer code. The original Numba writer subphase fields therefore
cannot be cited as current-source evidence.

The executor created a new clean POD tree from local `HEAD` using `git archive`,
copied only the built OptiX library and public sample data, and reran the public
sample.

The clean rerun still shows that the current tracked Numba helper is not a
performance win, but the writer subphase explanation changes from stale
path-split fields to the current generic-output-assembly/chain-loop route.

## Requested Verdict Label

Use one of:

- `approve_goal4949_erratum_clean_head_rerun`
- `approve_with_required_amendments`
- `fail_redo_goal4949_erratum`

## Review Questions

1. Does the erratum correctly identify the stale POD directory as invalid evidence for current `HEAD`?
2. Does the clean rerun preserve correctness for both baseline and current Numba route?
3. Does the clean rerun still justify saying the current Numba helper is not a performance win?
4. Does the erratum correctly supersede the stale `path_split_*` fields?
5. Is the corrected bottleneck interpretation consistent with Goal4930 / Goal4938 / Goal4940?
6. Should Goal4949 remain closed, with the erratum attached, rather than being treated as a broad failure?
