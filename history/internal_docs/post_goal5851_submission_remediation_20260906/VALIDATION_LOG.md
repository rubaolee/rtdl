# Post-Goal5851 remediation validation log

Date: 2026-09-06

This is an append-only execution log. A successful command proves only the
scope stated beside it. It does not authorize a paper claim.

## R0 repository snapshot

Captured at `2026-09-06T16:19:39-0400`:

```text
branch=codex/cgo-goal5836-handoff
HEAD=04bd1d54f4641f12b6cf8e19a9e9eef5767a2021
HEAD_tree=06966bf16ea8ab1a2e8027543d8c00985c7389a6
measured_M=d653fe4ad170c5b51fee309d653c9565944dcf2e
measured_M_tree=d53af23a2599f9d6adb4ac0bfff39cd0ab31860b
predecessor_E=12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8
```

Commands executed with exit code 0:

```bash
git branch --show-current
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
git status --short
git diff --name-status d653fe4ad170c5b51fee309d653c9565944dcf2e..HEAD
git diff --cached --name-status
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
git rev-list --left-right --count '@{upstream}...HEAD'
```

The working tree was already dirty. Ownership is recorded in `STATUS.json`.
No pre-existing dirty file was reverted or staged. `git add -A` was not used.
The staged set was empty; the branch tracked
`origin/codex/cgo-goal5836-handoff` at zero ahead and zero behind.

The reviewed action-plan bytes were preserved before amendment:

```bash
git hash-object -w history/internal_docs/codex_final_action_plan_after_gpt6_claude_goal5851_20260906.md
```

Result: exit 0, Git blob
`98cfa4e85d435e9cb246eb0ffe4060c5bf31ac4f`, corresponding to reviewed
SHA-256 `6c3b1722b07a6e13d664a3f448f5d70ab1ac80fbe8bd413f94ff4b1d05a25136`.

## Four mandatory plan corrections

The current action plan applies all four strict-review corrections. A
structural check verified the required final-F sequence, separate template and
generated roots, minimum adverse main-text facts, and both Goal5838 IDs. The
actual selected ID was independently read from
`history/internal_docs/goal5838_generic_core_exam_20260902/FINAL_AUTHORITY.json`.

Current action-plan SHA-256:
`8cd80920667e56f15ef64802cc680e3a604529239abdcf55941ef2f395f1e282`.

One initial text assertion returned nonzero because it searched for the exact
single-line phrase `template and tool-source root only` while the plan uses
the semantically equivalent text `committed, frozen template and tool-source
root`. Direct inspection and the corrected structural check found the required
template/output separation. This failed assertion did not modify any file and
is retained here rather than hidden.

This closes only the plan-text corrections. It does not claim that F, the
artifact, or the final PDF exists.

## R0 evidence roots

A Python read-only verifier loaded both `EVIDENCE_MANIFEST.json` files,
recomputed each listed member's byte length and SHA-256, checked manifest
self-seals by canonical JSON encoding without `manifest_sha256`, and compared
the stored authority and recount bytes. Results:

```text
Ada:    2405/2405 members, 125718265 bytes, 0 hash failures, 80 workers
Ampere: 2405/2405 members, 125646793 bytes, 0 hash failures, 80 workers
Ada authority == recount: byte-identical
Ampere authority == recount: byte-identical
Cross-generation authority == recount: byte-identical
```

The exact paths and hashes are in `EVIDENCE_INDEX.json`.

Direct execution of each archived `.sha256` sidecar with `shasum -c` returned
exit 1 because the sidecar records its original `/workspace/...` absolute
path. Reading the expected digest and hashing the local archive by its local
basename succeeded for both archives. This is recorded as a portability
boundary, not a payload failure and not a PASS for the future anonymous
artifact.

## R0 toolchain

Actually probed tools:

```text
Python=/Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python
Python_version=3.12.14
Tectonic=/opt/homebrew/bin/tectonic
Tectonic_version=0.16.9
pdfinfo=/Users/rl2025/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdfinfo
pdftoppm=/Users/rl2025/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm
pdftotext=missing_from_current_PATH
qpdf=missing_from_current_PATH
mutool=missing_from_current_PATH
exiftool=missing_from_current_PATH
ghostscript=missing_from_current_PATH
numpy=2.4.4
numba=0.65.1
llvmlite=0.47.0
```

The current Python 3.12 environment did not report installed `setuptools`,
`pypdf`, or `pdfplumber`. These are not needed for the R0 Tectonic build, but
R6/R8 must use frozen available tooling or explicitly install and record a
dependency before the development freeze if executable support is needed.

## R0 old-manuscript environment probe

Executed from the repository root:

```bash
/opt/homebrew/bin/tectonic --only-cached --keep-logs --keep-intermediates \
  --outdir /tmp/rtdl-r0-manuscript-RKaSidUy paper/cgo2027/main.tex
```

Result:

```text
exit_code=0
PDF=/tmp/rtdl-r0-manuscript-RKaSidUy/main.pdf
PDF_sha256=140950d8dd5aa7edf6611e3fd7bfbe131d1afcbad7b464c9e95dc4386d249ad1
PDF_bytes=232764
PDF_pages=17
PDF_page_size=Letter
main_tex_sha256=d9cf2dc38f83e6545c4880efd6f101be27553c6729f41dcc7afe0e126c504716
references_bib_sha256=78b40edfe825b5c99bcde53456566e8e5d00179a09399efabc41058bb6562314
tectonic_log_sha256=7fc45fd16cd8dbf2c8d6a434ee771c4d36db2be4fb88b5040d22a48283347300
overfull_log_entries=107
```

The durable Tectonic log is `R0_OLD_MANUSCRIPT_BUILD.log`. No undefined
citation/reference message was observed in that log. The 17-page stale paper
and 107 overfull entries make this an environment PASS only, not a manuscript
or formatting PASS.

## R0 disposition

`R0=CLOSED_WITH_EVIDENCE` at the stated inventory scope. `R1=IN_PROGRESS`.
R2 through R8 remain open. No production, native, experiment, workload,
timer, estimator, threshold, or GPU execution changed.

## R1 receipt-scope adjudication and claim ledger

Direct source inspection separated four phases: native establishment,
successful pre-return checks, deferred detailed validation, and formal-worker
retention. The resulting adjudication inventories all 27 `_FastPathReceipt`
fields and separately covers raygen count, traversable identity, output digest,
and monotonic execution identity. The binding result is:

```text
machine_numerical_contract_passed=true
original_written_per_execution_receipt_requirement_fulfilled=false
wrong_output_observed_in_final_gpu_samples=false
public_prepared_a_over_direct_observation_retainable=true
implementation_entry_positive_performance_claim_allowed=false
```

Read-only recount of all 32 final Arm-A workers found 128 timed samples in each
worker, `latest_output_sha256=null` in each worker, one separate diagnostic
receipt in each worker, and one worker-level expected output digest in each
worker. Thus the evidence contains 4,096 timed A calls and 32 separate
diagnostic calls, not 4,096 detailed timed-call receipts.

The additive correction preserves the earlier historical self-review but
corrects its statement that timed receipts were materialized and bound after
timing. No authority, raw worker, archive, production source, native source, or
experiment source was modified.

Machine validation performed:

```text
python3 -m json.tool CLAIM_LEDGER.json: exit 0
claim_count=21
unique_claim_ids=21
required_fields_per_claim=10/10
all_claim_authorized=false
all referenced repository source hashes match=true
all referenced evidence roots readable=true
mandatory selected/candidate, adverse, receipt, human=0 boundaries present=true
trailing_whitespace_findings=0
```

R1 output identities:

```text
PROTOCOL_SCOPE_ADJUDICATION.md sha256=53b5f6028f6f549be0012bb949e46dfff0ed6823d02bff96bff672f53bed6531
RECEIPT_CLAIM_CORRECTION.md sha256=9ba0723900c2a648338b6d7f7a72a05d944b96e799025c6dd7481c28988a8a72
CLAIM_LEDGER.json sha256=d07e675d759d7b8f8ead8301632748d7bbbb60b60cd222eae43f97d03ba9493e
```

`R1=CLOSED_WITH_EVIDENCE`. This closes the scope decision, not the underlying
per-execution receipt, provider double-fault, or unsupported native-fork
implementation defects. No paper claim is authorized before R2 projection,
R4 rewrite, R6 replay, and R7 review of final bytes.

