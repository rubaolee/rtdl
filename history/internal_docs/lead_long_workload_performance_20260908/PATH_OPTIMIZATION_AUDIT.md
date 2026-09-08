# Prepared application-path optimization audit

Date: 2026-09-08. Reviewer: lead architecture subreview. This is a source audit and an implementation handoff, not a GPU experiment, causal timing attribution, or acceptance of a successor executable.

## 1. Scope, identity, and recommendation

The new user-authorized performance work permits a separately identified successor within that work. It does not rewrite the executable freeze or transfer success to old evidence. M/E/F2 and the first-batch `c5c8be48b743aa001e9c16c3344cc97c200600d1` transaction remain immutable. The main AI exclusively owns implementation. This audit changes only this document and runs no tests, compilation, or GPU work.

The inspection started at HEAD `2aad4f022386811789a56091d824bd41733ba4f6`. The eleven primary implementation/owner files listed in the final identity section were compared with `c5c8be48b...` and had no differences at inspection. Source facts below therefore describe the recorded first-batch path, not a new performance repair. This is a live working tree; a successor must record its own exact commit and executable identity.

**Recommended order, updated after the lead's profiling report:** first isolate and remove repeated filesystem path resolution from the trusted loaded-provider audit path (Section 8), before adding a native ABI solely to remove Python audit overhead. Next retain Graph's immutable compiled pipeline across segments while keeping its current general-leaf entries; collapse LibRTS's ordered traversal/reduction/copy work onto one stream and investigate GAS flags if measured native work warrants it; remove Particle's redundant host materialization and synchronous-copy boundaries while keeping its canonical collector. A more compact LibRTS native count implementation and a different Particle traversal strategy are separate lowerer changes, with stronger semantic validation requirements. No source-only argument predicts how much of 38x/39x/1.38x each change will remove.

The retained [RESULTS.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/v4_paper_apps_pyoptix_20260907/RESULTS.md) and [APP_MATRIX.md](/Users/rl2025/rtdl_v4_restricted_python_design/history/internal_docs/v4_paper_apps_pyoptix_20260907/APP_MATRIX.md) report:

| Registered prepared unit | V4 / public PyOptiX | Ratio | Actual selected route |
| --- | ---: | ---: | --- |
| Particle transition | 18.035 / 0.476 ms | 37.927723x | Standard callback compiled to four leaves; compiler any-hit collector; logical closest-hit/miss invoked from raygen |
| Graph RT-2A1 | 602.856 / 437.096 ms | 1.379226x | General Numba-leaf device-column count, per-segment native prepare/execute/destroy, CuPy checked weighted reduction |
| LibRTS point count | 8.916 / 0.230 ms | 38.466788x | Closed AABB count authority, resident prepared queries, fixed native traversal and scalar reduction |
| LibRTS range count | 9.140 / 0.233 ms | 39.083145x | Same fixed owner with range-contains operation |

These are post-input-loader method routes. Particle retained 32 prepared calls per worker, other units four, after one warmup. Complete/first/prepared have different work boundaries. Historical query residency, buffer reuse, and scalar reduction repairs have already happened: proposing them again as absent work would misdiagnose the recorded final route.

## 2. Graph: eliminate repeated execution-object construction first

### G1 — Reuse immutable module/program groups/pipeline/SBT; retain per-segment GAS

**Observed cost layer.** `PreparedSegmentedTriangleCountingV4.execute` regenerates segment geometry and calls the executor for each segment: [app:214](/Users/rl2025/rtdl_v4_restricted_python_design/Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py:214). `VerifiedTriangleDeviceColumnCountExecutor.execute_segment_unsealed` calls native prepare at [runtime:728](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_device_runtime.py:728), execute at 743, and destroy in `finally` at 822. Native `prepare_v4_triangle_reduction_device_columns_count_callback` builds the segment GAS and then calls `build_pipeline` at [native:4731](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:4731). `build_pipeline` creates a fresh module at [core:1959](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_core.cpp:1959) and allocates/packs/copies its three SBT records at 2075–2099. In this producer those records are header records; per-segment traversable and pointers enter launch parameters separately. The PyOptiX owner creates its pipeline once in prepare at [baseline:141](/Users/rl2025/rtdl_v4_restricted_python_design/experiments/v4_paper_apps_pyoptix/triangle_owner.py:141).

