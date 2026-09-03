# Goal5838 final internal hostile self-review

Date: 2026-09-03

Review mode: strict internal review only. External review was explicitly
deferred by the owner while traveling and is not claimed.

Verdict: `ACCEPT_AT_PREREGISTERED_BOUNDED_SCOPE`

Finding count: `P0=0`, `P1=0`, `P2=3`, `P3=2`.

## Reviewed surfaces

This review inspected the preregistration, frozen core seal, complete challenge
table, NIST selection result, post-selection implementation, Pod preflight,
native build manifest, final GPU artifact, RTDL-free verification, repair log,
final authority generator, authority tests, case-study README, and the final
technical report. It also reran the stored core/selection/authority verifiers,
focused tests, lint, compilation, and the post-seal frozen-file diff.

The whole-cohort run initially exposed a preexisting Goal5837 verifier error in
addition to the known Goal5832 debt. Goal5837 had bound a historical inventory
row to mutable current `AGENTS.md` bytes. The repair now reads historical rows
from the exact Goal5837 authority commit, leaves its stored authority unchanged,
and has a dedicated regression. Goal5837 passes 19/19; the final Goal583x run is
312/313 with only the disclosed Goal5832 error.

## P0 findings

None.

There is no evidence of fabricated GPU execution, silent oracle drift,
post-selection frozen-core mutation, app semantics inserted into the frozen
core, or a result promoted from the diagnostic run after verifier defects were
found.

## P1 findings

None.

Every preregistered completion condition is present in the final single-commit
run: independent post-seal selection, admitted and verified selected topology,
public generic lifecycle, two true OptiX executions, 12/12 oracle matches,
RTDL-free rederivation, evidence recovered off Pod, and zero frozen-core byte
changes.

## P2 findings

### P2-1: External review is deferred

No independent external AI or human reviewer has reviewed the final Pod
artifact and closure report. This does not block the owner-authorized internal
Goal5838 completion rule, but it blocks any external-consensus wording and
should remain an explicit later CGO review gate.

### P2-2: The prospective denominator is one topology on one hardware profile

The result demonstrates one independently selected built-in-sphere,
any-hit-count-and-continue topology on one RTX 2000 Ada / OptiX 9.0 profile. It
does not establish arbitrary Callback IR, every geometry kind, every control
topology, multiple providers, or universal GPU/SDK portability. The final
authority encodes all of these claim ceilings as false.

### P2-3: The native DSO is hash-bound but not committed

The 7,181,936-byte provider DSO was independently rehashed and remains in the
local raw-evidence directory, but generated binaries are not stored in Git.
The committed manifest preserves its SHA-256, complete source inventory,
toolchain files, headers, command, exported-symbol checks, and build result.
Future reviewers can verify the sealed evidence without rebuilding, but a full
binary-level rerun requires either retaining the raw DSO or reproducing the
recorded environment.

## P3 findings

### P3-1: Performance was intentionally not measured

The fixture is a semantic and architecture exam, not a benchmark. No timing or
speedup claim is authorized. Performance remains a separate future question.

### P3-2: The fixture is deliberately small

Six spheres and six queries, repeated in reverse order, are sufficient to cover
zero, one, and four-hit counts plus continuation and prepared-lifecycle reuse.
They are not a representative application corpus or evidence of application
correctness.

## Adversarial questions

| Attack | Review answer |
| --- | --- |
| Was the challenge chosen after seeing what worked? | No. A complete ten-row table and the three-file core were sealed before a future NIST pulse selected stable row 3. |
| Was the new topology secretly present before selection? | The table conservatively excluded exact preexisting callback topologies; the selected built-in-sphere any-hit U64 count topology was marked absent before selection. |
| Did implementation repairs invalidate prospectiveness? | No. Preregistration explicitly permits unlimited post-selection extension/provider/tooling repair while the core remains frozen. The core diff is empty. |
| Is this only CUDA code hosted in an OptiX library? | No. Receipts bind a built-in-sphere GAS, built-in intersection module, nonzero traversable, one SBT record, `optixTrace`, `optixIgnoreIntersection`, and two successful physical launches. |
| Could CPU expected values have been copied into output? | The verifier independently reconstructs the exact-rational oracle and checks physical traversal receipts and output digests. Primary and reverse query orders both execute. |
| Did the diagnostic verifier failures get hidden? | No. The diagnostic artifact and all three verifier defects are documented; final evidence was freshly regenerated only after repaired code was committed. |
| Does one pass prove a universal generic compiler? | No. The authority explicitly denies arbitrary IR and universal provider claims. |
| Does completion imply a benchmark or Paper App? | No. Both are explicitly false. |

## Authority review

`scripts/goal5838_build_final_authority.py` is standard-library-only. It
recomputes the domain-separated challenge-table, generic-core, selection,
preflight, build, GPU-result, verification, and final-authority seals. It checks
the exact evidence commit, frozen baseline, selected row, pre-selection zero
activity, clean build/execution custody, DSO identity, two launches, 12 exact
rows, and every negative claim boundary. It creates the authority exclusively
and refuses overwrite. Its tests prove exact stored rederivation and reject
semantic tampering.

## Final recommendation

Accept Goal5838 as complete only with the exact phrase "one bounded prospective
frozen-core topology success." Preserve all negative claim boundaries. Before a
CGO submission, obtain independent external review of the committed evidence,
add additional prospective topologies if the paper needs a broader empirical
generalization statement, and keep performance evaluation separate from this
architecture-validity experiment.
