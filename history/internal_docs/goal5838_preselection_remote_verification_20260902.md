# Goal5838 pre-selection remote and regression verification

Date: 2026-09-02

Status: `PASS__REMOTE_CLEAN_CLONE_REPRODUCES_PRESELECTION_SEAL`

## Remote clean-clone evidence

The active branch was pushed and then independently shallow-cloned from
`https://github.com/rubaolee/rtdl.git` into a fresh `/tmp` directory. The clone
resolved to commit `58f6e2fab526a5208a6da6ff8a9b5f4c004dedd1` and remained
Git-clean after verification.

The stored-seal verifier reported:

```text
status=PASS__GOAL5838_GENERIC_CORE_AND_CHALLENGE_TABLE_SEAL
frozen_core_file_count=3
eligible_candidate_count=10
selected_candidate_count=0
seal_sha256=c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae
challenge_table_sha256=0a2b2c01aed75ad08fad44f7fbc2509ef632d786545e0202b9a4b27425a30345
```

The remote clone passed `48/48` tests across the core-seal/selection tooling,
generic family lifecycle, and migrated family routes. The same focused set
passed in the source workspace.

## Broader regression context

The pre-seal Goal583x denominator ran 265 tests: 264 passed and the sole error
was the already registered Goal5832 current-tree custody mismatch
`goal5831.source_authorities[6] byte count drift`. This historical authority
froze an older root export file; later legitimate exports changed it. The
historical manifest is intentionally not rewritten.

A repository-wide discovery was also allowed to finish once. It ran 13,150
tests in 139.795 seconds and reported 750 failures, 6,206 errors, and 600 skips.
Inspection showed that this repository-wide set mixes many historical release
lines and tests requiring pruned archives, absent paper-app trees, missing
datasets, native binaries, GPU services, and old evidence reports. Representative
errors include missing `history.examples_internal`, removed RayJoin fixtures,
absent historical Barnes-Hut/X-HD paper-app paths, and a missing
`apps/goal15_lsi_native.cpp`.

That repository-wide result is disclosed but is not a Goal5838 acceptance
denominator. It predates and is structurally unrelated to the new core. The run
created nine untracked historical reports and one empty `history.db`; because
the workspace was clean before the run, those test-only products were removed.
The Goal5838 core seal and `48/48` focused set were then reverified successfully.

## Claim boundary

This evidence establishes remote byte custody and local functional regression
only. It is not challenge selection, candidate implementation, true-GPU
execution, performance evidence, external review, consensus, or prospective
success. The target pulse remained in the future throughout this verification.
