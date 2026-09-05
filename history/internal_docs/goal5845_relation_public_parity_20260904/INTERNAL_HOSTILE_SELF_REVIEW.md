# Goal5845 internal hostile self-review

## Verdict

Accept only at the exact internal prepared-steady scope. The implementation
turns the Goal5843 row-returning performance deficit into a strong pass without
removing the public output, traversal proof, fail-closed status checks, source
reuse checks, or app-neutral engine boundary. Reject any broader performance
wording until the remaining gates are run.

## Strongest attacks

### The PyOptiX baseline is deliberately weak

This is the strongest attack. The pinned PyOptiX arm transfers 8,192 raw events
and uses host `sorted(set(...))`, whereas RTDL performs generic device semantic
compaction and transfers 4,096 canonical rows. An expert PyOptiX user could add
a custom CUDA/CuPy compaction kernel.

Response: both arms implement the same public relation contract, and avoiding
that manual continuation is exactly the language/runtime feature under test.
The result proves that RTDL's abstraction need not cost performance against the
pinned compatible-API implementation. It does not prove an intrinsic 9.53x
advantage over every possible PyOptiX program. Manuscript language must name
the exact pinned arm and disclose the continuation difference.

### Validation was moved outside the timer

Optional forensic serialization was moved outside ordinary steady execution;
validation was not. Every timed RTDL call validates the 128-byte native receipt,
all 19 traversal stamp words, two launches, status-before-output ordering,
output size and bytes, source generation/reuse, device compaction, route,
program bundle, provider identity, and bound output digest. The public family
result is produced inside the timer. Full role/counter diagnostics remain
available only when explicitly requested.

The defense fails if the paper implies that a full diagnostic audit costs
0.366 ms. It does not; the observed diagnostic median is 9.259 ms.

### The fast types are forgeable Python wrappers

The fast branch requires exact factory-created internal classes with private
construction tokens, not duck-typed mappings. This is a fail-closed API and
lifecycle boundary, not cryptographic isolation from a malicious user who can
mutate process memory or use unrestricted Python introspection. Claims must not
state in-process adversarial security.

### Immutable output reuse hides changed results

Reuse is keyed by exact packed canonical output bytes and digest. A byte change
forces decoding and validation; a native status failure prevents output
transfer. Tests mutate output, receipt fields, generations, and status ordering.
The downloaded authority also verifies that all formal workers have the same
frozen output hash and independent nonces.

### The 9.53x result is a cache artifact

Both arms run in fresh processes per block, use the same alternating schedule,
receive 16 warmups, and retain 128 samples. Every block passes, with ratios in
the narrow `0.104055x–0.107302x` interval. RTDL-first and PyOptiX-first blocks
agree. Preflight and diagnostic samples are not pooled.

The task intentionally evaluates prepared/reused execution, so reuse inside a
worker is part of the contract. This result says nothing about cold start.

### Cold performance is still worse

Correct. RTDL's median recorded setup is materially larger than PyOptiX's, and
one cold materialization paid about 33.98 seconds. Prepared steady performance
is scientifically useful for repeated-query workloads, but it cannot be used
to imply low-reuse or one-shot superiority. Persisted compiled artifacts and
prepared target reuse across processes remain a genuine performance debt.

### The native engine was polluted with benchmark semantics

The new symbol and implementation describe bounded canonical binary relation
execution, compact status, and traversal audit. They contain no benchmark app,
database, graph, collision, or paper-specific dispatch. Predicate/codegen input
remains outside the engine. The same relation mechanism can support any app
whose contract is canonical bounded pairs.

The engine is nevertheless specialized by behavior. That is acceptable only
because bounded canonical relation is a reusable language/runtime behavior,
not an application formula. A future app-specific branch inside this symbol
would violate the accepted boundary.

### The native binary is not committed

True. The Git evidence retains the DSO hash, exact build manifest, toolchain
identities, source commit/tree, every native source Git blob hash, exact build
command, and post-build symbol listing, but not the 7.19 MB DSO. Rebuilding can
test reproducibility; it cannot prove byte availability if the pod disappears.
This is a custody limitation, not a timing validity failure.

### The summary could be self-authored or altered

The authority builder imports neither RTDL nor a GPU package. It independently
loads the 16 worker files, checks each worker and compact-receipt seal, validates
native stamp arithmetic, checks duplicate stdout copies and empty stderr,
recomputes all timing summaries and estimands, verifies source blobs from the
exact Git commit, and enforces the internal-only claim boundary. Mutation tests
exercise the main substitution paths. This prevents accidental or simple
resealed evidence changes; it is not a trusted-third-party attestation.

### Goal5843 was silently discarded

No. Goal5843 remains the controlling adverse historical measurement at its
exact A6000 commit. Goal5845 uses a different commit, GPU generation, and
preregistered transaction. No old sample enters the new estimator, and no
cross-machine before/after speedup is claimed.

### Is this sufficient for a CGO performance claim?

Not yet. It removes one major reviewer attack: the public row-returning path no
longer loses materially to the pinned PyOptiX implementation on the frozen Ada
task. External review, broader workloads, and possibly another GPU generation
are still needed. Human authoring evidence remains a separate unavailable gate
and must not be replaced by this performance result.

## Residual risks

1. One fixed sparse relation shape may favor compaction; dense and output-heavy
   shapes require a workload ladder before a general relation claim.
2. The PyOptiX arm is pinned and reproducible but not a best-possible custom
   device-compaction implementation.
3. Cold compile/materialize/prepare cost remains substantial.
4. Only one Ada GPU and one driver/toolchain transaction are represented.
5. Post-capture showed no competing compute processes, but there is no
   continuous exclusive-GPU trace covering every sample.
6. External review count is zero; the authority is internally generated.

## Closure checks

- Rebuild and verify the stored authority.
- Run the mutation suite and adjacent functional regressions.
- Preserve Goal5843 unchanged and do not pool it.
- Commit and push all source, evidence, reports, and verifier code.
- Request external review only when it is actually available.
