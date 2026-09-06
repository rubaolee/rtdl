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
