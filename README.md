# RTDL V4

**Restricted Python callbacks compiled into verified NVIDIA OptiX programs.**

RTDL V4 lets a user express callback-local ray-tracing behavior in a closed,
typed Python subset. The source is parsed as data—never imported or executed—
then admitted through shared schema, identity, and lifecycle checks. Supported
families use topology-specific trusted lowerers, a deterministic ABI, isolated
Numba device-leaf compilation, and a trusted OptiX wrapper. This is a bounded
compiler architecture, not arbitrary Python, arbitrary Callback IR, or
topology-generic native lowering.

```text
restricted Python callback text
             ↓
typed Callback IR + proof/resource contracts
             ↓
CPU semantic oracle + deterministic ABI
             ↓
isolated Numba leaves + trusted OptiX wrapper
             ↓
target-bound native execution + explicit status
             ↓
exact output + behavioral traversal receipt
```

V4 keeps the programming flexibility that V3 lacked without reopening an
arbitrary callback escape hatch.  Imports, reflection, allocation, recursion,
dynamic loops, arbitrary calls, user PTX and exception-based device control
flow are rejected.  Bulk non-traversal work may use admitted Numba/CuPy partner
compositions under explicit ownership and lifecycle contracts.

## Quickstart

Python 3.10+ and NumPy are enough for CPU authoring/verification:

```bash
git clone https://github.com/rubaolee/rtdl.git
cd rtdl
python -m pip install -e .
python examples/current/v4_restricted_callback_quickstart.py
```

Expected key fields:

```json
{
  "status": "verified_cpu_semantics",
  "first_hit": {"item_id": 3, "t": 4.0},
  "user_source_executed_by_python": false,
  "gpu_execution_claimed": false
}
```

Linux target execution additionally needs an NVIDIA GPU, CUDA, OptiX SDK,
Numba, CuPy and a compatible compiler.  Target natives are rebuilt and frozen
per exact environment; source identity alone does not imply byte-identical
native output.

## What is implemented

- a finite restricted callback language with typed records/views, closed
  effects, numeric/resource budgets, and supported callback roles;
- shared admission, semantic ABI, provider/executable identity, lifecycle, and
  fail-closed status machinery for supported families;
- two stable public fixed constructors plus separately classified successor
  routes and topology-specific lowerers;
- deterministic C/device ABI, isolated Numba leaf compilation, exact PTX
  composition, and prepared Numba/CUDA continuation;
- one author-defined ten-candidate prospective composition exam, selecting
  `builtin_sphere::any_hit_count_continue_u64_per_query`; and
- a separately implemented finite Goal5840 checker over its registered routes,
  modes, properties, and mutations.

The prospective composition count is one. The unbiased new-application and
external-human authoring counts are both zero. These implementation facts do
not establish automatic lowering for an unseen topology or broad usability.

## Evidence boundary

RTDL V4 is currently a **research release candidate**, not a finished CGO
artifact or an authorized public performance result. Earlier nine-app/thirteen-
lane functional and 26-row cold-frontdoor studies remain historical evidence;
they were not rerun or converted into the current two-task experiment.

At measured implementation M (`d653fe4...`), one frozen triangle task and one
owner-grouped relation task passed the machine numerical contract independently
on RTX 4090 Ada and RTX 3090 Ampere. Prepared public RTDL/Direct medians were
`1.175066x` and `1.076852x` on Ada, and `1.133636x` and `1.094795x` on Ampere.
These are exact-path overhead observations, not intrinsic language speedups or
universal parity. There is no registered A/D worst-block gate.

The original written requirement for a detailed retained receipt on every
timed execution was not fulfilled: 4,096 timed Arm-A calls have 32 separate
diagnostic receipts. Synchronous native/compact status and explicit output
oracles remained active, and no wrong output was observed in the retained final
GPU samples. Post-import diagnostics are adverse on all four rows and reach
`2.377129x`; both first-result endpoints are lifecycle/import-confounded.
Relative to predecessor E, first-result medians regress about 8%--22% at entry
and 16%--31% post-import; those comparisons are post hoc and non-gating.

Final tooling snapshot F2 has passed clean-checkout replay. R4 has produced the
eight-page manuscript candidate, and R6 has paired it with the exact anonymous
evidence package and replayed that package in two isolated extraction roots.
Final-byte review, claim adjudication, and submission checks remain open; no
upload or public/manuscript claim is authorized. Current state and exact claim
boundaries are in
`history/internal_docs/post_goal5851_submission_remediation_20260906/`.

## Documentation

- [Current examples](examples/current/README.md)
- [Getting started examples](examples/current/getting_started/README.md)
- [Current feature examples](examples/current/features/README.md)
- [Current research benchmarks](examples/current/research_benchmarks/README.md)
- [CGO manuscript workspace](paper/cgo2027/README.md)
- [Historical/current custody boundaries](KNOWN_STALE_CUSTODY_CHECKS.md)

The repository retains earlier V1-V3 examples and reports as historical
material. They are not the V4 public compiler specification and must not be
used to infer current V4 support.
