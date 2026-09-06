# RTDL CGO 2027 final action plan after the GPT-6 and Claude reviews

Date: 2026-09-06

Author: Codex, after an independent reread of the named reviews, relevant
source and protocol, followed by comparison against the GPT-6 remediation
plan

Status: `PLAN_FOR_REVIEW__REMEDIATION_NOT_YET_EXECUTED`

Execution verdict:
`PROCEED_TO_BOUNDED_REMEDIATION__SUBMISSION_REMAINS_CONDITIONAL`

Execution-contract amendment (2026-09-06): the reviewed 773-line version is
preserved as Git blob `98cfa4e85d435e9cb246eb0ffe4060c5bf31ac4f` and SHA-256
`6c3b1722b07a6e13d664a3f448f5d70ab1ac80fbe8bd413f94ff4b1d05a25136`.
The current version applies the four mandatory P2 corrections in
`strict_review_codex_final_action_plan_goal5851_20260906.md`, as directed by
`lead_execution_directive_post_goal5851_20260906.md`. The amendments bind the
successful rehearsal to final F, separate frozen templates from generated
outputs, preserve minimum adverse lifecycle disclosure in the main paper, and
distinguish the eligible curve candidate from the actually selected sphere
topology. These amendments modify execution mechanics and factual wording;
they do not report R0-R8 work as completed.

## 1. Purpose and exact inputs

This plan answers one question: what is the smallest rigorous sequence that
can turn the post-Goal5851 repository into a defensible CGO 2027 submission
without changing the measured implementation, hiding adverse evidence, or
claiming more than the source and retained bytes establish?

I read the inputs in the requested order:

1. GPT-6 review:
   `history/internal_docs/codex_review_post_goal5851_cgo2027_20260906.md`,
   SHA-256
   `83ed4c27b95fffdbcddce1fcd8193dcfd594ef3647cd895feb036f2de2094fed`.
2. Claude review:
   `history/internal_docs/review_post_goal5851_cgo2027_20260906.md`,
   SHA-256
   `f27bd7422a21015c3387c154de1d44507fb02c0a244b67d55a7a462fc5b3bdc9`.
3. Only after forming the independent judgment in Section 3, the GPT-6
   execution plan:
   `history/internal_docs/cgo2027_post_goal5851_remediation_execution_plan_20260906.md`,
   SHA-256
   `1be752a1026b5a499bd666f06e368977155dd2a065d8c316b153a1614cec6fdd`.

I then read the plan-referenced absorption record to identify already-known
reviewer-text errors, but did not use it as a substitute for the source audit:
`history/internal_docs/codex_claude_post_goal5851_review_absorption_20260906.md`.

Snapshot when this plan was prepared:

| Item | Value |
| --- | --- |
| Repository | `/Users/rl2025/rtdl_v4_restricted_python_design` |
| Branch | `codex/cgo-goal5836-handoff` |
| HEAD | `04bd1d54f4641f12b6cf8e19a9e9eef5767a2021` |
| HEAD tree | `06966bf16ea8ab1a2e8027543d8c00985c7389a6` |
| Measured source M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` |
| Measured tree | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` |
| Hard development freeze | 2026-09-08 00:00 America/New_York |
| CGO R2 deadline | 2026-09-10 AoE |

At plan start, `memory/decisions.md`, `memory/progress.md`, and
`memory/todo.md` were already modified by another process. Five review/plan
documents were untracked. I did not modify or stage any of them. R0 must
recapture this inventory because it is not safe to assume the same state at
execution time. In particular, `git add -A` is forbidden.

The official CGO page currently confirms an 11-page text limit excluding
references, ACM SIGPLAN format, anonymous double-blind PDF, Letter paper,
review line numbers, black-and-white readability, English text, and separately
uploaded anonymized supplementary material. The official second-round date is
10 September 2026 AoE. These rules must be rechecked at R8 rather than treated
as immutable project memory:
`https://2027.cgo.org/track/cgo-2027-papers`.

## 2. What both reviews establish

The reviews agree on the following high-value conclusions.

| Question | Consensus |
| --- | --- |
| Is there a real compiler contribution? | Yes, if framed as bounded whole-protocol compilation/admission: schema-parametric admission, planning, identity, provider binding and lifecycle, with compiler-owned topology-specific lowerers. |
| Is executable lowering topology-generic? | No. The paper must state the trusted topology-specific implementation and TCB cost. |
| Does Goal5838 prove broad generality? | No. It is one past-tense prospective compositional extension over a frozen, author-defined ten-row domain. |
| Is Goal5840 a general semantic proof? | No. It is a separately implemented finite structural check over named routes, modes and properties. |
| Do the final GPU numbers reconstruct? | Yes. The same `d653fe4` source passes the registered machine contracts on RTX 4090 Ada and RTX 3090 Ampere, with zero retry/discard. |
| What is the strongest performance statement? | For an implementation tuned using two frozen workloads, the prepared public RTDL path has four task-by-GPU median RTDL/Direct ratios spanning `1.076852x` to `1.175066x` across two GPU generations. This is a bounded median-tax observation, not speedup or universal parity. |
| Is the current manuscript submit-ready? | No. Its architecture, counts, experiment, hardware, performance and artifact sections are stale. |
| Is more application or GPU optimization required? | No. Further tuning would deepen adaptivity and displace the actual deadline work. |
| Are usability and real-world prevalence established? | No. Delete those claims; do not rush a weak study. |
| Is the artifact ready? | No. Raw evidence is strong, but the anonymous, portable, layered delivery and actual replay logs do not yet exist. |

