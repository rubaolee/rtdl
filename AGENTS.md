# RTDL Codex Working Guide

## Critical deadline override: no development after 2026-09-08 00:00 ET

The CGO 2027 submission date is 2026-09-10. Production, compiler, native,
experiment-script, test, workload, arm, timer, estimator and threshold changes
must stop at 2026-09-08 00:00 America/New_York. After that point, only
manuscript/bibliography edits, claim narrowing, execution of already committed
tools, evidence preservation, artifact packaging/replay, external review and
submission checks are allowed. A defect found after freeze removes or narrows
the affected submission claim; it does not authorize code repair or rerunning a
changed experiment.

The controlling final-sprint sequence is
`history/internal_docs/cgo2027_final_sprint_goals_20260905.md`. Goal5849 is
complete at its recorded local gates; Goal5850's first RTX generation is now
complete under the successor protocol; Goal5851 is next. Both passing RTX
generations must use exact source commit `c4351f612...`. Goal5852 is the
irreversible code/evidence freeze.

## Critical current override: Goal5850 generation A complete (2026-09-06)

Goal5850 is internally complete at exactly
`PASS__GOAL5850_GENERATION_A_COMPLETE__GOAL5851_REQUIRED`. The exact source is
commit `c4351f6120d1d73d7c2b72ff4d61ad747061f836`, tree
`1faf8ca2a99e4c1011443942479e2edf7b297edb`. On one NVIDIA RTX 2000 Ada
Generation GPU (CC 8.9, UUID
`GPU-2fe387f0-ed74-e62c-0686-750461318361`), all 512 instrumentation workers and
all 80 formal workers completed with zero retry/discard. Both tasks passed all
frozen primary gates, and the controller authority and independent recount are
byte-identical.

The successful archive SHA-256 is
`f487f42580ac8cb81c202fe867b976ba7a267b9ca7ccffb980c626d775b112c8`;
the authority internal seal is
`fb681997646ffed254e19ee2a3a2180f2676f8dc6e9d79ae0356ddd50f1911d8`.
The complete result and retained failure chain are documented in
`history/internal_docs/goal5850_generation_a_final_report_20260906.md`.

This is one-generation internal evidence only. The old post-import diagnostic
remains adverse: `1.997967x` for triangle and `2.111030x` for relation. Public
or manuscript performance wording, external consensus and Goal5848 completion
remain unauthorized. Goal5851 must run the identical `c4351f612...` code on a
different RTX compute-capability generation and GPU UUID; a later documentation
commit is not an admissible substitute experiment source.

## Retained Goal5848 failure history through transaction 2 (2026-09-05--06)

The following section preserves the earlier failure-state rationale. The
Goal5850 generation-A completion override above is the current authority.

Goal5850's first complete transaction at `95f7d4fc...` retained every row and
failed the original post-import gate. Subsequent fresh-process diagnosis proved
that pinned PyOptix's required `import optix` creates the CUDA context before
that arm's timer, while lazy RTDL creates the context inside its timer. Do not
claim those endpoints represent equivalent lifecycle state, and do not move
RTDL initialization into import to manufacture a pass.

The pre-freeze successor is defined by
`history/internal_docs/goal5850_lifecycle_endpoint_repair_20260906.md`. Its
primary first-result endpoint starts before implementation-specific imports,
retains the same `1.20x` median and `1.35x` worst-block limits, and records an
exact import/gap/post-import decomposition. The original post-import ratio
remains a mandatory non-gating diagnostic. Prepared RTDL/Direct, regression,
competence, safety, custody, instrumentation and two-generation gates are not
weakened. A new clean commit, fresh preregistration and wholly fresh transaction
are required; no old or exploratory sample may be pooled.

The first lifecycle-corrected transaction at `70f85796...` retained all 80
formal cells and passed its transaction gates, but failed afterward while
building the single-generation authority. The authority incorrectly required
the native Direct OptiX receipt's runtime identity to equal the preregistered
Python version instead of its exact `none__native_direct_optix` sentinel. Its
failure archive SHA-256 is
`fde22b987fdaf9b3617e9371ebb391254fa856eb2495688006ca54acf60d99fc`.
It remains a failed transaction and may not be relabeled, pooled or reused.
The immediate successor was required to distinguish native Direct and Python
runtime identity fail closed, commit and push that repair, and execute wholly
fresh artifacts, preregistration, instrumentation, formal cells and authority.
That repair and later transaction state are controlled by the current override
above.

Goal5848 is defined in
`history/internal_docs/goal5848_strong_baseline_post_import_20260905/GOAL5848.md`.
Its original primary target was the Goal5847 post-import debt: RTDL took
637.846 ms versus 263.349 ms for pinned precompiled PyOptix (`2.504242x` paired
median). Transaction 1 proved that endpoint compared unequal CUDA lifecycle
states, so the lifecycle repair above made it a mandatory adverse diagnostic
and moved the primary endpoint before implementation-specific imports. Do not
cite the favorable complete-process result dominated by PyOptix/CuPy import
latency as an intrinsic language speedup.

The goal requires both the frozen 4,096-by-4,096 canonical relation and the
16,384-query checked-U64 triangle scalar, plus idiomatic PyOptix, equivalently
device-optimized PyOptix and Direct OptiX arms. The corrected hard gates include
implementation-entry RTDL/strong-PyOptix median `<=1.20x`, every block
`<=1.35x`, prepared public RTDL/Direct `<=1.20x`, same-machine
successor/predecessor regression
`<=1.05x`, compiler-free RTDL deploy, exact output/OptiX receipts, fail-closed
mutations, exact AOT cache reuse and independent replay on two RTX generations.

No validation-off path, weak host-continuation baseline, task-specific engine
logic, hidden timer movement, discarded adverse row or cross-machine raw-time
ratio is admissible. Formal timing requires a committed preregistration after
exploration and repair. At this retained checkpoint Goal5848 had no performance
result; the current single-generation result is controlled above and external
review remains a later claim gate.

## Critical current override: Goal5845 relation steady debt closed (2026-09-04)

Goal5845 is internally complete at exactly
`PASS__GOAL5845_RELATION_PUBLIC_STEADY_PERFORMANCE_DEBT_CLOSED__EXTERNAL_REVIEW_PENDING`.
At clean source commit `22c6a45020e3da6894fa108fe92d50fbd2c5aa27`,
one RTX 2000 Ada transaction retained 1,024 samples per arm in eight balanced
alternating-order blocks. The prepared public RTDL and pinned PyOptiX medians
were 366,340 ns and 3,486,126 ns. Median within-block RTDL/PyOptiX was
`0.1049444491x` (reciprocal `9.5288508222x`), and the worst block was
`0.1073019810x`. The median RTDL public/direct-native ratio was
`1.3291058851x`.

The repair is generic bounded-relation device compaction plus compact traversal
audit and exact immutable row transport; no app dispatch or app formula entered
the engine. Both arms returned the same 4,096 canonical rows, all registered
samples were retained, and every RTDL execution recorded two actual OptiX
launches. The controlling authority is
`history/internal_docs/goal5845_relation_public_parity_20260904/GOAL5845_INTERNAL_AUTHORITY.json`;
its internal seal is
`49827211b3b721fd7c893c15386c32b9fe701362258e7b168e64072807466e6a`.
Verify it with
`python3 scripts/goal5845_build_relation_public_parity_authority.py --verify-stored`.

This is exact-task prepared-steady internal evidence only. The PyOptiX arm
returns raw duplicate events and canonicalizes on the host, so the result is
not a best-possible PyOptiX lower bound or an intrinsic 9.53x language/API
claim. Cold RTDL setup remains materially slower and is the next performance
debt for low-reuse claims. External review, consensus, public/manuscript
wording, cross-hardware generalization, arbitrary-workload claims, and
cold-start parity remain unauthorized. Preserve Goal5843's adverse relation
transaction; no old samples were pooled into Goal5845.

Mechanism wording must be exact: RTDL device-deduplicates, transfers the
deduplicated packed rows, then performs final native-host `std::sort` and
`std::unique`. The pinned PyOptiX arm transfers raw duplicate events and uses
NumPy/Python object materialization plus Python `sorted(set(...))`. No retained
phase experiment causally allocates the exact-arm difference. The controlling
correction is
`history/internal_docs/goal5845_relation_public_parity_20260904/CAUSAL_WORDING_CORRECTION_20260905.md`;
do not rewrite the historical report.

## Critical current override: Goal5844 internal parity target met (2026-09-04)

Goal5844's first complete GPU transaction is immutable adverse evidence. At
source commit `5e1518afe24230be677484f8e437e0a0da6bb30d`, one RTX 2000 Ada run
retained 1,024 samples per arm and produced a median within-block
RTDL/PyOptiX ratio of `2.1713906352x`; the public-arm medians were 273,457 ns
and 129,368 ns. The summary SHA-256 is
`4d6548238849c49e7aa89dcb663f08febb2815d83da924dd3a083db5549a94d3`
and the downloaded archive SHA-256 is
`d4d57100f77c74b1f43187d7c82e290fa6071524aa8478b8369f0925a6e93814`.
Do not discard, pool with, or relabel this failed target transaction.

The measured cause was repeated public-envelope proof serialization and static
identity hashing, not the native v8 OptiX operation. The successor
defers only JSON transport expansion for an eagerly validated immutable compact
receipt, retains per-execution validation of all 19 native stamp words, caches
only immutable bundle/digest identities, and preserves the old strict path for
external providers, ordinary mappings, and non-scalar outputs.

The clean successor transaction at source commit
`ee0237963bcd838d652a059f15ecc0d3f56dfd09` passed on the same GPU UUID. It
retained 1,024 samples per arm in eight balanced alternating-order blocks. RTDL
and PyOptiX public medians were 132,534 ns and 131,744 ns; median within-block
RTDL/PyOptiX was `1.0456709697x`, and the worst block was `1.1543425588x`.
The RTDL-first and PyOptiX-first stratified medians were respectively
`1.0456709697x` and `1.0456883372x`. Direct native time remained stable at
82,592 ns versus 82,757 ns before. The successor summary seal is
`6229aeba61fa681cbcda37e0ca253f725269fe08c2dd5e85f91502e5ad0a3b03`;
the archive SHA-256 is
`4336526eb6084d18353812187b2bd6c57515a642d804313abbaa79b52b1b678d`.

This successor intentionally adds memoization to
`src/rtdsl/v4_generic_family_lifecycle.py` after the completed Goal5838
prospective exam. Goal5838's preselection seal and exact evidence commit remain
immutable historical authority, but current-tree byte-identity and its old
current-file replay test are no longer valid successor claims. This is a
generic lifecycle optimization, not a repair made during the prospective
exam and not application dispatch. Goal5843 also remains immutable. All
Goal5844 results are internal engineering evidence; no public/manuscript
performance claim, hardware-independent claim, external review, or consensus
is authorized. The controlling internal authority is
`history/internal_docs/goal5844_public_execution_parity_20260904/GOAL5844_INTERNAL_AUTHORITY.json`;
verify it with
`PYTHONPATH=src:. python scripts/goal5844_build_public_parity_authority.py --verify-stored`.

## Critical current override: Goal5843 fair post-R1 baseline internally complete (2026-09-04)

Goal5843 is internally technically complete at exactly
`PASS__GOAL5843_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`. The
controlling authority is
`history/internal_docs/goal5843_post_r1_fair_baseline_20260904/GOAL5843_FINAL_INTERNAL_AUTHORITY.json`.
Its internal authority seal is
`c40b9fe5d3ace2f58fe29a1a39363ce25373332f774f3c36ffa839ce650bdba8`.
Verify it with
`PYTHONPATH=src:. python scripts/goal5843_build_final_authority.py --verify-stored`.

The accepted v4 transaction uses formal source commit
`c2662603c4d24902361fbd70325832ee7d98a0a4` and one RTX A6000 Ampere GPU. It
retains all 108 composites and 216 subworker receipts; the Mac recount is
byte-identical to the pod recount. The primary triangle scalar steady median
is 0.436590 ms, 2.910x pinned PyOptiX and 4.689x Direct. The adverse relation
row path remains 12.774231 ms, 3.333x PyOptiX and 9.950x Direct. These are
current-path internal measurements, not parity, a hardware-independent result,
or an intrinsic language-overhead bound.

The prior v3 transaction remains terminal because its preregistered local
archive verifier compared safely normalized extraction modes to original
custody modes. Preserve its full archive, 7,020 timing samples, and explicit
no-pooling rule. v4 is a separately preregistered transaction with unchanged
experimental contracts and a repaired custody verifier; it is not a retry of
v3. The Goal5838 frozen core remains byte-identical.

At the exact Goal5843 source commit, the Goal5838 frozen core remained
byte-identical. The exact successor regression is 91/91. A broader adjacent-history run is
245/247 because two old Goal5840 repair-freezer tests try to rebuild an early
source manifest from later legitimate Goal5840 files; do not hide these two
historical current-tree replay errors or rewrite old evidence to make them
green. External review count is zero, so public/manuscript performance wording
and consensus remain forbidden. The next performance target is to instrument
and reduce remaining public steady dispatch/receipt overhead without weakening
public checks or app-neutral boundaries.

## Critical current override: Goal5842R1 implementation repair complete (2026-09-04)

Goal5842R1 is internally complete at exactly
`PASS__GOAL5842R1_INTERNAL_IMPLEMENTATION_REPAIR_COMPLETE__FRESH_FAIR_BASELINE_AND_EXTERNAL_REVIEW_PENDING`.
The controlling authority is
`history/internal_docs/goal5842r1_public_reuse_scalar_fastpath_20260903/GOAL5842R1_INTERNAL_AUTHORITY.json`;
its internal seal is
`7897058f51dedc3b6b5c652b5c3d69418610919557f9ee9a9c70214a5f184248`.
Verify it with
`PYTHONPATH=src:. python scripts/goal5842r1_build_internal_authority.py --verify-stored`.

At implementation commit `207e7afc4afd44ddef537f74d97c47ae323743b2`,
the public toolchain has an explicit validated formal-leaf cache, prepared
triangle owners reuse exact successfully published immutable query objects,
and the ordinary public triangle route performs generic device-resident
checked-U64 reduction while returning only an 8-byte scalar. Three complete
nonformal repeats on one RTX A6000 matched exact scalar and per-ray oracles,
recorded one OptiX launch with zero reused-input upload bytes, and measured
0.289--0.295 ms scalar steady medians. The before/after layer diagnostic
isolates the removed approximately 23 ms to repeated Python immutable-input
scanning; the native v7 median remained approximately 0.067 ms.

These are internal implementation diagnostics on one GPU, not a fresh fair
Direct/PyOptiX/RTDL baseline, a second-generation R1 replication, public or
manuscript speedup evidence, external review, consensus, or human authoring
evidence. Formal Goal5842 V12 and the Goal5838 frozen core remain unchanged.
The next performance transaction must be separately preregistered and compare
all providers at one frozen post-R1 source/output contract without discarding
adverse rows. Do not optimize the row-returning bounded-relation route by
pretending it has the triangle scalar contract.

## Critical current override: Goal5842 internally complete on Ada and Ampere (2026-09-03)

Goal5842 is internally technically complete at exactly
`PASS__GOAL5842_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`. The
controlling authority is
`history/internal_docs/goal5842_causal_admission_cost_20260903/GOAL5842_FINAL_INTERNAL_AUTHORITY.json`;
its seal is
`5c8044d9204df6b5d622142aecab8fcd25990e2ca1a19c7c5055ef4e16a31e43`.
Verify it with
`PYTHONPATH=src:. python scripts/goal5842_build_final_authority.py --verify-stored`.

The exact V12 experiment at source commit
`04305fc820290cc183a599376f13d2fb48175233` passed independently on RTX 2000
Ada and RTX A6000 Ampere GPUs with distinct UUIDs. Both complete archives are
hash-bound; each contains 216 causal receipts, 216 baseline subworker receipts,
108 baseline composites, and seven passing formal stages. Fresh Mac replays
from frozen Git blobs reproduce both pod recounts byte for byte. The frozen
cross-generation gate passes without pooling V11 rows or computing
cross-machine raw-time ratios.

Both generations show that generic admission has a measurable cost but is not
the dominant current setup gap; target materialization plus native prepare is
the dominant phase class. All adverse baseline rows remain mandatory. On
Ampere, relation steady RTDL/PyOptiX is 3.13x and triangle is 155.21x; these are
current-implementation measurements, not intrinsic language bounds. Do not
recommend the private checker-off path or authorize public/manuscript
performance wording. External review and consensus remain owner-deferred.

The next engineering work is a new goal, not a Goal5842 rewrite: reuse exact-
identity compiled/prepared state, remove repeated Python/native materialization,
and move triangle checked-U64 reduction to the existing generic device-resident
path while returning only the public scalar. Any post-optimization baseline
requires a fresh preregistration and must retain V12 unchanged.

## Critical current override: Goal5840 bounded refinement evidence complete (2026-09-03)

Goal5840 is complete at exactly
`PASS__GOAL5840_COMPLETE_AT_PREREGISTERED_BOUNDED_REFINEMENT_SCOPE`. The
controlling authority is
`history/internal_docs/goal5840_independent_lowering_refinement_20260903/FINAL_AUTHORITY.json`;
its internal seal is
`3857a8c1f579808ea96a2f54c58e5698818deae7b879c849523ccf72a3f59a80`.
The exact GPU evidence source commit is
`79fdbb61c2afd602a16e8fc01b27d0cf8a576e7b`.

One fresh Attempt-07 run on RTX 2000 Ada / OptiX 9.0 passed all four true-OptiX
modes across three bounded routes. A separately implemented target checker
passed 20/20 property applications, and the isolated mutation suite rejected
15 unique frozen mutations across 20 mode applications. The downloaded
artifact verifier replayed the exact Linux DSO, Git blobs, four bundles, four
checker reports, and all mutations; two Mac runs were byte-identical. The three
Goal5838 frozen-core files changed by zero bytes. Verify the final authority
with
`PYTHONPATH=src:. python3 scripts/goal5840_build_final_authority.py --verify-stored`.

This is bounded structural lowering/refinement evidence for exactly three route
groups, four modes, and five properties. It is not a general compiler-soundness
theorem, arbitrary Callback-IR support, application correctness, performance or
speedup evidence, independent hardware attestation, external review, or
consensus. Attempts 1 through 6 remain preserved engineering failures and must
not be hidden or promoted. External review remains owner-deferred. The next
scientific gates are Goal5841 external-human authoring evidence and Goal5842
causal admission-cost/performance evaluation; do not keep extending the
Goal5840 evidence harness.

## Critical current override: Goal5838 bounded prospective exam complete (2026-09-03)

Goal5838 is complete at exactly
`PASS__GOAL5838_COMPLETE_AT_PREREGISTERED_BOUNDED_SCOPE`. The controlling
machine-readable authority is
`history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_AUTHORITY.json`;
its internal seal is
`c0578a22e006e2bee2dec39e6de98201ce547eca95dc20b6b7f4c1a891479a8e`.
The exact GPU evidence source commit is
`7da68056550818d8e2f6cdb4d7aa3e9029cc4524`.

The independently selected topology is
`builtin_sphere::any_hit_count_continue_u64_per_query`. On one RTX 2000 Ada /
OptiX 9.0 profile, two true OptiX launches matched all 12 independent oracle
rows. The three frozen core files changed by zero bytes after their seal. The
RTDL-free verifier passed and was reproduced byte-identically on the Mac.
Verify the final authority with
`PYTHONPATH=src:. python3 scripts/goal5838_build_final_authority.py --verify-stored`.

This is one bounded prospective frozen-core topology success. It is not
arbitrary Callback-IR execution, universal provider portability, performance
or speedup evidence, a Paper App, application correctness, external review, or
consensus. External review remains owner-deferred. Preserve the frozen core and
all committed Goal5838 evidence; do not rewrite history or broaden wording.
The final technical report and internal hostile review are respectively
`FINAL_TECHNICAL_REPORT.md` and `FINAL_INTERNAL_HOSTILE_SELF_REVIEW.md` beside
the authority. Goal5838 focused tests pass 91/91, inherited Goal5833 tests pass
70/70, and the whole Goal583x audit is 312/313 with only the previously
disclosed Goal5832 current-tree custody error.

## Critical current override: Goal5838 generic core sealed before selection (2026-09-02)

Goal5838 Stage B is frozen at remote commit `1ad0628`. The controlling files
are `history/internal_docs/goal5838_generic_core_exam_20260902/GENERIC_CORE_SEAL.json`
and `CHALLENGE_TABLE.json`; their internal seals are respectively
`c2a461c8a4a61650044b724d103a80d25241b44b7b486c071b601946292e5dae`
and `0a2b2c01aed75ad08fad44f7fbc2509ef632d786545e0202b9a4b27425a30345`.
Verify them with
`PYTHONPATH=src:. python3 scripts/goal5838_freeze_generic_core.py --verify-stored`.

