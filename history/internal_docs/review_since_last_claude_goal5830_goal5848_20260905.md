# External review: RTDL progress since the 2026-08-29 Claude review

Reviewer: Claude, acting as an independent critical reviewer with no prior
RTDL memory.

Review date: 2026-09-05

Target venue: CGO 2027 (submission 2026-09-10)

Review class: adversarial compiler/systems architecture, generality, evidence,
baseline-fairness, and claim-boundary review.

## 0. Review custody record

Captured on the reviewed machine before any analysis:

```text
pwd     = /Users/rl2025/rtdl_v4_restricted_python_design
HEAD    = 5de0e7ec3a48af73b2e645a5ff0edaae9b8c6696
subject = "Define Goal5848 performance closure gates"
author  = Rubao Lee <lee.lestat@gmail.com>, Sat Sep 5 11:55:27 2026 -0400
branch  = codex/cgo-goal5836-handoff
```

Working tree is dirty exactly as the request declares: 53 entries in
`git status --short`, of which 52 are tracked additions/modifications and one
(`tests/goal5848_worker_failure_cleanup_test.py`) is untracked.

```text
git diff HEAD | shasum -a 256
  = 52f185f3d92fffdc792014add5344f593b79fbdd52589a3650a96766350de424
diffstat = 52 files changed, 16040 insertions(+), 30 deletions(-)
untracked = tests/goal5848_worker_failure_cleanup_test.py
```

Modified tracked V4 source in the WIP set is limited to
`src/native/optix/rtdl_optix_core.cpp`, `src/rtdsl/v4_rtdlexe.py`,
`src/rtdsl/v4_aot_cache.py` (new), and
`tests/goal5847_aot_provider_initialization_test.py`. Everything else is new
Goal5848 experiment, script, and test material.

Goals through Goal5847 were read from committed Git objects. Goal5848 was
reviewed as work in progress from the working tree only. No Goal5848
performance statement is authorized anywhere in this review.

Review was read-only with two exceptions that must be recorded:

1. A `git status` invocation left a zero-byte `.git/index.lock`. The reviewing
   shell cannot unlink files, so the lock was renamed to
   `.git/index.lock.stale-cowork` to unblock Git. Please delete that file.
   No repository object, index entry, or working-tree source byte was altered.
2. This report file was created, as Section 14 of the request requires.

No source was repaired, no evidence was rewritten, no authority was
regenerated, no adverse transaction was discarded, and the manuscript was not
touched.

The request specifies `/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python`.
That interpreter is outside the folder exposed to this review and could not be
executed. Focused tests were therefore run with the workspace `python3`
(3.10.12) under `PYTHONPATH=src:.`. Every test result below was obtained that
way and should be reconfirmed on the project's pinned 3.12 environment before
being treated as authoritative.

## 1. Cold-start understanding

**Problem.** A repurposed OptiX computation is not one kernel. It is a protocol
spread over host setup, geometry and acceleration-structure construction,
several device callbacks, payload and attribute conventions, continuation and
status rules, and the specific executable that finally launches. Every
individual fragment can be legal to CUDA, to OptiX, and to the host language
while the assembled protocol is incoherent: a producer and a consumer can
disagree about what an integer slot means, a required role can be missing, a
host can publish a truncated buffer after an overflow, a physical binding can
contradict what the callbacks assume, or the reviewed declaration can be paired
with different bytes at launch. Nothing in the existing toolchain is positioned
to reject those programs, because no existing tool takes the assembled protocol
as its input.

**Proposed contribution.** Move the unit of compilation and admission from the
callback or kernel to the complete cross-role protocol. RTDL accepts callback
bodies in a closed, typed subset of Python that it parses as data and never
imports; lowers them to a typed role-indexed Callback IR; combines that IR with
separately sourced semantic, physical, continuation, target, provider and
executable authorities; discharges five whole-protocol obligations (role-effect
closure, semantic ABI ownership, physical binding, status-gated continuation and
completeness, executable identity) as one obligation set; and only then lowers
admitted leaves through compiler-owned OptiX wrappers into a materialize →
prepare → execute → close lifecycle whose output is status-gated.

**Non-goals.** RTDL does not discover profitable RT mappings, compile arbitrary
Python, cover the OptiX API, prove accepted programs correct, or own the
application's algorithm, geometry construction, predicates, or oracle. The
developer still chooses the ray-tracing formulation.

**Strongest current evidence, in my ranking.**

1. Goal5840's separately implemented target-side checker. It shares no code
   with the implementation, explicitly refuses compiler-produced projections,
   partially evaluates the generated device source against declared role
   semantics, cross-checks role symbols across ABI, wrapper source and compiled
   PTX, and rejects 15 unique frozen mutations. Six preserved failed attempts
   precede it. This is the most credible artifact in the review interval.
2. The preserved adverse performance chain. Goal5842/5843 published RTDL as
   3.13x and 155.21x pinned PyOptix, Goal5844's first transaction failed its own
   target at 2.171x, Goal5846 disclosed an adverse precompiled-PTX sensitivity,
   and Goal5847 published the adverse `2.504242x` post-import result rather than
   the flattering complete-process number. Custody discipline here is real and
   is itself a reviewable contribution.
3. Goal5836's terminal source-fidelity refusal. Acquiring the author artifact,
   finding a material predicate difference, and stopping before input freeze,
   execution, timing, and Paper App promotion is the correct scientific move and
   should be reported as a result.
4. Goal5848's experiment design. Arms B and C are genuinely distinct, timer
   boundaries are symmetric, cache policy is fail-closed on both driver and RTDL
   sides, and the authority builder independently reconstructs the frozen
   preregistration and the exact 80 worker commands.

**Largest open threat, in one sentence.** The headline generality result does
not mean what its label says: the sealed "generic core" performs no lowering and
no code generation, so admitting the selected topology without changing it was
achieved by hand-writing a complete new per-topology back end beside it, and the
challenge table from which the topology was drawn contains only recombinations
of already-supported primitives with three near-identical any-hit variants.

**My restatement differs from the request in three places**, which I flag as
required by the cold-start contract:

- The request calls Goal5838 evidence that "a schema-driven core" admitted a new
  topology. On the source, the sealed core is an admission, identity, artifact
  and lifecycle framework; lowering and codegen live entirely outside it. See
  P0-1.
- The request states the root `README.md` "instructs `pip install -e .` even
  though this checkout has no packaging metadata that authorizes an editable-
  install claim." `pyproject.toml` at the repository root does declare a
  complete setuptools build system, project metadata, and
  `[tool.setuptools.packages.find] where = ["src"]`, and `src/
  rtdl_source_tree.egg-info/` exists. The editable-install instruction is
  supported; the actual README defect is seven dead `docs/v4/` links. See P2-4.
- The request discloses exactly one stale current-tree custody check
  (Goal5832). There are at least two, and the second one guards the Goal5838
  generality claim. See P1-1.

**Current claim ceiling as I would state it.** RTDL is a bounded whole-protocol
admission and identity system with hand-written per-topology back ends, for
which one recombination within an author-defined 4x3 table was instantiated
prospectively without modifying the admission framework, and for which bounded
structural refinement evidence exists over three routes, four modes and five
properties. No generality, usability, prevalence, or net language-performance
claim is currently supportable.

## 2. Prior-finding closure table

| Prior attack | Current disposition | Evidence that closes or fails to close it | Remaining blocker | Severity |
|---|---|---|---|---|
| Only two closed protocol families; generality zero | Partially addressed, much less than claimed | Goal5838 added one prospective instantiation, but it required ~2,635 new hand-written lines in `src/rtdsl/v4_sphere_any_hit_count_*` including a hard-coded CUDA/OptiX skeleton (`v4_sphere_any_hit_count_wrapper_codegen.py:288-360`); the sealed core's `lower_canonical_compilation_plan` emits a JSON document with `"executable": false` (`v4_family_schema.py:1461-1467`) | Generality sentence must be rewritten to framework-parametricity, not compiler genericity | P0 |
| No prospective frozen-core exam | Addressed in form, weak in substance | NIST beacon 2.0 pulse selection, pre-committed 10-row table, seal predates selection (`GENERIC_CORE_SEAL.json`, `CHALLENGE_SELECTION_RESULT.json`) | Table is a 4x3 cartesian product whose three topologies share the role set {make_ray, any_hit, miss, finalize} and all use `count_relation: query_count`; the beacon cannot protect a domain the authors defined | P0 |
| No real-world protocol-defect prevalence evidence | Not closed | Goal5839 froze denominator, discovery order and adjudication rule but produced zero classifications; Goal5820's `0/4/16` is not paper-ready | Remove empirical motivation entirely or replace with constructed-defect framing | P1 |
| No external human author | Not closed, not closable before deadline | Author count 0, usability studies 0 | Delete every ease, productivity and usability sentence | P1 |
| Native OptiX/OWL/PyOptix boundary unclear | Substantially addressed | Goal5848 Arm B (idiomatic), Arm C (device-continuation, `strong_pyoptix.py:100-112` loads `goal5802_relation_unique_compact` CUBIN), Arm D (Direct), Arm E (predecessor) | Arms exist but have 0/2 GPU transactions | P1 |
| No causal admission-cost analysis | Addressed | Goal5842 V12 on two generations, 216 causal + 216 baseline receipts each, 7 formal stages | None; conclusions remain implementation-specific | closed |
| Weak/asymmetric performance baseline | Partially addressed | Goal5845's arm is explicitly weak; Goal5848 Arm C is the intended repair and is real | Until Arm C executes, no strong-baseline statement exists | P0 |
| Application-specific logic may leak into engine | Substantially addressed for V4 | No collision/robot/trajectory/RT-CCD vocabulary in V4 generic paths; an explicit guard exists at `v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py:267` | Guard is applied to one route only; `src/rtdsl/grouped_reduction_contracts.py:36` still ships `"app": "robot_collision_screening"` in the package | P2 |
| No independent lowering/refinement evidence | Addressed at bounded scope | `scripts/goal5840_independent_target_checker.py` (2,795 lines) imports no `rtdsl`, forbids compiler projections (`TC000_COMPILER_PROJECTION_FORBIDDEN`), partial-evaluates generated source (`TC001_PARTIAL_EVAL_*`) | Denominator is three routes, four modes, five properties; nothing more | closed at scope |
| Adverse results could be hidden by successor optimization | Addressed procedurally, verified | Goal5842/5843 deficits, Goal5844 failed first transaction, Goal5846 adverse sensitivity, Goal5847 adverse `2.504242x`, Goal5840 attempts 1-6, Goal5836 terminal refusal all remain in the tree | None. This is the project's strongest habit | closed |

