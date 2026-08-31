# CGO related-work taxonomy, OWL separation, and repurposed-RT landscape revision

Date: 2026-08-29 (America/New_York)

Status: local manuscript revision complete; **not sent for external review**.

## 1. Why this revision was necessary

The previous manuscript had the right mechanism but an insufficiently organized
novelty argument. It compared several systems one by one, which left three
reviewer questions too easy to ask:

1. Is RTDL merely another host binding or convenience wrapper after PyOptiX?
2. Is RTDL merely OWL plus an unspecified type checker?
3. Does the paper understand the wider RT programming and repurposed-application
   landscape, or only the nine applications implemented by its authors?

The revision therefore changes the unit of comparison from product names to
**programming responsibility**. It also turns the OWL distinction into an
information-boundary argument and makes the frozen repurposed-RT landscape
inspectable instead of referring only to selected examples.

## 2. Pre-revision binding

- Repository: `C:\Users\Lestat\Desktop\work\rtdl_v4_restricted_python_design`
- Resolved HEAD ref: `1af120d187228035db733ce690de3a3bf5b54ee5`; the commit
  object is unavailable locally, so ordinary `git status` is not a trustworthy
  change authority for this workspace. No Git repair was attempted.
- Pre-revision `paper/cgo2027/main.tex` SHA-256:
  `0056cc7e19c7ca3120b8a792132008ee0d3752d5c7ae8dc7174be714f8853c19`
- The pre-revision working PDF was 11 pages and 565,436 bytes.

The owner later explicitly directed that this pass prioritize content and not
the page limit. Accordingly, no scientific or related-work content was removed
to recover 11 pages.

## 3. What changed

### 3.1 A problem-scoped four-responsibility taxonomy

The Introduction and Related Work now organize relevant systems, for the
application-to-RT correspondence studied here, into at most four responsibilities:

1. **Interface systems** ask whether declared stages, interfaces, accesses,
   sequencing, and target capabilities are legal. Examples include OptiX typed
   payloads, DXR Payload Access Qualifiers, Vulkan shader interfaces, Slang
   capabilities, and OptiX Utility.
2. **Construction systems** assemble modules, acceleration structures,
   pipelines, SBTs, resources, and launches. Examples include PyOptiX, OWL,
   Shader Components, and Slang.
3. **Mapping systems** generate, specialize, or translate high-level
   computations for RT-capable backends. Examples include Dr.Jit,
   LuisaRender/LuisaCompute, and CrossRT.
4. **Proposed responsibility: protocol admission** asks whether the assembled
   executable is admissible against one declared application protocol before
   launch. RTDL implements this responsibility only for two closed OptiX
   families.

The manuscript explicitly says that systems may span classes and that this is a
problem-scoped responsibility taxonomy, not a claim that all RT software falls
into an exhaustive universal taxonomy. Repurposed applications are the workload
population to which the responsibilities apply, not a fifth kind of programming
system.

### 3.2 Coverage beyond the closest competitors

A coverage paragraph places additional families without creating more classes:

- HLSL/DXR and SPIR-V/Vulkan remain interface systems;
- OSL and MDL are renderer-domain interface/construction languages;
- Embree and HIP RT are traversal libraries in interface/construction;
- Taichi is a general mapping/generation substrate when used to emit accelerator
  code.

The paragraph makes no fault-survival claim for systems not executed by this
project. Its purpose is to demonstrate coverage of the landscape, not to create
weak opponents.

### 3.3 The OWL argument is now an information-boundary argument

The revised text gives OWL full credit for managed acceleration structures,
programs, pipelines, SBT construction, resources, and launch. It also credits
OWL variable names and types for documenting local intent and enforcing
host-record layout.

The separation is now stated more precisely:

- composition legality and executable bytes do not determine the intended
  nominal application meaning;
- fix one executable and one legal OWL object graph: the same pair can be
  correct when attribute zero means `primitive_index` and incorrect when the
  intended contract says `application_item_id`;
- a checker limited to composition facts cannot know which interpretation is
  required unless the application intent is separately stated or otherwise
  formalized;
- this is not a missing validation switch. Adding the missing fact changes the
  abstraction from object construction to whole-protocol admission;
- RTDL does not infer the correct intent. It requires an explicit authority and
  checks a bounded implementation against it.

The argument is deliberately independent of whether a future OWL API exposes
`OptixPayloadType`: native payload declarations strengthen access checking but
do not themselves provide nominal meaning, physical obligations, continuation
policy, or executable-selection authority.

The execution statement remains bounded to what Goal5800 actually established:
each preregistered invalid realization and its nearby legal control share the
same OWL composition skeleton and slot layout for that task; all build and
launch; RTDL rejects the corresponding declared mismatches before launch. The
text does **not** claim byte-identical valid/invalid executables or identical
object graphs.

Local evidence anchor:

- `history/internal_docs/goal5800_three_arm_responsibility_and_executable_residual_result_v6_20260824.json`
- SHA-256 `32b48e335e788320395fd8727c94f7b6636f11c3d95ea6f976e7a9608b3523c0`

### 3.4 The repurposed-RT landscape is now inspectable

The paper adds a landscape table derived from the frozen public survey-table
projection. It contains all:

- 35 paper--problem rows;
- 32 distinct problem labels; and
- 29 unique cited works.

The table uses four presentation themes only: data/indexing/graph analytics;
geometry/spatial predicates; physics/simulation; and visualization/
representation. It names the works and cites all 29.

This is intentionally **not** described as the complete 59-document
bibliometric corpus, as 35 unique papers, or as an enforcement census. The
exact local projection contains 29 unique citation keys, not 35. Twenty-two
missing BibTeX records were imported from the pinned survey bibliography, while
seven existing paper keys were reused.