The frozen core is exactly `src/rtdsl/v4_family_schema.py`,
`src/rtdsl/v4_generic_family_lifecycle.py`, and `src/rtdsl/v4_family.py`.
Do not modify any byte in those files during this prospective attempt. The
complete ten-row table and exact NIST target pulse at
`2026-09-02T19:00:00.000Z` were committed before revelation; selected count is
still zero at this checkpoint. Candidate/provider/app/oracle/test/build layers
remain mutable only after selection. Ordinary defects in those extension
layers, missing infrastructure, or a missing pod are pending engineering, not
scientific failure. Scientific failure requires all five preregistered
conditions including a minimal witness that a frozen semantic core change is
necessary.

Stage B has `75/75` focused tests after sealing and the full Goal583x run is
`264/265`, with only the already disclosed Goal5832 current-tree custody error.
This is no prospective GPU success, performance result, external review, or
consensus. External review remains owner-deferred while traveling.

## Critical current override: Goal5837 successor classification frozen (2026-09-02)

Goal5837 is complete at classification-only scope. The controlling authority is
`history/internal_docs/goal5837_owner_grouped_classification_20260902/GOAL5837_AUTHORITY.json`.
Its exact verdict is
`ADDITIONAL_ROOT_EXPORTED_CLOSED_SUCCESSOR_ROUTE__NOT_STABLE_V4_FIXED_CONSTRUCTOR`.
The stable `rtdsl.v4` fixed-constructor count remains two; the owner-grouped
Boolean route is one additional root-exported closed successor route. These are
heterogeneous categories and must not be summed into a claim of three stable V4
constructors.

The authority binds the app-neutral `OWNER_GROUPED_ANY_HIT / BOOL_OR` behavior,
the built-in round-linear-curve OptiX provider, the bounded linear RT-CCD case
study, 9/9 local reference cases, and the already recorded exact-profile OptiX
8 result of 30/30 true launches and oracle matches. It adds no GPU execution.
The successor is not registered as a Goal5832 family-shape/protocol instance
and is not a prospective frozen-core generalization exam. Performance,
speedup, benchmark-app, Paper App, full-reproduction, OptiX 9, external-review,
and consensus claims remain forbidden. External review is owner-deferred while
traveling. Verify with
`python3 scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored`.

The next scientific step is a separately preregistered Goal5838 new-topology
prospective exam. Do not retrospectively use Goal5837 as that exam, and do not
modify the frozen Goal5835/5836 transaction.

## Critical current override: strict Goal5835/5836 audit (2026-09-01)

The controlling post-Goal5836 internal audit is
`history/internal_docs/goal5835_goal5836_strict_audit_20260901/STRICT_AUDIT_AUTHORITY.json`.
Goal5835 is only
`BOUNDED_APP_SEMANTIC_PROJECTION_WITH_INHERITED_TRUE_OPTIX_EVIDENCE`: it
reconstructs app-shaped inputs equal to inherited true-OptiX B3 fixture bytes,
but does not execute the app front door, create a positive complete-mesh case,
or add a Goal5835 GPU launch. Never call it a paper reproduction, executed
Paper App, or full RT-CCD.

Goal5836 remains complete at the A1 negative branch. Do not reopen A2--A5 or
rewrite any hash-bound Goal5835/5836 source, README, result, report, or
authority. Current status is in
`case_studies/sui_derived_edge_crossing_core/CURRENT_STATUS_AFTER_GOAL5836.md`.
The review is internal only: external review was owner-deferred, count is zero,
and no consensus may be claimed. No pod is required for this audit. Verify with
`python3 scripts/audit_goal5835_goal5836.py --verify-stored`.

## Critical current override: Goal5836 terminal at A1; no A2 gate (2026-09-01)

Goal5836 is complete at its preregistered A1 negative branch. The controlling
authority is
`history/internal_docs/goal5836_a1_source_fidelity_20260901/SOURCE_FIDELITY_AUTHORITY.json`
with whole-file SHA-256
`f05b026c2e96506466a400de71ee8ab6893f8deecb547447f29b8af567842c5f`
and internal seal
`5d52efd485eb9433a442c3a9a81d880e91e80bb38de33d6b4499a2329c3034d6`.

Exact static inspection found `MATERIAL_PREDICATE_DIFFERENCE`: the author
benchmark actually enables a strongly connected directed obstacle-edge graph
to preserve inside-start correctness for one-sided rays against hollow round
curves, while Goal5835 retains one arbitrary deduplicated edge direction and
explicitly excludes initial overlap. Ordinary piecewise-linear swept-sphere,
radius/endcap, edge-only and Boolean semantics still match at their bounded
levels.

Machine status is
`TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE`. A2--A5 are
unreachable; there is no next owner gate inside Goal5836. Do not freeze an
input, materialize routes, build/run author or RTDL code, mutate product or
case-study source, use a POD/GPU, collect timing, promote Paper App status,
request external review or make public claims under this transaction. A future
repair requires a new owner-defined preaction and an app-neutral generic
orientation/connectivity contract. Verify with
`python3 scripts/goal5836_a1_build_source_fidelity.py --verify-stored`.

## Historical record: Goal5836 A0 complete before A1 (2026-09-01)

Goal5836 A0 exact source acquisition is complete at
`history/internal_docs/goal5836_a0_source_acquisition_20260901/`.
The controlling authority has whole-file SHA-256
`5d18d5736be47288e6867d29df93a05bc2f7a81462101e563d65f88c5d236bef`
and internal seal
`e266b5376f075c0da96ae93fa5c44e20245a3583e6f122a56e1032035c1c7050`.
The exact arXiv v2 paper, planned author commit
`bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7`, reconstructed root tree
`3e5e1c3a2a128148eae61bc94a22eaae491e496f`, complete 269-file inventory,
203-file selected source capsule and exact MIT license are preserved.

The A0 self-review is
`history/internal_docs/self_review_goal5836_a0_source_acquisition_20260901.md`
at `P0=0/P1=0/P2=3/P3=1`. The official arXiv v2 PDF is not the IEEE publisher
PDF; omitted large author assets require exact-commit reacquisition; metadata
discovery incidentally exposed paper method text but no author source semantics
were inspected and no fidelity classification was made.

At that checkpoint the only next possible owner decision was
`AUTHORIZE_STAGE_A1_AUTHOR_SOURCE_FIDELITY_CLASSIFICATION_ONLY`. It was later
granted and consumed, with the terminal result recorded in the controlling
override above. Verify the historical A0 bytes with
`python3 scripts/goal5836_a0_build_source_acquisition.py --verify-stored`.

## Historical record: Goal5836 preaction before A0 (2026-09-01)

The deterministic preaction is
`history/internal_docs/goal5836_sui_same_input_preaction_authority_20260901.json`
with whole-file SHA-256 `7e021a874a13454488bf056c44402225bc1deadfc990cf2a8aeb48eaed9c7f40`
and internal authority seal
`64457edb02f8b7d9f0636e2b6b08563e7b65069c510446643e5d4588224790dd`.
Its technical plan is
`history/internal_docs/goal5836_sui_same_input_preaction_technical_plan_20260901.md`.
All six stages A0--A5 have `authorized_now=false`; only creation of the
preaction itself was authorized.

At that checkpoint the next possible owner decision was exactly
`AUTHORIZE_STAGE_A0_SOURCE_ACQUISITION_AND_HASHING_ONLY`. It was later granted
and consumed. The historical preaction remains immutable and locally
verifiable with
`python3 scripts/goal5836_build_sui_same_input_preaction.py --verify-stored`.

## Critical current override: MacBook pre-Goal5836 handoff controls continuation (2026-08-31)

The complete cross-machine continuation entrypoint is
`history/internal_docs/handoff_macbook_pre_goal5836_cgo_checkpoint_20260831.md`.
Read it before taking any task action. The correct project is
`rtdl_v4_restricted_python_design`, not the similarly named
`rtdl_v0_4_release_prep_review` workspace. The Git-native recovery branch is
`codex/cgo-goal5836-handoff`; checkpoint `d0bb938...` is an ancestor of the
current branch. The repaired verifier passes both a Git working tree and an
independent capsule extraction at 5358 payloads / 77164522 bytes, the five
controlling evidence hashes match, and the macOS Goal5833--5835 denominator is
102/102.

The first Mac task,
`PRE-GOAL5836-A1__HOSTILE_REVIEW_AND_PREACTION_DECISION`: finish the
interrupted strict review, is complete at
`history/internal_docs/self_review_pre_goal5836_macbook_handoff_a1_20260831.md`.
Its final verdict is `P0=0/P1=0/P2=4/P3=2` and authorizes creation of a
Goal5836 preaction only. Goal5836 execution, author-source acquisition or
comparison, product mutations, POD/modern-RTX execution, performance,
Paper-App promotion and external review remain locked. macOS is for source,
oracle and preaction authoring; it cannot produce OptiX evidence. Do not call
Claude.

## Critical current override: Goal5835 bounded Sui-derived mapping complete; Goal5836 locked (2026-08-30)

Goal5835 implements the research-prototype application mapping at
`case_studies/sui_derived_edge_crossing_core/`: piecewise-linear robot-sphere
segments map one-to-one to round-linear curve capsules; obstacle triangles map
to deterministic shared-edge-deduplicated queries; identities reconstruct to
sphere/path and edge/triangle provenance; the public result aliases the already
sealed generic vector as `per_edge_hit` and its host OR as `collision`.

The controlling result is
`history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_result_20260830.json`
at `ae370da1...ccff`; a separate generation is byte-identical. All 11 mappings
reproduce the exact Goal5834-B3 public static/query commitments and match both
the inherited sealed true-OptiX bits and a second active-set oracle. Goal5835
adds zero GPU launches and zero timings; it explicitly reports the 33 inherited
B3 launches rather than relabelling them. Goal5833--5835 tests pass 102/102.

The result remains `NOT_A_PAPER_APP` with source relation
`SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES` and generalization count zero.
Hit cases use registered edges; only the face-boundary miss reconstructs a
complete triangle. Start-inside/initial overlap, near-tangent/parallel and
face-interior-only collision are outside scope. Exact source provenance,
paper-source positive mesh fixture, author-code same-input comparison and a
modern-RTX end-to-end app run are absent.

Goal5836, any POD/modern-RTX run, author-code acquisition/comparison,
performance, Paper-App promotion and external review are locked until a
separate exact Goal5836 preaction is written and owner-authorized. Do not call
Claude.

## Critical current override: Goal5834-B3 Boolean bridge passed; narrow Goal5835 mapping authorized (2026-08-30)

Goal5834's general First Contact capsule-numeric status remains
`INCOMPLETE`; it was not repaired or relabelled. A separate fixed Boolean
Callback specialization now exposes only `provider_any_contact_bit` per query,
seals the raw GPU vector, and performs host OR afterward. Its shape-only public
admission contains no query-by-primitive CPU geometry.

The controlling B3 result is
`history/internal_docs/goal5834_b3_boolean_collision_bridge_result_20260830.json`.
On Home GTX1070/OptiX 9, 11/11 pre-frozen concrete executions from 10
author-designed fixture families match the independent canonical-f32
segment/capsule oracle. There are 11 primary, 11 repeat and 11 reverse-order
true-OptiX launches, zero status failures and zero registered timings. Home and
local RTDL-free evaluator results are byte-identical. All 21 frozen
query/capsule pair distances also reproduce under a second active-set
implementation. This is registered-fixture evidence, not a generalization
exam, representative corpus, capsule theorem, Paper App, modern-RTX or
performance result.

Preserve both terminal predecessors. B1 reused a single-use live executable
across static scenes. B2 discovered that repeated same-process NVRTC wrapper
compilation changes raw PTX `callseq` comment bytes; identity checks were not
weakened. B3 materializes once in a CUDA-clean parent and lets one sequential
child per static scene consume a fork-private copy of the exact live object.
This is evidence-harness orchestration, not a public usability claim.

Goal5835 is authorized only for the exact registered-fixture Sui-derived
sphere-trajectory/obstacle-edge mapping, inheriting fixture authority
`0f13ab8a...` and worker bytes `55eeff37...`. It may add mapping, deterministic
triangle-edge deduplication, identity reconstruction, README and functional
receipt only. It may not add GPU fixtures, change normalization/oracle/margins,
claim full RT-CCD or Paper App status, measure performance, use a POD, or
request external review. Goal5836 remains the only paper-source/author-code/
modern-RTX/Paper-App promotion gate. Do not call Claude.

## Critical current override: owner reassigns Goals5833--5836 to sphere, curve, and RT-CCD (2026-08-30)

The controlling owner plan is
`history/internal_docs/goal5833_goal5836_sphere_curve_rtccd_owner_replan_20260830.md`.
It append-only supersedes the prior Goal5833--5836 numbering in the next
section. Goal5833 is now the app-neutral OptiX built-in-sphere public lifecycle
plus First Contact and an independent CPU oracle. Goal5834 is the app-neutral
built-in round-linear-curve lifecycle plus capsule/swept-sphere validation.
Goal5835 is the bounded piecewise-linear edge-intersection core of Sui et al.
RT-CCD. Goal5836 pins paper/source/input provenance, performs a same-input
author comparison and modern-RTX functional gate, and promotes the result to a
Paper App only if every explicit gate passes.

The partially created `src/rtdsl/v4_family_schema.py` and
`tests/goal5833_family_schema_compilation_plan_test.py` are an unfinished,
noncontrolling generic-core prototype. Fourteen isolated tests pass, but the
prototype is not integrated, is not Goal5833 evidence, and does not establish
a generic GPU compiler or prospective generalization. Preserve it without
silent promotion; resume that line only under a separately named owner goal.

Sphere and round-linear curve completion may support third- and fourth-leaf-
kind public routes. `4/4` always means leaf-kind presence in the pinned
taxonomy, not complete category/topology/application coverage. RT-CCD remains
a paper-derived core until Goal5836's author/same-input/oracle/hardware gates
pass. No performance or external review is authorized. Do not call Claude.

## Critical current override: Goals5831--5832 complete at family-scope specification level; generic compiler still absent (2026-08-30)

Goal5831 has replaced the false/ambiguous “exactly two public GPU families”
language.  Exact current facts are: pinned OptiX 9 has 6 build-input kinds and
4 leaf primitives; current public routes instantiate 2 build-input enum kinds
(2/6 and 2/4 leaf kinds as kind-presence only, not complete category support),
while RTDL has 2 physical geometry kinds, 2 fixed protocol constructors, and 1 bounded
caller-authored built-in-triangle `u32x3` GPU template.  Particle is a public
specialization of that template; M1--M6 and the 9-system/13-lane cohort are not
family denominators.  Application-semantic protocol shapes are an open set.

Goal5832 freezes a three-domain protocol-shape algebra: family shape
`<G,R,V,E,H,B,C,X,L>`, protocol instance, and deployment.  The exact authority
is
`history/internal_docs/goal5832_protocol_shape_algebra_authority_v1_20260830.json`;
the recursive exact typed validator and 23/23 hostile tests pass; authority
overclaim, support promotion and schema-only identities are rejected, and the
custody manifests are rehashed.  This is explicitly a research
specification/reference validator, not a family-parametric GPU compiler.
Current provider/compiler branches remain concrete-family-specific;
prospective frozen-core new-shape exams and external human authors both remain
zero.  Do not claim arbitrary Callback-IR GPU execution, generic-family GPU
compilation, representative coverage, or a finite percentage of all protocols.

The owner-authorized content-first manuscript is 17 pages at
`paper/cgo2027/goal5832_main.pdf`.  It supersedes the old Goal5822 scientific
content and exact hashes, but is not a page-limited/anonymized submission
artifact.  A new final byte/anonymity gate is required after later compression.
No external review was requested; do not call Claude.  No POD, GPU execution,
formal worker or performance measurement was used in Goals5831--5832.

Next critical path is Goal5833 generic schema admission/compilation plan,
Goal5834 provider-independent GPU lifecycle, Goal5835 refinement, Goal5836
exact core freeze, then parallel prospective Goal5837 new-primitive and
Goal5838 new-topology exams.  A third enum branch or copied wrapper does not
count.  If a prospective challenge changes frozen generic-core bytes, that
exam is a scientific failure.

## Critical current override: Goal5822 CGO scientific/double-blind bytes passed; upload destination only remains (2026-08-29)

The exact eight-page anonymous review PDF is
`paper/cgo2027/main.pdf` at
`1674abc383c7652fc6cbe00d331c4c8f39fb03eca1effed1f47480c20decbcd4`
(524,918 bytes). Its exact source is `paper/cgo2027/main.tex` at
`8457388817734c3a20b515b546f8b4c359f401a0f895803749bad809e7c6fddd`
(41,713 bytes). The deterministic anonymous artifact is
`paper/cgo2027/rtdl_cgo2027_anonymous_artifact.tar.gz` at
`55efd603c7a03111e365b7a6caee109e196bff621bef0f68913e37440c042bac`
(43,396 bytes). Final hostile gate: P0=0/P1=0/P2=0/P3=1; the sole P3 is a
nonblocking verifier PASS-banner shorthand, while the paper/README/verifier
body accurately state the preserved-projection boundary.

Goal5818 strongest-native/OWL residual authority is A3
`448ebaa2...d7960`: OptiX 9 typed payload semantics are active; five
preregistered typed-route realizations survive the evaluated native route;
CP004 is only partial status-gated continuation/completeness; strongest-native
scope is one GTX1070/Pascal environment with a disclosed two-line PyOptiX FFI
repair, not stock-PyOptiX, modern RTX, or performance evidence. Goal5819 A3
`e904026a...8458` freezes the two-task/single-RTX-4000-Ada performance sentence:
steady RTDL/PyOptiX passes the registered 1.05 gate on both tasks; observed
deployment-cold/prepare setup delta is 162--223 ms; Direct rows are descriptive.
Goal5820 completed validly at 0 ENFORCED / 4 NOT_FOUND / 16 UNCERTAIN but is
non-paper-ready and excluded without rescue.

Binding limits remain: exactly two closed public GPU families, nine project-
authored apps/thirteen lanes, prospective unbiased new-app exams 0, third-party
human authors 0, human usability studies 0. Do not claim arbitrary Callback IR
GPU execution, ease/productivity, zero overhead, stock-PyOptiX strongest-native
evidence, or universal Direct parity.

Authoritative result/self-review/single-file CFR are
`history/internal_docs/goal5822_final_cgo_submission_byte_gate_20260829.json`,
`history/internal_docs/self_review_goal5822_final_cgo_submission_bytes_20260829.md`,
and
`history/internal_docs/call_for_review_goal5822_final_cgo_submission_bytes_20260829.md`.
Send only the CFR for external review. No POD or Goal5823 checker-off experiment
is needed before submission. The only remaining mutation is insertion of an
anonymous artifact URL or approved supplementary destination, followed by a
delta-only rebuild and anonymity scan. Any other manuscript change breaks the
frozen hashes and requires a new final gate.

## Critical current override: Goal5793 S0 externally accepted and closed; X1 local CPU work only is authorized (2026-08-22)

The owner-returned external review is
`history/internal_docs/review_goal5793_s0_preregistration_and_generic_examiner_entry_20260822.md`,
21,765 bytes at `339929b0...aae09`. Verdict is P0=0/P1=0/P2=2/P3=1:
S0 is accepted, and only X1 may proceed after append-only owner absorption.
The review independently reconstructed all seven S0 roots, the 326-row declared
source/native-source surface, 324/326 exact v26 custody with the two declared
missing paths, all 35 permanently ineligible legacy rows, zero qualified Role A,
zero ordered triplets, the TLV/rejection KAT and all twenty hostile fail classes.
S0 acceptance is not a Goal5793 result: exam and generalization evidence counts
remain zero.

The owner send receipt is
`history/internal_docs/goal5793_s0_owner_send_receipt_20260822.json`, 2,878 bytes,
file `8d5b3137...8efb9`, internal `c0fec710...b095e`. The owner supplied the
date `2026-08-22`, UTC offset `-04:00` and recipient
`Claude (claude-opus-5)` but no time of day. The receipt preserves that partial
precision literally; it does not substitute the current time or file mtime and
does not claim an exact RFC3339 timestamp. Exactly one CFR was sent and no S0
packet was sent.

