# Goal5842 V12 pre-execution internal hostile review

Date: 2026-09-03
Review mode: internal only; external review is owner-deferred while traveling.

## Review question

Can a new V12 transaction be scientifically useful after V11 exposed all
registered controller results but failed only in its final independent
validator?

## Findings

### P0

None found, subject to every pre-execution gate below passing before worker
zero.

### P1

1. V12 is not result-blind. V11 completed all registered measurements and its
   controller summaries were observed before this repair. V12 must disclose
   that fact and may not be described as a blind replication.
2. V11 is terminal. A corrected diagnostic recount cannot reclassify it as a
   successful transaction, and none of its rows may enter a V12 estimator.
3. A successful Ada V12 transaction is still only one architecture generation.
   It cannot complete Goal5842 or authorize cross-generation wording.

### P2

1. The old synthetic transaction test copied one common receipt shape across
   all arms and therefore failed to model a documented Direct-only field. The
   revised test must make this arm distinction observable to the independent
   recount.
2. The independent validator must reject both directions of schema drift:
   missing or non-false Direct markers, and Direct-only markers on Python arms.
3. Repeating the same unchanged schedule on the same GPU can establish a clean
   first-generation transaction, but it does not add hardware diversity.

### P3

1. V11's read-only postmortem found no second inconsistency after the exact
   arm-specific schema correction. That is useful diagnosis, not formal
   evidence.
2. The existing registered estimator has no success threshold, which limits
   the opportunity for result-dependent goalpost movement. All adverse rows
   remain mandatory.

## Scientific-design comparison

V12 retains V11's scientific question, causal estimand, task and output
contracts, fixed input bytes, causal and baseline arms, schedules, phase
boundaries, sample counts, warm-ups, repetitions, bootstrap procedure,
hardware gate, and failure policy. Its only execution-behavior change is the
independent recount's arm-specific field-set validation; the synthetic test
now covers that shape. Preregistration contracts, the builder, and documents
also change to preserve append-only V12 custody. No registered interval, GPU
implementation, generated device source, provider implementation, native
engine, or frozen generic core is changed.

## Required pre-execution gates

- Preserve and hash-bind the complete terminal V11 archive.
- Prove from that archive that Direct receipts have the marker exactly false
  and Python receipts omit it.
- Recount every archived V11 raw receipt in a test while retaining V11's
  terminal status.
- Require byte-identical independent V12 preregistration rebuilds.
- Pass the focused Goal5842, prepared-cache, immutable-input, and selected
  sphere suites.
- Pass Ruff, `py_compile`, `git diff --check`, and frozen-core SHA checks.
- Commit and push V12 before any V12 GPU call.
- Use fresh commit-bound native and Direct builds, an idle-GPU gate, and a
  never-before-used create-only output root.

## Completed local gates

- The focused Goal5842, prepared-cache, immutable-input, and selected-sphere
  suites passed `74/74` on the macOS Python 3.12 environment.
- The V11 archive regression independently rehashed the terminal evidence,
  classified all 216 baseline receipts by arm, and recounted every causal row
  and baseline composite after the exact validator repair.
- V12 records zero unregistered complete executions and zero OptiX launches
  before its preregistration freeze; V11's observed calls remain predecessor
  provenance rather than being relabelled as V12 preflight.
- Three negative receipt mutations fail closed: a missing Direct marker, a
  non-false Direct marker, and a Direct-only marker on a Python arm.
- Ruff, `py_compile`, and `git diff --check` passed for the modified Python
  files.
- The combined Goal5840/5842 regression run is `112/114`. The two errors are
  the already disclosed historical Goal5840 repair-builder tests
  `test_repair_authority_is_append_only_and_preserves_scientific_inputs` and
  `test_attempt02_repair_authority_preserves_both_failures_and_inputs`; both
  compare a later legitimate current tree to old attempt-local scientific
  inputs. Goal5842 tests in that run pass. The historical errors are not
  relabelled as passes and are not repaired by rewriting frozen evidence.
- Two independent in-memory V12 preregistration builds were equal and matched
  the generated file byte for byte before this review completion note. The
  final preregistration is regenerated after this note and must pass the same
  check again before commit.
- Frozen-core SHA-256 values remain
  `2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224`,
  `7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c`,
  and `d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8`.

## Verdict

`ACCEPT_FOR_ONE_V12_TRANSACTION_ONLY_IF_ALL_PRE_EXECUTION_GATES_PASS`.

This verdict authorizes no accepted V11 result, no one-generation completion,
no public performance claim, no external review, and no consensus.
