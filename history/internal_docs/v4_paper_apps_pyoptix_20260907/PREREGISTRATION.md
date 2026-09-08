# Preregistration: V4 paper applications versus PyOptiX

## Question and arms

For each registered application stage, measure the cost of the ordinary V4
public application path (Arm A) relative to a competent public PyOptiX
implementation (Arm C) under the same algorithm, input bytes, output contract,
GPU, software stack, and lifecycle endpoint. PyOptiX can implement every task;
the comparison tests RTDL's cost, not computability.

Arm A may use RTDL's public compiler/runtime and application-owned partner work.
It may not disable public checks, call a checker-off private core, or rename a
native primitive microbenchmark as the app. Arm C owns normal PyOptiX context,
module, program-group, pipeline, SBT, GAS, launch, device continuation and
public result materialization. It may reuse proven shared PyOptiX owner code,
but the new transaction freezes the exact bytes and does not inherit old result
authority.

## Registered applications

The nine rows and exact stages are fixed by `APP_MATRIX.md` and
`experiments/v4_paper_apps_pyoptix/contracts.py`. Execution priority is:

1. Particle strict-interior single step.
2. Graph triangle counting RT-2A1 on `com-dblp`.
3. LibRTS `point_contains` and `range_contains` counts on parks.
4. RTNN, X-HD, RT-DBSCAN, RayDB, Spatial RayJoin, and RT-BarnesHut in matrix
   order as their competent PyOptiX owners become runnable.

Priority was fixed before new application performance was observed. It is not
a winner-selection rule. `com-dblp` is the first graph because it is the
smallest official registered SNAP input; `cit-Patents` and
`soc-LiveJournal1` remain scale extensions, not silent replacements.

## Output parity gate

No timed worker may start for an app/input until both arms pass an untimed
fresh-process run against the same independent output contract:

- Discrete IDs, labels, counts, ordering, tie rules and overflow status are
  exact.
- Particle output is the complete ordered U32x3 matrix.
- Triangle and LibRTS outputs are checked U64 scalars; count-only output is not
  described as a materialized relation.
- RTNN/X-HD floating values use only their pre-existing frozen tolerances while
  IDs/ranks remain exact.
- Barnes-Hut uses its pre-existing absolute/relative force comparator.
- Bounded output overflow fails closed and exposes no partial application
  result.

An incorrect output is a failed comparison, never a timing sample.

## Lifecycle endpoints

Three endpoints are reported separately where the registered app supports
them:

| Endpoint | Timer starts | Timer ends |
| --- | --- | --- |
| Complete application stage | After loading the common immutable app input, before implementation-specific imports and preparation | After complete public output and required synchronous status/oracle checks, plus method-owned close |
| First result | Before the first execution after input loading and explicit preparation have been reported separately | After the first complete public output and required checks |
| Prepared replay | Before one logical execute on a retained owner and retained registered input | After the complete public output and required checks |

Input load, preparation, compile, GAS, transfer, traversal, continuation,
materialization and close are also recorded as mutually exclusive diagnostic
phases where directly observed. Diagnostics do not replace the wall endpoint.
Preparation is never called free. RayDB has no prepared endpoint. Triangle
prepared replay still executes all deterministic graph segments and returns the
one final scalar.

Disk input loading is outside every primary A/C timer. Its duration and exact
input identity remain retained. This follows the application-stage question,
which starts from the same in-memory domain input, and prevents filesystem page
cache order from dominating the language/runtime comparison.

Arm C uses prebuilt PTX generated once before worker zero. The PTX manifest
binds each device source, PTX byte digest, OptiX/CUDA headers, CUDA bindings,
compute capability, clean source commit/tree, and diagnostic compile time.
Workers rehash the PTX before use. PTX source compilation is excluded from all
primary A/C timers. OptiX module/pipeline/SBT/GAS creation required by a fresh
owner remains inside complete preparation. V4 Particle and triangle retain
their ordinary public restricted-callback compile work; V4 LibRTS accurately
uses its existing fixed native specialization. These route-class differences
must be reported and are not interpreted as intrinsic language effects.

The Particle V4 arm uses the recovered application's `prepare_v4` public
callback owner, not the `rtdlexe` lifecycle. The RT-2A1 V4 arm composes the
standard callback but invokes the device-column native entry with
`fast_control == nullptr`; its measured callback work therefore follows the
general Numba-leaf ABI, and CuPy performs the checked weighted device reduction.
The exact-IR fast branch present in the composed wrapper is not the executed
triangle route in this transaction.

