# MacBook continuation handoff: pre-Goal5836 RT-CCD/CGO checkpoint

Date: 2026-08-31 (America/New_York)  
Purpose: allow a new model/session on a MacBook to continue without repeating
finished work, changing scientific scope, or confusing a platform limitation
with a research result.  
Status: **Goal5833, Goal5834-B3, and Goal5835 are complete at their declared
bounded scopes. Goal5836 remains locked.**  
External review: **not authorized; do not send anything for review.**  
Performance: **not authorized; do not collect timings.**

## 0. Read this first: the one-line handoff

The next agent must first finish the interrupted, hostile **pre-Goal5836
review**. It must not start author-code acquisition, change product source,
use a POD, or promote Goal5835 to a Paper App until it has written a local
review that explicitly decides whether a separate Goal5836 preaction may be
created. The research target is a bounded CGO case study, not production RT-CCD
software and not a full robot stack.

## 1. Select the correct workspace before doing anything

The completed work is in this Windows directory:

```text
C:\Users\Lestat\Desktop\work\rtdl_v4_restricted_python_design
```

It is **not** in:

```text
C:\Users\Lestat\Desktop\work\rtdl_v0_4_release_prep_review
```

The Codex application has previously opened the second directory by default.
That mismatch can make the project appear to jump backwards in time. On the
Mac, define one explicit root and never infer it from the app's default CWD:

```bash
export RTDL_REPO=/absolute/path/to/rtdl_v4_restricted_python_design
cd "$RTDL_REPO"
test -f history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_result_20260830.json
test -f case_studies/sui_derived_edge_crossing_core/bounded_piecewise_linear_core.py
```

If either check fails, stop: the wrong or incomplete workspace is open.

### 1.1 Git is not the current state authority

The Windows working tree currently reports:

```text
git rev-parse HEAD
1af120d187228035db733ce690de3a3bf5b54ee5

git status --short
fatal: bad object HEAD
```

Therefore:

- do not say the Goal5833--5835 work is committed;
- do not use `git pull`, `git checkout`, `git reset`, or a branch name to
  reconstruct the current state;
- transfer/copy the exact working snapshot and verify the file hashes below;
- do not repair Git as a side task during the CGO evidence window;
- if a clean Git lineage is later required, create a separately named recovery
  goal after preserving this exact snapshot.

The apparent `rev-parse` value is historical metadata, not proof that the
working files belong to that commit.

### 1.2 The project in two minutes

RTDL V4 is a restricted-Python research DSL/compiler for **repurposed
ray-tracing applications**: programs that use OptiX/RT hardware for graph,
database, geometry, particle, nearest-neighbor, collision, or similar
non-rendering computation. It does not claim to invent those RT algorithms.

The research problem is that an OptiX application is not one kernel. Its
meaning is distributed across ray generation, intersection, any-hit,
closest-hit, miss, exception/callable roles, payload/attribute slots, SBT/GAS
bindings, launch parameters, device status, and the exact executable loaded.
CUDA, OptiX validation, PyOptiX, and OWL can accept a locally well-formed
program while these pieces disagree semantically. Rendering often tolerates or
visually masks small mistakes; repurposed computation consumes payloads and
status as exact application data, so a silent mismatch can change counts,
indices, relations, or collision decisions.

RTDL's central idea is:

> Treat the complete callback protocol, rather than an individual shader or
> host wrapper, as the compilation and checking unit.

The contribution is a **mechanism plus an executable research prototype**, not
a new sorting/collision/nearest-neighbor algorithm. Its five current residual
mechanism classes are:

1. cross-role payload/attribute meaning and ownership;
2. role/effect production and consumption closure;
3. logical protocol to physical GAS/SBT/program/buffer binding;
4. fail-closed device status before output consumption; and
5. exact executable/program identity binding.

The mechanism is conceptually portable to another RT API such as Vulkan RT or
DXR, but the current implementation/evidence is OptiX-specific. The Callback
IR supplies the backend-neutral semantic vocabulary; the OptiX provider proves
one concrete realization. Do not convert that architectural possibility into
a demonstrated Vulkan/DXR result.

