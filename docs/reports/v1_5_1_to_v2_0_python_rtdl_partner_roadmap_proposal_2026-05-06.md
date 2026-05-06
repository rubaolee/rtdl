# RTDL v1.5.1-v2.0 Python+RTDL and Partner Roadmap Proposal - 2026-05-06

## Verdict

Adopt a two-track roadmap:

- `v1.5.1` through at most `v1.5.10`, followed by `v1.6`, should deliver the
  first complete architecture: Python + RTDL.
- `v1.7` through `v2.0` should deliver the second complete architecture:
  Python + partner + RTDL.

This revises the earlier broad statement that `v1.6-v2.0` are all partner-track
milestones. Under this proposal, `v1.6` becomes the public closure point for the
first Python+RTDL architecture, and partner-system work starts after that.

## Architectural Principle

Every version should move RTDL toward app-generic Embree and NVIDIA RT engines.
The native engine should know RTDL primitives, buffer contracts, traversal
contracts, and backend capabilities. It should not know app names or
app-specific business logic.

The intended layering is:

```text
Python app/control layer
    -> RTDL language/runtime primitive contract
        -> app-generic Embree and OptiX engines
```

Later partner integration adds a partner execution layer without changing that
principle:

```text
Python app/control layer
    -> partner compute/data layer for non-RT custom logic
    -> RTDL language/runtime primitive contract
        -> app-generic Embree and OptiX engines
```

RTDL should not become a magic Python compiler or a general CUDA graph compiler.
The partner track should connect RTDL to external compute/data systems through
explicit contracts.

## Python+RTDL Track

The `v1.5.x` series should close the remaining gaps in the first architecture.
These releases are not a goal log; they are a bounded release lane for removing
known architectural debt between Python, RTDL, and app-generic native engines.

Recommended scope:

- `v1.5.1`: promote `COLLECT_K_BOUNDED` from experimental to a stable
  app-generic primitive if, and only if, it has fail-closed overflow semantics,
  Embree/OptiX parity, bounded result buffers, and benchmark evidence.
- `v1.5.2`: stabilize the generic result-buffer ABI for scalar and bounded
  collection outputs.
- `v1.5.3`: reduce Python/native bulk-copy overhead for source-tree workflows
  by using typed, contiguous, preallocated buffers instead of nested Python
  result materialization on hot paths.
- `v1.5.4`: formalize persistent scene/query/result buffer lifecycle for
  repeated workloads.
- `v1.5.5`: strengthen app-generic OptiX parity and performance evidence for
  the stable primitive set.
- `v1.5.6-v1.5.10`: reserve for hardening, cross-platform validation,
  documentation, release-facing wording, and removal of remaining app-name
  leakage from supported Embree/OptiX primitive paths.
- `v1.6`: declare the first Python+RTDL architecture complete only if the
  supported surface is app-generic, documented, benchmarked, and externally
  reviewed. This closure is a key release and architecture decision requiring
  Codex plus two independent external AI reviews, normally Claude and Gemini,
  with artifacts saved under `docs/reports/`.

The exact numbering may change, but `v1.5.10` should be treated as the maximum
patch-style runway before a `v1.6` closure decision. If the Python+RTDL
architecture cannot be closed by then, the project should explicitly reassess
scope rather than extending the lane indefinitely.

Before each `v1.5.x` promotion after `v1.5.1`, the project should check whether
the buffer ABI or lifecycle change is semantically breaking enough to require
early `v1.6` closure rather than another patch-style milestone. The numbering is
a planning lane, not permission to hide breaking architecture work inside patch
labels.

## Collect Primitives And Zero-Copy

`COLLECT_K_BOUNDED` and zero-copy are related but not the same.

`COLLECT_K_BOUNDED` is a language/runtime primitive. It defines what RTDL
returns when traversal produces bounded row-like candidate output:

```text
query_id -> up to K candidate ids, plus count and overflow/fail-closed status
```

Zero-copy is a memory and interoperability architecture. It defines how Python,
RTDL, native engines, CPU memory, and GPU memory avoid repeated bulk copies.

The fundamental fix for bulk-copy overhead is a stable buffer ownership model,
not merely a faster Python wrapper. RTDL should move toward explicit typed
buffers:

```text
SceneBuffer
QueryBuffer
ResultBuffer
```

Each buffer should have at least:

```text
pointer or backend handle
dtype
shape
stride/layout
device: cpu | cuda
lifetime owner
mutability
capacity
valid count
overflow/fail-closed status
```

