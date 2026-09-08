# Anonymous Application-Performance Projection Artifact

Date: 2026-09-08, America/New_York.

Status:
`AUTHOR_LOCAL_ARTIFACT_RECOUNT_PASS__INDEPENDENT_FINAL_BYTE_REVIEW_PENDING`.

This report records a derived anonymous offline projection for the separate
long-workload application transaction. It does not alter the raw transaction,
replace its independent clean-checkout recount, rerun GPU work, or authorize a
public or manuscript claim.

## Exact identities

| Object | Bytes | SHA-256 |
| --- | ---: | --- |
| Retained private raw archive | 730,851 | `ef2ca7890c9d415dc1edbe71966aabc512209c9d8608d4eaf460c7c1fddf8bdc` |
| Anonymous projection JSON | 545,481 | `ae2cb7011f407c37b3850aa2a854d177baa4a6494d704eb2ddf68e89f574578c` |
| Projection verifier | 15,284 | `787e2240496a53fe20e8834859af20de1cd1c3ec753f98bf827e49270c62a45b` |
| Projection manifest | 1,126 | `bd191292e268328c432578168ea39c21fc2721e7737515cb2abd23fdd553f552` |
| Normalized public artifact | 83,877 | `e713529fb3f3370aeef57b30793a85c5e894ee34da8bcc177fa12272816fee77` |

The public package is
`output/artifact/rtdl-cgo2027-application-performance.tar.gz`. Its tracked
source is `paper/cgo2027/artifact_long_workload/`.

## Projection and recount scope

The package retains all 240 formal worker rows, all 1,248 primary timing
samples, 120 warmups, 80 paired three-arm cells, input identity hashes, output
hashes, order, registered CPU-affinity observations, and ten evaluations. It
removes absolute paths, hostname, GPU UUID, process IDs, source commits, and
source trees. Process IDs are represented only by salted one-way tokens so the
verifier can check that all 240 workers were distinct.

The standard-library verifier independently reconstructs each worker median,
all three within-cell ratios, all ten paired medians and maxima, output/input
parity, threshold decisions, sample counts, and retry/discard/timeout counts.
It imports no RTDL or third-party module.

The package cross-binds to the retained raw archive and its formal summary,
preregistration, schedule, progress, and independent recount by SHA-256. Since
those raw bytes are intentionally absent from the anonymous package, this is a
hash cross-binding, not an independent raw-custody proof.

## Author-local validation

- Source-tree replay under ordinary Python: PASS.
- Source-tree replay under optimized Python: PASS.
- Ordinary and optimized JSON outputs: byte-identical.
- Two independently constructed normalized ustar/gzip packages:
  byte-identical.
- Replay after extraction under an unrelated path containing spaces: PASS in
  ordinary and optimized Python; outputs byte-identical.
- One timing-sample mutation: rejected.
- One unexpected-file mutation: rejected.
- One symlink mutation: rejected.
- Forbidden private-path, host, repository-link, GPU-UUID, internal-goal, and
  40-hex source-identity scan: PASS for package payload files.

The first verifier draft correctly rejected a `.5 ns` discrepancy because the
frozen worker records `int(statistics.median(samples))` for even sample counts.
The verifier was corrected to reproduce that frozen estimator; no projected
sample or retained raw byte was changed.

## Limits

The projection cannot establish honest GPU production, reproduce missing raw
inputs, execute CUDA/OptiX, validate application semantics independently, or
replace final-byte review. It supports exact offline arithmetic and identity
recount only. The old nine-member F2 artifact remains byte-for-byte unchanged
and has a different evidence population.
