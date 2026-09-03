# Goal5839 preregistration internal hostile self-review

Date: 2026-09-03

Verdict:
`ACCEPT_PREREGISTRATION_FOR_GIT_FREEZE__NOT_A_CENSUS_RESULT__EXTERNAL_GATE_OPEN`

This is an internal Codex review. It is not independent review, external AI
review, multi-AI consensus, or paper authorization.

## 1. Scope reviewed

- `scripts/goal5839_build_real_artifact_census_preregistration.py`
- `tests/goal5839_real_artifact_census_preregistration_test.py`
- `GOAL5839_PREREGISTRATION.json`
- `PREREGISTRATION.md`
- the exact survey source archive reacquired from the frozen arXiv source URL
- the Goal5838 frozen-core verifier and all 91 Goal5838 tests

The review occurred before any Goal5839 candidate repository clone, candidate
source inspection, protocol-property classification, adjudication, upstream
notification, GPU execution or timing.

## 2. Blocking findings repaired before freeze

### R1: one canonical artifact per work could permit selection bias

The first draft retained every work but classified only one canonical official
artifact when a work had multiple distinct releases. That was weaker than the
roadmap's preferred all-artifact denominator. The final protocol inventories
and classifies every distinct eligible official artifact and every explicit
paper-evaluated OptiX route. Fixed precedence now collapses only duplicate or
byte-identical mirrors, never distinct artifacts, and observed labels cannot
influence selection.

### R2: copied legacy-generator logic was not the legacy generator

The first implementation manually reproduced Goal5753's old builder to show
that the missing old JSON cannot be recreated byte-identically. That left an
avoidable common-implementation challenge. The final implementation directly
calls `goal5753_build_held_out_universe.build` on temporary files containing
the exact reacquired `prob.csv` and `sample.bib` bytes. The resulting current
generator output is 42,754 bytes at
`fb90228614107a82d028d3ecc85a97d624f8d80d8f6fd650acb4ae5fe5858697`,
which differs from the historical 43,892-byte
`fb89d1da0e9b7bc18ce3333eb11a5920ffdef9f23ba227f4ecbf96e898234b05`
identity. The old JSON is therefore explicitly excluded as a Goal5839 source
authority.

## 3. Remaining nonblocking risks

### P2-1: finite discovery is not an Internet-completeness theorem

Paper links, publisher supplements, GitHub search and general-web search can
miss an artifact, and result ranking can change. The protocol freezes query
order and result caps and requires preservation of returned identities. The
claim is complete only for the 29-work denominator under that procedure. It
must not be rewritten as “all released RT code.”

### P2-2: corpus blindness is impossible

The project has previously used several denominator works, and the historical
survey registry conservatively treated all 186 bibliography entries as prior
exposure. Goal5839 is a preregistered complete-denominator census, not an
unseen-corpus test. Prior exposure must remain adjacent to any result.

### P2-3: external independence is currently unavailable

One internal extraction can be performed, but no cell is paper-ready until it
has a second independent extraction or external adjudication. The project
author cannot resolve ambiguity favorably. This is an open execution gate, not
a reason to weaken the labels.

### P2-4: public Git is itself disclosure

A named `VIOLATED` row committed to this public repository would disclose the
finding. The protocol therefore forbids commit or push before independent
adjudication, private upstream notice, a repair offer and a 14-day response
window unless maintainers consent earlier. Potential violations must remain in
a private local packet until that gate is satisfied.

### P3-1: the exact survey archive is not stored in Git

The 752,766-byte archive was successfully reacquired and matched the frozen
SHA-256 exactly. The authority embeds all 29 works and 35 problem rows, and its
verifier can rederive them when the archive is supplied. Future source-URL
availability remains a custody risk; it does not change the frozen embedded
denominator.

### P3-2: some properties may be semantically inapplicable

The four-label contract deliberately has no reviewer-convenient
`NOT_APPLICABLE`. Such a cell remains `UNRESOLVED_WITH_REASON` until independent
adjudication. This may increase unresolved counts, but it avoids silently
dropping difficult cells or inflating enforcement.

## 4. Verification evidence

- Authority seal:
  `767fb5e8601268aea8c505babec0fcbf25d6c9407b54cb9801c5271c8015df0c`
- Authority file SHA-256:
  `995dbbf1e23cb561a97472a83e240a1c29d7972899bf586e8748f7b8a0ba26f3`
- Goal5839 preregistration tests: 8/8 pass.
- Stored authority verification without the source archive: pass.
- Byte-identical full rebuild with the exact source archive: pass.
- Goal5838 regression tests: 91/91 pass.
- Goal5838 frozen-core seal verification: pass.
- Frozen-core source modifications: zero.
- `git diff --check`: pass.

## 5. Claim ceiling at this checkpoint

The accepted result is only this: before Goal5839 source inspection, RTDL froze
a complete 29-work denominator, all-distinct-official-artifact discovery rule,
five property definitions, four labels, evidence schema, independent review
gate and responsible-disclosure gate against exact survey-source bytes.

It does not establish that any real artifact enforces, omits or violates a
property. It adds no field prevalence, defect, application, performance,
external-review or consensus claim.