For Embree, this can begin with contiguous CPU buffers visible to Python through
NumPy-compatible memory. For OptiX, true zero-copy is only possible when data is
already GPU-resident or shareable through a supported device-memory mechanism.
Otherwise, the practical target is to avoid repeated host/device transfers by
using persistent GPU buffers, pinned/staging buffers, and explicit reuse.

For `v1.5.2`, a CPU-contiguous-first result-buffer ABI is acceptable if the
release states that GPU-resident zero-copy is not claimed. For `v1.5.3`, pinned
or staging-buffer reuse may be claimed only as reduced-copy or reduced-transfer
reuse, not as true zero-copy. True GPU zero-copy wording requires an explicit
GPU-resident or externally shareable device-memory path.

CUDA unified memory or managed-memory paths must be named explicitly if used.
They should not be described as true zero-copy unless the measured access and
ownership semantics justify that exact claim.

## Partner Track

The `v1.7-v2.0` track should introduce Python + partner + RTDL after the
Python+RTDL surface has a stable primitive and buffer contract.

The partner track should focus on explicit interoperability with external
systems that own non-RT computation, custom reductions, dataframe/tensor
processing, or application-specific logic. Candidate partner styles include
Triton, CuPy, Numba, PyTorch/DLPack-style tensors, dataframe systems, or other
explicit adapters.

RTDL should remain the traversal/runtime layer. The partner should own custom
compute logic that does not belong inside the RT engine.

Recommended scope:

- `v1.7`: partner API design and one minimal adapter. The initial baseline
  partner candidate should be a DLPack-compatible tensor handoff, with PyTorch
  or CuPy as the first practical consumer. Triton, Numba, dataframe engines, and
  other systems remain candidates for later adapters, but v1.7 should not start
  with an open-ended partner menu.
- `v1.8`: partner buffer/execution contract and conformance tests.
  The v1.8 artifact must record the conformance-suite pass-rate baseline and
  the exact adapter paths covered. A later v2.0 claim must meet or exceed the
  applicable baseline rather than merely stating that tests exist.
- `v1.9`: partner examples, cross-platform validation, and failure-mode
  hardening.
- `v2.0`: public Python+partner+RTDL milestone if partner contracts are
  documented, measured, and externally reviewed.

The `v2.0` measurement gate should include exact metrics rather than broad
speedup language: conformance pass rate, buffer transfer counts, round-trip
latency for named adapter paths, and benchmark comparisons against explicit
Python materialization or host-copy baselines. No partner-track speedup claim is
allowed without exact-subpath evidence.

## Release Gates

No release in either track should claim success unless all applicable gates are
met:

- app-generic Embree and OptiX engine paths for the claimed primitive surface;
- no native app-name dependency in stable primitive paths;
- same-contract correctness across Embree and OptiX where both are claimed;
- Embree-only or OptiX-only support is acceptable only when the unsupported
  backend is not claimed and the release clearly states the covered backends;
- clear fail-closed behavior for bounded collection overflow and unsupported
  backend cases;
- bounds-testing validation for bounded collection capacity, exact `K`, zero
  results, full buffers, overflow, deterministic count reporting, and
  fail-closed behavior;
- benchmark evidence for exact claimed subpaths only;
- public wording that does not claim package install, whole-app speedups, broad
  RTX speedups, or unsupported backends;
- required external AI review and consensus artifacts saved in `docs/reports/`.

For this roadmap, "Codex" means the OpenAI Codex coding agent acting as the
internal project reviewer/implementer in the active workspace. Important release
or architecture decisions require at least Codex plus one independent external
AI review. Key release, public-claim, architecture-boundary, or roadmap
decisions require Codex plus two independent external AI reviews, normally
Claude and Gemini. A review counts only if its output is saved under
`docs/reports/` and contains an explicit acceptable verdict or a precisely
bounded conditional verdict. Blocking disagreement must be resolved in the
proposal or recorded as a non-consensus item.

The `v1.6` Python+RTDL public closure, the `v2.0` Python+partner+RTDL public
closure, and any broad public architecture or performance claim are key
decisions under this rule.

## Recommendation

Proceed with this roadmap if external review agrees:

```text
v1.5.1-v1.5.10: finish Python+RTDL architecture
v1.6: close and publish Python+RTDL as the first architecture milestone
v1.7-v2.0: build Python+partner+RTDL as the second architecture milestone
```

This roadmap gives v1.5.1 a clear first task: promote `COLLECT_K_BOUNDED` as an
app-generic primitive without solving the entire partner ecosystem prematurely.
