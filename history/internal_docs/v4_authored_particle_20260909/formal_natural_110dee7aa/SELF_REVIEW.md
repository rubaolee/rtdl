# Self-review: Particle setup-remediation successor

Date: 2026-09-09

Verdict:
`INTERNAL_ACCEPT_EXACT_PARTICLE_PREPARED_AND_SETUP_RESULT__LEAD_REVIEW_PENDING`.

## Passed checks

- Exact source commit/tree, GPU, native library, PyOptiX PTX, input, oracle and
  output identities are bound.
- The new GPU helper and packed-query runtime are app-neutral: no Particle
  name, dataset identity, expected result, query-count dispatch or
  cell-transition formula selects the path.
- The original split-column prepared-query ABI remains available when the new
  packed ABI symbol is absent.
- The packed query object owns one immutable bytes-backed snapshot, so caller
  mutation after admission cannot alter the native batch.
- The native batch token and pinned output pointer are published only after
  allocation, upload, GPU validation, capacity preparation and registry insert
  succeed.
- A 36-test focused suite passed on the pod, including packed-ABI discovery,
  partial-ABI rejection, immutable ownership, app-neutral source inspection,
  fallback ABI behavior, compiler batch isolation and Particle API tests.
- The native library built from a clean exact commit and exported the new ABI.
- A valid 5,000-query public smoke produced the exact output and
  `optix_traversal_observed` role evidence.
- An injected zero-direction row was rejected before usable batch admission.
- The pre-worker-zero 160M RTDL compatibility probe and three independent
  PyOptiX calibration workers produced the exact output.
- Eight fresh-process paired blocks used four RTDL-first and four PyOptiX-first
  orders. All 16 workers, 48 samples and 16 warmups are retained with zero
  retry, discard, timeout or wrong output.
- A separate recount script verified all 117 archive members, build artifacts,
  source closure, commands, streams, worker results, ledger and statistics.
- A second invocation from a new detached clean Mac worktree reproduced every
  recount field except the expected machine-local absolute archive path.
- A post-formal same-source/toolchain reconstruction exported 13 RTDL compiler
  artifacts. Its program and executable identities match all eight original
  RTDL worker records, and its 160M replay reproduced the formal output digest
  with a full traversal/lifecycle receipt.
- A later untimed replay saved the complete 1.92 GB observed output together
  with query/oracle/base data, deployed artifacts, commands and a standalone
  verifier on the RunPod network volume. The verifier rehashed all 45 payload
  files and compared every output row to the transformed independent oracle.

## Reviewer-style attacks checked

### The improvement is app-specific native code

Rejected for the new mechanism. It accepts a generic built-in-triangle ray-row
shape and performs only row validation and layout conversion. The app still
defines face-first meaning outside the engine. This does not erase older
app-shaped code elsewhere in the repository and is not evidence of a fully
app-independent engine.

### RTDL wins by weakening the PyOptiX baseline

Rejected for this transaction. PyOptiX uses its public prepared owner,
precompiled PTX, resident inputs, native closest-hit path, complete contiguous
AoS output and exact validation. The identical PTX bytes are rebuilt into a
manifest bound to the successor commit.

### RTDL hides output transfer or validation

Rejected for the prepared endpoint. Both arms return the complete 1.92 GB
output and perform exact public validation inside every timed action. The
controller also binds the complete output digest.

### The setup comparison uses unequal input state

Not observed in the worker. Both setup intervals start after the common domain
input is loaded into memory and end with reusable device-resident query state.
The implementations have different internal layouts and API work, which is the
measured implementation cost rather than an omitted common phase.

### The result was selected after seeing RTDL

Rejected. The 160M scale and order schedule predate this successor. The freeze
step retained one RTDL compatibility probe and three PyOptiX calibration rows,
then wrote an immutable preregistration before formal worker zero.

## Adverse facts and residual risks

- The first packed-ABI commit failed the physical-binding contract because the
  frozen runtime source hash was stale. The exact failure is retained; the
  successor changed the binding rather than weakening the contract.
- An initial invalid-input diagnostic attempted to mutate a read-only test
  array and failed before invoking RTDL. A copied array was then used and the
  native rejection passed. The first diagnostic is not product evidence.
- The full `goal5756_v4_builtin_triangle_runtime_test` module cannot currently
  be collected from this checkout because a referenced historical
  `goal5753_held_out_particle_tracking_exam_evidence_20260811.tar.gz` fixture is
  absent from the repository. The new focused compiler test and all directly
  affected modules pass, but this historical fixture gap remains.
- The 160M prepared action remains about 0.35 seconds, below the preferred
  one-second natural-action target.
- No formal peak-memory measurement exists. Device transpose reduces host
  duplication but temporarily adds a 4.48 GB packed device buffer; memory cost
  could matter on smaller GPUs.
- `cudaMemcpy` and validation status synchronization remain in setup. The
  optimization does not make setup asynchronous or zero-copy.
- The result is from one RTX 4000 Ada GPU with unlocked clocks. It is not a
  cross-generation or CPU-invariant authority.
- The archive omits the multi-gigabyte input/output arrays and depends on their
  exact external manifests and hashes for data custody.
- The original archive also omits RTDL generated leaf/wrapper/composed bytes
  and every timed worker's full traversal receipt. Timed workers retained
  compact execution evidence and executable/program identities. The separate
  post-formal reconstruction is identity-matched but is not original timed
  evidence and is not pooled with the formal transaction.
- The complete post-formal output and multi-gigabyte data handoff are not in
  Git. Their RunPod network-volume availability depends on the owner retaining
  that volume and does not become original timed-worker custody.
- Lead independent review and external review have not occurred. The pod and
  Mac recounts are tool-level reconstructions performed under the same
  engineering effort, not independent reviewer votes.

## Rejected shortcuts

- No protocol hash, target identity, output byte, D2H transfer, status check,
  oracle check or worst block was removed.
- No prior failed transaction or diagnostic sample was pooled into formal data.
- No query was duplicated and no sleep, repeated action or weakened baseline
  was used to increase duration.
- No app name, query count, input hash or expected output selects the new
  native path.
- No public, paper or portfolio-wide performance claim is authorized here.

## Next gate

Lead review must verify the new source, original archive and separately labeled
post-formal supplement, rerun the independent recount from a foreign clean
checkout, and decide how narrowly the paper may use this result. The reviewer
must not treat the reconstructed receipt as a retained timed-worker receipt.
Cross-generation replay and peak-memory evidence are desirable but remain
separate work, not silently satisfied by this transaction.
