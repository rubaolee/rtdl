# R5 final F2 clean-checkout rehearsal report

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE__F2_SUPERSEDES_F1`

This report supersedes `R5_FINAL_F_REHEARSAL_REPORT.md` for the final tooling
identity. The earlier F1 report remains unchanged as history. F1 was replaced
because the public dependency note did not explicitly inventory the packaged
project-authored components and their distribution boundary, and its report
did not include the complete 128/128 normal, 128/128 optimized, and 7/7
regression matrix required by the remediation plan.

This is an offline evidence-tool rehearsal. It is not a GPU experiment, a
change to measured implementation M, an external review, or public-claim
authorization.

## 1. Frozen identities and remote recovery

| Role | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Final tooling snapshot F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |

F2 was pushed to `origin/codex/cgo-goal5836-handoff`. A remote
`git ls-remote` returned the exact F2 commit. A new empty repository at
`/tmp/rtdl-cgo2027-F2-9771face-clean` fetched that remote ref with depth one
and detached at `FETCH_HEAD`. The checkout reported the exact F2 commit and
tree and was clean before and after all tests, exports, and replays.

Relative to M, `src/`, `include/`, and `experiments/` have no changed path.
The complete executable-tool whitelist introduced between M and F2 is:

- `paper/cgo2027/artifact_post_goal5851/verify.py`
- `scripts/goal5852_build_submission_evidence.py`
- `tests/goal5852_submission_evidence_test.py`

No workload, native implementation, timer, estimator, threshold, measured
sample, or original evidence file changed.

## 2. Tool and input bindings

| Tool | SHA-256 |
| --- | --- |
| Packaged verifier template | `5a41e246412870118f1c11cb11a1622e86d8999d664dcf578eee638f63ec0100` |
| Exporter | `ba3075214564cad6b51dfea93cb8741c100d19f149ecd5b5d1a70eee89ffabd1` |
| Tool tests | `a75d897032d44becdc4838ec49c1ffe31119943adf0f8d4735fbc9277047dcd9` |

The frozen raw inputs were unchanged:

| Input | SHA-256 |
| --- | --- |
| Ada evidence manifest | `e71f98c713ee9c7c0bb5733d5ff1921d11eea5bc819ec3fea217961f9a690f6f` |
| Ada complete archive | `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced` |
| Ada single-generation authority | `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7` |
| Ampere evidence manifest | `9f1031c4fc07bf23635904f7f93e075a0a3c1a0ed5aaa21f6dc48e47d92b9340` |
| Ampere complete archive | `7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2` |
| Ampere single-generation authority | `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3` |
| Cross-generation authority and recount | `99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692` |

## 3. Clean-F2 regression matrix

The following commands ran from the fresh F2 checkout with bytecode disabled:

```text
python -m unittest tests.goal5852_submission_evidence_test
exit=0; 14/14 PASS

python -O -m unittest tests.goal5852_submission_evidence_test
exit=0; 14/14 PASS

python -m unittest discover -s tests -p 'goal5848*_test.py'
exit=0; 128/128 PASS

python -O -m unittest discover -s tests -p 'goal5848*_test.py'
exit=0; 128/128 PASS

python -m unittest tests.goal5851_triangle_fused_replay_test
exit=0; 7/7 PASS

python -m ruff check scripts/goal5852_build_submission_evidence.py \
  paper/cgo2027/artifact_post_goal5851/verify.py \
  tests/goal5852_submission_evidence_test.py