## 3. Independent adjudication before reading the GPT-6 plan

### 3.1 Receipt-before-publication

The GPT-6 review is correct about the literal protocol mismatch, while Claude
is correct about the narrower semantic consequence.

The original Goal5848 contract says:

- output is unavailable until native status and the compact execution receipt
  pass validation; and
- every execution records launches, raygen count, traversable identity, output
  digest and monotonic execution identity.

Current `d653fe4` instead does the following on the ordinary triangle replay:

1. checks the public owner/process/thread/reentrancy boundary;
2. runs native replay;
3. synchronously rejects nonzero native status;
4. reads and synchronously gates compact status;
5. reads the scalar and checks the exact oracle when supplied;
6. returns a result whose detailed `_FastPathReceipt` validation is deferred;
7. runs one separate diagnostic execution after the formal sample loop.

The formal worker validates every returned task result against the frozen
output contract, but it does not expand and persist a complete physical receipt
for every timed invocation. The separate diagnostic receipt cannot be relabeled
as 128 per-sample receipts. `_FastPathReceipt` also does not itself carry all
the raygen, traversable, output-digest and monotonic-identity fields named in
the original written invariant.

My verdict is therefore deliberately two-part:

- `semantic_publication_failure_observed = false`: no evidence shows a wrong
  GPU output escaping; native status, compact status and the exact experiment
  oracle remain meaningful synchronous/experiment gates.
- `original_written_per_execution_receipt_requirement_fulfilled = false`:
  the literal Goal5848 receipt/evidence requirement cannot be signed as
  satisfied by the retained data.

This is a claim and protocol-compliance blocker, not evidence that the final
GPU values are fabricated or numerically wrong. It should be closed by an
explicit protocol-scope adjudication and claim removal, not by inventing old
receipts or modifying the measured source.

### 3.2 Lifecycle endpoint

Claude identifies the strongest presentation threat. The implementation-entry
endpoint includes implementation-specific imports. In the retained runs, Arm C
spends about 65%-69% of entry time in import while Arm A spends about 15%-18%.
The direction reverses between endpoints:

- A/C implementation-entry: RTDL is numerically lower (`0.618x`-`0.681x`);
- A/C post-import: RTDL is numerically higher (`1.560x`-`1.837x` median), with
  an observed Ampere-relation maximum block of `2.377129x`.

The post-import endpoint is also confounded because PyOptix creates CUDA state
during the excluded import while RTDL remains lazy. Thus neither first-result
endpoint isolates language/compiler cost, and they are not a clean upper/lower
bound on such a cost.

My decision is stricter than merely reporting both numbers somewhere:

- prepared public RTDL/Direct is the only headline performance comparison;
- entry and post-import must be adjacent in a separately labeled lifecycle
  diagnostic table or panel;
- neither first-result direction may be called speedup, parity, compiler cost,
  or a primary performance success;
- the registered entry gate remains part of historical machine-contract
  custody, but not a positive paper claim;
- the A/E first-result regressions must accompany any lifecycle discussion,
  because the successor improves steady state while regressing both first-
  result endpoints in all four median rows.

### 3.3 Provider double-fault and native fork

The bind/close double-fault is real: a secondary cleanup failure can mask the
primary failure and lose retry ownership. It does not publish output and did
not occur in the retained successful samples. Repairing it now would change
the submitted source identity without strengthening the bounded performance
observation enough to justify that cost. The plan therefore discloses and
descopes universal cleanup claims; it does not patch the runtime before
submission.

The cached PID check is reliable for the supported Python `os.fork()` lifecycle
because the registered child hook refreshes process state. It is not a proof
for native `fork()` paths that bypass Python's hook. The paper and artifact
must prohibit reuse of inherited GPU owners after unsupported native fork and
must not claim universal process-boundary rejection.

### 3.4 Instrumentation, baseline and adaptivity

- The 512-worker ON/OFF qualification covers Arm A only. A/B/C use the same
  formal timer policy, but that is not measured overhead qualification for B/C.
- Strong Arm C is competent relative to B, but it is not a globally optimal
  PyOptix lower bound and is not operation-for-operation identical to A.
- Repeated measurement-guided repair on the same two tasks makes the final
  transactions fresh engineering-gate validation of a task-tuned system, not
  confirmatory or unseen-workload evidence.
- A/E is a registered steady-only regression gate. It cannot be cited as a
  first-result regression safeguard.

### 3.5 Overall decision

The two review labels are compatible once their scope is made explicit:

