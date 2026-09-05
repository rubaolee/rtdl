# Goal5847 internal hostile self-review

## Verdict

Accept only at the exact internal precompiled-AOT relation scope. Goal5847
passes every frozen gate, preserves correctness and behavioral true-OptiX
evidence, removes eager runtime-compiler loading, and does not add app-specific
engine logic. Reject any wording that upgrades the result to intrinsic RTDL
language superiority, arbitrary callbacks, all workloads, first-ever build
latency, cross-hardware behavior, production security, external consensus or a
public/manuscript claim.

## Strongest attacks

### The 4.36x result is mostly a PyOptix import benchmark

This attack is valid against an intrinsic-language claim. Median PyOptix
implementation import is 5.206 s because the pinned public stack imports CuPy
and maps NVRTC; RTDL import is 136.718 ms. The primary endpoint intentionally
measures a complete fresh deploy process and was frozen before execution. It
answers a user-visible startup question, not a pure OptiX API microbenchmark.

The report therefore states both results. Complete-process median paired ratio
is `0.229370x`, while post-import median paired ratio is adverse at `2.504242x`.
No sentence may translate the primary reciprocal into “RTDL the language is
4.36x faster than PyOptix.”

### RTDL is still 2.5x slower after imports

Correct. Signed trust installation, detached artifact/authority validation,
static and dynamic typed input construction, provider initialization and its
join are real costs. The frozen gate allowed a median ratio at most 3.0 and a
worst block at most 4.0; observed values are 2.504 and 3.212. Passing the gate
does not erase this remaining optimization opportunity.

This goal closes the defined deployability blocker because the complete
process is materially faster and steady execution remains strong. It does not
claim that every setup decomposition is at parity. A future goal may reduce
the 638 ms post-import path, but rewriting Goal5847 thresholds after seeing the
data would be invalid.

### The steady comparison gives RTDL better continuation semantics

Correct and disclosed. RTDL performs generic device semantic compaction and
returns 4,096 canonical rows. The pinned PyOptix reference emits 8,192 raw
events and canonicalizes them on the host. Both satisfy the same public output
contract, but they are not identical internal algorithms. The `11.677x`
reciprocal is a same-contract implementation result, not a pure dispatch cost
or a lower bound on optimized PyOptix.

### First-ever AOT construction still takes 94 seconds

Correct. Candidate materialize/build/sign took 94.171 s and is excluded from
the deploy endpoint. The experiment asks whether a distributable prebuilt
artifact starts efficiently, just as the PyOptix arm receives precompiled PTX.
Any interactive-authoring or first-build claim must separately report this
cost. Goal5847 does not solve compiler throughput.

### RTDL verifies signatures while PyOptix validation is OFF

This is not a symmetric security contract. The RTDL arm verifies a signed,
family-bound deployment and native identity; PyOptix validation mode is OFF and
has no equivalent installed trust protocol. That asymmetry is adverse to RTDL
post-import time and favorable to RTDL's safety story. It cannot support a
claim that the two APIs provide equal security guarantees.

### Precompiled PyOptix still maps NVRTC

The harness does not call a source compiler and consumes fixed PTX, but its
CuPy-based dependency stack maps `libnvrtc` and a CuPy NVRTC extension during
import. Therefore “both harnesses are stack-wide compiler-free” is false. The
defensible wording is: both execute precompiled device programs; RTDL's deploy
path neither imports nor maps a runtime compiler, while this pinned PyOptix
stack maps NVRTC without the harness invoking source compilation.

### The RTDL native image is not truly minimal

The AOT build starts from shared native source and relies on function/data
section garbage collection plus a version-script allowlist. The resulting DSO
exports exactly 23 required generic relation/triangle runtime and audit symbols
and no unexpected symbol. `readelf`, `ldd`, the build manifest and process maps
show no eager NVRTC. This proves the measured binary surface, not that every
unexported byte is formally minimal or that future families need no new code.

### Cached Python rows could hide a bad native result

Every measured call still invokes native OptiX. The cache key is not just an
input identity: newly returned packed row bytes are copied and compared with
the previous bytes. A changed count or byte sequence forces decoding and oracle
validation. Native error, overflow, oracle mismatch, audit failure or native
source-cache commit failure prevents publication. Tests prove two native calls
occur for two cache hits and that an intervening wrong result neither returns
nor poisons the old immutable tuple.

