# Natural-scale authored Particle formal comparison

Date: 2026-09-09

## Verdict

The exact `c06fd73a5` successor passes the preregistered prepared-path
engineering envelope against the competent public PyOptiX arm on one NVIDIA
RTX 4000 Ada Generation GPU:

- paired median RTDL / PyOptiX: `1.0012547857230567x`;
- worst paired block: `1.1199250803752048x`;
- deterministic block-bootstrap interval: `[0.9935120111696512,
  1.0866721880197918]`;
- limits: paired median at most `1.20x`, every block at most `1.35x`;
- 16/16 fresh workers, 48 timed samples and 16 warmups retained;
- retry and discard counts: zero.

The separate clean-clone recount reconstructed the same result from raw
bytes. This is an internal engineering result. Lead review, external review,
paper wording and public claims remain unauthorized.

## Workload and contract

The workload performs one natural, large batch of face-first cell-transition
queries over the real Particle mesh:

- 314,587 vertices and 3,392,530 indexed triangles;
- 160,000,000 distinct strict-interior query rays;
- seven `float32` input columns, 4.48 GB total;
- complete ordered `(face_id, selected_cell, neighbor_cell)`
  `uint32[160000000,3]` output, 1.92 GB;
- resident query buffers during every timed action;
- complete D2H output and exact public output validation inside each timed
  action for both arms.

This is a single transition-stage batch, not full multi-step particle
advection or temporal simulation. Despite its scale, a prepared action takes
about 0.35 seconds, so it does not satisfy the directive's desired
one-second-per-natural-action workload duration.

## Exact identity

- Source commit: `c06fd73a542e7cadaf01bc041b45b2adb327dd2e`.
- Source tree: `0bbb295019891e002b29929e6ea31727a517efa8`.
- GPU: NVIDIA RTX 4000 Ada Generation, CC 8.9.
- GPU UUID: `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`.
- Driver: `550.127.05`.
- Input SHA-256:
  `16955209bbfa75875bab41918e95643b371bb8f0a89dbc1418202ddbe52ee187`.
- Independent oracle SHA-256:
  `71354f158a3dce581dfbf927adaac6624bcbbf314092ff8c5acee3e02a2a6edb`.
- Output SHA-256:
  `6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89`.
- Native library SHA-256:
  `dc7068b6c590b18b8101d24137d653d4f4b76448b1885b0c284952a41879fd01`.
- Public PyOptiX PTX SHA-256:
  `658590f7d6adcde0f936fb3619ca95f3d26c61c914e581327b015f2fd9ef91fc`.
- Formal archive: 2,520,008 bytes, 117 members, SHA-256
  `90a0a99ed5df30bd9f2e45f9b798b044a479a957cdbb6fa46e75d90169360132`.
- Independent recount SHA-256:
  `c18451a94acb5ad139ddc3ad63adeb97075691e0f41a9c299d1b86012d0983c1`.

The preregistration binds the venv CUDA component prefix, the NVRTC library
path and `NUMBA_CUDA_USE_NVIDIA_BINDING=1`. A full RTDL target-compatibility
probe ran before formal worker zero and returned the exact output.

## Paired result

All times are medians of three complete prepared actions in a fresh process.

| Block | Order | RTDL ms | PyOptiX ms | RTDL / PyOptiX |
| ---: | --- | ---: | ---: | ---: |
| 0 | RTDL, PyOptiX | 346.147 | 348.408 | 0.993512x |
| 1 | PyOptiX, RTDL | 384.307 | 353.655 | 1.086672x |
| 2 | RTDL, PyOptiX | 387.963 | 346.419 | 1.119925x |
| 3 | PyOptiX, RTDL | 347.536 | 347.814 | 0.999200x |
| 4 | PyOptiX, RTDL | 348.601 | 351.163 | 0.992703x |
| 5 | RTDL, PyOptiX | 349.355 | 348.203 | 1.003310x |
| 6 | PyOptiX, RTDL | 355.299 | 354.112 | 1.003352x |
| 7 | RTDL, PyOptiX | 348.141 | 348.584 | 0.998732x |

The separate medians of worker medians are approximately 348.978 ms for RTDL
and 348.496 ms for PyOptiX. They are descriptive and are not substituted for
the preregistered median-of-paired-block-ratios estimator. Both arms sustain
roughly 0.46 billion queries per second under this sparse strict-interior
distribution.

## Performance mechanism

The original trusted wrapper invoked separately compiled Numba C-ABI leaf
functions for `make_ray`, hit/miss handling and `finalize` for every ray. The
native traversal itself was not the dominant difference: diagnostics placed
the old RTDL launch near 139--150 ms before full output materialization, while
the direct PyOptiX launch was much lower.

The successor adds a generic compiler lowering for verified straight-line
Callback IR. It inlines immutable lets, pure projections, comparisons,
selects, constructors and read-only view loads into one generated CUDA/OptiX
module. Unsupported effects or control flow fail closed to the existing
audited Numba-leaf route. No application name, input hash, Particle field name,
expected answer or force/cell-transition formula selects this optimization.

At 160M queries, diagnostic native launch time fell to roughly 30--32 ms while
the same complete 1.92 GB output and validation remained. The formal paired
result confirms that this compiler-level change removes the material steady
state overhead rather than hiding output transfer or correctness work.

## Retained failure chronology

The first formal v2 successor at `b3b0331e3` failed before completing worker
zero. Its NVRTC wrapper emitted PTX 8.4 while Numba leaves emitted PTX 8.7;
the exact composer correctly rejected `target_identity: make_ray`. That
transaction is retained and is not pooled with this result.

A first repair explicitly pinned the Numba CUDA binding, but a follow-up dry
run proved that this alone was insufficient. A 2x2 diagnosis isolated
`CUDA_HOME`/NVVM selection: the venv CUDA component prefix emitted PTX 8.4,
while `/usr/local/cuda-12.8` emitted PTX 8.7 against the pinned PTX 8.4 NVRTC
wrapper. The final v3 protocol binds both choices and adds a full RTDL
compatibility probe before preregistration can be written. No target check was
weakened.

## Remaining performance debt

- Median RTDL preparation is 24.259 seconds versus 10.241 seconds for
  PyOptiX. Preparation was not the primary endpoint, but this adverse 2.37x
  difference is material and remains unresolved.
- The all-inline route still constructs and compiles fallback Numba leaves
  before selecting the direct single-module executable. Avoiding that
  redundant work when complete structural admission succeeds is the next
  generic setup optimization candidate.
- The prepared natural action remains below one second. Artificial repetition,
  sleeps or duplicate queries are forbidden; this row must remain labeled as
  a 160M-query natural transition-stage batch rather than a one-second task.
- Only one Ada GPU is measured; clocks were not locked and no
  cross-generation result exists.
- The structural inline subset is deliberately bounded. This result does not
  prove arbitrary restricted-Python callbacks, all Callback IR, all
  applications, author productivity or an app-independent engine.

## Claim boundary

The defensible internal conclusion is that the exact generic straight-line
lowering makes this 160M-query prepared RTDL path effectively performance
competitive with the competent public PyOptiX implementation while preserving
the full output and fail-closed compiler boundary. It does not establish
first-result parity, complete-application parity, a one-second Particle task,
cross-GPU stability, public performance authority or paper acceptance.
