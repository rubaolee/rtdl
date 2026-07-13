# Goal5063 RT-BarnesHut Paper-Reproduction Requirements And Plan

Date: 2026-07-06

## Decision

RT-BarnesHut is not currently a completed RTDL paper-reproduction app.

The repository has substantial Barnes-Hut / RT-BarnesHut-style benchmark work,
including author-code build/timing evidence and RTDL-side 3-D diagnostic
evidence. That work must not be silently promoted into paper reproduction.
The next correct step is to create a separate paper-reproduction app line under
`Paper-reproduction-apps/rt-barneshut-paper/`.

## What Already Exists

### User-facing benchmark assets

- `examples/current/research_benchmarks/barnes_hut/rtdl_barnes_hut_benchmark_app.py`
- `examples/current/apps/simulation/rtdl_barnes_hut_force_app.py`
- `src/rtdsl/app_adapters/barnes_hut.py`
- `src/rtdsl/app_reference/aggregate_force_math.py`

These are benchmark/application assets. They are useful implementation sources
but not a paper-reproduction package.

### Historical author-code evidence

The author artifact was previously identified as:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `BarnesHutRT`
- commit: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- sample: `samples/cmdline/s01-rtbarneshut`
- target: `rtbarneshut`

The author program was built on an RTX A5000 pod with OptiX SDK 8.1 and CUDA
12.6 after compatibility edits:

- add CUDA compile flag `-include array`;
- patch hardcoded `gpuDeviceID = 1` to `0` for a single-GPU pod;
- rebuild with controlled `NUM_POINTS` values such as 8192 or 32768.

The author `new` mode produced orientation force-phase timings, but same-input
`treelogy` reload segfaulted in the old pod. Therefore the old author timing
is not a same-input comparator.

### Historical RTDL evidence

The strongest RTDL-side diagnostic was a 3-D scalar inverse-square subtree
diagnostic on an authors-generated input:

- body count: 32768;
- resident kernel min: about `0.50 ms`;
- correctness: zero structural deltas against RTDL's own Python reference;
- boundary: not the same tree/traversal contract as the author program.

This is useful engineering evidence, not proof of RT-BarnesHut paper
reproduction.

### RT-DBSCAN check

RT-DBSCAN also has a current benchmark app and same-contract evidence, but no
post-V4 paper-reproduction app under `Paper-reproduction-apps/`. It is not the
missing paper-reproduction app the user is asking for here.

## Required Paper-Reproduction Gates

Goal5063 defines these gates before any completed claim is allowed:

1. Build the pinned author artifact as `AuthorOfficial`.
2. Produce or expose author per-body force output or a stable checksum for the
   same input used by RTDL.
3. Run RTDL on the same input under a documented RTDL contract.
4. Compare numeric output under explicit tolerances.
5. Report performance under matched phase boundaries.
6. Disclose every author-source patch as compatibility-only, author-derived,
   or RTDL-defined.

## v2.14.4 Route Principle

RTDL is the language/runtime system; RT-BarnesHut is an app on top of it.

Allowed RTDL/system work:

- generic prepared spatial hierarchy or aggregate-frontier traversal;
- generic device-column / partner continuation handoff;
- generic grouped stream or vector-reduction contracts.

App-owned work:

- author checkout and patches;
- Barnes-Hut input generation/import;
- opening rule and force-law interpretation;
- output/checksum formatting and comparator reporting.

Disallowed promotion:

- Barnes-Hut-specific native force primitive in RTDL core;
- speedup claim from old non-same-contract rows;
- calling existing benchmark evidence a paper reproduction.

## Files Added In This Step