- GPT-6: `PROCEED_ONLY_AFTER_LISTED_BLOCKERS_ARE_FIXED` correctly describes
  the current repository and paper.
- Claude: `SUBMIT_AFTER_BOUNDED_REWRITE` correctly describes the likely result
  after the blockers are closed entirely by adjudication, writing, artifact
  delivery and review.

My current state is therefore not `SUBMIT_READY`. It is
`PROCEED_TO_BOUNDED_REMEDIATION__SUBMISSION_REMAINS_CONDITIONAL`.

## 4. Non-negotiable execution rules

1. Keep measured source M (`d653fe4`) immutable. Do not change `src/`, native
   code, measured experiments, measured workloads, timers, estimators,
   thresholds or their tests to improve this submission.
2. Do not run a new performance experiment, rent a POD, add an application, or
   construct a user study. No current blocker requires one.
3. Do not rewrite or reseal historical authorities, raw archives or adverse
   outcomes. Corrections are additive errata and derived projections receive
   new identities.
4. Do not invent missing per-sample receipts. If a claim requires them, remove
   or narrow the claim.
5. Permit only minimal read-only evidence export/recount/packaging tools before
   2026-09-08 00:00 ET. They must be separately identified as tool snapshot F,
   not as the GPU-measured source M.
6. After the hard freeze, make no executable change anywhere, including code
   hidden under `paper/`, an artifact directory or a Markdown-generated helper.
7. One writer owns `paper/cgo2027/main.tex`. Evidence and artifact work may run
   in parallel, but no second agent edits the manuscript concurrently.
8. Never use `git add -A` in the current dirty multi-agent worktree. Stage
   explicit reviewed paths only.
9. An AI review is review evidence, not a human usability study and not an
   automatic mutation of `external_review_complete` or
   `public_or_manuscript_claim_authorized` in historical authorities.

## 5. Execution plan and measurable gates

This adopts GPT-6's R0-R8 structure. Each stage produces actual files and logs;
writing that a stage is complete is not completion.

### R0. Establish a recoverable execution root

Actions:

1. Recapture time, HEAD/tree/branch, status, staged state and
   `d653fe4..HEAD` name-status.
2. Assign ownership to every pre-existing dirty path; preserve unrelated
   agent/user changes.
3. Create
   `history/internal_docs/post_goal5851_submission_remediation_20260906/`
   with an initially honest `STATUS.json` and `VALIDATION_LOG.md`.
4. Verify the Ada, Ampere and cross-generation evidence roots, archives,
   manifests, authorities and recounts by path and SHA-256. The expected
   starting roots are:
   - `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass/`;
   - `/Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass/`;
   - `/Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete/`.
   A path named in a report is not a substitute for finding and hashing the
   payload itself.
5. Inventory Python 3.12, Tectonic, PDF metadata/text/render tools and all
   artifact-builder dependencies.
6. Build the old manuscript once into a fresh temporary directory. Record the
   command, exit code, log and generated PDF hash; this is an environment
   probe, not manuscript completion.

Acceptance gate:

- every dirty path and evidence input has an owner/classification;
- all three evidence roots are readable or an exact fallback claim is chosen;
- the manuscript toolchain has one genuinely executed build result;
- no review/evidence file was overwritten or silently staged.

Deadline target: 2026-09-06 17:00 ET.

### R1. Freeze protocol-scope adjudication and claim ledger

Required outputs:

- `PROTOCOL_SCOPE_ADJUDICATION.md`;
- `CLAIM_LEDGER.json`;
- a correction record for the earlier self-review sentence that implied all
  timed receipts were materialized after timing.

The adjudication must map each obligation to four distinct phases:

1. established before execution;
2. checked before public return;
3. checked only when detailed receipt is observed;
4. retained in each formal worker/archive.

It must enumerate all 27 `_FastPathReceipt` ABI fields and separately account
for the original invariant's raygen count, traversable identity, output digest
and monotonic execution identity, which are not equivalent to merely creating
the ctypes object.

The required 27-field inventory is:

```text
schema_version, optix_launch_count, host_blocking_boundary_count,
control_d2h_bytes, output_d2h_bytes, status_before_output,
output_d2h_after_status_failure, role_counters_materialized,
prepared_input_reused, dynamic_device_upload_call_count,
dynamic_accel_build_count, dynamic_explicit_sync_count,
dynamic_blocking_upload_call_count, dynamic_device_upload_bytes,
dynamic_input_generation, semantic_compaction_launch_count,
semantic_compaction_key_capacity, semantic_compaction_scratch_bytes,
callback_status_kernel_launch_count, checked_product_kernel_launch_count,
compact_control_finalizer_kernel_launch_count,
total_auxiliary_cuda_kernel_launch_count, execution_parameter_h2d_bytes,
execution_parameter_h2d_copy_call_count, stream_ordered_memset_call_count,
status_d2h_copy_call_count, output_d2h_copy_call_count
```

The ledger must include stable IDs for at least:

