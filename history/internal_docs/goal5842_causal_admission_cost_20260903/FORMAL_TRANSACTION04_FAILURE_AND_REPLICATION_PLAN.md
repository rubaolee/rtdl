# Goal5842 transaction04 failure and independent-replication plan

## Immutable transaction04 status

Transaction04 ran on the supplied pod `root@213.173.108.100:12943` from clean
commit `c1fe04d76511f5db57ea802e8ba7c305c1a088d3`. Its bound GPU was an NVIDIA
RTX 2000 Ada Generation, UUID
`GPU-f0ab2afa-0ec0-7da9-c951-01fc713ee1e9`, compute capability 8.9, driver
580.159.04. The execution authority, native DSO, build manifest, Direct binary,
PyOptiX package/source tree, CUDA/OptiX headers, and Python environment were all
hash-bound before worker zero.

The six-call no-timing CHECK_ON/CHECK_OFF witness passed for all three tasks.
The causal cohort then completed all 216/216 fresh workers with zero failures.
Stage `03_three_arm_baseline` completed the first Direct relation composite and
failed before timing the first PyOptiX subworker. The top-level marker is
`TRANSACTION_FAILED_NO_RETRY.json` with `worker_zero_reached=true` and
`new_transaction_after_repair_permitted=false`. Transaction04 will never be
resumed, retried, renamed as a success, or silently omitted.

The complete transaction directory is preserved as the repository artifact
`pod_artifacts/goal5842_transaction04_failure.tar.gz`: 222,439 bytes, SHA-256
`d22ccd42bb55c876c5f0e575aa3a50d2110d347b037cd325fb4a0fbf1a22a603`.
A broader local custody archive containing transactions 01--04 and their
build/preflight artifacts is 9,959,557 bytes with SHA-256
`d7fd477f74f4950178416cec28423e96605743f1250970da44bef7e698c0c265`.

Key whole-file identities inside transaction04 are:

| Artifact | SHA-256 |
|---|---|
| `execution_authority.json` | `3edf3f9c84c66bb7cd13966f22e4a3c3aee2fc67ed49bcf4ba56c15ad101a043` |
| `gpu_identity_witness.json` | `d449a979ab7dad6ab0cc27717b2cd1faf0e8455cab10fd7bb565390da3379945` |
| `causal/result.json` | `828fbe5e63b9692a0bbc59a9fca4869fd4e78e6f2eb1b5e4c89af3155fbc71c1` |
| `TRANSACTION_FAILED_NO_RETRY.json` | `7d2350daed571bbea14c509089a558ee47f9c5ef7e11c483305bdafc90b2e338` |
| first Direct receipt | `29045cf9b412d13b481558ae5621f86891038245dc813ef583e10731ba0b1c62` |
| steady Direct receipt | `6120253e37c85d15432205f2baeda025485688ca88c649f3722d1d818e7f7f11` |
| failed PyOptiX marker | `de6b7d6b34208a8bf5b32c31e3a8003444c76c3b75b49cce0ebf9c5fa81cf021` |
| failed PyOptiX stderr | `c6cb5b2fdaad61768e0fb8b032497da3919859dff25529e8a8d97335c970cb99` |

## Observed results that cannot be unseen

The complete V4 causal result produced the following median CHECK_ON minus
CHECK_OFF admission-phase deltas. These values are preserved as V4 results and
must not be pooled into a later replication estimator.

| Task | Median delta | Preregistered bootstrap 95% interval | Route negative control |
|---|---:|---:|---:|
| custom-AABB relation | 38.442 ms | [36.394, 41.342] ms | 3.599 ms |
| built-in triangle | 33.431 ms | [31.488, 35.856] ms | -1.960 ms |
| built-in sphere | 28.916 ms | [27.132, 29.833] ms | 0.269 ms |

One Direct relation composite also exists. Its first complete execution was
1.012 ms and its 64-sample steady median was 0.855 ms. One block is not an
aggregate and authorizes no cross-arm or public performance claim.

## Failure root cause

`experiments.goal5842_causal_admission.baseline_worker` imports the historical
Goal5798 PyOptiX worker as a package. That worker and its `worker_common`
dependency used script-directory-only imports. The failed subworker therefore
raised `ModuleNotFoundError: No module named 'worker_common'` before importing
CUDA, constructing the provider, invoking the GPU, or entering a registered
timing phase. The defect was reproducible on the Mac through the same package
front door.

The repair is limited to conditional package-relative imports while preserving
direct-script imports. No task, query, geometry, generated device source,
provider implementation, phase boundary, schedule, warmup/repetition count,
statistic, threshold, engine code, or frozen V4 core byte changes.

## Independent replication, not retry

The next execution is a new V5 independent replication. It does not supersede,
resume, or repair transaction04. It starts from a new clean commit and a new
create-only root, repeats the complete fixed V4 task set and schedules, and
produces its own estimator. Transaction04's completed causal and Direct rows
remain outside V5's summaries; V4 and V5 may be compared descriptively but are
not pooled.

Before V5 worker zero, two timer-free gates must pass:

1. the existing six-call RTDL CHECK_ON/CHECK_OFF executable/output identity
   witness for all three routes;
2. a new package-front-door PyOptiX relation/triangle witness that executes and
   validates both frozen outputs without calling a clock in the witness module
   or recording any duration field. Historical dependencies may still import
   their existing timing helpers, but the witness does not invoke them.

The independent recount rejects any unexpected top-level or per-task witness
field, binds the device source and OptiX API to the execution authority, and
requires both tasks to reproduce one identical PTX digest. Consequently an
extra timing field cannot be hidden behind a self-reported zero counter.

If either gate fails, the V5 transaction may be repaired only before worker
zero through another explicit preregistration. After worker zero, V5 retains
the same no-retry, no-row-replacement, no-task-change, and no-post-result
optimization rules as V4.

## Claim boundary

Transaction04 is useful causal evidence and a disclosed failed full
transaction. It is not a completed one-generation Goal5842 evaluation. V5 can
become the first complete Ada-generation replication only if every fixed
worker and independent recount passes. A second distinct NVIDIA architecture
generation executing the exact V5 bytes is still required. External review,
consensus, hardware-independent claims, and public performance wording remain
unauthorized.