The formal steady task repeats one fixed input. This does not prove cache
correctness under arbitrary concurrent mutation; prepared owners are
thread-bound and reject reentrancy.

### Asynchronous initialization could leak or bind the wrong artifact

The background capability consumes native identity and compute capability only
from an installed signed slot. It cannot prepare or execute. `bind` joins the
worker and rechecks the loaded artifact, trust identities, family, executable,
native digest, target and producer descriptor. Tests cover delayed overlap,
wrong loaded slot, background failure, abandoned capability, direct
construction, fork rejection, repeated bind, close and resource release.

This is strong lifecycle evidence, not a proof against arbitrary Python
introspection or forced asynchronous exception injection at every bytecode.
Unrestricted same-process Python remains in the trusted computing base.

### One diagnostic receipt cannot prove every timed call used RT cores

Correct. Each of eight RTDL workers records one full diagnostic receipt after
steady timing, and the independent validator records relation and triangle
receipts. The timed calls execute through the same prepared native operation,
validate native status and output, but do not expand a full forensic receipt
inside each timer. Claim exactly ten recounted receipts, not 1,034 receipts.

### Storage and driver caches make “cold start” misleading

Every arm/block uses a fresh Python process, but block-device page cache, driver
state and GPU state across workers are not reset. The schedule alternates arm
order across eight blocks to expose order sensitivity. The valid term is
“fresh-process complete deploy,” not “machine-cold” or “device-cold.”

### The experiment uses only one sparse relation and one Ada GPU

Correct. The exact task has one canonical row per query and predictable
duplicate raw hits. Dense, overflow-heavy, differently sized and other callback
families may behave differently. Triangle was validated for correctness and
security but was not part of the formal PyOptix timing comparison. No
cross-generation or portfolio-wide claim is authorized.

### The test signing roots are not production security

Correct. Two fresh 2,048-bit RSA roots sign the exact deployment chains and the
private test keys are destroyed. The verifier proves signature mathematics and
binding, not organizational key custody, rotation, revocation service,
hardware-backed keys or production operations.

### The first formal attempt failed

Correct. Attempt 01 terminated after one successful RTDL worker because the
controller looked for launch counters at the wrong JSON level. Its archive and
traceback remain immutable. The repair was committed, the actual receipt was
replayed through the canonical verifier, V2 was separately preregistered and no
Attempt 01 timing entered V2. Hiding or pooling that attempt would invalidate
the result.

### The authority is still authored by the implementation team

Correct. The standard-library verifier checks a hard-bound archive, every file,
Git blobs, two RSA chains, artifacts, native exports/dependencies, full receipt
arithmetic, duplicate stdout transport, all samples and all gates. Mutation
tests attack independent layers. This makes the internal evidence reproducible
and fail closed; it is not third-party attestation. External review count is
zero by explicit travel constraint.

### The adjacent test run has four errors

The 198-test run has 193 passes, one environment skip and four old Goal5803
errors. All four try to open Git-excluded historical snapshot files absent on
this Mac and fail before behavior assertions. Goal5847's 29 current-path tests
and seven authority tests pass. Do not call the broad run fully green, but do
not fabricate old evidence or misclassify missing historical files as a new
runtime regression.

## Residual risks

1. Post-import RTDL setup remains `2.504x` the pinned PyOptix arm by the frozen
   paired estimator.
2. First-ever AOT materialize/build/sign remains 94.171 s.
3. One relation shape and one RTX 2000 Ada GPU are measured.
4. Storage page cache and persistent driver/GPU state are uncontrolled.
5. The PyOptix arm is pinned and reproducible but not a best-possible custom
   device-compaction implementation.
6. Full traversal receipts are diagnostic samples, not inside every steady
   timer.
7. Test signing is not production key custody.
8. External review and consensus are absent.

## Closure checks

- Rebuild and verify the stored independent authority.
- Run Goal5847 and authority hostile tests.
- Preserve Attempt 01, all exploratory/no-pooling disclosures and formal V2.
- Commit and push implementation, preregistration, complete evidence, verifier,
  tests and reports.
- Keep the manuscript unchanged until external review explicitly authorizes a
  bounded claim.

At this scope, Goal5847 is a valuable systems contribution rather than a
trivial benchmark adjustment: a signed generic RT artifact no longer drags a
runtime compiler into deployment, initialization overlaps without weakening
identity checks, and both complete-process and steady performance clear frozen
same-contract gates. Its remaining post-import and first-build costs stay
visible.