**Repair.** Introduce an owner-local retained compiled target object for exact composed PTX, producer specification/entry names, OptiX/CUDA context and target identity. Segment owners borrow that object and own only current GAS, geometry, launch buffers and per-execution status. Keep reference lifetimes explicit; destroying one segment must not destroy a shared pipeline. First construct an owner-local cache rather than an unbounded process-global cache.

**Must preserve.** The current device-column route intentionally binds `v4_rtdlexe_triangle_diagnostic_producer_spec()` — those are the general callback entries. [Native:4750–4755](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:4750) explains why the product entries with null `fast_control` previously represented an empty-launch hazard. Pipeline reuse is not permission to select the product intrinsic. GAS construction/segment generation remain charged to execute unless a separately disclosed endpoint gives both arms equivalent prepared-geometry ownership.

**Acceptance.** On repeated segments, the exact pipeline/program/SBT identity stays fixed while GAS/launch identities follow each segment. Changing PTX, entry names, resource/payload specification, context/device, or target must cause rebuild or rejection. Validate multiple unequal segments, zero-hit segments, close/use-after-close, prepare failure, and failure after one successful segment. Per-segment actual launch evidence, complete scalar, and checked segment sum must remain correct; no stale GAS/pointer may be reused solely because counts match.

### G2 — Reuse scratch capacity and stop defeating the allocator

**Observed cost layer.** [Native:5693–5702](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:5693) allocates seven f32 query columns plus errors/events/status/counters for every segment, although the prepared native object already has some buffers. It packs incoming f64 columns, synchronizes, and reads the pack error at 5718–5725. The app explicitly calls `cp.get_default_memory_pool().free_all_blocks()` after every segment at [app:251](/Users/rl2025/rtdl_v4_restricted_python_design/Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py:251).

**Repair.** Retain bounded scratch buffers in the reusable owner, growing on demand with checked capacities and releasing on close. Reuse parameter/status/counter allocations; reinitialize all execution-dependent contents. Let CuPy retain a bounded pool or explicit scratch allocation, rather than releasing all cached blocks inside the timed loop. Preserve bounded segmentation and record peak memory so improved reuse does not become hidden unbounded materialization.

**Acceptance.** Alternating small/large/small batches must not expose stale data; capacity growth failure must return no result and leave a defined owner state. Buffer identities may persist, contents and status must be reset each execution. Wrong device, noncontiguous columns, count/weight mismatch and invalid f64→f32 rays remain rejected. Report peak device memory and per-call allocation count separately from elapsed time.

### G3 — Compact status transfer and stream the checked reduction only after G1/G2

**Observed cost layer.** [Native:5761–5774](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:5761) synchronizes, reads the event count, downloads every `V4FormalLaunchStatus`, scans it, and downloads counters. Per-ray output itself remains on device. [Runtime:751–774](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_reduction_device_runtime.py:751) checks lifecycle counters and invokes the existing CuPy checked-U64 reduction. [Checked reducer:152–175](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_checked_u64_device_reduction.py:152) enforces the observed maximum/domain and multiplication/sum bounds; summary copying occurs at 231. `execute_segment()` then seals receipts before returning at runtime:831–850.

**Repair.** If G1/G2 leave material cost, reduce status on device to a compact fail-closed summary and chain traversal/summary/reduction on an explicitly owned stream, with final completion before publication. This changes native control and must preserve error discovery; it is not removal of checking. Do not substitute unchecked `cp.sum(per_ray * weights)` or replace general-leaf counting with an intrinsic under the same route label. Fusing the reduction into raygen is another target implementation requiring its own guard and validation.

**Acceptance.** Inject failure in early and late query rows, nonzero event emission, inconsistent role counts, observed count beyond its declared bound, checked multiplication/sum overflow, and failed reduction/stream completion. Each must suppress the public scalar. Keep `REQUIRE_SINGLE_ANYHIT_CALL`, physical ignore after accepted events, exact all-hit coverage and the graph's checked host sum across segments. Existing source tests do not prove GPU equivalence of a new summary or fused kernel.

