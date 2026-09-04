# Goal5843 Pre-Execution Internal Hostile Self-Review

## Verdict

`ACCEPT_FOR_PREREGISTRATION_AND_PREMEASUREMENT_COMMIT`

## Attacks Resolved Before Worker Zero

- **Cherry-picking:** all 18 blocks, all three arms, both tasks, and all adverse
  rows are mandatory. There is no performance threshold or outlier deletion.
- **Changed output:** each task fixes one input digest and one public-output
  digest shared by all arms. Triangle compares the checked-U64 scalar only;
  relation compares all canonical rows.
- **Warm/cold ambiguity:** first and steady use separate fresh processes.
  Steady reuses prepared targets and queries after exactly eight warmups.
- **Shifted input cost:** RTDL's initial query upload occurs in first execute,
  while Direct/PyOptiX place it in prepare. Setup and first are therefore
  descriptive only; receipts expose the difference rather than normalize it
  away.
- **Compilation laundering:** every setup phase remains recorded. Only the
  content-addressed RTDL leaf cache is installed before worker zero and sealed
  read-only; it is not called free compilation or equivalent provider work.
- **Private fast path:** only the ordinary public check-on front door is legal.
- **Disappearing pod implementation:** exact native, Direct, and pinned
  PyOptiX implementation bytes are copied create-only before worker zero and
  checked against the execution authority after archive download.
- **Unsafe or substituted archive:** the local verifier rejects path traversal,
  links, special files, duplicate normalized names, and multiple archive roots;
  it then recomputes the full result and requires byte-identical pod/local
  recounts.
- **False RT evidence:** the RTDL triangle execution receipt must prove one
  OptiX launch and zero reused-input upload/GAS-build work.
- **Oracle contamination:** expected-output comparison occurs after each timed
  complete execution. Required status and public output transfer remain inside.
- **Asynchronous timing:** Direct executes `cuStreamSynchronize(0)` in its
  pinned launch helper; PyOptiX synchronizes its launch stream; RTDL returns
  only after its required control/scalar download. Every timer therefore ends
  after the required GPU work and public output transfer, not after enqueue.
- **Result-dependent repair:** after worker zero, any defect terminates this
  transaction and requires a new preregistration.

## Residual Threats Accepted, Not Hidden

- The task set has two synthetic frozen workloads and cannot establish broad
  language or application performance.
- Direct, PyOptiX, and RTDL have different implementation internals. The study
  matches semantic input/output and phase definitions, not every hidden
  instruction.
- One hardware run is an internal bounded result, not cross-generation or
  hardware-independent evidence.
- GPU clocks and power state are not manually locked. Balanced within-block
  arm order and per-process warmups reduce but do not eliminate temporal or
  thermal confounding.
- The inherited Direct executable emits a Goal5842-named raw transport schema.
  Goal5843 treats that string only as a hash-bound transport interface and
  wraps it in its own authority and receipt schema.
- External review is unavailable while traveling. No public/manuscript claim
  may be made until an independent review is preserved later.