Local evidence anchors:

- `history/internal_docs/goal5753_held_out_candidate_universe_20260811.json`
  at SHA-256
  `fb89d1da0e9b7bc18ce3333eb11a5920ffdef9f23ba227f4ecbf96e898234b05`;
- pinned `sample.bib` at SHA-256
  `9e394f5712478c5b84f8dd88b80490e009a033dffd1e17773f24aadb0c2eb26a`.

The accompanying prose draws only a responsibility conclusion: after an
algorithm-to-RT mapping is chosen, its relationship to callbacks, semantic
slots, host bindings, status handling, and the selected executable remains an
application responsibility unless an equivalent protocol layer is supplied.
The application still owns the mathematical adequacy of the mapping and its
semantic oracle.

### 3.5 Contribution and conclusion alignment

The contribution list and conclusion now identify RTDL's novelty as a bounded
**protocol-admission compilation unit**, distinct from interface checking,
construction, and mapping. The manuscript does not claim a new rendering
language, a mapping algorithm, a general protocol type theory, or arbitrary
Callback-IR-to-GPU execution.

## 4. Why this is stronger for CGO

The revised argument gives a reviewer a short, falsifiable answer to the core
novelty question:

> Existing systems validate interfaces, construct RT pipelines, or map
> computations to RT backends. RTDL proposes a fourth bounded responsibility:
> making the declared whole callback protocol the unit of pre-launch admission.

Against PyOptiX, the distinction is not syntax or Python convenience: PyOptiX
exposes the host API, whereas RTDL transfers selected cross-role protocol
responsibilities into a checked unit.

Against OWL, the distinction is not SBT convenience: OWL already solves that
well. The residual is application-semantic authority that cannot be recovered
from legal composition alone. OWL could add an equivalent abstraction, but that
would adopt the protocol-admission responsibility rather than reveal an
existing configuration switch.

Against mapping and JIT systems, RTDL begins after the traversal formulation is
chosen. It does not compete on automatic mapping, optimization,
differentiation, or cross-platform generation.

This framing avoids attacking systems for goals they never claimed, while
making RTDL's actual new unit of reasoning visible.

## 5. Stronger claims deliberately rejected

The revision does **not** say any of the following:

- “OWL cannot ever solve this problem.”
- “OWL exposes no semantic names or types.”
- “OptiX/DXR/Vulkan only check trivial structure.”
- “All or most of the 59 papers rely exclusively on manual checking.”
- “We audited nearly every repurposed-RT artifact.”
- “The four preliminary third-party artifacts enforce none of the properties.”
- “The 35 survey rows are 35 unique papers.”
- “RTDL proves the algorithm-to-RT mapping correct.”
- “RTDL is a sound general protocol type system.”
- “The residuals survive DXR, Vulkan, OptiX Utility, Embree, HIP RT, or other
  unexecuted systems.”

Goal5820's incomplete `NOT_FOUND/UNCERTAIN` artifact observations were therefore
not promoted into the manuscript. A complete, frozen-denominator enforcement
census remains necessary before claiming empirical prevalence of manual
protocol maintenance.

## 6. Files changed

- `paper/cgo2027/main.tex`
- `paper/cgo2027/references.bib`
- `paper/cgo2027/main.pdf`
- `paper/cgo2027/README.md`
- this report

No compiler, runtime, checker, application, experimental result, or evidence
archive was changed.

## 7. Build and visual verification

The manuscript was rebuilt in a clean directory with:

1. `pdflatex`;
2. `bibtex`;
3. `pdflatex`;
4. `pdflatex`.

Results:

- zero undefined citations;
- zero undefined cross-references;
- zero overfull horizontal boxes in the final build;
- one 4.052 pt vertical-page warning in bibliography pagination, visually
  inspected with no clipping or overlap;
- pages 8--13 rendered to PNG and inspected for the responsibility table, OWL
  argument, landscape table, conclusion, and bibliography;
- current content-first PDF: 13 letter-size pages, 597,024 bytes.

Final hashes:

- `paper/cgo2027/main.tex`:
  `6d870366f549dc862ad8edd71d8bff49ed22e47271a17bd51f8dcf3149d6b3a9`
- `paper/cgo2027/references.bib`:
  `78b40edfe825b5c99bcde53456566e8e5d00179a09399efabc41058bb6562314`
- `paper/cgo2027/main.pdf`:
  `747b6ed92b113bd0e52a287a7df621aa1d842f44515c3fb218c5d4fbc144d235`
- `paper/cgo2027/README.md`:
  `71e5e7a510387d8229c9b543b6f6662b278597540cddca66f226b3f03fdde2d1`

The imported survey BibTeX records preserve incomplete metadata present in the
pinned source, so BibTeX still emits missing-field warnings. This is a later
bibliography-quality task, not a content or citation-resolution failure.

## 8. Remaining work

1. **Page-budget pass, later:** the owner explicitly deferred page-limit work.
   The 13-page content-first version must eventually be compressed to the
   submission limit without deleting the novelty boundary or evidence ceilings.
2. **Bibliography metadata:** verify and complete the 22 imported records from
   primary publisher pages, preserving citation identity.
3. **Empirical prevalence:** if the paper is to claim that most published
   artifacts rely on manual protocol maintenance, perform a frozen-denominator
   census with `MECHANICALLY_ENFORCED`, `DOCUMENTED_ONLY`, `MANUAL`, and
   `UNOBSERVABLE` outcomes. Current prose correctly stops short of that claim.
4. **Final submission gate:** because manuscript bytes changed, any previous
   final-byte/anonymization gate is stale and must be rerun only when the owner
   decides the content is ready. No external review was initiated in this pass.
