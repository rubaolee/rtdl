# Final self-review: V4 paper applications versus public PyOptiX

Date: 2026-09-08 America/New_York.

## Decision

`ACCEPT_AS_VALID_ADVERSE_POST_LOADER_ROUTE_EVIDENCE__REJECT_RAW_DOMAIN_END_TO_END_OR_BROAD_CLAIMS`

The frozen first-batch experiment is internally valid at its registered
post-input-loader method-route scope. It does not show that V4 is competitive
with a competent public PyOptiX implementation across paper applications. It
does not measure raw-domain end-to-end application cost, use operation-identical
device programs for Particle, or complete the registered nine-application
denominator. These are research results and scope limits, not infrastructure
failures.

## Exact authority

- Final source: commit `c5c8be48b743aa001e9c16c3344cc97c200600d1`,
  tree `e3bb0001f4c2d1e3171ab0431c0479500dfc7136`.
- Final native library SHA-256:
  `719ac27d884c93634f8b3a9ed2936b95d6231fccb437da7da62448adf2ec15ba`.
- Machine: NVIDIA RTX A4500, CC 8.6, UUID
  `GPU-5dbda20d-af85-650e-7250-10b265a77143`, driver `550.127.05`.
- Frozen harness preflight: 28/28 focused tests PASS in the clean pod checkout.
- Untimed final output gate: 8/8 fresh workers PASS.
- Formal transaction: 192/192 fresh workers PASS, 0 retry, 0 discard.
- Controller source/config end-state checks: PASS.
- Independent recount: `RECOUNT_MATCH` over all 192 worker files.
- Formal summary SHA-256:
  `67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf`.
- Recount SHA-256:
  `667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64`.
- Compact evidence archive SHA-256:
  `2d7dc4413639e46994ca74251d230b74d5e9d775a23b457336cb00f9df80f4ff`.

The formal source was committed, pushed, freshly built, configured, and
successfully dry-run rehearsed before the 2026-09-08 00:00 ET executable
freeze. Its formal transaction also completed before the freeze. No post-freeze
executable repair is permitted.

## Review questions

### 1. Are the comparisons valid?

Yes, only for the registered post-loader application routes. Both arms consume
the same frozen derived-input identity and return the same complete public
output. Each timed result is accepted only after exact output/status checks.
Process isolation, paired order, repetitions, warmups, and the block estimator
are symmetric and preregistered. Public PyOptiX does not call a private RTDL
native path.

The excluded loader includes application work, not only disk I/O. It loads
pre-encoded Particle arrays, constructs Triangle's degree-oriented filtered and
deduplicated CSR, and loads LibRTS index caches while converting WKT queries.
Therefore the original broader requirement to time all required domain encoding
was not fulfilled. The registered `complete` result begins after that work and
must be called a post-loader method setup-and-execution endpoint.

The device programs are semantically matched for the frozen outputs, not
byte-identical or operation-identical. Most importantly, V4 Particle enumerates
any-hit candidates and performs canonical selection before one logical
closest-hit call, whereas PyOptiX disables any-hit and uses native closest-hit.
`first_result` also excludes only work already completed by `_prepare_case`;
application-internal setup remains timed. For Triangle, both arms rebuild
per-segment geometry/GAS, while V4 additionally rebuilds its composed module,
program groups, pipeline, and SBT inside every segment execution and PyOptiX
reuses those prepared objects. Each timed execute also contains the registered
adapter-level synchronous output/oracle and status checks, digest work, and
compact evidence projection; it is not isolated native-runtime latency.
This is an application-route comparison, not a controlled measurement of one
compiler pass. The table must not be described as intrinsic DSL overhead.

### 2. Is the PyOptiX baseline competent?

Yes at this scope. It owns public PyOptiX context, module, program groups,
pipeline, SBT, GAS, launch, device buffers, status, continuation/reduction,
synchronization, and output materialization. PTX is compiled once before worker
zero and hash-bound; compile time is diagnostic rather than repeatedly charged.
Triangle and LibRTS reduce on the device. Particle returns the full 5,000 by 3
U32 matrix. No host-only straw baseline is used.

This means `complete` is not a compiler-time-symmetric endpoint: PyOptiX uses
prebuilt PTX while ordinary V4 Particle and Triangle compilation occurs during
their method preparation. That difference is part of the measured public-route
cost and must be disclosed, not interpreted as a controlled compiler comparison.
Triangle's PyOptiX device source is handwritten CUDA/OptiX compiled to PTX; it
is not a second Numba implementation.

### 3. What useful capability does RTDL add?

RTDL lets these applications select supported typed callback/result families
without writing the corresponding OptiX context/module/program-group/SBT/GAS
and launch plumbing. It verifies callback/type/effect/physical-schema or closed
algebra authority as applicable, manages prepared ownership, checks public
result and failure metadata, and returns evidence that real OptiX traversal was
observed.

This is concrete language/runtime functionality. It is not proof that RTDL
automatically discovers the RT formulation, verifies the whole application, or
is easier for independent users. The latter requires authoring evidence absent
from this packet.

### 4. How much application work remains?

- Particle still owns the mesh-to-face/adjacency mapping, strict-interior
  transition meaning, queries, output schema, and oracle. RTDL compiles and
  executes the project standard-library built-in-triangle callback protocol;
  this is not an independent user-authored callback study.