## 3. LibRTS: residency is already implemented; audit the native count path

### L1 — One ordered stream, one final completion boundary

**Observed cost layer.** [Prepared owner:118–134](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_aabb_relation_count_lowering.py:118) already binds one immutable query batch. [Native:18072–18100](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_workloads.cpp:18072) reuses query data, per-query count scratch, parameter scratch and scalar scratch. In contrast, `launch_aabb_index_count_pass_optix` synchronizes at [17815](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_workloads.cpp:17815), followed by `reduce_device_u32_sum_u64` whose scalar download is blocking at 17575. The PyOptiX owner chains launch, U64 reduction and asynchronous scalar/status copies in one stream, then synchronizes once at [baseline:334–375](/Users/rl2025/rtdl_v4_restricted_python_design/experiments/v4_paper_apps_pyoptix/librts_owner.py:334).

**Repair.** Thread an explicit owner stream through memset, parameter upload, traversal, reduction and result/status copies. Enqueue the reduction after traversal in that stream; wait once before returning and before closing the traversal audit. Existing `launch_aabb_index_count_pass_optix_async` at native:17818 is a useful implementation reference, not a drop-in cure: its temporary launch-parameter ownership and upload semantics also need to be respected. Keep buffers alive through stream completion and clean up on asynchronous error.

**Acceptance.** Compare exact point/range scalars on both repeated and varying batches. Wrong operation/query layout, closed owner, cross-process/thread use, empty inputs, invalid coordinates, native launch failure and reduction/copy failure must retain defined rejection behavior. Failed work must not return a previously computed count. The host scalar must be ready before public return, and nonce-bound traversal evidence must describe the completed launch. No query-upload saving may be claimed for a path already using prepared resident queries.

### L2 — Match sensible GAS policy before redesigning the kernel

**Observed cost layer.** `PreparedAabbIndex2DOptix` builds with `ALLOW_RANDOM_VERTEX_ACCESS`, optionally `ALLOW_UPDATE`, but without `PREFER_FAST_TRACE` at [native:17587–17615](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_workloads.cpp:17587). The baseline uses `PREFER_FAST_TRACE` at [baseline:253](/Users/rl2025/rtdl_v4_restricted_python_design/experiments/v4_paper_apps_pyoptix/librts_owner.py:253).

**Repair.** For this long-lived prepared index, evaluate a trace-preferred build policy with target/build identity recorded. Preserve required flags, bounds and update/refit contracts. Do not silently change the default of every generic mutable AABB owner if a narrower immutable prepared-count owner suffices.

**Acceptance.** Exact boundary predicates and counts are unchanged; update-enabled owners still either support correct update/refit or explicitly reject the unsupported policy. Report build time, memory, and prepared time together: more costly setup can be acceptable for long reuse but is not free. A flag change alone does not establish that it causes the full historical gap.

### L3 — A compact count-only native lowering is plausible but a new implementation

**Observed cost layer.** [Native raygen/IS:17369–17462](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_workloads.cpp:17369) handles three operations, AoS records, intersect passes and optional row collection. Point/range counts use exact predicates followed by per-query U32 atomic increments. The PyOptiX source uses compact SoA data and a count-only route. The new scalar reducer already avoids downloading the 100,000-entry count column; it uses block reductions and one atomic add per nonzero block, not one global atomic per hit.

**Repair.** After measuring L1/L2, a generic closed point-contains/range-contains backend may specialize away unrelated branches and use SoA columns, while preserving the same fixed algebra, normalization and inclusive boundary predicates. Select by admitted operation/layout identity, never by app name, dataset or expected count. Preserve the broader original route for row materialization/range-intersects. Do not replace per-query accumulation with one globally contended atomic per hit merely to avoid the reduction.

