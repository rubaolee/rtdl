# Manuscript Change Map for P-double-prime

Date: 2026-09-06 America/New_York.

Status: `N4_COMPLETE__FINAL_EIGHT_PAGE_RENDER_MAPPED`.

Baseline wording is P-prime at commit
`818c2ed284cde8acae9a09b531b8bfed3bf925ee`. Replacement wording is the
working P-double-prime source and remains unauthorized until the actual
P-double-prime bytes receive the required independent reviews.

## 1. Material claim changes

| Map ID | P-prime wording or proposition | P-double-prime wording or action | N1/N2/N3 evidence | File/location | Claim ID | Final PDF page |
| --- | --- | --- | --- | --- | --- | --- |
| `MCM-01` | "Existing Python interfaces ... do not establish" one admitted execution | Replaced with a source-bounded statement that existing systems provide strong checks, Python access, and construction; checked materials do not state the same joint condition | `RW-RT-01`--`RW-SC-08`; N3 Section 1 | `paper/cgo2027/main.tex:24-31` | `RELATED-WORK-EXACT-GUARANTEE-BOUNDARY-024` | 1 |
| `MCM-02` | Python users assemble largely conventional pieces; question centered on admitting an "entire" protocol | Explicitly concedes PyOptiX/SlangPy, OWL/Luisa, DXR PAQs, and Slang capabilities; asks about the relation spanning semantic fields, physical artifacts, continuation, and exact executable | N1 Sections 3-5; N3 Section 1 | `paper/cgo2027/main.tex:81-95` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022`, `RELATED-WORK-EXACT-GUARANTEE-BOUNDARY-024` | 1 |
| `MCM-03` | Four contributions could read as four independent innovations | Reorganized as one core systems contribution, one implementation method, and bounded validation evidence | N3 Sections 1 and 5 | `paper/cgo2027/main.tex:103-117` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022`, `METHOD-TYPED-EFFECT-TRUSTED-LOWERING-023` | 1--2 |
| `MCM-04` | Defective semantic-ABI route was "executed," reached launch, and returned `(100,0),(101,1)` | Marks those rows as an illustrative same-width semantic substitution; expressly says no retained defective-route execution exists | N2 Sections 2 and 7 | `paper/cgo2027/main.tex:153-163` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022` | 2 |
| `MCM-05` | Admission compares "authorities" and rejects disagreement before launch | States exact source: trusted relation schema -> compiled relation contract -> separately derived compiler projection; mutation rejects before native load; same compiler TCB and wrong coherent schema remain limitations | `PC-02_ATTRIBUTE_OWNER`; N2 Sections 3-5 | `paper/cgo2027/main.tex:165-174` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022` | 2 |
| `MCM-06` | Typed effects described without one concrete hardware-operation chain | Adds verified effect -> deterministic ABI/status tag -> Numba leaf -> trusted wrapper -> payload/ignore/terminate chain | N2 Section 6; N3 `CONTRIB-TYPED-EFFECT-LOWERING` | `paper/cgo2027/main.tex:260-268` | `METHOD-TYPED-EFFECT-TRUSTED-LOWERING-023` | 3 |
| `MCM-07` | Semantic target facts called generated route sources; identity phrasing could obscure limits | Names trusted family schema and compiled contract; states same-compiler derivation and that hash equality gives coherence, not semantics | N2 Sections 3, 4, 4.1 | `paper/cgo2027/main.tex:313-334` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022` | 4 |
| `MCM-08` | Three PyOptiX/OWL-style residuals described as complete wrong-output witnesses | Removes those runs as affirmative evidence because independently verifiable records are not distributed; retains 19 mutations and integrated pre-load rejection only | N2 Section 7; N1 evidence vocabulary | `paper/cgo2027/main.tex:459-472` | `RELATED-WORK-EXACT-GUARANTEE-BOUNDARY-024` | 4--5 |
| `MCM-09` | Decomposition described as reusable beyond implementation | Downgrades to a suggested design pattern and states that no other domain/backend was validated | N3 Section 2 | `paper/cgo2027/main.tex:611-617` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022` | 6 |
| `MCM-10` | Related work mainly said RTDL had a different focus | Replaced with guarantee-level comparison that concedes PAQs, capabilities, SBT/pipeline automation, Python RT, reflection, staging, and formal protocol/linking antecedents | N1 full audit; N3 Section 3 | `paper/cgo2027/main.tex:619-654` | `RELATED-WORK-EXACT-GUARANTEE-BOUNDARY-024` | 6 |
| `MCM-11` | Threats omitted the unexecuted witness, trusted semantic premise, and UNKNOWN literature cells | Adds all three limits and forbids first/only/impossibility inference | N1 Sections 2 and 7; N2 Sections 2 and 9 | `paper/cgo2027/main.tex:668-705` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022`, `RELATED-WORK-EXACT-GUARANTEE-BOUNDARY-024` | 7 |
| `MCM-12` | Conclusion emphasized complete protocol admission | Names protocol-carrying admitted executables and five seams, while adding no semantic inference, arbitrary lowering, novelty-by-absence, or soundness claim | N3 Sections 1, 5, 8 | `paper/cgo2027/main.tex:709-720` | `NOVELTY-PROTOCOL-ADMITTED-EXECUTABLE-022`, `METHOD-TYPED-EFFECT-TRUSTED-LOWERING-023` | 7 |

## 2. Bibliography changes

| Map ID | Action | Reason/evidence | File/location | Final PDF page |
| --- | --- | --- | --- | --- |
| `MCM-B01` | Added current Vulkan RT/SBT specification entry | Distinguish general shader interfaces from RT SBT rules | `paper/cgo2027/references.bib`, `khronosVulkanRT` | 8 |
| `MCM-B02` | Corrected Slang capabilities URL and added Shader Cursors | Current capabilities/reflection behavior cannot be inferred only from the 2018 paper | `paper/cgo2027/references.bib`, `slangCapabilities`, `slangShaderCursors` | 8 |
| `MCM-B03` | Added current SlangPy documentation entry | Current Python RT pipeline/hit-group/SBT/dispatch capability must be acknowledged | `paper/cgo2027/references.bib`, `slangPy` | 8 |
| `MCM-B04` | Added official LuisaCompute repository entry | Current Python frontend and runtime capabilities supplement the 2022 paper | `paper/cgo2027/references.bib`, `luisaCompute` | 8 |
| `MCM-B05` | Corrected CrossRT author name order | Match arXiv v1 primary metadata | `paper/cgo2027/references.bib`, `frolov2024crossrt` | 7 |

Dynamic official documentation is cited as documentation, not presented as a
peer-reviewed paper. The 2026 RT-core survey remains workload/mapping background
only and is not used as evidence that a programming abstraction is absent.

## 3. Mandatory disclosures preserved

| Required disclosure | Current source location | Status before N5 |
| --- | --- | --- |
| Original per-call detailed-receipt requirement was not met | `main.tex:371-375`, `main.tex:698-700`; PDF pp. 4, 7 | Preserved and rendered |
| 4,096 timed A executions versus 32 separate diagnostic receipts | `main.tex:371-373`; PDF p. 4 | Preserved and rendered |
| Prepared timer ends before worker oracle; first-result endpoint includes oracle | `main.tex:395-403`, `main.tex:525-528`; PDF pp. 5--6 | Preserved and rendered |
| All post-import A/C rows adverse; maximum block 2.377129x (rounded 2.377x in prose/table) | `main.tex:568-572`, Table 6; PDF pp. 6--7 | Preserved and rendered |
| M versus E first-result regressions, entry about 8-22%, post-import about 16-31%, post hoc/non-gating | `main.tex:570-572`, Table 6 caption; PDF pp. 6--7 | Preserved and rendered |
| Import/lifecycle confounding | `main.tex:527-529`, `main.tex:681-685`; PDF pp. 5, 7 | Preserved and rendered |
| Provider double-fault and native-fork limits | `main.tex:185-190`, `main.tex:686-688`; PDF pp. 2, 7 | Preserved and rendered |
| Zero independent human authoring/prevalence evidence | `main.tex:442`, `main.tex:693-695`; PDF pp. 4, 7 | Preserved and rendered |
| Goal5838 required about 2,635 topology-specific LOC and compiler changes | `main.tex:350-354`, `main.tex:698-700`; PDF pp. 4, 7 | Preserved and rendered |
| Goal5840 checker is finite/structural and missed an early-return probe | `main.tex:488-501`, `main.tex:698-700`; PDF pp. 5, 7 | Preserved and rendered |
| Artifact is offline recount, not product install or GPU rerun | `main.tex:654-666`, `main.tex:702-705`; PDF pp. 6--7 | Preserved and rendered |

All eight final-layout pages were rendered and inspected. Extracted PDF text was
searched for the mandatory counts, ratios, scope statements, and unresolved
limits. No disclosure above was removed to preserve a stronger positive sentence.

## 4. Authorization state

Claims 022-024 were added to `CLAIM_LEDGER.json` with
`claim_authorized=false`. All prior claim flags remain false. This map is not a
review acceptance. The page mapping above refers to the built P-double-prime
working bytes; N5 records their immutable hash and Git identity.
