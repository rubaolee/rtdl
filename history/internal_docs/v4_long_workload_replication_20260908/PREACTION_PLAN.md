# cit-Patents/4M prepared cross-GPU reproducibility preaction plan

Date: 2026-09-08 America/New_York.

Status: tooling is locally implemented and tested; GPU worker zero has not
started. The original RTX A4500 endpoint `213.173.98.71:15797` returned TCP
`Connection refused` on five checks. The replacement endpoint
`213.173.108.11:12978` passed preflight as a different RTX 4000 Ada GPU, so it
requires a separately identified `cross_gpu_reproducibility` transaction. No
result is precommitted.

## 1. Question and boundary

The prior retained successor transaction measured one genuine multi-second
prepared computation: the complete 28-segment RT-2A1 count of cit-Patents at a
4,000,000 relation-row segment cap. Its eight-block paired RTDL/PyOptiX median
was `1.057361x`, and its largest block was `1.083735x`.

This new transaction asks whether the exact task and measurement contract
reproduce on a separately registered RTX 4000 Ada GPU. It is requested after
seeing the prior result, is not a same-host temporal replay or new-workload
result, and is never pooled with the prior transaction. The unavailable
same-host temporal replay remains an explicit missing result.

Immutable prior archive:

- SHA-256:
  `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc`
- Prior formal-summary SHA-256:
  `74c8196f6e6f8e3fc13f1d4bce312087950d1e38571909042815ff6470d0672d`
- Measured successor source:
  `02e84374fc092d2bb916cca633eda9592b4ecf07`, tree
  `8aad15d686bbc9e1c3b11df998898a0a063a01f1`
- Existing exact config SHA-256:
  `491d399343fee27fbf97f6a72837ff38b4b7d04fa5324525cf3b3780caf72e1d`

The current CGO paper candidate and all prior M/E/F2/application evidence are
read-only. This transaction does not edit the canonical paper.

## 2. Frozen workload and population

| Field | Fixed value |
| --- | --- |
| Unit | `triangle_counting__cit_patents__rt_2a1__4m` |
| Dataset | complete registered `cit-Patents` edge relation |
| Algorithm | RT-2A1 on both arms |
| Segment cap | 4,000,000 relation rows |
| Expected result | checked U64 count `7,515,023` |
| Endpoint | prepared checked adapter action |
| Arms | successor `new_v4` and competent public `pyoptix` |
| Blocks | 8 fresh-process paired blocks |
| Order | 4 RTDL-first, 4 PyOptiX-first, fixed alternating sequence |
| Per worker | 1 untimed warmup, then 3 complete natural graph actions |
| Worker population | 16 total, no replacement |
| CPU condition | exact logical CPU set `{8}` before and after each worker |
| Retry/discard | forbidden |
| Threshold | paired median `<=1.20x`; every block `<=1.35x` |

The timer remains the prior timer. It encloses one complete checked adapter
action, including output comparison/digest checks and compact evidence
construction. Journal writes follow the action timer. It is not isolated GPU
traversal time, and no new endpoint is silently substituted.

If all workers and outputs are valid but a threshold is missed, the controller
records `COMPLETE__REPLICATION_TARGET_NOT_MET` and returns a complete scientific
transaction. It does not drop, replace, or rerun an adverse block.

## 3. Tooling and local validation

New create-only tools:

| File | Current SHA-256 before commit |
| --- | --- |
| `scripts/v4_long_workload_replication_controller.py` | `71b3a0f65c675d4e6ea97c954a28136a2f2c781d00da946df573bb90062272d6` |
| `scripts/v4_long_workload_replication_freeze.py` | `b7017cb02907b6b136542c763c16e5b88a9990b2ecc6475182210398385bfe22` |
| `scripts/v4_long_workload_replication_recount.py` | `348df4f6fdc3bbdda33adc516f4bff054e810f538183e09d79185df2733f7a45` |
| unchanged `scripts/v4_long_workload_worker.py` | `0009137c032dc13f03065898283c95ed087153eb11a36a69723fea32a4b7ed50` |

The independent recount imports only the Python standard library. It
reconstructs the 16-row schedule, checks all raw-file hashes, journals,
progress rows, source/native/machine identities, distinct PIDs, input/output
parity, medians, ratios and verdict. It does not trust only the controller
summary.

Local ordinary and optimized Python each pass 22/22 combined original-harness
and replication-harness tests. The tests include a full synthetic
dry-run/freeze/formal/raw-file/recount round trip, adverse target retention,
output mismatch rejection, schedule balance, fixed workload rejection, CPU
affinity failure, and rejection of raw paths outside the exact evidence root.

## 4. Exact execution sequence after the Pod returns

1. Verify the endpoint with `scripts/current_pod_ssh.py preflight`. Record the
   replacement RTX 4000 Ada UUID, driver, compute capability, Python executable
   and CPU `{8}` in a new config. The freezer must use the explicit
   `cross_gpu_reproducibility` scope and rejects a scope/GPU mismatch.
2. Fetch the pushed tooling commit into a new clean checkout. Verify the three
   new tool hashes and unchanged worker hash.
3. Use the prior config only as a read-only source of task semantics. Rebuild
   and bind replacement-machine paths and artifacts while preserving the exact
   source commit, cit-Patents bytes, algorithm, cap, output contract, timer and
   worker population. Verify the new data manifest, clean successor source,
   native library, RTDL executable and PyOptiX PTX identities.
4. Run the two-worker dry run into a new create-only directory. Both arms must
   match the exact input identity and output digest.
5. Run `v4_long_workload_replication_freeze.py` with a unique transaction ID.
   Copy the config, dry summary and generated preregistration into the new
   evidence root; hash and commit the preaction bytes before formal worker zero.
6. Run the 16 formal workers once through
   `v4_long_workload_replication_controller.py`. Preserve every output,
   journal, stdout, stderr and progress record, regardless of verdict.
7. Run `v4_long_workload_replication_recount.py` from a different clean
   checkout/path. It must use the exact committed controller and worker bytes.
8. Build a deterministic archive, verify it from another extraction, and add
   only the new transaction's numerical result and limitations to the lead's
   structured performance handoff.

No source, input, cap, repetition count, affinity, output contract, threshold
or timeout may be changed after the preregistration is frozen. Any tooling or
environment defect retains the failed transaction; a repair requires a new
successor identity.

## 5. Claim boundary

A passing transaction would support only this statement: on one separately
registered RTX 4000 Ada GPU, the same cit-Patents/4M prepared comparison
completed within the registered engineering envelope. It would not establish a
same-host temporal replay, broad GPU portability, broad application coverage,
intrinsic language overhead, independent reviewer acceptance, or submission
readiness.
