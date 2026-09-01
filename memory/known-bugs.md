# Known Bugs And Failure Modes

## Goal5835 evidence is a semantic projection, not app-front-door execution

The Goal5835 receipt constructs app-shaped objects whose normalized bytes match
the inherited Goal5834-B3 fixtures, then composes the prior true-OptiX result.
It never calls the case-study execution front door or its trajectory/mesh
builders and adds zero Goal5835 GPU launches. Describe it only as
`BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE`.

The strict audit also preserves these defects: no positive complete-mesh row;
synthetic per-primitive sphere IDs; no cardinality/OR consistency check in the
app result adapter; duplicate triangle IDs can reverse a predicate-significant
edge according to caller order; absolute-path receipt fields; and permissive
non-integral ID validation. Do not repair hash-bound Goal5835 files in place.
Use a separately preregistered successor.

## Goal5835 does not preserve the author's directed-edge predicate

Goal5835 deduplicates shared triangle edges by unordered identity and preserves
one arbitrary first direction. The exact author benchmark instead enables a
strongly connected directed obstacle-edge graph because its one-sided edge ray
can start inside a hollow round curve and miss a back-face-only crossing.
Goal5835 also explicitly excludes initial overlap. Do not describe Goal5835 as
source-faithful, complete RT-CCD or a Paper App. Goal5836 terminated at A1; any
repair must use a new preregistered goal and a generic, app-agnostic
orientation/connectivity contract.

## Goal5836 A0 omits large author assets from RTDL Git by design

The exact author commit contains 132,303,954 blob bytes, mostly images, GIFs,
meshes and data. RTDL preserves a complete path/mode/OID/size/SHA-256 inventory
and a compact 203-file source capsule, not a second copy of every large asset.
Any later stage needing an omitted file must reacquire commit `bacbf77...0ac7`
and match root tree `3e5e1c...e496f` plus the inventory. If exact reacquisition
fails, stop; never replace the asset. The acquired paper is official arXiv v2,
not the IEEE publisher byte stream.

## Goal5836 Git-native capsule environment paths (fixed 2026-09-01)

The first Git-native handoff verifier enumerated `.git/**` as payload and could
not pass in the fresh clone required by its own instructions. It also retained
the minimum checkpoint's stale payload-byte receipt. The bounded repair makes
the verifier ignore only repository/venv/cache/editable-install environment
artifacts while preserving exact checks over every manifest payload and
failing on any other extra path. The root tree and independent outer-capsule
extraction both pass; an injected ordinary extra file still fails closed.
Whenever the handoff, verifier or included internal review changes, rebuild the
manifest/outer capsule and update both handoff receipt copies together.

## Curve verified executables are single-use across static prepares

`consume_verified_curve_executable` deletes the live-registry entry when a
prepared static scene is created. Reusing one `MaterializedBuiltinCurveProgram`
for a second distinct static input fails with
`curve executable live-registry identity drift`. This is intentional liveness,
not a provider failure. A normal application should prepare its one static
scene once. Multi-scene evidence runners must use separately live executables
without weakening exact identity; Goal5834-B3 uses one pre-CUDA materialization
and sequential fork-private copies.

## Repeated same-process NVRTC wrapper PTX is not raw-byte-identical

Repeated NVRTC compilation of identical trusted curve wrapper source in one
process increments PTX comment-only `callseq` identifiers. Wrapper source,
generated leaves, four compiled leaf PTX digests and compiler log remain equal,
but wrapper/composed PTX and the sealed executable SHA differ. Never predict or
whitelist a second executable identity from the first, strip the comments
post-result, or weaken the raw PTX gate. Use a fresh process or preserve the
exact live executable object when exact-byte identity is required.

## Goal5768 review authority is string-only (P0, blocks POD)

