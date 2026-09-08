# Post-freeze endpoint and physical-route correction

Date: 2026-09-08 America/New_York.

## Decision

`NUMERICAL_AUTHORITY_RETAINED__ENDPOINT_AND_CAUSAL_SCOPE_NARROWED`

The 192-worker final transaction, its twelve ratios, exact outputs, and
independent recount remain valid. A lead review after the first evidence commit
identified four interpretation errors or missing disclosures. This correction records them without
editing any worker, formal summary, frozen executable, timer, or raw sample.

## 1. Registered complete is post-loader, not raw-domain end to end

The worker calls `_load_input` before starting `complete_started`
(`scripts/v4_paper_apps_pyoptix_worker.py:571--576`). The returned record
explicitly states `input_load_included_in_primary_timer: false` at line 635.
That excluded loader performs more than filesystem I/O:

- Particle loads pre-encoded vertex, triangle, front/back adjacency, query, and
  oracle arrays (`experiments/v4_paper_apps_pyoptix/inputs.py:26--67`).
- Triangle calls `build_segmented_rt_graph_csr_binary` before the timer
  (`inputs.py:70--103`). That producer computes degrees, orients edges, removes
  low-degree/self/duplicate edges, and constructs CSR
  (`segmented_rt_graph.py:41--193`).
- LibRTS loads a prebuilt index-column cache and converts 100,000 WKT queries to
  points or MBRs before the timer (`inputs.py:167--209`).

The excluded-loader medians from the final `complete` workers are:

| Unit | V4 ms | PyOptiX ms |
| --- | ---: | ---: |
| Particle Tracking | 1309.203 | 1280.814 |
| Triangle Counting RT-2A1 | 1615.432 | 1601.093 |
| LibRTS point contains | 2286.838 | 2201.239 |
| LibRTS range contains | 4064.573 | 3890.047 |

These diagnostics are not added to the preregistered primary result after the
fact. The valid interpretation is method setup plus checked execution from a
registered derived representation. The original lead objective that complete
include all required domain encoding was not fulfilled.

## 2. Protocol `first_result` is post-prepare execute, not cold start

The worker completes `_prepare_case` at lines 575--577 and starts the per-call
timer only at lines 587--590. For `first_result`, repetitions are one and
warmups are zero, so the number is the first checked execute on a newly prepared
owner. It excludes only work completed by `_load_input` and `_prepare_case`;
work performed inside an application's `execute` closure remains timed. In
particular, Triangle still constructs bounded device geometry for every segment
in both arms. V4 additionally performs native segment preparation, including
GAS plus composed module/program-group/pipeline/SBT construction, inside
`execute_segment`, whereas PyOptiX reuses the module, program groups, pipeline,
and SBT prepared by `_prepare_case` and, among those RT objects, rebuilds only
its per-segment GAS. Any use of "cold", "deployment", "pure launch", or "first
result from a fresh environment" for this row is rejected.

The timed `execute` closure also performs the registered synchronous
output/oracle and status checks, output digest construction, and compact
execution-evidence projection. Thus `first_result` and `prepared` are complete
public-action measurements, not isolated native-runtime latency.

The registered `complete` row does include method preparation. However,
PyOptiX consumes PTX compiled and hash-bound before worker zero, while ordinary
V4 Particle and Triangle callback compilation remains in their complete
preparation. This is a disclosed public-route comparison, not a symmetric
compiler-time comparison.

## 3. Particle physical algorithms differ

The frozen outputs and application meaning match on all registered inputs, but
the device operations are not identical:

- V4's generated wrapper uses any-hit to enumerate candidates, canonicalize
  boundary ownership, select the minimum `(t, primitive_id)`, call
  `optixIgnoreIntersection`, reconstruct selected-hit data, and then invoke one
  logical closest-hit leaf
  (`src/rtdsl/v4_triangle_optix_wrapper_codegen.py:277--303,327--465,468--518`).
- The PyOptiX program launches with `OPTIX_RAY_FLAG_DISABLE_ANYHIT` and uses
  native closest-hit to validate strict interior and return primitive/front-face
  payloads (`experiments/v4_paper_apps_pyoptix/particle_device.cu:48--109`).

The PyOptiX route is a competent implementation of the frozen application
output. The V4 route pays for a more general deterministic collector protocol.
Therefore the 37.927723x prepared ratio is a total route difference, not a
measurement of DSL checks, Python overhead, or receipt overhead. No retained
ablation allocates the ratio among device algorithm, transfer, materialization,
and host/runtime work.

## 4. Triangle execution lifecycles and device programs differ

Both Triangle arms consume the same derived graph contract, deterministic
RT-2A1 segment iterator, and checked U64 output oracle. Their timed physical
routes are nevertheless not lifecycle-identical:

- V4 calls native `_prepare`, `_execute`, and `_destroy` for every segment
  (`src/rtdsl/v4_triangle_reduction_device_runtime.py:726--829`). Native
  segment preparation builds the GAS and calls `build_pipeline`, which creates
  the composed module, program groups, pipeline, and SBT
  (`src/native/optix/rtdl_optix_v4_callback_poc.cpp:4731--4770`;
  `src/native/optix/rtdl_optix_core.cpp:1924--2232`). The callback leaf is
  produced through the general Numba-backed restricted-callback route.
- PyOptiX creates and retains its context, module, program groups, pipeline,
  SBT, stream, and parameter staging buffers in owner preparation
  (`experiments/v4_paper_apps_pyoptix/triangle_owner.py:74--161`).
  Timed segment execution still constructs device row layouts and a new GAS,
  launches the retained pipeline, performs checked U64 reduction, and copies
  status/scalar results (`triangle_owner.py:204--288`). Its device program is
  the handwritten CUDA/OptiX source
  `experiments/v4_paper_apps_pyoptix/triangle_counting_device.cu`, compiled to
  the hash-bound PTX before worker zero; it is not a Numba baseline.

Consequently, the 1.379226x prepared Triangle ratio is a complete timed-route
observation that includes different pipeline-lifecycle choices. It cannot be
reported as Numba code-generation overhead, callback dispatch overhead, or a
controlled comparison of identical OptiX programs.

## Custody and claim impact

- Frozen source remains commit `c5c8be48b743aa001e9c16c3344cc97c200600d1`,
  tree `e3bb0001f4c2d1e3171ab0431c0479500dfc7136`.
- Formal summary SHA-256 remains
  `67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf`.
- Recount SHA-256 remains
  `667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64`.
- The prior evidence commits remain immutable review history. This document and
  corresponding prose edits are an append-only interpretive correction.
- Allowed: exact-output parity and measured post-loader public-route cost for
  three of nine applications.
- Not allowed: raw-domain end-to-end, cold-start, pure-launch first-result,
  operation-identical Particle, lifecycle-identical Triangle, intrinsic language
  overhead, speedup, near-PyOptiX, easier-authoring, nine-application completion,
  upload, or submission claims.
