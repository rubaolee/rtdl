# LibRTS distinct-query long-workload successor

Date: 2026-09-09, America/New_York. Measurement source commit
`123f76ec99b2539eb819831a840b8b79e0fd5414`, tree
`fef996da5762be4e863a7c82b4104c64218e2ebc`. Independent-verifier commit
`8e5679efa872a3778bf4136ff83e9ffc4847a6d6`, tree
`f99026dba9a0357926d754576df6618f87ffa594`.

Internal status:
`PASS__INDEPENDENT_RECOUNT__INTERNAL_ENGINEERING_TARGETS_MET`.
Manuscript/public claim authorization: **false** pending claim review,
manuscript integration, final-byte review, and submission controls.

## Result

The LibRTS long-query gap is closed for the two measured AABB relation-count
operations on one RTX 4000 Ada. The same public RTDL and competent public
PyOptiX implementations processed one logical batch of 1,225,000,000 distinct
queries over the same 11,544,398-box Parks index. Both returned the exact
independent-oracle count. All 64 formal workers and all 32 paired cells passed
with zero timeout, retry, discard, or output mismatch.

| Operation | Endpoint | RTDL median | PyOptiX median | Paired RTDL/PyOptiX median [range] | PyOptiX/RTDL |
| --- | --- | ---: | ---: | ---: | ---: |
| Point contains | Complete | 4.851 s | 6.241 s | 0.77595 [0.76592--0.78870] | 1.289x |
| Point contains | Prepared | 2.143 s | 2.725 s | 0.78434 [0.77767--0.78883] | 1.275x |
| Range contains | Complete | 8.247 s | 10.063 s | 0.82060 [0.81426--0.83206] | 1.219x |
| Range contains | Prepared | 4.805 s | 5.817 s | 0.82539 [0.81887--0.83666] | 1.212x |

All four paired medians are below the preregistered `1.20x` ceiling and all
32 blocks are below the `1.35x` ceiling. The reciprocal column is descriptive;
the primary estimator is the median of eight within-block RTDL/PyOptiX ratios.
Displayed arm medians therefore need not divide exactly to that estimator.

The following descriptive phase medians are reconstructed from the eight fresh
worker records in each cell family. They are not substitutes for the paired
estimator above. `Prepare` builds and binds the static indexed state; `Action`
processes the complete 1,225,000,000-query logical batch. Input loading and
full-file hashing are excluded and are disclosed separately below.

| Operation | Endpoint | Arm | Prepare | Action | Throughput |
| --- | --- | --- | ---: | ---: | ---: |
| Point contains | Complete | RTDL | 1.891 s | 2.894 s | 423.3 Mquery/s |
| Point contains | Complete | PyOptiX | 0.810 s | 5.434 s | 225.4 Mquery/s |
| Point contains | Prepared | RTDL | 1.879 s | 2.143 s | 571.8 Mquery/s |
| Point contains | Prepared | PyOptiX | 0.807 s | 2.725 s | 449.6 Mquery/s |
| Range contains | Complete | RTDL | 1.894 s | 6.301 s | 194.4 Mquery/s |
| Range contains | Complete | PyOptiX | 0.822 s | 9.238 s | 132.6 Mquery/s |
| Range contains | Prepared | RTDL | 1.898 s | 4.805 s | 254.9 Mquery/s |
| Range contains | Prepared | PyOptiX | 0.816 s | 5.817 s | 210.6 Mquery/s |

Median input-load-and-digest time is 7.89--7.97 seconds for point columns and
15.75--15.82 seconds for range columns across the arms and endpoints. Those
file-I/O costs are recorded but excluded symmetrically. RTDL therefore retains
an approximately 1.08-second preparation disadvantage on this machine; the
measured complete result passes because its long action is faster. These phase
records do not identify a unique hardware or software cause, so no part of the
action difference is attributed to one mechanism without a separate profiler.

## What changed

Two generic implementation debts were removed without adding LibRTS, Parks,
paper, query-count, or expected-answer dispatch to the engine:

1. Typed point and range query columns remain in device-columnar `float32` SoA
   form. RTDL no longer repacks point columns into 16-byte rows or range columns
   into 20-byte rows before native upload. The embedded OptiX program loads the
   generic SoA columns directly while preserving the legacy packed ABI for old
   callers and the packed range-intersects route that requires query GAS.
2. One logical typed-column query batch can be executed through bounded,
   contiguous, non-overlapping chunks. Each chunk includes validation, H2D,
   OptiX traversal, device U32-to-U64 reduction, synchronization, status check,
   and checked scalar return in the action timer. Failure in any chunk aborts
   the logical result; checked accumulation rejects U64 overflow.

The RTDL path additionally validates a real compact OptiX traversal receipt for
every chunk. The public PyOptiX arm uses its own custom-AABB pipeline and device
reduction and does not call a private RTDL entrypoint.

## Workload and oracle

The indexed data is the authors' real `parks.bz2.wkt` object set, materialized
as 11,544,398 inclusive float32 AABBs. Cache NPZ SHA-256:
`64f8e9d4f567c4e694ab1da67a74299f588880c47696d82dcc56e4369cfca0b5`.

The queries are synthetic but not repeated. Each workload is a deterministic
35,000 by 35,000 Cartesian product of unique float32 axes derived from the
authors' 100,000-query files:

| Operation | Query-manifest SHA-256 | Query columns | Expected U64 count | Mean hits/query |
| --- | --- | ---: | ---: | ---: |
| Point contains | `4a0a064a2609bfe53253db59a47644cc00f47e9b9cfc83c1f2d5406b61b24bc9` | 2 x 4,900,000,128 bytes | 102,886,094 | 0.08398865 |
| Range contains | `a5327c1482122cedd027a7c23e956d693a5725abdf5783b3512fbc450fb8f670` | 4 x 4,900,000,128 bytes | 97,075,897 | 0.07924563 |

