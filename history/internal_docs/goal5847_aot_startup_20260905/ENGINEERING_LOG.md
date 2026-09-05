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

## 2026-09-05T14:46:13Z: Formal Successor V2 Complete

- Ran all 16 frozen workers in eight balanced alternating-order blocks on the
  same RTX 2000 Ada GPU; retained 1,024 steady samples per arm and discarded
  zero.
- All exact oracles, candidate bindings, source identities and preregistered
  gates passed. Median within-block complete-process RTDL/PyOptix ratio is
  `0.229370473012883`; worst block is `0.2587280703779318`.
- Median within-block post-import ratio is `2.50424177977926`; worst block is
  `3.211852628078743`. This adverse decomposition is retained.
- Pooled steady medians are 299,403 ns for RTDL and 3,496,252 ns for PyOptix,
  ratio `0.085635417584316`. RTDL is `0.8172817601135557x` the Goal5845
  steady reference.
- The RTDL arm recorded zero runtime-compiler attempts, no compiler modules and
  no NVRTC mappings. The PyOptix harness consumed precompiled PTX and did not
  call a source compiler, but its CuPy dependency stack mapped NVRTC.
- Captured the complete formal transaction, candidates, native image/build,
  GPU validator, preregistration, PyOptix source/extension/receipt/PTX and
  environment records in `FORMAL_V2_EVIDENCE.tar.gz`, SHA-256
  `65ee646c36e801fbf957de6eeb0c8b03106a48fa01bb2008d3aed0761fd037e8`.

Formal successor V2 status:
`PASS__GOAL5847_PREREGISTERED_AOT_PERFORMANCE_GATES`.

## 2026-09-05: Internal Closure Audit

- Added a standard-library-only authority builder that checks safe tar
  membership, every retained byte, frozen Git blobs, native exports and
  dependencies, AOT artifact chains, two RSA installed-trust chains, ten full
  OptiX receipts, all worker transports, all 2,048 timing samples and all
  preregistered gates.
- Stored authority seal:
  `3501c83ab4c13a3ef63890b446dd949baade2443ed578e9cd75a71d3fa88a301`.
- Authority hostile tests pass 7/7; Goal5847 current-path tests pass 29/29;
  lint and byte-identical `--verify-stored` recount pass.
- A broader 198-test adjacent run has 193 passes, one environment skip and four
  old Goal5803 errors caused by absent Git-excluded historical snapshots. They
  fail before behavior assertions and remain disclosed rather than fabricated.
- Internal hostile review accepts only the exact engineering scope. External
  review and all public/manuscript claims remain pending.

Goal5847 internal status:
`PASS__GOAL5847_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`.
