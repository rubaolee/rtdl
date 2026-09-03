# Goal5842 V5 pre-execution internal hostile review

## Verdict

`READY_FOR_NEW_INDEPENDENT_REPLICATION__NOT_GOAL5842_COMPLETE`

The V5 harness may be committed and executed on the available Ada pod. This
verdict authorizes no performance claim. It does not convert transaction04
into a success, permit any V4 row to enter a V5 estimator, satisfy the required
second GPU architecture generation, or substitute for deferred external
review.

The frozen V5 preregistration has internal seal
`bcb1980055d608b4b4b7d0242defbfd3f11669aab5a2b6ecc716cb7e669e43cc`.
Its whole-file SHA-256 is
`f2d6f7039d27b5fbddd0c5636e994669ab1ffdc22c522cb083bcb4ddc444fdf3`.
It retains the V4 tasks, schedules, phase boundaries, statistics, thresholds,
and failure policy exactly. Its only execution repair is package-safe loading
of the historical PyOptiX worker. Its additional pre-worker-zero gate executes
the two PyOptiX provider tasks without recording timing.

## Hostile questions and disposition

### Was the failed V4 transaction hidden or retried?

No. The repository contains the complete transaction04 archive, formal failure
report, terminal no-retry marker, complete 216-worker causal result, completed
Direct receipts, and failed PyOptiX receipt. Tests verify both the outer archive
hash and the hashes and content of the critical records inside it. V5 is a new
full replication root and its estimators read only V5 receipts.

### Was the experiment changed after seeing V4 causal results?

No task, schedule, arm, phase, warmup count, repetition count, statistic,
bootstrap rule, threshold, provider implementation, or frozen RTDL core byte
changed. V4 and V5 schedule-bearing fields are asserted exactly equal. The
observed V4 causal values remain disclosed and may be compared descriptively
only.

### Could the PyOptiX repair alter the measured provider implementation?

The repair changes imports only: package-relative imports are used through the
Goal5842 package front door, while direct-script imports remain available for
the historical entrypoint. A regression test imports both prepared classes
through the package and executes the historical script's `--help` path. The
formal provider classes, device source, task fixtures, setup phases, and
execution loops are unchanged and source-hash-bound.

### Could a broken provider survive until after worker zero again?

The V5 runner now executes a package-front-door PyOptiX relation/triangle
witness before starting the causal controller. It performs two complete
provider executions and three OptiX launches, validates exact frozen outputs,
and emits no duration. The independent recount requires exact witness fields,
rejects hidden timing fields, binds source/API/repository identity, and checks
the provider baseline outputs against the witness.

### Could repeated NVRTC compilation make the witness nondeterministic?

The witness compiles the pinned CUDA source once, then uses the exact same PTX
bytes to construct both task pipelines. This avoids treating changes in
generated non-semantic comments across repeated compiler calls as a scientific
failure. The formal provider-baseline workers remain unchanged and independent.

### Does byte identity improperly claim that independent providers emit the
same implementation bytes?

No. Exact byte identity applies only to CHECK_ON versus CHECK_OFF within each
RTDL task. Direct, PyOptiX, and public RTDL are independent implementations
required to share the same semantic input/output contract, not generated
bytes. Cross-provider execution-time comparisons remain phase-qualified.

### Was app-specific behavior added to the engine or frozen generic core?

No product or native engine source changed. The three frozen generic-core files
retain their sealed SHA-256 identities. All changes are experiment harness,
historical-worker import compatibility, evidence custody, tests, and reports.

## Remaining blockers and risks

- V5 has not yet executed on any GPU. Package import success on macOS is not a
  substitute for the pre-worker-zero real PyOptiX witness on the pod.
- A complete Ada V5 transaction is necessary but insufficient. Goal5842
  requires an exact replay on a second NVIDIA architecture generation with a
  distinct GPU UUID.
- The Direct executable has no timer-free mode. V5 therefore relies on the
  already completed V4 Direct relation execution plus a fresh formal V5 full
  baseline; this exclusion is preregistered rather than silently invented.
- Raw time ratios across different machines are forbidden. Each architecture's
  absolute results must remain separate.
- External review and consensus are still owner-deferred. This internal review
  cannot satisfy either gate.

## Verification at review time

- Goal5842 focused tests: 26/26 pass.
- Goal5838 frozen-core regressions: 91/91 pass.
- Goal5840 refinement regressions: 65/65 pass.
- Goal5798 immutable-input reuse tests: 5/5 pass.
- Active Goal5842 Ruff checks and Python compilation: pass.
- Git whitespace check: pass.
- Frozen core SHA-256 values: unchanged.

P0 findings: 0. P1 findings: 0. Unresolved claim/evidence gates are explicitly
listed above and prevent premature completion or publication wording.