**Acceptance.** Differentially validate old V4, new V4, competent PyOptiX and an independent small-input oracle on reversed bounds/normalization, boundary-touching containment, degenerate admissible boxes, duplicates, zero/all hits, dense overlap and both operations. Check the supported numeric domain: per-query U32 counts and total U64 accumulation must be justified by admitted cardinality/delivery bounds, or reject/raise overflow. Preserve complete scalar rather than early terminating at any hit. This is a separately identified trusted native lowering, not additional evidence of arbitrary callback compilation.

## 4. Particle: keep canonical semantics while removing redundant transport

### P1 — Remove repeated Python/NumPy representations and oracle conversion

**Observed cost layer.** [App:299–329](/Users/rl2025/rtdl_v4_restricted_python_design/Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py:299) reconstructs a tuple of expected rows on each call, passes it to the owner, then compares the returned array with a newly constructed NumPy expected array. The outer worker timer includes that work even though the app's own inner timer starts later. [Runtime:229–239](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_prepared_runtime.py:229) converts and validates the Nx7 query array, then copies origin/direction/tmax slices. It allocates output/diagnostic/status ctypes arrays at 278–282 and assembles an output matrix at 294–298. Native code repacks origin/direction arrays to seven SoA vectors at [2189–2205](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:2189).

**Repair.** Normalize the immutable expected array once during preparation and compare it per execution in one well-defined layer; preserve an independent experiment oracle at the registered endpoint. Introduce a validated immutable query batch or contiguous owned column representation so a prepared owner need not rebuild the same tuples/slices/native vectors. Retain a validating path for ordinary mutable input. Preallocate bounded host output/status storage in the nonreentrant owner. Previously returned outputs must remain immutable snapshots or explicitly owned independent results; reuse must not mutate a prior public result.

**Acceptance.** A same-object NumPy pointer is not an immutability proof. Mutation, shape/count drift, nonfinite rays, zero direction, nonpositive tmax, wrong dtype/strides/device, old-output-as-new-oracle, concurrent execution and use-after-close remain rejected or correctly revalidated. Exact ordered `(selected, neighbor, face)` rows and miss sentinels must match. A duplicate oracle scan can be removed only when the retained check validates the same complete result before accepted publication; no expected values may enter target computation.

### P2 — Batch transfers; download only the result contract's required diagnostics

**Observed cost layer.** [Native:2224–2227](/Users/rl2025/rtdl_v4_restricted_python_design/src/native/optix/rtdl_optix_v4_callback_poc.cpp:2224) issues seven synchronous query uploads. At 2261–2269 it synchronizes and downloads three output columns, four hit-observation columns, full status and seven counters. The `partner_column_output` path already returns no hit-observation rows at [runtime:357](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_prepared_runtime.py:357), but the C ABI still performs their D2H copies. Native and Python both inspect the full status vector.

**Repair.** Use pinned/owned staging and an owner stream for asynchronous uploads and result copies, or accept validated column pointers so packing occurs once. Native device buffers already have `ensure_execution_capacity`; preserve that reuse. For the column-result interface only, avoid transporting unused hit observations, or add a versioned compact result/status ABI. Keep the full-diagnostic interface for callers that request it. Device-side status compaction may remove a transfer and duplicate host scan, but must preserve all error predicates and required lifecycle counters. Do not suppress actual device checks or fabricate a successful receipt.

**Acceptance.** Inputs/staging buffers must outlive queued copies, output/status copies must finish before return, and changing batch size must not leak stale rows. Inject a failing status at a late query, wrong effect tag, missing role, out-of-bounds metadata access, launch failure and audit failure; no result is published. Verify full and compact interfaces agree on valid outputs and rejection. Diagnostic bytes saved and synchronization/allocation counts can be measured without attributing the historical total ratio to them.

### P3 — Do not substitute native closest-hit under the existing generic contract

The measured V4 path's compiler collector implements the canonical minimum `(t, primitive_index)` and boundary-owner handling, followed by one logical CH/MS leaf: [wrapper:277–281](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/v4_triangle_optix_wrapper_codegen.py:277), 446–459, 499–514. Native closest-hit in the baseline uses a different physical algorithm. Equality on the frozen strict-interior Particle input is not a proof that the generic template may remove tie/boundary rules.