### 1.3 Why another system when PyOptiX and OWL exist?

PyOptiX exposes OptiX from Python. OWL productively owns program, GAS, pipeline,
SBT, memory-transfer, and launch composition. Those are real strengths and
must not be attacked or denied. RTDL's claimed residual is different: neither
abstraction, in the examined public paths, makes the **application's complete
cross-program semantic protocol** a checked object with the five obligations
above.

The clean comparison is therefore not “RTDL replaces OWL” or “RTDL is easier
than PyOptiX.” It is:

> Even when a mature abstraction owns RT plumbing, whole-protocol semantic
> defects can remain; RTDL makes those obligations explicit and rejects the
> mismatch before launch.

Platform-native `OptixPayloadType`/`OptixPayloadSemantics`, DXR PAQ, and Vulkan
cross-stage interface rules are relevant related work. They constrain access
and stage interfaces but do not automatically establish nominal application
meaning, attribute-slot semantics, cross-role production order, physical
binding, status-before-consume, or executable identity. Every final paper
claim must state the exact residual instead of pretending the platform has no
checks.

### 1.4 What evidence exists before Goal5836?

The project has substantially more evidence than this one case study, but the
claim boundaries matter:

- a formal restricted-Python Callback IR, verifier, deterministic CPU
  interpreter, canonical ABI/layout compilation, trusted PTX composition, and
  public materialize/prepare/execute/close paths;
- all seven OptiX callback roles represented in the IR/mechanism;
- nine author-written repurposed applications at the earlier V4 functional
  checkpoint, plus later illustrative sorting, sphere, curve, and bounded
  collision work;
- five single-mechanism semantic mutations that OptiX validation accepted and
  RTDL rejected, with exact outputs frozen before execution;
- populated-leaf liveness campaigns added after an earlier inert
  `roles[].effects` defect was honestly discovered;
- public PyOptiX/OWL responsibility analysis and matched performance work.

The currently defensible performance summary is scoped to two matched tasks on
one RTX 4000 Ada:

- RTDL showed a one-time setup delta of roughly 162--223 ms relative to the
  matched PyOptiX arm in the deployment-cold/prepare regimes;
- under that experiment's resolution, no additional per-execution cost was
  detected;
- Python-host OptiX routes were much slower than expert direct C++ in those
  tiny tasks, but most of that gap was shared by PyOptiX and RTDL and must not
  be attributed to checking without a checker-off causal ablation.

Do not rewrite this as zero overhead, performance neutrality, admission cost,
or superiority over CUDA/OptiX.

### 1.5 The two existential concerns

The owner has repeatedly required honest answers to two questions.

**Concern A -- only works on author-tested cases.** The project has strong
anti-overclaim controls, but prospective new-application generalization remains
zero. Sphere/curve extend platform-interface coverage and Goal5835 adds a
materially different robotics-derived mapping; none is an unseen-app exam.
Goal5836 may produce a bounded paper-source same-input application result, not
universal generalization.

**Concern B -- unusable compared with direct CUDA/OptiX.** No third-party user
study exists, all applications were author written, and no claim that RTDL is
easier or more productive is authorized. The public lifecycle is now usable by
the authors, but usability evidence remains zero. The paper's value must rest
on making a class of protocol errors rejectable, not on unsupported LOC or
ease claims.

### 1.6 Immediate CGO priority

The submission deadline is fixed at 2026-09-10. The project must submit an
honest bounded paper even if the evidence does not reach strong-accept level.
At this checkpoint the highest-value missing case-study evidence is one exact,
paper/source-derived, same-input author/RTDL/oracle result on modern RTX. That
is Goal5836. Production engineering, broad API cleanup, full RT-CCD, and new
performance programmes are lower priority than paper/source fidelity and the
bounded correctness experiment.

## 2. Scientific status at handoff

### 2.1 Goal5833: built-in sphere public route

Completed at bounded First Contact scope. It uses the public lifecycle and the
OptiX built-in sphere path, with an independent CPU oracle and Home behavioral
OptiX evidence. It is an author-designed qualification, not an unseen-app
generalization result and not performance evidence.

