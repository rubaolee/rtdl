# Natural-scale Particle setup-remediation formal comparison

Date: 2026-09-09

## Verdict

The exact `110dee7aa` successor passes the preregistered prepared-path
engineering envelope against the competent public PyOptiX arm on one NVIDIA
RTX 4000 Ada Generation GPU:

- paired median RTDL / PyOptiX: `0.9941092578237594x`;
- worst paired block: `1.0623042952807356x`;
- deterministic block-bootstrap interval: `[0.9293607544514662,
  1.0198384562965996]`;
- limits: paired median at most `1.20x`, every block at most `1.35x`;
- 16/16 fresh workers, 48 timed samples and 16 warmups retained;
- retry and discard counts: zero.

The separately invoked independent recount reconstructed the same result from
the raw archive without importing the controller. A bounded lead review at
local commit `6a87302149180777d784f63cf76a8843a7c732a4` accepted the exact numerical
observation and a narrow source-route interpretation for author-side manuscript
wording. It did not authorize superiority, one-second, arbitrary-callback,
external-review, public-release or submission claims.

## Setup debt result

The formal worker's preparation interval begins after loading the common domain
input and ends after each implementation has created its reusable prepared
query state. It includes RTDL source verification, compilation/materialization,
static triangle-owner preparation, expected-output digesting and query-batch
admission. The corresponding PyOptiX interval includes its equivalent owner and
prepared-input construction.

- successor RTDL preparation median: `8.9835259945 s`;
- current PyOptiX preparation median: `10.4627816595 s`;
- RTDL / PyOptiX preparation ratio: `0.8586173627x`;
- predecessor `c06fd73a5` RTDL preparation median: `24.2592035885 s`;
- same-machine predecessor-to-successor RTDL improvement: `2.7004100176x`.

The setup ratio was not a preregistered pass/fail endpoint. It is a retained
descriptive result for this exact source, host, workload and environment, not a
general cold-start or deployment claim.

## Workload and contract

The workload performs one natural, large batch of face-first cell-transition
queries over the real Particle mesh:

- 314,587 vertices and 3,392,530 indexed triangles;
- 160,000,000 distinct strict-interior query rays;
- packed `float32[160000000,7]` logical input, 4.48 GB;
- complete ordered `(face_id, selected_cell, neighbor_cell)`
  `uint32[160000000,3]` output, 1.92 GB;
- device-resident query columns during every timed action;
- complete D2H output and exact public output validation inside each timed
  action for both arms.

This is a single transition-stage batch, not full multi-step particle
advection or temporal simulation. A prepared action remains about 0.35 seconds,
so it does not satisfy the directive's desired one-second-per-natural-action
duration. The scale was not changed after observing the successor.

## Exact identity

- Source commit: `110dee7aa11e57e984cc2509163e021d787c692a`.
- Source tree: `1e549d791fedd23659bb0e0636747016938cd1c4`.
- GPU: NVIDIA RTX 4000 Ada Generation, CC 8.9.
- GPU UUID: `GPU-2a00572b-6cef-b9e6-db0a-c127783a5d46`.
- Driver: `550.127.05`.
- Preregistration SHA-256:
  `dc9b429dd5387bd0f7cf6f7073415ee26a002bae31f5f94a1d0af3db86f3813d`.
- Input SHA-256:
  `16955209bbfa75875bab41918e95643b371bb8f0a89dbc1418202ddbe52ee187`.
- Independent oracle SHA-256:
  `71354f158a3dce581dfbf927adaac6624bcbbf314092ff8c5acee3e02a2a6edb`.
- Output SHA-256:
  `6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89`.
- Native library SHA-256:
  `e797495ac513056dc3b66796d81716a73639b1499c609938eacdc14f5b4f5011`.
- Public PyOptiX PTX SHA-256:
  `658590f7d6adcde0f936fb3619ca95f3d26c61c914e581327b015f2fd9ef91fc`.
- Controller result SHA-256:
  `f79c84da0e4ed6ea8e998f82b5ac2b3a225f93f3831500a0fadfd52bf6f8592e`.
- Formal archive: 2,526,713 bytes, 117 members, SHA-256
  `42ebdf176e9625c8c95d7b2e2504ddccc70b42ed4b692fe3360f3c2c5b08bccf`.
- Independent recount SHA-256:
  `d3ce86641c9d6cee4bd9e4c092207808ab6ff94515dd73112761793564ca2212`.
- Mac clean-worktree recount SHA-256:
  `a5597b2a6f3f2fb113ec64b59d1c87ccac7226446e2769147c3cc90b2fd66eeb`.
- Post-formal compiler-artifact and replay-receipt supplement: 33,286 bytes,
  17 archive members, SHA-256
  `9de850a354bd85366eb354ef796d45e0b9d1ccc71428b117961fd67c684d933a`.

