# RTDL V4

**Restricted Python callbacks compiled into verified NVIDIA OptiX programs.**

RTDL V4 lets a user express callback-local ray-tracing behavior in a closed,
typed Python subset.  The source is parsed as data—never imported or executed—
then lowered through verified Callback IR, a deterministic ABI, isolated Numba
device-leaf compilation and a trusted OptiX wrapper.  Runtime faults use an
explicit status envelope and successful runs require exact output plus
behavioral OptiX traversal evidence.

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

- seven restricted callback roles plus built-in-triangle execution;
- typed records/views, closed effects, strict numeric/resource budgets;
- compiler-derived any-hit confluence proof and external custom-geometry proof
  authority;
- explicit deterministic C/device ABI and race-safe status reporting;
- IR-derived trusted code generation, isolated Numba compilation and exact PTX
  composition;
- prepared partner lifecycle for Numba/CUDA continuation;
- M1–M6 compositions covering triangle reduction, bounded relation emission,
  multiround spatial search, exact predicate/global witness, grouped-event
  reduction and hierarchy frontier; and
- representative semantics from nine Paper Apps / thirteen paper lanes exact
  and behaviorally true-OptiX in one Home functional identity; and
- thirteen complete application performance frontdoors measured in one
  312-worker RTX 4000 Ada V2/V3/V4 cohort.

## Evidence boundary

RTDL V4 is currently a **research release candidate**.  Its nine-app / thirteen-
lane implementation is exact and behaviorally true-OptiX on Home and modern
RTX.  Its current **cold** application lifecycle is not performance-viable:
the frozen RTX 4000 Ada cohort is 1 pass / 25 fail across 26 independent
V2/V4 and V3/V4 rows.  V4 recompiles callback artifacts inside each cold
frontdoor; an explicit prepared application lifecycle remains the primary
product gap.  This evidence does not establish universal expressiveness,
production security, author superiority or hardware RT-core utilization.

## Documentation

- [V4 overview](docs/v4/README.md)
- [Tutorial](docs/v4/tutorial.md)
- [Public API](docs/v4/api_reference.md)
- [Security model](docs/v4/security_model.md)
- [Nine-application coverage](docs/v4/nine_app_coverage.md)
- [V3 migration](docs/v4/migration_from_v3.md)
- [Full design](docs/v4/restricted_python_optix_callbacks_design.md)

V3 remains documented under [`docs/v3`](docs/v3/README.md).  Its canonical
Action model is still useful when an existing closed primitive already matches
the application.