- central bounded compiler contribution;
- static admission and loaded-image identity;
- topology-specific trusted lowering/TCB;
- Goal5838 bounded prospective composition;
- Goal5840 finite structural checking;
- four A/D prepared rows;
- A/C dual lifecycle endpoints and their confounds;
- A/E steady improvement and first-result regression;
- A-only instrumentation qualification;
- provider double-fault and supported-process lifecycle;
- AOT/deployment limits;
- artifact portability;
- human authoring and prevalence equal to zero.

Required machine-readable decisions:

```text
machine_numerical_contract_passed = true
original_written_per_execution_receipt_requirement_fulfilled = false
wrong_output_observed_in_final_gpu_samples = false
public_prepared_a_over_direct_observation_retainable = true
implementation_entry_positive_performance_claim_allowed = false
```

Acceptance gate:

- no sentence says the original receipt invariant passed unchanged;
- no sentence converts the mock probe into a real GPU corruption;
- synchronous native/compact/oracle checks are preserved accurately;
- every intended paper claim has source/evidence identity, scope, limitation,
  destination and disposition;
- an independent reader can reproduce the two-part receipt verdict.

Deadline target: 2026-09-06 21:00 ET.

### R2. Freeze raw-to-table projection and offline verifier

Before the hard development freeze, implement only these bounded additions if
they do not already exist with equivalent reviewed behavior:

- `scripts/goal5852_build_submission_evidence.py`;
- `paper/cgo2027/artifact_post_goal5851/verify.py`;
- `tests/goal5852_submission_evidence_test.py`.

They must be standard-library-capable for offline verification, explicitly
parameterized, fail closed, refuse output overwrite, preserve a private
raw-to-projection provenance map and never invoke a GPU or mutate raw data.
`paper/cgo2027/artifact_post_goal5851/` is the committed template/tool-source
root only. Every exporter invocation must take an explicit, nonexistent
repository-external generated-output root; it must reject an existing output
root rather than overwrite it. Determinism is tested with two distinct new
generated roots, not by reusing the template root.

Required reconstructed data:

- 160 formal cells and all 20,480 steady samples across the two generations;
- 160/160 worker medians independently recomputed from samples;
- all 32 A/D block ratios plus four medians and four observed maxima;
- all A/C entry and post-import block arrays, medians and ranges;
- all A/E steady, entry and post-import derived ratios, clearly labeling the
  latter two as post hoc and non-gating;
- eight arm/task/generation import-gap-post-import-entry decompositions;
- A-only instrumentation denominator, C/B competence and AOT evidence with
  their actual scopes;
- exact source split: A-D at M and E at its declared predecessor.

The following values are reconstruction oracles, not values to copy into the
projection. The exporter must derive them from raw worker samples before
comparing against these expectations:

| GPU/task | A/D steady median | A/D max block | A/C entry median | A/C post-import median |
| --- | ---: | ---: | ---: | ---: |
| Ada triangle | 1.175066 | 1.211025 | 0.642180 | 1.559788 |
| Ada relation | 1.076852 | 1.092253 | 0.653826 | 1.749327 |
| Ampere triangle | 1.133636 | 1.142675 | 0.618362 | 1.637468 |
| Ampere relation | 1.094795 | 1.118811 | 0.681393 | 1.837415 |

The A/E first-result rows are post hoc, non-gating diagnostics:

| GPU/task | A/E steady registered | A/E post-import | A/E entry |
| --- | ---: | ---: | ---: |
| Ada triangle | 0.903016 | 1.169262 | 1.079554 |
| Ada relation | 0.584438 | 1.305383 | 1.192358 |
| Ampere triangle | 0.922388 | 1.162775 | 1.137637 |
| Ampere relation | 0.608228 | 1.261676 | 1.216714 |

These expected summaries do not replace the raw oracle: the acceptance gate
still requires recomputation of all 160 worker medians and preservation of all
20,480 steady samples. The Ampere-relation A/C post-import maximum block must
reconstruct as `2.377129x`.

Required adversarial tests:

- missing worker;
- duplicate schedule cell;
- missing sample;
- one mutated nanosecond value;
- wrong source identity, preserving the legal E exception;
- wrong threshold/gate type;
- malformed projection hash;
- unexpected extra member;
- overwrite attempt;
- `python -O` execution so rejection does not rely on `assert`.

Pre-freeze end-to-end gate:

1. raw evidence to anonymous projection;
2. deterministic package build twice with byte-identical output;
3. extract into a directory outside the repository whose path contains a
   space;
4. clear project `PYTHONPATH` and do not use author-local modules;
5. run `verify.py` offline;
6. obtain the same tables and a manifest-clean result;
7. scan file names, text, archive members and metadata for identity leakage.

If this successful chain is not frozen before 2026-09-08 00:00 ET, do not add
code later. Reduce the artifact promise to the already demonstrated portable
checks and remove any stronger package-replay claim.

Deadline target: implementation and successful rehearsal by
2026-09-07 18:00 ET.

### R3. Correct current control documents; preserve historical custody

Required changes:

1. Add a current override to `AGENTS.md` naming M, the receipt adjudication,
   endpoint rule, A-only instrumentation, native-fork boundary, provider
   double-fault and actual artifact state.
