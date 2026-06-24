# Goal 493: Post-v0.7 Public Surface 3C Audit

## Objective

After `v0.7.0` is tagged and merged to `main`, audit and refresh the public
front page, documentation index, tutorials, feature index, v0.7 release reports,
and examples index for 3C quality:

- correctness
- consistency
- comprehensiveness

## Scope

Primary files:

- `README.md`
- `docs/README.md`
- `docs/quick_tutorial.md`
- `docs/release_facing_examples.md`
- `docs/tutorials/*.md`
- `docs/features/README.md`
- `docs/features/db_workloads/README.md`
- `docs/rtdl_feature_guide.md`
- `docs/current_milestone_qa.md`
- `docs/release_reports/v0_7/*.md`
- `examples/README.md`

## Acceptance Criteria

- Public docs describe `v0.7.0` as the current released mainline state.
- Historical docs remain clearly historical where they are retained.
- Tutorial commands point to existing runnable scripts.
- Portable public examples pass on the CPU/Python path.
- A per-file 3C ledger is generated.
- Claude, Gemini, and Codex each review or audit the result before closure.
