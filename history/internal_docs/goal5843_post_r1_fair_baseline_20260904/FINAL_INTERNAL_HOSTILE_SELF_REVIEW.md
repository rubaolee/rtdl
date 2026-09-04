# Goal5843 final internal hostile self-review

Date: 2026-09-04

Verdict:
`ACCEPT__INTERNAL_TECHNICAL_COMPLETE__EXTERNAL_REVIEW_PENDING`

This review applies only to the accepted v4 transaction at source commit
`c2662603c4d24902361fbd70325832ee7d98a0a4`. The v3 transaction remains a
separately preserved terminal verifier failure and is not part of the accepted
sample.

## Reviewed surfaces

- v4 preregistration, source pins, schedule, and claim ceiling;
- Direct, pinned PyOptiX-compatible, and public RTDL worker routes;
- formal leaf cache, independent oracle, execution authority, and custody;
- all 108 composites and 216 subworker receipts;
- controller summary and independent standard-library recount;
- downloaded archive safety, mode custody, and local recount;
- both pre-worker repairs and the terminal v3 post-worker verifier repair;
- final technical report and final-authority generator;
- byte identity of all three frozen Goal5838 core files.

## P0 findings

No P0 finding remains for the bounded internal Goal5843 completion claim.

## P1 findings

No P1 finding remains for the bounded internal Goal5843 completion claim.
Performance parity, public wording, manuscript wording, and external consensus
are outside that claim and remain explicitly false.

## P2 findings

### P2-1: External review is absent

The experiment, repair history, interpretation, and final authority have only
strict internal review. This blocks public or manuscript performance claims and
consensus wording. The evidence must be independently reviewed after the owner
restores external-review availability.

### P2-2: One hardware profile cannot support broad generalization

The accepted transaction used one RTX A6000 UUID, one driver, one CUDA/OptiX
stack, and one host. Balanced blocks address temporal order within this host,
not cross-generation behavior. No hardware-independent or general language
performance claim is justified.

### P2-3: The workloads are synthetic and bounded

The primary triangle scalar and relation negative control are useful frozen
micro-workloads. They do not establish whole-application performance or
represent all callback families, output densities, scene structures, or data
sizes.

### P2-4: Remaining steady RTDL overhead is not causally decomposed

The primary accepted result says public RTDL is 2.910x PyOptiX and 4.689x
Direct. It does not isolate exact shares for Python dispatch, ctypes, receipt
construction, status transfer, scalar transfer, or native launch. Earlier R1
layer diagnostics are informative but are not pooled formal Goal5843 rows.

### P2-5: Provider setup and first-execution work are asymmetric

RTDL performs its first prepared-query upload in first execute. Direct and
PyOptiX place upload in prepare. The report correctly treats setup and FIRST as
descriptive, but readers may still misuse the 134.6x and 232.3x triangle FIRST
ratios. They must not be presented as steady language overhead.

### P2-6: v4 was designed after observing a complete v3 result

v3 revealed performance before its post-download verifier failed. This creates
a potential researcher-degree-of-freedom attack. The mitigation is strong but
must remain visible: v4 changes only archive-mode verification and its tests,
retains exactly the v3 task/arm/schedule/sampling/estimand/failure/claim
contracts, has no performance success threshold, preserves v3 in full, and
does not pool one v3 timing sample. External review should verify this diff.

## P3 findings

### P3-1: GPU clocks and power were not manually locked

Within-block balancing and all arm permutations reduce order and thermal bias,
but they do not eliminate it. This is acceptable for the internal bounded
baseline, not for an unrestricted hardware claim.

### P3-2: Hidden implementation work is deliberately not identical

All arms match semantic inputs, required public outputs, fresh-process policy,
prepared steady reuse, and GPU completion. They do not share identical
compiler, pipeline, ownership, result-construction, or receipt machinery. The
study measures user-visible implementation paths rather than a single kernel
wrapped three ways.

### P3-3: The Direct raw transport retains a Goal5842 schema name

The Direct executable is inherited and hash-bound. Goal5843 validates and
wraps it into its own receipt. The old raw schema string is confusing but does
not change the measured contract.

