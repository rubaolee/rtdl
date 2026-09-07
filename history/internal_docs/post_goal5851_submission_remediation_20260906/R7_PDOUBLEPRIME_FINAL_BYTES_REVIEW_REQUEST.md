# R7 P-Double-Prime Exact Final-Bytes Review Request

Date: 2026-09-06 America/New_York.

Please perform an independent hostile review of the exact P-double-prime paper
bytes and unchanged F2 evidence artifact below. The old-P verdict was
`REVISE_AND_REREVIEW_CHANGED_BYTES`; P-prime was author-remediated but received
zero independent acceptances before this novelty rewrite superseded it. Neither
old review, author audit, this request, nor a review of reconstructed bytes
counts as acceptance of P-double-prime.

Review the Git object and exact delivery bytes, not this summary.

## 1. Exact identities

| Object | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor control E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Frozen tooling F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |
| Rejected old P | `c6020fd63097b35b5294778cf54c2fb84c879ad6` | `dc4b78ba3ec0f7816f87b87fdd74353c806caced` |
| Superseded P-prime | `818c2ed284cde8acae9a09b531b8bfed3bf925ee` | `59e6eaacadac711f8b0d93980b1bfbbd3d772dc7` |
| **P-double-prime under review** | **`b28076ad568d3b7b36cfa48b0c5846accff3cb95`** | **`2a63fecbcf09727dbe4e38f83edb253d80fa3cab`** |

