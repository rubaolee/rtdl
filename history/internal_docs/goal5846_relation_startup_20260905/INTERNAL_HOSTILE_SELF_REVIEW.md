# Goal5846 internal hostile self-review

## Verdict

Accept only at the exact internal warm-cache fresh-process scope. The
implementation reaches setup-plus-first parity with the frozen source-compiling
PyOptiX contract, preserves the Goal5845 steady result, retains exact output
and true-OptiX provenance, and adds no app-specific engine branch. Reject any
wording that silently upgrades this to first-ever compilation, AOT deployment,
all PyOptiX programs, arbitrary relations, cross-hardware behavior, external
consensus, or a paper claim.

## Strongest attacks

### The comparison gives RTDL a cache but makes PyOptiX compile source

This is the strongest attack and is valid against a broad claim. The RTDL arm
loads seven sealed leaf artifacts plus one sealed complete executable, while
the inherited PyOptiX arm compiles the pinned device source in each worker.
That asymmetry is preregistered and is the exact old setup debt being tested:
can RTDL persist its compiler result rather than rebuild it every process?

The result closes that exact debt only. It does not show parity with a
precompiled PyOptiX deployment. The retained precompiled-PTX, validation-off
sensitivity is about 236.415 ms, versus a 577.153 ms formal RTDL median. AOT
parity remains open and must be the next performance goal.

### The 36.982-second first fill is unacceptable

Correct for one-shot use. Seven isolated Numba leaf compilations dominate the
first fill. Goal5846 proves amortizable, identity-bound persistence; it does not
make compilation cheap. Any manuscript statement about interactive first use,
installation, or one-shot work must disclose or exclude this cost explicitly.

### Calling the cache read-only is false because files are mode 0666

The pod artifacts and manifests are mode `0666`. Therefore no report may claim
OS-level write protection. The runtime meaning is logical hit-only: a supplied
manifest and SHA-256 forbid misses and stores; workers snapshot every artifact
before and after; changed bytes fail validation. The final authority uses the
exact phrase `logical_hit_only_not_os_permission` to prevent ambiguity.

### Overlap hides native initialization instead of paying for it

The native initialization start call is fast because it launches target-bound
work asynchronously. The prepare phase joins that work, so unfinished CUDA or
OptiX initialization remains inside setup-plus-first. The measured phase sum is
the sequential wall intervals observed by the public setup path, not a sum of
independent background CPU times. Removing the join or timing only thread
creation would be invalid; this implementation does neither.

### Post-hoc correctness validation is outside the timer

Full oracle comparison and expanded receipt validation are outside both arms'
timed intervals as preregistered. Required RTDL public-path checks remain in the
timed execution: native fail-closed status, compact receipt acquisition,
canonical output construction/reuse, and bound execution facts. The result
does not claim that a full forensic audit costs 0.365 ms.

### The public output is reused, so steady timing could return stale data

Reuse requires the exact factory-created immutable output type and exact packed
byte digest. Changed output bytes force revalidation; native failure prevents
output publication. Every formal call retains the same frozen input and output
contract, and mutation tests cover output, source generation, executable token,
cache artifact, and receipt changes. This is lifecycle correctness, not an
in-process adversarial-security theorem.

### The one-shot executable token can be forged or replayed

The token is factory-created, process/thread bound, weak-reference tracked,
protected by a lock, rechecks its bound identity immediately before use, and is
atomically consumed. Public mappings and structurally similar user objects do
not enter the fast branch. Unrestricted Python introspection can attack any
same-process object, so no cryptographic sandbox claim is authorized.

### The provider source hash was cached and could hide mutation

An early implementation did memoize source hashes globally. Internal review
rejected it and restored a fresh hash read at each relevant use. This cost is
visible in setup. The final implementation does not trade mutation detection
for a benchmark result.

### The paired result is noisy and may not prove RTDL is faster

