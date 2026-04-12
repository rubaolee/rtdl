# RTDL v0.4.0 Published State: v0.5 Readiness Review

Date: 2026-04-11  
Reviewer: Claude (Sonnet 4.6)  
Scope: README.md, docs/README.md, docs/tutorials/README.md,
docs/tutorials/rendering_and_visual_demos.md,
docs/release_reports/v0_4/README.md,
docs/release_reports/v0_4/release_statement.md,
docs/release_reports/v0_4/support_matrix.md,
docs/reports/goal256_hidden_star_4k_artifact_integration_2026-04-11.md,
docs/reports/goal256_front_page_and_4k_integration_2ai_consensus_2026-04-11.md

---

## Verdict

**v0.4.0 is cleanly closed and the published surface is ready to serve as
the honest baseline for scoping v0.5.**

The front page, tutorial ladder, release statement, support matrix, and
4K demo integration are internally consistent and scope-honest. No
contradictions, over-claims, or dangling stubs were found in the reviewed
material. The package can be handed to a v0.5 planning conversation without
clean-up debt.

---

## Findings

### 1. Release layering is clear and cumulative

The three-layer story is stated consistently across every reviewed document:

- `v0.2.0`: stable segment/polygon/overlap workload core
- `v0.3.0`: released RTDL-plus-Python bounded application/demo proof
- `v0.4.0`: nearest-neighbor workload expansion (`fixed_radius_neighbors`, `knn_rows`)

Each layer is additive. No document contradicts the stack or blurs
layer boundaries.

### 2. Scope language is correct

The front page and docs/README.md both state:

> RTDL is not a general-purpose renderer or graphics engine.

The 4K demo is framed consistently as a bounded RTDL-plus-Python
application artifact, not a renderer claim. The 2-AI consensus report
(Goal 256) confirms this framing survived review from both Gemini and Claude.

The tutorial `rendering_and_visual_demos.md` follows the same discipline:
it names the exact RTDL/Python boundary in code and prose and does not
inflate the visual demo into a rendering product.

### 3. Workload surface is fully enumerated with honest status

The support matrix gives exact status (`accepted`, `accepted, bounded`,
`supporting baseline`) for every backend, platform, and workload. Nothing
is silently claimed. The honesty boundary in the release statement matches
what the matrix says.

Full accepted workload catalog as of `v0.4.0`:

- `segment_polygon_hitcount` (accepted)
- `segment_polygon_anyhit_rows` (accepted)
- `polygon_pair_overlap_area_rows` (accepted, bounded)
- `polygon_set_jaccard` (accepted, bounded)
- `fixed_radius_neighbors` (accepted)
- `knn_rows` (accepted)

### 4. Tutorial ladder is complete for the current surface

The five-step ladder covers all released surface:

| Step | Tutorial |
| --- | --- |
| 0 | Quick Tutorial (first-run) |
| 1 | Hello World |
| 2 | Sorting Demo |
| 3 | Segment and Polygon Workloads (v0.2.0 families) |
| 4 | Nearest-Neighbor Workloads (v0.4.0 families) |
| 5 | RTDL Plus Python Rendering (demo/app layer) |

No released workload is tutorial-orphaned. The three learning tracks
(language basics, workload tutorials, application demos) map cleanly to
the release layers.

### 5. 4K demo artifact is fully integrated and verified

Goal 256 integration covers:

- chunked MP4 driver (`render_hidden_star_chunked_video.py`)
- `crossed_dual_hidden` scene, dual-light shading, batched shadow rays
- explicit `imageio`/`imageio-ffmpeg` dependency declaration in
  `requirements.txt`
- unit test coverage: 11 tests, OK, 2 skipped
- direct smoke tests for both the demo script and the chunked video path
- public YouTube link (`https://youtu.be/d3yJB7AmCLM`) wired into every
  relevant entry point

### 6. Multi-backend execution is closed

Both `fixed_radius_neighbors` and `knn_rows` run across:

- Python reference (correctness/truth)
- native CPU/oracle
- Embree
- OptiX
- Vulkan (accepted, bounded — correctness-first, performance-bounded)

Heavy Linux benchmark evidence and an accelerated boundary fix are cited
in the release statement as part of the final closure evidence. The
whole-line audit (Gemini + Claude) cleared the package.

### 7. docs/README.md index is dense but navigable

The index lists 27+ items in a flat numbered list. It serves as a
comprehensive reference but is not structured for quick scanning by
someone new to the project. This is not a blocking issue for v0.5
planning, but is a usability signal worth carrying forward.

---

## Risks

### R1: Vulkan is bounded — no performance claim

Vulkan is accepted under a "correctness-first, performance-bounded"
contract. If v0.5 work touches the nearest-neighbor GPU line, any
Vulkan performance story will need to be re-evaluated explicitly.
This is not a defect in v0.4.0, but it is a constraint v0.5 inherits.

### R2: macOS and Windows are limited platforms

macOS is "local development/doc/focused-test platform — accepted,
bounded." Windows is "secondary validation host — accepted, bounded."
Linux is the only fully validated platform. Any v0.5 workload that
claims cross-platform closure will need to explicitly revisit macOS and
Windows validation bars.

### R3: v0.5 scope is not defined in any reviewed document

None of the reviewed documents define what v0.5 will contain. The front
page references `docs/future_ray_tracing_directions.md` and uses the phrase
"the language goal is broader than spatial workloads alone," but no
specific v0.5 candidate surface is committed. This is appropriate — v0.4.0
is not the right document for that — but it means **v0.5 planning starts
from a blank scope**. The risk is scope drift without an explicit
scoping conversation anchored to the v0.4.0 baseline.

### R4: docs/README.md flat index may not scale

At 27+ numbered items, the docs index is growing past easy cognitive
scanning. If v0.5 adds another release report set, tutorial, and goal
doc layer, the index will need structural work (sections, grouping by
audience) or it will become a liability for onboarding.

### R5: 4K render is Windows/Embree-only

The production 4K artifact was rendered on a Windows Embree host. The
chunked video driver is integrated and tested at small scale on Linux,
but the full-resolution render evidence is single-platform. This is
documented honestly in Goal 256, but it means the 4K demo is not yet
a multi-platform production artifact.

---

## Conclusion

The published v0.4.0 surface is clean, scope-honest, and audit-closed.
The tutorial ladder covers the full released surface. The 4K demo is
integrated and verified. The support matrix is accurate. No deferred
clean-up debt was found that would block a v0.5 planning conversation.

The main thing v0.5 planning needs to establish — which is absent by
design from these documents — is an explicit scope definition: what
workload family or language capability the next release line targets.
The inherited constraints to carry into that conversation are:

- Vulkan performance is bounded
- macOS and Windows are secondary platforms
- the docs index needs structural attention if the document count grows
- the 4K render pipeline exists but is currently single-platform production

Recommended first step for v0.5: open a scoping document that names the
target workload or language surface, states the platform closure bar,
and commits the audit approach before implementation begins.