The preregistration binds the venv CUDA component prefix, NVRTC library path,
`NUMBA_CUDA_USE_NVIDIA_BINDING=1`, native build manifest, public PyOptiX PTX
build manifest and clean source identity. A complete RTDL compatibility worker
and three independent PyOptiX calibration workers ran before formal worker
zero. Their PyOptiX medians were `354.820694`, `349.655162` and `345.382969`
ms; all were retained.

After downloading the archive, a new detached clean worktree on the Mac reran
the independent recount. Every field matched the pod recount except the
expected absolute archive path; the statistics, hashes, ledger, source closure
and status were identical.

## Post-formal custody correction

The original 117-member formal archive preserves the measured native DSO,
public PyOptiX PTX, source closure, manifests, commands, process streams,
compact per-worker execution evidence, append-only ledger and all timing
samples. It does **not** preserve the RTDL generated leaf source/PTX bytes,
wrapper source/PTX, composed PTX, any timed worker's full traversal receipt, or
the multi-gigabyte input/output arrays. The earlier phrase "all
executable/evidence bytes" was therefore too broad and is corrected here.

While the same pod state was still available, a separately identified
post-formal replay at the exact `110dee7aa` source exported 13 compiler
artifacts and one full traversal/lifecycle receipt. Its reconstructed program
identity
`da62ce40ed6e51db638eb916c842161e6025d764abedb4932dfe84f3db710530`
and executable identity
`0663bfeefefac2b389c31edbe6d331adbc7fa54f4c7632db666cc6a87a4fa19c`
match all eight original RTDL worker records. The replay observed OptiX
traversal, produced role counters
`[0,160000000,0,0,160000000,0,160000000]`, and reproduced output SHA-256
`6c4ec71524be3d7b241c3d66c4cd06a5aa7089b3948bf1d8dd8aab550f0dec89`.
Its full traversal receipt SHA-256 is
`3c27d744eeb7c660442506d1cc3a2a72aa65ea63cd7d87f5fc9594d2aba29773`.

This supplement is a same-source/toolchain reconstruction and correctness
replay, not an original timed-worker artifact. It is not pooled with the
formal timing transaction and does not repair the absence of original full
receipts. Its only role is to make the generated executable bytes available,
show that their recorded identities rederive, and preserve a complete
post-formal execution receipt under an explicit boundary.

Before Pod shutdown, the available 160M query, query-cell and oracle arrays,
the complete post-formal observed output, base mesh, deployed artifacts,
original formal package, exact source archive, reconstruction tools and
environment records were copied to the RunPod network volume at
`/workspace/rtdl-particle-110dee7aa-durable`. Its 47 payload files are bound by
`SHA256SUMS` SHA-256
`43e0bc33cd0eb9a702a35619ddc71f9a1a8d66fc7a2cd9df95b3e95dbf3645c5`.
The standalone verifier rehashed all members and compared the observed output
to the independent oracle in bounded chunks. This is a durable handoff while
the owner retains the network volume, not repository custody or original
timed-worker output custody. See `DURABLE_DATA_HANDOFF.md`.

## Paired result

Each row is a fresh-process worker median of three complete prepared actions
after one untimed warmup.

| Block | Order | RTDL ms | PyOptiX ms | RTDL / PyOptiX |
| ---: | --- | ---: | ---: | ---: |
| 0 | RTDL, PyOptiX | 354.949 | 348.044 | 1.019838x |
| 1 | PyOptiX, RTDL | 376.724 | 354.629 | 1.062304x |
| 2 | RTDL, PyOptiX | 347.104 | 346.353 | 1.002169x |
| 3 | PyOptiX, RTDL | 352.061 | 380.292 | 0.925766x |
| 4 | PyOptiX, RTDL | 348.779 | 353.714 | 0.986049x |
| 5 | RTDL, PyOptiX | 346.250 | 357.106 | 0.969601x |
| 6 | PyOptiX, RTDL | 353.367 | 347.952 | 1.015564x |
| 7 | RTDL, PyOptiX | 356.259 | 383.338 | 0.929361x |

The separate medians of worker medians are `352.714179 ms` for RTDL and
`354.171108 ms` for PyOptiX. They are descriptive and are not substituted for
the preregistered median of paired block ratios. Both arms sustain roughly
0.45 billion queries per second for this sparse strict-interior distribution.

## Performance mechanism

Three generic changes removed preparation work without changing the RT
algorithm or the public output contract:

1. The triangle compiler sends all four fallback Numba leaves through one
   isolated child instead of spawning four independent Python/compiler
   processes. Per-leaf source, IR, role, ABI, nonce and artifact checks remain.
2. A packed app-neutral `Nx7 float32` ray-row ABI takes one immutable Python
   snapshot instead of creating three separately transposed immutable host
   arrays and then reconstructing seven native columns.
