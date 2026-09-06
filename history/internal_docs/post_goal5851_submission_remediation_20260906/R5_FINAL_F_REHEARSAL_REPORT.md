# R5 final candidate-F clean-checkout rehearsal report

Date: 2026-09-06

Status: `CLOSED_WITH_EVIDENCE`

This report records the indivisible R5 rehearsal required by the lead
execution directive. It is not a new GPU experiment, a change to measured
implementation M, an external review, a paper acceptance, or public-claim
authorization.

## 1. Frozen identities

| Role | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Tool snapshot F | `61190073428fbe487721262cfe1f4a77d4cb5d2f` | `2f2aa13221d2e1f7777b03e0ef3b1fd9feefcf6f` |

F was pushed to `origin/codex/cgo-goal5836-handoff`. A subsequent
`git ls-remote origin refs/heads/codex/cgo-goal5836-handoff` returned the exact
F commit. F adds offline projection, verification, control, and report files;
it does not change `src/`, `include/`, or `experiments/` relative to M.

## 2. Remote recovery and clean checkout

The first remote clone command exceeded its 30-second command window and left
an incomplete repository without `HEAD`:

```text
git clone --no-local --branch codex/cgo-goal5836-handoff --single-branch https://github.com/rubaolee/rtdl.git /tmp/rtdl-cgo2027-F611900734-clean
observed result: incomplete clone; HEAD unresolved
```

No result from that incomplete state was reused. The same new repository was
completed from the remote and detached at the fetched commit:

```text
git fetch --depth=1 origin refs/heads/codex/cgo-goal5836-handoff
exit=0
git switch --detach FETCH_HEAD
exit=0
```

Before and after all tests and exports, `git status --porcelain=v1` emitted no
path. `git rev-parse HEAD` and `git rev-parse HEAD^{tree}` returned the F
identities above. The F template root contained only
`paper/cgo2027/artifact_post_goal5851/verify.py`; no bytecode or generated
package was written under the repository.

## 3. Input and tool bindings

The clean F checkout used these tool bytes:

| File | SHA-256 |
| --- | --- |
| `paper/cgo2027/artifact_post_goal5851/verify.py` | `5a41e246412870118f1c11cb11a1622e86d8999d664dcf578eee638f63ec0100` |
| `scripts/goal5852_build_submission_evidence.py` | `642f60ece4bd7f5848b19bfdf8a6c66556a2fb1ac70e3b68ad7d9d9e39c47c69` |
| `tests/goal5852_submission_evidence_test.py` | `e7217191c6e513d4bf3b4e652f025c75ac18eba9c6f701d2f8651831c24315c6` |

The raw inputs remained:

| Input | SHA-256 |
| --- | --- |
| Ada `EVIDENCE_MANIFEST.json` | `e71f98c713ee9c7c0bb5733d5ff1921d11eea5bc819ec3fea217961f9a690f6f` |
| Ampere `EVIDENCE_MANIFEST.json` | `9f1031c4fc07bf23635904f7f93e075a0a3c1a0ed5aaa21f6dc48e47d92b9340` |
| Cross-generation authority | `99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692` |

The focused F suite ran from the clean checkout with bytecode disabled:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:. /Users/rl2025/.venvs/rtdl-goal5837-py312/bin/python -m unittest tests.goal5848_strong_baseline_contract_test tests.goal5848_transaction_authority_test tests.goal5848_cross_generation_authority_test tests.goal5852_submission_evidence_test
exit=0; 65/65 PASS
```

Ruff also returned exit 0 for the exporter, packaged verifier, and R2 tests.

## 4. Two external-root builds

The exporter was invoked twice from F with the same three raw roots and F's
template root. The output roots were new, explicit, and outside the repository:

```text
/tmp/rtdl-cgo2027-R5-F611900734-build-a-20260906-1722
/tmp/rtdl-cgo2027-R5-F611900734-build-b-20260906-1722
```

Both invocations returned exit 0 and
`PASS__RAW_TO_ANONYMOUS_PROJECTION_AND_PACKAGE`. `diff -qr` over the complete
roots returned exit 0 with no output. Each exporter invocation also built its
archive twice in process and required byte equality. Reusing root A through
the actual CLI returned exit 1 with
`output root already exists; overwrite refused`.

The shared output identities are:

| Output | Self-seal | File SHA-256 |
| --- | --- | --- |
| Projection | `fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca` | `94144ab768d669ebcdf83a12d018decd66a306f940fa4bf1cf18a1fcc91ae77f` |
| Recount summary | `54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105` | `2a98ea207004153b4e04c52a36ce3ae5940cc7a7ddbc5723caa3fb5f6d498ddd` |
| Public manifest | `b0a26d5630815f65035f6c58e9429d865d47a52fd13ec7117eb3d2d0bbfa653a` | `feba2ad47422559c867ac04b18a826c00f9aa859d9882c8bddf2b33acf305929` |
| Private provenance | `4a58eec716bf4694e6cacdde33151b21c6dd08b3a9d8ad630a0be2d6e18e57fb` | `ebeea758deb57ae23a00e8527f87ebb23cc0d5756718223b6f079b34ca899a81` |
| Export receipt | `5c6b83f5e1c4a7786cee62445b61240cabf38b2e8911930bc990aa0d4407b701` | `c65d0d2a13041a348ea49d39d1268013448408d94d261c720046171e16897576` |

The deterministic nine-member archive is 179,978 bytes with SHA-256
`963acc1c543df70609fccc06e0fa79f63b886be75b46699b9a2a51c662092639`.

## 5. Foreign-path replay and anonymity

The archive from build A was extracted to:

```text
/tmp/RTDL CGO final F replay 611900734/rtdl-cgo2027-artifact
```

The following commands ran with project `PYTHONPATH` removed, user site
disabled, and isolated Python mode:

```text
env -u PYTHONPATH PYTHONNOUSERSITE=1 /usr/bin/python3 -I verify.py --artifact-root .
exit=0; PASS__OFFLINE_PROJECTION_RECOUNT
env -u PYTHONPATH PYTHONNOUSERSITE=1 /usr/bin/python3 -I -O verify.py --artifact-root .
exit=0; PASS__OFFLINE_PROJECTION_RECOUNT
```

Both reconstructed 160 formal cells, 20,480 formal samples, 1,024
instrumentation endpoints, 20 AOT qualifications, and eight competence
workers. Both reported `gpu_execution_performed=false`,
`project_import_performed=false`, and
`public_or_manuscript_claim_authorized=false`.

`cmp` proved the packaged `verify.py` byte-identical to F's verifier. A scan of
all extracted public bytes returned no internal Goal identifier, author or
workspace path, username, GPU UUID, SSH endpoint, internal-history path,
GitHub identity, or author name. Archive members were regular mode-0444 files
with uid/gid zero, empty owner/group names, and mtime zero.

## 6. Verdict and remaining boundary

R5 is closed. Candidate F is committed, pushed, remotely recoverable, and has
passed the required clean-checkout raw export, two-build determinism,
foreign-path normal and optimized replay, anonymity, overwrite rejection, and
verifier-identity checks.

R5 does not authorize any public or manuscript claim. R4 manuscript rewrite,
R6 final PDF/package pairing, R7 final-bytes reviews, and R8 submission checks
remain open. Any later executable change creates a new F candidate and requires
this rehearsal again.