Append-only absorption is
`history/internal_docs/goal5793_s0_owner_returned_external_review_absorption_20260822.json`,
8,453 bytes, file `268053e3...98e6`, internal `e020ae2a...3e60`.
The controlling closure is
`history/internal_docs/goal5793_s0_postreview_closure_and_x1_entry_20260822.json`,
9,317 bytes, file `4d6e37bc...1f41`, internal `cc118989...0a1a`.
It moves only to `S0_35ROW_TERMINAL_REVIEWED`; X1 is authorized for local CPU
scripts/tests/evidence only and is neither implemented nor externally reviewed.

Both review P2s are mandatory X1 closure gates, not retroactively closed S0
findings. X1 must provide one self-contained reviewer-runnable delivery that can
reconstruct all 326 rows, the pinned Goal519/521 blobs and all twenty hostile
classes without Git, workspace `src/**` or network. X1 must also bind the exact
752,766-byte survey source archive at `bfe852a1...3857`, conservatively place
every bibliography entry into the permanent exposure registry, and preserve all
coverage gaps. New X1 set digests use one named shared canonical helper; no
historical Goal5789 or S0 digest is reinterpreted.

No X2 work, systematic search, live provider call, entropy anchor/draw,
selection, candidate implementation/execution, product or `src/**` change,
native-source/family/role/opcode/rule/facade change, candidate-specific native,
ambient library search, GPU/Home/POD/SSH, worker, registered/performance timing,
external reviewer contact, public release, publication or submission is
authorized. X1 must receive its own returned review at P0=0/P1=0 and append-only
owner closure before X2 can be considered.

## Critical current override: Goal5789-A2 postreview technical closure complete; Goal5793 S0 preregistration authoring only is next (2026-08-22)

Goal5789-A2 has technically closed the Callback-IR authority gap and all three
P2 plus one P3 findings from the owner-returned external review. The controlling
review is
`history/internal_docs/review_goal5789_a2_callback_ir_authority_binding_and_goal5793_entry_20260821.md`
at `88e0aff9...1bd3a` (`P0=0/P1=0/P2=3/P3=1`). Append-only repair result and
absorption report are
`history/internal_docs/goal5789_a2_postreview_repairs_result_20260821.json`
at `e4875811...23b89` (internal `16c320c4...e05cc`) and
`history/internal_docs/goal5789_a2_owner_returned_external_review_absorption_and_repairs_20260821.md`
at `0ed7b9c4...23307`.

The hostile matrix successor preserves the same 159 case identities but now
checks exact normalized reason sets for all 126 certificate-only cases. Report
the matrix only as 143 negative mutations, 15 baselines and one passing TCB
control; never call it 159 rejections or 159 negative attacks. RTXRMQ source
custody is recovered from the immutable Goal5783 archive already nested in the
reviewed packet. The historical packet had no direct repository-path RTXRMQ
payload and could not run the unchanged materializer after only top-level
extraction. The successor exposes the exact `0823fdf3...a3b0b1` source and a
fresh interpreter reproduces Callback authority `16422fc2...0a5a59a` and pin
`98e2aa6b...dd1a0d` byte-for-byte. The old packet remains historically
unchanged.

The deterministic postreview packet and twin are
`history/internal_docs/goal5789_a2_postreview_repair_packet_v1_20260822.tar.gz`
and `_twin_20260822.tar.gz`, both 50,169,373 bytes at
`e8da7847...dac7f5`. Its manifest is `f33ddfca...762c04`: 137 exact payloads,
52,428,037 payload bytes and payload-set `a51759a0...1b11`. Independent audit
is `a91c53ac...c7e23`, internal `7aae0d00...3fb6`; it replays the materializer,
checks all payloads, canonical paths/order/gzip/tar metadata, empty PAX and
uname/gname, and explicitly does not claim a hermetic Python environment.
Postwrite combined tests pass 27/27, and two independent closure audits returned
`P0=0/P1=0/P2=0`.

The controlling closure is
`history/internal_docs/goal5789_a2_postreview_closure_and_goal5793_s0_entry_20260822.json`,
11,247 bytes, file `ad06d871...7c288e`, internal `650de991...03aa4`.
It append-only supersedes the two Goal5789-A1 overrides below. The accepted
claim remains bounded: six of fifteen inventory rows are Callback-bound and
compatible; nine are unbound UNKNOWN. Binding establishes executed-program
identity and exact projection, not semantic correctness. Product IR,
authority producers and external roots remain TCB; mutually consistent
jointly-wrong authorities are not detected. Particle and RTXRMQ share an exact
Callback program, so this layer does not distinguish their semantics. No
soundness, completeness, false-rejection rate, generalization, third-family,
all-path gating, usability, production, performance, public, publication or
submission claim is authorized.

The only newly authorized action is authoring and freezing a separate exact
Goal5793 S0 preregistration. Entropy draw, candidate selection, candidate
implementation or execution, Goal5793 result claims, product/checker/native/
application/registry/rule/toolchain changes, GPU/Home/POD/SSH, workers,
timings, reviewer contact, public release, publication and submission remain
forbidden. RTXRMQ cannot count as a Goal5793 exam. Do not call Claude for this
closed Goal5789-A2 transaction.

## Critical current override: Goal5789-A1 postreview P1 blocks Goal5793 entry (2026-08-21)

The returned Goal5789-A1 review remains exact and its Q2/Q4 scientific replays
remain valid, but a postreview hostile audit found a missed C1 binding gap. In a
frozen passing certificate, clearing every `callback_contract.roles[*].effects`
list, retaining the IR/effect digests, and resealing only the certificate still
returns compatible with complete reference admission. The Goal5789 builder
constructs these summaries rather than loading an independent Callback-IR
authority. Role names are decisive; allowed-subset effect contents are not
independently bound.

The controlling terminal is
`history/internal_docs/goal5789_a1_postreview_local_p1_role_effect_binding_terminal_20260821.json`
(file `8a296014...be7be`, internal `96d11078...7f862`); its human report is
`bbcbf08c...04676`. Windows/POSIX reproduction commands are append-only
clarified by `11526212...da243`. It append-only supersedes the S0-entry authority in the
postreview closure below without changing the external review or its packet.
Goal5793 is blocked, including S0 authoring, entropy, selection, implementation
and execution.

Before Goal5793, the owner must separately authorize either (preferred) a
successor that binds callback role/effect/resource summaries and IR/effect
identities to an independent Callback-IR authority, with coordinated re-sign
attacks and successor external review, or a material narrowing that declares
those summaries builder/certificate TCB and receives external review. Do not
classify this central obligation as ordinary metadata. No checker/product
change, Home GPU, POD, SSH, worker, timing, public, publication or submission
action is currently authorized.

## Critical current override: Goal5789-A1 externally approved and absorbed; Goal5793 S0 preregistration is next (2026-08-21)

The owner-returned external review at
`history/internal_docs/review_goal5789_a1_post_goal5792_theory_readiness_and_goal5793_entry_20260821.md`
(SHA-256 `13130c81...c3e2a`) approves C1 only at bounded, registered
assume-guarantee catalog scope over two geometry families. It independently
replays 6 compatible / 9 UNKNOWN / 0 incompatible inventory rows, the six
legal-self-consistent-wrong counterexamples, the sharp Q4 policy mismatch, and
the Q2 jointly-wrong-authority attack. Authorities remain TCB: the checker
detects disagreement between registered parties, not error shared by them.

Append-only absorption is
`history/internal_docs/goal5789_a1_owner_returned_external_review_absorption_20260821.json`
(file `2836bd40...91051b`, internal `b3f82817...873eb7`). Postreview closure is
`history/internal_docs/goal5789_a1_postreview_closure_and_goal5793_s0_entry_20260821.json`
(file `6da608cc...7bbad`, internal `7cc9d2f5...cccdf`). P2-2 and P2-3 are
closed by immutable-name disambiguation and an explicit RayDB private-route
facade boundary. P3-1 is closed by a supplemental canonical payload-set digest
verifier. P2-1 remains an accepted technical residual: the independent checker
does not bind `total_static_iterations` to an authority or target upper bound.
It is explicitly classified as audit metadata and may not be counted as a
checked obligation; original K6 is not claimed fully discharged.

Goal5793 may now enter only S0 preregistration authoring. Before any entropy
draw or candidate selection, freeze the postreview core, the P2-1 residual,
candidate universe, all eligible role-stratified triplets, entropy source and
selection algorithm. No candidate selection, implementation, execution, Home
GPU, POD, SSH, performance timing, public, publication or submission action is
authorized by this closure. Goal5793 cannot establish a third family or a
false-rejection rate, and any valid rejection, UNKNOWN or 0/3 result is terminal
and may not trigger outcome-directed rescue.

## Critical current override: Goal5791 local science complete; controller terminal, zero paper-eligible clear wins, owner review required (2026-08-21)

Goal5791 completed its one preregistered same-source, same-cohort Triangle
RT-2A1 fusion ablation on RTX 4000 Ada CC8.9. Exactly 96 workers ran once in 96
fresh parent PIDs; all outputs are exact and behaviorally true-OptiX. No worker
failed, timed out, retried, resumed, was replaced, dropped or relabelled. The
ratio is fusion-OFF/fusion-ON, so greater than one favors fusion-ON.

The statistical result is 2/6 CI-clear wins, 0/6 clear losses and 4/6 CI
crossings. Both statistical wins exceed the frozen conservative trace-cost
eligibility threshold: cit-Patents cold-process/warm-system is 2.85180597% and
soc-LiveJournal1 prepared is 4.66384339%, versus the required <=1%. Therefore
the paper-eligible result is 0/6 and the only permitted preregistered branch is
`zero_clear_winning_rows`. Do not claim fusion is slower; do not claim a clear
end-to-end fusion benefit, universal compiler fusion, or Particle causality.
C1 remains the manuscript center of gravity.

The controller transaction is permanently terminal. It launched all workers,
then the frozen evaluator rejected two honest producer identities before
publication: it equated two independently generated nonce roles and compared a
plan's dataset-oracle authority to the generic oracle-contract digest. The
final formal root was never created. The immutable terminal tar is
`history/internal_docs/goal5791_formal_v4_terminal_20260821.tar.gz` at
`53845c83...7f0252` (92,199,259 bytes). Corrected analysis consumers changed no
worker, timing or scientific rule and produced primary `69e56a62...970b819`,
recount `d50d7ae7...0ace38`, and sealed offline successor result
`e8417161...0c6bc5` (internal `b91c1dc8...c1bc8`). Never relabel this as an
ordinary controller publication.

The sole controlling third audit is `AUDIT_V3.json` at
`719ec679...0b7317` (internal `87ea0582...3d96`). Audit v1/v2 are preserved but
superseded because hostile review exposed incomplete governance checks. The
five-module formal regression is 57/57 PASS, evaluator/recount is 17/17 PASS,
terminal-successor hostile tests are 4/4 PASS, and two independent fixed-byte
local reviews returned P0=0/P1=0. Local closure is
`history/internal_docs/goal5791_formal_v4_local_scientific_closure_20260821.json`
at `829f1996...7302` (internal `0175b116...ed10`). Exact POD staging, terminal
tar and materialization roots were removed only after local closure; cleanup
receipt is `history/internal_docs/goal5791_formal_v4_remote_cleanup_receipt_20260821.json`.

Four P2 caveats are binding: the pre-POD mock fixture missed two real producer
shapes; controller-terminal and science-complete must remain distinct; the
12,202 ns/event trace bound was measured on the Windows/Sandy Bridge-EP build
host rather than the target CPU; and audit v3 does not itself reopen
`FORMAL_CONTRACT.json`, though two reviewers independently reproduced its
canonical digest. External review is owner-controlled through
`history/internal_docs/call_for_review_goal5791_formal_v4_rtx4000ada_result_20260821.md`.
Read it together with amendment A1 at
`history/internal_docs/call_for_review_goal5791_formal_v4_rtx4000ada_result_amendment_a1_20260821.md`.
The A1 authority `c0128ff5...e2d7d5` (internal `e71be2de...a77a33`)
append-only corrects a P2-count header transcription, classifies the nonce-only
repair hashes as non-controlling intermediate lineage, and supplies the exact
12-key all-false authorization vocabulary. It changes no science or controller
status.

Owner-returned external review is now complete. The main review at
`history/internal_docs/review_goal5791_formal_v4_rtx4000ada_result_20260821.md`
(`c97052ee...687100`) accepts P0=0/P1=0/P2=3/P3=2 and independently rules the
zero-clear-row branch mechanically supported. The A1 follow-up at
`history/internal_docs/review_goal5791_formal_v4_rtx4000ada_result_amendment_a1_20260821.md`
(`2ff0652f...d6ed0`) accepts the append-only correction.

The current discoverable entry point is repository-root
`GOAL5791_EXTERNAL_REVIEW_ENTRYPOINT_20260821.json` (`933014cc...3a45f`,
internal `7a80112c...af097`). External-review absorption A2 is
`history/internal_docs/goal5791_formal_v4_external_review_absorption_and_amendment_a2_20260821.json`
(`4303f2ca...5a4a89`, internal `cc629b3d...f94859a`). A2 provides a re-runnable
claim-hygiene scan, immutable archive of the corrected analysis sources, the
required future nonce-check repointing, and a clearly non-controlling post-hoc
sensitivity note: both statistical wins survive subtraction of the entire
frozen trace bound, but the preregistered 1% eligibility gate and
`zero_clear_winning_rows` branch do not change. Recount independence must be
qualified as independent implementation/statistical reconstruction under a
shared consumer contract.

Do not call Claude. No rerun, new POD, tuning, replacement worker, timing reuse,
row removal, public release or submission is authorized by Goal5791.

## Critical current override: Goal5790-A1 bounded rejected-program Home closure complete; owner review required before Goal5791 (2026-08-16)

Goal5790-A1 is complete at bounded Home semantic/physical rejection scope. The
exact suite contains six preregistered silent-wrong counterexamples across four
real application families and two OptiX geometry families. Eighteen arms ran in
eighteen fresh parent PIDs on Home `lx1` (GTX 1070, CC6.1): five associations
were rejected by the public semantically admitted compiler facade and Particle
orientation was rejected earlier by Typed Physical Schema. All reject arms had
zero product launch. Six isolated test-only diagnostics legally executed and
produced the independently predicted wrong application answer. Five admitted
controls returned the correct value; the checked-U64 control correctly failed
closed before wraparound, output, or traversal receipt.

There are eleven behaviorally true-OptiX receipts covering thirteen successful,
complete launches and sixteen raygen invocations, with zero failed/incomplete/
unbound/pending/session-error state. Formal workers and registered performance
timings are both zero; no POD or performance claim exists. Executed scientific
source is portable v3 `091035a8...fa69` (tree `b458afac...273d`), native is
digest-only `4686286f...d325`, and target is `194ce94a...c263`. Portable v4
`fe7cb3ea...fd1f` is strictly a postrun verifier successor: it reran zero worker
and zero GPU action and did not replace scientific bytes.

Final evidence/twin is `006842c8...d0ac` (50 manifested payloads / 2,111,178
payload bytes; 51 regular members including the non-self manifest). Independent
raw-byte audit reproduced 6/18/18, the 5+1 rejection split, all six wrong-answer
pairs, 11 receipts, 13 launches and 16 raygen with no discrepancy. Authoritative
result/report/self-review/CFR are
`history/internal_docs/goal5790_a1_home_rejected_program_suite_result_20260816.json`,
`history/internal_docs/goal5790_a1_home_rejected_program_suite_technical_report_20260816.md`,
`history/internal_docs/self_review_goal5790_a1_home_rejected_program_suite_20260816.md`,
and
`history/internal_docs/call_for_review_goal5790_a1_home_rejected_program_suite_20260816.md`.
The non-self delivery manifest is
`history/internal_docs/goal5790_a1_delivery_manifest_20260816.json` at
`cc309514...041e0` (57 files / 44,478,743 bytes, zero mismatch).

The scoped verdict is P0=0/P1=0/P2=3: the private classifier registry and the
test-only six-case catalog are TCB; admission binds a compiler tuple rather
than arbitrary runtime arrays; and the unchecked-U64 diagnostic event is
transitively rather than self-sealed. Do not claim arbitrary-Python semantic
inference, universal soundness/completeness, mechanized proof, hostile
same-process security, six facade rejects, six accepted traversal receipts,
native/PTX bytes shipped in the evidence archive, performance, RT-silicon,
POD, public, production or submission readiness. Goal5789 remains 6 compatible
/ 9 UNKNOWN; old Goal5790 fusion evidence is unchanged. External review is
owner-controlled. Do not call Claude and do not begin Goal5791 without owner
approval.

## Critical current override: Goal5785 local pre-POD readiness complete; exact v1 awaits RTX 4000 Ada target (2026-08-15)

Goal5785 has completed every material local step for the single final nine-app
V2-direct/V4 real-scale cohort.  The sole deterministic bundle and twin are
`history/internal_docs/goal5785_final_nine_app_pre_pod_bundle_v1_20260815.tar.gz`
at `0c21adeb...d7d6`; exact source and twin are `26926fdb...e96b`, and the
unchanged real-scale data archive is `f84ed439...81ad`.  The scientific source
is exact Goal5782 plus one complete 637-file source manifest; zero existing
source files changed and no target native is bundled.

The frozen matrix is nine apps, 464 fresh workers, 232 V2-direct/232 V4 and 34
independent rows (15 cold, 19 prepared).  V3 is neither required nor executed.
Goal5776 remains immutable at 9/34 median pass and Goal5784 at 5/8; all losses,
uncertainty and CI endpoints remain mandatory.  The expected result is
pre-registered as mixed and overall all-row no-slower is not expected.

Exact-source verification passes 637/637 manifest entries and 78/78 tests on
Windows and Home Linux; Goal5785 transaction/authority/upload tests pass 6/6.
Bundle/source twins, upload manifest and clean audit all pass.  Home Linux
exposed and preserved one zero-worker PowerShell-to-SSH `$PWD` interpolation
mistake; the unchanged source passed after the command used absolute remote
paths.  This is Pascal qualification, not modern-RTX performance evidence.

The conservative measured bound is 7.859 hours for formal execution and 8.859
hours including prepare; request at least a ten-hour uninterrupted target
window.  The exact runbook and target-derived authority helper are frozen.
Stage-A inspection on the new POD caught one pre-upload P1: upload-manifest v1
omitted the exact OptiX 9 header archive required by the runbook.  V1 remains
rejected; append-only v2 adds `goal5749_optix9_include_20260811.tar.gz` at
`7fae86ce...bee54` (`OPTIX_VERSION=90000`) without changing the candidate,
source, data or experiment.
One create-only RTX 4000 Ada prepare must come first and emit zero formal
workers/timings.  The 464-worker matrix requires a second exact owner authority
binding the returned target/prepared/runtime identities.  No repair, retry,
resume, replacement, timing reuse, row dropping or relabelling is allowed.

Authoritative readiness result/report/two self-reviews/CFR are
`history/internal_docs/goal5785_final_nine_app_pre_pod_readiness_result_20260815.json`,
`history/internal_docs/goal5785_final_nine_app_pre_pod_readiness_technical_report_20260815.md`,
`history/internal_docs/self_review_goal5785_final_nine_app_pre_pod_readiness_20260815.md`,
`history/internal_docs/self_review_goal5785_second_pass_paid_run_failure_prevention_20260815.md`
and
`history/internal_docs/call_for_review_goal5785_final_nine_app_pre_pod_readiness_20260815.md`.
No POD or formal performance result exists yet.  Do not call Claude.  No
performance/no-slower/outperformance, author, RT-silicon, production, public or
submission-ready claim is authorized.

## Critical current override: Goal5784 complete; Triangle RT-2A1 is the second named fusion family (2026-08-15)

Goal5784 completed one exact targeted RTX 4000 Ada v5 measurement: three
Triangle RT-2A1 datasets plus RT-BarnesHut author-32768, cold and prepared,
eight ABBA pairs, V2-direct and V4.  All 128 workers are exact-output correct,
behaviorally true-OptiX and use unique parent PIDs.  There is one exact
source/native/target/prepared/plan/runtime/formal identity, zero V4 leaf-cache
misses or disabled entries, 37,504 leaf traversal receipts and zero failed,
incomplete, unbound, pending or session-error launches.

The exact row-local result is 5/8 median pass and 3/8 fail.  Four CIs are wholly
above one, three wholly below one and one crosses one.  Triangle cit-Patents
and LiveJournal are clear V4 wins under both cold and prepared lifecycles;
Triangle com-dblp fails both; RT-BarnesHut cold fails and prepared is uncertain.
Cold and prepared all-row no-slower are both false.  No cross-row/lifecycle
compensation is allowed.

