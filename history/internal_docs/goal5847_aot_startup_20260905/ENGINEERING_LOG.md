# Goal5847 Engineering Log

## 2026-09-05T14:33:51Z: Preregistration Frozen

- Implemented a minimal deploy-only AOT DSO with lazy runtime-compiler loading,
  a fail-closed asynchronous provider initialization capability, and the public
  family `.rtdlexe` build/load/bind/prepare route.
- Repaired the PyOptix worker's `(context, logger)` result unpacking before any
  formal transaction.
- Removed the measured prepared-steady RTDL regression by preallocating generic
  bounded-relation ABI storage and reusing an immutable decoded row tuple only
  after byte-identical native output and successful oracle/audit/cache commit.
- Local current-path regression: 191 tests passed with three environment skips.
  A 209-test superset had three known Goal5843 frozen-current-tree replay
  failures caused by later legitimate source evolution; these are not hidden
  or rewritten.
- Exact GPU validation passed relation correctness (4,096 canonical rows),
  triangle correctness (`65530`), true OptiX receipts, zero RTDL runtime
  compiler use, and five isolated mutation rejections.
- Exploratory RTDL steady medians after the repair were 295,638 ns, 297,183 ns,
  and 298,299 ns. Exploratory paired primary ratios were 0.238x, 0.202x, and
  0.278x; later paired post-import ratios were 2.321x and 2.187x. These values
  informed confidence only and are forbidden from the formal sample pool.
- Frozen `PREREGISTRATION.json` before launching any formal worker.

## Attempt 01: Terminal Verifier Failure

- The first formal worker completed exact RTDL execution and wrote its sealed
  result, but the controller rejected the result before launching worker two.
- Root cause: the controller incorrectly looked for
  `successful_launch_count` and `raygen_invocation_count` at receipt top level.
  The full receipt contract stores both under `native_snapshot`.
- This is a formal verifier defect, not a GPU, correctness, traversal, or
  performance failure. The attempt remains terminal and cannot be pooled into
  a successor transaction.
- Complete terminal archive:
  `ATTEMPT_01_TERMINAL_FAILURE.tar.gz`
- Archive SHA-256:
  `d59b368b337d20d928329d1fd919551c49f8e397ba941b45d71bb8e22a80f8ea`
- Remediation requires a new source commit and a separately frozen successor
  preregistration. The controller must invoke the strict full traversal
  receipt verifier rather than weaken or omit receipt validation.

Formal attempt 01 status: `TERMINAL__CONTROLLER_RECEIPT_LAYOUT_DEFECT`.

## 2026-09-05T14:40:41Z: Successor V2 Preregistration Frozen

- Repaired the controller to invoke the canonical strict full traversal
  receipt verifier instead of reading nonexistent top-level counters.
- Added positive full-receipt coverage and a re-sealed nested launch-count
  mutation test. Replayed the actual Attempt 01 receipt through the repaired
  verifier successfully.
- Ran 192 current-path adjacent tests: all passed, with three environment
  skips.
- Rebuilt the minimal DSO and both family-bound artifacts at exact clean
  source commit `f5e337feef6829e063c6aff06f4e8bd6d5466b3b`.
- Re-ran GPU relation, triangle, compiler-absence, true-OptiX, and isolated
  mutation validation successfully.
- Frozen `PREREGISTRATION_V2.json`; its design and gates are unchanged. No
  Attempt 01 or exploratory sample may be pooled into V2.

Formal successor V2 status: `NOT_STARTED`.
