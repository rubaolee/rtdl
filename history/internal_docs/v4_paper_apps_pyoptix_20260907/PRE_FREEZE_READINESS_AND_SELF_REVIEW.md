# V4 paper-app / PyOptiX pre-freeze readiness and hostile self-review

Date: 2026-09-07 America/New_York.

## Verdict

`READY_FOR_FREEZE_COMMIT__GPU_DRY_RUN_REQUIRED`

The first batch is locally code-ready but has produced zero GPU dry-run workers,
zero formal workers, and zero performance results. No public or manuscript
performance claim is authorized. The target denominator remains all nine V4
paper applications; this packet implements only the first execution batch of
three applications and four operation units.

## Research alignment

The experiment supports the lead's repurposed-RT problem statement only at a
cost/evidence boundary. It asks what the ordinary V4 public application route
costs relative to a competent public PyOptiX owner under the same application
algorithm, input, output, GPU, and lifecycle endpoint. It does not establish a
historical first, arbitrary callback expressiveness, application correctness in
general, or an intrinsic speedup of a language abstraction.

The implementation adds no code under `src/rtdsl` or `src/native`. All new
PyOptiX device semantics remain experiment/app-owned. The V4 arm uses existing
public language/runtime routes with their checks intact.

## Registered scope

| Unit | Exact stage | V4 physical route | Public PyOptiX route | Output gate |
| --- | --- | --- | --- | --- |
| Particle | One strict-interior closest-face/cell-transition step, 3,392,530 triangles and 5,000 queries | Existing public Particle executable lifecycle | Triangle GAS, closest-hit strict-interior program, full U32x3 materialization | Exact 5,000x3 U32 matrix and historical independent-oracle identity |
| Triangle counting | RT-2A1 on official SNAP `com-dblp` | Standard restricted callback through the general Numba-leaf device-column entry, followed by CuPy checked-U64 weighted reduction over deterministic segments; `fast_control` is null | Same shared RT-2A1 geometry, triangle GAS, any-hit continue traversal, checked-U64 device reduction | Exact published count 2,224,385 |
| LibRTS point | 11,544,398 parks boxes and 100,000 point queries | Closed AABB relation-to-device-count lowering | Custom-AABB GAS, exact point-containment intersection predicate, device count reduction | Exact checked-U64 count 112,729 |
| LibRTS range | Same index and 100,000 range queries | Closed AABB relation-to-device-count lowering | Custom-AABB GAS, exact range-containment intersection predicate, device count reduction | Exact checked-U64 count 105,826 |

Particle is not the full 50,000-step advection. Triangle returns a scalar and
does not claim relation materialization. LibRTS returns counts and does not
claim collection. The six second-batch applications remain in the matrix with
missing PyOptiX owners; none is silently removed from the denominator.

## Fair timing boundaries

- `complete` starts from the already-loaded common in-memory domain input,
  before implementation-specific imports and preparation. It ends after the
  first complete output, synchronous status/oracle checks, materialization, and
  owner close.
- `first_result` measures the first complete public execution after input load
  and explicit preparation; load and preparation are retained separately.
- `prepared` measures warm owner reuse after one untimed warmup. Particle uses
  32 retained calls per worker; each triangle/LibRTS unit uses four.
- Disk load is never included in a primary ratio. It remains a diagnostic so
  page-cache behavior cannot be mistaken for compiler/runtime cost.
- Eight balanced paired blocks use fresh processes, four V4-first and four
  PyOptiX-first. There is no performance pass threshold and no winner-based row
  deletion.
- Public PyOptiX uses prebuilt, hash-bound PTX generated before worker zero.
  PTX compile time is retained separately and excluded from primary ratios.
  Fresh module, pipeline, SBT, GAS, transfer, execute, and public result work
  remain in the applicable endpoint.

## Custody and fail-closed controls

The pre-freeze self-review found and repaired five evidence weaknesses before
worker zero:

1. Dry-run output parity alone did not freeze the actual input bytes. The dry
   run now requires identical per-unit `input_identity` objects across arms,
   registers them into the formal summary, and every formal worker and the
   independent recount must match them exactly.
2. The recount counted 192 worker references without proving 192 unique output
   files. It now rejects duplicate worker paths and malformed or duplicate arm
   registrations.
