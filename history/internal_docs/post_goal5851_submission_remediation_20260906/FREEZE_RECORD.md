# CGO 2027 executable and evidence freeze record

Recorded: 2026-09-06T21:32:49Z / 2026-09-06T17:32:49-0400

Status: `FROZEN_TOOLING_CANDIDATE_F2__R5_CLOSED__PAPER_AND_REVIEW_PENDING`

The hard development freeze begins at 2026-09-08T00:00:00-0400. This record
fixes the executable bytes already accepted before that deadline. It belongs
to a later documentation/paper snapshot P and therefore does not claim to be
contained in F2 itself.

## 1. Git identities

| Role | Commit | Tree |
| --- | --- | --- |
| Measured implementation M | `d653fe4ad170c5b51fee309d653c9565944dcf2e` | `d53af23a2599f9d6adb4ac0bfff39cd0ab31860b` |
| Frozen predecessor E | `12ab1bc0a8ebbcefe42e93c677a151c04c3ba3c8` | `aa8b9b12a7bf9cf4395cb71e4fb8e6eb0f169ab6` |
| Final tooling snapshot F2 | `9771facece4ccd807e26c15b21892b9d0a701d32` | `11c62c28bdebcc7d437f8ab3326635af0832ce48` |

- Branch: `codex/cgo-goal5836-handoff`.
- Remote: `https://github.com/rubaolee/rtdl`.
- Pushed ref observed: F2 exactly at
  `refs/heads/codex/cgo-goal5836-handoff`.
- Fresh remote checkout: `/tmp/rtdl-cgo2027-F2-9771face-clean`.
- Checkout status before and after validation: clean.
- Git submodules: none reported by `git submodule status`.
- Paper/document snapshot P: not yet assigned.

## 2. Executable whitelist and immutable measured source

`git diff M..F2 -- src include experiments` reports no changed path. The only
new executable files between M and F2 are:

| Path | F2 SHA-256 | Purpose |
| --- | --- | --- |
| `paper/cgo2027/artifact_post_goal5851/verify.py` | `5a41e246412870118f1c11cb11a1622e86d8999d664dcf578eee638f63ec0100` | Standard-library offline projection verifier |
| `scripts/goal5852_build_submission_evidence.py` | `ba3075214564cad6b51dfea93cb8741c100d19f149ecd5b5d1a70eee89ffabd1` | Fail-closed raw-to-anonymous exporter and deterministic packager |
| `tests/goal5852_submission_evidence_test.py` | `a75d897032d44becdc4838ec49c1ffe31119943adf0f8d4735fbc9277047dcd9` | Export/verifier rejection and structural tests |

All other M-to-F2 changes are control, review, evidence-index, or report text.
F2 does not change measured workloads, native or compiler implementation,
partner code, experiment execution, timers, estimators, thresholds, retained
samples, or historical authorities.

## 3. Toolchain used for the F2 rehearsal

| Tool | Version |
| --- | --- |
| Git | 2.54.0 |
| Development Python | 3.12.14 |
| Ruff | 0.16.5 |
| Foreign replay `/usr/bin/python3` | 3.9.6 |
| Tectonic available for later paper build | 0.16.9 |

The anonymous verifier itself requires Python 3.10 or newer. The macOS system
Python 3.9.6 passed this specific standard-library replay, but that observation
does not broaden the package's declared support floor.

## 4. Frozen raw evidence

| Input | SHA-256 |
| --- | --- |
| Ada evidence manifest | `e71f98c713ee9c7c0bb5733d5ff1921d11eea5bc819ec3fea217961f9a690f6f` |
| Ada complete archive | `c9128bae15da7ed3262c0bad96799e8cc56d1292c14f9af8713ea174cfc2cced` |
| Ada single-generation authority/recount | `191e85ea19a2af2186cddf873d19483753197f258b5afddba06abd57cc0a66b7` |
| Ampere evidence manifest | `9f1031c4fc07bf23635904f7f93e075a0a3c1a0ed5aaa21f6dc48e47d92b9340` |
| Ampere complete archive | `7bbabfc8d1d9dfd3cc9bd701bd7f40e9f50c8ccfcbbac9504db43e9e42b7c2a2` |
| Ampere single-generation authority/recount | `35049de227c9c251314615039f07aaf6af71dd26bf24e8c6f5e1c74fb8ceadb3` |
| Cross-generation authority/recount | `99e1eab6f33e609a8739caecb26dc05e5c8d669b3ad67f58fd0540d781151692` |

