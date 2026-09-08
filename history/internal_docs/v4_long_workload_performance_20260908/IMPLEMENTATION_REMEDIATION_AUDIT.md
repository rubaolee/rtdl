# Long-workload implementation-remediation audit

Date: 2026-09-08, America/New_York. This audit separates measured mechanisms
from broader language claims. Formal successor results and their independent
recount are documented separately; manuscript and public review remain open.

## Starting problem

The retained `c5c8be48b` application transaction proved output-equivalent
public execution but measured large costs: Particle and LibRTS prepared paths
were approximately 37--39x public PyOptiX, and Graph RT-2A1 prepared was
1.379x. Source inspection and phase diagnostics showed repeated callback/device
compilation, repeated provider-path work, detailed receipt construction,
unnecessary dependency imports, host materialization, and per-segment program
lifecycle work. These are implementation debts, not intrinsic costs proved by
the language design.

## Implemented mechanisms

### Shared public lifecycle and provider identity

Commit `04456efcf` added a registered loaded-provider identity and exact-core
completion paths so internal capture can reuse an already verified library
object/path/digest. Explicit external paths still resolve and validate. The
same change delays detailed evidence projection until after the exact core
completion while retaining synchronous device status, output ownership,
process/thread/reentrancy checks, and fail-closed result publication.

This was a broad change: 14 files, 1,258 insertions, and 161 deletions including
tests. It must not be described as a trivial wrapper optimization.

### LibRTS custom-AABB count route

Commits `36ff25b54`, `5f07cce58`, `88c4859e2`, and `a47544e0c` do four distinct
things:

1. embed the audited AABB OptiX PTX in the native snapshot rather than compiling
   it in every fresh measurement worker;
2. embed checked count reduction in that build so the prepared route returns a
   scalar rather than materializing an all-hit row stream;
3. use a compact traversal receipt while retaining native/device status and
   exact output checks; and
4. import only dependencies required by the scalar-count route.

The lowering is shape/operation based (`POINT_CONTAINS` or `RANGE_CONTAINS`
over typed custom AABBs), not dispatched by the LibRTS application name,
dataset hash, or expected answer. The application still owns operation choice,
Parks input decoding, and the exact count oracle.

### Particle fixed standard-library route

Commits `4ba2814e8` and `37e730831` make the performance arm load a prebuilt,
identity-bound `.rtdlexe` and immutable admitted input snapshots. Offline
compilation is excluded from both RTDL and PyOptiX application execution; load,
artifact admission, provider binding, input deployment, execute, output, and
close remain in the complete endpoint.

This is deliberately not a generic-particle claim. The route is a fixed
strict-interior built-in-triangle standard-library specialization with a
5,000-query shape, typed columns, unique-hit/positive-barycentric assumptions,
orientation authority, and exact output contract. Existing native symbols and
types still use Particle vocabulary. That app-shaped native surface predates
this remediation and is a TCB/generality limitation; performance evidence for
this row cannot establish an app-independent engine.

### Graph built-in-triangle reduction route

Commits `537b3a990` and `0c3420f42` make RT-2A1 consume a verified generic
`builtin_triangle_reduction_v1` executable. The `.rtdlexe`, detached authority,
trust chain, native DSO, source tree, target, callback IR, and lowering identity
are hash-bound. Immutable leaf/module/program state is loaded once while each
graph segment still supplies its own geometry and columns; checked U64 segment
accumulation, graph orientation, segmentation, and final oracle remain
application-owned.

The first commit is substantial: eight files, 1,125 insertions and 38 deletions
including three new test modules and the artifact builder. The second binds the
loaded family executable back to the accepted lowered callback contract rather
than accepting family-name equality alone.

### Measurement scheduling contract

Commit `02e84374f` adds optional exact one-CPU affinity to generic worker,
controller, freeze, and independent-recount tooling. It has no application or
GPU execution changes. The contract is applied before implementation imports,
recorded before and after execution, and rejected on drift. All three arms use
the same CPU. This controls a diagnosed cloud-host variance source; it is not an
RTDL optimization and must not be counted as implementation speedup.

## Trust and code-size cost

The remediation is not free. The performance-relevant commits add artifact
builders, identity checks, native embedded programs, compact ABI/receipt paths,
and tests. Selected commit-level gross changes are:

| Commit | Gross change including tests/tooling |
| --- | ---: |
| `04456efcf` lifecycle/provider repair | +1,258 / -161 lines |
| `36ff25b54` embedded AABB PTX | +324 / -7 lines |
| `4ba2814e8` Particle verified executable | +714 / -12 lines |
| `5f07cce58` embedded count reduction | +259 / -11 lines |
| `88c4859e2` compact LibRTS receipts | +74 / -12 lines |
| `a47544e0c` count-only imports | +71 / -28 lines |
| `37e730831` immutable Particle snapshots | +22 / -2 lines |
| `537b3a990` Graph verified executable | +1,125 / -38 lines |
| `0c3420f42` lowered-contract binding | +11 / -3 lines |
| `02e84374f` affinity evidence | +169 / -0 lines |

These totals overlap neither semantics nor TCB uniformly: tests and builders
are not all runtime TCB, while generated native wrappers and artifact admission
are. The paper should claim bounded fixed-family compilation and deployment,
not arbitrary callback lowering or negligible compiler complexity.

## App-independent boundary verdict

- The new LibRTS scalar route and Graph triangle reduction are reusable typed
  shape/operation families; application names and expected answers do not
  select native execution.
- Graph orientation, segmentation, input generation, and oracle remain in the
  app. LibRTS WKT/data interpretation and oracle remain in the app.
- Particle uses a pre-existing app-shaped native standard-library route. Its
  exact assumptions are checked, but it is not evidence that the engine has no
  application knowledge.
- CPU affinity belongs only to measurement control.

Therefore the defensible result is that bounded precompiled RTDL families can
reach a competent public-PyOptiX cost envelope on the tested routes. It is not
evidence that every RTDL program receives this performance or that all native
engine customization has been removed.

## Verification completed before final result

- Final 15-worker dry run: 15/15 correct, zero retry/discard, exact CPU `{8}`
  at preflight and postflight.
- Local registered Python 3.12 regression: 84/84 tests passed across provider
  identity, AABB lowering, embedded PTX, Particle/Graph `.rtdlexe`, harness,
  and public owner modules.
- A bare Homebrew Python 3.14 invocation lacked NumPy and produced import
  errors; rerunning under the registered project venv passed. This is an
  environment error, not silently converted into a test pass.

## Final measurement disposition

The formal successor subsequently completed all 240 workers and ten controller
evaluations. All ten registered rows met the paired-median `<= 1.20` and
every-block `<= 1.35` engineering thresholds. A foreign-directory clean
checkout independently reconstructed the raw transaction and returned
`PASS__METHOD_AND_TARGET`; the deterministic archive is preserved at SHA-256
`ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc`.

This closes internal implementation-remediation acceptance for the measured
families. It does not remove the trust/code-size costs above, convert Particle
into an application-neutral route, extend coverage to six unmeasured historical
applications, or authorize paper wording without a new-byte review.