3. The controller checked source cleanliness before worker zero but not after
   the final worker. It now records an end-of-transaction commit/tree/clean
   check, includes it in transaction status, and the recount requires it.
4. PyOptiX originally invoked NVRTC in every fresh worker, while the V4 LibRTS
   route uses a precompiled native specialization. All three PyOptiX programs
   are now compiled once before worker zero and independently hash-bound.
   Compilation cost remains visible as a diagnostic but cannot inflate the
   PyOptiX primary denominator.
5. Formal worker references originally used pod-absolute paths. Registrations
   now bind safe transaction-relative paths, and a test copies the complete
   synthetic transaction to a new directory and independently recounts all 192
   workers there.
6. A final cross-agent source trace found that the Particle matrix had called
   its `prepare_v4` callback owner an `rtdlexe` route, and that the triangle
   worker metadata had called a general-leaf device-column execution a fast
   specialization. Before any GPU worker, both descriptions were corrected;
   no algorithm, workload, timer, repetition, or native path changed.

The explicit source-hash projection now includes `contracts.py` and the PTX
builder in addition to all owners, device programs, input/geometry producers,
and experiment scripts.
The wider clean Git tree binds all imported RTDL and recovered app bytes.

Every call retains output parity, compact physical-execution evidence, public
materialization status, process identity, runtime identity, source identity,
and retry/discard counts. Detailed expanded receipt retention is explicitly
zero; no requirement claims one detailed receipt per call.

## Local verification

- Recovered source manifest independently regenerated: 9 applications, 134
  files, directory digest
  `a2cdb9f9f83a49485f8964c9ae8391ed9531c9b7f25bfe4cf16164c594bfa0cb`.
- Focused experiment suite: 25 tests passed.
- Directly relevant pre-existing runtime-input, AABB-count, triangle-device,
  and public Particle owner tests: 26 tests passed with
  `PYTHONPATH=src:scripts:tests:.`.
- Ruff lint and format checks pass for all new Python files. `compileall` passes.
- The staged diff outside the exact recovered app snapshot passes
  `git diff --check`. The snapshot retains 116 CRLF files by design; normalizing
  them would destroy the source-recovery identities.
- Static preflight reports
  `PASS__LOCAL_STATIC_ONLY__GPU_DRY_RUN_REQUIRED`, 192 formal workers,
  `gpu_used=false`, `performance_result_exists=false`.

The static preflight necessarily reports a dirty tree before the freeze commit.
A clean-checkout preflight remains mandatory after commit and on the GPU host.

## Preserved adverse and historical boundaries

- A selected older 68-test historical regression remains 67 passes plus one
  missing Git-object dependency (`b8058860f`). It is not weakened or rewritten.
- An additional relevant exploratory run found the existing
  `goal5814_particle_rtdlexe_lifecycle_test` depends on missing historical file
  `goal5814_particle_tracking_scientific_scope_and_measurement_policy_preaction_20260828.json`.
  Other selected current paths passed. This missing historical artifact is not
  reconstructed merely to manufacture a green broad suite.
- Three recovered app sources match retained historical hashes. The other six
  are candidate source inputs for a new experiment, not recovered historical
  authorities. The expected Goal5785 archive remains unavailable.

## GPU blocker and next exact action

No local RT-capable GPU is available. On a supported NVIDIA RT GPU, use the
committed `RUNBOOK.md` without changing workloads or estimators:

1. Fetch the exact clean source commit and verify the 1,155,932,998-byte data
   archive SHA-256.
2. Build the driver-compatible RTDL native library and pinned public PyOptiX.
3. Precompile and bind all three public-PyOptiX PTX programs.
4. Run clean local preflight and create the machine/config binding.
5. Run eight untimed dry-run workers and require exact input/output parity.
6. Only then run all 192 formal workers and the independent recount.
7. Preserve and archive every pass, error, timeout, OOM, and zero-retry status.

GPU compile/runtime compatibility, exact output parity, timing, and baseline
competence remain unvalidated until those steps execute. A failure is retained
as evidence and does not authorize an after-worker-zero patch inside the same
transaction.

## Claim boundary

This packet authorizes only the statement that a preregistered, locally checked
first-batch comparison implementation exists. It does not authorize any V4
versus PyOptiX ratio, nine-app coverage claim, compiler-performance conclusion,
new-problem priority claim, paper-byte acceptance, upload, or submission.