## R2 anonymous projection and offline recount rehearsal

R2 implemented a deterministic, fail-closed raw-evidence exporter and a
standard-library-only packaged verifier. Generated files were written only to
new repository-external roots; `paper/cgo2027/artifact_post_goal5851/` remained
a template and tool-source root. The exporter validated both 2,405-member raw
manifests, every listed byte/hash/path, authority/recount equality, all formal
worker contracts, process receipts, source identities, hardware identities,
and output oracles before projection.

The anonymous projection retained 160 formal cells, 20,480 steady samples,
1,024 instrumentation endpoints, 20 AOT durations, eight competence workers,
and all required lifecycle fields. Its self-seal was:

```text
f3dda1e5427e5b2d30d4a07f910c4dc639c2b66697e7d2f55b014c64e5e77a99
```

Two independent builds at the following new roots were byte-identical:

```text
/tmp/rtdl-goal5852-r2-a-20260906-1648-002
/tmp/rtdl-goal5852-r2-b-20260906-1648-003
```

The deterministic nine-member archive was 179,819 bytes with SHA-256:

```text
7094e9d3dc0d4922aebd81994373b122d7c77c053da84e5ec5388d1aef8dacaf
```

The archive was extracted under a path containing spaces and replayed with the
project removed from `PYTHONPATH`, user-site packages disabled, and then again
under `python -O`. Both returned `PASS__OFFLINE_PROJECTION_RECOUNT`; the
package reported no GPU execution and no project import. A text scan found no
forbidden author path, workspace path, username, GPU UUID, SSH endpoint, or
internal-history token. Reuse of an existing output root failed closed.

Machine checks completed:

```text
new R2 unit suite: 12/12 normal
new R2 unit suite under python -O: 11 active PASS, 1 parent launcher SKIP
focused Goal5848/Goal5852 regression: 64/64 PASS
Python compilation checks: PASS
assert statements in exporter/verifier: 0
git diff M -- src include experiments: empty
```

Retained pre-success tool failures:

1. A first shell wrapper containing a destructive pre-clean command was
   rejected by local command policy before exporter execution.
2. Bootstrap replay exposed task-order disagreement between the new verifier
   and frozen contract; the verifier was corrected to the frozen order.
3. The same correction exposed one oracle lookup that still assumed the old
   positional order; it was replaced by task-keyed lookup.
4. A first generated verifier contained forbidden identity strings literally
   in its own blacklist and self-matched; runtime byte concatenation preserved
   the checks without exposing those literals, and a new output root was used.

Output identities at closure:

```text
R2_SUBMISSION_EVIDENCE_REPORT.md sha256=2b2b0eff131e4d9e75c773379b70d1bbecfce355185586020a0f6abfde1d4096
CLAIM_LEDGER.json sha256=4fb50fefb5fd564e90233c078714b460f00f10cd26b53ecf4233f757cb2bf3df
verify.py sha256=5cfa27f8c0500c7b36d1f505fcd0b5def073a8825590a7cfc93c28926a31badd
goal5852_build_submission_evidence.py sha256=81c206d19ebb0cd7e43177964cee28d31430156857479c5bedf241b2a027c2b1
goal5852_submission_evidence_test.py sha256=28a3b0b891cb4d49805379b4dfd2f9f3692fc4bb36b0f8a0531bcf75d1cc4f16
```

`R2=CLOSED_WITH_EVIDENCE_PRE_F`. This is a rehearsal, not the final artifact
gate. R5 must repeat the indivisible chain from a clean checkout of committed
candidate F and prove the packaged verifier is byte-identical to F. Public and
manuscript claims remain unauthorized.

## R3 current-control and exact-snapshot custody reconciliation

R3 updated only current control documents and added an errata ledger. It did
not edit historical authorities, reviews, calls for review, raw evidence, or
archives. The ledger contains 14 corrections with original locations and
replacement facts, including the malformed Ada digest, Direct gate semantics,
receipt retention, A-only instrumentation, Goal5838 candidate roles and
selection, finite Goal5840 scope, and three contradictions/overstatements in
the returned review prose.

The two omitted custody checks were executed first on the current tree:

```text
PYTHONPATH=src:. python scripts/goal5837_freeze_owner_grouped_classification.py --verify-stored
exit=1
Goal5837Error: AUTHORITY_CURRENT_INPUT_MISMATCH

PYTHONPATH=src:. python scripts/goal5843_build_final_authority.py --verify-stored
exit=1
Goal5843ContractError: preregistration differs from canonical builder
```

Fresh local clones were then checked out at each historical sealing commit.
The unchanged commands returned exit 0:

```text
Goal5837 commit=0f5c9d4297f73e412732e5a8ab133423fe4cfd21
Goal5837 tree=5b80f7f07807679a7ea9eae5e7b29b303ab387ed
Goal5837 authority_self_seal=025090252ac60b722cc398402297656877405a998024d221592e18aa888f0465

Goal5843 commit=75b2b34fad1f0280a43ce6cbc00e99d4b9d9d937
Goal5843 tree=50fc7f1b60fbbf1ecbf65cd99c02f5c39b6717f8
Goal5843 authority_self_seal=c40b9fe5d3ace2f58fe29a1a39363ce25373332f774f3c36ffa839ce650bdba8
```

Current-document checks:

```text
relative Markdown links checked=7, missing=0
Goal5838 eligible candidates=10
Goal5838 four-role candidates=7
Goal5838 six-role candidates=3
Goal5838 selected=builtin_sphere::any_hit_count_continue_u64_per_query
git diff --check=PASS
git diff M -- src include experiments=empty
active-current malformed Ada digest reuse=0
stale paper README 324-worker/7128-timing/18-row text=0
```

R3 output identities:

```text
R3_CONTROL_AND_CUSTODY_CORRECTION_LEDGER.md sha256=74525efb2b30f73c3de0d30d5ff3a3125a6577228db5a090b8a1700e3ae5cf33
AGENTS.md sha256=9f77c3f9c261e15530e87462a8ebfd740cdd0cec59563ef512846b045ae8535f
KNOWN_STALE_CUSTODY_CHECKS.md sha256=9fa769bf587dc27db4bf772557d38e4697f049d6aa78178d37802b91762ae991
README.md sha256=c52eb28a97bdd34d5c286a08a620c1042ce135939a35ea5e4a034a26c27ff98d
paper/cgo2027/README.md sha256=53e3fe4667347cc5e013fde88d818756a6f40ed50610446828162af50765a31d
cgo2027_final_sprint_goals_20260905.md sha256=dd4b7676b7c93af04bdc7373a3a1a57bbc2469782c07030acfa41938a18eabe6
memory/decisions.md sha256=cc62cf08052988ec8eb37fa0a3f078c187c7d84af55ba99ad36a46708e2afd7c
memory/progress.md sha256=d9a56c6f05a36e90c58c69ba4857ff5e16721509b9fea92ba6996e91f016fd2d
memory/todo.md sha256=d55252812fd01dae1379a3e3b878cf9cedf06960ad805e277c8417329134944b
```

`R3=CLOSED_WITH_EVIDENCE`. Candidate F and its clean-checkout rehearsal remain
open under R5. Current claim authorization remains false.

## R2 pre-F corrective successor after static and anonymity self-audit

The earlier R2 entry above remains a historical pre-F attempt. It was
superseded before candidate F after static analysis and direct inspection of
the extracted public package found four defects: a late-bound recount closure,
internal Goal identifiers in public schemas and the predecessor arm, bytecode
written into the source-only template root, and an optimized-mode unit child
that skipped rather than executed its mutation rejection. None affected raw
GPU evidence or numerical results. All four were fixed before this successor
rehearsal.

Current tool identities:

```text
paper/cgo2027/artifact_post_goal5851/verify.py sha256=5a41e246412870118f1c11cb11a1622e86d8999d664dcf578eee638f63ec0100
scripts/goal5852_build_submission_evidence.py sha256=642f60ece4bd7f5848b19bfdf8a6c66556a2fb1ac70e3b68ad7d9d9e39c47c69
tests/goal5852_submission_evidence_test.py sha256=e7217191c6e513d4bf3b4e652f025c75ac18eba9c6f701d2f8651831c24315c6
```