## Adversarial questions

| Attack | Review answer |
| --- | --- |
| Were favorable rows selected? | No. All 18 blocks, 108 composites, 216 receipts, and adverse rows are present. There is no threshold or outlier rule. |
| Was the private checker-off path used? | No. The arm is the ordinary public check-on front door, and every RTDL triangle receipt passes the v7 scalar gate. |
| Did RTDL avoid real OptiX work? | No. Triangle receipts require one OptiX launch; relation receipts require two successful launches, exact route and DSO identity, zero failures, and 8,192 raygen invocations. |
| Did the scalar optimization change the public result? | No. All arms match the independently derived exact checked-U64 scalar 65,530. |
| Was relation quietly converted to the scalar route? | No. It returns and validates all 4,096 canonical rows and remains the adverse control. |
| Was v3 silently repaired after seeing results? | No. v3 is terminal, its full archive and seals are committed, its rows are ineligible for pooling, and v4 is a new preregistration and complete transaction. |
| Did the v4 verifier merely ignore file modes? | No. It checks original mode against the tar header, while safe extraction intentionally normalizes local mode; size and SHA-256 are independently checked after extraction. A mode substitution test is required. |
| Could the pod recount copy the controller result? | The recount is a separate standard-library implementation and the Mac reconstructs it from the downloaded receipts. Pod and Mac outputs are byte-identical. |
| Does the 2.910x ratio prove intrinsic language overhead? | No. It is the current public implementation ratio for one bounded task and stack. |
| Does the large improvement over V12 authorize a speedup claim? | No. It is descriptive cross-transaction context and external review is absent. |
| Did Goal5842R1 finish performance work? | No. It removed the catastrophic repeated materialization path, but public RTDL remains slower than both low-level arms. |
| Can setup or FIRST ratios be used causally? | No. Initial query-upload phase placement differs by provider. |

## Authority checks

- Accepted formal source commit:
  `c2662603c4d24902361fbd70325832ee7d98a0a4`.
- v4 preregistration seal:
  `c0ad3a566e99f925341d98c987854714cfabc415254ccd7178efcd465e664b66`.
- Execution authority seal:
  `41510173122a06c48d0c137f05f9183bc2ac3dad256a0a6bdb435fa59f0e0101`.
- Pod/local recount seal:
  `6dd6a575e4278fad9b3add4b6599b49df95dc9c7cafe0db62872a30a5916dac5`.
- Downloaded archive verification seal:
  `4a93956c80d7983601f3704addd4c2f25fd61387997fb404d2ddf97b7e39c18b`.
- Frozen Goal5838 core diff: empty.
- External-review count: zero.

## Post-transaction local regression audit

The exact Goal5842/V12, Goal5842R1, Goal5843 preregistration, and final-
authority successor suite passes 91/91 on the Mac. This is the previously
passing 86-test successor set plus five final-authority tests. The added tests
rederive the final authority, verify the v4 archive and byte-identical pod/Mac
recounts, preserve the terminal v3 archive and its no-pooling rule, and verify
all three Goal5838 frozen-core hashes.

An intentionally broader adjacent-history run passed 245/247. Its two errors
are both old Goal5840 repair-freezer unit tests that rebuild an early frozen
mode-case source manifest from today's legitimately evolved Goal5840 files and
therefore report `scientific inputs differ`. The frozen Goal5840 authority
itself and the Goal5843 successor suite are not failing. Do not describe the
247-test exploratory run as fully green; repairing historical current-tree
replay semantics is a separate test-infrastructure debt and must not rewrite
the old Goal5840 evidence.

## Final recommendation

Accept Goal5843 as internally technically complete at its exact preregistered
scope. Preserve the adverse result: the post-R1 public triangle path is much
closer to low-level baselines but remains 2.91x PyOptiX and 4.69x Direct, while
relation remains 3.33x and 9.95x respectively. Do not authorize public or
manuscript performance wording until external review confirms protocol,
repair history, archive verifier, analysis, and claim boundaries.
