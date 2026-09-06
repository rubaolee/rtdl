# R7 call for independent review of exact final candidate bytes

Date: 2026-09-06

Status: `REVIEW_REQUEST_READY__TWO_INDEPENDENT_RESPONSES_REQUIRED`

This request is self-contained enough for a reviewer with no previous RTDL
project context. Review the exact repository snapshot, PDF, and artifact named
below. Do not substitute an older manuscript, an older report, or a rebuilt PDF
with different bytes. This is a double-blind CGO 2027 candidate; do not publish
private identities from repository history in the review response.

## 1. Project and claimed contribution

RTDL investigates a language/runtime boundary for Python-authored programs that
repurpose ray-tracing hardware. Its current claim is deliberately bounded:

> RTDL admits a bounded whole ray-tracing protocol across restricted source,
> role/effect rules, semantic and physical ABI, topology-specific trusted
> lowering, executable identity, and lifecycle state.

The candidate does **not** claim arbitrary Python, arbitrary Callback IR,
topology-generic lowering, discovery of profitable RT mappings, complete OptiX
coverage, intrinsic speedup, universal performance parity, demonstrated human
usability, or real-world defect prevalence.

The architectural question for review is whether this bounded protocol-admission
contribution remains technically meaningful and accurately described even though
native lowering is topology-specific and stays inside the trusted computing
base.

## 2. Immutable identities under review

| Role | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Final executable tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Candidate paper/package snapshot P | `c6020fd63097b35b5294778cf54c2fb84c879ad6` | `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |

P is pushed on `origin/codex/cgo-goal5836-handoff`. At P, the exact delivery
pair is:

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 138,969 | `4529946fff21edd2e5634792397d5e3af0213f6c2ab2c4ebdf001b9246f73453` |
| `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The delivery PDF is byte-identical to `paper/cgo2027/main.pdf`. The delivery
archive is byte-identical to the archive produced by the clean F2 rehearsal.

## 3. Controlling adjudication and evidence

Review these records at P:

| Record | SHA-256 |
| --- | --- |
| `PROTOCOL_SCOPE_ADJUDICATION.md` | `53b5f6028f6f549be0012bb949e46dfff0ed6823d02bff96bff672f53bed6531` |
| `RECEIPT_CLAIM_CORRECTION.md` | `9ba0723900c2a648338b6d7f7a72a05d944b96e799025c6dd7481c28988a8a72` |
| `CLAIM_LEDGER.json` | `476b623eecb92bdf30432623b95966c884ee13523ea57b88398f3369ab863006` |
| `R2_SUBMISSION_EVIDENCE_REPORT.md` | `73ebd0b77b1c68b7f2d6e2a8801f5e70ded4eb38dcabe8deb0fc8c03e27374dc` |
| `FREEZE_RECORD.md` | `fe1ab9ae325b735a99ef54327f3b30528dac269952a0d2a990899e475ea1f620` |
| `R5_FINAL_F2_REHEARSAL_REPORT.md` | `1a380b92fa2cc957c424865d91b64791fcdf826ff21f970046447fcfd1ad0d1b` |
| `R4_MANUSCRIPT_REWRITE_AND_RENDER_REPORT.md` | `2e534bbd2986bba0a7838889e43ecce705381c2b76925f7cfd1cdddf55447af2` |
| `R6_FINAL_DELIVERY_PAIR_AND_REPLAY_REPORT.md` | `35945caded4ee4223498ca88574c6680bd6292203a349c4c4e840b402f2b7f4d` |

All paths above are under
`history/internal_docs/post_goal5851_submission_remediation_20260906/`.
The claim ledger contains 21 entries; every `claim_authorized` value and the
global authorization remain `false` pending R7.

## 4. Binding receipt adjudication

The reviewer must directly accept or reject this two-part conclusion:

```text
machine_numerical_contract_passed = true
original_written_per_execution_receipt_requirement_fulfilled = false
wrong_output_observed_in_final_gpu_samples = false
public_prepared_a_over_direct_observation_retainable = true
implementation_entry_positive_performance_claim_allowed = false
```

