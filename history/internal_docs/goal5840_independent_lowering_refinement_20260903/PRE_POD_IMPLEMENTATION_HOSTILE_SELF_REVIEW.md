# Goal5840 pre-pod implementation hostile self-review

Date: 2026-09-03

Verdict:
`READY_FOR_EXACT_GPU_EXECUTION__NOT_A_GOAL5840_RESULT`

Review type: strict internal self-review. External review count remains zero
under the owner-deferred travel constraint. This document is not consensus.

## Scope reviewed

The review covers the target-evidence bundle v2, exact control-flow source
capture, real lifecycle evidence capture, standalone target checker, frozen
mutation suite, four-mode GPU harness, downloaded-artifact verifier, and the
pre-pod input authority. It does not review a GPU result because Goal5840 has
performed zero GPU launches at this checkpoint.

Controlling pre-pod authority:

- Internal authority seal:
  `785529613e79a806937b5cc56b041e671de90a164e7434d6772de9b7f4989d91`
- Whole-file SHA-256:
  `a34a59767b75cd125f00f85613597197017c8b7cd7a8c66a0f55b66737177f82`
- Frozen denominator: three route groups, four modes, five properties per
  route, 15 unique mutation units, and 20 mode-replicated mutation
  applications.

## Blocking findings found and repaired before freeze

### Fixed P0: post-pod verifier initially rejected every real Git commit

The first full synthetic capsule replay exposed that the verifier applied the
64-hex SHA-256 validator to a 40-hex Git object ID. The implementation now has
separate strict validators and requires an independently supplied exact commit
to equal the commit in `RESULT.json`.

### Fixed P0: mutation evidence was initially inspected but not replayed

A digest seal is not a signature. Merely validating the stored 20-row mutation
report would permit a trusted runner to fabricate it. The mutation suite now
runs under `python -I`, and the downloaded-artifact verifier independently
reapplies all 20 mode-replicated mutations and requires byte-equivalent JSON
to the pod report.

### Fixed P1: reused build manifest had an incomplete Goal5840 ABI statement

The Goal5838 builder's required-symbol set covered its sphere exam but not the
bounded-relation and triangle-reduction prepared routes. The Goal5840 runner
now checks 17 exact external dynamic symbols using GNU `nm`; the local verifier
independently parses the downloaded ELF64 dynamic symbol table and requires the
same set. The builder manifest's own seal, build-input digest, exact ten native
source blobs, exact commit, and DSO digest are also revalidated.

### Fixed P1: frozen-core preservation was initially only counted post hoc

The verifier now requires the complete three-file frozen-core record in the
GPU result to equal the pre-pod authority, then independently resolves those
three blobs from the externally supplied Git commit. A reported count of three
is no longer sufficient.

### Fixed P1: duplicate mutation logic existed in a test module

The obsolete test-local mutation implementation was removed. Tests and the GPU
runner now use one production mutation suite, while the downloaded verifier
executes that suite in an isolated process.

## Remaining non-blocking risks and trusted base

### P1: same-author conceptual bias remains

Codex implemented both the evidence capture and the separate checker. Process
isolation and an RTDL-import ban prevent direct reuse of declaration-side
projection code, but do not prove conceptual independence. External critical
review remains required before manuscript wording or consensus.

### P1: the evidence capturer and runtime trust-root recorder remain trusted

The capturer reaches through the generic lifecycle's private materialization
bridge to recover the executable object. It verifies the public lifecycle
identity chain and preserves exact generated source/PTX, but this bridge is
evidence infrastructure rather than a supported public API. The post-
materialization executable identity root is recorded by the runner and is not
independent hardware attestation.

### P1: CP004 is bounded syntactic control-flow evidence

The checker parses exact Python ASTs and exact native/wrapper source anchors to
establish status-before-publication for the three selected routes. It is not a
general control-flow proof and does not establish NVIDIA implementation
semantics. Unknown syntax fails closed.

### P2: integrity seals require an external trust anchor

All JSON seals are unkeyed SHA-256 commitments, not signatures. The downloaded
verifier therefore requires the caller to supply the exact 40-hex source
commit, verifies all relevant Git blobs, and refuses to trust the commit named
only by the result itself.

### P2: the positive fixtures are deliberately small

The four frozen fixtures are deterministic and non-degenerate: three bounded
pairs, five triangle hits, weighted result 35, and six sphere queries with
mixed hit counts. They test exact lowering/refinement evidence, not workload
generalization, application correctness, throughput, or speedup.

### P2: NVIDIA compiler and OptiX semantics remain outside the proof

The bundle binds generated CUDA source, leaf PTX, wrapper PTX, composed PTX,
target profile, native DSO, build inputs, SBT/buffer contracts, true-OptiX
traversal receipt, and output digest. It does not prove NVVM, NVRTC, PTX, OptiX,
the CUDA driver, or hardware correct.

## Verification completed at this checkpoint

- Goal5840 focused tests: 38/38 pass.
- Inherited bounded-relation, triangle-reduction, and selected-sphere route
  regressions: 83/83 pass.
- Complete synthetic evidence capsule: four positive checker replays and all
  20 mutation applications pass the post-download verifier.
- Isolated mutation-suite CLI: runs under `python -I` outside the repository
  working directory.
- Goal5838 frozen-core verifier: pass with zero changed files.
- Python compilation and `git diff --check`: pass.

The broad `goal58*_test.py` historical collection is not a passing regression
gate in this source-only travel checkout: 1093 tests produced 4 failures, 88
errors, 18 skips, and the remainder passed. The 92 non-passes belong only to
Goals 5800, 5801, 5802, 5803, 5805, 5807, 5808, 5809, 5814, 5818, and the
already disclosed Goal5832 custody drift. Most are missing Git-excluded frozen
capsules or machine-specific `/proc`, tool-symlink, and interpreter contracts.
There is no Goal5840 non-pass in that run. This classification does not relabel
or forgive those historical failures; it records why the whole historical
collection cannot replace the focused 38/38 and direct-route 83/83 gates.

## Decision

The implementation is ready to run exactly once from the eventual committed
and pushed source state on the supplied NVIDIA pod. A valid GPU result must
pass all four true-OptiX modes, 20 independent property checks, all 15 unique
frozen mutation units (20 mode replications), exact DSO ABI/source custody, and
local post-download replay. Failure of tooling or pod setup is an engineering
defect to repair; no scientific failure may be claimed unless a frozen claim
unit itself cannot be satisfied without changing the preregistered scope.

This checkpoint authorizes no lowering-preservation statement, compiler
soundness theorem, Paper App, application result, performance claim, external
review, consensus, or CGO manuscript claim.