The preregistered mechanism gate is satisfied: all 48 Triangle V4 workers bind
actual per-segment `compiler_fused_checked_u64_device_reduction` evidence and
four Triangle rows have CI lower bound above one.  Therefore Triangle RT-2A1
is the second named demonstrated fusion family.  RT-BarnesHut is explicitly
non-fusion and never contributes to this claim.  This is not nine-app V4
superiority or overall all-row no-slower.

Primary evaluation, submitted recount and a third independently implemented
raw recount agree exactly on all 64 ratios, eight medians and sixteen CI
endpoints.  Exact source/native bytes and all raw workers are local.  Final
evidence/twin is
`history/internal_docs/goal5784_a4_final_evidence_20260815.tar.gz` at
`a1f2ea4d...fd18` (19 payloads / 71,414,545 payload bytes); exact data
archive/twin remains the local sidecar `f186cd28...e6eb`.  Authoritative result,
report, A3/A4 self-reviews and CFR are
`history/internal_docs/goal5784_a4_targeted_modern_rtx_result_20260815.json`,
`history/internal_docs/goal5784_a4_targeted_modern_rtx_technical_report_20260815.md`,
`history/internal_docs/self_review_goal5784_a3_v5_formal_execution_20260815.md`,
`history/internal_docs/self_review_goal5784_a4_final_closeout_20260815.md` and
`history/internal_docs/call_for_review_goal5784_complete_targeted_modern_rtx_result_20260815.md`.

Preserve two failed lineages: v3 A2 had zero formal workers; v4 A3 has one
unpaired V2 timing and was never reused.  The v5 cohort is fresh.  Two process
P1s are disclosed: the formal wall time exceeded the frozen budget by 29.22%,
and the operator first spoke 4/8 before immediately correcting to 5/8.  Neither
affected scientific bytes or statistics.

Goal5784 is terminal and internally triple-reviewed.  External review remains
owner-controlled; do not call Claude.  Do not start a Goal5784 repair, rerun or
new POD.  Do not claim overall all-row no-slower, nine-app superiority, author
performance, universal GPU/scale results, RT-silicon utilization, public or
production readiness, or submission readiness from this result alone.

## Critical current override: Goal5784 targeted second self-review closed a P1; exact v3 is the sole local pre-POD candidate (2026-08-14)

Goal5784 has completed all material local work for the smallest defensible
modern-RTX confirmation of Goal5782.  The sole candidate is deterministic
bundle v3 `history/internal_docs/goal5784_targeted_pre_pod_bundle_v3_20260814.tar.gz`
at `171a7d83...5f65`; its twin is byte-identical.  It binds exact Goal5782
scientific source `3237354a...ebec`, deterministic targeted data
`f186cd28...e6eb` (five payloads / 700,548,773 raw bytes), frozen
preregistration `89fd0200...f9be`, budget `d4667795...6505` and expectation
`30d8426d...c6cd`.  It contains no target native.

A deliberately non-duplicative second self-review found one real P1 before any
POD or timing: bundle v2 could have awarded the Triangle second-fusion-family
claim from a favorable CI without requiring the actual per-segment checked-U64
device-reduction receipts in every V4 worker.  Bundle v3 propagates and
canonicalizes those real receipts after the application-owned registered timer;
the primary evaluator requires all 48 Triangle V4 workers to bind them and the
independent recount verifies each worker separately.  Source/program names are
not accepted as behavioral substitutes.  Bundle v1 and v2 are superseded and
must not execute.

The exact scope is three Triangle RT-2A1 real datasets plus RT-BarnesHut 32,768,
cold and prepared, eight ABBA pairs, two methods: 128 workers / eight
independent rows.  The earlier oral 64-worker statement was a self-caught P1;
correct arithmetic is 4 * 2 * 8 * 2 = 128.  It was caught before any worker or
POD.

Workspace, Windows clean extraction and Home Linux exact-bundle checks pass;
the focused suite is 31/31.  Exact v3 also rebuilt a fresh Home native and ran
the real com-dblp RT-2A1 V4 path: output was exact, traversal was behaviorally
true-OptiX, and all eight segments carried one checked-U64 device-kernel launch
and one synchronization.  This diagnostic retained no performance timing.
There are zero formal workers, zero registered timings and no POD authorization.
A future RTX 4000 Ada transaction first requires exact owner authority for
create-only preparation.  Preparation emits zero formal workers and generates
the target native/prepared/plan/runtime identities.  The 128-worker matrix then
requires a second exact owner authority binding those identities and confirming
the 7,873.533832750981-second formal budget.  No repair/retry/resume/replacement/
row drop/relabel is allowed.

The original readiness packet remains immutable.  Its append-only correction is
`history/internal_docs/goal5784_amendment_a1_mechanism_binding_result_20260814.json`
and the targeted second review is
`history/internal_docs/self_review_goal5784_second_pass_targeted_mechanism_binding_20260814.md`.
No external review has been performed by the agent; whether one is necessary is
an owner decision.  Do not call Claude.  No performance, no-slower,
second-fusion-family, publication, public or production claim exists yet.

## Critical current override: Goal5783-A1 externally accepted; held-out functional exam evidence complete (2026-08-14)

The owner-returned external review at
`history/internal_docs/review_goal5783_amendment_a1_external_audit_convenience_20260814.md`
(`d436c961...eab3b`) accepts the append-only Goal5783-A1 closeout with no
blocking finding. The shipped Goal5782 frozen source archive independently
rehashes to `3237354a...ebec` and contains exactly 318 frozen `src/` files.
Both held-out RTXRMQ runtime call sites now pass literal
`expected_output=None`; result comparison occurs only after runtime return.
The A1 Home rerun remains 4/4 exact and behaviorally true-OptiX with 19 raygen
invocations. Independent CPU closest-hit reconstruction confirms the frozen
geometry implements RMQ argmin including leftmost ties.

Structured absorption and closure are
`history/internal_docs/goal5783_amendment_a1_owner_returned_external_review_absorption_20260814.json`
and
`history/internal_docs/goal5783_amendment_a1_postreview_closure_20260814.md`.
The original Goal5783 approval and all limits remain unchanged: this is a
small-n held-out functional existence proof under deliberate strong-fit
selection, not a hit-rate, full Algorithm-5, performance, modern-RTX,
RT-silicon, Paper App, universal, production, public-release or submission
claim. Do not call Claude. No POD or successor is authorized by this review.

## Critical current override: next-stage plan approved; A1 frozen; Goal5778 local/Home closure complete (2026-08-14)

The owner-returned external review
`history/internal_docs/review_v4_cgo_next_stage_plan_after_goal5776_20260814.md`
at `92eec43b...9ef17` approves the Goal5776 absorption, the revised V4/CGO
plan, local Goal5778 completion, and observation-only Goal5779/5780.  Its
three conditions are frozen in
`history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json`
(`343015ce...9fca`) and the matching Markdown (`c7b7f4f4...feca`): Goal5779
competitiveness means a lower 95% CI endpoint at least 0.95 on every one of at
least three preregistered same-plan comparator families; fallback claims are
predeclared; and a clear favorable row counts as fusion only with a named,
causally evidenced mechanism.  The current fusion-mechanism count is one
(Particle); RayJoin batch5 does not count.  After Goals5779--5781, a mandatory
IMPLEMENT/REJECT/LEAVE-OPEN decision register blocks a fourth audit and Goal5782.

Goal5778 is complete at generic capability and local/Home functional scope.
The app-neutral checked-U64 weighted device reduction replaces three CuPy
reductions, three synchronizations and a product temporary with one kernel and
one sync.  Strict review caught and fixed an unsound caller-declared value
bound before final evidence; the final kernel returns actual maximum value and
fails closed if it exceeds the semantic bound.  Home GTX1070 evidence has four
generic exact cases, three fail-closed attacks, exact RT-DBSCAN second-consumer
directed-edge total, and both Triangle algorithms exact/behaviorally
true-OptiX; 23/23 focused/regression tests pass.  Evidence archive/twin is
`f00ccf88...ff72` (17 payloads / 103,163 payload bytes).  Goal5776 is unchanged.

Authoritative Goal5778 result/report/self-review/CFR are
`history/internal_docs/goal5778_generic_checked_u64_device_reduction_result_20260814.json`,
`history/internal_docs/goal5778_generic_checked_u64_device_reduction_technical_report_20260814.md`,
`history/internal_docs/self_review_goal5778_generic_checked_u64_device_reduction_20260814.md`,
and
`history/internal_docs/call_for_review_goal5778_generic_checked_u64_device_reduction_20260814.md`.
No POD or target performance is authorized.  Next is Goal5779 Stage A static
comparator freeze only; no device timing may occur before its exact hashed
identity artifact exists.  Do not call Claude.

## Critical current override: Goal5776 externally approved; V4/CGO next-stage plan awaits owner decision (2026-08-14)

The owner-returned external review at
`history/internal_docs/review_goal5776_v9_rtx4000ada_real_scale_v2_v4_result_20260814.md`
(SHA-256 `c2d489ae...f62aff1`) independently reconstructs the exact Goal5776
measurement and approves it.  The correct headline is 34 independent rows,
9 pass by median / 25 fail, but only two rows have 95% CIs wholly above one;
cold is 1/15 and prepared is 8/19.  All-row no-slower and broad V4
outperformance are not met.  Goal5776 remains immutable and closed as a
measurement.  The append-only clarification and structured absorption are
`history/internal_docs/goal5776_v9_postreview_presentation_and_provenance_closure_20260814.md`
and
`history/internal_docs/goal5776_v9_owner_returned_external_review_absorption_20260814.json`.

A draft CGO-centered next-stage plan is in
`history/internal_docs/v4_cgo_next_stage_work_report_and_plan_after_goal5776_20260814.md`,
with machine-readable register
`history/internal_docs/v4_cgo_next_stage_goal_register_after_goal5776_20260814.json`
and CFR
`history/internal_docs/call_for_review_v4_cgo_next_stage_plan_after_goal5776_20260814.md`
(SHA-256 `ceb9429e...38873`).  It asks the owner to replace the future
publication gate of absolute every-row outperformance with an evidence
contract of absolute correctness/true-OptiX, controlled same-plan code-quality
competitiveness, and statistically clear cross-application fusion wins.  This
does not change Goal5776 statistics.  The plan is not yet owner-approved and
authorizes no POD or performance claim.

Goal5778 is the already-authorized local successor from Goal5777: an
app-neutral fused checked-U64 device reduction.  It has partial local code,
12 focused Goal5777/5778 tests pass, and a Home micro-diagnostic is explicitly
non-formal.  Goal5778 is not complete.  Do not start Goals5779+ before owner
approval.  V3 is not deleted; the draft proposes freezing further V3
development and retaining it only as a bounded predecessor/ablation.  Do not
call Claude; external review remains owner-controlled.

## Critical current override: Goal5776 v9 RTX 4000 Ada real-scale V2/V4 matrix complete; 9/34, no-slower not met (2026-08-14)

The exact v9 transaction completed one uninterrupted 464-worker RTX 4000 Ada
formal matrix. All 464 workers are exact-output correct and behaviorally
true-OptiX with unique parent PIDs, one exact source/native/plan/formal
identity, 232 V2-direct and 232 V4 workers, and 232 exact input/output pair
groups. No repair, retry, resume, replacement, row dropping, timing reuse or
relabeling occurred after worker zero.

Primary and independent raw recount agree exactly on all 34 independent rows.
The ratio is V2-direct/V4, so greater than one favors V4. The result is 9 pass
/ 25 fail: installed cold compile+prepare+execute is 1/15; prepared first
execute is 8/19. Cold and prepared results remain separate; preparation is
reported outside the prepared timer and prepared results do not replace cold.
All-row no-slower and broad V4 outperformance are not met. Preserve this
honestly unfavorable result.

Exact bundle is `3a3a46f7...1be61`, execution source `9c21d6e7...dd021`,
native `efcc147b...6feab`, plan `97c82ceb...d1c5`, formal identity
`a540cadf...afba`. Deterministic evidence and twin are byte-identical at
`e06d49dd...c04d07` (634 payloads / 282,708,427 payload bytes). A local
independent audit rehashed 634/634 payloads with zero mismatch, verified all
464 workers and 75,216 leaf traversal receipts, and reran the independent
recount with semantic equality.

Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5776_v9_rtx4000ada_real_scale_v2_v4_result_20260814.json`,
`history/internal_docs/goal5776_v9_rtx4000ada_real_scale_v2_v4_technical_report_20260814.md`,
`history/internal_docs/self_review_goal5776_v9_rtx4000ada_real_scale_v2_v4_result_20260814.md`,
and
`history/internal_docs/call_for_review_goal5776_v9_rtx4000ada_real_scale_v2_v4_result_20260814.md`.

Preserve v5/v6/v7 terminal zero-worker lineages. v5 found and repaired a real
V4 triangle repeated-any-hit correctness defect; v6 was a bundle/validator
version mismatch; v7 was a post-seal `.pyc` import-order failure. v8 was
rejected locally and never executed. Do not call Claude. Do not start a
repair, rerun, new POD, universal/no-slower/author/RT-silicon/production/public
or submission claim from this result. Goal5776 measurement is complete; V4
performance development remains open.

## Critical current override: Goal5776 final pre-POD double-check found v4 terminal syntax defect; exact v5 is the sole locally ready candidate (2026-08-14)

The strict final double-check found that bundle v4 (`6836a631...e33a3d`)
was not executable: `goal5776_target_real_scale_functional_prepare.py`
contained a missing closing parenthesis.  The existing tests had exercised
helper behavior without compiling the real target functional entrypoint, so a
POD would have failed before completing the 126 functional paths and before
formal worker zero.  Bundle v4 is terminal and must never execute.

The syntax is fixed and the exact coverage hole is closed by compiling all
eight execution-facing scripts from the target-prepare test.  Bundle v5 and
twin are byte-identical at `9cb85dbb...67ed4c`; exact source is
`83c89734...05e98`.  The source-manifest delta from v4 has exactly four files:
the syntax repair, the execution-entrypoint compile regression test, the
bundle-version declaration and the exact target admission gate.  No
application algorithm, native/CUDA/OptiX code, data, lifecycle, timer,
schedule or statistic changed.

On the exact clean v5 source: all 35 Goal5776 scripts parse, all eight real CLI
entrypoints reach `--help`, target-prepare tests pass 5/5, the Goal5776 suite
passes 75/75 both in the workspace and clean extraction, and the 619-file
source manifest passes.  A Linux CPython 3.12 offline wheelhouse is staged at
`history/internal_docs/goal5776_linux_cp312_wheelhouse_v2_20260814.tar.gz`
(`a2172435...9b520e`); OptiX 9 headers remain `7fae86ce...ebee54`.

Durable result and strict self-review are
`history/internal_docs/goal5776_amendment_a2_zero_worker_syntax_repair_and_final_pre_pod_readiness_20260814.json`
and
`history/internal_docs/self_review_goal5776_amendment_a2_zero_worker_syntax_repair_and_final_pre_pod_readiness_20260814.md`.
The operational sequence is pinned in
`history/internal_docs/goal5776_pod_execution_runbook_v5_20260814.md`.

There is no known local pre-POD blocker, but no POD is currently authorized.
Prepare remains create-only and must run 75 tests plus 126 untimed real paths.
The 464-worker/34-row formal matrix requires a second exact owner authority
binding the prepared source/native/target/runtime/plan identities.  The
registered conservative formal budget is 5.7945 hours; reserve a ten-hour POD
window and at least 20 GB free storage.  Do not call Claude.  Do not claim a
favorable V4 result: the frozen expectation is that many or all rows may remain
slower, and Goal5769 cold 1/26 plus Goal5774 prepared 0/26 remain immutable.

## Critical current override: Goal5774 prepared V2-direct/V4 result is 0/26 (2026-08-13)

The exact v13 candidate completed one owner-directed RTX 4000 Ada prepared
V2-direct/V4 matrix: 208/208 workers, 208 unique parent PIDs, and 624/624
activation/registered calls are exact-output correct and behaviorally
true-OptiX with one exact source/native/prepared/target/formal identity. V3 was
not run. The ratio is V2-direct/V4, so greater than one favors V4. All 26
independent rows fail the median >=1 no-slower gate, and every bootstrap CI is
wholly below one. The median range is 0.0195777944--0.9289288422. Prepared
all-row no-slower is decisively not met.

Exact executed source is `2cf2e101...98dc`; native is `190deccb...4711`;
prepared identity is `0bb89863...4306`; formal identity is
`3ab5c6af...66fe`. Deterministic evidence archive and twin are
`66cc3cf8...fc73` (264 payloads / 37,109,245 payload bytes; zero mismatch).
Primary evaluation and the independent raw recount match exactly, and a local
recount of the copied raw bytes is byte-identical.

Preserve two zero-worker create-only failures: the fresh POD initially lacked
Numba, then the target harness resolved a venv Python symlink back to the
system interpreter. Both were environment-readiness defects, not scientific
results. The bundle/scientific bytes did not change. The formal matrix used no
repair, retry, resume, replacement, timing reuse, row dropping or relabeling.
It was owner-directed and internally reviewed; no external preexecution review
is claimed.

Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_formal_result_20260813.json`,
`history/internal_docs/goal5774_v13_rtx4000ada_prepared_v2_v4_formal_technical_report_20260813.md`,
`history/internal_docs/self_review_goal5774_v13_rtx4000ada_prepared_v2_v4_formal_result_20260813.md`,
and
`history/internal_docs/call_for_review_goal5774_v13_rtx4000ada_prepared_v2_v4_formal_result_20260813.md`.
Do not call Claude. Do not repair, rerun, start another POD, or claim V4
no-slower/speedup, cold replacement, deployment amortization, full-paper-data
performance, author performance, RT-silicon utilization, production, public or
submission readiness before owner-controlled review. Goal5769 cold V2/V4
subset remains immutable at 0/13.

## Critical current override: Goal5774 V2-direct/V4 pre-POD readiness complete (2026-08-13)

V3 is outside the current critical path. Goal5774 compares only the strongest
eligible V2-direct true-OptiX backport with V4 restricted-callback true-OptiX
over nine applications / thirteen representative prepared semantic lanes. The
inputs are frozen application-contract fixtures, not full paper datasets.

The sole candidate is deterministic bundle v13 and twin at
`8a2d177a4...4cccb`; portable source is `5af5e184...b1246`. Clean Windows
extraction passes 13/13 Goal5774 and 272/272 broad V4 tests. Clean Home GTX1070
create-only prepare passes 17/17 fixed-radius proof cases and 78/78 exact,
behaviorally true-OptiX activation/measured-shape calls, with 39/39 V2/V4
input/output matches. Exact Home execution source is `b8ad2502...276bf`, native
`ecf94d8a...92cb3`, prepared identity `ca912385...48640`, and formal identity
`9b87f08e...36473`. Zero formal workers and zero registered formal timings have
run. Evidence v2 is `70820095...28384` (33 payloads / 41,105,304 payload bytes,
zero mismatch, byte-identical twin).

The 208-worker modern-RTX matrix is not yet authorized. Next action requires
one ordinary modern RTX endpoint for create-only prepare. After exact target
source/native/prepared/formal identities are copied locally, a second exact
owner authorization is required before worker zero. Do not call Claude. Do not
run V3, enlarge to full paper datasets, repair/tune, or claim V4 speed/no-slower,
deployment amortization, author performance, stock-v2.14, silicon utilization,
production, public or submission readiness. Goal5769 cold evidence remains
immutable and prepared results cannot replace it.

## Critical current override: V4 Goals5748--5768 strict pre-POD self-audit blocks Goal5768 v9 (2026-08-12)

The strict cross-goal self-audit preserves the scientific and functional
results of Goals5748--5768, but rejects the current Goal5768 v9 Stage-A
execution gate. `scripts/goal5768_target_prepare.py` accepts any 64-character
`owner_returned_external_review_sha256`; it does not hash an actual review or
absorption artifact, verify P0/P1, bind the review to exact bundle v9, or
distinguish Stage-A recommendation from Stage-B authorization. The current
test suite attacks only an empty string. This is a P0 governance defect: do
not execute bundle v9 until an append-only successor makes the authority
file-backed, content-bound and adversarially tested.

The same audit finds a P1 portability/toolchain conflict: Goal5749 froze
Python 3.12.3, Numba 0.65.1, NumPy 2.2.6, llvmlite 0.47.0, CUDA 12.8 and
OptiX 9.0, while later results record NumPy 2.4.4 and CUDA 12.0 without an
append-only toolchain amendment. Bundle v9 carries no pinned wheels/debs and
does not pin/probe CuPy or an exact driver. It also does not enforce exact
test cardinalities. No POD is authorized by the audit.

