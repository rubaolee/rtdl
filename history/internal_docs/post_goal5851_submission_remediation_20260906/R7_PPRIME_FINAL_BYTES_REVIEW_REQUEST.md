# R7 P-Prime Exact Final-Bytes Review Request

Date: 2026-09-06 America/New_York.

Please perform an independent hostile review of the exact P-prime PDF and the
unchanged nine-member artifact identified below. The old-P lead review verdict
was `REVISE_AND_REREVIEW_CHANGED_BYTES`; it is an input to this request, not an
approval of P-prime. Review the actual Git objects and delivery bytes rather
than trusting this request's summaries.

## 1. Exact identities

| Object | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor control E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Rejected old P | `c6020fd63097b35b5294778cf54c2fb84c879ad6` | `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |
| P-prime under review | `818c2ed284cde8acae9a09b531b8bfed3bf925ee` | `59e6eaacadac711f8b0d93980b1bfbbd3d772dc7` |

P-prime was pushed to `origin/codex/cgo-goal5836-handoff`.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 140,343 | `9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b` |
| `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 20,699 | `1d76d60b1f72487a414ef2fe649415938bc12a3ea6baedd65396b9378b4d90ed` |
| `paper/cgo2027/main.tex` | 38,521 | `ef2a5387f8b54ee8b571688ce90f80d22350006e042e7124eb99eb190f97288f` |
| `paper/cgo2027/references.bib` | 19,067 | `7eda90e69e190c3cbd545f86fbf964fa252b75265bc523a1d8dc06c9c9310c66` |

The source bundle is a custody/buildability aid, not presumed submission
material. The artifact is byte-identical to old P and F2; the PDF and source
bundle changed.

## 3. Controlling records

Read these files from P-prime or the current branch:

- `PROTOCOL_SCOPE_ADJUDICATION.md`
- `CLAIM_LEDGER.json`
- `R2_SUBMISSION_EVIDENCE_REPORT.md`
- `R5_FINAL_F2_REHEARSAL_REPORT.md`
- `R6_FINAL_DELIVERY_PAIR_AND_REPLAY_REPORT.md`
- `R7_LEAD_INDEPENDENT_FINAL_BYTES_REVIEW.md`
- `R7_OLD_P_CONTROL_RECORD_ERRATUM.md`
- `R7_PPRIME_LEAD_REMEDIATION_REPORT.md`

All paths except the paper and outputs are under
`history/internal_docs/post_goal5851_submission_remediation_20260906/`.
The remediation report and this request were added after the exact P-prime
commit; they are control records, not part of the reviewed PDF.

## 4. Binding decisions that must remain distinct

```text
machine_numerical_contract_passed = true
original_written_per_execution_receipt_requirement_fulfilled = false
wrong_output_observed_in_final_gpu_samples = false
public_prepared_a_over_direct_observation_retainable = true
implementation_entry_positive_performance_claim_allowed = false
```

The formal A population contains 4,096 timed public executions and 32 separate
post-loop diagnostic detailed receipts, one per A worker. Do not infer a
detailed physical receipt per timed call. Native and compact status are checked
before public output; an optional caller-supplied expected output is also
checked before return. The experiment worker validates the returned output and
digest after public return. The prepared steady timer ends at public return;
the first-result endpoints end after worker validation.

## 5. Endpoint and comparison identities

Implementation-entry starts immediately before implementation-specific imports
and ends after the first result and worker output validation. Post-import starts
after those imports and ends at the same validation boundary. Pinned PyOptiX
initializes CUDA context state during import, whereas RTDL does so lazily later;
the endpoints include different lifecycle work.

A/C implementation-entry had a historical registered criterion, but P-prime
treats it as a lifecycle-confounded, non-confirmatory diagnostic and makes no
positive entry claim. Only prepared A/E was a registered regression gate. A/E
first-result entry and post-import comparisons are post hoc, non-gating
diagnostics. D is a named Direct reference implementation, not a proved minimum
latency. E is a frozen predecessor control, not M's immediate parent.

