# Goal5848 definition-stage internal hostile self-review

Date: 2026-09-05

Review scope: `GOAL5848.md` only. No implementation, GPU result, external
review or consensus exists yet.

## Verdict

`ACCEPT_DEFINITION_FOR_IMPLEMENTATION__NO_PERFORMANCE_RESULT`

The goal attacks a real measured debt and prevents the two easiest favorable
but scientifically weak substitutions: PyOptix import latency for language
performance, and host-heavy PyOptix continuation for abstraction overhead.
Its hard gates are intentionally stronger than Goal5847 and are fixed before
Goal5848 implementation or formal timing.

## Hostile questions and resolutions

### Is the goal optimizing the wrong number?

No. The primary endpoint excludes implementation import and includes all work
from deterministic fixture construction through the first exact public
result. Complete-process timing remains visible but secondary. This prevents
the approximately 5.2 s PyOptix/CuPy import from manufacturing the primary
result.

### Can RTDL win because the PyOptix baseline still performs host work?

Not for acceptance. The idiomatic pinned arm is retained for user-facing
context, but the hard AC3 comparison is against a separately frozen optimized
PyOptix arm with equivalent device continuation and compact public transport.
Direct OptiX supplies an additional lower bound. If the optimized arm is
wrong, unavailable or knowingly handicapped, the goal is blocked rather than
passed.

The optimized arm may require frozen CUDA support in addition to the
PyOptix-compatible binding. It must therefore be labeled accurately as
PyOptix-compatible plus disclosed device continuation, not falsely described
as pure PyOptix API code.

### Does moving work before the timer solve the target?

No. The primary interval starts immediately after imports and includes fixture
materialization, trust/deployment, provider initialization, input deployment,
prepare, first execution and exact validation. Artifact generation is a
separate first-build endpoint rather than silently precharged or omitted.

### Does the goal permit disabling security for speed?

No. AC6 and AC7 require compiler-free deployment, exact trust and executable
identity, dynamic status, physical receipts and isolated fail-closed attacks.
A validation-off counterfactual may diagnose cost but can never be an accepted
public arm.

### Is `1.20x` a scientific constant?

No. It is an engineering acceptance threshold chosen before formal timing to
make “no material performance loss” falsifiable. It is not a universal
definition of acceptable compiler overhead and must not be presented as a
statistical law. Absolute times, every block and adverse values remain
mandatory.

### Can the two tasks be pooled to hide failure?

No. AC3--AC5 apply independently to relation and triangle. A pass on one task
cannot offset a failure on the other. Ratios are computed within host and
block; cross-machine raw-time ratios are forbidden.

### Is two-generation replay overconstrained to one cloud image?

No fixed GPU model, cloud vendor, driver branch or CUDA/OptiX minor version is
required. Source, task and experiment contracts remain fixed. Native/device
artifacts may be rebuilt for each architecture before worker zero, with exact
build manifests and binary hashes bound on each host.

### Does exact artifact caching create a trust bypass?

It must not. A hit requires exact content, build-input, provider, target,
family, native ABI and trust identity. The returned object is a verified
capability, not an unverified path lookup. Cache mutation, stale-process use
and cross-family substitution belong in the fail-closed suite.

### Can a ratio-only cache gate permit a multi-second hit?

The original relative-only gate could: ten percent of a 94 s cold build is
still 9.4 s. The reviewed definition therefore requires both zero compiler
invocations and a `<=1.0 s` median cache hit, in addition to the `<=0.10x`
relative bound.

### Is PTX driver JIT incorrectly forbidden?

The reviewed definition distinguishes source compilation from normal OptiX
module creation. Driver loading/JIT of frozen PTX is allowed, measured and
attributed. Runtime CUDA/Numba/NVRTC source compilation inside registered
deploy or execution endpoints is forbidden.

### Can phase instrumentation distort the result?

The phase partition must reconcile with each endpoint within the greater of
2 ms or 1%, and instrumentation overhead must remain at most 5% of the
uninstrumented endpoint median. Formal primary values come from the frozen
worker protocol, not from selectively summed phase medians.

## Deliberately unresolved risks

1. The hard `1.20x` Direct and strong-PyOptix gates may fail. That is an
   intended falsifiable outcome, not a reason to loosen them after timing.
2. Equivalent device continuation may expose that Goal5847's large steady
   advantage was mostly baseline implementation quality. That adverse result
   must be retained.
3. Two architecture generations require two suitable GPU opportunities.
   Availability affects schedule, not the acceptance rule.
4. The first cold build may remain tens of seconds even after exact reuse is
   fixed. Goal5848 requires decomposition and fast exact-repeat reuse, not an
   unsupported claim that cold compilation is cheap.
5. Two families do not establish arbitrary Callback-IR or workload
   generality. The final claim ceiling states this explicitly.
6. External reviewers have not examined the definition. Internal acceptance
   cannot authorize manuscript wording.

## Definition integrity conclusion

The plan is sufficiently explicit to begin implementation. It names the
unfavorable current result, requires competent baselines, freezes hard
performance and security gates, separates exploration from formal evidence,
and defines failure without claim dilution. Any later change to a task, arm,
endpoint, estimator or threshold after formal results are observed requires a
new versioned preregistration and preservation of the failed transaction.
