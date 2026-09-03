# Goal5839 real-artifact protocol-property census preregistration

Date frozen: 2026-09-03T06:56:46Z

Status: `FROZEN_PROTOCOL__CENSUS_EXTRACTION_NOT_STARTED__NO_FIELD_RESULT`

Machine authority: `GOAL5839_PREREGISTRATION.json`

## 1. Research question

The CGO reviewer attack is that RTDL's five executed failures are constructed
by the project authors and therefore do not show that whole-protocol mistakes
matter in released RT-repurposing code. Goal5839 asks a narrower empirical
question:

> Across the exact RT-repurposing works in one pinned survey projection, what
> fraction of inspectable author artifacts machine-enforce each of RTDL's five
> protocol properties, appear manually consistent without that enforcement,
> contain an adjudicated concrete violation, or cannot be resolved from the
> available evidence?

The experiment does not require a positive defect count. Zero violations is a
valid result. Absence of a check is not a bug.

## 2. Frozen denominator

The source is the exact arXiv source archive for *Ray Tracing Cores for
General-Purpose Computing: A Literature Review*:

- archive: 752,766 bytes, SHA-256
  `bfe852a1425b01b63ee0298f75646c824e9daf67429184211d446ba7f3643857`;
- `sample.bib`: SHA-256
  `9e394f5712478c5b84f8dd88b80490e009a033dffd1e17773f24aadb0c2eb26a`;
- `prob.csv`: SHA-256
  `88749ea23e465c972afb9c6efa1553bc1a4e0a25b6faa5f00c1c5b9c27979e95`.

The complete work denominator is all 29 unique cited works represented by the
35 exact rows in `prob.csv`; those rows contain 32 distinct problem labels.
Every work remains in the final table. A work with no eligible public author
artifact is not removed: it receives an explicit availability outcome and five
`UNRESOLVED_WITH_REASON` cells.

The old Goal5753 JSON is not the source authority for this experiment. Its
reported identity is 43,892 bytes at
`fb89d1da0e9b7bc18ce3333eb11a5920ffdef9f23ba227f4ecbf96e898234b05`,
but that file is unavailable in the current repository and the current
generator does not reproduce it byte-identically from the exact survey
archive. Goal5839 therefore binds the original archive and embeds its complete
29-work/35-row projection. It does not claim that the old JSON was recovered.

This corpus is not blind. The project has previously read or used some of these
works, and an older 186-entry survey-bibliography exposure registry treated all
of its rows as prior exposure. The freeze prevents outcome-dependent shrinking
or replacement; it does not create an unseen-corpus claim.

## 3. Artifact discovery and canonical selection

For each work, discovery follows one fixed order:

1. Inspect exact bibliography DOI/URL fields and the canonical paper page.
2. Inspect the paper and publisher supplement for author-declared code links.
3. Preserve the first 50 GitHub repository-search results for the exact title.
4. Preserve the first 20 general-web results for the quoted title plus
   `source code`.
5. Read candidate README, citation and license metadata only to establish the
   author/paper relation before protocol classification.

An eligible artifact is public source explicitly linked by the paper or
publisher, or maintained by a paper author/institution with metadata that
identifies the paper, and it must contain a buildable or statically inspectable
implementation of the paper's NVIDIA OptiX route.
CUDA-only baselines, unrelated renderers, third-party ports, duplicate mirrors,
paper pseudocode and binary-only releases are excluded.

For duplicate releases or byte-identical mirrors, precedence is paper-named
exact revision, publisher archive, first paper-listed repository, then
author/institution repository. A tie at one level is resolved by
lexicographically smallest normalized URL, never by an observed
classification. Use a paper-declared revision when exact; otherwise pin the
observed default-branch HEAD, tree, submodules and acquisition time. Inventory
and classify every distinct eligible official artifact; precedence only
collapses duplicates. Within each artifact, classify every explicitly named
paper-evaluated OptiX route, or the documented default route if none is named.
Ambiguous route selection fails to `UNRESOLVED_WITH_REASON`.