### 2.2 Goal5834-B3: built-in round-linear curve Boolean route

Completed at registered-fixture Boolean collision scope:

- fixed app-neutral `curve_any_contact_boolean_source()`;
- built-in `OPTIX_PRIMITIVE_TYPE_ROUND_LINEAR`, not a custom intersection;
- 10 fixture families, 11 concrete executions;
- 11 primary + 11 repeat + 11 reverse-order functional launches;
- 33 successful behavioral true-OptiX launches on Home GTX1070;
- 11/11 Boolean vectors match the independent capsule oracle;
- a second active-set algorithm matches all 21 frozen query/capsule pairs;
- zero status failures and zero performance samples.

The exact Home environment was Linux host `lx1` at `192.168.1.20`, GTX1070,
driver `580.173.02`, compute capability 6.1, OptiX 9.0.0, CUDA 12.0. This is
behavioral OptiX evidence, **not modern RT-core-silicon evidence**.

Two terminal failures are part of the record and must not be erased:

1. B1 reused a single-use verified curve executable across static scenes and
   correctly failed on live-registry identity drift.
2. B2 discovered that repeated same-process NVRTC materialization changes
   comment-only `callseq` values in wrapper/composed PTX. B3 solved this by one
   exact materialization followed by sequential fork-private children; it did
   not strip comments or weaken executable identity.

### 2.3 Goal5835: bounded Sui-derived edge-crossing mapping

Completed status:

```text
GOAL5835_COMPLETE_BOUNDED_SUI_DERIVED_EDGE_CROSSING_MAPPING
```

Implemented application mapping:

```text
piecewise-linear sphere trajectory
  -> one swept capsule per path segment
  -> one built-in round-linear curve per capsule

triangle-mesh boundary or registered obstacle edge
  -> deterministic finite edge query
  -> sealed per-edge GPU hit bit

collision = OR(per_edge_hit)
```

For all 11 registered executions, Goal5835 reconstructs exact public static
and query commitments equal to the already executed Goal5834-B3 bytes. Those
sealed GPU bits match a new, RTDL-free active-set oracle. The result honestly
records zero new Goal5835 GPU launches and 33 inherited B3 launches.

Current mandatory labels:

```text
paper_app_status: NOT_A_PAPER_APP
source_relation: SUI_DERIVED_MAPPING__AUTHOR_DESIGNED_FIXTURES
generalization_exam_count: 0
registered_performance_timing_count: 0
```

Do not upgrade or paraphrase these labels.

## 3. Exact claim boundary for CGO

The strongest currently supported statement is:

> RTDL's app-neutral callback-protocol mechanism has public built-in sphere and
> round-linear-curve instantiations. On a small, author-designed registered
> corpus, the curve route executes a bounded robotics-derived predicate in
> which piecewise-linear sphere motion is represented as capsules and finite
> obstacle edges are queried for contact; sealed GPU Boolean vectors agree
> with two independent CPU geometry calculations.

The following are false or unsupported today:

- full Sui/Sentis/Bylard RT-CCD reproduction;
- complete sphere-versus-triangle collision;
- collision confined to a triangle face interior;
- initial-overlap/start-inside support;
- near-tangent or near-parallel support;
- exact time of impact or collided-object identity output;
- a paper-source fixture or same-input author-code comparison;
- a new-app prospective generalization exam;
- a third-party user/usability result;
- modern-RTX execution for this mapped application;
- any performance, ease-of-use, productivity, or no-overhead result.

The value for the paper is narrower but real: the same whole-protocol
mechanism has crossed two additional platform-produced intersection
interfaces and has been instantiated in a non-rendering robotics predicate
without adding Sui-specific dispatch to generic RTDL source.

## 4. Exact files and hashes that define the checkpoint

Use `shasum -a 256 <path>` on macOS. The following hashes were rechecked on
Windows immediately before this handoff.

### 4.1 Controlling evidence

