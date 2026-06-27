# Front-Page Proposal for RTDL v0.4.0

Date: 2026-04-11
Author: Claude (review pass, Goal 255)
Status: proposal only — no edits made to README.md

---

## Diagnosis

The current `README.md` was largely written for the v0.2.0 release and has not
been coherently updated to reflect v0.4.0. The identity block at the top
correctly names `v0.4.0` as the repo state anchor and the nearest-neighbor
expansion, but the body of the page contradicts it at every turn. The concrete
problems fall into four clusters.

### 1. v0.4 workloads are absent from the body

`fixed_radius_neighbors` and `knn_rows` — the two new public workloads
introduced in v0.4 — appear nowhere in:

- "What RTDL Is" (spatial-query bullet list)
- "Why It Is Useful" (released workload surfaces list)
- "Start Fast" (the second command still runs `rtdl_segment_polygon_hitcount.py`)
- "See It Quickly" (primary front-door links)
- "Current Main Position" (workload surface bullet list)
- "Strongest Current Backend Story" (three-story block)

The release statement and the v0.4 support matrix are unambiguous: the live
released engineering line on `main` is the nearest-neighbor surface.
`docs/README.md` correctly says exactly this in its Live State Summary. The
front page does not.

### 2. "Current Main Position" describes v0.2.0, not v0.4.0

This section opens with "two important status layers: the archived v0.1 trust
anchor / the live released v0.2.0 state on main." It then lists the v0.2.0
workload surface as the current accepted surface and names v0.1 the trust
anchor. There is no mention of v0.4 in this section. A reader who reads only
this section will believe v0.2.0 is the current release.

The "Strongest Current Backend Story" has three stories: v0.1 trust-anchor,
v0.2 large-row, and Jaccard stress. There is no v0.4 nearest-neighbor story.

### 3. Navigation is duplicated and stale in two places

"Start Fast" and "Where To Start" are near-duplicates and both send readers to
the v0.2 user guide as a primary entry. Meanwhile the quick tutorial's Step 4
already uses `rtdl_fixed_radius_neighbors.py` as the spatial-query example —
making the tutorial more current than the page that links to it.

The v0.4 release statement identifies `rtdl_fixed_radius_neighbors.py` and
`rtdl_knn_rows.py` as the main public workload entry points. Neither appears
in "See It Quickly."

### 4. "What The Video Means" is oversized and defensive

This section runs roughly 300 words to explain that the visual demo is a proof
of capability, not a product pivot. That explanation was appropriate when the
v0.3 visual-demo layer was new. At v0.4 the project has moved on; the section
now reads as an extended apology. Its useful core — that RTDL can act as the
query core inside a larger Python application — is already covered in "What
RTDL Is" and "Why It Is Useful."

---

## Proposed Structure

The proposal preserves all existing content that is still correct and removes
nothing substantive. Changes are limited to: updating workload lists to v0.4,
adding v0.4 navigation links, collapsing the duplicate start-here section, and
retiring the extended video explanation.

```
# RTDL
[keep current one-paragraph tagline and use-case bullets]

Current checkout identity:
  [keep four-bullet block — it is accurate]
  [one wording change: lead the v0.4 bullet rather than listing it last]

## Before Your First Run
  [keep as-is; setup instructions are version-agnostic]

## See It Quickly
  [keep table/thumbnail layout]
  [add two v0.4 entry-point links alongside the existing six]
    - rtdl_fixed_radius_neighbors.py
    - rtdl_knn_rows.py

## What RTDL Is
  [keep conceptual framing — it is accurate]
  [add nearest-neighbor examples to the spatial-query bullet list]

## Why It Is Useful
  [keep framing]
  [update "current strongest released workload surfaces" to include
   fixed_radius_neighbors and knn_rows alongside the v0.2 families]

## Start Fast
  [replace the second shell command with rtdl_fixed_radius_neighbors.py,
   which is already the Step 4 command in the quick tutorial]
  [Windows equivalents: update to match]
  [add v0.4 application examples to the continuation link list]

## Current Workload Surface  [rename from "Current Main Position"]
  [rewrite the opening to name v0.4 as the live released state]
  [keep the layered reading: v0.2.0 core + v0.3.0 demo + v0.4 NN expansion]
  [list all six accepted surfaces from the v0.4 support matrix:
     segment_polygon_hitcount          accepted
     segment_polygon_anyhit_rows       accepted
     polygon_pair_overlap_area_rows    accepted, bounded
     polygon_set_jaccard               accepted, bounded
     fixed_radius_neighbors            accepted
     knn_rows                          accepted]
  [retain the "current main does not mean" honesty boundary list]

## Strongest Current Backend Story  [keep, add v0.4 story]
  [add a fourth story: v0.4 nearest-neighbor multi-backend closure across
   CPU/oracle, Embree, OptiX, and Vulkan, with Vulkan marked as bounded]
  [keep the v0.1 trust-anchor, v0.2 large-row, and Jaccard stories]

## Backend Roles
  [keep as-is]

## Current Limits
  [keep as-is]

## What The Video Means  [collapse to ~4 lines]
  [retain: "RTDL is still the query engine; Python handles the surrounding
   application pipeline; the demo demonstrates versatility, not a product pivot"]
  [retain the rtdl_lit_ball_demo.py link]
  [remove: three-variant demo comparison and internal-stability notes]

## Example Layout
  [keep as-is]

## Why RTDL Exists
  [keep the RayJoin paragraph and citation]
  [keep the research-direction sentence]
  [keep the six-paper bibliography — it is already self-contained and
   cross-links to docs/future_ray_tracing_directions.md]

## Release Reports
  [add v0.4 release package link alongside v0.2 and v0.1]

## Where To Start
  [keep, add v0.4 Application Examples entry]
  [move v0.2 user guide to step 3 so the quick tutorial is step 1]

## Project Status / Copyright
  [update status paragraph to name v0.4.0 as the current released state]
```