Each of these two commands returned exit 0; only `--output-root` differed:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python scripts/goal5852_build_submission_evidence.py --ada-root /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass --ampere-root /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass --cross-root /Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete --template-root /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/artifact_post_goal5851 --output-root /tmp/rtdl-cgo2027-r2-anonymous-final-a-20260906-1745
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python scripts/goal5852_build_submission_evidence.py --ada-root /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ada_d653fe4_pass --ampere-root /Users/rl2025/RTDL_evidence/goal5848/goal5851_successor_ampere_d653fe4_pass --cross-root /Users/rl2025/RTDL_evidence/goal5848/goal5851_cross_generation_d653fe4_complete --template-root /Users/rl2025/rtdl_v4_restricted_python_design/paper/cgo2027/artifact_post_goal5851 --output-root /tmp/rtdl-cgo2027-r2-anonymous-final-b-20260906-1745
```

`diff -qr` across the two complete output roots returned exit 0. Reusing root
A through the actual CLI returned exit 1 and
`output root already exists; overwrite refused`. Both raw manifest file hashes
and the cross-generation authority remained unchanged:

```text
Ada manifest=e71f98c713ee9c7c0bb5733d5ff1921d11eea5bc819ec3fea217961f9a690f6f
Ampere manifest=9f1031c4fc07bf23635904f7f93e075a0a3c1a0ed5aaa21f6dc48e47d92b9340
cross authority=99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692
```

Current output identities:

```text
projection self=fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca
projection file=94144ab768d669ebcdf83a12d018decd66a306f940fa4bf1cf18a1fcc91ae77f
summary self=54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105
summary file=2a98ea207004153b4e04c52a36ce3ae5940cc7a7ddbc5723caa3fb5f6d498ddd
manifest self=b0a26d5630815f65035f6c58e9429d865d47a52fd13ec7117eb3d2d0bbfa653a
manifest file=feba2ad47422559c867ac04b18a826c00f9aa859d9882c8bddf2b33acf305929
private provenance self=4a58eec716bf4694e6cacdde33151b21c6dd08b3a9d8ad630a0be2d6e18e57fb
private provenance file=ebeea758deb57ae23a00e8527f87ebb23cc0d5756718223b6f079b34ca899a81
export receipt self=5c6b83f5e1c4a7786cee62445b61240cabf38b2e8911930bc990aa0d4407b701
export receipt file=c65d0d2a13041a348ea49d39d1268013448408d94d261c720046171e16897576
archive sha256=963acc1c543df70609fccc06e0fa79f63b886be75b46699b9a2a51c662092639
archive bytes=179978
archive members=9
```

The archive was extracted to
`/tmp/RTDL CGO artifact foreign replay 04/rtdl-cgo2027-artifact`. With
`PYTHONPATH` removed, user site disabled, and isolated mode enabled, both
`/usr/bin/python3 -I verify.py --artifact-root .` and
`/usr/bin/python3 -I -O verify.py --artifact-root .` returned exit 0 and
`PASS__OFFLINE_PROJECTION_RECOUNT`. `cmp` proved the packaged verifier
byte-identical to the template. The identity scan for internal Goal numbers,
author/workspace paths, username, GPU UUID, SSH endpoint, internal-history
path, GitHub identity, and author name returned no match. Archive members were
regular mode-0444 files with uid/gid zero, empty owner/group names, and mtime
zero. The template root contained only `verify.py` after the builds.

Final pre-F static and regression checks:

```text
R2 unit suite: 13/13 PASS
R2 unit suite under python -O: 13/13 PASS
explicit optimized mutation child: 1/1 PASS
focused Goal5848/Goal5852 regression: 65/65 PASS
Ruff: PASS
JSON parse for CLAIM_LEDGER/EVIDENCE_INDEX/STATUS: PASS
git diff --check excluding exact raw R0 transcript: PASS
git diff M -- src include experiments: empty
```

Current record identities at this checkpoint:

```text
R2_SUBMISSION_EVIDENCE_REPORT.md=3f5585470558c9e0ab47ee1ea93cedaebdc08eb7531a0283ce5d9b7494acd439
CLAIM_LEDGER.json=c1ecbd56b2c6d0f4fd157770b38e404247f066d7d00cdf0e09aad1f31a3d44ca
EVIDENCE_INDEX.json=758fe3fc16c36ff42753c353bdd9bae79671734bc15e6fe37fbc584b1d89763f
STATUS.json=d0068e29632165e2d4360758977e6957328fd731149f963e63880dbd032ef63b
memory/progress.md=00c3da70989f34e3dd76d75af2e12a71352c74426fffb250234e97544e897645
```

This closes the corrected pre-F R2 rehearsal only. Candidate F remains
uncommitted, its required clean-checkout replay remains pending under R5, and
public/manuscript claim authorization remains false.

## R5 committed-F clean-checkout rehearsal

Candidate F was committed and pushed:

```text
commit=61190073428fbe487721262cfe1f4a77d4cb5d2f
tree=2f2aa13221d2e1f7777b03e0ef3b1fd9feefcf6f
remote=origin/codex/cgo-goal5836-handoff
remote ref after push=61190073428fbe487721262cfe1f4a77d4cb5d2f
```

The first remote clone command exceeded its command window and left no
resolvable `HEAD`; no output from that state was used. The new repository was
completed with an exact remote fetch and detached switch to F. Its status was
clean before and after all operations. From that checkout, the 65-test focused
suite and Ruff passed, then the complete exporter ran successfully into two
new external roots:

```text
/tmp/rtdl-cgo2027-R5-F611900734-build-a-20260906-1722
/tmp/rtdl-cgo2027-R5-F611900734-build-b-20260906-1722
```

The complete roots were byte-identical. Both reproduced the pre-F projection,
summary, manifest, private provenance, receipt, and archive identities. Reuse
of root A returned exit 1 with overwrite refused. The archive was extracted to
`/tmp/RTDL CGO final F replay 611900734/rtdl-cgo2027-artifact`; isolated normal
and optimized Python replay both returned exit 0 and
`PASS__OFFLINE_PROJECTION_RECOUNT`. The public identity scan returned no match,
and the packaged verifier was byte-identical to F.

```text
projection=fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca
summary=54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105
manifest=b0a26d5630815f65035f6c58e9429d865d47a52fd13ec7117eb3d2d0bbfa653a
archive=963acc1c543df70609fccc06e0fa79f63b886be75b46699b9a2a51c662092639
archive_bytes=179978
archive_members=9
R5_FINAL_F_REHEARSAL_REPORT.md=249a012cf7435c2dc40f998dc657173201ea773cfe015c02a88c67fb5e4f734c
CLAIM_LEDGER.json=f148027baa49756bdd22d24d7c5c77058a951653dd73edf9308a97cb412370d8
EVIDENCE_INDEX.json=dcb2202f9a572d302606057b81dcd66eadddd06cba469a071b34f5e548ba5be4
STATUS.json=fd29698dd296b6d3a54e9160be6913ebcdecb30f2f3ba4e8d135d0b80aae8e03
memory/progress.md=0ee3675a5d396f07d76d2b02dbb6966d9c4f11706f73925a16d289b30252a1fc
```

`R5=CLOSED_WITH_EVIDENCE`. R4, R6, R7, and R8 remain open, and claim
authorization remains false.

## Final F2 component-boundary successor and clean replay

F1 remains a retained pre-final tooling snapshot. Inspection against the R6
acceptance text found that its `DEPENDENCIES.md` did not explicitly inventory
the packaged project-authored components or their distribution basis. The
exporter was changed before the hard freeze to produce that component boundary,
and its test suite gained one focused check. No measured source, experiment,
raw input, projection row, numerical summary, or verifier changed.

Three pre-commit development test invocations failed while narrowing the new
test: two incorrectly routed a synthetic fixture through frozen production
projection/numerical identities, and one matched a phrase split across a
Markdown newline. The final test inspects only the static generated inventory.
No verifier or numerical gate was weakened.

F2 was committed and pushed:

```text
commit=9771facece4ccd807e26c15b21892b9d0a701d32
tree=11c62c28bdebcc7d437f8ab3326635af0832ce48
remote=origin/codex/cgo-goal5836-handoff
remote ref after push=9771facece4ccd807e26c15b21892b9d0a701d32
verifier=5a41e246412870118f1c11cb11a1622e86d8999d664dcf578eee638f63ec0100
exporter=ba3075214564cad6b51dfea93cb8741c100d19f149ecd5b5d1a70eee89ffabd1
tests=a75d897032d44becdc4838ec49c1ffe31119943adf0f8d4735fbc9277047dcd9
```

A new empty repository fetched the remote branch at depth one and detached at
F2 under `/tmp/rtdl-cgo2027-F2-9771face-clean`. It was clean before and after
the transaction. Actual clean-F2 results:

```text
submission-evidence tests: normal 14/14 PASS; -O 14/14 PASS
Goal5848 discovery: normal 128/128 PASS; -O 128/128 PASS
Goal5851 fused replay: 7/7 PASS
Ruff: PASS
skips=0
```

Two new external roots were built successfully and were byte-identical:

```text
/tmp/rtdl-cgo2027-F2-9771face-build-a-20260906-173128
/tmp/rtdl-cgo2027-F2-9771face-build-b-20260906-173128
```

Actual CLI reuse of root A returned exit 1 with overwrite refused. The first
foreign extraction command incorrectly duplicated the archive's own top-level
directory and then returned exit 2 because `verify.py` was not in that mistaken
cwd. The failed directory was retained and not reused. Extraction into the
second new parent succeeded at
`/tmp/RTDL CGO final F2 replay 9771face retry/rtdl-cgo2027-artifact`.
Both `/usr/bin/python3 -I` and `-I -O` returned exit 0 and
`PASS__OFFLINE_PROJECTION_RECOUNT`. Verifier `cmp`, public identity scan, and
archive metadata checks passed.

```text
projection self=fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca
projection file=94144ab768d669ebcdf83a12d018decd66a306f940fa4bf1cf18a1fcc91ae77f
summary self=54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105
summary file=2a98ea207004153b4e04c52a36ce3ae5940cc7a7ddbc5723caa3fb5f6d498ddd
manifest self=4a62601b0e421033e67169ed3f89818c6cf62b8acc7723df9cc3ca4c8a46fc32
manifest file=da73f16918c572dbffc5d803627837ae412197afc3ea9eee341b4989d9b494d8
private provenance self=12b47d35ddde66259343bb59b76fca3d93048af9e2908381352ccf01ddc3fc85
private provenance file=97ac92b95af2d0f21c2445b1ef533c9a686181bff236561f2db4a45f328a037f
receipt self=9294627a889356590b7a2ea53e126fb40711a7aefb739788e8ec0294dc67a522
receipt file=6e03835f3b53a1a49dfab6b4f095a6c5cc2f984c07d0508c5cc7492ec98f099c
archive=916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8
archive_bytes=180308
archive_members=9
```

`R5_FINAL_F2_REHEARSAL_REPORT.md` and `FREEZE_RECORD.md` now control R5.
F2 is immutable. R4, R6, R7, and R8 remain open, and claim authorization
remains false.

## P-prime post-lead-remediation verification

Timestamp: 2026-09-06T21:44:17-0400

The independent lead review of old P was preserved byte-for-byte at SHA-256
`c449a6c6eed4f177496a762b38f13434a09b1447aa3b3521db56c66b818d5ddd`.
Its verdict is `REVISE_AND_REREVIEW_CHANGED_BYTES`. The resulting author-side
P-prime is commit `818c2ed284cde8acae9a09b531b8bfed3bf925ee`, tree
`59e6eaacadac711f8b0d93980b1bfbbd3d772dc7`.

Exact candidate identities:

```text
main.tex=ef2a5387f8b54ee8b571688ce90f80d22350006e042e7124eb99eb190f97288f bytes=38521
paper PDF=9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b bytes=140343
delivery PDF=9bce71368ff0398efbc0d24685a80939fc691288663074ebf72ec9b20619013b bytes=140343
source bundle=1d76d60b1f72487a414ef2fe649415938bc12a3ea6baedd65396b9378b4d90ed bytes=20699
artifact=916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8 bytes=180308 members=9
```

The author-side verification returned:

```text
tests.goal5852_submission_evidence_test: 14/14 PASS
tests.goal5852_submission_evidence_test under python -O: 14/14 PASS
CLAIM_LEDGER.json and STATUS.json parse: PASS
claim_authorized flags: 21/21 false
git diff --check: PASS
P-prime diff from its parent under src/include/experiments/scripts/tests/artifact template: empty
paper PDF and delivery PDF cmp: PASS
PDF pages: 8
PDF page size: US Letter
fonts embedded: 12/12
fonts with Unicode mappings: 12/12
foreign-path source-bundle Tectonic build: exit 0, 8 pages, US Letter
artifact isolated replay: four runs, normal and -O, all exit 0
artifact replay outputs: four-way byte-identical
artifact replay output=c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8
PDF extracted-text private-identity scan: PASS
source-bundle main.tex/references.bib identity against P-prime: PASS
```

Three operator-command failures were retained rather than hidden. A first PDF
inspection command returned exit 127 only because `pdffonts` was not on PATH;
the bundled Poppler binary then reported all 12 fonts embedded with Unicode
mappings. A first source compile returned exit 1 because the temporary output
directory had not been created; creating that directory made the same source
bundle compile successfully. A first artifact replay returned exit 1 because
shell redirection created `normal-a.json` inside the sealed artifact before the
verifier started; the verifier correctly rejected the unexpected member. Four
fresh corrected runs wrote output outside the artifact and all passed with the
identical hash above.

Hostile review of the uncommitted P-prime review request found one transcription
error before publication: its Ada relation A/C post-import maximum was
`1.866331`, while the frozen summary, verifier, R2 report, old-P lead review,
and paper rounding all resolve from `1.865823`. The request was corrected to
`1.865823`; no candidate paper, artifact, measured value, or claim changed.

No GPU experiment, numerical table, frozen tool, native/production source, or
artifact byte changed. These checks are author-side only. P-prime remains at
zero of two independent acceptances; R7 and R8 remain open, no upload or
submission receipt exists, and every public/manuscript claim authorization
remains false.

## P-double-prime novelty remediation precommit validation

Timestamp: 2026-09-06T23:28:33-0400.

The novelty directive was executed without changing production, native,
compiler, experiment, workload, test, F2 template, timer, estimator, or
threshold code. Primary-source and current-source audits produced the N1--N3
records; N4 changed only manuscript, bibliography, claim/control documentation,
and generated delivery bytes.

Failures and adverse intermediate states were retained:

1. An initial read-only staging command containing `rm -rf` was rejected by the
   execution policy before it ran. No repository or evidence file changed.
2. An initial PDF-text command used `pdftotext` without its bundled absolute
   path and returned exit 127. The bundled Poppler executable then succeeded.
3. The first N2 test command omitted `PYTHONPATH=src:.`; two imports failed and
   no tests ran. With the prescribed environment, the two complete modules ran
   20 tests: 19 passed and one existing custody check errored because
   `history/internal_docs/goal5797_s0_five_mechanism_ablation_preaction_20260823.json`
   is absent. Six explicitly selected N2 mechanism/integrated checks then passed
   in 0.045 seconds. The missing historical fixture was not repaired or hidden.
4. One exploratory `jq` expression changed its input from the root object to an
   array before reading `.claims`; it printed an intermediate zero and then
   failed. The corrected query reported 24 total claims and zero authorization
   values other than `false`.
5. The first N4 PDF build succeeded but was nine pages and contained five small
   horizontal and one vertical overfull box. It was rejected as a candidate.
   Content-level deduplication, without changing the ACM template, margins, or
   font sizes and without deleting adverse evidence, produced the accepted
   eight-page layout.
6. One attempted hash correction patch used an inexact expected line and was
   rejected without changing the file. The exact line was then corrected and
   both JSON control files parsed successfully.

Final precommit results:

```text
Tectonic cached build: PASS, exit 0
PDF: 8 pages, US Letter, 143803 bytes
PDF SHA-256: a8d3194b07fbf0105b59944e8044da1769b9ca8877f92d3a93aa44f605b6aa84
paper PDF / delivery PDF cmp: PASS
horizontal overfull boxes: 0
vertical overfull boxes: 0
unresolved citations/references: 0
all exact pages rendered and visually inspected: 8/8 PASS
fonts embedded with Unicode mappings: 12/12 PASS
private-identity scan over PDF text/metadata/source/bibliography: PASS
normalized source twin-build cmp: PASS
source bundle SHA-256: 5f2bbc858b0b783983d773e09d46be92b0b47ebc6f87e079c1dd855ac42f55df
source bundle bytes: 20540
source bundle regular files: 2
foreign-path source compile: PASS, exit 0, 8 pages, US Letter
tests.goal5852_submission_evidence_test: 14/14 PASS
tests.goal5852_submission_evidence_test under python -O: 14/14 PASS
working diff from starting HEAD under executable/frozen paths: empty
F2 artifact SHA-256: 916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8
F2 artifact bytes/members: 180308 / 9
GPU execution: not performed
claim_authorized values other than false: 0 of 24
```

The source-bundle rebuild is a buildability check, not the exact submission PDF.
The unchanged F2 archive is still only an offline evidence recount and does not
reproduce the novelty literature audit, the illustrative semantic witness, or a
GPU run. P-double-prime commit/tree identity and its final review request remain
pending at this checkpoint. It has zero of two independent final-byte
acceptances; R8, authenticated-form review, upload, downloaded-byte verification,
and receipt remain open.

### P-double-prime commit-object binding

P-double-prime was then committed without changing the validated paper/source
bytes:

```text
commit=b28076ad568d3b7b36cfa48b0c5846accff3cb95
tree=2a63fecbcf09727dbe4e38f83edb253d80fa3cab
parent=50ca45521013f56b141402f4902a3af189b469f9
subject=Strengthen CGO novelty argument
```

`git show <commit>:<path> | shasum -a 256` independently recovered the
committed manuscript, bibliography, PDF, source bundle, and F2 identities shown
above. The committed diff from its parent remains empty under all frozen
executable paths. The P-double-prime R7 request was then created as a control
record at SHA-256
`2c56e0bc183a927bf6e3e24dfa69d5da02b04134af95dc110d051dc6da67a01e`.
This binding creates no acceptance: P-double-prime remains 0/2, claims remain
unauthorized, and no upload or submission occurred.

## P-triple-prime seven-finding remediation and preflight

Date: 2026-09-07 America/New_York.

The author-side pass applied the lead P-double-prime review and directive to
the manuscript, bibliography, N1/N2/N3, change map, and claim ledger. It did
not modify production/compiler/native code, experiments, scripts, tests,
workloads, timers, thresholds, or F2, and it performed no GPU run.

Failures and adverse intermediate states were retained:

1. The first P-triple-prime PDF build produced eight pages but had horizontal
   overfull boxes of 2.28424 pt and 38.34424 pt. Subsequent content-level edits
   reduced but did not immediately eliminate the larger box; a later draft
   still had 7.16423 pt. None was accepted as final.
2. The first bibliography pass warned that the PCC entry lacked page numbers.
   Pages 229--243 were added and the final BibTeX pass had zero warnings.
3. `pdftotext` was unavailable on the default path. A first fallback PDF-text
   command also had a local string/output scripting error. The corrected pypdf
   extraction produced text for all eight pages and enabled the required scans.
4. A naive top-level PDF font scan initially reported 6/12 embedded fonts. The
   check was wrong for Type0 descendant fonts; recursive descriptor inspection
   found 12/12 embedded with 12/12 ToUnicode mappings.
5. One hash command used the nonexistent path
   `paper/cgo2027/artifact_post_goal5851.tar.gz`. The actual frozen artifact at
   `output/artifact/rtdl-cgo2027-artifact.tar.gz` then matched its expected hash
   and nine-member inventory.
6. A quick `jq` projection queried nonexistent top-level `review_state` and
   `updated_at` fields and printed nulls. Parsing had succeeded; the corrected
   query used `.review` and `.updated_at_utc`, confirmed 24 claims, and found
   zero authorized claims.
7. A combined delete/add `apply_patch` for the remediation report was rejected
   before mutation because both operations targeted one file. Separate
   apply-patch delete and add operations succeeded.
8. A proposed relative-link correction targeted `paper/cgo2027/README.md`, but
   the expected link list was actually in the repository-root README. The
   context check rejected the patch before mutation; the root-relative links
   were already valid and no correction was needed.

Final precommit and candidate-object results:

```text
Tectonic cached build: PASS, exit 0
PDF: 8 pages, 612 x 792 pt US Letter, 146231 bytes
PDF SHA-256: 2840d348459d2cdeba02cda3a4b17547ce83bc208876736f805a2f5682c3d303
paper PDF / delivery PDF cmp: PASS
horizontal overfull boxes: 0
vertical overfull boxes: 0
unresolved citations/references: 0
BibTeX warnings: 0
all exact pages rendered and visually inspected: 8/8 PASS
fonts embedded / ToUnicode: 12/12 / 12/12 PASS
private-identity scan over PDF text/metadata/source/bibliography: PASS
normalized source twin-build cmp: PASS
source bundle SHA-256: 26e80da4004761203a0e6542dcb9a186690768facaf12eee7400ecc519f2b16a
source bundle bytes: 21624
source bundle regular files: 2
foreign-path source compile: PASS, exit 0, 8 pages, US Letter
tests.goal5852_submission_evidence_test: 14/14 PASS
tests.goal5852_submission_evidence_test under python -O: 14/14 PASS
candidate-parent executable/frozen path diff: empty
F2 artifact SHA-256: 916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8
F2 artifact bytes/members: 180308 / 9
GPU execution: not performed
claim_authorized values other than false: 0 of 24
```

P-triple-prime was committed without changing the validated paper/source
bytes:

```text
commit=c26c88a69382d9786c2f5f77c6cdc6763fc51e7c
tree=b45bae5d83ec9c803657b28132c677d514897bb3
parent=5334f0fc5deda053f54dbad12d09f4c43016875c
subject=Remediate P-triple-prime review findings
```

Commit-object extraction recovers the recorded manuscript, bibliography, PDF,
and source identities. The candidate-parent diff is empty under `src/`,
`include/`, `experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`. The unchanged F2 hash and member count
also match.

The candidate remains 0/2 independent acceptances. The local preflight and
author remediation do not authorize a claim, upload, or submission.

## P-quadruple-prime result-route contribution pass and preflight

Date: 2026-09-07 America/New_York.

The contribution directive was executed as a manuscript, literature-boundary,
and existing-evidence pass. It changed no production/compiler/native source,
experiment, script, test, workload, timer, estimator, threshold, or F2 byte,
and it performed no GPU or remote-pod run.

The new paper centers one bounded result-route relation: observable output
obligations constrain admissible callback effects, trusted traversal
interpretation, and fail-closed publication. W1 and W2 are source traces; W3
is an existing source-to-wrapper component test. They are not new GPU
experiments or a general semantic proof.

The existing witness checks were replayed with the committed Python 3.12
environment, `PYTHONPATH=src:.`, and `PYTHONDONTWRITEBYTECODE=1`:

```text
tests.goal5759_v4_triangle_reduction_target_test.Goal5759TriangleReductionTargetTests.test_count_intrinsic_requires_the_exact_standard_callback_ir
tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_schema_and_wrapper_are_deterministic_app_neutral_true_optix
tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_capacity_overflow_rejects_partial_result
tests.goal5760_v4_bounded_relation_test.Goal5760BoundedRelationTests.test_duplicate_policy_is_explicit_and_canonical
```

Result: 4/4 PASS, exit 0, `Ran 4 tests in 0.017s`, `OK`. The selected
source/test identities were:

```text
src/rtdsl/v4_bounded_relation.py
  4ac50a83ffb80400c6b950150a5702633b3cafa0e43b0b54527f7db44949467a