## Sampling and ordering

- Eight paired blocks per app/input/endpoint.
- Blocks 0, 2, 5, and 7 are A-first; blocks 1, 3, 4, and 6 are C-first.
- Each arm/block is one independent fresh process.
- Complete and first-result endpoints have one registered observation per fresh
  process because they are expensive and stateful.
- Prepared replay uses the pre-observation fixed counts in the config: 32 calls
  for Particle and 4 calls each for triangle counting, LibRTS point containment,
  and LibRTS range containment. Each prepared worker performs one untimed
  warmup. These smaller real-scale counts were fixed before GPU execution; a
  change after seeing results starts a new transaction.
- Every raw nanosecond, output digest, order, process ID, error, timeout, OOM,
  retry and discard is retained. No formal worker is retried or replaced inside
  a transaction.
- The untimed dry run registers one exact input-identity object per unit after
  proving both arms loaded identical bytes. Every later formal worker must
  reproduce that object exactly. The independent recount rejects any drift.
- All 192 retained worker output paths must be unique. The controller checks
  the source commit/tree and clean state both before worker zero and after the
  final worker; the recount requires the resulting transaction flag.
- Formal registrations retain safe paths relative to the transaction root.
  Recount rejects absolute or escaping relative paths and has a local
  relocation test, so a copied complete archive can be recomputed without
  recreating the pod's absolute directory.

For each block, the estimator is median Arm-A ns divided by median Arm-C ns.
Report the median of eight paired block ratios and the full min/max block
range. A ratio above one means RTDL is slower. If a confidence interval is
shown, resample the eight blocks, never same-process calls as independent
observations. There is no pass/fail performance threshold and no winner-based
row removal.

The first batch contains four registered units, three endpoints, eight paired
blocks, and two arms: exactly 192 fresh formal worker processes. The untimed
GPU dry run uses eight additional fresh processes, one per unit and arm.

## Identity and environment

Before worker zero, commit and push all application sources, PyOptiX sources,
device source/PTX build recipe, RTDL adapters, controller, workers, oracle,
analysis, tests, this preregistration and the source manifest. Freeze:

- Git commit/tree and every executable source SHA-256.
- Real-scale data archive and per-input member SHA-256.
- GPU name/UUID/compute capability, driver, CUDA, OptiX, Python, NumPy, Numba,
  CuPy and PyOptiX versions.
- Generated PTX/native identities, build flags, public entrypoints and output
  schemas.
- The prebuilt-PyOptiX PTX manifest, source/header/compiler identities, and all
  three exact PTX byte hashes.
- The verified Goal5776 data manifest, fresh native build manifest, pinned
  PyOptiX build/install receipt, loaded PyOptiX extension hash, Python
  executable hash, and exact package versions.
- The worker schedule and runtime budget.

The explicit executable-source projection includes the application contract
inventory, common input loader, shared RT-2A1 geometry producer, public
Particle owner, all experiment owners/device programs, and every
controller/config/worker/recount script. The clean Git tree remains the broader
authority for imported RTDL and recovered application bytes.

Formal application performance requires a GPU with RT cores. The reachable GTX
1070 may perform compatibility checks but cannot produce the registered RT-core
performance evidence.

## Frozen tools and commands

The executable entrypoints are:

- `scripts/v4_paper_apps_pyoptix_extract_data.py`: create-only safe extraction
  and per-member verification of the 1,155,932,998-byte data archive.
- `scripts/v4_paper_apps_pyoptix_local_preflight.py`: source-manifest, device
  entrypoint, no-private-RTDL-baseline, schedule, and focused-test authority.
- `scripts/v4_paper_apps_pyoptix_make_config.py`: clean-source config bound to
  data, native-build, PyOptiX-build, interpreter, and package identities.
- `scripts/v4_paper_apps_pyoptix_prepare_ptx.py`: create-only pre-worker-zero
  compilation of all three public-PyOptiX device programs; compile timings are
  diagnostics, not primary samples.
- `scripts/v4_paper_apps_pyoptix_controller.py --mode dry-run`: eight untimed
  exact-output workers; no formal worker zero.
- `scripts/v4_paper_apps_pyoptix_controller.py --mode formal`: the fixed 192
  worker transaction, allowed only after the dry-run summary passes.
- `scripts/v4_paper_apps_pyoptix_recount.py`: independent reconstruction from
  all retained worker JSON bytes.

Exact setup and invocation commands are in `RUNBOOK.md`. Result roots must be
outside the Git checkout so source cleanliness remains testable.