## 3. Executive verdict

The post-2026-08-29 work is real engineering and the evidence custody is better
than most submissions I would see at this venue, but it did not accomplish what
its labels say. The compilation-unit insight remains the paper's genuine
contribution and is defensible. The generality result is the problem: the sealed
"generic core" contains admission, identity, artifact binding and lifecycle, and
contains no lowering or code generation at all, so the selected topology was
admitted without touching it only because a complete new per-topology back end —
contract, Numba codegen, a hard-coded CUDA/OptiX wrapper skeleton, an OptiX
compiler, a prepared runtime, a public API and a route adapter — was hand-written
beside it after selection. The challenge table compounds this: all ten rows
recombine an already-supported primitive with one of three any-hit variants that
share a single role set, so the NIST beacon randomized a choice that was
architecturally pre-solved. Goal5840, by contrast, is honest and useful, and the
preserved adverse performance chain is a credit to the project. The performance
story is not currently reportable: Goal5845's favorable reciprocal rests on a
baseline the project itself calls weak, and its published explanation — device
compaction versus host canonicalization — is inaccurate, because RTDL also
host-sorts and host-uniques the rows it transfers. Goal5848's design is the right
answer to all of this and I would trust its gates, but it has zero of two
required transactions and therefore contributes nothing to a 2026-09-10 paper
unless it runs. Two current-tree custody checks now fail, one of them the very
seal verifier that guards the generality claim, and only one of the two was
disclosed. A scientifically defensible CGO paper is still submittable in five
days, but only as a whole-protocol admission-and-identity paper with a sharply
narrowed generality sentence, the manuscript resynchronized, and the 9.53x
reciprocal deleted.

## 4. Findings

### P0-1 — The sealed "generic core" performs no lowering, so the headline generality result is mislabeled

Architectural, not a local bug.

The three sealed files are `src/rtdsl/v4_family_schema.py` (1,533 lines),
`src/rtdsl/v4_generic_family_lifecycle.py` (1,360 lines) and
`src/rtdsl/v4_family.py` (92 lines). Reading them:

- `v4_family.py` is a re-export facade only. It contains no logic.
- `v4_family_schema.py` is a JSON-document validator for a family shape and
  protocol instance, plus canonicalization and domain-separated digests.
- The function named `lower_canonical_compilation_plan`
  (`v4_family_schema.py:1461-1467`) does not lower anything. It constructs a
  canonical JSON document that literally carries `"executable": False`
  (`v4_family_schema.py:1422`) and hashes it.
- `v4_generic_family_lifecycle.py` defines artifact binding, provider descriptor
  and projection, executable identity, deployment export, and the abstract
  provider SPI `FamilyProviderV1` with `descriptor` / `project` / `materialize`
  (`v4_generic_family_lifecycle.py:907-932`).

Every compilation responsibility a CGO reader would associate with the word
"core" — Callback IR verification, Numba device codegen, OptiX wrapper
generation, PTX composition, provider runtime — is outside the seal.

The post-selection diff confirms the consequence. Between the seal-adjacent
commit `19b3fda` and the evidence commit `7da6805`, `git diff --stat` over
`src/`, `tests/` and `case_studies/` shows 4,740 insertions, of which the
following are new `src/rtdsl/` modules written *after* the challenge was
revealed:

| New post-selection module | Lines |
|---|---:|
| `v4_sphere_any_hit_count_contract.py` | 619 |
| `v4_sphere_any_hit_count_prepared_runtime.py` | 560 |
| `v4_sphere_any_hit_count_wrapper_codegen.py` | 384 |
| `v4_sphere_any_hit_count_family_route.py` | 373 |
| `v4_sphere_any_hit_count_optix_compiler.py` | 293 |
| `v4_public_sphere_any_hit_count.py` | 266 |
| `v4_sphere_any_hit_count_numba_codegen.py` | 107 |
| `v4_sphere_any_hit_count.py` | 33 |
| **total** | **2,635** |

plus 28 modified lines in `v4_sphere_optix_compiler.py`. That is 88% of the
sealed core's own size, authored after selection, in the engine package.

`v4_sphere_any_hit_count_wrapper_codegen.py:288-360` is the decisive artifact.
It is a hand-authored CUDA/OptiX program skeleton with the IR expressions
interpolated into fixed slots. Hard-coded in the template, not derived from the
Callback IR or the family schema:

- `OPTIX_RAY_FLAG_DISABLE_CLOSESTHIT` as a literal;
- an unconditional `optixIgnoreIntersection()` terminating the any-hit program
  (line 348), so accept-and-continue semantics are baked in rather than selected
  by the declared effect;
- a u64-split-across-`payload_0`/`payload_1` convention with `payload_2` through
  `payload_7` written as literal zeros;
- an `output_0`/`output_1`/`output_2` result layout with
  `params.output_2[query] = 0u;` as a literal;
- per-role error codes `0xffff3802` through `0xffff3807` as literals;
- a fixed `SPHERE_ANY_HIT_COUNT_TEMPLATE` physical template.

I checked whether this was template reuse rather than new work. It is new work:
`difflib.SequenceMatcher` line ratios against the pre-existing sphere stack are
0.302 (wrapper codegen), 0.398 (optix compiler), 0.196 (prepared runtime) and
0.231 (public API). The topology back end was written by hand, not generated.

**What is nevertheless true and worth claiming.** The admission, identity,
artifact-binding, provider-projection and public-lifecycle framework *is*
topology-parametric, and it did absorb a new protocol shape with zero byte
changes. The restricted-Python callback bodies genuinely are compiled and type-
checked into those fixed slots. That is a real and non-trivial result about the
framework. It is not a result about a compiler.

**Smallest credible repair.** No code. Replace the generality sentence. See
Section 12 for the exact wording I would defend.

### P0-2 — The challenge table forecloses the generality question it was built to test

Architectural.

`CHALLENGE_TABLE.json` declares `generation_rule.cartesian_product` as "all four
primitive kinds exercised by pre-Goal5838 V4 provider paths crossed with all
three predeclared challenge topologies", `manual_row_addition_or_removal: false`,
and an exclusion rule that removes "only exact callback role/effect/result
topologies whose implementation existed before Goal5838". Two rows were excluded,
both `builtin_triangle`, leaving 10.

The protection this gives is real but narrow: it prevents the authors from
picking a convenient row after seeing core behaviour. It gives no protection at
all against the domain being easy, and the domain is easy:

- All three topologies in `topology_domain` have the identical role set
  `{make_ray, any_hit, miss, finalize}`.
- All three declare `result.count_relation: "query_count"`.
- They differ only in continuation policy (`terminate_on_first_accepted_hit`,
  `accept_every_hit_and_continue`, `ignore_excluded_hits_...and_continue`) and
  result type (`bool`, `u64`, `u64` plus one `primitive.include` metadata
  channel).
- All four primitives in `primitive_domain` were already exercised by
  pre-Goal5838 provider paths, by the generation rule's own wording.

So every one of the ten rows is a recombination of a solved primitive with a
minor variant of a solved topology. Absent from the domain entirely: any
closest-hit topology, any user-intersection topology, any topology whose result
count relation is not per-query, any grouped or owner-indexed output, any
row-returning relation output — which is one of RTDL's own two stable
constructors — any multi-payload or attribute-carrying shape, and any nested or
repeated trace.

The selected row, `builtin_sphere::any_hit_count_continue_u64_per_query`, is the
clearest instance: the sphere primitive was delivered by Goal5833, and the
`any_hit_count_continue_u64_per_query` topology already existed for triangle as
`compile_count_callback` in `src/rtdsl/v4_triangle_standard_library.py` — the
table's own exclusion list says so, and excludes it *for triangle only*. The
exam therefore asked whether a solved primitive could be combined with a solved
topology, and the answer was yes at a cost of 2,635 new lines.