Total structural change: one section renamed, one section collapsed, workload
lists and navigation updated in five places. All other sections survive intact.

---

## Style Notes

1. **Keep the terse declarative voice.** The existing README has a disciplined
   style: short sentences, no marketing adjectives. The rewrite should not
   introduce "powerful," "seamless," or similar.

2. **Keep the honesty boundary list.** The "does not mean" block is one of the
   most useful things on the page. It should survive and expand if v0.4 adds
   new limits worth noting.

3. **Do not promote Vulkan past its boundary.** The support matrix marks Vulkan
   as "accepted, bounded" on the nearest-neighbor line. Any update must carry
   that qualifier forward.

4. **Preserve the checkout identity block.** It is accurate at v0.4.0 and is
   the clearest version-story summary on the page. The only change needed is to
   lead the listing with v0.4 rather than listing it last.

5. **Keep the PYTHONPATH/ModuleNotFoundError note.** It is specific, actionable,
   and prevents a common new-user failure.

6. **docs/README.md is already correct.** It correctly leads with v0.4.0 as the
   live released surface. README.md should match it, not contradict it.

---

## Risks

**Risk 1: Retiring "What The Video Means" detail causes reviewer confusion.**
That section may exist partly to satisfy a prior review pass that asked for
explicit framing of the demo layer. If auditors expect it, collapsing it could
raise a flag. Mitigation: collapse rather than delete — reduce to three or four
sentences, keep the `rtdl_lit_ball_demo.py` link and the one-sentence
product-direction clarification.

**Risk 2: Updating "Start Fast" to use a v0.4 example may confuse users who
arrived from v0.2-era links.** Mitigation: add a one-line note after the v0.4
command pointing to `docs/release_facing_examples.md` for the full v0.2
workload set.

**Risk 3: The v0.2 user guide is still the most complete user-facing reference
document.** Demoting it in "Where To Start" might leave new users without a
natural next step. Mitigation: keep it in the list at step 3 (after Quick
Tutorial) rather than removing it.

**Risk 4: Renaming "Current Main Position" breaks any external links or
internal cross-references.** Mitigation: check for anchor links in
`docs/README.md` and other docs before renaming.

---

## Recommendation

The front page has a clear, bounded problem: the body was not updated when v0.4
was released. The fix does not require a structural redesign. Five targeted
edits cover the main gap:

1. Update the workload lists in "What RTDL Is," "Why It Is Useful," "Current
   Main Position," and "Strongest Current Backend Story" to include
   `fixed_radius_neighbors` and `knn_rows`.

2. Replace the second "Start Fast" command with `rtdl_fixed_radius_neighbors.py`
   (already the Step 4 command in the quick tutorial).

3. Add v0.4 entry-point links to "See It Quickly."

4. Rename "Current Main Position" to "Current Workload Surface" and rewrite
   its opening two sentences to name v0.4 as the live released state.

5. Collapse "What The Video Means" to three or four sentences.

Items 1–4 are low-risk factual corrections. Item 5 is the only judgment call
and can be deferred if prior review context requires the section to survive in
longer form.

Do not attempt a full structural rewrite. The page's voice, density, and
honesty-boundary discipline are assets; they should be preserved.
