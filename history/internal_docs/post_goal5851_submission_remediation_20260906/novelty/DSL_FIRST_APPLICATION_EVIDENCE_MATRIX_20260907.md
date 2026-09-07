# DSL-First V4 Application Evidence Matrix

Date: 2026-09-07 America/New_York.

Status: `AUTHOR_EVIDENCE_RECOVERY_COMPLETE__DSL_FIRST_MANUSCRIPT_INTEGRATED__FINAL_BYTES_AND_INDEPENDENT_REVIEW_PENDING`.

This record supports the DSL-first manuscript rewrite directed by
`lead_dsl_first_submission_directive_20260907.md` and
`lead_repurposed_rt_problem_statement_and_evidence_20260907.md`. It is an
author-side recovery record, not a new execution, an independent review, a
performance authorization, or a submission authorization.

## 1. Evidence roots and recovery boundary

The current checkout does not contain the nine historical
`Paper-reproduction-apps/.../v4_whole_app.py` files or the frozen 10.8 MB
execution-source archive. No application was rerun in this pass. The matrix
below is therefore recovered from the surviving source-index, responsibility,
and independent-recount scripts. These scripts are evidence about the earlier
frozen source and audits; they do not make the absent source files currently
runnable.

| Surviving source | Current SHA-256 | What it supports |
| --- | --- | --- |
| `scripts/goal5773_build_evidence.py` | `273cf68bb8cdce27193e77218404af3ca7b0d98a5ab9355b7667e58d3329e70c` | Exact nine-entry historical V4 source-path index |
| `scripts/goal5787_build_cgo_integration.py` | `4deac345052a79ff25cf439740395fc554e7bc3316662fa0a91c519b2eebb393` | Per-application algorithm/composition/responsibility inventory and the frozen 34-row performance classification |
| `scripts/goal5789_a2_independent_recount.py` | `3bc0b7df1b05ad6ea7d7d91c394b9f797c237f1da7a1dac931c2b7a2d6239050` | Exact callback authorities and recoverable exact consumer-source hashes for Particle, Triangle, and LibRTS |
| `scripts/goal5792_source_backed_responsibility_audit.py` | `2a50d597fd25370dcfb8d2b0acda7535c73884899bbfcb81f1e9927ecca0a376` | Frozen-archive AST audit design, app/shared responsibility split, 8/9 registered-loader result, and RayDB exception |

The scripts pin the historical execution-source archive as 10,836,249 bytes,
SHA-256
`75bd1ce4647de8a198110dbb9be12b3f9a04e8b7ca53946227ddbbc78ac3ba41`.
The file was not recovered and rehashed in this pass. The associated raw
evidence and evaluation identities are recorded as
`2b6d808f566886b74469bbe4cf32fc6d426d2a91858237a7e939883f9b89394a`
and
`af630fa74ff6b60d1917234b7998e703d8ee60cf91c47cf4ef49ccebf065846a`,
respectively; those files are also absent and were not reverified here.

## 2. Historical nine-application matrix

“Application-owned” means the project did not claim to infer or prove that
domain decision. “RTDL/shared” means the frozen audit attributed that
integration responsibility to a shared V4 compiler/runtime or trusted physical
partner. It does not mean every operation ran on RT cores or that all low-level
implementation code was generated from unrestricted user source.