2. Update the sprint state without rewriting its historical chronology.
3. Extend `KNOWN_STALE_CUSTODY_CHECKS.md` with Goal5837 and Goal5843, while
   preserving Goal5832's missing historical commit and Goal5838/5840 off-Git
   byte distinctions.
4. Add explicit errata rather than silently changing historical evidence:
   - malformed 63-character Ada archive digest in the CFR/self-review;
   - three, not two, Goal5850 Ada blocks above 1.35;
   - no registered A/D worst-block gate;
   - timed receipts were not all expanded/persisted after sampling;
   - instrumentation qualification measured A only;
   - stable constructors remain two and unbiased new-application count remains
     zero;
   - Goal5840 is finite structural checking, not general partial evaluation.
5. Update root README, paper README and memory to point to the current bounded
   state without claiming the paper or artifact is complete.
6. Record, but do not edit away, errors inside reviewer prose:
   - Claude's final paragraph says the session could not recount even though
     Sections 1.1 and 9 report a completed recount;
   - the historical 5.206-second PyOptix import belongs to Goal5847, whereas
     current Goal5848 C import medians are about 467-578 ms;
   - the Ampere relation entry outlier does not by itself prove import caused
     the dispersion;
- any claim that all ten Goal5838 candidates share four roles is false;
  seven are four-role built-ins and three have custom bounds/intersection
  roles;
- the eligible denominator remains ten because the earlier curve Boolean
  route was closest-hit, while
  `builtin_round_linear_curve::any_hit_terminate_bool_per_query` is a distinct
  eligible candidate;
- the actual selected Goal5838 topology is
  `builtin_sphere::any_hit_count_continue_u64_per_query`, not the curve
  any-hit-terminate candidate.

Acceptance gate:

- a new session reading AGENTS/README/memory reaches the correct current state;
- every correction has an original location and replacement fact;
- no historical authority, archive or reviewer report is silently rewritten;
- `rg` finds no active downstream reuse of the malformed hash or nonexistent
  A/D tail gate outside an explicitly labeled erratum/history context.

Deadline target: 2026-09-07 18:00 ET.

### R4. Rewrite the whole manuscript around the bounded thesis

One writer edits `paper/cgo2027/main.tex`. Architecture and nonnumeric sections
may begin after R1 while R2 completes; final evaluation numbers must come only
from the frozen R2 projection.

Required narrative:

1. Problem: individually legal non-rendering OptiX fragments can form an
   incoherent cross-role protocol.
2. Contribution: the supported complete protocol is the compilation/admission
   unit; obligations span typed callbacks, semantic ABI, physical resources,
   provider/executable identity and publication lifecycle.
3. Boundary: schema-parametric admission/planning/identity/lifecycle;
   compiler-owned topology-specific lowering; no arbitrary Callback IR or
   automatic profitable RT mapping.
4. Generality evidence: Goal5838 as one bounded author-domain compositional
   extension with implementation/TCB cost; Goal5840 as finite structural
   checking over explicit denominators.
5. Performance: prepared A/D is the headline; two tasks, two GPUs, exact source,
   median-only gate, all blocks reported, no speedup wording.
6. Lifecycle: entry and post-import adjacent as confounded diagnostics, with
   the observed post-import maximum and A/E first-result regressions visible.
7. Safety/evidence: synchronous native/compact/oracle facts separated from the
   original per-execution detailed-receipt requirement that was not fulfilled.
8. Threats: task-directed adaptivity, Strong C residual differences, A-only
   instrumentation, topology-specific TCB, checker limit, double-fault,
   native-fork limit, no human/prevalence evidence and artifact portability.

Performance-table rule:

- Main table: A/D steady medians and observed block range/max, plus exact
  task/GPU/source/estimator scope. Put all 32 individual A/D block ratios in
  the supplement and artifact rather than crowding the 11-page paper.
- Separate adjacent lifecycle table: A/C entry and post-import together, plus
  A/E first-result derived rows. Caption must say descriptive/confounded and
  non-speedup.
- Supplement: complete arrays, failure lineage and detailed decompositions.

Minimum adverse main-text disclosure is non-negotiable even if the complete
lifecycle table moves to the supplement. The main paper must state that the
post-import direction is adverse and its largest formal diagnostic block is
`2.377129x`; that A/E first-result medians regress by approximately 8%-22% at
entry and 16%-31% post-import and are post hoc, non-gating observations; that
the primary endpoint changed after the earlier adverse endpoint was observed;
and that both endpoints are confounded by lifecycle/dependency initialization.

This split deliberately prevents a registered but confounded entry PASS from
being visually interpreted as the paper's primary performance success.

Acceptance gate:

- one thesis and at most four contributions;
- every quantitative sentence resolves to a frozen ledger ID;
- no arbitrary/generic-lowering, unbiased-new-app, intrinsic-speedup,
  confirmatory, Direct-parity/tail, usability or prevalence claim;
- stable constructors=2, composition exam=1, unbiased new application=0,
  external human author=0, with distinct denominators;
