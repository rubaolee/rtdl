# V4 paper applications versus public PyOptiX: first-batch results

Date: 2026-09-07 America/New_York. Final executable source before the hard
freeze: commit `c5c8be48b743aa001e9c16c3344cc97c200600d1`, tree
`e3bb0001f4c2d1e3171ab0431c0479500dfc7136`.

## Verdict

The final first-batch transaction is valid: all 192 registered fresh-process
workers passed, retry and discard counts are zero, source and config remained
unchanged, and the independent recount reports `RECOUNT_MATCH` over all 192
worker files. Exact output parity passed for Particle Tracking, RT-2A1 triangle
counting, and both LibRTS count operations.

The performance result is adverse. V4 is slower than the competent public
PyOptiX arm at every registered endpoint. The smallest final median ratio is
`1.079542x` for LibRTS range complete; the largest is `75.533295x` for
Particle first result. This packet does not authorize a public or manuscript
speedup, near-PyOptiX, usability, nine-application completion, upload, or
submission claim.

The target denominator remains nine applications. This transaction covers
three applications and four operation units. The other six remain unexecuted
because their frozen competent PyOptiX owners were not complete before the
2026-09-08 00:00 ET executable freeze.

## Machine and protocol

- GPU: NVIDIA RTX A4500, CC 8.6, UUID
  `GPU-5dbda20d-af85-650e-7250-10b265a77143`.
- Driver `550.127.05`; OptiX SDK `8.0.0`; Python `3.12.3`; PyOptiX `9.1.0`.
- Eight paired blocks per unit and endpoint, with four V4-first and four
  PyOptiX-first blocks. Each arm/block ran in a fresh process.
- Complete and first-result workers retained one observation. Prepared workers
  retained 32 calls for Particle and four calls for each other unit after one
  untimed warmup.
- Ratios are the median of eight within-block V4/PyOptiX ratios. The absolute
  columns below are diagnostics: the median across the eight arm-specific
  block medians. A ratio above one means V4 is slower.
- Disk input loading is excluded from primary endpoints. Complete begins from
  common in-memory domain input and includes implementation import,
  preparation, execution, required public checks/materialization, and close.

## Final transaction

| Unit | Endpoint | V4 median ms | PyOptiX median ms | V4/PyOptiX median | Block range |
| --- | --- | ---: | ---: | ---: | ---: |
| Particle Tracking | complete | 24020.112 | 2405.894 | 10.208260x | 9.559144-10.675932x |
| Particle Tracking | first result | 54.817 | 0.728 | 75.533295x | 57.802708-82.876756x |
| Particle Tracking | prepared | 18.035 | 0.476 | 37.927723x | 35.338217-41.235553x |
| Triangle Counting RT-2A1 | complete | 11847.933 | 3508.170 | 3.410621x | 3.292015-3.590890x |
| Triangle Counting RT-2A1 | first result | 3516.714 | 1312.973 | 2.731653x | 2.448916-2.806382x |
| Triangle Counting RT-2A1 | prepared | 602.856 | 437.096 | 1.379226x | 1.299988-1.415015x |
| LibRTS point contains | complete | 5502.395 | 4147.360 | 1.311772x | 1.060957-2.021146x |
| LibRTS point contains | first result | 10.796 | 0.902 | 12.058793x | 9.439534-17.776229x |
| LibRTS point contains | prepared | 8.916 | 0.230 | 38.466788x | 34.687357-41.240009x |
| LibRTS range contains | complete | 4565.787 | 4173.109 | 1.079542x | 1.009269-1.195565x |
| LibRTS range contains | first result | 12.352 | 0.890 | 13.421842x | 12.182152-23.730743x |
| LibRTS range contains | prepared | 9.140 | 0.233 | 39.083145x | 34.129091-42.384681x |

All four public outputs are complete for their registered stage: a 5,000 by 3
U32 Particle matrix, checked U64 Triangle count `2,224,385`, checked U64
LibRTS point count `112,729`, and checked U64 LibRTS range count `105,826`.
Triangle and LibRTS count rows are not relation-materialization claims.

## Retained transaction chronology

No samples are pooled across these source identities. Each row is a separate
192-worker transaction on the same GPU/stack, and every row passed an
independent recount.

| Source | Pre-registered change | Particle prepared | Triangle prepared | Point complete / first / prepared | Range complete / first / prepared |
| --- | --- | ---: | ---: | ---: | ---: |
| `f6936f472` | First complete public comparison | 37.983x | 1.374x | 4.189x / 4.120x / 9.678x | 1.073x / 6.347x / 16.198x |
| `43655ff1b` | Symmetric prepared query residency | 38.636x | 1.396x | 2.129x / 167.461x / 36.117x | 1.331x / 182.403x / 42.683x |
| `df7db5c38` | Generic execution/scratch reuse and eager AABB pipeline | 38.763x | 1.339x | 1.015x / 14.215x / 42.739x | 1.120x / 13.974x / 36.862x |
| `c5c8be48b` | Generic per-query U32 to scalar U64 device reduction | 37.928x | 1.379x | 1.312x / 12.059x / 38.467x | 1.080x / 13.422x / 39.083x |

