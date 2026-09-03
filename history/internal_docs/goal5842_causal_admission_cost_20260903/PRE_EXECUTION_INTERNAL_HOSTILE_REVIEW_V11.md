# Goal5842 V11 pre-execution internal hostile review

Date: 2026-09-03
Review mode: internal only; external review is owner-deferred while traveling.

## Review question

Does V11 honestly repair V10 without changing the scientific design or using
the 290 prior timer-free calls as a result-dependent advantage?

## Findings

### P0

None found.

### P1

None found, subject to the pre-execution gates below.

### P2

1. V8's repair narrative asserted the wrong sphere owner because it reasoned
   from the legacy public built-in-sphere path instead of tracing the actual
   Goal5842 task's `sphere_any_hit_count_family_route`. V11 preserves that
   historical error and corrects it append-only rather than rewriting V8.
2. The old Goal5842 unit test fabricated its expected sphere receipt from the
   same wrong literal used by the witness. V11 adds a behavioral check against
   the real selected-sphere owner lifecycle property, so the test no longer
   merely agrees with itself.
3. V11 still provides at most one GPU architecture generation. Even a complete
   Ada transaction cannot close Goal5842's required second-generation gate.

### P3

1. The selected sphere prepared runtime is added to the V11 source manifest.
   This changes custody coverage, not runtime behavior or the estimand.
2. V10 completed substantial timer-free GPU work before failing. V11 binds the
   exact archive and call count, forbids pooling, and repeats all witnesses.

## Scientific-design comparison

V10 and V11 retain byte-identical task contracts, input values, public outputs,
causal and baseline schedules, phase boundaries, sample counts, bootstrap
procedure, baseline arms, hardware design, and failure policy. The only
execution behavior changed is which exact schema string the no-timing witness
and recount require for the selected sphere provider lifecycle. Neither change
lies inside a registered interval.

The Direct and PyOptiX fair-output correction remains unchanged. The
checker-off arm remains private experiment code. No product API or frozen
generic-family core is changed.

## Required pre-execution gates

- Rebuild `PREREGISTRATION_V11.json` twice and require byte identity.
- Pass the focused Goal5842, prepared-cache, and immutable-input tests.
- Verify all three frozen-core SHA-256 values remain unchanged.
- Commit and push V11 before any formal V11 GPU call.
- Build fresh commit-bound native and Direct binaries in new output paths.
- Require zero foreign GPU processes and a never-before-used transaction root.

## Completed local gates

- Goal5842, prepared-cache, and immutable-input suites passed `53/53` on the
  macOS Python 3.12 environment.
- The inherited selected-sphere suite passed `20/20`.
- The modified Python files passed Ruff check and `py_compile`; `git diff
  --check` passed.
- The V10 archive test independently rehashed the archive, execution
  authority, failure marker, Stage 01 command/stdout/stderr, internal authority
  seal, and exact progress boundary.
- Frozen-core SHA-256 values remain
  `2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224`,
  `7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c`,
  and `d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8`.

After these document bytes were fixed, the V11 preregistration rebuilt
byte-identically from a separate in-memory generation. Commit/push, fresh pod
builds, the idle-GPU gate, and a never-before-used V11 transaction root remain
required.

## Verdict

`ACCEPT_FOR_ONE_V11_TRANSACTION_ONLY_IF_ALL_PRE_EXECUTION_GATES_PASS`.

This verdict authorizes no performance claim. Any failure before worker zero
must be preserved and superseded explicitly; any failure after worker zero
terminates V11 with no retry or row replacement.