Correct. Four block ratios are above one and four below. The RTDL-first stratum
median is 1.0335; the PyOptiX-first stratum median is 0.9647. The 0.991 primary
ratio must be interpreted as practical parity under a 1.25 gate, not as a
statistically meaningful 0.9-percent speedup. The worst block, 1.1323, is
retained.

### The 1.25 gate was chosen to make a weak result pass

The gate was frozen before the formal transaction. It permits a 25-percent
setup overhead because setup is driver-sensitive and because the goal asks
whether language/runtime persistence avoids a material penalty, not whether
RTDL wins by a tiny margin. The observed median is 0.991 and the worst block is
1.132, so the conclusion does not rely on a result near 1.25. A stricter AOT
goal is still required.

### PyOptiX steady execution has periodic large outliers

The raw samples retain periodic approximately 16 ms PyOptiX values. The median
was frozen as the estimator for both arms, and all samples remain in evidence.
The startup primary uses exactly one setup-plus-first value per fresh process,
so these steady outliers do not create the startup result. No tail-latency
claim is authorized.

### Import and CUDA-context costs are not symmetrically timed

Correct. Worker process startup and module import occur before each arm's setup
timer. PyOptiX import through CuPy may establish CUDA state before the timer,
while RTDL explicitly pays target initialization after the timer begins. That
bias is adverse to RTDL, but it also means Goal5846 is not a full user-visible
process-start comparison. Such a claim requires a new process-wall experiment.

### The engine was polluted with a benchmark-specific fast path

The new concepts are content-addressed executable persistence, target-bound
initialization, and bounded canonical relation preparation. No RayDB,
collision, graph, or paper-app name/predicate appears in the native ABI. A
bounded canonical relation is a reusable language behavior already established
before this goal. Future app dispatch inside the ABI would violate this result.

### The authority is still written by the project agent

Yes. The authority builder is independent of RTDL and GPU packages, checks
retained duplicate transports and immutable hashes, and has mutation tests. It
prevents accidental or simple coherently resealed changes; it is not trusted
third-party attestation. External review count remains zero.

### The DSO itself is not in Git

Correct. The 7.19 MB DSO is absent. Evidence retains its SHA-256, byte count,
complete dynamic symbol listing, exact clean source commit/tree, every native
source blob hash, build command, toolchain and header hashes. This supports
rebuild and identity checking but not byte custody after the pod disappears.

### The post-formal test suite failed once

The first run had two errors because the pod clone was shallow and lacked an
old Goal5842 commit used by history-integrity tests. Both errors occurred in
`git cat-file/show`, before semantic assertions. The failure log is retained.
Fetching that exact commit without changing HEAD, source tree, DSO, caches, or
formal samples produced 232/232 passes. Calling the first run a code regression
would be wrong; hiding it would also be wrong.

## Residual risks

1. Precompiled/AOT PyOptiX remains substantially faster in the unregistered
   sensitivity.
2. First-ever Numba compilation remains tens of seconds.
3. Only one sparse relation shape and one Ada GPU are represented.
4. There is no full process-wall/import comparison.
5. The pinned PyOptiX arm is reproducible but not a best-possible custom CUDA
   continuation.
6. The cache is cryptographically checked, not protected by filesystem
   permissions or a trusted artifact signer.
7. External review and consensus are absent.

## Closure checks

- Rebuild and verify the stored independent authority.
- Run the mutation suite and affected regression surface.
- Preserve all formal workers, preflight evidence, first-fill evidence, and
  both post-formal test attempts.
- Commit and push source, evidence, reports, tests, and verifier.
- Do not use Goal5846 for public/manuscript wording before external review.

At this bounded scope, Goal5846 is a real performance result rather than a
trivial timing cleanup: it turns a repeated compiler/runtime setup penalty into
an identity-bound reusable artifact path while preserving safety and true RT
execution. Its remaining AOT deployment gap is equally real and is not closed
by this verdict.