I also note a self-consistency risk the project should check: the table does
not exclude `builtin_round_linear_curve::any_hit_terminate_bool_per_query`,
although Goal5834-B3 delivered a per-query Boolean curve route before Goal5838.
If that row was in fact implemented pre-selection, the eligible denominator is
9, not 10, and one of the ten "unseen" rows was already solved.

**Exact remaining selection channel.** Domain construction. The beacon
randomizes within a set the authors chose, and the set was chosen after the
authors knew which primitives and which continuation policies the system
handled.

**Smallest credible repair.** No code, and no rerun is feasible in five days.
State the denominator explicitly in the paper — "one row of a ten-row table
formed by crossing four already-supported primitives with three any-hit
continuation variants sharing one role set" — and let the reader price it. Do
not describe the row as "unseen" or "new" without that sentence adjacent.

### P0-3 — Goal5845's published explanation of its favorable ratio is inaccurate

Correctness of a reported explanation, not of code.

Goal5845 reports RTDL 366,340 ns against pinned PyOptix 3,486,126 ns
(0.1049x median, reciprocal 9.53x) and explains it as: the PyOptix arm emits
8,192 raw duplicate events and canonicalizes 4,096 rows on the host, while RTDL
performs generic device semantic compaction. `AGENTS.md:2669` repeats this
framing for Goal5847.

The source does not support the contrast. In
`src/native/optix/rtdl_optix_v4_callback_poc.cpp`, function
`execute_v4_prepared_bounded_relation_callback`:

- `stored = fast_mode ? unique_count_u32 : min(raw_count, raw_event_capacity)`
  (line 6835-6837);
- in fast mode, `cuMemcpyDtoHAsync` transfers `stored` rows from
  `prepared->unique_rows` (line 6843-6845);
- and then, on the host, lines 6849-6860 run `std::sort` over
  `[begin, begin+stored)` with a `(source_id, item_id)` comparator, followed by
  `std::unique` with the same key.

RTDL therefore also canonicalizes on the host. The genuine difference is the
number of rows crossing D2H — roughly 4,096 for RTDL versus 8,192 for the
baseline — and the corresponding host sort size. A 2x transfer and 2x host-sort
difference does not account for a 9.53x end-to-end gap, which means the gap is
dominated by unaccounted-for weakness in that specific pinned arm.

This matters beyond wording. The project's own claim discipline
(`AGENTS.md:2551`) forbids claiming performance parity unless phase boundaries
match, and forbids presenting app-specific work as generic improvement. A
reported causal explanation that the source contradicts is a more serious defect
than an unexplained number.

I record the favorable finding alongside it: the status gate is real. Lines
6826-6832 set the fast status and return with
`output_d2h_after_status_failure = 0u` before any D2H when the status code is
non-zero, so CP004 is enforced at the transfer boundary, not after it.

**Smallest credible repair.** Correct the sentence in
`goal5845_relation_public_parity_20260904/FINAL_ENGINEERING_REPORT.md` and in
`AGENTS.md:2669` to "RTDL performs device-side deduplication and transfers only
the deduplicated rows, then canonicalizes them on the host; the pinned baseline
transfers all raw events and canonicalizes them on the host." Then delete the
reciprocal from any paper-facing text; Goal5848 Arm C is the honest comparator.

### P1-1 — The Goal5838 seal verifier fails on the current tree, and this is not disclosed

Evidence custody.

The request discloses exactly one stale custody check, in Goal5832. There are
two, and the undisclosed one guards the generality claim.

Recomputing the sealed hashes against the current working tree:

| Sealed file | Sealed bytes | Current bytes | Match |
|---|---:|---:|---|
| `src/rtdsl/v4_family_schema.py` | 58,007 | 59,169 | no |
| `src/rtdsl/v4_generic_family_lifecycle.py` | 41,675 | 51,523 | no |
| `src/rtdsl/v4_family.py` | 2,792 | 2,938 | no |

The project's own test agrees:

```text
$ PYTHONPATH=src:. python3 -m unittest tests.goal5838_core_seal_and_selection_test
ERROR: test_07_stored_seal_verifier_passes_after_generation
  scripts.goal5838_freeze_generic_core.Goal5838SealError:
  sealed file drift: src/rtdsl/v4_family_schema.py
Ran 39 tests ... FAILED (errors=1)
```

Three commits after the Goal5838 evidence commit modified sealed files:
`ee0237963` (Goal5844), `a6f395cc9` (Goal5846) and `5da96b008` (Goal5847). The
Goal5844 change is two decorator lines adding `@lru_cache(maxsize=4096)` beneath
`@property` on `FamilyProviderProjectionV1.projection_sha256` and
`FamilyExecutableIdentityV1.identity_sha256`.

`GENERIC_CORE_SEAL.json` records `core_mutation_allowed_after_seal: false`. I
read that as scoped to the Goal5838 exam window rather than a permanent
prohibition, and the later mutations are legitimate performance engineering.
The finding is not that the mutations were wrong. It is that:

1. the Goal5838 result is bound to commit `7da6805` and must be stated in the
   past tense against that commit, never in the present tense about the shipped
   system; and
2. a reviewer or artifact evaluator running the current tree gets a failing seal
   verifier with no disclosure telling them to expect it.

I also confirmed the disclosed Goal5832 staleness, and it has widened. The seal
recorded the known error as `goal5831.source_authorities[6]`; the current tree
fails earlier, at `goal5831.source_authorities[1]`:

```text
$ PYTHONPATH=src:. python3 -m unittest tests.goal5832_protocol_shape_algebra_test
ERROR: goal5832_protocol_shape_algebra.AlgebraError:
  goal5831.source_authorities[1] byte count drift
Ran 23 tests ... FAILED (errors=1)
```

**Smallest credible repair.** Add a `KNOWN_STALE_CUSTODY_CHECKS.md` naming both
failures, the commits that caused them, and the exact commits at which each
authority must be replayed. Roughly one hour. Do not re-seal, and do not
"repair" by rewriting historical manifests.

### P1-2 — The near-parallel curve domain exclusion is not enforced on the route the collision case study uses

Correctness boundary.

Goal5834 preserved a genuine adverse result: a ray exactly collinear with a
capsule axis was accepted by the initial domain, the closed-capsule oracle
reported a hit, and OptiX reported a miss. The repair restricts a bounded
near-parallel domain before launch.

That repair lives in `verify_curve_motion_segments`
(`src/rtdsl/v4_curve_physical_schema.py:851-915`), which rejects
`near_parallel_curve_query` (line 891), a segment/capsule distance separation
below `2^-12` (line 898-903), and a front entry inside the endpoint guard
(line 904-912).

The Boolean route uses a different, deliberately weaker function.
`verify_curve_boolean_motion_segments` (line 917-949) checks only cardinality,
vec3 shape, float32 representability and non-zero direction. Its docstring is
explicit about why: "This function intentionally accepts no static geometry.
Introducing control points, widths, or primitive indices here would reintroduce
the O(query x primitive) CPU collision prepass excluded by Goal5834-B1."

The Boolean function is what every Boolean and owner-grouped public entry point
calls:

- `src/rtdsl/v4_public_builtin_curve.py:147`
- `src/rtdsl/v4_curve_prepared_runtime.py:534`
- `src/rtdsl/v4_curve_owner_grouped_any_hit_public.py:137`
- `src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py:489`

So the route that carries the Goal5837 owner-grouped result and the entire
collision case study admits precisely the geometry class in which OptiX and a
closed-capsule oracle were observed to disagree.

The case study's own admission does not cover it either.
`case_studies/linear_rtccd_owner_grouped/linear_rtccd_owner_grouped.py:252-294`
certifies an O(P+Q) sufficient condition that no finite query is wholly inside
one capsule — minimum query length strictly greater than maximum capsule
diameter. That excludes containment, a different degeneracy. A query edge much
longer than any capsule diameter can still be nearly collinear with a capsule
axis.

The performance rationale is legitimate and I would not ask for the O(P*Q)
prepass. But Goal5837's "30/30 oracle match" is then an unconditioned result:
the workloads presumably avoided the degenerate domain, and nothing enforced
that they did.

**Smallest credible repair, in preference order.** (a) Add the O(P+Q) sufficient
near-parallel guard that is expressible without pairwise work — a bound on the
angle between each query direction and every capsule axis is O(P+Q) if the axis
set is bounded — and enforce it at the Boolean entry points; or (b) if that is
not reachable in five days, state in the paper and in the case-study README that
the near-parallel exclusion is enforced only on the First Contact route, and that
the Boolean and owner-grouped routes are validated on workloads that avoid it by
construction rather than by admission. Option (b) is roughly two hours and is
sufficient for the compiler claim.

### P1-3 — Neither the native provider nor the raw evidence capsules are in the repository

Artifact readiness.

`goal5838/FINAL_AUTHORITY.json` records `native_provider.committed_to_git:
false` with `bytes: 7181936`. `goal5840/FINAL_AUTHORITY.json` records the same
for its provider (`bytes: 7181936`, different digest) and additionally
`off_repository_raw_capsule: {bytes: 3170210, committed_to_git: false,
contains_native_dso: true, rebuild_required_if_raw_bytes_are_not_retained:
true}`.