- no old 324-worker/7,128-timing/18-block table remains as current evidence;
- receipt deviation and first-result confounds appear in the main paper;
- actual built PDF fits at most 11 pages of text excluding references without
  hidden font/margin manipulation.

Deadline target: complete claim-consistent draft by 2026-09-08 18:00 ET.

### R5. Freeze executable bytes and usable claims

Before 2026-09-08 00:00 ET, create `FREEZE_RECORD.md` recording:

- M and its tree;
- E and its tree;
- tool snapshot F commit/tree and exact whitelist of M-to-F executable changes;
- all raw archive/manifest/authority hashes;
- R1 adjudication and ledger hashes;
- Python/tool versions;
- branch, clean/dirty classification and pushed state;
- UTC and ET freeze timestamps.

Required freeze decisions:

```text
machine_numerical_result = retained_with_exact_scope
original_written_receipt_requirements_fulfilled = false
submission_performance_headline = prepared_public_rtdl_over_direct
first_result = dual_endpoint_diagnostic_only
new_executable_work_after_freeze = forbidden
```

Before recording F, run the following bounded regression matrix with the
Python 3.12 interpreter resolved in R0. The currently expected local
interpreter is `/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python`, but the
log must record the executable actually used:

```bash
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 <python-3.12> \
  -m unittest discover -s tests -p 'goal5848*_test.py'
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 <python-3.12> -O \
  -m unittest discover -s tests -p 'goal5848*_test.py'
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 <python-3.12> \
  -m unittest tests.goal5851_triangle_fused_replay_test
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 <python-3.12> \
  -m unittest tests.goal5852_submission_evidence_test
PYTHONPATH=src:. PYTHONDONTWRITEBYTECODE=1 <python-3.12> -O \
  -m unittest tests.goal5852_submission_evidence_test
git diff --check
```

The existing-suite expectations are `128/128`, `128/128`, and `7/7` for the
first three commands. The new Goal5852 count is whatever the frozen test file
actually defines; every declared adversarial mutation must be represented and
must fail closed in both normal and `-O` execution. Platform skips and known
historical seal failures are reported separately, never counted as passes and
never repaired by resealing old evidence. Full repository discovery is not a
submission gate unless it is intentionally run and honestly classified.

The final-F rehearsal is an indivisible ordered gate:

1. commit candidate F with an explicit path whitelist and preferably push it;
2. create a new clean checkout at that exact F commit outside the working tree;
3. from that checkout, generate only into new repository-external output roots;
4. execute raw export, two deterministic package builds, extraction into a
   foreign path containing a space, and offline verification;
5. record F commit/tree, exporter/template/verifier hashes, raw input hashes,
   generated output/package hashes, exact commands and exit codes, and clean
   checkout status before and after;
6. verify that the packaged verifier is byte-identical to F's verifier.

Any later change to an executable tool or template creates a new candidate F
and invalidates the affected rehearsal. If push is unavailable, a reason alone
does not pass the gate: build and hash a recovery bundle, validate its Git
object completeness, recover the identical F into a new checkout from that
bundle, and run the same rehearsal there. `FREEZE_RECORD.md` may be committed
in the later document snapshot P because a commit cannot contain its own hash.

Acceptance gate:

- all executable helpers needed after freeze already exist in F and passed R2;
- measured runtime/experiment bytes from M remain byte-identical;
- every F-only executable file is named and justified;
- branch is pushed, or the exact reason and recovery bundle are recorded;
- no promise depends on writing another verifier after freeze.

Deadline target: 2026-09-07 22:00 ET, with absolute limit
2026-09-08 00:00 ET.

### R6. Build and replay the anonymous artifact

Use `paper/cgo2027/artifact_post_goal5851/` only as the committed, frozen
template and tool-source root. It is not an exporter output directory.

Each export/package run must receive an explicit, nonexistent output root
outside the repository, such as distinct `package-a` and `package-b`
subdirectories under a temporary parent. The exporter creates the selected
root, copies the frozen verifier, and generates data, documentation and the
manifest there. Two new roots must build successfully; reuse of either
existing root must fail closed. Template and raw-evidence hashes, plus the
clean F checkout state, must remain unchanged across generation.

Keep two identities separate:

- private custody: immutable raw archives, real paths/UUIDs, authorities and
  private provenance;
- anonymous delivery: new projection/package hashes, neutral identifiers and
  complete retained measurement structure needed for paper claims.

Required package contents:

- `README.md` with one exact quick-start path;
- `manifest.json` with path, bytes and SHA-256;
- `data/` containing every sample/field needed to reconstruct retained paper
  values;
- frozen `verify.py` and only its declared standard-library dependencies;
- `EXPECTED_RESULTS.md`, `CLAIM_SCOPE.md`, `REPLAY_MATRIX.md`;
- dependency/license/proprietary-component disclosure;
- explicit distinction between portable manifest/worker recount and
  nonportable full historical authority replay.

Acceptance gate:

- manifest and all mutation/rejection checks pass;
- two clean extraction roots, including one with spaces, reproduce identical
  numerical output offline and without project `PYTHONPATH`;