`scripts/goal5768_target_prepare.py` checks only that the claimed owner review
SHA is a 64-character string. It does not read or hash a review artifact,
verify its verdict, or bind it to the exact execution bundle and Stage-A
scope. Any forged 64-character value can satisfy the current check. Treat the
Goal5768 v9 pre-POD state as fail-closed until a reviewed successor fixes it.

## V4 target dependency identity is not closed (P1)

Goal5749 froze Python 3.12.3, Numba 0.65.1, NumPy 2.2.6, llvmlite 0.47.0,
CUDA 12.8 and OptiX 9.0. Later evidence records NumPy 2.4.4 and CUDA 12.0,
while the Goal5768 v9 bundle carries no exact wheels/debs and does not pin
CuPy or an exact driver. This is a provenance/portability defect, not evidence
that past functional outputs are wrong.

## Goal5752 historical twin is absent

The primary Goal5752 evidence archive exists and its manifest rehashes cleanly,
but the result's `archive_twin_byte_identical=true` claim cannot currently be
verified because no twin artifact or independent twin-builder input is
delivered. Preserve the primary archive and the append-only correction; do not
manufacture a retrospective twin.

## LibRTS WKT Parsing Is App-Owned, Not An RTDL Core Backlog

The prepared-phase matrix uses the app-owned `load_geometry_mbrs` parser. It
scans WKT text with Python regexes and stores Python tuple/float objects before
calling the generic RTDL prepared API. On the exact official inputs this costs
`404.471s` for `lakes.bz2` and `553.019s` for `parks.bz2`, while the prepared
query itself stays below `0.41s`. This is an app/input-front-door floor, not a
claim that the RTDL prepared index or OptiX query is intrinsically that slow.
RTDL does not own WKT parsing and must not grow a WKT parser or WKT-specific
cache lifecycle. The system boundary begins at generic columns, Arrow-like
arrays, DLPack/CUDA-array-interface views, or another format-neutral buffer.
WKT time remains visible only as app end-to-end accounting; it is not an RTDL
optimization target.

## Prepared-Phase Timing Is Not An Author Performance Denominator

Goal5485 exposes separate RTDL WKT-load, index-prepare, prepared-query wall,
and native primitive fields. The author `Query Time` field is an internal
metric with loading excluded. Even on identical official input, these fields
are not a ratio denominator until the execution model and phase boundary are
explicitly accepted by review. Keep `performance_ratio_authorized=false` and
report the values side by side.

## Large Count Gates Should Not Materialize Rows

The standard author point-contains binary exposes an integer count and does not
expose pair rows. On the largest exact `parks.bz2` input, the row-producing
RTDL gate completed the geometric work but entered avoidable page/cleanup
pressure. The corrected exact count-only gate uses the generic public
`query_aabb_index_2d(operation="point_contains")` API with
`row_output_requested=false`. Keep this distinction visible: count agreement
does not prove pair-row agreement.

## Count Agreement Is Not Pointwise Containment Agreement

The exact Figure-6 point-contains gates compare the integer result exposed by
the standard author binary. Two implementations can return the same total
while assigning different query points to polygons. Keep the six-case claim
count-level only. Goal5467's canonical 71,626-row relation match is a separate
app-instrumented representative PIP workload, not a proof for the exact
Figure-6 cases.

## Query Batching Is Not Partitioned Traversal Fanout

Prepared batches, multiple CUDA streams, and repeated-query sessions can look
similar to a fanout policy in timing summaries, but they do not reduce the
number of intersections handled by one RT ray. Do not claim Ray-Multicast or
partitioned-traversal equivalence unless primitives are assigned to disjoint
partitions, each original ray visits every partition, payload filtering
preserves exact pair coverage, and the measured route includes all fanout cost.

## LibRTS Author PIP Semantics Differ From Standard RTDL PIP

On the Goal5467 representative workload:

```text
author = 71,626 rows
standard RTDL point_in_polygon = 71,624 rows
```