3. Native preparation performs one packed H2D transfer, then a precompiled GPU
   kernel validates every row and transposes it into the seven device-resident
   query columns. Any nonfinite value, nonpositive `tmax` or zero direction is
   reported before the batch token and host output pointer are published.

Same-pod diagnostic phase measurements, which are not the formal estimator,
observed `prepare_batch` fall from approximately `19.278 s` before the packed
ABI to `9.267 s`, then to `5.334 s` after device transpose. In the final
diagnostic, `3.430 s` was Python immutable-snapshot work and `1.904 s` was the
native call. The final prepared execution samples remained in the same range
as PyOptiX and the predecessor.

Selection is based on ABI capability and verified built-in-triangle ray-row
shape. No application name, dataset hash, query count, expected answer,
Particle field or cell-transition formula is present in the new path. The old
split-column ABI remains as a compatibility fallback.

## Descriptive peak-memory diagnostic

A separate balanced-order `A,C,C,A` diagnostic ran two fresh workers per arm
with requested 10 ms host-RSS and whole-device NVML sampling. All four workers
returned the formal output digest. The pre-worker whole-device baseline was
identical at 345,571,328 bytes.

| Arm | Whole-device peak | Baseline-subtracted peak | Direct-worker RSS median |
| --- | ---: | ---: | ---: |
| RTDL | 9.153 GiB | 8.831 GiB | 14.537 GiB |
| Public PyOptiX | 6.831 GiB | 6.509 GiB | 18.603 GiB |

RTDL therefore used 2.322 GiB more whole-device memory while its direct worker
RSS was 4.066 GiB lower in this diagnostic. This is the expected trade-off of
keeping one packed host snapshot while temporarily holding packed device
staging beside the transposed device columns. NVML per-process accounting was
unavailable, so the GPU values are whole-device totals, not allocation
attribution. Sampling can miss shorter peaks, direct RSS excludes compiler
children, and the monitor perturbs latency; no sampled latency enters the
formal estimator. The raw result is `PEAK_MEMORY_DIAGNOSTIC.json`, SHA-256
`0c3ee2df8d9411f3a6ef4e6e344cc802abe4b97bbba3d94b5e8eba20099ce49e`.

## Retained failure chronology

Commit `5cc68659c0dc38990b57866511b2b6834613d1f3` first introduced the packed
ABI but did not update the compiler's frozen prepared-runtime source hash. A
real 5,000-query public-path smoke therefore correctly failed before GPU state
creation with
`GC014_PROTOCOL_CONTRACT_REJECTED@materialize.contract:`
`CP003_PHYSICAL_BINDING_MISMATCH`. Commit `219170fee...` updated the binding and
passed the exact contract test and public smoke. This failure is retained and
was not relabeled or pooled.

Before formal execution, the GPU-transpose candidate passed a valid 5,000-query
public-path smoke and rejected an injected zero-direction row with
`contains an invalid ray`. The final clean source then passed the complete
160M compatibility worker before preregistration.

## Remaining limits and costs

- The natural prepared action is below one second. This row does not satisfy
  the preferred long-action duration despite processing 160M distinct rays.
- Only one Ada GPU was measured; clocks were not locked and no
  cross-generation successor result exists.
- Formal peak host/GPU memory was not captured. A separate descriptive
  diagnostic found lower direct-worker RSS but higher whole-device peak for
  RTDL. It is not pooled with formal timing and does not authorize a general
  peak-memory claim.
- The original archive contains exact data manifests, both deployed arm
  binaries, compact worker evidence and all timing records, but not RTDL's
  generated compiler bytes, full timed-worker receipts, or the multi-gigabyte
  query/output arrays. The separately identified post-formal supplement
  reconstructs the compiler bytes and one full receipt with matching recorded
  identities; it is not original timed evidence. Complete post-formal replay
  output exists in the separately verified network-volume handoff, not Git.
- The input is an authored distinct strict-interior ensemble over the real
  Particle mesh. It does not cover boundary ties, dense multi-hit rays or a
  full temporal simulation.
- The path remains a bounded built-in-triangle callback specialization. It
  does not establish arbitrary restricted-Python callbacks, all Callback IR,
  all applications, author productivity or an app-independent engine.

## Claim boundary

The defensible internal conclusion is narrow: for this exact 160M-query
transition-stage batch and eight measured blocks, the generic compiler and
packed device-preparation successor is within the registered performance
envelope of competent public PyOptiX in prepared execution and removes the
previously measured same-machine setup disadvantage. Its lower direct-worker
RSS comes with a higher sampled whole-device peak. It does not authorize a
public speedup, complete-application parity, one-second-workload coverage,
cross-GPU stability or paper acceptance.