- deterministic package builds are byte-identical;
- anonymous scan covers names, content, members, metadata and binary strings;
- no private review, memory, network endpoint, username or provenance map is
  in the public package;
- no claim says offline recount is a new GPU run or complete product install.

Deadline target: 2026-09-09 12:00 ET.

### R7. Review the actual final bytes

Prepare one self-contained review request containing:

- M/F/P identities;
- final PDF and artifact hashes;
- R1 adjudication and final claim ledger;
- raw-to-projection-to-table logs;
- artifact replay logs;
- source/tool whitelist;
- expected-green, expected-red, hardware-gated and not-provided matrices;
- every known limitation and reviewer disagreement.

Obtain two independent reviews of the actual final PDF and artifact, not the
old manuscript or this plan. For every material finding, record
`accept`, `reject_with_source_evidence`, `claim_descope`, or `open`, together
with changed file/line and evidence.

Acceptance gate:

- all findings that affect a retained central claim are closed or that claim
  is removed;
- receipt disagreement receives a direct written disposition;
- endpoint presentation is explicitly approved or narrowed further;
- any post-review substantive change is re-reviewed at least over its diff;
- pending review is never called consensus.

Deadline target: 2026-09-09 22:00 ET.

### R8. Final submission gate

Recheck the official CGO page and actual submission form. Validate the exact
uploaded candidates, not only local source:

- standard research-paper category remains intentional;
- main text <=11 pages excluding references;
- ACM SIGPLAN review/anonymous/line-number format on Letter paper;
- English, black-and-white readability, readable graph labels and page numbers;
- no main-PDF appendix; anonymous supplement uploaded separately if used;
- all citations/references resolve, no build rerun warning, and every page is
  visually inspected for clipping/overlap;
- PDF/source/supplement/artifact hashes match the reviewed bytes;
- title, filenames, PDF metadata, paths, acknowledgements and self-citations
  pass two independent anonymity scans;
- final closure report records every R0-R8 status and unresolved limitation;
- upload receipt and downloaded-hash check are retained if upload is
  authorized and performed.

Acceptance gate:

- `FINAL_CLOSURE_REPORT.md` contains actual files, hashes, commands, exit codes,
  review dispositions and claim deletions;
- no `OPEN` issue affects a retained central claim;
- if not uploaded, status says `SUBMISSION_PACKAGE_READY__UPLOAD_NOT_EXECUTED`,
  not `SUBMITTED`.

Target: submission-ready bytes by 2026-09-10 12:00 ET, leaving margin before
the official AoE deadline.

## 6. Critical path and concurrency

| Time | Primary writer | Parallel read-only/bounded work | Exit condition |
| --- | --- | --- | --- |
| 09-06 afternoon | R0 owner | Evidence/path inventory | Recoverable snapshot and toolchain probe |
| 09-06 evening | R1 owner | R2 design and R3 correction inventory | Signed scope adjudication and claim ledger |
| 09-07 | R2/R3 owners | Main writer starts nonnumeric bounded skeleton after R1 | Frozen tools pass clean offline rehearsal; current docs corrected |
| 09-07 22:00 | Freeze owner | Final M-to-F byte audit | F committed/pushed; no future executable dependency |
| 09-08 | Main writer | Frozen tools may generate tables; artifact assembly only | Claim-complete <=11-page draft |
| 09-09 | Artifact owner then reviewers | Main writer fixes wording/layout only | Clean artifact replay and two final-byte reviews |
| 09-10 | Submission owner | Independent anonymity/rule/hash checks | Reviewed submission-ready package or explicit no-go |

No task waits for a calendar time if its prerequisites are already satisfied.
No missed target moves the hard development freeze.

## 7. Differences from the GPT-6 execution plan

The default is conformance. The following table lists every intentional
change, addition or clarification; there is no hidden divergence.

| ID | GPT-6 plan | This plan | Reason |
| --- | --- | --- | --- |
| D1 | R2 proposes one main table containing A/D steady plus A/C entry and post-import columns. | Split the paper presentation into an A/D prepared main table and a separate adjacent dual-endpoint lifecycle table. Preserve all numbers and the registered machine-contract status. | Claude's P0-2 shows that import composition flips direction and dominates Arm C entry. A single main table risks visually promoting a confounded entry PASS. This is stricter presentation, not data deletion or gate rewriting. |
| D2 | R1 already distinguishes machine PASS from the unfulfilled original receipt requirement. | Add explicit paired booleans for semantic wrong-output evidence and literal receipt compliance. | This prevents both errors: claiming a GPU correctness failure that was not observed, and claiming the original per-execution proof requirement passed. It strengthens, rather than contradicts, R1. |
| D3 | R3 lists the major review-packet errata. | Add Claude's internal recount sentence contradiction and the review's historical 5.206-second import/dispersion causal overstatements to the correction ledger. | The final reviewer must not copy inaccurate reviewer prose into the paper. These are additive review-adjudication facts, not edits to Claude's report. |
| D4 | R4 follows R1, with its numerical section following R2. | Start only the nonnumeric architecture skeleton after R1 while R2 runs; freeze numerical prose until R2 output is fixed. | This uses the same dependency graph while reducing deadline risk and preserving one-writer ownership. |
| D5 | The plan preserves implementation-entry as a registered operational gate and limits its wording. | Preserve it in custody and lifecycle diagnostics, but forbid it as a positive paper performance claim even if described as operational. | The registered result remains factual. The stricter claim rule neutralizes endpoint selection after an adverse observation and aligns with Claude's binding condition. |

