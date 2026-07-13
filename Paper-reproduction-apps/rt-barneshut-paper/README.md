# RT-BarnesHut Paper Reproduction App

This directory is the RT-BarnesHut paper-reproduction engineering project.
It is separate from the promoted benchmark-app suite. Benchmark apps exercise
RTDL broadly; this project keeps the paper comparator, inputs, RTDL route, and
claim boundary together.

Paper:

- `RT-BarnesHut: Accelerating Barnes-Hut Using Ray-Tracing Hardware`
- PPoPP 2025
- DOI: `10.1145/3710848.3710885`

## Current Status

This project has completed the bounded same-input RT-BarnesHut prepared-state
force-output reproduction against `AuthorOfficial` on a CUDA/OptiX POD. It has
not completed independent tree construction or the full paper Section 5
evaluation matrix.

The existing RTDL codebase already has Barnes-Hut-style benchmark routes for
node coverage, aggregate-frontier candidates, and app-layer force reduction.
Those routes were useful starting assets, but the paper app now keeps the
author comparator, same-input prepared state, RTDL route, force comparison, and
phase-boundary review together.

Local contract probes are now in place:

- an 8-body single-bucket synthetic case matches the author-contract Python
  reference and the current RTDL Python diagnostic reference after applying
  the author's `GRAVITATIONAL_CONSTANT = 0.1` force scale;
- a 64-body multi-bucket synthetic case intentionally exposes the current
  contract gap: the author bucket-tree contract and the historical RTDL
  diagnostic tree contract diverge once more than one bucket is involved.
- the same 64-body case matches when the app expresses the author bucket tree
  as generic flattened aggregate arrays and uses the author traversal policy.

The full POD gate is closed for the bounded 32,768-body same-input run:

- patched author `new` vs `treelogy` same-input force output: exact match;
- patched author vs RTDL force output: `32768` bodies, `mismatch_count = 0`,
  `max_abs_error = 1830.0`, `max_rel_error = 2.1112736725325853e-06`;
- narrow force-kernel phase comparison pending explicit phase-boundary
  acceptance: RTDL resident-kernel min `0.856544017791748 ms` and mean
  `0.9283008098602294 ms` vs author RT force phase `2.083 ms`,
  min-ratio `0.4112069216475026`, mean-ratio `0.4456556936438931`.

This is not a whole-program runtime claim. Tree preparation, extension
compilation, tensor preparation, force-file writing, author preprocessing, and
author execution time are reported separately.

The same timing artifact also reports the broader envelope around that narrow
kernel phase: RTDL spends about `469.35 ms` in reported CPU tree preparation,
extension compilation, host-to-device tensor preparation, and the resident
kernel, while the author's reported preprocessing plus execution is about
`185.45 ms`. That broader reported envelope is therefore not favorable to RTDL
(`2.53x` slower) even though the isolated resident force-kernel phase is lower
under the narrow pending-review comparison.

## What Is Included

