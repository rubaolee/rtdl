# Goal5842 V9 pre-execution internal hostile review

## Verdict

`ACCEPT_FOR_PREREGISTRATION_AND_GPU_EXECUTION_ONLY`.

V9 repairs a real output/timing-contract defect before worker zero. It does not
authorize a performance, overhead, portability, or CGO claim.

## Hostile questions and answers

### Is V9 hiding a failed or adverse result?

No. V8 is archived with exact bytes and hashes. It produced no registered
timing and failed after 145 untimed GPU executions. V4 and V5 partial timing is
also retained. V9 explicitly states that prior partial timing existed and that
no prior row is pooled.

### Is the change data dependent?

The correction followed source inspection of the registered interval, not a
selected favorable ratio. Nevertheless, because prior partial timing existed,
V9 is classified as a new fair-baseline design rather than a strict
replication. The tasks, schedules, statistics, causal estimand, and absence of
a success threshold are unchanged.

### Do the three baseline arms now expose the same result?

Yes at the registered contract boundary. Relation returns the complete
canonical row set. Triangle returns the checked weighted U64 scalar. Direct and
PyOptiX skip auxiliary per-ray host copies in their explicit Goal5842 timed
mode. RTDL's public route also returns the scalar, but its current provider
internally materializes per-ray values before reduction; that cost is retained
rather than optimized away after observing prior runs.

### Was correctness weakened to obtain better timing?

No. Expected-output comparison moved outside the measured interval but remains
mandatory after every sample. Before worker zero, RTDL, PyOptiX, and Direct each
have an untimed full-output witness. The RTDL generic on/off witness separately
checks repeated public outputs, exact executable identity, lifecycle counts,
and observed OptiX traversal.

### Could an implementation return a stale scalar and still pass?

Each sample is checked immediately after its interval. The RTDL prepared cache
has a two-phase commit and native digest check from the V6 repair. FIRST and
STEADY execute in fresh independent processes. The independent recount binds
input, public output, implementation identity, witness identity, schedule, and
all phase vectors.

### Did V9 modify the frozen generic family core?

No. The required hashes remain:

- `src/rtdsl/v4_family_schema.py`:
  `2d118697d10cb2bc2a8672700ae5a991eaf94e66834bb3e08fd898323720f224`
- `src/rtdsl/v4_generic_family_lifecycle.py`:
  `7ac68832de9d1e04fdd6f0f11bfa0de7d6109d892ab22e42c9aeb2825d28228c`
- `src/rtdsl/v4_family.py`:
  `d25c487823e966a8e9083092811c9a1a2b6aa0fef6ce8f3a0a5b8919c5b809e8`

### Is the Direct no-clock claim credible?

The new witness invokes a dedicated measurement-contract branch before the
legacy `Clock::now()` timing path. Its raw schema contains no duration field,
reports no witness-path clock call, and is independently checked for hidden
duration keys. The normal Goal5798 mode remains unchanged unless the new
measurement contract is explicitly selected.

### What remains fatal to completion?

- Any pre-worker witness failure prevents worker zero and permits only a new
  append-only repair transaction.
- Any failure after worker zero terminates that transaction without retry or
  dropped rows.
- One Ada result cannot complete Goal5842.
- Raw timing ratios across different machines are forbidden.
- External review and consensus remain absent.

## Pre-execution gate

Before GPU execution, the V9 preregistration must rebuild byte identically,
all focused tests and static checks must pass, the repository must be clean at
the exact pushed commit, the direct and native binaries must be freshly built
from that commit, and all three frozen-core hashes must match. Any failure keeps
the performance claim ceiling closed.