The pinned author uses float32 coordinates, `(0,0)` sentinel vertices, and CUDA
fast-math PNPOLY. Do not "fix" generic RTDL polygon semantics to imitate this
artifact. For author artifact reproduction, use the app-owned
`librts_author_pip_compat.py` composition over generic RTDL AABB candidates and
keep both the standard mismatch and compatibility match visible.

## Pinned LibRTS Instance-Update Temp Buffer

Symptom:

```text
tempBufferSizeInBytes is less than tempUpdateSizeInBytes
OPTIX_ERROR_INVALID_VALUE during SpatialIndex::Update
```

Cause:

The pinned author `updateInstanceAccel()` allocates
`tempUpdateSizeInBytes` but passes `tempSizeInBytes` to `optixAccelBuild`.

Mitigation:

Apply and disclose
`Paper-reproduction-apps/librts-paper/author_patches/goal5460_fix_instance_update_temp_buffer.patch`.
Treat the evidence as patched-author, not unmodified author artifact evidence.

## Wrong POD Key

Symptom:

```text
Permission denied (publickey,password)
```

Known cause:

Using default/old SSH identity instead of:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Mitigation:

Use `scripts/current_pod_ssh.py`; never use naked SSH.

## Local CUDA Driver Missing

Local desktop OptiX probes can fail with missing `libcuda.so.1`. This is a
local environment limitation, not route correctness. Use a CUDA/OptiX POD for
OptiX gates.

## Warm/Replay Regime Overclaim

Past work repeatedly produced attractive warm/replay numbers that were not fair
fresh or paper-performance results. Always label regime and denominator.

## Signature Gates Too Weak

RT-DBSCAN showed that aggregate signatures can miss semantic mismatches. Prefer
partition equivalence or behavior-level assertions where possible.

## App-Specific Drift

Any new "generic" primitive extracted from a paper must prove genericity by
app-neutral naming, claim-boundary metadata, source scans, and preferably a
non-paper consumer/test.

## App-Artifact Parity Drift Without Stop-Loss

X-HD `-lb` showed that a long chain of goals can chase an author implementation
artifact (rows, hashes, internal streams, or option-specific state) even after
the parent paper figure is blocked.  This can produce a "success means
app-specific, failure means no reusable capability" no-win line.

Mitigation:

```text
history/internal_docs/governance_rule_stop_loss_gate_for_app_artifact_parity_2026-07-10.md
scripts/xhd_stop_loss_gate_check.py
```

Any report or call-for-review with app-artifact parity signals must include:

```text
gate_generic_capability_produced: true|false
gate_non_app_consumer: <name or none>
gate_requires_app_specific_logic: true|false
gate_downstream_consumer_reachable: true|false
```

If the gate does not pass, fail-close before implementation.

## Memory Drift

Long sessions can leave important state only in chat. This makes later agents
repeat work, forget claim boundaries, or reopen settled POD/debug issues.
Mitigation: update `AGENTS.md` and `memory/*.md` at every major handoff and
check them before trusting conversational recollection.

## X-HD Paper Branch Long Paths On Windows

The author `paper` branch has many files under `expr/for_the_paper/logs` with
very long names. A normal Windows checkout of that branch can fail with
`Filename too long` while updating the working tree.

Mitigation:

- do not rely on ordinary Windows checkout for parsing the paper-branch log
  tree;
- use `git ls-tree` / git object access for inventory;
- use a Linux/POD checkout or a purpose-built git-object parser for full
  paper-branch workload extraction.

## Stale Embedded Memory Accounting

Some X-HD hd_exec-compatible JSON artifacts carry an embedded
`RTDL.memory_accounting` object. If `xhd_memory_accounting.py` semantics change,
downstream matrix builders must recompute accounting through the current helper
instead of trusting old embedded fields.

Goal5277 exposed this with the `WL` status: older artifacts said
`estimated_from_frontier_row_capacity`, but the corrected status is
`estimated_rtdl_frontier_row_capacity_not_author_in_miss_queue` after auditing
the author source.