| Path | Purpose |
| --- | --- |
| `data/manifest.json` | Paper, author artifact, known input, and comparator status. |
| `author_patches/` | Compatibility and comparator patch notes for the author program. |
| `scripts/apply_author_official_patch.py` | Applies documented compatibility edits plus optional `RTBH_FORCE_OUT` and `RTBH_PREPARED_ARRAYS_OUT` comparator/debug hooks to the author source. |
| `scripts/check_pod_environment.sh` | Checks CUDA driver, nvcc, CMake, OptiX headers, and Torch CUDA before POD gates. |
| `scripts/setup_author_official.sh` | Clones and builds the RT-BarnesHut author artifact with documented compatibility edits. |
| `scripts/run_author_smoke.sh` | Runs the built author binary in its supported `new` mode for orientation and input generation. |
| `scripts/run_author_same_input.sh` | Runs the patched author binary in `treelogy` mode on an existing input and writes per-body force output when supported by the patch. |
| `scripts/compare_force_outputs.py` | Compares per-body force output files under explicit tolerances. |
| `scripts/run_author_source_contract_gate.sh` | Audits the pinned raw author source for the input, z-order, bucket-tree, opening-rule, and force-law anchors assumed by this app. |
| `scripts/run_author_comparator_gate.sh` | One-command POD gate for author build, `new`, same-input `treelogy`, and force comparison. |
| `scripts/run_rtdl_diagnostic.sh` | Runs the current RTDL 3-D diagnostic route on generated or provided body input. |
| `scripts/run_author_contract_rtdl_cuda_gate.sh` | POD diagnostic gate comparing the Python author-contract reference to the RTDL CUDA route over author-prepared aggregate arrays. |
| `scripts/run_same_input_rtdl_comparison_gate.sh` | Uses the patched author binary's dumped prepared aggregate arrays, runs RTDL on that same-input contract with `author-optix-payload`, and compares RTDL force output to the author force output. |
| `scripts/run_same_input_performance_gate.sh` | Summarizes same-input author and RTDL timing fields after correctness gates close; it does not authorize a paper-performance claim by itself. |
| `scripts/run_phase_boundary_review_gate.sh` | Validates that a human phase-boundary review artifact is bound to the same timing summary, phase labels, and ratio. |
| `scripts/run_full_pod_reproduction_gate.sh` | One-command POD gate for environment preflight, RTDL author-contract CUDA comparison, patched-author same-input comparison, author-vs-RTDL same-input comparison, and timing summary. |
| `scripts/run_remote_full_pod_gate.py` | Uploads the minimal current source package to a reachable Linux POD, runs the full POD gate there, and pulls `_runs` evidence back locally. |
| `scripts/run_completion_audit.sh` | Reads manifest and gate summaries and refuses a completed paper-reproduction claim until all required evidence and phase-boundary review are present. |
| `author_contract_reference.py` | Python reference for the author source's bucket-tree scalar force contract, used to localize contract gaps before POD runs. |
| `scripts/run_author_contract_reference.sh` | Runs the Python author-contract reference on a provided or synthetic input. |
| `scripts/compare_author_contract_to_rtdl_reference.py` | Local CPU diagnostic comparing the author bucket-tree contract against the existing RTDL Python diagnostic tree contract. |
| `scripts/run_local_contract_gate.sh` | Runs the three local contract probes as one fail-closed gate: one-bucket current diagnostic match, multi-bucket current diagnostic gap, and multi-bucket author-prepared aggregate-array match. |
| `rt_barneshut_reproduction.py` | Project entry point for status, manifest checks, and bounded RTDL diagnostic execution. |

Generated source, data, and run products should stay under ignored local
directories:

- `_work/author_official/`
- `_data/`
- `_runs/`

## Comparator Boundary

The target comparator is `AuthorOfficial`: the pinned author RT-BarnesHut
source plus compatibility edits required to build and run on the current CUDA,
OptiX, and single-GPU pod environment.

The known author artifact is:

- repository: `https://github.com/vani-nag/OWLRayTracing`
- branch: `BarnesHutRT`
- pinned commit: `2a3c60da0bbbd00ff1777cb57ec2089cb0029cf7`
- sample target: `samples/cmdline/s01-rtbarneshut`
- binary target: `rtbarneshut`

Compatibility edits are allowed for build portability, device ordinal, and
controlled body count. Algorithmic edits require a separate disclosure and
must not be hidden inside a performance comparison.

## RTDL Design Boundary

RTDL should provide generic machinery:

- prepared spatial hierarchy / aggregate-frontier traversal where available;
- device-column and partner handoff for numeric continuations;
- generic grouped reduction or stream-style continuation contracts.

The RT-BarnesHut app owns paper-specific logic:

- author source checkout and build configuration;
- body input generation or import;
- Barnes-Hut opening policy and force-law interpretation;
- output checksum and comparator reporting.

The historical benchmark route is still not the paper app. The completed
reproduction route consumes the paper app's same-input `AuthorOfficial`
prepared state and comparator evidence.

## Commands

Show current project status:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py \
  --mode status \
  --output /tmp/rt_barneshut_status.json
```

Build the author artifact on Linux after installing CUDA and OptiX:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.sh
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/check_pod_environment.sh
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/setup_author_official.sh
```

The source-contract gate uses a dedicated ignored checkout under `_work/` and
checks the pinned raw source before compatibility patches are applied. It does
not build or run the author binary.

Run the author binary in supported `new` mode:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_smoke.sh
```

Run the patched author binary on the same input:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_same_input.sh \
  Paper-reproduction-apps/rt-barneshut-paper/_runs/author_smoke/rtbarneshut_author_new_input.txt
```

Run the author comparator gate:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_comparator_gate.sh
```

Run the current RTDL 3-D diagnostic route:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_rtdl_diagnostic.sh
```

The RTDL diagnostic writes `rtdl_forces.txt` when the CUDA/Torch runtime is
available. The paper-app wrapper scales that force file by the author's
`GRAVITATIONAL_CONSTANT = 0.1`; the diagnostic kernel reports an unscaled
inverse-square scalar sum. With author binary dumped prepared arrays and
`--traversal-policy author-optix-payload`, this is the bounded same-input
paper-comparison route.