There are 4,096 timed Arm-A calls. The worker validates every returned output
against the frozen output contract, and the public path synchronously checks
native and compact status before returning. However, the evidence retains only
32 separate post-loop detailed diagnostic receipts, not a validated 27-field
receipt for every timed call. The paper must not turn the absence of observed
wrong output into proof that the original receipt requirement was met.

## 5. Numerical population and mandatory disclosures

The anonymous projection reconstructs:

| Population | Count |
| --- | ---: |
| Formal worker cells | 160 |
| Formal steady samples | 20,480 |
| Arm-A instrumentation endpoints | 1,024 |
| AOT observations | 20 |
| Nonformal competence workers | 8 |

The only main positive performance rows are exact prepared public A/D:

| GPU | Task | Median A/D | Observed maximum A/D |
| --- | --- | ---: | ---: |
| RTX 4090 | Relation | 1.076852 | 1.092253 |
| RTX 4090 | Triangle | 1.175066 | 1.211025 |
| RTX 3090 | Relation | 1.094795 | 1.118811 |
| RTX 3090 | Triangle | 1.133636 | 1.142675 |

Lower is better. These are observations for two exact tasks and paths, not a
universal or intrinsic-language result. No A/D observed-maximum gate was
preregistered.

The main paper must retain all of the following adverse facts:

- post-import A/C is adverse in all four rows, with median ratios
  1.559788--1.837415 and maximum formal block 2.377129;
- relative to E, first-result medians regress about 8%--22% at entry and
  16%--31% post-import;
- the first-result rows are post hoc and non-gating;
- the entry endpoint was revised after an adverse observation;
- both first-result endpoints are lifecycle/import-confounded;
- instrumentation qualification measured Arm A only.

Please independently recompute or spot-check these values from the packaged
projection. Do not infer cross-machine raw-time ratios.

## 6. Bounded generality evidence

Check that the paper preserves these exact limits:

- stable public facade: two constructors;
- stable facade kind presence: 2/6 OptiX build-input enum values and 2/4 leaf
  kinds;
- full bounded V4 corpus: 4/6 build-input enum values and 4/4 leaf kinds;
- these are presence counts, not complete support for each category;
- selected Goal5838 row:
  `builtin_sphere::any_hit_count_continue_u64_per_query`;
- curve any-hit-terminate is an eligible candidate, not the selected row;
- Goal5838's domain has ten author-defined rows made from known primitive and
  topology recombinations, two true launches, and 12/12 oracle checks;
- the selected route required about 2,635 topology-specific lines plus about
  28 shared compiler lines;
- Goal5840 imports no `rtdsl`, covers three route groups, four modes, five
  generated-code property classes, 20 registered instances, and 15 unique
  mutations;
- Goal5840 is a finite target-structure checker with an early-return
  limitation, not a compiler soundness theorem.

## 7. Source/tool boundary

Relative to M, P has no diff under `src/`, `include/`, or `experiments/`. The
only executable whitelist between M and F2/P is:

```text
paper/cgo2027/artifact_post_goal5851/verify.py
scripts/goal5852_build_submission_evidence.py
tests/goal5852_submission_evidence_test.py
```

Those tools export/recount/package frozen evidence; they do not modify or rerun
the measured GPU implementation. Reviewers should reject any wording that makes
F2 appear to be the implementation measured at M.

## 8. Exact artifact replay

Extract the exact archive into a new directory, then run from the package root:

```text
PYTHONNOUSERSITE=1 /usr/bin/python3 -I verify.py --artifact-root .
PYTHONNOUSERSITE=1 /usr/bin/python3 -I -O verify.py --artifact-root .
```

Expected result for both is exit 0 and
`PASS__OFFLINE_PROJECTION_RECOUNT`. Four R6 executions, from two fresh roots
including one path with spaces, produced byte-identical JSON at SHA-256
`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`.
The projection, recount-summary, and manifest self-seals are respectively:

```text
fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca
54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105
4a62601b0e421033e67169ed3f89818c6cf62b8acc7723df9cc3ca4c8a46fc32
```

