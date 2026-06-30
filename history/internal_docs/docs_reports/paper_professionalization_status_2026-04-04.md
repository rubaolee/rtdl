# Paper Professionalization Status

Date: 2026-04-04

Status:
- final local manuscript revision completed
- publish decision still separate from external review/push
- Gemini paper audit completed
- second rewrite pass completed locally
- manual Codex revision pass completed after the Gemini revision report review
- figure redesign pass completed locally
- another external review pass still desirable before publication-quality acceptance
- Gemini 3.1 Pro rerun blocked by quota
- Gemini Flash rerun started but had not returned a final verdict at the time of
  this status snapshot

Problem statement:
- the current `paper/rtdl_rayjoin_2026` package is technically honest, but the
  manuscript tone is still too close to an internal audit memo
- the prose overuses qualifiers such as `accepted`, `bounded`, `analogue`, and
  `explicitly`
- several sections read as project-status narrative rather than as a polished
  systems paper for external review

Current Codex assessment:
- format/build state is solid
- claim boundaries are honest
- professionalism and presentation quality have improved materially
- results/methods language is closer to a systems-paper voice
- the worst presentation problem was the figure set, and that problem is now
  materially reduced after regenerating the scalability and overlay figures
- the RTDL design section is stronger after adding a clearer explanation of the
  lowered representation and runtime-adapter boundary
- the manuscript now reads like a complete paper rather than a polished audit
  report
- one more review pass is still desirable before treating the paper as ready to
  publish

Rewrite progress now completed locally:
- abstract rewritten toward a systems-paper voice
- introduction rewritten around the system problem and contribution
- contributions reframed to emphasize RTDL itself, not only reproduction limits
- `How RTDL Mirrors the RayJoin Paper` renamed to `Relationship to RayJoin`
- methodology naming improved:
  - `Evidence Policy` renamed to `Experimental Scope`
- RTDL design section strengthened with:
  - a representative kernel listing
  - a clearer execution-pipeline explanation
- acknowledgment section removed from the submission draft
- major repository/process wording reduced across:
  - methodology
  - results
  - RayJoin comparison
  - limitations
  - conclusion
- the main manuscript no longer matches the earlier repo-jargon sweep for:
  - `accepted`
  - `bounded`
  - `analogue`
  - `paper-facing`
  - `done-bounded`
- title tightened to keep the paper focused on non-graphical spatial workloads
  without over-broadening the claim surface
- abstract and introduction reframed around the programmability problem,
  backend portability, and RayJoin-oriented evaluation
- methodology/results wording tightened to sound less like repository history
  and more like a systems paper
- the performance interpretation and RayJoin comparison sections were rewritten
  to be sharper and less checklist-like
- the small LKAU table overflow was reduced with tighter table spacing
- the Figure 13 / Figure 14 generators were redesigned from 2x2 dashboard-style
  composites into paper-oriented two-panel figures with overlaid uniform and
  gaussian series
- the Figure 15 generator was redesigned into a cleaner paper bar chart
- a new RTDL execution-architecture figure was added to the design section
- the paper figure PNG assets were regenerated from the checked-in experiment
  payloads and the manuscript PDF was rebuilt successfully
- the compiled-representation / lowering section now explains more clearly what
  semantic information survives lowering and how runtime adapters consume it
- the overlay-seed contract presentation was cleaned up from inline prose into a
  proper list
- the exact four-system parity statement was rewritten as normal paper prose
- manuscript still compiles with `tectonic`

Remaining major work:
1. run another review on the revised manuscript
2. tighten any remaining awkward results/caption prose
3. improve bibliography quality where source papers are available
4. optional final venue-specific pass if the target conference requires
   anonymization or layout tweaks

Highest-priority rewrite targets:
1. remaining caption polish
2. RTDL design section depth
3. bibliography quality
4. optional architecture figure

Gemini review summary:
- blocking:
  - manuscript still reads too much like an internal status/audit report
  - repository-process terminology is too visible in the prose
  - design section is too thin for a systems paper
  - acknowledgment section should be removed from the submission draft
- non-blocking:
  - captions repeat too many reproduction disclaimers
  - bibliography should lean more on canonical paper citations where possible
  - `Evidence Policy` should be renamed to a more standard methodology label

Latest manual paper-design update:
- Figures 13 and 14 are no longer dashboard composites pasted into the paper.
  Each is now a readable two-panel figure designed for the manuscript page.
- Figure 15 also received a layout cleanup so the bar chart reads like a paper
  result rather than a report screenshot.
- The paper now includes a compact RTDL execution-architecture figure so the
  authored-kernel to backend-validation flow is visible without reconstructing
  it from prose alone.
- The manuscript PDF rebuild after the figure refresh succeeded. Remaining TeX
  warnings are underfull-box warnings, not figure overflow failures.
- A subsequent paper-structure pass also improved the design/methodology
  sections so the manuscript reads less like a results-first artifact report.

Important boundaries that must remain intact during revision:
- no paper-identical reproduction claim
- no nationwide closure claim
- overlay must remain labeled as a seed-generation evaluation rather than full
  polygon materialization
- Vulkan must remain outside the reported paper results