After the author comparator gate has produced author forces, run:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_rtdl_comparison_gate.sh
```

This gate is expected to pass after `run_author_comparator_gate.sh` has produced
the author same-input force file and dumped prepared arrays. The CUDA
diagnostic consumes the generic flattened aggregate shape with
`--traversal-policy author-optix-payload`; the paper app owns the
author-binary prepared-state dump and comparator boundary.

For local contract debugging without CUDA/OptiX:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_reference.sh
```

This produces a Python reference force file for the author source's bucket-tree
scalar force rule. It is a debugging reference for contract alignment; the
paper comparator remains the patched author binary.

Compare the author contract reference against the current RTDL diagnostic
reference locally:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/scripts/compare_author_contract_to_rtdl_reference.py \
  --synthetic-count 64 \
  --output /tmp/rtbh_author_vs_rtdl_reference_gap.json
```

For this comparison, RTDL is fed the author-sorted body order so force vector
indices align with the author program's output order. Any remaining mismatch is
therefore a tree/traversal contract gap, not an output-index mismatch.

Run the local contract gate:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_local_contract_gate.sh
```

This wraps the one-bucket match, multi-bucket historical diagnostic gap, and
multi-bucket author-prepared aggregate-array match into a single local gate.
It is still a local CPU contract gate; the patched author binary remains the
paper comparator.

On a CUDA Linux POD, validate the RTDL CUDA diagnostic route against the Python
author-contract reference before building the patched author binary:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_rtdl_cuda_gate.sh
```

This gate is not the paper comparator. It is a cheap RTDL-side gate that proves
the CUDA diagnostic can consume the app-owned author-prepared aggregate arrays
and reproduce the Python author-contract force file.

Run the full POD gate sequence:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.sh
```

From Windows or another control machine, run the same full gate on a reachable
Linux POD and pull evidence back:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py \
  --host 157.157.221.29 \
  --port 22051
```

The remote runner uploads only the source needed for this app (`src/`, the
Barnes-Hut diagnostic script, and this paper-app directory) and excludes
generated `_work/`, `_runs/`, `_data/`, and cache directories. Its package-only
mode also verifies critical gate entry points such as the full POD gate,
environment preflight, author patcher, source audit, same-input comparison, and
performance-summary scripts.
Without a live POD, validate the upload package locally:

```bash
PYTHONPATH=src:. python Paper-reproduction-apps/rt-barneshut-paper/scripts/run_remote_full_pod_gate.py \
  --package-only
```

Audit whether the paper-reproduction evidence is complete:

```bash
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_phase_boundary_review_gate.sh --write-template
bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_completion_audit.sh
```

The completion audit is expected to remain incomplete until the POD correctness
gates and a matched performance phase-boundary review gate both close. The
`--write-template` command creates a draft review artifact after the
same-input performance summary is ready; a human reviewer must accept the phase
boundary before rerunning the gate and completion audit.

The full gate writes
`Paper-reproduction-apps/rt-barneshut-paper/_runs/full_pod_reproduction_gate/summary.json`.
It records pass/fail/skipped status for the local contract gate, pinned
author-source contract gate, environment preflight, RTDL CUDA author-contract
comparison, patched-author same-input comparison, and author-vs-RTDL same-input
comparison, plus a timing-summary gate when correctness has closed. It still
does not authorize a completed paper-reproduction claim until matched
performance phase boundaries are reviewed and accepted by
`run_phase_boundary_review_gate.sh`.

Current local probe results:

| Synthetic input | Result | Meaning |
| --- | --- | --- |
| 8 bodies | match, max abs error `4.44e-16` | One-bucket exact pairwise force law and output order are aligned. |
| 64 bodies, historical RTDL diagnostic tree | mismatch, max rel error about `6.77e-2` | Multi-bucket tree/traversal contracts differ. |
| 64 bodies, author-prepared aggregate arrays | match, max abs error `2.27e-13` | The author bucket-tree contract can be expressed through generic flattened aggregate arrays at the app layer and fed to the RTDL diagnostic route. |

The actual RTDL diagnostic script's prepared-array reader is covered by local
tests for the 64-body author-prepared case. The bounded same-input CUDA/POD
gate against the patched author binary has also passed. What remains outside
this bounded line is independent tree construction and full-paper completion.

## Evidence Needed For Completion

A completed paper-reproduction claim requires all of the following:

1. The author artifact builds from the pinned source plus documented patches.
2. The author route can produce or expose per-body force output or a stable
   output checksum for the same input used by RTDL.
3. RTDL runs the same input under a documented contract.
4. Numeric agreement and timing are reported under the same phase boundary.
5. Any remaining comparator patch is disclosed as author-derived,
   compatibility-only, or RTDL-defined.

The bounded same-input prepared-state line is closed. Until the full set of
completion gates above pass, this directory is still not a completed full-paper
reproduction result.