All other GPT-6 requirements are adopted, including the R0-R8 sequence,
receipt adjudication, no measured-source repair, frozen offline tooling,
complete 20,480-sample projection, layered custody, anonymous clean replay,
two final-byte reviews and official submission checks.

## 8. Risks and fail-closed fallback decisions

| Risk | Trigger | Mandatory response |
| --- | --- | --- |
| Receipt claim remains disputed | Reviewer requires original per-execution physical proof | Remove the affected fully-checked/per-execution claim. Retain only the exact output/status and bounded performance observation explicitly allowed by the adjudication. Do not create retroactive receipts. |
| Offline tool misses freeze | R2 successful clean replay is absent at 2026-09-08 00:00 ET | Freeze without it. Reduce artifact claims to existing verified portable operations; do not write a verifier after freeze. |
| Artifact cannot distribute raw bytes | Licensing, identity or size prevents inclusion | Deliver a manifest-bound anonymous projection with private provenance and narrow the replay claim; state which original bytes are not distributed. |
| Manuscript exceeds 11 pages | Rendered text crosses page 11 before references | Compress historical portfolio and detailed lineage into supplement; keep thesis, method, principal table and central threats in the main paper. Never shrink below readable format. |
| Final review rejects lifecycle presentation | Entry/post-import still appears misleading | Remove the detailed first-result table and any positive first-result claim if necessary, but keep the minimum adverse disclosure in the main text: adverse post-import direction and `2.377129x` maximum diagnostic block, A/E entry and post-import median-regression ranges, endpoint revision after adverse observation, and both lifecycle/import confounds. Moving complete arrays to the supplement cannot erase this floor. Any stronger deletion requires an explicit claim-removal disposition and another consistency review. |
| Final review deems receipt mismatch central/fatal | Narrowing no longer preserves the stated contribution | Remove the performance-proof coupling and rewrite around admission/identity architecture; if the remaining paper is not defensible, report no-go rather than patch after freeze. |
| Dirty multi-agent work conflicts | Another process changes a file owned by this plan | Stop that file's edit, capture both identities, and adjudicate ownership. Never overwrite or revert silently. |
| Final external review is unavailable | R7 cannot obtain two actual reviews | Keep review state pending, perform documented internal hostile checks, and do not claim consensus. Submission decision remains explicitly risk-bearing and user-owned. |

## 9. Definition of submission-ready

The package is submission-ready only if all of the following are true:

1. M remains the exact source associated with A-D and all reported successor
   GPU performance; predecessor-only E observations remain explicitly bound to
   E rather than being mislabeled as executions of M.
2. The receipt adjudication explicitly records literal non-fulfillment without
   inventing a wrong-output event.
3. Every retained paper claim has a closed ledger row and exact evidence.
4. Prepared A/D is the only positive headline performance result.
5. Any first-result discussion is dual-endpoint, confounded, adjacent and
   accompanied by A/E startup regression scope.
6. The manuscript is internally consistent, <=11 text pages, anonymous and
   visually valid.
7. The artifact exists, has a manifest, replays in two clean locations and
   states precisely what is portable and what is not.
8. Current, historical, platform and optional tests are separated; expected
   red checks are named rather than hidden.
9. Two reviews target the final PDF/artifact bytes and every central finding
   is closed or its claim removed.
10. Final hashes and, if authorized, upload/download receipt are retained.

Until then, the only accurate project status is:

`REMEDIATION_IN_PROGRESS__NOT_SUBMISSION_READY__NO_NEW_PERFORMANCE_DEVELOPMENT`

## 10. Questions for review of this plan

The reviewer should answer these directly before execution proceeds past R1:

1. Is the two-part receipt verdict accurate and sufficient to retain the narrow
   prepared public-path performance observation?
2. Is splitting A/D from the lifecycle table the correct resolution of
   Claude's endpoint criticism, or should first-result data leave the main
   paper entirely?
3. Does descope/disclosure adequately handle provider double-fault and native
   fork, given that neither affected a retained successful sample?
4. Is the bounded offline exporter/verifier the smallest credible artifact
   development before freeze, or should its promise be reduced further?
5. Are any of D1-D5 inconsistent with the GPT-6 plan in a way not justified by
   source, retained data or deadline risk?
6. Does any planned manuscript statement still imply topology-generic
   lowering, confirmatory validation, Direct speedup/parity, universal cleanup,
   human usability or real-world defect prevalence?

Review acceptance of this plan authorizes execution of the plan, not any
paper claim. Claim authorization remains a later, final-byte decision.
