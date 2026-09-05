# Goal5844 internal hostile self-review

## Verdict

Accept at internal engineering scope only. The successor meets its exact
1.25x threshold with a 1.0457x median block ratio, every block passes, order
strata agree, and native time is stable. Reject any broader wording until
external review and additional hardware evidence exist.

## Strongest reviewer attacks

### Was PyOptiX weakened?

No evidence supports that explanation. Both attempts rebuilt the same pinned
PyOptiX commit against the same selected OptiX 9.0 headers and CUDA 12.8 stack.
Its aggregate median changed from 129.368 us to 131.744 us, only 1.0184x. The
matched device source SHA is identical in both retained evidence sets.

### Did RTDL move validation outside the timer?

It moved optional JSON transport expansion outside steady execution, but not
physical validation. Every timed RTDL call still validates the native v8 fast
operation receipt, all 19 integrated audit words, output status, output digest,
provider identity, route, program bundle, ray count, executable identity, and
family envelope. Explicit full-forensic expansion is separately metered and
remains available.

This separation is defensible because canonicalizing the same validated proof
at four adjacent layers adds no new fact. The public result still exposes a
Mapping; inspecting it materializes and seals the ordinary transport document.

### Is the fast path forgeable by an app?

The optimized branches require the exact factory-created
`ValidatedCompactTraversalReceipt` type, not a protocol or duck-typed Mapping.
Its constructor requires a private token, and the protocol accepts it only for
the triangle-reduction family. Ordinary provider receipts and external
providers retain full canonicalization. Python cannot provide cryptographic
in-process isolation from a malicious user with arbitrary module introspection;
the claim is fail-closed API/lifecycle behavior, not protection against an
attacker executing arbitrary Python in the same process.

### Is memoization hiding changed outputs?

No. Integer digest caches are keyed by the exact integer output and reproduce
the same canonical JSON bytes. SHA validation caches are keyed by immutable
strings. Program IDs are keyed by exact nonempty strings. Executable identity
caches are keyed by frozen dataclass values. Dynamic stamp and output binding
checks still execute each call. Tests cover repeated valid values and invalid
values after cache population.

### Is the before/after comparison cherry-picked?

The adverse transaction is retained in full reduced evidence and by archive
hash. The successor used a new exact commit, checkout, environment, builds,
worker-zero, and output directory. No rows were pooled. All eight alternating
blocks and 1,024 samples per arm are retained. The best block was 0.9681x and
the worst 1.1543x; both are reported.

### Did changing the Goal5838 frozen core invalidate generalization evidence?

It invalidates only a current-tree byte-identity statement, not the historical
prospective transaction at its exact Git commit. The optimization happened
after Goal5838 completed and is generic identity memoization, not selected-app
dispatch. Reports must cite the Goal5838 commit for the frozen-core experiment
and the Goal5844 commit for current performance. Any statement that the current
tree still matches the old seal is forbidden.

### Is this enough for the CGO paper?

Not alone. It closes the strongest triangle public-steady overhead attack on
one Ada GPU. The relation row path remains adverse, external review is pending,
and human authoring evidence is unavailable. The paper can use this result only
after review and with exact scope; it cannot imply universal PyOptiX parity.

## Residual risks

1. The full archives are retained locally and by SHA, but generated DSOs are
   not committed to Git. Reviewers can inspect all worker JSON and rebuild the
   exact source commit.
2. The memoization benefit is strongest for repeated prepared executions with
   stable identities and outputs. Output-diverse workloads require separate
   evaluation.
3. One block reached 1.1543x while the median was 1.0457x. This remains below
   threshold but motivates replication rather than a zero-overhead claim.
4. Historical current-file hash tests now reject the legitimate successor.
   They must not be rewritten to pretend byte identity; exact-commit replay is
   the correct historical mechanism.
5. External review count is zero. No consensus or publication claim exists.

## Closure conditions

- Rebuild and verify the stored internal authority.
- Run its dedicated mutation/claim tests.
- Re-run the current focused functional set after evidence integration.
- Commit and push the evidence/report successor.
- Seek external review later; preserve any adverse finding.