A new strict-interior/unique-hit contract could support a separately selected physical route only after its preconditions are explicit and established without using the expected output. Do not claim native closest-hit has the same primitive-ID tie behavior. Necessary adversarial coverage includes equal-distance hits, shared edges/vertices, reversed orientation, misses, multiple valid candidates, extreme/near-boundary rays and metadata indexing. Unsupported cases must reject or use the existing canonical route. This is high-semantic-risk lowering work, not a safe removal of redundant checks and not the first recommended repair.

## 5. Hashes, receipts and checks: what can and cannot be amortized

Large native-file hashing is already amortized. [`_loaded_provider_sha256`:134–171](/Users/rl2025/rtdl_v4_restricted_python_design/src/rtdsl/physical_execution_provenance.py:134) binds the digest to the loaded handle and caches it; `OptixTraversalAuditSession.open` uses that identity at 1116–1131. The prepared owners also cache native/PTX hashes in construction. Do not assert that every prepared call rereads the DSO or that removing this nonexistent work will solve 39x.

Particle still constructs binding dictionaries and hashes their static/count facts each call at runtime:254–269; its output digest and fresh nonce-bound execution receipt depend on new execution at 338–351. Static immutable program/ABI/target substructures may be precomputed; current query counts, owner epochs, output and actual launch observation cannot be replaced with an old success. Compact validated receipt representation is a possible representation change, not a checker-off path. The public endpoint must continue to include whichever checks and materialization it promises; moving required work after the timer is not an optimization result.

## 6. Verification and measurement needed for any successor claim

The following existing tests are useful starting points, not sufficient GPU validation of new native code. This audit did not run them:

| Existing entry | What it presently checks / limitation |
| --- | --- |
| `tests/goal5756_v4_builtin_triangle_runtime_test.py::test_wrapper_uses_optix_owned_deterministic_triangle_channels` | Canonical collector/tie/boundary source structure; does not execute revised kernels |
| Same file, `test_runtime_rechecks_native_plan_bindings_and_per_launch_lifecycle` | Mock authority/lifecycle behavior; not native timing or GPU semantic proof |
| `tests/goal5776_v4_triangle_device_columns_test.py` | Delivery flag, device-column API, checked-reduction source invariants, close behavior, bounded app ownership; several tests are structural |
| `tests/goal5776_v4_aabb_relation_count_lowering_test.py` | Closed generic algebra, resident query binding, layout/operation mismatch and duplicate bind rejection, using source/mocks |
| `tests/v4_paper_apps_pyoptix_owners_test.py` | Baseline normalization/layout/entry and symmetric residency checks |
| `tests/v4_paper_apps_pyoptix_harness_test.py` | Endpoint and retained-population custody checks; no license to reuse old outcomes after an implementation change |

The main AI should implement behavior tests at the changed ownership/stream/error boundary, then use a fresh exact-source native build and new correctness transaction before performance. For low-level changes, include small independently checkable adversarial inputs as well as the old real-scale output contract. A passing source-string test alone cannot close a stream, stale-buffer, overflow or traversal-semantic risk.

For causal diagnosis, record disjoint intervals/counters for: host validation and packing; reusable program construction; per-segment geometry/GAS; allocation and transfer bytes; packing kernels; actual traversal; status and checked reduction; result publication and evidence expansion. Existing `goal5807` native hooks in `rtdl_optix_core.cpp:164–200,1959–2105` can identify pipeline construction, but they do not already measure every layer above. Do not sum nested intervals or treat outer Python elapsed time as isolated GPU traversal. Profiling runs and successive repairs remain separate from preregistered formal comparisons.

The user's at-least-one-second objective needs a named arm and endpoint, a larger genuine workload and an independently established output contract. Summing many unchanged sub-millisecond invocations is not evidence of a larger single task; extra sleeps, dummy work or app-specific slowdown are excluded. Use the same derived data and return contract for both arms, retain all scale points including adverse/OOM/failure, and disclose whether geometry construction, query upload, compilation and validation are included. Preserve the old small-workload result alongside the new scale behavior. An amortization improvement, physical-route repair and reduced checking overhead are different findings; label only what the new measurements identify.

## 7. Identity ledger