The archive has nine regular 0444 files with normalized owner and timestamp
metadata. It is an anonymous standard-library offline recount package, not a
GPU rerun, product installation, source distribution, or reconstruction of the
private historical authority.

## 9. Expected outcome matrix

| Class | Expected state |
| --- | --- |
| Green | exact hashes; two isolated normal/optimized replays; all projection recounts; PDF is eight US-Letter pages; no horizontal clipping; no undefined citations; 14/14 frozen evidence tests |
| Expected red | reused exporter output root rejects; all claim authorization stays false before R7; original per-execution detailed-receipt requirement is false |
| Hardware gated | no GPU execution is performed by the public artifact; new GPU reproduction requires CUDA, OptiX, drivers, hardware, and private experiment inputs |
| Not provided | arbitrary Python/Callback IR/topology lowering; full OptiX coverage; unbiased new application; external human authoring/usability; prevalence; complete raw GPU authority; third-party source or binaries |

The PDF log has zero horizontal overfull boxes, zero undefined citations or
references, and zero BibTeX/ACM class warnings. It has one 1.90399pt
end-of-document output-routine overfull vbox. All eight exact pages were
rendered at 130 dpi and show no visible clipping or overlap. Review whether the
warning is acceptable as disclosed; do not silently describe it as zero
overfull boxes.

## 10. Known limitations and prior reviewer disagreements

1. Earlier reviewers attacked the purported generic core because the canonical
   plan itself is non-executable and topology-specific wrappers/lowerers contain
   substantial trusted native structure. The current paper accepts this and
   claims bounded admission, not topology-generic lowering.
2. Earlier reviewers found the prospective challenge domain author-defined and
   composed only of known primitives/topologies. The paper now reports exactly
   one selected bounded composition and zero unbiased new-application exams.
3. An earlier causal explanation attributed a predecessor performance gap to a
   different sort/unique path, but source showed both paths sort/unique. That
   explanation is removed; current performance wording is observational.
4. The numerical machine contract passed, but the original detailed-receipt
   requirement did not. This is a deliberate claim narrowing, not a runtime
   repair.
5. The provider double-fault and native-fork limitations remain outside the
   supported claim. They are disclosed rather than fixed after freeze.
6. Two old public-document test modules fail in both P's parent HEAD and the
   candidate because they target historical documentation absent from this
   restricted repository; this is not counted as a candidate pass.
7. Independent human authoring evidence and unbiased new-application evidence
   are both zero.

## 11. Required review procedure

1. Verify P, PDF, and archive hashes before reading reports.
2. Read the PDF itself page by page; do not review only `main.tex` or the R4
   report.
3. Replay the exact archive in a fresh path under normal and optimized isolated
   Python.
4. Check all 21 ledger dispositions against actual PDF sentences and tables.
5. Recompute the four A/D rows and spot-check the adverse A/C and A/E rows.
6. Audit anonymity in PDF text/metadata, filenames, and every archive member.
7. Check that package-content prose names only the nine actual members and keeps
   private custody records outside the package.
8. Check contribution novelty against the admitted topology-specific TCB and
   finite validation scope.
9. Check official CGO format, bibliography, accessibility, and page limits.
10. Return a finding table using the disposition vocabulary below.

## 12. Required response format

For every material finding, provide:

| Field | Required value |
| --- | --- |
| ID | stable reviewer identifier |
| Severity | blocking, major, minor, or note |
| Disposition | `accept`, `reject_with_source_evidence`, `claim_descope`, or `open` |
| Exact location | PDF page/line or repository path/line |
| Evidence | source, projection, package replay, or official-rule basis |
| Required action | exact edit/check, or explicit none |
| Claim IDs affected | one or more ledger IDs, or none |

End with one verdict: `ACCEPT_EXACT_BYTES`, `ACCEPT_AFTER_NONBYTE_RECORD_FIX`,
`REVISE_AND_REREVIEW_CHANGED_BYTES`, or `REJECT_CURRENT_SUBMISSION`.

R7 closes only after two independent responses to these exact bytes are
received and every material finding is closed or the affected claim is removed.
An internal author self-review does not count toward the two.
