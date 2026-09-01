# Internal hostile self-review: Goal5836 A1 source fidelity

Date: 2026-09-01
Review type: internal self-review, not external review
Reviewed stage: A1 static paper/source classification only
Product/case-study source mutation: none
Author/RTDL execution: none
GPU/POD/timing: none

## 1. Verdict

```text
P0 = 0
P1 = 0
P2 = 2
P3 = 1

A1 VERDICT:
PASS__TERMINAL_NEGATIVE_OUTCOME__GOAL5836_COMPLETE_AT_A1__NO_PROMOTION
```

The A1 authority is exact, portable and fail-closed. The material predicate
difference is supported independently by the paper method, the author's actual
benchmark call chain and Goal5835's frozen source boundary. It is not inferred
from a program output or timing.

The verdict completes the Goal5836 transaction under its preregistered negative
branch. It does not authorize A2, repair the predicate, build or execute either
route, use a POD/GPU, collect performance, promote Goal5835 to Paper App status,
request external review or make a public performance/correctness claim.

## 2. Acceptance checks

### 2.1 Authorization and predecessor binding

Pass. A1 begins from the exact A0 authority and the 1,189-byte owner record at
SHA-256 `066dbd5e...efa47`. The authority allows only A1 static inspection;
A2--A5, source mutation, execution, GPU, timing and external review are false.
The authorization is consumed.

### 2.2 Exact evidence custody

Pass. The builder revalidates the A0 authority and the complete 203-file source
capsule before selecting seven semantic call-chain files. Every selected file
matches its A0 inventory row, Git blob OID, byte length and SHA-256. Paper and
Goal5835 inputs are exact-byte bound. All identity paths are repository-relative.

### 2.3 Source-fidelity reasoning

Pass. The ordinary round-linear swept-sphere, constant radius, endcap, edge-only
and Boolean semantics are recorded as matches rather than over-rejected. The
material result is limited to two connected dimensions: directed obstacle-edge
orientation and the resulting inside-start/initial-overlap coverage.

The source path proving this is not dead code. The actual curve benchmark calls
`buildSharedScene(true)`, the obstacle selects loop edges, mesh construction
creates the directed graph and the collision detector traces one-sided finite
edge rays. Goal5835 instead preserves one arbitrary first direction and states
that initial overlap is excluded.

### 2.4 Frozen negative branch

Pass. `MATERIAL_PREDICATE_DIFFERENCE` maps exactly to
`TERMINAL_MAPPING_REFUSAL__KEEP_GOAL5835_SCOPE__A2_NOT_REACHABLE`. A2--A5 are
all false and unreachable. Coordinated re-sealing cannot upgrade the result,
hide either material row, authorize A2 or reopen the transaction.

### 2.5 Claim boundary

Pass. Goal5835 remains `NOT_A_PAPER_APP`; complete RT-CCD, Goal5836 functional
execution, generalization and performance counts remain false/zero. No result
is relabelled as author-code, modern-RTX or Paper-App evidence.

## 3. Findings

### P2-1: The exact paper remains arXiv v2, not publisher bytes

This is inherited from A0. The official versioned author-submitted PDF contains
the needed method and appendix, is exact-byte preserved and is linked to the
ICRA DOI. It is not the IEEE-hosted publisher byte stream. The classification
may be stated against arXiv:2409.09918v2 only. A stronger publisher-byte
identity claim remains prohibited.

### P2-2: Paper semantic locators are human-checked, not machine re-extracted

The authority byte-binds the exact 34,726,851-byte PDF and records exact pages
and sections, but its deterministic rebuild does not parse PDF content and
rederive the support strings. A1 used read-only human inspection of those
pages. This is auditable because the exact PDF is preserved, but a reviewer
must inspect pages 5, 7 and 10 rather than treating the support strings as a
machine proof. Source-side anchors are mechanically line- and hash-bound.

### P3-1: One local invocation failed before authority creation

The first direct execution of the new A1 builder failed with
`ModuleNotFoundError: scripts` because the repository root was not inserted in
`sys.path` for script-mode execution. The builder was fixed before it produced
an authority. The final output was created once under the corrected source,
binds that source and its tests, and verifies exactly. No authority was edited
in place.

The local host also lacked `pdftotext`; `pypdf==6.0.0` was installed into the
dedicated external venv `~/.venvs/rtdl-goal5836-mac` solely for
read-only inspection. The committed authority and verifier do not depend on
that package or absolute path.

## 4. Hostile counterfactuals

| Attack or failure | Result |
|---|---|
| Re-seal classification as a match | Policy validation rejects it |
| Remove or relabel one material row | Policy validation rejects it |
| Set A2 authorization or reachability true | Authorization/transition validation rejects it |
| Use source outside exact A0 capsule | File set/OID/SHA verification rejects it |
| Drift one source anchor or line | Exact rebuild differs and stored verification fails |
| Add build, execution, input, route, GPU, timing or review observation | Policy validation rejects it |
| Claim Paper App, complete RT-CCD or performance | Claim-boundary validation rejects it |
| Treat directed connectivity as an optimization only | Contradicted by paper correctness text and actual benchmark call chain |
| Continue with a replacement input after A1 | Frozen transition forbids A2 and input replacement |

## 5. Verification result

```text
A1 hostile tests: 18/18 PASS
Goal5833--Goal5836 regression: 148/148 PASS
A1 stored verifier: PASS
authority whole-file SHA-256:
f05b026c2e96506466a400de71ee8ab6893f8deecb547447f29b8af567842c5f
authority internal seal:
5d52efd485eb9433a442c3a9a81d880e91e80bb38de33d6b4499a2329c3034d6
```

## 6. Strongest current claim

> Exact static source-fidelity inspection found a material predicate difference
> between the author's directed-connectivity/inside-start contract and
> Goal5835's arbitrary single-direction, initial-overlap-excluding mapping.
> Goal5836 has therefore completed at its preregistered A1 terminal negative
> branch. Goal5835 remains a bounded Sui-derived mapping and not a Paper App.

## 7. Next action

There is no next stage or owner gate inside Goal5836. Preserve all A0/A1 bytes,
reports and claim ceilings. If the owner later wants a corrected mapping, create
a new named goal and preaction; do not continue A2, mutate this authority or
silently broaden Goal5835.

That successor would need an application-neutral directed-connectivity or
orientation contract and must not put robot-collision semantics into the
engine. Cross-application justification and new prospective evidence belong to
the successor design, not to this completed A1 transaction.