| Historical V4 port and original work | Historical V4 source identity | Application mapping and application-owned responsibility | Reused V4/compiler/runtime responsibility | Evidence class and mandatory caveat |
| --- | --- | --- | --- | --- |
| Particle tracking~(Wang et al.) | `Paper-reproduction-apps/goal5753-held-out-particle-tracking/v4_whole_app.py`; exact source SHA-256 `e2d26dd9a67025066ca77d1c57f358c34a8e4446a679b32f772a228ee52712a4` | Tetrahedral closest-face transition; domain encoding, transition semantics, and I/O contract remain application-owned | Built-in-triangle GAS, restricted closest-hit state update, callback validation/lowering, prepared lifecycle, and receipt construction | Historical source-audited port plus exact consumer hash. RTDL did not invent the algorithm or hardware traversal primitive. |
| Triangle counting~(Xiao et al.) | `Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py`; exact source SHA-256 `8ab4f4ad6c5913483633b06e70035a26637bc2b2a0589ce470623504d86e6210` | Application selects RT-1A2 or RT-2A1 and owns graph orientation/layout and triangle-count semantics | Built-in-triangle traversal, restricted per-hit callback, capacity/status checks, segmented device reduction, and prepared lifecycle | Historical source-audited port plus exact consumer hash. The final M weighted all-hit task is not this complete graph algorithm. |
| RayDB~(Shi et al.) | `Paper-reproduction-apps/raydb-paper/v4_whole_app.py`; individual source hash not recoverable from current files | Partitioned triangle grouped-I64 aggregate; query relation, grouping keys, partition layout, and aggregate semantics remain application-owned | Bounded emission ABI, trusted traversal, overflow fail-close, grouped exact-I64 reduction, and receipt construction | Historical archive-indexed/source-audited mapping only in this checkout. It directly imported the private OptiX loader; runtime loading was not behind the registered V4 interface. |
| LibRTS~(Geng et al.) | `Paper-reproduction-apps/librts-paper/v4_whole_app.py`; exact source SHA-256 `2952d38b341525d5b529a4391949df5b1ab59cd463c752f4da4df0823e40b987` | AABB point/range containment; spatial predicate, column/schema binding, and count/collect semantics remain application-owned | Custom-AABB bounded relation, typed physical schema, capacity proof, trusted traversal, reduction, and receipt | Historical source-audited port plus exact consumer hash. LibRTS itself is a strong prior programming-abstraction baseline. |
| X-HD~(Geng et al.) | `Paper-reproduction-apps/x-hd-paper/v4_whole_app.py`; individual source hash not recoverable from current files | Directed exact max-of-nearest witness; Hausdorff semantics, schemas, and witness output remain application-owned | Exact-state checks, cell-MBR trusted traversal, deterministic tie breaking/reduction, and fail-closed continuation | Historical archive-indexed/source-audited mapping only in this checkout; no automatic choice among application algorithms. |
| RTNN~(Zhu) | `Paper-reproduction-apps/rtnn-paper/v4_whole_app.py`; individual source hash not recoverable from current files | Multiround distance-window top-k; metric/search contract, K, domain bounds, and result order remain application-owned | Round/refit lifecycle, bounded selection state/capacity checks, target lowering, and receipt | Historical archive-indexed/source-audited mapping only in this checkout; metric-specific traversal is a trusted physical family. |
| RT-DBSCAN~(Nagarajan and Kulkarni) | `Paper-reproduction-apps/rt-dbscan-paper/v4_whole_app.py`; individual source hash not recoverable from current files | Radius-graph and component partition; radius/min-points semantics, bounds, and cluster output remain application-owned | Bounded edge emission, grouped continuation, overflow/status contract, prepared refinement, and component partner composition | Historical archive-indexed/source-audited mapping only in this checkout. Not every clustering stage ran on RT cores. |
| Spatial RayJoin~(Geng et al.) | `Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py`; individual source hash not recoverable from current files | Six-batch planar overlay; schedule, predicates, and six output tables remain application-owned | Typed carrier/effect checks, capacity and signed-I64 checks, producer/reducer lifecycle, and physical receipts | Historical archive-indexed/source-audited mapping only in this checkout. It substantially reused reviewed trusted legacy physical partners. |
| RT-BarnesHut~(Nagarajan et al.) | `Paper-reproduction-apps/rt-barneshut-paper/v4_whole_app.py`; individual source hash not recoverable from current files | Aggregate-hierarchy inverse-square force; tree/body schema, acceptance rule, and force math remain application-owned | Hierarchy/GAS ABI, frontier safety checks, callback lowering, deterministic continuation, and prepared traversal | Historical archive-indexed/source-audited mapping only in this checkout. Tree construction and aggregate traversal remain trusted partners. |

All nine historical application sources were checked by the frozen audit for
absence of selected raw OptiX/CUDA/PTX assembly tokens. That structural check
supports a shift in integration responsibility, not developer-time savings,
raw-LOC productivity, full code generation, or elimination of trusted native
partners. The audit recorded registered-interface runtime loading for eight of
nine applications; RayDB is the sole private-loader exception.

## 3. Denominators that must remain separate

| Evidence set | Exact denominator and safe use | Forbidden merger or reading |
| --- | --- | --- |
| Historical V4 portfolio | Nine project-authored ports and thirteen selected paper lanes. Use for bounded mapping/composition diversity, with original algorithms attributed to their papers. | Not nine unseen authors, thirteen independent protocol topologies, current runnable examples, or a universal generalization rate. |
| Historical RTX 4000 Ada comparison | 464 exact/behaviorally true-OptiX workers and 34 V2-direct/V4 rows. The row-local median split was 16 pass / 18 fail; 95% CI classification was 11 clear V4 wins / 10 clear V4 losses / 13 uncertain. | Not a PyOptiX comparison, not final M, not broad performance superiority, and not reverified in this pass. |
| Final measured source M | Two exact tasks: a 4,096-object/4,096-query bounded relation and a 16,384-primitive/16,384-query weighted all-hit reduction, on RTX 4090 Ada and RTX 3090 Ampere. | Relation is not a full database app; weighted reduction is not the historical graph triangle-counting algorithm; two tasks do not measure all nine ports. |
| Sealed sphere composition | One selected composition, two launches, and 12/12 rational-oracle rows after an author-defined ten-row challenge. | Not a full application, an unbiased new-app exam, or topology-generic lowering. |
| Owner-grouped collision/CCD route | One bounded functional closed route with inherited exact OptiX observations. | Not a third stable constructor, a complete collision system, or a performance result. |
| Sui-derived edge crossing | Bounded semantic projection only. | Not an executed application front door or a completed reproduction of the paper. |

## 4. Manuscript use rules

1. The paper may describe the historical nine ports as project-authored,
   source-audited V4 mappings, while marking the current source-recovery level.
2. The application table must show what remains application-owned, not only
   what RTDL takes over.
3. The RayDB private-loader exception must appear in the RayDB row.
4. LibRTS must be treated as a strong prior abstraction, not only an
   application used by RTDL.
5. Historical mixed performance must either be omitted or reported with all
   pass/fail/uncertain counts above. It may not be summarized as a win.
6. Final M performance remains the only current primary latency result and
   must stay scoped to its two exact specialized routes.
7. No statement in this matrix authorizes a public claim, submission, GPU run,
   or modification of the immutable F2 artifact.
