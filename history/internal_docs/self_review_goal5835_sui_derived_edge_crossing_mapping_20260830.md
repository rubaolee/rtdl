# Strict self-review — Goal5835 bounded Sui-derived mapping

## Verdict

`P0=0 / P1=0 / P2=3 / P3=2`

Accept Goal5835 as an implemented and exactly bound application mapping. Do
not call it a Paper App, full RT-CCD implementation, prospective generalization
result, third-party application, usability result or performance result.

## What would make this result fake?

### If the app mapping generated different bytes from the GPU experiment

It does not. All 11 reconstructed public static/query commitments equal the
pre-frozen B3 worker commitments. The case-study receipt refuses any different
fixture authority, worker input, B3 raw receipt or B3 evaluation hash.

### If the application worker secretly used the CPU oracle

It does not. `execute_registered_problem` only constructs public inputs,
prepares the supplied public materialization, and calls `prepared.execute`.
The independent oracle is imported only by the post-result receipt builder.
The underlying B3 worker had no expected output or pairwise geometry.

### If old GPU evidence were relabelled as a new Goal5835 run

It is not. The result explicitly reports
`new_goal5835_gpu_launch_count: 0` and
`inherited_b3_true_optix_launch_count: 33`. Goal5835's new evidence is exact
mapping equivalence plus a second independent oracle, not another provider
measurement.

### If “Sui-derived” meant “we reproduced the paper”

It does not. The result says `NOT_A_PAPER_APP` and
`SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES`. Exact source provenance,
paper-source input and author-code comparison are absent and assigned only to
Goal5836.

## Open P2 findings

1. **No paper-source or author comparison.** The present mapping implements the
   conceptual sphere-trajectory/obstacle-edge core, but it has not yet been
   checked against a pinned Sui source fixture or the authors' implementation.
2. **The positive GPU cases use registered edges, not complete meshes.** Mesh
   deduplication is implemented and structurally tested; the one complete
   triangle fixture is the deliberate face-interior miss. Goal5836 needs a
   paper/source-derived mesh case containing a robust positive edge crossing.
3. **No new end-to-end app-wrapper hardware run.** Exact public commitments
   compose the mapping with B3's executed bytes, which is sufficient for this
   bounded mapping goal. A reviewer can still reasonably ask for the actual
   case-study front door on modern RTX; that remains a Goal5836 gate.

## P3 findings

1. The current one-u32 native identity uses globally unique path-segment IDs;
   sphere identity is reconstructed from the application mapping receipt, not
   carried as a separate device-visible field. This is harmless for a Boolean
   result but is not a general multi-sphere identity ABI.
2. Internal receipts contain absolute workspace paths. They are internal
   custody records and must not enter the double-blind artifact without
   sanitization.

## Tests and reconstruction

- 102/102 Goal5833--5835 tests pass.
- Goal5835's focused mapping/oracle suite passes 6/6.
- 11/11 static/query commitment pairs match B3.
- 21/21 active-set query/capsule decisions match.
- Two complete Goal5835 receipts are byte-identical at `ae370da1...`.

There is no P0/P1 defect within the declared mapping scope. Goal5836 remains
unauthorized until a separate exact plan freezes source provenance, author
comparison inputs, modern-RTX environment and unconditional outcome branches.
