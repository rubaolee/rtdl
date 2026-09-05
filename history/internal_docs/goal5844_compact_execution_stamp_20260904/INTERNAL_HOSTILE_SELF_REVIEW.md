# Goal5844 internal hostile self-review

Date: 2026-09-04

Status:
`ACCEPT_PRE_POD_IMPLEMENTATION_WITH_GPU_BUILD_AND_PERFORMANCE_GATE_OPEN`

External review count: zero. This is an internal review and cannot be counted
as independent consensus.

## Question under review

Goal5843 measured the ordinary public triangle scalar path at 0.436590 ms,
2.910x the pinned PyOptiX-compatible API on one RTX A6000. Goal5842R1 layer
diagnostics placed the existing native v7 operation near 0.066 ms, provider
execution without the old audit near 0.143 ms, provider execution with the old
audit near 0.236 ms, and the public path near 0.276 ms. Goal5844 asks whether
the remaining public overhead can be reduced without removing semantic,
native-identity, status-before-output, and true-OptiX traversal checks.

## Implemented change

- A versioned native v8 ABI wraps the existing app-neutral v7 triangle
  operation with traversal-audit begin and finish inside one native call.
- The ordinary scalar route receives one native snapshot, validates a compact
  execution stamp, and emits a sealed compact receipt.
- The stamp binds fresh nonce/sequence, launch and context counts, raygen
  count, both program-bundle edges, one nonzero traversable, bundle/traversable
  mixes, provider identity, route identity, semantic identity, and output.
- The steady integrated route no longer calls the separate native cache-digest
  accessor. Native v8 still validates the expected digest in-call and returns
  the exact prepared-input generation, which Python checks.
- Query pointers, scalar/status/fast-receipt storage, and the successful status
  row are retained under the prepared owner's existing process/thread and
  nonreentrancy boundary.
- Full forensic expansion remains available explicitly after execution; it is
  not constructed inside ordinary public timing.
- Old DSOs without v8 continue through the existing v7 plus separate-audit
  route.
- The balanced GPU controller retains all samples, alternates arm order,
  recomputes worker seals and medians, and independently revalidates compact
  and full traversal receipts.

## Hostile findings and resolutions

### Verified: forensic snapshot ownership

The runner expands and retains the provider-owned forensic observation before
entering direct-native attribution. The direct probe uses separate scalar,
status, receipt, and audit-snapshot storage, so it cannot mutate the retained
provider receipt. The two layers remain separately labeled.

### Resolved: unnecessary core authority churn

The first implementation placed checked audit helpers in
`rtdl_optix_core.cpp`. That file is a source-authority anchor for unrelated
physical contracts. The helpers now live only in `rtdl_optix_api.cpp`, next to
the old exported audit wrappers and new v8 ABI. The core file is byte-identical
to HEAD.

### Resolved: mutable ctypes alias risk

The lazy fast-operation receipt references prepared-owner scratch storage.
That object appears only in the owner's latest lifecycle boundary and is
materialized into a plain dictionary whenever the lifecycle receipt is read.
No public execution result retains that mutable view. Compact traversal
receipts are fresh ordinary dictionaries and survive the frozen generic
execution envelope unchanged.

### Resolved: controller trusted worker summaries

The first controller read worker medians without independently checking their
seals or retained samples. It now recomputes each worker seal, sample count,
minimum, median, and maximum; checks source, arm, block, hardware, task and
claim boundaries; rehashes native/device sources; and revalidates RTDL compact
and full receipts.

### Resolved: clean source did not prove the loaded PyOptiX binary

The first Goal5844 worker checked the pinned PyOptiX Git commit/tree and hashed
the loaded extension, but those two facts did not prove that the extension was
built from that tree. The new create-only builder now builds from `git archive`,
preserves both source and selected-header archives, hashes the wheel and its
single `_optix` member, installs that wheel, copies the loaded extension, and
requires byte identity among wheel member, installed copy, and live module.
The receipt also records exact Python, CMake, C++, NVCC, Ninja, build commands,
environment, package freeze, and logs. Pip is fixed at 26.2.1; every direct and
transitive Python build/runtime dependency is version-fixed, its download hash
is retained in the pip installation report, and its actually installed version
is independently probed from the isolated interpreter. Every worker and the
controller reject a missing, altered, differently built, or differently loaded
receipt before timing.

### Resolved: pod assumptions and transfer fragility

The old preparation examples embedded GPU-model, driver, Python-path, and
historical-wheel assumptions. Goal5844 now chooses the highest compatible
frozen OptiX stack only from the observed driver; no GPU model is selected.
It selects an installed NVCC only if that compiler advertises the observed
compute capability, and otherwise attempts an agent-owned CUDA 12 toolkit
repair. Python is restricted to 3.11/3.12; the last-resort Python installer is
fixed `uv==0.12.10` installed through a hash-recorded pip report rather than a
mutable online installer script.
Physical GPU 0 is explicit in both CUDA visibility and `nvidia-smi`, so a
multi-GPU pod cannot make identity collection spuriously return several rows.
The launcher fetches the exact pushed commit and streams the evidence archive
through SSH stdout, so SCP/SFTP availability is irrelevant.

