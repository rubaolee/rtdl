# Goal5842 V11 terminal recount failure and V12 plan

## Immutable V11 status

V11 is a terminal failed transaction. It is not resumed, repaired in place,
or reclassified as successful. The create-only transaction root was
`/workspace/goal5842-ada-478876b25-transaction11`; worker zero was crossed,
all registered workers completed, and Stage 06 then wrote
`TRANSACTION_FAILED_NO_RETRY.json` after the independent recount returned 1.

The exact source commit was
`478876b257c2b4bb46f2deedf54a7ef2a6d8abff`. The V11 preregistration internal
seal is
`6f1012d4c7f06c279426debfdf80ec9f046311f581488621ca4507854e9e1ff1`;
its whole-file SHA-256 is
`8290f51d7aabcb9022fd7d7e0582b2872f01b9dd7e93c705a03863f96543bccb`.
The bound GPU was an NVIDIA RTX 2000 Ada Generation, compute capability 8.9,
UUID `GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`, driver 580.159.04.

The repository-preserved archive is
`pod_artifacts/goal5842_v11_ada_terminal_failure.tar.gz`: 3,778,593 bytes,
2,324 archive members, SHA-256
`9385c90ec126745ae44859f7bd46b16be1f7b7565fe274782613af4b975b8a15`.
It includes the complete transaction root, top-level driver logs, the fresh
native build and manifest, and the fresh Direct executable.

Selected archive member whole-file identities are:

| Member | Bytes | SHA-256 |
|---|---:|---|
| `execution_authority.json` | 3,894 | `281d08a87e88a6bdf1a6aa42e9a597768097c0639f5d4b92ce18e1dff7020c17` |
| `gpu_identity_witness.json` | 528,551 | `c1a59bdf3fa5cf4a64ca903ef38e04df62ca6f5f983ba1ddace6e575f479d314` |
| `pyoptix_identity_witness.json` | 2,608 | `3d69556da94be5a745eb7544d7d042c68e446e2f82a822ef567609739d887269` |
| `direct_identity_witness.json` | 2,162 | `15af1c59b639fd3b9e7c02c0ed55b37c704b66709d538563672a18f80c9b5c07` |
| `causal/result.json` | 47,224 | `4252ee1257d4d78b017068820eb7b50d9a04f20f07f3e842bc6735f3d23b60cb` |
| `baseline/result.json` | 434,099 | `b7428e91d5d0482181dce21d275b791b17fcb15801ed66f61550b3dcb349f386` |
| `TRANSACTION_FAILED_NO_RETRY.json` | 148 | `b47f288eb9fee428a2e01500549e04865fad9fd8c2ec02ecd4fe5377dc7e3b5f` |
| Stage 06 `command.json` | 1,035 | `224331a413bc65170d1b31839ae0c146343135f3dd416f1f6f9c34c33333f9f1` |
| Stage 06 `stdout.txt` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Stage 06 `stderr.txt` | 953 | `d3cb8983c909ec22c00bb18c46022ec22350a25fd4f20a41710f62a451f7762a` |
| Stage 06 `returncode.txt` | 2 | `4355a46b19d348dc2f57c046f8ef63d4538ebb936000f3c9ee954a27460dd865` |

The execution authority internal seal is
`d955e8d48c91c6afb715e01118e6c0679a037bb7414cc537c329a279939fdbb3`.
The controller-result internal seals are
`3be63b9c97c33e42d98d03f464576028044ae6b8702d87882c8e39f288347698`
for causal admission and
`0a79d83a592cd01f8cae4af6e87f4a6f8e82f14705462bd878a90f543b81fec3`
for the baseline.

## What completed before failure

- All four identity stages passed before worker zero. The RTDL witness made
  291 complete calls, PyOptiX made 144, and Direct made two; none registered a
  timing observation.
- All 216 causal workers completed with zero failures.
- All 216 baseline subworkers completed with zero failures and formed 108
  three-arm composites. They contain 7,020 registered execution samples and
  864 explicitly unregistered warm-up executions.