Durable audit artifacts are
`history/internal_docs/self_review_v4_goals5748_5768_project_delivery_and_pre_pod_audit_20260812.md`,
`history/internal_docs/v4_goals5748_5768_project_delivery_audit_20260812.json`,
and
`history/internal_docs/call_for_review_v4_goals5748_5768_project_delivery_and_pre_pod_audit_20260812.md`.
Do not call Claude. Owner controls external review. Preserve the immutable
Goal5753 held-out failure and Goal5768 original 0/13 hard stop.

## Critical current override: Goals5763--5768 externally approved; exact Goal5768 v9 awaits owner Stage-A authorization (2026-08-12)

The owner-returned unified external review at attachment SHA-256
`60afe13582bb266cac04c0fd1f2d5d1f36ff0b208870e12c269b2d6feae2be5d`
approves Goals5763--5768 at P0=0/P1=0/P2=1. It independently verified that
the thirteen successor front doors are real Paper-reproduction-app whole-app
programs rather than semantic fixtures, import no evaluation/controller code,
enforce identical outputs, and use symmetric cold-complete timers with the
comparator outside. It confirmed the strongest frozen X-HD cell-MBR V2,
explicit pre-timing Particle V2/V3 backports, RayJoin V3's independence from
V4 M5, behavioral true-OptiX admission, independent recount and two distinct
owner decisions for paid work.

The original Goal5768 0/13 hard stop remains immutable and approved as the
correct negative readiness result. The successor deterministic bundle v9
`18a1f3ea946c17691e8af5162fc5181be8df64ff66b31b04045f104118d35bcb`
is the sole local pre-POD candidate. Local evidence/twin is
`24a149cf1e6b719897728aa70dcc4036524d04b1a6ad4f3b761a9ddc143c5e57`
(21 payloads / 10,769,194 payload bytes). Clean v9 validation is 205/205.

The review recommends, but does not authorize, at most one separately
owner-authorized create-only modern-RTX Stage-A prepare: fresh native, 39
untimed functional lanes, zero formal workers and zero registered timings.
The 312-worker Stage-B formal matrix is explicitly not preapproved and needs a
second exact owner authority after the prepared/target/plan/cost identities
exist. Do not call Claude. Do not start a POD without the owner's exact Stage-A
command. No V4 performance, no-slower/outperformance, author, stock V2/V3,
full-paper-dataset, RT-silicon, cross-GPU, production/public or submission
claim is authorized.

Normalized review, structured absorption and closure are
`history/internal_docs/review_goals5763_5768_v4_completion_owner_returned_external_20260812.md`,
`history/internal_docs/goals5763_5768_owner_returned_external_review_absorption_20260812.json`
and
`history/internal_docs/goals5763_5768_postreview_closure_20260812.md`.

## Critical current override: Goals5763--5768 local program complete; Goal5768 hard-stops performance POD (2026-08-12)

Owner-authorized continuous local Goals5763--5768 are complete and await one
combined owner-controlled external review. Goal5763/M5 adds generic verified
grouped-event reduction with RayJoin and Polygon Set Jaccard consumers.
Goal5764/M6 adds content-bound hierarchy-frontier composition with RT-BarnesHut
and a non-paper coverage consumer. Goal5765 reruns nine applications / thirteen
**representative semantic** lanes under one Home source/native (13/13 exact and
behaviorally true-OptiX). Goal5766 clean-rematerializes a portable RC without
`.codex` or prebuilt native. Goal5767 supplies a narrow installable 4.0.0rc1 API,
tutorial/security/coverage docs and isolated wheel proof.

Goal5768 found a binding hard stop: the existing nine-app evidence is
representative semantic execution, not nine complete application performance
front doors. Eight app trees have no direct V4 import; Particle Tracking lacks
frozen V2/V3 comparators and a complete timer. The M1 RayDB/Triangle functional
geometries encode already-derived events/counts and must never be timed as the
paper algorithms. Mechanical result: 13/13 representative functional lanes,
0/13 formal V2/V3/V4 performance-eligible. No performance plan/bundle, formal
worker, registered timing or POD exists.

Authoritative Goal5768 result/report/self-review/CFR are
`history/internal_docs/goal5768_v2_v3_v4_performance_readiness_result_20260812.json`,
`history/internal_docs/goal5768_v2_v3_v4_performance_readiness_technical_report_20260812.md`,
`history/internal_docs/self_review_goal5768_v2_v3_v4_performance_readiness_20260812.md`
and
`history/internal_docs/call_for_review_goals5763_5768_v4_completion_and_performance_hard_stop_20260812.md`.
Deterministic evidence/twin is `b88785c4...b8a1d` (12 payloads / 73,132
bytes). Current V4-pattern tests pass 191/191. Do not call Claude. Do not open a
POD or claim nine-app end-to-end completion/performance. Next material work is
application-owned V4 frontdoor integration and exact V2/V3/V4 comparator/timer
freeze; it requires new owner direction after the combined review.

## Critical current override: Goal5767 usable V4 research RC complete; Goal5768 pre-POD performance freeze active (2026-08-12)

Goal5767 exposes a narrow `rtdsl.v4` public authoring API at version
`4.0.0rc1`, an executable CPU semantic quickstart, V4 front page, tutorial,
API reference, security model, nine-app coverage and V3 migration guide. The
public surface contains no arbitrary Python/Numba/PTX/provider escape hatch.
An AST audit finds zero application/publication identity dispatch in V4 product
control flow.

The sole portable candidate is v6 `50e37b1d...1955c` (source
`f6afb259...6ceff`). In a new clean directory it passes 20 modules / 186 tests,
all documentation links, exact quickstart IR/ABI/semantics, offline wheel build,
isolated installation and installed-package quickstart. Source pre/post hashes
match. The source-delta audit proves zero changes to existing V4 execution
modules and no native change relative to Goal5766. Five preliminary candidates
are preserved; none used a GPU/POD or registered performance timing.

Deterministic evidence/twin is `69536600...71e30` (35 payloads / 10,765,340
payload bytes). Authoritative result/report/self-review are
`history/internal_docs/goal5767_v4_usable_release_surface_result_20260812.json`,
`history/internal_docs/goal5767_v4_usable_release_surface_technical_report_20260812.md`
and `history/internal_docs/self_review_goal5767_v4_usable_release_surface_20260812.md`.

Goal5768 is active. It must first audit whether each frozen paper lane has a
genuinely comparable V2/V3/V4 complete endpoint; missing comparable endpoints
must fail closed rather than be fabricated. Then it may freeze and dry-run only
the eligible modern-RTX cohort, with row-local statistics, no compensation and
separate owner/external-review gates before POD. No performance result or POD is
authorized.

## Critical current override: Goal5766 portable V4 RC complete; Goal5767 usability/documentation audit active (2026-08-12)

Goal5766 packages the exact Goal5765 nine-app source as deterministic portable
RC v3 `ac6ae68e...b9808`, with a byte-identical twin, no private `.codex`
dependency and no prebuilt target native. A clean Home Linux extraction in a
new `/tmp` root rebuilt native `0c6e912e...99891`, passed the complete V4 suite
180/180, and reran all nine Paper Apps / thirteen paper lanes: 13/13 exact and
13/13 behaviorally true-OptiX under one source/native identity. The
route-independent returned-raw recount is `f16c270a...b74f`. There are zero
registered performance timings and Pascal is not claimed as RT-silicon use.

Portable v1 and v2 were rejected locally before GPU use because their clean
audits found missing frozen test authorities; neither lineage is a functional
or performance result. The sole candidate is v3. Deterministic evidence/twin
is `ddeb2045...3b0d` (69 payloads / 57,768,580 payload bytes). Authoritative
result/report/self-review are
`history/internal_docs/goal5766_portable_v4_release_candidate_result_20260812.json`,
`history/internal_docs/goal5766_portable_v4_release_candidate_technical_report_20260812.md`
and `history/internal_docs/self_review_goal5766_portable_v4_release_candidate_20260812.md`.

Goal5767 is active: turn the verified compiler into a comprehensible usable
research release surface with a narrow public API, executable tutorial,
security model, nine-app coverage, migration guidance, front-page claim
hygiene and mechanically checked documentation/audit rules. No POD,
performance, modern-RTX, production, public-release or submission claim is
authorized.

## Critical current override: Goal5765 nine-app single-identity functional closure complete; Goal5766 portable RC active (2026-08-12)

Goal5765 reran the frozen nine-Paper-App, thirteen-paper-lane V4 inventory from
one exact Home execution source and one native library. All 13 paper lanes are
exact and behaviorally true-OptiX; three real non-paper second-consumer lanes
also pass, for 16/16 raw lanes. Exact source is `883785d7...e2486`, native is
`3e19b8c8...c4dcf`, and the route-independent integrated recount is
`5cfc41f2...2271`. The full V4 suite passes 180/180 and the Goal5757 successor
freeze chain passes. Deterministic evidence/twin is `bf5aa26a...8feb` (70
payloads / 55,484,646 payload bytes). No performance timing was registered.

Goal5753's held-out Particle Tracking failure remains immutable and was not
relabelled. Current particle coverage derives from the later Goal5756
built-in-triangle capability. Five partial integration lineages exposed missing
fixture/app-contract files in the minimal M6 subset; all were rejected before
the final source freeze and final M0--M6 rerun. No product/native repair or POD
occurred.

Authoritative local result/report/self-review are
`history/internal_docs/goal5765_nine_app_single_identity_result_20260812.json`,
`history/internal_docs/goal5765_nine_app_single_identity_technical_report_20260812.md`
and `history/internal_docs/self_review_goal5765_nine_app_single_identity_20260812.md`.
Goal5766 is active: construct a deterministic portable V4 release candidate,
clean-extract it, rebuild a target native and rerun the nine-app/13-lane gate
without `.codex` or ambient workspace dependencies. No POD or performance is
authorized.

## Critical current override: Goals5763/M5 and 5764/M6 complete locally; Goal5765 integration active (2026-08-12)

Goal5763 implements app-neutral grouped-event reduction over verified OptiX
producer rows and the existing checked Numba/CUDA grouped reducer. RayJoin M4
point-location events and Polygon Set Jaccard M2 broad-phase events are two
real consumers. Final Home evidence is 2/2 exact and behaviorally true-OptiX,
and both lanes use the device grouped reducer. Product source is
`2bfc0e43...dac1`, Home native is `3e19b8c8...c4dcf`, final raw result is
`6f36e276...a423`, independent recount is `00536dad...711`, and deterministic
evidence/twin is `878c4926...ecd7` (19 payloads / 19,402,162 payload bytes).

Goal5764 implements an app-neutral verified hierarchy-frontier composition over
the existing true-OptiX aggregate-hierarchy family, with closed
`aggregate_count` and `inverse_square_scalar_sum` reducers, compiler-derived
visit bounds, complete behavioral receipts and content binding for every
semantic hierarchy/topology column. RT-BarnesHut and a real non-paper hierarchy
coverage application are two consumers. Final Home evidence is 2/2 exact and
behaviorally true-OptiX. Product source is `a5421dae...42b8`, final raw result
is `dda1992f...19fc`, independent recount is `f2897402...26b`, Home native is
the same `3e19b8c8...c4dcf`, and deterministic evidence/twin is
`640c49e8...78cf` (19 payloads / 19,656,628 payload bytes). The strict
self-review rejected a preliminary same-shape-only proof and required content
hashes before the final Home rerun. No performance claim exists.

Goal5765 is now the active local goal: run the frozen nine-paper-app,
thirteen-lane representative matrix under one exact final V4 source/native
identity, independently recount it, and preserve the historical Goal5753
held-out failure without relabelling it. No POD or performance is authorized.

## Critical current override: Goal5762/M4 externally approved; Goals5763--5768 owner-authorized locally until POD boundary (2026-08-12)

Owner attachment `6e5fa0a...481bd` approves Goal5762 at P0=0/P1=0. It
independently verifies exact signed-46-bit integer SoS, conservative outward
projection at the 46-bit boundary, 3/3 exact behavioral-OptiX lanes,
route-independent broad-phase recount and the machine-recorded X-HD
semantic-only boundary. Goal5762 is closed at exact scope.

Normalized review, absorption and closure are
`history/internal_docs/review_goal5762_owner_returned_external_20260812.md`,
`history/internal_docs/goal5762_owner_returned_external_review_absorption_20260812.json`
and `history/internal_docs/goal5762_postreview_closure_20260812.md`.

The review itself blocks M5+, POD and broader claims. The owner separately
authorizes continuous Goals5763--5768 local work until the first genuine POD
boundary, with strict internal self-review for every goal and no intermediate
external review. Do not call Claude. Do not execute POD or registered modern-
RTX performance without a final combined owner-returned review and exact owner
authorization.

## Critical current override: Goal5762 V4 M4 exact-predicate / witness composition complete; owner-controlled review required (2026-08-12)

Goal5762 implements one app-neutral typed layer that composes verified V4
OptiX candidate producers with three closed partners: deterministic global
nearest witness, signed-46-bit exact directed point-location SoS, and exact
segment-pair SoS plus grouped counts. Candidate rows are not final authority.
The product owns conservative outward-rounded segment and vertical-ray AABB
projections; an independent verifier rebuilds those projections and both full
RayJoin broad phases from exact inputs. No native family or prior product
module changed, and no app/publication dispatch or arbitrary user reducer was
added.

Final Home GTX1070/CC6.1 evidence is 3/3 exact and 3/3 behaviorally true-OptiX,
with five successful/complete launches, 19 raygen invocations and zero failed,
incomplete, unbound, pending or session-error state. Source archive is
`661aa0a5...71584`, native `3e19b8c8...c4dcf`, raw result
`e638359b...e9d5d`, recount `10375ba4...3e7ac`; deterministic evidence/twin is
`e132649a...dad083` (26 payloads / 23,169,075 payload bytes). M1--M4 focused
tests pass 37/37 and the Goal5757 successor chain passes.

Preserve all development lineages: the missing-PYTHONPATH local invocation,
single-use executable replay failure, wrong endpoint-SoS fixture expectation,
and the preliminary 3/3 result rejected as final until projection became
compiler-owned. The X-HD lane closes only the representative exact semantic
contract via the frozen audit's sphere-nearest fragment; do not claim the V4
route is the paper cell-MBR physical algorithm. CPU exact refinement is not
RT-core work. GTX1070 is behavioral OptiX evidence, not modern RT-silicon or
performance evidence.

Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5762_m4_exact_predicate_witness_result_20260812.json`,
`history/internal_docs/goal5762_m4_exact_predicate_witness_technical_report_20260812.md`,
`history/internal_docs/self_review_goal5762_m4_exact_predicate_witness_20260812.md`
and
`history/internal_docs/call_for_review_goal5762_m4_exact_predicate_witness_20260812.md`.
External review is owner-controlled; do not call Claude. Do not start M5,
POD, performance, a full-nine-app claim, production, public release or
submission. Frozen representative progress is 10/12 paper lanes (11/13 with
the held-out lane); this is not full application migration.

## Critical current override: Goal5761/M3 owner-returned external review approved; Goal5762/M4 separately owner-authorized (2026-08-12)

Owner attachment `4aff6b6f...c91b9b9` approves Goal5761 at P0=0/P1=0:
generic compiler-owned prepared multi-round spatial composition, 2/2 exact and
behaviorally true-OptiX representative Home contracts, one persistent GAS per
owner with RTNN refits, RT-DBSCAN 54 exact edges recomputed from 58 broad-phase
candidates, and route-independent recount.  The reviewer independently
confirmed the immutable Goal5757 RTNN prose conflicts with its pinned executable
oracle and accepts the append-only strict-open `(query,item,rank,distance²)`
correction.  Goal5761 is closed at exact scope.

Normalized review, absorption and closure are
`history/internal_docs/review_goal5761_owner_returned_external_20260812.md`,
`history/internal_docs/goal5761_owner_returned_external_review_absorption_20260812.json`
and `history/internal_docs/goal5761_postreview_closure_20260812.md`.
The review itself blocks M4+, performance/POD, full nine-app, modern RTX/RT
silicon, production, public and submission claims.  After absorbing the review,
the owner separately commanded completion of the next goal, thereby authorizing
Goal5762/M4 only.  Do not call Claude.

## Critical current override: Goal5760/M2 owner-returned external review approved; M3 remains blocked (2026-08-12)

Owner attachment `7be9de2b...c7f56d` approves Goal5760 at P0=0/P1=0:
generic capacity-bounded U32-pair relation emission, two frozen LibRTS lanes,
one real Polygon Set Jaccard authored-case broad-phase, 3/3 exact and
behaviorally true-OptiX, whole-result device overflow rejection, full-U32 item
ID through verified attribute 0, route-independent recount and the append-only
Goal5759→Goal5760 freeze chain.  The reviewer independently rehashed the exact
24-payload evidence archive and accepted all four preserved development
lineages.

Normalized review, structured absorption and closure are
`history/internal_docs/review_goal5760_owner_returned_external_20260812.md`,
`history/internal_docs/goal5760_owner_returned_external_review_absorption_20260812.json`
and
`history/internal_docs/goal5760_postreview_closure_20260812.md`.
Goal5760 is closed at exact scope.  The review does not authorize a successor.
Do not start M3 or later batches, performance/POD, complete LibRTS or Polygon
Set Jaccard migration, modern RTX/RT-silicon, production, public, Paper-App
closure or submission work without separate explicit owner direction.  Do not
call Claude.

## Critical current override: Goal5760/M2 generic bounded relation emission complete; owner-controlled review required (2026-08-12)

Goal5760 closes M2 at generic capability and Home functional scope.  One
app-neutral verified custom-AABB target emits a capacity-bounded two-column U32
relation with lexicographic canonical order, explicit duplicate policy and
whole-result fail-closed overflow.  The exact callback/typed-schema/target/ABI/
contract are rebound before one-shot execution; the product/native path has no
application, publication, dataset or batch dispatch and accepts no arbitrary
reducer or serializer.

On Home Linux GTX1070/CC6.1 the two frozen LibRTS contracts and the existing
Polygon Set Jaccard authored-case broad-phase are 3/3 exact and 3/3
behaviorally true-OptiX.  Each uses two successful/complete launches; all seven
roles execute across the cohort, with zero failed/incomplete/unbound/pending
state.  An independent recount importing no product/compiler/runtime reproduces
all canonical rows and duplicate counts.  A device capacity=1 attack observes
overflow and rejects the complete result; no partial relation is authority.
There are zero registered performance timings and no POD.

The final native is `0f576c10...86af9`; raw result is `8dfb4e58...0c491`.
Deterministic evidence/twin is `2383e9b2...4be59` (24 payloads / 6,979,866
payload bytes).  Goal5757's freeze verifier now follows an append-only Goal5759
to Goal5760 successor-manifest chain and passes; Goal5759 itself is unchanged.
Focused Goal5757--5760 tests pass 22/22 and the explicit V4 M0--M2 regression
set passes 134/134.

Preserve four non-performance development lineages: pre-overflow, pre-recount,
pre-saturation and pre-real-consumer.  True device work caught that arbitrary
U32 item IDs cannot use OptiX's seven-bit hit-kind channel; the final target
uses verified intersection attribute 0 and a fixed zero hit kind.  The final
non-LibRTS lane derives boxes from the real existing application fixture, but
does not claim the full Jaccard continuation migrated.

Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5760_m2_bounded_relation_emission_result_20260812.json`,
`history/internal_docs/goal5760_m2_bounded_relation_emission_technical_report_20260812.md`,
`history/internal_docs/self_review_goal5760_m2_bounded_relation_emission_20260812.md`
and
`history/internal_docs/call_for_review_goal5760_m2_bounded_relation_emission_20260812.md`.
Do not call Claude.  External review is owner-controlled.  Do not start M3,
performance/POD, full Paper-App migration, modern-RTX/RT-silicon, production,
public or submission work before owner-returned review and explicit direction.

## Critical current override: Goal5759/M1 owner-returned external review approved; M2 was owner-authorized separately (2026-08-12)

Owner attachment `ad4d715e...dacd56c` approves Goal5759 at P0=0/P1=0/P2=2:
3/3 exact, 3/3 behaviorally true-OptiX, raw native callback counters
11/2,224,385/444,877, route-independent recount, byte-unchanged Goal5758
product and exactly two native replacements.  Approval is limited to generic
target capability and frozen consumer fixtures; it does not authorize M2+,
performance, complete Paper Apps, modern RTX or RT silicon.  The owner then
explicitly commanded completion of the next goal, thereby starting Goal5760/M2
only.  Do not reinterpret the Goal5759 review as automatic later-batch approval.

## Critical current override: Goal5759/M1 Home target closure complete; owner-controlled review required (2026-08-12)