Both authorities are internally consistent and independently recomputable *from
bytes the repository does not contain*. An external reviewer or CGO artifact
evaluator can verify that a digest matches a file only if they possess the file.
They do not.

Combined with P1-1 this is the artifact story a reviewer will actually
encounter: two failing custody tests, and the two headline authorities bound to
binaries that are not shipped.

**Smallest credible repair.** Either commit the two DSOs and the 3.17 MB capsule
via LFS, or add an explicit artifact statement naming exactly which authorities
cannot be replayed from the repository alone and what a rebuild requires.
Roughly two hours for the statement.

### P1-4 — The manuscript contradicts the evidence in both directions

Submission blocker.

`paper/cgo2027/main.tex` (1,579 lines) predates the entire review interval. Its
anonymity is clean — I found no author name, institution, email, repository URL
or pod endpoint in the file — but its factual content is stale, and notably it
*understates* the current position in several places:

| Line | Current text | Status |
|---:|---|---|
| 673 | "prospective frozen-core extension exams remain zero" | now one, at bounded scope |
| 1114-1115 | "report a prospective unbiased new-application exam count of zero" | same |
| 935 | "Leaf primitives ... RTDL coverage & 2 / 4" | now 4/4 kind presence |
| 650 | "of which four" (leaf kinds) with 2-kind instantiation | stale |
| 50, 128, 156, 899, 1211, 1354, 1506, 1564 | "two fixed protocol constructors" | still literally true for stable constructors, but must now be stated alongside Goal5837's root-exported successor and Goal5838's instantiation |
| 1183 | "Direct is 1.36--2.83$\times$ faster than both Python-host arms at steady state" | superseded by Goals 5842-5847 |

I want to be precise about line 1183, because it is easy to misread as an
overclaim: it is an *adverse-to-RTDL* statement. The manuscript is not currently
overclaiming performance. It is reporting a superseded experiment whose numbers
no longer correspond to any committed authority.

**Smallest credible repair.** A full evaluation-section rewrite is required
regardless. See Section 12.

### P2-1 — Executable identity for the native provider is bound at load time, not at execution time

Claim boundary, introduced by performance work.

`src/rtdsl/physical_execution_provenance.py:132-176` hashes the provider `.so`
once per loaded handle and reuses the digest for every subsequent receipt. The
docstring states the intent plainly: "rereading the same multi-megabyte provider
file is not part of that per-call evidence."

The defensive engineering around this is good: `_LOADED_PROVIDER_IDENTITIES` is
keyed by `id(library)` but stores the library object and checks
`current_library is not library` (line 147-149), so integer id reuse cannot
substitute a handle, and the resolved path and digest are both pinned.

The residual claim boundary is real. CP005 asserts a chain to "provider/native
objects". After load, that assertion is about bytes read at load time. If the
file is replaced afterwards, receipts continue to report the original digest.
That is arguably the more meaningful statement — the loaded pages are what
execute — but the paper must say which one it makes.

Two lifecycle notes attach here. `_LOADED_PROVIDER_IDENTITIES` and
`_AUDIT_ABI_REGISTERED` are process-global dictionaries holding strong
references to library objects, and nothing removes entries, so `close()` cannot
release a provider handle. Separately, the two `@property` + `@lru_cache`
decorators added by Goal5844 retain up to 4,096 instances of each identity class
for the process lifetime. I checked correctness carefully: both classes are
`@dataclass(frozen=True, slots=True)`
(`v4_generic_family_lifecycle.py:565, 680`), so they hash by value over
immutable fields, the cached digest cannot go stale, and the memoization is of a
pure function. This is a legitimate generic repair, not benchmark
special-casing — but it is a memory-retention construct in the sealed core that
survives `close()`.

**Smallest credible repair.** One manuscript sentence scoping CP005 to load-time
provider binding. Optionally convert the two caches to instance-level cached
attributes so teardown releases them; not required before the deadline.

### P2-2 — The application-vocabulary guard is applied to one route only

`src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py:267` asserts
that the generated wrapper source contains none of
`("collision", "trajectory", "robot", "pose", "raydb")`. This is a good
architectural invariant and exactly the right place to enforce it.

It is absent from `v4_sphere_any_hit_count_wrapper_codegen.py` and from the
other wrapper generators. A stated architectural invariant enforced on one of
several equivalent paths is weaker evidence than it appears.

**Smallest credible repair.** Lift the check into the shared
`v4_callback_optix_wrapper_codegen` helper so every generator inherits it.
Roughly one hour, low risk.

### P2-3 — Application vocabulary ships inside the engine package

`src/rtdsl/grouped_reduction_contracts.py:36` contains
`"app": "robot_collision_screening"` with `"group_key": "pose_id"`, and further
rows for `"app": "database_analytics"`. The module is re-exported from
`rtdsl/__init__.py` at lines 744-780, 1981, 2093 and 3136-3137.

In fairness this is v1.5 legacy metadata, not V4 engine logic; only the constant
`V1_5_GROUPED_THRESHOLD_BOOL_RESULT_LAYOUT` is consumed by
`src/rtdsl/generic_primitives.py:24`, and each row carries its own
`claim_boundary` disavowing app claims. The V4 generic paths are clean: I grepped
`src/rtdsl/v4_*.py`, `src/native/optix/rtdl_optix_core.cpp` and
`rtdl_optix_api.cpp` for collision, robot, swept, capsule, obstacle, RT-CCD and
trajectory, and every hit is either an unrelated use of "collision" (hash or
artifact name collision), the legitimate geometric term "capsule" for a
round-linear curve segment, or the negative guard above.

The finding is artifact hygiene, not architecture: a CGO artifact reviewer will
grep `src/rtdsl/` for application names and find `robot_collision_screening` in
a package the paper describes as application-neutral.

**Smallest credible repair.** Exclude v1/v2 legacy modules from the artifact
tree, or add one sentence to the artifact README partitioning `src/rtdsl/` into
the V4 engine and the retained v1/v2 portfolio.

### P2-4 — README links seven documentation files that do not exist

`README.md:91-97` links `docs/v4/README.md`, `tutorial.md`,
`api_reference.md`, `security_model.md`, `nine_app_coverage.md`,
`migration_from_v3.md` and `restricted_python_optix_callbacks_design.md`.
`ls docs` returns "No such file or directory".

As recorded in Section 1, the request's companion assertion about
`pip install -e .` does not hold: `pyproject.toml` declares a setuptools build
backend, project metadata and `packages.find where=["src"]`, and
`src/rtdl_source_tree.egg-info/` is present. The editable install is authorized;
only the documentation links are broken.

**Smallest credible repair.** Delete the seven links or write minimal stubs.
Under one hour.

### P3-1 — Phase instrumentation is gated asymmetrically across Goal5848 arms

In `experiments/goal5848_strong_baseline/worker.py`, the RTDL arm wraps each
phase in `_measure_if(..., enabled=phase_instrumentation)` (lines 425-437), so
the per-phase timers can be compiled out. The strong-PyOptix arm uses
unconditional `_measure(...)` (lines 773-796).

The magnitude is negligible — four `perf_counter_ns` pairs against a ~263 ms
endpoint — and the direction is not obviously favorable to RTDL. But it is a
structural asymmetry in an experiment whose entire value is symmetry, and a
hostile reviewer will name it before checking the magnitude.

**Smallest credible repair.** Use the same gating helper on all arms. Under one
hour, and worth doing before the formal transactions run.

### P3-2 — Pod SSH endpoints are embedded in authorities

`goal5838/FINAL_AUTHORITY.json` and `goal5840/FINAL_AUTHORITY.json` both record
`pod_target.ssh_endpoint: "root@213.173.108.100:12943"`. This is a rented
compute endpoint rather than author-identifying information, so it is not an
anonymity violation, but it should not ship in a public artifact.

**Smallest credible repair.** Scrub at artifact-packaging time; do not rewrite
the sealed authorities, since that would break their digests.

## 5. Architecture and generalization verdict

Answering Section 6 of the request in order.

**6.1 — Is the protocol-shape algebra a meaningful compiler abstraction or a
descriptive schema over concrete families?** Descriptive, at present. Goal5832
froze `<G,R,V,E,H,B,C,X,L>` with a recursive reference validator and hostile
tests, and the algebra does real work: it separates family shape, protocol
instance and deployment identity, and it gives the admission framework a typed
document to check. But nothing downstream is parameterized *by* the algebra to
produce code. It classifies and validates; it does not drive lowering.

**6.2 — Is the frozen core large enough to contain the scientifically important
generic mechanism?** No. See P0-1. The core contains the admission, identity and
lifecycle mechanism, which is genuinely generic. It contains none of the
lowering mechanism, and lowering is where a CGO reader locates the compiler.
The seal was drawn around the part that was already parametric.

