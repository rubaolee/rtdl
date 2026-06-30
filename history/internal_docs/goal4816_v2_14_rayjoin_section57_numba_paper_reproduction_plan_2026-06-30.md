# Goal4816 — v2.14 RayJoin Section 5.7 Numba Paper Reproduction Plan

Date: 2026-06-30

Status: preparation-only goal document. This document does not start the
implementation, does not authorize POD runs, does not authorize runtime edits,
and does not authorize any new public reproduction or performance claim.

## Goal Number Decision

Use **Goal4816**.

Reason: the archived V4/RayJoin exploration already used Goal4807 through
Goal4815 for a released-V4 API-map/user-app sequence. This new work is a
separate v2.14 paper-reproduction line, so reusing Goal4807 would create an
audit collision. Goal4816 is the next non-conflicting goal number.

## Objective

Build the first strict paper-reproduction goal for **RayJoin Section 5.7 Polygon
Overlay** using:

- RTDL **v2.14** as the current released system baseline.
- **Numba** as the explicit partner for user/application continuation code.
- Existing RTDL v2.14 primitives and prepared routes only.
- The RayJoin authors' original paper and source program as the correctness and
protocol authority.

The intended end state of the later implementation is not "RTDL beats RayJoin"
by wording. The intended end state is:

1. reproduce the Section 5.7 workload as exactly as the available inputs allow;
2. compare RTDL v2.14 + Numba + existing primitives against the author
   C++/CUDA/OptiX implementation under a clearly documented same-input
   contract;
3. state honestly whether the result is full paper reproduction, bounded
   available-input reproduction, or blocked by input/semantic/runtime gaps.

## Non-Negotiable Boundaries

- Do not modify `src/rtdsl/**` or `src/native/**` to make this reproduction pass.
- Do not modify the v2.14 release surface.
- Do not add a RayJoin-specific RTDL runtime primitive.
- Do not count scalar LSI/PIP rows as full polygon-overlay reproduction.
- Do not claim full Section 5.7 reproduction from the current known 2/8
  exact-ready subset.
- Do not publish author-hot-compute parity unless timing phases are comparable
  and the comparison excludes incompatible process-wall work.
- If v2.14 lacks a necessary generic primitive or exposed row contract, record a
  product/capability gap instead of patching the runtime inside this goal.

## Required Reading Before Coding

Goal4816 implementation must begin by reading and recording notes from:

1. **Paper**: `C:\Users\Lestat\Downloads\ics24 (1).pdf`
   - Required sections: Section 3.2 for the ray/RT execution contract and
     Section 5.7 for Polygon Overlay workload details, datasets, parameters,
     metrics, and Table/Figure references.
2. **Author original program/source**
   - Existing artifact paths show the old pod ran
     `/workspace/RayJoin_fresh/release/bin/polyover_exec`.
   - The implementation must locate the corresponding author source tree,
     record its repository/commit if available, and inspect the code paths for:
     `polyover_exec`, `run_overlay`, LSI, PIP/point location,
     `LocateVerticesInOtherMap`, CDB parsing, Simulation of Simplicity
     tie-breaking, output-chain generation, and timing output.
3. **Existing RTDL v2.14 evidence**
   - `history/internal_docs/docs_reports/goal4380_v2_14_pod_benchmark_execution_2026-06-14.md`
   - `history/internal_docs/docs_reports/goal4380_v2_14_benchmark_runs_2026-06-14/rayjoin_section57_overlay/section57_overlay_summary.md`
   - `history/release_reports/v2_14_internal_closeout_2026-06-30/rayjoin_author_vs_rtdl_caveat.md`
   - `history/release_reports/v2_14_internal_closeout_2026-06-30/public_rt_vs_embree_comparison.md`

No implementation step is valid until these reading notes exist.

## What Goal4380 Already Proved

Goal4380 did real work and must not be repeated blindly.

Known results:

| Item | Goal4380 status |
| --- | --- |
| Non-overlay RayJoin LSI | Prepared segment-pair scalar count; OptiX 29.93x faster than Embree in the Goal4380 matrix. This is scalar-count evidence, not full paper reproduction. |
| Non-overlay RayJoin PIP | Prepared PIP scalar count; OptiX 1.10x faster than Embree. This is modest scalar-count evidence, not full overlay reproduction. |
| Section 5.7 overlay coverage | 2/8 exact-ready pairs completed; 6/8 skipped because exact preprocessed CDB inputs were missing from the pod artifact set. |
| County x Zipcode | Local author RT process wall 5.521s; RTDL OptiX 5.782s; RTDL Embree 15.121s; count match true. |
| Block x Water | Local author RT process wall 27.944s; RTDL OptiX 28.650s; RTDL Embree 53.793s; count match true. |
| Allowed v2.14 interpretation | RTDL OptiX is near local author process wall and faster than RTDL Embree on the two exact-ready Section 5.7 rows. |
| Blocked interpretation | Full 8/8 Section 5.7 reproduction; RTDL hot compute matches the authors' specialized C++/CUDA/OptiX hot path. |

Therefore Goal4816 starts from "2/8 available-input reproduction evidence
exists", not from zero.

## Existing v2.14 Primitives And Code To Reuse

The implementation must first map and reuse existing v2.14 assets:

- LSI/segment-pair intersection prepared primitive:
  `src/rtdsl/rayjoin_overlay.py::_run_lsi_rows`.
- Directed segment point-location / PIP prepared primitive:
  `src/rtdsl/rayjoin_overlay.py::_run_point_location_faces` and
  `src/rtdsl/rayjoin_overlay.py::_PreparedPointLocationRunner`.
- Current v2.14 RayJoin benchmark front door:
  `examples/current/research_benchmarks/spatial_rayjoin/rtdl_rayjoin_v2_spatial_join_app.py`.
- Numba compact-mask continuation plan:
  `describe_rayjoin_v2_6_numba_compact_mask_continuation`.
- Numba segmented compact-mask preview:
  `run_rayjoin_v2_6_numba_compact_mask_preview` /
  `run_rayjoin_segmented_compact_mask_numba_preview`.
- Numba side-aware topology continuation:
  `run_rayjoin_v2_9_numba_side_aware_topology_reference`.
- Generic Numba owner-face/side filter:
  `src/rtdsl/closed_shape_topology.py::filter_closed_shape_membership_candidate_columns_by_owner_face_side_numba`.

The key design rule is: application logic may live in the paper-reproduction app,
and Numba may implement the application continuation, but RTDL runtime/native
code must stay unchanged.

## Author-Reply / Determinism Principle To Carry Forward

The user-provided determinism summary at
`C:\Users\Lestat\Downloads\rayjoin_pip_determinism_summary.md` must be treated as
a first-class uncertainty note.

Principle:

- Repeated RT-mode runs on County x Zipcode showed stable LSI and stable map1 PIP
  counts, but map0 PIP positives varied.
- The observed differences were exterior/non-exterior flips; when both runs
  classified a point as non-exterior, face ids agreed.
- Sampled differing points had competing selected edges with the same scaled
  vertical intersection height (`xsect_y`).
- The likely mechanism is OptiX traversal/pruning order among equal-height
  boundary candidates, bypassing the intended SoS tie-breaker if equal `t`
  candidates are pruned before the shader can compare them.
- A deterministic reproduction must discover and follow the author-code SoS
  contract or explicitly record that the exact tie-break rule remains unresolved.

Goal4816 must not "fix" this by silently inventing a new RTDL policy. The policy
must come from the paper, the author source, or an explicit author clarification.

## Planned Work After This Preparation Document

### Goal4816-A — Paper And Source Contract Extraction

Purpose: define the exact Section 5.7 reproduction contract before coding.

Work:

- Read paper Section 3.2 and Section 5.7.
- Read author source for the `polyover_exec` execution path.
- Extract datasets, parameters, CLI flags, output semantics, timing semantics,
  and correctness criteria.
- Extract the SoS/tie-break behavior used by PIP/point location.

Exit evidence:

- Notes file with paper/source citations and exact reproduction contract.
- Author source location and commit/hash recorded.
- If author source cannot be obtained, stop with `blocked_by_author_source_gap`.

### Goal4816-B — Existing Work And Primitive Capability Map

Purpose: avoid repeating Goal4380 and avoid using hidden or wrong routes.

Work:

- Inventory Goal4380 artifacts and exact 2/8 completed rows.
- Inventory the current v2.14 RayJoin app, LSI primitive, PIP primitive, overlay
  helper route, and Numba continuation functions.