## LibRTS WKT Loader Dominates Large Exact Point-Contains Runs

Goal5489 measured the generic AABB query on exact `lakes.bz2` with a prepared
query wall near `0.22s`, while the LibRTS app-owned WKT-to-column loader took
`406.570s`. The existing row/regex loader and an experimental NumPy numeric
replacement are both host-side app behavior; Goal5490 did not demonstrate a
material improvement from the latter. Do not move WKT parsing into RTDL core
or report prepared-query time as end-to-end performance.

Goal5491 adds an app-owned workaround: a SHA-bound numeric AABB cache. It
avoids reparsing on later exact-input runs, but the one-time build and 286MB
storage remain costs. Do not treat cache reuse as an author-performance ratio
or promote its WKT-specific lifecycle into RTDL core.

## LibRTS Exact Batch Runner Preconditions

Goal5500 exposed two batch-runner integration hazards. A batch caller must
create each per-case author `serialize_dir` before invoking the single-case
gate; the single-case CLI does this in `main()`, but a direct batch call does
not. The batch also must pass the size+MD5 verified Goal5479 archive evidence to
the exact-input validator; the Goal5492 inventory is not a replacement for
archive verification. Keep both preconditions in the runner and its tests.

## LibRTS Range-Intersects Contract Divergence And Author Capacity Boundary

Goal5500 found two small full-input count disagreements (`parks_Europe` and
`lakes.bz2`) and one author-side CUDA allocation failure (`parks.bz2`).
Goal5501/5502 prefixes show RTDL matches an independent CPU float32 AABB oracle
on all five feasible probes, while the author diverges on four. This does not
identify the author/RTDL full-input contract difference. The author binary emits counts only, so count agreement
cannot establish pair-row equality. Keep the result as an unresolved contract
diagnostic and capacity boundary; do not silently change RTDL semantics or
call the author wrong. Any resolution requires a new, explicitly scoped
full-input or relation-level campaign.

## Author-Validity Gate Is Prefix-Only

Goal5502 must not be used to declare the author wrong on the full dataset. Its
selected generic float32 contract is validated only on Goal5501 prefixes. The
gate is a decision aid: RTDL/oracle agreement blocks author-specific core
behavior, while a future author/oracle agreement plus RTDL divergence would
require a generic RTDL fix. Full-input contract resolution still needs a
stronger oracle or author relation output.

## Goal5503 CPU/GPU Contract Distinction

The Goal5502 independent CPU float32 inclusive AABB oracle must not be treated
as a source-level implementation of the author's GPU range-intersects path.
The author uses `RayParams<float,2>::IsHit`, `nextafterf(1.0, FLT_MAX)`, and
`FLT_GAMMA(3)` `tFar` expansion in the OptiX shader. Boundary-sensitive count
differences can therefore remain unresolved until Goal5504 exercises the
actual distinction. This is a contract-knowledge gap, not permission to add
author-specific behavior to RTDL.

## Goal5504 Source-Driven Emulation Is Not Runtime Evidence

The Goal5504 Python RayParams emulation is useful for discriminating the
source-level contract, but it is not a substitute for executing the pinned
author GPU binary. Its one boundary divergence must not be used alone to
declare the author wrong, fix RTDL, or adjudicate the full inputs.

## Goal5505 Bounded Runtime Difference

The source-driven RayParams model matches the author on a five-query POD
fixture, while pre-fix RTDL misses the `one_ulp_gap_after_box_max` case. Goal5507
applies the generic float32 upper interval/tFar expansion and source-aligned
two-direction acceptance rule; a clean POD build then matches the author on
the fixture and the 8,192-pair probe. This does not establish that the large
official-input disagreements share the same cause; full-input claims remain
closed.

## Goal5506 Scalable Contract Difference