P-double-prime's parent is starting HEAD
`50ca45521013f56b141402f4902a3af189b469f9`. It changes literature,
manuscript, bibliography, control records, and generated paper/source delivery
bytes only. Its diff from the parent is empty under `src/`, `include/`,
`experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. No GPU run occurred.

## 2. Exact deliverables

| Deliverable | Bytes | SHA-256 |
| --- | ---: | --- |
| `output/pdf/rtdl_cgo2027_submission_candidate.pdf` | 143,803 | `a8d3194b07fbf0105b59944e8044da1769b9ca8877f92d3a93aa44f605b6aa84` |
| `paper/cgo2027/main.pdf` | 143,803 | `a8d3194b07fbf0105b59944e8044da1769b9ca8877f92d3a93aa44f605b6aa84` |
| `paper/cgo2027/main.tex` | 36,994 | `f75b29160f015d7c5de3dd0eae560e54df2933f5e065ec97170c2ac9f0f92186` |
| `paper/cgo2027/references.bib` | 20,196 | `a8c62657c74a42f39926974c4b655e0b83149beb1b548d1a0fa647115a82e6ab` |
| `output/source/rtdl-cgo2027-source.tar.gz` | 20,540 | `5f2bbc858b0b783983d773e09d46be92b0b47ebc6f87e079c1dd855ac42f55df` |
| unchanged `output/artifact/rtdl-cgo2027-artifact.tar.gz` | 180,308 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |

The PDF paths are byte-identical. The two-file source bundle is a normalized
custody/buildability aid, not presumed submission material. The nine-member F2
archive is unchanged from P-prime and supports offline evidence recount only;
it does not reproduce the novelty study, illustrative witness, GPU run, or
private historical custody.

## 3. Novelty-remediation records

Read these records from P-double-prime:

| Record | SHA-256 | Review purpose |
| --- | --- | --- |
| `novelty/RELATED_WORK_BOUNDARIES.md` | `4ce0c48d7e0131d5d6ee2e3de531f4973136955c48dc8b6f7d4beb084c24c847` | Proposition-level primary-source boundary audit |
| `novelty/PROTOCOL_WITNESS_AND_DERIVATION.md` | `12c13d5cb11e3773c4aff37089aae47013f45b6b1d7cb636fe967ed9b6244aca` | Fact-source, rejection-point, and lowering trace |
| `novelty/CGO_CONTRIBUTION_ARGUMENT.md` | `caefe3edb19e0b305c1919e44dccdf57f97c6266516faba0365fe9f2e874dcbc` | Bounded design/method contribution argument |
| `novelty/MANUSCRIPT_CHANGE_MAP.md` | `29c89d3e20a191e9f058b196f2e99eff5befa1fe322b45586f1271f0c70d3dd3` | Claim/evidence/source/PDF-page map |
| `novelty/EXECUTION_REPORT.md` | `557ede75ad743413d4348b6871350cd4a288111308b3e244d582bfdecf887fc9` | N0--N5 execution and limitations |

The paths above are relative to
`history/internal_docs/post_goal5851_submission_remediation_20260906/`.
Also read `CLAIM_LEDGER.json`, `PROTOCOL_SCOPE_ADJUDICATION.md`,
`R7_LEAD_INDEPENDENT_FINAL_BYTES_REVIEW.md`,
`R7_PPRIME_LEAD_REMEDIATION_REPORT.md`, and
`R5_FINAL_F2_REHEARSAL_REPORT.md`. All 24 claim flags remain false.

## 4. Core research question to adjudicate

The paper now claims one bounded systems-design contribution:

> For finite supported RT routes, make a protocol-carrying executable the
> admission unit across role/effect closure, semantic attribute ownership,
> physical binding, fail-closed continuation, and executable identity, and use
> that joint decision at materialization, load, lifecycle, and publication
> boundaries.

It separately presents one implementation method: restricted callbacks return
role-indexed typed effects; ABI lowering assigns fields/tags; a generated Numba
leaf writes those values; a trusted topology-specific wrapper checks the tag and
status before issuing OptiX payload, ignore, or terminate operations.

Determine whether the manuscript accurately presents this as a bounded
compiler-systems organization and implementation method rather than as a new
calculus, general algorithm, automatic semantic inference, generic topology
lowerer, soundness theorem, or exclusivity result.

## 5. Related-work challenge

Audit the N1 table and manuscript against the cited primary sources. In
particular:

1. Confirm that strong existing capabilities are acknowledged: PyOptiX and
   SlangPy Python access; OWL/Luisa construction; OptiX/Vulkan/DXR pipeline,
   interface, payload, and SBT rules; Slang capabilities/reflection/cursors;
   Dr.Jit and CrossRT generation; typestate, interface automata, session types,
   typed linking, and FFI checking.
2. Reject any sentence that turns a finite source study or a source's silence
   into "cannot implement," first/only, or impossibility.
3. Verify that `AUTHOR_BOUNDARY`, `DOCUMENTED_CAPABILITY`,
   `DERIVED_INFERENCE`, and `UNKNOWN` are used consistently and quotes remain in
   context and within the recorded quotation budget.
4. Confirm that the 2026 RT-core survey is only workload/mapping background and
   is not novelty-gap evidence.
5. Decide whether the incremental research value is stated concretely enough
   against protocol models and typed linking/FFI, rather than merely saying
   "we integrated five checks."

## 6. Witness and trust-boundary challenge

The `(100,0),(101,1)` same-width semantic-ABI mismatch is now explicitly
illustrative. No retained run executed that defective route. Existing evidence
is mutation sensitivity and integrated pre-native-load rejection plus a mocked
adjacent correct control. Verify that no abstract, introduction, body, figure,
or conclusion upgrades it to executed evidence.

Check the source trace independently:

- semantic ownership originates in a trusted bounded-relation schema;
- the compiled contract carries its row source into a separately derived target
  projection inside the same compiler TCB;
- a wrong but internally coherent trusted schema can pass;
- CP002 mutation proves check liveness, not semantic inference;
- CP005 hash equality proves identity coherence, not program semantics;
- materialization and preparation reject before native load, while runtime
  status/optional expected-output checks precede public return and the worker
  oracle follows return.

Any stronger statement should be a finding against claims 022 or 023.

## 7. Generality and implementation-cost challenge

- Stable public scope is two constructors; the bounded corpus contains four
  leaf kinds. It is not arbitrary Python or Callback IR.
- The canonical plan is non-executable. Concrete lowerers and wrappers remain
  topology-specific TCB.
- The prospective ten-row domain was author defined from supported ingredients;
  all continuations were per-query count. One sphere composition was selected.
- That route required about 2,635 new topology-specific lines and 28 compiler
  line changes despite three sealed shared files remaining byte-identical.
- The independent checker covers finite target structures and missed an
  out-of-authority early-return probe for selected helper checks.
- There is no independent-user authoring evidence or prevalence measurement.

Ensure the paper treats these as scope limits, not as proof of generic lowering,
unseen-workload generalization, formal verification, or ease of use.

## 8. Performance and custody facts that must remain distinct

```text
machine_numerical_contract_passed = true
original_written_per_execution_receipt_requirement_fulfilled = false
wrong_output_observed_in_final_gpu_samples = false
public_prepared_a_over_direct_observation_retainable = true
implementation_entry_positive_performance_claim_allowed = false
```

The main A population has 4,096 timed calls but only 32 separate post-loop
detailed receipts. Prepared timing ends at public return; worker validation is
outside it. First-result endpoints include validation and remain lifecycle/import
confounded. All A/C post-import medians are adverse, and the worst block is
2.377129x. A versus E regresses about 8--22% at entry and 16--31% post-import;
those first-result A/E comparisons are post hoc and non-gating. Paired timer
instrumentation exists only for A. Direct is named, not proved optimal.

Spot-check the exact numerical rows in Section 6 of the superseded P-prime
request; P-double-prime changes their framing and layout, not the measurements.
No cross-machine raw-time, intrinsic-overhead, broad parity, or speedup claim is
authorized.

## 9. Unrepaired and artifact limits

- Provider double fault can replace the primary exception and lose cleanup
  retry ownership; a focused mock reproduced it. It emitted no public output and
  did not occur in retained successful GPU workers.
- A native fork bypassing the registered Python at-fork hook can evade the
  cached-PID guard; inherited owner use is unsupported.
- The finite checker is not arbitrary-control-flow or semantic verification.
- The PDF is untagged; no PDF/UA claim is made.
- F2 recount is not GPU rerun, product installation, novelty verification, or
  reconstruction of private history.

## 10. Byte and format checks

Verify from P-double-prime that:

- PDF is anonymous, eight US-Letter pages, review mode with page/line numbers,
  and has no clipping, overlap, missing glyph, unresolved citation/reference,
  or overfull box;
- all fonts are embedded; private paths, usernames, hosts, keys, internal Goal
  IDs, and author identities are absent from PDF text and metadata;
- the source archive has only normalized directories plus `main.tex` and
  `references.bib`, and builds from a foreign path;
- the two PDF paths are byte-identical;
- F2 artifact has nine regular members and the exact unchanged hash;
- no executable-path diff exists from P-double-prime's parent.

The previous author-side source replay and page inspection are evidence to
challenge, not independent acceptance.

## 11. Old-P finding mapping

Recheck every old-P finding against new bytes:

1. Figure 1 timer/public-return/worker-oracle ordering.
2. Entry and post-import endpoint definitions and confirmatory status.
3. Finite lexical/ordering checker wording and early-return miss.
4. Native-fork and provider-double-fault scope.
5. Implementation, source bundle, and evidence artifact terminology.
6. Direct/E/prepared/instrumentation terminology and all adverse values.
7. Append-only historical errata and no rewritten old control record.

Then additionally adjudicate the three novelty claims 022--024 and all N1/N2
trust limits. Closing old findings alone is insufficient.

## 12. Required verdict format

Report each finding with severity, exact PDF page/source location, evidence,
required action, and affected claim IDs. End with exactly one verdict:

```text
ACCEPT_PDOUBLEPRIME_FINAL_BYTES
REVISE_AND_REREVIEW_CHANGED_BYTES
REJECT_CLAIM_OR_SUBMISSION_SCOPE
```

An acceptance must repeat the exact P-double-prime commit/tree, PDF SHA-256, and
F2 SHA-256. Review of old P, P-prime, rebuilt PDF bytes, or another artifact does
not count. Two independent acceptances are required. This request authorizes no
claim, upload, or submission.