Completeness means complete for these 29 works under this finite procedure. It
does not mean every source release ever placed on the Internet was found.

## 4. Five properties

`CP001_ROLE_EFFECT_CLOSURE` asks whether the artifact machine-checks allowed
callback-role effects and required cross-role effect topology.

`CP002_SEMANTIC_ABI_OWNERSHIP` asks whether nominal payload, attribute, SBT and
result meanings and their producer/consumer ownership are checked, rather than
only machine types.

`CP003_PHYSICAL_BINDING` asks whether callback assumptions are checked against
geometry kind, GAS/SBT association, buffer layout, field mapping, output,
reducer and target bindings.

`CP004_STATUS_GATED_CONTINUATION_AND_COMPLETENESS` asks whether failure,
overflow, truncation and incompleteness prevent output exposure or continuation
until status is accepted.

`CP005_EXECUTABLE_IDENTITY_CHAIN` asks whether the intended protocol and
physical plan are bound to the exact generated source/PTX, native/provider
objects, target and launched executable. This is custody, not correctness.

## 5. The only labels

- `ENFORCED`: a relevant machine check compares independently sourced facts
  and rejects the incompatible route before launch or result consumption.
- `UNCHECKED_BUT_APPARENTLY_CONSISTENT`: no complete check was found, but the
  exact route's inspected producers, consumers, bindings and continuation
  appear mutually consistent. This is neither proof nor a defect.
- `VIOLATED`: exact source establishes a concrete reachable mismatch in the
  canonical route. Public naming still requires independent adjudication and
  responsible disclosure.
- `UNRESOLVED_WITH_REASON`: exact evidence is missing, ambiguous, unavailable,
  or depends on an unreproducible generated artifact. The reason must come from
  the machine authority's frozen taxonomy.

There is no fifth `NOT_APPLICABLE` label. A genuinely inapplicable property
requires independent adjudication and is reported as
`UNRESOLVED_WITH_REASON`. Ambiguity always fails to unresolved. Matching types,
a successful build, or a correct sample output cannot be upgraded to
`ENFORCED`.

## 6. Extraction, independence and disclosure

Each extraction must bind repository URL, revision, tree, submodules, license,
source inventory, canonical route, extractor and timestamp. Every property row
must cite exact files and lines or symbols and record producer, consumer,
enforcement or gap, and unresolved reason. Callback roles, channel meanings,
physical bindings, status/continuation and executable construction are
mandatory route-level inventories.

A paper claim requires two independent extractions or one extraction plus an
external adjudication for every reported cell. Repeating extraction in the same
Codex session is not independent. The project author cannot resolve ambiguity
in RTDL's favor. While external review is unavailable, this goal may produce a
first internal extraction but cannot produce a paper-ready census claim.

Before a concrete violation is named publicly, an independent reviewer must
adjudicate it, upstream maintainers must receive private notice and a proposed
repair, and they receive at least 14 days to respond unless they consent to
earlier disclosure. A named potential violation must not be committed or
pushed before that gate.

## 7. Reporting and claim boundary

The final report must show all 29 works and every distinct eligible official
artifact and selected route, including unavailable sources, all unresolved
rows, disagreements and a zero-violation result if that is what the evidence
shows. It reports work, artifact and route denominators plus all property cells
by label with explicit numerators and denominators. The five correlated
properties are not five independent defect observations.

At this freeze there has been no Goal5839 artifact search, candidate-source
inspection, classification, adjudication, notification, GPU use or timing. The
authority establishes only a preregistered protocol. It establishes no field
prevalence, real-code violation, absence of enforcement, performance result,
paper-ready table, external review or consensus.

## 8. Verification

From the repository root:

```bash
PYTHONPATH=src:. python3 scripts/goal5839_build_real_artifact_census_preregistration.py --verify-stored
```

When the exact survey archive is available, add
`--survey-archive /path/to/exact/archive` to rederive every denominator row and
require byte-identical authority output.