Query residency was a necessary fairness repair: it reduced V4 LibRTS
prepared time from hundreds of milliseconds to roughly 8-16 ms, but it also
reduced the competent PyOptiX arm to roughly 0.23 ms. The resulting larger
ratio exposed rather than caused the steady-state gap. Execution-buffer and
scratch reuse moved LibRTS complete/first costs in the intended direction but
did not close prepared replay. Device reduction removed a 400,000-byte D2H
count column and CPU sum, yet left about 8.7-8.9 ms of absolute prepared gap.
It therefore addressed a real transfer debt but not the dominant physical-route
debt.

Commit `56e5c2ff4` proposed one global U64 atomic and was rejected by internal
review before any GPU worker because it could replace transfer cost with severe
hit contention. It is not a measured transaction.

## What RTDL provides, and what the application still owns

| Application | Application-author responsibility | RTDL responsibility in the measured V4 route | Important route boundary | Final measured cost |
| --- | --- | --- | --- | --- |
| Particle Tracking | Mesh-to-oriented-face/adjacency mapping, strict-interior transition semantics, query construction, cell/neighbor/face output meaning, and oracle | Restricted callback compilation, typed program/ABI checks, trusted built-in-triangle wrapper, GAS/pipeline/SBT ownership, prepared lifecycle, public result checks, and traversal receipt | Public callback owner, but not the `rtdlexe` lifecycle; device source is semantically matched rather than shared with PyOptiX | 10.21x complete, 75.53x first, 37.93x prepared |
| Triangle Counting | Select RT-2A1, construct degree-oriented CSR segments and geometry, supply ray weights, combine segment scalars, and enforce graph oracle | Compile/verify the count callback and delivery proof, execute through the general Numba-leaf device-column ABI, own OptiX traversal, and produce per-segment receipts | CuPy still performs checked-U64 weighted device reduction; the measured route does not use the exact-IR `fast_control` specialization | 3.41x complete, 2.73x first, 1.38x prepared |
| LibRTS | Select point/range algebra, provide indexed/query columns and expected count | Verify a closed AABB count authority, prepare generic AABB index/query handles, execute the fixed count route, check scalar metadata, and issue a traversal receipt | Fixed standard specialization, not arbitrary callback lowering; its generic multi-operation native kernel is broader than the app-specific PyOptiX kernel | 1.31x/1.08x complete, 12.06x/13.42x first, 38.47x/39.08x prepared |

The PyOptiX arms explicitly own context/module/program groups/pipeline/SBT/GAS,
device buffers, launch, device continuation/reduction, status, synchronization,
and result materialization. RTDL removes much of that OptiX plumbing and adds
admission, identity, lifecycle, and physical-execution checks. The measurements
show the cost of each complete measured route; they do not isolate an intrinsic
cost for any single language check.

No independent authoring study is part of this packet. The responsibility
comparison supports a concrete capability description, not a claim that RTDL
is easier to use.

## Mechanism findings and remaining debt

- Particle's two arms both upload queries on each execute. The likely V4 costs
  include NumPy/ctypes/native repacking, seven synchronous query-column H2D
  copies, full output plus diagnostic/status D2H, and receipt/materialization
  work. The current evidence does not provide a causal ablation for each item.
- Triangle uses the same graph contract, segmentation, geometry producer, and
  complete scalar output in both arms. Its prepared gap is much smaller than
  its complete/first gaps, but partner-owned segment production and reduction
  mean the ratio is not pure callback-compiler overhead.
- LibRTS no longer repacks or uploads 100,000 queries per prepared call. Static
  source comparison shows that V4 still uses a general multi-operation AoS
  native route, an intermediate traversal synchronization followed by a
  reduction/copy synchronization, and an indexed GAS built with
  `ALLOW_RANDOM_VERTEX_ACCESS` but without `PREFER_FAST_TRACE`. The PyOptiX arm
  uses a compact SoA kernel, `PREFER_FAST_TRACE`, and one same-stream
  traversal/reduction/copy chain. These are credible next mechanisms, not
  measured causal attributions.
- The final source was committed, pushed, freshly built, PTX-bound, and dry-run
  rehearsed before the executable freeze. No further source repair is allowed
  for this submission. Post-freeze work may only report/narrow claims, package
  evidence, rerun frozen tools, and conduct review/submission checks.

## Evidence identities

- Final formal summary SHA-256:
  `67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf`.
- Final independent recount SHA-256:
  `667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64`.
- Final config SHA-256:
  `29a070b67d9756dda08dd8be6a006bc77be8990a1e584a8295e322c2fdba2e38`.
- Final native library SHA-256:
  `719ac27d884c93634f8b3a9ed2936b95d6231fccb437da7da62448adf2ec15ba`.
- Final compact archive SHA-256:
  `2d7dc4413639e46994ca74251d230b74d5e9d775a23b457336cb00f9df80f4ff`.

The exact compact files and archives are indexed by `EVIDENCE_INDEX.json`.