exit=0
```

There were no skips. Before F2 was committed, the new component-inventory test
failed three development invocations: first because a synthetic projection was
passed to the frozen projection-identity gate, second because it was passed to
the frozen numerical oracle, and third because an assertion crossed a Markdown
line break. The test was narrowed to its actual responsibility: inspecting the
generated static component inventory with a minimal empty performance-row
input. No production verifier or numerical gate was weakened.

## 4. Deterministic external-root builds

Two actual exporter invocations from F2 used the same three raw roots and two
new repository-external output roots:

```text
/tmp/rtdl-cgo2027-F2-9771face-build-a-20260906-173128
/tmp/rtdl-cgo2027-F2-9771face-build-b-20260906-173128
```

Both returned exit 0 and
`PASS__RAW_TO_ANONYMOUS_PROJECTION_AND_PACKAGE`. Each invocation also required
two byte-identical in-process archive builds. `diff -qr` over the complete A
and B output roots returned exit 0 with no output. Reusing root A through the
actual exporter CLI returned exit 1 and
`output root already exists; overwrite refused`.

The package contains the explicit `DEPENDENCIES.md` component and distribution
inventory required as the R6 equivalent of a license/component checklist. It
states that only project-authored source, derived data, and documentation are
packaged; Python is an external prerequisite; and CUDA, OptiX, proprietary
headers, drivers, measured binaries, and signing keys are not distributed.

## 5. Frozen derived identities

| Output | Self-seal | File SHA-256 |
| --- | --- | --- |
| Performance projection | `fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca` | `94144ab768d669ebcdf83a12d018decd66a306f940fa4bf1cf18a1fcc91ae77f` |
| Recount summary | `54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105` | `2a98ea207004153b4e04c52a36ce3ae5940cc7a7ddbc5723caa3fb5f6d498ddd` |
| Public manifest | `4a62601b0e421033e67169ed3f89818c6cf62b8acc7723df9cc3ca4c8a46fc32` | `da73f16918c572dbffc5d803627837ae412197afc3ea9eee341b4989d9b494d8` |
| Private provenance | `12b47d35ddde66259343bb59b76fca3d93048af9e2908381352ccf01ddc3fc85` | `97ac92b95af2d0f21c2445b1ef533c9a686181bff236561f2db4a45f328a037f` |
| Export receipt | `9294627a889356590b7a2ea53e126fb40711a7aefb739788e8ec0294dc67a522` | `6e03835f3b53a1a49dfab6b4f095a6c5cc2f984c07d0508c5cc7492ec98f099c` |

The deterministic nine-member archive is 180,308 bytes with SHA-256
`916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8`.
The performance projection and recount identities are byte-identical to F1;
only the component inventory and consequently bound package metadata changed.

## 6. Foreign replay, identity scan, and retained operator error

The first extraction command incorrectly pre-created the archive's own
`rtdl-cgo2027-artifact` top-level directory. This produced a duplicated nested
directory and `/usr/bin/python3` returned exit 2 because `verify.py` was not at
the mistaken working directory. No package member or tool was changed, and the
failed directory was not reused.

The archive was then extracted into a second new parent containing spaces:

```text
/tmp/RTDL CGO final F2 replay 9771face retry/rtdl-cgo2027-artifact
```

From that extracted package, with project `PYTHONPATH` removed and user site
disabled, both commands passed:

```text
/usr/bin/python3 -I verify.py --artifact-root .
exit=0; PASS__OFFLINE_PROJECTION_RECOUNT

/usr/bin/python3 -I -O verify.py --artifact-root .
exit=0; PASS__OFFLINE_PROJECTION_RECOUNT
```

Both reconstructed 160 formal cells, 20,480 formal steady samples, 1,024
instrumentation endpoints, 20 AOT qualifications, and eight nonformal
competence workers. Both returned `gpu_execution_performed=false`,
`project_import_performed=false`, and
`public_or_manuscript_claim_authorized=false`.

`cmp` proved the packaged verifier byte-identical to F2. A content scan found
no internal Goal identifier, username, author/workspace path, GPU UUID, SSH
endpoint, internal-history path, GitHub identity, or author name. Archive
members are regular mode-0444 files with uid/gid zero, empty owner/group names,
and mtime zero.

## 7. Verdict and remaining boundary

F2 is the final executable/tooling snapshot. R5 is closed at F2 with actual
remote recovery, complete regression, deterministic twin export, overwrite
rejection, foreign-path normal and optimized replay, verifier binding,
component inventory, and anonymity evidence.

This does not authorize a manuscript claim. R4 manuscript rewrite, R6 final
PDF/package pairing, R7 final-byte reviews, and R8 format/submission checks
remain open. Any later executable change would create another F candidate and
require the full transaction again; after the 2026-09-08 00:00 ET hard freeze,
such a change is forbidden and must instead narrow or remove the affected
claim.