```text
0f13ab8a7408c253114c56a51645c015d0e5e36ca96a4290c9dd1a2ba700adad  history/internal_docs/goal5834_b1_fixture_preaction_20260830/FIXTURE_AUTHORITY.json
55eeff377c93c32fed8cc326ad975cb9d2437df85812e30b9d916b3e7cc581a4  history/internal_docs/goal5834_b1_fixture_preaction_20260830/WORKER_INPUTS.json
b50043e81713aacf6a70986a6e334789cbfeef17342ae97a8ae401ab1507f513  history/internal_docs/goal5834_b3_home_result_20260830/RAW_GPU_RECEIPT_B3.json
786ebd4970dadf842c57aa6c08539694d0cdbe8a6b2f6672932029b5f19be02a  history/internal_docs/goal5834_b3_home_result_20260830/INDEPENDENT_EVALUATION_B3.json
ae370da1ca5ac96562d0956438e7c6c8eee39fddf2d9894953db8e956c47ccff  history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_result_20260830.json
```

Goal5835's separately generated recount is byte-identical to the last file.

### 4.2 Goal5834 product/oracle source

```text
a0ccb359a2e759ca4c86a2569c0c36c2a73d905a6a66145ada9a02a05ead524a  src/rtdsl/v4_curve_physical_schema.py
23cb357263c3b2343738d3b1019ce8caa091e82f17e8dcc9b01b8e4c76382502  src/rtdsl/v4_builtin_curve_standard_library.py
4a8a75fcfdd597f4a07c754af9a4bba115129d0f30da5cc3f0d70f7d70f28f01  src/rtdsl/v4_sphere_optix_wrapper_codegen.py
176cef4ce6e8a7c4a56e5d813e11d7c52d3c6cc118bee8372c90a65a7304aaf9  src/rtdsl/v4_curve_optix_wrapper_codegen.py
3ec1f0903ad22290e4f8013ef4a2eff6e1fa35d22a7710861f6e080105320523  src/rtdsl/v4_public_builtin_curve.py
98c698048501713d46dab03335774bf7ba15ee3fffeec529dbef43975e48a5ed  src/rtdsl/v4_curve_prepared_runtime.py
9fe88e6669ea4fe1edccf4e73659dfc80a8c7c113b5212859eff14240d446b85  src/rtdsl/v4_curve.py
61111750c21441bea1e5547a86bca1e1b8f24c48152f172f46ea72295b46ddfb  examples/curve_boolean_contact/independent_oracle.py
543d5e4c00e2451621ffb497e1582a59b193385216efd6ba79339c8a83eb4844  examples/curve_boolean_contact/fixtures.py
```

### 4.3 Goal5835 case-study source

```text
65e61185117a9cb052a1b4a6c29cc83346f9405911231784b7f2cd8b5eb0952f  case_studies/sui_derived_edge_crossing_core/bounded_piecewise_linear_core.py
1eb825e6d528185013eaff960ebd28ca3cfd3c2e068bdd928c014dc80e8e7a97  case_studies/sui_derived_edge_crossing_core/independent_edge_capsule_oracle.py
a204010d9bd2794da6fb1972f895232e4e51f0549bf82028e3891871de471bc5  case_studies/sui_derived_edge_crossing_core/fixtures.py
ceb038092790f6a54ae84f455021769f00f42a618da8e84c7192b404a778717c  case_studies/sui_derived_edge_crossing_core/run_functional_receipt.py
b8ff0817518785635d005665601b7590664e01a1854a860d39ea604e290abdbd  case_studies/sui_derived_edge_crossing_core/README.md
```

### 4.4 Focused tests

```text
fb8bd0b296661d309bc3f76eac8b604f9f407f9be1991b465bc4ff6c5df58bc4  tests/goal5834_b1_curve_boolean_specialization_test.py
05965708d5170619faace6e07f91e60864392419772b7df263ab77ebc85f0885  tests/goal5834_b1_boolean_fixture_oracle_test.py
d3e7b7916073044e7749933ef0aa965b64e7f855b7c0353e8a65480e25cf8696  tests/goal5834_b3_independent_geometry_crosscheck_test.py
2d6fc8c6ea8f89bb9506a921a65af457826824ba7b380480c9f77fe519e360c0  tests/goal5835_sui_derived_edge_crossing_mapping_test.py
```