**6.3 — Does the selected extension instantiate a generic contract, or
implement a third special case?** It is a third special case with respect to
codegen and runtime, and a genuine instantiation with respect to admission and
identity. Concretely: `v4_sphere_any_hit_count_family_route.py` does import
`v4_family_schema` and `v4_generic_family_lifecycle` and does register through
the generic SPI — that part is a real instantiation. Everything the route needs
to actually run on a GPU was hand-written after selection.

**6.4 — Is the NIST-pulse selection credible protection against cherry-picking?**
Partially. The mechanism is sound: a pre-committed table, a pre-committed client
script with a recorded digest, a pinned certificate, a target timestamp that was
in the future when the protocol was committed, domain-separated SHA-256 with
rejection sampling, and the previous pulse retained. It genuinely prevents
post-hoc row selection. It provides no protection against the domain, and the
domain is the problem. See P0-2 for the exact remaining channel.

**6.5 — Does package-external provider construction represent a real extension
boundary?** Partially. `tests/fixtures/goal5838_external_provider.py` (4,848
bytes) exists and is sealed as Stage-B evidence, and `v4_family.py` deliberately
re-exports only the schema, lifecycle and provider SPI while declining to
re-export concrete routes. That is the right instinct. But since the SPI's
`materialize` returns a handle whose behaviour is entirely provider-authored,
"package-external" currently means "the provider may be written elsewhere",
not "the compiler generates the provider". The boundary is real for
registration and unhelpful for the generality claim.

**6.6 — The strongest exact generality sentence supported by Goal5838.** I would
defend exactly this and nothing broader:

> At commit `7da68056550818d8e2f6cdb4d7aa3e9029cc4524`, a protocol shape
> selected by a NIST Randomness Beacon pulse from a ten-row table — formed by
> crossing four already-supported OptiX primitive kinds with three any-hit
> continuation variants that share a single four-role topology — was admitted,
> lowered, executed on an RTX 2000 Ada GPU under OptiX 9 in two true OptiX
> launches, and matched all twelve rows of an independent rational oracle,
> without modifying the three previously sealed files that implement schema
> admission, provider projection, executable identity and the public lifecycle.
> Realizing the shape required approximately 2,635 lines of new
> topology-specific contract, code generation, wrapper and runtime code outside
> those files. The result establishes that RTDL's admission and identity
> framework is topology-parametric. It does not establish that RTDL's lowering
> is generic, and it does not establish arbitrary Callback IR execution.

**6.7 — Is Goal5840 circular?** No. `scripts/goal5840_independent_target_checker.py`
imports only `argparse`, `ast`, `base64`, `hashlib`, `json`, `re`, `pathlib` and
`typing`. It never imports `rtdsl`; the only occurrences of that string are
source *paths* it reads and parses. It refuses to consume compiler-produced
projections at all (`TC000_COMPILER_PROJECTION_FORBIDDEN`). This is a genuinely
separate implementation.

**6.8 — Are the five properties sufficient, and what is missing?** Sufficient
for the bounded claim as stated, and the checker is stronger than the label
"structural" suggests: `TC001_PARTIAL_EVAL_*` partially evaluates generated
device source against expected `make_ray`, `intersection`, `any_hit`,
`accept_continue` and `finalize` semantics, and `TC001_*_SYMBOL_*` cross-checks
each role symbol against the compiled ABI metadata, the wrapper source and the
compiled PTX. Missing, and worth naming as future work rather than as a blocker:
numeric refinement (float rounding and ordering between the CPU reference and
the device program), SBT-record-to-program-group correspondence checked at the
OptiX API level rather than from declarations, launch-time verification that the
built pipeline's entry names equal the declared role symbols, and any property
covering multi-launch or continuation-across-launch behaviour.

**6.9 — Do Goals 5838 and 5840 together support a bounded compiler contribution,
or a checker plus templates?** Closer to the latter, and the paper should say
so without embarrassment. What exists is: a real restricted-Python front end and
typed Callback IR; a real whole-protocol admission system enforcing five
obligations as one set; a real identity and fail-closed lifecycle; hand-written
per-(primitive, topology) trusted wrapper templates into which verified callback
bodies are compiled; and bounded independent evidence that the lowering into
three of those templates preserves five declared properties. That is a coherent
and publishable systems contribution. It is not a generic compiler, and every
sentence implying otherwise should go.

**6.10 — Is the absence of an external human author fatal?** Not fatal for CGO.
CGO evaluates compiler construction, not usability, and no reviewer will require
a user study for a language-and-admission paper. It becomes fatal only if the
paper makes any ease, productivity, learnability or "developers can" claim.
Remove all such language and the absence is an ordinary limitation. Do not
substitute agent-authored examples for it, even as anecdote.

## 6. Sphere, curve, and collision verdict

Answering Section 7 in order.

**7.1 — True built-in geometry, no hidden user intersection program?**
Confirmed. `src/native/optix/rtdl_optix_v4_callback_poc.cpp` sets
`input.type = OPTIX_BUILD_INPUT_TYPE_SPHERES` (line 2476) and
`OPTIX_BUILD_INPUT_TYPE_CURVES` with `curves.curveType =
OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR` (lines 3115-3117), and sets
`spec.builtin_is_type` to `OPTIX_PRIMITIVE_TYPE_SPHERE` (2602) and
`OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR` (3264, 3746). The module is obtained from
OptiX via `optixBuiltinISModuleGet` at
`src/native/optix/rtdl_optix_core.cpp:1981`, and the hit group sets
`desc.hitgroup.entryFunctionNameIS = nullptr` when built-in IS is used
(line 2017-2019). Critically, line 1974-1976 fails closed:

```cpp
if (spec.intersection_name || spec.builtin_is_type == OPTIX_PRIMITIVE_TYPE_CUSTOM)
    throw std::runtime_error("OptiX built-in IS producer specification is invalid");
```

so supplying a user intersection program alongside built-in IS is rejected
rather than silently preferred. This is clean.

**7.2 — Did application semantics leak into `src/rtdsl/**` or `src/native/**`?**
Not into the V4 generic paths. See P2-3 for the full grep result and the one
legacy exception. I want to credit the negative guard at
`v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py:267` explicitly — an
assertion that generated source contains no application vocabulary is a better
defence than a naming convention, and I would keep it and generalize it (P2-2).

**7.3 — Is the near-parallel exclusion principled, visible, and enforced at all
public entry points?** Principled yes, visible yes, enforced at all entry points
**no**. See P1-2. This is the most substantive defect I found in this area.

**7.4 — Is `OWNER_GROUPED_ANY_HIT / BOOL_OR` genuinely generic?** Yes, on the
source. The reduction is `owner_hit_bits[owner_ids[primitive_id]] |= 1` over
accepted `(query_id, primitive_id)` events, with `atomicOr` and
`optixIgnoreIntersection` in the wrapper and no application vocabulary anywhere
in the generated source. Nothing in it knows what an owner means. It is reusable
for any owner-partitioned existential query — set membership, bucketed
occupancy, group-level reachability — and I would describe it that way rather
than as a collision primitive.

**7.5 — Do geometry construction, predicate interpretation and oracle remain
application-owned?** Yes. Swept-capsule construction, edge direction choice,
identity reconstruction and `collision = OR(per_edge_hit)` all live in
`case_studies/`, along with `independent_oracle.py` and
`independent_edge_capsule_oracle.py`. The engine receives geometry and returns
grouped bits. This boundary is correctly drawn and is one of the review
interval's genuine successes.

**7.6 — Is Goal5835 fairly described as a bounded case study?** Yes.
It added no GPU launches and no timing, it binds app-shaped bytes to
already-executed Goal5834-B3 functional evidence, and it carries
`NOT_A_PAPER_APP`. The description is accurate.

**7.7 — Does Goal5836's terminal result forbid same-input comparison and Paper
App promotion?** Yes, and the logic is sound. A material predicate difference —
the author benchmark's strongly connected directed obstacle-edge graph preserving
inside-start correctness for one-sided rays against hollow round curves, versus
Goal5835's single arbitrary deduplicated edge direction with initial overlap
excluded — means the two systems do not compute the same function on the same
input. Timing them against each other would compare different problems. Stopping
before input freeze was correct, and
`TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE` should be
reported in the paper as a result, not hidden as a failed branch.

**7.8 — Any path by which current prose invites a Sui reproduction reading?**
Two. First, the case-study directory names `sui_derived_edge_crossing_core` and
`linear_rtccd_owner_grouped` embed "sui" and "rtccd"; a reader browsing the
artifact will read those as reproduction claims before reaching
`CURRENT_STATUS_AFTER_GOAL5836.md`. Second, any paper sentence pairing "collision
detection" with a citation to Sui et al. in the same clause will be read as
reproduction regardless of hedging. Rename or prominently disclaim the former;
for the latter, cite Sui et al. only as the source of the *mapping idea* and
state the refusal in the same paragraph.

**7.9 — What additional collision work is scientifically necessary?** For the
compiler claim, none. The case study's job is to show that a reusable
owner-grouped Boolean reduction lives in the engine while swept-shape
construction and collision meaning live outside it, and it does that. I would
explicitly *not* require initial overlap, near-tangent contact, face-interior
collision, exact time of impact, or collided-primitive identity. The only
necessary work is the P1-2 disclosure or guard.

## 7. Goal5838 prospective-exam verdict

The exam was honestly run and it is worth less than its label.