The following eleven files were compared read-only against exact first-batch executable commit `c5c8be48b743aa001e9c16c3344cc97c200600d1`; `git diff --name-only c5c8be48b... -- <these files>` returned no paths at inspection:

- `Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py`
- `Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py`
- `src/rtdsl/v4_triangle_prepared_runtime.py`
- `src/rtdsl/v4_triangle_reduction_device_runtime.py`
- `src/rtdsl/v4_aabb_relation_count_lowering.py`
- `src/rtdsl/physical_execution_provenance.py`
- `src/native/optix/rtdl_optix_v4_callback_poc.cpp`
- `src/native/optix/rtdl_optix_workloads.cpp`
- `src/native/optix/rtdl_optix_core.cpp`
- `experiments/v4_paper_apps_pyoptix/librts_owner.py`
- `experiments/v4_paper_apps_pyoptix/triangle_owner.py`

Source anchors are line numbers observed at the inspection HEAD above. This identity comparison establishes which old implementation the audit describes, not successful execution of a new one. No M/E/F2 authority, original transaction, source, test or manuscript file was edited by this audit.

## 8. Priority update: preserve audit semantics while eliminating repeated host work

### 8.1 Profile status and arithmetic

The main AI reported a new diagnostic with 17 native prepared LibRTS count calls taking about 4 ms in aggregate and Python audit open/finish taking about 14.8 ms per call. **These numbers are reported, not independently verified in this document.** At the time of this addendum, the local `v4_long_workload_performance_20260908` directory contained only `STATUS.json` and `WORKLOAD_MATRIX.md`, not raw profile output or the exact invocation. The latter fixes strong-C execution of a genuine task at 1–10 seconds as the scale target, and retains old-input successor regression.

Before making a causal statement, preserve the command, exact source/native identity, input operation/count, raw profiler output and wall-clock spans. Establish whether each number is seconds, milliseconds, total, per-call, self time or inclusive time, and whether the 17 calls include warmup. If 4 ms is indeed the total of 17 calls, the corresponding arithmetic mean is about 0.235 ms/call; if 14.8 ms is per call, its 17-call total is about 251.6 ms. Those calculations are not evidence that the calls were measured in the same disjoint intervals. In particular, `finish()` includes `capture()` and `build_receipt()`; their cumulative times cannot be summed again. cProfile can perturb short Python/ctypes boundaries and does not by itself establish device-only latency. Recheck the leading mechanism with an unprofiled end-to-end diagnostic after the small repair, separately from the formal transaction.

### 8.2 Lowest-risk first change: reuse the registered resolved provider identity

The following chain is source-established:

1. LibRTS `execute_count` passes `library_path=self._native_path` into `OptixTraversalAuditSession.open` at `v4_aabb_relation_count_lowering.py:187–188`.
2. The explicit-path branch at `physical_execution_provenance.py:1129` calls `Path.resolve()`, then `_loaded_provider_sha256` calls it again at 143 before checking the loaded-handle registry.
3. `capture()` calls `captured_traversal_observation_from_snapshot`; that helper resolves the path again at 419. Particle and Graph already omit the explicit path at open, but still use this shared capture helper.
4. `_registered_loaded_provider_identity` at 174–191 is expressly a filesystem-free lookup. The registry retains the exact Python handle object as well as its resolved path and digest, and detects integer-id reuse; registration at 114–131 rejects inconsistent path/digest identity. The DSO content hash is already cached and is not the per-call repeated operation being identified here.

**Repair candidate.** For an internal prepared owner with an established registered provider handle, omit the redundant explicit path at `open`; carry the registered, already resolved `Path` and digest through an internal capture construction path that does not resolve them again. Keep the untrusted/external `captured_traversal_observation_from_snapshot` entry and explicit-path branch validating their inputs. Do not add a caller-controlled `already_verified=True` escape hatch or treat an arbitrary Path/string as proof of loaded-provider identity. The cached identity describes the exact loaded handle, not an assertion that a mutable pathname will always name those bytes on disk.