The author/source model count (21) and RTDL count (20) still differ on the
8,192-pair probe while CPU inclusive and RTDL both report 20. This confirms a
nontrivial contract difference but does not identify whether the author or
RTDL behavior is the required paper semantics. Full-input count differences
remain unresolved; do not treat this as permission for an app-specific patch.

## Goal5508 Fixed Float32-degenerate Indexed AABB Bug

The two Goal5502 official-prefix count disagreements were caused by four
indexed geometries per prefix becoming zero-width or zero-height after the
actual float32 conversion. RTDL's `1e-6` OptiX GAS padding made these records
traversable, while the author strict-validity path returned zero for the
isolated subsets. Goal5508 adds a generic strict indexed-AABB validity guard
inside the native intersection kernel and selects the correct indexed record
for forward versus backward passes. Both official prefixes and both isolated
subsets now match the author. Do not remove the guard or reclassify this as a
LibRTS-specific behavior. Remaining full-matrix/pair-row/performance claims
are still closed.

## Goal5509 Batch Checkpoint Loss

The first six-case Goal5509 runner held all results in memory. After the large
parks/lakes cases, the POD reclaimed the process before the aggregate batch
JSON was written, losing already completed in-memory results. This is an
app-runner evidence durability bug, not an RTDL semantic bug. Use per-case
checkpoint files for large official workloads; never aggregate a long batch
only at process exit.

## Goal5511 checkpoint discipline

Goal5511 avoids the prior batch-loss bug by writing one JSON result per case
before proceeding. The extraction manifest contains 22 selected members (the
verified earlier geometry/query members plus the four `.001` query members).
Do not use the aggregate selected-member count as a complete archive-matrix
claim; it is only provenance for the bounded cases actually executed.

## Goal5512 Author Capacity And Workspace Quota Boundaries

The large parks workload reaches a pinned-author CUDA allocation failure even
with substantial host memory available. The lakes workload first hit a
workspace output-stream/quota path and then succeeded when serialized under
`/tmp`. Preserve these as separate author/environment statuses. Never infer
RTDL semantic failure from an author capacity failure, and never report the
temporary-path retry as a performance improvement.

## Goal5513 Workspace Output Quota

Large author runs can fail with a Boost archive output-stream error when the
serialize directory is under the workspace quota path even though the shared
filesystem has free capacity. A `/tmp` serialize directory is a valid
evidence-preserving workaround for same-input correctness runs. Record the
path change and never treat it as a performance result.

Goal5514 confirms that the parks.bz2 CUDA allocation failure persists even
when the serialize path is moved to `/tmp`; it is therefore not merely a
workspace output-stream issue. Keep it classified as an author capacity
boundary and do not add RTDL app-specific behavior to compensate.

## LibRTS exact query availability and capacity (2026-07-12)

The verified range-intersects evidence currently has five count matches and
one explicit author CUDA allocation failure for the `.01 x 10000` family.
Goal5515 shows the two historical mismatches no longer reproduce after the
generic indexed-AABB validity correction. Do not infer missing query members
from the operation inventory alone: staged POD extraction currently exposes
four `.001 x 10000` query files, and absent members must be verified from the
archive or separately extracted before a new run.

Goal5517 also confirms that `/workspace` may report `Disk quota exceeded`
despite large shared-filesystem free space. Quota-safe exact extraction under
`/tmp` works and preserves hashes, but must be documented as an environment
workaround rather than an algorithmic or performance change.

## Goal5749 causal attribution and PTX-composer hazards (2026-08-11)

Do not infer that OptiX rejects a linkage mechanism from a run containing an
independent NumbaEnv or program-group confounder. The first Goal5749 conclusion
was overbroad; a legal two-module construction works on Home.

The trusted composer must reject ambiguous extern blocks, target or ABI drift,
duplicate leaf identities, referenced or multiple NumbaEnv state and new
external dependencies. It strips leaf `.file`/`.loc` information, so composed
leaf source-line debugging is unavailable. Never pass original user callable
state or user PTX through this boundary.