## 6. Numerical rows to spot-check

| GPU/task | A/D median | A/D max | A/C entry | A/C post median | A/C post max | A/E entry | A/E post |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4090 Relation | 1.076852 | 1.092253 | 0.653826 | 1.749327 | 1.865823 | 1.192358 | 1.305383 |
| 4090 Triangle | 1.175066 | 1.211025 | 0.642180 | 1.559788 | 1.639385 | 1.079554 | 1.169262 |
| 3090 Relation | 1.094795 | 1.118811 | 0.681393 | 1.837415 | 2.377129 | 1.216714 | 1.261676 |
| 3090 Triangle | 1.133636 | 1.142675 | 0.618362 | 1.637468 | 1.652853 | 1.137637 | 1.162775 |

Lower is better. A/D observations cover two exact tasks and two GPU
generations; they do not prove Direct optimality, intrinsic language overhead,
cross-machine raw-time comparability, or general performance parity. Paired
instrumentation overhead was measured only for A.

## 7. Bounded generality and checker limits

- The stable public facade has two constructors; the bounded corpus contains
  four OptiX leaf kinds. This is not arbitrary Python, Callback IR, or
  topology-generic lowering.
- The canonical compilation plan is deliberately non-executable. Concrete
  topology-specific lowerers and wrappers remain trusted.
- The ten-row prospective domain was author defined from already-supported
  primitive/topology ingredients. Sphere any-hit count/continue was selected;
  curve any-hit terminate was only eligible. The selected route required about
  2,635 lines of topology-specific code and 28 modified compiler lines.
- The independent checker imports no RTDL module and covers three route groups,
  four modes, five property classes, 20 registered instances, and 15 unique
  mutations. It checks selected lexical patterns and ordering constraints; it
  is not partial evaluation, arbitrary-control-flow verification, or a
  soundness proof. Preserve the disclosed early-return miss.
- No independent human authoring study or representative prevalence
  measurement exists.

## 8. Known unrepaired limits

- A focused mock reproduced a provider double fault in which a secondary
  bind/close failure can replace the primary exception and lose cleanup retry
  ownership. It produced no public output and was not observed in retained
  successful GPU workers.
- The fork guard covers Python-managed forks invoking the registered at-fork
  hook. A native fork bypassing that hook can evade the cached-PID guard even
  if its child later calls the public API; inherited owner use is unsupported.
- The PDF is not tagged; source `Description` text is not a PDF/UA claim.
- The evidence artifact supports offline recount, not GPU rerun, product
  installation, or full reconstruction of private custody.

## 9. Artifact replay

Extract the exact artifact into a fresh directory and run:

```text
PYTHONNOUSERSITE=1 /usr/bin/python3 -I verify.py --artifact-root .
PYTHONNOUSERSITE=1 /usr/bin/python3 -I -O verify.py --artifact-root .
```

Expected status is `PASS__OFFLINE_PROJECTION_RECOUNT`; expected stdout SHA-256
is `c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`.
The archive has nine regular files, no links, normalized ownership/timestamps,
and no third-party source or binary.

## 10. Old-P finding closure to verify independently

Review each row of `R7_PPRIME_LEAD_REMEDIATION_REPORT.md`, especially:

1. Figure 1 timing and oracle order.
2. Exact lifecycle endpoint starts/ends and A/C versus A/E status.
3. Lexical/ordering checker wording.
4. Native-fork and provider-double-fault scope.
5. Implementation versus artifact terminology.
6. Direct, E, prepared endpoint, and instrumentation terminology.
7. Additive old-control-record erratum without historical rewrite.

## 11. Required verdict format

Report every finding with severity, exact PDF page/source location, evidence,
required action, and affected claim IDs. End with exactly one verdict:

```text
ACCEPT_PPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must identify the exact P-prime commit/tree and PDF/artifact
SHA-256 values. Any review of old P, reconstructed PDF bytes, or a different
artifact does not count. This request does not itself authorize claims or
submission.