**Acceptance.** No filesystem resolution/re-read in repeated trusted-provider open/capture after registration; a newly loaded/external provider is still validated once. Explicit mismatched path, mismatched provider digest, wrong handle, unregistered handle, handle lifetime/lease closure and id-reuse attempts do not acquire the fast path. An external symlink/path update must still follow explicit-path resolution rules. Retained receipt path/digest continue to name the identity established when the exact handle was accepted. Fresh nonzero nonce, native begin/finish, complete launch observation and output/semantic digest checks remain in every execution. Instrument the resolution count and compare old/new receipt decisions on the same native snapshots; do not infer speedup from source removal alone.

### 8.3 If still justified: integrate begin/count/finish into one native call

This is a viable second step, not a prerequisite for eliminating path resolution. Existing examples are `rtdl_optix_api.cpp:1143–1186` (triangle v8) and `1540–1579` (bounded relation v8): they call checked begin, the real operation, checked finish, and abort their own active session on failure. Python already has `build_validated_compact_traversal_receipt` at `physical_execution_provenance.py:643–699`, which eagerly validates native facts and defers only JSON expansion. These are reusable implementation patterns, not an automatic proof of the new LibRTS entry.

Required boundaries for a new integrated LibRTS operation:

| Boundary | Required retained behavior and negative case |
| --- | --- |
| Owner admission | Exact closed point/range algebra, prepared index/query handle association, loaded provider/native identity, process/thread/closed state and nonreentrant ownership. Wrong handle, wrong operation/query layout and stale owner must fail before successful publication. |
| Entry and nonce | Generate a private nonzero owner nonce plus a monotonically consumed attempt sequence; reject exhaustion. Check that **both returned nonce words equal this call's expected pair**. The generic compact validator checks positive nonce words and `nonce_lo == execution_sequence`, but has no expected `nonce_hi` argument: an owner must not omit that additional binding merely because the helper returned success. Same-sequence snapshots from a different owner and replay of a previous attempt must fail. |
| Active audit state | `begin_checked` at API:26 rejects an existing active session without clearing it. An integrated wrapper must not abort another caller's preexisting session after begin fails. After this call has begun, only its own matching active session may be aborted. Test nested begin, stale pending context, wrong-nonce finish and failure during the count. |
| Observed traversal | Counts derive from the actual audited `optixLaunch` wrapper at core:291, not hard-coded success fields. For this nonempty count route, check one attempted/successful/complete-context launch, zero failed/incomplete launches, one context bind, expected bundle ID/mix, nonzero expected traversable, query-count raygen invocations, and zero pending-context/session/callsite error. Preserve the documented empty-input behavior separately rather than forging a launch. |
| GPU completion and scalar | Count, reduction, copy and error checks complete before successful return. Native `optixLaunch` success is submission success, not sufficient proof of completed GPU work. A late asynchronous failure, wrong scalar, overflow/domain violation or copy failure must not publish cached output/stamp. Bind the actual returned scalar's digest, operation, query count and accepted authority to the receipt. |
| Exit and failure | Clear/poison output and stamp storage before each attempt; only validate it after the native status reports success. Finish resets TLS state at API:58–59. On count/finish failure, release only this call's session and resources, retain the primary failure, invalidate any prior-success publication cache, and leave a specified retry/closed state. Failure after a successful earlier call must not reissue that receipt. |
| Compact representation | Validate the complete fixed stamp before public return. Returning an immutable validated compact object can defer dictionary/JSON formatting, not decision-bearing validation. Version the receipt representation and adapt consumers explicitly: reading generic mapping keys can materialize the envelope immediately, erasing the intended saving. Ordinary external providers and generic mappings retain the existing strict path. |

The native audit is trusted instrumentation, not independent hardware attestation or protection against an arbitrarily malicious loaded DSO. Mock tests should establish that consumer-side status/stamp validation rejects each altered field and stale identity; they must not be described as real GPU faults. The successor should retain small real native failure/status tests and independent exact output checks as well as those mocks.

**Priority consequence:** if raw profiling confirms audit-side filesystem resolution dominates this batch, do the narrow registered-path repair first and remeasure. The earlier Graph/LibRTS/Particle transport and lowering observations remain valid candidate costs, but must not be promoted to the measured dominant cause merely because they are visible in source.
