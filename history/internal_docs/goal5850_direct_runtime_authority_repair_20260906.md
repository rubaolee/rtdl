# Goal5850 Direct runtime authority repair

Date: 2026-09-06

Status: `IMPLEMENTED_LOCALLY__FRESH_FORMAL_TRANSACTION_REQUIRED`

Review status: strict internal hostile self-review only. No external review,
public performance claim, manuscript claim, or cross-generation conclusion is
authorized by this document.

## 1. Retained failed transaction

The first lifecycle-corrected Goal5850 transaction used exact clean source
commit `70f85796a145bff05de9ff421198e26b6356c716`, tree
`fd62a2d305281291ece4abbc6c55ba84cf194ea4`, on an NVIDIA RTX 2000 Ada
Generation GPU. It used a fresh build, fresh schema-v2 preregistration, all 512
instrumentation workers, and all 80 formal cells with zero retry and zero
discard.

The 80-cell controller transaction passed, including both lifecycle-corrected
primary gates, prepared Direct gates, predecessor regression gates and Strong
PyOptix competence gates. The original post-import diagnostic remained
adverse, as required. However, the subsequent single-generation authority
builder failed, so the Goal5850 transaction as a whole failed.

The retained failure archive is:

`/workspace/goal5848-ada89-rtx2000-70f85796-transaction2-20260906.failure.tar.gz`

Its SHA-256 is:

`fde22b987fdaf9b3617e9371ebb391254fa856eb2495688006ca54acf60d99fc`

This transaction may not be relabeled as successful, pooled with another run,
or reused as formal timing evidence.

## 2. Retained transaction observations

These values explain what the failed transaction observed; they do not create
a single-generation authority or authorize a claim.

| Task | RTDL/Strong implementation-entry median | Worst block | RTDL/Strong old post-import median | RTDL/Direct steady median |
| --- | ---: | ---: | ---: | ---: |
| bounded relation | 0.565x | 0.796x | 3.041x (diagnostic fail) | 1.195x |
| weighted triangle | 0.286x | 0.761x | 1.293x (diagnostic fail) | 1.144x |

The successor/predecessor steady medians were `0.708x` for relation and
`0.787x` for triangle. Strong/idiomatic Pyoptix medians were `0.228x` and
`0.676x`, respectively. Every value remains subordinate to the failed custody
status.

## 3. Exact failure

The authority builder stopped on the first Direct row:

`G5848_S003_B00_CUSTOM_AABB_CLOSED_RELATION_COUNT_V1_D_DIRECT_CUDA_OPTIX`

The preregistration correctly recorded Python `3.12.3`. The native Direct C++
bridge correctly recorded:

`python = "none__native_direct_optix"`

The authority builder nevertheless applied this Python-only check to every
arm:

`worker["python"] == preregistration["python_version"]`

That check was impossible for an honest Direct receipt. Earlier transactions
had failed before this authority stage, so the latent branch error had not
previously executed against a complete real archive. Synthetic authority
fixtures also incorrectly assigned a Python version to Direct rows and hid the
defect.

## 4. Repair

The repair does not touch a workload, native implementation, timer, estimator,
threshold, schedule, sample count, or performance path.

It introduces one contract constant:

`DIRECT_RUNTIME_IDENTITY = "none__native_direct_optix"`

The Direct bridge emits that exact identity. Worker validation rejects any
other Direct identity. The independent authority now requires the Direct
sentinel only for Direct rows and still requires the exact preregistered Python
version for every Python row. Synthetic receipts now model the real split.

Two hostile tests cover both layers:

1. a coherently resealed Direct worker that substitutes a Python version fails
   the worker contract; and
2. the same substitution with matching forged process stdout and hashes still
   fails the authority builder.

The corrected local suite passes all 124 `goal5848_*_test.py` tests. Fatal Ruff
checks and `git diff --check` also pass.

## 5. Mandatory successor

This is a post-transaction verifier repair, not permission to rebuild an
authority over the failed transaction. A diagnostic replay of the corrected
verifier may be used only to discover further latent verifier defects.

A valid successor still requires:

1. one new clean pushed source commit;
2. all source-dependent artifacts rebuilt from that commit;
3. a fresh zero-sample preregistration;
4. all 512 instrumentation workers rerun;
5. all 80 formal cells rerun once with zero retry/discard; and
6. two byte-identical successful independent authority recounts.