### Resolved: verifier and archive trusted pod paths

The controller now copies the DSO, native build manifest/log, symbol inventory,
device source, and complete PyOptiX build evidence into the result before the
first worker. A non-self-referential manifest hashes every result payload.
The offline verifier rejects unsafe/symbolic paths, missing or duplicate worker
rows, altered schedules, stale seals, changed raw samples, incorrect medians,
PyOptiX extension substitution, native-manifest drift, missing v8 exports, and
aggregate mismatch. It does not dereference pod-only absolute paths.

### Resolved: preflight could contaminate measured state

Minimal arm validation uses disposable RTDL-formal, CUDA, CuPy, Numba, and XDG
cache roots. The balanced comparison requires distinct nonexistent roots for
all five cache classes and a separate output root. Compilation- and timing-
sensitive inherited environment variables are cleared before either build.
The return archive excludes the venv, upstream clones, and all caches, avoiding
multi-gigabyte transfer without dropping comparison evidence.

### Resolved: active setup failures were silent after SSH returned

The pod script emits one line at each stage. Every active rejection and shell
error after output creation records the exact stage, line, and return code and
creates a compact failure archive. The host launcher retrieves, hashes, and
safely extracts that archive when the main transaction fails. A clean temporary
repository rehearsal forced the no-NVIDIA branch and verified the fail-closed
return code, stage record, and archive.

### Resolved: failure and replay paths

Tests cover native-call failure, compact device-status failure, prepared-input
generation mismatch, and replayed native audit sequence. Each case publishes
no scalar, clears local reuse identity, consumes the failed sequence, and
requires a fresh upload before a later successful execution. Native fresh
upload invalidates any uncommitted predecessor before fallible work, so a
Python-side post-launch proof rejection cannot make stale native state reusable.

## Remaining GPU-only gates

1. The new C++ path has not been compiled against a real CUDA/OptiX toolchain.
2. Native v8 success, failure cleanup, exact snapshot contents, and DSO symbol
   export have not been exercised on a GPU.
3. No balanced RTDL/PyOptiX Goal5844 timing exists. The 1.25x ratio is an
   engineering target, not a result.
4. If the ratio remains above 1.25x, retained adverse rows must drive the next
   measured optimization. Relabeling the interval or dropping slow samples is
   forbidden.
5. External review remains deferred. No public or manuscript wording is
   authorized even if the internal engineering target passes.

These are execution/evidence gates, not missing pre-pod design work. A supplied
pod does not need a prescribed RTX model or R570/R590 label. It does need an
NVIDIA Linux driver accepted by the frozen compatibility registry and either a
CUDA development toolkit or sufficient network/root access for agent-owned
installation, because native compilation cannot be simulated by Python.

## Local validation

- Goal5844 compact-stamp tests: 12/12 PASS.
- Goal5844 pod-readiness/provenance/offline-verifier tests: 16/16 PASS.
- Combined Goal5844 local suite: 28/28 PASS.
- Goal5842 causal-admission/cache/evidence compatibility set: 64/64 PASS
  inside the adjacent run.
- Goal5838 frozen-core seal verification: PASS; all three frozen files are
  unchanged.
- Goal5840--Goal5844 adjacent run: 175 tests executed with five known
  historical/current-tree identity refusals and no new functional failure.
  Two are old Goal5840 repair-freezer replay debts, one is the frozen
  Goal5842R1 implementation-commit check, and two require the current tree to
  equal the old Goal5843 preregistration. These historical artifacts must not
  be rewritten to make a successor worktree appear green.
- Python compile checks and `git diff --check`: PASS.
- Ruff checks for all new Goal5844 files and changed worker imports: PASS.
- Pod shell syntax, safe-return-archive rejection, exact-commit remote-command
  construction, no-model/no-single-driver assertions, and SSH-stream transfer
  construction: PASS.
- A broader ad hoc combination exposed three old Goal5790 integration errors
  before execution because their generated Goal5789 shared-contract freeze is
  absent from the current Git tree. That historical authority was not
  fabricated, and those errors are not counted as Goal5844 functional passes.

The focused count above must be regenerated after any further source change.

## Claim ceiling

The implementation supports only this statement before GPU work: RTDL has a
source-level, locally tested compact proof path intended to remove redundant
steady crossings while preserving the public scalar and proof boundary. It
does not yet establish lower latency, PyOptiX parity, a general language
overhead bound, hardware independence, public performance, manuscript
performance, or consensus.