What was done correctly, and I want this on the record because it is unusual:
the core inventory and hash seal predate challenge revelation; the ten-row table
was frozen with a recorded digest before selection; the selection client script
was committed with its own digest; the target pulse timestamp was in the future
when the protocol was committed; the previous pulse was retained alongside the
target; pre-selection activity is recorded as zero candidate executions, zero
candidate-specific provider implementations and zero prospective successes; the
only-scientific-failure condition was defined in advance with a five-part test
requiring a minimal witness; a first pod execution failure was preserved in a
repair log rather than discarded; and an RTDL-free verifier reproduced the
authority byte-identically. Very few papers I review have this much process.

What it establishes: the admission, provider-projection, executable-identity and
public-lifecycle framework absorbed a new protocol shape with zero byte changes,
and the resulting route produced two true OptiX launches matching twelve
independent oracle rows on an RTX 2000 Ada under OptiX 9.

What it does not establish, and what the current framing implies: that the core
*compiles* new topologies. It does not compile anything (P0-1). That the selected
topology was unseen in any strong sense. It was a recombination of a solved
primitive with a solved topology drawn from a domain of three near-identical
any-hit variants (P0-2). And the result is bound to commit `7da6805`; on the
current tree the seal verifier fails (P1-1).

Verdict: one bounded prospective framework-parametricity result, correctly
executed, mislabeled as a generality result. Keep it, reweight it, and state the
denominator.

## 8. Goal5840 refinement-evidence verdict

This is the strongest artifact produced in the review interval and I would keep
it prominent in the paper.

Independence is real, not asserted: no `rtdsl` import, no shared code, and an
explicit refusal to consume any compiler-produced projection. Depth is greater
than "structural" suggests: the checker partially evaluates generated device
source against expected role semantics rather than pattern-matching it, and it
cross-checks each role symbol against compiled ABI metadata, wrapper source and
compiled PTX simultaneously — a mismatch in any one of the three fails. The
mutation evidence is meaningful: 15 unique mutations rejected across 20 mode
applications, with 20/20 property applications passing. Six preserved failed
attempts precede the passing seventh.

Two honest qualifications the paper must carry. First, the checker is
route-hard-coded: `_check_host_status_flow` branches on
`route_id.startswith("stable::bounded_relation")` and names specific functions
such as `PreparedBoundedRelationOwner.execute` and
`verify_precanonical_bounded_relation`. It verifies three specific routes, not a
route-generic refinement relation, and a legitimate refactor would break it
without any semantic change. Second, part of what it checks is source-level
ordering — that the launch precedes the fail-closed verification which precedes
result publication, and that the verifier has exactly one guarded fail branch
before its single return. That is a real and valuable property to check
independently, and it is a property of the host program's shape rather than of
the compiled device semantics.

Verdict: bounded, non-circular, genuinely independent structural and
partial-evaluation refinement evidence over three routes, four modes and five
properties. Not a soundness theorem, and the paper already says so.

## 9. Performance and baseline-fairness verdict

Answering Section 8 in order, compactly where the answer is clean.

**8.1 — Causal chain, and did any repair special-case a benchmark?** The chain
is coherent: Goal5842 measured, Goal5842R1 repaired, Goal5843 re-measured fairly
and remained adverse, Goal5844 repaired the triangle envelope, Goal5845 repaired
relation continuation, Goal5846 repaired warm-cache startup, Goal5847 repaired
deployable AOT startup and exposed the post-import debt, Goal5848 exists to
close it against a strong baseline. I found no task-specific native kernel added
by a repair. The Goal5844 change is a value-keyed memoization of two pure digest
functions plus provenance restructuring; the Goal5845 change is device-side
deduplication in the bounded-relation execution path, available to any bounded
relation rather than to one benchmark.

**8.2 — Does Goal5844's fast path cache only immutable facts?** Yes, and I
checked this specifically because it is the obvious place for a stale-proof bug.
Both cached properties belong to `@dataclass(frozen=True, slots=True)` classes,
so the cache key is the full immutable field tuple and a cached digest cannot go
stale for a given value. Status, proof and traversal obligations are preserved;
the provider-identity relaxation is separate and is covered in P2-1. The
residual cost is memory retention, not correctness.

**8.3 — Is Goal5845's compaction generic or a disguised application kernel?**
Generic. It is deduplication over `(source_id, item_id)` in the bounded-relation
path, which is the semantics of the bounded relation itself, not of any
application. The claim that it is device-side is what fails (P0-3).

**8.4 — Is 1.0457x a fair public-envelope parity statement despite identical
device bytes?** Yes, provided the sentence says what it measures. Both arms
ultimately execute the same device program bytes, so the number is a statement
about the host-side public envelope — admission, proof serialization, identity
hashing, status handling, output publication — and nothing else. Stated that way
it is a legitimate and useful result: it shows the whole-protocol envelope need
not dominate a scalar route. State the worst block (1.1543x) alongside the
median, and confine it to one task on one GPU.

**8.5 — Is the 9.53x reciprocal useful evidence at all?** No, and not merely
because the baseline is weak. Its published causal explanation is contradicted by
the source (P0-3). Delete it from all paper-facing text. If the project insists
on retaining something, the only defensible form is a negative one: "a pinned
PyOptix arm that transfers all raw events and canonicalizes them on the host is
roughly an order of magnitude slower on this task; we do not attribute this to
RTDL and we replace this comparison with a device-continuation baseline." Arm C
is the right comparator and the paper should wait for it.

**8.6 — Does Goal5846 fairly compare warm-cache RTDL against source-compiling
PyOptix?** Present it as an engineering milestone only. The contract is
asymmetric by construction — one arm compiles from source, the other reuses a
content-addressed cache — and the project already disclosed the adverse
precompiled-PTX sensitivity (~236 ms, making RTDL ~2.44x slower) that follows
from equalizing it. The milestone is worth one sentence; the sensitivity is worth
the same sentence.

**8.7 — Does Goal5847's complete-process result have value after the CuPy
confound is disclosed?** Very little, and I would report only the adverse
post-import endpoint. A 0.229x complete-process ratio dominated by a 5.2 s
dependency import measures the baseline's packaging, not RTDL. Reporting it even
with a disclaimer invites the citation "0.23x" to escape into a summary. Report
`2.504242x` post-import, name it as open debt, and move on. This is also what
`AGENTS.md:2669` already instructs.

**8.8 — Did Goals 5844-5847 violate the prior warning against arm-specific
optimization?** No, and I confirm the project's reasoning. The distinguishing
test is whether the repair benefits only the measured benchmark or any program
on that route, and whether the pre-repair transaction survives. Both hold: the
repairs are in generic public-path code, and every adverse predecessor
transaction remains in the tree. What the project must not do is *report* the
repaired numbers without the predecessors, and so far it has not.

**8.9 — Are Arms B and C sufficiently distinct, and is work placement fair?**
Yes, and this is well designed. `strong_pyoptix.py:100-112` loads a
`goal5802_relation_unique_compact` CUBIN as a CuPy `RawModule` and binds it as a
compaction kernel, giving Arm C the device-side deduplication that Arm B lacks —
which is precisely the handicap that made Goal5845 uninformative. Arm C also
gets a validation-off OptiX context (`_make_validation_off_context`), which is
the fast configuration and therefore the fair one. I found no unfair work
placement. The one asymmetry is instrumentation gating (P3-1).

**8.10 — Is Arm D a meaningful lower bound?** Design-level yes; unverifiable
until it runs. `direct_bridge.py` (384 lines) plus
`scripts/goal5848_render_direct_worker.py` derive it, and
`tests/goal5848_direct_derivation_test.py` and `direct_bridge_test.py` cover the
derivation. The gates require exact output and physical OptiX execution for
every relevant arm, which covers matching output semantics, launch counts and
D2H obligations in principle. Confirm against receipts after the transaction.

**8.11 — Is Arm E sufficient to prove no prepared-path regression?** Yes. A
`<= 1.05x` successor/predecessor gate against the exact pre-Goal5848 RTDL
predecessor is the right control, and it is the specific defence against the
failure mode where post-import parity is bought by regressing the previously fast
prepared path. Keep it as a hard gate, not a diagnostic.

**8.12 — Are the thresholds defensible?** Mostly, with one caveat.
`C/B <= 1.05x` as a baseline-competence gate is well judged: it forces the strong
arm to actually be strong before its comparison counts, and it is falsifiable.
`A/C <= 1.20x` median with every block `<= 1.35x` is a reasonable
"reasonable bounded overhead" operationalization, and requiring a per-block bound
rather than only a median is the right choice. `A/D <= 1.20x` against a
purpose-built Direct route is the most demanding gate and the most likely to
fail; the project should decide *now* what it will report if only that gate
fails, because "RTDL is within 20% of a hand-written CUDA/OptiX implementation"
is a strong claim that a failure does not merely weaken but inverts. The caveat:
thresholds were frozen by the same team that tuned the implementation, so they
are preregistered but not adversarially set. Disclose that.