## Freeze and claims

Executable development stops at `2026-09-08 00:00 America/New_York`. After that
time only already committed and successfully rehearsed tools may execute. Old
M/E/F2 evidence remains immutable and is not pooled. This transaction does not
authorize public/manuscript performance, usability, nine-app completion,
submission, or upload claims.

## Pre-freeze prepared-query residency successor

The first complete formal transaction at commit
`f6936f47291ad28825244d2cb3c996c62193a57d` retained all 192 workers,
reported zero retry/discard, passed exact output parity, and independently
recounted. It also exposed adverse prepared costs: V4/PyOptiX was about 9.68x
for LibRTS point containment and 16.20x for range containment. Those bytes and
results remain immutable and are not pooled with a successor.

Source inspection identified repeated query preparation inside the timed V4
execute path: every replay normalized 100,000 Python rows, packed a native host
buffer, and recreated the native device query allocation. The existing generic
OptiX runtime already supports an app-neutral prepared AABB query handle. The
successor may expose that handle through the public AABB index/count owner and
bind the registered immutable query batch once during preparation. The public
PyOptiX owner must symmetrically normalize, upload, and retain the same query
columns during its preparation. Both execute paths then consume their retained
query columns and still return the same checked U64 scalar.

This successor changes no application predicate, input, output, OptiX device
program, native traversal kernel, block order, endpoint definition, repetition
count, warmup count, estimator, or performance threshold. Complete timing still
includes query binding; first-result and prepared timing still begin after
explicit preparation. It requires a new clean commit/tree, config, passing
eight-process dry run, complete 192-worker transaction, independent recount,
and separately named archive. The first transaction remains adverse evidence
even if the successor improves performance.

## Pre-freeze built-in-triangle execution-buffer residency successor

The first complete formal transaction and the prepared-query-residency
transaction retain their own immutable source, config, worker, and summary
identities. Neither transaction may be discarded or pooled with this
successor. Their Particle Tracking observations identify a separate generic
runtime cost: every call through `V4PreparedBuiltinTriangle` allocates fresh
device buffers for seven query columns, three public output columns, four
diagnostic columns, per-query status, counters, and launch parameters. The
competent PyOptiX arm already retains equivalent execution storage in its
prepared owner.

This successor may retain capacity-bounded device execution buffers inside
the app-neutral prepared built-in-triangle owner and reuse them under the
owner's existing process/thread/non-reentrant guard. It may resize only when a
later query batch exceeds retained capacity. It changes no callback source,
typed IR, effect admission, composed PTX, traversal configuration, application
predicate, query bytes, public U32x3 output, fail-closed status checks,
diagnostic receipt, oracle, endpoint, block order, repetition count, warmup
count, estimator, or performance threshold. It adds no Particle identity or
application dispatch to native/runtime code.

Before any GPU worker used the buffer-residency source commit
`3b8c2ebcae62f3557b0253a93293f090cfcf3ee8`, the still-running prior
transaction exposed a second generic preparation debt: the native AABB count
pipeline is first materialized inside `execute`, while the public PyOptiX
owner materializes its pipeline inside `prepare`. The executable successor
therefore supersedes `3b8c2ebcae62f3557b0253a93293f090cfcf3ee8`
pre-worker-zero and must call the existing app-neutral AABB pipeline
initializer while constructing the prepared index. This moves work between
the already registered prepare and execute phases; it does not remove work
from the complete endpoint or alter traversal semantics.

Before commit `14831b9a9f1565c8d9194da96d718eb3dddd099f` reached GPU
worker zero, prepared LibRTS blocks from the retained prior transaction also
confirmed that the generic native packed-query route allocates query-count
scratch and launch-parameter storage on every call. The final executable
successor therefore also lets each prepared AABB query handle retain those two
app-neutral buffers. Commit `14831b9a9f1565c8d9194da96d718eb3dddd099f`
is superseded pre-worker-zero. Device reduction, D2H result scope, predicates,
and all registered protocol fields remain unchanged; this is allocation
lifetime repair only.

The expected mechanism is removal of repeated `cuMemAlloc`/`cuMemFree` work,
not a guaranteed speedup. The complete endpoint still includes owner
preparation; first-result still includes first capacity allocation; prepared
timing follows the registered warmup and may reuse retained capacity in both
arms. Authority requires a new clean commit/tree, fresh native and PTX
manifests, a passing eight-process dry run before the executable freeze, a
wholly fresh 192-worker transaction, an independent recount, and a separately
named archive. All adverse outcomes remain reportable evidence.