- `Paper-reproduction-apps/rt-barneshut-paper/README.md`
- `Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json`
- `Paper-reproduction-apps/rt-barneshut-paper/author_patches/README.md`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/apply_author_official_patch.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/check_pod_environment.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/setup_author_official.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_smoke.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_same_input.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_force_outputs.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_comparator_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_rtdl_diagnostic.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_rtdl_comparison_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_performance_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_performance_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_local_contract_gate.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_local_contract_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_reference.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_rtdl_cuda_gate.sh`
- `Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_author_contract_to_rtdl_reference.py`
- `Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py`
- `tests/goal5063_rt_barneshut_paper_reproduction_scaffold_test.py`

## Source Audit Update

The pinned author source was cloned locally under the ignored paper-app
workspace for inspection:

`Paper-reproduction-apps/rt-barneshut-paper/_work/source_audit/OWLRayTracing`

The source inspection confirmed:

- `hostCode.cu` implements `new`, `treelogy`, and `csv` modes.
- `new` writes a Treelogy-style text input with five header rows followed by
  `mass x y z vx vy vz` rows.
- `treelogy` reads the same seven-column body rows.
- the author executable reports timing but does not normally write per-body
  force outputs.
- `GeomTypes.h` hardcodes `constexpr int NUM_POINTS = 100000000`.
- `hostCode.cu` hardcodes `int gpuDeviceID = 1`.

The app now includes a Python author-contract reference that mirrors the
author source's local CPU contract:

- z-order sort using the float bit-level comparator from `less.hpp`;
- body IDs reassigned after sort, matching `hostCode.cu`;
- groups of `BUCKET_SIZE=32` sorted bodies collapsed into bucket leaves;
- bucket leaves inserted into the author octree with the same octant rule;
- center of mass recomputed recursively;
- scalar force rule `0.1 * m1 * m2 / r^2`;
- opening rule `node.s < distance * THRESHOLD`.

This reference is for contract localization and local debugging. The paper
comparator remains the patched author binary.

Important alignment finding:

The author program reassigns `point.idX` after z-order sorting, and its
`computedForces[i]` output is in that sorted/reassigned order. Therefore
RTDL-vs-author force-file comparison must feed RTDL an author-sorted same-input
file. Otherwise force vector indices are misaligned before any mathematical
comparison begins. The `run_same_input_rtdl_comparison_gate.sh` gate now writes
an author-sorted input file before invoking RTDL.

Important force-law finding:

The historical RTDL Goal2547 diagnostic reports an unscaled inverse-square
scalar sum. The author source multiplies force contributions by
`GRAVITATIONAL_CONSTANT = 0.1`. The paper-app force-output path therefore
applies a `0.1` scale to RTDL force files before comparing with author force
outputs. Without this scale, even a one-bucket exact pairwise case differs by
exactly the force-law constant rather than by a tree/traversal issue.

The new patch script now applies three comparator/build edits:

1. changes the active `NUM_POINTS` definition to the requested body count;
2. makes CUDA device ordinal configurable through `RTBH_CUDA_DEVICE`, default
   `0`;
3. adds `RTBH_FORCE_OUT`, an optional per-body force dump after the measured
   force phase.

The force dump is comparator instrumentation. It must not be counted inside
the author force-phase timing, and it does not intentionally change tree
construction, traversal, or force accumulation.

The patch script was tested against the real pinned author source. An initial
regex would have matched a commented `NUM_POINTS` line; this was fixed by
anchoring the pattern to the active line (`^constexpr int NUM_POINTS = ...`).

## Local Contract Alignment Update

The paper app now has two RTDL-reference comparison modes:

- `current-rtdl-diagnostic-tree`: feeds author-sorted bodies to the historical
  RTDL diagnostic tree builder. This mode preserves the known pre-existing
  contract gap for diagnosis.
- `author-prepared-arrays`: converts the author z-order bucket tree into
  generic flattened aggregate arrays and uses the author's traversal policy.
  This is app-layer contract preparation over a generic aggregate-array shape;
  it is not a Barnes-Hut force primitive in RTDL core.

Local synthetic evidence:

| Input | RTDL-reference mode | Result |
| --- | --- | --- |
| 8 bodies | current diagnostic tree | match, max abs error `4.440892098500626e-16` |
| 64 bodies | current diagnostic tree | mismatch, max rel error `0.06766160877325857`, mismatch count `64` |
| 64 bodies | author-prepared arrays | match, max abs error `2.2737367544323206e-13`, mismatch count `0` |

Interpretation:

- force-law scaling, author post-sort output order, and one-bucket exact
  pairwise semantics are aligned;
- the previous 64-body mismatch was caused by tree/traversal contract
  differences, not by indexing or gravitational scaling;
- a paper-app route can express the author bucket-tree contract as generic
  flattened aggregate arrays, but the patched author binary POD gate remains
  the authoritative comparator.

## Next Work

1. On a CUDA/OptiX Linux pod, run `scripts/check_pod_environment.sh` to verify
   CUDA driver access, nvcc, CMake, OptiX headers, and Torch CUDA before the
   heavier gates.
2. Build the author artifact with
   `scripts/setup_author_official.sh`.
3. Before the patched-author comparator gate, run
   `scripts/run_author_contract_rtdl_cuda_gate.sh` as a cheap RTDL-side gate.
   This compares the Python author-contract reference to the RTDL CUDA
   diagnostic over author-prepared generic aggregate arrays.
4. Run author `new` mode with `RTBH_FORCE_OUT` and verify that per-body forces
   are written.
5. Run author `treelogy` mode on the generated input with `RTBH_FORCE_OUT`.
   This directly retests the historical same-input segfault.
6. Compare the two author force files with `compare_force_outputs.py`.
7. Run the RTDL 3-D diagnostic on the exact same input.
   The RTDL diagnostic now has an optional per-body `--force-out` path so it
   can produce a comparable force file. The same-input gate now prepares the
   author bucket tree as generic flattened aggregate arrays and invokes the
   diagnostic with `--traversal-policy author-opening`.
8. Compare author `treelogy` force output against RTDL force output to measure
   the actual remaining gap against the patched author binary.
9. Decide whether v2.14.4 public APIs are sufficient or whether a generic
   aggregate-frontier/device-column primitive is missing.

## Local Verification

Local Windows verification completed:

- `py -m unittest tests.goal5063_rt_barneshut_paper_reproduction_scaffold_test`
  passes with 23 tests. The added behavior tests exercise
  `scripts/run_same_input_performance_gate.py` against fixture summaries and
  `scripts/run_full_pod_reproduction_gate.py` with stubbed gate outcomes:
  ready cases verify the narrow RTDL/author force-kernel ratio and full-gate
  phase-boundary-review status; blocked cases verify missing-summary and
  failed-preflight fail-closed behavior.
- The test suite now also executes `scripts/run_local_contract_gate.py` in a
  temporary run directory and verifies all three local probes: one-bucket
  current diagnostic match, multi-bucket current diagnostic gap, and
  multi-bucket author-prepared aggregate-array match.
- The test suite exercises `scripts/run_phase_boundary_review_gate.py` with a
  matching review artifact and with mismatched phase/ratio fields, confirming
  that completion cannot be obtained by writing unbound review booleans.
- The test suite also exercises the author-source contract audit logic on a
  minimal source fixture, confirming that the gate checks the source anchors
  rather than merely checking file existence.
- All paper-app shell scripts pass `bash -n`.
- `rt_barneshut_reproduction.py --mode status` writes the expected in-progress
  JSON.
- `rt_barneshut_reproduction.py --mode rtdl-3d-diagnostic` fails closed on the
  local machine because `torch` is unavailable, and writes a structured
  `blocked_missing_runtime_dependency` JSON. A local smoke also confirms that
  the blocked JSON records `prepared_arrays_json` and
  `traversal_policy=author-opening` when the author-prepared route is selected.
- Local author-contract vs RTDL-reference probes now show:
  - `--synthetic-count 8`: match, max abs error `4.440892098500626e-16`,
    max rel error `3.108429370453451e-16`, mismatch count `0`.
  - `--synthetic-count 64 --rtdl-contract current-rtdl-diagnostic-tree`:
    mismatch, max abs error
    `38.30712417614427`, max rel error `0.06766160877325857`, mismatch
    count `64`.
  - `--synthetic-count 64 --rtdl-contract author-prepared-arrays`: match,
    max abs error `2.2737367544323206e-13`, max rel error
    `5.071228799412329e-16`, mismatch count `0`.
- `scripts/run_local_contract_gate.sh` now wraps the three local probes above
  into one fail-closed gate. It writes
  `_runs/local_contract_gate/summary.json`, passes only when the one-bucket
  current diagnostic matches, the multi-bucket current diagnostic exposes the
  expected contract gap, and the multi-bucket author-prepared aggregate-array
  route matches. This remains a local CPU contract gate; it does not replace
  the patched-author binary POD comparator.
- `scripts/run_author_source_contract_gate.sh` now audits a dedicated pinned
  raw author checkout under `_work/source_contract_gate/OWLRayTracing`. It
  verifies that the raw source is clean, at commit
  `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`, has the expected `new` and
  `treelogy` input contracts, z-order sort, post-sort `idX` reassignment,
  bucket leaf construction, center-of-mass recomputation, opening rule, and
  inverse-square force-law constants. It intentionally checks that the raw
  source does not already contain the `RTBH_FORCE_OUT` comparator patch.
- The actual `scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py`
  prepared-array reader consumes the author-prepared JSON and reproduces the
  same 64-body author-contract reference locally under `author-opening`
  traversal policy.
- `scripts/run_author_contract_rtdl_cuda_gate.sh` is now available as the next
  POD-side RTDL diagnostic gate before the patched author binary gate.
- `scripts/check_pod_environment.sh` is now available as the first POD-side
  preflight. It writes `_runs/pod_preflight/pod_environment_preflight.json`
  and distinguishes `ready_for_author_build` from `ready_for_rtdl_cuda_gate`.
- `scripts/run_full_pod_reproduction_gate.sh` is now available as the
  one-command POD entry point. It first runs the local contract gate and
  author-source contract gate, then the environment preflight, RTDL CUDA
  author-contract gate, patched-author same-input gate, and author-vs-RTDL
  same-input force gate when their dependencies are satisfied, then summarizes
  same-input timing fields for phase-boundary review. It always writes
  `_runs/full_pod_reproduction_gate/summary.json` with pass/fail/skipped gate
  statuses and keeps `paper_reproduction_complete=false` until correctness and
  the matched performance phase-boundary review gate are both closed.
- `scripts/run_same_input_performance_gate.sh` reads the existing author and
  RTDL summaries after correctness closes, reports the author `rt_core_force_ms`
  and RTDL `resident_kernel_min` fields under an explicit narrow force-kernel
  boundary, and keeps `performance_review_complete=false` until a human review
  accepts the phase boundary.
- `scripts/run_phase_boundary_review_gate.sh` validates that the human
  phase-boundary review artifact is bound to the same performance summary,
  phase labels, and ratio. It can write a draft template, but it only accepts
  after a reviewer sets `performance_review_complete=true` and
  `phase_boundary_accepted=true` on a matching review artifact.
- `scripts/run_completion_audit.sh` reads the manifest, local contract gate
  summary, author-source contract gate summary, full POD gate summary, and
  phase-boundary review gate summary. It keeps
  `paper_reproduction_complete=false` until all required evidence is present.
- Local execution of `scripts/check_pod_environment.sh` fails closed with
  `ready_for_author_build=false` and `ready_for_rtdl_cuda_gate=false`, as
  expected on the Windows/WSL machine without CUDA, OptiX, CMake, or Torch
  CUDA.
- Local execution of `scripts/run_full_pod_reproduction_gate.sh` first passes
  the local contract gate and author-source contract gate, then fails closed at
  the POD preflight stage and writes
  `_runs/full_pod_reproduction_gate/summary.json`. The summary marks
  `overall_status=blocked_by_pod_environment_preflight`, skips the downstream
  CUDA/author gates with dependency reasons, and keeps
  `paper_reproduction_complete=false`.
- Local execution of `scripts/run_completion_audit.sh` writes
  `_runs/completion_audit/summary.json` and returns incomplete. The audit marks
  the author artifact pin, local contract gate, author-source contract gate,
  and full-gate summary as present, but marks same-input correctness,
  same-input timing, and the phase-boundary review gate as not complete. This
  is the expected current state.
- Interpretation: one-bucket exact pairwise force law, author output order,
  and RTDL force scaling are aligned. Multi-bucket cases only fail under the
  old RTDL diagnostic tree contract; author-prepared aggregate arrays close the
  local contract gap.
- `git diff --check` passes.
- The previous POD address checked in this thread refused SSH connection, so
  CUDA/OptiX execution remains pending external POD availability.

## Next POD Command Sequence

From the repository root on a CUDA/OptiX Linux pod:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.sh
```