- Classify each required Section 5.7 phase as:
  `existing_v2_14_primitive`, `numba_partner_continuation`,
  `paper_app_logic`, `author_baseline_only`, `missing_input`, or
  `missing_v2_14_capability`.

Exit evidence:

- Capability map table.
- Explicit answer to whether the full 8/8 target is blocked by missing inputs,
  missing source/build, missing primitive exposure, or unresolved semantics.

### Goal4816-C — App-Only Reproduction Design

Purpose: design the implementation without changing RTDL.

Work:

- Define a paper-reproduction app path under examples or an internal
  reproduction workspace, using v2.14 imports only.
- Plan how LSI rows, PIP/face ids, midpoint/chain construction, owner-face/side
  logic, and output-chain assembly flow through existing RTDL primitives and
  Numba continuations.
- Mark any use of `rayjoin_overlay` bundled helpers honestly; if they are used,
  separate "RTDL shipped helper path" from "user-composed primitives path".

Exit evidence:

- A no-runtime-edit implementation design.
- A list of exact functions to call and exact places where Numba owns the
  continuation.

### Goal4816-D — Local Correctness Smoke Plan

Purpose: define the first cheap correctness check before POD.

Work:

- Select the smallest exact CDB pair available locally or on local Linux.
- Define byte-equality, topology-hash, and count-level checks.
- Require LSI/PIP/output-chain diagnostics, not just a final count.

Exit evidence:

- Smoke test command plan and expected artifact names.
- Stop condition if only count-level validation is possible.

### Goal4816-E — POD Performance And Full-Input Plan

Purpose: define the serious run only after correctness and source contract pass.

Work:

- Reuse the known author command shape:
  `polyover_exec -poly1 ... -poly2 ... -serialize=... -grid_size=15000 -mode=rt -v=1 -fau -xsect_factor 0.1 -enlarge=3.5 -check=false`.
- Compare author C++/CUDA/OptiX, RTDL v2.14 + OptiX primitives + Numba
  continuation, and any existing Goal4380 route under a same-input protocol.
- Report process wall and hot phases separately when available.
- Attempt all 8 pairs only if exact CDB inputs exist; otherwise preserve the
  2/8 available-input boundary.

Exit evidence:

- Per-pair artifact table with raw logs.
- Correctness table and performance table.
- Clear final label:
  `full_section57_reproduction`, `bounded_2_of_8_available_input_reproduction`,
  `blocked_by_missing_exact_inputs`, `blocked_by_author_source_gap`,
  `blocked_by_pip_tie_break_gap`, or `blocked_by_v2_14_capability_gap`.

## Acceptance Criteria

Goal4816 can only proceed to implementation after this preparation is approved.
The eventual implementation goal can only be considered successful if:

- Paper Section 3.2 and 5.7 requirements are explicitly recorded.
- Author source code path and commit/hash are recorded.
- The author program builds/runs or a clear source/build gap is recorded.
- v2.14 runtime/native code remains unchanged.
- Numba is used only as explicit partner continuation, not as a hidden runtime
  patch.
- Existing RTDL primitives are named and used directly.
- Correctness uses byte-equivalent output or topology-equivalent output with
  diagnostic evidence; count-only is not enough for full reproduction.
- Performance numbers include baseline, denominator, scale, hardware, protocol,
  and raw artifact paths.

## Goal-Level Decision Audit

1. **Am I being foolish?**
   Not if this remains a preparation gate. It would become foolish if I started
   coding or running POD before reading the paper/source and mapping Goal4380.

2. **What actions would make the decision foolish?**
   Reusing the old 2/8 result as "full reproduction", treating scalar LSI/PIP as
   overlay, changing RTDL runtime/native code, ignoring the PIP tie-break issue,
   or presenting process-wall near-parity as author-hot-compute parity.

3. **Is there another path that avoids being trapped in one bad idea?**
   Yes. If exact 8/8 input or author-source access is missing, close honestly as
   bounded available-input reproduction or a source/input gap. If a primitive is
   missing, close as a v2.14 capability gap instead of patching the runtime.

4. **Can I try a different path that actually solves the problem?**
   Yes. The correct path is paper/source first, then existing primitive map, then
   app-only v2.14 + Numba reproduction, then POD only after correctness is
   meaningful.