Private source roots remain outside Git under `/Users/rl2025/RTDL_evidence/`.
They retain real machine identity and historical custody bytes. They are not
the anonymous package and were not modified by export.

## 5. Scope adjudication bindings

| Record | SHA-256 |
| --- | --- |
| `PROTOCOL_SCOPE_ADJUDICATION.md` | `53b5f6028f6f549be0012bb949e46dfff0ed6823d02bff96bff672f53bed6531` |
| `CLAIM_LEDGER.json` | `f148027baa49756bdd22d24d7c5c77058a951653dd73edf9308a97cb412370d8` |

The binding decisions are:

```text
machine_numerical_contract_passed=true
original_written_per_execution_receipt_requirement_fulfilled=false
wrong_output_observed_in_final_gpu_samples=false
public_prepared_a_over_direct_observation_retainable=true
implementation_entry_positive_performance_claim_allowed=false
```

The main performance observation is exact-task prepared public A/D. Entry and
post-import results are lifecycle diagnostics. Post-import is adverse in all
four rows and reaches 2.377129x. Relative to E, first-result medians regress by
about 8%--22% at entry and 16%--31% post-import; these comparisons are post hoc,
non-gating, and lifecycle/import-confounded. No intrinsic speedup, broad parity,
unbiased unseen-application, arbitrary lowering, usability, prevalence, or
complete per-execution physical-receipt claim is authorized.

## 6. F2 validation and derived package

Clean-F2 regression results:

- Submission-evidence tests: 14/14 normal and 14/14 under `python -O`.
- Goal5848 discovery: 128/128 normal and 128/128 under `python -O`.
- Goal5851 fused replay: 7/7.
- Ruff over all three F2 executable files: pass.
- Skips: zero.

Two new external output roots were byte-identical, in-process archive builds
were byte-identical, an existing output root was rejected, and normal plus
optimized isolated replay passed from a second extraction path containing
spaces. The full record is `R5_FINAL_F2_REHEARSAL_REPORT.md`.

| Derived output | Identity |
| --- | --- |
| Projection self-seal | `fa30b906b0d5a6edfdcc3267f24cea8274c9c9450a79edeef0058e89f6d252ca` |
| Projection file SHA-256 | `94144ab768d669ebcdf83a12d018decd66a306f940fa4bf1cf18a1fcc91ae77f` |
| Summary self-seal | `54ecfddf642cfbd00dfba8af343392524143781744c698e2bc72a3c1b3843105` |
| Summary file SHA-256 | `2a98ea207004153b4e04c52a36ce3ae5940cc7a7ddbc5723caa3fb5f6d498ddd` |
| Manifest self-seal | `4a62601b0e421033e67169ed3f89818c6cf62b8acc7723df9cc3ca4c8a46fc32` |
| Manifest file SHA-256 | `da73f16918c572dbffc5d803627837ae412197afc3ea9eee341b4989d9b494d8` |
| Export receipt self-seal | `9294627a889356590b7a2ea53e126fb40711a7aefb739788e8ec0294dc67a522` |
| Export receipt file SHA-256 | `6e03835f3b53a1a49dfab6b4f095a6c5cc2f984c07d0508c5cc7492ec98f099c` |
| Nine-member archive SHA-256 | `916cedbb7001c7aa43e66df3f992b543b7b3ca5a013f0f997790113a2e3738b8` |
| Archive bytes | 180,308 |

The package is evidence-only. Its component inventory states the distribution
boundary and excludes third-party code, CUDA, OptiX, GPU drivers, proprietary
headers, measured binaries, and signing keys. It supports offline numerical
recount, not GPU execution or full historical environment reconstruction.

## 7. Freeze rule

F2 is immutable. A pre-deadline executable change would require a new F,
another remote clean checkout, all tests above, twin deterministic export,
overwrite rejection, foreign normal/optimized replay, verifier binding, and a
new freeze record. After 2026-09-08T00:00:00-0400, executable changes are
forbidden; a newly found defect must narrow or remove the affected paper or
artifact claim.

Remaining work is non-GPU submission work: rewrite and render the paper (R4),
pair the final PDF and anonymous package (R6), review final bytes (R7), and run
format/anonymity/submission checks (R8). No external upload or submission has
occurred.