The independent oracle sums x-axis coverage times y-axis coverage for each
indexed AABB under inclusive float32 boundaries. It does not call RTDL,
PyOptiX, or RT traversal. The query stream uses seven chunks: six of 200,000,000
rows and one of 25,000,000 rows. This is one full logical query batch, not seven
reported tasks and not repeated execution of one small input.

This workload establishes long sparse-query behavior on a real index. It does
not establish dense-overlap, high-output, adversarial, or original-paper query
behavior.

## Scale selection

The earlier 400,000,000-query candidate was retained as a failed scale
selection because three fresh point PyOptiX actions were about 0.263 seconds;
no RTDL worker was run before that candidate was rejected.

The selected 1,225,000,000-query scale was chosen with only public PyOptiX:

| Operation | Three fresh C samples | Median |
| --- | --- | ---: |
| Point contains | 2.785805, 2.766635, 2.721792 s | 2.766635 s |
| Range contains | 6.073499, 5.860972, 5.797781 s | 5.860972 s |

The calibration completed 6/6 workers, recorded `rtdl_worker_count: 0`, and
froze both selected manifests before any full-scale RTDL/PyOptiX dry-run pair.
Calibration SHA-256:
`e81d178a20b12fe34d528dc1b935309a9bc6ee9e9d32a63c4f4fc41ebffc2652`.

## Formal protocol

- GPU: NVIDIA RTX 4000 Ada Generation, CC 8.9, driver 550.127.05, UUID bound
  in the private preregistration.
- Runtime: Python 3.12.3, PyOptiX 9.1.0, CuPy CUDA 12x 14.0.1, NumPy 2.4.4,
  OptiX 8.0.
- Native RTDL SHA-256:
  `bb12235ab171cf7bd17bb662b7f0c3a4794b361852e9be3c38a95f6ed607e421`.
- PyOptiX LibRTS PTX SHA-256:
  `737aac24f259cf63ba54a6569582ae06cc37fcb098ad0b0d53e1eed8c6dbf1f5`.
- Two operations, two endpoints, eight fresh-process paired blocks per row,
  four RTDL-first and four PyOptiX-first.
- Prepared workers use one untimed warmup and three timed natural actions.
  Complete workers use no warmup and one timed natural action.
- Input file loading and full-file hashing are recorded but excluded from both
  endpoints. Complete includes index preparation, one action, and close.
  Prepared reports the median action after equal static-state preparation.
- Formal total: 64 workers, 32 paired cells, 128 timed actions, 32 untimed
  warmups, zero retry, discard, timeout, or mismatch.

The exact public-source entrypoints are
`scripts/generate_v4_librts_long_query_grid.py` for query generation,
`scripts/v4_librts_long_worker.py` for both arms,
`scripts/v4_librts_long_c_only_calibrate.py` for C-only scale selection,
`scripts/v4_librts_long_formal_compare.py` for the preregistered transaction,
and `scripts/v4_librts_long_independent_recount.py` for verification. RTDL uses
the public verified AABB relation-count lowering and the native library hash
above; PyOptiX uses the public custom-AABB owner and the PTX hash above. Both
output one checked U64 count for the entire streamed logical batch.

Preregistration SHA-256:
`2a74b12fcf39f9c3b9940ff199ba082ad1cd23d7d22f3812f669dba6465c7a0e`.
Formal result SHA-256:
`f35ab60dc8ffa588a1da8cd4db8c1f51c313c9db0cbf9d4bdaef911953c61800`.

## Verification and retained defect

The first independent-recount attempt correctly stopped before publishing a
result: its JSON reader required every file to be an object even though the
formal controller intentionally stores `COMMAND.json` as a string array. This
was an evidence-tool defect, not a measurement failure. Commit `8e5679efa`
fixed the verifier without changing the measured source or transaction. The
successor verifier now:

- accepts only nonempty string arrays for command files;
- reconstructs and exactly compares every command from the preregistration;
- parses stdout as one JSON document and compares it with the corresponding
  `WORKER_RESULT.json`;
- independently reads exact source bytes from Git and reconstructs all cells,
  ratios, summaries, and gate decisions.

Its focused 8/8 tests passed in a clean worktree. The canonical recount
SHA-256 is
`a733b464ac5b20307762463ce1695d360a3c990ba2364a5112d657b64a943611`.

The broader focused regression invocation ran 52 tests: 50 passed. One error
requires a historical Goal4383 report absent from this successor checkout; the
other is the old recovered-source manifest correctly rejecting the previously
changed Particle successor. Neither error exercises this LibRTS route. They
are not counted as passing tests and remain packaging/history debts. The 37
direct implementation tests and the four real-GPU streamed smoke arms passed.

## Custody and claim boundary

The compact evidence archive is
`raw/rtdl-librts-long-123f76ec9-evidence-v1.tar.gz`, 159,954 bytes, 504 members,
SHA-256
`b93e8a9f21faa2b7c68aceb7560beacd3007abe4569135fc9850d107970eb4ea`.
It contains build manifests, query manifests, calibration, dry runs,
preregistration, every formal worker record, controller output, and recounts.
The 30 GB query-column payload remains on the private RunPod volume and is
bound by per-column size and SHA-256 rather than committed to Git.

The evidence supports only the two named operations, endpoints, workload, GPU,
source, and public PyOptiX baseline. It does not prove general RTDL speedup,
arbitrary callback performance, other GPUs, CPU/clock invariance, peak memory,
dense-hit scalability, original-paper reproduction, or easier authoring. No
external review, public claim, paper-byte integration, upload, or submission
is authorized by this internal engineering result.
