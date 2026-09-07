# Manuscript Change Map for P-Sextuple-Prime (DSL-First)

Date: 2026-09-07 America/New_York.

Status: `DSL_FIRST_REPURPOSED_RT_REWRITE_COMPLETE_AUTHOR_SCOPE__EXACT_CANDIDATE_COMMIT_BINDING_AND_TWO_INDEPENDENT_REVIEWS_PENDING`.

The immediate baseline is P-quintuple-prime at commit
`41bbec66c6f9f8f770d18075fb9dacbed16d499d`, tree
`135f2bc214927acdb305cf2edd2c5ef98690b4a2`, PDF SHA-256
`34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385`.
Its control commit is `8dfdc810c9c23f259b20c511caf69d250f2b86ce`.

P-sextuple-prime replaces those manuscript bytes with a DSL-first paper. It
retains all earlier result-route, trust, receipt, adverse-performance, and
artifact corrections. Exact candidate commit and tree are recorded only after
the immutable candidate commit exists. No review of an earlier candidate
transfers to these bytes.

No production source, native code, experiment, test, workload, timer,
estimator, threshold, measured evidence, or F2 artifact changed. No GPU ran and
no unchanged test suite was rerun.

## 1. Controlling directives

| Directive | SHA-256 | Applied boundary |
| --- | --- | --- |
| `history/internal_docs/lead_dsl_first_submission_directive_20260907.md` | `ddbf047144a1e8641428f84a3588cf50f0171b0babfb0691399994e7efd68edf` | Make the restricted-Python DSL/compiler the paper's main subject; whole-protocol is one contribution, not the title-level subject. |
| `history/internal_docs/lead_repurposed_rt_problem_statement_and_evidence_20260907.md` | `ca85675a7321c138603e858794e02aa6fe75b8f8b446a572908a620ea838c3e6` | State a bounded result-obligation compiler problem, credit prior solutions, add application evidence, and forbid first/only/impossibility claims. |

Both directives authorize manuscript, bibliography, evidence-recovery, and
control work only. They do not authorize implementation or new experiments.

## 2. DSL-first manuscript restructuring

| Map ID | P-quintuple-prime weakness | P-sextuple-prime action | Evidence boundary | PDF pages |
| --- | --- | --- | --- | ---: |
| `DSL-01` | Title and opening centered on a contract audit rather than the language. | Retitles the paper `RTDL: A Restricted-Python DSL for Repurposed RT`; rewrites the abstract and introduction around the language/compiler problem. | Positioning change only; no new implementation or performance claim. | 1--2 |
| `DSL-02` | The paper did not show a concrete user program early. | Adds an abridged, typed all-hit count program derived from the real supported standard-library source, with explicit omissions and a non-standalone caption. | Exact supported source family; no claim of arbitrary Python. | 2 |
| `DSL-03` | Author and compiler responsibilities were diffuse. | Separates author-owned callback source, records, manifest, geometry mapping, predicates, and oracle from compiler-owned parsing, IR, ABI, wrapper/PTX, binding, status, and lifecycle. | Descriptive boundary of current V4 implementation. | 2, 6--7, 9--11 |
| `DSL-04` | Contributions were organized as seams rather than language/compiler artifacts. | States four contributions: programming model, typed IR and admission, code generation/runtime, and application/evaluation evidence. | Fixed-family implementation; no soundness or usability claim. | 1--2 |
| `DSL-05` | Language subset and target path were scattered. | Adds a representation table, role-indexed effects, fail-closed judgments, and a source-to-prepared-execution pipeline. | Explanatory judgments summarize implemented checks; they are not a mechanized theorem. | 2--6 |
| `DSL-06` | General leaves and measured specializations could be conflated. | Gives code generation its own section and distinguishes Numba leaf ABI, trusted topology wrappers, exact-IR specializations, and the non-executable canonical plan. | Measured rows remain bound to exact specialized paths. | 5--7, 9 |

## 3. Repurposed-RT problem and prior solutions

The paper now asks: for an author-selected geometric mapping, how can a
restricted language represent bounded computation while making selected result
obligations constrain callbacks, data interpretation, traversal actions, and
result return?

| Map ID | Action | Attribution and claim ceiling | PDF pages |
| --- | --- | --- | ---: |
| `PRT-01` | Adds an obligation table for RTNN, RayJoin, and RayDB. | Their range/nearest maintenance, continue-after-hit, identity, deduplication, and aggregation techniques are prior solutions, not RTDL inventions. | 1, 3 |
| `PRT-02` | Makes LibRTS the closest application-facing abstraction. | RTDL claims neither API superiority nor inability of LibRTS to add checks. | 7, 9--10 |
| `PRT-03` | Adds CrossRT, Luisa, Dr.Jit, Scion, TTA/TTA+, OptiX, OSL, Slang, Shader Components, PyOptiX, and OWL comparisons. | Cross-host/device generation, pipeline automation, specialization, BVH language design, event control, and rendering-domain contracts are all credited as prior capability. | 1, 9--10, 12 |
| `PRT-04` | Narrows the increment to the implemented connection from selected fixed-family result obligations to effect admission, trusted target-action generation, executable identity, and interface-specific failure checks. | No first, only, exhaustive, superiority, or impossibility claim; source silence remains `UNKNOWN`. | 1--6, 10--11 |

The Scion bibliography entry uses its final PLDI 2026 title, `Decoupling Data
Layouts from Bounding Volume Hierarchies`, Article 175, 39 pages, DOI
`10.1145/3808253`. TTA/TTA+ is cited as MICRO 2024, DOI
`10.1109/MICRO61859.2024.00080`.

## 4. Historical application evidence recovery