src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py
  f7d1f07b4462a6713a4bcda7aaf64f3a480575f1034059f3fbe61d640044eecb
tests/goal5759_v4_triangle_reduction_target_test.py
  3d44b0285afba026333e81abd4f262232db075b5b8150871c9fc14bab767101f
tests/goal5760_v4_bounded_relation_test.py
  faa1550b98990c771c20b516b808258edc96b5d0de49c9caca6bf5a9dd4b99fd
```

All four files and `src/rtdsl/v4_callback_ir.py` have zero diff from measured
implementation M. The complete unchanged submission-evidence suite passed
14/14 normally and 14/14 under `python -O`.

Author-side PDF/source validation produced:

```text
Tectonic cached build: PASS, exit 0
PDF: 9 pages, 612 x 792 pt US Letter, 153809 bytes
PDF SHA-256: bb957c0969bbd92c6a4be952c4e40a4ce5a183bf565c5f54a19b410102c77aca
paper PDF / delivery PDF cmp: PASS
horizontal overfull boxes: 0
vertical overfull boxes: 0
unresolved citations/references: 0
all exact pages rendered and visually inspected: 9/9 PASS
fonts embedded / ToUnicode: 12/12 / 12/12 PASS
PDF text/metadata private-identity scan: PASS
normalized source twin-build cmp: PASS
source bundle SHA-256: e845010a64f8373dc40ac65f8cc42e4c4024687ce6fd1eb80b8fd4067a623266
source bundle bytes: 23504
source bundle regular files: 2
foreign-path source compile: PASS, exit 0, 9 pages, US Letter
F2 artifact SHA-256: 916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8
F2 artifact bytes/members: 180308 / 9
GPU execution: not performed
claim_authorized values other than false: 0 of 24
```

Retained failed/intermediate states:

1. The first PDF draft had five overfull boxes and was rejected. Text-level
   edits removed them without changing the ACM template or deleting adverse
   evidence.
2. Initial `tar -czf` source archives differed because of gzip header time
   metadata and were rejected. Normalized ustar archives compressed with
   `gzip -n` were byte-identical.
3. One orchestration JavaScript invocation was syntactically incomplete and
   failed before any nested tool call. It modified nothing and generated no
   evidence.

The immutable candidate was committed as:

```text
commit=70a081e90c4c50ecf92d24741529de9859841c70
tree=b4b1628345536976e2ed8fbb67ab5b4ff21fc802
parent=b608f9aa5e4e04d083d8a2963d552e00287b47cd
subject=Strengthen CGO result-route contribution
main_tex_sha256=22564330dea504e9f3005ce9cf9185c62306f47dc8e07c1a3bff430dec9d9dbc
references_bib_sha256=71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6
pdf_sha256=bb957c0969bbd92c6a4be952c4e40a4ce5a183bf565c5f54a19b410102c77aca
source_bundle_sha256=e845010a64f8373dc40ac65f8cc42e4c4024687ce6fd1eb80b8fd4067a623266
```

Commit-object extraction recovered every recorded deliverable identity. The
candidate-parent diff is empty under `src/`, `include/`, `experiments/`,
`scripts/`, `tests/`, and `paper/cgo2027/artifact_post_goal5851/`.

P-quadruple-prime remains 0/2 independent acceptances. No public/manuscript
claim is authorized, and no upload or submission occurred.

## P-quintuple-prime three-question closure and preflight

Date: 2026-09-07 America/New_York.

The final lead directive was applied as a minimum manuscript and evidence-
linkage closure. It required explicit answers to: what fixed-family knowledge
the compiler has beyond local typing, what that knowledge makes it reject,
generate, or select, and what implemented increment remains after conceding
the strongest prior mechanisms.

The manuscript changed in exactly three argument areas:

1. Table 1 now uses concrete reject/generate/select actions and keeps each
   action adjacent to its result obligation and evidence boundary.
2. Section 3.2 now states that the general leaf ABI/wrapper and exact standard-
   count specialization implement the same known increment-and-continue
   behavior; the exact-IR guard selects trusted code rather than proving
   equivalence.
3. Related Work now identifies the contribution as the implemented connection
   from fixed result obligations to admission, trusted lowering, and
   publication, and explicitly states the restricted-expressiveness and
   topology-specific-TCB cost without claiming superiority.

N1, N2, and N3 remained unchanged because their existing bytes already carried
the necessary prior-art concessions, witness boundaries, and route comparison.
No production/compiler/native source, experiment, script, test, workload,
timer, estimator, threshold, frozen F2 byte, or numerical result changed. No
GPU ran and no previously passed test was rerun.

Author-side PDF and source validation produced:

```text
Tectonic cached build: PASS, exit 0
PDF: 9 pages, 612 x 792 pt US Letter, 154295 bytes
PDF SHA-256: 34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385
paper PDF / delivery PDF cmp: PASS
horizontal overfull boxes: 0
vertical overfull boxes: 0
unresolved citations/references: 0
all exact pages rendered and visually inspected: 9/9 PASS
fonts embedded / subset / ToUnicode: 12/12 / 12/12 / 12/12 PASS
PDF private-identity text scan: PASS
normalized source twin-build cmp: PASS
source bundle SHA-256: f9e70fd7e709eeb611ba740628654379866e638d3534c9ddb94a3b8c0f3ea30a
source bundle bytes: 23637
source bundle regular files: 2
foreign-path source compile: PASS, exit 0, 9 pages, US Letter
F2 artifact SHA-256: 916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8
F2 artifact bytes/members: 180308 / 9
tests rerun: 0, by directive because executable/F2 inputs did not change
GPU execution: not performed
claim_authorized values other than false: 0 of 24
```

The immutable candidate was committed as:

```text
commit=41bbec66c6f9f8f770d18075fb9dacbed16d499d
tree=135f2bc214927acdb305cf2edd2c5ef98690b4a2
parent=8b4475893a7a4486fb89fa35f1ce2470fb2d13f4
subject=Close CGO three-question argument
main_tex_sha256=537efb44319297733f8c94717be2769dbea88fdee738d8e7ac7c7e185bb58430
references_bib_sha256=71c379b4ea23a8eaa08e97f94a3c9569d703ea7cb99186b81e0df0f00d5e4dd6
pdf_sha256=34dad89878f7a283662e51059d1b81c4d266198657e0d4db065f0c3df2c41385
source_bundle_sha256=f9e70fd7e709eeb611ba740628654379866e638d3534c9ddb94a3b8c0f3ea30a
```

Commit-object extraction reproduced every identity above and the unchanged F2
hash. The candidate-parent diff is empty under `src/`, `include/`,
`experiments/`, `scripts/`, `tests/`, and
`paper/cgo2027/artifact_post_goal5851/`.

One first font-check command used an obsolete cached wrapper path and an awk
variable name colliding with a built-in. It failed before producing a result,
changed no file, and was not counted as evidence. The corrected invocation
used the installed Poppler binary and produced the 12/12 result above.

P-quintuple-prime starts at 0/2 independent exact-byte acceptances. The author
closure and local preflight count as zero. No claim is authorized, no upload
was attempted, and no submission receipt exists.

## P-sextuple-prime DSL-first candidate and local preflight (2026-09-07)

The two owner directives for a DSL-first paper and a bounded repurposed-RT
problem statement were applied without changing compiler/runtime/native code,
apps, experiments, tests, workloads, thresholds, evidence, or F2. The immutable
candidate is commit `7959b325e4f42efc42b773fd363d3c5e9dedb1e1`, tree
`b6f738e135050cafb8923c84ef33aa2665e2b749`, parent
`8dfdc810c9c23f259b20c511caf69d250f2b86ce`.

The exact `main.tex` SHA-256 is
`a339ace8ec2f071cd85c2416e9f67b5d76ae533d43a41a96dbfa2f6647be7de0`;
the bibliography SHA-256 is
`bb0b71ae0fec49492888fbc9252ed412897cb2d4d7f1e33008f902cdb3b74e61`.
The paper and delivery PDFs are byte-identical, 182,617 bytes, and SHA-256
`a1772fc41809deb91f64466fc0cccb9557023c143d99d361b4f3b9aa38ad36f0`.
The normalized two-file source bundle is 29,176 bytes at SHA-256
`a49ea4aedc2b96084eefddf2ee987e20e968b59416c678caa30c5ab0c4606afa`.
F2 remains byte-identical at SHA-256
`916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`.

Author-side validation passed a cached Tectonic build, 12-page US-Letter page
and layout checks, zero horizontal or vertical overfull boxes, zero unresolved
citations/references, 12/12 embedded/subset/Unicode fonts, all-page visual
inspection, tested private-identity scanning, twin normalized source builds,
and a foreign-path source compile. BibTeX retained disclosed nonfatal
completeness warnings. No unchanged test was rerun and no GPU ran by directive.

The claim ledger contains 28 unique claims, zero authorized. The exact R7
request is `R7_PSEXTUPLEPRIME_FINAL_BYTES_REVIEW_REQUEST.md`, SHA-256
`c0d5fe4f37525e8a98f70eef28d04bd77f89e45e7c26a14b6ca43f5882d5adbc`.
The author-local R8 preflight is
`R8_PSEXTUPLEPRIME_LOCAL_PREFLIGHT_REPORT.md`, SHA-256
`e65a4533418adc2ba15bedddd160139bf20a3c98fca19cc7f1008f730dfbb701`.
R7 remains 0/2; no earlier review transfers. No claim is authorized, no upload
was attempted, and no submission receipt exists.

## P-septuple-prime application-cost integration and frozen replay (2026-09-08)

The final frozen selected-stage application transaction was integrated into
the manuscript without modifying source, native code, experiments, tests,
workloads, timers, estimators, thresholds, raw evidence, or F2. The immutable
paper candidate is commit
`72d60cb392031134dd3064a8da5cb603bde18e47`, tree
`759cc1246830b785a8d30e98704b51266033194a`, parent
`700b3165ba2a0bca15981aa273c9f02ed9a63992`.

Exact candidate identities are:

```text
main.tex bytes/SHA-256: 61234 / 0dd724df5b1d64051e28ce7ee31f09f4e3e5adccf389a0775fa9be7ef36c6076
references.bib bytes/SHA-256: 21640 / d27ce8c5db0a6855e9879b90a38e98fb07f56ecf993ee4fe2eaddea5b57619f5
paper and delivery PDF bytes/SHA-256: 183938 / 32189aec5d5ebda4956c83dfe948128bef8dd50e3dbbeb308290988a2acaea07
source bundle bytes/SHA-256: 29743 / e4a291f9e86b125438f2b1c9a5334110a035a36b4a88955267ea319a4e596f6f
unchanged F2 bytes/SHA-256: 180308 / 916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8
```

Author-side validation passed the cached Tectonic build, 12-page US-Letter
format, main-text boundary on page 11, byte-identical paper/delivery PDFs,
zero horizontal and vertical overfull boxes, zero unresolved citations or
references, 12/12 embedded/subset/Unicode fonts, all-page visual inspection,
tested private-identity scanning, twin normalized source construction, and a
foreign-path source compile. Three nonstandard bibliography commentary notes
were removed; no cited author, title, venue, year, DOI, or URL was removed.
Disclosed nonfatal bibliography completeness warnings remain.

The final application source is pre-freeze commit
`c5c8be48b743aa001e9c16c3344cc97c200600d1`, tree
`e3bb0001f4c2d1e3171ab0431c0479500dfc7136`. On one RTX A4500 it retained 192
workers, 96 paired blocks, 12 evaluations, and zero retry/discard. Exact output
contracts passed, but all 96 individual block ratios and all 12 endpoint
medians were adverse to V4. The median range was `1.080--75.533x`. This is
selected-stage evidence from three of nine mappings and four operation units,
not raw-domain application end to end, broad performance, productivity,
causal-overhead allocation, or proof of unavoidable language cost. Endpoint
and physical-route asymmetries are disclosed in the exact paper and R7 request.

The application authority identities are:

```text
FORMAL_SUMMARY.json: 67a353cd796080b06442dcef64624bd176f65c513d185e0198aca0b7640df4bf
INDEPENDENT_RECOUNT_c5c8be48b.json: 667cafd0f3599b62b77aab96f92e18eaac4cb925832c077004b1ced2b09d7b64
complete archive: 2d7dc4413639e46994ca74251d230b74d5e9d775a23b457336cb00f9df80f4ff
```

A fresh pod clone on the same retained A4500 host independently matched the
candidate commit/tree and all delivery hashes. Normal and optimized Python F2
replay outputs were byte-identical at SHA-256
`c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8`
and returned `PASS__OFFLINE_PROJECTION_RECOUNT` with 20,480 formal steady
samples, 160 formal workers, 1,024 instrumentation workers, 20 AOT
observations, and eight competence workers. No GPU experiment ran.

Normal and optimized application recount outputs were byte-identical at
SHA-256
`63388474457a4e234f6915186aa364176ef80dd418936cf4c3e2c09cdc614fc8`.
After removal of only environment-dependent absolute summary and worker paths,
the new recount equaled the retained recount exactly. An initial diagnostic
correctly failed after removing only the summary path because worker paths also
differed, and a later print expression used the wrong ratio nesting after its
equality assertions had passed. Neither invocation changed code or evidence;
only the corrected fail-closed result is counted above.

The P-septuple-prime claim ledger has 29 unique claims and zero authorized
claims. R7 starts at 0/2 independent exact-byte acceptances; no earlier review,
author-side analysis, local preflight, or pod replay transfers as an
acceptance. No authenticated submission-form check, upload, downloaded-byte
verification, or submission receipt exists.

## P-decuple-prime final narrative, figures, source package, and replay (2026-09-08)

The final DSL-first narrative, complete authored example, result-obligation
figures, implementation-route figure, prior-protocol comparison, related-work
boundary, and successor performance figure were integrated without changing
production, compiler, native, experiment, workload, timer, estimator,
threshold, or test code. The manuscript/evidence commit is
`ed4df9330a3c47c116912cb5a817fd7a84dccdfe`, tree
`d4bede2eea645716fe6749de479b69c9413da2bc`. Its exact identities are:

```text
main.tex bytes/SHA-256: 57947 / 81299d0bddd605bdb42694d7204b5898fca3cf4436ff2aeec519038fa97fed52
references.bib bytes/SHA-256: 22538 / 0bd5a31016fc847ef2ac52b45185533e16f0a23e439b83919d1794b9143da948
paper and delivery PDF bytes/SHA-256: 254212 / 3f4ec710fa54248dcd8dde0116920d94e75a00ce0424d7b8cf60b8f3e67202e3
design-figure bytes/SHA-256: 62908 / 920bc8c2dd7d083df3a13cb8c289e419162966de1fb4d8528d0cfe8d071a5092
performance-figure bytes/SHA-256: 27603 / 3ce0081120db0202a8e2a5a8b623acd27394559e9f42fe2039c96abb2b4454cf
```

The deterministic performance-figure builder is 7,671 bytes at SHA-256
`e34599f8dd3fb1688e8628fa55883ae9246754542014aa71f876c9ee5bec8b55`.
It binds anonymous projection SHA-256
`ae2cb7011f407c37b3850aa2a854d177baa4a6494d704eb2ddf68e89f574578c`
and asserts all ten exact evaluation rows. Two independent builds were
byte-identical to the committed figure.

Two independent processes built an eight-member normalized USTAR/gzip source
bundle directly from the exact manuscript/evidence Git blobs. The twin bundles
were byte-identical. The official bundle was committed separately as
`c0c23e20ee325fb246c769ba1920566474d869c6`, tree
`c25914560f096175630f89453e33bcd42019992e`, and is 106,838 bytes at SHA-256
`8015a14bdb6af036d45f1500152637a0a5c5f29f56018dc01324992dea240108`.
It contains four directory records plus exact `main.tex`, `references.bib`,
and both figure PDFs. A fresh read-only extraction under a path containing
spaces preserved all hashes and compiled to 13 US-Letter pages.

The immutable candidate checkpoint is
`8a485a6aae353e0d1dbfee7ce5a96610cee5d31d`, tree
`b59d795819f489d4e53f34f264eb46d31f1ec45f`. It differs from the source-
package assembly only in `paper/cgo2027/README.md`, so submission bytes are
unchanged. A canonical local build and exact PDF inspection produced:

```text
pages: 13, US Letter
main text: pages 1--11
references: pages 12--13
horizontal overfull boxes: 0
vertical overfull boxes: one final-output 1.87198pt event
unresolved citations/references: 0
BibTeX completeness warnings: 17 nonfatal inherited warnings
embedded/subset/ToUnicode fonts: 18/18 / 18/18 / 18/18
visual inspection: 13/13 pages PASS
tested private-identity scan: PASS
local focused tests: 14/14 plus 39/39 PASS
```

The small final vertical event occurs during ACM bibliography output. Visual
inspection found no clipping or overlap. It is disclosed rather than called a
zero-warning build. The PDF uses the official limit of 11 text pages plus two
reference pages.

A fresh Pod clone completed to 100% and verified the exact candidate commit,
tree, clean status, delivery hashes, source member metadata, and source payload
hashes on host `4735c6e75b0c`, NVIDIA RTX A4500, driver 550.127.05, Python
3.12.3. An earlier interrupted worktree remained `initializing`; it was
rejected and never used as evidence.

The clean Pod replay produced byte-identical normal/optimized outputs:

```text
F2: c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8
status: PASS__OFFLINE_PROJECTION_RECOUNT
application projection: c22a23a782779683385a546634e0d9f3a7dc2cca575dc0c54197c75e0496b4f9
status: PASS__APPLICATION_PROJECTION_RECOUNT
CPU sensitivity: 005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0
status: PASS__POST_FORMAL_DESCRIPTIVE_CPU_SENSITIVITY_RECOUNT
```

The CPU recount retained Particle CPU-8 `1.399873664x`, rank 47/48, and
LibRTS-range CPU-8 `0.804614022x`, rank 6/48. No adverse row was removed or
pooled. No GPU experiment ran.

Pod system Python lacked Numba. Its first extra long-workload test attempt
failed during import and was not counted. A checkout-external temporary venv
with Numba 0.61.2, NumPy 2.2.6, and llvmlite 0.44.0 then passed both focused
suites under normal and optimized Python, 106/106 test invocations. This does
not establish zero-install package completeness.

GNU tar 1.35 as container root restored the application artifact's `0555`
root directory before creating children and failed direct extraction. Python
3.12 `tarfile --filter data` extracted the exact same bytes and both verifier
modes passed. The failed extraction attempts ended before verifier execution;
this portability limitation is retained. Tectonic was absent on the Pod, so
no Pod-side source compile is claimed.

The P-decuple-prime claim ledger still has 31 claims and zero authorized
claims. R7 starts at 0/2 exact-final-byte acceptances. No earlier review
transfers. Authenticated submission-form checks, upload authorization,
downloaded-byte verification, submission ID, and receipt remain absent.

## P-decuple-prime Linux source-package build replay (2026-09-08)

The replacement SSH endpoint resolved to the same retained Pod hostname
`4735c6e75b0c`, NVIDIA RTX A4500, driver 550.127.05. It is therefore not a
second-machine or cross-host replication. The existing exact-candidate checkout
remained at commit `8a485a6aae353e0d1dbfee7ce5a96610cee5d31d`, tree
`b59d795819f489d4e53f34f264eb46d31f1ec45f`, with empty porcelain status
before and after this replay.

Tectonic was not preinstalled. The official GitHub release API identified
Tectonic 0.17.0's Linux x86-64 GNU archive as 22,749,118 bytes with SHA-256
`1a715688baf591e650c8aeb160ae934e181685eecbb38b317de30b269ac5d606`.
The downloaded archive matched that digest. Default GNU-tar extraction first
failed because the RunPod network volume rejected restoration of UID/GID 1001;
the failed destination was not reused. Extraction into a new directory with
`--no-same-owner` passed, and the installed binary reported Tectonic 0.17.0.

The exact 106,838-byte source package at SHA-256
`8015a14bdb6af036d45f1500152637a0a5c5f29f56018dc01324992dea240108`
was extracted with Python 3.12 `tarfile --filter data` into two distinct fresh
roots. The first build populated the Tectonic resource cache and passed. The
second build used `--only-cached`, printed `using only cached resource files`,
and also passed. Results were:

```text
first Linux PDF: 253043 bytes
first Linux PDF SHA-256: 7204a3dfeda6946a279a9c0dbc3662f9b00233c85e72d1dc8faf5e45bd97085e
cached Linux PDF: 253043 bytes
cached Linux PDF SHA-256: 5027d8eec85b10f632698eddb5e34fa71a2650d9709abe5add3a473773a991e1
pages: 13, all 612 x 792 pt US Letter
main text ends: page 11
references begin: page 12
horizontal overfull boxes: 0
vertical overfull boxes: one 1.87198pt final bibliography event
undefined citations/references: 0
BibTeX completeness warnings: 17
```

The committed candidate PDF and both Linux PDFs had identical extracted text
on all 13 pages. Their joined page-text SHA-256 was
`14d41d1173e172e6eef9f28a3dd5e1f78df9693fbb7e6099421e0ab7aa6a1a4c`.
The two Linux builds also produced byte-identical `.aux`, `.bbl`, and `.out`
files. The three PDFs are not byte-identical: each metadata dictionary records
a different `/CreationDate`. Only exact-source buildability, page geometry,
page boundary, converged intermediates, and extracted page-text equivalence are
claimed; cross-build PDF byte identity is explicitly not claimed.

This was author-side preflight on the same Pod. It ran no CUDA/OptiX workload,
created no new GPU result, changed no candidate or evidence byte, and counts as
zero independent R7 acceptances. The claim ledger remains 31/31 unauthorized;
upload and submission remain unperformed.

## P-decuple-prime-r1 dead-link repair and exact replay (2026-09-08)

An author-side live-link scan found that P-decuple-prime's NVIDIA OptiX 9
programming-guide URL returned HTTP 404. The bibliography now cites the
official NVIDIA `optix-sdk` v9.0.0 tagged guide. The scan exercised all 30
explicit bibliography URLs/DOIs; publisher bot blocks were not classified as
dead links. This repair changes no manuscript prose, research claim,
implementation, experiment, workload, timer, threshold, estimator, or test.

The repaired bibliography and two byte-identical PDFs were committed as
`f377500fd85d4477529433fde282be59d60d7a81`, tree
`f9471e81ce097d87ba27f5782cee4505ddbb81be`. Two independent normalized
source-bundle builds from that commit's exact Git blobs were byte-identical.
The bundle was committed as `a9e6a76802e7f91b95935201d93ccddf19c844f6`,
tree `299de87bba09cf3ab7c480dbc37a1dbf9077d3fd`. Candidate metadata alone
then established P-decuple-prime-r1 at commit
`7c7dfce8e2aad8621d86246b58bb142ab9ed2329`, tree
`25d8d07d26ccba02d65711eb671d9324e433cb41`.

Exact changed deliverable identities are:

```text
references.bib: 22550 bytes / 55b138e56d1bd748885ab0765002a1fa7c28d9d09b000f93efae67955fa4f3b6
both PDFs: 254266 bytes / a810e3d8c465c6764da06a2ccdefd13fa5444c1c480ecd9441b54adadde26631
source bundle: 106843 bytes / fc2f42b342843260d02d68884dcae3d1dcaa582a070c4eefde3d412a34876f78
```

Local Tectonic 0.16.9 produced 13 US-Letter pages, with main text ending on
page 11 and references beginning on page 12. There were zero horizontal
overfull boxes, one visually harmless final-output `1.90399pt` vertical event,
zero unresolved references/citations, 17 inherited BibTeX completeness
warnings, and 18/18 recursively discovered fonts embedded, subset, and Unicode
mapped. All 13 rendered pages were inspected. Pages 1--11 are text-identical
to P-decuple-prime; only the URL and consequent reference-line flow differ on
pages 12--13. Local ordinary/optimized frozen tests passed 106/106.

The supplied SSH endpoint resolved to the same retained host `4735c6e75b0c`,
NVIDIA RTX A4500, driver 550.127.05; it is not an independent host. A new clean
worktree from the verified Pod object store matched the candidate commit/tree
and remained porcelain-clean before and after replay. A redundant full-clone
attempt exceeded the SSH window and was abandoned without use as evidence.

The exact source bundle compiled with hash-verified official Tectonic 0.17.0
both normally and from a separate fresh extraction under `--only-cached`:

```text
first Linux PDF: 253086 bytes / 499021af5d2324e33b7355f589cc33d1e857d056e48e0b435ac6387200ba40d4
cached Linux PDF: 253086 bytes / 9708e51b9417735901c896f520abe9d5228a0b8aa47ab3ccb7fc004749b977e3
```

The committed PDF and both Linux PDFs had 13/13 equal page texts under pypdf
6.0.0; joined page-text SHA-256 was
`063d022570868872acacb4f3bdc3e2d97a18ebcef39bad7b4794a0c58d6415fe`.
The Linux `.aux`, `.bbl`, and `.out` pairs were byte-identical. The PDF byte
hashes differ because creation timestamps differ, so cross-build PDF byte
identity is not claimed.

Pod ordinary/optimized frozen tests passed 106/106. Retained-data replays were
also byte-identical across normal and optimized Python:

```text
F2: c47aaee24bea18be6b30eaae45a856e30c7a2a74bd5b50fe7daf0f741bdf0ee8
application projection: c22a23a782779683385a546634e0d9f3a7dc2cca575dc0c54197c75e0496b4f9
CPU sensitivity: 005caca0475516bafa6834594144a95c445eee771b171d1af0dbb448f80364d0
```

The CPU recount retained the adverse CPU-8 values. No CUDA/OptiX workload or
new GPU measurement ran, and the post-replay GPU compute-process list was
empty. P-decuple-prime-r1 starts at 0/2 independent exact-final-byte
acceptances. The 31-entry claim ledger remains 0 authorized. Authenticated
submission-form checks, upload authorization, upload, downloaded-byte
verification, submission ID, and receipt remain absent.
