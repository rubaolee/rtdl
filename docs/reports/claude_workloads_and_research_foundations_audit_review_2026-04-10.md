# Review: workloads_and_research_foundations.md
**Reviewer:** Claude (Sonnet 4.6)
**Date:** 2026-04-10
**File reviewed:** `docs/workloads_and_research_foundations.md`

---

## Verdict

**Approved with minor notes.**

The page is accurate, honest, and well-structured for public consumption. It
correctly separates implementation status from research motivation, names its
limitations explicitly, and does not overstate any claim. No blocking issues were
found. Several small improvements would sharpen clarity for a reader unfamiliar
with the project.

---

## Findings

### Strengths

**1. Correct use of status tiers.**
The three-tier distinction — released, active preview, additional implemented — is
the right model for a project at this stage. It prevents readers from treating all
workloads as equally available while still documenting what exists.

**2. Honest self-description of research coupling.**
The `polygon_pair_overlap_area_rows` / `polygon_set_jaccard` section acknowledges
that these workloads are "research-adjacent" rather than direct paper reproduction
targets. This is accurate and avoids inflating the scientific basis of that line.

**3. Citations are complete and properly attributed.**
All five papers carry full author lists, venue names, year, and DOI. The one
exception (X-HD, ICS 2026) correctly explains that the DOI is not yet public —
this is an honest handling of a forthcoming paper rather than a fabricated link.

**4. The "Broader System Papers" section adds real context.**
RTScan, LibRTS, and RayDB are not one-to-one workload justifications, and the page
says so. Listing them with an explicit "why they matter" paragraph shows readers
the research ecosystem without overclaiming workload derivation.

**5. "Honest Summary" section is an asset.**
Few public documentation pages name their own weak spots. Flagging the Jaccard
line's weaker paper coupling and warning against "arbitrary feature accumulation"
reads as trustworthy and is appropriate for a research-backed project.

### Issues and Suggestions

**F1. The "Reading Rule" preamble is inside-facing prose.**
The "Reading Rule" section explains conventions as if coaching the reader through
the page. For a public-facing document, either remove it and let section headers
carry the structure, or rewrite it as one or two sentences rather than a
multi-bullet explanation. The current form makes the page feel like internal
tooling documentation rather than a public reference.

**F2. "Active v0.4 preview workload surface" label could confuse release readers.**
A reader arriving from a package index may not know what "v0.4 preview" means
relative to the released `v0.2.0`. A single clarifying sentence — that v0.4 is an
unreleased development branch, not a minor-release series between v0.2 and some
future v1.0 — would prevent misreading.

**F3. The "Additional implemented workload families" section uses imprecise language.**
Five workload names are listed under "exist in the repo... but they are not all
part of the current released headline surface." The phrase "not all" implies a
subset is released, but none of the five (`lsi`, `pip`, `overlay`,
`ray_tri_hitcount`, `point_nearest_segment`) appear in the released v0.2.0 list.
If none are released, say "none of these are part of the released surface" to
remove false ambiguity.

**F4. `ray_tri_hitcount` has no research mapping.**
The other four workloads in the same section (`lsi`, `pip`, `overlay`,
`point_nearest_segment`) are covered by the RayJoin paper mapping. Nothing
connects `ray_tri_hitcount` to any paper or design rationale. For a page that
argues the project is "intentional and research-backed," this is a visible gap.
Either add a one-line note (e.g., "ray_tri_hitcount is a low-level primitive, not
tied to a named paper target") or drop it from the list if it is purely internal.

**F5. X-HD DOI phrasing reads as a broken field.**
> DOI: not listed in the current public materials yet

A reader scanning citations will not know whether the paper is forthcoming,
preprint-only, or simply missing data. Preferred phrasing: "DOI: forthcoming" or
"DOI: not yet available (ICS 2026 proceedings)." The surrounding text is otherwise
correct.

**F6. No explicit definition of what "public workload" means.**
The page distinguishes released, preview, and additional workloads but never
defines what it means for a workload to be "public" (i.e., stable API, documented,
tested end-to-end). A single definitional sentence at the top of the "Current
Supported Workloads" section would make the tier structure unambiguous.

---

## Residual Risks

| Risk | Severity | Notes |
|------|----------|-------|
| X-HD DOI placeholder phrasing | Low–Medium | Reads as a broken field in any rendered DOI link checker. Easy fix. |
| `ray_tri_hitcount` unmapped | Low | Leaves a visible gap in the "research-backed" narrative. Worth a one-liner. |
| "Active v0.4 preview" becomes stale on release | Low | Routine update required; not a current error. |
| Jaccard line labeled only "research-adjacent" without rationale | Low | Accurate framing, but reads thin without any supporting context for the label. |
| No last-updated timestamp on document body | Low | File name includes a date in the artifact naming convention, but the document itself carries no "Last updated" field; section content will drift without a visible staleness signal. |

---

## Summary

The document succeeds at its stated purpose: making the project's workload surface
look intentional and research-backed rather than ad hoc. Citation quality is high,
status tiering is correct, and the self-critical tone in the Honest Summary section
is a genuine asset for a research project page. The main improvements needed are:
(1) converting the "Reading Rule" section into less inside-facing prose; (2)
tightening the "not all" language in the Additional Workloads section; (3) mapping
or annotating `ray_tri_hitcount`; and (4) adding a last-updated marker. None of
these are blocking. The page is ready for public exposure as-is, with the above
treated as tracked follow-on items.
