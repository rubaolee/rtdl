# Paper Revision Brief For Gemini

Date: 2026-04-04

Target files:
- `/Users/rl2025/rtdl_python_only/paper/rtdl_rayjoin_2026/main.tex`
- `/Users/rl2025/rtdl_python_only/paper/rtdl_rayjoin_2026/main.pdf`
- `/Users/rl2025/rtdl_python_only/paper/rtdl_rayjoin_2026/references.bib`

Purpose:
- produce a professional IEEE/ACM-style paper revision plan and concrete prose
  revisions for the RTDL manuscript
- the current paper is technically honest, but still not strong enough in tone,
  presentation quality, and figure quality
- the next Gemini pass should act as a serious paper editor, not a generic code
  reviewer

## Current manuscript state

What is already improved:
- the abstract, introduction, and contributions have already been rewritten once
- repo/process jargon such as `accepted`, `bounded`, `analogue`,
  `paper-facing`, and `done-bounded` has been substantially reduced
- the design section now includes:
  - a representative RTDL kernel listing
  - an execution-pipeline subsection
- the acknowledgment section has been removed
- the manuscript builds successfully with `tectonic`

What is still weak:
- parts of the prose still read like a project-history summary rather than a
  polished systems paper
- the relationship-to-RayJoin framing is still somewhat administrative rather
  than sharply comparative
- the figures are currently poor:
  - they look like embedded dashboard screenshots rather than publication-grade
    paper figures
  - the layout is visually awkward
  - the panel composition is weak
  - labels and captions are not yet conference-paper quality
- some results/caption text is still more defensive than necessary
- bibliography quality should be checked for canonical citations and consistent
  style

## Hard boundaries that must remain true

These must not be violated during revision:
- do **not** claim a full paper-identical reproduction of RayJoin
- do **not** claim nationwide closure
- do **not** claim unavailable dataset families are complete
- do **not** claim full polygon overlay materialization
- overlay must remain described as RTDL's current seed-generation /
  overlay-seed evaluation surface
- Vulkan must remain outside the reported paper results
- PostGIS remains an external correctness reference on the validated real-data
  packages only
- the reported evidence must stay aligned with the actual validated packages:
  - County `⊲⊳` Zipcode `top4_tx_ca_ny_pa`
  - BlockGroup `⊲⊳` WaterBodies `county2300_s10`
  - bounded `LKAU ⊲⊳ PKAU` `sunshine_tiny`
  - `LKAU ⊲⊳ PKAU` overlay-seed evaluation

## What Gemini should do

Gemini should perform a full paper-editor pass with these concrete outputs:

1. Review the manuscript as a submission draft
- assess:
  - professionalism of prose
  - technical framing
  - section structure
  - results narration
  - RayJoin comparison quality
  - figure/table presentation quality
  - bibliography quality

2. Identify the weakest sections
- rank the weakest sections by severity
- explain why each weak section reads poorly for peer review

3. Provide concrete replacement prose
- give rewritten replacement prose, not just general advice, for:
  - abstract
  - first 2-4 paragraphs of the introduction
  - the contributions list/paragraph
  - the performance interpretation subsection
  - the `Relationship to RayJoin` section
  - the conclusion

4. Provide figure and table revision guidance
- focus especially on the current scalability figure page, which is visibly poor
- explain:
  - why the current figures are unprofessional
  - how to redesign them for a paper
  - whether the current two-wide side-by-side composite should be split,
    simplified, or redrawn
  - what typography, labeling, panel titles, legends, and caption style should
    change
- suggest better caption wording

5. Review bibliography quality
- note whether the reference list is missing more canonical citations
- note whether any entries read like ad hoc web/documentation references rather
  than paper-quality supporting citations
- recommend which references should stay and which should be improved if needed

## Specific paper issues Gemini should address

### 1. Professional tone

The paper should sound like:
- a careful systems paper
- a research tool paper with real experimental grounding

The paper should not sound like:
- a repository milestone summary
- an audit memo
- a lab notebook
- an internal project update

Gemini should specifically look for:
- overqualification
- repetitive disclaimers
- awkward wording about validation boundaries
- sections that explain process history instead of technical contribution

### 2. Introduction quality

The introduction should:
- clearly state the problem
- explain why non-graphical ray tracing needs a DSL/runtime abstraction
- explain why RayJoin is the right evaluation target
- establish the paper's thesis cleanly
- present contributions crisply

The introduction should not:
- spend too much time on repository state
- read like a justification memo
- front-load too many defensive limitations before the contribution is clear

### 3. Design section depth

Gemini should check whether the paper now explains enough of:
- language surface
- compiled representation
- lowering
- backend execution pipeline
- oracle role
- correctness model

If it is still too thin, Gemini should say exactly what technical explanation is
missing and propose added prose or subsections.

### 4. Results presentation

Gemini should check whether the results section:
- interprets the numbers like a paper
- compares systems cleanly
- explains the PostGIS-vs-RTDL performance relationship well
- avoids sounding defensive or overly apologetic

Particular issue:
- the paper must explain why PostGIS is much faster on indexed positive-hit PIP
  without sounding like a hand-waving excuse
- the explanation should stay technically precise:
  - indexed positive-hit DB query
  - RTDL full truth-row materialization contract
  - different end-to-end work

### 5. Relationship to RayJoin

This section should become a real comparative framing section, not a checklist.

Gemini should improve:
- the framing of what RTDL mirrors from RayJoin
- the framing of where RTDL intentionally diverges
- the language around substitutions/analogs so it sounds research-appropriate
- the narrative around why unavailable datasets are deferred

### 6. Figures

This is currently one of the worst visual problems.

The current issues include:
- the figures look like dashboard exports rather than publication figures
- side-by-side composites are too busy
- panel titles are visually awkward
- there is too much empty white space mixed with overly dense content
- the combined page looks unbalanced
- the figures do not visually match the rest of the manuscript style

Gemini should propose:
- whether Figure 13 and Figure 14 should remain combined or be separated
- whether each should have fewer subpanels
- whether the plots should be redrawn with simpler styling
- better caption wording
- better panel naming
- whether the axes/legends/titles should be simplified

Gemini does **not** need to generate images itself. But it should produce a
clear editorial plan for how the figures should be redone.

### 7. PDF / formatting review

Gemini should also review:
- caption lengths
- table readability
- page flow
- whether any sections look too dense or visually awkward
- whether the PDF still looks like a draft despite technically compiling

## Preferred output format from Gemini

Ask Gemini to produce:

1. Executive verdict
- Is the paper:
  - not ready
  - close but still needs work
  - or near submission quality

2. Ranked findings
- ordered by severity
- concise but concrete

3. Replacement prose
- explicit replacement text for the targeted sections

4. Figure revision plan
- specific, actionable, and paper-quality

5. Bibliography notes
- specific improvements only if needed

6. Final recommendation
- what should be changed next before treating the paper as submission-ready

## Notes for Gemini

Please optimize for:
- professionalism
- clarity
- peer-review readiness
- technical honesty
- stronger presentation

Please do **not** optimize for:
- making the claims larger than the evidence
- turning the paper into a marketing document
- hiding the limitations
- rewriting the paper into a different project than RTDL actually is