**8.13 — Does disabling CUDA and RTDL OptiX disk caches improve fairness or
create an unrepresentative deployment claim?** Both, and the distinction matters.
On fairness it is correct and I verified the symmetry:
`contracts.py:265-275` fails closed unless both `CUDA_CACHE_DISABLE=1` and
`RTDL_OPTIX_DISK_CACHE_POLICY=disabled` are set, and the PyOptix side disables
its context cache explicitly via `setCacheEnabled(False)`, with a `TypeError` if
the control is absent. Both arms consume precompiled device programs and both pay
OptiX module JIT in-process. That is symmetric. On representativeness it is not
the deployment RTDL advocates: Goals 5846 and 5847 exist precisely to exploit a
warm content-addressed cache. So Goal5848's numbers, if they pass, license a
statement about compute cost under a cold, cache-disabled configuration, and
license nothing about deployed startup. Say which one you are reporting.

**8.14 — Are eight blocks and 128 samples per arm/task/block sufficient?** Yes
for the medians and for the per-block worst-case gate, which together already
express dispersion. I would not require confidence intervals here: they would
answer no threat that the per-block bound does not already answer. Retain the
no-discard rule, which matters more than sample count.

**8.15 — Does the two-generation design establish portability?** It establishes
that the *conclusion* replicates on two RTX generations, which is the right
claim, and the refusal to pool raw times or compute cross-machine ratios is
correct. It does not establish portability across vendors, driver versions or
OptiX versions, and the paper should say "replicated on two NVIDIA RTX
generations" rather than "portable".

**8.16 — What performance sentence could be used after Goal5848 passes and
receives external review?** Only something of this exact shape:

> On a 4,096-by-4,096 bounded canonical relation returning exactly 4,096 rows
> and on a 16,384-query weighted triangle checked-U64 reduction, measured from
> the end of implementation imports to the first validated exact result, with
> driver and OptiX disk caches disabled and all arms consuming precompiled
> device programs, RTDL's public verified path was within 1.20x of a PyOptix
> implementation that performs equivalent device-side continuation and was
> itself within 1.05x of the idiomatic PyOptix route, and within 1.20x of a
> purpose-built Direct CUDA/OptiX route, with no block exceeding 1.35x, on two
> NVIDIA RTX generations.

Every clause in that sentence is load-bearing. Removing the endpoint definition,
the cache policy, the baseline-competence qualifier, the block bound, or the
task descriptions produces a claim the evidence does not support.

## 10. Goal5848 design-readiness verdict

**This is a readiness verdict only. Goal5848 has zero of two required GPU
transactions. Nothing in this section authorizes any performance statement,
gate outcome, or manuscript sentence.**

The design is sound and, on the specific attacks the request asks about, better
than I expected.

Verified favorably from the working tree:

- Timer boundaries are symmetric. Both the RTDL arm (`worker.py:343-439`) and
  the strong-PyOptix arm (`worker.py:771-799`) place workload construction,
  load, prepare, first execution and public output validation inside
  `endpoint_start .. endpoint_end`, and both feed `_sample` with matching warmup
  and repetition counts and per-result validation. Output validation is inside
  the timed region on both arms, which is the conservative choice.
- The post-import boundary is drawn correctly.
  `old_arm.preload_pyoptix_runtime()` is called before `import_ns` stops
  (`worker.py:765-768`), so the CuPy/PyOptix dependency import counts as import
  and not as endpoint. This is what makes the endpoint the honest one.
- Cache policy is symmetric and fail-closed, as detailed in 8.13.
- Failure-path ownership is properly implemented.
  `_close_rtdl_worker_resources` (`worker.py:304-326`) closes every acquired
  layer, and cleanup failures are attached with `add_note` rather than replacing
  the primary exception — so the original error is never hidden and no acquired
  resource is silently leaked. The provider-initialization path (lines 292-302)
  and the strong-adapter path (lines 817-826) follow the same pattern. The four
  tests in `tests/goal5848_worker_failure_cleanup_test.py` cover artifact-load,
  RTDL-input, preflight-input and adapter load/prepare failures, and pass.
- Authority independence is materially hardened.
  `scripts/goal5848_build_transaction_authority.py` independently reconstructs
  the preregistration (`_validate_preregistration`), the expected process
  commands including python, source, predecessor and PyOptix identities
  (`_expected_process_command`, lines 397-528), the execution context
  (`_expected_execution_context`), and device artifacts including compiler and
  NVRTC evidence (`_validate_device_artifacts_independently`, lines 590-713).
  This closes the coherent-resealing and substituted-command attacks over the
  command and artifact surfaces.

Focused tests I ran and their results:

```text
tests.goal5848_worker_failure_cleanup_test                 4 tests  OK
tests.goal5848_transaction_authority_test  +
tests.goal5848_strong_baseline_contract_test +
tests.goal5848_preregistration_controller_test            38 tests  OK
```

Residual issues, none of which I consider blocking for the transaction:

- Instrumentation gating asymmetry (P3-1). Fix before running, since it costs
  under an hour and removes a reviewer objection permanently.
- `_git_identity` shells out to `git -C <root>` at authority-build time. If the
  authority is built on the machine that produced the evidence, the git identity
  is the tree's self-report. This is inherent to the trust model the request
  already declares — an authority is not external review — and I raise it only so
  the paper does not describe the authority as independent of the producing host.
- The `<= 1.20x` A/D gate deserves a pre-agreed reporting plan for failure, per
  8.12.

Answering the request's specific question about whether the latest changes
"fully close resource-ownership and coherent-resealing/substituted-command
attacks": resource ownership, yes for the audited paths, with tests. Resealing
and command substitution, closed for the command, preregistration, worker-source
and device-artifact surfaces; not closed against an operator with write access to
the producing tree, which no in-tree mechanism can close.

Status remains exactly `IMPLEMENTED_AND_LOCALLY_AUDITED__FORMAL_GPU_EVIDENCE_0_OF_2`.

## 11. Claim-by-claim classification

| # | Statement | Classification | Required condition |
|---:|---|---|---|
| 1 | RTDL makes the complete callback protocol the compilation unit | `SUPPORTED` | CP001-CP005 are discharged as one obligation set before lowering; this is the paper's contribution and it holds |
| 2 | RTDL enforces cross-role callback invariants before GPU execution | `SUPPORTED` | Admission precedes materialize/prepare/execute; verified in the lifecycle |
| 3 | RTDL is a generic callback-protocol compiler | `NOT_YET_SUPPORTED` | Lowering and codegen are hand-written per (primitive, topology); see P0-1 |
| 4 | RTDL executes arbitrary restricted-Python callbacks on RT cores | `FORBIDDEN` | No evidence of arbitrary Callback IR execution exists |
| 5 | A schema-driven frozen core admitted one independently selected unseen topology without modification | `SUPPORTED_WITH_REWRITE` | Must define "core" as admission/identity/lifecycle excluding lowering, state the 4x3 author-defined domain, bind to commit `7da6805`, and disclose current-tree drift |
| 6 | RTDL supports all OptiX primitive types | `FORBIDDEN` | Two of six build-input kinds; bounded routes only |
| 7 | RTDL instantiates all four pinned OptiX leaf-primitive kinds in bounded public routes | `SUPPORTED_WITH_REWRITE` | Must read "one bounded route per leaf kind"; 4/4 is kind presence, never category, topology or application coverage |
| 8 | RTDL reproduces Sui et al. RT-CCD | `FORBIDDEN` | Goal5836 terminal `MATERIAL_PREDICATE_DIFFERENCE` refusal forbids it |
| 9 | A bounded collision-detection case study consumes an app-neutral owner-grouped any-hit Boolean primitive | `SUPPORTED_WITH_REWRITE` | Accurate as to app-neutrality; must disclose that the Boolean route carries no near-parallel domain guard (P1-2) |
| 10 | Independent developers can use RTDL more easily than PyOptix | `FORBIDDEN` | Zero external authors, zero usability studies |
| 11 | RTDL has negligible runtime overhead | `FORBIDDEN` | Contradicted by Goals 5842/5843 and by the open `2.504242x` post-import debt |
| 12 | RTDL is 9.53x faster than PyOptix | `FORBIDDEN` | Weak baseline and a causal explanation the source contradicts (P0-3) |
| 13 | On one exact scalar route, the repaired public envelope was within the preregistered parity bound of pinned PyOptix | `SUPPORTED` | Report worst block 1.1543x beside the 1.0457x median; one task, one GPU, identical device bytes |
| 14 | On one exact row-returning route, generic RTDL device compaction was much faster than a pinned host-continuation PyOptix implementation | `SUPPORTED_WITH_REWRITE` | "device compaction" is inaccurate — RTDL also host-canonicalizes; and the baseline must be labelled explicitly weak. I recommend deleting rather than rewriting |
| 15 | Goal5848 closes strong-baseline and post-import performance | `NOT_YET_SUPPORTED` | Zero of two formal transactions |
| 16 | The real-artifact census shows protocol bugs are prevalent | `FORBIDDEN` | Goal5839 has zero classifications; Goal5820's `0/4/16` is not paper-ready |
| 17 | RTDL's target lowering is formally proven sound | `FORBIDDEN` | Goal5840 is bounded structural and partial-evaluation evidence, not a theorem |
| 18 | A separately implemented checker found bounded structural refinement for three route groups, four modes, and five properties | `SUPPORTED` | Independence verified: no `rtdsl` import, compiler projections refused |