- Triangle still owns RT-2A1 selection, CSR segmentation, geometry production,
  ray weights, cross-segment accumulation, and graph oracle. RTDL executes the
  general Numba-leaf callback ABI, while CuPy performs checked-U64 weighted
  device reduction.
- LibRTS still selects the point/range algebra and supplies indexed/query
  columns plus expected counts. RTDL executes a fixed generic AABB-count
  specialization. This row is not evidence for arbitrary callback lowering.

The implementation therefore demonstrates a mix of callback generation,
generic partner composition, and trusted closed-family specialization. It must
not be reported as one uniform fully generated route.

### 5. Did the final optimization solve the performance debt?

No. It solved one real transfer debt but not the dominant route cost. The final
generic block reduction preserves per-query U32 counts, reduces them into one
device U64 scalar, and downloads eight bytes. It contains no LibRTS or
application identity. Exact output and all transaction gates pass.

Point prepared changed from `42.739321x` at `df7db5c38` to `38.466788x`; range
prepared changed from `36.862044x` to `39.083145x`. Cross-transaction movement
is post hoc, not a significance result. In the final transaction, V4 remains
about 8.9-9.1 ms versus 0.23 ms for PyOptiX. The removed 400,000-byte D2H column
and CPU loop were not the dominant cost.

### 6. What is the strongest performance conclusion?

All 12 final endpoint ratios are above one. Triangle prepared is the closest
steady route at `1.379226x`. LibRTS complete is close only because both arms
pay seconds of preparation: point is `1.311772x` and range is `1.079542x`.
Particle remains `37.927723x` slower prepared. Full values and block ranges are
in `RESULTS.md`.

The evidence supports an honest cost characterization and pinpoints physical
route debt. It does not support a positive V4/PyOptiX performance claim.

### 7. Is nine-application coverage complete?

No. Three of nine applications, represented by four operation units, have a
valid frozen comparison. RTNN, X-HD, RT-DBSCAN, RayDB, Spatial RayJoin, and
RT-BarnesHut lack a complete frozen competent PyOptiX owner. The hard freeze
prevents implementing those missing owners for this submission. They remain
visible as unexecuted matrix rows.

## Mechanism assessment

The next credible causes are supported by source comparison but not by a
formal causal ablation:

1. Prepared Particle still crosses NumPy/ctypes/native layout boundaries,
   performs seven query-column H2D copies, and downloads complete output plus
   diagnostics/status. More fundamentally, V4 enumerates all candidate hits for
   canonical tie/boundary selection and then invokes one logical closest-hit
   leaf, while PyOptiX disables any-hit and runs native closest-hit. Both arms
   upload queries, and no retained ablation separates these costs.
2. Triangle reconstructs bounded device geometry by segment in both arms. V4's
   general Numba-leaf route additionally performs native prepare/execute/destroy
   per segment, including GAS plus module/program-group/pipeline/SBT construction;
   PyOptiX runs handwritten CUDA/OptiX PTX and retains those objects while
   rebuilding only per-segment GAS. Its 1.38x prepared result is a complete route cost, not
   solely a callback dispatch or language-code-generation cost.
3. V4 LibRTS uses a general multi-operation AoS kernel and an indexed GAS built
   with `ALLOW_RANDOM_VERTEX_ACCESS` but no `PREFER_FAST_TRACE`. It synchronizes
   after traversal, then launches reduction and synchronizes through scalar
   download. PyOptiX uses a compact SoA kernel, `PREFER_FAST_TRACE`, and chains
   traversal, reduction, scalar/status copies on one stream before one sync.
4. Python-side LibRTS execute no longer normalizes/uploads the 100,000 queries
   or loops over their counts. Its remaining guards, small hashes, receipt
   projection, and ctypes call are real but do not by inspection explain the
   full approximately 9 ms V4 time.

These mechanisms define future engineering work after the submission freeze.
They may not be silently repaired or tested in the current candidate.

## Submission consequences

- The manuscript may state that a frozen first-batch experiment found exact
  output parity and measured substantial post-loader route-dependent cost,
  provided it includes all adverse rows, exact starting representations, path
  classes, hardware, estimator, and coverage denominator.
- The manuscript may use this result to motivate runtime/lowering limitations.
- It may not claim raw-domain end-to-end application timing, operation-identical
  Particle algorithms, lifecycle-identical Triangle execution, cold-start or
  pure-launch first-result timing, broad near-PyOptiX performance, speedup,
  nine-app completion, arbitrary callback efficiency, or demonstrated ease of
  use.
- Existing Goal5848 near-Direct observations remain separate synthetic-task
  evidence. They cannot replace or override these application results.
- External final-byte review, paper integration, artifact review, authenticated
  form checks, upload, receipt, and submission authorization remain pending.

## Residual verification debt

A broader unrelated 29-test selection previously reported 26 passes and three
stale failures: two tests require absent historical v2 documents and one
expects an obsolete Embree claim string. No final-source file involved in
those assertions changed in the `c5c8be48b` reduction patch. This is retained
test-suite debt, not silently relabeled as a green full regression.

The evidence packet and exact hashes are in `EVIDENCE_INDEX.json`. That index,
the controller summary, and the independent recount are the numerical
authority; this narrative does not replace them.