Goal5759 closes Goal5758's explicit target-execution gap for the three frozen
M1 consumer fixtures.  On clean-current Home Linux GTX1070/CC6.1, RayDB keyed
I64, Triangle RT-1A2 plain U64 and Triangle RT-2A1 weighted U64 are 3/3 exact
and 3/3 behaviorally true-OptiX.  Device any-hit counts are respectively 11,
2,224,385 and 444,877; Triangle outputs equal the com-dblp author count
2,224,385.  There are zero registered performance timings.

The approved Goal5758 semantic product is unchanged.  One app-neutral trusted
wrapper/compiler/runtime and one generic built-in-triangle native ABI implement
the device target.  The Goal5757 freeze now accepts an explicit successor
manifest with exactly two pinned native replacements; all other 17 core files
remain frozen.  Windows Goal5750--5759 tests pass 137/137; clean Home Goal5758/
5759 target tests pass 11/11.  Exact final native is `c5e6ba1b...abb6f6`.

Reject the earlier correct-output Home run derived from a Goal5756 base tree;
it is not final evidence.  The final run was rebuilt and rerun from the current
Goal5758 tree.  Deterministic evidence/twin is `5355c4be...2056a` (43 payloads /
7,626,792 bytes).  CFR is
`history/internal_docs/call_for_review_goal5759_m1_home_true_optix_closure_20260812.md`.
Do not call Claude.  External review is owner-controlled.  Do not claim full
Paper App migration, performance/no-slower, RT-silicon, M2+, POD, production,
public or submission status from Goal5759.

## Critical current override: Goal5758/M1 local capability complete; owner-controlled review required (2026-08-12)

Goal5758/M1 implements an app-neutral successor built-in-triangle metadata and
checked-reduction contract shared by RayDB and Triangle Counting.  The three
closed algebras are checked keyed-I64 sum with explicit identical-event dedup,
checked U64 sum, and checked U64 product-sum.  RayDB's real bounded-Q21 fixture
including duplicate physical delivery matches both an independent oracle and
the frozen app reference; both Triangle reducer fixtures reproduce the
published com-dblp count 2,224,385.  Product identity-dispatch hits are zero.

The frozen Particle `TypedPhysicalSchemaV1` and V1 ABI remain byte-identical at
`cdc279c1...77345` and `3f4be4d9...74fb5`; the complete Goal5757 core-freeze
verifier and Goal5750--5758 suite pass (131/131).  Deterministic evidence and
twin are `history/internal_docs/goal5758_m1_local_evidence_20260812.tar.gz`
and `..._twin_...`, both `1227d0ad...e1cb0` (19 manifest payloads / 233,873
payload bytes).  Independent raw recount is 3/3 with zero manifest mismatch.

This is local semantic/compiler-contract completion only.  The canonical
contract is non-executable and all three lanes remain
`GPU_TARGET_EXECUTION_PENDING`, not `SUPPORTED_NOW`.  No native/GPU/POD or
performance work occurred.  External review is owner-controlled; do not call
Claude.  Do not start GPU execution, M2--M6, Paper App/data/native changes,
performance, production/public/submission work before owner-returned review and
explicit direction.  Authoritative report/self-review/CFR are
`history/internal_docs/goal5758_m1_generic_triangle_metadata_and_checked_reducers_technical_report_20260812.md`,
`history/internal_docs/self_review_goal5758_m1_generic_triangle_metadata_and_checked_reducers_20260812.md`,
and
`history/internal_docs/call_for_review_goal5758_m1_generic_triangle_metadata_and_checked_reducers_20260812.md`.

## Critical current override: Goal5757 externally approved; Goal5758/M1 explicitly authorized (2026-08-12)

The owner-returned external review attachment `03761dca...fdb2` approves the
exact Goal5757 local coverage audit and migration design at P0=0/P1=0/P2=1.
It independently reproduced 9 Paper Apps / 13 lanes / 1 supported / 0
partner-only / 12 missing generic semantic, including 2 frontend, 3 typed-
schema and 7 canonical-plan failures.  Fragment plans were not promoted; even
the earlier sphere capability remains only an RTNN fragment.  Particle
Tracking is a known-regression supported lane, not a Goal5753 held-out pass.
The P2 binds the coverage vocabulary to these frozen thirteen lanes and not an
arbitrary-application theorem.

Normalized review and structured absorption are
`history/internal_docs/review_goal5757_owner_returned_external_20260812.md`
and
`history/internal_docs/goal5757_owner_returned_external_review_absorption_20260812.json`.
Do not call Claude.  Goal5757 itself did not auto-authorize M1--M6.  The owner
subsequently explicitly instructed completion of the next goal, which starts
Goal5758/M1 only: generic built-in-triangle metadata channels plus typed
checked reducers shared by RayDB and Triangle Counting.  Preserve Particle
front/back orientation exactly; no app/publication dispatch, Paper-App/data
patch, POD, performance, author, silicon, production/public/submission claim,
or automatic M2+ work is authorized.

## Critical current override: Goal5756 trusted built-in-triangle runtime and Home GPU evidence complete; owner-controlled external review required (2026-08-11)

Goal5756 closes the exact target-GPU P2 left by the owner-returned Goal5755
review. The Goal5755 typed physical schema and live triangle-orientation
authority now drive a real trusted OptiX built-in-triangle GAS/SBT/pipeline.
Four verified Numba roles (make-ray, closest-hit, miss, finalize) execute in a
single composed module; the native ABI has no user intersection-program
parameter and any-hit is disabled.

On Home Linux GTX1070/CC6.1, one front ray, one back ray and one miss are exact
against the independent CPU Callback-IR interpreter. The device directly
reports primitive indices `[0,0,null]`, hit kinds `[0xFE,0xFF,null]` and exact
binary32 barycentrics. Role counters are `[0,3,0,0,2,1,3]`; all launch status
is clean. The receipt proves one successful/complete/context-bound OptiX
launch, three raygen invocations, a nonzero traversable and zero failed,
incomplete, pending or session state.

Strict self-review rejected an earlier working lineage because the runtime
still accepted raw composed PTX. The final runtime requires a trusted-compiler
issued, process-local, single-use `VerifiedTriangleExecutable`; raw/serialized
PTX, copied authority and replay all fail closed. A second pre-launch property
error is also preserved. Final local Goal5750--5756 tests pass 113/113 and
Home Goal5755/5756 tests pass 26/26.

Final deterministic evidence and twin are
`history/internal_docs/goal5756_home_final_evidence_20260811.tar.gz` and
`history/internal_docs/goal5756_home_final_evidence_twin_20260811.tar.gz`,
both `848c0aef...f2955c7` (18 manifest payloads, zero recount mismatch). Exact
source is reconstructible from base commit `c061dbdc...` plus overlay
`a1e7fd2c...86baa7`; exact native is `9c9ffd91...bc5cd`.

Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5756_builtin_triangle_runtime_and_home_result_20260811.json`,
`history/internal_docs/goal5756_builtin_triangle_runtime_and_home_technical_report_20260811.md`,
`history/internal_docs/self_review_goal5756_builtin_triangle_runtime_and_home_20260811.md`
and
`history/internal_docs/call_for_review_goal5756_builtin_triangle_runtime_and_home_20260811.md`.
External review is owner-controlled; do not call Claude. Goal5753 remains a
failed held-out exam and Particle Tracking is not passed. No POD, performance,
RT-silicon, modern-RTX, held-out generalization, production, public or
submission claim is authorized.

## Critical current override: Goal5755 typed physical schema and CPU/reference planner complete; GPU runtime remains open (2026-08-11)

Goal5755 implements the Goal5754 design at local product-type and
CPU/reference scope. Callback IR v1 remains the legacy custom-AABB seven-role
contract; the geometry-indexed built-in-triangle successor is explicitly v2
and cannot pass the old public verifier. The new product module
`src/rtdsl/v4_typed_physical_schema.py` supplies closed typed buffer,
hit-channel and GAS schemas, strict digest revalidation, owner/device/stream/
epoch/count binding checks, target-f32 triangle validity checks, external
triangle-orientation authority and a sole-canonical-template reference planner
whose output is always `executable=False`.

The Goal5754 P2 is mechanically addressed. Tests directly rehash frozen
Goal5753 author `optixQueryKernel.cu` at `e67c909d...`, bind OptiX front/back
hit kinds 0xFE/0xFF, confirm the author's front-selected/back-neighbor and
back-selected/front-neighbor rule, and differentially check adjacent cell
identities using the independent rational tetra oracle `61a724c4...`.
Neutral field IDs prove that names do not authorize semantics. Missing,
swapped or forged authorities, wrong SDK constants, channel types, role/index
bindings, ownership/counts and triangle geometry fail closed.

Focused Goal5755 tests pass 19/19; Goal5750--5755 regressions pass 106/106.
No native, OptiX runtime, Paper App, GPU, timer, data or performance path was
changed. Goal5753 remains a failed held-out exam and is not retroactively
passed. Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5755_typed_physical_schema_and_reference_planner_result_20260811.json`,
`history/internal_docs/goal5755_typed_physical_schema_and_reference_planner_technical_report_20260811.md`,
`history/internal_docs/self_review_goal5755_typed_physical_schema_and_reference_planner_20260811.md`
and
`history/internal_docs/call_for_review_goal5755_typed_physical_schema_and_reference_planner_20260811.md`.
The closed manifest is
`history/internal_docs/goal5755_typed_physical_schema_and_reference_planner_manifest_20260811.json`.

External review is owner-controlled; do not call Claude. Goal5755 authorizes no
successor, GPU/POD/native runtime work, Particle Tracking completion,
performance, generalization, production, public or submission claim. A future
Goal5756 requires separate owner authorization and must implement the trusted
built-in triangle GAS/wrapper against the exact Goal5755 authority, then obtain
local/Home functional evidence before any paid target or performance work.

## Critical current override: Goal5754 externally approved; Goal5755 locally authorized with winding/front-back P2 as hard gate (2026-08-11)

Owner-returned review attachment `34ed60f7...437e57` approves Goal5754 at
design and machine-checked contract scope, P0=0/P1=0/P2=1. It independently
confirmed the app-neutral geometry-indexed topology, 18 focused attacks, zero
product/native/app drift and the anti-laundering rules. Its 86/87 broad run had
one environment-only error: a Goal5753 `git show` provenance test in a mounted
non-git sandbox.

The sole P2 is now a hard Goal5755 gate: triangle winding and front/back
adjacency value mapping must be an explicit typed authority and must be
differentially tested against a CPU oracle and author semantics; field names or
self-authored serialized data are not authority. Normalized review, absorption
and closure are
`history/internal_docs/review_goal5754_owner_returned_external_20260811.md`,
`history/internal_docs/goal5754_owner_returned_external_review_absorption_20260811.json`
and `history/internal_docs/goal5754_postreview_closure_20260811.md`.

The owner subsequently authorized completion of Goal5755. Authorized local
scope: product TypedPhysicalSchema types, strict parsing/reverification,
geometry-indexed role topology, CPU/reference canonical planner and adversarial
tests. Do not call Claude. No GPU/POD, native/runtime/GAS implementation,
application correctness, behavioral true-OptiX, performance, renewed
generalization, production, public or submission claim is authorized.

## Critical current override: Goal5754 typed physical schema/GAS ABI design complete; implementation not started (2026-08-11)

Goal5754 completes the design-only response to the Goal5753 held-out P0. The
application-neutral `TypedPhysicalSchemaV1` binds verified Callback IR to typed
geometry, buffers, hit channels, GAS/SBT ownership, target/provider identity
and a geometry-indexed role topology. Initial canonical families are
`custom_aabb` and `builtin_triangle`. Custom AABB requires restricted bounds
and intersection. Built-in triangle forbids both because OptiX owns bounds and
triangle intersection; it supplies compiler-owned primitive index, front/back
hit kind and optional barycentrics. Admission maps to exactly one canonical
template or fails closed; this is not a cost optimizer or app-name dispatch.

The machine model and design-only validator pass 18/18 focused tests; the full
Goal5750--5754 local set passes 87/87 with the repository's existing
`PYTHONPATH=src`. No product, native or Goal5753 application/evidence byte was
changed, and no GPU/POD worker exists. Goal5753 remains a failed held-out exam
forever; future repair makes it only a known regression. A renewed
generalization claim requires a newly frozen core and a newly selected unseen
application.

Authoritative design/result/report/self-review/CFR are
`docs/v4/typed_physical_schema_and_gas_abi_design.md`,
`history/internal_docs/goal5754_typed_physical_schema_design_result_20260811.json`,
`history/internal_docs/goal5754_typed_physical_schema_design_technical_report_20260811.md`,
`history/internal_docs/self_review_goal5754_typed_physical_schema_design_20260811.md`
and
`history/internal_docs/call_for_review_goal5754_typed_physical_schema_and_gas_abi_design_20260811.md`.
External review is owner-controlled; do not call Claude. Goal5754 authorizes no
Goal5755 implementation, product/native/app change, GPU/POD, application
correctness, behavioral true-OptiX, performance, production, public or
submission claim.

## Critical current override: Goal5753 external review approves honest held-out failure; V4 end-to-end generalization refuted (2026-08-11)

The owner-returned review at attachment SHA `354c4c79...b860e9`
independently reproduces the Goal5753 selection
(`Wang2022AnGP::particle_tracking`, index 13/17), 106-second post-freeze NIST
beacon timing, broad universe, 283-file zero-drift core seal, exact Goal5752
native, author triangle/front-back requirements, prelaunch physical-template
rejection, rational oracle and 39-payload evidence archive. Verdict: approve
Goal5753 as a complete honest held-out failure, P0=1 architectural, P1=0,
P2=2 as disclosed.

The restricted frontend and ABI partially generalize, but the frozen physical
layer remains analytic-sphere-only. Current V4 end-to-end held-out
generalization is refuted. Particle tracking has zero GPU launch and is not a
V4 correctness or behavioral true-OptiX result. It may be a future known
regression, but must never be relabelled as a held-out pass after repair; a
future held-out claim requires a new core freeze and newly selected unseen app.

Normalized review, absorption and closure are
`history/internal_docs/review_goal5753_owner_returned_external_20260811.md`,
`history/internal_docs/goal5753_owner_returned_external_review_absorption_20260811.json`
and `history/internal_docs/goal5753_postreview_closure_20260811.md`.
Do not call Claude. The review authorizes no Goal5754 implementation,
core/native repair, POD, performance, production, public or submission claim.
Any successor begins with a separately authorized app-neutral typed
geometry/GAS/schema ABI design.

## Critical current override: Goal5751 formal seven-role OptiX runtime complete at Home functional scope; owner review required (2026-08-11)

Goal5751 now lowers verified Goal5750 Callback IR through a canonical ABI into
seven compiler-generated Numba C-ABI PTX leaves, composes them with one trusted
OptiX wrapper, materializes/reloads the exact PTX through an RTDL-owned provider
cache and behaviorally executes all seven roles. Home GTX1070 device output is
exactly equal to the CPU semantics: `[(3,4.0),(UINT32_MAX,100.0)]`; device role
counters `[3,2,3,2,1,1,2]` are all nonzero. The receipt records one successful
complete-context OptiX launch, two raygen invocations and zero failed,
incomplete, unbound, pending or session-error state. Exact native is
`aa0146a7...b28b97`; exact composed PTX is `0b4e81f0...e74e16`; generated
provider key is `792d5eec...d61676`.

A wrong-bounds device program fails closed with stable code `0xffff000a`, one
intact atomic first-error claim and no accepted output. The device tranche found
and corrected three load-bearing cross-layer defects: miss-stage ray-state
ownership, nonconfluent closest-hit overwrite after canonical any-hit, and
wrapper/effect field order differing from canonical ABI order. These failures
must remain disclosed. The first cache-integrated evidence adapter also stopped
before launch on a wrong dataclass field and remains a zero-launch lineage.

The combined Goal5749–5751 suite passes 72/72. Durable result/report/self-review/CFR are
`history/internal_docs/goal5751_formal_callback_runtime_and_home_device_result_20260811.json`,
`history/internal_docs/goal5751_formal_callback_runtime_and_home_device_technical_report_20260811.md`,
`history/internal_docs/self_review_goal5751_formal_callback_runtime_and_home_device_20260811.md`, and
`history/internal_docs/call_for_review_goal5751_formal_callback_runtime_and_home_device_20260811.md`.
Evidence/twin are byte-identical at `f414f640...eb11b6` (32 payloads /
7,072,275 payload bytes).

This closes Goal5751 only at one compiler-owned analytic-sphere physical
template and Home functional scope. Bounds executes and is checked against the
admitted GAS but does not yet construct arbitrary GAS. GTX1070 is behavioral
OptiX evidence, not RT-core-silicon evidence. No app, held-out generalization,
modern RTX, performance, production, public or publication claim is authorized.
External review is owner-controlled; do not call Claude. Goal5752 requires new
owner direction after review.

## Superseded current override: Goal5751 T3 seven-leaf trusted PTX composition complete; OptiX runtime still open (2026-08-11)

Goal5751 now composes all seven real formal Numba PTX leaves through a closed,
deterministic product compiler component. Home Linux preflight binds exact
roles/symbols/digests and equal PTX version/target/address size, removes seven
exact wrapper externs and eight exact inert Numba environments, and emits a
deterministic composed PTX digest. Target/digest drift, unknown or ambiguous
externs, duplicate/cross symbols, external dependencies, referenced environment
state, environment-cardinality drift and stale role bindings fail closed.

The load-bearing Goal5749 compatibility delta is bounded: each formal leaf may
remove exactly `1 + transitive reachable verified helpers` inert environments,
as derived from verified IR. PTX cannot self-declare this number. The reference
roles have counts 1/1/1/1/1/1/2; `finalize` is the sole helper consumer.

Durable result/receipt/self-review are
`history/internal_docs/goal5751_t3_seven_leaf_ptx_composer_result_20260811.json`,
`history/internal_docs/goal5751_home_seven_leaf_composer_preflight_20260811.json`
and
`history/internal_docs/self_review_goal5751_t3_seven_leaf_ptx_composer_20260811.md`.
The preflight wrapper is a grammar fixture, not an OptiX module. Goal5751 is
not complete: trusted wrapper generation, real OptiX pipeline, atomic status,
CPU/device differential and behavioral receipts remain. Do not call Claude.
No POD, application, performance, production, public or submission claim is
authorized.

## Superseded current override: Goal5751 T2 formal IR-to-Numba PTX bridge complete; OptiX runtime still open (2026-08-11)

Goal5751 now has a canonical seven-role Callback ABI and deterministic trusted
IR-to-Python/Numba lowering. On Home Linux (GTX1070 CC6.1, Python 3.12.3,
Numba 0.65.1, NumPy 2.4.4), all seven Goal5750 reference roles compile in
isolated child processes to audited PTX ISA 8.0 targeting `sm_61`; every PTX
external-symbol set is empty. The original restricted-Python source/callable,
globals, defaults and overloads never enter Numba. Compiler-generated helper
bodies are registered only as internal device functions. Runtime-checkable
faults use the explicit RTDL status/out ABI; checked integer arithmetic not yet
lowered fails closed rather than wrapping silently.

Durable compiler receipt and internal result/review are
`history/internal_docs/goal5751_home_formal_numba_ptx_preflight_20260811.json`,
`history/internal_docs/goal5751_t2_formal_numba_codegen_result_20260811.json`
and
`history/internal_docs/self_review_goal5751_t2_formal_numba_codegen_20260811.md`.
Goal5751 is not complete: seven-leaf trusted composition, dynamic OptiX
pipeline, atomic first-error behavior, CPU-interpreter/device differential and
behavioral traversal receipts remain. Do not call Claude. No POD, application
migration, performance, production, public or submission claim is authorized.

## Superseded current override: Goal5751 T1 canonical Callback ABI complete locally (2026-08-11)

Goal5751 has begun with a material local tranche, not a GPU claim. New
`src/rtdsl/v4_callback_abi.py` compiles exact `VerifiedCallbackProgram` input
into a deterministic seven-role ABI: recursive scalar layouts, typed SoA
device-pointer columns for read-only views, tagged effect variants, stable
symbols/nonces and an explicit per-launch status contract. Serialized ABI is
not self-authorizing; consumers must recompile the exact verified IR and
require full artifact equality.

Any-hit now stops before code generation unless an external authority binds
the exact IR/effect/delivery/proof identities and a recognized proof kind. A
manifest enum alone is rejected. Geometry authority is rechecked. Ten focused
tests and the 13 Goal5750 tests pass (23/23 combined). Durable result and
self-review are
`history/internal_docs/goal5751_t1_canonical_callback_abi_result_20260811.json`
and
`history/internal_docs/self_review_goal5751_t1_canonical_callback_abi_20260811.md`.

