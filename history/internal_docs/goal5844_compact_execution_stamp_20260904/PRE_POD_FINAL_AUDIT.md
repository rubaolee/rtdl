# Goal5844 final pre-pod audit

Date: 2026-09-04

Verdict: `READY_FOR_EXACT_COMMIT_GPU_TRANSACTION`

Review kind: strict internal hostile self-review. Independent external review
count remains zero by owner instruction.

## Completion boundary

All work that can be made truthful without CUDA/OptiX hardware is complete:

| Area | State | Evidence |
|---|---|---|
| Native v8 compact execution stamp | Implemented and locally tested | 12 compact-stamp tests |
| Pinned PyOptiX source-to-loaded-binary chain | Sealed and substitution-tested | build/install receipt plus hostile replacement test |
| Python dependency closure | Fully version-fixed and observed | hashed pip report plus isolated metadata probe |
| Driver-dependent OptiX selection | Deterministic, app/result independent | frozen 7.6--9.1 compatibility registry |
| Pod setup | One local launcher and one pod-local entry point | exact-commit clone, isolated venv, fresh builds |
| Worker-zero | Scripted for both arms with disposable formal/CUDA/CuPy/Numba/XDG caches | mandatory before comparison |
| Comparison | Alternating isolated processes, all samples retained | controller schema v2 |
| Evidence custody | Hash manifest plus remote archive SHA256 | no SCP/SFTP dependency; verified failure bundle on abort |
| Downloaded verification | Recomputes workers, schedule, medians, ratios, receipts | offline verifier plus synthetic full-directory test |
| Frozen language/core boundary | Unchanged | zero diff for three Goal5838 files and `rtdl_optix_core.cpp` |

## Hostile questions and answers

**Could an old or unrelated PyOptiX `.so` be loaded?** No accepted worker can
do so. The live extension bytes must equal the installed evidence copy and the
single `_optix` member of the wheel built from the pinned clean Git archive.

**Could a worker edit samples and recompute only its own seal?** No accepted
summary can do so. The independent verifier recomputes each timing summary,
the complete alternating schedule, every within-block ratio, both aggregate
medians, and the top-level seal from all worker files. A re-sealed worker
tamper test reaches and fails this recomputation gate.

**Could a path escape the evidence root or a tar member overwrite a local
file?** No. Absolute paths, `..`, symlinks, hard links, intermediate symlink
escapes, missing regular files, and hash/size drift are rejected.

**Could preflight warm the measured cache?** No. Preflight and comparison use
different create-only roots for formal leaves, CUDA, CuPy, Numba, and XDG
caches; the controller refuses a preexisting comparison cache.

**Could a mutable installer or transitive package change the baseline?** The
ordinary path fixes Python to 3.11/3.12, pip to 26.2.1, all direct and
transitive dependencies, and `uv` fallback to 0.12.10. The receipt retains
download hashes and probes installed metadata independently. The mutable
`astral.sh/uv/install.sh` path is not used.

**Could an installed NVCC be too old for the supplied GPU?** It is not
accepted merely because it exists. The runner requires `nvcc --list-gpu-code`
to contain the observed compute capability and searches alternate installed
toolkits before attempting an agent-owned CUDA 12 toolkit installation.

**Could an arbitrary output be called a speedup?** No. Both target-met and
adverse statuses retain the same claim boundary: internal engineering only,
not formal, not externally reviewed, and not public/manuscript authorized.

**Does the synthetic offline test replace real GPU validation?** No. It tests
custody, schedule, recomputation, and tamper rejection. The existing 12 compact
stamp tests exercise native-state semantics through controlled doubles. Only a
real pod can compile the C++/CUDA path, execute OptiX, and produce performance.

## Exact remaining work after endpoint delivery

1. Run `scripts/goal5844_launch_pod_transaction.py` from the clean pushed tip.
2. If setup or either worker-zero fails, repair the pod environment or source
   defect before any timing; never bypass the receipt or preflight.
3. If comparison completes, preserve every row and inspect the four RTDL
   attribution layers against PyOptiX.
4. If RTDL/PyOptiX is above 1.25x, optimize only the measured dominant layer and
   run a new separately labeled engineering transaction.
5. Keep all wording internal until deferred external review and a later formal
   experiment authorize manuscript use.

There is no honest way to complete the three GPU-only facts locally: native v8
toolchain compilation, true OptiX execution, and measured RTDL/PyOptiX latency.
Everything required to obtain and independently verify those facts is prepared.

## Final local evidence

- Goal5844 compact stamp: 12/12 PASS.
- Goal5844 pod readiness, provenance, transfer, and verifier: 16/16 PASS.
- Combined Goal5844: 28/28 PASS.
- Goal5842 compatibility set: 64/64 PASS within the adjacent run.
- Goal5838 frozen core/selection: 9/9 PASS.
- Goal5840--Goal5844 adjacent history: 175 executed, exactly five known
  historical/current-tree identity refusals and no new functional failure.
- Python compilation, Ruff, Bash syntax, `git diff --check`, archive failure
  rehearsal, and frozen-file zero-diff checks: PASS.
