# Bounded source × binding semantic controls

This is a **lead candidate**, not a GPU result or performance benchmark. MainAI
must adopt/freeze the candidate with the actual compiler and native build in a
new experiment identity. No production code is changed by these files.

The question is whether authored computation and declared physical bindings
actually control the output of the public four-role route. This is a separate
small language experiment, not a tenth app, a replacement for Particle, a
generality proof, or a new GPU algorithm.

## Fixed design and expected behavior

- P2 computes `first_metadata[p] + 2*second_metadata[p]` using repeated additions.
- P3 computes `first_metadata[p] + 3*second_metadata[p]` with unchanged types/effects.
- Normal associates argument 2/3 with arrays F/B; swapped associates them with B/F.
  Both are legal declared computations. Swapped binding is not an error the
  compiler is expected to infer or reject.
- F[p]=1000+11p; B[p]=31+3p. The first output is a weighted value, not an object ID.
- 32 disjoint triangles in 16 pairs, far triangle first, and 64 rays cover nearest
  of two, one forward hit, tmax miss, and spatial miss. Coordinates are exact
  binary32; hits are strict interior and nearest distances are unequal.
- A scalar ray-plane/barycentric check independently confirms the input cases.
  `oracle.py` imports no RTDL and computes expected integers before any GPU run.
- Four positive fresh processes each execute normal order and reverse order on
  one owner. Full matrix: eight launches, 512 output rows, 64 distinct rays.
- A fifth fresh process attempts P3 with the P2 plan and must obtain exactly
  `PhysicalSchemaError.code == callback_binding`, before materialization.
- Default canonical hit-selection policy is retained. There are no edge/tie
  cases, so this experiment does not establish edge/tie behavior.

## Commands

CPU admission, wrapper generation, predeclared geometry and negative control:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python /absolute/candidate/run.py \
  --mode cpu-preflight --out /absolute/new-cpu-result
```

CPU mode creates an explicitly named `IDENTITY_ONLY_NOT_A_NATIVE_LIBRARY` file
for target-neutral compile identity. It never materializes, loads this file,
compiles PTX, or calls a GPU. It assumes a synthetic OptiX9/CC8.9 profile only
for this CPU check. These metadata must never be used as actual GPU provenance.

GPU command, after MainAI source adoption and registration:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. python /absolute/adopted/run.py \
  --mode gpu --config /absolute/registered-target.json \
  --out /absolute/new-gpu-matrix
```

Configuration fields are mandatory: `native`, `native_sha256`, `optix_sdk`,
`compute_capability` (e.g. the **actual** `8.9`), `optix_include`, `cuda_include`,
`python_version`, `numba_version`, `numpy_version`, `header_sha256` (absolute
actual header paths to SHA256), and `frozen_python_sources` (the exact dictionary
returned by `run.source_inventory()` in the adopted target directory).

Supply real build metadata and header versions; do not copy the synthetic CPU
target. Freeze the exact source/configuration before the GPU attempt. The source
inventory includes candidate Python files and every Python file under the actual
imported rtdsl package. MainAI must retain the corresponding native build inputs
and build log separately; hashing a DSO does not prove how it was built.

## Retention and failure behavior

Output paths must not exist. Every child has independent stdout/stderr, exit,
before/after source inventory, target and started record. Expected/input arrays
are saved before execution. Admitted callback IR, ABI, physical plan, declared
bindings and wrapper source are retained; GPU mode additionally retains all
four generated Python leaves and PTX, wrapper/composed PTX, executable metadata,
protocol decision, full outputs and full public result receipts. Private object
attributes are read only to retain compiler artifacts; verify/compile/
materialize/prepare/execute/close are all public calls. Compiler log text is not
exposed by this public materialization API; its digest is retained. If an exact
log is needed MainAI must preserve existing build-process logs externally, not
invent text from its digest.

Failures, including cleanup failures, are retained. The matrix stops after a
failed cell and names every not-attempted cell. No retry, silent source repair,
substitution of a fixed-family app, or reduction of output occurs. Source and
configuration must remain identical across the matrix. After a repair, use a
new frozen identity and a completely new output directory/matrix.

The driver saves returned bytes before future calls and close; it does not
test retained-result ownership. The separately reported pinned-output lifetime
bug must be fixed before GPU acceptance. Passing this bounded output experiment
would not certify that unrelated lifetime property or arbitrary accepted code.
It uses ordinary public batches under canonical selection; it does not exercise
prepared query batches, the new pinned-output fast path, native closest-hit
selection, or the corresponding inline-control optimization.

## Current evidence

`cpu_preflight_01/` is the first successful CPU-only run and is immutable;
later driver changes require a new result directory. No GPU matrix has been
executed by the lead. Per-cell output matches and full source-to-loaded-PTX
consistency must be independently recounted from actual GPU artifacts before
paper wording changes. Nine-app performance still has its own gates.

`recount.py` reads retained full arrays, source/plan/executable identities and
receipts without importing RTDL. Run it with the candidate's adopted oracle:

```sh
python /absolute/adopted/recount.py /absolute/gpu-matrix --out /absolute/new-recount.json
```

This checks output and identity data; it does not independently reimplement the
public runtime's traversal-receipt semantic validator. Earlier CPU source bytes
are retained by SHA under `source_versions/`, with their original absolute-path
inventory in each request and `SOURCE_RECOVERY_COMPLETE.json`.