The new application evidence matrix is
`novelty/DSL_FIRST_APPLICATION_EVIDENCE_MATRIX_20260907.md`. It records exactly
what survives and prevents the paper from treating absent application sources
as current runnable examples.

| Evidence class | Applications | Safe use | Mandatory limit |
| --- | --- | --- | --- |
| `E1` | Particle tracking, triangle counting, LibRTS | Exact historical application-source hash and callback-consumer binding remain recoverable from retained recount scripts. | The actual historical application files are absent from the current checkout and submission artifact. |
| `E2` | RayDB, X-HD, RTNN, RT-DBSCAN, Spatial RayJoin, RT-BarnesHut | Frozen source-audit records retain path, mapping, and structural responsibility information. | Individual source bytes are absent; rows are not current runnable examples. |

The manuscript table names all nine project-authored mappings, the
application-owned semantics, reused RTDL/shared responsibilities, and the
evidence caveat. It discloses RayDB as the sole private-loader exception,
attributes every application algorithm to its original paper, and does not
claim that every application stage ran on RT cores.

## 5. Evidence denominators remain separate

| Evidence set | Exact denominator retained in P-sextuple-prime | Forbidden interpretation |
| --- | --- | --- |
| Historical portfolio | Nine mappings and thirteen selected paper lanes | Not nine external users, current runnable examples, or unseen-app generalization. |
| Historical V2/V4 authority | 464 exact behaviorally true-OptiX workers; 34 rows; 16 pass, 18 fail; 11 clear V4 wins, 10 clear losses, 13 uncertain | Not PyOptiX, not final M, not a broad performance win, and not pooled with final M. Raw archive is absent and was not rerun. |
| Final measured M | Two exact specialized tasks on RTX 4090 Ada and RTX 3090 Ampere; 160 cells and 20,480 steady samples | Not all nine apps, arbitrary callbacks, generic Numba-leaf execution, or intrinsic language overhead. |
| Sealed composition | One author-defined selected sphere composition, two launches, 12/12 oracle rows | Not an unbiased unseen-app exam or topology-generic synthesis. |
| Finite target checker | Five property classes applied 20 times with 15 unique mutations | Not control-flow, numerical, or refinement soundness. |

## 6. Inherited corrections retained

P-sextuple-prime preserves all earlier corrections, including:

- concrete reject/generate/select decisions for the bounded relation, all-hit
  count, and exact-IR specialization;
- explicit separation of general Numba leaves from measured trusted
  specializations;
- exact app-free warm/load may precede route admission;
- materialized-program receipts versus the measured AOT fast result;
- provider double-fault and native-fork limitations;
- proof-carrying code, typed linking/FFI, Slang/Shader Components, and formal
  GPU verification as stronger or adjacent precedents; and
- source hashes establishing identity rather than semantics.

## 7. Mandatory disclosures in the final text

| Disclosure | PDF location |
| --- | ---: |
| Prepared public RTDL/Direct medians are `1.077--1.175x`, not a speedup claim | 1, 9, 11 |
| All post-import RTDL/strong-PyOptiX medians are adverse; worst block `2.377x` | 1, 9--11 |
| Entry was revised after an adverse result; first-result endpoints remain confounded | 9, 11 |
| M versus E first-result regression is post hoc and non-gating | 9--10 |
| 4,096 timed A calls have only 32 separate diagnostic receipts | 6, 11 |
| Paired instrumentation qualification covers A only | 9, 11 |
| Selected sphere route required about 2,635 topology-specific lines and 28 compiler lines | 5, 8, 11 |
| Finite checker missed an out-of-authority early-return probe | 8, 11 |
| Zero independent-user sessions or authoring-time measures | 7, 9, 11 |
| Six historical app sources and the old raw archive are absent | 6--8, 11 |
| Artifact is offline evidence recount, not product install or GPU rerun | 10--11 |

## 8. Exact pre-commit candidate bytes and author QA

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `paper/cgo2027/main.tex` | 60,755 | `a339ace8ec2f071cd85c2416e9f67b5d76ae533d43a41a96dbfa2f6647be7de0` |
| `paper/cgo2027/references.bib` | 21,953 | `bb0b71ae0fec49492888fbc9252ed412897cb2d4d7f1e33008f902cdb3b74e61` |
| Both candidate PDF paths | 182,617 each | `a1772fc41809deb91f64466fc0cccb9557023c143d99d361b4f3b9aa38ad36f0` |
| Normalized source bundle | 29,176 | `a49ea4aedc2b96084eefddf2ee987e20e968b59416c678caa30c5ab0c4606afa` |
| Unchanged F2 artifact | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

Author-side checks passed: cached Tectonic build; 12 US-Letter pages; main
content ends on page 11; zero horizontal or vertical overfull boxes; zero
undefined citations/references; 12/12 fonts embedded, subset, and Unicode
mapped; both PDF paths byte-identical; two independently generated normalized
source archives byte-identical; source hashes preserved after extraction to a
foreign path containing spaces; foreign-path compilation exited zero; all 12
pages rendered and visually inspected; and no tested private path, username,
host, key, internal Goal ID, or agent name appeared in extracted PDF text.

These are author-side checks, not an independent acceptance. BibTeX emits
nonfatal completeness warnings for several inherited conference records and
the in-press survey; all cited entries render and no citation is unresolved.

## 9. Authorization state

The claim ledger now contains 28 entries and zero authorized flags. The four
new entries cover the restricted-Python DSL surface, historical application
evidence, complete mixed historical performance counts, and the bounded
repurposed-RT problem statement. P-sextuple-prime begins at 0/2 independent
acceptances. No prior vote transfers, no authenticated submission form has
been checked, no upload has occurred, and no submission receipt exists.