This is only T1. Goal5751 remains open. Next implement deterministic trusted
formal-IR-to-Python source lowering for this exact ABI, compile only generated
source in the isolated Numba child, then prove PTX/composer/wrapper/status and
CPU/device differential behavior. Do not call Claude. No GPU/POD,
application migration, performance or production claim is authorized.

## Critical current override: Goal5750 externally approved; decode P2 closed (2026-08-11)

The owner-returned review attachment at `bd9a42b...0703058` approves Goal5750
at P0=0/P1=0/P2=1 after independently matching all packet hashes, reproducing
33/33 tests and exercising hostile frontend/decoder/linkage/geometry attacks
with zero fail-open. Accepted scope is backend-neutral Callback IR,
independent verifier, strict JSON reverification, external geometry authority
and deterministic CPU semantics.

The sole P2 was uniform error observability: some malformed enum/shape inputs
raised bare `ValueError`/`KeyError`. Goal5750 Amendment A1 closes it by wrapping
all such hostile decode failures as coded `CallbackVerificationError` while
preserving existing structured codes. Successor IR SHA is `1ac7c79d...78336`;
successor test SHA is `d5fcca40...08f3a`; combined tests remain 33/33. Original
Goal5750 result/evidence bytes are immutable and not relabelled.

Durable review, absorption and closure are
`history/internal_docs/review_goal5750_owner_returned_external_20260811.md`,
`history/internal_docs/goal5750_owner_returned_external_review_absorption_20260811.json`
and
`history/internal_docs/goal5750_amendment_a1_uniform_decode_errors_closure_20260811.md`.
Do not call Claude. Goal5751 remains a separate owner-directed successor; PTX,
OptiX integration, application migration, GPU/POD, performance and production
claims are not implied by Goal5750 approval.

## Critical current override: Goal5750 formal Callback IR complete; owner review required (2026-08-11)

Goal5750 is complete at backend-neutral restricted-Python Callback IR,
independent fail-closed verifier and deterministic CPU-interpreter scope. Exact
implementation lives in `src/rtdsl/v4_callback_ir.py`,
`src/rtdsl/v4_callback_frontend.py` and
`src/rtdsl/v4_callback_interpreter.py`; the normative contract is
`docs/v4/callback_ir_v1.md`. All seven OptiX roles, closed types/effects,
bounded control/helpers/resources, strict numeric faults, strict JSON
reverification and semantic receipts are implemented.

Two internal P1 findings were corrected before freeze: helper frames now carry
frozen constants plus formal arguments only, and verified geometry now requires
an out-of-program authority binding exact source SHA, proof SHA, contract name
and rounding policy. A manifest cannot certify itself. Any-hit confluence and
general IR CPU/device differential equivalence remain explicit P2 gaps.

Targeted Goal5750 plus Goal5749 regression tests pass 33/33. Deterministic
evidence and twin are `38c7af0d...12f49b` (11 payloads / 183,783 bytes, zero
manifest mismatch). Authoritative result/report/self-review/CFR are
`history/internal_docs/goal5750_formal_callback_ir_verifier_cpu_interpreter_result_20260811.json`,
`history/internal_docs/goal5750_formal_callback_ir_verifier_cpu_interpreter_technical_report_20260811.md`,
`history/internal_docs/self_review_goal5750_formal_callback_ir_verifier_cpu_interpreter_20260811.md`
and
`history/internal_docs/call_for_review_goal5750_formal_callback_ir_verifier_cpu_interpreter_20260811.md`.

External review is owner-controlled; do not call Claude. Goal5751, PTX/Numba
lowering, OptiX integration, application migration, GPU/POD, performance,
production, public and publication claims remain blocked pending separate
owner direction.

## Critical current override: Goal5749 P1 closure externally approved (2026-08-11)

The owner-returned external review at attachment SHA
`0033ec3e...3374cf` approves the Goal5749 linkage/composer closure at
P0=0/P1=0/P2=0. Both prior P1 findings and all three prior P2 items are closed.
The old statement that OptiX 9 rejected ordinary cross-module linking is
withdrawn as confounded: a legal NumbaEnv-stripped two-module Home diagnostic
matches interpreter digest `593a55a1...de436` and is behaviorally true-OptiX
with zero registered timings. It remains diagnostic-only and has no modern-RTX,
performance or production-selection claim.

The trusted single-module composer remains the selected exact Goal5749 PoC
mechanism because it has Home and modern-RTX functional evidence. It is now
explicitly load-bearing compiler work with a reviewed compatibility contract
and a real C++/NVRTC hostile-mutation suite (5/5 fail closed). The accepted
Goal5749 result `c424c633...2683` is immutable and was not rerun, changed,
backfilled, replaced or relabelled. The outer harness remains
`EXECUTED_HARNESS_NOT_INDEPENDENTLY_REVIEWED`.

Durable review, structured absorption and closure are
`history/internal_docs/review_goal5749_p1_linkage_and_composer_closure_owner_returned_external_20260811.md`,
`history/internal_docs/goal5749_p1_linkage_and_composer_closure_owner_returned_external_review_absorption_20260811.json`
and
`history/internal_docs/goal5749_p1_linkage_and_composer_closure_postreview_20260811.md`.
Do not call Claude. Goal5750+, Goal5749-B, performance, optimization,
application migration, arbitrary Python/OptiX coverage, author comparison,
RT-silicon utilization and production/public/submission claims remain blocked.
Goal5750 requires a separate owner-approved plan and must explicitly state the
production linkage mechanism and rationale.

This file is the first-stop guide for Codex or any other coding agent working in
this repository. Read it before making changes, then read the files under
`memory/`.

## Durable Memory Protocol

Important project state must live in repository files, not only in a chat
thread. At the start of a session, read:

```text
AGENTS.md
memory/project-facts.md
memory/architecture.md
memory/decisions.md
memory/progress.md
memory/todo.md
memory/known-bugs.md
memory/roadmap.md
```

At any meaningful handoff or major goal boundary, update the relevant `memory/`
files before stopping:

- `architecture.md`: current system architecture and app/core ownership;
- `progress.md`: what was actually implemented, measured, and verified;
- `decisions.md`: durable architectural or claim-boundary decisions;
- `todo.md`: next concrete work, stale TODO removal, and review debt;
- `known-bugs.md`: recurring failure modes and how to avoid them;
- `roadmap.md`: only when the project direction changes.

Do not treat conversation history as the source of truth when a memory file or
goal report exists. If they conflict, inspect the files and report the conflict.

For long-running paper-reproduction work, this protocol is mandatory rather
than optional. Any fact that would be expensive to rediscover after a new Codex
session must be written into `memory/` or a goal report before handoff:

- current best numbers and their exact regime;
- claim boundaries and forbidden summaries;
- active POD endpoint / wrapper rule;
- next concrete goal and the reasons old alternatives were rejected;
- implemented-but-review-pending status.

Never rely on "the previous chat probably has it" for these items.

## Project Identity

RTDL is a general spatial language/system. Paper reproduction apps are evidence
and pressure tests for the language; they must not turn RTDL core into a
single-paper or single-app codebase.

Core principle:

```text
RTDL core exposes generic spatial/dataflow primitives.
Paper apps own paper-specific inputs, wrappers, comparators, formatting,
tolerances, and claim boundaries.
```

## Current Workstream

No paper-app implementation line is active. LibRTS received an unconditional
external approval for Goals5519-5525 on 2026-07-13 and is closed at `scoped
correctness and system extraction complete`. X-HD is a completed historical
line at its owner-approved same-input directed-HDResult boundary.

Closed LibRTS record:

- Goal5453 pins the PPoPP 2025 paper, author repository/commit, Zenodo artifact,
  and a five-row local CPU reference fixture;
- Goal5454 runs that same tiny input through pinned author RTSpatial/OptiX and
  RTDL OptiX on local Linux. Both report count `5`; RTDL also emits all five
  exact expected rows. The author example is count-only, so author pair-row
  equality is not claimed;
- Goal5455 adds a direction-discriminating range-contains fixture: correct
  indexed-box-contains-query count is `5`, reversed direction is `2`, and both
  author/RTDL OptiX report `5`;
- Goal5456 adds predicate-discriminating range-intersects: intersects count is
  `8` versus contains `5`; author/RTDL counts match and RTDL emits all 8 native
  rows;
- Goals5457-5459 add an app-neutral mutable AABB index with stable IDs and
  atomic snapshot rebuilds, validated on CPU and Linux OptiX. It explicitly
  does not claim native incremental mutation;
- Goal5460 runs the same insert/update/delete/insert/clear sequence through the
  patched-author public API and RTDL OptiX. Both produce counts
  `[2,1,0,1,0]` and append ID `2`. The author uses native GAS/IAS update while
  RTDL rebuilds snapshots, so execution/performance parity is not claimed;
- Goals5461-5462 add generic OptiX sparse-slot native refit for pure Update.
  Same-host GTX1070 diagnostics measure about `12.62x` at 4,096 boxes and
  `15.63x` at 65,536 boxes versus RTDL full snapshot rebuild. Insert/Delete/
  Clear still rebuild; these are RTDL system microbenchmarks, not paper or
  author-performance results;
- Goal5463 closes the sparse-refit review amendments: the call-for-review now
  reports the evidence-backed `12.62x` / `15.63x`, Linux hardware fault
  injection verifies old records/GAS recovery after a post-update fault, and a
  rollback failure poisons the prepared handle so later operations fail closed.
  Goals5461-5463 are externally reviewed and approved;
- Goals5464-5465 add a bounded same-input PIP gate from the exact author AE
  source chain. Author and RTDL OptiX both report `4` polygon-refined hits; RTDL emits
  all four expected rows, while the fixture has `5` MBR-only candidates.
  These goals are implemented / external review pending;
- Goals5466-5467 add a Level-B representative PIP gate with 64 public-source
  Block Group polygons and 100K points from the pinned author generator. The
  unmodified author, instrumented author comparator, and RTDL app-compatible
  route all produce 71,626 rows; complete pair-row hashes match. Standard RTDL
  PIP semantics produce 71,624 and that difference remains disclosed. These
  goals are implemented / external review pending;
- Goals5468-5469 pin the paper/source Ray-Multicast mechanism and add a generic
  `partitioned_traversal` Python reference contract. A Contact-Manifold-style
  broad-phase test proves complete pair coverage and non-LibRTS reuse. Native
  OptiX execution and runtime speedup are not implemented; one bounded POD
  spike is authorized only after strict review;
- the pinned author artifact needs a disclosed one-line update-buffer fix:
  `updateInstanceAccel` allocates `tempUpdateSizeInBytes` but originally passes
  `tempSizeInBytes` to OptiX;
- no LibRTS paper performance claim exists. The next recommended milestone is
  strict review of Goals5468-5469, followed by the bounded generic OptiX
  partitioned-traversal POD spike if approved;
- until a POD is available, use `lestat@192.168.1.20` for Linux functional
  validation. Treat its GTX 1070 as smoke hardware, not paper-performance
  evidence;
- Embree is explicitly out of scope for the entire LibRTS campaign. Do not
  build, test, compare, or report Embree evidence. HIPRT is also inactive.

Historical X-HD status:

Key status:

- bounded X-HD same-input value reproduction is complete and externally
  reviewed through Goal5126;
- generic nearest/witness/reduction extraction is complete through Goals5127
  and 5128;
- full paper reproduction is not complete because exact paper datasets are not
  available;
- Level B Stanford Dragon/HappyBuddha evidence is now the strongest current
  representative line;
- Goal5186 runs author `hd_exec` on the full public Dragon/HappyBuddha pair and
  matches the paper-branch author-log HDResult;
- Goal5187 runs the RTDL scalable all-source route on that same public pair and
  matches the author HDResult;
- Goal5188 records the full-public phase-boundary matrix and refuses a
  performance ratio because author internal timing, author process wall, RTDL
  route, and RTDL total are different denominators;
- Goal5189/5190 tested generic seed strategies; local-grid is faster than
  grid-branch-bound on the full-public Level-B route;
- Goal5191 raises the generic native inline-nearest threshold to consume all
  frontier rows and adds a fail-closed empty-frontier passthrough; current best
  Level-B route wall is about `3.65s`;
- Goal5192 adds optional native inline-nearest telemetry; the same route
  performs about `1.24B` inline point-distance evaluations inside OptiX payload
  code, so the remaining native collector floor is real inline work rather than
  Python continuation or row materialization;
- Goal5193 tested a generic bounded grid-cell seed and intermediate inline
  thresholds; both matched author HDResult but did not beat local-grid +
  inline512, so the current default remains unchanged;
- Goal5194 fixed native inline-nearest pruning to use the updated payload
  current best instead of only the initial query seed; full-public Level-B route
  still matches author HDResult, warmed route wall is about `3.46s`, and
  telemetry inline point evaluations drop from about `1.24B` to `0.40B`;
- Goal5195 moved the same payload-current-best prune into the native
  intersection stage before `optixReportIntersection` for inline-nearest /
  no-pruned-row mode; full-public Level-B route still matches author HDResult,
  warmed route wall is about `2.6s`, and native frontier / inline time is about
  `0.93-0.94s`;
- Goal5196 changed the generic grid-cell seed occupied-cell lookup from
  repeated binary search to a dense encoded-cell position table with fallback
  for local-grid, grid-cell-budget, and grid-branch-bound seed helpers;
  full-public Level-B route still matches author HDResult, dense local-grid
  route wall is about `2.26s`, and dense budget / branch-bound controls do not
  beat it;
- Goal5197 carries intersection-computed `min_sq` into any-hit via OptiX
  attributes and computes row-only distances lazily; full-public Level-B route
  still matches author HDResult and remains about `2.25-2.28s`, so this is a
  generic cleanup / neutral optimization rather than a new speedup headline;
- Goal5198 measures grid-shape telemetry and keeps 32^3 as the current default:
  24^3 fails the empty-frontier route at capacity 0, while 48^3/64^3/128^3
  match but are slower despite reducing inline point evaluations;
- Goal5199 tests a generic trace-tmax bound in the native OptiX cell-MBR
  traversal and records a no-go: correctness still matches, but inline cell hits
  and point evaluations are unchanged and route wall does not improve; the
  temporary code change was reverted;
- Goal5200 tests an explicit experimental generic native CUDA executor for the
  local-grid seed and records a no-go: correctness, POD build, focused tests,
  and a small native call pass, but same-POD full-public route wall worsens
  (`2.436s` native CUDA vs `2.258s` auto/Numba), so the default remains
  auto/Numba;
- Goal5201 instruments the generic native 3-D cell-MBR frontier collector and
  records that route-level `frontier_rows ~= 0.920s` contains native frontier
  total `~= 0.600s`, native OptiX launch / inline-nearest work `~= 0.377s`, and
  native accel build only `~= 0.0004s`;
- Goal5202 adds generic packed coordinate matrix reuse for point-column front
  doors; the full-public Level-B route still matches author HDResult and the
  no-timing route wall is about `2.027s` versus the Goal5200 auto/Numba control
  at about `2.258s`;
- Goal5203 changes the X-HD app-owned public PLY input front door to load
  directly into NumPy coordinate matrices; the full-public Level-B route still
  matches author HDResult and the route wall is about `1.238-1.239s`;
- Goal5204 makes the generic max-nearest reducer linear for finite distances
  by sorting only the maximum-distance tie set; the full-public Level-B route
  still matches author HDResult and the route wall is about `1.17-1.18s`;
- Goal5205 changes the app-owned public ASCII PLY input loader to use NumPy
  column loading instead of Python per-line tuple parsing; the same route still
  matches author HDResult, `load_full_inputs` is about `0.68s`, full gate total
  is about `2.06s`, and route wall remains about `1.16-1.17s`;
- Goal5206 records a first-use vs same-process warm diagnostic: one-shot route
  remains about `1.16-1.17s`, while a near-identical second case in the same
  process is about `0.61s`; this is a regime diagnostic only and must not
  replace the fresh headline;
- Goal5207 adds an explicit app-owned route warmup protocol:
  `--route-warmup-source-limit` records warmup separately and excludes it from
  measured summary statistics; current all-source warm measured route is about
  `0.626s` after a reported warmup case total of about `1.389s`;
- Goal5208 tested lower native inline-nearest thresholds under the explicit
  warmup protocol and records a no-go: 384 is noise-level and worsens the full
  warmup-including run, while 256/128 are slower because frontier rows and
  continuation work return; keep `max_inline_points=512`;
- Goal5209 tested static generic cell primitive ordering by point count and
  records a no-go: `point-count-asc` moves route median by only about 1.4ms and
  does not improve case-total median, while `point-count-desc` is slower; keep
  native cell order;
- Goal5210 disables closest-hit in the generic cell-MBR frontier OptiX raygen
  because that pipeline has no closest-hit program; correctness is preserved,
  but same-POD repeats show no material route or OptiX-launch speedup, so treat
  it as neutral semantic cleanup rather than a performance win;
- Goal5211 implements a generic global-bound early-break experiment for
  directed-Hausdorff/max-nearest reductions. It preserves the Goal5186 author
  HDResult and improves the Level-B Dragon/HappyBuddha route (`~0.849s` fresh
  route, `~0.362s` explicit-warm route median). It remains review pending and explicit: early-aborted per-source
  witnesses may be approximate, so this is a max-nearest/directed-HD contract,
  not a default for generic exact nearest-witness APIs.
- Goal5212 removes all-source subset materialization in the full-public runner;
  with Goal5211 enabled, fresh full total including load is about `1.531s`, and
  explicit-warm measured case total is about `0.288s`. This is app-runner
  hygiene, not native route speedup.
- Goals5272-5277 move Figure 11 memory from vague "missing accounting" into a
  status-bearing decision: author-side Figure 11 memory logs are extracted,
  RTDL has bounded native telemetry for OptiX GAS output bytes, but author `WL`
  is in/miss queues and author `WL Heavy Peak` is a heavy-cell offload peak.
  Current RTDL `WL` is generic frontier row-table capacity and has no
  author-like heavy offload peak, so `same_denominator_author_figure11=false`
  and Figure 11 remains not reproduced.
- Goal5279 implements the first generic system primitive for that Figure 11
  gap: `heavy_offload_worklist_numpy_columns` plus generic active/miss/deferred
  row schema and queue/peak telemetry at CPU-reference level. It is
  implemented but review pending, and native/POD peak telemetry still does not
  exist.
- Goal5280 adds a non-X-HD retry/backlog consumer for that generic worklist
  helper; it is implemented but review pending.
- Goal5281 adds the first native/POD v2 telemetry ABI for generic offload
  frontier rows. POD evidence shows both v1 and v2 symbols are exported and a
  tiny native route reports schema-v2 telemetry with six offload rows and
  96 peak queue bytes. It is implemented but review pending, and still does not
  reproduce X-HD Figure 11 or authorize author memory parity.
- Goal5282 maps that generic v2 telemetry into author-shaped X-HD fields:
  OffloadingSize row-count shape is available, and an author-width WL Heavy
  Peak candidate can be computed, but same-denominator Figure 11 remains false
  because RTDL measured queue bytes use 64-bit id pairs and RTDL WL is not the
  author's in_queue + miss_queue. It is implemented but review pending.
- Goal5283 closes the current Figure 11 line as
  denominator-not-aligned after native mapping. There is a shape-only offload
  candidate, but it is not a paper Figure 11 row and no memory ratio is
  authorized. Reopen Figure 11 only with a denominator-aligned generic native
  worklist or external review accepting a different memory question.
- Goal5284 maps the author paper-branch `run_all/auto_tune` logs for Figure 9.
  The logs contain 1814 `auto_tune` records over 907 pairs, with exactly two
  observed config labels and `Running.num_points_per_cell = 8` throughout.
  They are useful author-log semantics evidence, but they do not contain a
  multi-value grid-size sweep or paper-selected grid-size choices, so Figure 9
  remains not reproduced.
- Goal5285 audits the pinned author paper-branch Figure-9-like source/scripts:
  `effective_autoune.py` expects four auto-tune variants and saves
  `auto-tune.pdf`, but current `run_all/auto_tune` logs contain only two
  variants. `logs/train` sweeps exist, but they are a different denominator and
  must not be promoted to Figure 9 reproduction without an externally reviewed
  mapping.
- Goal5286 audits all pinned author branches for the missing Figure 9 variants:
  `paper` still has only the same two `run_all/auto_tune` configs and a
  checked-in `auto-tune.pdf`, while `main` and `hybrid` have no Figure-9-like
  logs/scripts/PDF. A checked-in PDF is evidence, not a reproducible RTDL/author
  denominator.