- The baseline controller reported 7,884 GPU complete executions and a null
  registered performance gate. No threshold was selected.
- No `independent_recount.json` or `TRANSACTION_COMPLETE.json` exists.

The V11 controller outputs contain already-observed timing. They remain
failed-transaction diagnostics and are never pooled into V12 or a
cross-generation estimator. The primary causal-delta diagnostics were
38.074 ms for relation, 34.671 ms for triangle, and 30.585 ms for sphere. The
two baseline tasks also showed substantial RTDL overhead relative to both
comparison arms. These values are disclosed so a later replication cannot be
described as result-blind; they are not a Goal5842 performance result.

## Failure root cause

The Direct controller deliberately emits the additional receipt field
`direct_close_phase_available=false`; Direct has no comparable explicit close
phase. The Python RTDL and PyOptiX receipts correctly omit that Direct-only
field. The baseline controller validates this shape and publishes
`close_phase_comparable_across_all_arms=false`.

The independent recount instead required one unconditional 19-field set for
all three arms. It therefore rejected the first sealed Direct receipt, whose
20th field was `direct_close_phase_available`, with
`RuntimeError: baseline receipt field set mismatch`. The synthetic recount test
had generated an unrealistically uniform 19-field shape for Direct and Python
receipts, so it agreed with the validator rather than reproducing the
controller contract.

This is an independent-validator contract defect. It is not a GPU, RTDL
runtime, output-correctness, worker, schedule, estimator, or timing failure.
It nevertheless occurred after worker zero and therefore terminates V11.

## Read-only postmortem

A local in-memory diagnostic changed no archived byte and generated no formal
transaction marker. It selected the expected field set by arm, required the
Direct-only marker to be exactly false, and then ran the otherwise unchanged
independent recount over the extracted archive. The diagnostic traversed all
216 causal receipts and all 108 baseline composites and reached
`PASS__ONE_GPU_GENERATION_RECOUNT_COMPLETE` with diagnostic recount digest
`e344facbfd4e87d66f1edcd22acb72855969f1affa0a440d9e38063eb5445d9b`.

This isolates the first failure and found no second inconsistency. It does not
remove the terminal marker, create a formal recount, complete V11, authorize
pooling, or authorize a performance claim.

## V12 repair boundary

The V12 behavioral repair is limited to the independent validator and its
test:

1. Keep the 19 common receipt fields mandatory for all arms.
2. Require `direct_close_phase_available=false` only for Direct receipts.
3. Forbid that Direct-only field on RTDL and PyOptiX receipts.
4. Make the synthetic full-transaction test emit the real arm-specific shape.
5. Preserve all V11 task values, outputs, schedules, arms, phase boundaries,
   warm-ups, repetitions, statistics, failure policy, and absence of a success
   threshold.
6. Modify no product runtime, provider, device program, native engine, or
   frozen generic-family core byte.

Non-behavioral evidence bookkeeping also advances the preregistration and
recount schema versions, updates their builder/validator, appends this failure
record and the V12 hostile review, and binds all changed files in the V12
source manifest. Those custody edits do not execute inside a registered
interval.

## Independent V12 execution

V12 is a new create-only full replication, not a continuation or retry of
V11. It starts from a new clean commit and output root, repeats every identity
witness before worker zero, and executes every fixed worker. V11 remains
terminal and all of its rows remain outside V12 summaries. The V12
preregistration binds the complete V11 archive and explicitly records that V11
timings were visible before V12 was frozen.

V12 can become one complete Ada-generation transaction only if its original
independent recount passes without modification. A second distinct NVIDIA GPU
architecture generation and UUID must then execute the exact V12 committed
bytes, workloads, schedules, and recount. One Ada transaction cannot complete
Goal5842. External review and consensus remain owner-deferred.

## Claim boundary

V11 provides a disclosed terminal failed transaction and diagnostic evidence
about a validator bug. It provides no accepted Goal5842 estimator, speedup,
cross-generation result, public performance wording, external review, or CGO
claim.