If a hash differs, do not silently overwrite either copy. Preserve both,
identify whether the transfer, line endings, or source actually changed, and
report the exact delta.

## 5. MacBook bootstrap and verification

macOS has no NVIDIA OptiX execution path. It is suitable for source analysis,
paper/author mapping design, oracle work, tests, evidence schema design, and
Goal5836 preaction construction. It cannot produce the modern-RTX result.

### 5.1 Local environment

The package declares Python `>=3.10`; the last Windows verification used
Python 3.11.9. Use a clean virtual environment and record the exact version:

```bash
cd "$RTDL_REPO"
python3 --version
python3 -m venv .venv-goal5836
source .venv-goal5836/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
export PYTHONPATH="$RTDL_REPO/src:$RTDL_REPO"
```

Do not install CUDA/OptiX emulators or create a fake GPU result on macOS.

### 5.2 Baseline tests

Run:

```bash
python -m unittest discover -s tests -p 'goal583[3-5]*_test.py'
```

The transferred Windows checkpoint is:

```text
Ran 102 tests
OK
```

That exact count is the expected scientific denominator, but it has not yet
been qualified on macOS. A Mac-only failure is a portability observation, not
permission to change product semantics. Preserve the traceback and determine
whether the test assumes Windows path syntax, Linux ELF/OptiX availability, or
actual platform-neutral behavior.

The first Windows rerun accidentally omitted the `src` import root and produced
one `ModuleNotFoundError`; after `PYTHONPATH=src:<repo>` the exact suite passed
102/102. Do not report the import-command mistake as a product failure.

### 5.3 Cross-machine receipt caveat

`case_studies/sui_derived_edge_crossing_core/run_functional_receipt.py` embeds
absolute source paths in `application_sources`. Therefore a Mac reconstruction
can be semantically identical while its complete JSON bytes differ from
`ae370da1...`.

Rules:

- preserve the frozen Windows result and recount unchanged;
- do not edit them to carry Mac paths;
- do not claim cross-machine byte identity for Goal5835;
- compare source hashes and semantic fields when auditing on Mac;
- every new Goal5836 artifact must use repository-relative logical paths plus
  content hashes, with absolute execution paths in a separately labelled
  non-identity diagnostic field if they are needed at all.

This is a known portability defect in evidence serialization, not evidence
that the collision predicate changed.

## 6. The first task on the MacBook

### Task name

```text
PRE-GOAL5836-A1__HOSTILE_REVIEW_AND_PREACTION_DECISION
```

### Objective

Finish the strict review that was interrupted by this machine handoff. Produce
one local report; do not change product source while reviewing. The report may
do exactly one of the following:

1. authorize creation of a Goal5836 **preaction only**;
2. require bounded fixes before that preaction; or
3. refuse Goal5836 if the paper/source mapping does not support the selected
   edge predicate.

It may not authorize a POD, GPU worker, performance sample, Paper App label,
or external review.

### Read in this exact order

1. this handoff;
2. `AGENTS.md` and the first relevant Goal5833--5835 sections of
   `memory/progress.md`, `memory/roadmap.md`, `memory/todo.md`, and
   `memory/known-bugs.md`;
3. `history/internal_docs/goal5833_goal5836_sphere_curve_rtccd_owner_replan_20260830.md`;
4. `history/internal_docs/goal5834_b1_goal5835_cgo_rtccd_boolean_bridge_implementation_plan_20260830.md`;
5. `history/internal_docs/goal5834_b3_boolean_collision_bridge_technical_report_20260830.md`;
6. `history/internal_docs/self_review_goal5834_b3_boolean_collision_bridge_20260830.md`;
7. `history/internal_docs/goal5835_sui_derived_edge_crossing_mapping_technical_report_20260830.md`;
8. `history/internal_docs/self_review_goal5835_sui_derived_edge_crossing_mapping_20260830.md`;
9. the five case-study source files and four focused tests listed above.

### Required hostile questions

The review must answer these with code/evidence, not optimism:

1. **Paper fidelity:** does the pinned Sui author source actually implement the
   same directed mesh-edge versus swept-sphere/capsule predicate, or have we
   inferred a convenient subset from secondary description?
2. **Width semantics:** in the exact OptiX 9 API/provider used here, do the
   curve width buffers encode the radius assumed by the CPU capsule or a
   different physical convention? Bind the answer to official interface/source
   evidence and the executed provider path; do not answer from memory.
3. **Mesh completeness:** which collision configurations are detected by edge
   queries, which require discrete endpoint/pose checks, and which face-interior
   configurations remain impossible? Never rename edge crossing as complete
   sphere-triangle CCD.
4. **Evidence independence:** confirm that GPU workers contain no expected
   output or CPU geometry, that the raw vector was sealed before evaluation,
   and that Goal5835's active-set oracle is algorithmically separate from the
   primary Goal5834 oracle.
5. **Composition validity:** is equality of exact public commitments sufficient
   to bind Goal5835 application objects to B3 execution, without pretending
   that zero new app-wrapper launches are new hardware evidence?
6. **Frozen-input relevance:** do the positive cases include a complete
   mesh-derived positive edge crossing? Today the answer appears to be no; this
   is a Goal5836 requirement, not something to hide.
7. **Type/identity boundaries:** determine whether permissive Python values for
   `sphere_id`/`path_segment_id`, duplicate triangle IDs, degenerate triangles,
   or the single-u32 physical identity can alter the exact Goal5836 scientific
   mapping. Fix only a load-bearing defect; do not turn the sprint into API
   polish.
8. **Cross-machine custody:** ensure no new result identity depends on Windows
   or Mac absolute paths.
9. **Claim test:** write the exact strongest sentence that remains true if the
   author binary cannot build or disagrees.

### Observations already made before interruption

The partial review established only the following:

- no immediate evidence cycle was found: B3 workers had no expected output,
  the Goal5835 oracle imports no RTDL module, and public commitments bind the
  mapped bytes to the old GPU execution;
- the implementation explicitly labels face-interior-only collision as a miss
  and `NOT_A_PAPER_APP`;
- exact author paper/source bytes are not present in this workspace; only the
  planned repository URL and commit are recorded;
- the width/radius physical convention had not yet been independently checked
  against the official OptiX interface when the review was interrupted;
- Python type guards may be incomplete for non-integer numeric IDs, and mesh
  objects do not yet reject every degeneracy/duplicate identity. These are
  review leads, not established P0/P1 findings;
- the Goal5835 whole-file receipt is path-dependent across machines.

Do not promote any lead to a finding without a reproducing counterexample and
an impact on the declared scientific scope.

### Output file

Recommended path:

```text
history/internal_docs/self_review_pre_goal5836_macbook_handoff_a1_20260831.md
```

The report must contain `P0/P1/P2/P3`, a clear GO/NO-GO for **preaction only**,
and the exact unresolved facts. Do not call it an external review or CFR.

## 7. Goal5836 only after a new owner GO

The controlling source plan names:

```text
paper: Sizhe Sui, Luis Sentis, and Andrew Bylard,
       Hardware-Accelerated Ray Tracing for Discrete and Continuous
       Collision Detection on GPUs, ICRA 2025, 16133--16139
repository: https://github.com/Ssz990220/RTCollisionDetection
planned commit: bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7
planned license: MIT
```

These values are planning claims until the exact paper bytes, Git object, and
license bytes are locally acquired and hashed. The current workspace contains
no author checkout. Acquisition itself remains locked until the owner approves
Goal5836 or its preaction.

When authorized, Goal5836 must be staged as follows.

### 7.1 Local/macOS stage: source and experiment freeze

1. Pin and hash the paper PDF, author commit, license, and selected source
   files. Preserve fetch receipts; never update a pin to match returned bytes.
2. Locate the exact author path that defines geometry, edge direction,
   trajectory/capsule representation, collision Boolean, and any discrete
   endpoint checks.
3. Select one small, robust, paper/source-derived common input **before** seeing
   RTDL or author output. A complete mesh-derived positive edge crossing is
   mandatory because Goal5835 has none.