- Goal5287 closes the current Figure 9 line as
  `figure9_closed_current_line_author_denominator_missing`: the plot script
  expects four variants, current logs provide two, main/hybrid do not recover
  the missing variants, the checked-in PDF is not a reproducible denominator,
  and training sweeps require an externally reviewed mapping before use.
- Goal5288 audits Figure 5 timing denominators: author run_all logs cover 2535
  records / 507 complete pairs across BraTS, geo, and graphics, but current RTDL
  evidence lacks BraTS and geo full gates and author `Running.AvgTime` /
  `ReportedTime` is not the same denominator as RTDL route/process wall. Figure
  5 remains not reproduced and no speedup ratio is authorized.
- Goal5289 runs a bounded same-POD Figure 5 graphics probe on the currently
  available Dragon -> AsianDragon scaled-1e-3 candidate. The POD is reachable
  through the wrapper, author `hd_exec` runs, and RTDL runs on the same POD, but
  author X-HD/LB=256 returns `0.06545527279376984` while the RTDL exact route
  returns `0.06536787240753439` (`matched_value=false`). This candidate is a
  no-go for Figure 5 performance comparison and no ratio is authorized.
- Goal5290 performs the cheaper author-only value precheck for the same Figure
  5 graphics pair. The paper log target is `0.06536811590194702`; the available
  POD unscaled AsianDragon author run returns `52.4535`, and the scaled-1e-3
  variant returns `0.0654553`. Neither matches, so do not spend RTDL timing on
  this candidate again unless exact input provenance or a new value-matched
  variant appears.
- Goal5291 consolidates the Dragon -> HappyBuddha Figure 5 graphics candidate.
  Paper log `HDResult=0.12572969496250153`, author rerun
  `0.12572988867759705`, and RTDL route `0.12572988629271128` match within
  `1e-6`, so this is the strongest current Figure 5 graphics Level-B
  value-matched candidate. It is still not exact paper dataset reproduction,
  not the full Figure 5 matrix, and no author-vs-RTDL performance ratio is
  authorized because timing denominators differ.
- Goal5292 audits Figure 7 load-balance / heavy-cell offload source and logs.
  The pinned author source has `run_lb.sh` and `draw_lb.py`, and checked-in
  `run_all/rt_gpu` logs have LB=256 profiling-style fields, but the checked-in
  `lb_comparison` matrix has zero JSON files and there is no LB=0 counterpart.
  Figure 7 remains not reproduced; RTDL comparison should not start until an
  author `lb=0`/`lb=256` matrix is regenerated or a separately named Level-B
  diagnostic is approved. Goal5292 is implemented / review pending.
- Goal5293 audits Figure 8 radius-growing strategy source and logs. The pinned
  author source has `run_radius_tuning.sh` and `draw_tune_radius.py`, aligned on
  add/double/adaptive strategies and geo/graphics categories, but checked-in
  `logs/tune_radius` has zero JSON records and the paper-branch `run_all`
  mapping has no Figure 8 radius-strategy records. Figure 8 remains not
  reproduced; RTDL comparison should not start until the author
  add/double/adaptive matrix is regenerated or a separately named Level-B
  diagnostic is approved. Goal5293 is implemented / review pending.
- Goal5294 audits Figure 10 scalability / overlap source and logs. The pinned
  author source has `run_scalability.sh` and `draw_scalability.py`, aligned on
  size and translate/overlap sweeps over `all_nodes.wkt`, but checked-in
  `logs/scalability` has zero JSON records. The paper-branch `run_all` mapping
  has 4535 workload-family records, but no Figure 10 scale/overlap subset
  labels or overlap diagnostics. Figure 10 remains not reproduced; RTDL
  comparison should not start until the author size/translate matrix is
  regenerated or a separately named Level-B scalability/overlap diagnostic is
  approved. Goal5294 is implemented / review pending.
- Goal5295 checks whether the current POD can regenerate the missing Figure
  7/8/10 author matrices. The POD wrapper preflight succeeds and the author
  build exists, but `/local/storage/shared/HDDatasets` is missing, along with
  all required graphics/geo/all_nodes inputs. Only a partial Dragon/Asian
  temporary subset is present. Therefore exact author regeneration for Figures
  7/8/10 is blocked on the current POD; the POD is usable, but the author
  dataset root is absent. Goal5295 is implemented / review pending.
- Goal5296 uses that partial temporary Dragon/Asian input only as a separately
  named Level-B author-side load-balance diagnostic. Author `hd_exec` returns
  identical HDResult for `lb=0` and `lb=256` (`52.453487396240234`), but on
  this single run `lb=256` is slower by `Running.AvgTime` (`131.841ms` vs
  `107.254ms`) and process wall (`17.09s` vs `16.25s`) despite reducing
  iteration-3 compared points. This is not Figure 7 reproduction, not RTDL
  comparison, and not a performance ratio. Goal5296 is implemented / review
  pending.
- Goal5297 creates the X-HD dataset acquisition manifest. The current POD is
  usable but lacks `/local/storage/shared/HDDatasets`; local workspace has
  public Stanford graphics candidates for Dragon, HappyBuddha, AsianDragon, and
  ThaiStatuette with recorded hashes. These files can advance Level-B
  same-source graphics diagnostics after upload, but they are not exact paper
  datasets. BraTS, Census/TIGER, and OSM remain acquisition/provenance blocked.
  Recommended next goal: upload missing public Stanford graphics files to POD
  via `scripts/current_pod_ssh.py` and run author-only Level-B graphics value
  prechecks before any new RTDL comparison. Goal5297 is implemented / review
  pending.
- Goal5298 uploads the missing public Stanford graphics files to the current
  POD and runs author-only Level-B graphics value prechecks. Three cases match
  paper-branch author-log HDResult within `1e-6`: Dragon->HappyBuddha,
  ThaiStatuette-scaled->HappyBuddha, and ThaiStatuette-scaled->AsianDragon-
  scaled. Dragon->AsianDragon-scaled remains a no-go (`0.0654552728` vs paper
  log `0.0653681159`, diff `~8.7e-5`). Goal5298 does not run RTDL and does not
  authorize figure reproduction, exact dataset status, or performance ratios.
  Goal5298 is implemented / review pending.
- Goal5299 runs RTDL on the Goal5298 value-matched ThaiStatuette-scaled ->
  HappyBuddha case. Both `cell-mbr-exact-witness` and `cell-mbr-fast-scalar`
  match the author rerun scalar HDResult within `1e-6` (`abs diff ~= 6.3e-9`).
  Exact-witness route wall is about `5.00s` with `per_source_witness_exact=true`;
  fast-scalar route wall is about `1.00s` but has
  `per_source_witness_exact=false` because global-bound early-break leaves most
  per-source witnesses approximate. No author-vs-RTDL ratio, figure
  reproduction, exact dataset status, or author RT-core equivalence is
  authorized. Goal5299 is implemented / review pending.
- Goal5300 runs RTDL on the Goal5298 value-matched ThaiStatuette-scaled ->
  AsianDragon-scaled case. Both routes match the author rerun scalar HDResult
  within `1e-6` (`abs diff ~= 1.1e-8`). On this workload exact-witness is
  faster (`~10.76s` route wall, `per_source_witness_exact=true`) than
  fast-scalar (`~12.51s`, `per_source_witness_exact=false`) because
  fast-scalar produces `~4.66M` frontier rows and spends most time in nearest
  continuation. This is Level-B same-source scalar evidence only; no ratio,
  figure reproduction, exact dataset status, or author RT-core equivalence is
  authorized. Goal5300 is implemented / review pending.
- Goal5301 consolidates non-graphics X-HD dataset provenance. It does not run
  POD, author code, or RTDL code; the blocker is input identity/acquisition.
  Exact paper inputs still require file/hash provenance or deterministic author
  regeneration, not count/Gini matching. BraTS is access-gated, OSM
  Lakes/Parks/AllNodes are public but snapshot/filter/scale blocked, and
  Census/TIGER-like public geo inputs are the best next non-graphics target.
  Goal5301 is implemented / review pending.
- Goal5302 resolves the first Census/TIGER-like geo source plan. Author
  `run_fig5.sh` uses `dtl_cnty.wkt -> uszipcode.wkt` and
  `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` as
  2D WKT inputs with `normalize=false`; the author WKT loader emits polygon
  outer-ring vertices, linestring vertices, and points. Probe-verified
  TIGER2023 candidates exist for national COUNTY and ZCTA520; BG and AREAWATER
  are shard-based from the evidence here. County-ZCTA is the recommended first
  executable Level-B geo candidate. Goal5302 is implemented / review pending.
- Goal5303 creates the first bounded County-ZCTA WKT input artifact using
  ArcGIS name-matched County and ZIP/ZCTA FeatureServer exports. It writes
  one-geometry-per-line WKT files plus hashes and author-loader outer-ring
  point-count estimates. This is Level-B ingestion/conversion evidence only:
  the first County rows are Alabama counties and the first ZIP/ZCTA rows are
  Alaska ZCTAs, so it is not geographic representativeness, exact paper input,
  author/RTDL correctness, Figure 5, or performance evidence. Goal5303 is
  implemented / review pending.
- Goal5304 runs author `hd_exec` on that Goal5303 bounded WKT fixture on the
  current POD. Author ingestion succeeds with `HDResult=65.44752502441406`,
  point counts `38034/50272`, and `Running.AvgTime=6.169ms`. This is
  author-only Level-B ingestion evidence and remains implemented / review
  pending.
- Goal5305 runs RTDL on the same bounded County-ZCTA WKT fixture using the
  generic partner route `directed_max_of_nearest_distance_2d_partner_columns`
  with `partner="triton"` and `triton_strategy="dense_point_nearest_tiled"`.
  It matches the Goal5304 author scalar result: RTDL
  `65.44751976280666` vs author `65.44752502441406`, absolute difference
  `5.2616073986655465e-06 <= 1e-5`, point counts `38034/50272`.
  This is Level-B bounded same-fixture scalar correctness only; no exact geo
  dataset, Figure 5, author RT-core equivalence, performance ratio, or
  full-paper claim is authorized. The initial Numba partner attempt failed on
  this POD due to PTX/JIT compatibility (generated PTX 8.7, available path
  accepts PTX 8.4); treat that as a POD toolchain no-go, not a semantic
  mismatch. Goal5305 is implemented / review pending.
- Goal5306 creates the second bounded geo WKT fixture for
  `USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt` using
  ArcGIS name-matched WaterBodies and BlockGroups FeatureServer exports. It
  requests the first 5 features of each service by OBJECTID and records
  author-loader point-count estimates `124/894`. It is fixture evidence only,
  not exact paper input or Figure 5 reproduction. Goal5306 is implemented /
  review pending.
- Goal5307 runs author `hd_exec` and RTDL on the Goal5306 bounded
  WaterBodies->BlockGroups fixture. It matches the author scalar result:
  RTDL `72.38664516014835` vs author `72.38665008544922`, absolute difference
  `4.925300871150284e-06 <= 1e-5`, point counts `124/894`. This is Level-B
  bounded same-fixture scalar correctness only; no exact geo dataset, Figure 5,
  author RT-core equivalence, performance ratio, or full-paper claim is
  authorized. Goal5307 is implemented / review pending.
- Current geo status: both X-HD Figure-5 WKT pair names now have bounded
  author/RTDL scalar matches, but neither has exact paper input provenance or a
  denominator-aligned performance claim.
- Goal5308 records the geo exact/full-public decision: exact author WKT paths
  are known from paper logs but unavailable locally and on the current POD.
  Paper-log point counts are much larger than the bounded fixtures
  (`9,438,045/43,952,878` for County-ZCTA and
  `22,818,694/52,271,340` for WaterBodies-BG). Figure-5 and exact-input claims
  remain blocked. Goal5308 is implemented / review pending.
- Goal5309 fully probes the four name-matched full-public ArcGIS services for
  author-loader point counts and MBRs. All MBRs match paper logs to <1e-5
  degrees. ZCTA, WaterBodies, and BlockGroups point counts are very close to
  paper logs, but County has `12,477,179` points vs paper `9,438,045`
  (+32.2%), so County-ZCTA cannot be promoted to exact/Figure-5 status.
  WaterBodies-BlockGroups is the strongest full-public geo candidate
  (`+6,129` and `+127` points), but still lacks exact file/hash provenance.
  Goal5309 is implemented / review pending.
- do not repeat lower-threshold, static cell-order, scalar ray-extent, or
  trace-flag tuning without a changed execution model or new evidence, and do
  not prioritize prepared cell-MBR accel-build caching without new evidence.

## Claim Discipline

Never claim:

- full paper reproduction unless exact inputs, author contract, RTDL route, and
  review gates all support it;
- performance parity unless denominator, hardware, dataset, phase boundary, and
  runtime regime match;
- native backend completion when only a reference/front-door route exists;
- app-specific code as a generic RTDL system improvement.

Always distinguish:

- bounded same-input correctness;
- same-source representative correctness;
- exact paper dataset reproduction;
- author internal `Running.AvgTime` / `ReportedTime`;
- process wall time;
- RTDL route time;
- cold process vs warm long-lived process vs prepared replay.

## Important Directories

```text
src/rtdsl/                         RTDL public/system APIs
src/native/                        native backends
tests/                             regression and goal tests
Paper-reproduction-apps/           paper reproduction apps, app-owned wrappers
history/internal_docs/             goal reports, reviews, call-for-review docs
memory/                            durable project memory for future sessions
scripts/                           local/remote helper scripts
```

## Remote POD Rule

Do not use naked SSH for POD work. Use:

```text
py scripts/current_pod_ssh.py --host <host> --port <port> preflight
py scripts/current_pod_ssh.py --host <host> --port <port> exec "<remote command>"
```

The wrapper pins the current POD key:

```text
~/.ssh/id_ed25519_rtdl_codex_current_pod
```

Before declaring a POD broken or blocked, run the wrapper preflight. The recent
Goal5144 failure was caused by using the wrong local SSH key, not by a bad POD.

## Testing Expectations

Prefer focused tests for the touched goal, plus nearby regression tests. Example
for the current X-HD cell-MBR line:

```text
py -m unittest \
  tests.goal5145_dimension_generic_cell_mbr_frontdoor_test \
  tests.goal5144_cell_mbr_backend_assisted_gate_runner_test \
  tests.goal5142_generic_cell_mbr_backend_assisted_frontdoor_test \
  tests.goal5140_generic_cell_mbr_traversal_abi_test \
  tests.goal5139_generic_nearest_state_frontier_api_test \
  tests.goal5138_generic_grid_cell_candidate_api_test
```

On this Windows setup, `py` may print:

```text
Could not find platform independent libraries <prefix>
```

Treat that as noisy environment output if tests still pass.

## Editing Rules

- Use `apply_patch` for manual edits.
- Do not revert user or prior-agent changes unless explicitly asked.
- Keep app-specific paper semantics out of `src/rtdsl` and `src/native`.
- If a report says "implemented; review pending", do not silently upgrade it to
  reviewed/approved.
- Update `memory/progress.md`, `memory/decisions.md`, and `memory/todo.md` at
  meaningful handoff points.
# Critical current override: Goal5777 read-only causal audit complete; Triangle RT-2A1 is the next local target (2026-08-14)

Goal5777 independently reconstructed all 34 Goal5776 rows from 464 raw workers
without importing the formal controller/evaluator/recount.  All registered
ratios reproduce, the split remains 9 pass / 25 fail, and pairwise phase
accounting has exactly zero residual.  Prepared attribution uses only the
registered execute phase; loading/preparation/close remain separately reported
outside the prepared timer.  Nine pass rows are retained as controls.

The failures are not one defect.  Eight of 14 cold failures are principally
located in V4 preparation in at least 6/8 pairs.  The strongest execution-path
signal is Triangle RT-2A1: all three prepared real-scale rows have CIs wholly
below one and V4-minus-V2 median deficits of 0.0845 s, 1.9521 s and 24.4048 s.
Frozen source proves that the V4 weighted partner path performs canonical-ID
device validation plus multiple CuPy max/sum/product scans and synchronization
points, while V2-direct consumes a native weighted scalar summary.  Those
extra operations are source-proven, but their individual seconds and
eliminability are not claimed.

RT-BarnesHut prepared remains a severe measured regression (0.5759, +98.95 ms)
despite the same program bundle, one launch and 32,768 raygen invocations.
Source shows additional V4 full-row copying/hashing/status validation, but no
profiler assigns the measured deficit to those scans; an immediate repair is
therefore blocked pending observation.  Only RayJoin batch0 fails while
batches1-5 are controls, so a global RayJoin patch is rejected.

Durable audit/result/source findings/report/self-review/CFR are under
`history/internal_docs/goal5777_*_20260814.*`; focused tests pass 6/6 and the
audit twin is byte-identical.  Goal5776 and its 9/25 result remain immutable.
The next authorized local work is an app-neutral fused checked-U64 device
reduction design/implementation for the weighted callback path, preserving
canonical IDs, overflow, lifecycle, exact output and behavioral true-OptiX.
No POD, formal matrix, predicted saving, RT-BarnesHut repair or performance/
no-slower/author/silicon/public/production claim is authorized by Goal5777.

# Critical current override: Goal5847 deployable AOT target met (2026-09-05)

Goal5847 is internally technically complete only at
`PASS__GOAL5847_INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`.
Its controlling authority is
`history/internal_docs/goal5847_aot_startup_20260905/GOAL5847_INTERNAL_AUTHORITY.json`;
verify it with
`python3 scripts/goal5847_build_aot_startup_authority.py --verify-stored`.

At clean implementation commit
`f5e337feef6829e063c6aff06f4e8bd6d5466b3b` on one RTX 2000 Ada GPU, the
exact precompiled 4,096-by-4,096 bounded-relation transaction retained 1,024
steady samples per arm and all eight paired complete-process rows. Median
within-block complete-process RTDL/precompiled-PyOptix is `0.229370x`, worst
block `0.258728x`. Pooled steady medians are 299,403 ns and 3,496,252 ns,
ratio `0.085635x`. RTDL maps no NVRTC/compiler module and records zero runtime-
compiler attempts while preserving signed family/provider identity and true
OptiX evidence.

Do not generalize Goal5847. PyOptix's 5.206 s median dependency import
dominates the complete-process result and maps NVRTC even though the harness
does not compile source. After implementation import, RTDL remains `2.504x`
slower by the paired median. First-ever RTDL materialize/build/sign is 94.171 s
and excluded. The steady arms satisfy the same output contract but RTDL uses
generic device semantic compaction while PyOptix returns duplicate raw events
for host canonicalization. Storage page cache is uncontrolled; signing is
test-only; only one relation shape and one GPU generation are measured.
External review, consensus, public/manuscript wording, intrinsic-language,
arbitrary-workload, cross-hardware and production-security claims remain
unauthorized.

# Critical current override: Goal5846 exact warm-cache startup target met; superseded by Goal5847 AOT evidence (2026-09-05)

Goal5846 is internally complete only at
`PASS__GOAL5846_EXACT_WARM_CACHE_FRESH_PROCESS_STARTUP_TARGET_MET__EXTERNAL_REVIEW_PENDING`.
Its controlling authority is
`history/internal_docs/goal5846_relation_startup_20260905/GOAL5846_INTERNAL_AUTHORITY.json`.
On one RTX 2000 Ada GPU, the exact 4,096-by-4,096 bounded-relation task retained
1,024 steady samples per arm and all eight fresh-process paired setup rows. The
median within-block setup-plus-first RTDL/PyOptiX ratio is `0.990957x`, worst
block `1.132343x`; pooled RTDL steady is 364,985 ns versus PyOptiX 3,487,496 ns.
This closes the exact inherited source-compiling PyOptiX warm-cache setup debt
without regressing Goal5845 or adding app-specific engine logic.

Do not generalize Goal5846. First-ever cache fill remains 36.982 s. A separate
unregistered precompiled-PTX, validation-off PyOptiX sensitivity is about
236.415 ms and remains materially faster than RTDL's 577.153 ms formal median.
The cache is logical manifest-bound hit-only, not OS-permission read-only; pod
files were mode 0666. External review, consensus, public/manuscript wording,
cross-hardware claims, arbitrary-workload claims, full process-wall parity, and
precompiled/AOT PyOptiX parity remain unauthorized.

The next performance target is a generic deployable whole-route/AOT artifact:
load a provider-compatible verified executable without first-use leaf compile,
retain exact source/provider/ABI/proof identities and fail-closed mutation
behavior, and compare against a precompiled PyOptiX arm under a new frozen
same-contract experiment. Do not rewrite or pool Goal5846 evidence.
