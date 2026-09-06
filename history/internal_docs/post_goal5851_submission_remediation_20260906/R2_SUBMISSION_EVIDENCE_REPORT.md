# R2 raw-to-table projection and offline-package execution report

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE__PRE_F_BODY_SUPERSEDED_BY_FINAL_F2_R5`

## Final F2 supersession notice

The body below preserves the original pre-F R2 rehearsal and its then-current
hashes. R5 is now closed at final tooling snapshot F2, commit
`9771facece4ccd807e26c15b21892b9d0a701d32`, tree
`11c62c28bdebcc7d437f8ab3326635af0832ce48`. The controlling final report is
`R5_FINAL_F2_REHEARSAL_REPORT.md`; the executable/evidence boundary is
`FREEZE_RECORD.md`.

F2 did not change the projection or recount bytes. It added an explicit
component/distribution inventory to generated `DEPENDENCIES.md` and one test.
Consequently, the final archive is 180,308 bytes with SHA-256
`916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`.
The F2 clean remote checkout passed 14/14 submission-evidence tests normally
and under `-O`, 128/128 Goal5848 tests normally and under `-O`, 7/7 Goal5851
tests, Ruff, twin deterministic export, overwrite rejection, and isolated
normal/optimized foreign-path replay. Any pre-F or F1 identity below is
historical and must not be cited as the final package identity.

This is an execution report, not a new plan, manuscript acceptance, artifact
review, or public-claim authorization. It records the actual pre-freeze tool
implementation and rehearsal required by R2. The final successful rehearsal
was subsequently repeated from a clean remote checkout of F2 under R5, as the
supersession notice records.

## 1. Preserved boundaries

- Measured implementation M remained
  `d653fe4ad170c5b51fee309d653c9565944dcf2e`, tree
  `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b`.
- Predecessor E remained
  `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8`, tree
  `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6`.
- No production, native, experiment, workload, timer, estimator, threshold, raw
  evidence, authority, recount, or archive byte was modified.
- `paper/cgo2027/artifact_post_goal5851/` is a committed template/tool-source
  root. Generated data and packages used new repository-external roots only.
- The exporter imports the frozen standard-library experiment contracts to
  validate raw worker receipts, but it does not import or call
  `evaluate_complete_transaction`. The packaged verifier imports no project
  module and uses only the Python standard library.

## 2. Implemented tool surface

| File | Purpose | SHA-256 at this rehearsal |
| --- | --- | --- |
| `scripts/goal5852_build_submission_evidence.py` | Validate exact raw inputs, project anonymous data, write private provenance, build deterministic package | `642f60ece4bd7f5848b19bfdf8a6c66556a2fb1ac70e3b68ad7d9d9e39c47c69` |
| `paper/cgo2027/artifact_post_goal5851/verify.py` | Standard-library exact-member, integrity, schedule, estimator, and oracle replay | `5a41e246412870118f1c11cb11a1622e86d8999d664dcf578eee638f63ec0100` |
| `tests/goal5852_submission_evidence_test.py` | Structural, mutation, overwrite, anonymity, and optimized-mode rejection tests | `e7217191c6e513d4bf3b4e652f025c75ac18eba9c6f701d2f8651831c24315c6` |

The frozen anonymous projection self-identity is
`fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca`.
The verifier contains this identity and rejects a different projection even if
an outer manifest is rebuilt.

## 3. Raw input validation

The exporter read each `EVIDENCE_MANIFEST.json`, recomputed its self-seal,
checked every listed member's path, byte length, and SHA-256, rejected symlinks
and unexpected files, checked the local archive digest against its sidecar, and
required the stored single-generation authority and recount to be byte equal.

| Generation | Manifest file SHA-256 | Members | Bytes | Authority/recount SHA-256 |
| --- | --- | ---: | ---: | --- |
| G0 Ada | `e71f98c713ee9c7c0bb5733d5ff1921d11eea5bc819ec3fea217961f9a690f6f` | 2,405 | 125,718,265 | `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7` |
| G1 Ampere | `9f1031c4fc07bf23635904f7f93e075a0a3c1a0ed5aaa21f6dc48e47d92b9340` | 2,405 | 125,646,793 | `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3` |

The cross-generation authority and recount were byte equal at
`99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692`.

For each formal worker, the exporter additionally validated the frozen
schedule, worker self-seal, M/E source exception, exact hardware equality,
output oracle, detailed retained execution evidence, process-receipt seal,
exit status, stdout/stderr hashes, and stdout-to-worker JSON equality.

## 4. Exported population

| Layer | Retained anonymous data | Recount result |
| --- | ---: | --- |
| Formal performance | 160 cells and 20,480 steady ns samples | 160/160 worker medians reconstructed |
| Lifecycle | Every non-Direct worker import, gap, post-import, entry, partition, and component field | Every worker reconciled before aggregation |
| Instrumentation | 1,024 Arm-A endpoint observations | Four paired block estimators reconstructed |
| AOT | 20 fresh-process hit durations plus four cold denominators | Four medians and hit/cold ratios reconstructed |
| Nonformal competence | 8 B/C workers and 1,024 steady samples | Eight medians and four ratios reconstructed |

Private provenance maps every projected formal, instrumentation, AOT, and
competence row to its raw relative path, raw file hash, and raw receipt hash.
It also retains real roots, commits, trees, hardware identities, manifest
identities, and anonymization rules. The private map is outside `public/` and
outside the tar archive.

The public boundary maps the raw predecessor arm name to
`E_FROZEN_RTDL_CONTROL`, uses neutral `submission_evidence` schema names, and
rejects any `Goal<digits>` token. Raw internal identifiers remain available
only in the private provenance and input validator.

## 5. Independently reconstructed performance tables

All ratios are numerator/denominator within one machine. The estimator uses
integer worker medians, rounded integer ppm per block, then the integer median
of eight block ratios.

| Generation/task | A/D prepared median | A/D observed max | A/C entry median | A/C post-import median | A/C post-import range |
| --- | ---: | ---: | ---: | ---: | ---: |
| Ada triangle | 1.175066x | 1.211025x | 0.642180x | 1.559788x | 1.527058x-1.639385x |
| Ada relation | 1.076852x | 1.092253x | 0.653826x | 1.749327x | 1.724948x-1.865823x |
| Ampere triangle | 1.133636x | 1.142675x | 0.618362x | 1.637468x | 1.608213x-1.652853x |
| Ampere relation | 1.094795x | 1.118811x | 0.681393x | 1.837415x | 1.815733x-2.377129x |

The A/D maximum is descriptive; the registered A/D gate has no worst-block
threshold. A/C implementation entry is lifecycle-confounded and is not
authorized as a positive performance claim. Post-import is adverse on all four
rows, and 2.377129x is retained as the maximum formal diagnostic block.

| Generation/task | A/E prepared median | A/E post-import | A/E entry |
| --- | ---: | ---: | ---: |
| Ada triangle | 0.903016x | 1.169262x | 1.079554x |
| Ada relation | 0.584438x | 1.305383x | 1.192358x |
| Ampere triangle | 0.922388x | 1.162775x | 1.137637x |
| Ampere relation | 0.608228x | 1.261676x | 1.216714x |

Only A/E prepared steady was a registered gate. The first-result A/E rows are
post hoc non-gating diagnostics: M improved prepared steady performance but
regressed all four median first-result rows relative to E.

All 32 A/D block ratios are retained in the generated recount summary:

```text
Ada relation:    1.092253 1.081622 1.071687 1.066402 1.081821 1.079510 1.074195 1.067929
Ada triangle:    1.173303 1.211025 1.176830 1.171694 1.188183 1.178393 1.158989 1.161689
Ampere relation: 1.094816 1.094538 1.094775 1.101122 1.091728 1.118811 1.100408 1.087112
Ampere triangle: 1.135639 1.130437 1.141042 1.142675 1.132267 1.135005 1.131221 1.124331
```

The verifier also reconstructed all A/C entry and post-import arrays, all A/E
steady, post-import, and entry arrays, and all C/B prepared arrays. Those exact
arrays remain in `data/recount_summary.json` rather than being shortened in
this report.

## 6. Lifecycle, instrumentation, AOT, and competence

Eight A/C lifecycle rows reproduced the separately aggregated import,
post-import, and entry medians. Each individual worker, not the medians, obeys
`entry = import + gap + post-import`; medians of components are explicitly
marked non-additive.

| Generation/task/arm | Import ms | Gap ms | Post-import ms | Entry ms |
| --- | ---: | ---: | ---: | ---: |
| Ada relation A | 77.533247 | 0.006601 | 455.176354 | 532.028248 |
| Ada relation C | 577.765364 | 0.008765 | 261.400088 | 841.974925 |
| Ada triangle A | 76.945387 | 0.006330 | 449.360871 | 526.017079 |
| Ada triangle C | 529.643869 | 0.009665 | 287.443064 | 817.456190 |
| Ampere relation A | 81.205542 | 0.004534 | 379.391600 | 460.452378 |
| Ampere relation C | 467.040680 | 0.006292 | 206.312319 | 673.359247 |
| Ampere triangle A | 80.106317 | 0.004614 | 370.675186 | 451.894144 |
| Ampere triangle C | 502.762916 | 0.005976 | 226.534499 | 729.125644 |

Arm-A instrumentation overheads were 2,781 ppm, 2,349 ppm, 2,431 ppm,
and 0 ppm for Ada relation, Ada triangle, Ampere relation, and Ampere triangle,
respectively. This qualification does not cover B or C.

AOT fresh-hit medians/hit-over-cold ratios were 78,176,935 ns/11,171 ppm,
76,826,501 ns/20,166 ppm, 58,279,761 ns/10,431 ppm, and
58,513,283 ns/19,626 ppm in the same row order. A cache hit is not first-ever
compilation, signing, cache fill, or deployment.

The nonformal preflight C/B ratios were 0.222572x, 0.599132x, 0.223010x,
and 0.655328x in the same row order. Formal C/B competence remains in the main
recount; neither layer proves a globally optimal baseline.

## 7. Deterministic package rehearsal

Two explicit nonexistent external roots were generated successfully:

```text
/tmp/rtdl-cgo2027-r2-anonymous-final-a-20260906-1745
/tmp/rtdl-cgo2027-r2-anonymous-final-b-20260906-1745
```

The public trees, private provenance files, export receipts, and tar archives
were byte-identical across the roots. Reusing the first root through the actual
CLI returned exit 1 with `output root already exists; overwrite refused`.

| Output | Identity |
| --- | --- |
| Projection self-seal | `fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca` |
| Projection JSON file | `94144ab768d669ebcdf83a12d018decd66a306f940fa4bf1cf18a1fcc91ae77f` |
| Recount summary self-seal | `54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105` |
| Recount summary JSON file | `2a98ea207004153b4e04c52a36ce3ae5940cc7a7ddbc5723caa3fb5f6d498ddd` |
| Manifest self-seal | `b0a26d5630815f65035f6c58e9429d865d47a52fd13ec7117eb3d2d0bbfa653a` |
| Manifest JSON file | `feba2ad47422559c867ac04b18a826c00f9aa859d9882c8bddf2b33acf305929` |
| Private provenance self-seal | `4a58eec716bf4694e6cacdde33151b21c6dd08b3a9d8ad630a0be2d6e18e57fb` |
| Private provenance JSON file | `ebeea758deb57ae23a00e8527f87ebb23cc0d5756718223b6f079b34ca899a81` |
| Export receipt self-seal | `5c6b83f5e1c4a7786cee62445b61240cabf38b2e8911930bc990aa0d4407b701` |
| Export receipt JSON file | `c65d0d2a13041a348ea49d39d1268013448408d94d261c720046171e16897576` |
| Deterministic archive | `963acc1c543df70609fccc06e0fa79f63b886be75b46699b9a2a51c662092639` |
| Archive bytes/members | 179,978 / 9 |

The archive was extracted under:

```text
/tmp/RTDL CGO artifact foreign replay 04/rtdl-cgo2027-artifact
```

With project `PYTHONPATH` removed and user site packages disabled, both normal
Python and `python -O` returned
`PASS__OFFLINE_PROJECTION_RECOUNT`. The extracted package reported 160 formal
workers, 20,480 formal samples, 1,024 instrumentation workers, 20 AOT
qualifications, 8 competence workers, `gpu_execution_performed=false`, and
`project_import_performed=false`. Text scanning found no forbidden author path,
workspace path, username, GPU UUID, SSH endpoint, internal-history token, GitHub
identity, or internal Goal identifier. The packaged verifier was byte-identical
to the template verifier.

## 8. Rejection tests and retained failed attempts

The new unit suite has 13 tests and passed in normal mode and under `python -O`.
The optimized-mode launcher additionally ran its mutation rejection in a
separate optimized child; that child passed rather than skipping. The suite
covers:

- missing formal worker;
- duplicate schedule cell;
- missing sample after coherent outer resealing;
- one modified ns with coherent row/projection resealing but stale sample
  digest;
- illegal M/E source substitution while accepting the exact E exception;
- wrong threshold and wrong gate type;
- malformed projection hash;
- unexpected public member;
- existing output-root overwrite;
- absence of internal Goal identifiers from the public verifier;
- rejection behavior under `python -O`.

The actual CLI and package verifier add exact raw manifest identities, complete
member hashes, frozen projection identity, exact public member set, and
deterministic archive metadata. A single raw mutation therefore fails the exact
input manifest before projection.

Seven pre-success defects or rejected attempts are retained rather than hidden:

1. The first shell wrapper was rejected by local command policy because it
   contained a destructive pre-clean step. No exporter execution occurred.
2. Bootstrap replay rejected a task-order mismatch between the new verifier
   and the frozen contract. The verifier was corrected to the contract's
   relation-then-triangle order.
3. The first generated package rejected its verifier because forbidden strings
   appeared literally in the verifier's own blacklist. Runtime concatenation
   preserved the checks without self-matching; a new output root was used.
4. Static analysis then found a late-bound loop closure in summary recount plus
   import/style defects. The ratio helper was moved outside the loop and Ruff
   now passes.
5. A nominally anonymous package still exposed internal Goal identifiers in a
   schema and predecessor arm name. Both were mapped to neutral public names,
   and the package verifier now rejects any `Goal<digits>` token.
6. Template imports wrote bytecode under the source-only template root. The
   exporter and test loaders now suppress bytecode writes; generated template
   bytecode was removed before the final rehearsal.
7. The first optimized-mode unit launcher let its child skip the actual
   mutation test. The child now mutates a sample and proves fail-closed
   rejection under `python -O`.

These were new-tool defects before candidate F, not failures or modifications
of the retained GPU evidence.

## 9. Regression result and remaining gate

The focused suite completed 65 tests with zero failures. It included the new
R2 tests plus Goal5848 contract, transaction-authority, and cross-generation
authority tests. Ruff and compilation checks passed. `git diff M -- src
include experiments` remained empty.

R2 was closed at this historical pre-F evidence scope. It did not authorize
paper wording or public claims. The formerly pending R5 transaction has since
passed at F2 as stated in the supersession notice. Claim authorization remains
false pending R4, R6, R7, and R8.
