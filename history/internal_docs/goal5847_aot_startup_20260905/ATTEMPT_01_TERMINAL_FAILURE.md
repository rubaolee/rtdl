# Goal5847 Formal Attempt 01 Terminal Failure

Status: `TERMINAL__CONTROLLER_RECEIPT_LAYOUT_DEFECT`

Attempt 01 used the preregistered implementation commit
`11096b168eadccff0511c6e9e8f57234c58ce10a`. The first scheduled RTDL worker
completed and emitted a sealed exact-result record. Before worker two was
launched, the controller rejected that record because it looked for launch
counts at receipt top level. The full receipt schema correctly stores those
counts in `native_snapshot`.

No Attempt 01 timing sample is eligible for a successor transaction. The
complete output directory is preserved in
`ATTEMPT_01_TERMINAL_FAILURE.tar.gz` with SHA-256
`d59b368b337d20d928329d1fd919551c49f8e397ba941b45d71bb8e22a80f8ea`.
The worker stderr is empty; the controller traceback is recorded in the
engineering log and repository history.

The successor repair must retain strict validation by calling the canonical
traversal-receipt verifier with exact provider, output, route, program-bundle,
launch-count, and raygen-count bindings. It may not relabel, discard, or pool
Attempt 01.