## 12. Required manuscript edits and evidence cuts

**Cuts, in order of danger.**

1. Delete the 9.53x reciprocal and any sentence built on Goal5845's PyOptix
   arm. Its explanation does not survive source inspection (P0-3).
2. Delete Goal5847's 0.229x complete-process ratio from all paper-facing text.
   Report `2.504242x` post-import as open debt.
3. Delete every ease, usability, productivity, learnability and "developers can"
   sentence. Zero external authors.
4. Delete the real-artifact prevalence motivation entirely. Neither Goal5820 nor
   Goal5839 supports it. Replace the motivation with constructed defect classes
   in author-controlled examples, honestly labelled as such.
5. Delete or replace the stale evaluation numbers at `main.tex:1183` and the
   surrounding table; they correspond to no current authority.

**Rewrites.**

6. Replace the generality claim with the sentence in Section 6.6 verbatim.
7. Update `main.tex:673` and `main.tex:1114-1115` — the prospective exam count is
   one, not zero, at the bounded scope defined above.
8. Update `main.tex:935` and `main.tex:650` — leaf-kind presence is 4/4, build-
   input kinds remain 2/6, stable fixed constructors remain 2, plus one
   root-exported successor route and one prospectively instantiated topology.
   Present these as four distinct denominators, never merged.
9. Add the Goal5836 terminal refusal as a reported result, in the evaluation
   section rather than in limitations.
10. Scope CP005 to load-time provider binding (P2-1).
11. Add a limitations paragraph naming, without softening: zero external authors;
    zero prevalence evidence; lowering is per-(primitive, topology) hand-written;
    the challenge domain was author-defined; the near-parallel guard covers only
    the First Contact route; the frozen core has since changed; and the native
    provider and raw capsules are not in the repository.

**Additions.**

12. Add `KNOWN_STALE_CUSTODY_CHECKS.md` (P1-1) and reference it from the artifact
    section.
13. Repair the seven dead `docs/v4/` README links (P2-4). Note that the
    `pip install -e .` instruction is fine and needs no change.

## 13. Smallest credible repair plan, ordered by submission value

1. **Rewrite the generality claim** to Section 6.6's sentence and propagate it
   through abstract, introduction, contributions and evaluation. Nothing else
   changes the paper's correctness this much for this little effort. ~3 h.
2. **Resynchronize the manuscript** with the four denominators, the new goals,
   and the corrected evaluation. This is unavoidable and is the largest single
   block of work. ~12 h.
3. **Correct the Goal5845 causal sentence** in the engineering report and in
   `AGENTS.md:2669`, and delete the reciprocal from paper-facing text. ~2 h.
4. **Decide the performance section's fate**: either run the two Goal5848
   transactions, or descope to Goal5844's parity result plus Goal5847's adverse
   post-import debt. Decide by 2026-09-07 so the writing can proceed either way.
5. **Disclose the two stale custody checks** and the off-repository binaries.
   ~2 h combined.
6. **Disclose or guard the near-parallel Boolean domain.** ~2 h for disclosure.
7. **Generalize the app-vocabulary guard and fix instrumentation gating.** ~2 h,
   both low-risk, both remove standing reviewer objections.
8. **Artifact hygiene**: dead links, legacy-module partitioning, pod endpoint
   scrubbing at packaging time. ~3 h.

Items 1-5 are the paper. Items 6-8 are the artifact.

## 14. Deadline-aware action matrix

Five submission-critical actions, ranked. Everything else appears below the
table as explicitly droppable.

| Finding | Fatal if unfixed? | Repair or descope | Est. focused hours | Exact files/evidence | Must finish before 2026-09-10? |
|---|---|---|---:|---|---|
| P0-1/P0-2 generality claim is mislabeled and its domain is author-defined | Yes — this is the claim a reviewer will attack first and the current wording does not survive source inspection | Descope: adopt Section 6.6's sentence verbatim; state the 4x3 domain and the 2,635 post-selection lines | 3 | `paper/cgo2027/main.tex` abstract/intro/contributions; `history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_TECHNICAL_REPORT.md` | Yes |
| P1-4 manuscript predates the evidence in both directions | Yes — submitting a manuscript that says prospective exams are zero and reports superseded numbers is not defensible | Repair: rewrite evaluation, coverage table and denominators | 12 | `main.tex:50,128,156,650,673,899,935,1114-1115,1183,1211,1354,1506,1564` | Yes |
| P0-3 Goal5845's causal explanation is contradicted by the source | Yes if the number is used; No if deleted | Descope: delete the reciprocal; correct the sentence in both places | 2 | `goal5845_.../FINAL_ENGINEERING_REPORT.md`; `AGENTS.md:2669`; `rtdl_optix_v4_callback_poc.cpp:6835-6860` | Yes |
| Goal5848 is 0/2 and the paper has no strong-baseline result | No — the paper can proceed reporting Goal5844 parity plus the adverse `2.504242x` | Decide: run both transactions, or descope the performance section | decision by 09-07 | `experiments/goal5848_strong_baseline/`, `GPU_RUNBOOK.md` | Decision yes; execution optional |
| P1-1/P1-3 two stale custody checks and off-repository binaries, undisclosed | No for the science; Yes for artifact evaluation | Repair: add `KNOWN_STALE_CUSTODY_CHECKS.md` and an artifact-replay statement | 2 | `tests/goal5838_core_seal_and_selection_test.py`, `tests/goal5832_protocol_shape_algebra_test.py`, both `FINAL_AUTHORITY.json` | Yes |

**Explicitly droppable before the deadline**, with the claim each drop costs:

- **Goal5839 prevalence census.** Cannot be completed. Cost: the empirical
  motivation. Replace with constructed defect classes. The paper survives; a
  protocol-compiler paper does not require a prevalence study to motivate a
  soundness gap that is demonstrable by construction.
- **Goal5841 external human authoring.** Cannot be completed. Cost: all
  usability language. The paper survives; CGO does not require it.
- **Full Sui et al. reproduction.** Should not be attempted. Cost: nothing —
  Goal5836's refusal is a better result than a forced reproduction.
- **P1-2 near-parallel guard implementation.** Two-hour disclosure substitutes.
  Cost: the case study is validated on workloads that avoid the domain by
  construction rather than by admission, which must be said.
- **P2-1 cache-lifetime cleanup, P2-2 guard generalization, P2-3 legacy
  partitioning, P3-1 instrumentation symmetry.** All post-deadline except where
  a one-hour fix is convenient. Cost: nothing to the science.

I recommend against spending any remaining time on evidence infrastructure. The
infrastructure is already stronger than the claims it supports; the deficit is
in what the claims say, not in how well they are sealed.

## 15. Final verdicts

- **A. Architecture and bounded generalization** — `ACCEPT_WITH_BLOCKING_FIXES`

  The compilation-unit insight is sound and the admission/identity framework is
  genuinely topology-parametric. The generality claim as currently worded does
  not survive source inspection and must be rewritten before submission
  (P0-1, P0-2), and the frozen-core drift must be disclosed (P1-1).

- **B. Sphere/curve/collision architecture boundary** — `ACCEPT_WITH_BLOCKING_FIXES`

  Built-in geometry is genuine and fail-closed, the engine/application boundary
  is correctly drawn, and the owner-grouped Boolean behaviour is honestly
  generic. The near-parallel domain exclusion is not enforced on the route the
  case study uses and must be guarded or disclosed (P1-2).

- **C. Independent lowering/refinement evidence** — `ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS`

  Non-circular, genuinely independent, deeper than its label. Keep it and keep
  its stated bounds.

- **D. Committed performance evidence through Goal5847** — `ACCEPT_WITH_BLOCKING_FIXES`

  The causal chain is real, the repairs are generic, and adverse-result custody
  is exemplary. One published causal explanation is contradicted by the source
  and must be corrected, and the 9.53x reciprocal must be deleted (P0-3).

- **E. Goal5848 experiment design and implementation readiness** — `ACCEPT_POST_REVIEW_PROGRESS_WITH_SCOPED_CLAIMS`

  Readiness only. Symmetric timers, symmetric fail-closed cache policy, a
  genuinely strong Arm C, sound failure-path ownership, and an authority that
  independently reconstructs the preregistration and worker commands. Formal
  evidence remains `0/2` and no performance statement is authorized.

- **F. Current CGO submission readiness** — `ACCEPT_WITH_BLOCKING_FIXES`

  The manuscript contradicts the evidence in both directions, two custody checks
  fail undisclosed, and the artifact has dead links and off-repository binaries.
  All are repairable in the remaining time.

**Overall recommendation: `PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED`**

A scientifically defensible CGO 2027 submission is achievable by 2026-09-10.
It is a whole-protocol admission-and-identity paper with hand-written
per-topology back ends, one bounded prospective framework-parametricity result
with its denominator stated, bounded independent refinement evidence, a bounded
application-neutral case study, and a performance section that reports one
exact-task envelope parity result and one open adverse post-import debt. It is
not a generic-compiler paper, and the five blockers above are what stand between
the current bytes and the defensible one.