From a local control machine with SSH access to the pod, upload the minimal
current source package, run the full gate remotely, and pull `_runs` evidence
back:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py \
  --host <pod-host> \
  --port <pod-port>
```

The remote runner includes `src/`, the Barnes-Hut diagnostic script, and the
RT-BarnesHut paper-app directory, while excluding generated `_work/`, `_runs/`,
`_data/`, and cache directories.

Without a live pod, validate the remote upload package locally:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py \
  --package-only
```

The package-only mode writes a local summary with `overall_status=package_ready`
only when the required source roots are present and no excluded generated
directory is included in the archive. It also checks critical gate entry files
individually, including the environment preflight, author patcher, source
contract gate, full POD gate, same-input comparison gate, and performance
summary gate.

The full gate is the preferred entry point. For manual staged debugging, use:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.sh
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/check_pod_environment.sh
```

If the environment preflight passes, run:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_rtdl_cuda_gate.sh
```

If that RTDL-side contract gate closes, run:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_comparator_gate.sh
```

If the author same-input comparator closes, run:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_rtdl_comparison_gate.sh
```

Expected interpretation:

- if author `new` and author `treelogy` force files do not match, fix the
  author same-input comparator before touching RTDL;
- if author files match but author-vs-RTDL does not, the gap is the RTDL
  tree/traversal contract, not input reproducibility;
- if author-vs-RTDL matches under reviewed tolerance, then performance can be
  measured under the same phase boundary.

After `same_input_performance_gate` reports
`ready_for_phase_boundary_review`, generate and review the phase-boundary
template:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.sh --write-template
```

The reviewer must edit
`_runs/same_input_performance_gate/phase_boundary_review.json` to accept or
reject the matched phase boundary, then rerun:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.sh
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.sh
```

## Exit Label

`rt_barneshut_paper_reproduction_scaffold_created__same_input_author_comparator_open`