4. Freeze three independently implemented routes:
   author adapter, RTDL public adapter, and stdlib-only CPU oracle.
5. Freeze mappings to exact input bytes, output predicate, status rules,
   driver/toolchain target, worker count, and no-replacement rule.
6. Freeze unconditional branches for agreement, scientific mismatch,
   author-build failure, mapping failure, unsupported capability, and
   infrastructure invalidity.
7. Build all CPU-only, schema, hostile, and materializer tests on Mac. Do not
   simulate OptiX.

The desired scope is deliberately bounded: one paper-derived piecewise-linear
collision core sufficient for a CGO application case study. Do not add URDF,
full Franka kinematics, B-splines, production batching, every paper scene, or
performance merely to look complete.

### 7.2 Linux/modern-RTX stage: later, after a separate execution gate

Only after all local bytes and branches are frozen:

- use one modern NVIDIA RTX Linux host/POD;
- verify exact GPU, driver, CUDA, OptiX, author source, RTDL source, generated
  source, native binary, and input hashes before worker zero;
- run the author route, RTDL public route, and independent recount on exactly
  the frozen common input;
- preserve true-OptiX receipts proving built-in sphere/curve use;
- collect functional correctness only, with zero timing fields;
- accept disagreement or author-build failure without replacing the case.

The Mac user should request a POD only when a sealed execution bundle and a
zero-worker preflight command are ready. **No POD is needed now.** Home Linux
may be useful for an untimed smoke if reachable, but it cannot replace the
modern-RTX Goal5836 gate.

### 7.3 Paper-App promotion gate

Paper App status requires all of:

1. exact paper and author-source provenance;
2. faithful, frozen same-input mapping;
3. successful author execution;
4. RTDL public-lifecycle execution;
5. author/RTDL/oracle agreement or a scientifically resolved difference that
   does not change the frozen rule;
6. independently recountable identity/custody evidence;
7. all limitations and negative cases visible;
8. no performance inference.

If any item fails, report the strongest lower status. Never repair the wording
to convert a failed gate into a Paper App.

## 8. Work that is explicitly a waste of the CGO window

Do not spend time on:

- production API polish unrelated to the frozen common input;
- fixing the broken Git object graph;
- general arbitrary Callback-IR-to-GPU compilation;
- supporting all OptiX curve variants, motion blur, instancing, or recursion;
- performance infrastructure or benchmarking;
- human usability studies during this goal;
- full RT-CCD/robotics stack reproduction;
- rewriting old Goal5834/5835 artifacts for path portability;
- a new external review package;
- broad type cleanup unless a concrete Goal5836 input exploits the defect.

The highest-value work is paper/source fidelity, one exact same-input
three-route experiment, and preservation of the claim boundary.

## 9. Non-negotiable safety and honesty rules

1. No external review without a new explicit owner command.
2. No POD or GPU worker before a separately frozen execution gate.
3. No performance samples anywhere in Goals5833--5836.
4. Never call Goal5835 a Paper App or a generalization exam.
5. Never call edge crossing complete triangle/robot CCD.
6. Never treat macOS inability to run OptiX as a negative scientific result.
7. Never use old B3 launches as if they were new Goal5836 application runs.
8. Never change inputs, thresholds, margins, or output predicates after seeing
   author/RTDL results.
9. Never let an oracle or expected output enter the GPU worker process.
10. Never claim a commit while `git status` reports `bad object HEAD`.

## 10. Handoff acceptance checklist

Before the new session claims it is ready to continue, it must report:

```text
[ ] exact RTDL_REPO path
[ ] five controlling evidence hashes match
[ ] Python and macOS version recorded
[ ] baseline Goal5833--5835 test denominator and outcome recorded
[ ] Goal5835 remains NOT_A_PAPER_APP
[ ] Goal5836 remains locked
[ ] no external review/POD/performance action occurred
[ ] interrupted hostile review resumed at Section 6, not restarted from history
```

At that point the receiver can work immediately on the pre-Goal5836 review.
The next owner decision should be based on that report: either authorize a
bounded Goal5836 preaction or keep Goal5835 at its honest current scope.
